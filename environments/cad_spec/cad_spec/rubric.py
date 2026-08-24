"""Scoring. This is the part that has to be right before anything else matters.

Design notes:
  * Every requirement is a named, independently checkable predicate. Partial
    credit is the fraction of requirements met, so a model that gets the plate
    right but the holes wrong scores better than one that gets nothing right,
    which is what gives RL a gradient to climb.
  * Gates run first and zero the score. They exist because dimensional checks
    alone are trivially gameable: a solid block with no holes passes R1-R3.
  * Each layer tests exactly one thing: gates test part identity, R1-R3 own
    overall dimensions, R4-R5 own the holes, R6 owns material consistency.
    R6 therefore compares against volume predicted from the MEASURED envelope
    minus NOMINAL bores - decoupled from dimension errors, so a thickness
    miss costs R3 alone rather than also torching R6.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .measure import BuildError, Hole, Measurements, build_and_measure
from .tasks import Spec

LINEAR_TOL = 0.5      # mm, on overall dimensions
HOLE_TOL = 0.2        # mm, on hole diameter
POSITION_TOL = 0.5    # mm, on hole centres
GATE_VOLUME_BAND = 0.12  # identity band: measured vs bbox-predicted volume
MATERIAL_TOL = 0.03   # fraction, R6: material vs envelope-minus-nominal-bores
DEPTH_TOL = 0.01      # mm, hole depth vs stock thickness


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


@dataclass
class Report:
    reward: float
    checks: list[Check]
    error: str | None = None
    parsed: bool = False

    @property
    def summary(self) -> str:
        if self.error:
            return f"BUILD FAILED: {self.error}"
        lines = [f"{'PASS' if c.passed else 'FAIL'}  {c.name:<22} {c.detail}" for c in self.checks]
        lines.append(f"reward = {self.reward:.3f}")
        return "\n".join(lines)


def _close(actual: float, target: float, tol: float) -> bool:
    return abs(actual - target) <= tol


def _gates(m: Measurements, spec: Spec) -> list[Check]:
    """Anti-hacking checks. Any failure zeroes the reward.

    Each exists because of a specific way to fake a passing part:
      single_solid         - four loose corner tabs would satisfy the bbox
      simple_through_holes - blind dimples measure like fastener holes from
                             above; counterbores/countersinks are coaxial
                             steps, i.e. a different fastener interface
      hole_count_sane      - swiss-cheesing the plate to hit a volume target
      is_plate             - a shell, hollow box, or ellipse extrusion with
                             the right bounding box

    is_plate compares measured volume against volume predicted from the
    MEASURED geometry within a wide identity band. It answers "is this even
    a prismatic plate with these bores", not "is this the right plate" -
    strict material conformance is requirement R6's job, at partial credit.
    """
    predicted = m.length * m.width * m.thickness
    predicted -= sum(math.pi * (h.diameter / 2) ** 2 * h.depth for h in m.holes)

    by_position: dict[tuple[float, float], list[Hole]] = {}
    for h in m.holes:
        by_position.setdefault((h.x, h.y), []).append(h)

    simple_through = bool(m.holes) and all(
        len({h.diameter for h in group}) == 1
        and _close(group[0].depth, m.thickness, DEPTH_TOL)
        for group in by_position.values()
    )

    return [
        Check(
            "gate:single_solid",
            m.solid_count == 1,
            f"{m.solid_count} solid(s)",
        ),
        Check(
            "gate:simple_through_holes",
            simple_through,
            f"{len(by_position)} position(s), diameters "
            f"{sorted(set(h.diameter for h in m.holes))}, depths "
            f"{sorted(set(round(h.depth, 2) for h in m.holes))} vs {m.thickness} mm stock",
        ),
        # Gross over-drilling is degenerate, not "nearly right". The band is
        # wide enough that an honest miscount (3 or 6 holes) keeps its credit.
        Check(
            "gate:hole_count_sane",
            m.hole_count <= 3 * spec.hole_count,
            f"{m.hole_count} bore(s), degenerate above {3 * spec.hole_count}",
        ),
        Check(
            "gate:is_plate",
            predicted > 0 and _close(m.volume, predicted, GATE_VOLUME_BAND * predicted),
            f"{m.volume:.1f} vs {predicted:.1f} mm3 predicted from measurement",
        ),
    ]


def _requirements(m: Measurements, spec: Spec) -> list[Check]:
    checks = [
        Check("R1:length", _close(m.length, spec.length, LINEAR_TOL),
              f"{m.length} vs {spec.length} mm"),
        Check("R2:width", _close(m.width, spec.width, LINEAR_TOL),
              f"{m.width} vs {spec.width} mm"),
        Check("R3:thickness", _close(m.thickness, spec.thickness, LINEAR_TOL),
              f"{m.thickness} vs {spec.thickness} mm"),
        Check("R4a:hole_count", m.hole_count == spec.hole_count,
              f"{m.hole_count} vs {spec.hole_count}"),
    ]

    diameters = [h.diameter for h in m.holes]
    checks.append(Check(
        "R4b:hole_diameter",
        bool(diameters) and all(_close(d, spec.hole_diameter, HOLE_TOL) for d in diameters),
        f"{sorted(set(round(d, 2) for d in diameters))} vs {spec.hole_diameter} mm",
    ))

    expected = {
        (round(sx * spec.pitch_x / 2, 2), round(sy * spec.pitch_y / 2, 2))
        for sx in (-1, 1) for sy in (-1, 1)
    }
    matched = 0
    for hx, hy in expected:
        if any(math.dist((h.x, h.y), (hx, hy)) <= POSITION_TOL for h in m.holes):
            matched += 1
    checks.append(Check(
        "R5:hole_pattern",
        matched == len(expected),
        f"{matched}/{len(expected)} positions matched",
    ))

    # Material consistency, isolated from dimension errors: what SHOULD this
    # envelope weigh once the nominal bores are cut? Extra features (pockets,
    # bosses) and missing material show up here at partial credit, not zero.
    expected_material = m.length * m.width * m.thickness
    expected_material -= spec.hole_count * math.pi * (spec.hole_diameter / 2) ** 2 * m.thickness
    checks.append(Check(
        "R6:material",
        expected_material > 0 and _close(m.volume, expected_material, MATERIAL_TOL * expected_material),
        f"{m.volume:.1f} vs {expected_material:.1f} mm3 for this envelope",
    ))

    return checks


def score(completion: str, spec: Spec) -> Report:
    try:
        m = build_and_measure(completion)
    except BuildError as exc:
        return Report(reward=0.0, checks=[], error=str(exc), parsed=False)

    gates = _gates(m, spec)
    reqs = _requirements(m, spec)
    checks = gates + reqs

    if not all(g.passed for g in gates):
        return Report(reward=0.0, checks=checks, parsed=True)

    reward = sum(1 for c in reqs if c.passed) / len(reqs)
    return Report(reward=round(reward, 4), checks=checks, parsed=True)
