"""Archive the exact payload `prime train run CONFIG` would send, without sending it.

    python scripts/archive_run_payload.py configs/rl/cad-spec-9b.toml \\
        --out results/training/run1/payload-cad-spec-9b.json

Runs the Prime CLI's own `run` command (same config parsing, same payload
builder, `RLClient.create_run`), with every network WRITE blocked at the API
client: the create request is recorded and refused, any other write request is
refused. Read requests (environment and pricing lookups) go through, so it
needs a logged-in CLI. It cannot create a run: no POST, PUT, PATCH or DELETE
leaves this process.

Why: the service does not echo sampling settings (temperature, thinking) in
the run record, so the archived payload is the record of what was requested.
Use the Python that has the Prime CLI importable (for a uv tool install:
`uv tool run --from prime python scripts/archive_run_payload.py ...`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from importlib import metadata
from pathlib import Path
from typing import Any

WRITES = {"POST", "PUT", "PATCH", "DELETE"}


class WriteBlockedError(RuntimeError):
    """A write request was refused (by design)."""


def _blocked_verb(guard: Any, verb: str) -> Any:
    def blocked(self: Any, endpoint: str, *a: Any, **k: Any) -> None:
        guard(verb, endpoint, k.get("json"))

    return blocked


def _install_guard(captured: list[dict[str, Any]]) -> None:
    from prime_cli.core import client as core

    def guard(method: str, endpoint: str, payload: Any) -> None:
        if method.upper() in WRITES:
            if payload is not None and "rft/runs" in endpoint and "preview" not in endpoint:
                captured.append({"method": method.upper(), "endpoint": endpoint, "json": payload})
            raise WriteBlockedError(f"write refused by archive_run_payload: {method.upper()} {endpoint}")

    for name in ("APIClient", "AsyncAPIClient"):
        cls = getattr(core, name, None)
        if cls is None:
            continue
        orig_request = cls.request
        if name == "APIClient":
            def request(self, method, endpoint, *a, _orig=orig_request, **k):
                guard(method, endpoint, k.get("json"))
                return _orig(self, method, endpoint, *a, **k)

            def post(self, endpoint, json=None, **k):
                guard("POST", endpoint, json)
                raise WriteBlockedError("unreachable")
        else:
            async def request(self, method, endpoint, *a, _orig=orig_request, **k):
                guard(method, endpoint, k.get("json"))
                return await _orig(self, method, endpoint, *a, **k)

            async def post(self, endpoint, json=None, **k):
                guard("POST", endpoint, json)
                raise WriteBlockedError("unreachable")
        cls.request = request
        for verb in ("put", "patch", "delete"):
            if hasattr(cls, verb):
                setattr(cls, verb, _blocked_verb(guard, verb.upper()))
        cls.post = post


def archive(config: Path) -> dict[str, Any]:
    captured: list[dict[str, Any]] = []
    _install_guard(captured)
    from prime_cli.commands.rl import app
    from typer.testing import CliRunner

    result = CliRunner().invoke(app, ["run", str(config), "--yes"], catch_exceptions=True)
    return {
        "captured": captured,
        "cli_exit_code": result.exit_code,
        "cli_output_tail": (result.output or "").strip().splitlines()[-6:],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("config", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    raw = args.config.read_bytes()
    res = archive(args.config)
    if len(res["captured"]) != 1:
        print(f"no create payload captured ({len(res['captured'])} found); CLI said:", *res["cli_output_tail"],
              sep="\n  ", file=sys.stderr)
        return 1
    record = {
        "archived_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prime_cli_version": metadata.version("prime"),
        "config": args.config.as_posix(),
        "config_sha256": hashlib.sha256(raw).hexdigest(),
        "request": res["captured"][0],
        "note": "Recorded by blocking the write; nothing was sent.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    body = record["request"]["json"]
    print(f"archived {record['request']['method']} {record['request']['endpoint']} -> {args.out}")
    print(f"  model: {(body.get('model') or {}).get('name')}")
    for k in ("max_steps", "batch_size", "rollouts_per_example", "max_tokens", "temperature", "enable_thinking"):
        print(f"  {k}: {body.get(k)}")
    for e in body.get("environments", []):
        print(f"  env {e.get('name')}: {e.get('id')}@{e.get('version')} ratio {e.get('ratio')} args {e.get('args')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
