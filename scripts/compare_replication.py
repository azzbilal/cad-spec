"""Pre-registered analysis of replication 1 (docs/experiments/replication-1.md).

    python scripts/compare_replication.py --base BASE.jsonl --adapter ADAPTER.jsonl \\
        --out results/training/replication1/verdict

Both files are runner outputs on the REPLICATION SPLIT (60 fresh specs, tiers
L1 to L4, greedy), for the base model and for the frozen run 1 adapter. The
paired test, its bootstrap, its seed and every conformity rule are imported
unchanged from the frozen scripts/compare_training.py; this script only adds
what is specific to a replication. A run that departs from the registration
is refused with the reason, never analysed.

Verdicts (thresholds fixed at registration; do not change without a dated
amendment in the registration document):

- R1, primary: all-pass on L2 and L4 together, adapter minus base, the run 1
  test (paired by tier and spec, specs resampled, 10,000 resamples, seed
  20261001). REPLICATED if the lower bound of the 95% interval is above 0 AND
  the point estimate is at least +10 points. SMALLER THAN WORTHWHILE if the
  lower bound is above 0 but the point estimate is below +10. NOT REPLICATED
  otherwise.
- R2, secondary: the same on L4 alone. Reported, not part of the claim.
- R3, consistency of size: the L2 + L4 gain on the replication split minus the
  gain on the original test split. 95% percentile interval, specs of each
  split resampled independently, 10,000 resamples, seed 20261004. CONSISTENT
  if the interval contains 0, SMALLER if it lies below 0, LARGER if above.
- R4, ceiling: specs where the adapter passes both L2 and L4, pooled over the
  original test split and the replication split (120 specs), with the exact
  (Clopper-Pearson) two-sided 95% lower bound. Reported, no threshold.
- Regression: L1 and L3 each, a point-estimate drop of more than 10 points is
  flagged as a REGRESSION.
- Every adapter failure is listed with its failed checks and whether the base
  model fails the same task.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_training as ct  # noqa: E402
from replication_split import REPLICATION_SPLIT_SHA256  # noqa: E402

BASE_MODEL = "Qwen/Qwen3.5-9B"
ADAPTER_MODEL = "Qwen/Qwen3.5-9B:xfisiyo5vlhn0ys65sf4uad7"  # frozen: the run 1 end-of-run adapter
PACKAGE = "0.4.5"
BASE_URL = "https://api.pinference.ai/api/v1"
ORIGINAL_BASE = ROOT / "results" / "training" / "run1" / "eval" / "base-test.jsonl"
ORIGINAL_ADAPTER = ROOT / "results" / "training" / "run1" / "eval" / "adapter-test.jsonl"
CONSISTENCY_SEED = 20261004
SPEC_IDS = frozenset(f"rep-{i:04d}" for i in range(1, ct.N_SPECS + 1))


def conformity(meta: dict[str, Any], rows: list[dict[str, Any]], end: dict[str, Any]) -> list[str]:
    """Every way this run departs from the replication's registration (empty = conforms)."""
    problems = []
    split = meta.get("replication_split") or {}
    if meta.get("split") != "replication" or split.get("sha256") != REPLICATION_SPLIT_SHA256:
        problems.append("not the replication split with the registered fingerprint")
    # Every other rule is the frozen run 1 rule, applied as written there.
    as_run1 = {**meta, "split": "test", "test_split": {"sha256": ct.TEST_SPLIT_SHA256}}
    problems += ct.conformity(as_run1, rows, end)
    if {r["spec_id"] for r in rows} != SPEC_IDS:
        problems.append("spec ids are not exactly rep-0001 to rep-0060")
    if meta.get("package_version") != PACKAGE:
        problems.append(f"cad-spec {meta.get('package_version')}, registered {PACKAGE}")
    if meta.get("base_url") != BASE_URL:
        problems.append(f"endpoint {meta.get('base_url')}, registered {BASE_URL}")
    return problems


def consistency(orig: list[list[int]], rep: list[list[int]]) -> dict[str, Any]:
    """Replication gain minus original gain, specs of each split resampled independently."""

    def mean(per_spec: list[list[int]]) -> float:
        return sum(sum(d) for d in per_spec) / (len(per_spec) * len(per_spec[0]))

    rng = random.Random(CONSISTENCY_SEED)
    draws = []
    for _ in range(ct.BOOTSTRAP):
        o = [orig[rng.randrange(len(orig))] for _ in orig]
        r = [rep[rng.randrange(len(rep))] for _ in rep]
        draws.append(mean(r) - mean(o))
    draws.sort()
    lo, hi = draws[int(0.025 * ct.BOOTSTRAP)], draws[int(0.975 * ct.BOOTSTRAP) - 1]
    verdict = "smaller" if hi < 0 else "larger" if lo > 0 else "consistent"
    return {"original_gain": mean(orig), "replication_gain": mean(rep),
            "difference": mean(rep) - mean(orig), "ci95": [lo, hi], "verdict": verdict}


