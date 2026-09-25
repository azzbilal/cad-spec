"""Build a CadQuery script and extract the measurements a spec can be checked against.

This module is deliberately dumb about specs. It answers one question:
"given a piece of code, what geometry actually came out?"
Everything spec-related lives in rubric.py.

Hole detection uses exact surface geometry, not bounding-box guesses. Two
independent discriminators decide whether a cylindrical face is a drilled
bore, because each alone admits a false-positive class the other exists to
catch:

  * A membership probe placed just inside the surface asks whether material
    continues immediately inward. It rejects CONVEX cylinders - external
    rounds, bosses, the outer wall of a shell - but cannot reject concave
    partial cylinders such as inner corner fillets: those genuinely have
    material on their outside, which is precisely what the probe defines a
    bore to be.
  * An area completeness check asks whether the coaxial group closes into a
    full cylinder (pi*d*h over its Z extent). It rejects concave PARTIAL
    cylinders - an inner corner fillet is a quarter arc covering ~25% of
    its full cylinder - but cannot reject convex geometry: a boss is a
    complete cylinder.

Coaxial faces are grouped by axis position, so counterbores and seam-split
cylinders are handled explicitly rather than by luck.

Known limitation, stated plainly because it shapes scores: the completeness
check drops any bore that does not close into a full cylinder (since 0.3.0
such groups are REPORTED in Measurements.partial_bores, but still not scored) -
a hole intersecting another hole, breaking out through a side wall, or
opening into a pocket is returned as fewer holes, with nothing said. The
scoring consequence is asymmetric: a model that places a hole too close to
an edge is scored as having MISSED that hole rather than misplaced it,
losing hole count as well as position and pattern - two-plus requirements
for one mistake. The check is kept anyway because partial cylinders are
exactly how corner fillets masquerade as bores; anyone comparing model
scores should know the asymmetry is there.

Trust boundary (0.4.0): model code never hands the scorer a Python object.
The untrusted side (build_brep) executes the code, collects the OCCT shapes
bound to `result` and serialises them to BREP, a plain-text geometry format.
The trusted side (load_brep + measure) parses those bytes with the kernel
and measures what they describe. Before 0.4.0 the scorer called methods on
whatever object `result` was, so a class that answered BoundingBox() and
Volume() with nominal numbers scored 1.0 while its real geometry was a 1 mm
cube; and in fork mode the result came back as a pickle, which can execute
code when loaded. Neither path exists any more.

Execution safety: model code never runs in the caller's process. On POSIX
a warm worker forks a disposable, rlimited, env-scrubbed child per rollout
(CAD_SPEC_SANDBOX=fork) and measures the returned BREP itself; on Windows
one persistent worker runs rollouts in fresh temp directories
(CAD_SPEC_SANDBOX=reuse). CAD_SPEC_EXEC_TIMEOUT bounds each build (seconds,
default 10). CAD_SPEC_INPROC=1 disables isolation for debugging. This is
containment, not a security boundary; see SECURITY.md for what each mode
does and does not guarantee.

Windows note: the spawn-based worker requires callers to follow the standard
multiprocessing contract - entry scripts must guard top-level code with
if __name__ == "__main__":
"""

from __future__ import annotations

import atexit
import contextlib
import math
import multiprocessing
import os
import re
import tempfile
import textwrap
from dataclasses import dataclass, field
from typing import Any

# The newline after the fence is REQUIRED and not part of the capture: a bare
# \s* swallows it plus the first code line's leading indentation, which orphans
# every following line and raises IndentationError on otherwise valid code.
CODE_BLOCK = re.compile(r"```(?:python)?[ \t]*\r?\n(.*?)```", re.DOTALL)

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
# Minimum coverage (dimensionless) for a rejected concave group to be REPORTED
# as a partial bore. Below it the group is treated as fillet-like noise.
PARTIAL_REPORT_MIN = 0.30
# Gap (mm) under which two Z intervals of one coaxial group are merged. Faces
# split by a symmetric cutter meet exactly at the split plane; the kernel
# tolerance is far below this.
INTERVAL_MERGE_TOL = 1e-4
# Open-passage probe: a rod of this fraction of the bore radius, run along the
# axis past both faces of the stock, must intersect less than this volume
# (mm3) of material. A 0.00001 mm membrane on a 6.5 mm bore leaves ~8e-5 mm3.
OPEN_PROBE_RADIUS_FRACTION = 0.5
OPEN_VOLUME_TOL = 1e-6
# Largest BREP a rollout may hand back (bytes). The plates here are 5-50 kB.
MAX_BREP_BYTES = 8 << 20


