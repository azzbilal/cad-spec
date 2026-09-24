"""Summarize run JSONL files from run_baseline.py, one block per (run, tier).

Reports what the evaluation protocol asks for: all-requirements pass rate
(pass@1 over rollouts), mean and median reward with a 95% bootstrap interval
over SPECS (rollouts of one spec are not independent), build rate, gate hits,
timeouts, truncated answers, API errors, cost, per-check pass rates. Tiers
are never averaged together. Any (model, tier) with more than 5% truncated
or failed calls is listed as not publishable: that is a run configuration
problem, not a model result.

    python scripts/summarize_results.py results/runs/*.jsonl
    python scripts/summarize_results.py results/runs/*.jsonl --markdown results/baselines.md
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

CHECKS = ("R1:length", "R2:width", "R3:thickness", "R4a:hole_count", "R4b:hole_diameter",
          "R5:hole_pattern", "R6:material", "R7:edge_margin")
GATES = ("gate:single_solid", "gate:simple_through_holes", "gate:hole_count_sane", "gate:is_plate")


def bootstrap_ci(per_spec: list[float], iters: int = 2000, seed: int = 0) -> tuple[float, float]:
    """95% percentile interval of the mean, resampling specs."""
    if len(per_spec) < 2:
        v = per_spec[0] if per_spec else 0.0
        return v, v
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(per_spec, k=len(per_spec))) for _ in range(iters))
    return means[int(0.025 * iters)], means[int(0.975 * iters) - 1]


def load(paths: list[str]) -> tuple[dict[str, dict], dict[tuple[str, str], list[dict]]]:
    metas: dict[str, dict] = {}
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for p in paths:
        with open(p) as fh:
            for line in fh:
                row = json.loads(line)
                if "meta" in row:
                    metas[row["meta"]["run_id"]] = row["meta"]
                    continue
                groups[(row["run_id"], row["tier"])].append(row)
    return metas, groups


def _looks_truncated(row: dict) -> bool:
    """Rows from before finish_reason was recorded: an empty answer that used the whole
    token budget (the signature of the September 2026 qwen3 incident)."""
    if "finish_reason" in row:
        return False
    used = (row.get("usage") or {}).get("completion_tokens") or 0
    return not row.get("completion", "").strip() and used >= 1000


def summarize(rows: list[dict]) -> dict:
    by_spec: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_spec[r["spec_id"]].append(r)
    spec_mean = [statistics.fmean(r["reward"] for r in rs) for rs in by_spec.values()]
    spec_full = [statistics.fmean(float(r["reward"] >= 1.0) for r in rs) for rs in by_spec.values()]
    built = [r for r in rows if r["built"]]
    out = {
        "specs": len(by_spec), "rollouts": len(rows),
        "mean_reward": statistics.fmean(spec_mean), "mean_reward_ci95": bootstrap_ci(spec_mean),
        "median_reward": statistics.median(r["reward"] for r in rows),
        "all_requirements_pass": statistics.fmean(spec_full), "all_requirements_pass_ci95": bootstrap_ci(spec_full),
        "built_rate": len(built) / len(rows),
        "gate_hit_rate": sum(1 for r in built if not r["gates_passed"]) / max(1, len(built)),
        "timeouts": sum(r.get("timeout", False) for r in rows),
        "truncated": sum(bool(r.get("truncated")) or _looks_truncated(r) for r in rows),
        "cost_usd": sum(float(r.get("cost_usd") or 0.0) for r in rows),
        "api_errors": sum(bool(r.get("api_error")) for r in rows),
        "per_check": {c: sum(r["checks"].get(c, False) for r in rows) / len(rows) for c in CHECKS},
        "per_gate_fail": {g: sum(not r["checks"].get(g, True) for r in built) / max(1, len(built)) for g in GATES},
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--markdown", default="")
    args = ap.parse_args()
    metas, groups = load(args.paths)

    md = ["| Model | Tier | Specs x rollouts | Mean reward [95% CI] | All-8 pass [95% CI] | Built | Gate hits |"
          " Timeouts | Truncated | API errors | Cost $ | R1 | R2 | R3 | R4a | R4b | R5 | R6 | R7 |",
          "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|" + "---:|" * 8]
    flagged: list[str] = []
    for (run_id, tier), rows in sorted(groups.items(), key=lambda kv: (metas.get(kv[0][0], {}).get("model", ""),
                                                                       kv[0][1])):
        s = summarize(rows)
        m = metas.get(run_id, {})
        lo, hi = s["mean_reward_ci95"]
        flo, fhi = s["all_requirements_pass_ci95"]
        md.append(
            f"| {m.get('model', '?')} | {tier} | {s['specs']}x{s['rollouts'] // max(1, s['specs'])} | "
            f"{s['mean_reward']:.3f} [{lo:.3f}, {hi:.3f}] | {s['all_requirements_pass']:.1%} "
            f"[{flo:.1%}, {fhi:.1%}] | {s['built_rate']:.0%} | {s['gate_hit_rate']:.0%} | {s['timeouts']} | "
            f"{s['truncated']} | {s['api_errors']} | {s['cost_usd']:.4f} | "
            + " | ".join(f"{s['per_check'][c]:.0%}" for c in CHECKS) + " |"
        )
    for (run_id, tier), rows in groups.items():
        s = summarize(rows)
        if s["truncated"] + s["api_errors"] > 0.05 * len(rows):
            flagged.append(f"{metas.get(run_id, {}).get('model', '?')} {tier}: "
                           f"{s['truncated']} truncated, {s['api_errors']} API errors of {len(rows)}")
    if flagged:
        md += ["", "**Not publishable as a model result** (over 5% of answers truncated or failed at the API; "
               "fix the run configuration and rerun):", *[f"- {f}" for f in sorted(flagged)]]
    scorers = sorted({m.get("scorer_version", "?") for m in metas.values()})
    revs = sorted({m.get("git_rev", "?") for m in metas.values()})
    md += ["", f"Scorer version(s): {', '.join(scorers)}. Code revision(s): {', '.join(revs)}. "
           "Intervals: 95% bootstrap over specs."]
    text = "\n".join(md)
    print(text)
    if args.markdown:
        Path(args.markdown).write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
