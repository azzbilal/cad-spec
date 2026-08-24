"""Build a CadQuery script and extract the measurements a spec can be checked against.

This module is deliberately dumb about specs. It answers one question:
"given a piece of code, what geometry actually came out?"
Everything spec-related lives in rubric.py.

Hole detection uses exact surface geometry, not bounding-box guesses: the
cylinder radius and axis come from the kernel, a just-inside-the-surface
membership probe rejects convex rounds and shell walls, a full-cylinder
area check rejects concave corner fillets, and coaxial faces are grouped
so counterbores and seam-split cylinders are handled explicitly rather
than by luck.

Execution safety: model code runs inside a persistent worker PROCESS so a
hung or side-effecting rollout can neither wedge the scorer nor dirty the
workspace. CAD_SPEC_EXEC_TIMEOUT bounds each build (seconds, default 10).
CAD_SPEC_INPROC=1 disables isolation for debugging. This is containment,
not a security boundary; Prime's sandbox remains the real one.

Windows note: the spawn-based worker requires callers to follow the standard
multiprocessing contract - entry scripts must guard top-level code with
if __name__ == "__main__":
"""

from __future__ import annotations

import atexit
import math
import multiprocessing
import os
import re
import tempfile
from dataclasses import dataclass, field
from typing import Any

CODE_BLOCK = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)

# A drilled bore is a cylinder whose axis is parallel to Z.
AXIS_TOL = 1e-6
# Decimal places used when grouping coaxial cylindrical faces into features.
COAXIAL_DP = 3
# Fraction of the cylinder radius (dimensionless) to back off FROM THE SURFACE
# before probing membership, floored at PROBE_INSET_MIN_MM so hairline bores
# still probe strictly inside their own air channel. Asking "does material
# continue immediately inward of this surface" stays correct on hollow parts;
# probes deeper toward the axis lie there - a shelled box's outer-fillet axis
# sits in open cavity, so halfway-to-axis air reads as a phantom bore.
PROBE_INSET_FRACTION = 0.05
# Absolute floor for the surface-inset probe distance, in millimetres.
PROBE_INSET_MIN_MM = 1e-3
# Minimum covered fraction (dimensionless) of a FULL cylinder - summed
# cylindrical face area in mm^2 vs pi * d * h over the group's Z extent -
# for a coaxial group to count as a drilled bore. Separates closed bores
# from concave corner fillets, which probe like bores but cover only ~0.25
# as quarter arcs; seam-split bores still reach ~1.0 across their halves.
AREA_COMPLETENESS_MIN = 0.99


class BuildError(Exception):
    """Model code did not produce a usable solid."""


@dataclass
class Hole:
    diameter: float
    x: float
    y: float
    depth: float


@dataclass
class Measurements:
    length: float          # bbox X
    width: float           # bbox Y
    thickness: float       # bbox Z
    volume: float          # mm^3
    solid_count: int       # >1 means disconnected pieces
    holes: list[Hole] = field(default_factory=list)

    @property
    def hole_count(self) -> int:
        return len(self.holes)


def extract_code(completion: str) -> str:
    """Pull python out of a model response. Falls back to the raw text."""
    blocks = CODE_BLOCK.findall(completion)
    if blocks:
        return max(blocks, key=len).strip()
    return completion.strip()


def build(code: str) -> Any:
    """Exec model code and return the object bound to `result`.

    Not a security boundary. Used directly by tests and by the isolated
    worker; production scoring goes through build_and_measure().
    """
    import cadquery as cq

    namespace: dict[str, Any] = {"cq": cq, "cadquery": cq, "math": math}
    # Executing model code IS the task; containment happens in the worker.
    try:
        exec(compile(code, "<model>", "exec"), namespace)
    except Exception as exc:
        raise BuildError(f"execution failed: {type(exc).__name__}: {exc}") from exc

    obj = namespace.get("result")
    if obj is None:
        raise BuildError("code did not define `result`")

    try:
        solid = obj.val() if hasattr(obj, "val") else obj
    except Exception as exc:
        raise BuildError(f"could not resolve result to a shape: {exc}") from exc

    if not hasattr(solid, "Volume"):
        raise BuildError(f"`result` is not a shape (got {type(obj).__name__})")

    return solid