class ScorerUnavailableError(RuntimeError):
    """The scorer itself cannot run: CadQuery missing, worker cannot start.

    Deliberately NOT a BuildError. A BuildError means "the model's code did
    not produce a part" and is scored as a model failure; this means "we
    could not look", and must never become a score. score() does not catch
    it, so every script stops with this message instead of recording zeros.
    (September 2026: a session without the virtualenv active scored every
    answer of a llama run as unbuildable before this existed.)
    """


def require_cadquery() -> str:
    """Return the CadQuery version, or raise ScorerUnavailableError with the fix."""
    import sys

    try:
        import cadquery
    except ImportError as exc:
        raise ScorerUnavailableError(
            f"CadQuery is not importable from {sys.executable} ({exc}). Activate the environment "
            "that has it installed (e.g. `source environments/cad_spec/.venv/Scripts/activate` on "
            "Windows Git Bash, `source .venv/bin/activate` elsewhere) and rerun."
        ) from exc
    return str(getattr(cadquery, "__version__", "unknown"))


class BuildError(Exception):
    """Model code did not produce a usable solid."""


@dataclass
class Hole:
    """A closed, Z-parallel bore: one diameter at one axis position.

    `depth` is the TOTAL axial length the bore wall covers, computed as the
    union of every coaxial face's Z interval (0.3.0 fix: it used to be the
    tallest single face, so a bore cut by a symmetric cutter that left two
    stacked 3 mm faces in a 6 mm plate read as 3 mm deep). `z_min`/`z_max`
    bound that union; `segments` > 1 means the wall is interrupted along Z.
    """

    diameter: float
    x: float
    y: float
    depth: float
    z_min: float = 0.0
    z_max: float = 0.0
    segments: int = 1
    # True when a rod along the bore axis meets no material anywhere through
    # the stock. Endpoint coordinates alone cannot tell a through hole from a
    # blind one that stops a few microns short, leaving a membrane (0.3.x
    # scored a 0.005 mm membrane as "through").
    open: bool = True


@dataclass
class PartialBore:
    """A concave Z-parallel cylinder group that does NOT close into a full bore.

    Diagnostic only, never scored. Corner fillets land here at ~0.25
    coverage; a hole breaking out through a side wall or intersecting
    another feature lands here at intermediate coverage. Reporting them
    turns the detector's old silent drop into a visible, auditable one.
    """

    diameter: float
    x: float
    y: float
    coverage: float  # covered fraction of the full cylinder over its merged Z span


@dataclass
class Measurements:
    length: float          # bbox X
    width: float           # bbox Y
    thickness: float       # bbox Z
    volume: float          # mm^3
    solid_count: int       # >1 means disconnected pieces
    holes: list[Hole] = field(default_factory=list)
    # Envelope datums (0.3.0). Sizes alone are translation-invariant, which
    # let a plate shifted off its hole pattern keep full credit; edge-margin
    # and datum checks need the actual coordinates.
    x_min: float = 0.0
    x_max: float = 0.0
    y_min: float = 0.0
    y_max: float = 0.0
    z_min: float = 0.0
    z_max: float = 0.0
    partial_bores: list[PartialBore] = field(default_factory=list)
    # Topology (0.4.0). A plate is one solid bounded by ONE shell: a second
    # shell is an enclosed cavity. Loose faces, edges or vertices outside the
    # solids are extra geometry that no volume check can see.
    shell_count: int = 1
    loose_count: int = 0
    valid: bool = True

    @property
    def hole_count(self) -> int:
        return len(self.holes)

    @property
    def centre(self) -> tuple[float, float, float]:
        return (
            round((self.x_min + self.x_max) / 2, 4),
            round((self.y_min + self.y_max) / 2, 4),
            round((self.z_min + self.z_max) / 2, 4),
        )


