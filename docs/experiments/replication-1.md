# Replication 1: does the run 1 result hold on fresh specs? (pre-registration)

Registered 2 October 2026, before any model answer on the replication split
exists. The merge commit of this file is the registration. Everything below
the heading "Result" is added afterwards; nothing above it is edited after
the evaluation files exist, except through dated amendments.

This document does not replace [training-run-1.md](training-run-1.md). The
original verdict and claim stay as written, whatever happens here.

## 1. Question

Training run 1 improved the all-requirements pass rate on L2 and L4 of the
locked 60-spec test split from 60% to 100% (+40 points, 95% interval +32.5
to +47.5). That is one evaluation on one split, with the adapter at the
ceiling. The question here is narrow: **with the same frozen adapter, the
same base model and the same protocol, does the gain appear again on 60
specs that nothing has ever been evaluated on?**

What it tests: that the result is not specific to the 60 test specs.

What it does not test: another training run or seed, another model, another
part family, harder change orders, or the equivalence of the two serving
routes. Base and adapter are served exactly as before, so a route effect, if
one exists, would be reproduced, not detected. The bridge check in
training-run-1.md (2 October 2026) is the evidence on that point.

## 2. What is frozen

| Item | Value |
|---|---|
| Adapter | `xfisiyo5vlhn0ys65sf4uad7` (run `mk9qcuq2dsckzrf68gycyqls`, end-of-run, step 38), served as `Qwen/Qwen3.5-9B:xfisiyo5vlhn0ys65sf4uad7`. No other checkpoint is evaluated. |
| Base model | `Qwen/Qwen3.5-9B` on Prime Inference |
| Endpoint | `https://api.pinference.ai/api/v1` for both |
| Package and scorer | cad-spec 0.4.5, scorer 0.4.0 (unchanged) |
| Prompt | system prompt plus the packaged cheat-sheet, fingerprint `a9050c1d...1e5128c`, identical in the four runs (two original, two here) |
| Decoding | greedy (temperature 0), 2,048 output tokens, thinking off, same request body as the registered evaluation |
| Tiers | L1, L2, L3, L4, each spec once per tier: 240 answers per model |

## 3. The replication split

`scripts/replication_split.py`, `make_replication_split()`:

- 60 specs from the same generator (`sample_spec`) as every other split,
  seed **20261003**, ids `rep-0001` to `rep-0060`.
- Disjoint by parameters (length, width, thickness, hole diameter, edge
  margin) from the 200 train specs, the 30 dev specs and the 60 specs of the
  locked test split, and from each other.
- Fingerprint **`REPLICATION_SPLIT_SHA256 =
  01ac4bde217e879653c1227760e4abde3d06c0034d16b2a200b0394d7bc14bdd`**,
  checked by the runner, by the analysis and by a self-test in CI.
- The seed was fixed before the split was generated, and the split was
  generated once. No seed was tried and discarded.
- L3 uses the two held-out wordings, as the test split does (30 specs each).
  L4 change orders are derived from the new ids; 46 of 60 change the length,
  the width or the edge margin and therefore move the hole pitch (45 of 60 in
  the test split).
- The split lives in `scripts/`, not in the package, so the published 0.4.5
  wheel stays identical to the one the adapter was trained with.
- Locked like the test split: the runner refuses it without
  `--unlock-replication`. It is evaluated once, for this replication, and
  then counts as used.

Free checks made at registration with no model (computed answers only):

| Provider | Tiers | Result |
|---|---|---|
| `reference` (the reference solution of each spec) | L1 to L4 | 240 of 240 all-pass |
| `rev-a` (the unedited rev A model) | L4 | 0 of 60 all-pass |

So every task is solvable and no L4 task passes without the edit.

## 4. Protocol

Identical to the registered evaluation of run 1 except for the split. Both
runs are made on the same day, once each.

```bash
# Base model
python scripts/run_baseline.py --provider openai \
  --base-url https://api.pinference.ai/api/v1 --key-env PRIME_API_KEY \
  --model Qwen/Qwen3.5-9B --arm hint --hints \
  --split replication --unlock-replication --tiers L1 L2 L3 L4 \
  --temperature 0 --max-tokens 2048 \
  --extra-body '{"chat_template_kwargs": {"enable_thinking": false}}' \
  --price-in 0.18 --price-out 0.54 --budget 0.35 \
  --out results/training/replication1/eval/base-rep.jsonl

# Adapter (after deployment, see section 7)
python scripts/run_baseline.py --provider openai \
  --base-url https://api.pinference.ai/api/v1 --key-env PRIME_API_KEY \
  --model Qwen/Qwen3.5-9B:xfisiyo5vlhn0ys65sf4uad7 --arm hint --hints \
  --split replication --unlock-replication --tiers L1 L2 L3 L4 \
  --temperature 0 --max-tokens 2048 \
  --extra-body '{"chat_template_kwargs": {"enable_thinking": false}}' \
  --price-in 0.10 --price-out 0.20 --budget 0.15 \
  --out results/training/replication1/eval/adapter-rep.jsonl
```

