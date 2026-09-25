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
  one axis misplaced                            X right and Y wrong, or the reverse
  some holes right, some wrong                  at least one hole at a nominal
                                                position, not all
  holes misplaced (other)
  gate: <name>                                  a cheat gate fired (overlapping
                                                holes merge into one opening, so
                                                hole positions count bore axes,
                                                not separate openings)
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
import ast
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.measure import BuildError, ScorerUnavailableError, build_and_measure, extract_code, require_cadquery
from cad_spec.rubric import SCORER_VERSION
from cad_spec.tasks import TASKS, Spec, edit_source, make_splits

DETERMINISTIC = {"reference", "parser-copy", "parser-derive", "parser-template", "rev-a"}
from degenerate import is_degenerate
from summarize_results import load, select_runs

TOL = 0.5  # mm, same class as the rubric's position tolerance
UNFINISHED = ("API error", "degenerate loop", "cut off")
NOT_BUILT = ("syntax error", "CadQuery API error", "Python error in model code", "no part produced", "timeout",
             "build failed")
ORDER = UNFINISHED + NOT_BUILT + (
    "change order ignored", "change not propagated to pitch",
    "holes stacked at one point", "no holes", "pattern anchored at a corner", "margin applied twice",
    "X and Y swapped", "pitch read as coordinates", "one axis misplaced", "some holes right, some wrong",
    "holes misplaced (other)",
    "gate: single_solid", "gate: clean_solid", "gate: simple_through_holes", "gate: hole_count_sane",
    "gate: is_plate", "wrong plate size", "off Z datum", "wrong hole diameter", "wrong hole count",
    "material off", "edge margin off", "other",
)
# Last: an answer the classifier itself could not read (never silently dropped).
ORDER = (*ORDER, "classifier error")


def close(a: float, b: float) -> bool:
    return abs(a - b) <= TOL


_CQ_TYPES = (r"(?:Workplane|Sketch|Assembly|Shape|Solid|Compound|Face|Wire|Edge|Vertex|Shell"
             r"|Vector|Location|Plane|Matrix)")
_CADQUERY_MESSAGE = re.compile(
    rf"AttributeError: '{_CQ_TYPES}' object has no attribute"
    r"|AttributeError: module 'cadquery[\w.]*' has no attribute"
    rf"|TypeError: {_CQ_TYPES}\.\w+\(\)"
    r"|DispatchError|Standard_\w+|StdFail|TopoDS|BRep_API"
    r"|Cannot find a solid on the stack|No pending wires present|No pending edges"
    r"|Do not know how to handle until argument|Cannot union type"
)


def executable_code(completion: str) -> str:
    """The answer's code with comments and formatting normalised away, so
    code-based rules see what runs, not what a comment says. Falls back to
    the raw code when it does not parse."""
    code = extract_code(completion or "")
    try:
        return ast.unparse(ast.parse(code))
    except (SyntaxError, ValueError, RecursionError):
        return code


def _rect_literals(completion: str) -> list[tuple[float, float]]:
    """Literal (x, y) arguments of every .rect() call in the executable code."""
    try:
        tree = ast.parse(extract_code(completion or ""))
    except (SyntaxError, ValueError, RecursionError):
        return []
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "rect" and len(node.args) >= 2):
            try:
                out.append((float(ast.literal_eval(node.args[0])), float(ast.literal_eval(node.args[1]))))
            except (ValueError, TypeError, SyntaxError):
                continue
    return out


def _unbuilt_label(row: dict) -> str:
    err = row.get("error") or ""
    if row.get("timeout") or "execution budget" in err:
        return "timeout"
    if re.search(r"SyntaxError|IndentationError", err):
        return "syntax error"
    # CadQuery misuse needs evidence: the message names a CadQuery object or a
    # CadQuery-only condition, or the error was raised inside CadQuery (the
    # scorer records where). Missing methods and bad arguments are raised at
    # the caller, so the message decides those. A plain Python error in the
    # model's own code is not a CadQuery weakness (audit, September 2026).
    if err.startswith("execution failed:"):
        origin = re.search(r"\[raised in ([\w ]+)\]\s*$", err)
        if _CADQUERY_MESSAGE.search(err) or (origin and origin.group(1) == "cadquery"):
            return "CadQuery API error"
        if origin and origin.group(1) == "model code":
            return "Python error in model code"
        return "build failed"
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


