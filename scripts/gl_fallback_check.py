"""Gate before a Hosted Training smoke test: can cad-spec score on this machine?

    python scripts/gl_fallback_check.py --expect vendored \\
        --out results/training/gl-fallback/<label>

Run it with the Python of an environment where the BUILT WHEEL is installed
(not the repository copy), on Linux x86_64. To reproduce the Hosted Training
image's condition (no libGL.so.1 / libX11.so.6), run it in a container without
them, or hide the system copies first (root), e.g. on Ubuntu:

    L=/usr/lib/x86_64-linux-gnu; mkdir -p /tmp/hidden
    for f in libGL.so.1* libGLX.so.0* libGLdispatch.so.0* libX11.so.6* \\
             libxcb.so.1* libXau.so.6* libXdmcp.so.6*; do mv $L/$f /tmp/hidden/; done
    ... run the check ...
    mv /tmp/hidden/* $L/

What it records (JSON and Markdown under --out):
1. The environment: platform, glibc, Python, cad_spec version and location,
   sandbox mode (fork on POSIX), and where the GL libraries came from.
2. Fail-fast cost: time and peak memory of `require_cadquery()` in a fresh
   process (what `load_environment` now pays at startup).
3. Scoring through verifiers (`env.init_state`, `env.rubric.score_rollout`):
   the reference answer (binary 1.0), the known L4 failure (new plate, old
   pitch: binary 0.0, continuous 8/10), and a complete `env.rollout` with a
   stand-in model.
4. Concurrency: saved screening answers scored at once, 1, 8, 32 and 64 at a
   time, with wall time, per-call latency, and the binary reward compared with
   the reward recorded in the screening file.

Gate (exit 0 only if all hold): GL source as --expect; reference 1.0; L4
failure 0.0 binary and 8/10 continuous; full rollout 1.0 without error; every
concurrency level matches the screening rewards exactly; 64 at once within
120 s.
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import os
import platform
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCREENING = ROOT / "results" / "training" / "screening" / "qwen3.5-9b-t0.7-x8-2k.jsonl"
LEVELS = (1, 8, 32, 64)
WALL_LIMIT_64 = 120.0

STARTUP_PROBE = (
    "import time, resource\n"
    "t = time.perf_counter()\n"
    "from cad_spec.measure import require_cadquery, _ensure_gl_libraries\n"
    "v = require_cadquery()\n"
    "dt = time.perf_counter() - t\n"
    "print(v, _ensure_gl_libraries(), round(dt, 2), resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024)\n"
)


def environment_facts() -> dict[str, Any]:
    import cad_spec
    from cad_spec import measure

    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "glibc": "-".join(platform.libc_ver()),
        "python": sys.version.split()[0],
        "cpus": os.cpu_count(),
        "cad_spec": cad_spec.__version__,
        "cad_spec_path": str(Path(cad_spec.__file__).parent),
        "installed_wheel": "site-packages" in cad_spec.__file__ or "dist-packages" in cad_spec.__file__,
        "sandbox_mode": measure._sandbox_mode(),
    }


def startup_cost() -> dict[str, Any]:
    """Fresh process: what load_environment's fail-fast check costs."""
    out = subprocess.run([sys.executable, "-c", STARTUP_PROBE], capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        return {"ok": False, "error": (out.stderr or out.stdout).strip().splitlines()[-1:]}
    version, gl, seconds, rss_mb = out.stdout.split()
    return {"ok": True, "cadquery": version, "gl_source": gl, "seconds": float(seconds), "peak_rss_mb": int(rss_mb)}


def _client(answer_code: str | None = None):
    from unittest.mock import AsyncMock, MagicMock

    from verifiers.legacy.clients import Client
    from verifiers.legacy.types import Response, ResponseMessage

    c = MagicMock(spec=Client)
    if answer_code is not None:
        c.get_response = AsyncMock(return_value=Response(
            id="r", created=int(time.time()), model="m",
            message=ResponseMessage(content="```python\n" + answer_code + "\n```",
                                    finish_reason="stop", is_truncated=False)))
    return c


async def _score(env, row, completion_text):
    st = await env.init_state(input=dict(row), client=_client(), model="m")
    st["completion"] = [{"role": "assistant", "content": completion_text}]
    t = time.perf_counter()
    await env.rubric.score_rollout(st)
    return st, time.perf_counter() - t


def scoring_checks() -> dict[str, Any]:
    import cad_spec.environment as env_mod
    from cad_spec.environment import EVAL_SPECS, SPECS, load_environment
    from cad_spec.tasks import reference_solution

    env = load_environment(tier=["L4"], hints=True, reward="binary")
    row = dict(env.dataset[0])
    ref = "```python\n" + reference_solution(SPECS[row["answer"]]) + "\n```"
    st, _ = asyncio.run(_score(env, row, ref))
    reference = float(st["reward"])

    base = EVAL_SPECS[0]
    target = dataclasses.replace(base, id="gl-check-eco", length=base.length + 20)
    env_mod.SPECS[target.id] = target
    stale = reference_solution(target).replace(
        f".rect({target.pitch_x}, {target.pitch_y}", f".rect({base.pitch_x}, {base.pitch_y}")
    frow = {**row, "answer": target.id, "info": {"spec_id": target.id, "tier": "L4"}}
    st, _ = asyncio.run(_score(env, frow, "```python\n" + stale + "\n```"))
    failure_binary, failure_continuous = float(st["reward"]), float(st["metrics"]["spec_reward"])

    env2 = load_environment(tier=["L2"], hints=True, reward="binary")
    row2 = dict(env2.dataset[0])
    client = _client(reference_solution(SPECS[row2["answer"]]))
    st = asyncio.run(env2.rollout(input=row2, client=client, model="m", sampling_args={}))
    asyncio.run(env2.rubric.score_rollout(st))
    return {
        "reference_binary": reference,
        "l4_failure_binary": failure_binary,
        "l4_failure_continuous": round(failure_continuous, 4),
        "full_rollout_reward": float(st["reward"]),
        "full_rollout_error": None if st.get("error") is None else str(st.get("error")),
    }


def concurrency(levels=LEVELS) -> list[dict[str, Any]]:
    from cad_spec.environment import load_environment

    rows = [json.loads(x) for x in SCREENING.read_text(encoding="utf-8").splitlines() if '"tier"' in x]
    rows = [r for r in rows if r.get("finish_reason") != "length"]
    random.Random(7).shuffle(rows)
    # The saved screening answers were recorded under scorer 0.4.0; this check
    # compares against those recorded rewards, so it scores with that version.
    envs = {t: load_environment(tier=[t], hints=True, reward="binary", scorer_version="0.4.0")
            for t in ("L1", "L2", "L3", "L4")}

    async def one(r):
        row = {"prompt": [{"role": "user", "content": "x"}], "answer": r["spec_id"],
               "info": {"spec_id": r["spec_id"], "tier": r["tier"]}, "example_id": 0}
        st, dt = await _score(envs[r["tier"]], row, r["completion"])
        return float(st["reward"]), float(r["reward"] == 1.0), dt

    async def run(batch):
        t = time.perf_counter()
        res = await asyncio.gather(*(one(r) for r in batch))
        return res, time.perf_counter() - t

    out = []
    for n in levels:
        res, wall = asyncio.run(run(rows[:n]))
        lat = sorted(d for *_, d in res)
        out.append({"n": n, "wall_s": round(wall, 2), "median_call_s": round(lat[len(lat) // 2], 3),
                    "max_call_s": round(lat[-1], 2), "matches": sum(a == b for a, b, _ in res),
                    "all_pass": int(sum(a for a, _, _ in res))})
    return out


def gate(report: dict[str, Any], expect: str) -> list[str]:
    fails = []
    s, c, sc = report["startup"], report["concurrency"], report["scoring"]
    if not s.get("ok") or s.get("gl_source") != expect:
        fails.append(f"GL source {s.get('gl_source')!r}, expected {expect!r} ({s.get('error')})")
    if sc["reference_binary"] != 1.0:
        fails.append("reference answer did not score 1.0")
    if sc["l4_failure_binary"] != 0.0 or abs(sc["l4_failure_continuous"] - 8 / 10) > 1e-3:
        fails.append("known L4 failure did not score 0 binary / 8/10 continuous")
    if sc["full_rollout_reward"] != 1.0 or sc["full_rollout_error"]:
        fails.append("full rollout did not score 1.0 without error")
    for level in c:
        if level["matches"] != level["n"]:
            fails.append(f"n={level['n']}: {level['matches']}/{level['n']} rewards match the screening file")
    top = [x for x in c if x["n"] == 64]
    if top and top[0]["wall_s"] > WALL_LIMIT_64:
        fails.append(f"64 at once took {top[0]['wall_s']} s (limit {WALL_LIMIT_64})")
    return fails


def markdown(r: dict[str, Any]) -> str:
    e, s, sc = r["environment"], r["startup"], r["scoring"]
    lines = [
        f"# GL fallback and scoring check: {r['label']}",
        "",
        f"Run {r['when']} with `{' '.join(r['command'])}`.",
        "",
        "| Environment | |", "|---|---|",
        *[f"| {k} | `{v}` |" for k, v in e.items()],
        f"| system GL/X11 before the run | {r['system_gl_note']} |",
        "",
        "| Startup (fresh process, `require_cadquery`) | |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in s.items()],
        "",
        "| Scoring through verifiers | Result |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in sc.items()],
        "",
        "| Concurrent answers | Wall (s) | Median call (s) | Max call (s) | Rewards matching screening | All-pass |",
        "|---|---|---|---|---|---|",
        *[f"| {x['n']} | {x['wall_s']} | {x['median_call_s']} | {x['max_call_s']} | {x['matches']}/{x['n']} | "
          f"{x['all_pass']} |" for x in r["concurrency"]],
        "",
        f"**Gate: {'PASS' if not r['gate_failures'] else 'FAIL'}.**"
        + ("" if not r["gate_failures"] else " " + "; ".join(r["gate_failures"])),
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--expect", choices=["system", "vendored"], required=True,
                    help="where the GL libraries must come from on this machine")
    ap.add_argument("--label", default=None, help="short name for this run (defaults to --expect)")
    ap.add_argument("--system-gl-note", default="not stated",
                    help="how the machine's own GL/X11 libraries were set up (e.g. 'hidden')")
    ap.add_argument("--out", type=Path, required=True, help="write OUT.json and OUT.md")
    args = ap.parse_args(argv)
    report = {
        "label": args.label or args.expect,
        "when": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "command": [Path(sys.argv[0]).name, *(argv if argv is not None else sys.argv[1:])],
        "system_gl_note": args.system_gl_note,
        "environment": environment_facts(),
        "startup": startup_cost(),
    }
    report["scoring"] = scoring_checks()
    report["concurrency"] = concurrency()
    report["gate_failures"] = gate(report, args.expect)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    text = markdown(report)
    args.out.with_suffix(".md").write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if not report["gate_failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
