# ruff: noqa: E402
"""Re-score saved runs under the current scorer. No model calls, no cost.

Every run file stores each model's full answer, so a scorer change never
requires regenerating anything: this script replays the saved completions
through the current scorer and writes new files beside a clear provenance
trail. Model-side fields (completion, cost, tokens, finish_reason, API
errors) are kept exactly; score fields are recomputed.

    python scripts/rescore.py results/runs/*.jsonl
    python scripts/summarize_results.py results/rescored/0.4.0/*.jsonl

Output: results/rescored/<scorer version>/<same file name>. Existing outputs
are never overwritten; pass --force to replace them.

Rows whose spec id is unknown to the current task set are copied unchanged
and counted, so nothing is silently dropped.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.measure import ScorerUnavailableError, require_cadquery
from cad_spec.rubric import SCORER_VERSION, score
from cad_spec.tasks import TASKS, make_splits


def spec_table() -> dict:
    train, evals = make_splits()
    return {s.id: s for s in [*train, *evals, *TASKS]}


def rescore_file(src: Path, dst: Path, specs: dict) -> tuple[int, int, int]:
    """Returns (rows rescored, rows whose reward changed, rows copied unscored)."""
    rescored = changed = copied = 0
    with src.open() as fin, dst.open("w") as fout:
        for line in fin:
            if not line.strip():
                continue
            row = json.loads(line)
            if "meta" in row:
                meta = row["meta"]
                meta["rescored_from_version"] = meta.get("scorer_version")
                meta["rescored_from_file"] = src.name
                meta["scorer_version"] = SCORER_VERSION
                meta["rescored_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                fout.write(json.dumps({"meta": meta}) + "\n")
                continue
            if "end" in row or row.get("spec_id") not in specs:
                if "end" not in row:
                    copied += 1
                fout.write(json.dumps(row) + "\n")
                continue
            report = score(row.get("completion") or "", specs[row["spec_id"]])
            old = row.get("reward")
            row.update({
                "reward": report.reward,
                "built": report.parsed,
                "error": report.error,
                "checks": {c.name: c.passed for c in report.checks},
                "gates_passed": bool(report.checks) and all(
                    c.passed for c in report.checks if c.name.startswith("gate:")),
                "timeout": bool(report.error and "execution budget" in report.error),
                "previous_reward": old,
            })
            rescored += 1
            changed += old is None or abs(old - report.reward) > 1e-9
            fout.write(json.dumps(row) + "\n")
    return rescored, changed, copied


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out-dir", default=str(ROOT / "results" / "rescored" / SCORER_VERSION))
    ap.add_argument("--force", action="store_true", help="replace existing rescored files")
    args = ap.parse_args()
    try:
        require_cadquery()
    except ScorerUnavailableError as exc:
        raise SystemExit(f"cad-spec: {exc}") from None

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = spec_table()
    for p in map(Path, args.paths):
        dst = out_dir / p.name
        if dst.exists() and not args.force:
            print(f"skip   {p.name} (already rescored; --force to redo)")
            continue
        t0 = time.time()
        n, changed, copied = rescore_file(p, dst, specs)
        note = f", {copied} rows with unknown spec ids copied unscored" if copied else ""
        print(f"done   {p.name}: {n} rows, reward changed on {changed}{note} ({time.time() - t0:.0f}s)")
    shown = out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir
    print(f"\nRescored files are in {out_dir}. Summarize them with:\n"
          f"  python scripts/summarize_results.py {shown}/*.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
