# ruff: noqa: E402
"""Run a baseline over the frozen eval split, per tier, with full provenance.

Every rollout is written as one JSON line carrying the model, provider,
sampling settings, seed, tier, spec id, scorer version, git revision and the
per-check outcome, so any number in a README can be traced back to rows.
Summarize with scripts/summarize_results.py.

Providers
  parser-copy    deterministic: copies labelled numbers from requirement
                 tables into the template. No arithmetic, no language.
  parser-derive  parser-copy plus one rule: pitch = size - 2 * margin.
  rev-a          L4 only meaningfully: returns the rev A code unchanged
                 (the "ignore the change order" baseline).
  reference      the known-correct answer (upper bound, sanity check).
  openai         any OpenAI-compatible /chat/completions server: Ollama,
                 vLLM, LM Studio, OpenRouter, Prime inference.
                 --base-url, key from --key-env (default OPENAI_API_KEY).
  anthropic      Anthropic Messages API, key from ANTHROPIC_API_KEY.

Examples
  python scripts/run_baseline.py --provider parser-copy --tiers L0 L1 L2 L3 L4
  python scripts/run_baseline.py --provider openai --base-url http://localhost:11434/v1 \\
      --model qwen2.5-coder:7b --tiers L0 L1 L2 L3 L4 --rollouts 3 --temperature 0.7
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec import __version__
from cad_spec.measure import sandbox_info
from cad_spec.rubric import SCORER_VERSION, score
from cad_spec.tasks import SAMPLE_SEED, TIERS, Spec, edit_source, make_splits, prompt_for, reference_solution

SYSTEM_PROMPT = (
    "You are a mechanical design engineer who writes CadQuery.\n"
    "Return a single Python code block and nothing else.\n"
    "Import cadquery as cq and bind the finished part to a variable named `result`.\n"
    'Build solids with the Workplane API, for example cq.Workplane("XY").box(l, w, h).\n'
)

_TEMPLATE = """import cadquery as cq
result = (
    cq.Workplane("XY")
    .box({L}, {W}, {T})
    .faces(">Z").workplane()
    .rect({PX}, {PY}, forConstruction=True)
    .vertices()
    .hole({D})
)
"""

_LABELS = {
    "L": r"Overall length \(X\):\s*([\d.]+)",
    "W": r"Overall width \(Y\):\s*([\d.]+)",
    "T": r"Plate thickness \(Z\):\s*([\d.]+)",
    "D": r"through,\s*([\d.]+) mm diameter",
    "PXPY": r"rectangular,\s*([\d.]+) mm x ([\d.]+) mm centres",
    "M": r"Edge margin:\s*([\d.]+)",
}


def parser_answer(prompt: str, derive: bool) -> str:
    """Fill the template from labelled table rows; give up (prose) otherwise."""
    got: dict[str, Any] = {}
    for key, pat in _LABELS.items():
        m = re.search(pat, prompt)
        if m:
            got[key] = m.groups() if key == "PXPY" else m.group(1)
    if not all(k in got for k in ("L", "W", "T", "D")):
        return "I could not find a requirements table."
    if "PXPY" in got:
        px, py = got["PXPY"]
    elif derive and "M" in got:
        margin = float(got["M"])
        px, py = f"{float(got['L']) - 2 * margin:g}", f"{float(got['W']) - 2 * margin:g}"
    else:
        return "I could not find the hole pattern pitch."
    return "```python\n" + _TEMPLATE.format(L=got["L"], W=got["W"], T=got["T"], PX=px, PY=py, D=got["D"]) + "```"


def _post(url: str, headers: dict[str, str], body: dict[str, Any], timeout: float) -> dict[str, Any]:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def model_answer(args: argparse.Namespace, prompt: str, seed: int) -> tuple[str, dict[str, Any]]:
    if args.provider == "openai":
        key = os.environ.get(args.key_env, "none")
        body = {
            "model": args.model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "seed": seed,
        }
        out = _post(args.base_url.rstrip("/") + "/chat/completions",
                    {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}, body, args.timeout)
        return out["choices"][0]["message"]["content"] or "", out.get("usage") or {}
    if args.provider == "anthropic":
        body = {
            "model": args.model,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
        }
        headers = {"Content-Type": "application/json", "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                   "anthropic-version": "2023-06-01"}
        out = _post("https://api.anthropic.com/v1/messages", headers, body, args.timeout)
        text = "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
        return text, out.get("usage") or {}
    raise ValueError(args.provider)


def answer(args: argparse.Namespace, spec: Spec, tier: str, prompt: str, seed: int) -> tuple[str, dict[str, Any]]:
    if args.provider == "parser-copy":
        return parser_answer(prompt, derive=False), {}
    if args.provider == "parser-derive":
        return parser_answer(prompt, derive=True), {}
    if args.provider == "reference":
        return reference_solution(spec), {}
    if args.provider == "rev-a":
        return (reference_solution(edit_source(spec)) if tier == "L4" else parser_answer(prompt, True)), {}
    return model_answer(args, prompt, seed)


def git_rev() -> str:
    try:
        rev = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = subprocess.call(["git", "diff", "--quiet"], cwd=ROOT) != 0
        return rev + ("-dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provider", required=True,
                    choices=["parser-copy", "parser-derive", "rev-a", "reference", "openai", "anthropic"])
    ap.add_argument("--model", default="")
    ap.add_argument("--base-url", default="http://localhost:11434/v1")
    ap.add_argument("--key-env", default="OPENAI_API_KEY")
    ap.add_argument("--tiers", nargs="+", default=["L0"], choices=list(TIERS))
    ap.add_argument("--split", default="eval", choices=["eval", "train"])
    ap.add_argument("--limit", type=int, default=0, help="first N specs only (0 = all)")
    ap.add_argument("--rollouts", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=0, help="base sampling seed; rollout k uses seed + k")
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--out", default="", help="JSONL path (default results/runs/<auto>.jsonl)")
    args = ap.parse_args()
    if args.provider in ("openai", "anthropic") and not args.model:
        ap.error("--model is required for model providers")

    train, evals = make_splits()
    specs = evals if args.split == "eval" else train
    if args.limit:
        specs = specs[: args.limit]
    run_id = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    label = args.model.replace("/", "_").replace(":", "_") if args.model else args.provider
    out = Path(args.out) if args.out else ROOT / "results" / "runs" / f"{run_id}_{label}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    meta = {
        "run_id": run_id, "provider": args.provider, "model": args.model or args.provider,
        "temperature": args.temperature, "max_tokens": args.max_tokens, "base_seed": args.seed,
        "rollouts": args.rollouts, "split": args.split, "sample_seed": SAMPLE_SEED,
        "scorer_version": SCORER_VERSION, "package_version": __version__, "git_rev": git_rev(),
        "sandbox": sandbox_info(), "system_prompt": SYSTEM_PROMPT,
    }
    n = 0
    with out.open("w") as fh:
        fh.write(json.dumps({"meta": meta}) + "\n")
        for tier in args.tiers:
            for spec in specs:
                prompt = prompt_for(spec, tier, args.split)
                for k in range(args.rollouts):
                    t0 = time.time()
                    try:
                        text, usage = answer(args, spec, tier, prompt, args.seed + k)
                        api_error = None
                    except Exception as exc:  # network / API errors are data too
                        text, usage, api_error = "", {}, f"{type(exc).__name__}: {exc}"
                    gen_s = time.time() - t0
                    report = score(text, spec)
                    row = {
                        "run_id": run_id, "tier": tier, "spec_id": spec.id, "rollout": k,
                        "seed": args.seed + k, "reward": report.reward, "built": report.parsed,
                        "error": report.error, "api_error": api_error,
                        "checks": {c.name: c.passed for c in report.checks},
                        "gates_passed": bool(report.checks) and all(
                            c.passed for c in report.checks if c.name.startswith("gate:")),
                        "timeout": bool(report.error and "execution budget" in report.error),
                        "completion_chars": len(text), "usage": usage, "gen_seconds": round(gen_s, 3),
                        "completion": text,
                    }
                    fh.write(json.dumps(row) + "\n")
                    n += 1
            print(f"{tier}: done", file=sys.stderr)
    print(f"wrote {n} rollouts to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
