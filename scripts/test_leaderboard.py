"""Self-test for the leaderboard's ranking rules (runs in CI).

    python scripts/test_leaderboard.py

A run is ranked only if every headline tier answers exactly the 30 held-out
specs. The first version averaged over the specs common to all tiers, so a run
whose failures carried stray spec ids scored its passes only: 50% per tier
headlined as 100% (external audit, September 2026).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.tasks import make_splits  # noqa: E402

TIERS = ["L0", "L1", "L2", "L3", "L4"]


def write_run(d: Path, name: str, stray_ids: bool) -> None:
    _, evals = make_splits()
    rows = []
    for tier in TIERS:
        for i, s in enumerate(evals):
            ok = i < 15
            sid = s.id if ok or not stray_ids else f"stray-{tier}-{i}"
            rows.append({"run_id": name, "tier": tier, "spec_id": sid, "rollout": 0, "reward": float(ok),
                         "built": True, "gates_passed": True, "checks": {"R1": ok}, "finish_reason": "stop"})
    meta = {"meta": {"run_id": name, "model": name,
                     "planned": {"tiers": TIERS, "spec_ids": [s.id for s in evals], "rollouts": 1, "total": 150}}}
    end = {"end": {"status": "complete", "written": 150, "planned": 150}}
    (d / f"{name}.jsonl").write_text("\n".join(json.dumps(x) for x in [meta, *rows, end]) + "\n")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        write_run(d, "honest-half", stray_ids=False)
        write_run(d, "stray-ids", stray_ids=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "leaderboard.py"), *map(str, d.glob("*.jsonl")),
                        "--out", str(d / "lb")], check=True, capture_output=True)
        md = (d / "lb" / "leaderboard.md").read_text()
    ranked = [line for line in md.splitlines() if line.startswith("| 1 |")]
    ok_honest = len(ranked) == 1 and "honest-half" in ranked[0] and "| 50% [" in ranked[0]
    ok_stray = "stray-ids" not in "".join(ranked) and "Not ranked" in md and "stray-ids" in md
    print(f"[{'ok ' if ok_honest else 'BAD'}] a complete 50% run is ranked at 50%")
    print(f"[{'ok ' if ok_stray else 'BAD'}] a run with stray spec ids is not ranked, and says why")
    return 0 if ok_honest and ok_stray else 1


if __name__ == "__main__":
    raise SystemExit(main())
