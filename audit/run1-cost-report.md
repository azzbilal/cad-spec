# Training run 1 cost audit

Audit date: 2 October 2026. Repository HEAD verified as `fc1130c`. Analysis is offline except public documentation/source reads. No Prime run, evaluation, inference, deployment, push, commit, or live stop was performed. Existing files outside `audit/` were not edited.

## Summary in six lines

1. Root cause: filling 128 useful answers required progressively more paid generation after flat binary-reward groups were rejected; answers also became longer. [Reconstruction](reconstruction.json), `phases`.
2. Confidence: 95% judgment for this explanation, based on exact token/count identities and matching pre-filter rejection rates; billing discounts and unassigned generation remain unresolved.
3. Run cost was $13.8721 over 38 steps, $0.3651/step, or 2.76 times the smoke average; the roughly fivefold figure describes late steps, not the whole run. [Usage](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/usage.json), `total_cost_usd`; [phases](reconstruction.json).
4. Avoidable opportunity: about $7.01 is attributed to discarded completed-cohort inference; exact attainable savings while retaining the same learning signal cannot be established. [Calculation](extra-analysis.json), `discard_total`.
5. Double filtering has no measured additional rejection; inference outside completed cohorts receives a $0.857 attribution, with its exact cause unresolved. [Reconstruction](reconstruction.json), `summaries.run`.
6. Most important guardrail: refuse launch without a verified provider dollar cap or a cumulative dispatch/token reservation bound; add an automatic recorded-spend stop as a second layer.

## Evidence, definitions, and reproducibility

Read first as requested: [registration and Amendments 1 to 5](../docs/experiments/training-run-1.md), [smoke acceptance](../results/training/run1/smoke-acceptance.md), [screening report](../results/training/screening/report.md), [training config](../configs/rl/cad-spec-9b.toml). The two archived request JSON objects match except `max_steps` and `name`; their outer config paths, timestamps and hashes also differ. Thus the literal claim "except max_steps" needs the harmless run-name qualification. Both requests explicitly send temperature 0.7, thinking off, 2,048 maximum output tokens and the same three environment versions/ratios. Service application of temperature/thinking is not independently echoed, as Amendment 4 acknowledges. [Payloads](../results/training/run1/payload-cad-spec-9b.json), `request.json`; [smoke payload](../results/training/run1/payload-cad-spec-9b-smoke.json).

Reproduce with Git Bash:

```bash
source "$HOME/cadspec.sh"
export PYTHONIOENCODING=utf-8 PRIME_DISABLE_VERSION_CHECK=1
python audit/scratch/reconstruct_cost.py
python audit/scratch/extra_analysis.py
python audit/scratch/test_guard_offline.py
```

[reconstruct_cost.py](scratch/reconstruct_cost.py) verifies every captured file's byte count and SHA-256 against both manifests, validates all 43 smoke/run steps, and writes [run-steps.csv](run-steps.csv), [smoke-steps.csv](smoke-steps.csv), [reconstructed-tables.md](reconstructed-tables.md) and [reconstruction.json](reconstruction.json). [extra_analysis.py](scratch/extra_analysis.py) writes [extra-analysis.json](extra-analysis.json) and the proposed patch. Each table below derives from these scripts and the archived `metrics.json`/distributions. Rewards are used solely to explain discarded generation, without judging training effectiveness.

| Quantity | Field and calculation |
| --- | --- |
| Generated answers N | `metrics.metrics[step-1]["progress/rollouts"]`. These are completed groups accounted to a batching cohort, not all requests billed during that wall-clock interval. |
| Generated answers per environment N_e | `N * batch/cad-spec-{L4,L2,L1-L3}`. This ratio describes generated answers, not the trained mix. |
| Trained answers E_e | `N_e * train/cad-spec-ENV/all/is_trainable/mean`; aggregate `N * train/agg/all/is_trainable/mean` is 128 at all 38 steps. |
| Flat groups F_e | `(N_e-E_e)/8`, checked against `pre_filters/all/dropped_rate`, `pre_filters/all/zero_advantage/rate` and `train/agg/all/filters/zero_advantage/mean`. |
| All-solved flat groups S_e | `(N_e * train/cad-spec-ENV/all/reward/mean - E_e * train/cad-spec-ENV/effective/reward/mean)/8`. All-failed = `F_e-S_e`. An absent effective mean contributes zero because E_e=0. |
| Output tokens per generated answer | `train/cad-spec-ENV/all/num_output_tokens/mean`. `n/a` means no answers from that environment. |
| Truncation | `train/agg/all/is_truncated/mean`, all generated answers; the CSV also includes each environment's truncation. Log truncation refers to effective samples and can differ. |
| Duration | `time/step`, orchestrator batching time in seconds, excluding startup and the uncompleted final batch. |
| Generated input/output | `N * train/agg/all/num_{input,output}_tokens/mean`. Sum equals `progress/tokens` exactly. |
| Trained tokens | `progress/input_tokens + progress/output_tokens`, both effective-sample totals. Do not price `progress/tokens` as training tokens. |
| Distribution check | `bins.rewards[].count` sums to 128 for every successful capture. These are trained-batch histograms, not raw grouped rewards; they cannot independently enumerate discarded groups. |

The solved/failed split is an algebraic reconstruction: it assumes the configured binary rewards and only whole zero-advantage groups are rejected. It is supported by integer group counts, exact rejection identities and zero effective zero-advantage rates at every step. Raw group vectors are not archived. No scoring-error mean is nonzero. Current public source explains the token scopes similarly, but the deployed trainer revision was not captured, so that source is corroboration rather than proof of its exact deployed implementation. [Metrics](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/metrics.json), fields above; [reference source](sources/registered-orchestrator.py), token accounting block.

## Reconstructed steps

Flat groups are `all-solved/all-failed`. Output means use all generated answers. Truncation uses all generated answers. Flat counts are algebraically reconstructed from aggregate binary rewards, not raw group vectors. `429` means the distribution capture failed.

