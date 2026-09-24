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

Run:
    python scripts/validate_scorer.py            # 30 eval specs, ~1-2 min
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
MARGIN_TOL = getattr(R, "MARGIN_TOL", R.POSITION_TOL)  # R7 did not exist before 0.3.0
DATUM_TOL = getattr(R, "DATUM_TOL", R.POSITION_TOL)  # R8 did not exist before 0.4.0
EXACT = 1e-9  # a deviation this close to a tolerance is AT the limit: inside, by definition
BOUNDARY_GUARD = 0.02  # mm for linear checks, fraction-of-band for R6/is_plate

GATES = ("gate:single_solid", "gate:clean_solid", "gate:simple_through_holes", "gate:hole_count_sane",
         "gate:is_plate")
REQS = ("R1:length", "R2:width", "R3:thickness", "R4a:hole_count", "R4b:hole_diameter",
        "R5:hole_pattern", "R6:material", "R7:edge_margin", "R8:z_datum")


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
    method: str = "hole_top"  # hole_top | cutter_both | cutter_split


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


def to_code(g: Geometry) -> str:
    lines = [
        "import cadquery as cq",
        f"plate = cq.Workplane('XY').box({g.L}, {g.W}, {g.T}).translate(({g.ox}, {g.oy}, {g.oz}))",
    ]
    if g.fillet:
        lines.append(f"plate = plate.edges('|Z').fillet({g.fillet})")
    top, bot = g.oz + g.T / 2, g.oz - g.T / 2
    for h in g.holes:
        r = h.d / 2
        if not h.through:
            z0, length = top - h.depth, h.depth
            lines.append(f"plate = plate.cut(cq.Workplane('XY').workplane(offset={z0}).center({h.x}, {h.y})"
                         f".circle({r}).extrude({length}))")
        elif g.method == "hole_top":
            lines.append(f"plate = plate.faces('>Z').workplane().pushPoints([({h.x}, {h.y})]).hole({h.d})")
        elif g.method == "cutter_both":
            lines.append(f"plate = plate.cut(cq.Workplane('XY').center({h.x}, {h.y})"
                         f".circle({r}).extrude({g.T + 4}, both=True))")
        elif g.method == "cutter_split":  # two abutting cutters: top half and bottom half
            lines.append(f"plate = plate.cut(cq.Workplane('XY').center({h.x}, {h.y}).circle({r}).extrude({top + 2}))")
            lines.append(f"plate = plate.cut(cq.Workplane('XY').center({h.x}, {h.y}).circle({r}).extrude({bot - 2}))")
        else:
            raise ValueError(g.method)
    if g.cavity:  # 1.5 x 1.5 mm, 40% of the thickness: clear of any hole (web >= 2 mm)
        void = f"cq.Workplane('XY').box(1.5, 1.5, {0.4 * g.T}).translate(({g.ox}, {g.oy}, {g.oz}))"
        lines.append(f"plate = plate.cut({void})")
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
        ok, a = _edge(value, target, R.LINEAR_TOL)
        fails |= set() if ok else {name}
        amb |= {name} if a else set()
    if len(inside) != spec.hole_count:
        fails.add("R4a:hole_count")
    diam_ok = bool(inside)
    for h in inside:
        ok, a = _edge(h.d, spec.hole_diameter, R.HOLE_TOL)
        diam_ok &= ok
        amb |= {"R4b:hole_diameter"} if a else set()
    if not diam_ok:
        fails.add("R4b:hole_diameter")
    expected = [(sx * spec.pitch_x / 2, sy * spec.pitch_y / 2) for sx in (-1, 1) for sy in (-1, 1)]
    for ex, ey in expected:
        dists = [math.dist((h.x, h.y), (ex, ey)) for h in inside]
        best = min(dists, default=math.inf)
        if best > R.POSITION_TOL:
            fails.add("R5:hole_pattern")
        if abs(best - R.POSITION_TOL) < BOUNDARY_GUARD:
            amb.add("R5:hole_pattern")
    worst = 0.0
    for h in inside:
        dx = min(h.x - x0, x1 - h.x)
        dy = min(h.y - y0, y1 - h.y)
        worst = max(worst, abs(dx - spec.edge_margin), abs(dy - spec.edge_margin))
    if not inside or worst > MARGIN_TOL:
        fails.add("R7:edge_margin")
    if inside and abs(worst - MARGIN_TOL) < BOUNDARY_GUARD:
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
    band = R.MATERIAL_TOL * exp_mat
    if abs(volume - exp_mat) > band:
        fails.add("R6:material")
    if abs(abs(volume - exp_mat) - band) < BOUNDARY_GUARD * band:
        amb.add("R6:material")

    predicted = g.L * g.W * g.T - removed  # is_plate sees measured bores only
    if abs(volume - predicted) > R.GATE_VOLUME_BAND * predicted:
        fails.add("gate:is_plate")
    return fails, amb


