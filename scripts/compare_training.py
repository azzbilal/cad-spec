"""Pre-registered analysis of training run 1 (docs/experiments/training-run-1.md).

    python scripts/compare_training.py --base BASE.jsonl --adapter ADAPTER.jsonl \\
        --out results/training/run1/verdict

Both files are runner outputs on the LOCKED TEST SPLIT (60 specs, tiers L1 to
L4, greedy). The adapter file must come from the same model id plus the
adapter suffix (``Qwen/Qwen3.5-9B:<adapter_id>``). Before any number is
computed, both runs must match their registration: test split with the
registered fingerprint, temperature 0, 2,048 output tokens, the packaged
cheat-sheet (identical system prompt), thinking off, scorer 0.4.0, complete,
under 5% truncated, and exactly 60 specs once per tier. A run that departs
from this is refused with the reason, never analysed.

Verdicts (thresholds fixed at registration; do not change without a dated
amendment in the registration document):

- H1, primary: all-pass on L2 and L4 together, adapter minus base, paired by
  (tier, spec). 95% percentile bootstrap interval, resampling SPECS (each
  spec's L2 and L4 outcomes together), 10,000 resamples, seed 20261001.
  CONFIRMED if the lower bound is above 0. The gain is called WORTHWHILE if
  the point estimate is at least +10 points (the gain the test split was
  sized for: 84% power in simulation).
- H2, secondary: the same on L4 alone. Reported, not part of the claim.
- Regression: L1 and L3 each, a point-estimate drop of more than 10 points is
  flagged as a REGRESSION and reported next to the verdict.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.tasks import TEST_SPLIT_SHA256  # noqa: E402

TIERS = ("L1", "L2", "L3", "L4")
PRIMARY = ("L2", "L4")
SECONDARY = ("L4",)
REGRESSION_TIERS = ("L1", "L3")
N_SPECS = 60
MIN_WORTHWHILE = 0.10
REGRESSION_DROP = 0.10
BOOTSTRAP = 10_000
SEED = 20261001
MAX_TOKENS = 2048
SCORER = "0.4.0"
MAX_TRUNCATED = 0.05


def load(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
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


def conformity(meta: dict[str, Any], rows: list[dict[str, Any]], end: dict[str, Any]) -> list[str]:
    """Every way this run departs from its registration (empty = conforms)."""
    problems = []
    split = meta.get("test_split") or {}
    if meta.get("split") != "test" or split.get("sha256") != TEST_SPLIT_SHA256:
        problems.append("not the locked test split with the registered fingerprint")
    if meta.get("temperature") != 0.0:
        problems.append(f"temperature {meta.get('temperature')}, registered 0")
    if meta.get("max_tokens") != MAX_TOKENS:
        problems.append(f"max_tokens {meta.get('max_tokens')}, registered {MAX_TOKENS}")
    if meta.get("arm") != "hint" or meta.get("hints_source") is None:
        problems.append("not the hint arm with the packaged cheat-sheet")
    extra = meta.get("extra_body") or {}
    if isinstance(extra, str):  # the runner records --extra-body as given (a JSON string)
        try:
            extra = json.loads(extra)
        except ValueError:
            extra = {}
    thinking = ((extra or {}).get("chat_template_kwargs") or {}).get("enable_thinking")
    if thinking is not False:
        problems.append("thinking not switched off (enable_thinking false)")
    if meta.get("scorer_version") != SCORER:
        problems.append(f"scorer {meta.get('scorer_version')}, registered {SCORER}")
    if end.get("status") != "complete":
        problems.append(f"run status {end.get('status')!r}, registered complete")
    if rows and sum(r.get("finish_reason") == "length" for r in rows) / len(rows) >= MAX_TRUNCATED:
        problems.append("5% or more of answers truncated")
    if any(r.get("api_error") for r in rows):
        problems.append("API errors among the answers")
    seen: dict[str, list[str]] = {t: [] for t in TIERS}
    for r in rows:
        seen.setdefault(r["tier"], []).append(r["spec_id"])
    for t in TIERS:
        ids = seen.get(t, [])
        if len(ids) != N_SPECS or len(set(ids)) != N_SPECS:
            problems.append(f"tier {t}: {len(ids)} answers over {len(set(ids))} specs, registered {N_SPECS} once each")
    if set(seen) - set(TIERS):
        problems.append(f"unregistered tiers {sorted(set(seen) - set(TIERS))}")
    return problems


def outcomes(rows: list[dict[str, Any]]) -> dict[tuple[str, str], int]:
    return {(r["tier"], r["spec_id"]): int(r["reward"] == 1.0) for r in rows}


def paired(base: dict, adapter: dict, tiers: tuple[str, ...]) -> dict[str, Any]:
    """Point estimate and spec-resampled 95% interval of adapter minus base."""
    specs = sorted({s for (t, s) in base if t in tiers})
    per_spec = [[adapter[(t, s)] - base[(t, s)] for t in tiers] for s in specs]
    n = len(per_spec) * len(tiers)
    point = sum(sum(d) for d in per_spec) / n
    rng = random.Random(SEED)
    draws = []
    for _ in range(BOOTSTRAP):
        sample = [per_spec[rng.randrange(len(per_spec))] for _ in per_spec]
        draws.append(sum(sum(d) for d in sample) / n)
    draws.sort()
    return {
        "tiers": list(tiers),
        "base_all_pass": sum(base[(t, s)] for t in tiers for s in specs) / n,
        "adapter_all_pass": sum(adapter[(t, s)] for t in tiers for s in specs) / n,
        "difference": point,
        "ci95": [draws[int(0.025 * BOOTSTRAP)], draws[int(0.975 * BOOTSTRAP) - 1]],
        "pairs": n,
    }


def analyse(base_path: Path, adapter_path: Path) -> dict[str, Any]:
    bmeta, brows, bend = load(base_path)
    ameta, arows, aend = load(adapter_path)
    refused = {}
    for label, (m, r, e) in {"base": (bmeta, brows, bend), "adapter": (ameta, arows, aend)}.items():
        problems = conformity(m, r, e)
        if problems:
            refused[label] = problems
    base_model = str(bmeta.get("model"))
    if not str(ameta.get("model", "")).startswith(base_model + ":"):
        refused.setdefault("adapter", []).append(
            f"model {ameta.get('model')!r} is not the base model {base_model!r} plus an adapter suffix")
    if bmeta.get("system_prompt_sha256") != ameta.get("system_prompt_sha256"):
        refused.setdefault("adapter", []).append("system prompt differs from the base run")
    if refused:
        return {"status": "refused", "refused": refused}

    base, adapter = outcomes(brows), outcomes(arows)
    h1 = paired(base, adapter, PRIMARY)
    h2 = paired(base, adapter, SECONDARY)
    regression = {t: paired(base, adapter, (t,)) for t in REGRESSION_TIERS}
    h1["verdict"] = "confirmed" if h1["ci95"][0] > 0 else "not confirmed"
    h1["worthwhile"] = h1["difference"] >= MIN_WORTHWHILE
    h2["verdict"] = "gain" if h2["ci95"][0] > 0 else "no clear gain"
    for r in regression.values():
        r["regression"] = r["difference"] < -REGRESSION_DROP
    return {
        "status": "analysed",
        "base_model": base_model, "adapter_model": ameta.get("model"),
        "per_tier": {t: paired(base, adapter, (t,)) for t in TIERS},
        "H1": h1, "H2": h2, "regression": regression,
        "thresholds": {"min_worthwhile": MIN_WORTHWHILE, "regression_drop": REGRESSION_DROP,
                       "bootstrap": BOOTSTRAP, "seed": SEED},
    }


def _p(x: float) -> str:
    return f"{100 * x:+.1f}" if x else "+0.0"


def markdown(rep: dict[str, Any]) -> str:
    if rep["status"] == "refused":
        lines = ["# Training run 1: analysis REFUSED", ""]
        for label, problems in rep["refused"].items():
            lines += [f"- {label}: {p}" for p in problems]
        return "\n".join(lines) + "\n"
    h1, h2 = rep["H1"], rep["H2"]
    lines = [
        "# Training run 1: pre-registered verdict",
        "",
        f"Base `{rep['base_model']}` vs adapter `{rep['adapter_model']}`, locked test split, greedy.",
        "",
        "| Tier | Base all-pass | Adapter all-pass | Difference (points) | 95% interval |",
        "|---|---|---|---|---|",
    ]
    for t, s in rep["per_tier"].items():
        lines.append(f"| {t} | {100 * s['base_all_pass']:.1f}% | {100 * s['adapter_all_pass']:.1f}% | "
                     f"{_p(s['difference'])} | [{_p(s['ci95'][0])}, {_p(s['ci95'][1])}] |")
    lines += [
        "",
        f"**H1 (L2 + L4, primary): {h1['verdict'].upper()}.** Difference {_p(h1['difference'])} points, "
        f"95% interval [{_p(h1['ci95'][0])}, {_p(h1['ci95'][1])}], {h1['pairs']} pairs. "
        f"{'Worthwhile' if h1['worthwhile'] else 'Below the worthwhile gain'} "
        f"(registered minimum +{100 * MIN_WORTHWHILE:.0f} points).",
        "",
        f"H2 (L4 alone, secondary): {h2['verdict']}, {_p(h2['difference'])} points "
        f"[{_p(h2['ci95'][0])}, {_p(h2['ci95'][1])}].",
        "",
    ]
    for t, r in rep["regression"].items():
        flag = "REGRESSION" if r["regression"] else "no regression"
        lines.append(f"Regression check {t}: {flag} ({_p(r['difference'])} points; flagged below "
                     f"-{100 * REGRESSION_DROP:.0f}).")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--adapter", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None, help="write OUT.md and OUT.json")
    args = ap.parse_args(argv)
    rep = analyse(args.base, args.adapter)
    text = markdown(rep)
    sys.stdout.write(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.with_suffix(".md").write_text(text, encoding="utf-8")
        args.out.with_suffix(".json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    return 0 if rep["status"] == "analysed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
