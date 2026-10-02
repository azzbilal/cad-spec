> ## Documentation Index
> Fetch the complete documentation index at: https://docs.primeintellect.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Full Fine-Tuning (Beta)

> Dedicated full-parameter RL training on Hosted Training

<Note>
  Full fine-tuning is in **closed beta**. Access is gated per-team — reach out to us to get enabled.
</Note>

Full fine-tuning updates every parameter of the model on a dedicated cluster reserved for your run, instead of training a LoRA adapter on top of a shared deployment.

## Before you start

Full-FT runs dispatch onto a cluster that already has your base model in its local weight cache — runs never download weights at start-up. **A model that isn't cached can't be dispatched**, so check first:

```bash theme={null}
prime train models --fft-only
```

The table lists each cached model and the GPU types it's warm on. If the model you want is missing, reach out to us to get it added.

To see every GPU type you can dispatch on:

```bash theme={null}
prime train gpus
```

Two platform limits apply by default:

| Limit | Default |
| - | - |
| GPUs per run (trainer + inference, all pods) | 64 |
| Queued runs per user | 10 |

Reach out if your campaign needs more than that.

## Config

Full-FT runs use the native [prime-rl](https://github.com/PrimeIntellect-ai/prime-rl) config schema unchanged — no platform-specific fields. Size the run with `[deployment]`; its presence is what routes the run to full-FT dispatch (see [Launching a run](#launching-a-run)).

Minimal single-node example (1 trainer GPU + 1 inference GPU):

```toml theme={null}
name = "reverse-text-full-ft"
max_steps = 100
seq_len = 2048

[model]
name = "PrimeIntellect/Qwen3-0.6B-Reverse-Text-SFT"

[deployment]
num_train_gpus = 1
num_infer_gpus = 1

[trainer.optim]
lr = 3e-6

[orchestrator]
batch_size = 64
group_size = 8

[orchestrator.train.sampling]
max_completion_tokens = 512

[[orchestrator.train.source]]
name = "reverse-text"

[orchestrator.train.source.env.taskset]
id = "reverse-text"

[orchestrator.train.source.env.agent.harness]
id = "null"

[orchestrator.train.source.env.agent.runtime]
type = "subprocess"

# This fine-tune's name misses the renderer map's exact match, so select explicitly.
[orchestrator.renderer]
name = "prime-qwen3"

[inference]
```

Multi-node example (2 train nodes + 2 inference nodes, each a full 8-GPU node):

```toml theme={null}
name = "qwen30b-math"
seq_len = 32768

[model]
name = "Qwen/Qwen3-30B-A3B-Thinking-2507"

[deployment]
type = "multi_node"                # required — `single_node` is the default variant
num_train_nodes = 2
num_infer_nodes = 2                # per inference replica; see `num_infer_replicas`

[trainer.model]
attn = "flash_attention_3"
ep = 8                             # expert parallel (MoE)

[trainer.optim]
type = "adamw"
lr = 1e-6

[orchestrator]
batch_size = 512
max_off_policy_steps = 8

[orchestrator.concurrency]
max_inflight = 1024                # ceiling on in-flight episodes

[orchestrator.train.sampling]
max_completion_tokens = 32768

[[orchestrator.train.source]]
name = "math"

[orchestrator.train.source.env.taskset]
id = "i3_math"

[orchestrator.train.source.env.agent.harness]
id = "null"

[orchestrator.train.source.env.agent.runtime]
type = "subprocess"

[inference.vllm]
tensor_parallel_size = 8           # tensor parallel inside each inference replica
```

<Note>
  Training and eval environments are arrays of `source` tables, each carrying a nested `env` block (`env.taskset`, `env.agent.harness`, `env.agent.runtime`). The older flat `[[orchestrator.train.env]]` shape with an `id` field was removed from prime-rl and is rejected at dispatch — see [Environments](/prime-rl/configuration#environments) for the current shape.
</Note>

<Tip>
  Multi-node runs broadcast weights over NCCL by default and auto-discover the cluster's RDMA devices — no extra config needed.
</Tip>

See the [prime-rl docs](/prime-rl/configuration) and [config examples](https://github.com/PrimeIntellect-ai/prime-rl/tree/main/configs) for the full schema.

## Launching a run

Same CLI as LoRA. A config with a `[deployment]` block is auto-detected and dispatched on the full-FT endpoint — no flag needed:

```bash theme={null}
prime train run configs/full-ft.toml
```

Pass `--full-finetune` (or `--fft`) explicitly if your config doesn't have `[deployment]` yet; either way, an explicit `[deployment]` block is required before dispatch — without one you get an error before any GPU is reserved.

On dispatch you get a run ID and a dashboard link:

```
Dispatched hosted run wn2cjdrzdo6bmfqajoeuu30p

Monitor run at:
  https://app.primeintellect.ai/dashboard/training/wn2cjdrzdo6bmfqajoeuu30p
```

Pass credentials with `-e / --env-var` or `--env-file`:

```bash theme={null}
prime train run configs/full-ft.toml -e WANDB_API_KEY -e HF_TOKEN -e OPENAI_API_KEY
```

`-e KEY` reads the value from your shell, `-e KEY=VALUE` sets it inline, and `--env-file path/to/.env` loads a whole file.

Every key you pass is written to a per-run secret and projected onto the trainer, inference, orchestrator, and env-server pods, so an environment that needs a third-party API key can read it straight from the process environment. `WANDB_API_KEY` and `HF_TOKEN` are recognized and routed to their own fields.

A few constraints on the secret map:

| Constraint | Value |
| - | - |
| Entries per run | 32 |
| Name | POSIX env-var name, ≤ 128 chars |
| Value | ≤ 32 KB |
| Total | ≤ 256 KB |

<Note>
  `WANDB_API_KEY` is required for the `[wandb]` block to take effect — without it the block is stripped and the run trains without W\&B logging.
</Note>

Two dispatch-level knobs are full-FT only. Both accept a CLI flag or a top-level TOML key, and the flag wins:

| Knob | Flag | TOML | Default |
| - | - | - | - |
| prime-rl image build | `--image-tag v0.5.1` | `image_tag = "v0.5.1"` | `main` |
| GPU type to dispatch on | `--gpu-type H200_141GB` | `gpu_type = "H200_141GB"` | auto-pick |

To keep run outputs across runs, create a [volume](/hosted-training/volumes) and pass its name with `--volume`. Each run writes to its own `runs/<runId>/` directory on the volume.

## Run lifecycle

A dispatched run moves through:

```
QUEUED → PENDING → CREATING → PULLING_IMAGE → RUNNING → COMPLETED / FAILED / STOPPED
```

* **QUEUED** — no cluster has GPU headroom yet. The run is admitted and promoted automatically as capacity frees; you don't need to resubmit.
* **PULLING\_IMAGE** — pods are scheduled and pulling the prime-rl image. This is multiple GB and can take many minutes on a cold node. It's expected, not a stall.

Config errors (bad schema, uncached model, oversized deployment) are caught synchronously and fail the dispatch immediately with a reason, before any GPU is reserved.

Stop a run early to release the cluster:

```bash theme={null}
prime train stop <run-id>
```

<Warning>
  When a run reaches a terminal state, its cluster resources are torn down automatically. Orchestrator logs are captured to the run record first, but trainer, inference, and env-server pod logs go away with the pods — pull anything you need while the run is live. Metrics, samples, distributions, and progress are persisted and stay available in the dashboard.
</Warning>

## Monitoring

A full-FT run has several distinct components. Pick which one to read with `-c / --component`:

```bash theme={null}
prime train logs <run-id>                  # orchestrator (default)
prime train logs <run-id> -c trainer       # trainer (FSDP / torchrun)
prime train logs <run-id> -c inference     # vLLM inference server
prime train logs <run-id> --env <env-name> # env-server for a specific env
```

List the orchestrator and env-server components for a run:

```bash theme={null}
prime train components <run-id>
```

Follow and filter the same way as LoRA — `-f`, `--search`, `--regex`, `--level`, `--since`. See [Monitoring](/hosted-training/end-to-end-run#step-6-monitor-the-run) for details.

The dashboard works as it does for LoRA runs: reward curves, rubric scores, and individual rollouts at `https://app.primeintellect.ai/dashboard/training/<run-id>`.

<CardGroup cols={2}>
  <Card title="End-to-End Run" icon="rocket" href="/hosted-training/end-to-end-run">
    LoRA walkthrough — most workflow steps apply identically.
  </Card>

  <Card title="prime-rl Configuration" icon="gear" href="/prime-rl/configuration">
    Full reference for the underlying training framework config schema.
  </Card>
</CardGroup>


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.