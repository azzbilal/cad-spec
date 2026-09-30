"""Self-test for scripts/archive_run_payload.py (no network, no Prime login).

The archiver must record the create payload and must never let a write
request reach the API client's real transport.

    python scripts/test_archive_payload.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def check(ok: bool, what: str) -> bool:
    print(f"[{'ok ' if ok else 'BAD'}] {what}")
    return ok


def main() -> int:
    try:
        from prime_cli.core import client as core
    except ImportError:
        print("[skip] Prime CLI not importable here")
        return 0
    reached: list[tuple[str, str]] = []

    def transport(self, method, endpoint, *a, **k):  # stands in for the real HTTP call
        reached.append((method.upper(), endpoint))
        return {}

    core.APIClient.request = transport
    import archive_run_payload as arp

    res = arp.archive(ROOT / "configs" / "rl" / "cad-spec-9b.toml")
    writes = [r for r in reached if r[0] in arp.WRITES]
    ok = check(not writes, f"no write request reached the transport ({writes or 'none'})")
    ok &= check(len(res["captured"]) == 1 and res["captured"][0]["endpoint"].endswith("/rft/runs"),
                "exactly one create request recorded")
    body = res["captured"][0]["json"] if res["captured"] else {}
    ok &= check(body.get("temperature") == 0.7 and body.get("enable_thinking") is False
                and body.get("max_tokens") == 2048 and body.get("max_steps") == 104,
                "payload carries the registered sampling settings and run length")
    ok &= check({e["version"] for e in body.get("environments", [])} == {"0.4.5"},
                "payload pins the registered environment version")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
