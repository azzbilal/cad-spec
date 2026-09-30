# Training run 1: can RL teach what the cheat-sheet cannot? (pre-registration)

Registered 29 September 2026, before any training run, adapter or test-split
answer exists. Thresholds, configuration and analysis below are fixed. Any
change is a dated entry in "Amendments", made before the data it concerns.

## 1. Question

The hint experiment ([hint-feedback.md](hint-feedback.md)) showed that a
seven-line CadQuery cheat-sheet removes knowledge failures (API misuse,
stacked drilling) but leaves reasoning failures untouched: propagating an
engineering change order to the hole pitch (L4) and deriving the pitch from
the edge margin (L2). This run asks whether reinforcement learning on
cad-spec's measured reward closes part of that reasoning gap, for a model that
already has the cheat-sheet.

## 2. Evidence behind the design (step 3, screening)

Qwen3.5-9B on the 30 development specs, cheat-sheet on, thinking off. Runs in
`results/training/screening/`, report `results/training/screening/report.md`.

| | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Greedy all-pass (1,024 tokens) | 80% | 63% | 87% | 43% |
| Temperature 0.7, 2,048 tokens, 8 samples: all-pass | 62% | 69% | 64% | 43% |
| Groups with signal, binary reward | 100% | 97% | 100% | 30% |
| Mean abs advantage, binary reward | 0.426 | 0.393 | 0.419 | 0.093 |

- Temperature 1.0 with 1,024 tokens cut 10% of answers off and dropped L1 to
  L3 to about 40%; 0.7 with 2,048 tokens cut 1% off.
- L4 fails one way: 137 of its failed answers miss R5 (hole pattern) and R7
  (edge margin) together, the plate changed but the pitch did not.
- prime-rl's GRPO advantage is the reward minus the group mean, without
  division by the standard deviation (prime-rl `algo/grpo.py`, commit
  `9eacd47`). Under partial credit that failure scores 7/9 = 0.78, so its
  lesson is small; hence the binary training reward (cad-spec 0.4.2).

## 3. Design

| Item | Registered value |
|---|---|
| Base model | `Qwen/Qwen3.5-9B` (Hosted Training, LoRA) |
| Environment | `bazzouzi/cad-spec@0.4.2`, wheel SHA-256 `482d399c5cc374f7a564eacfded927cc09aacd879fa9756fb34881efe455c6cb`, verify_hub 200/200 IDENTICAL. **Amendment 1: 0.4.3**, packaging fix; **Amendment 2: 0.4.4**, rollout-input fix; **Amendment 3: 0.4.5**, CadQuery loads on the training image; same scoring |
| Scorer | 0.4.0 (unchanged since the leaderboard) |
| Training reward | binary: 1.0 only when all nine requirements pass (`reward = "binary"`) |
| Prompt | system prompt plus the packaged cheat-sheet (`hints = true`), training and evaluation alike |
| Training data | train split only (200 specs per tier); the test split is never used in training |
| Tier mix | L4 0.50, L2 0.25, L1 + L3 0.25 (`ratio` per `[[env]]`) |
| Sampling | temperature 0.7, 2,048 tokens, thinking off; top_p 1, no top_k (Hosted Training has no truncation fields) |
| Groups | 8 rollouts per example, batch 128 rollouts per step |
| Filter | zero-advantage groups kept out of each batch |
| Hyperparameters | Hosted Training defaults (learning rate, LoRA), recorded from the run afterwards |
| Adapter | the end-of-run adapter only: no checkpoint selection |
| Configs | [configs/rl/cad-spec-9b.toml](../../configs/rl/cad-spec-9b.toml) and [configs/rl/cad-spec-9b-smoke.toml](../../configs/rl/cad-spec-9b-smoke.toml), both validated against the Prime CLI 0.8.0 schema |

## 4. Hypotheses and analysis

