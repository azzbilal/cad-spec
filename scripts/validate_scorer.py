# ruff: noqa: E402, N812
"""Validate the scorer against labelled one-change mutants.

Ground truth here does NOT come from the scorer. Every mutant is generated
from an explicit geometry description (plate size and placement, a list of
holes with position, diameter and depth, optional corner fillets). An ORACLE
computes which gates and requirements that geometry should pass using only
those parameters and the published tolerances. The scorer, which sees only
the built B-rep, is then compared against the oracle.

Reported:
  false_full_credit  oracle says the part is wrong, scorer gives 1.0
  false_rejection    oracle says the part is right, scorer gives < 1.0
  exact_agreement    scorer's failed-check set == oracle's
  per-check          confusion counts for every gate and requirement

Mutants whose oracle outcome sits within BOUNDARY_GUARD of a tolerance edge
are marked ambiguous for that check and excluded from its comparison: at the
edge, float noise in the kernel decides, and that is not a scorer defect.

The contract (suite 0.5.0). A correct part is one rectangular plate with
exactly four through holes and nothing else: no extra cut, notch, slot,
pocket, cross-bore, chamfer or fillet, and no material left inside a bore.
Tolerances are 0.1 mm on every dimension, position, margin, datum and
diameter. They are stated HERE, not read from the scorer under test, so the
same suite can be run against an older scorer (CAD_SPEC_PKG) to measure what
a release fixed. Specs sit on a 0.5 mm grid and hole centres on a 0.25 mm
grid, so the families include errors of exactly one grid step.

Run:
    python scripts/validate_scorer.py            # 30 eval specs, ~2-3 min
    python scripts/validate_scorer.py --specs 5  # quick
Writes results/scorer-validation-<scorer version>.{json,md}.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# CAD_SPEC_PKG points the validator at another scorer checkout, e.g. an older
# release extracted with `git archive`, to measure what a change fixed.
sys.path.insert(0, os.environ.get("CAD_SPEC_PKG", str(ROOT / "environments" / "cad_spec")))

from cad_spec import rubric as R
from cad_spec.tasks import Spec, make_splits

SCORER_VERSION = getattr(R, "SCORER_VERSION", "0.2.0")
SUITE_VERSION = "0.5.0"
# The contract, independent of the scorer under test.
LINEAR_TOL = HOLE_TOL = POSITION_TOL = MARGIN_TOL = DATUM_TOL = 0.1   # mm
MATERIAL_TOL = 0.03       # fraction, R6
GATE_VOLUME_BAND = 0.12   # fraction, gate:is_plate
WITHIN, BEYOND = 0.5, 1.5  # multiples of a tolerance used by the within/beyond families
EXACT = 1e-9  # a deviation this close to a tolerance is AT the limit: inside, by definition
BOUNDARY_GUARD = 0.02  # mm for linear checks, fraction-of-band for R6/is_plate

GATES = ("gate:single_solid", "gate:clean_solid", "gate:simple_through_holes", "gate:hole_count_sane",
         "gate:is_plate")
REQS = ("R1:length", "R2:width", "R3:thickness", "R4a:hole_count", "R4b:hole_diameter",
        "R5:hole_pattern", "R6:material", "R7:edge_margin", "R8:z_datum", "R9:no_other_features")


@dataclass(frozen=True)
class HoleG:
    x: float
    y: float
    d: float
    through: bool = True
    depth: float = 0.0  # blind depth from the top face when not through


@dataclass(frozen=True)
class Geometry:
    L: float
    W: float
    T: float
    ox: float = 0.0          # plate centre offset
    oy: float = 0.0
    oz: float = 0.0
    cavity: bool = False     # a small sealed void at the centre of the plate
    holes: tuple[HoleG, ...] = ()
    fillet: float = 0.0      # vertical corner fillet radius
    # hole_top | cutter_both | cutter_split | sketch_extrude | rect_vertices | off_centre
    method: str = "hole_top"
    # Unrequested features, each a wrong part under the strict contract:
    # edge_notch | slot | pocket | cross_bore | clipped_corner | chamfer_top | fillet_top | bore_burr
    extras: tuple[str, ...] = ()
    fillet_or_clip: float = 0.0  # leg of the clipped corner


@dataclass
class Mutant:
    spec_id: str
    name: str
    family: str
    geometry: Geometry
    oracle_fails: set[str] = field(default_factory=set)
    ambiguous: set[str] = field(default_factory=set)
    note: str = ""


def nominal(spec: Spec) -> Geometry:
    px, py = spec.pitch_x / 2, spec.pitch_y / 2
    holes = tuple(HoleG(sx * px, sy * py, spec.hole_diameter) for sx in (-1, 1) for sy in (-1, 1))
    return Geometry(spec.length, spec.width, spec.thickness, holes=holes)


OFF_CENTRE = (10.0, -7.0, 3.0)  # where the off_centre method builds the part before moving it back


def clip_leg(spec: Spec) -> float:
    """Size of a corner fillet or clipped corner that stays clear of the holes."""
    return round(min(2.0, spec.edge_margin - spec.hole_diameter / 2 - 1.0), 1)


def to_code(g: Geometry) -> str:
    sx, sy, sz = OFF_CENTRE if g.method == "off_centre" else (0.0, 0.0, 0.0)
    cx, cy, cz = g.ox + sx, g.oy + sy, g.oz + sz
    lines = ["import cadquery as cq"]
    if g.method == "sketch_extrude":
        lines.append(f"plate = cq.Workplane('XY').rect({g.L}, {g.W}).extrude({g.T})"
                     f".translate(({cx}, {cy}, {cz - g.T / 2}))")
    else:
        lines.append(f"plate = cq.Workplane('XY').box({g.L}, {g.W}, {g.T}).translate(({cx}, {cy}, {cz}))")
    if g.fillet:
        lines.append(f"plate = plate.edges('|Z').fillet({g.fillet})")
    if "chamfer_top" in g.extras:
        lines.append("plate = plate.faces('>Z').edges().chamfer(0.3)")
    if "fillet_top" in g.extras:
        lines.append("plate = plate.faces('>Z').edges().fillet(0.3)")
    top, bot = cz + g.T / 2, cz - g.T / 2
    if g.method == "rect_vertices":  # only meaningful for the nominal, origin-centred pattern
        px = max(h.x for h in g.holes) - min(h.x for h in g.holes)
        py = max(h.y for h in g.holes) - min(h.y for h in g.holes)
        lines.append(f"plate = plate.faces('>Z').workplane().rect({px}, {py}, forConstruction=True)"
                     f".vertices().hole({g.holes[0].d})")
    for h in g.holes if g.method != "rect_vertices" else ():
        r = h.d / 2
        hx, hy = h.x + sx, h.y + sy
        if not h.through:
            z0, length = top - h.depth, h.depth
            lines.append(f"plate = plate.cut(cq.Workplane('XY').workplane(offset={z0}).center({hx}, {hy})"
                         f".circle({r}).extrude({length}))")
        elif g.method == "cutter_both":
            lines.append(f"plate = plate.cut(cq.Workplane('XY').center({hx}, {hy})"
                         f".circle({r}).extrude({g.T + 4}, both=True))")
        elif g.method == "cutter_split":  # two abutting cutters: top half and bottom half
            lines.append(f"plate = plate.cut(cq.Workplane('XY').center({hx}, {hy}).circle({r}).extrude({top + 2}))")
            lines.append(f"plate = plate.cut(cq.Workplane('XY').center({hx}, {hy}).circle({r}).extrude({bot - 2}))")
        elif g.method in ("hole_top", "sketch_extrude", "off_centre"):
            lines.append(f"plate = plate.faces('>Z').workplane().pushPoints([({hx}, {hy})]).hole({h.d})")
        else:
            raise ValueError(g.method)
    if g.cavity:  # 1.5 x 1.5 mm, 40% of the thickness: clear of any hole (web >= 2 mm)
        void = f"cq.Workplane('XY').box(1.5, 1.5, {0.4 * g.T}).translate(({cx}, {cy}, {cz}))"
        lines.append(f"plate = plate.cut({void})")
    through = f"extrude({g.T + 4}, both=True)"
    mid = f"cq.Workplane('XY').workplane(offset={cz})"
    if "edge_notch" in g.extras:  # a hole-sized cutter centred on the +Y edge: half of it breaks out
        r = g.holes[0].d / 2
        lines.append(f"plate = plate.cut({mid}.center({cx}, {cy + g.W / 2}).circle({r}).{through})")
    if "slot" in g.extras:  # 6 x 2 mm through slot at the plate centre
        lines.append(f"plate = plate.cut({mid}.center({cx}, {cy}).rect(6, 2).{through})")
    if "pocket" in g.extras:  # 4 x 4 mm blind pocket, 30% of the thickness, from the top face
        depth = round(0.3 * g.T, 4)
        lines.append(f"plate = plate.cut(cq.Workplane('XY').workplane(offset={top - depth})"
                     f".center({cx}, {cy}).rect(4, 4).extrude({depth}))")
    if "cross_bore" in g.extras:  # a bore along X through the mid-plane, between the hole rows
        rc = round(min(1.0, g.T / 4), 3)
        lines.append(f"plate = plate.cut(cq.Workplane('YZ').center({cy}, {cz}).circle({rc})"
                     f".extrude({g.L + 4}, both=True).translate(({cx}, 0, 0)))")
    if "clipped_corner" in g.extras:  # one vertical corner cut off at 45 degrees
        c = g.fillet_or_clip
        x1, y1 = cx + g.L / 2, cy + g.W / 2
        lines.append(f"plate = plate.cut({mid}.polyline([({x1 + 1}, {y1 + 1}), ({x1 - c}, {y1 + 1}), "
                     f"({x1 - c}, {y1}), ({x1}, {y1 - c}), ({x1 + 1}, {y1 - c})]).close().{through})")
    if "bore_burr" in g.extras:  # a small lug on the wall of the first bore, clear of its axis
        h = g.holes[0]
        lines.append(f"plate = plate.union(cq.Workplane('XY').box(0.6, 0.3, {round(0.2 * g.T, 4)})"
                     f".translate(({h.x + sx + h.d / 2}, {h.y + sy}, {cz})))")
    if g.method == "off_centre":
        lines.append(f"plate = plate.translate(({-sx}, {-sy}, {-sz}))")
    lines.append("result = plate")
    return "\n".join(lines) + "\n"


# --- oracle -------------------------------------------------------------------

def _edge(value: float, target: float, tol: float) -> tuple[bool, bool]:
    """(passes, ambiguous) for |value - target| <= tol, tolerance INCLUSIVE.

    Exactly at the limit is a pass and NOT ambiguous: the scorer must get
    exact decimal endpoints right (0.3.x failed 6.7 against 6.5 +/- 0.2).
    Only near-misses on either side are left to kernel noise.
    """
    dev = abs(value - target)
    if abs(dev - tol) <= EXACT:
        return True, False
    return dev <= tol, abs(dev - tol) < BOUNDARY_GUARD


def oracle(spec: Spec, g: Geometry) -> tuple[set[str], set[str]]:
    fails: set[str] = set()
    amb: set[str] = set()
    x0, x1 = g.ox - g.L / 2, g.ox + g.L / 2
    y0, y1 = g.oy - g.W / 2, g.oy + g.W / 2
    # Holes that close inside the stock. A hole cut past the edge is not a
    # bore an inspector could gauge; the literal-geometry view the scorer
    # also takes (see the LIMIT_breakout family and the report).
    inside = [h for h in g.holes if x0 + h.d / 2 < h.x < x1 - h.d / 2 and y0 + h.d / 2 < h.y < y1 - h.d / 2]
    # gates
    # Per-position rule: every bore is one plain diameter running through.
    # Different diameters at DIFFERENT positions are an R4b error, not a gate.
    if not inside or any(not h.through for h in inside):
        fails.add("gate:simple_through_holes")
    if len(inside) > 3 * spec.hole_count:
        fails.add("gate:hole_count_sane")
    if g.cavity:
        fails.add("gate:clean_solid")

    # requirements
    for name, value, target in (("R1:length", g.L, spec.length), ("R2:width", g.W, spec.width),
                                ("R3:thickness", g.T, spec.thickness)):
        ok, a = _edge(value, target, LINEAR_TOL)
        fails |= set() if ok else {name}
        amb |= {name} if a else set()
    if len(inside) != spec.hole_count:
        fails.add("R4a:hole_count")
    diam_ok = bool(inside)
    for h in inside:
        ok, a = _edge(h.d, spec.hole_diameter, HOLE_TOL)
        diam_ok &= ok
        amb |= {"R4b:hole_diameter"} if a else set()
    if not diam_ok:
        fails.add("R4b:hole_diameter")
    expected = [(sx * spec.pitch_x / 2, sy * spec.pitch_y / 2) for sx in (-1, 1) for sy in (-1, 1)]
    for ex, ey in expected:
        dists = [math.dist((h.x, h.y), (ex, ey)) for h in inside]
        best = min(dists, default=math.inf)
        if best > POSITION_TOL + EXACT:
            fails.add("R5:hole_pattern")
        elif abs(best - POSITION_TOL) <= EXACT:
            continue  # exactly at the limit: inside, and not ambiguous
        if abs(best - POSITION_TOL) < BOUNDARY_GUARD:
            amb.add("R5:hole_pattern")
    worst = 0.0
    for h in inside:
        dx = min(h.x - x0, x1 - h.x)
        dy = min(h.y - y0, y1 - h.y)
        worst = max(worst, abs(dx - spec.edge_margin), abs(dy - spec.edge_margin))
    if not inside or worst > MARGIN_TOL + EXACT:
        fails.add("R7:edge_margin")
    if inside and EXACT < abs(worst - MARGIN_TOL) < BOUNDARY_GUARD:
        amb.add("R7:edge_margin")

    ok, a = _edge(g.oz, 0.0, DATUM_TOL)
    if not ok:
        fails.add("R8:z_datum")
    if a:
        amb.add("R8:z_datum")

    fillet_loss = 4 * (g.fillet ** 2 - math.pi * g.fillet ** 2 / 4) * g.T
    cavity_loss = 1.5 * 1.5 * 0.4 * g.T if g.cavity else 0.0
    removed = sum(math.pi * (h.d / 2) ** 2 * (g.T if h.through else h.depth) for h in inside)
    volume = g.L * g.W * g.T - fillet_loss - removed - cavity_loss
    exp_mat = g.L * g.W * g.T - spec.hole_count * math.pi * (spec.hole_diameter / 2) ** 2 * g.T
    band = MATERIAL_TOL * exp_mat
    if abs(volume - exp_mat) > band:
        fails.add("R6:material")
    if abs(abs(volume - exp_mat) - band) < BOUNDARY_GUARD * band:
        amb.add("R6:material")

    predicted = g.L * g.W * g.T - removed  # is_plate sees measured bores only
    if abs(volume - predicted) > GATE_VOLUME_BAND * predicted:
        fails.add("gate:is_plate")

    # R9, the strict contract: the plate and its through bores, nothing else.
    # A blind bore leaves a plug of material where the bore should be; a hole
    # that breaks out through an edge removes material that is not a bore.
    breakout = [h for h in g.holes if h not in inside and (
        x0 - h.d / 2 < h.x < x1 + h.d / 2 and y0 - h.d / 2 < h.y < y1 + h.d / 2)]
    if g.fillet or g.cavity or g.extras or breakout or any(not h.through for h in inside):
        fails.add("R9:no_other_features")
    if g.extras or breakout:
        # The volume bookkeeping above does not model these features; their
        # effect on the two volume checks is not part of what is being tested.
        amb |= {"R6:material", "gate:is_plate"}
    return fails, amb


# --- mutant families ------------------------------------------------------------

def _shift_holes(g: Geometry, dx: float, dy: float, only: int | None = None) -> Geometry:
    holes = tuple(replace(h, x=h.x + dx, y=h.y + dy) if only is None or i == only else h
                  for i, h in enumerate(g.holes))
    return replace(g, holes=holes)


def mutants_for(spec: Spec) -> list[Mutant]:
    g0 = nominal(spec)
    d0 = spec.hole_diameter
    out: list[tuple[str, str, Geometry, str]] = [
        ("nominal", "benign", g0, ""),
        ("method_cutter_both", "benign", replace(g0, method="cutter_both"), "audit P0-2"),
        ("method_cutter_split", "benign", replace(g0, method="cutter_split"), "stacked faces"),
        ("method_sketch_extrude", "benign", replace(g0, method="sketch_extrude"), "extruded sketch, not a box"),
        ("method_rect_vertices", "benign", replace(g0, method="rect_vertices"), "rect().vertices().hole()"),
        ("method_off_centre", "benign", replace(g0, method="off_centre"), "built off-centre, then moved back"),
        ("holes_reverse_order", "benign", replace(g0, holes=tuple(reversed(g0.holes))), ""),
    ]

    def resized(attr: str, signed_delta: float) -> Geometry:
        """Change one dimension and move the holes with their edges, so margins stay nominal."""
        g = replace(g0, **{attr: getattr(g0, attr) + signed_delta})
        # Outward when the part grows, inward when it shrinks. (0.3.x used
        # copysign here, which drops the sign of the change.)
        if attr == "L":
            g = replace(g, holes=tuple(replace(h, x=h.x + (1 if h.x > 0 else -1) * signed_delta / 2)
                                       for h in g.holes))
        if attr == "W":
            g = replace(g, holes=tuple(replace(h, y=h.y + (1 if h.y > 0 else -1) * signed_delta / 2)
                                       for h in g.holes))
        return g

    steps = ((WITHIN * LINEAR_TOL, "within_tol"), (BEYOND * LINEAR_TOL, "beyond_tol"),
             (0.25, "grid_error"), (0.5, "grid_error"))
    for attr in ("L", "W", "T"):
        for sign in (-1, 1):
            for delta, fam in steps:
                out.append((f"{attr}{'+' if sign > 0 else '-'}{delta:.2f}", fam, resized(attr, sign * delta),
                            "margins kept"))
    for sign in (-1, 1):
        for delta, fam in ((WITHIN * HOLE_TOL, "within_tol"), (BEYOND * HOLE_TOL, "beyond_tol"),
                           (0.2, "grid_error"), (0.5, "grid_error")):
            d = round(d0 + sign * delta, 6)
            out.append((f"D{'+' if sign > 0 else '-'}{delta:.2f}", fam,
                        replace(g0, holes=tuple(replace(h, d=d) for h in g0.holes)), ""))
        d = round(d0 + sign * HOLE_TOL, 6)
        out.append((f"D_exact{'+' if sign > 0 else '-'}", "exact_limit",
                    replace(g0, holes=tuple(replace(h, d=d) for h in g0.holes)), "audit F07"))
    for delta, fam in ((WITHIN * POSITION_TOL, "within_tol"), (BEYOND * POSITION_TOL, "beyond_tol"),
                       (0.25, "grid_error"), (0.5, "grid_error")):
        out.append((f"pattern_dx{delta:.2f}", fam, _shift_holes(g0, delta, 0), "pattern slides on plate"))
        out.append((f"one_hole_dy{delta:.2f}", fam, _shift_holes(g0, 0, delta, only=0), ""))
        out.append((f"stock_dx{delta:.2f}", fam, replace(g0, ox=delta), "audit P0-1: plate slides under holes"))
        out.append((f"part_dx{delta:.2f}", fam, replace(_shift_holes(g0, delta, 0), ox=delta),
                    "whole part off origin"))
    out.append(("one_hole_dx_exact", "exact_limit", _shift_holes(g0, POSITION_TOL, 0, only=0), "inclusive limit"))
    out.append(("drop_one_hole", "count", replace(g0, holes=g0.holes[1:]), ""))
    out.append(("extra_centre_hole", "count", replace(g0, holes=(*g0.holes, HoleG(0, 0, d0))), ""))
    out.append(("blind_all", "gate", replace(g0, holes=tuple(
        replace(h, through=False, depth=round(spec.thickness * 0.6, 2)) for h in g0.holes)), ""))
    out.append(("blind_one", "gate", replace(g0, holes=(
        replace(g0.holes[0], through=False, depth=round(spec.thickness * 0.6, 2)), *g0.holes[1:])), ""))
    out.append(("mixed_diameters", "diameter", replace(g0, holes=(
        replace(g0.holes[0], d=d0 + 1.0), *g0.holes[1:])), ""))
    for delta, fam in ((WITHIN * DATUM_TOL, "within_tol"), (DATUM_TOL, "exact_limit"),
                       (BEYOND * DATUM_TOL, "beyond_tol"), (0.5, "grid_error")):
        out.append((f"part_dz{delta:.2f}", fam, replace(g0, oz=delta), "audit K1: Z datum"))
    out.append(("membrane", "gate", replace(g0, holes=tuple(
        replace(h, through=False, depth=round(spec.thickness - 0.005, 4)) for h in g0.holes)), "audit F04"))
    out.append(("cavity", "gate", replace(g0, cavity=True), "audit F05"))

    # Strict contract (suite 0.5.0): unrequested features. Each is built only
    # where it stays clear of the four holes, so the defect is the only change.
    px, py, r0 = spec.pitch_x / 2, spec.pitch_y / 2, d0 / 2
    leg = clip_leg(spec)
    if leg >= 0.5:
        out.append(("corner_fillets", "extra_feature", replace(g0, fillet=leg), "allowed by 0.4.0"))
        out.append(("clipped_corner", "extra_feature",
                    replace(g0, extras=("clipped_corner",), fillet_or_clip=leg), "external audit C2"))
    out.append(("chamfer_top", "extra_feature", replace(g0, extras=("chamfer_top",)), "0.3 mm edge break"))
    out.append(("fillet_top", "extra_feature", replace(g0, extras=("fillet_top",)), "0.3 mm edge break"))
    if px - r0 > r0 + 0.5:
        out.append(("edge_notch", "extra_feature", replace(g0, extras=("edge_notch",)),
                    "the defect of the saved dev answer gen-0021"))
    if px - r0 > 3.5 or py - r0 > 1.5:
        out.append(("slot", "extra_feature", replace(g0, extras=("slot",)), "external audit F02"))
    if px - r0 > 2.5 or py - r0 > 2.5:
        out.append(("pocket", "extra_feature", replace(g0, extras=("pocket",)), "allowed by 0.4.0"))
    rc = min(1.0, spec.thickness / 4)
    if py - r0 > rc + 0.5:
        out.append(("cross_bore", "extra_feature", replace(g0, extras=("cross_bore",)), "external audit F02"))
    out.append(("bore_burr", "extra_feature", replace(g0, extras=("bore_burr",)), "external audit C2"))
    bx = spec.length / 2 - d0 / 4
    out.append(("breakout", "extra_feature",
                replace(g0, holes=(replace(g0.holes[-1], x=bx), *g0.holes[:-1])), "a known limitation of 0.4.0"))

    mutants = []
    for name, fam, g, note in out:
        fails, amb = oracle(spec, g)
        mutants.append(Mutant(spec.id, name, fam, g, fails, amb, note))
    return mutants


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", type=int, default=30, help="number of eval specs to mutate")
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()
    try:
        from cad_spec.measure import ScorerUnavailableError, require_cadquery
    except ImportError:  # pre-0.4.1 scorer: plain import check
        import cadquery  # noqa: F401
    else:
        try:
            require_cadquery()
        except ScorerUnavailableError as exc:
            raise SystemExit(f"cad-spec: {exc}") from None

    _, eval_specs = make_splits()
    specs = eval_specs[: args.specs]
    rows = []
    t0 = time.time()
    for spec in specs:
        for m in mutants_for(spec):
            report = R.score(to_code(m.geometry), spec)
            # A part that did not build fails every check. 0.3.x put "build"
            # outside the compared set, so a build failure read as all-pass
            # in the per-check table.
            got = set(GATES + REQS) if report.error else {c.name for c in report.checks if not c.passed}
            compare = set(GATES + REQS) - m.ambiguous
            want = m.oracle_fails & compare
            have = got & compare
            gated = bool(want & set(GATES))
            if gated:  # a gated part: only gates are meaningful
                want, have = want & set(GATES), have & set(GATES)
            oracle_reward = 0.0 if gated else 1 - len(m.oracle_fails & set(REQS)) / len(REQS)
            rows.append({
                "spec_id": spec.id, "mutant": m.name, "family": m.family, "note": m.note,
                "oracle_fails": sorted(m.oracle_fails), "ambiguous": sorted(m.ambiguous),
                "scorer_fails": sorted(got), "scorer_reward": report.reward,
                "oracle_full_credit": not m.oracle_fails, "agree": want == have,
                "oracle_reward": round(oracle_reward, 4), "error": report.error,
            })
    elapsed = time.time() - t0

    scored = [r for r in rows if r["family"] != "known_limitation"]
    wrong = [r for r in scored if not r["oracle_full_credit"]]
    right = [r for r in scored if r["oracle_full_credit"]]
    ffc = [r for r in wrong if r["scorer_reward"] >= 1.0]
    frj = [r for r in right if r["scorer_reward"] < 1.0]
    per_check: dict[str, Counter] = defaultdict(Counter)
    for r in scored:
        amb = set(r["ambiguous"])
        of, sf = set(r["oracle_fails"]), set(r["scorer_fails"])
        gated = bool(of & set(GATES))
        for c in GATES + (() if gated else REQS):
            if c in amb:
                per_check[c]["ambiguous"] += 1
                continue
            key = ("fail" if c in of else "pass") + "/" + ("fail" if c in sf else "pass")
            per_check[c][key] += 1
    by_family = Counter((r["family"], r["agree"]) for r in rows)

    try:
        from cad_spec.measure import sandbox_info
    except ImportError:  # older scorer
        def sandbox_info() -> dict:
            return {"mode": "unknown (pre-0.3.0 scorer)"}

    summary = {
        "scorer_version": SCORER_VERSION,
        "specs": len(specs),
        "mutants": len(rows),
        "scored_mutants": len(scored),
        "oracle_wrong_parts": len(wrong),
        "oracle_correct_parts": len(right),
        "false_full_credit": len(ffc),
        "false_full_credit_rate": round(len(ffc) / max(1, len(wrong)), 4),
        "false_rejection": len(frj),
        "false_rejection_rate": round(len(frj) / max(1, len(right)), 4),
        "exact_agreement_rate": round(sum(r["agree"] for r in scored) / max(1, len(scored)), 4),
        "known_limitation_mutants": len(rows) - len(scored),
        "known_limitation_agree_with_scorer_rule": sum(r["agree"] for r in rows if r["family"] == "known_limitation"),
        "per_check": {k: dict(v) for k, v in sorted(per_check.items())},
        "agreement_by_family": {f"{f}:{'agree' if a else 'disagree'}": n for (f, a), n in sorted(by_family.items())},
        "suite_version": SUITE_VERSION,
        "contract_tolerances": {"LINEAR_TOL": LINEAR_TOL, "HOLE_TOL": HOLE_TOL, "POSITION_TOL": POSITION_TOL,
                                "MARGIN_TOL": MARGIN_TOL, "DATUM_TOL": DATUM_TOL, "MATERIAL_TOL": MATERIAL_TOL,
                                "GATE_VOLUME_BAND": GATE_VOLUME_BAND, "BOUNDARY_GUARD": BOUNDARY_GUARD},
        "sandbox": sandbox_info(),
        "seconds": round(elapsed, 1),
    }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"scorer-validation-{SCORER_VERSION}"
    json_path, md_path = out / f"{stem}.json", out / f"{stem}.md"
    with json_path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"summary": summary, "rows": rows}, indent=1) + "\n")

    ffc_by_family = Counter(r["family"] for r in ffc)
    wrong_by_family = Counter(r["family"] for r in wrong)
    md = [f"# Scorer validation, cad-spec {SCORER_VERSION} (suite {SUITE_VERSION})", "",
          (f"{len(rows)} mutants over {len(specs)} held-out specs, generated by "
           "`scripts/validate_scorer.py`. Ground truth comes from the geometry "
           "parameters (oracle), never from the scorer. Contract: one plate, four through "
           f"holes, nothing else; {LINEAR_TOL} mm on every dimension, position, margin, datum "
           "and diameter."), "",
          "| Metric | Value |", "|---|---:|",
          f"| Wrong parts (oracle) | {len(wrong)} |",
          f"| False full credit | {len(ffc)} ({summary['false_full_credit_rate']:.1%}) |",
          f"| Correct parts (oracle) | {len(right)} |",
          f"| False rejection | {len(frj)} ({summary['false_rejection_rate']:.1%}) |",
          f"| Exact failed-check agreement | {summary['exact_agreement_rate']:.1%} |", "",
          "## Wrong parts by family", "",
          "| Family | Wrong parts | Given full credit |", "|---|---:|---:|"]
    for fam in sorted(wrong_by_family):
        md.append(f"| {fam} | {wrong_by_family[fam]} | {ffc_by_family.get(fam, 0)} |")
    if ffc:
        names = Counter(r["mutant"] for r in ffc)
        md += ["", "Full credit given to: " + ", ".join(f"`{k}` ({v})" for k, v in sorted(names.items())) + "."]
    md += ["", "## Per check (oracle/scorer)", "",
           "| Check | pass/pass | fail/fail | pass/fail (false reject) | fail/pass (false accept) | ambiguous |",
           "|---|---:|---:|---:|---:|---:|"]
    for c in GATES + REQS:
        v = per_check.get(c, Counter())
        md.append(f"| `{c}` | {v['pass/pass']} | {v['fail/fail']} | {v['pass/fail']} | {v['fail/pass']} | "
                  f"{v['ambiguous']} |")
    md += ["", "## Disagreements", ""]
    dis = [r for r in scored if not r["agree"]]
    if not dis:
        md.append("None.")
    for r in dis[:40]:
        md.append(f"- `{r['spec_id']}` `{r['mutant']}`: oracle {r['oracle_fails']}, scorer {r['scorer_fails']}")
    if len(dis) > 40:
        md.append(f"- and {len(dis) - 40} more, see the JSON file.")
    md += ["", f"Runtime {summary['seconds']} s, sandbox `{summary['sandbox'].get('mode')}`."]
    with md_path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")

    print("\n".join(md[:11]))
    print(f"\nwrote {json_path} and {md_path.name}")
    return 1 if ffc or frj else 0


if __name__ == "__main__":
    raise SystemExit(main())
