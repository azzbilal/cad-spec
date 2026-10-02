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
  Check 2 (temperature 0.7) is established as **sent**, not as applied: the
  Prime CLI source and the archived create request (recorded without sending,
  `results/training/run1/payload-*.json`) carry `temperature: 0.7` and
  `enable_thinking: false`; the service echoes neither in the run record,
  logs or rollouts. Snapshots of every figure, with hashes, are in
  `results/training/run1/snapshots/`.
- Cost per step, from recorded charges: $0.6604 / 5 = $0.13208 (training
  $0.3539, inference $0.3065; the table view's rounded per-bucket amounts do
  not add up and are not used). Smoke tests so far: $0.6854 ($0.0000,
  $0.0000, $0.0250, $0.6604).
- **Run length, by the registered rule:** `max_steps = floor((15.00 - 0.6854
  - 0.50) / 0.13208) = 104`. `configs/rl/cad-spec-9b.toml` now says 104;
  nothing else in it changes. Projected $13.74, total $14.42.
- **Sensitivity:** $0.58 of headroom is 4.2% of the projected cost; a 4.2%
  rise in cost per step uses it. The run's own recorded spend must stay
  under $14.31; per section 6.3 the run is stopped only for a technical
  failure or if recorded spend (smoke tests included) reaches $15.

### Amendment 5 (30 September 2026): run stopped at step 38 on cost; its end-of-run adapter is the one evaluated

Made after the training run stopped and before any evaluation; no test-split
answer exists.

- **What happened.** Training run `mk9qcuq2dsckzrf68gycyqls` (config and
  archived request as registered) ran from 15:44 to 17:02 (Prime CLI times)
  and completed **38 of 104 steps** (per-step distributions exist for steps
  1 to 38 only). Its cost per step rose from about $0.13 in the smoke test to
  about $0.36 over steps 17 to 28 and about $0.68 over steps 33 to 38, while
  steps slowed down. Recorded charges: training $3.7668, inference $10.1053,
  total **$13.8721**. Inference output reached 15.15M tokens, about 400K per
  step against about 80K in the smoke test: only a small share of generated
  answers entered each trained batch, the rest being dropped by the
  zero-advantage filter. At that rate the remaining 66 steps would have cost
  roughly $45, beyond the ceiling and the wallet.
- **Stop.** The run was stopped at 17:02 under section 6.3 (technical
  failure: the run could no longer fill its batches at a cost the
  registration or the wallet could bear). A ceiling increase to $20 had been
  drafted during the run, on the projection then available, and was never
  adopted: the stop came first, and total spend stayed within the original
  ceiling: **$14.5575** ($13.8721 + $0.6854 smoke tests) of $15.
- **Adapter.** The service produced adapter `xfisiyo5vlhn0ys65sf4uad7`
  (`cad-spec-9b-run1`, created 17:02:45, READY, deployable): the model's
  state at the stop, after the last completed step, 38. It is the run's
  end-of-run adapter in the sense of section 3, and the only one evaluated;
  the checkpoints saved every 5 steps (15 to 35) are not used.
- **Evaluation unchanged.** Section 4 applies as registered to this adapter:
  same test split, base model, conditions, analysis and thresholds. The
  result is reported as that of a 38-step run (37% of the registered 104
  steps), with the cost behaviour above.
- **Context.** Prime announced that shared Hosted Training for LoRA runs
  stops accepting new runs on 5 October 2026 (existing LoRA adapters stay
  deployable), so no rerun of this setup is planned.
- Evidence: `results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/`
  (run record, usage, per-step metrics and distributions, logs, with a
  hashed manifest).

## Result (2 October 2026)

Recorded after the single registered evaluation. Nothing above this section
was changed after the evaluation files existed.

### Execution

- **Base model**, `Qwen/Qwen3.5-9B` on Prime Inference (listed $0.18 /
  $0.54 per 1M tokens): 240 answers (60 test specs x L1 to L4), status
  complete, no API error, 1 truncated (0.4%, L1). Computed cost $0.0734.