def exact_lower_bound(k: int, n: int, alpha: float = 0.05) -> float:
    """Clopper-Pearson two-sided lower bound for k successes out of n."""
    if k <= 0:
        return 0.0

    def tail(p: float) -> float:  # P(X >= k) for X ~ Binomial(n, p)
        return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))

    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if tail(mid) < alpha / 2:
            lo = mid
        else:
            hi = mid
    return lo


def per_spec_diffs(base: dict, adapter: dict, tiers: tuple[str, ...]) -> list[list[int]]:
    specs = sorted({s for (t, s) in base if t in tiers})
    return [[adapter[(t, s)] - base[(t, s)] for t in tiers] for s in specs]


def both_pass(adapter: dict, tiers: tuple[str, ...]) -> tuple[int, int]:
    specs = sorted({s for (t, s) in adapter if t in tiers})
    return sum(all(adapter[(t, s)] for t in tiers) for s in specs), len(specs)


def analyse(base_path: Path, adapter_path: Path,
            orig_base_path: Path = ORIGINAL_BASE, orig_adapter_path: Path = ORIGINAL_ADAPTER) -> dict[str, Any]:
    bmeta, brows, bend = ct.load(base_path)
    ameta, arows, aend = ct.load(adapter_path)
    refused: dict[str, list[str]] = {}
    for label, (m, r, e) in {"base": (bmeta, brows, bend), "adapter": (ameta, arows, aend)}.items():
        problems = conformity(m, r, e)
        if problems:
            refused[label] = problems
    if bmeta.get("model") != BASE_MODEL:
        refused.setdefault("base", []).append(f"model {bmeta.get('model')!r}, registered {BASE_MODEL!r}")
    if ameta.get("model") != ADAPTER_MODEL:
        refused.setdefault("adapter", []).append(f"model {ameta.get('model')!r}, registered {ADAPTER_MODEL!r}")

    # The original evaluation, read from the repository and checked by its own frozen rules.
    obmeta, obrows, obend = ct.load(orig_base_path)
    oameta, oarows, oaend = ct.load(orig_adapter_path)
    for label, (m, r, e) in {"original base": (obmeta, obrows, obend),
                             "original adapter": (oameta, oarows, oaend)}.items():
        problems = ct.conformity(m, r, e)
        if problems:
            refused[label] = problems
    prompts = {m.get("system_prompt_sha256") for m in (bmeta, ameta, obmeta, oameta)}
    if len(prompts) != 1:
        refused.setdefault("adapter", []).append("system prompt differs between the four runs")
    if refused:
        return {"status": "refused", "refused": refused}

    base, adapter = ct.outcomes(brows), ct.outcomes(arows)
    obase, oadapter = ct.outcomes(obrows), ct.outcomes(oarows)
    r1 = ct.paired(base, adapter, ct.PRIMARY)
    r2 = ct.paired(base, adapter, ct.SECONDARY)
    confirmed = r1["ci95"][0] > 0
    worthwhile = r1["difference"] >= ct.MIN_WORTHWHILE
    r1["verdict"] = ("replicated" if confirmed and worthwhile
                     else "smaller than worthwhile" if confirmed else "not replicated")
    r2["verdict"] = "gain" if r2["ci95"][0] > 0 else "no clear gain"
    regression = {t: ct.paired(base, adapter, (t,)) for t in ct.REGRESSION_TIERS}
    for r in regression.values():
        r["regression"] = r["difference"] < -ct.REGRESSION_DROP
    r3 = consistency(per_spec_diffs(obase, oadapter, ct.PRIMARY), per_spec_diffs(base, adapter, ct.PRIMARY))
    k_rep, n_rep = both_pass(adapter, ct.PRIMARY)
    k_orig, n_orig = both_pass(oadapter, ct.PRIMARY)
    r4 = {
        "replication": {"pass": k_rep, "specs": n_rep, "lower95": exact_lower_bound(k_rep, n_rep)},
        "original": {"pass": k_orig, "specs": n_orig, "lower95": exact_lower_bound(k_orig, n_orig)},
        "pooled": {"pass": k_rep + k_orig, "specs": n_rep + n_orig,
                   "lower95": exact_lower_bound(k_rep + k_orig, n_rep + n_orig)},
    }
    by_key = {(r["tier"], r["spec_id"]): r for r in arows}
    failures = [
        {"tier": t, "spec_id": s, "base_also_fails": base[(t, s)] == 0,
         "failed_checks": sorted(k for k, v in (by_key[(t, s)].get("checks") or {}).items() if v is False),
         "finish_reason": by_key[(t, s)].get("finish_reason")}
        for (t, s), v in sorted(adapter.items()) if v == 0
    ]
    return {
        "status": "analysed", "base_model": BASE_MODEL, "adapter_model": ADAPTER_MODEL,
        "per_tier": {t: ct.paired(base, adapter, (t,)) for t in ct.TIERS},
        "R1": r1, "R2": r2, "R3": r3, "R4": r4, "regression": regression,
        "adapter_failures": failures,
        "pairs": {"improved": sum(adapter[k] > base[k] for k in base),
                  "worsened": sum(adapter[k] < base[k] for k in base)},
        "thresholds": {"min_worthwhile": ct.MIN_WORTHWHILE, "regression_drop": ct.REGRESSION_DROP,
                       "bootstrap": ct.BOOTSTRAP, "seed": ct.SEED, "consistency_seed": CONSISTENCY_SEED},
    }


