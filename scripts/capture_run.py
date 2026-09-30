"""Capture a Hosted Training run's records as dated, hashed snapshot files.

    python scripts/capture_run.py RUN_ID --out results/training/run1/snapshots

Writes OUT/RUN_ID/: `get.json` (run record), `usage.json` (billed tokens and
cost), `metrics.json` (per-step metrics), `distributions-step-N.json` for
every step 1..max_steps that has data, `logs.txt` (orchestrator log tail),
and `manifest.json` listing, for each file, the exact command, the UTC time,
the Prime CLI version, the exit code, the byte size and the SHA-256. Reads
only; it never changes the run. Needs a logged-in Prime CLI on PATH.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

LOG_LINES = 5000


def _env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("SSLKEYLOGFILE", None)  # an unreadable path breaks the CLI
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PRIME_DISABLE_VERSION_CHECK", "1")
    return env


def run_cli(args: list[str], timeout: int = 180) -> tuple[int, str]:
    out = subprocess.run(["prime", *args], capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=timeout, env=_env())
    return out.returncode, out.stdout if out.returncode == 0 else (out.stdout + out.stderr)


def cli_version() -> str:
    code, text = run_cli(["--version"], timeout=60)
    return text.strip().split()[-1] if code == 0 and text.strip() else "unknown"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run_id")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    folder = args.out / args.run_id
    folder.mkdir(parents=True, exist_ok=True)
    version = cli_version()
    manifest: dict[str, Any] = {"run_id": args.run_id, "prime_cli_version": version, "files": []}

    def save(name: str, cli_args: list[str], must_be_json: bool) -> Any:
        code, text = run_cli(cli_args)
        parsed = None
        if must_be_json and code == 0:
            try:
                parsed = json.loads(text)
            except ValueError:
                code = code or 99  # not JSON: keep the text, flag it
        path = folder / name
        path.write_text(text, encoding="utf-8")
        data = path.read_bytes()
        manifest["files"].append({
            "file": name, "command": "prime " + " ".join(cli_args),
            "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "exit_code": code, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        })
        print(f"{'ok ' if code == 0 else 'ERR'} {name} ({len(data)} bytes)")
        return parsed

    run = save("get.json", ["train", "get", args.run_id, "-o", "json"], True)
    save("usage.json", ["train", "usage", args.run_id, "-o", "json"], True)
    save("metrics.json", ["train", "metrics", args.run_id], True)
    max_steps = int(((run or {}).get("run") or {}).get("max_steps") or 0)
    for step in range(1, max_steps + 1):
        save(f"distributions-step-{step}.json",
             ["train", "distributions", args.run_id, "--step", str(step)], True)
    save("logs.txt", ["train", "logs", args.run_id, "-n", str(LOG_LINES)], False)
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    failed = [f["file"] for f in manifest["files"] if f["exit_code"] != 0]
    print(f"\n{len(manifest['files'])} files in {folder}; CLI {version}; "
          + ("all captured" if not failed else f"FAILED: {failed}"))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
