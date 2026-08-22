"""Build a CadQuery script and extract the measurements a spec can be checked against.

This module is deliberately dumb about specs. It answers one question:
"given a piece of code, what geometry actually came out?"
Everything spec-related lives in rubric.py.

Hole detection uses exact surface geometry, not bounding-box guesses: the
cylinder radius and axis come from the kernel, a point-membership probe
separates internal bores from external rounds and fillets, and coaxial faces
are grouped so counterbores and seam-split cylinders are handled explicitly
rather than by luck.

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
    try:
        exec(compile(code, "<model>", "exec"), namespace)  # noqa: S102 - the task IS model code
    except Exception as exc:  # noqa: BLE001 - any failure is a build failure
        raise BuildError(f"execution failed: {type(exc).__name__}: {exc}") from exc

    obj = namespace.get("result")
    if obj is None:
        raise BuildError("code did not define `result`")

    try:
        solid = obj.val() if hasattr(obj, "val") else obj
    except Exception as exc:  # noqa: BLE001
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

    A cylindrical face counts as a bore when material does NOT continue
    radially inward from its surface toward its own axis - probed with a
    solid classifier halfway between surface point and axis. Grouping by
    axis position merges seam-split halves into one feature and exposes
    coaxial stacks (counterbores) as separate diameters per position.
    """
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_State

    classifier = BRepClass3d_SolidClassifier(solid.wrapped)

    # position -> {diameter -> max depth seen}
    features: dict[tuple[float, float], dict[float, float]] = {}
    for radius, cx, cy, face in _z_aligned_cylinders(solid):
        fbb = face.BoundingBox()
        if fbb.zlen <= 0:
            continue
        probe = gp_Pnt(cx + radius * 0.5, cy, (fbb.zmin + fbb.zmax) / 2)
        classifier.Perform(probe, 1e-6)
        if classifier.State() == TopAbs_State.TopAbs_IN:
            continue  # material toward the axis => convex round/fillet/boss
        key = (round(cx, COAXIAL_DP), round(cy, COAXIAL_DP))
        diameter = round(2 * radius, 4)
        depths = features.setdefault(key, {})
        depths[diameter] = max(depths.get(diameter, 0.0), round(fbb.zlen, 4))

    holes: list[Hole] = []
    for (x, y), diameters in sorted(features.items()):
        for diameter, depth in sorted(diameters.items()):
            holes.append(Hole(diameter=diameter, x=round(x, 4), y=round(y, 4), depth=depth))
    return holes


def measure(solid: Any) -> Measurements:
    """Extract features from a built solid."""
    try:
        bb = solid.BoundingBox()
        volume = solid.Volume()
        solids = solid.Solids()
    except Exception as exc:  # noqa: BLE001
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


def _inproc_requested() -> bool:
    return os.environ.get("CAD_SPEC_INPROC", "") == "1"


def _worker_main(conn: Any) -> None:
    os.chdir(tempfile.mkdtemp(prefix="cad-spec-worker-"))
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
        except Exception as exc:  # noqa: BLE001 - report faults before dying
            conn.send(("error", f"worker fault: {type(exc).__name__}: {exc}"))


class _Worker:
    def __init__(self) -> None:
        ctx = multiprocessing.get_context("spawn")
        parent_conn, child_conn = ctx.Pipe()
        self.proc = ctx.Process(target=_worker_main, args=(child_conn,), daemon=True)
        self.proc.start()
        child_conn.close()
        self.conn = parent_conn

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
    except Exception as exc:  # noqa: BLE001 - anything else means the worker is unwell
        shutdown_worker()
        raise BuildError(f"isolated scorer failed: {type(exc).__name__}: {exc}") from exc
