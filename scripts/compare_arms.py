# ruff: noqa: E402
"""Compare the hint and feedback arms with first-shot answers, and evaluate
the predictions pre-registered in docs/experiments/hint-feedback.md.

    python scripts/compare_arms.py results/rescored/0.4.0/*.jsonl \\
        --failures results/failure-modes-0.4.0.json

Every share is over the model's 120 answers on tiers L1 to L4 in that arm.
Differences are paired by (tier, spec) against the first-shot arm; their 95%
intervals resample SPECS (each spec's four tier outcomes together), since the
same 30 specs appear in every tier (amendment 1). The thresholds below are the
pre-registered ones; do not change them without a dated amendment.

An arm enters the verdicts only if it matches its registration: held-out
split, temperature 0, 1,024 output tokens, its exact condition (the
registered cheat-sheet text, or one feedback retry), a clean complete run,
and exactly the 30 held-out specs once per tier. Failure labels are joined by
run id; a failed answer without a label stops the analysis rather than being
counted as anything.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.tasks import make_splits
from run_baseline import SYSTEM_PROMPT
from summarize_results import load, run_arm, select_runs

TIERS = ("L1", "L2", "L3", "L4")
BASE, HINT, FEEDBACK = "first-shot", "hint", "feedback"
API, STACKED = "CadQuery API error", "holes stacked at one point"
KNOWLEDGE = (API, STACKED)
REASONING = ("margin applied twice", "change not propagated to pitch")
KNOWLEDGE_MODELS = ("google/gemma-3-27b-it", "mistralai/codestral-2508",
                    "meta-llama/llama-3.3-70b-instruct", "mistralai/mistral-small-3.2-24b-instruct")
ALL_MODELS = (*KNOWLEDGE_MODELS, "openai/gpt-4o-mini")
# Pre-registered thresholds.
P1_MAX_RATIO = 0.5       # hint knowledge share <= half of first-shot
P2_API_MAX_RATIO = 0.5   # feedback API-error share <= half of first-shot
P2_STACK_MIN_RATIO = 0.75  # feedback stacked share >= three quarters of first-shot
P3_MAX_SHIFT = 0.05      # reasoning labels move at most 5 points
HINTS_FILE = ROOT / "prompts" / "cadquery-hints.md"
REGISTERED = {"split": "eval", "temperature": 0.0, "max_tokens": 1024}


def registered_system_prompt(arm: str) -> str:
    if arm == HINT:
        return SYSTEM_PROMPT + "\n" + HINTS_FILE.read_text(encoding="utf-8").strip() + "\n"
    return SYSTEM_PROMPT


def arm_problems(meta: dict, arm: str) -> list[str]:
    """How a run departs from its arm's registration; empty if it does not."""
    out = [f"{k}={meta.get(k)!r}, registered {v!r}" for k, v in REGISTERED.items() if meta.get(k) != v]
    retries, want = meta.get("feedback_retries") or 0, 1 if arm == FEEDBACK else 0
    if retries != want:
        out.append(f"feedback retries {retries}, registered {want}")
    if meta.get("system_prompt") != registered_system_prompt(arm):
        out.append("system prompt differs from the registered one" + (" (cheat-sheet changed?)" if arm == HINT else ""))
    return out