def extract_code(completion: str) -> str:
    """Pull python out of a model response. Falls back to the raw text.

    Indentation is load-bearing, so the block is dedented BEFORE it is
    stripped: a uniformly indented fenced block (a model echoing an indented
    template) dedents to runnable module-level code, while a block already at
    column zero is left untouched. Stripping first would delete the first
    line's indentation, destroy the common prefix, and turn dedent into a
    no-op.
    """
    blocks = CODE_BLOCK.findall(completion)
    if blocks:
        return textwrap.dedent(max(blocks, key=len)).strip()
    return textwrap.dedent(completion).strip()


def _raised_in(exc: BaseException) -> str:
    """Where an exception from model code was raised: "model code",
    "cadquery: <function>" (CadQuery, its OCP kernel bindings or its
    multimethod dispatch; the innermost CadQuery function named) or "other
    library". Failure analysis only; it never affects a score. Argument
    errors and missing attributes are raised at the caller, so this alone
    does not prove who is at fault; the message says the rest.
    """
    tb = exc.__traceback__
    last, cq_func, origin_is_cq = None, None, False
    while tb is not None:
        code = tb.tb_frame.f_code
        last = code.co_filename
        if any(part in last.replace("\\", "/") for part in ("/cadquery/", "/OCP", "/multimethod")):
            if "/cadquery/" in last.replace("\\", "/"):
                cq_func = getattr(code, "co_qualname", code.co_name)
            origin_is_cq = True
        else:
            origin_is_cq = False
        tb = tb.tb_next
    if last is None or last == "<model>":
        return "model code"
    if origin_is_cq:
        return f"cadquery: {cq_func}" if cq_func else "cadquery"
    return "other library"


def _exec_result(code: str) -> Any:
    """Execute model code and return the object bound to `result`. Untrusted."""
    import cadquery as cq

    namespace: dict[str, Any] = {"cq": cq, "cadquery": cq, "math": math}
    # Executing model code IS the task; containment happens in the worker.
    try:
        exec(compile(code, "<model>", "exec"), namespace)
    except Exception as exc:
        # The tag goes FIRST: error text is capped (_MAX_ERROR_CHARS) where it
        # leaves the sandbox, and a tag at the end was cut off long messages
        # (label check, seed 20260927). Only the scorer writes this prefix, so
        # a model cannot forge it through its own exception message.
        raise BuildError(f"execution failed [raised in {_raised_in(exc)}]: {type(exc).__name__}: {exc}") from exc
    obj = namespace.get("result")
    if obj is None:
        raise BuildError("code did not define `result`")
    return obj


def _result_topods(obj: Any) -> Any:
    """The OCCT shapes `result` holds, as one TopoDS_Shape. Untrusted side.

    Only the kernel handle (`.wrapped`, a TopoDS_Shape) of each shape is
    used; no method of the model's object is trusted to describe geometry.
    A Workplane contributes every shape on its stack (non-shape stack items
    such as vectors carry no geometry and are ignored); anything else must
    itself wrap a TopoDS_Shape.
    """
    import cadquery as cq
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound, TopoDS_Shape

    items = obj.vals() if isinstance(obj, cq.Workplane) else [obj]
    shapes = []
    for item in items:
        wrapped = getattr(item, "wrapped", None)
        if isinstance(wrapped, TopoDS_Shape) and not wrapped.IsNull():
            shapes.append(wrapped)
    if not shapes:
        raise BuildError(f"`result` holds no CadQuery shape (got {type(obj).__name__})")
    if len(shapes) == 1:
        return shapes[0]
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for shape in shapes:
        builder.Add(compound, shape)
    return compound


def build_brep(code: str) -> bytes:
    """Execute model code; return its geometry as BREP bytes. Untrusted side."""
    import shutil

    from OCP.BRepTools import BRepTools

    shape = _result_topods(_exec_result(code))
    workdir = tempfile.mkdtemp(prefix="cad-spec-brep-")
    try:
        path = os.path.join(workdir, "result.brep")
        if not BRepTools.Write_s(shape, path):
            raise BuildError("result geometry could not be serialised")
        with open(path, "rb") as fh:
            data = fh.read(MAX_BREP_BYTES + 1)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if len(data) > MAX_BREP_BYTES:
        raise BuildError("result geometry is too large")
    return data


