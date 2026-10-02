> ## Documentation Index
> Fetch the complete documentation index at: https://docs.primeintellect.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Advanced Configurations

> Full configuration reference for Hosted Training runs

The legacy shared LoRA service uses a `.toml` config file. This page covers its configuration fields, from basic setup to multi-environment training, online evaluation, and W\&B integration. Full fine-tuning (FFT) is currently in closed beta.

<Warning>
  Shared Hosted Training for LoRA runs will stop accepting new runs on October 5, 2026. Hosted Training is transitioning to dedicated runs. Existing LoRA adapters will remain downloadable and deployable until further notice.
</Warning>

Hosted Training accepts both Verifiers environment config shapes:

* **Legacy (Verifiers v0) environments** use `id` and optional `args`.
* **Verifiers v1 (taskset/harness) environments** use `taskset = { ... }` and optional `harness = { ... }`.

The outer Hosted Training config still uses `[[env]]` and `[[eval.env]]`; the native `prime-rl` equivalent is `[[orchestrator.train.env]]` and `[[orchestrator.eval.env]]`. See [the environment model](/hosted-training/environment-model#legacy-and-verifiers-v1-environment-configs) for the conceptual difference between the two shapes.

## Full Config Reference

Below is a complete annotated config showing all available fields. Required fields are uncommented; optional fields are shown as comments with their defaults.

```toml theme={null}
# ============================================================
# Core Configuration (required)
# ============================================================
model = "Qwen/Qwen3-30B-A3B-Instruct-2507"   # HuggingFace model ID
max_steps = 100                                # Total training steps
batch_size = 256                               # Rollouts per training batch
rollouts_per_example = 8                       # Rollouts generated per dataset example

# ============================================================
# Training Hyperparameters (optional)
# ============================================================
# learning_rate = 1e-4                         # Learning rate for LoRA
# lora_alpha = 16                              # LoRA alpha scaling factor
# oversampling_factor = 2.0                    # Oversample factor for rollout generation
# trajectory_strategy = "interleaved"          # "interleaved" or "branching"

# ============================================================
# Secrets (optional)
# ============================================================
# env_file = ["secrets.env"]                   # File(s) containing environment secrets

# ============================================================
# Sampling Configuration (required)
# ============================================================
[sampling]
max_tokens = 512                               # Max tokens per model response
# enable_thinking = false                      # Toggle thinking mode (Qwen3.5, Nemotron)
# reasoning_effort = "high"                    # Reasoning effort: "low" | "medium" | "high" (GPT-OSS)

# ============================================================
# Environment(s) (at least one required)
# ============================================================
[[env]]
id = "primeintellect/alphabet-sort"            # Environments Hub ID (owner/name)
# args = { min_turns = 3, max_turns = 5 }      # Arguments passed to load_environment()

# Verifiers v1 taskset/harness shape:
# [[env]]
# name = "alphabet-sort"
# taskset = { id = "alphabet-sort-v1", min_turns = 3, max_turns = 5, power_per_turn = false }
# harness = { id = "default", runtime = { type = "subprocess" } }

# Add multiple [[env]] sections for multi-environment training:
# [[env]]
# id = "primeintellect/another-env"
# args = { split = "train", max_examples = 1000 }

# ============================================================
# Weights & Biases Logging (optional)
# ============================================================
# [wandb]
# project = "my-project"                       # W&B project name
# name = "my-run-name"                         # W&B run name
# entity = "my-team"                           # W&B team/entity

# ============================================================
# Online Evaluation (optional)
# ============================================================
# [eval]
# interval = 100                               # Run eval every N training steps
# num_examples = -1                            # Number of eval examples (-1 = all)
# rollouts_per_example = 1                     # Rollouts per eval example
# skip_first_step = false                      # Skip the pre-training eval of the base model
#
# [eval.sampling]                              # Eval-time sampling overrides
# max_tokens = 2048                            # Max tokens per eval response
# temperature = 0.0                            # Eval sampling temperature
# enable_thinking = false                      # Toggle thinking mode at eval time
# reasoning_effort = "high"                    # Reasoning effort at eval time
#
# [[eval.env]]                                 # Environment-specific eval overrides
# id = "primeintellect/eval-env"
# args = { split = "test" }
# num_examples = 30
# rollouts_per_example = 4
#
# Verifiers v1 eval envs use the same taskset/harness shape:
# [[eval.env]]
# taskset = { id = "gsm8k-v1", split = "test" }
# harness = { id = "default", runtime = { type = "subprocess" } }
# num_examples = 256
# group_size = 4

# ============================================================
# Validation During Training (optional)
# ============================================================
# [val]
# num_examples = 64                            # Validation examples per check
# rollouts_per_example = 1                     # Rollouts per validation example
# interval = 5                                 # Validate every N steps

# ============================================================
# Rollout Filters (optional)
# ============================================================
# [[pre_batch_filters]]                        # Applied before rollouts fill a batch slot
# type = "zero_advantage"                      # "gibberish" | "repetition" | "zero_advantage"
# enforce = true                               # Drop flagged rollouts (false = metrics only)
#
# [[post_batch_filters]]                       # Applied after a batch is assembled
# type = "repetition"
# enforce = false

# ============================================================
# Warm-Start from Checkpoint (optional)
# ============================================================
# checkpoint_id = "..."                        # Resume training from an existing checkpoint

# ============================================================
# Checkpoints (optional)
# ============================================================
# [checkpoints]
# interval = 100                               # Save checkpoint every N steps
# keep_cloud = 5                               # Keep N checkpoints in cloud (-1 = keep all)

# ============================================================
# Adapters (optional)
# ============================================================
# [adapters]
# interval = 0                                 # Upload adapter every N steps (0 = only at run end)
# keep_last = 3                                # Keep N adapters in cloud (-1 = keep all)

# ============================================================
# Infrastructure (optional)
# ============================================================
# [infrastructure]
# compute_size = "M"                           # CPU allocation: S, M (default), or L
```

## Field Reference

### Core Fields

| Field | Type | Required | Description |
| - | - | - | - |
| `model` | string | ✓ | HuggingFace model ID. Must be a [supported model](/hosted-training/models-and-pricing). Run `prime train models` to see available options. |
| `max_steps` | integer | ✓ | Total number of training steps. |
| `batch_size` | integer | ✓ | Number of rollouts consumed per training batch. Larger values improve stability. |
| `rollouts_per_example` | integer | ✓ | Number of rollouts generated per dataset example. Higher values give more reward signal diversity. |
| `checkpoint_id` | string | — | Checkpoint ID to warm-start from. The checkpoint must be in READY status, accessible to you, and from a run using the same model. See [Warm-Starting from a Checkpoint](#warm-starting-from-a-checkpoint). |

### Training Hyperparameters

| Field | Type | Default | Description |
| - | - | - | - |
| `learning_rate` | float | `1e-4` | Learning rate for the LoRA adapter. |
| `lora_alpha` | integer | `16` | LoRA alpha scaling factor. Controls the magnitude of LoRA updates. |
| `oversampling_factor` | float | `2.0` | Generate this many more rollouts than needed per batch to ensure sufficient data. |
| `trajectory_strategy` | string | `"interleaved"` | How multi-turn trajectories are generated. `"interleaved"` runs turns across examples concurrently. `"branching"` generates full trajectories per example before moving on. |
| `env_file` | array of strings | `[]` | Path(s) to `.env` files containing secrets (e.g., API keys). See [Secrets Management](#secrets-management). |

### Sampling

| Field | Type | Required | Description |
| - | - | - | - |
| `[sampling].max_tokens` | integer | ✓ | Maximum number of tokens the model can generate per response turn. |
| `[sampling].enable_thinking` | boolean | — | Toggle thinking mode for supported models. Mutually exclusive with `reasoning_effort`. |
| `[sampling].reasoning_effort` | string | — | Reasoning effort for supported models. One of `"low"`, `"medium"`, `"high"`. Mutually exclusive with `enable_thinking`. |

### Eval Sampling

Overrides the inference server's default sampling for eval-time rollouts only. All fields are optional; when the whole `[eval.sampling]` block is omitted, eval uses the server defaults.

| Field | Type | Required | Description |
| - | - | - | - |
| `[eval.sampling].max_tokens` | integer | — | Maximum tokens generated per eval response turn. |
| `[eval.sampling].temperature` | float | — | Eval sampling temperature. `0.0` for deterministic eval scoring. |
| `[eval.sampling].extra_body` | table | — | Free-form extra parameters forwarded with each eval request to the inference server. |
| `[eval.sampling].enable_thinking` | boolean | — | Toggle thinking mode at eval time for supported models. Mutually exclusive with `reasoning_effort`. |
| `[eval.sampling].reasoning_effort` | string | — | Reasoning effort at eval time for supported models. One of `"low"`, `"medium"`, `"high"`. Mutually exclusive with `enable_thinking`. |

### Environment

Each `[[env]]` entry must provide either a legacy (Verifiers v0) `id` or a Verifiers v1 `taskset.id`.

| Field | Type | Required | Description |
| - | - | - | - |
| `[[env]].id` | string | Either `id` or `taskset.id` | Legacy environment ID. Use `owner/name` for an Environments Hub package, or a bare id for a runtime-installed/local environment. |
| `[[env]].args` | table | — | Legacy v0 arguments passed to `load_environment(**args)`. |
| `[[env]].name` | string | — | Display name for this environment instance. Defaults to `id` or `taskset.id`. Use this when the same env appears more than once. |
| `[[env]].taskset` | table | Either `id` or `taskset.id` | v1 taskset config. Must include `id`, plus taskset-specific fields such as `split`, `min_turns`, or dataset options. |
| `[[env]].harness` | table | — | v1 harness config. If omitted, the runtime default harness is used. Include `runtime` when the harness should run in a specific backend such as `subprocess` or `modal`. |
| `[[env]].ratio` | float | — | Relative sampling weight for multi-environment v1 runs. If one env sets `ratio`, set it on all envs in the group. |
| `[[env]].group_size` | integer | — | Per-environment rollout group size for v1 training. Defaults to the top-level `rollouts_per_example`. |
| `[[env]].pool` | table | — | v1 env-server worker pool config, for example `{ type = "static", num_workers = 4 }`. |
| `[[env]].timeout` | table | — | v1 rollout/setup/scoring timeout config. |
| `[[env]].retries` | table | — | v1 retry policy config. |
| `[[env]].sampling` | table | — | Per-environment v1 sampling overrides. |
| `[[env]].max_turns` | integer | — | Per-environment turn limit. |
| `[[env]].max_input_tokens` | integer | — | Per-environment input-token limit. |
| `[[env]].max_output_tokens` | integer | — | Per-environment output-token limit. |
| `[[env]].max_total_tokens` | integer | — | Per-environment total-token limit. |
| `[[env]].multiplex` | integer | — | v1 environment multiplexing setting. |

`taskset.id`, `harness.id`, and legacy `id` can be bare runtime ids or Hub refs. Bare ids such as `"alphabet-sort-v1"` or `"default"` are resolved by the installed runtime package. Slash-shaped ids such as `"team/my-taskset"` are resolved through the Environments Hub and can include `@version`.

### Legacy (Verifiers v0) envs

Use `id` and optional `args` for existing Verifiers environments that expose `load_environment(**args)`:

```toml theme={null}
[[env]]
id = "primeintellect/alphabet-sort"
args = { min_turns = 3, max_turns = 5 }
```

### Verifiers v1 (taskset/harness) envs

Use `taskset` and `harness` for Verifiers v1 environments:

```toml theme={null}
[[env]]
name = "alphabet-sort"
taskset = { id = "alphabet-sort-v1", min_turns = 3, max_turns = 5, power_per_turn = false }
harness = { id = "default", runtime = { type = "subprocess" } }
```

`taskset` owns task data, task controls, rewards, metrics, and task-owned tools. `harness` selects the program that drives the model — the built-in `default` harness, or an agent harness such as `bash` or `codex` — and its nested `runtime` field selects where that program runs: a local `subprocess`, or a `docker`/`prime`/`modal` sandbox.

## Multi-Environment Training

You can train on multiple environments simultaneously by adding multiple `[[env]]` sections:

```toml theme={null}
[[env]]
id = "primeintellect/alphabet-sort"
args = { min_turns = 3, max_turns = 5 }

[[env]]
id = "primeintellect/gsm8k"
args = { split = "train" }
```

For Verifiers v1 envs, put sampling weights directly on each `[[env]]` entry:

```toml theme={null}
[[env]]
name = "alphabet-sort"
taskset = { id = "alphabet-sort-v1", min_turns = 3, max_turns = 5 }
harness = { id = "default", runtime = { type = "subprocess" } }
ratio = 0.75

[[env]]
name = "gsm8k"
taskset = { id = "gsm8k-v1", split = "train" }
harness = { id = "default", runtime = { type = "subprocess" } }
ratio = 0.25
```

## Online Evaluation

Enable periodic evaluation during training to track progress without interrupting the run:

```toml theme={null}
[eval]
interval = 100                    # Evaluate every 100 steps
num_examples = -1                 # Use all eval examples
rollouts_per_example = 1
skip_first_step = false           # Evaluate the base model before training starts

[[eval.env]]
id = "primeintellect/alphabet-sort"
args = { split = "test" }
num_examples = 50
rollouts_per_example = 4
```

The `[eval]` section sets global defaults, and `[[eval.env]]` sections can override settings per environment.

Verifiers v1 eval entries use the same `taskset`/`harness` shape. `group_size` is the v1 name for per-env eval rollouts; `rollouts_per_example` is still accepted for compatibility.

```toml theme={null}
[[eval.env]]
taskset = { id = "alphabet-sort-v1", split = "test" }
harness = { id = "default", runtime = { type = "subprocess" } }
num_examples = 50
group_size = 4
```

### Eval Sampling

Eval rollouts use the inference server's default sampling unless overridden via `[eval.sampling]`. The fields mirror `[sampling]` and `[teacher.sampling]` so the same knobs work everywhere — most commonly, you'd turn thinking off at eval time to get deterministic, faster scoring on a model that uses chain-of-thought during training:

```toml theme={null}
[eval.sampling]
max_tokens = 2048
temperature = 0.0
enable_thinking = false           # Disable thinking at eval time
# reasoning_effort = "high"       # Or constrain reasoning effort
```

`enable_thinking` and `reasoning_effort` are mutually exclusive — set at most one. Both ride on `extra_body.chat_template_kwargs` under the hood; you can also set `extra_body` directly if you need other chat-template controls.

## Validation

Validation is a lightweight check that runs more frequently than full evaluation:

```toml theme={null}
[val]
num_examples = 64
rollouts_per_example = 1
interval = 5                      # Validate every 5 steps
```

This uses the training environment's validation split (if available) and reports metrics to W\&B and the dashboard.

## Rollout Filters

prime-rl filters rollouts at two points in the training pipeline. `[[pre_batch_filters]]` run before a rollout enters the training batch, so flagged rollouts never consume a batch slot; `[[post_batch_filters]]` run after a batch is assembled, and flagged rollouts are recorded but not shipped to the trainer. Three filter types are available — `gibberish`, `repetition`, and `zero_advantage` — and each either records detection metrics only (`enforce = false`) or drops flagged rollouts (`enforce = true`).

By default, all three filters run in monitor mode pre-batch and `zero_advantage` is enforced post-batch. Setting either section replaces the default filter list for that slot.

To focus training compute on examples with useful reward signal — the successor to the removed difficulty buffer's `online_difficulty_filtering` — enforce the zero-advantage filter pre-batch:

```toml theme={null}
[[pre_batch_filters]]
type = "zero_advantage"
enforce = true
```

Type-specific tuning knobs (such as `repetition`'s `window` and `prob_threshold`) pass through to the trainer as written.

## Checkpoints

Control how often checkpoints are saved and how many are retained in cloud storage:

```toml theme={null}
[checkpoints]
interval = 100    # Save checkpoint every 100 steps
keep_cloud = 5    # Keep last 5 checkpoints in cloud
```

| Field | Type | Default | Description |
| - | - | - | - |
| `interval` | integer | cluster default | Save a checkpoint every N training steps. |
| `keep_cloud` | integer | `5` | Number of checkpoints to retain in cloud storage. Set to `-1` to keep all checkpoints. |

Checkpoints enable resuming training from a specific step if a run is interrupted. They're automatically uploaded to cloud storage and can be used to create new runs from a saved state.

## Warm-Starting from a Checkpoint

Start a new run from an existing checkpoint by setting `checkpoint_id` at the top level of your config. The checkpoint must be READY, use the same model, and you need access to the original run.

```toml theme={null}
checkpoint_id = "cp_abc123"
```

List available checkpoints with `prime train checkpoints <run-id>`.

## Adapters

Configure periodic adapter uploads during training. Adapters are LoRA weights that can be deployed for inference.

```toml theme={null}
[adapters]
interval = 100    # Upload adapter every 100 steps
keep_last = 3     # Keep last 3 adapters in cloud
```

| Field | Type | Default | Description |
| - | - | - | - |
| `interval` | integer | `0` | Upload adapter every N training steps. Set to `0` to only upload the final adapter at run end. |
| `keep_last` | integer | `3` | Number of adapters to retain in cloud storage. Set to `-1` to keep all adapters. |

<Note>
  Deployed adapters are protected from automatic cleanup. If you deploy an adapter for inference, it will not be deleted even if it exceeds the `keep_last` limit.
</Note>

## Infrastructure

Control the CPU and memory resources allocated to your environment containers. This only affects the environments you provide — trainer and inference infrastructure is fully managed by us.

```toml theme={null}
[infrastructure]
compute_size = "L"
```

| Size | Description |
| - | - |
| `S` | Lower CPU allocation. Suitable for lightweight environments. |
| `M` | Default. Balanced allocation for most workloads. |
| `L` | High CPU allocation. Use for environments that compile code or for vision-language models with heavy image processing. |

<Note>
  If not specified, runs default to `M`. Most users won't need to change this — use `L` if you notice slow CPU-bound operations during training.
</Note>

## Tailscale Networking

<Note>
  Tailscale networking is an **enterprise-only** feature. Contact your account team to enable it on your organization.
</Note>

When enabled, every env-server (training and eval) for the run joins your Tailscale tailnet via a sidecar. From inside your environment code you can then reach private services — internal APIs, MCP servers, datasets behind a VPN — by their Tailscale IP, MagicDNS hostname, or by native LAN IP if a [subnet router](https://tailscale.com/kb/1019/subnets) advertises it.

```toml theme={null}
[tailscale]
enabled = true
# auth_key = "tskey-auth-..."        # preferably via TAILSCALE_AUTH_KEY env var
# hostname_prefix = "prime-hosted-training"
```

| Field | Type | Default | Description |
| - | - | - | - |
| `[tailscale].enabled` | boolean | `false` | Toggle the per-run sidecar. |
| `[tailscale].auth_key` | string | — | Tailscale [pre-authenticated key](https://tailscale.com/kb/1085/auth-keys) (must start with `tskey-auth-`). OAuth client secrets are not supported. Prefer the `TAILSCALE_AUTH_KEY` environment variable so the secret is not committed to `rl.toml`. |
| `[tailscale].hostname_prefix` | string | `"prime-hosted-training"` | Prefix for the Tailscale node name. The full name is derived as `{prefix}-env-{idx}-{run_id}`. 1–30 lowercase alphanumeric chars or hyphens, must start with a letter. |

<Tip>
  Use a **tagged**, ephemeral, reusable auth key. Tagged keys let you scope the env-servers in your tailnet ACL without granting them the same access as a user-owned device.
</Tip>

## Weights & Biases Integration

Log training metrics, reward curves, and rollout samples to W\&B:

```toml theme={null}
[wandb]
project = "my-rl-experiments"
name = "qwen3-30b-alphabet-sort"
entity = "my-team"
```

When W\&B is configured, all training metrics, evaluation results, and sample rollouts are logged automatically.

## Secrets Management

<Tip>
  The recommended way to supply secrets to Hosted Training is via [environment secrets](/tutorials-environments/secrets). Secrets linked or added to your environment are automatically injected at runtime — no config changes needed.
</Tip>

If you prefer to supply secrets via a file, you can use `env_file` in your training config instead:

```toml theme={null}
env_file = ["secrets.env"]
```

The `secrets.env` file should contain key-value pairs:

```
OPENAI_API_KEY=sk-...
CUSTOM_API_KEY=...
```

You can also manage secrets via the CLI:

```bash theme={null}
prime secret list              # list global secrets
prime env secret list my-env   # list secrets for an environment
```

In your environment code, validate required keys early using `vf.ensure_keys()`:

```python theme={null}
def load_environment(api_key_var: str = "OPENAI_API_KEY") -> vf.Environment:
    vf.ensure_keys([api_key_var])
    # ...
```

<CardGroup cols={2}>
  <Card title="End-to-End Run" icon="rocket" href="/hosted-training/end-to-end-run">
    Walk through a complete training run step by step.
  </Card>

  <Card title="Troubleshooting" icon="wrench" href="/hosted-training/troubleshooting">
    Solutions for common issues with Hosted Training.
  </Card>
</CardGroup>


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.