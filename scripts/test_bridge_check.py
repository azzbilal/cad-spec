"""Self-test for scripts/bridge_check.py (runs in CI, no network).

    python scripts/test_bridge_check.py

Synthetic screening groups and synthetic step-1 metrics only: the interval
arithmetic, the three verdict positions, the prompt count derived from batch
shares, the pooled value, and the refusals on mismatched settings. It never
reads the archived run metrics.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import bridge_check as bc  # noqa: E402


def check(ok: bool, what: str) -> bool:
    print(f"[{'ok ' if ok else 'BAD'}] {what}")
    return ok


def group(passes: int) -> list[int]:
    return [1] * passes + [0] * (bc.K - passes)


def screening(l4: list[int]) -> dict[str, dict[str, list[int]]]:
    """L4 groups as given; L1, L2, L3 with 4 of 8 passing in each of 6 specs."""
    out = {t: {f"s{i}": group(4) for i in range(6)} for t in ("L1", "L2", "L3")}
    out["L4"] = {f"s{i}": group(p) for i, p in enumerate(l4)}
    return out


def metrics_row(l4: float, m: tuple[int, int, int] = (10, 8, 2)) -> dict:
    tasks = sum(m)
    names = list(bc.ENVS)
    row: dict = {"step": 1, "progress/tasks": float(tasks)}
    for name, n in zip(names, m, strict=True):
        row[f"batch/{name}"] = n / tasks
        row[f"train/{name}/all/metrics/all_pass_reward/mean"] = 0.5
    row[f"train/{bc.PRIMARY_ENV}/all/metrics/all_pass_reward/mean"] = l4
    return row


def refuses(fn, *args) -> bool:
    try:
        fn(*args)
    except bc.RefusalError:
        return True
    return False


def main() -> int:
    ok = True

    flat = [group(4)] * 5
    lo, hi = bc.predictive_interval(flat, 7, seed=1)
    ok &= check(lo == hi == 0.5, "identical groups give a zero-width interval at their rate")

    bimodal = [group(8)] * 15 + [group(0)] * 15
    lo, hi = bc.predictive_interval(bimodal, 10, seed=1)
    ok &= check(0.1 <= lo <= 0.3 and 0.7 <= hi <= 0.9 and (lo, hi) == bc.predictive_interval(bimodal, 10, seed=1),
                "bimodal groups, 10 prompts: wide interval around 50%, reproducible for a fixed seed")
    lo40, hi40 = bc.predictive_interval(bimodal, 40, seed=1)
    ok &= check(hi40 - lo40 < hi - lo, "more prompts give a narrower interval")

    ok &= check(
        [bc.classify(x, 0.2, 0.8) for x in (0.2, 0.8, 0.81, 0.19)]
        == ["BRIDGED", "BRIDGED", "OPEN_INFLATING", "STACKS_DIFFER_NOT_INFLATING"],
        "interval bounds are inclusive; above is inflating, below is not",
    )

    ok &= check(bc.prompts_per_env(metrics_row(0.5, (11, 11, 2))) ==
                {"cad-spec-L4": 11, "cad-spec-L2": 11, "cad-spec-L1-L3": 2},
                "prompt counts come from batch shares times prompts")
    bad = metrics_row(0.5)
    bad["batch/cad-spec-L4"] = 0.47
    ok &= check(refuses(bc.prompts_per_env, bad), "a share that is not a whole number of prompts is refused")

    scr = screening([8] * 15 + [0] * 15)
    res = bc.analyse(scr, [("run-a", "primary", metrics_row(0.5)), ("run-b", "second sample", metrics_row(0.55))])
    p = res["runs"][0]["environments"]["cad-spec-L4"]
    ok &= check(res["verdict"] == "BRIDGED" and p["reference"] == 0.5 and p["prompts"] == 10
                and p["observed_passes"] == 40 and p["count_consistent"] and res["corroboration_agrees"]
                and res["share_of_registered_l4_gain"] is None,
                "matching rates: BRIDGED, counts consistent, no share reported")
    ok &= check(res["pooled_l4"]["prompts"] == 20 and abs(res["pooled_l4"]["observed"] - 0.525) < 1e-12,
                "the pooled L4 value weights the two runs by their prompts")
    l13 = res["runs"][0]["environments"]["cad-spec-L1-L3"]
    ok &= check(l13["reference_groups"] == 12 and l13["prompts"] == 2, "L1+L3 pools both screening tiers")

    high = bc.analyse(scr, [("run-a", "primary", metrics_row(1.0)), ("run-b", "second sample", metrics_row(0.5))])
    ok &= check(high["verdict"] == "OPEN_INFLATING" and not high["corroboration_agrees"]
                and abs(high["share_of_registered_l4_gain"] - 50 / bc.REGISTERED_L4_GAIN) < 1e-9,
                "step 1 above the interval: OPEN_INFLATING with the share of the gain; disagreement is flagged")
    low = bc.analyse(scr, [("run-a", "primary", metrics_row(0.0)), ("run-b", "second sample", metrics_row(0.0))])
    ok &= check(low["verdict"] == "STACKS_DIFFER_NOT_INFLATING", "step 1 below the interval is not inflating")
    odd = bc.analyse(scr, [("run-a", "primary", metrics_row(0.503)), ("run-b", "second sample", metrics_row(0.5))])
    ok &= check(not odd["runs"][0]["environments"]["cad-spec-L4"]["count_consistent"],
                "a rate that is not a whole number of answers is flagged")
    ok &= check("| both runs pooled |" in bc.render(res) and "**Verdict: BRIDGED**" in bc.render(res),
                "the report has the verdict and the pooled row")

    good_meta = {"temperature": 0.7, "max_tokens": 2048, "rollouts": 8, "arm": "hint",
                 "extra_body": json.dumps({"chat_template_kwargs": {"enable_thinking": False}})}
    ok &= check(not refuses(bc.check_screening_settings, good_meta), "matched screening settings are accepted")
    ok &= check(refuses(bc.check_screening_settings, {**good_meta, "temperature": 0.0})
                and refuses(bc.check_screening_settings, {**good_meta, "arm": "control"}),
                "a greedy or no-cheat-sheet screening run is refused")

    def payload(**over: object) -> dict:
        req = {"temperature": 0.7, "max_tokens": 2048, "rollouts_per_example": 8, "enable_thinking": False,
               "environments": [{"name": n, "args": {"hints": True, "reward": "binary"}} for n in bc.ENVS]}
        req.update(over)
        return {"request": {"json": req}}

    ok &= check(not refuses(bc.check_payload_settings, payload(), "p"), "matched training settings are accepted")
    ok &= check(refuses(bc.check_payload_settings, payload(temperature=1.0), "p")
                and refuses(bc.check_payload_settings, payload(environments=[]), "p"),
                "a different temperature or a missing environment is refused")

    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "s.jsonl"
        rows = [{"meta": good_meta}, {"tier": "L4", "spec_id": "a", "reward": 1.0},
                {"tier": "L4", "spec_id": "a", "reward": 8 / 9}]
        f.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        ok &= check(refuses(bc.load_screening, f), "a screening file without a complete end marker is refused")
        f.write_text("\n".join(json.dumps(r) for r in [*rows, {"end": {"status": "complete"}}]), encoding="utf-8")
        _, groups = bc.load_screening(f)
        ok &= check(groups == {"L4": {"a": [1, 0]}}, "all-pass means reward exactly 1.0; partial credit is a fail")
        ok &= check(refuses(bc.reference_groups, groups, ["L4"]), "a screening group without 8 answers is refused")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