def _z_aligned_cylinders(solid: Any) -> list[tuple[float, float, float, Any]]:
    """Exact kernel geometry for every Z-parallel cylindrical face."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_SurfaceType

    out: list[tuple[float, float, float, Any]] = []
    for face in solid.Faces():
        adaptor = BRepAdaptor_Surface(face.wrapped)
        if adaptor.GetType() != GeomAbs_SurfaceType.GeomAbs_Cylinder:
            continue
        cylinder = adaptor.Cylinder()
        direction = cylinder.Axis().Direction()
        if abs(direction.X()) > AXIS_TOL or abs(direction.Y()) > AXIS_TOL:
            continue  # horizontal or angled cylinder: not a drilled bore
        location = cylinder.Axis().Location()
        out.append((cylinder.Radius(), location.X(), location.Y(), face))
    return out


def _extract_holes(solid: Any) -> list[Hole]:
    """Internal bores only. Fillets, external rounds and bosses are excluded.

    Two independent discriminators, because hollow geometry defeats either
    alone:

    1. Membership probed JUST INSIDE the cylindrical surface: material there
       means the face is convex - an external round, a boss, or the outer
       wall of a shell - and the face is rejected. Probes deeper toward the
       axis ask "is the axis buried in material", which is the wrong
       question on hollow parts and answers "no" for phantom reasons.
    2. Completeness: a coaxial group must cover AREA_COMPLETENESS_MIN of the
       full cylinder pi*d*h over its Z extent. Concave corner fillets pass
       discriminator 1 honestly (material really does continue outward) yet
       are quarter arcs, locally indistinguishable from bores; only closed-
       cylinder area separates them.

    Grouping by axis position merges seam-split halves into one feature,
    exposes coaxial stacks (counterbores) as separate diameters per position,
    and gives discriminator 2 its per-group face-area sum.
    """
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_State

    classifier = BRepClass3d_SolidClassifier(solid.wrapped)

    # position -> {diameter -> [summed cylindrical face area mm^2, deepest face height mm]}
    features: dict[tuple[float, float], dict[float, list[float]]] = {}
    for radius, cx, cy, face in _z_aligned_cylinders(solid):
        fbb = face.BoundingBox()
        if fbb.zlen <= 0:
            continue
        inset = max(radius * PROBE_INSET_FRACTION, PROBE_INSET_MIN_MM)
        probe = gp_Pnt(cx + (radius - inset), cy, (fbb.zmin + fbb.zmax) / 2)
        classifier.Perform(probe, 1e-6)
        if classifier.State() == TopAbs_State.TopAbs_IN:
            continue  # material immediately inward => convex round/fillet/boss/wall
        key = (round(cx, COAXIAL_DP), round(cy, COAXIAL_DP))
        diameter = round(2 * radius, 4)
        entry = features.setdefault(key, {}).setdefault(diameter, [0.0, 0.0])
        entry[0] += face.Area()
        entry[1] = max(entry[1], round(fbb.zlen, 4))

    holes: list[Hole] = []
    for (x, y), diameters in sorted(features.items()):
        for diameter, (area, depth) in sorted(diameters.items()):
            full_cylinder_area = math.pi * diameter * depth
            if area < AREA_COMPLETENESS_MIN * full_cylinder_area:
                continue  # partial arc (corner fillet etc.), not a closed bore
            holes.append(Hole(diameter=diameter, x=round(x, 4), y=round(y, 4), depth=depth))
    return holes


def measure(solid: Any) -> Measurements:
    """Extract features from a built solid."""
    try:
        bb = solid.BoundingBox()
        volume = solid.Volume()
        solids = solid.Solids()
    except Exception as exc:
        raise BuildError(f"shape could not be measured: {exc}") from exc

    if volume <= 0:
        raise BuildError("shape has zero or negative volume")

    return Measurements(
        length=round(bb.xlen, 4),
        width=round(bb.ylen, 4),
        thickness=round(bb.zlen, 4),
        volume=round(volume, 4),
        solid_count=len(solids),
        holes=_extract_holes(solid),
    )


def _measure_code(code: str) -> Measurements:
    return measure(build(code))


# --- isolated execution ------------------------------------------------------
#
# One persistent worker process owns the cadquery import and serves build
# requests over a pipe. Per-call timeouts kill hung rollouts; crashes respawn
# the worker on the next call. Spawn context keeps Windows and CI identical.


def _exec_timeout() -> float:
    return float(os.environ.get("CAD_SPEC_EXEC_TIMEOUT", "10"))


# Fixed window for a fresh worker to spawn, import the kernel and announce
# readiness. Deliberately independent of CAD_SPEC_EXEC_TIMEOUT.
_STARTUP_TIMEOUT = 120.0


def _inproc_requested() -> bool:
    return os.environ.get("CAD_SPEC_INPROC", "") == "1"


def _worker_main(conn: Any) -> None:
    os.chdir(tempfile.mkdtemp(prefix="cad-spec-worker-"))
    import cadquery  # noqa: F401 - warm the kernel BEFORE announcing readiness

    conn.send(("ready", None))
    while True:
        try:
            kind, payload = conn.recv()
        except (EOFError, KeyboardInterrupt):
            return
        if kind == "stop":
            conn.send(("ok", None))
            return
        try:
            conn.send(("ok", _measure_code(payload)))
        except BuildError as exc:
            conn.send(("error", str(exc)))
        except Exception as exc:  # report faults before dying
            conn.send(("error", f"worker fault: {type(exc).__name__}: {exc}"))


class _Worker:
    def __init__(self) -> None:
        ctx = multiprocessing.get_context("spawn")
        parent_conn, child_conn = ctx.Pipe()
        self.proc = ctx.Process(target=_worker_main, args=(child_conn,), daemon=True)
        self.proc.start()
        child_conn.close()
        self.conn = parent_conn
        # Interpreter spawn + kernel warm-up wait on a generous fixed window,
        # NOT the per-build budget: CAD_SPEC_EXEC_TIMEOUT must measure model
        # code only, so a tight budget stays usable right after a respawn.
        if not self.conn.poll(_STARTUP_TIMEOUT):
            self.kill()
            raise BuildError(f"scorer worker did not start within {_STARTUP_TIMEOUT:g}s")
        try:
            status, _payload = self.conn.recv()
        except EOFError as exc:
            raise BuildError("scorer worker died during startup") from exc
        if status != "ready":
            raise BuildError("scorer worker sent an unexpected startup message")

    @property
    def alive(self) -> bool:
        return self.proc.is_alive()

    def call(self, code: str) -> Measurements:
        try:
            self.conn.send(("measure", code))
        except (BrokenPipeError, OSError) as exc:
            raise BuildError(f"scorer pipe broke: {exc}") from exc
        if not self.conn.poll(_exec_timeout()):
            self.kill()
            raise BuildError(f"model code exceeded {_exec_timeout():g}s execution budget")
        try:
            status, payload = self.conn.recv()
        except EOFError as exc:
            raise BuildError("scorer worker died while executing model code") from exc
        if status == "error":
            raise BuildError(str(payload))
        return payload

    def kill(self) -> None:
        self.proc.terminate()
        self.proc.join(timeout=5)

    def stop(self) -> None:
        try:
            if self.alive:
                self.conn.send(("stop", None))
                self.proc.join(timeout=5)
                if self.alive:
                    self.kill()
        except (OSError, BrokenPipeError):
            self.kill()


_worker: _Worker | None = None


def _get_worker() -> _Worker:
    global _worker
    if _worker is None or not _worker.alive:
        _worker = _Worker()
    return _worker


def shutdown_worker() -> None:
    global _worker
    if _worker is not None:
        _worker.stop()
        _worker = None


atexit.register(shutdown_worker)


def build_and_measure(completion: str) -> Measurements:
    """Extract code, run it isolated, measure the result. Raises BuildError."""
    code = extract_code(completion)
    if _inproc_requested():
        return _measure_code(code)
    try:
        return _get_worker().call(code)
    except BuildError:
        raise
    except Exception as exc:  # anything else means the worker is unwell
        shutdown_worker()
        raise BuildError(f"isolated scorer failed: {type(exc).__name__}: {exc}") from exc