| Step | Generated | Trained | Share | L4 flat S/F | L2 flat S/F | L1-L3 flat S/F | Output mean L4/L2/L1-L3 | Trunc % | Seconds | Dist |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 192 | 128 | 66.7% | 2/6 | 0/0 | 0/0 | 113.0/363.2/402.4 | 0.00 | 42.2 | ok |
| 2 | 280 | 128 | 45.7% | 7/10 | 1/0 | 1/0 | 92.4/387.6/419.4 | 0.00 | 57.6 | ok |
| 3 | 160 | 128 | 80.0% | 2/2 | 0/0 | 0/0 | 133.3/408.4/602.8 | 0.62 | 48.5 | ok |
| 4 | 256 | 128 | 50.0% | 6/7 | 1/0 | 2/0 | 152.2/426.7/537.7 | 0.39 | 55.0 | ok |
| 5 | 240 | 128 | 53.3% | 5/3 | 4/0 | 2/0 | 267.9/447.7/468.8 | 0.00 | 42.3 | ok |
| 6 | 232 | 128 | 55.2% | 5/0 | 6/0 | 2/0 | 245.2/445.1/632.9 | 0.00 | 47.3 | ok |
| 7 | 248 | 128 | 51.6% | 4/2 | 5/0 | 4/0 | 345.3/436.6/527.4 | 0.40 | 49.5 | ok |
| 8 | 216 | 128 | 59.3% | 5/3 | 0/0 | 3/0 | 336.6/n/a/551.9 | 1.39 | 30.8 | ok |
| 9 | 224 | 128 | 57.1% | 5/2 | 0/0 | 5/0 | 212.4/423.8/450.5 | 0.00 | 52.2 | ok |
| 10 | 408 | 128 | 31.4% | 13/0 | 15/0 | 6/1 | 264.2/435.3/554.8 | 0.00 | 62.9 | ok |
| 11 | 288 | 128 | 44.4% | 8/1 | 4/0 | 6/1 | 423.4/440.5/558.8 | 0.35 | 38.0 | ok |
| 12 | 296 | 128 | 43.2% | 6/0 | 7/0 | 8/0 | 297.8/417.7/569.5 | 0.34 | 46.8 | ok |
| 13 | 344 | 128 | 37.2% | 7/0 | 12/0 | 8/0 | 371.3/431.2/548.3 | 0.00 | 60.4 | ok |
| 14 | 232 | 128 | 55.2% | 4/0 | 7/0 | 2/0 | 471.3/468.5/633.8 | 0.86 | 40.1 | ok |
| 15 | 312 | 128 | 41.0% | 19/0 | 4/0 | 0/0 | 419.4/491.5/750.0 | 0.64 | 67.6 | ok |
| 16 | 456 | 128 | 28.1% | 10/0 | 17/0 | 14/0 | 499.7/477.3/643.3 | 0.22 | 76.5 | ok |
| 17 | 344 | 128 | 37.2% | 7/0 | 12/0 | 8/0 | 723.2/486.9/672.2 | 1.16 | 58.3 | ok |
| 18 | 536 | 128 | 23.9% | 19/0 | 15/0 | 17/0 | 621.4/495.1/613.1 | 1.12 | 108.8 | ok |
| 19 | 456 | 128 | 28.1% | 17/0 | 17/0 | 7/0 | 635.4/520.9/691.2 | 0.44 | 87.7 | ok |
| 20 | 272 | 128 | 47.1% | 11/0 | 2/0 | 5/0 | 678.8/522.4/666.0 | 2.94 | 54.2 | ok |
| 21 | 304 | 128 | 42.1% | 11/0 | 2/0 | 9/0 | 727.0/534.2/757.3 | 0.66 | 56.2 | ok |
| 22 | 360 | 128 | 35.6% | 14/0 | 9/0 | 6/0 | 859.0/594.3/742.4 | 1.67 | 75.5 | ok |
| 23 | 560 | 128 | 22.9% | 21/0 | 19/0 | 14/0 | 783.7/617.0/802.8 | 1.43 | 131.9 | ok |
| 24 | 472 | 128 | 27.1% | 22/0 | 8/0 | 13/0 | 831.8/625.9/822.6 | 1.48 | 112.4 | ok |
| 25 | 584 | 128 | 21.9% | 26/0 | 20/0 | 11/0 | 750.4/647.6/849.9 | 0.68 | 122.8 | ok |
| 26 | 608 | 128 | 21.1% | 30/0 | 19/0 | 11/0 | 880.8/650.9/864.1 | 1.48 | 149.4 | ok |
| 27 | 592 | 128 | 21.6% | 23/0 | 23/0 | 11/1 | 839.7/656.0/871.3 | 1.35 | 124.4 | ok |
| 28 | 704 | 128 | 18.2% | 37/0 | 19/0 | 16/0 | 822.8/647.6/816.6 | 0.71 | 162.4 | ok |
| 29 | 888 | 128 | 14.4% | 37/0 | 28/0 | 30/0 | 771.5/666.6/828.4 | 1.01 | 187.3 | ok |
| 30 | 592 | 128 | 21.6% | 27/0 | 15/0 | 16/0 | 879.0/678.6/887.5 | 1.52 | 136.8 | ok |
| 31 | 544 | 128 | 23.5% | 28/0 | 15/0 | 9/0 | 814.8/666.3/869.4 | 1.84 | 115.4 | ok |
| 32 | 896 | 128 | 14.3% | 45/0 | 25/0 | 26/0 | 785.9/607.6/776.6 | 0.45 | 183.0 | ok |
| 33 | 1208 | 128 | 10.6% | 62/0 | 40/0 | 33/0 | 722.8/596.5/762.4 | 0.25 | 236.3 | ok |
| 34 | 1488 | 128 | 8.6% | 68/0 | 63/0 | 39/0 | 714.8/573.7/731.6 | 0.20 | 272.2 | 429 |
| 35 | 1216 | 128 | 10.5% | 57/0 | 46/0 | 33/0 | 732.0/556.1/699.6 | 0.49 | 235.2 | 429 |
| 36 | 2032 | 128 | 6.3% | 122/0 | 56/0 | 60/0 | 686.2/553.0/677.2 | 0.05 | 365.3 | 429 |
| 37 | 1264 | 128 | 10.1% | 70/0 | 44/0 | 28/0 | 710.5/538.2/682.4 | 0.00 | 235.8 | ok |
| 38 | 1232 | 128 | 10.4% | 56/0 | 43/0 | 39/0 | 769.4/529.8/706.9 | 0.32 | 248.4 | ok |

## Step cost attribution

