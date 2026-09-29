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
| Environment | `bazzouzi/cad-spec@0.4.2`, wheel SHA-256 `482d399c5cc374f7a564eacfded927cc09aacd879fa9756fb34881efe455c6cb`, verify_hub 200/200 IDENTICAL |
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

None yet.