def load_brep(data: bytes) -> Any:
    """Parse BREP bytes into a CadQuery shape. Trusted side: bytes are data."""
    import shutil

    import cadquery as cq
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape

    if not data or len(data) > MAX_BREP_BYTES:
        raise BuildError("result geometry is empty or too large")
    workdir = tempfile.mkdtemp(prefix="cad-spec-load-")
    try:
        path = os.path.join(workdir, "result.brep")
        with open(path, "wb") as fh:
            fh.write(data)
        shape = TopoDS_Shape()
        ok = BRepTools.Read_s(shape, path, BRep_Builder())
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if not ok or shape.IsNull():
        raise BuildError("result geometry could not be read")
    return cq.Shape.cast(shape)


def build(code: str) -> Any:
    """Exec model code and return its geometry as a trusted CadQuery shape.

    Goes through the same BREP round-trip as production scoring, so tests
    measure exactly what the scorer measures. Not a security boundary: it
    runs the code in the calling process.
    """
    return load_brep(build_brep(code))


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


def _merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Union of closed Z intervals, merging touching or overlapping ones."""
    merged: list[list[float]] = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1] + INTERVAL_MERGE_TOL:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    return [(lo, hi) for lo, hi in merged]


def _classify_cylinders(solid: Any) -> tuple[list[Hole], list[PartialBore]]:
    """Closed internal bores, plus rejected concave groups as diagnostics.

    Two independent discriminators, because hollow geometry defeats either
    alone:

    1. Membership probed JUST INSIDE the cylindrical surface: material there
       means the face is convex - an external round, a boss, or the outer
       wall of a shell - and the face is rejected. Probes deeper toward the
       axis ask "is the axis buried in material", which is the wrong
       question on hollow parts and answers "no" for phantom reasons.
    2. Completeness: a coaxial group must cover AREA_COMPLETENESS_MIN of the
       full cylinder pi*d*L, where L is the length of the UNION of its faces'
       Z intervals. Concave corner fillets pass discriminator 1 honestly yet
       are quarter arcs; only closed-cylinder area separates them.

    Depth is the union length, not the tallest face: a bore whose wall is
    split into stacked faces (symmetric cutter, two-sided cut) is the same
    bore, and the modelling operation must not change its score.
    """
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_State

    classifier = BRepClass3d_SolidClassifier(solid.wrapped)

    # position -> diameter -> (summed face area mm^2, [Z intervals])
    features: dict[tuple[float, float], dict[float, tuple[list[float], list[tuple[float, float]]]]] = {}
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
        area_acc, intervals = features.setdefault(key, {}).setdefault(diameter, ([0.0], []))
        area_acc[0] += face.Area()
        intervals.append((fbb.zmin, fbb.zmax))

    holes: list[Hole] = []
    partial: list[PartialBore] = []
    for (x, y), diameters in sorted(features.items()):
        for diameter, (area_acc, intervals) in sorted(diameters.items()):
            spans = _merge_intervals(intervals)
            covered = sum(hi - lo for lo, hi in spans)
            if covered <= 0:
                continue
            coverage = area_acc[0] / (math.pi * diameter * covered)
            if coverage < AREA_COMPLETENESS_MIN:
                if coverage >= PARTIAL_REPORT_MIN:
                    partial.append(PartialBore(diameter, round(x, 4), round(y, 4), round(coverage, 4)))
                continue  # partial arc (fillet, breakout), not a closed bore
            holes.append(Hole(
                diameter=diameter,
                x=round(x, 4),
                y=round(y, 4),
                depth=round(covered, 4),
                z_min=round(spans[0][0], 4),
                z_max=round(spans[-1][1], 4),
                segments=len(spans),
            ))
    return holes, partial


def _extract_holes(solid: Any) -> list[Hole]:
    """Closed internal bores only (kept for callers of the 0.2 API)."""
    return _classify_cylinders(solid)[0]


def _count(shape: Any, kind: Any, avoid: Any = None) -> int:
    from OCP.TopExp import TopExp_Explorer

    explorer = TopExp_Explorer(shape, kind) if avoid is None else TopExp_Explorer(shape, kind, avoid)
    n = 0
    while explorer.More():
        n += 1
        explorer.Next()
    return n


def _bore_is_open(solid: Any, hole: Hole, z_min: float, z_max: float) -> bool:
    """Does a rod along the bore axis, through the whole stock, meet no material?"""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepGProp import BRepGProp
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.GProp import GProp_GProps

    radius = hole.diameter / 2 * OPEN_PROBE_RADIUS_FRACTION
    axis = gp_Ax2(gp_Pnt(hole.x, hole.y, z_min - 1.0), gp_Dir(0, 0, 1))
    rod = BRepPrimAPI_MakeCylinder(axis, radius, (z_max - z_min) + 2.0).Shape()
    common = BRepAlgoAPI_Common(solid.wrapped, rod)
    common.Build()
    if not common.IsDone():
        return False
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(common.Shape(), props)
    return abs(props.Mass()) < OPEN_VOLUME_TOL


def measure(solid: Any) -> Measurements:
    """Extract features from a trusted shape (see load_brep)."""
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX

    try:
        bb = solid.BoundingBox()
        volume = solid.Volume()
        topo = solid.wrapped
        solid_count = _count(topo, TopAbs_SOLID)
    except Exception as exc:
        raise BuildError(f"shape could not be measured: {exc}") from exc

    if solid_count == 0:
        raise BuildError("result contains no solid")
    if volume <= 0:
        raise BuildError("shape has zero or negative volume")

    loose = (
        _count(topo, TopAbs_SHELL, TopAbs_SOLID)
        + _count(topo, TopAbs_FACE, TopAbs_SHELL)
        + _count(topo, TopAbs_EDGE, TopAbs_FACE)
        + _count(topo, TopAbs_VERTEX, TopAbs_EDGE)
    )
    holes, partial = _classify_cylinders(solid)
    for h in holes:
        h.open = _bore_is_open(solid, h, bb.zmin, bb.zmax)
    return Measurements(
        length=round(bb.xlen, 4),
        width=round(bb.ylen, 4),
        thickness=round(bb.zlen, 4),
        volume=round(volume, 4),
        solid_count=solid_count,
        holes=holes,
        x_min=round(bb.xmin, 4),
        x_max=round(bb.xmax, 4),
        y_min=round(bb.ymin, 4),
        y_max=round(bb.ymax, 4),
        z_min=round(bb.zmin, 4),
        z_max=round(bb.zmax, 4),
        partial_bores=partial,
        shell_count=_count(topo, TopAbs_SHELL),
        loose_count=loose,
        valid=bool(BRepCheck_Analyzer(topo).IsValid()),
    )


def _measure_code(code: str) -> Measurements:
    """Build and measure in THIS process (inproc and reuse modes)."""
    return measure(load_brep(build_brep(code)))


# --- isolated execution ------------------------------------------------------
#
# One persistent worker process owns the cadquery import and serves build
# requests over a pipe. Per-call timeouts kill hung rollouts; crashes respawn
# the worker on the next call. Spawn context keeps Windows and CI identical.
#
# Sandbox modes (CAD_SPEC_SANDBOX), see SECURITY.md for the threat model:
#
#   fork   (default on POSIX) the warm worker forks a FRESH child per rollout.
#          The child gets its own temp directory (deleted afterwards), its
#          own process group (killed whole afterwards, descendants included),
#          a scrubbed environment (no API keys or tokens inherited), every
#          inherited file descriptor closed except its result pipe, stdout
#          and stderr sent to /dev/null, and rlimits on CPU time, file size,
#          open files and (Linux only) address space. It is best-effort moved
#          into new user + network namespaces. The child sends back ONLY a
#          status byte plus either BREP geometry bytes or a short error text;
#          the worker parses the geometry with the kernel and measures it.
#          No object from the child is ever unpickled. Nothing a rollout does
#          to Python state survives into the next rollout, because the child
#          exits.
#   reuse  (default on Windows, which has no fork) one persistent process runs
#          every rollout, each in a fresh temp directory. State CAN leak
#          between rollouts. Trusted debugging and Windows dev only.
#
# Neither mode is a hard security boundary against deliberately malicious
# code: the child still runs as your user and can read files your user can
# read. For untrusted output at scale, run the scorer inside the provided
# container (Dockerfile) or Prime's sandbox.


def _exec_timeout() -> float:
    return float(os.environ.get("CAD_SPEC_EXEC_TIMEOUT", "10"))


def _mem_limit_mb() -> int:
    return int(os.environ.get("CAD_SPEC_MEM_MB", "2048"))


def _sandbox_mode() -> str:
    default = "fork" if hasattr(os, "fork") else "reuse"
    mode = os.environ.get("CAD_SPEC_SANDBOX", default)
    if mode == "fork" and not hasattr(os, "fork"):
        return "reuse"
    return mode if mode in ("fork", "reuse") else default


# Fixed window for a fresh worker to spawn, import the kernel and announce
# readiness. Deliberately independent of CAD_SPEC_EXEC_TIMEOUT.
_STARTUP_TIMEOUT = 120.0
# Extra seconds the parent allows beyond the model budget for fork, pickling
# and cleanup before it declares the whole worker wedged.
_GRACE = 10.0
# Largest payload a child may send back (bytes): one status byte + BREP.
_MAX_RESULT_BYTES = MAX_BREP_BYTES + 1
# Longest error text a child may send back (characters). Error text is the
# only free-form data that crosses from model code to the scorer; it is
# length-capped and stripped of control characters, and treated as data.
_MAX_ERROR_CHARS = 300
# Environment variables a rollout child keeps. Everything else (tokens, keys,
# proxy credentials) is dropped.
_ENV_KEEP = ("PATH", "LANG", "LC_ALL", "PYTHONHASHSEED", "SYSTEMROOT", "TMP", "TEMP")


def _inproc_requested() -> bool:
    return os.environ.get("CAD_SPEC_INPROC", "") == "1"


def _try_netns() -> bool:
    """Best-effort: detach from the network via unprivileged namespaces."""
    unshare = getattr(os, "unshare", None)
    flags = getattr(os, "CLONE_NEWUSER", 0) | getattr(os, "CLONE_NEWNET", 0)
    if unshare is None or not flags:
        return False
    try:
        unshare(flags)
        return True
    except OSError:
        return False


def _vm_size_bytes() -> int:
    try:
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmSize:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        pass
    return 0


def _clean_error(text: str) -> str:
    text = "".join(ch if ch.isprintable() else " " for ch in text)
    return text[:_MAX_ERROR_CHARS]


def _harden_child(workdir: str, budget_s: float, mem_mb: int, keep_fd: int) -> None:
    """Runs in the forked child only, before model code.

    Every argument is captured by the trusted parent BEFORE the environment
    is scrubbed (0.3.x read CAD_SPEC_MEM_MB after scrubbing, so the default
    2048 always applied).
    """
    import resource

    os.setpgid(0, 0)  # own process group: the parent kills it whole
    _try_netns()
    os.chdir(workdir)
    keep = {k: v for k, v in os.environ.items() if k in _ENV_KEEP}
    os.environ.clear()
    os.environ.update(keep)
    os.environ["HOME"] = workdir
    os.environ["TMPDIR"] = workdir

    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    # Close everything inherited (the worker's control pipe included) except
    # the result pipe. The child must not be able to talk to the worker on
    # any channel but the one the worker parses as plain bytes.
    for lo, hi in ((3, keep_fd), (keep_fd + 1, 4096)):
        if lo < hi:
            os.closerange(lo, hi)

    budget = max(1, math.ceil(budget_s))
    limits = {
        "RLIMIT_CPU": (budget + 1, budget + 2),
        "RLIMIT_FSIZE": (MAX_BREP_BYTES * 2, MAX_BREP_BYTES * 2),
        "RLIMIT_NOFILE": (64, 64),
    }
    vm = _vm_size_bytes()  # Linux /proc only; macOS gets no RLIMIT_AS
    if vm:
        cap = vm + mem_mb * (1 << 20)
        limits["RLIMIT_AS"] = (cap, cap)
    for name, value in limits.items():
        res = getattr(resource, name, None)
        if res is not None:
            with contextlib.suppress(ValueError, OSError):
                resource.setrlimit(res, value)


def _kill_group(pid: int) -> None:
    """SIGKILL the rollout's process group (the child set pgid = its pid)."""
    import signal

    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pid, signal.SIGKILL)