- **Adapter** `xfisiyo5vlhn0ys65sf4uad7` (end-of-run adapter, step 38),
  deployed at 16:11 (Prime CLI time) and served as
  `Qwen/Qwen3.5-9B:xfisiyo5vlhn0ys65sf4uad7` (listed $0.10 / $0.20 per 1M
  tokens). A one-answer probe outside the test split confirmed the name,
  then 240 answers, complete, no API error, none truncated. Computed cost
  $0.0464. Unloaded right after (`prime deployments delete`; status
  NOT_DEPLOYED). The planned 10-minute idle balance check was **not
  recorded**, so the absence of a time-based deployment fee is unverified.
- Both runs: locked test split with the registered fingerprint, greedy,
  2,048 tokens, thinking off, the packaged cheat-sheet (identical system
  prompt), scorer 0.4.0, cad-spec 0.4.5. Costs above are computed by the
  runner from the listed prices; the rounded `usage.cost` fields sum to
  $0.0764 and $0.0473.
- Files: `results/training/run1/eval/base-test.jsonl` (SHA-256
  `6aee6424...639ffb3`), `results/training/run1/eval/adapter-test.jsonl`
  (`d937884c...3117e4`); verdict `results/training/run1/verdict.md`
  (`5bfcc2e9...b627b5`) and `verdict.json` (`30a037bf...8925ed`), written
  once by the frozen `scripts/compare_training.py`.

### Verdict (registered analysis, run once)

| Tier | Base all-pass | Adapter all-pass | Difference | 95% interval |
|---|---|---|---|---|
| L1 | 86.7% | 100.0% | +13.3 | [+5.0, +21.7] |
| L2 | 83.3% | 100.0% | +16.7 | [+8.3, +26.7] |
| L3 | 75.0% | 98.3% | +23.3 | [+13.3, +35.0] |
| L4 | 36.7% | 100.0% | +63.3 | [+51.7, +75.0] |

- **H1 (L2 + L4, primary): CONFIRMED.** 60.0% to 100.0%, **+40.0 points,
  95% interval [+32.5, +47.5]**, 120 pairs over 60 specs. Worthwhile
  (registered minimum +10 points).
- H2 (L4 alone, secondary): gain, +63.3 points [+51.7, +75.0].
- Regression checks: none on L1 (+13.3) or L3 (+23.3).
- Overall: base 169/240, adapter 239/240. 70 pairs improved, none worsened;
  the one adapter failure (L3, test-0054) also fails in the base model.

### Integrity audit

An independent read-only audit (`audit/run1-result-integrity.md`) tried to
break the result before publication. It survives, with caveats:

- the verdict reproduces byte for byte; all 480 answers re-score
  identically with the repository scorer and with the published 0.4.5
  wheel, in both orders;
- **no reward hacking found**: only CadQuery imports, no file access,
  introspection or monkeypatching; 240 distinct programs, each using its own
  spec's numbers; all 239 passing parts match the requested geometry
  exactly under a check independent of `cad_spec.measure` (same OpenCascade
  kernel); 72 of 72 out-of-tolerance perturbations of passing answers fail
  the expected check;
- **no leakage**: no test spec in the train or development splits by id or
  dimensions, disjoint L3 wordings, and the training dataset rebuilt
  locally contains no test id;
- what changed: on L4 the base model resized the plate but kept the old
  pitch in all 38 of its failures (R5 and R7); the adapter recomputes the
  pitch. Its answers are longer (L4 mean output 133 to 682 tokens).

### Limits

One training run and seed, stopped on cost after 38 of 104 registered steps;
one model; one plate generator; the same cheat-sheet in both arms; 60 test
specs (120 correlated primary pairs); two held-out L3 wordings. The adapter
is at the ceiling on the primary slice: 60/60 specs bounds the success rate
below at about 94% (exact two-sided 95%, independent specs assumed), not at
100%, and the bootstrap cannot see unobserved failures. Base and adapter
were served by different Prime routes; their numerical equivalence (weights,
precision, templates, applied decoding) is not attested. Scoring ran in the
Windows `reuse` sandbox; a Linux `fork` replay is pending. Results say
nothing yet about other part families.

### Claim

