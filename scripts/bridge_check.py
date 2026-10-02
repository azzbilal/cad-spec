"""Serving-route bridge check for training run 1 (frozen rule, no paid call).

    python scripts/bridge_check.py --out results/training/run1/bridge-check

Question: the registered evaluation served the base model and the adapter
through different Prime routes. Could a difference between the two stacks,
rather than training, explain the jump on L4? This script compares the
all-pass rate of the nearly untrained model inside the TRAINING stack (step 1
of the archived run metrics) with the BASE ROUTE at matched sampling settings
(the pre-training screening file: temperature 0.7, 8 samples per spec,
2,048 tokens, thinking off, cheat-sheet on).

Rule, registered in docs/experiments/training-run-1.md before any step-1
reward value was read:

- observed: `train/<env>/all/metrics/all_pass_reward/mean` at step 1;
- reference: the screening answers of the same tier(s), grouped by spec;
- interval: resample whole spec groups with replacement, as many groups as
  step 1 has prompts of that environment, 10,000 draws, fixed seed; the 2.5th
  and 97.5th percentiles of the resampled all-pass rate form a 95% predictive
  interval for "same model, same settings";
- verdict on L4 of the training run (primary): inside the interval is
  BRIDGED; above is OPEN_INFLATING; below is STACKS_DIFFER_NOT_INFLATING.

The smoke run with identical settings, L2 and L1+L3, and the pooled L4 value
are reported as corroboration and do not change the verdict. The script
refuses to run when the sampling settings of the three sources differ.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RUN1 = ROOT / "results" / "training" / "run1"
SCREENING = ROOT / "results" / "training" / "screening" / "qwen3.5-9b-t0.7-x8-2k.jsonl"

# (run id, role, archived create request)
RUNS: list[tuple[str, str, str]] = [
    ("mk9qcuq2dsckzrf68gycyqls", "primary", "payload-cad-spec-9b.json"),
    ("k3rwpbbk5sio4936onuai7ok", "second sample", "payload-cad-spec-9b-smoke.json"),
]
# training environment name -> screening tiers it draws from
ENVS: dict[str, list[str]] = {
    "cad-spec-L4": ["L4"],
    "cad-spec-L2": ["L2"],
    "cad-spec-L1-L3": ["L1", "L3"],
}
PRIMARY_ENV = "cad-spec-L4"
STEP = 1
SEED = 20261002
DRAWS = 10_000
K = 8  # samples per prompt, in screening and in training
SETTINGS = {"temperature": 0.7, "max_tokens": 2048, "rollouts": K, "thinking": False}
REGISTERED_L4_GAIN = 63.3  # points, results/training/run1/verdict.md


class RefusalError(Exception):
    """The inputs do not match the registered comparison."""


def load_screening(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, list[int]]]]:
    """Return (meta, tier -> spec id -> list of 0/1 all-pass flags)."""
    meta: dict[str, Any] = {}
    groups: dict[str, dict[str, list[int]]] = {}
    complete = False
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            if "meta" in row:
                meta = row["meta"]
            elif "end" in row:
                complete = row["end"].get("status") == "complete"
            elif "tier" in row:
                groups.setdefault(row["tier"], {}).setdefault(row["spec_id"], []).append(
                    1 if row["reward"] == 1.0 else 0
                )
    if not complete:
        raise RefusalError(f"{path.name}: run is not marked complete")
    return meta, groups


def check_screening_settings(meta: dict[str, Any]) -> None:
    extra = json.loads(meta.get("extra_body") or "{}")
    thinking = extra.get("chat_template_kwargs", {}).get("enable_thinking")
    got = {
        "temperature": meta.get("temperature"),
        "max_tokens": meta.get("max_tokens"),
        "rollouts": meta.get("rollouts"),
        "thinking": thinking,
    }
    if got != SETTINGS:
        raise RefusalError(f"screening settings {got} differ from {SETTINGS}")
    if meta.get("arm") != "hint":
        raise RefusalError("screening run is not the cheat-sheet (hint) arm")


def check_payload_settings(payload: dict[str, Any], name: str) -> None:
    req = payload["request"]["json"]
    got = {
        "temperature": req.get("temperature"),
        "max_tokens": req.get("max_tokens"),
        "rollouts": req.get("rollouts_per_example"),
        "thinking": req.get("enable_thinking"),
    }
    if got != SETTINGS:
        raise RefusalError(f"{name}: training settings {got} differ from {SETTINGS}")
    envs = {e["name"]: e["args"] for e in req.get("environments", [])}
    for env in ENVS:
        args = envs.get(env)
        if args is None or args.get("hints") is not True or args.get("reward") != "binary":
            raise RefusalError(f"{name}: environment {env} is not cheat-sheet + binary reward")


def predictive_interval(groups: list[list[int]], m: int, seed: int, draws: int = DRAWS) -> tuple[float, float]:
    """95% interval of the all-pass rate of m spec groups resampled with replacement."""
    if m < 1 or not groups:
        raise RefusalError("no groups to resample")
    rates = [sum(g) / len(g) for g in groups]
    rng = random.Random(seed)
    n = len(rates)
    sims = sorted(sum(rates[rng.randrange(n)] for _ in range(m)) / m for _ in range(draws))
    return sims[int(0.025 * draws)], sims[int(0.975 * draws) - 1]


def classify(observed: float, lo: float, hi: float) -> str:
    if observed > hi:
        return "OPEN_INFLATING"
    if observed < lo:
        return "STACKS_DIFFER_NOT_INFLATING"
    return "BRIDGED"


def step_row(metrics: dict[str, Any], step: int) -> dict[str, Any]:
    rows = [r for r in metrics["metrics"] if r.get("step") == step]
    if len(rows) != 1:
        raise RefusalError(f"expected exactly one row for step {step}, found {len(rows)}")
    return rows[0]


def prompts_per_env(row: dict[str, Any]) -> dict[str, int]:
    """Prompts generated per environment at this step (batch share x prompts)."""
    tasks = row["progress/tasks"]
    out: dict[str, int] = {}
    for env in ENVS:
        exact = row[f"batch/{env}"] * tasks
        if abs(exact - round(exact)) > 1e-6:
            raise RefusalError(f"batch share of {env} is not a whole number of prompts ({exact})")
        out[env] = round(exact)
    if sum(out.values()) != round(tasks):
        raise RefusalError(f"per-environment prompts {out} do not add up to {tasks}")
    return out


def reference_groups(groups: dict[str, dict[str, list[int]]], tiers: list[str]) -> list[list[int]]:
    out: list[list[int]] = []
    for tier in tiers:
        for spec_id in sorted(groups.get(tier, {})):
            g = groups[tier][spec_id]
            if len(g) != K:
                raise RefusalError(f"screening group {tier}/{spec_id} has {len(g)} answers, expected {K}")
            out.append(g)
    if not out:
        raise RefusalError(f"no screening groups for {tiers}")
    return out


def compare(observed: float, m: int, ref: list[list[int]], seed: int) -> dict[str, Any]:
    ref_rate = sum(sum(g) for g in ref) / sum(len(g) for g in ref)
    lo, hi = predictive_interval(ref, m, seed)
    passes = observed * m * K
    return {
        "prompts": m,
        "answers": m * K,
        "observed": observed,
        "observed_passes": round(passes),
        "count_consistent": abs(passes - round(passes)) < 1e-6,
        "reference": ref_rate,
        "reference_groups": len(ref),
        "interval95": [lo, hi],
        "difference_points": 100 * (observed - ref_rate),
        "position": classify(observed, lo, hi),
    }


def analyse(
    screening: dict[str, dict[str, list[int]]],
    runs: list[tuple[str, str, dict[str, Any]]],
) -> dict[str, Any]:
    """runs: (run id, role, step-1 metrics row). Seeds follow a fixed order."""
    out: dict[str, Any] = {"runs": [], "seed": SEED, "draws": DRAWS, "step": STEP}
    seed = SEED
    pooled_m = 0
    pooled_pass = 0.0
    for run_id, role, row in runs:
        m_by_env = prompts_per_env(row)
        envs: dict[str, Any] = {}
        for env, tiers in ENVS.items():
            observed = row[f"train/{env}/all/metrics/all_pass_reward/mean"]
            envs[env] = compare(observed, m_by_env[env], reference_groups(screening, tiers), seed)
            seed += 1
        pooled_m += m_by_env[PRIMARY_ENV]
        pooled_pass += envs[PRIMARY_ENV]["observed"] * m_by_env[PRIMARY_ENV]
        out["runs"].append({"run_id": run_id, "role": role, "environments": envs})
    out["pooled_l4"] = compare(
        pooled_pass / pooled_m, pooled_m, reference_groups(screening, ENVS[PRIMARY_ENV]), seed
    )
    primary = next(r for r in out["runs"] if r["role"] == "primary")["environments"][PRIMARY_ENV]
    out["verdict"] = primary["position"]
    out["share_of_registered_l4_gain"] = (
        primary["difference_points"] / REGISTERED_L4_GAIN if out["verdict"] == "OPEN_INFLATING" else None
    )
    others = [r["environments"][PRIMARY_ENV]["position"] for r in out["runs"] if r["role"] != "primary"]
    others.append(out["pooled_l4"]["position"])
    out["corroboration_agrees"] = all(p == out["verdict"] for p in others)
    return out


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Serving-route bridge check (training run 1)",
        "",
        f"Frozen rule: `scripts/bridge_check.py`, step {result['step']}, seed {result['seed']}, "
        f"{result['draws']:,} draws. Reference: `results/training/screening/{SCREENING.name}` "
        "(base route, temperature 0.7, 8 samples per spec, 2,048 tokens, thinking off, cheat-sheet).",
        "",
        f"**Verdict: {result['verdict']}** (L4 of the training run). "
        f"Corroboration agrees: {'yes' if result['corroboration_agrees'] else 'no'}.",
        "",
        "| Run | Environment | Prompts | Answers | Training stack, step 1 | Base route | 95% interval | Position |",
        "|---|---|---|---|---|---|---|---|",
    ]

    def row(label: str, env: str, c: dict[str, Any]) -> str:
        lo, hi = c["interval95"]
        return (
            f"| {label} | {env} | {c['prompts']} | {c['answers']} | {_pct(c['observed'])} | "
            f"{_pct(c['reference'])} | [{_pct(lo)}, {_pct(hi)}] | {c['position']} |"
        )

    for run in result["runs"]:
        for env, c in run["environments"].items():
            lines.append(row(f"`{run['run_id']}` ({run['role']})", env, c))
    lines.append(row("both runs pooled", PRIMARY_ENV, result["pooled_l4"]))
    if result["share_of_registered_l4_gain"] is not None:
        lines += [
            "",
            f"Share of the registered +{REGISTERED_L4_GAIN} point L4 gain that a stack difference "
            f"could account for: {_pct(result['share_of_registered_l4_gain'])}.",
        ]
    flagged = [
        f"{run['run_id']}/{env}"
        for run in result["runs"]
        for env, c in run["environments"].items()
        if not c["count_consistent"]
    ]
    lines += [
        "",
        "Counts: " + ("every observed rate is a whole number of passing answers." if not flagged else
                      "rates that are not a whole number of passing answers: " + ", ".join(flagged) + "."),
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True, help="output path without extension")
    args = ap.parse_args(argv)
    try:
        meta, screening = load_screening(SCREENING)
        check_screening_settings(meta)
        runs = []
        for run_id, role, payload_name in RUNS:
            payload = json.loads((RUN1 / payload_name).read_text(encoding="utf-8"))
            check_payload_settings(payload, payload_name)
            metrics = json.loads((RUN1 / "snapshots" / run_id / "metrics.json").read_text(encoding="utf-8"))
            runs.append((run_id, role, step_row(metrics, STEP)))
        result = analyse(screening, runs)
    except RefusalError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    result["screening"] = {"file": SCREENING.name, "run_id": meta.get("run_id"), "base_url": meta.get("base_url")}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.with_suffix(".json").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(result, indent=2) + "\n")
    text = render(result)
    with args.out.with_suffix(".md").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