def answers_by_arm(paths: list[str], failures: dict) -> tuple[dict, dict]:
    """(model -> arm -> (tier, spec) -> "pass" or label, model -> arm -> reasons excluded)."""
    metas, groups, ends = load(paths)
    held_out = {s.id for s in make_splits()[1]}
    labels = {(r.get("run_id"), r["tier"], r["spec_id"], r.get("rollout", 0)): r["label"] for r in failures["rows"]}
    data: dict = defaultdict(lambda: defaultdict(dict))
    excluded: dict = defaultdict(lambda: defaultdict(list))
    missing = 0
    for (_, tier), run in sorted(select_runs(metas, groups, ends).items()):
        meta = run["meta"]
        model, arm = meta.get("model", "?"), run_arm(meta)
        if tier not in TIERS or arm not in (BASE, HINT, FEEDBACK):
            continue
        problems = list(run["problems"]) + arm_problems(meta, arm)
        if {(r["spec_id"], r.get("rollout", 0)) for r in run["rows"]} != {(sid, 0) for sid in held_out}:
            problems.append("answers do not cover exactly the 30 held-out specs, once each")
        if problems:
            excluded[model][arm] += [f"{tier}: {p}" for p in problems]
            continue
        for r in run["rows"]:
            key = (tier, r["spec_id"])
            if bool(r.get("checks")) and all(r["checks"].values()):
                data[model][arm][key] = "pass"
                continue
            label = labels.get((run["run_id"], tier, r["spec_id"], 0))
            if label is None:
                missing += 1
                continue
            data[model][arm][key] = label
    if missing:
        raise SystemExit(f"{missing} failed answers have no failure label for their run. Regenerate the labels "
                         "from the same run files first: python scripts/failure_modes.py <the same files>")
    for model in list(data):
        for arm in list(data[model]):
            tiers = {t for t, _ in data[model][arm]}
            if excluded[model].get(arm) or tiers != set(TIERS):
                excluded[model][arm] = excluded[model].get(arm) or [f"tiers present: {sorted(tiers)}"]
                del data[model][arm]
    return data, excluded


def share(answers: dict[tuple[str, str], str], wanted: tuple[str, ...]) -> float:
    return sum(v in wanted for v in answers.values()) / len(answers) if answers else float("nan")


def paired(base: dict, arm: dict, wanted: tuple[str, ...], iters: int = 2000) -> tuple[float, float, float]:
    """Mean paired difference (arm - base) in the share, with a 95% interval
    from resampling SPECS: each spec keeps its four tier outcomes together."""
    keys = sorted(set(base) & set(arm))
    if not keys:
        return float("nan"), float("nan"), float("nan")
    by_spec: dict[str, list[int]] = defaultdict(list)
    for tier, spec in keys:
        by_spec[spec].append((arm[(tier, spec)] in wanted) - (base[(tier, spec)] in wanted))
    clusters = list(by_spec.values())
    point = statistics.fmean(d for c in clusters for d in c)
    rng = random.Random(0)
    boots = []
    for _ in range(iters):
        sample = rng.choices(clusters, k=len(clusters))
        boots.append(statistics.fmean(d for c in sample for d in c))
    boots.sort()
    return point, boots[int(0.025 * iters)], boots[int(0.975 * iters) - 1]


def verdicts(data: dict, excluded: dict | None = None) -> list[tuple[str, str, str, str]]:
    """(prediction, model, held/failed/no data, evidence), per pre-registered rule."""
    out = []
    for m in KNOWLEDGE_MODELS:
        arms = data.get(m, {})
        if BASE in arms and HINT in arms:
            a, b = share(arms[BASE], KNOWLEDGE), share(arms[HINT], KNOWLEDGE)
            out.append(("P1", m, "held" if b <= P1_MAX_RATIO * a else "failed",
                        f"knowledge failures {a:.0%} -> {b:.0%}"))
        else:
            out.append(("P1", m, "no data", _why(excluded, m, (BASE, HINT))))
        if BASE in arms and FEEDBACK in arms:
            api_a, api_c = share(arms[BASE], (API,)), share(arms[FEEDBACK], (API,))
            st_a, st_c = share(arms[BASE], (STACKED,)), share(arms[FEEDBACK], (STACKED,))
            held = api_c <= P2_API_MAX_RATIO * api_a and st_c >= P2_STACK_MIN_RATIO * st_a
            out.append(("P2", m, "held" if held else "failed",
                        f"API errors {api_a:.0%} -> {api_c:.0%}; stacked {st_a:.0%} -> {st_c:.0%}"))
        else:
            out.append(("P2", m, "no data", _why(excluded, m, (BASE, FEEDBACK))))
    for m in ALL_MODELS:
        arms = data.get(m, {})
        for arm in (HINT, FEEDBACK):
            if BASE not in arms or arm not in arms:
                out.append(("P3", f"{m} [{arm}]", "no data", _why(excluded, m, (BASE, arm))))
                continue
            shifts = {lab: share(arms[arm], (lab,)) - share(arms[BASE], (lab,)) for lab in REASONING}
            held = all(abs(v) <= P3_MAX_SHIFT for v in shifts.values())
            out.append(("P3", f"{m} [{arm}]", "held" if held else "failed",
                        "; ".join(f"{lab} {v:+.0%}" for lab, v in shifts.items())))
    return out