These are estimates for completed-step cohorts, not per-step invoices. Training token pricing is exact before four-decimal usage rounding; inference applies the run-level billing/list ratio uniformly. The unassigned tail remains separate.

| Step | Generated input | Generated output | Trained tokens | Training $ | Inference list $ | Allocated total $ |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 112176 | 48347 | 114964 | 0.0690 | 0.0514 | 0.1129 |
| 2 | 163488 | 63330 | 114919 | 0.0690 | 0.0707 | 0.1293 |
| 3 | 94448 | 51759 | 123626 | 0.0742 | 0.0499 | 0.1168 |
| 4 | 149728 | 75500 | 124880 | 0.0749 | 0.0752 | 0.1392 |
| 5 | 140472 | 82562 | 128691 | 0.0772 | 0.0776 | 0.1435 |
| 6 | 136960 | 88197 | 131006 | 0.0786 | 0.0803 | 0.1472 |
| 7 | 145152 | 100938 | 135397 | 0.0812 | 0.0896 | 0.1578 |
| 8 | 128568 | 84763 | 138144 | 0.0829 | 0.0766 | 0.1483 |
| 9 | 129056 | 68312 | 116274 | 0.0698 | 0.0668 | 0.1268 |
| 10 | 236960 | 156638 | 134048 | 0.0804 | 0.1414 | 0.2012 |
| 11 | 168720 | 135486 | 145573 | 0.0873 | 0.1150 | 0.1856 |
| 12 | 172288 | 118777 | 126863 | 0.0761 | 0.1057 | 0.1664 |
| 13 | 200304 | 147182 | 138142 | 0.0829 | 0.1284 | 0.1926 |
| 14 | 136048 | 116937 | 153173 | 0.0919 | 0.0974 | 0.1751 |
| 15 | 188824 | 141664 | 166216 | 0.0997 | 0.1228 | 0.2046 |
| 16 | 263416 | 242668 | 156162 | 0.0937 | 0.1983 | 0.2631 |
| 17 | 198624 | 215523 | 167988 | 0.1008 | 0.1690 | 0.2452 |
| 18 | 309472 | 315577 | 182262 | 0.1094 | 0.2512 | 0.3240 |
| 19 | 268528 | 277259 | 173527 | 0.1041 | 0.2201 | 0.2921 |
| 20 | 161544 | 180056 | 183979 | 0.1104 | 0.1403 | 0.2303 |
| 21 | 179104 | 221061 | 183536 | 0.1101 | 0.1685 | 0.2540 |
| 22 | 212152 | 277311 | 191823 | 0.1151 | 0.2088 | 0.2935 |
| 23 | 324648 | 412116 | 193145 | 0.1159 | 0.3122 | 0.3826 |
| 24 | 275488 | 374973 | 187835 | 0.1127 | 0.2801 | 0.3520 |
| 25 | 341864 | 435334 | 191200 | 0.1147 | 0.3296 | 0.3963 |
| 26 | 355424 | 491081 | 194170 | 0.1165 | 0.3657 | 0.4290 |
| 27 | 342904 | 467579 | 198285 | 0.1190 | 0.3491 | 0.4172 |
| 28 | 412296 | 547563 | 202316 | 0.1214 | 0.4110 | 0.4725 |
| 29 | 510064 | 676303 | 203796 | 0.1223 | 0.5078 | 0.5561 |
| 30 | 350824 | 494282 | 205787 | 0.1235 | 0.3667 | 0.4368 |
| 31 | 320200 | 428746 | 197409 | 0.1184 | 0.3213 | 0.3929 |
| 32 | 524096 | 664851 | 196321 | 0.1178 | 0.5037 | 0.5482 |
| 33 | 701240 | 842386 | 173973 | 0.1044 | 0.6457 | 0.6560 |
| 34 | 862592 | 997309 | 179366 | 0.1076 | 0.7709 | 0.7662 |
| 35 | 707568 | 813890 | 184236 | 0.1105 | 0.6298 | 0.6486 |
| 36 | 1181280 | 1326767 | 170658 | 0.1024 | 1.0323 | 0.9843 |
| 37 | 736776 | 828208 | 180456 | 0.1083 | 0.6443 | 0.6587 |
| 38 | 715320 | 844494 | 187818 | 0.1127 | 0.6498 | 0.6678 |

## Phases

| Cohort | Generated/step | Share | Output/answer | Seconds/step | Allocated $/step | List $/step |
| --- | --- | --- | --- | --- | --- | --- |
| smoke 1-5 | 201.6 | 63.5% | 260.1 | 47.9 | 0.1110 | 0.1259 |
| run 1-5 | 225.6 | 56.7% | 285.0 | 49.1 | 0.1284 | 0.1378 |
| run 6-14 | 276.4 | 46.3% | 408.9 | 47.5 | 0.1668 | 0.1814 |
| run 15-24 | 407.2 | 31.4% | 652.8 | 82.9 | 0.2841 | 0.3143 |
| run 17-28 | 482.7 | 26.5% | 727.8 | 103.7 | 0.3407 | 0.3796 |
| run 25-32 | 676.0 | 18.9% | 777.7 | 147.7 | 0.4561 | 0.5136 |
| run 33-38 | 1406.7 | 9.1% | 669.8 | 265.5 | 0.7303 | 0.8364 |
| run 1-38 | 566.7 | 22.6% | 643.4 | 112.6 | 0.3425 | 0.3840 |

## Cost reconciliation

All figures in this section are calculated in [reconstruction.json](reconstruction.json), `summaries`, and [extra-analysis.json](extra-analysis.json), `reconciliation`, from the two archived `usage.json` files and metric fields listed above.

| Meter | Smoke: metrics | Smoke: billed tokens | Run: metrics | Run: billed tokens |
| --- | --- | --- | --- | --- |
| Trained tokens | 589,781 | 589,781 | 6,277,964 | 6,277,964 |
| Inference input | 591,888 | 892,292 | 12,558,616 | 13,698,416 |
| Inference output | 262,160 | 402,795 | 13,855,729 | 15,147,461 |
| Inference outside completed cohorts | 441,039 total tokens | | 2,431,532 total tokens | |

Training reconciles exactly: `6,277,964 * $0.60/1M = $3.7667784`, reported $3.7668. Smoke training likewise costs $0.3538686, reported $0.3539.

