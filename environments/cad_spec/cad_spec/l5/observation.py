"""L5 observation map: a measured solid -> contract variables.

Design note, section 7 (docs/design/L5-region-graded-change-orders-v1.0.md),
with the implementation amendments (docs/design/L5-amendments.md).

The map answers one question: "what are L, W, T, n, D, mx, my, px, py of this
part?", and it gives one of four verdicts with the numbers:

  ok                the variables are measured and the part has no other face
  form_violation    the part has a feature nobody asked for. The numbers are
                    reported for diagnosis only: with a boss, a spline face
                    or loose geometry they may not describe the plate.
  out_of_scope      a variable cannot be measured without guessing (a stepped
                    hole, a tilted hole, holes of different diameters, a
                    feature too small to classify, one hole split across
                    the measurement's grouping or whose faces disagree on
                    its axis). The map refuses loudly
                    instead of returning a wrong number.
  not_single_solid  zero or several solids: nothing to measure

Only `ok` lets a contract be evaluated. `ok` is not compliance: it says the
numbers can be trusted, and the contract (including the family rules that a
hole lies inside the plate and that holes do not overlap) is the next gate.

Nothing is re-measured here. The numbers come from the strict measurement of
scorer 0.5.0 (measure(strict=True)) and the form verdict IS that scorer's R9
(rubric.form_verdict). Tolerances are imported from scorer 0.5.0 by name,
never copied and never following a later default.

Position is not a contract variable in L5 v1: a plate moved off the origin
measures the same. Orientation is: L is read along X and W along Y, so a
plate turned 90 degrees about Z has L and W swapped.

px and py are the extent of the hole centres along X and Y. For the family's
four-corner pattern that is the pitch; for any other pattern it is only the
extent, and `rectangular` says which case applies.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from ..measure import COAXIAL_DP, FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
from ..rubric import TOLERANCES, form_verdict

OBSERVATION_VERSION = "2"  # 2: straight-line centered; split, spread and all-face D checks (fourth review)
SCORER_BASIS = "0.5.0"  # the validated scorer this map is built on; pinned, not "the current one"

# One source of truth: that scorer's own constants.
EPS_DIM_MM: float = TOLERANCES[SCORER_BASIS].eps  # two dimensions closer than this are the same dimension
EPS_FORM_MM: float = FORM_LINEAR_TOL              # two positions closer than this are the same position

# Supported size. The inward probe that tells a hole from a boss cannot
# classify a cylinder much smaller than this, so the map refuses instead of
# missing it. The generator's smallest hole is 3 mm.
MIN_CYLINDER_DIAMETER_MM = 0.01

# The strict measurement groups cylinder faces into holes by axis position
# rounded to COAXIAL_DP decimals and by diameter rounded to 4 decimals. The 4
# is a literal in measure._classify_cylinders (no name to import), so it is
# restated here. The gate cases review_hole_split_across_* pin it, and check
# that the measurement really splits those parts.
_DIAMETER_KEY_DP = 4

# The faces of one hole must agree on its axis to half the dimension slack, so
# that an extent combining two holes (px, py) stays within the slack.
SPREAD_LIMIT_MM: float = EPS_DIM_MM / 2

OK = "ok"
FORM_VIOLATION = "form_violation"
OUT_OF_SCOPE = "out_of_scope"
NOT_SINGLE_SOLID = "not_single_solid"

Value = float | int | bool | None
_NO_VALUES: Mapping[str, Value] = MappingProxyType({})


@dataclass(frozen=True)
class Observation:
    """Contract variables of one part, with the verdict on how far to trust them.

    `values` (read-only) holds L, W, T (bounding box), n (through holes along
    Z), D, mx, my, px, py, and the booleans rectangular, centered, symmetric.
    `centered` compares the straight-line distance from the mean hole centre
    to the bounding-box centre with the form tolerance. `rectangular` and
    `symmetric` match positions coordinate by coordinate at that tolerance.
    A variable that does not exist (D with no hole) is None. With
    `out_of_scope` only the variables measured before the refusal are present.
    """

    status: str
    reason: str = ""
    values: Mapping[str, Value] = field(default_factory=lambda: _NO_VALUES)
    centre: tuple[float, float, float] | None = None  # bounding-box centre, for information

    @property
    def ok(self) -> bool:
        """May a contract be evaluated on `values`? Only then."""
        return self.status == OK


def _through(hole: Hole, m: Measurements) -> bool:
    """One uninterrupted, open cylinder from the bottom face to the top face."""
    return (hole.open and hole.segments == 1
            and abs(hole.z_min - m.z_min) <= EPS_FORM_MM and abs(hole.z_max - m.z_max) <= EPS_FORM_MM)


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= EPS_FORM_MM


def _same_cylinder(a: tuple[float, float, float], b: tuple[float, float, float]) -> bool:
    """Two concave Z faces of one cylinder: axes within the form tolerance, diameters within the slack."""
    (x, y, d), (u, v, e) = a, b
    return math.hypot(x - u, y - v) <= EPS_FORM_MM and abs(d - e) <= EPS_DIM_MM


def _group_key(x: float, y: float, d: float) -> tuple[float, float, float]:
    """The key under which the strict measurement groups a face into a hole."""
    return (round(x, COAXIAL_DP), round(y, COAXIAL_DP), round(d, _DIAMETER_KEY_DP))


def _split(axes: list[tuple[float, float, float]]) -> bool:
    """Is one cylinder split across two hole groups of the measurement?

    Two faces of one cylinder (by the rule of _same_cylinder) can lie on
    either side of a rounding key: axes 8e-10 mm apart around x = 20.0005, or
    diameters 8e-10 mm apart around 10.00005. The measurement then makes two
    half-depth holes, neither of which is a through hole, and n would be one
    short under `ok`. The map refuses instead.
    """
    return any(_same_cylinder(a, b) and _group_key(*a) != _group_key(*b)
               for i, a in enumerate(axes) for b in axes[i + 1:])


def _axis_spread(axes: list[tuple[float, float, float]]) -> bool:
    """Do two faces of one cylinder have axes more than half the dimension slack apart?

    The measurement reads a hole's axis from one of its faces, whichever comes
    first. With faces 8e-8 mm apart at a corner, mx was 14.99999992 or 15.0
    depending on the order of the cuts. The faces of one hole must agree on
    its axis to half the dimension slack, 0.5e-9 mm, or the map refuses. Under
    `ok` each hole's position is then right to 0.5e-9 mm, and px or py, which
    combine two holes, to 1e-9 mm: every variable is within the slack
    whichever face is read.
    """
    return any(_same_cylinder(a, b) and math.hypot(a[0] - b[0], a[1] - b[1]) > SPREAD_LIMIT_MM
               for i, a in enumerate(axes) for b in axes[i + 1:])


def _through_face_diameters(through: list[Hole], axes: list[tuple[float, float, float]]) -> list[float]:
    """The diameter of every concave Z face that belongs to a through hole.

    A hole reports the diameter of one of its faces, and the faces of one hole
    may differ by up to the dimension slack. Comparing one face per hole made
    the "one D" verdict depend on the order of the cuts, and could report `ok`
    with a D 1.8e-9 mm from another hole's face. Every face is compared instead.

    Valid only after _nested and _split have passed: only then is "the same
    cylinder as a hole's own face" the same as "a face of that hole's group".
    The caller also adds each hole's own diameter, as a guard.
    """
    return [a[2] for a in axes if any(_same_cylinder((h.x, h.y, h.diameter), a) for h in through)]


def _nested(axes: list[tuple[float, float, float]]) -> bool:
    """Do two DIFFERENT concave Z cylinders share one hole position?

    Two faces of the same cylinder (same axis, same diameter) are one
    cylinder. Otherwise, when the axis of one lies inside the other, they form
    a counterbore, a stepped hole or an offset step: D is not one number.
    Two separate holes that merely overlap are not nested (a form matter).
    """
    for i, (x, y, d) in enumerate(axes):
        for u, v, e in axes[i + 1:]:
            if _same_cylinder((x, y, d), (u, v, e)):
                continue
            if math.hypot(x - u, y - v) < max(d, e) / 2:
                return True
    return False


def observe(m: Measurements) -> Observation:
    """Map a STRICT measurement (measure(strict=True)) to contract variables."""
    if not m.strict:
        raise ValueError("observe() needs a strict measurement: measure(solid, strict=True)")
    if m.solid_count != 1:
        return Observation(NOT_SINGLE_SOLID, f"{m.solid_count} solids, exactly one is required")

    centre = ((m.x_min + m.x_max) / 2, (m.y_min + m.y_max) / 2, (m.z_min + m.z_max) / 2)
    values: dict[str, Value] = {"L": m.length, "W": m.width, "T": m.thickness}

    def done(status: str, reason: str = "") -> Observation:
        return Observation(status, reason, MappingProxyType(dict(values)), centre)

    # Scope: anything that would make a hole variable a guess. Refusals come
    # before any hole variable is written.
    if m.scope_error or m.off_axis_concave is None or m.scope_axes is None:
        return done(OUT_OF_SCOPE, f"the scope checks could not be completed ({m.scope_error or 'no detail'})")
    if m.min_cylinder_diameter is not None and m.min_cylinder_diameter < MIN_CYLINDER_DIAMETER_MM:
        return done(OUT_OF_SCOPE, f"a cylindrical face under {MIN_CYLINDER_DIAMETER_MM} mm in diameter: "
                                  "below the supported size")
    if m.off_axis_bores or m.off_axis_concave:
        return done(OUT_OF_SCOPE, "a hole whose axis is not parallel to Z")
    if _nested(m.scope_axes):
        return done(OUT_OF_SCOPE, "two different cylinders at one hole position "
                                  "(counterbore, stepped or offset hole)")
    if _split(m.scope_axes):
        return done(OUT_OF_SCOPE, "one cylinder split across two hole groups of the measurement "
                                  "(faces within the tolerances, on either side of a rounding key)")
    if _axis_spread(m.scope_axes):
        return done(OUT_OF_SCOPE, f"the faces of one hole have axes more than {SPREAD_LIMIT_MM:g} mm apart: "
                                  "its position is not one number")
    through = [h for h in m.holes if _through(h, m)]
    values["n"] = len(through)
    diameters = _through_face_diameters(through, m.scope_axes) + [h.diameter for h in through]
    if diameters and max(diameters) - min(diameters) > EPS_DIM_MM:
        return done(OUT_OF_SCOPE, "through holes of different diameters: D is not one number")

    if through:
        xs, ys = sorted(h.x for h in through), sorted(h.y for h in through)
        values["D"] = through[0].diameter
        values["mx"] = min(min(h.x - m.x_min, m.x_max - h.x) for h in through)
        values["my"] = min(min(h.y - m.y_min, m.y_max - h.y) for h in through)
        values["px"], values["py"] = xs[-1] - xs[0], ys[-1] - ys[0]
        corners = [(x, y) for x in (xs[0], xs[-1]) for y in (ys[0], ys[-1])]
        values["rectangular"] = len(through) == 4 and all(
            sum(_same(h.x, x) and _same(h.y, y) for h in through) == 1 for x, y in corners)
        # Straight-line distance from the mean hole centre to the bounding-box
        # centre, as for the tilt limit: a 2D offset is judged by its length.
        values["centered"] = math.hypot(sum(xs) / len(xs) - centre[0], sum(ys) / len(ys) - centre[1]) <= EPS_FORM_MM
        values["symmetric"] = all(
            any(_same(o.x, 2 * centre[0] - h.x) and _same(o.y, h.y) for o in through)
            and any(_same(o.x, h.x) and _same(o.y, 2 * centre[1] - h.y) for o in through)
            for h in through)
    else:
        values.update({"D": None, "mx": None, "my": None, "px": None, "py": None,
                       "rectangular": False, "centered": False, "symmetric": False})

    # Form: measurable does not mean acceptable. Same verdict as scorer 0.5.0.
    if not (m.valid and m.shell_count == 1 and m.loose_count == 0):
        return done(FORM_VIOLATION, "not one clean, valid, single-shell solid")
    passed, why = form_verdict(m)
    return done(OK) if passed else done(FORM_VIOLATION, why)


def observe_code(completion: str) -> Observation:
    """Build an answer in the sandbox, measure it strictly, and observe it.

    Raises BuildError when the code yields no part (gate G1's business) and
    ScorerUnavailableError when the scorer itself cannot run.
    """
    return observe(build_and_measure(completion, strict=True))
