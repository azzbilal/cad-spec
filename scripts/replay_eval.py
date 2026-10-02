"""Re-score saved test-split evaluation files and compare with what they record.

    python scripts/replay_eval.py results/training/run1/eval/base-test.jsonl \\
        results/training/run1/eval/adapter-test.jsonl --out results/training/run1/linux-replay.json

Every answer (`completion`) is scored again by this machine's scorer against
the locked test split, and its reward and every check verdict are compared
with the recorded ones. On Linux the scorer runs in the `fork` sandbox, the
isolation used on training machines; the original evaluations were scored on
Windows in `reuse` mode. Exit 1 on any mismatch. Offline and free: no model
is called.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "environments" / "cad_spec"))

import cad_spec
from cad_spec.measure import _sandbox_mode
from cad_spec.rubric import SCORER_VERSION, score
from cad_spec.tasks import make_test_split


def replay(path: Path, specs: dict) -> dict:
    raw = path.read_bytes()
    rows = [json.loads(x) for x in raw.decode("utf-8").splitlines() if '"tier"' in x]
    mismatches, passes = [], 0
    for r in rows:
        rep = score(r["completion"], specs[r["spec_id"]])
        checks = {c.name: c.passed for c in rep.checks}
        passes += rep.reward == 1.0
        if rep.reward != r["reward"] or checks != r["checks"]:
            mismatches.append({"tier": r["tier"], "spec": r["spec_id"], "recorded": r["reward"],
                               "replayed": rep.reward,
                               "checks": {k: [r["checks"].get(k), v] for k, v in checks.items()
                                          if r["checks"].get(k) != v}})
    lf = raw.replace(b"\r\n", b"\n")
    return {"file": path.as_posix(), "rows": len(rows), "all_pass": passes, "mismatches": mismatches,
            "sha256_lf": hashlib.sha256(lf).hexdigest(),
            "sha256_crlf": hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", type=Path, nargs="+")
    ap.add_argument("--out", type=Path, default=None, help="write the result as JSON (LF line endings)")
    args = ap.parse_args(argv)
    specs = {s.id: s for s in make_test_split()}
    t0 = time.time()
    result = {"platform": platform.platform(), "python": platform.python_version(),
              "sandbox_mode": _sandbox_mode(), "cad_spec": cad_spec.__version__, "scorer": SCORER_VERSION,
              "files": [replay(f, specs) for f in args.files]}
    result["seconds"] = round(time.time() - t0, 1)
    total = sum(len(f["mismatches"]) for f in result["files"])
    for f in result["files"]:
        print(f"{f['file']}: {f['rows']} answers, {f['all_pass']} all-pass, {len(f['mismatches'])} mismatches")
    print(f"sandbox {result['sandbox_mode']}, {result['seconds']} s, total mismatches {total}")
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
