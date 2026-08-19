"""Step 4: run the environment against a model you are not paying Prime for.

  Ollama (free):
      ollama pull qwen2.5-coder:1.5b
      py scripts/eval_local.py --model qwen2.5-coder:1.5b

  Anthropic (your API credits, useful for checking the task is solvable at all):
      py scripts/eval_local.py --provider anthropic --model claude-haiku-4-5-20251001

What you are looking for is NOT a high score. It is spread. If every rollout
scores identically, the rubric is not discriminating and training will flatline.

verifiers 0.1.14 returns {"metadata": ..., "outputs": [ {...}, {...} ]} where
each output dict carries reward, completion, error, and the per-function scores.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verifiers.types import ClientConfig

# provider -> (base url, env var holding the key, value to use if unset)
PROVIDERS = {
    "ollama": ("http://localhost:11434/v1", "OLLAMA_API_KEY", "ollama"),
    "anthropic": ("https://api.anthropic.com/v1", "ANTHROPIC_API_KEY", None),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="ollama", choices=sorted(PROVIDERS))
    ap.add_argument("--model", required=True)
    ap.add_argument("--num-examples", type=int, default=5)
    ap.add_argument("--rollouts", type=int, default=1)
    ap.add_argument("--show", type=int, default=1, help="how many rollouts to print in full")
    args = ap.parse_args()

    base_url, key_var, fallback = PROVIDERS[args.provider]
    if not os.environ.get(key_var):
        if fallback is None:
            print(f"set {key_var} first", file=sys.stderr)
            return 1
        os.environ[key_var] = fallback

    client_config = ClientConfig(
        client_type="openai_chat_completions",
        api_base_url=base_url,
        api_key_var=key_var,
    )

    from cad_spec.environment import load_environment

    env = load_environment()
    results = asyncio.run(
        env.evaluate(
            client_config,
            model=args.model,
            num_examples=args.num_examples,
            rollouts_per_example=args.rollouts,
        )
    )

    outputs = results["outputs"]
    rewards = [o.get("reward", 0.0) or 0.0 for o in outputs]

    print()
    print(f"rollouts {len(rewards)}")
    print(f"mean     {statistics.mean(rewards):.3f}")
    print(f"min      {min(rewards):.3f}")
    print(f"max      {max(rewards):.3f}")
    print(f"zeros    {sum(1 for r in rewards if r == 0)}/{len(rewards)}")
    print(f"spread   {len(set(round(r, 3) for r in rewards))} distinct values")
    print(f"values   {sorted(round(r, 3) for r in rewards)}")

    parses = [o.get("code_parses") for o in outputs if o.get("code_parses") is not None]
    if parses:
        print(f"parsed   {sum(1 for p in parses if p)}/{len(parses)} produced runnable CadQuery")

    errors = [str(o.get("error")) for o in outputs if o.get("error")]
    if errors:
        print()
        print("errors:")
        for msg, n in Counter(errors).most_common(5):
            print(f"  {n}x  {msg[:200]}")

    order = sorted(range(len(rewards)), key=lambda i: rewards[i])
    for rank, idx in enumerate(order[: max(0, args.show)]):
        print()
        print(f"--- rollout {idx} (reward {rewards[idx]:.3f}) ---")
        print(str(outputs[idx].get("completion"))[:2000])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
