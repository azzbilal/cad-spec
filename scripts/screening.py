"""Screening analysis for training candidates (step 3 of the training plan).

    python scripts/screening.py results/training/screening/*.jsonl
    python scripts/screening.py RUN.jsonl --out results/training/screening/report

For each run file, per tier:

- all-pass: share of answers meeting all 9 requirements (pass@1);
- pass@k: share of specs solved by at least one of the k samples;
- mean reward (partial credit k/9 included);
- learning signal: GRPO-style RL learns from reward differences between the
  samples of one prompt. A group whose samples all get the same reward has a
  zero advantage for every sample and teaches nothing. The report splits
  those groups into all solved, all zero, and all the same partial score, and
  gives the mean within-group standard deviation and mean |advantage|;
- truncation: answers cut off at --max-tokens, split into CUT OFF (the budget
  was too small for a real answer: a configuration problem) and DEGENERATE
  (a repetition loop: a model failure), with the mean reward of each and the
  output-token distribution of the answers that finished.

Greedy runs (one sample per spec) have no groups: the signal columns read
"n/a". Screening runs stay in results/training/ and never enter the board.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

TIERS = ("L0", "L1", "L2", "L3", "L4")


def load_run(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """(meta, result rows, end record) of one run file."""
    meta: dict[str, Any] = {}
    end: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if "meta" in rec:
            meta = rec["meta"]
        elif "end" in rec:
            end = rec["end"]
        elif "tier" in rec:
            rows.append(rec)
    return meta, rows, end


def _pct(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


def _tokens(row: dict[str, Any]) -> float | None:
    usage = row.get("usage") or {}
    tok = usage.get("completion_tokens", usage.get("output_tokens"))
    return float(tok) if tok is not None else None


def tier_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Statistics of one tier's answers (every sample of every spec)."""
    # A group is one prompt: the same spec at the same tier. Keying on the spec
    # alone would merge a spec's four tiers into one fake group in "All".
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in rows:
        groups[(r["tier"], r["spec_id"])].append(float(r["reward"]))
    sizes = {len(g) for g in groups.values()}
    k = max(sizes) if sizes else 0
    n = len(rows)
    rewards = [float(r["reward"]) for r in rows]
    trunc = [r for r in rows if r.get("finish_reason") == "length"]
    loops = [r for r in trunc if r.get("degenerate")]
    cut = [r for r in trunc if not r.get("degenerate")]
    done_tokens = [t for r in rows if r.get("finish_reason") != "length" and (t := _tokens(r)) is not None]
    finished = [float(r["reward"]) for r in rows if r.get("finish_reason") != "length"]
    out: dict[str, Any] = {
        "answers": n,
        "prompts": len(groups),
        "samples_per_spec": k if len(sizes) == 1 else sorted(sizes),
        "all_pass": sum(x == 1.0 for x in rewards) / n if n else None,
        "pass_at_k": sum(any(x == 1.0 for x in g) for g in groups.values()) / len(groups) if groups else None,
        "mean_reward": statistics.fmean(rewards) if rewards else None,
        "mean_reward_finished": statistics.fmean(finished) if finished else None,
        "truncated": len(trunc) / n if n else None,
        "cut_off": len(cut) / n if n else None,
        "degenerate": len(loops) / n if n else None,
        "mean_reward_truncated": statistics.fmean(float(r["reward"]) for r in trunc) if trunc else None,
        "tokens_finished": {"p50": _pct(done_tokens, 0.5), "p90": _pct(done_tokens, 0.9),
                            "p99": _pct(done_tokens, 0.99), "max": max(done_tokens) if done_tokens else None},
    }
    multi = [g for g in groups.values() if len(g) > 1]
    if multi:
        flat = [g for g in multi if max(g) == min(g)]
        out["groups"] = len(multi)
        out["signal"] = 1 - len(flat) / len(multi)
        out["flat_all_solved"] = sum(g[0] == 1.0 for g in flat) / len(multi)
        out["flat_all_zero"] = sum(g[0] == 0.0 for g in flat) / len(multi)
        out["flat_partial"] = sum(0.0 < g[0] < 1.0 for g in flat) / len(multi)
        out["mean_group_std"] = statistics.fmean(statistics.pstdev(g) for g in multi)
        out["mean_abs_advantage"] = statistics.fmean(
            abs(x - statistics.fmean(g)) for g in multi for x in g)
    return out