def _why(excluded: dict | None, model: str, arms: tuple[str, ...]) -> str:
    reasons = [f"{a}: {r}" for a in arms for r in ((excluded or {}).get(model, {}).get(a) or [])]
    return "; ".join(reasons[:3]) or "arm not run"


def summary(results: list[tuple[str, str, str, str]]) -> dict[str, str]:
    by_pred: dict[str, list[str]] = defaultdict(list)
    for pred, _, verdict, _ in results:
        by_pred[pred].append(verdict)
    return {p: ("incomplete" if "no data" in v else "confirmed" if all(x == "held" for x in v) else "not confirmed")
            for p, v in sorted(by_pred.items())}


def report(data: dict, excluded: dict | None = None) -> str:
    cols = (("all pass", ("pass",)), ("API error", (API,)), ("stacked", (STACKED,)),
            ("margin twice", (REASONING[0],)), ("not propagated", (REASONING[1],)))
    md = ["# Hint and feedback arms: results", "",
          "Pre-registered in [docs/experiments/hint-feedback.md](../../docs/experiments/hint-feedback.md). "
          "Shares over each model's 120 answers on L1 to L4; changes are paired by spec against first-shot, "
          "with 95% intervals from resampling specs.", ""]
    for m in sorted(data):
        arms = data[m]
        if BASE not in arms or len(arms) < 2:
            continue
        md += [f"## {m}", "", "| Arm | n | " + " | ".join(c for c, _ in cols) + " |",
               "|---|---:|" + "---:|" * len(cols)]
        for arm in (BASE, HINT, FEEDBACK):
            if arm not in arms:
                continue
            cells = []
            for _, wanted in cols:
                s = share(arms[arm], wanted)
                if arm == BASE:
                    cells.append(f"{s:.0%}")
                else:
                    d, lo, hi = paired(arms[BASE], arms[arm], wanted)
                    cells.append(f"{s:.0%} ({d:+.0%} [{lo:+.0%}, {hi:+.0%}])")
            md.append(f"| {arm} | {len(arms[arm])} | " + " | ".join(cells) + " |")
        md.append("")
    gone = [(m, a, r) for m, arms in sorted((excluded or {}).items()) for a, r in sorted(arms.items()) if r]
    if gone:
        md += ["## Arms excluded from the verdicts", "", "| Model | Arm | Why |", "|---|---|---|"]
        md += [f"| {m} | {a} | {'; '.join(r[:3])} |" for m, a, r in gone]
        md.append("")
    results = verdicts(data, excluded)
    md += ["## Pre-registered predictions", "", "| Prediction | Result |", "|---|---|"]
    md += [f"| {p} | {v} |" for p, v in summary(results).items()]
    md += ["", "| Prediction | Model | Verdict | Evidence |", "|---|---|---|---|"]
    md += [f"| {p} | {m} | {v} | {e} |" for p, m, v, e in results]
    return "\n".join(md) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--failures", required=True)
    ap.add_argument("--out", default=str(ROOT / "results" / "experiments" / "hint-feedback-results.md"))
    args = ap.parse_args()
    data, excluded = answers_by_arm(args.paths, json.loads(Path(args.failures).read_text(encoding="utf-8")))
    text = report(data, excluded)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