def _run_forked(code: str, budget: float, mem_mb: int) -> tuple[str, Any]:
    """Run one rollout in a disposable forked child. Returns (status, payload).

    The child replies with b"O" + BREP bytes or b"E" + UTF-8 error text. The
    worker (this process, trusted) parses and measures the BREP itself.
    """
    import select
    import shutil
    import signal
    import time

    workdir = tempfile.mkdtemp(prefix="cad-spec-rollout-")
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # --- child: untrusted from here on -------------------------
        os.close(read_fd)
        try:
            _harden_child(workdir, budget, mem_mb, write_fd)
            try:
                out = b"O" + build_brep(code)
            except BuildError as exc:
                out = b"E" + _clean_error(str(exc)).encode()
            except MemoryError:
                out = b"E" + b"model code exceeded the memory budget"
            except BaseException as exc:
                out = b"E" + _clean_error(f"worker fault: {type(exc).__name__}: {exc}").encode()
            with os.fdopen(write_fd, "wb") as fh:
                fh.write(out)
        finally:
            os._exit(0)

    # --- parent: the warm worker, trusted ------------------------------------
    # Completion is "the child exited", not "the pipe closed": a descendant
    # the model code started inherits the pipe and would otherwise hold it
    # open until the deadline, turning a finished rollout into a timeout.
    os.close(write_fd)
    chunks: list[bytes] = []
    total = 0
    timed_out = oversized = False
    status: int | None = None
    deadline = time.monotonic() + budget

    def _read_available(wait: float) -> bool:
        """Read what is ready within `wait` s. False once the pipe hits EOF."""
        nonlocal total, oversized
        ready, _, _ = select.select([read_fd], [], [], wait)
        if not ready:
            return True
        chunk = os.read(read_fd, 65536)
        if not chunk:
            return False
        total += len(chunk)
        if total > _MAX_RESULT_BYTES:
            oversized = True
            return False
        chunks.append(chunk)
        return True

    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                break
            if not _read_available(min(remaining, 0.05)) or oversized:
                break
            reaped, st = os.waitpid(pid, os.WNOHANG)
            if reaped:
                status = st
                # The child is gone; take whatever it wrote, without waiting
                # for descendants that may still hold the pipe open.
                while _read_available(0.0) and not oversized:
                    ready, _, _ = select.select([read_fd], [], [], 0.0)
                    if not ready:
                        break
                break
    finally:
        os.close(read_fd)
        _kill_group(pid)  # always: kills descendants the child left running
        if status is None:
            _, status = os.waitpid(pid, 0)
        shutil.rmtree(workdir, ignore_errors=True)

    if timed_out:
        return ("error", f"model code exceeded {budget:g}s execution budget")
    if oversized:
        return ("error", "result geometry is too large")
    data = b"".join(chunks)
    if not data:
        if os.WIFSIGNALED(status) and os.WTERMSIG(status) == signal.SIGXCPU:
            return ("error", f"model code exceeded {budget:g}s execution budget")
        return ("error", "rollout process exited without a result")
    tag, body = data[:1], data[1:]
    if tag == b"E":
        return ("error", _clean_error(body.decode("utf-8", errors="replace")))
    if tag != b"O":
        return ("error", "rollout process returned a malformed result")
    try:
        return ("ok", measure(load_brep(body)))
    except BuildError as exc:
        return ("error", str(exc))
    except Exception as exc:
        return ("error", f"result geometry could not be measured: {type(exc).__name__}")


