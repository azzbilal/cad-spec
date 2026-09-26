"""Prove an installed cad_spec (the Hub copy) scores exactly like the repository.

Install the package from the Hub into a separate environment, then run this
script with THAT environment's Python, from the repository root:

    python scripts/verify_hub.py                 # 200 saved answers
    python scripts/verify_hub.py --n 0           # every saved answer

It re-scores a deterministic sample of the answers saved in
results/rescored/<scorer version>/ and requires, for every one, the same
reward and the same verdict on every check as the repository recorded. It
refuses to run against the repository's own source: that would prove nothing.

Answers whose recorded outcome was a timeout are skipped (timing depends on
the machine); the count is reported. Error wording is not compared, only
rewards and checks.

Exit code 0: identical. 1: at least one mismatch. 2: wrong setup.
"""

from __future__ import annotations

import argparse
import glob
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="saved run files (default: results/rescored/<scorer>/*.jsonl)")
    ap.add_argument("--n", type=int, default=200, help="answers to re-score (0 = all)")
    ap.add_argument("--seed", type=int, default=0, help="sampling seed")
    args = ap.parse_args()

    try:
        import cad_spec
        from cad_spec.rubric import SCORER_VERSION, score
        from cad_spec.tasks import TASKS, make_splits
    except ImportError as exc:
        print(f"cad_spec is not installed in this Python ({sys.executable}): {exc}")
        return 2
    installed = Path(cad_spec.__file__).resolve()
    if ROOT in installed.parents:
        print(f"this Python imports the repository's own copy ({installed}); run it from an "
              "environment where the package was installed from the Hub")
        return 2

    files = args.files or sorted(glob.glob(str(ROOT / "results" / "rescored" / SCORER_VERSION / "*.jsonl")))
    if not files:
        print(f"no saved answers for scorer {SCORER_VERSION} under results/rescored/")
        return 2

    train, evals = make_splits()
    specs = {s.id: s for s in [*train, *evals, *TASKS]}
    try:
        from cad_spec.tasks import make_test_split
        specs.update({s.id: s for s in make_test_split()})
    except ImportError:  # packages before 0.4.1 have no test split
        pass

    rows, timeouts = [], 0
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                row = json.loads(line)
                if "meta" in row or "end" in row or row.get("spec_id") not in specs or "checks" not in row:
                    continue
                if row.get("timeout"):
                    timeouts += 1
                    continue
                rows.append(row)
    rows.sort(key=lambda r: (r.get("run_id", ""), r["tier"], r["spec_id"], r.get("rollout", 0)))
    if args.n and args.n < len(rows):
        rows = random.Random(args.seed).sample(rows, args.n)

    print(f"installed copy : {installed.parent}")
    print(f"package        : {cad_spec.__version__}, scorer {SCORER_VERSION}")
    print(f"re-scoring     : {len(rows)} saved answers from {len(files)} files "
          f"({timeouts} timeout answers skipped)")
    mismatches = []
    for i, row in enumerate(rows, 1):
        report = score(row.get("completion") or "", specs[row["spec_id"]])
        checks = {c.name: c.passed for c in report.checks}
        if abs(report.reward - row["reward"]) > 1e-9 or checks != row["checks"]:
            mismatches.append((row, report.reward, checks))
        if i % 50 == 0:
            print(f"  {i}/{len(rows)}")
    if mismatches:
        print(f"\nMISMATCH: {len(mismatches)} of {len(rows)} answers score differently")
        for row, reward, checks in mismatches[:5]:
            diff = sorted(k for k in set(checks) | set(row["checks"]) if checks.get(k) != row["checks"].get(k))
            print(f"  {row.get('run_id')} {row['tier']} {row['spec_id']}: recorded {row['reward']:.4f}, "
                  f"installed {reward:.4f}; checks differing: {', '.join(diff) or 'none'}")
        return 1
    print(f"\nIDENTICAL: all {len(rows)} answers get the same reward and the same check verdicts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
