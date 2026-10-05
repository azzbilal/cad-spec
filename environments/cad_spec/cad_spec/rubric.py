"""Scoring. This is the part that has to be right before anything else matters.

Design notes:
  * Every requirement is a named, independently checkable predicate. Partial
    credit is the fraction of requirements met, so a model that gets the plate
    right but the holes wrong scores better than one that gets nothing right,
    which is what gives RL a gradient to climb.
  * Gates run first and zero the score. They exist because dimensional checks
    alone are trivially gameable: a solid block with no holes passes R1-R3.
  * Each layer tests exactly one thing: gates test part identity, R1-R3 own
    overall dimensions, R4-R5 own the holes, R6 owns material consistency,
    R7 owns hole-to-edge margins, R8 owns the Z datum. R6 therefore compares against volume
    predicted from the MEASURED envelope minus NOMINAL bores - decoupled from
    dimension errors, so a thickness miss costs R3 alone rather than also
    torching R6. "Material" means volume consistency only: not alloy,
    strength, fit, or manufacturability.
  * Datums, stated so nobody has to guess: R5 references hole centres to
    the ORIGIN in X and Y (the prompt fixes the plate centred on it), R7
    references them to the part's own EDGES, and R8 references the plate's
    mid-plane to Z = 0. A plate slid off its holes fails R7; a part moved in
    X or Y fails R5; a part moved in Z fails R8. Before 0.3.0 only sizes
    were checked, which are translation-invariant, and a plate shifted 2 mm
    against nominal holes scored 1.0; before 0.4.0 Z was unchecked.
  * Rotations are not normalised: the prompt fixes the axes, so a part
    turned 90 degrees is a different part and loses the checks it breaks.
  * Scorer 0.5.0 states a strict contract: the part is one rectangular plate
    with exactly four through holes and NOTHING ELSE. 0.4.0 gave full credit
    to a saved answer with four extra notches through its edges (external
    audit, 3 October 2026), because R6 tolerates 3% of missing material. R9
    checks the FORM of the part: every face must lie on one of the six planes
    of the part's own envelope or on one of its recognised bores. A second
    audit (5 October 2026) showed that a volume comparison alone cannot do
    this job: shallow pockets and bosses hide inside any band, and tiny
    features under any volume threshold. The volume comparison stays as a
    cruder second look. Tolerances drop from 0.5 mm to 0.1 mm, compared on
    unrounded measurements: specs sit on a 0.5 mm grid and hole centres on a
    0.25 mm grid, so 0.5 mm accepted an error of a whole grid step. The hole
    pattern is matched one to one.
  * Versions live side by side. `score(..., version="0.4.0")` reproduces every
    result recorded under 0.4.0 exactly; recorded verdicts are never rescored
    under a newer scorer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .measure import SHAPE_BAND_MM, BuildError, Hole, Measurements, build_and_measure
from .tasks import Spec


@dataclass(frozen=True)
class Tolerances:
    linear: float     # mm, on overall dimensions (R1 to R3)
    hole: float       # mm, on hole diameter (R4b)
    position: float   # mm, on hole centres (R5)
    margin: float     # mm, hole centre to nearest edge (R7)
    datum: float      # mm, plate mid-plane to Z = 0 (R8)


# One entry per scorer version that can still be asked for. An entry is never
# edited: a change that can move a score is a new version.
TOLERANCES: dict[str, Tolerances] = {
    "0.4.0": Tolerances(linear=0.5, hole=0.2, position=0.5, margin=0.5, datum=0.5),
    "0.5.0": Tolerances(linear=0.1, hole=0.1, position=0.1, margin=0.1, datum=0.1),
}

# Bump on ANY change that can move a score. Recorded in every results file so
# numbers from different scorer revisions are never silently compared.
SCORER_VERSION = "0.5.0"
SUPPORTED_VERSIONS = tuple(TOLERANCES)

# The current version's tolerances, under their historical names.
LINEAR_TOL = TOLERANCES[SCORER_VERSION].linear
HOLE_TOL = TOLERANCES[SCORER_VERSION].hole
POSITION_TOL = TOLERANCES[SCORER_VERSION].position
MARGIN_TOL = TOLERANCES[SCORER_VERSION].margin
DATUM_TOL = TOLERANCES[SCORER_VERSION].datum
GATE_VOLUME_BAND = 0.12  # identity band: measured vs bbox-predicted volume
MATERIAL_TOL = 0.03   # fraction, R6: material vs envelope-minus-nominal-bores
DEPTH_TOL = 0.01      # mm, hole depth vs stock thickness
# R9 (0.5.0), second look only: largest volume of extra or of missing material
# outside a band of SHAPE_BAND_MM around the ideal part. The form check
# (measure._surface_conformance) is what decides R9; this bound alone would
# accept thin or tiny features, which is why it is never used alone.
SHAPE_VOLUME_TOL = 1e-3  # mm3
# Numerical slack on every tolerance comparison. Tolerances are INCLUSIVE:
# 6.7 is inside 6.5 +/- 0.2, but abs(6.7 - 6.5) is 0.20000000000000018 in
# binary floating point, and 0.3.x failed it. 1e-6 mm is far below any
# engineering meaning and far above float noise at these magnitudes.
NUM_EPS = 1e-6


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
    return abs(actual - target) <= tol + NUM_EPS


def _gates(m: Measurements, spec: Spec) -> list[Check]:
    """Anti-hacking checks. Any failure zeroes the reward.

    Each exists because of a specific way to fake a passing part:
      single_solid         - four loose corner tabs would satisfy the bbox
      clean_solid          - a valid solid bounded by exactly one shell, with
                             no loose faces, edges or vertices: an enclosed
                             cavity (a second shell) or stray geometry changes
                             the part without moving the volume check (0.4.0)
      simple_through_holes - blind dimples measure like fastener holes from
                             above; counterbores/countersinks are coaxial
                             steps, i.e. a different fastener interface; and
                             since 0.4.0 the passage must be OPEN (a rod
                             along the axis meets no material), so a hole
                             stopping microns short of the far face fails
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

    # Through = one uninterrupted wall spanning the stock's actual bottom and
    # top faces (datums), not "the tallest face is as tall as the plate".
    simple_through = bool(m.holes) and all(
        len({h.diameter for h in group}) == 1
        and group[0].segments == 1
        and _close(group[0].z_min, m.z_min, DEPTH_TOL)
        and _close(group[0].z_max, m.z_max, DEPTH_TOL)
        and all(h.open for h in group)
        for group in by_position.values()
    )

    return [
        Check(
            "gate:single_solid",
            m.solid_count == 1,
            f"{m.solid_count} solid(s)",
        ),
        Check(
            "gate:clean_solid",
            m.valid and m.shell_count == m.solid_count and m.loose_count == 0,
            f"valid={m.valid}, {m.shell_count} shell(s) for {m.solid_count} solid(s), "
            f"{m.loose_count} loose sub-shape(s)",
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


def _one_to_one(expected: list[tuple[float, float]], holes: list[Hole], tol: float) -> int:
    """Largest number of expected positions matched to DISTINCT holes within tol."""
    near = [[i for i, h in enumerate(holes) if math.dist((h.x, h.y), e) <= tol + NUM_EPS] for e in expected]
    owner: dict[int, int] = {}  # hole index -> expected position it is matched to

    def augment(k: int, seen: set[int]) -> bool:
        """Give position k a hole, moving earlier positions to other holes if needed."""
        for i in near[k]:
            if i in seen:
                continue
            seen.add(i)
            if i not in owner or augment(owner[i], seen):
                owner[i] = k
                return True
        return False

    return sum(augment(k, set()) for k in range(len(near)))


def _requirements(m: Measurements, spec: Spec, version: str) -> list[Check]:
    tol = TOLERANCES[version]
    strict = version != "0.4.0"
    checks = [
        Check("R1:length", _close(m.length, spec.length, tol.linear),
              f"{m.length} vs {spec.length} mm"),
        Check("R2:width", _close(m.width, spec.width, tol.linear),
              f"{m.width} vs {spec.width} mm"),
        Check("R3:thickness", _close(m.thickness, spec.thickness, tol.linear),
              f"{m.thickness} vs {spec.thickness} mm"),
        Check("R4a:hole_count", m.hole_count == spec.hole_count,
              f"{m.hole_count} vs {spec.hole_count}"),
    ]

    diameters = [h.diameter for h in m.holes]
    checks.append(Check(
        "R4b:hole_diameter",
        bool(diameters) and all(_close(d, spec.hole_diameter, tol.hole) for d in diameters),
        f"{sorted(set(round(d, 2) for d in diameters))} vs {spec.hole_diameter} mm",
    ))

    expected = {
        (round(sx * spec.pitch_x / 2, 2), round(sy * spec.pitch_y / 2, 2))
        for sx in (-1, 1) for sy in (-1, 1)
    }
    if strict:  # each measured hole may satisfy one expected position only
        matched = _one_to_one(sorted(expected), m.holes, tol.position)
    else:
        matched = 0
        for hx, hy in expected:
            if any(math.dist((h.x, h.y), (hx, hy)) <= tol.position + NUM_EPS for h in m.holes):
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

    # R7: hole centre to its nearest X edge and nearest Y edge, measured from
    # the part's actual envelope. Owns placement relative to the stock; R5
    # owns placement relative to the origin datum.
    worst = 0.0
    for h in m.holes:
        dx = min(h.x - m.x_min, m.x_max - h.x)
        dy = min(h.y - m.y_min, m.y_max - h.y)
        worst = max(worst, abs(dx - spec.edge_margin), abs(dy - spec.edge_margin))
    checks.append(Check(
        "R7:edge_margin",
        bool(m.holes) and worst <= tol.margin + NUM_EPS,
        f"worst deviation {worst:.2f} mm from {spec.edge_margin} mm margin"
        if m.holes else "no bores to measure",
    ))

    # R8: the Z datum. The prompt fixes the plate centred on the origin with
    # its thickness along Z. R5 and R7 together pin X and Y; nothing pinned Z
    # before 0.4.0, and a correct part floating 100 mm up scored 1.0.
    z_mid = (m.z_min + m.z_max) / 2
    checks.append(Check(
        "R8:z_datum",
        abs(z_mid) <= tol.datum + NUM_EPS,
        f"mid-plane at Z = {z_mid:.3f} mm (nominal 0)",
    ))

    if strict:
        # R9: the strict contract. A plate with bores is bounded only by the
        # six planes of its own envelope and by its recognised bores. Any
        # other face is something nobody asked for: a notch, slot, pocket,
        # boss, cross-bore, chamfer, fillet, draft, a lug in a bore, a plate
        # turned off its axes. Because the envelope and the bores are the
        # MEASURED ones, a wrong dimension does not fail R9: it fails for one
        # reason only. The volume residual is a cruder second look at the
        # same question and can only add a failure, never remove one.
        extra, missing = m.extra_volume, m.missing_volume
        if m.surface_conformance is None or extra is None or missing is None:
            checks.append(Check("R9:no_other_features", False,  # could not check: never a pass
                                f"the form of the part could not be checked ({m.shape_error or 'no detail'})"))
        else:
            residual_ok = extra <= SHAPE_VOLUME_TOL and missing <= SHAPE_VOLUME_TOL
            checks.append(Check(
                "R9:no_other_features",
                m.surface_conformance and residual_ok,
                ("every face lies on the envelope or on a bore" if m.surface_conformance
                 else "a face lies neither on the envelope nor on a recognised bore")
                + f"; {extra:.3f} mm3 extra, {missing:.3f} mm3 missing outside a {SHAPE_BAND_MM} mm band",
            ))

    return checks


def score(completion: str, spec: Spec, version: str = SCORER_VERSION) -> Report:
    """Score one answer. `version` selects a recorded scorer; the default is the current one."""
    if version not in TOLERANCES:
        raise ValueError(f"unknown scorer version {version!r}; supported: {', '.join(SUPPORTED_VERSIONS)}")
    try:
        # The legacy scorer gets the legacy measurement: nothing added, nothing
        # slower, values rounded as they were when its results were recorded.
        m = build_and_measure(completion, strict=version != "0.4.0")
    except BuildError as exc:
        return Report(reward=0.0, checks=[], error=str(exc), parsed=False)

    gates = _gates(m, spec)
    reqs = _requirements(m, spec, version)
    checks = gates + reqs

    if not all(g.passed for g in gates):
        return Report(reward=0.0, checks=checks, parsed=True)

    reward = sum(1 for c in reqs if c.passed) / len(reqs)
    return Report(reward=round(reward, 4), checks=checks, parsed=True)
