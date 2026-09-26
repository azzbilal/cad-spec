# Pre-registration: knowledge or reasoning? Hint and feedback arms

Written and committed BEFORE any run of this experiment. The git history of
this file is the record that the predictions, thresholds and analysis below
were fixed in advance. Any later change to them is a new, dated section, not
an edit.

## Question

The first-shot leaderboard shows which failures happen. This experiment asks
which of them come from missing CadQuery knowledge (fixable by documentation
or by an error message) and which from reasoning about the drawing (not
fixable that way).

## Arms

| Arm | Condition | Source |
|---|---|---|
| A. first-shot | the standard prompt, one answer | the existing runs in `results/runs/` (no rerun) |
| B. hint | the standard system prompt plus [`prompts/cadquery-hints.md`](../../prompts/cadquery-hints.md), one answer | `--arm hint --system-prompt-file prompts/cadquery-hints.md` |
| C. feedback | the standard prompt; if the code does not build, the model sees the error (exception type and message, as a Python traceback would show) and gets one retry | `--arm feedback --feedback-retries 1` |

The hint is general CadQuery knowledge and contains no number from any spec.
Feedback is given only for code that does not build; code that builds but is
wrong gets none, because that would leak the grader. Both arms use the same
settings as arm A: temperature 0, 1,024 output tokens, the 30 held-out specs.

## Models

First-shot shares over the 120 answers the experiment analyses (tiers L1 to
L4; corrected in amendment 1, the first version divided by all 150 answers):

| Model | Why | First-shot main failure (L1 to L4) |
|---|---|---|
| google/gemma-3-27b-it | stacked drilling | holes stacked at one point, 54/120 (45%) |
| mistralai/codestral-2508 | stacked drilling | holes stacked at one point, 50/120 (42%) |
| meta-llama/llama-3.3-70b-instruct | API misuse | CadQuery API error, 56/120 (47%) |
| mistralai/mistral-small-3.2-24b-instruct | API misuse | CadQuery API error, 43/120 (36%) |
| openai/gpt-4o-mini | reasoning control | margin applied twice, 19/120 (16%); no API errors |

## Measures

Tiers L1 to L4 (120 answers per model and arm; L0 is a template tier and is
excluded, as on the leaderboard). Failure labels from
`scripts/failure_modes.py` at the version committed with this file. For each
model and arm, the share of the 120 answers carrying a label, and the
all-pass rate. Differences are paired by (tier, spec) against arm A, with a
95% bootstrap interval over the pairs.

"Knowledge failures" = "CadQuery API error" + "holes stacked at one point".
"Reasoning failures" = "margin applied twice" and "change not propagated to
pitch", each tracked separately.

## Predictions

**P1, hint cuts knowledge failures.** For each of the four API or stacking
models, the knowledge-failure share in arm B is at most half its share in
arm A.

**P2, feedback fixes errors but not stacking.** For each of the four API or
stacking models, the "CadQuery API error" share in arm C is at most half its
share in arm A, AND the "holes stacked at one point" share in arm C is at
least three quarters of its share in arm A. Reason: stacked code builds
without an error, so there is nothing for feedback to act on.

**P3, neither arm fixes reasoning.** For all five models and both arms B and
C, the share of "margin applied twice" and of "change not propagated to pitch"
each moves by at most 5 percentage points (6 answers of 120) from arm A.

Each prediction is reported per model as held or failed, and as confirmed
only if it holds for every model it covers. A failed prediction is a result,
reported as such.

## Analysis

```bash
python scripts/compare_arms.py results/rescored/0.4.0/*.jsonl --failures results/failure-modes-0.4.0.json
```

The script computes the measures above and evaluates P1 to P3 with exactly
these thresholds. It was committed together with this file.

## Budget and stopping

At most $0.20 per run (5 models x 2 arms, 10 runs, 4 tiers each). A run that
ends incomplete is rerun once; if it is still incomplete, the model is
reported as incomplete for that arm and excluded from the verdicts.

## Amendment 1 (2026-09-25, before any run)

An external audit of the analysis code, done before any data was collected,
found that the analysis could produce verdicts it should not. Changed, with
the predictions and their thresholds untouched:

