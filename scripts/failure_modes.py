# ruff: noqa: E402
"""Classify every failed answer into a failure mode ("fingerprint").

A leaderboard says how often a model fails; this says how. Each answer that
did not meet every requirement gets exactly one label, decided from the
recorded run data and, for answers that built a part, from its re-measured
geometry (hole positions, plate size) compared with the spec. Labels are
checked in order, so each answer lands in the first one that fits:

  API error, degenerate loop, cut off           the answer never finished
  syntax error, CadQuery API error, no part,    the code did not build a part
  timeout, build failed
  change order ignored (L4)                     part matches rev A, not rev B
  change not propagated to pitch (L4)           size edited, pitch left as rev A
  holes stacked at one point                    positions planned but never bound
                                                to .hole() (e.g. no .vertices())
  no holes
  pattern anchored at a corner                  right spacing, starts at origin
                                                (when only one hole lands on the
                                                plate, the code breaks the tie)
  margin applied twice                          spacing = pitch - 2 x margin
  X and Y swapped                               spacing uses the other axis pitch
  pitch read as coordinates                     spacing = 2 x pitch
  holes misplaced (other)
  gate: <name>                                  a cheat gate fired
  wrong plate size, off Z datum, wrong hole     pattern right, one other thing
  diameter, wrong hole count, material off,     wrong
  edge margin off, other

    python scripts/failure_modes.py results/rescored/0.4.0/*.jsonl
    python scripts/failure_modes.py results/rescored/0.4.0/*.jsonl --tiers L1 L2 L3

Writes results/failure-modes-<scorer version>.{json,md}. Rebuilding parts
takes a few minutes for a full board (only failed, built answers are rebuilt).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.measure import BuildError, build_and_measure
from cad_spec.rubric import SCORER_VERSION
from cad_spec.tasks import TASKS, Spec, edit_source, make_splits
from degenerate import is_degenerate

TOL = 0.5  # mm, same class as the rubric's position tolerance
UNFINISHED = ("API error", "degenerate loop", "cut off")
NOT_BUILT = ("syntax error", "CadQuery API error", "no part produced", "timeout", "build failed")
ORDER = UNFINISHED + NOT_BUILT + (
    "change order ignored", "change not propagated to pitch",
    "holes stacked at one point", "no holes", "pattern anchored at a corner", "margin applied twice",
    "X and Y swapped", "pitch read as coordinates", "holes misplaced (other)",
    "gate: single_solid", "gate: clean_solid", "gate: simple_through_holes", "gate: hole_count_sane",
    "gate: is_plate", "wrong plate size", "off Z datum", "wrong hole diameter", "wrong hole count",
    "material off", "edge margin off", "other",
)


def close(a: float, b: float) -> bool:
    return abs(a - b) <= TOL


def _unbuilt_label(row: dict) -> str:
    err = row.get("error") or ""
    if row.get("timeout") or "execution budget" in err:
        return "timeout"
    if re.search(r"SyntaxError|IndentationError", err):
        return "syntax error"
    if re.search(r"execution failed: (AttributeError|TypeError|ValueError|NameError|IndexError|KeyError|"
                 r"Standard_\w+|OCP|StdFail)", err):
        return "CadQuery API error"
    if re.search(r"did not define|no CadQuery shape|no solid|no code|not a shape", err) or not err:
        return "no part produced"
    return "build failed"


def _axis(vals: list[float], pitch: float, other_pitch: float, margin: float) -> str:
    spacing, centre = max(vals) - min(vals), (max(vals) + min(vals)) / 2
    if close(spacing, pitch):
        if close(centre, 0):
            return "ok"
        return "corner" if close(abs(centre), pitch / 2) else "shifted"
    if close(spacing, abs(pitch - 2 * margin)):
        return "margin twice"
    if close(spacing, other_pitch) and not close(pitch, other_pitch):
        return "swapped"
    if close(spacing, 2 * pitch):
        return "coords"
    return "other"


_STACK_SIGNS = (
    re.compile(r"(\.hole\([^)]*\)\s*){2,}"),                     # .hole().hole(): same spot twice
    re.compile(r"for\s+(\w+)[^:]*:\s*\n(?:(?!\1).)*?\.hole\(", re.S),  # loop var never used
)
# A (0, 0) POINT in a list of positions (not `.center(0, 0)`), or an explicit
# corner-anchored rectangle.
_CORNER_SIGNS = re.compile(r"centered\s*=\s*False|[\[,]\s*\(\s*0(\.0)?\s*,\s*0(\.0)?\s*\)")


def _single_point_label(x: float, y: float, code: str) -> str:
    """Only one hole position on the plate. Geometry alone cannot tell four
    holes drilled at one spot from a corner-anchored pattern whose other
    holes fell off the plate, so the code breaks the tie."""
    if close(x, 0) and close(y, 0):
        compact = re.sub(r"\s+", "", code)
        rect_no_bind = ".rect(" in compact and ".vertices()" not in compact and "pushPoints" not in compact
        if rect_no_bind or any(sign.search(code) for sign in _STACK_SIGNS):
            return "holes stacked at one point"
        if _CORNER_SIGNS.search(code):
            return "pattern anchored at a corner"
    return "holes misplaced (other)"


def _pattern_label(points: list[tuple[float, float]], spec: Spec, code: str = "") -> str | None:
    """None when the hole pattern is right; otherwise the pattern failure."""
    if not points:
        return "no holes"
    distinct = {(round(x / TOL), round(y / TOL)) for x, y in points}
    if len(distinct) == 1:
        return _single_point_label(points[0][0], points[0][1], code)
    ax = _axis([p[0] for p in points], spec.pitch_x, spec.pitch_y, spec.edge_margin)
    ay = _axis([p[1] for p in points], spec.pitch_y, spec.pitch_x, spec.edge_margin)
    kinds = {ax, ay}
    if kinds == {"ok"}:
        return None
    if "corner" in kinds and kinds <= {"corner", "ok"}:
        return "pattern anchored at a corner"
    if "margin twice" in kinds and kinds <= {"margin twice", "ok"}:
        return "margin applied twice"
    if kinds == {"swapped"}:
        return "X and Y swapped"
    if "coords" in kinds and kinds <= {"coords", "ok"}:
        return "pitch read as coordinates"
    return "holes misplaced (other)"


def _l4_label(m, spec: Spec) -> str | None:
    """Change-order specific failures, judged against rev A and rev B."""
    rev_a = edit_source(spec)
    size = (m.length, m.width, m.thickness)
    size_a = (rev_a.length, rev_a.width, rev_a.thickness)
    size_b = (spec.length, spec.width, spec.thickness)
    holes = sorted({round(h.diameter, 1) for h in m.holes})
    pts = [(h.x, h.y) for h in m.holes] + [(p.x, p.y) for p in m.partial_bores]
    xs = [p[0] for p in pts] or [0.0]
    ys = [p[1] for p in pts] or [0.0]
    pitch = (max(xs) - min(xs), max(ys) - min(ys))
    same = lambda a, b: all(close(u, v) for u, v in zip(a, b, strict=True))  # noqa: E731
    looks_a = same(size, size_a) and same(pitch, (rev_a.pitch_x, rev_a.pitch_y)) and (
        not holes or close(holes[0], rev_a.hole_diameter))
    a_differs_from_b = not same(size_a, size_b) or not close(rev_a.hole_diameter, spec.hole_diameter)
    if looks_a and a_differs_from_b:
        return "change order ignored"
    pitch_changes = not same((rev_a.pitch_x, rev_a.pitch_y), (spec.pitch_x, spec.pitch_y))
    if pitch_changes and same(size, size_b) and same(pitch, (rev_a.pitch_x, rev_a.pitch_y)):
        return "change not propagated to pitch"
    return None


def _checks_label(checks: dict[str, bool]) -> str:
    for gate in ("single_solid", "clean_solid", "simple_through_holes", "hole_count_sane", "is_plate"):
        if checks.get(f"gate:{gate}") is False:
            return f"gate: {gate}"
    order = (("R1:length", "wrong plate size"), ("R2:width", "wrong plate size"), ("R3:thickness", "wrong plate size"),
             ("R8:z_datum", "off Z datum"), ("R4b:hole_diameter", "wrong hole diameter"),
             ("R4a:hole_count", "wrong hole count"), ("R6:material", "material off"),
             ("R7:edge_margin", "edge margin off"))
    for name, label in order:
        if checks.get(name) is False:
            return label
    return "other"


def classify(row: dict, spec: Spec, max_tokens: int | None) -> str:
    if row.get("api_error"):
        return "API error"
    capped = row.get("truncated") or (
        "finish_reason" not in row and max_tokens
        and ((row.get("usage") or {}).get("completion_tokens") or 0) >= max_tokens)
    if capped:
        return "degenerate loop" if row.get("degenerate", is_degenerate(row.get("completion", ""))) else "cut off"
    if not row.get("built"):
        return _unbuilt_label(row)
    try:
        m = build_and_measure(row.get("completion", ""))
    except BuildError:
        return "build failed"
    if row.get("tier") == "L4":
        label = _l4_label(m, spec)
        if label:
            return label
    # Hole pattern before gates: misplaced holes often overlap or break out
    # through an edge, which also fires a gate; the pattern is the diagnosis.
    points = [(h.x, h.y) for h in m.holes] + [(p.x, p.y) for p in m.partial_bores]
    pattern = _pattern_label(points, spec, row.get("completion", ""))
    return pattern or _checks_label(row["checks"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--tiers", nargs="+", default=["L0", "L1", "L2", "L3", "L4"])
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()

    train, evals = make_splits()
    specs = {s.id: s for s in [*train, *evals, *TASKS]}
    per_model: dict[str, Counter] = defaultdict(Counter)
    per_model_tier: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    totals: Counter = Counter()
    labelled = []
    for path in args.paths:
        lines = [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]
        meta = lines[0].get("meta", {})
        model = meta.get("model", Path(path).stem)
        for row in lines:
            if row.get("tier") not in args.tiers or row.get("spec_id") not in specs:
                continue
            totals[model] += 1
            passed = bool(row.get("checks")) and all(row["checks"].values())
            if passed:
                continue
            label = classify(row, specs[row["spec_id"]], meta.get("max_tokens"))
            per_model[model][label] += 1
            per_model_tier[model][row["tier"]][label] += 1
            labelled.append({"model": model, "tier": row["tier"], "spec_id": row["spec_id"],
                             "rollout": row.get("rollout", 0), "label": label})
        print(f"classified {model}", file=sys.stderr)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = out / f"failure-modes-{SCORER_VERSION}"
    Path(f"{stem}.json").write_text(json.dumps({
        "scorer_version": SCORER_VERSION, "tiers": args.tiers, "order": list(ORDER),
        "totals": totals, "per_model": per_model,
        "per_model_tier": {m: dict(t) for m, t in per_model_tier.items()}, "rows": labelled,
    }, indent=1))

    used = [lab for lab in ORDER if any(c[lab] for c in per_model.values())]
    md = [f"# Failure modes, cad-spec {SCORER_VERSION}", "",
          f"Tiers {', '.join(args.tiers)}. Each failed answer gets one label (first match, in column order). "
          "Cells are the share of ALL the model's answers; the last column is the all-pass rate.", "",
          "| Model | " + " | ".join(used) + " | all pass |", "|---|" + "---:|" * (len(used) + 1)]
    for model in sorted(per_model, key=lambda k: -sum(per_model[k].values()) / max(1, totals[k])):
        n = max(1, totals[model])
        failed = sum(per_model[model].values())
        cells = [f"{per_model[model][lab] / n:.0%}" if per_model[model][lab] else "" for lab in used]
        md.append(f"| {model} | " + " | ".join(cells) + f" | {1 - failed / n:.0%} |")
    Path(f"{stem}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\nwrote {stem}.json and .md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