Inference does **not** match the reported list rates: smoke $0.4201354 at list versus $0.3065 recorded, a $0.1136354 difference; run $11.8281598 at list versus $10.1053 recorded, a $1.7228598 difference. Billing/list ratios are 0.7295267 and 0.8543425. Run inference accounts for 72.85% of the $13.8721 total. The CLI's table input/output dollar rows are calculated from tokens and prices, whereas the JSON total is supplied by the backend. Its source comment claims the rows reconcile, but these snapshots contradict that claim. [CLI usage source](sources/installed-cli-usage.py:104); [billing schema/client](sources/installed-api-billing.py:10).

**Hypothesis, not a finding:** discounted/cached input could explain this. If output were charged at full $0.60, the implied input rates would be $0.07265/M in smoke and $0.07423/M in run. The snapshots contain no cached-token breakdown or per-meter actual inference charges; neither a discount nor a billing error can be proven. [Calculation](extra-analysis.json), `inferred_input_rates_if_output_full_list`. Future budgets should use full list prices until resolved.

The step cost table applies the run's billing/list ratio uniformly to each cohort's list inference cost and adds exact training token cost. It sums to **$13.01517**, leaving **$0.85693** outside completed cohorts, including four-decimal rounding. This is a declared allocation, not a per-step invoice. In smoke the comparable subtotal is $0.55498 with $0.10542 outside cohorts. The archived usage schema exposes only run totals and `record_count`, not timestamped billing rows; exact per-step charged costs cannot be recovered from it. [Billing schema](sources/installed-api-billing.py:28).

The user's monitoring transcript gives $(6.89-2.88)/(28-17) = $0.3645 per additional step and $(13.04-9.63)/(38-33) = $0.682 per additional step. Those intervals overlap partially generated batches and use log-derived step numbers. They are consistent with the trend but are not step invoices. Completed-cohort allocation for steps 33 to 38 averages $0.7303, 5.53 times the billed smoke average $0.13208; the full-run billed average is only 2.76 times smoke. [User-provided monitoring table, audit prompt]; [phases](reconstruction.json).

## Root cause and quantified contributions

1. **Flat-group replenishment is the main multiplier.** Smoke generated 1,008 answers to train 640: 63.49% share, 201.6 generated/step. Run generated 21,536 to train 4,864: 22.59% share. Late steps 33 to 38 generated 8,440 to train 768: 9.10% share, 1,406.7 generated/step, 6.98 times smoke. Step 36 generated 2,032 to train 128, a 6.30% share. Its groups contain 238 flat all-solved groups and 16 useful groups. All late flat groups are all-solved. [Step tables](reconstructed-tables.md), [phases](reconstruction.json), `env.solved/failed`.
2. **Longer outputs amplify generation cost.** Generated output mean rises from 260.1 tokens in smoke to 643.4 over run, 669.8 late, a 2.58 multiplier late. Per-environment smoke to late: L4 128.3 to 717.7 (5.59 times), L2 369.3 to 558.6 (1.51), L1-L3 488.7 to 707.8 (1.45). Generated input mean barely changes, 587.2 to 581.1 late. Late generated output volume is 942K/step versus 52.4K in smoke's completed cohorts. Billed run output/38 is 398.6K versus billed smoke output/5 of 80.6K, the approximately fivefold volume claim in Amendment 5. These are different averaging windows. [Phases](reconstruction.json); [usage totals](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/usage.json).
3. **Symmetric contribution accounting avoids assigning the interaction twice.** At list prices, completed-cohort cost rises from $0.12591/step in smoke to $0.83645 late, +$0.71054. Decompose inference as `N * mean per-answer cost`, sharing its interaction equally: more answers +$0.47696 (67.13% of increase); longer output +$0.19768 (27.82%); changed input length -$0.00097 (-0.14%); longer trained sequences +$0.03688 (5.19%). This is an accounting decomposition, not an independently identified causal experiment. [Reconstruction](reconstruction.json), `decomposition`; formula in script.
4. **Double filtering does not multiply rejection.** At all 38 steps, the pre-filter dropped rate equals the overall zero-advantage rate and `1-E/N`; effective zero-advantage rate is zero. No additional loss is measured after the pre-filter. Reapplying the identical zero-advantage criterion to surviving groups is idempotent. Gibberish/repetition are monitoring-only in smoke startup logs. Run's archived tail does not contain startup filter configuration, so its matching service defaults are supported by the registration/live account and metrics, not an archived startup log. [Smoke log](../results/training/run1/snapshots/k3rwpbbk5sio4936onuai7ok/logs.txt:41); [metrics and assertions](scratch/reconstruct_cost.py).
5. **Asynchrony adds exposure but does not explain the main multiplier.** Billed tokens exceed completed-cohort inference by 9.21% in run and 51.64% in smoke. Run residual attribution is $0.857, 6.18% of total. Thus the relative unassigned overhead is smaller in run. Logs show 128 in flight, partial-group buffers and maximum policy lag 0 or 1 in steps 33 to 38. A log's `Max Off-Policy 1` is observed staleness, not an oversampling factor. After step 38 at 16:56:53, generation continues until the last archived line at 17:02:37, when the next batch is 104/128, plus 57 buffered and 128 in flight. That supports an unfinished-final-batch explanation for some excess tokens. Exact allocation among final work, startup, cancellations and other accounting differences is unresolved. [Run log](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/logs.txt:492); `get.run.completed_at` is 17:02:52.
6. **The fixed tier mix keeps sampling flat easy groups.** Over run, generated share is L4 49.48%, L2 26.08%, L1-L3 24.44%; useful shares within environments are 28.38%, 11.25%, 22.95%. Flat groups reconstructed: L4 918 solved/36 failed, L2 623/0, L1-L3 504/3. Discarded-cohort inference attribution is L4 $3.218, L2 $1.920, L1-L3 $1.873, total **$7.011**. These are candidate savings if a sampler can avoid those prompts before generation, not a guaranteed saving from removing a filter. Trained mix is L4 62.17%, L2 12.99%, L1-L3 24.84%. The smoke acceptance document's "realized mix of trained groups" actually describes generated ratios; smoke's aggregate trained L4 share is 31.25%. [CSV](run-steps.csv); [phase totals](reconstruction.json); [discard-cost calculation](extra-analysis.json).

