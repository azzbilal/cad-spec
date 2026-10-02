> ## Documentation Index
> Fetch the complete documentation index at: https://docs.primeintellect.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Models & Pricing

> Supported models and pricing for Hosted Training

This page lists supported models and per-token pricing for the legacy shared LoRA service. Full fine-tuning (FFT) is currently in closed beta.

<Warning>
  Shared Hosted Training for LoRA runs will stop accepting new runs on October 5, 2026. Hosted Training is transitioning to dedicated runs. Existing LoRA adapters will remain downloadable and deployable until further notice.
</Warning>

## Available Models

Prices are per million tokens, billed separately for input, output, and training.

| Model | Input (\$ / 1M) | Output (\$ / 1M) | Train (\$ / 1M) |
| - | - | - | - |
| `Qwen/Qwen3.5-0.8B` | 0.02 | 0.06 | 0.06 |
| `Qwen/Qwen3.5-2B` | 0.05 | 0.15 | 0.15 |
| `Qwen/Qwen3.5-4B` | 0.10 | 0.30 | 0.30 |
| `Qwen/Qwen3.5-9B` | 0.20 | 0.60 | 0.60 |
| `Qwen/Qwen3.5-35B-A3B` | 0.25 | 0.75 | 1.00 |
| `Qwen/Qwen3.6-35B-A3B` | 0.25 | 0.75 | 1.00 |
| `meta-llama/Llama-3.2-1B-Instruct` | 0.02 | 0.06 | 0.06 |
| `meta-llama/Llama-3.2-3B-Instruct` | 0.05 | 0.15 | 0.15 |
| `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` | 0.15 | 0.45 | 0.60 |
| `openai/gpt-oss-20b` | 0.10 | 0.30 | 0.40 |
| `poolside/Laguna-XS.2` | 0.00 | 0.00 | 0.00 |
| `sprints/Llama-3.2-1B-Instruct` | 0.00 | 0.00 | 0.00 |

## Choosing a Model

### For Validation and Debugging

Start with a small, fast model to verify your environment and config work correctly before committing compute to a larger run.

**Recommended:** `Qwen/Qwen3.5-0.8B` or `meta-llama/Llama-3.2-1B-Instruct`

```toml theme={null}
model = "Qwen/Qwen3.5-0.8B"
max_steps = 50
batch_size = 128
rollouts_per_example = 8
```

### For Experimentation

MoE models with small active parameter counts give strong performance per token.

**Recommended:** `Qwen/Qwen3.5-35B-A3B`

```toml theme={null}
model = "Qwen/Qwen3.5-35B-A3B"
max_steps = 200
batch_size = 256
rollouts_per_example = 16
```

### For Production Training

For serious training runs where you want the strongest results available, use a flagship MoE model.

**Recommended:** `Qwen/Qwen3.6-35B-A3B`

```toml theme={null}
model = "Qwen/Qwen3.6-35B-A3B"
max_steps = 500
batch_size = 512
rollouts_per_example = 16
```

### Thinking Mode

Qwen3.5 and Nemotron models support a thinking mode that produces extended chain-of-thought reasoning before the final answer. Toggle it via `[sampling].enable_thinking` in your config. Thinking mode tends to help on tasks that benefit from multi-step reasoning (math, code, logic) at the cost of longer outputs.

## Checking Available Models

Always use the CLI to check the current list of supported models:

```bash theme={null}
prime train models
```

Add `--output json` to get the live pricing alongside the model list. This may differ from this page as models are being added regularly.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.