- **Arms are exactly the three registered conditions.** The runner accepts
  only `first-shot`, `hint` (requires the cheat-sheet, no retries) and
  `feedback` (one retry, no cheat-sheet); the first version accepted any
  name and let hint and feedback be combined under one.
- **An arm must match its registration to be judged.** Held-out split,
  temperature 0, 1,024 output tokens, its exact condition (the cheat-sheet
  text as committed, or one retry), a clean complete run, and exactly the 30
  held-out specs once per tier. Anything else is excluded from the verdicts,
  with its reasons in the report.
- **Failure labels are joined by run id, and a missing label stops the
  analysis.** The first version matched labels by model name and counted a
  failure it could not find as a non-failure, so a stale label file could
  turn 100% knowledge failures into 0% and a held P1.
- **Intervals resample specs,** keeping each spec's four tier outcomes
  together (the same 30 specs appear in every tier); the first version
  resampled the 120 answers independently. Intervals are reported only; the
  verdicts use the registered point thresholds, which do not change.
- **Retry costs** are summed call by call, so an unpriced or failed retry no
  longer hides the first attempt's spend.
- **The model table** above now uses the analysed denominator (120 answers).

Each change has a regression case in `scripts/test_arms.py`, including an
end-to-end test from run files through the real failure classifier.

## Deviations

None. All ten runs (five models, two arms) completed on 2026-09-26 with 120
answers each and no API errors; total spend $0.18. No arm was excluded by
the registration checks.

## Outcome (2026-09-26)

Full tables, intervals and per-model verdicts:
[`results/experiments/hint-feedback-results.md`](../../results/experiments/hint-feedback-results.md).
The analysis was reproduced independently on a second machine (Linux,
Windows first) from the committed run files, with identical tables,
intervals and verdicts.

| Prediction | Result |
|---|---|
| P1, the hint halves knowledge failures | **confirmed, 4 of 4 models**: 46 to 59% of answers down to 0 to 4% |
| P2, feedback halves API errors but not stacking | **not confirmed**: the stacking half held for 4 of 4 models; the API-error half held for 1 of 4 (mistral-small, 36% to 18%) and failed for 3 (gemma 11% to 8%, codestral 18% to 10%, llama-3.3 47% to 40%) |
| P3, neither arm moves reasoning failures by more than 5 points | **confirmed, 10 of 10 arms**: the largest move was 3 points |

All-pass rate on L1 to L4, with the paired change against first-shot and its
95% interval (resampling specs):

| Model | First-shot | Hint | Feedback |
|---|---:|---:|---:|
| mistral-small-3.2-24b | 32% | 83% (+51 [+42, +59]) | 43% (+11 [+2, +19]) |
| gemma-3-27b | 12% | 68% (+56 [+50, +62]) | 12% (+0 [+0, +0]) |
| llama-3.3-70b | 16% | 62% (+47 [+40, +53]) | 13% (-2 [-5, +0]) |
| codestral-2508 | 13% | 55% (+42 [+35, +48]) | 12% (-1 [-2, +0]) |
| gpt-4o-mini (control) | 40% | 31% (-9 [-18, +0]) | 40% (+0 [-8, +8]) |

**Reading.** The failures the leaderboard attributes to CadQuery (API misuse
and stacked drilling) are knowledge failures: seven lines of general API
facts remove them almost entirely, and stacked drilling disappears for every
model (gemma 45% to 0%, codestral 42% to 0%). A build error and one retry do
not do the same: P2's API-error half failed. The reasoning failures (margin
applied twice, a change order not propagated to the pitch) are unmoved by
either arm, and "change not propagated" becomes the main remaining failure
once the knowledge gap is closed (gemma 13% under every arm).

**Exploratory, not pre-registered.** These were noticed in the data, not
predicted, and are hypotheses for a future registered test:

- *Retries mostly repeat the error.* Across the four models, 127 answers got
  their build error and a retry; 14 (11%) then passed and 66 (52%) failed
  with the same exception and message as the first attempt. This is
  consistent with error messages naming the symptom ("cannot find a solid on
  the stack") rather than the fix, but that explanation was not tested.
- *The hint hurt the control model.* gpt-4o-mini, which made no API errors,
  fell from 40% to 31% with the cheat-sheet (interval -18 to 0 points; its
  "no holes" and misplaced-hole failures rose). Documentation aimed at one
  failure can disturb a model that did not have it.