def _run_reused(code: str, budget: float, mem_mb: int) -> tuple[str, Any]:
    """Run one rollout in this (persistent) process, in a fresh temp dir.

    `budget` is enforced by the parent, which kills this whole process;
    `mem_mb` cannot be enforced without fork and is ignored.
    """
    del budget, mem_mb
    import shutil

    workdir = tempfile.mkdtemp(prefix="cad-spec-rollout-")
    previous = os.getcwd()
    try:
        os.chdir(workdir)
        return ("ok", _measure_code(code))
    except BuildError as exc:
        return ("error", _clean_error(str(exc)))
    except Exception as exc:
        return ("error", _clean_error(f"worker fault: {type(exc).__name__}: {exc}"))
    finally:
        os.chdir(previous)
        shutil.rmtree(workdir, ignore_errors=True)


def _worker_main(conn: Any, mode: str) -> None:
    os.chdir(tempfile.mkdtemp(prefix="cad-spec-worker-"))
    try:
        require_cadquery()  # warm the kernel BEFORE announcing readiness
    except ScorerUnavailableError as exc:
        conn.send(("unavailable", str(exc)))
        return
    conn.send(("ready", None))
    run = _run_forked if mode == "fork" else _run_reused
    while True:
        try:
            kind, payload = conn.recv()
        except (EOFError, KeyboardInterrupt):
            return
        if kind == "stop":
            conn.send(("ok", None))
            return
        code, budget, mem_mb = payload
        try:
            conn.send(run(code, budget, mem_mb))
        except Exception as exc:  # report faults before dying
            conn.send(("error", f"worker fault: {type(exc).__name__}: {exc}"))