The $7.011 opportunity is 50.54% of run spend under the uniform billing allocation. Preserving all 38 identical updates while avoiding it is not demonstrated. Another counterfactual is an initial $5 spending envelope: $8.8721 above that envelope could have been prevented **less unreported work and stop latency**; this is arithmetic, not measured stop performance. No exact causal "avoidable dollars" claim is possible from one observed run.

### The two anomalies

**Steps 34 to 36:** each file contains `HTTP 429: Too Many Requests (per-token limit)`. The manifest records exit code 1, 105 bytes, identical hashes, captured at 14:12:55, 14:12:57 and 14:12:58 UTC on 2 October. Steps 33, 37 and 38 were successful captures. The two-line files are collection errors, not empty training distributions. The 38 metric rows and logged completed steps are intact. No live refetch is needed to settle the cause; retrying those three read-only distribution calls later would only fill the archive. [Manifest](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/manifest.json), entries for these files; [step 34 error](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/distributions-step-34.json).

**L2 step 12:** 56 generated answers, seven all-solved groups; `all/reward/mean=1`, `all/num_turns/mean=1`, `all/is_trainable/mean=0`, `all/has_error/mean=0`; the `effective/reward/mean` and `effective/num_turns/mean` fields are null. The logged zero reward/turns is an empty-effective-subset display, not scorer failure or zero-turn generation. Step 38 repeats the pattern for L2: 344 generated answers, all solved, none trained. The step-12 log excerpt itself is supplied by the user, because the archived tail starts much later. [Metrics](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/metrics.json), rows `step=12,38`, prefix `train/cad-spec-L2`.

## Why the estimate failed, and a usable cost model

Screening already indicated L4 binary groups were 70% flat, L2 about 3.33% flat, L1/L3 zero in the 30 development prompts. With generated mix 0.50/0.25/0.25, expected initial useful share is `0.5*0.30 + 0.25*(29/30) + 0.25*1 = 0.6417`, requiring about 199.5 generated answers for 128 useful ones. Smoke's 63.49% share and 201.6 generated/step match this initial estimate. This predicts the starting condition, not its evolution. Screening was on development specs, not the training distribution, another extrapolation limit. [Screening report](../results/training/screening/report.md), temperature-0.7 binary-signal table; [smoke phase](reconstruction.json).

For a prompt whose independent answers solve with probability p, an eight-answer group is flat with probability `p^8 + (1-p)^8`. Near p=0.5 this is 0.78%; at p=0.99 it is 92.27%. Real answers need not be independent, so use observed group rates rather than substituting overall pass rate. As more sampled prompts produce identical successful answers, groups lose GRPO signal and pre-filter refill becomes expensive. GRPO subtracts the group mean, so equal binary rewards give zero advantages. [Registered GRPO reference](sources/registered-grpo.py:34); this is a mathematical cost mechanism, not an evaluation of learning.

Five smoke steps never reach the later flat-group regime. Run's first five allocated costs average $0.1284; steps 15 to 24 average $0.2841, steps 25 to 32 $0.4561, steps 33 to 38 $0.7303. The length model also becomes stale: trained tokens/answer rise from 921.5 smoke to 1,552.0 in steps 25 to 32. Both replenishment and length change. Budget sensitivity was only 4.2%, smaller even than these early fluctuations. [Phases](reconstruction.json); [Amendment 4](../docs/experiments/training-run-1.md).

Let B be useful answers per step, g answers/group, f the flat-group fraction, I/O generated input/output tokens per answer, T total tokens per useful trained answer, and prices p_i/p_o/p_t per million tokens. The expected replenishment model is:

```text
useful groups = B/g
expected generated groups = (B/g)/(1-f)
N = g * expected generated groups = B/(1-f)
C_step = p_t * B*T/1e6
       + alpha * eta * B/(1-f) * (p_i*I + p_o*O)/1e6
```

For multiple environments, `1-f = sum(w_e*(1-f_e))` and token means are weighted by generated shares w_e. If useful trained shares are prescribed instead, compute generation separately per environment. g cancels algebraically but changes f: reducing group size is not a free division of total cost. The model assumes stable group yield during that step; starvation f=1 is unbounded without another stop rule.

Calibrate billing ratio alpha separately: smoke 0.72953, run 0.85434. Completed-cohort inference multipliers for billing overhead are smoke input/output 1.50754/1.53645 and run 1.09076/1.09323. These overheads are not known platform constants. A pooled scalar eta is 1.10534 across both archives. [Reconstruction](reconstruction.json); [overhead calculations](extra-analysis.json).

| Retrospective model for the 38 observed steps | Predicted total | Error versus $13.8721 |
| --- | --- | --- |
| Frozen registered smoke cost $0.13208/step | $5.0190 | -63.82% |
| Observed per-step f, frozen smoke lengths, list prices, pooled eta | $9.1996 | -33.68% |
| Observed per-step f and lengths, list prices, pooled eta | $15.7323 | +13.41% |
| Observed f/lengths, run alpha, no eta, plus separately observed residual | $13.8721 | Exact accounting identity, not forecast validation |

Compared with the explicit per-step allocation proxy `allocated_cost + $0.85693/38`, the length-aware list model has MAE $0.0512/step and RMSE $0.0765 across 38 steps. Actual per-step invoice error is unavailable. This model describes observed costs once f and lengths are supplied; no source supports an accurate advance forecast of how quickly f evolves. [extra-analysis.json](extra-analysis.json), `proxy_errors_38`; [script](scratch/extra_analysis.py).

For preflight, use **alpha=1**, **eta=1.54**, stress f at 0.91 and 0.95, generated I=587/O=800, T=1,552, and a further **25% margin**. These are proposed conservative scenarios from the observed ranges, not guaranteed upper bounds. The [offline preflight candidate](scratch/preflight_candidate.py) estimates $185.59 for 104 steps at f=0.91 including margin, versus $12.3146 available from the registered $15 ceiling after prior smoke spend and a proposed $2 operational reserve. It refuses launch. For a genuine bound, cap dispatch count and input/output tokens before spending, or obtain a provider-enforced dollar cap.

## Platform controls, defaults, and limitations

The installed package is Prime 0.8.0 (`prime-0.8.0.dist-info/METADATA`). Its source was copied and hashed under [sources/manifest.json](sources/manifest.json). Current docs and upstream code do not fully agree with the legacy Hosted interface. Do not promote documentation examples or returned null fields into verified service defaults.

