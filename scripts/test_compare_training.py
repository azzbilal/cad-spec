"""Self-test for scripts/compare_training.py (runs in CI, no network).

    python scripts/test_compare_training.py

Synthetic base and adapter runs on the registered design (60 specs x L1 to
L4): the verdict rules, the worthwhile threshold, the regression flag, and
every refusal of a run that departs from its registration.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_training as ct  # noqa: E402

MODEL = "Qwen/Qwen3.5-9B"
EXTRA = '{"chat_template_kwargs": {"enable_thinking": false}, "top_p": 1.0}'


def check(ok: bool, what: str) -> bool:
    print(f"[{'ok ' if ok else 'BAD'}] {what}")
    return ok


def meta(model: str = MODEL, **over) -> dict:
    m = {"model": model, "split": "test", "test_split": {"seed": 20260927, "sha256": ct.TEST_SPLIT_SHA256},
         "temperature": 0.0, "max_tokens": 2048, "arm": "hint", "hints_source": "packaged",
         "system_prompt_sha256": "abc", "extra_body": EXTRA, "scorer_version": "0.4.0"}
    m.update(over)
    return m


def run(path: Path, m: dict, passes: dict[str, int], drop: dict | None = None) -> Path:
    """passes[tier] = number of the 60 specs that pass (the first n spec ids)."""
    rows = []
    for t in ct.TIERS:
        for i in range(ct.N_SPECS):
            rows.append({"tier": t, "spec_id": f"test-{i:03d}", "reward": 1.0 if i < passes[t] else 7 / 9,
                         "finish_reason": "stop", "api_error": None})
    if drop:
        rows = [r for r in rows if not (r["tier"] == drop["tier"] and r["spec_id"] == drop["spec_id"])]
    recs = [{"meta": m}, *rows, {"end": {"status": "complete"}}]
    path.write_text("\n".join(json.dumps(r) for r in recs), encoding="utf-8")
    return path


def main() -> int:
    ok = True
    base_pass = {"L1": 48, "L2": 38, "L3": 52, "L4": 26}
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        base = run(d / "base.jsonl", meta(), base_pass)

        good = run(d / "good.jsonl", meta(f"{MODEL}:ad1"), {"L1": 47, "L2": 46, "L3": 52, "L4": 36})
        rep = ct.analyse(base, good)
        ok &= check(rep["status"] == "analysed" and rep["H1"]["verdict"] == "confirmed"
                    and abs(rep["H1"]["difference"] - 18 / 120) < 1e-12 and rep["H1"]["worthwhile"],
                    "+18 of 120 pairs on L2+L4: confirmed and worthwhile (+15 points >= +10)")
        ok &= check(not rep["regression"]["L1"]["regression"] and rep["H2"]["verdict"] == "gain",
                    "L1 down 1 spec is not a regression; L4 +10 specs is a clear gain")

        small = run(d / "small.jsonl", meta(f"{MODEL}:ad2"), {"L1": 48, "L2": 40, "L3": 52, "L4": 28})
        rep = ct.analyse(base, small)
        ok &= check(rep["H1"]["verdict"] == "confirmed" and not rep["H1"]["worthwhile"],
                    "+4 of 120 on paired designs with no losses: confirmed but below the worthwhile gain")

        none = run(d / "none.jsonl", meta(f"{MODEL}:ad3"), base_pass)
        ok &= check(ct.analyse(base, none)["H1"]["verdict"] == "not confirmed",
                    "no change: not confirmed")

        regress = run(d / "reg.jsonl", meta(f"{MODEL}:ad4"), {"L1": 40, "L2": 46, "L3": 52, "L4": 36})
        rep = ct.analyse(base, regress)
        ok &= check(rep["regression"]["L1"]["regression"] and not rep["regression"]["L3"]["regression"],
                    "L1 down 8 of 60 (-13 points) is flagged as a regression, L3 is not")

        refusals = {
            "train split": run(d / "r1.jsonl", meta(f"{MODEL}:x", split="eval"), base_pass),
            "temperature": run(d / "r2.jsonl", meta(f"{MODEL}:x", temperature=0.7), base_pass),
            "max tokens": run(d / "r3.jsonl", meta(f"{MODEL}:x", max_tokens=1024), base_pass),
            "thinking on": run(d / "r4.jsonl", meta(f"{MODEL}:x", extra_body=None), base_pass),
            "other model": run(d / "r5.jsonl", meta("Qwen/Qwen3.5-4B:x"), base_pass),
            "other prompt": run(d / "r6.jsonl", meta(f"{MODEL}:x", system_prompt_sha256="zzz"), base_pass),
            "missing spec": run(d / "r7.jsonl", meta(f"{MODEL}:x"), base_pass,
                                drop={"tier": "L4", "spec_id": "test-005"}),
            "no adapter": run(d / "r8.jsonl", meta(MODEL), base_pass),
        }
        refused = {k: ct.analyse(base, p)["status"] == "refused" for k, p in refusals.items()}
        names = ", ".join(k for k, v in refused.items() if v)
        ok &= check(all(refused.values()), f"refused before any number: {names}")
        text = ct.markdown(ct.analyse(base, refusals["temperature"]))
        ok &= check("REFUSED" in text and "temperature 0.7" in text, "a refusal says why")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
