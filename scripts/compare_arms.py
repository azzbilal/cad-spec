# ruff: noqa: E402
"""Compare the hint and feedback arms with first-shot answers, and evaluate
the predictions pre-registered in docs/experiments/hint-feedback.md.

    python scripts/compare_arms.py results/rescored/0.4.0/*.jsonl \\
        --failures results/failure-modes-0.4.0.json

Every share is over the model's 120 answers on tiers L1 to L4 in that arm.
Differences are paired by (tier, spec) against the first-shot arm, with a 95%
bootstrap interval. The thresholds below are the pre-registered ones; do not
change them without adding a dated deviation to the pre-registration.
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


def answers_by_arm(paths: list[str], failures: dict) -> dict[str, dict[str, dict[tuple[str, str], str]]]:
    """model -> arm -> (tier, spec) -> "pass" or failure label (rollout 0)."""
    metas, groups, ends = load(paths)
    labels = {(r["model"], r["tier"], r["spec_id"], r.get("rollout", 0)): r["label"] for r in failures["rows"]}
    out: dict[str, dict[str, dict[tuple[str, str], str]]] = defaultdict(lambda: defaultdict(dict))
    for (name, tier), run in select_runs(metas, groups, ends).items():
        if tier not in TIERS:
            continue
        meta = run["meta"]
        for r in run["rows"]:
            if r.get("rollout", 0) != 0:
                continue
            passed = bool(r.get("checks")) and all(r["checks"].values())
            key = (tier, r["spec_id"])
            out[meta.get("model", "?")][run_arm(meta)][key] = (
                "pass" if passed else labels.get((name, tier, r["spec_id"], 0), "unlabelled"))
    return out


def share(answers: dict[tuple[str, str], str], wanted: tuple[str, ...]) -> float:
    return sum(v in wanted for v in answers.values()) / len(answers) if answers else float("nan")


def paired(base: dict, arm: dict, wanted: tuple[str, ...], iters: int = 2000) -> tuple[float, float, float]:
    """Mean paired difference (arm - base) in the share, with a 95% bootstrap interval."""
    keys = sorted(set(base) & set(arm))
    if not keys:
        return float("nan"), float("nan"), float("nan")
    diffs = [(arm[k] in wanted) - (base[k] in wanted) for k in keys]
    rng = random.Random(0)
    boots = sorted(statistics.fmean(rng.choices(diffs, k=len(diffs))) for _ in range(iters))
    return statistics.fmean(diffs), boots[int(0.025 * iters)], boots[int(0.975 * iters) - 1]


def verdicts(data: dict) -> list[tuple[str, str, str, str]]:
    """(prediction, model, held/failed/no data, evidence), per pre-registered rule."""
    out = []
    for m in KNOWLEDGE_MODELS:
        arms = data.get(m, {})
        if BASE in arms and HINT in arms:
            a, b = share(arms[BASE], KNOWLEDGE), share(arms[HINT], KNOWLEDGE)
            out.append(("P1", m, "held" if b <= P1_MAX_RATIO * a else "failed",
                        f"knowledge failures {a:.0%} -> {b:.0%}"))
        else:
            out.append(("P1", m, "no data", ""))
        if BASE in arms and FEEDBACK in arms:
            api_a, api_c = share(arms[BASE], (API,)), share(arms[FEEDBACK], (API,))
            st_a, st_c = share(arms[BASE], (STACKED,)), share(arms[FEEDBACK], (STACKED,))
            held = api_c <= P2_API_MAX_RATIO * api_a and st_c >= P2_STACK_MIN_RATIO * st_a
            out.append(("P2", m, "held" if held else "failed",
                        f"API errors {api_a:.0%} -> {api_c:.0%}; stacked {st_a:.0%} -> {st_c:.0%}"))
        else:
            out.append(("P2", m, "no data", ""))
    for m in ALL_MODELS:
        arms = data.get(m, {})
        for arm in (HINT, FEEDBACK):
            if BASE not in arms or arm not in arms:
                out.append(("P3", f"{m} [{arm}]", "no data", ""))
                continue
            shifts = {lab: share(arms[arm], (lab,)) - share(arms[BASE], (lab,)) for lab in REASONING}
            held = all(abs(v) <= P3_MAX_SHIFT for v in shifts.values())
            out.append(("P3", f"{m} [{arm}]", "held" if held else "failed",
                        "; ".join(f"{lab} {v:+.0%}" for lab, v in shifts.items())))
    return out


def summary(results: list[tuple[str, str, str, str]]) -> dict[str, str]:
    by_pred: dict[str, list[str]] = defaultdict(list)
    for pred, _, verdict, _ in results:
        by_pred[pred].append(verdict)
    return {p: ("incomplete" if "no data" in v else "confirmed" if all(x == "held" for x in v) else "not confirmed")
            for p, v in sorted(by_pred.items())}


def report(data: dict) -> str:
    cols = (("all pass", ("pass",)), ("API error", (API,)), ("stacked", (STACKED,)),
            ("margin twice", (REASONING[0],)), ("not propagated", (REASONING[1],)))
    md = ["# Hint and feedback arms: results", "",
          "Pre-registered in [docs/experiments/hint-feedback.md](../../docs/experiments/hint-feedback.md). "
          "Shares over each model's answers on L1 to L4; changes are paired by spec against first-shot, "
          "with 95% bootstrap intervals.", ""]
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
    results = verdicts(data)
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
    data = answers_by_arm(args.paths, json.loads(Path(args.failures).read_text(encoding="utf-8")))
    text = report(data)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