# Operations that put the next drill somewhere new. Their absence is what
# makes repeated .hole() calls pile up at one spot: CadQuery drills at the
# centre of whatever is on the stack, so .translate() (which moves the SOLID)
# and .faces().workplane() do not move the drill point.
_PLACEMENT = re.compile(
    r"\.(transformed|moveTo|move|pushPoints|vertices|rarray|polarArray)\s*\("
    r"|\.center\(\s*(?!0(\.0)?\s*,\s*0(\.0)?\s*\))"
)
_HOLE_CALL = re.compile(r"\.hole\s*\(")

_STACK_SIGNS = (
    re.compile(r"(\.hole\([^)]*\)\s*){2,}"),                     # .hole().hole(): same spot twice
    re.compile(r"for\s+(\w+)[^:]*:\s*\n(?:(?!\1).)*?\.hole\(", re.S),  # loop var never used
)
# A (0, 0) POINT in a list of positions (not `.center(0, 0)`), or an explicit
# corner-anchored rectangle.
_CORNER_SIGNS = re.compile(r"centered\s*=\s*False|[\[,]\s*\(\s*0(\.0)?\s*,\s*0(\.0)?\s*\)")


def _single_point_label(x: float, y: float, code: str) -> str:
    """Only one hole position on the plate: stacked drilling, or not?

    Stacked means several drills at one spot: two or more .hole() calls (or
    one in a loop that never uses its variable) with nothing in the code that
    sets a new position. A single measured position can also come from holes
    that really were placed apart but landed off the plate (e.g. cumulative
    .transformed() offsets); those are NOT stacked. When only the origin hole
    survived, the code decides between stacked and corner-anchored.
    (Label check, September 2026: the earlier rule required the .hole()
    calls to be adjacent and missed five stacked answers.)
    """
    repeated = len(_HOLE_CALL.findall(code)) >= 2 and not _PLACEMENT.search(code)
    if repeated or _STACK_SIGNS[1].search(code):
        return "holes stacked at one point"
    if close(x, 0) and close(y, 0):
        compact = re.sub(r"\s+", "", code)
        if ".rect(" in compact and ".vertices()" not in compact and "pushPoints" not in compact:
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
    nominal = [(a * spec.pitch_x / 2, b * spec.pitch_y / 2) for a in (-1, 1) for b in (-1, 1)]
    hits = sum(any(close(x, nx) and close(y, ny) for x, y in points) for nx, ny in nominal)
    if kinds == {"ok"}:
        # Right extremes are not a right pattern: every hole must sit at a
        # nominal corner (two right corners plus two holes between them
        # passed as "edge margin off"; audit, September 2026).
        stray = [p for p in points if not any(close(p[0], nx) and close(p[1], ny) for nx, ny in nominal)]
        if not stray:
            return None
        return "some holes right, some wrong" if hits else "holes misplaced (other)"
    if "corner" in kinds and kinds <= {"corner", "ok"}:
        return "pattern anchored at a corner"
    if "margin twice" in kinds and kinds <= {"margin twice", "ok"}:
        return "margin applied twice"
    if kinds == {"swapped"}:
        return "X and Y swapped"
    if "coords" in kinds and kinds <= {"coords", "ok"}:
        return "pitch read as coordinates"
    # Exact hits first: a true one-axis error puts NO hole at a nominal
    # position, while a partly right pattern can span the right distance on
    # one axis by coincidence.
    if 0 < hits < 4:
        return "some holes right, some wrong"
    if "ok" in kinds:
        return "one axis misplaced"
    return "holes misplaced (other)"


