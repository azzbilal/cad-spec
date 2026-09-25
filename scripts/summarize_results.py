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
from collections import Counter, defaultdict
from pathlib import Path

from degenerate import is_degenerate

CHECKS = ("R1:length", "R2:width", "R3:thickness", "R4a:hole_count", "R4b:hole_diameter",
          "R5:hole_pattern", "R6:material", "R7:edge_margin", "R8:z_datum")
GATES = ("gate:single_solid", "gate:clean_solid", "gate:simple_through_holes", "gate:hole_count_sane",
         "gate:is_plate")


def bootstrap_ci(per_spec: list[float], iters: int = 2000, seed: int = 0) -> tuple[float, float]:
    """95% percentile interval of the mean, resampling specs."""
    if len(per_spec) < 2:
        v = per_spec[0] if per_spec else 0.0
        return v, v
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(per_spec, k=len(per_spec))) for _ in range(iters))
    return means[int(0.025 * iters)], means[int(0.975 * iters) - 1]


def load(paths: list[str]) -> tuple[dict[str, dict], dict[tuple[str, str], list[dict]], dict[str, dict]]:
    """Returns run metadata, rows grouped by (run, tier), and end records by run."""
    metas: dict[str, dict] = {}
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    ends: dict[str, dict] = {}
    for p in paths:
        run_in_file = None
        with open(p) as fh:
            for line in fh:
                if not line.strip():
                    continue
                row = json.loads(line)
                if "meta" in row:
                    run_in_file = row["meta"]["run_id"]
                    if run_in_file in metas:
                        raise SystemExit(f"run id {run_in_file} appears in two files; refusing to merge them")
                    metas[run_in_file] = row["meta"]
                    continue
                if "end" in row:
                    if run_in_file:
                        ends[run_in_file] = row["end"]
                    continue
                groups[(row["run_id"], row["tier"])].append(row)
    return metas, groups, ends


def completeness_problems(run_id: str, tier: str, rows: list[dict], meta: dict, ends: dict[str, dict]) -> list[str]:
    """Why this (run, tier) is not a complete, clean evaluation; empty if it is."""
    problems = []
    planned = meta.get("planned") or {}
    seen = Counter((r.get("spec_id"), r.get("rollout", 0)) for r in rows)
    if planned and tier in planned.get("tiers", []):
        spec_ids, rollouts = planned.get("spec_ids"), planned.get("rollouts", 1)
        if not spec_ids:
            problems.append("run plan lists no spec ids")
        else:
            # Exact coverage, not a row count: a row count can be met by rows
            # for specs that were never planned (audit, September 2026).
            expected = {(sid, k) for sid in spec_ids for k in range(rollouts)}
            missing, extra = len(expected - set(seen)), len(set(seen) - expected)
            if missing:
                problems.append(f"{missing}/{len(expected)} planned rollouts missing")
            if extra:
                problems.append(f"{extra} rollouts for specs not in the plan")
    end = ends.get(run_id)
    if planned and end is None:
        problems.append("no end record (run interrupted or still running)")
    elif end and end.get("status") != "complete":
        problems.append(f"run ended: {end.get('status')}")
    dup = sum(c - 1 for c in seen.values() if c > 1)
    if dup:
        problems.append(f"{dup} duplicate rollouts")
    return problems


def _looks_truncated(row: dict, max_tokens: int | None) -> bool:
    """Rows from before finish_reason was recorded: judged against the run's
    ACTUAL token cap (0.3.x used a fixed 1,000). Any answer, empty or not,
    that used the whole cap counts as cut off."""
    if "finish_reason" in row:
        return False
    used = (row.get("usage") or {}).get("completion_tokens") or 0
    return bool(max_tokens) and used >= max_tokens


def _hit_cap(row: dict, max_tokens: int | None) -> bool:
    return bool(row.get("truncated")) or _looks_truncated(row, max_tokens)


def _is_loop(row: dict, max_tokens: int | None) -> bool:
    if "degenerate" in row:
        return bool(row["degenerate"])
    return _hit_cap(row, max_tokens) and is_degenerate(row.get("completion", ""))


def _cut_off(row: dict, max_tokens: int | None) -> bool:
    return _hit_cap(row, max_tokens) and not _is_loop(row, max_tokens)


def select_runs(metas: dict[str, dict], groups: dict[tuple[str, str], list[dict]],
                ends: dict[str, dict]) -> dict[tuple[str, str], dict]:
    """Choose ONE run per (model, tier). Shared by the leaderboard, the failure
    analysis and the label check, so no analysis counts a superseded run.

    Rule: the latest run with no problems (complete, under 5% cut off or API
    errors); if every run has problems, the latest one. Run ids start with a
    UTC timestamp, so they sort by time.
    """
    candidates: dict[tuple[str, str], list[tuple]] = defaultdict(list)
    for (run_id, tier), rows in groups.items():
        meta = metas.get(run_id, {})
        s = summarize(rows, meta.get("max_tokens"))
        problems = completeness_problems(run_id, tier, rows, meta, ends)
        if s["truncated"] + s["api_errors"] > 0.05 * len(rows):
            problems.append(f"{s['truncated']} cut off, {s['api_errors']} API errors")
        candidates[(meta.get("model", "?"), tier)].append((run_id, rows, problems, s["cost_usd"], meta))
    chosen = {}
    for key, runs in candidates.items():
        runs.sort(key=lambda r: r[0])
        clean = [r for r in runs if not r[2]]
        run_id, rows, problems, cost, meta = (clean or runs)[-1]
        chosen[key] = {"run_id": run_id, "rows": rows, "problems": list(dict.fromkeys(problems)),
                       "cost": cost, "meta": meta, "superseded": len(runs) - 1}
    return chosen