| Lever | What it does and default | Would it bound this run? |
| --- | --- | --- |
| `max_steps`, `batch_size`, `rollouts_per_example` | CLI defaults 100/128/8; run sends 104/128/8. Limits updates/useful batch size/group size. [CLI](sources/installed-cli-rl.py:773). | No cumulative generation or dollar bound when pre-filter replenishment can continue indefinitely. |
| `sampling.max_tokens` | CLI default null; run sends 2,048. Per-response output cap. `sampling.temperature` default null; 0.7 sent. [CLI](sources/installed-cli-rl.py:494). | Bounds each one-turn answer, not answers per batch. Input also needs a separate bound. |
| `max_inflight_rollouts` | CLI default null; explicit positive capacity, at least group size; API forwards it. Mutually exclusive with oversampling. [CLI](sources/installed-cli-rl.py:776), validators 799; [API](sources/installed-api-rl.py:324). | Concurrency only. Run observes 128 in flight. Recommend 32 for future budgeted diagnostics; reduces immediate outstanding requests 75% versus 128, not steady-state cost per useful batch. |
| `oversampling_factor` | CLI default null; docs list 2.0. [Advanced docs](https://docs.primeintellect.ai/hosted-training/advanced-configs), Hyperparameters; [CLI](sources/installed-cli-rl.py:779). | No evidence of a cumulative generated-answer cap. 2.0 is not reconciled with observed 128 in flight; deployed effective default is unknown. Prefer explicit capacity 32 and omit this field. |
| `max_async_level` | Returned run schema default null, but no top-level RLConfig field or create-run argument. [API schema](sources/installed-api-rl.py:99); [CLI](sources/installed-cli-rl.py:766), [API signature](sources/installed-api-rl.py:214). | Not an available verified knob in this installed Hosted launch interface. `Max Off-Policy` log value is not its default. Do not invent a TOML value. |
| `buffer_config` / `[buffer]` | Response schema has optional null `buffer_config`; CLI removes `[buffer]` with a deprecation warning. [CLI](sources/installed-cli-rl.py:841); [API](sources/installed-api-rl.py:94). | No. Old difficulty-buffer settings would be ignored. Logged buffered rollouts are not evidence that this removed config still works. |
| Pre/post filters, `enforce` | CLI defaults lists and enforce to null, defers to service; explicit empty lists are forwarded. Pre-filter rejection occurs before batch slots; post-filter after assembly. `enforce=false` records metrics. [CLI](sources/installed-cli-rl.py:626); [API](sources/installed-api-rl.py:311). | Enforced pre zero-advantage causes refill. Moving filtering may allow smaller effective batches, but hosted refill semantics need verification; do not assume it imposes a bound. |
| Difficulty/curriculum | No explicit Hosted legacy curriculum field. Native reference has optional per-source curriculum; default standard sampler/no gates, optional difficulty pools (hard <=.25 weight .2; normal <=.75 weight 1; easy <=1 weight .2). [Native source](sources/registered-orchestrator-config.py:241). | Could reduce sampling of flat prompts; no automatic spend guarantee and not verified exposed by Hosted legacy. |
| Native constant effective batch | Native `constant_trainer_batch_size=true`; false allows variable useful samples from a collected batch. [Native config](sources/registered-orchestrator-config.py:643), [sink](sources/registered-train-sink.py:270). | Candidate for a local/native redesign with fixed generated budget. Requires replay and dispatch-cap verification; cannot assume a legacy Hosted `run_config` passthrough supports it. |
| Native async/rate controls | Reference `max_off_policy_steps=8`, `tasks_per_minute=null`, concurrency min=1/max=1,024, optional heartbeat. [Native config](sources/registered-orchestrator-config.py:637). | Bound staleness, dispatch rate or outstanding work, not total spend. For native budgeted diagnostics propose max off-policy=1 and fixed concurrency 32; more stale cancellation can itself waste inference. |
| Input/turn/total caps | V1 EnvConfig offers optional null `max_turns`, `max_input_tokens`, `max_output_tokens`, `max_total_tokens`. [CLI fields](sources/installed-cli-rl.py:378). | Useful per-rollout limits for a future v1 environment; not proven effective on this v0 package. Keep one turn, require measured input cap, retain output 2,048 until local truncation replay supports reducing it. |
| Per-run spend cap or alert | No explicit spend, budget or alert field in RLConfig/create-run signature inspected. `run_config` is opaque passthrough. [CLI](sources/installed-cli-rl.py:766); [API](sources/installed-api-rl.py:214). | No verified per-run hard cap. Do not assume an undocumented key works. |
| Wallet limits/settings | Public admin schema exposes `spendLimit`, `overdraftLimit`, RFT resource limits; separate settings include auto top-up/cap. Defaults and Hosted spend-enforcement timing are not specified. [Wallet limits](https://docs.primeintellect.ai/api-reference/admin-users/update-user-limits), [wallet settings](https://docs.primeintellect.ai/api-reference/admin-users/update-user-wallet-settings). | Possible provider control requiring provider confirmation; admin schema is not proof of user access, units, or a per-run atomic cap. No spend-alert mechanism was verified. |

No live Prime query was needed: A to C settled the main causes. More `train usage` calls would still return the same aggregate schema. The deployed fully resolved trainer config and detailed billing ledger require provider evidence.

## Process review

| Decision or event | Evidence and fair assessment |
| --- | --- |
| Stationary smoke extrapolation | Section 6.2 and Amendment 4 compute `floor((15-.6854-.50)/.13208)=104`. This followed the registered rule exactly; the rule was inadequate for evolving group yield and answer length. Screening initially predicted smoke well. |
| Small reserve | Projected total $14.42172 left $0.57828, 4.2% of projected run cost. Amendment 4 and smoke acceptance explicitly disclose this sensitivity. It was knowingly fragile, not a hidden billing arithmetic mistake. |
| Filters known in advance | Amendment 1 acknowledges service post filters; config comments say discarded generation is paid. The missing risk was refill volume as groups become flat, not discovering duplicate filters afterward. |
| Monitor crash/stale step | User reports Windows encoding failure and stale log reads. No monitor script, stdout traceback, restart timestamp or original polling records were found in the repo. Treat these as user-reported events, not independently verified causes or durations. UTF-8 fixes are justified by the known CLI glyph output and prior smoke audit. |
| Warning-only monitoring | User-provided table records continuing spend from $2.88 to $13.04 over 56 minutes, with no automatic stop. From $5.03 at 11:11 to final $13.8721 adds $8.8421. Exact preventable portion depends on when a new stop policy would have fired and unreported charges. The original rule stopped at $15 total or technical failure, not an earlier rate threshold. |
| Stop timing | `get.started_at=15:44:56.551`, `completed_at=17:02:52.081`, 77m55.53s. Last completed log step at 16:56:53, then another 5m59s of wall time with continued generation. This is not proven stop-command latency: the stop request time is missing. |
| Clock reconciliation | Metric timestamps are explicitly UTC. Step 38 metric is 16:56:56 UTC, consistent with Chicago 11:56:56 and the user's 11:57 poll. The log success line precedes its metric by about 3 seconds. Do not infer stop latency by treating the monitoring and CLI clock displays as the same zone. |
| Drafted ceiling increase | Amendment 5 says a $20 ceiling was drafted but never adopted. No draft file or decision timestamp was found. The record shows total $14.5575, below the unchanged $15 ceiling by $0.4425; calling this a $15 ceiling breach would be false. |

Sources: [registration](../docs/experiments/training-run-1.md), [smoke acceptance](../results/training/run1/smoke-acceptance.md), [run record](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/get.json), [run log](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/logs.txt), [metric timestamps](extra-analysis.json), and the audit prompt's monitoring account. Amendment 5 records adapter `xfisiyo5vlhn0ys65sf4uad7` and smoke totals $0.6854. Their sum with run usage is $14.5575. Adapter inventory was not independently queried; wallet "nearly empty" and current auto top-up off are user-reported, not verified current account state.

## Guardrails ranked by impact

These are proposals for a future registration, not changes to run 1. Complete script changes are in [guardrails-proposed.patch](guardrails-proposed.patch); nothing under `scripts/` or `configs/` was changed. Scratch candidates exist solely for offline fixture tests.

| Rank | Change and why | Free test before launch | Expected effect and limitation |
| --- | --- | --- | --- |
| 1 | Require provider-enforced dollar cap, or local cumulative dispatch/token reservations. For native training, reserve worst-case input + 2,048 output cost before each request; include trainer and finalization cost. Propose at most 32 groups/256 answers per attempted update, then abort or accept a smaller useful batch. | Replay archived group counts, token maxima and charge fixtures; prove no dispatch can occur when its worst-case reservation exceeds remaining funds and no batch loop can bypass its 256-answer cap. Provider cap needs written scope/lag evidence. | Removes unbounded replenishment. At 128 useful answers, a 256-answer budget can only fill when useful share is roughly >=50%; late observed 9.1% would terminate or yield a smaller batch. If no enforceable bound is available, refuse paid launch. |
| 2 | Add separate automatic usage guard, poll 15s, recorded limit minus explicit reserve, fail closed on unreadable usage, wrong identity or regressing cost, independent runtime stop; verify terminal state after `stop --force`. | [Nine mocked scenarios](scratch/test_guard_offline.py): crossing threshold, terminal run, malformed/429, wrong id, timeout, regressing spend, runtime expiry, stop transport timeout; child encoding/env mocked too. No real CLI call is permitted in tests. | Shrinks the five-minute detection interval about 20-fold. For an illustrative run ceiling $14.3146 and $2 reserve, trigger $12.3146, not at final ceiling. Final spend still can exceed trigger because billing has no freshness timestamp and stop is asynchronous. Reserve $2 is proposed, not a validated bound. |
| 3 | Preflight compares stressed cost plus 25% margin with `min(wallet minus evaluation reserve, registered ceiling minus prior spend) minus operational reserve`; reject missing enforcement. | [Offline candidate](scratch/preflight_candidate.py), no APIs. Replaying run1's 104-step scenario returns $185.59 against $12.3146 and correctly refuses. Test price changes, f=1, nonfinite numbers, insufficient wallet and missing cap evidence. | Prevents launch of this plan under its budget. Does not certify future f or platform prices. |
| 4 | Set explicit `max_inflight_rollouts=32`, omit oversampling, keep g=8 and max output=2,048 initially; native max off-policy=1 only after stale-work replay. Archive exact effective config. | Local schema validation and blocked-write request recorder; verify fields arrive. Replay worst-case output/input caps. Provider must confirm effective semantics without launching a paid run. | Outstanding inference requests fall from 128 to 32. This reduces shutdown exposure and possibly throughput; it does not cap cumulative generation per batch. |
| 5 | Sample train-only prompts with recent mixed reward groups; retire consistently solved/failed prompts with a small registered exploration share, for example 10%, to detect changing difficulty. Use native difficulty pools or a versioned train-only sampler. | Replay archived counts or already saved development answers; no new model calls. Exact train prompt-level history is not in these aggregates, so validate on saved prompt records before adopting. | Targets the approximately $7.01 discarded-inference opportunity; magnitude is uncertain. Removing always-failed prompts can remove difficult targets; removing solved prompts risks forgetting. Training tier mix becomes a new registered choice. |
| 6 | Use fixed generated batches and variable useful batches when supported; pre zero-advantage can be monitoring-only with post rejection, but only if constant useful-batch refill is disabled/absent. Evaluate g=4 against g=8 using offline grouping. | Confirm post-filter/refill behavior in local trainer simulation. Group existing answers into four without generating more and compare usable-group yield. | Keeps surviving GRPO signal while avoiding refill. At p=.99, g=8 useful probability is 7.73%, g=4 is 3.94%; smaller g is not automatically cheaper at fixed useful B. Smaller/variable useful batches change update noise. Removing duplicate post filter alone saves no measured inference. |
| 7 | Replace startup-only smoke acceptance with offline stress replay plus a separately capped pilot. Require >=15 to 20 updates or a predeclared cost/time stop if signal collapses sooner; inspect rolling five-step generation share, output length, charge slope and finalization bill. | Replay all 38 archived steps through candidate policies now. Require multiple windows within, for example, 20% cost variation, plus stress f=.95; a stopped/unstable pilot fails launch acceptance. | Run1 already shows substantial cost changes by steps 15 to 24. Even 20 steps cannot rule out later flat-group collapse, so this supplements a hard bound rather than proving affordability. Pilot cost is included in ceiling. No pilot is launched in this audit. |
| 8 | Keep auto top-up off; verify fresh wallet, reserve evaluation funds and prohibit ceiling increases during a live run. Use verified provider alerts if available; otherwise local console/file warnings at 50/75/90% are informational. | Review settings and dated balance screenshot/read-only evidence; fixture-replay alert thresholds and ensure warning failure cannot prevent stop. | Limits exposure to added funds, but wallet balance alone is not a verified hard cap because overdraft/charge lag is unresolved. Alerts are not stop controls. No top-up, alert setting or wallet setting was changed. |

The proposed guard's central decision is:

```diff
+cost, status = validate_usage(json.loads(call(
+    ['train', 'usage', run_id, '-o', 'json'])), run_id, previous)
+reason = ('recorded spend limit' if cost >= limit - reserve else
+          'runtime limit' if now() - start >= max_seconds else None)
+# Any usage/parse failure also triggers stop.
+if reason:
+    stop_and_verify(run_id, call, sleep)
```

The [full diff](guardrails-proposed.patch) sets child UTF-8 encoding, removes `SSLKEYLOGFILE`, disables version checks, avoids shell interpolation, never reads log steps, requires explicit `--execute`, and retries stop/terminal verification at most three times. It reports unconfirmed stop as an error. It cannot detect a stale-but-monotonic backend total, hence the independent runtime limit and the mandatory enforcement layer. A provider outage or killed local monitor still defeats client-only protection.

## Five-minute preflight checklist

1. Confirm new registration, dated ceiling, prior spend, fresh prices and wallet; reserve evaluation funds and keep auto top-up off.
2. Verify a provider hard dollar cap or cumulative dispatch/token bound, including input/output/trainer cost, lag, retries and teardown. If unverified, do not launch.
3. Run offline stressed preflight and archive its inputs/output. Compare with wallet and ceiling after reserves; reject f=1 or an unaffordable scenario.
4. Validate and archive the exact blocked-write payload: environment version, train-only data, tier mix, grouping, filters, explicit concurrency and token caps. Confirm effective runtime semantics.
5. Run mocked guard tests and stress replay; verify UTF-8, bad JSON/429/timeout handling, stop identity and terminal confirmation. Record owner and independent monitor lifetime.
6. Launch only a separately capped accepted pilot, with the guard ready before dispatch; a full run requires the registered pilot acceptance and the same hard bound. No ceiling increase while it runs.

## Future pre-registration text and platform options

Draft for a **new** experiment, not a retrospective edit:

> Training stops for a registered dollar, cumulative generation/token, wall-time or technical limit, independent of evaluation results. Total budget includes all pilots, failed startup attempts, unreported-work reserve and finalization. Length is set from rolling cost windows and stressed flat-group/length scenarios at full verified prices, with at least 25% margin. A five-step mean alone does not determine run length. No launch occurs without verified spend enforcement. The final adapter at the actual stop is used, with actual completed steps and stopping reason reported. No checkpoint selection follows training rewards. Any changed sampler, tier mix, useful/generated batch definition, group size, filter placement or platform is registered before launch. The locked evaluation, hypotheses and analysis remain pending and blind.

Prime's current [Models & Pricing](https://docs.primeintellect.ai/hosted-training/models-and-pricing) confirms new shared LoRA runs stop being accepted on **5 October 2026**; existing adapters remain downloadable/deployable until further notice. The listed Qwen3.5-9B $0.20/$0.60/$0.60 rates are explicitly legacy shared-LoRA prices, not FFT prices.

Dedicated FFT is closed beta, uses cached models/registered clusters and native configs. Its docs state default limits of 64 GPUs/run and 10 queued runs/user, but publish **no FFT dollar rate** on the inspected page. Obtain a written compute/storage quote; do not extrapolate these LoRA prices. [FFT docs](https://docs.primeintellect.ai/hosted-training/full-finetuning).

Other-provider option: [Tinker pricing](https://tinker-docs.thinkingmachines.ai/tinker/models/) lists Qwen3.5-9B at $0.66/M prefill ($0.132 cached), $1.995/M sampling, $1.463/M training, with checkpoint storage $0.10/GB/month. These are materially different meters/prices and require a fresh budget and trainer integration; no migration is performed. Local `prime-rl` is an alternative whose cost depends on owned/rented GPUs and electricity, not these token rates; native controls make custom dispatch reservations possible. Hardware availability and Qwen9B training throughput on this user's machine are unverified. [Prime training guide](https://docs.primeintellect.ai/verifiers/training).

## Open questions and cheapest resolution

| Question left open | Cheapest way to settle it |
| --- | --- |
| Why billed inference is below list | Ask provider for run-specific timestamped charge ledger, cached-input counts, applied rates and adjustment policy for both IDs. Existing usage totals cannot distinguish caching/discount/error. No new inference needed. |
| Exact charges for each step and 2.43M excess tokens | Obtain that ledger plus request/cancellation/finalization timestamps and resolved deployed config. Align UTC to cohort step timestamps; do not assign all residual to async without evidence. |
| True Hosted defaults and valid native overrides | Provider resolves max inflight, oversampling, async lag, filter refill semantics and run_config allowlist for this deployed revision. Public docs and native code conflict with legacy observed behavior. |
| Atomic wallet/per-run cap and charge/stop lag | Provider confirms units, scope, default overdraft, enforcement point and worst-case delay, with a zero-cost simulation or existing ledger. Until then launch gate fails. |
| Actual monitor failure/restart and stop-request time | Recover original monitor code/output and stop command timestamp from user/session history. No additional platform query can reconstruct an unarchived local crash. |
| Missing distribution captures | Optional read-only retry of only steps 34 to 36 with backoff, preserving original files and manifest; not required for the current count/cost explanation. |
| Prompt-level avoidable generation and curriculum effect | Use already saved train prompt histories if available, otherwise local sampler fixtures and saved development answers. Aggregates cannot identify which exact train prompts should be retired. No test-split access. |
| Current wallet and adapter inventory | Fresh read-only account evidence or allowed deployment inventory; not necessary to establish run cost. This audit relies on user wallet account and Amendment 5's adapter record. |

Verification: all archived hashes and reconstruction identities passed. Nine offline guard scenarios passed with every Prime child process mocked. The stressed preflight refusal was expected. No paid action or locked evaluation occurred; no repository proposal was applied outside `audit/`.