class _Worker:
    def __init__(self) -> None:
        self.mode = _sandbox_mode()
        ctx = multiprocessing.get_context("spawn")
        parent_conn, child_conn = ctx.Pipe()
        self.proc = ctx.Process(target=_worker_main, args=(child_conn, self.mode), daemon=True)
        self.proc.start()
        child_conn.close()
        self.conn = parent_conn
        # Interpreter spawn + kernel warm-up wait on a generous fixed window,
        # NOT the per-build budget: CAD_SPEC_EXEC_TIMEOUT must measure model
        # code only, so a tight budget stays usable right after a respawn.
        if not self.conn.poll(_STARTUP_TIMEOUT):
            self.kill()
            raise ScorerUnavailableError(f"scorer worker did not start within {_STARTUP_TIMEOUT:g}s")
        try:
            status, _payload = self.conn.recv()
        except EOFError as exc:
            raise ScorerUnavailableError("scorer worker died during startup") from exc
        if status == "unavailable":
            self.kill()
            raise ScorerUnavailableError(str(_payload))
        if status != "ready":
            raise ScorerUnavailableError("scorer worker sent an unexpected startup message")

    @property
    def alive(self) -> bool:
        return self.proc.is_alive()

    def call(self, code: str) -> Measurements:
        try:
            self.conn.send(("measure", (code, _exec_timeout(), _mem_limit_mb())))
        except (BrokenPipeError, OSError) as exc:
            raise BuildError(f"scorer pipe broke: {exc}") from exc
        # In fork mode the worker enforces the budget itself and survives;
        # the outer window is a backstop for a wedged worker. In reuse mode
        # the outer window IS the budget, and a timeout kills the worker.
        window = _exec_timeout() + (_GRACE if self.mode == "fork" else 0.0)
        if not self.conn.poll(window):
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
        if self.proc.is_alive():  # terminate ignored: force it
            self.proc.kill()
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


