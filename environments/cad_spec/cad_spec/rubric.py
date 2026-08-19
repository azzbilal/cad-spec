"""Scoring. This is the part that has to be right before anything else matters.

Design notes:
  * Every requirement is a named, independently checkable predicate. Partial
    credit is the fraction of requirements met, so a model that gets the plate
    right but the holes wrong scores better than one that gets nothing right,
    which is what gives RL a gradient to climb.
  * Gates run first and zero the score. They exist because dimensional checks
    alone are trivially gameable: a solid block with no holes passes R1-R3.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .measure import BuildError, Measurements, build_and_measure
from .tasks import Spec


LINEAR_TOL = 0.5   # mm, on overall dimensions
HOLE_TOL = 0.2     # mm, on hole diameter
POSITION_TOL = 0.5 # mm, on hole centres
VOLUME_TOL = 0.02  # fraction, on total material volume


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
      single_solid  - four loose corner tabs would satisfy the bounding box
      has_holes     - a plain block passes every dimensional check
      is_plate      - the part is actually a prismatic plate with these bores,
                      not a shell, a hollow box, or some other shape that
                      happens to share the bounding box

    is_plate compares measured volume against volume predicted from the
    MEASURED geometry, not from the spec. That distinction matters: gating on
    the spec means any dimensional error also zeroes the score, which removes
    the partial credit RL needs to climb.
    """
    predicted = m.length * m.width * m.thickness
    predicted -= sum(math.pi * (h.diameter / 2) ** 2 * h.depth for h in m.holes)

    return [
        Check(
            "gate:single_solid",
            m.solid_count == 1,
            f"{m.solid_count} solid(s)",
        ),
        # Through-ness is a gate, not a requirement. A blind dimple is not a
        # fastener hole, so a plate full of them is not a partially correct
        # answer; it is a different part that happens to measure well.
        Check(
            "gate:through_holes",
            bool(m.holes) and all(_close(h.depth, m.thickness, 0.01) for h in m.holes),
            f"{m.hole_count} bore(s), depths {sorted(set(round(h.depth, 2) for h in m.holes))}"
            f" vs {m.thickness} mm stock",
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
            predicted > 0 and _close(m.volume, predicted, VOLUME_TOL * predicted),
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

    return checks


def score(completion: str, spec: Spec) -> Report:
    try:
        m = build_and_measure(completion)
    except BuildError as exc:
        return Report(reward=0.0, checks=[], error=str(exc))

    gates = _gates(m, spec)
    reqs = _requirements(m, spec)
    checks = gates + reqs

    if not all(g.passed for g in gates):
        return Report(reward=0.0, checks=checks)

    reward = sum(1 for c in reqs if c.passed) / len(reqs)
    return Report(reward=round(reward, 4), checks=checks)
