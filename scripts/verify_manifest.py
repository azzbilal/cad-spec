"""Verify a snapshot manifest written by scripts/capture_run.py, on any OS.

    python scripts/verify_manifest.py results/training/run1/snapshots/*/manifest.json

Each file listed in a manifest is checked against its recorded SHA-256 in
two forms: the bytes as they are on disk, and the same bytes with LF line
endings written as CRLF. Manifests captured on Windows before 2 October 2026
hashed CRLF files (Python's default text mode there), while Git stores them
with LF, so on Linux they match only in the CRLF form. The script reports
which form matched for every file and fails if any file matches neither.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def check(manifest: Path) -> tuple[int, int, int, list[str]]:
    m = json.loads(manifest.read_text(encoding="utf-8"))
    exact = crlf = 0
    bad: list[str] = []
    for entry in m.get("files", []):
        path = manifest.parent / entry["file"]
        if not path.exists():
            bad.append(f"{entry['file']}: missing")
            continue
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() == entry["sha256"]:
            exact += 1
        elif hashlib.sha256(raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest() == entry["sha256"]:
            crlf += 1
        else:
            bad.append(f"{entry['file']}: hash differs in both forms")
    return len(m.get("files", [])), exact, crlf, bad


def main(argv: list[str] | None = None) -> int:
    paths = [Path(p) for p in (argv if argv is not None else sys.argv[1:])]
    if not paths:
        print(__doc__.split("\n\n")[1])
        return 2
    failed = False
    for p in paths:
        n, exact, crlf, bad = check(p)
        status = "ok" if not bad else "FAILED"
        print(f"{status} {p}: {n} files, {exact} exact, {crlf} as CRLF" + "".join(f"\n  {b}" for b in bad))
        failed |= bool(bad)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