Before the adapter run, one answer on the dev split (`--split eval --limit 1
--tiers L1`) confirms that the adapter name resolves, as in run 1. It is not
analysed.

## 5. Hypotheses and analysis

The analysis is [scripts/compare_replication.py](../../scripts/compare_replication.py),
written and tested before any data (self-test
`scripts/test_compare_replication.py` in CI). The paired test, its bootstrap,
its seed and every conformity rule are imported unchanged from the frozen
`scripts/compare_training.py`.

- **R1 (primary, the claim).** All-pass on L2 and L4 together, adapter minus
  base, paired by tier and spec (120 pairs, specs resampled with both tiers
  together, 10,000 resamples, seed 20261001).
  - **REPLICATED** if the lower bound of the 95% interval is above 0 **and**
    the point estimate is at least +10 points (the gain run 1 called
    worthwhile).
  - **SMALLER THAN WORTHWHILE** if the lower bound is above 0 but the point
    estimate is below +10.
  - **NOT REPLICATED** otherwise.
- **R2 (secondary).** The same on L4 alone. Reported, not claimed.
- **R3 (size).** The L2 + L4 gain here minus the gain on the original test
  split, with a 95% interval from resampling the specs of each split
  independently (10,000 resamples, seed 20261004). **CONSISTENT** if the
  interval contains 0, **SMALLER** if it lies below 0, **LARGER** if above.
  A SMALLER verdict is reported next to R1 even when R1 is REPLICATED.
- **R4 (ceiling).** Specs where the adapter passes both L2 and L4, pooled
  over the original test split and this one (120 specs), with the exact
  (Clopper-Pearson) two-sided 95% lower bound. No threshold. With 120 of 120
  the bound would be about 97.0%; the original 60 of 60 gave about 94.0%.
- **Regression check.** L1 and L3: a point-estimate drop of more than 10
  points is reported as a regression next to the verdict.
- **Failures.** Every adapter failure is listed with its failed checks and
  whether the base model fails the same task.
- **Refusal.** A run that departs from sections 2 to 4 (split, fingerprint,
  spec ids, model names, endpoint, package, temperature, tokens, prompt,
  thinking, scorer, completeness, API errors, 5% or more truncated) is not
  analysed. The script says why.

How the outcome will be worded:

| R1 | R3 | Wording |
|---|---|---|
| REPLICATED | CONSISTENT or LARGER | The gain replicated on a second, disjoint 60-spec split. |
| REPLICATED | SMALLER | A worthwhile gain replicated, smaller than on the original split. Both numbers are given. |
| SMALLER THAN WORTHWHILE | any | The original estimate overstated the gain. Both numbers are given and the README claim is qualified. |
| NOT REPLICATED | any | The result did not replicate. The README says so next to the original claim. |

## 6. Power

Simulated with the base rates of the original test split (L2 83.3%, L4
36.7%), 60 specs, the registered rule, and a pessimistic 5% of base passes
lost by the adapter (4,000 trials, 2,000 resamples each):

| True gain on L2 + L4 | 0 | +5 | +10 | +15 | +20 | +30 |
|---|---|---|---|---|---|---|
| Probability of REPLICATED | 0% | 6% | 56% | 92% | 100% | 100% |

The rule is strict at the threshold: a true gain of exactly +10 points is
called REPLICATED only about half the time, because the point estimate must
itself reach +10. A true gain of +15 or more is detected almost always. A
model with no gain is essentially never called REPLICATED.

## 7. Budget, wallet and stopping rules

Ceiling for this replication: **$1.00**, wallet auto top-up off.

- **Inference bound, per-token billing at the listed prices: $0.51.** The
  runner stops before a call that would cross its budget ($0.35 base, $0.15
  adapter); one call can overshoot by at most its own cost (about $0.0012
  base, $0.0005 adapter at 700 input and 2,048 output tokens), and the probe
  costs less than $0.001. Expected spend is about $0.12, as in run 1
  ($0.0734 + $0.0464).
