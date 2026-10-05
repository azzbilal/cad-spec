"""What scorer 0.5.0 would say about the two registered evaluations (descriptive).

    python scripts/scorer_sensitivity.py --out results/training/scorer-0.5-sensitivity

The registered verdicts of training run 1 and of replication 1 were recorded
under scorer 0.4.0 and stay as they are. This script re-scores the same saved
answers under 0.5.0 (strict contract, 0.1 mm tolerances) and reports what
changes.

Honest history: it was run three times. On 4 October 2026 against the first
0.5.0 draft, and twice on 5 October after each of two external audits broke a
draft with synthetic parts (shallow pockets, rounding, splines, displaced
plane origins) and the scorer was reworked. Each rework was driven by those
synthetic counterexamples and by train and dev parts, never by these answers:
both splits are used and cannot serve to tune anything. The three runs
changed the same six verdicts.

The paired bootstrap is the registered one (scripts/compare_training.py).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))
sys.path.insert(0, str(ROOT / "scripts"))

import compare_training as ct  # noqa: E402
from cad_spec.rubric import score  # noqa: E402
from cad_spec.tasks import make_test_split  # noqa: E402
from replication_split import make_replication_split  # noqa: E402

NEW = "0.5.0"
SPLITS = {
    "original test split": ("results/training/run1/eval/base-test.jsonl",
                            "results/training/run1/eval/adapter-test.jsonl"),
    "replication split": ("results/training/replication1/eval/base-rep-run2.jsonl",
                          "results/training/replication1/eval/adapter-rep.jsonl"),
}


def rescore(path: Path, specs: dict) -> tuple[dict, dict, list[dict]]:
    """(recorded outcomes, 0.5.0 outcomes, answers whose verdict changed)."""
    rows = [r for r in map(json.loads, path.open(encoding="utf-8")) if "tier" in r]
    old, new, changed = {}, {}, []
    for r in rows:
        key = (r["tier"], r["spec_id"])
        rep = score(r["completion"], specs[r["spec_id"]], NEW)
        old[key] = int(r["reward"] == 1.0)
        new[key] = int(rep.reward == 1.0)
        if old[key] != new[key]:
            changed.append({"tier": r["tier"], "spec_id": r["spec_id"], "recorded": old[key], "under_0.5.0": new[key],
                            "failed_checks": sorted(c.name for c in rep.checks if not c.passed)})
    return old, new, changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True, help="output path without extension")
    args = ap.parse_args()
    specs = {s.id: s for s in make_test_split() + make_replication_split()}
    report: dict = {"recorded_scorer": "0.4.0", "sensitivity_scorer": NEW, "splits": {}}
    lines = [
        "# Scorer 0.5.0 sensitivity of the two registered evaluations",
        "",
        "**Descriptive, not a verdict.** The registered results were recorded under scorer 0.4.0 and are",
        "unchanged. Here the same saved answers are re-scored under 0.5.0 (strict contract, 0.1 mm",
        "tolerances). Run on the final scorer 0.5.0 (5 October 2026). Two earlier runs, on two drafts",
        "that external audits then broke with synthetic parts, changed the same verdicts; the reworks",
        "were driven by those synthetic counterexamples, not by these answers.",
        "",
    ]
    for name, (base_path, adapter_path) in SPLITS.items():
        b_old, b_new, b_changed = rescore(ROOT / base_path, specs)
        a_old, a_new, a_changed = rescore(ROOT / adapter_path, specs)
        gain_old = ct.paired(b_old, a_old, ct.PRIMARY)
        gain_new = ct.paired(b_new, a_new, ct.PRIMARY)
        tiers = {}
        for t in ct.TIERS:
            n = sum(1 for k in b_old if k[0] == t)
            tiers[t] = {"n": n, **{f"{who}_{ver}": sum(v for k, v in d.items() if k[0] == t)
                                   for who, ver, d in (("base", "0.4.0", b_old), ("base", "0.5.0", b_new),
                                                       ("adapter", "0.4.0", a_old), ("adapter", "0.5.0", a_new))}}
        report["splits"][name] = {"per_tier": tiers, "l2_l4_gain_0.4.0": gain_old, "l2_l4_gain_0.5.0": gain_new,
                                  "base_changed": b_changed, "adapter_changed": a_changed}
        p = ct._p
        lines += [f"## {name.capitalize()}", "",
                  "| Tier | Base 0.4.0 | Base 0.5.0 | Adapter 0.4.0 | Adapter 0.5.0 |", "|---|---:|---:|---:|---:|"]
        for t, v in tiers.items():
            lines.append(f"| {t} | {v['base_0.4.0']}/{v['n']} | {v['base_0.5.0']}/{v['n']} | "
                         f"{v['adapter_0.4.0']}/{v['n']} | {v['adapter_0.5.0']}/{v['n']} |")
        lines += ["",
                  f"L2 + L4 gain: recorded {p(gain_old['difference'])} points "
                  f"[{p(gain_old['ci95'][0])}, {p(gain_old['ci95'][1])}]; under 0.5.0 "
                  f"{p(gain_new['difference'])} points [{p(gain_new['ci95'][0])}, {p(gain_new['ci95'][1])}].", ""]
        for who, changed in (("Base", b_changed), ("Adapter", a_changed)):
            if not changed:
                lines.append(f"{who}: no verdict changes.")
                continue
            lines.append(f"{who}: {len(changed)} verdict(s) change:")
            lines += [f"- {c['tier']} {c['spec_id']}: {'pass' if c['recorded'] else 'fail'} to "
                      f"{'pass' if c['under_0.5.0'] else 'fail'} ({', '.join(c['failed_checks']) or 'all checks pass'})"
                      for c in changed]
        lines.append("")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines)
    for suffix, body in ((".md", text), (".json", json.dumps(report, indent=2) + "\n")):
        # not with_suffix(): the stem contains a dot ("scorer-0.5-sensitivity")
        with Path(str(args.out) + suffix).open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