def _gates_ok(row: dict) -> bool:
    """Recorded gate verdict, or derived from the checks for rows without it."""
    if "gates_passed" in row:
        return bool(row["gates_passed"])
    return all(v for k, v in (row.get("checks") or {}).items() if k.startswith("gate:"))


def summarize(rows: list[dict], max_tokens: int | None = None) -> dict:
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
        "gate_hit_rate": sum(1 for r in built if not _gates_ok(r)) / max(1, len(built)),
        "timeouts": sum(r.get("timeout", False) for r in rows),
        # Truncated answers split in two: cut off mid-answer (budget too small:
        # a configuration problem) and degenerate loops (a model failure).
        "truncated": sum(_cut_off(r, max_tokens) for r in rows),
        "loops": sum(_is_loop(r, max_tokens) for r in rows),
        "unknown_cost": sum(1 for r in rows if r.get("cost_usd") is None and r.get("usage")),
        "cost_usd": sum(float(r.get("cost_usd") or 0.0) for r in rows),
        "api_errors": sum(bool(r.get("api_error")) for r in rows),
        "per_check": {c: (sum(r["checks"].get(c, False) for r in rows) / len(rows)
                          if any(c in r["checks"] for r in rows) or not any(r["checks"] for r in rows)
                          else None) for c in CHECKS},
        "per_gate_fail": {g: sum(not r["checks"].get(g, True) for r in built) / max(1, len(built)) for g in GATES},
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--markdown", default="")
    args = ap.parse_args()
    metas, groups, ends = load(args.paths)

    md = ["| Model | Tier | Specs x rollouts | Mean reward [95% CI] | Median | All-pass [95% CI] | Built | Gate hits |"
          " Timeouts | Cut off | Loops | API errors | Cost $ | " + " | ".join(c.split(":")[0] for c in CHECKS) + " |",
          "|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|" + "---:|" * len(CHECKS)]
    flagged: list[str] = []
    incomplete: list[str] = []
    for (run_id, tier), rows in sorted(groups.items(), key=lambda kv: (metas.get(kv[0][0], {}).get("model", ""),
                                                                       kv[0][1])):
        m = metas.get(run_id, {})
        s = summarize(rows, m.get("max_tokens"))
        lo, hi = s["mean_reward_ci95"]
        flo, fhi = s["all_requirements_pass_ci95"]
        problems = completeness_problems(run_id, tier, rows, m, ends)
        mark = " (incomplete)" if problems else ""
        cost = f"{s['cost_usd']:.4f}" + ("*" if s["unknown_cost"] else "")
        md.append(
            f"| {m.get('model', '?')}{mark} | {tier} | {s['specs']}x{s['rollouts'] // max(1, s['specs'])} | "
            f"{s['mean_reward']:.3f} [{lo:.3f}, {hi:.3f}] | {s['median_reward']:.3f} | "
            f"{s['all_requirements_pass']:.1%} [{flo:.1%}, {fhi:.1%}] | {s['built_rate']:.0%} | "
            f"{s['gate_hit_rate']:.0%} | {s['timeouts']} | {s['truncated']} | {s['loops']} | "
            f"{s['api_errors']} | {cost} | "
            + " | ".join("n/a" if s["per_check"][c] is None else f"{s['per_check'][c]:.0%}" for c in CHECKS)
            + " |"
        )
        if s["truncated"] + s["api_errors"] > 0.05 * len(rows):
            flagged.append(f"{m.get('model', '?')} {tier}: "
                           f"{s['truncated']} cut off, {s['api_errors']} API errors of {len(rows)}")
        if problems:
            incomplete.append(f"{m.get('model', '?')} {tier}: " + "; ".join(problems))
    if flagged:
        md += ["", "**Not publishable as a model result** (over 5% of answers cut off by the token budget or failed "
               "at the API; degenerate loops do not count here, they are model failures; "
               "fix the run configuration and rerun):", *[f"- {f}" for f in sorted(flagged)]]
    if incomplete:
        md += ["", "**Incomplete evaluations** (the eval split is ordered, so a partial run is a biased sample; "
               "do not rank these):", *[f"- {f}" for f in sorted(incomplete)]]
    if any(r.get("cost_usd") is None and r.get("usage") for rows in groups.values() for r in rows):
        md += ["", "\\* some calls had no cost reported by the provider; the cost shown is a lower bound."]
    scorers = sorted({m.get("scorer_version", "?") for m in metas.values()})
    revs = sorted({m.get("git_rev", "?") for m in metas.values()})
    if len(scorers) > 1:
        md += ["", f"**Mixed scorer versions ({', '.join(scorers)}): rows are not comparable across versions.** "
               "Rescore old runs with scripts/rescore.py."]
    md += ["", f"Scorer version(s): {', '.join(scorers)}. Code revision(s): {', '.join(revs)}. "
           "Intervals: 95% percentile bootstrap over specs (rollouts of one spec are averaged first). "
           "All-pass is pass@1: the share of rollouts meeting every requirement."]
    text = "\n".join(md)
    print(text)
    if args.markdown:
        Path(args.markdown).write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