def analyse(path: Path) -> dict[str, Any]:
    meta, rows, end = load_run(path)
    by_tier: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_tier[r["tier"]].append(r)
    tiers = {t: tier_stats(by_tier[t]) for t in TIERS if t in by_tier}
    return {
        "file": path.as_posix(),
        "model": meta.get("model"), "arm": meta.get("arm"), "split": meta.get("split"),
        "temperature": meta.get("temperature"), "max_tokens": meta.get("max_tokens"),
        "rollouts": meta.get("rollouts"), "extra_body": meta.get("extra_body"),
        "git_commit": meta.get("git_commit"), "scorer_version": meta.get("scorer_version"),
        "status": end.get("status"), "spent_usd": end.get("spent_usd"),
        "tiers": tiers, "all": tier_stats(rows) if rows else {},
    }


def _f(x: Any, pct: bool = True) -> str:
    if x is None:
        return "n/a"
    return f"{100 * x:.0f}%" if pct else f"{x:.3f}"


def _t(x: Any) -> str:
    return "n/a" if x is None else f"{x:.0f}"


def markdown(report: dict[str, Any]) -> str:
    r = report
    lines = [
        f"## {r['model']} ({r['arm']} arm, temperature {r['temperature']}, "
        f"{r['rollouts']} sample(s) per spec, max_tokens {r['max_tokens']})",
        "",
        f"File `{r['file']}`, split {r['split']}, scorer {r['scorer_version']}, "
        f"status {r['status']}, spent ${r['spent_usd']}, commit {str(r['git_commit'])[:7]}.",
        f"Extra body: `{r['extra_body']}`.",
        "",
        "### Scores",
        "",
        "| Tier | Answers | All-pass | pass@k | Mean reward | Mean reward (finished only) |",
        "|---|---|---|---|---|---|",
    ]
    rows = [*r["tiers"].items(), ("All", r["all"])]
    for t, s in rows:
        lines.append(f"| {t} | {s['answers']} | {_f(s['all_pass'])} | {_f(s['pass_at_k'])} | "
                     f"{_f(s['mean_reward'], False)} | {_f(s['mean_reward_finished'], False)} |")
    lines += [
        "",
        "### Learning signal (groups of samples of one spec)",
        "",
        "| Tier | Groups | With signal | Flat: all solved | Flat: all zero | Flat: same partial | "
        "Mean group std | Mean abs advantage |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for t, s in rows:
        if "groups" not in s:
            lines.append(f"| {t} | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
            continue
        lines.append(f"| {t} | {s['groups']} | {_f(s['signal'])} | {_f(s['flat_all_solved'])} | "
                     f"{_f(s['flat_all_zero'])} | {_f(s['flat_partial'])} | "
                     f"{_f(s['mean_group_std'], False)} | {_f(s['mean_abs_advantage'], False)} |")
    lines += [
        "",
        "### Truncation",
        "",
        "| Tier | Truncated | Cut off | Degenerate | Mean reward if truncated | "
        "Output tokens of finished answers (p50 / p90 / p99 / max) |",
        "|---|---|---|---|---|---|",
    ]
    for t, s in rows:
        tk = s["tokens_finished"]
        lines.append(f"| {t} | {_f(s['truncated'])} | {_f(s['cut_off'])} | {_f(s['degenerate'])} | "
                     f"{_f(s['mean_reward_truncated'], False)} | "
                     f"{_t(tk['p50'])} / {_t(tk['p90'])} / {_t(tk['p99'])} / {_t(tk['max'])} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=None,
                    help="write OUT.md and OUT.json as well as printing the report")
    args = ap.parse_args(argv)
    reports = [analyse(p) for p in args.files]
    text = "# Screening report\n\n" + "\n".join(markdown(r) for r in reports)
    sys.stdout.write(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.with_suffix(".md").write_text(text, encoding="utf-8")
        args.out.with_suffix(".json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
        print(f"\nwrote {args.out.with_suffix('.md')} and .json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
