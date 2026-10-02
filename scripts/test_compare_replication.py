"""Self-test for scripts/compare_replication.py and the replication split (CI, no network).

    python scripts/test_compare_replication.py

Synthetic base and adapter runs on the registered design (60 specs x L1 to
L4): the three R1 verdicts, the consistency rule, the exact lower bound, the
failure listing and every refusal. Then the split itself: fingerprint, size,
disjointness from train, dev and test, and the held-out L3 wording.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_replication as cr  # noqa: E402
import compare_training as ct  # noqa: E402
import replication_split as rs  # noqa: E402
from cad_spec.tasks import make_splits, make_test_split, prompt_for, split_fingerprint  # noqa: E402

EXTRA = '{"chat_template_kwargs": {"enable_thinking": false}}'


def check(ok: bool, what: str) -> bool:
    print(f"[{'ok ' if ok else 'BAD'}] {what}")
    return ok


def meta(model: str, original: bool = False, **over) -> dict:
    m = {"model": model, "temperature": 0.0, "max_tokens": 2048, "arm": "hint", "hints_source": "package",
         "system_prompt_sha256": "abc", "extra_body": EXTRA, "scorer_version": "0.4.0",
         "package_version": "0.4.5", "base_url": cr.BASE_URL}
    if original:
        m |= {"split": "test", "test_split": {"seed": 20260927, "sha256": ct.TEST_SPLIT_SHA256}}
    else:
        m |= {"split": "replication",
              "replication_split": {"seed": rs.REPLICATION_SEED, "sha256": rs.REPLICATION_SPLIT_SHA256}}
    m.update(over)
    return m


def run(path: Path, m: dict, passes: dict[str, int], prefix: str = "rep", drop: str | None = None) -> Path:
    """passes[tier] = number of the 60 specs that pass (the first n spec ids)."""
    rows = []
    for t in ct.TIERS:
        for i in range(1, ct.N_SPECS + 1):
            ok = i <= passes[t]
            rows.append({"tier": t, "spec_id": f"{prefix}-{i:04d}", "reward": 1.0 if ok else 7 / 9,
                         "finish_reason": "stop", "api_error": None,
                         "checks": {"R5_hole_pattern": ok, "R1_length": True}})
    if drop:
        rows = [r for r in rows if not (r["tier"] == "L4" and r["spec_id"] == drop)]
    recs = [{"meta": m}, *rows, {"end": {"status": "complete"}}]
    path.write_text("\n".join(json.dumps(r) for r in recs), encoding="utf-8")
    return path


def main() -> int:
    ok = True
    base_pass = {"L1": 52, "L2": 50, "L3": 45, "L4": 22}
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        ob = run(d / "ob.jsonl", meta(cr.BASE_MODEL, original=True), base_pass, prefix="test")
        oa = run(d / "oa.jsonl", meta(cr.ADAPTER_MODEL, original=True),
                 {"L1": 60, "L2": 60, "L3": 59, "L4": 60}, prefix="test")
        base = run(d / "base.jsonl", meta(cr.BASE_MODEL), base_pass)

        def analyse(adapter: Path, b: Path = base) -> dict:
            return cr.analyse(b, adapter, ob, oa)

        same = run(d / "same.jsonl", meta(cr.ADAPTER_MODEL), {"L1": 60, "L2": 60, "L3": 59, "L4": 60})
        rep = analyse(same)
        ok &= check(rep["status"] == "analysed" and rep["R1"]["verdict"] == "replicated"
                    and abs(rep["R1"]["difference"] - 48 / 120) < 1e-12 and rep["R3"]["verdict"] == "consistent"
                    and abs(rep["R3"]["difference"]) < 1e-12,
                    "same outcome as the original: R1 replicated (+40 points), R3 consistent")
        ok &= check(rep["R4"]["pooled"] == {"pass": 120, "specs": 120, "lower95": rep["R4"]["pooled"]["lower95"]}
                    and abs(rep["R4"]["pooled"]["lower95"] - 0.025 ** (1 / 120)) < 1e-9
                    and abs(rep["R4"]["original"]["lower95"] - 0.025 ** (1 / 60)) < 1e-9,
                    "R4: 120/120 pooled gives the exact bound 0.025^(1/120), about 97.0%; 60/60 about 94.0%")
        fails = rep["adapter_failures"]
        ok &= check(len(fails) == 1 and fails[0]["tier"] == "L3" and fails[0]["spec_id"] == "rep-0060"
                    and fails[0]["failed_checks"] == ["R5_hole_pattern"] and fails[0]["base_also_fails"]
                    and rep["pairs"] == {"improved": 70, "worsened": 0},
                    "the one adapter failure is listed with its failed check and the base outcome")
        text = cr.markdown(rep)
        ok &= check("**R1 (L2 + L4, primary): REPLICATED.**" in text and "R3 (size against" in text
                    and "pooled 120/120, at least 97.0%" in text and "- L3 rep-0060: R5_hole_pattern" in text,
                    "the report states R1 to R4 and lists the failure")

        shrunk = run(d / "shrunk.jsonl", meta(cr.ADAPTER_MODEL), {"L1": 52, "L2": 55, "L3": 45, "L4": 37})
        rep = analyse(shrunk)
        ok &= check(rep["R1"]["verdict"] == "replicated" and rep["R3"]["verdict"] == "smaller",
                    "+16.7 points: replicated by the rule, and R3 says smaller than the original")
        small = run(d / "small.jsonl", meta(cr.ADAPTER_MODEL), {"L1": 52, "L2": 52, "L3": 45, "L4": 26})
        ok &= check(analyse(small)["R1"]["verdict"] == "smaller than worthwhile",
                    "+5 points with no losses: above 0 but below the worthwhile gain")
        none = run(d / "none.jsonl", meta(cr.ADAPTER_MODEL), base_pass)
        ok &= check(analyse(none)["R1"]["verdict"] == "not replicated", "no change: not replicated")
        regress = run(d / "reg.jsonl", meta(cr.ADAPTER_MODEL), {"L1": 44, "L2": 60, "L3": 45, "L4": 60})
        rep = analyse(regress)
        ok &= check(rep["regression"]["L1"]["regression"] and not rep["regression"]["L3"]["regression"],
                    "L1 down 8 of 60 is flagged as a regression")

        ok &= check(cr.exact_lower_bound(0, 10) == 0.0 and abs(cr.exact_lower_bound(59, 60) - 0.91059) < 2e-4,
                    "exact lower bound: 0 successes is 0; 59/60 is about 91.1%")
        ok &= check(cr.consistency([[1, 1]] * 20, [[0, 0]] * 20)["verdict"] == "smaller"
                    and cr.consistency([[0, 0]] * 20, [[1, 1]] * 20)["verdict"] == "larger",
                    "consistency: an interval entirely below 0 is smaller, above 0 is larger")

        full = {"L1": 60, "L2": 60, "L3": 60, "L4": 60}
        refusals = {
            "test split file": run(d / "r1.jsonl", meta(cr.ADAPTER_MODEL, original=True), full),
            "wrong fingerprint": run(d / "r2.jsonl", meta(cr.ADAPTER_MODEL, replication_split={"sha256": "x"}), full),
            "temperature": run(d / "r3.jsonl", meta(cr.ADAPTER_MODEL, temperature=0.7), full),
            "thinking on": run(d / "r4.jsonl", meta(cr.ADAPTER_MODEL, extra_body=None), full),
            "another adapter": run(d / "r5.jsonl", meta(cr.BASE_MODEL + ":other"), full),
            "other prompt": run(d / "r6.jsonl", meta(cr.ADAPTER_MODEL, system_prompt_sha256="zzz"), full),
            "missing spec": run(d / "r7.jsonl", meta(cr.ADAPTER_MODEL), full, drop="rep-0005"),
            "test spec ids": run(d / "r8.jsonl", meta(cr.ADAPTER_MODEL), full, prefix="test"),
            "other package": run(d / "r9.jsonl", meta(cr.ADAPTER_MODEL, package_version="0.4.6"), full),
            "other endpoint": run(d / "r10.jsonl", meta(cr.ADAPTER_MODEL, base_url="https://openrouter.ai/api/v1"),
                                  full),
        }
        refused = {k: analyse(p)["status"] == "refused" for k, p in refusals.items()}
        names = ", ".join(k for k, v in refused.items() if v)
        ok &= check(all(refused.values()), f"refused before any number: {names}")
        wrong_base = run(d / "wb.jsonl", meta("Qwen/Qwen3.5-4B"), base_pass)
        rep = analyse(same, wrong_base)
        ok &= check(rep["status"] == "refused" and "registered 'Qwen/Qwen3.5-9B'" in cr.markdown(rep),
                    "another base model is refused, and the refusal says why")

    specs = rs.make_replication_split()
    train, dev = make_splits()
    used = {rs._params(s) for s in train + dev + make_test_split()}
    ok &= check(split_fingerprint(specs) == rs.REPLICATION_SPLIT_SHA256 and len(specs) == ct.N_SPECS
                and {s.id for s in specs} == cr.SPEC_IDS,
                "the replication split matches its locked fingerprint: 60 specs, rep-0001 to rep-0060")
    ok &= check(len({rs._params(s) for s in specs}) == len(specs) and not used & {rs._params(s) for s in specs},
                "no replication spec shares its parameters with a train, dev or test spec, or with another")
    held_out = prompt_for(specs[0], "L3", rs.prompt_split("replication"))
    ok &= check(held_out == prompt_for(specs[0], "L3", "test") and held_out != prompt_for(specs[0], "L3", "train")
                and rs.prompt_split("eval") == "eval",
                "replication prompts use the held-out L3 wording, like the test split")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
