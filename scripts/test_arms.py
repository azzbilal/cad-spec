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


def _run(argv: list[str]) -> bool:
    """True if the runner accepted the arguments (ran), False if it refused them."""
    sys.argv = ["run_baseline.py", "--provider", "openai", "--model", "stub", "--tiers", "L1", "--quiet", *argv]
    try:
        rb.main()
        return True
    except SystemExit:
        return False


def runner_arms() -> bool:
    _, evals = make_splits()
    by_prompt = {prompt_for(s, "L1", "eval"): s for s in evals[:2]}
    calls: list[tuple[str, object]] = []

    def stub(args, prompt, seed):
        calls.append((args.system_prompt, prompt))
        if isinstance(prompt, str):
            return BROKEN, {"usage": {}, "finish_reason": "stop", "cost_usd": 0.001}
        spec = by_prompt[prompt[0]["content"]]
        # the second spec's retry is unpriced: its first attempt must still count
        cost = 0.002 if spec is evals[0] else None
        return reference_solution(spec), {"usage": {}, "finish_reason": "stop", "cost_usd": cost}

    rb.model_answer = stub
    ok = True
    hints = str(ROOT / "prompts" / "cadquery-hints.md")
    with tempfile.TemporaryDirectory() as tmp:
        fb, hint = Path(tmp) / "fb.jsonl", Path(tmp) / "hint.jsonl"
        _run(["--limit", "2", "--arm", "feedback", "--feedback-retries", "1", "--out", str(fb)])
        feedback_calls = list(calls)
        calls.clear()
        _run(["--limit", "1", "--arm", "hint", "--system-prompt-file", hints, "--out", str(hint)])
        fb_lines = [json.loads(x) for x in fb.read_text(encoding="utf-8").splitlines() if x.strip()]
        hint_meta = json.loads(hint.read_text(encoding="utf-8").splitlines()[0])["meta"]
        refusals = [
            _run(["--limit", "1", "--system-prompt-file", hints, "--out", str(Path(tmp) / "a.jsonl")]),
            _run(["--limit", "1", "--arm", "feedback", "--feedback-retries", "1", "--system-prompt-file", hints,
                  "--out", str(Path(tmp) / "b.jsonl")]),
            _run(["--limit", "1", "--arm", "hint", "--out", str(Path(tmp) / "c.jsonl")]),
            _run(["--limit", "1", "--arm", "magic", "--out", str(Path(tmp) / "d.jsonl")]),
        ]
    rows = [r for r in fb_lines if "tier" in r]
    retry_msg = feedback_calls[1][1][-1]["content"] if isinstance(feedback_calls[1][1], list) else ""
    ok &= check(hint_meta["arm"] == "hint" and "There is no `.holes()`" in hint_meta["system_prompt"],
                "hint arm: the cheat-sheet is appended to the system prompt and the arm is recorded")
    ok &= check(fb_lines[0]["meta"]["arm"] == "feedback" and "There is no" not in fb_lines[0]["meta"]["system_prompt"],
                "feedback arm: standard system prompt, arm recorded")
    ok &= check(len(rows) == 2 and all(r["reward"] == 1.0 and len(r["attempts"]) == 1 for r in rows),
                "code that does not build gets one retry; the fixed answer is scored; the attempt is kept")
    ok &= check("Running your code failed" in retry_msg and "has no attribute 'holes'" in retry_msg
                and "[raised in" not in retry_msg, "feedback shows the plain error, without the scorer's tag")
    ok &= check(abs(rows[0]["cost_usd"] - 0.003) < 1e-9 and abs(rows[1]["cost_usd"] - 0.001) < 1e-9,
                "retry costs add up, and an unpriced retry keeps the first attempt's cost")
    ok &= check(not any(refusals), "refused: changed task without an arm, hint+feedback together, "
                "hint without its file, an unregistered arm name")
    return ok