def sandbox_info() -> dict[str, Any]:
    """What isolation the NEXT rollout will get. Recorded in results metadata."""
    if _inproc_requested():
        return {"mode": "inproc", "isolated": False}
    mode = _sandbox_mode()
    info: dict[str, Any] = {
        "mode": mode,
        "exec_timeout_s": _exec_timeout(),
        "per_rollout_process": mode == "fork",
        "state_isolated": mode == "fork",
        "env_scrubbed": mode == "fork",
        # Where geometry is measured: from BREP bytes in the trusted worker
        # (fork) or in the same process that ran the model code (reuse).
        "measured_in": "trusted worker" if mode == "fork" else "rollout process",
    }
    if mode == "fork":
        # Requested limits. Address-space limits apply on Linux only; the
        # namespace (no-network) step is best effort and not verified here.
        info["mem_limit_mb_requested"] = _mem_limit_mb()
    return info


def build_and_measure(completion: str) -> Measurements:
    """Extract code, run it isolated, measure the result.

    Raises BuildError when the model's code does not yield a part (a model
    failure), ScorerUnavailableError when the scorer cannot run at all (never a
    score).
    """
    code = extract_code(completion)
    if _inproc_requested():
        require_cadquery()
        return _measure_code(code)
    try:
        return _get_worker().call(code)
    except (BuildError, ScorerUnavailableError):
        raise
    except Exception as exc:  # anything else means the worker is unwell
        shutdown_worker()
        raise BuildError(f"isolated scorer failed: {type(exc).__name__}: {exc}") from exc