_API_KINDS = (
    (re.compile(r"DispatchError: \('(\w+): \d+ methods found', \(<class '[\w.]*?(\w+)'>"),
     "no matching signature for {1}.{0}()"),
    (re.compile(r"No pending wires present"), "operation needs a sketch or wire"),
    (re.compile(r"cannot be interpreted as an integer"), "non-integer count"),
    (re.compile(r"Do not know how to handle until argument"), "invalid extrude or cut argument"),
    (re.compile(r"AttributeError: '(\w+)' object has no attribute '(\w+)'"), "no such method: {0}.{1}"),
    (re.compile(r"AttributeError: module '([\w.]+)' has no attribute '(\w+)'"), "no such function: {0}.{1}"),
    (re.compile(r"TypeError: (?:[\w.]+\.)?(\w+)\(\) (?:takes|got|missing)"), "wrong arguments to {0}()"),
    (re.compile(r"Cannot find a solid on the stack"), "operation needs a solid on the stack"),
    (re.compile(r"NameError: name '(\w+)' is not defined"), "undefined name"),
    (re.compile(r"Standard_\w+|StdFail|BRep_API|OCP"), "geometry kernel refused the operation"),
)


def api_error_kind(error: str) -> str:
    """What the code got wrong, from the error text of a CadQuery API error."""
    for pattern, template in _API_KINDS:
        m = pattern.search(error or "")
        if m:
            return template.format(*m.groups()).replace(".__init__()", "()")
    m = re.search(r"execution failed: (\w+)", error or "")
    return m.group(1) if m else "unknown"


def _l4_label(m, spec: Spec, code: str = "") -> str | None:
    """Change-order specific failures, judged against rev A and rev B.

    The geometry decides when it can. When the stale pattern cannot be seen
    (every hole landed off the new, smaller plate: label check #25), the code
    decides: a rev B plate whose .rect() still carries rev A's pitch.
    """
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
    if pitch_changes and same(size, size_b):
        rects = _rect_literals(code)
        stale = any(same(r, (rev_a.pitch_x, rev_a.pitch_y)) for r in rects)
        fresh = any(same(r, (spec.pitch_x, spec.pitch_y)) for r in rects)
        if stale and not fresh:
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


def classify(row: dict, spec: Spec, max_tokens: int | None) -> tuple[str, dict]:
    """(label, detail). Detail keeps the evidence: error text, measured holes."""
    detail: dict = {}
    label = _classify(row, spec, max_tokens, detail)
    if label == "CadQuery API error":
        detail["api_kind"] = api_error_kind(row.get("error") or "")
    return label, detail


