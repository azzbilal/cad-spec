# ruff: noqa: E402
"""Pick OpenRouter models for a cad-spec run, with the cost estimated up front.

Reads OpenRouter's live model list (public endpoint, no key needed) and, for
each model, estimates what a full baseline costs: every tier x every eval
spec x rollouts, using token counts measured from the real cad-spec prompts.

    python scripts/openrouter_models.py                      # cheapest 40 text models
    python scripts/openrouter_models.py --search qwen coder  # filter by words in the id/name
    python scripts/openrouter_models.py --max-cost 0.50      # only runs under $0.50
    python scripts/openrouter_models.py --ids a/b c/d        # price specific models

Estimates, not quotes. Reasoning models are costed at --reasoning-tokens per
answer because their thinking is billed as output; the real run records the
exact cost of every call (usage.cost) and --budget enforces a hard stop.
Free (":free") models are listed but rate limited (50 calls/day on accounts
with under $10 of credit), too few for a 150-call run.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.tasks import TIERS, make_splits, prompt_for

MODELS_URL = "https://openrouter.ai/api/v1/models"
SYSTEM_PROMPT_TOKENS = 70     # the runner's system prompt, measured
ANSWER_TOKENS = 350           # a plain CadQuery answer, measured on local runs
CHARS_PER_TOKEN = 3.6         # English + code, conservative


def measured_prompt_tokens(tiers: list[str]) -> float:
    """Mean input tokens per call over the eval split for these tiers."""
    _, evals = make_splits()
    chars = [len(prompt_for(s, t, "eval")) for t in tiers for s in evals]
    return SYSTEM_PROMPT_TOKENS + sum(chars) / len(chars) / CHARS_PER_TOKEN


def fetch(path: str | None) -> list[dict]:
    if path:
        return json.loads(Path(path).read_text())["data"]
    req = urllib.request.Request(MODELS_URL, headers={"User-Agent": "cad-spec"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["data"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--search", nargs="*", default=[], help="all words must appear in the id or name")
    ap.add_argument("--ids", nargs="*", default=[], help="exact model ids to price")
    ap.add_argument("--tiers", nargs="+", default=list(TIERS))
    ap.add_argument("--rollouts", type=int, default=1)
    ap.add_argument("--max-cost", type=float, default=0.0, help="hide runs estimated above this (USD)")
    ap.add_argument("--reasoning-tokens", type=int, default=6000,
                    help="output tokens assumed per answer for reasoning models")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--free", action="store_true", help="include :free models")
    ap.add_argument("--from-file", default="", help="read a saved /models JSON instead of the network")
    args = ap.parse_args()

    _, evals = make_splits()
    calls = len(args.tiers) * len(evals) * args.rollouts
    tin = measured_prompt_tokens(args.tiers)

    rows = []
    for m in fetch(args.from_file):
        mid, name = m.get("id", ""), m.get("name", "")
        text = f"{mid} {name}".lower()
        if args.ids and mid not in args.ids:
            continue
        if args.search and not all(w.lower() in text for w in args.search):
            continue
        if mid.endswith(":free") and not (args.free or args.ids):
            continue
        modality = (m.get("architecture") or {}).get("output_modalities") or ["text"]
        if "text" not in modality:
            continue
        pricing = m.get("pricing") or {}
        try:
            p_in, p_out = float(pricing.get("prompt", 0)), float(pricing.get("completion", 0))
        except (TypeError, ValueError):
            continue
        if p_in < 0 or p_out < 0:  # routers with variable pricing report -1
            continue
        reasoning = "reasoning" in (m.get("supported_parameters") or [])
        tout = args.reasoning_tokens if reasoning else ANSWER_TOKENS
        cost = calls * (tin * p_in + tout * p_out)
        if args.max_cost and cost > args.max_cost:
            continue
        rows.append((cost, mid, p_in * 1e6, p_out * 1e6, m.get("context_length") or 0, reasoning))

    rows.sort()
    print(f"Estimate per model: {calls} calls ({', '.join(args.tiers)} x {len(evals)} specs x {args.rollouts}), "
          f"~{tin:.0f} input tokens/call, {ANSWER_TOKENS} output (reasoning: {args.reasoning_tokens}).\n")
    print(f"{'est. run $':>10}  {'$/M in':>7}  {'$/M out':>7}  {'context':>8}  {'think':>5}  model id")
    for cost, mid, pin, pout, ctx, reasoning in rows[: args.limit]:
        print(f"{cost:>10.3f}  {pin:>7.3f}  {pout:>7.3f}  {ctx:>8}  {'yes' if reasoning else '':>5}  {mid}")
    if not rows:
        print("(no models matched)")
    print("\nReasoning models: pass --max-tokens 8000 or more to run_baseline.py, or their answers get cut off.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
