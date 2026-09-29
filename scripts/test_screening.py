"""Self-test for scripts/screening.py (runs in CI, no network).

    python scripts/test_screening.py

Synthetic groups with hand-computed statistics: the learning-signal split
(all solved, all zero, same partial, mixed), pass@k, truncation split into
cut off and degenerate, and a greedy run that has no groups.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import screening as sc  # noqa: E402


def check(ok: bool, what: str) -> bool:
    print(f"[{'ok ' if ok else 'BAD'}] {what}")
    return ok


def row(spec: str, reward: float, finish: str = "stop", degenerate: bool = False,
        tokens: int = 300, tier: str = "L4") -> dict:
    return {"tier": tier, "spec_id": spec, "reward": reward, "finish_reason": finish,
            "degenerate": degenerate, "usage": {"completion_tokens": tokens}}


def main() -> int:
    rows = (
        [row("a", 1.0)] * 4                                           # flat, all solved
        + [row("b", 0.0)] * 4                                         # flat, all zero
        + [row("c", 5 / 9)] * 4                                       # flat, same partial
        + [row("d", 1.0), row("d", 1.0), row("d", 0.0, "length", tokens=1024),
           row("d", 0.0, "length", True, tokens=1024)]               # mixed: the only signal
    )
    s = sc.tier_stats(rows)
    ok = check(s["groups"] == 4 and abs(s["signal"] - 0.25) < 1e-12
               and s["flat_all_solved"] == s["flat_all_zero"] == s["flat_partial"] == 0.25,
               "flat groups split into all solved / all zero / same partial; one group in four has signal")
    ok &= check(abs(s["mean_group_std"] - 0.5 / 4) < 1e-12 and abs(s["mean_abs_advantage"] - 0.5 / 4) < 1e-12,
                "group std and mean |advantage|: 0.5 for the mixed group, 0 elsewhere, averaged over 4")
    # Binary view: a (1.0, 5/9 flat) group stays flat; the mixed group d is
    # (1, 1, 0, 0): signal 1/4, |adv| 0.5 each, 0.5/4 over all groups.
    ok &= check(s["binary_signal"] == 0.25 and abs(s["binary_mean_abs_advantage"] - 0.5 / 4) < 1e-12
                and s["binary_abs_advantage_per_useful_group"] == 0.5,
                "binary view: same groups scored 1 only when all pass; strength per useful group")
    partial = sc.tier_stats([row("p", 1.0), row("p", 7 / 9), row("p", 1.0), row("p", 7 / 9)])
    ok &= check(abs(partial["mean_abs_advantage"] - 1 / 9) < 1e-12 and partial["binary_mean_abs_advantage"] == 0.5,
                "the L4 failure (7/9 vs 1.0): |adv| 0.111 continuous, 0.5 binary")
    ok &= check(abs(s["all_pass"] - 6 / 16) < 1e-12 and s["pass_at_k"] == 0.5,
                "all-pass counts answers (6/16); pass@k counts specs solved at least once (2/4)")
    ok &= check(s["truncated"] == 2 / 16 and s["cut_off"] == 1 / 16 and s["degenerate"] == 1 / 16
                and s["mean_reward_truncated"] == 0.0,
                "truncation splits into cut off (budget) and degenerate (loop)")
    ok &= check(abs(s["mean_reward_finished"] - (6 + 4 * 5 / 9) / 14) < 1e-12
                and s["tokens_finished"]["max"] == 300,
                "finished-only reward and token percentiles leave the truncated answers out")

    across = sc.tier_stats([row("a", 1.0, tier="L1"), row("a", 1.0, tier="L1"),
                            row("a", 0.0, tier="L4"), row("a", 0.0, tier="L4")])
    ok &= check(across["groups"] == 2 and across["signal"] == 0.0 and across["pass_at_k"] == 0.5,
                "the overall row keeps one group per (tier, spec): tiers of one spec never merge")

    greedy = sc.tier_stats([row("a", 1.0), row("b", 0.0)])
    ok &= check("groups" not in greedy and greedy["samples_per_spec"] == 1,
                "a greedy run has no groups: the signal columns read n/a")

    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "run.jsonl"
        meta = {"meta": {"model": "m", "arm": "hint", "split": "eval", "temperature": 1.0,
                         "max_tokens": 1024, "rollouts": 4}}
        f.write_text("\n".join(json.dumps(x) for x in [meta, *rows, {"end": {"status": "complete"}}]),
                     encoding="utf-8")
        rep = sc.analyse(f)
        text = sc.markdown(rep)
    ok &= check(rep["tiers"]["L4"]["answers"] == 16 and "| L4 | 4 | 25% |" in text and "| All |" in text,
                "a run file becomes per-tier and overall tables")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