def markdown(rep: dict[str, Any]) -> str:
    p = ct._p
    if rep["status"] == "refused":
        lines = ["# Replication 1: analysis REFUSED", ""]
        for label, problems in rep["refused"].items():
            lines += [f"- {label}: {x}" for x in problems]
        return "\n".join(lines) + "\n"
    r1, r2, r3, r4 = rep["R1"], rep["R2"], rep["R3"], rep["R4"]
    lines = [
        "# Replication 1: pre-registered verdict",
        "",
        f"Base `{rep['base_model']}` vs adapter `{rep['adapter_model']}`, replication split, greedy.",
        "",
        "| Tier | Base all-pass | Adapter all-pass | Difference (points) | 95% interval |",
        "|---|---|---|---|---|",
    ]
    for t, s in rep["per_tier"].items():
        lines.append(f"| {t} | {100 * s['base_all_pass']:.1f}% | {100 * s['adapter_all_pass']:.1f}% | "
                     f"{p(s['difference'])} | [{p(s['ci95'][0])}, {p(s['ci95'][1])}] |")
    lines += [
        "",
        f"**R1 (L2 + L4, primary): {r1['verdict'].upper()}.** Difference {p(r1['difference'])} points, "
        f"95% interval [{p(r1['ci95'][0])}, {p(r1['ci95'][1])}], {r1['pairs']} pairs "
        f"(registered: lower bound above 0 and at least +{100 * ct.MIN_WORTHWHILE:.0f} points).",
        "",
        f"R2 (L4 alone, secondary): {r2['verdict']}, {p(r2['difference'])} points "
        f"[{p(r2['ci95'][0])}, {p(r2['ci95'][1])}].",
        "",
        f"R3 (size against the original test split): {r3['verdict'].upper()}. Original "
        f"{p(r3['original_gain'])}, replication {p(r3['replication_gain'])}, difference "
        f"{p(r3['difference'])} points [{p(r3['ci95'][0])}, {p(r3['ci95'][1])}].",
        "",
        "R4 (specs where the adapter passes both L2 and L4, exact two-sided 95% lower bound): "
        + "; ".join(f"{name} {v['pass']}/{v['specs']}, at least {100 * v['lower95']:.1f}%"
                    for name, v in r4.items()) + ".",
        "",
    ]
    for t, r in rep["regression"].items():
        flag = "REGRESSION" if r["regression"] else "no regression"
        lines.append(f"Regression check {t}: {flag} ({p(r['difference'])} points; flagged below "
                     f"-{100 * ct.REGRESSION_DROP:.0f}).")
    lines += ["", f"Pairs improved {rep['pairs']['improved']}, worsened {rep['pairs']['worsened']}.", ""]
    if rep["adapter_failures"]:
        lines += ["Adapter failures:", ""]
        for f in rep["adapter_failures"]:
            also = "base fails too" if f["base_also_fails"] else "base passes"
            checks = ", ".join(f["failed_checks"]) or "no check recorded"
            lines.append(f"- {f['tier']} {f['spec_id']}: {checks} ({f['finish_reason']}; {also})")
    else:
        lines.append("Adapter failures: none.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--adapter", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None, help="write OUT.md and OUT.json (LF line endings)")
    args = ap.parse_args(argv)
    rep = analyse(args.base, args.adapter)
    text = markdown(rep)
    sys.stdout.write(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        for suffix, body in ((".md", text), (".json", json.dumps(rep, indent=2) + "\n")):
            with args.out.with_suffix(suffix).open("w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
    return 0 if rep["status"] == "analysed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