# --- mutant families ------------------------------------------------------------

def _shift_holes(g: Geometry, dx: float, dy: float, only: int | None = None) -> Geometry:
    holes = tuple(replace(h, x=h.x + dx, y=h.y + dy) if only is None or i == only else h
                  for i, h in enumerate(g.holes))
    return replace(g, holes=holes)


def mutants_for(spec: Spec) -> list[Mutant]:
    g0 = nominal(spec)
    t_lin, t_hole, t_pos = R.LINEAR_TOL, R.HOLE_TOL, R.POSITION_TOL
    out: list[tuple[str, str, Geometry, str]] = [
        ("nominal", "benign", g0, ""),
        ("method_cutter_both", "benign", replace(g0, method="cutter_both"), "audit P0-2"),
        ("method_cutter_split", "benign", replace(g0, method="cutter_split"), "stacked faces"),
    ]
    fr = min(2.0, spec.edge_margin - spec.hole_diameter / 2 - 1.0)
    if fr >= 0.5:
        out.append(("corner_fillets", "benign", replace(g0, fillet=round(fr, 1)), ""))
    for field_name, attr, tol in (("L", "L", t_lin), ("W", "W", t_lin), ("T", "T", t_lin)):
        base = getattr(g0, attr)
        for sign in (-1, 1):
            # scale the whole part so margins stay nominal: holes move with the edge
            for delta, fam in ((tol - 0.1, "within_tol"), (tol + 0.1, "beyond_tol")):
                value = base + sign * delta
                g = replace(g0, **{attr: value})
                if attr in ("L", "W"):
                    k = 0 if attr == "L" else 1
                    # Move each hole outward (grow) or inward (shrink) with its
                    # edge so the margins stay nominal. 0.3.x used copysign,
                    # which drops the sign of `sign`: shrinking moved holes out.
                    def _out(v: float) -> float:
                        return 1.0 if v > 0 else -1.0

                    g = replace(g, holes=tuple(
                        replace(h, x=h.x + _out(h.x) * sign * delta / 2) if k == 0
                        else replace(h, y=h.y + _out(h.y) * sign * delta / 2) for h in g.holes))
                out.append((f"{field_name}{'+' if sign > 0 else '-'}{delta:.1f}", fam, g, "margins kept"))
    for sign in (-1, 1):
        for delta, fam in ((t_hole - 0.1, "within_tol"), (t_hole + 0.1, "beyond_tol")):
            d = spec.hole_diameter + sign * delta
            out.append((f"D{'+' if sign > 0 else '-'}{delta:.1f}", fam,
                        replace(g0, holes=tuple(replace(h, d=d) for h in g0.holes)), ""))
    for delta, fam in ((t_pos - 0.2, "within_tol"), (t_pos + 0.2, "beyond_tol")):
        out.append((f"pattern_dx{delta:.1f}", fam, _shift_holes(g0, delta, 0), "pattern slides on plate"))
        out.append((f"one_hole_dy{delta:.1f}", fam, _shift_holes(g0, 0, delta, only=0), ""))
        out.append((f"stock_dx{delta:.1f}", fam, replace(g0, ox=delta), "audit P0-1: plate slides under holes"))
        out.append((f"part_dx{delta:.1f}", fam, replace(_shift_holes(g0, delta, 0), ox=delta),
                    "whole part off origin"))
    out.append(("drop_one_hole", "count", replace(g0, holes=g0.holes[1:]), ""))
    out.append(("extra_centre_hole", "count", replace(g0, holes=(*g0.holes, HoleG(0, 0, spec.hole_diameter))), ""))
    out.append(("blind_all", "gate", replace(g0, holes=tuple(
        replace(h, through=False, depth=round(spec.thickness * 0.6, 2)) for h in g0.holes)), ""))
    out.append(("blind_one", "gate", replace(g0, holes=(
        replace(g0.holes[0], through=False, depth=round(spec.thickness * 0.6, 2)), *g0.holes[1:])), ""))
    out.append(("mixed_diameters", "diameter", replace(g0, holes=(
        replace(g0.holes[0], d=spec.hole_diameter + 1.0), *g0.holes[1:])), ""))
    # 0.4.0 families from the reference-grounded audit.
    for delta, fam in ((DATUM_TOL - 0.2, "within_tol"), (DATUM_TOL, "exact_limit"), (DATUM_TOL + 0.2, "beyond_tol")):
        out.append((f"part_dz{delta:.1f}", fam, replace(g0, oz=delta), "audit K1: Z datum"))
    for sign in (-1, 1):
        d = round(spec.hole_diameter + sign * t_hole, 6)
        out.append((f"D_exact{'+' if sign > 0 else '-'}", "exact_limit",
                    replace(g0, holes=tuple(replace(h, d=d) for h in g0.holes)), "audit F07"))
    out.append(("membrane", "gate", replace(g0, holes=tuple(
        replace(h, through=False, depth=round(spec.thickness - 0.005, 4)) for h in g0.holes)), "audit F04"))
    out.append(("cavity", "gate", replace(g0, cavity=True), "audit F05"))

    # Known limitation: a hole moved so it breaks out through the side wall.
    bx = spec.length / 2 - spec.hole_diameter / 4
    out.append(("LIMIT_breakout", "known_limitation",
                replace(g0, holes=(replace(g0.holes[-1], x=bx), *g0.holes[:-1])), "see measure.py docstring"))

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
        "tolerances": {"LINEAR_TOL": R.LINEAR_TOL, "HOLE_TOL": R.HOLE_TOL, "POSITION_TOL": R.POSITION_TOL,
                       "MARGIN_TOL": MARGIN_TOL, "MATERIAL_TOL": R.MATERIAL_TOL, "DEPTH_TOL": R.DEPTH_TOL,
                       "GATE_VOLUME_BAND": R.GATE_VOLUME_BAND, "BOUNDARY_GUARD": BOUNDARY_GUARD},
        "sandbox": sandbox_info(),
        "seconds": round(elapsed, 1),
    }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"scorer-validation-{SCORER_VERSION}"
    json_path, md_path = out / f"{stem}.json", out / f"{stem}.md"
    json_path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))

    md = [f"# Scorer validation, cad-spec {SCORER_VERSION}", "",
          (f"{len(rows)} mutants over {len(specs)} held-out specs, generated by "
           "`scripts/validate_scorer.py`. Ground truth comes from the geometry "
           "parameters (oracle), never from the scorer."), "",
          "| Metric | Value |", "|---|---:|",
          f"| Wrong parts (oracle) | {len(wrong)} |",
          f"| False full credit | {len(ffc)} ({summary['false_full_credit_rate']:.1%}) |",
          f"| Correct parts (oracle) | {len(right)} |",
          f"| False rejection | {len(frj)} ({summary['false_rejection_rate']:.1%}) |",
          f"| Exact failed-check agreement | {summary['exact_agreement_rate']:.1%} |",
          f"| Known-limitation mutants (excluded above) | {len(rows) - len(scored)} |", "",
          "## Per check (oracle/scorer)", "",
          "| Check | pass/pass | fail/fail | pass/fail (false reject) | fail/pass (false accept) | ambiguous |",
          "|---|---:|---:|---:|---:|---:|"]
    for c in GATES + REQS:
        v = per_check.get(c, Counter())
        md.append(f"| `{c}` | {v['pass/pass']} | {v['fail/fail']} | {v['pass/fail']} | {v['fail/pass']} | "
                  f"{v['ambiguous']} |")
    md += ["", "## Disagreements", ""]
    dis = [r for r in scored if not r["agree"]]
    if not dis:
        md.append("None outside the known-limitation family.")
    for r in dis[:40]:
        md.append(f"- `{r['spec_id']}` `{r['mutant']}`: oracle {r['oracle_fails']}, scorer {r['scorer_fails']}")
    md += ["", "## Known limitation: side-wall breakout", "",
           ("Scored under the documented rule (a breakout hole is not counted). An inspector would "
            "instead record 4 holes with one misplaced. The table above excludes these mutants; "
            f"{summary['known_limitation_agree_with_scorer_rule']}/{len(rows) - len(scored)} "
            "matched the oracle's literal geometry view."), "",
           f"Runtime {summary['seconds']} s, sandbox `{summary['sandbox'].get('mode')}`."]
    md_path.write_text("\n".join(md) + "\n")

    print("\n".join(md[:14]))
    print(f"\nwrote {json_path} and {md_path.name}")
    return 1 if ffc or frj else 0


if __name__ == "__main__":
    raise SystemExit(main())
