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
