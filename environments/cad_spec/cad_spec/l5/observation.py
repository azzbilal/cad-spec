"""L5 observation map: a measured solid -> contract variables.

Design note, section 7 (docs/design/L5-region-graded-change-orders-v1.0.md),
with the implementation amendments (docs/design/L5-amendments.md).

The map answers one question: "what are L, W, T, n, D, mx, my, px, py of this
part?", and it gives one of four verdicts with the numbers:

  ok                the variables are measured and the part has no other face
  form_violation    the variables are measured, but the part has a feature
                    nobody asked for. Measurable does not mean acceptable.
  out_of_scope      a variable cannot be measured without guessing (a stepped
                    hole, a tilted hole, holes of different diameters). The
                    map refuses loudly instead of returning a wrong number.
  not_single_solid  zero or several solids: nothing to measure

Nothing is re-measured here. The numbers come from the strict measurement of
scorer 0.5.0 (measure(strict=True)) and the form verdict IS that scorer's R9
(rubric.form_verdict). Tolerances are imported from the scorer, never copied,
so the two cannot drift apart.

Position is not a contract variable in L5 v1: a plate moved off the origin
measures the same. Orientation is: L is read along X and W along Y, so a
plate turned 90 degrees about Z has L and W swapped.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..measure import FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
from ..rubric import SCORER_VERSION, TOLERANCES, form_verdict

# One source of truth: the validated scorer's own constants.
EPS_DIM_MM: float = TOLERANCES[SCORER_VERSION].eps  # slack when a predicate compares a dimension
EPS_FORM_MM: float = FORM_LINEAR_TOL                # two positions closer than this are the same position

# Two cylinders whose axes are closer than this are "at one hole position".
# It only decides what counts as a stepped hole; it is far below any hole size.
_SAME_AXIS_MM = 1e-3

OK = "ok"
FORM_VIOLATION = "form_violation"
OUT_OF_SCOPE = "out_of_scope"
NOT_SINGLE_SOLID = "not_single_solid"

Value = float | int | bool | None


@dataclass(frozen=True)
class Observation:
    """Contract variables of one part, with the verdict on how far to trust them.

    `values` holds L, W, T (bounding box), n (through holes along Z), D, mx,
    my, px, py, and the booleans rectangular, centered, symmetric. A variable
    that does not exist (D with no hole) is None. With `out_of_scope` only the
    variables measured before the refusal are present.
    """

    status: str
    reason: str = ""
    values: dict[str, Value] = field(default_factory=dict)
    centre: tuple[float, float, float] | None = None  # bounding-box centre, for information

    @property
    def measurable(self) -> bool:
        """Can the contract predicates be evaluated on `values`?"""
        return self.status in (OK, FORM_VIOLATION)


def _through(hole: Hole, m: Measurements) -> bool:
    """One uninterrupted, open cylinder from the bottom face to the top face."""
    return (hole.open and hole.segments == 1
            and abs(hole.z_min - m.z_min) <= EPS_FORM_MM and abs(hole.z_max - m.z_max) <= EPS_FORM_MM)


def _positions(holes: list[Hole]) -> list[list[Hole]]:
    """Cylinders grouped by axis position."""
    groups: list[list[Hole]] = []
    for hole in holes:
        for group in groups:
            if math.hypot(hole.x - group[0].x, hole.y - group[0].y) <= _SAME_AXIS_MM:
                group.append(hole)
                break
        else:
            groups.append([hole])
    return groups


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= EPS_FORM_MM


def observe(m: Measurements) -> Observation:
    """Map a STRICT measurement (measure(strict=True)) to contract variables."""
    if m.solid_count != 1:
        return Observation(NOT_SINGLE_SOLID, f"{m.solid_count} solids, exactly one is required")

    centre = ((m.x_min + m.x_max) / 2, (m.y_min + m.y_max) / 2, (m.z_min + m.z_max) / 2)
    values: dict[str, Value] = {"L": m.length, "W": m.width, "T": m.thickness}

    def refuse(reason: str) -> Observation:
        return Observation(OUT_OF_SCOPE, reason, dict(values), centre)

    # Scope: anything that would make a hole variable a guess.
    if m.off_axis_concave is None:
        raise ValueError("observe() needs a strict measurement: measure(solid, strict=True)")
    if m.off_axis_bores or m.off_axis_concave:
        return refuse("a hole whose axis is not parallel to Z")
    groups = _positions(m.holes)
    if any(len(group) > 1 for group in groups):
        return refuse("two or more coaxial cylinders at one hole position (counterbore or stepped hole)")
    through = [group[0] for group in groups if _through(group[0], m)]
    values["n"] = len(through)
    if through and max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_FORM_MM:
        return refuse("through holes of different diameters: D is not one number")

    if through:
        xs, ys = sorted(h.x for h in through), sorted(h.y for h in through)
        values["D"] = through[0].diameter
        values["mx"] = min(min(h.x - m.x_min, m.x_max - h.x) for h in through)
        values["my"] = min(min(h.y - m.y_min, m.y_max - h.y) for h in through)
        values["px"], values["py"] = xs[-1] - xs[0], ys[-1] - ys[0]
        corners = [(x, y) for x in (xs[0], xs[-1]) for y in (ys[0], ys[-1])]
        values["rectangular"] = len(through) == 4 and all(
            sum(_same(h.x, x) and _same(h.y, y) for h in through) == 1 for x, y in corners)
        values["centered"] = (_same(sum(xs) / len(xs), centre[0]) and _same(sum(ys) / len(ys), centre[1]))
        values["symmetric"] = all(
            any(_same(o.x, 2 * centre[0] - h.x) and _same(o.y, h.y) for o in through)
            and any(_same(o.x, h.x) and _same(o.y, 2 * centre[1] - h.y) for o in through)
            for h in through)
    else:
        values.update({"D": None, "mx": None, "my": None, "px": None, "py": None,
                       "rectangular": False, "centered": False, "symmetric": False})

    # Form: measurable does not mean acceptable. Same verdict as scorer 0.5.0.
    if not (m.valid and m.shell_count == 1 and m.loose_count == 0):
        return Observation(FORM_VIOLATION, "not one clean, valid, single-shell solid", values, centre)
    passed, why = form_verdict(m)
    if not passed:
        return Observation(FORM_VIOLATION, why, values, centre)
    return Observation(OK, "", values, centre)


def observe_code(completion: str) -> Observation:
    """Build an answer in the sandbox, measure it strictly, and observe it.

    Raises BuildError when the code yields no part (gate G1's business) and
    ScorerUnavailableError when the scorer itself cannot run.
    """
    return observe(build_and_measure(completion, strict=True))