def runner_training_prep() -> bool:
    """0.4.1: packaged cheat-sheet, locked test split, token-priced costs, run selection."""
    import argparse

    import summarize_results as sr
    from cad_spec.tasks import TEST_SPLIT_SHA256

    def stub(args, prompt, seed):
        return "", {"usage": {}, "finish_reason": "stop", "cost_usd": 0.0}

    rb.model_answer = stub
    ok = True
    file_hints = str(ROOT / "prompts" / "cadquery-hints.md")
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        _run(["--limit", "1", "--arm", "hint", "--system-prompt-file", file_hints, "--out", str(t / "f.jsonl")])
        _run(["--limit", "1", "--arm", "hint", "--hints", "--out", str(t / "p.jsonl")])
        _run(["--limit", "1", "--split", "test", "--unlock-test", "--out", str(t / "t.jsonl")])
        refused = [
            _run(["--limit", "1", "--arm", "hint", "--hints", "--system-prompt-file", file_hints,
                  "--out", str(t / "x1.jsonl")]),
            _run(["--limit", "1", "--hints", "--out", str(t / "x2.jsonl")]),
            _run(["--limit", "1", "--split", "test", "--out", str(t / "x3.jsonl")]),
            _run(["--limit", "1", "--price-in", "0.2", "--out", str(t / "x4.jsonl")]),
        ]
        meta = {k: json.loads((t / f"{k}.jsonl").read_text(encoding="utf-8").splitlines()[0])["meta"]
                for k in ("f", "p", "t")}
    ok &= check(meta["p"]["system_prompt"] == meta["f"]["system_prompt"]
                and meta["p"]["hints_source"] == "package" and meta["f"]["hints_source"] == "file"
                and meta["p"]["system_prompt_sha256"] == meta["f"]["system_prompt_sha256"],
                "--hints (packaged) gives the exact hint-arm prompt of --system-prompt-file, fingerprinted")
    ok &= check(meta["t"]["split"] == "test" and meta["t"]["test_split"]["sha256"] == TEST_SPLIT_SHA256
                and meta["t"]["planned"]["spec_ids"] == ["test-0001"],
                "the locked test split runs only when unlocked, and records its fingerprint")
    ok &= check(not any(refused), "refused: --hints with a file, --hints outside the hint arm, "
                "the test split without --unlock-test, one price without the other")

    args = argparse.Namespace(price_in=0.2, price_out=0.6)
    ok &= check(rb._priced(args, 0.5, 1000, 1000) == (0.5, "provider")
                and rb._priced(args, None, 1_000_000, 500_000) == (0.2 + 0.3, "computed")
                and rb._priced(argparse.Namespace(), None, 10, 10) == (None, None),
                "cost: the provider's figure wins; otherwise tokens x price; unknown without prices")

    rows = [{"spec_id": "test-0001", "tier": "L1", "reward": 1.0, "built": True, "checks": {},
             "gates_passed": True, "cost_usd": 0.0, "finish_reason": "stop", "api_error": None,
             "completion_chars": 10, "error": None}]
    groups = {("r-test", "L1"): rows, ("r-eval", "L1"): [dict(rows[0], spec_id="gen-0000")]}
    metas = {"r-test": {"model": "m", "split": "test"}, "r-eval": {"model": "m", "split": "eval"}}
    chosen = sr.select_runs(metas, groups, {})
    ok &= check(all(v["run_id"] != "r-test" for v in chosen.values()),
                "board, failure analysis and label check never select a test-split run")
    return ok