Evaluation on the locked test split (60 specs, `TEST_SPLIT_SHA256`
`019d197e...`, never seen before), tiers L1 to L4, greedy, 2,048 tokens,
thinking off, cheat-sheet on, both models served by Prime Inference. Base:
`Qwen/Qwen3.5-9B`. Adapter: `Qwen/Qwen3.5-9B:<adapter_id>`. Both runs are made
after training, on the same day, once each. The analysis is
[scripts/compare_training.py](../../scripts/compare_training.py), written and
tested before any data (self-test `scripts/test_compare_training.py` in CI).

- **H1 (primary, the claim).** Adapter all-pass on L2 and L4 together exceeds
  the base: the 95% bootstrap interval of the paired difference (120 pairs,
  specs resampled with both tiers together, 10,000 resamples, seed 20261001)
  lies above 0. The gain is called **worthwhile** if the point estimate is at
  least **+10 points**.
- **H2 (secondary).** The same on L4 alone. Reported, not claimed.
- **Regression check.** L1 and L3: a point-estimate drop of more than 10
  points is reported as a regression next to the verdict.
- **Refusal.** A run that departs from the conditions above (split,
  fingerprint, temperature, tokens, prompt, thinking, scorer, completeness,
  API errors, 5% or more truncated) is not analysed. The script says why.

## 5. Power

Simulated with the greedy screening rates (L2 63%, L4 43%), 60 specs, the
registered test, and a pessimistic 5% of base passes lost by the adapter:

| True gain on L2 + L4 | +5 points | +10 points | +15 points | +20 points |
|---|---|---|---|---|
| Probability H1 is confirmed | 43% | 84% | 96% | 100% |

The test split is sized for the worthwhile gain (+10 points, 84%). A true
gain of +5 points will more often than not go undetected; the write-up will
say so rather than read a null as "no effect".

## 6. Budget and stopping rules

Training ceiling **$15** (smoke test included), wallet $30, auto top-up off.
Prices (Prime docs, Models & Pricing): $0.20 input, $0.60 output, $0.60
training per 1M tokens. Estimate from screening tokens: about $0.15 per step
with the filter, about $15 for 100 steps; evaluation about $0.15.

1. **Smoke test** (`cad-spec-9b-smoke.toml`, 5 steps, about $0.75). It must
   show: the three environments load at 0.4.2; temperature 0.7 in the run
   configuration; both rewards 0 and 1 present at every step; no scoring
   errors; the cost per step from the run's usage record (training plus
   inference, divided by the steps).
2. **Length of the run**, set from the smoke test before launch and recorded
   under Amendments: `max_steps = floor((15.00 - smoke cost - 0.50) / cost
   per step)`, at most 150. Below 30 steps the budget is insufficient: stop
   and amend instead of running.
3. **No stopping on results.** The run is stopped early only for a technical
   failure or if recorded spend reaches $15. Training curves are watched for
   failures, not to pick a moment.
4. **Evaluation once.** If an evaluation run fails technically (API errors,
   refused by the analysis for a technical reason), it is rerun and the
   reason is recorded; answers are never selected or re-drawn.

## 7. Known risks

- verifiers v0 is deprecated and being retired (no date given). cad-spec runs
  through the legacy bridge; the smoke test confirms it still does.
- The Hosted Training service may apply rollout filters of its own besides
  the registered one; the smoke test's run record shows the effective ones.
- The adapter is served as `base:adapter` on the same endpoint as the base
  model; if its per-token price differs, the runner records the tokens either
  way.

## Amendments

### Amendment 1 (29 September 2026): environment 0.4.2 → 0.4.3, packaging only

Made after the first smoke test failed and before any rollout, adapter or
test-split answer existed.