def _classify(row: dict, spec: Spec, max_tokens: int | None, detail: dict) -> str:
    if row.get("error"):
        detail["error"] = (row.get("error") or "")[:300]
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
    except BuildError as exc:
        detail["error"] = str(exc)[:300]
        return "build failed"
    if row.get("tier") == "L4":
        label = _l4_label(m, spec, row.get("completion", ""))
        if label:
            return label
    # Hole pattern before gates: misplaced holes often overlap or break out
    # through an edge, which also fires a gate; the pattern is the diagnosis.
    points = [(h.x, h.y) for h in m.holes] + [(p.x, p.y) for p in m.partial_bores]
    detail["holes"] = sorted({(round(x, 2), round(y, 2)) for x, y in points})
    detail["plate"] = [m.length, m.width, m.thickness]
    # Where the plate IS, not only its size: a moved plate puts correct-looking
    # holes "outside the footprint" (label check #26).
    detail["plate_bbox"] = {"x": [m.x_min, m.x_max], "y": [m.y_min, m.y_max], "z": [m.z_min, m.z_max]}
    pattern = _pattern_label(points, spec, executable_code(row.get("completion", "")))
    return pattern or _checks_label(row["checks"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--tiers", nargs="+", default=["L0", "L1", "L2", "L3", "L4"])
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()
    try:
        require_cadquery()
    except ScorerUnavailableError as exc:
        raise SystemExit(f"cad-spec: {exc}") from None

    train, evals = make_splits()
    specs = {s.id: s for s in [*train, *evals, *TASKS]}
    per_model: dict[str, Counter] = defaultdict(Counter)
    per_model_tier: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    totals: Counter = Counter()
    labelled = []
    api_kinds: dict[str, Counter] = defaultdict(Counter)
    metas, groups, ends = load(args.paths)
    for (model, tier), run in sorted(select_runs(metas, groups, ends).items()):
        if tier not in args.tiers:
            continue
        max_tokens = run["meta"].get("max_tokens")
        for row in run["rows"]:
            if row.get("spec_id") not in specs:
                continue
            totals[model] += 1
            if bool(row.get("checks")) and all(row["checks"].values()):
                continue
            try:
                label, detail = classify(row, specs[row["spec_id"]], max_tokens)
            except ScorerUnavailableError:
                raise
            except Exception as exc:  # one unreadable answer never stops the analysis
                label, detail = "classifier error", {"error": f"{type(exc).__name__}: {exc}"[:300]}
            if "api_kind" in detail:
                api_kinds[detail["api_kind"]][model] += 1
            per_model[model][label] += 1
            per_model_tier[model][tier][label] += 1
            labelled.append({"model": model, "run_id": run["run_id"], "tier": tier, "spec_id": row["spec_id"],
                             "rollout": row.get("rollout", 0), "label": label, **detail})
        print(f"classified {model} {tier} (run {run['run_id']})", file=sys.stderr)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = out / f"failure-modes-{SCORER_VERSION}"
    Path(f"{stem}.json").write_text(json.dumps({
        "scorer_version": SCORER_VERSION, "tiers": args.tiers, "order": list(ORDER),
        "totals": totals, "per_model": per_model,
        "per_model_tier": {m: dict(t) for m, t in per_model_tier.items()},
        "api_error_kinds": {k: dict(v) for k, v in api_kinds.items()}, "rows": labelled,
    }, indent=1))

    used = [lab for lab in ORDER if any(c[lab] for c in per_model.values())]
    header = ["| Model | " + " | ".join(used) + " | all pass |", "|---|" + "---:|" * (len(used) + 1)]

    def table_rows(names: list[str]) -> list[str]:
        out = []
        for model in sorted(names, key=lambda k: -sum(per_model[k].values()) / max(1, totals[k])):
            n = max(1, totals[model])
            failed = sum(per_model[model].values())
            cells = [f"{per_model[model][lab] / n:.0%}" if per_model[model][lab] else "" for lab in used]
            out.append(f"| {model} | " + " | ".join(cells) + f" | {1 - failed / n:.0%} |")
        return out

    models = [m for m in per_model if m not in DETERMINISTIC]
    refs = [m for m in per_model if m in DETERMINISTIC]
    md = [f"# Failure modes, cad-spec {SCORER_VERSION}", "",
          f"Tiers {', '.join(args.tiers)}. Each failed answer gets one label (first match, in column order). "
          "Cells are the share of ALL the model's answers; the last column is the all-pass rate.", "",
          "## Models", "", *header, *table_rows(models)]
    if refs:
        md += ["", "## Reference programs (no model; they answer only what their rule can parse)", "",
               *header, *table_rows(refs)]
    if api_kinds:
        md += ["", "## What the CadQuery API errors were", "",
               "| Error | Answers | Models with the most |", "|---|---:|---|"]
        for kind, by in sorted(api_kinds.items(), key=lambda kv: -sum(kv[1].values()))[:15]:
            top = ", ".join(f"{m} ({n})" for m, n in by.most_common(3))
            md.append(f"| {kind} | {sum(by.values())} | {top} |")
    Path(f"{stem}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\nwrote {stem}.json and .md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