> In one Qwen3.5-9B LoRA RL run stopped on cost after 38 of 104 planned steps, saved greedy Prime Inference outputs with the same CadQuery cheat-sheet improved the all-requirements pass rate on the locked 60-spec mounting-plate test split from 60% to 100% across L2 and L4, a paired gain of 40 points (registered spec-cluster bootstrap 95% interval: 32.5 to 47.5). Offline rescoring and independent BREP geometry checks reproduced the result; generalization beyond this generator and equivalence of the base and adapter serving backends remain unverified.

### Addendum (2 October 2026): Linux replay and file hashes

- **Linux replay done.** All 480 saved answers were re-scored on Linux in
  the `fork` sandbox (the isolation used on training machines) by
  `scripts/replay_eval.py`: **0 mismatches** in reward or any check; base
  169/240, adapter 239/240, as recorded on Windows. The "Windows `reuse`
  sandbox" limit above is closed. Result:
  `results/training/run1/linux-replay.json`; CI replays both files on every
  push.
- **Hashes and line endings.** The SHA-256 values quoted above were computed
  on the Windows working copies, which Git checks out with CRLF line
  endings. The repository stores the same files with LF. Both forms:

  | File | SHA-256, LF (repository) | SHA-256, CRLF (Windows copy, quoted above) |
  |---|---|---|
  | `eval/base-test.jsonl` | `f68479465920688379c90f4a8d15c682d47ddbf60bcd6e56e5c6180a843b761f` | `6aee64245417a56614f9d0654bf944469de193ea5e09bdbdad71c6195639ffb3` |
  | `eval/adapter-test.jsonl` | `2493f78ebc33610752658519370cccfafea993c1f96b6b410c19c47d8dcc6216` | `d937884ce262766a375042cb327a5f360978338a5db5daaf47579da34f3117e4` |

  The snapshot manifests have the same property (all 54 entries hash the
  CRLF form). `scripts/verify_manifest.py` checks them on any OS and reports
  which form matched; CI runs it. From now on `capture_run.py` and
  `archive_run_payload.py` write LF on every OS.

### Addendum (2 October 2026): serving-route bridge check, rule registered before the data is read

This is an unplanned, free, post hoc check on the limit "base and adapter
were served by different Prime routes". It was not part of the registered
analysis and changes neither the verdict nor the claim. The rule below was
written and committed before any step-1 reward value of the archived
training metrics was opened; only key names, sample counts and the archived
create requests had been read.

**Question.** Could a difference between the serving stacks, rather than
training, explain the jump on L4? If the nearly untrained model scores
inside the training stack what the base model scores on the base route, it
cannot.

**Quantities.**

- Observed: `train/<env>/all/metrics/all_pass_reward/mean` at step 1 of
  `metrics.json`, for the training run `mk9qcuq2dsckzrf68gycyqls` (primary)
  and the 0.4.5 smoke run `k3rwpbbk5sio4936onuai7ok` (second sample; its
  create request has the same sampling settings). The `all` set is used, not
  `effective`, so the zero-advantage filter cannot bias the rate.
- Reference: `results/training/screening/qwen3.5-9b-t0.7-x8-2k.jsonl`, the
  base route at matched settings (temperature 0.7, 8 samples per spec,
  2,048 tokens, thinking off, cheat-sheet on), 30 dev specs per tier. This
  replaces the greedy screening level as the comparison point because
  training samples at temperature 0.7.
- Interval: whole spec groups of 8 answers are resampled with replacement
  from the reference, as many groups as step 1 has prompts of that
  environment (batch share times prompts), 10,000 draws, seed 20261002. The
  2.5th and 97.5th percentiles form a 95% predictive interval for "same
  model, same settings".

**Verdict, on L4 of the training run (primary).**

- **BRIDGED**: the step-1 rate is inside the interval. A route difference is
  not supported as an explanation of the L4 gain.
- **OPEN_INFLATING**: above the interval. The gap to the reference is
  reported as a share of the registered +63.3 point L4 gain.
- **STACKS_DIFFER_NOT_INFLATING**: below the interval. The gain is not a
  route artifact, and the difference is recorded as unexplained.

