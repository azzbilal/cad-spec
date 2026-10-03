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

## Result (3 October 2026)

Recorded after the single registered evaluation. Nothing above this section
was changed after the evaluation files existed, except Amendment 1, which
was merged (18:59 UTC) before the base rerun started (19:03 UTC).

### Verdict (registered analysis, run once)

| Tier | Base all-pass | Adapter all-pass | Difference | 95% interval |
|---|---|---|---|---|
| L1 | 70.0% | 100.0% | +30.0 | [+18.3, +41.7] |
| L2 | 83.3% | 100.0% | +16.7 | [+8.3, +26.7] |
| L3 | 78.3% | 96.7% | +18.3 | [+6.7, +30.0] |
| L4 | 36.7% | 98.3% | +61.7 | [+50.0, +73.3] |

- **R1 (L2 + L4, primary): REPLICATED.** 60.0% to 99.2%, **+39.2 points,
  95% interval [+31.7, +46.7]**, 120 pairs over 60 specs (registered: lower
  bound above 0 and at least +10 points).
- R2 (L4 alone, secondary): gain, +61.7 points [+50.0, +73.3].
- **R3 (size): CONSISTENT.** Original +40.0, replication +39.2, difference
  -0.8 points [-11.7, +10.0].
- R4 (ceiling): the adapter passes both L2 and L4 on 59 of 60 specs here
  (exact lower bound 91.1%), 60 of 60 on the original split, **119 of 120
  pooled, lower bound 95.4%**.
- Regression checks: none on L1 (+30.0) or L3 (+18.3).
- Overall: base 161/240, adapter 237/240. 78 pairs improved, **2 worsened**.

By the wording fixed in section 5: **the gain replicated on a second,
disjoint 60-spec split.**

Files: `results/training/replication1/verdict.md` and `verdict.json`,
written by `scripts/compare_replication.py`; the answers in
`results/training/replication1/eval/`.

### The three adapter failures

- **L3 `rep-0014` and `rep-0056`: cut at the 2,048-token limit, on tasks the
  base model passes.** These are the two worsened pairs, the first ones in
  either evaluation. In both the adapter reasons at length inside code
  comments, restarts its solution, and runs out of tokens before the final
  code block is closed, so nothing can be executed.
- **L4 `rep-0020`: a real reasoning miss** (hole pattern and edge margin
  fail; the base fails the task too). The change order alters the width and
  the edge margin together. The adapter applied the new margin on the axis
  whose size changed and kept the old margin on the other axis, with the
  comment "Since length didn't change, the X margin is still 16.5 mm".

### Execution

| Time (UTC) | Event | Wallet |
|---|---|---|
| 2 Oct 23:31 | Reading B0 | $14.7334 |
| 2 Oct 23:32 | Base run started, interrupted by the operator after 1 answer (Amendment 1) | $14.7326 |
| 3 Oct 18:59 | Amendment 1 merged | |
| 3 Oct 19:02 | Reading B0 of the day | $14.7326 |
| 3 Oct 19:03 | Base rerun started (`base-rep-run2.jsonl`): 240 answers, complete, no API error, 1 truncated (L1) | $14.6562 |
| 3 Oct 19:20 | First deployment attempt: `DEPLOY_FAILED`, "Adapter failed to load" | $14.6562 |
| 3 Oct 19:22 | Second attempt: `DEPLOYED` | $14.6562 |
| 3 Oct 19:34 | After 10 idle minutes | $14.6562 |
| 3 Oct 19:39 | Probe (1 dev answer, name resolves), then the adapter run: 240 answers, complete, no API error, 2 truncated (L3) | $14.6063 |
| 3 Oct 20:15 | Unloaded, `NOT_DEPLOYED`, about 53 minutes after deployment | $14.6063 |
| 3 Oct 20:25 | Ten minutes after the unload | $14.6063 |

- Both runs: replication split with the registered fingerprint, greedy,
  2,048 tokens, thinking off, the packaged cheat-sheet (system prompt
  `a9050c1d...1e5128c`, the same as in run 1), scorer 0.4.0, cad-spec
  0.4.5, endpoint `https://api.pinference.ai/api/v1`. The service reported
  the requested model name on every answer.
- File hashes (SHA-256, LF): `base-rep-run2.jsonl` `210f900f...78c8e5fe`,
  `adapter-rep.jsonl` `790aab62...75f3814c`, interrupted `base-rep.jsonl`
  `8e14eb8b...63d6db1d`. Wallet readings: `wallet-log.txt`.

### Cost