- The bound assumes the billed prices do not exceed the prices given to the
  runner. `prime inference models` is checked before the run (free); if a
  listed price differs from section 4, the run waits for a dated amendment.
- **Deployment fee: unknown, measured this time.** The Prime documentation
  describes adapter serving as pay-per-token and lists no time-based fee
  (page "Deploying LoRA Adapters for Inference", read 2 October 2026). Run 1
  did not record the check. Until it is measured, the only hard bound on a
  time-based fee is the wallet balance with auto top-up off, so the balance
  is recorded before anything is deployed.

Order of execution, with the wallet balance read at each mark:

1. **B0**: balance before anything. Check the billing history of 2 October
   2026 for any charge tied to the run 1 deployment (free evidence).
2. Base run. **B1** after it.
3. `prime deployments create xfisiyo5vlhn0ys65sf4uad7`; wait for `DEPLOYED`.
   **B2**, with the time.
4. Ten minutes with no request. **B3**. The idle fee is B2 minus B3.
   **If it exceeds $0.05, unload at once and stop**; continuing needs a
   dated amendment with a new bound.
5. Probe, then the adapter run. **B4**.
6. `prime deployments delete xfisiyo5vlhn0ys65sf4uad7`; status
   `NOT_DEPLOYED`. **B5** ten minutes later.
7. The adapter is unloaded no later than **60 minutes** after step 3,
   whatever has or has not run.

Other rules:

- **Evaluation once.** If a run fails technically (API errors, budget stop,
  refused by the analysis for a technical reason), it is rerun to a new file
  and the reason is recorded; answers are never selected or re-drawn. A
  rerun counts against the ceiling.
- **No peeking between the runs.** The analysis is run once, after both
  files are complete.
- If the balance display lags behind usage, the lag is reported and the
  recorded charges are used instead.

## 8. Known risks

- Prime's shared LoRA Hosted Training stops accepting new runs on 5 October
  2026. Existing adapters are announced as still deployable; if deployment
  fails, the replication cannot run and that is reported as such.
- Greedy decoding is not guaranteed to be bit-reproducible on a shared
  service. Each answer is generated once and kept.
- The replication split shares the generator, the tolerances and the two
  held-out wordings with the test split. It is a new sample of the same
  population, not a harder or different one.
- One adapter from one run: a replicated result is still a statement about
  this adapter, not about the training method.

## Amendments

### Amendment 1 (3 October 2026): the base run was interrupted by the operator; rerun to a new file

Written and merged before the rerun, before the adapter run and before any
analysis.

**What happened.** On 2 October 2026 the base run of section 4 was started
at about 23:32 UTC, right after the wallet reading B0 (23:31:42 UTC, balance
$14.7334), and stopped by the operator with Ctrl+C about one minute later.
The reason was scheduling: the full protocol needs about 45 minutes in one
sitting and it was postponed to the next day. The runner closed the file
with its end record:

`{"status": "interrupted", "written": 1, "planned": 240, "spent_usd": 0.00032}`

The adapter was not deployed (`prime deployments list` showed `NOT_DEPLOYED`
and `prime deployments delete` answered "Model is not deployed"). The
analysis was not run. Nothing was decided on the basis of any answer.

**What the plan said.** Section 7 allows a rerun to a new file after a
technical failure. An interruption by the operator is not in that list, so
it is recorded here instead of being treated as covered.

**What changes.**

- The interrupted file `results/training/replication1/eval/base-rep.jsonl`
  is kept unchanged and committed with the results. Its one answer is **not
  used** in the analysis.
- The base run is made again with the command of section 4 unchanged except
  for the output path, `results/training/replication1/eval/base-rep-run2.jsonl`.
  It regenerates all 240 answers, including the task already answered once.
  The analysis reads `base-rep-run2.jsonl`.
- Whether the two answers to that one task are identical is reported with
  the result, as a small free observation on greedy reproducibility.
- The base rerun and the adapter run are made in one sitting on the same
  day, with a new wallet reading before the rerun. The readings of 2 October
  stay in the log.

**What does not change.** The split, the models, the protocol, the
hypotheses, the thresholds, the analysis script, the $0.35 and $0.15 runner
budgets and the $1.00 ceiling. The $0.00032 already spent counts against the
ceiling.

**Exposure.** The runner's progress line displays the reward of each answer,
so the outcome of that single base answer may have been seen. It cannot
select anything: the rerun is the registered command and covers every task.

Any further interruption or rerun needs its own dated amendment.

## Result

Not run yet.