- **What happened.** Smoke run `b32pcagfy8t4bqf2lnc6dep7` (5 steps) failed
  at environment startup, on all three environment servers, before the first
  rollout. Installing `cad-spec==0.4.2` on the training image replaced the
  platform's own verifiers (our range `verifiers>=0.3.0,<0.4`), which pulled
  `prime-sandboxes` 0.4.0; that release refuses to start next to the image's
  `connect-python` 0.9.0 (`RuntimeError`, then "env server did not become
  healthy in 120s", `BackoffLimitExceeded`). The same floor (0.3.0 >= 0.2.0)
  made `prime env push` publish this v0 package as v1.
- **Change.** cad-spec 0.4.3 declares `verifiers` without a version, as
  Prime's own legacy example environments do, and `datasets>=2`. Code,
  scorer (0.4.0), prompts, cheat-sheet, splits and rewards are identical to
  0.4.2. The configs now pin `bazzouzi/cad-spec@0.4.3`; nothing else in them
  changes. The 0.4.3 wheel SHA-256 and its verify_hub result are recorded in
  the CHANGELOG when pushed.
- **Observed platform filters** (from the failed run's log, answering the
  risk in section 7): the registered zero-advantage filter is enforced; the
  service adds post-batch filters of its own: gibberish and repetition in
  monitoring mode only (`enforce = false`), and zero-advantage again
  (enforced). Neither changes the design.
- The budget rule is unchanged: the failed smoke run's cost, whatever the
  usage record shows, counts toward the $15 ceiling. Recorded: $0.00 (no
  tokens). 0.4.3 was pushed as legacy v0, wheel SHA-256
  `b65ae73ec948ffb0e92ba590f44977d86f115b61c67607fdbe4356b1e205107c`, served
  wheel identical, verify_hub 200/200 IDENTICAL.

### Amendment 2 (30 September 2026): environment 0.4.3 → 0.4.4, rollout input

Made after the second smoke test was stopped and before any trained step,
adapter or test-split answer existed.

- **What happened.** Smoke run `jvryf7tsn20jw66cfxesbp08` got past startup
  (Amendment 1's fix held) but every rollout failed before scoring:
  `ValueError: Serialized task payloads must be JSON objects. Plain string
  task routes are no longer supported`. The dataset rows carried a
  top-level `"task": "cad-spec-<tier>"` string, an old v0 convention;
  verifiers' legacy path now decodes a string `task` as a JSON payload.
  Reproduced locally with verifiers 0.3.1 through `env.init_state`. No
  metrics were recorded; the run was stopped.
- **Change.** cad-spec 0.4.4 drops the `task` field (the tier stays in
  `info`). Prompts, answers, splits, scorer (0.4.0) and rewards are
  identical. New tests (`tests/test_rollout_path.py`) run the rollout path
  through verifiers itself (`init_state`, then the rubric): the reference
  scores 1.0 in both reward modes and the L4 failure scores 0 binary, 7/9
  continuous. All seven fail on 0.4.3. Configs pin `@0.4.4`.
- Cost of the stopped run: $0.00 (no tokens; rollouts failed before the
  model was called). 0.4.4 was pushed as legacy v0, wheel SHA-256
  `49737212123f9e341ae69bba81a1f8aeec7d4cdffe0bc07f49fc7aa92520144f`,
  served wheel identical, verify_hub 200/200 IDENTICAL.

### Amendment 3 (30 September 2026): environment 0.4.4 → 0.4.5, CadQuery on the training image

Made after the third smoke test was stopped and before any trained step,
adapter or test-split answer existed.

- **What happened.** Smoke run `jkqd5k12g1g5kvqyhmfg012k` started cleanly
  (environments ready with 200, 200 and 400 train tasks) but no training step
  completed in about 9 minutes: `Train batch 0/128` throughout, groups
  finalized and all dropped by the zero-advantage filter, L4 rollouts
  accumulating to 128 in flight. An audit of the environment-server logs
  (indexed selectors `cad-spec-l4/0`, `cad-spec-l2/1`, `cad-spec-l1-l3/2`)
  found in all three: `CadQuery is not importable ... libGL.so.1: cannot open
  shared object file`. cad-spec raised `ScorerUnavailableError` as designed;
  the hosted verifiers catches reward-function exceptions and substitutes
  0.0. No group survived the zero-advantage filter; the run exposed no
  per-group reward vectors (step-0 samples and distributions were empty),
  so "all groups flat" is the explanation consistent with the logs, not an
  enumerated observation. Usage: 0 training tokens, 85.68K input and 32.03K
  output inference tokens, $0.03, counted toward the $15 ceiling.
- **Root cause, checked.** OpenCascade's OCP binding links `libGL.so.1` and
  `libX11.so.6` at load time (`TKOpenGl`, `TKService`), including the
  headless "novtk" build of the same version, so no Python-level variant
  avoids them. No option to supply a custom environment image was found in
  Prime CLI 0.8.0 (its `image_tag` selects the prime-rl build for full
  fine-tuning runs on a registered cluster) or in the Hosted Training docs.
- **Change.** cad-spec 0.4.5 vendors the Ubuntu 20.04 builds of these
  libraries and their dependencies (8 files, 2.9 MB, glibc 2.26 at most;
  sources, hashes and licences in `cad_spec/_vendor/linux_x86_64/`) and loads
  them before CadQuery **only when the system has none**, as a complete set
  loaded by path (never mixed with system copies). Where the system has them
  (CI, local machines), nothing changes. Provenance verified from Ubuntu's
  signed `Release` files down to each file (`SOURCES.md`). And `load_environment` now
  refuses to load when the scorer cannot run, so this failure mode ends a run
  at startup instead of scoring 0. Checks, gates, rewards, prompts and splits
  are identical; scorer 0.4.0.
- **Evidence before any spend** (`scripts/gl_fallback_check.py`, saved in
  `results/training/gl-fallback/`). With the system GL and X11 libraries
  hidden (the training image's condition), without the fallback: the exact
  error of the logs. With the installed 0.4.5 wheel, fork sandbox, glibc
  2.39, one CPU: libraries loaded from the vendored copies; reference 1.0,
  the known L4 failure 0 binary and 7/9 continuous, a complete `env.rollout`
  1.0; 1, 8, 32 and 64 saved screening answers at once all scored identically
  to the screening file (64 in 3.6 s). The same gate passes with the system
  libraries. The fail-fast import costs 1.4 s and about 445 MB per process
  when warm, the same with either source; the first import after installing
  took 68 s on this machine's cold disk, paid by `load_environment` before
  the server reports ready. CI now runs this gate on every push, with the
  system libraries and with them hidden. Configs pin `@0.4.5`.
- Registered settings (temperature, tokens, mix, filter, binary reward) are
  unchanged. 0.4.5 was pushed as legacy v0, wheel SHA-256
  `9ceb772c19a985718cea3a6247ebae85dc3d4792601fda7b005229c5aced3569`
  (1,185,342 bytes), served wheel identical, verify_hub 200/200 IDENTICAL.

### Amendment 4 (30 September 2026): smoke test passed; run length set

Made after the smoke test and before launching the training run; no adapter
or test-split answer exists.

- Smoke run `k3rwpbbk5sio4936onuai7ok` (0.4.5) completed 5 steps in about
  6 minutes. All five acceptance checks of section 6.1 pass; the evidence,
  command by command, is in
  [results/training/run1/smoke-acceptance.md](../../results/training/run1/smoke-acceptance.md).
  Check 2 (temperature 0.7) is verified as sent in the run payload by the
  Prime CLI source and displayed before launch; the service does not echo it
  back in the run record, logs or rollouts. The training run uses the same
  config through the same code path.
- Cost per step: $0.66 / 5 = $0.132. Smoke tests so far: $0.69 ($0.00,
  $0.00, $0.03, $0.66).
- **Run length, by the registered rule:** `max_steps = floor((15.00 - 0.69 -
  0.50) / 0.132) = 104`. `configs/rl/cad-spec-9b.toml` now says 104;
  nothing else in it changes. Expected cost $13.73, total $14.42.
- Spend is watched during the run with `prime train usage`; per section 6.3,
  the run is stopped only for a technical failure or if recorded spend
  (smoke tests included) reaches $15.