L4 of the smoke run, L2, L1+L3 and the pooled L4 value of both runs are
reported as corroboration and do not change the verdict; any disagreement is
stated.

**Precondition.** The step-1 batch must have been generated before any
weight update (a LoRA adapter starts as a zero change to the base model).
This is checked in `logs.txt` of each snapshot and reported with the result.

**Limits known in advance.** Step 1 holds about 11 L4 prompts per run, so the
interval is wide: the check can rule out a stack effect large enough to
explain a 63 point jump, not a small one. Training prompts come from the
train split and the reference from the dev split (same generator, different
specs). The reference was produced with package 0.4.1 and the runs with
0.4.5 (scorer 0.4.0 in both). The check says nothing about the adapter route
itself.

**Analysis.** `scripts/bridge_check.py` (self-test
`scripts/test_bridge_check.py`, synthetic data only), frozen in this commit.
It refuses to run if the sampling settings of the three sources differ.

#### Outcome (2 October 2026, run once after the rule above was committed)

**Verdict by the registered rule: BRIDGED.** Result files:
`results/training/run1/bridge-check.md` and `bridge-check.json`.

| Run | Environment | Prompts | Passing answers | Training stack, step 1 | Base route | 95% interval | Position |
|---|---|---|---|---|---|---|---|
| training run (primary) | L4 | 11 | 25 of 88 | 28.4% | 42.9% | [18.2%, 69.3%] | inside |
| smoke run | L4 | 12 | 31 of 96 | 32.3% | 42.9% | [18.8%, 67.7%] | inside |
| both pooled | L4 | 23 | 56 of 184 | 30.4% | 42.9% | [25.5%, 61.4%] | inside |
| training run | L2 | 11 | 52 of 88 | 59.1% | 68.8% | [60.2%, 76.1%] | below |
| smoke run | L2 | 11 | 52 of 88 | 59.1% | 68.8% | [60.2%, 76.1%] | below |
| training run | L1+L3 | 2 | 12 of 16 | 75.0% | 63.1% | [43.8%, 81.2%] | inside |
| smoke run | L1+L3 | 2 | 10 of 16 | 62.5% | 63.1% | [43.8%, 81.2%] | inside |

- **What it supports.** With untrained weights the training stack does not
  score above the base route on L4: 28.4% against 42.9%, inside the
  interval, and far from the adapter's 100%. A stack that simply serves the
  same weights better is not supported as an explanation of the L4 gain.
- **What it does not close.** On L4 and L2 every point estimate is below the
  base route (L4 by 14.5 and 10.6 points, L2 by 9.7 points), and L2 falls
  below its interval by one answer in both runs (53 of 88 would be inside).
  By the rule this is a secondary result that does not change the verdict;
  it is recorded as unexplained. The direction is the non-inflating one.
  Untested candidates: the prompt draw (11 train prompts against 30 dev
  specs); decoding defaults (the screening run forced `top_p` 1.0, `top_k`
  -1 and `min_p` 0.0, while the training request carries only the
  temperature and the service does not echo what it applied); package 0.4.1
  against 0.4.5; a real numerical difference between the stacks.
- **The second sample is not independent.** Both runs have the same number
  of L2 and L1+L3 prompts and the same L2 count (52 of 88), and almost the
  same L4 group structure. They very likely drew the same first prompts, so
  the smoke run corroborates sampling noise, not the prompt draw.
- **Precondition.** Smoke run: confirmed in `logs.txt` ("Training from
  scratch", step 1 reported with "Max Off-Policy 0"). Training run: the
  archived `logs.txt` only holds steps 33 to 38, so it is **not directly
  confirmed**; it holds by construction (the first weight update consumes
  the step-1 batch) and `time/wait_for_policy` is 0 at step 1.
- **Context, not part of the rule.** Inside the training stack the same
  metric rose from 28.4% at step 1 to 97.1% at step 38 on L4 (all generated
  answers, temperature 0.7), and from 59.1% to 100% on L2. The gain is
  visible within one stack, without any comparison across routes.
- **Status of the limit.** Narrowed, not closed. The adapter route itself is
  still not attested, and the claim above stays as written.