def _arm_file(d: Path, name: str, arm: str, api_errors: int, specs: list[str] | None = None,
              system_prompt: str | None = None) -> Path:
    """A run file for one arm: `api_errors` answers fail with a CadQuery API error, the rest pass."""
    _, evals = make_splits()
    ids = specs or [s.id for s in evals]
    rows = []
    for t in ("L1", "L2", "L3", "L4"):
        for i, sid in enumerate(ids):
            fail = i < api_errors // 4 + (1 if t == "L1" and i == api_errors // 4 and api_errors % 4 else 0)
            rows.append({"run_id": name, "tier": t, "spec_id": sid, "rollout": 0, "reward": 0.0 if fail else 1.0,
                         "built": not fail, "gates_passed": True, "checks": {} if fail else {"R1": True},
                         "error": ("execution failed [raised in model code]: AttributeError: "
                                   "'Workplane' object has no attribute 'holes'") if fail else None,
                         "api_error": None, "finish_reason": "stop", "completion": "code"})
    meta = {"run_id": name, "model": "google/gemma-3-27b-it", "arm": arm, "split": "eval", "temperature": 0.0,
            "max_tokens": 1024, "feedback_retries": 1 if arm == "feedback" else 0,
            "system_prompt": system_prompt or ca.registered_system_prompt(arm),
            "planned": {"tiers": ["L1", "L2", "L3", "L4"], "spec_ids": ids, "rollouts": 1, "total": 4 * len(ids)}}
    path = d / f"{name}.jsonl"
    path.write_text("\n".join(json.dumps(x) for x in [{"meta": meta}, *rows, {"end": {"status": "complete"}}]) + "\n")
    return path


def analysis_joins_real_labels() -> bool:
    """Run files -> the real failure classifier -> the real analysis."""
    _, evals = make_splits()
    ok = True
    py, sc = sys.executable, ROOT / "scripts"
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        base = _arm_file(d, "20260101T000000Z-base", "first-shot", api_errors=20)
        hint = _arm_file(d, "20260102T000000Z-hint", "hint", api_errors=4)
        stale = d / "stale"
        subprocess.run([py, str(sc / "failure_modes.py"), str(base), "--out", str(stale)],
                       check=True, capture_output=True)
        subprocess.run([py, str(sc / "failure_modes.py"), str(base), str(hint), "--out", str(d)],
                       check=True, capture_output=True)
        cmp = subprocess.run([py, str(sc / "compare_arms.py"), str(base), str(hint),
                              "--failures", str(d / "failure-modes-0.4.0.json"), "--out", str(d / "r.md")],
                             capture_output=True, text=True)
        p1 = next((line for line in cmp.stdout.splitlines() if line.startswith("| P1 | google/gemma-3-27b-it")), "")
        evidence = p1.split("|")[4].strip() if p1 else cmp.stderr[-200:]
        ok &= check("held" in p1 and "17% -> 3%" in p1 and "unlabelled" not in cmp.stdout,
                    f"verdict computed from real labels joined by run id ({evidence})")
        refused = subprocess.run([py, str(sc / "compare_arms.py"), str(base), str(hint),
                                  "--failures", str(stale / "failure-modes-0.4.0.json"), "--out", str(d / "s.md")],
                                 capture_output=True, text=True)
        ok &= check(refused.returncode != 0 and "no failure label" in refused.stdout + refused.stderr,
                    "a label file that lacks the arm's run stops the analysis")
        short = _arm_file(d, "20260103T000000Z-hint", "hint", api_errors=4, specs=[s.id for s in evals[:25]])
        edited = _arm_file(d, "20260104T000000Z-fb", "feedback", api_errors=4, system_prompt="something else")
        subprocess.run([py, str(sc / "failure_modes.py"), str(base), str(short), str(edited), "--out", str(d)],
                       check=True, capture_output=True)
        out = subprocess.run([py, str(sc / "compare_arms.py"), str(base), str(short), str(edited),
                              "--failures", str(d / "failure-modes-0.4.0.json"), "--out", str(d / "t.md")],
                             capture_output=True, text=True).stdout
        ok &= check("| P1 | google/gemma-3-27b-it | no data |" in out and "held-out specs" in out,
                    "an arm missing held-out specs is excluded, not judged")
        ok &= check("| P2 | google/gemma-3-27b-it | no data |" in out and "system prompt differs" in out,
                    "an arm that departs from its registered condition is excluded, with the reason")
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
    results = [runner_arms(), runner_training_prep(), board_is_first_shot_only(), verdict_rules(),
               analysis_joins_real_labels()]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