- **Billed: $0.1271** (wallet $14.7334 to $14.6063), against the $1.00
  ceiling: $0.0008 for the interrupted attempt, $0.0764 for the base rerun,
  $0.0499 for the probe and the adapter run. The runner computed $0.1233 at
  list prices; the billed amounts are about 3% higher, as in run 1.
- **Deployment fee: none.** The balance did not move during ten deployed
  idle minutes, nor after the unload, and the billing history contains only
  `inference` rows for both days. The failed deployment attempt cost
  nothing. The billing history of 2 October likewise shows no charge for the
  run 1 deployment other than tokens. This closes the check that run 1 did
  not record.

### Deviations from the plan

1. **Amendment 1**: the interrupted base run and its rerun.
2. **The first deployment attempt failed** and was retried once, as the
   Prime documentation describes. No answer was involved.
3. The listed prices were checked on 2 October, when the run was first
   started, and not again on 3 October. The amounts billed on 3 October
   match the registered prices.
4. The runner's progress line shows the reward of each answer as it comes,
   so base outcomes were visible before the adapter run. The analysis was
   run once, after both files were complete, and nothing was decided in
   between.

### Checks after the result (not registered)

- **The verdict reproduces.** `compare_replication.py` run again on Linux
  from the same files prints the same verdict.
- **Linux replay: 0 mismatches over 481 answers** (240 + 240 + the
  interrupted one), every check of every answer identical to what the
  Windows run recorded (`linux-replay.json`). CI replays them on every push.
- **Independent geometry check, 0 unexplained disagreements over 960
  answers** (`independent-geometry.json`, script
  `audit/replication1_geometry_check.py`). It does not import the scorer:
  bounding box, volume and point membership at the expected hole centres,
  with a position tolerance of 0.25 mm, stricter than the scorer's 0.5 mm.
  No answer the scorer fails passes it, on this split or on the original
  one.
- **Boundary passes.** The stricter check rejects 4 answers the scorer
  passes here (base: L1 `rep-0037`, L4 `rep-0005`, L4 `rep-0034`; adapter:
  L1 `rep-0038`) and 2 on the original split (base: L4 `test-0007`,
  `test-0043`). In five of them a hole centre is off by exactly 0.5 mm on
  one axis (in `test-0007`, by 0.25 mm): an arithmetic slip of one grid
  step, which the scorer's inclusive 0.5 mm position tolerance accepts. Counting them as failures
  gives +40.8 points [+33.3, +48.3] here and +41.7 [+34.2, +49.2] on the
  original split, so neither verdict depends on them. It is a property of
  scorer 0.4.0 to revisit: specs are on a 0.5 mm grid and the position
  tolerance equals one grid step.
- **Code hygiene.** Both files: only `cadquery` is imported, 240 distinct
  programs, no file access, introspection or dynamic execution.
- **Greedy decoding is not reproducible across days.** The one task
  answered twice by the base model (L1 `rep-0001`, 2 and 3 October, same
  prompt) passes both times with different text (1,058 and 1,198
  characters).

### What the answers look like

- **Change orders.** Of the 60 L4 tasks, 46 move the hole pitch. The base
  passes 8 of those 46 and all 14 others; the adapter passes 45 of 46 and
  all 14 others. Its one miss is in the hardest class, orders that change
  the edge margin together with the length or the width (10 of 11 here, 4
  of 4 on the original split).
- **Length.** The adapter's answers are much longer: median 777 output
  tokens against 92 on L4, 678 against 423 on L3, 751 against 484 on L1,
  529 against 337 on L2. It reasons in code comments (thinking is off), and
  on 2 of 240 tasks that reasoning exceeded the token limit.
- The base model scores the same on L2 (50 of 60) and L4 (22 of 60) as on
  the original split.

### Claim

Supported: the frozen run 1 adapter improves all-requirements pass on L2 and
L4 by about 40 points on two disjoint 60-spec splits (+40.0 and +39.2), and
the two estimates agree. Pooled, the adapter passes both tiers on 119 of 120
specs.

Not supported, as before: anything about another training run, model, part
family or harder change orders, and the equivalence of the two serving
routes (both evaluations used the same routes). New: the adapter is not at a
true 100%, it can lose a task to its own verbosity, and its one L4 miss is
on a two-change order.

### Corrections after the external audit (3 October 2026, before merge)

An external audit reviewed this Result section before it was merged
(`audit/state-and-roadmap-audit.md`). It reproduced every number of the
verdict with its own code and found no error in R1 to R4. It did find wrong
or overstated sentences. The text above is left as written; **where the two
differ, the corrections below are the valid statement.** Each one was checked
again by the project before being accepted.

