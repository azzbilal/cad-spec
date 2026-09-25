# ruff: noqa: E402
"""Self-test for the hint and feedback arms (runs in CI, no network).

    python scripts/test_arms.py

1. The runner, with the model replaced by a stub that first writes code that
   does not build and then fixes it once it sees the error: the hint text
   reaches the system prompt, feedback shows the plain error (no scorer tag),
   every attempt is recorded, costs add up, and a run that changes the task
   must be named with --arm.
2. The leaderboard ranks first-shot runs only.
3. The pre-registered verdict rules in compare_arms.py.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

import compare_arms as ca
import run_baseline as rb
from cad_spec.tasks import make_splits, prompt_for, reference_solution

BROKEN = "```python\nimport cadquery as cq\nresult = cq.Workplane('XY').box(10, 10, 2).holes(3)\n```"


def check(ok: bool, what: str) -> bool:
    print(f"[{'ok ' if ok else 'BAD'}] {what}")
    return ok


def runner_feedback_and_hint() -> bool:
    _, evals = make_splits()
    by_prompt = {prompt_for(s, "L1", "eval"): s for s in evals[:2]}
    calls: list[tuple[str, object]] = []

    def stub(args, prompt, seed):
        calls.append((args.system_prompt, prompt))
        if isinstance(prompt, str):
            return BROKEN, {"usage": {}, "finish_reason": "stop", "cost_usd": 0.001}
        spec = by_prompt[prompt[0]["content"]]
        return reference_solution(spec), {"usage": {}, "finish_reason": "stop", "cost_usd": 0.002}

    rb.model_answer = stub
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "run.jsonl"
        sys.argv = ["run_baseline.py", "--provider", "openai", "--model", "stub", "--tiers", "L1", "--limit", "2",
                    "--arm", "feedback", "--feedback-retries", "1",
                    "--system-prompt-file", str(ROOT / "prompts" / "cadquery-hints.md"), "--out", str(out), "--quiet"]
        rb.main()
        lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    meta = lines[0]["meta"]
    rows = [r for r in lines if "tier" in r]
    retry_msg = calls[1][1][-1]["content"] if len(calls) > 1 and isinstance(calls[1][1], list) else ""
    ok &= check(meta["arm"] == "feedback" and "There is no `.holes()`" in meta["system_prompt"],
                "hint text is appended to the system prompt and the arm is recorded")
    ok &= check(len(rows) == 2 and all(r["reward"] == 1.0 and len(r["attempts"]) == 1 for r in rows),
                "code that does not build gets one retry; the fixed answer is scored; the attempt is kept")
    ok &= check("Running your code failed" in retry_msg and "has no attribute 'holes'" in retry_msg
                and "[raised in" not in retry_msg, "feedback shows the plain error, without the scorer's tag")
    ok &= check(all(abs(r["cost_usd"] - 0.003) < 1e-9 for r in rows), "the retry's cost is added to the answer's")
    sys.argv = ["run_baseline.py", "--provider", "openai", "--model", "stub", "--tiers", "L1", "--limit", "1",
                "--system-prompt-file", str(ROOT / "prompts" / "cadquery-hints.md"), "--quiet"]
    try:
        rb.main()
        refused = False
    except SystemExit:
        refused = True
    ok &= check(refused, "a changed task without --arm is refused")
    return ok


def board_is_first_shot_only() -> bool:
    _, evals = make_splits()
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for name, arm in (("first", None), ("hinted", "hint")):
            rows = [{"run_id": name, "tier": t, "spec_id": s.id, "rollout": 0, "reward": 1.0, "built": True,
                     "gates_passed": True, "checks": {"R1": True}, "finish_reason": "stop"}
                    for t in ("L0", "L1", "L2", "L3", "L4") for s in evals]
            meta = {"run_id": name, "model": "m", "planned": {"tiers": ["L0", "L1", "L2", "L3", "L4"],
                                                             "spec_ids": [s.id for s in evals], "rollouts": 1}}
            if arm:
                meta["arm"] = arm
            end = {"end": {"status": "complete"}}
            (d / f"{name}.jsonl").write_text("\n".join(json.dumps(x) for x in [{"meta": meta}, *rows, end]) + "\n")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "leaderboard.py"), *map(str, d.glob("*.jsonl")),
                        "--out", str(d / "lb")], check=True, capture_output=True)
        md = (d / "lb" / "leaderboard.md").read_text()
    return check("| m |" in md and "[hint]" not in md, "the leaderboard ranks first-shot runs only")


def verdict_rules() -> bool:
    def arm(counts: dict[str, int]) -> dict[tuple[str, str], str]:
        labels = [lab for lab, n in counts.items() for _ in range(n)]
        labels += ["pass"] * (120 - len(labels))
        return {(f"L{1 + i // 30}", f"s{i % 30}"): lab for i, lab in enumerate(labels)}

    data = {m: {} for m in ca.ALL_MODELS}
    for m in ca.KNOWLEDGE_MODELS:
        data[m] = {ca.BASE: arm({ca.API: 20, ca.STACKED: 20}),
                   ca.HINT: arm({ca.API: 5, ca.STACKED: 5}),          # 33% -> 8%: P1 held
                   ca.FEEDBACK: arm({ca.API: 5, ca.STACKED: 20})}     # API halved, stacking kept: P2 held
    data["openai/gpt-4o-mini"] = {ca.BASE: arm({"margin applied twice": 15}),
                                  ca.HINT: arm({"margin applied twice": 14}),
                                  ca.FEEDBACK: arm({"margin applied twice": 2})}  # -11 points: P3 fails
    got = ca.summary(ca.verdicts(data))
    ok = check(got == {"P1": "confirmed", "P2": "confirmed", "P3": "not confirmed"},
               f"verdicts follow the pre-registered thresholds ({got})")
    data["mistralai/codestral-2508"][ca.FEEDBACK] = arm({ca.API: 5, ca.STACKED: 10})  # stacking halved
    ok &= check(ca.summary(ca.verdicts(data))["P2"] == "not confirmed",
                "P2 fails when feedback also removes stacking")
    del data["meta-llama/llama-3.3-70b-instruct"][ca.HINT]
    ok &= check(ca.summary(ca.verdicts(data))["P1"] == "incomplete", "a missing arm makes a prediction incomplete")
    return ok


def main() -> int:
    results = [runner_feedback_and_hint(), board_is_first_shot_only(), verdict_rules()]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
