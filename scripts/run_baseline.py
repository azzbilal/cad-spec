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
                 On OpenRouter the exact USD cost of every call is recorded.
  anthropic      Anthropic Messages API, key from ANTHROPIC_API_KEY.

Every rollout records why generation stopped (finish_reason: "stop" = the
model finished, "length" = it hit --max-tokens and was cut off). Truncated
answers are a configuration problem, not a model result; the summary shows
their rate per tier so they can never hide inside a low score again.

--budget stops the run once the recorded spend reaches that many USD.
Everything scored so far stays in the file.

Examples
  python scripts/run_baseline.py --provider parser-copy --tiers L0 L1 L2 L3 L4
  python scripts/run_baseline.py --provider openai --base-url https://openrouter.ai/api/v1 \\
      --key-env OPENROUTER_API_KEY --model qwen/qwen-2.5-coder-32b-instruct \\
      --tiers L0 L1 L2 L3 L4 --budget 1.00
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

# A wrong key or model id fails every call; stop early instead of recording
# a whole run of errors.
MAX_CONSECUTIVE_API_ERRORS = 5

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


def _is_openrouter(args: argparse.Namespace) -> bool:
    return "openrouter.ai" in args.base_url


def model_answer(args: argparse.Namespace, prompt: str, seed: int) -> tuple[str, dict[str, Any]]:
    """Returns (answer text, call info: usage, finish_reason, cost_usd)."""
    if args.provider == "openai":
        key = os.environ.get(args.key_env, "")
        if _is_openrouter(args) and not key:
            raise RuntimeError(f"environment variable {args.key_env} is empty")
        body: dict[str, Any] = {
            "model": args.model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "seed": seed,
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key or 'none'}"}
        if _is_openrouter(args):
            body["usage"] = {"include": True}  # OpenRouter returns the exact cost of the call
            headers["X-Title"] = "cad-spec baseline"
        body.update(json.loads(args.extra_body) if args.extra_body else {})
        out = _post(args.base_url.rstrip("/") + "/chat/completions", headers, body, args.timeout)
        if "error" in out and not out.get("choices"):
            raise RuntimeError(f"API error: {out['error']}")
        choice = out["choices"][0]
        usage = out.get("usage") or {}
        info = {
            "usage": usage,
            "finish_reason": choice.get("finish_reason") or choice.get("native_finish_reason"),
            "cost_usd": usage.get("cost"),
            "provider": out.get("provider"),
        }
        return choice["message"].get("content") or "", info
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
        stop = out.get("stop_reason")
        return text, {"usage": out.get("usage") or {}, "cost_usd": None,
                      "finish_reason": "length" if stop == "max_tokens" else stop}
    raise ValueError(args.provider)


def answer(args: argparse.Namespace, spec: Spec, tier: str, prompt: str, seed: int) -> tuple[str, dict[str, Any]]:
    local = {"usage": {}, "finish_reason": "stop", "cost_usd": 0.0}
    if args.provider == "parser-copy":
        return parser_answer(prompt, derive=False), local
    if args.provider == "parser-derive":
        return parser_answer(prompt, derive=True), local
    if args.provider == "reference":
        return reference_solution(spec), local
    if args.provider == "rev-a":
        return (reference_solution(edit_source(spec)) if tier == "L4" else parser_answer(prompt, True)), local
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
    ap.add_argument("--budget", type=float, default=0.0,
                    help="stop once recorded spend reaches this many USD (0 = no limit)")
    ap.add_argument("--extra-body", default="",
                    help='JSON merged into the request, e.g. \'{"reasoning": {"effort": "low"}}\'')
    ap.add_argument("--quiet", action="store_true", help="no per-rollout progress line")
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
        "base_url": args.base_url if args.provider == "openai" else None,
        "extra_body": args.extra_body or None, "budget_usd": args.budget or None,
    }
    n = 0
    spent = 0.0
    truncated = 0
    stopped_on_budget = False
    consecutive_errors = 0
    last_error = ""
    aborted = ""
    total = len(args.tiers) * len(specs) * args.rollouts
    t_start = time.time()
    with out.open("w") as fh:
        fh.write(json.dumps({"meta": meta}) + "\n")
        for tier in args.tiers:
            for spec in specs:
                prompt = prompt_for(spec, tier, args.split)
                for k in range(args.rollouts):
                    if args.budget and spent >= args.budget:
                        stopped_on_budget = True
                        break
                    if consecutive_errors >= MAX_CONSECUTIVE_API_ERRORS:
                        aborted = last_error
                        break
                    t0 = time.time()
                    try:
                        text, info = answer(args, spec, tier, prompt, args.seed + k)
                        api_error = None
                    except Exception as exc:  # network / API errors are data too
                        text, info, api_error = "", {"usage": {}}, f"{type(exc).__name__}: {exc}"
                    gen_s = time.time() - t0
                    consecutive_errors = consecutive_errors + 1 if api_error else 0
                    last_error = api_error or last_error
                    report = score(text, spec)
                    cost = info.get("cost_usd")
                    spent += float(cost or 0.0)
                    finish = info.get("finish_reason")
                    truncated += finish == "length"
                    row = {
                        "run_id": run_id, "tier": tier, "spec_id": spec.id, "rollout": k,
                        "seed": args.seed + k, "reward": report.reward, "built": report.parsed,
                        "error": report.error, "api_error": api_error,
                        "checks": {c.name: c.passed for c in report.checks},
                        "gates_passed": bool(report.checks) and all(
                            c.passed for c in report.checks if c.name.startswith("gate:")),
                        "timeout": bool(report.error and "execution budget" in report.error),
                        "finish_reason": finish, "truncated": finish == "length",
                        "cost_usd": cost, "provider": info.get("provider"),
                        "completion_chars": len(text), "usage": info.get("usage") or {},
                        "gen_seconds": round(gen_s, 3), "completion": text,
                    }
                    fh.write(json.dumps(row) + "\n")
                    fh.flush()
                    n += 1
                    if not args.quiet:
                        elapsed = time.time() - t_start
                        eta = elapsed / n * (total - n)
                        money = f"  ${spent:.4f}" if spent else ""
                        warn = f"  truncated {truncated}" if truncated else ""
                        err = "  API ERROR" if api_error else ""
                        print(f"\r{tier} {n}/{total}  reward {report.reward:.2f}{money}{warn}{err}"
                              f"  eta {eta / 60:.0f} min   ", end="", file=sys.stderr, flush=True)
                if stopped_on_budget or aborted:
                    break
            if stopped_on_budget or aborted:
                break
    print(file=sys.stderr)
    if aborted:
        print(f"ABORTED after {MAX_CONSECUTIVE_API_ERRORS} API errors in a row (key, model id or network?). "
              f"Last error: {aborted}", file=sys.stderr)
    if stopped_on_budget:
        print(f"BUDGET REACHED (${spent:.4f} >= ${args.budget:.2f}): stopped after {n}/{total} rollouts",
              file=sys.stderr)
    if truncated:
        print(f"WARNING: {truncated}/{n} answers were cut off at --max-tokens {args.max_tokens}. "
              "Raise it (reasoning models need 8000+) before trusting these numbers.", file=sys.stderr)
    print(f"wrote {n} rollouts to {out}" + (f", spent ${spent:.4f}" if spent else ""))
    return 3 if aborted else 0


if __name__ == "__main__":
    raise SystemExit(main())