1. **File hashes (wrong label).** The three digests under "Execution" are
   the digests of the files as written on Windows (CRLF), not LF. Correct
   values (also in `linux-replay.json`):

   | File | SHA-256, LF (as stored in the repository) | SHA-256, CRLF (as written by the run) |
   |---|---|---|
   | `base-rep-run2.jsonl` | `d240c458...6d2f1180` | `210f900f...78c8e5fe` |
   | `adapter-rep.jsonl` | `c132e4d8...481e7a9c` | `790aab62...75f3814c` |
   | `base-rep.jsonl` | `0866ddde...28ef8864` | `8e14eb8b...63d6db1d` |

2. **The geometry check is not "stricter than the scorer".** It is a second
   implementation that tests some things the scorer does not and misses
   others the scorer catches (a membrane in a bore, a second solid, a
   diameter 0.4 mm too large); its 0.25 mm rings are not an exact bound on
   hole-centre error. The check was rebuilt around a stronger test, the one
   the audit used: each answer is compared with the independently built
   ideal part. Result, identical in the audit's implementation and in
   `audit/replication1_geometry_check.py`: **of the 806 passing answers of
   the two evaluations, 800 are the nominal part within 0.001 mm3**; the
   six others are the offset passes already listed; no failing answer is
   nominal. Adapter: 239 of 239 nominal on the original split, 236 of 237
   here. Counting only nominal passes gives +40.8 [+33.3, +48.3] here and
   +41.7 [+34.2, +49.2] on the original split, as stated above.
3. **"The two estimates agree" means the registered rule only.** R3 is a
   non-rejection rule with an interval about 22 points wide, not an
   equivalence test. Sensitivity (not registered): the 90% interval of the
   difference is [-10.0, +8.3], so equivalence is not shown within 5 points,
   is borderline within 10, and holds within 12.
4. **Deployment fee: none observed**, at the four-decimal precision of the
   wallet, from deployment to ten minutes after the unload. That is an
   observation over this window, not a guarantee.
5. **Billing.** The sentence "about 3% higher, as in run 1" is replaced by
   its explanation: the service bills each response rounded to the nearest
   $0.0001, and that reproduces all 481 recorded charges ($0.0764, $0.0497
   and $0.0003, plus $0.0002 for the probe, whose file is not archived).
   The remaining $0.0005 of wallet movement on 2 October is unexplained and
   is not attributed to anything.
6. **Deviation 4 is a breach of the registered rule.** Section 7 says "No
   peeking between the runs"; the runner's progress line showed base
   outcomes before the adapter run. The runs should have used `--quiet`.
   That nothing was decided in between is the operator's statement, which
   the archive cannot prove.
7. **"The hardest class"** is a description made after seeing one failure,
   not a measured ranking. The neutral statement: the one L4 miss is an
   order that changes the edge margin together with a plate dimension (10 of
   11 such orders pass here, 4 of 4 on the original split).
8. **Medians.** The base medians are 92.5 output tokens on L4 and 337.5 on
   L2 (written as 92 and 337 above).
9. **Code hygiene** means: a static scan of the programs that parse found
   only `cadquery` imports and none of a list of dangerous names. The two
   truncated adapter answers do not parse. This does not prove the absence
   of every exploit; geometry can be gamed with plain CadQuery.

Scope added by the audit (new information, verified by the project unless
noted):

- **L4 is a small closed grammar.** The audit wrote a short deterministic
  parser for the change orders, froze it after train and dev, and it passes
  60 of 60 L4 tasks on each evaluation split (audit result, not yet
  reproduced in this repository). What the adapter learned is a reliable
  dependency-update routine inside this grammar. Every change-field
  combination of this split also occurs in training (14 of 14), so the
  splits are disjoint in their instances, not in their structure.
- **Scorer 0.4.0 can give full credit to a part with extra cuts.** A saved
  development answer (`results/training/screening/qwen3.5-9b-t0.7-x8-2k.jsonl`,
  L3 `gen-0021`, first sample) drills a 4 x 4 grid: the four correct holes
  plus four notches through the long edges. It removes 1.6% of the material,
  inside the 3% tolerance of R6, and scores 1.0. None of the 806 passing
  evaluation answers has such a defect (correction 2), so the verdicts are
  not affected, but "reward 1" does not guarantee the requested part.
- **Execution mode.** The evaluation ran on Windows in `reuse` mode, where
  the solid is measured in the process that ran the model's code. The Linux
  replay runs in `fork` mode, with a separate trusted worker, and reproduces
  every check of every answer.
- **A nearly untrained adapter is not available as a route control.** The
  5-step smoke adapter already scores 52.5% on L4 in training against 32.3%
  at step 1, so it is not a stand-in for the base model.

