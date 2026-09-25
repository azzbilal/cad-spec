# Checking the failure labels by hand

`scripts/failure_modes.py` gives every failed answer one label, from its
re-measured geometry and its code: the first rule that fits, in a fixed order
(unbuilt code, change-order failures, hole-pattern mistakes, other
requirements). The labels feed the failure fingerprints on the leaderboard,
so they were checked by hand before publication.

## Method

`scripts/label_check.py` draws a random sample of failed answers whose label
involves judgement (mechanical failures such as API errors, syntax errors
and cut-off answers are left out, as are the reference programs). Each entry
shows the label, the spec, the correct hole centres worked out from it, the
plate's global position, the measured hole centres, any error, rev A for
change orders, and the full prompt and code. The reviewer answers one
question per entry: is this label the best name, from the list, for the main
failure? Both counts are reported: whether the label is a true statement
about the part, and whether it is the right category.

A sample used to change the rules cannot measure them afterwards, so every
check uses a new seed, and a figure is reported as measured before any fix
it prompted.

## Sample 1 (development, not evidence)

30 answers, reviewed with AI assistance (the maintainer's notes on the
disputed entries, cross-checked against two AI reviews). Every label was a true statement about the part (30/30); 25/30
named the right category. The 5 misses were one gap: answers that drilled
repeatedly at one spot, with the `.hole()` calls separated by `.translate()`,
`.faces().workplane()` or `mirror()`, were filed as "holes misplaced
(other)" instead of "holes stacked at one point".

This check also found a defect in the review file itself: it looked answers
up by model, tier and spec, which matched two different phi-4 runs, and
showed one run's code beside the other's measurements. Two entries that
looked like scorer anomalies were this mismatch. The review file now keys
every entry by run id and refuses ambiguous matches.

The stacked-drilling rule was rewritten from this sample, so it is not
counted as evidence.

## Sample 2 (the reported figure)

30 answers, seed 20260926, drawn from 1,318 failed answers after the sample 1
fixes. Reviewed by an AI agent working from the review file, without access to
any prior verdict on this sample.

**28/30 in the correct category (93%), AI-assisted.** This is not a human
validation. A human review of a new sample (new seed) is still to do and is
listed in the roadmap; until then, the labels should be read as checked by
software and an AI reviewer only.

| Entry | Label given | Correct label | Why it was missed |
|---|---|---|---|
| 15 | build failed | CadQuery API error | `cq.Location` given three vectors; CadQuery reports it as a `DispatchError`, which the API-error rule did not list |
| 25 | no holes | change not propagated to pitch | rev A's pitch kept on a smaller rev B plate put all four holes off the plate, so no measured hole could show the stale pitch |

Both were fixed afterwards: `DispatchError` counts as a CadQuery API error,
and a rev B plate whose code still carries rev A's pitch is labelled from the
code when the geometry cannot show it. The reviewer also suggested naming
three generic error kinds (pending wires, non-integer counts, invalid extrude
arguments); they are now named. The 28/30 stays the published figure; a new
sample is needed to measure the fixed rules.

## External audit of the analysis code

A later audit of the publish patch probed the classifier and the leaderboard
directly rather than sampling answers, and found defects no label sample had
reached:

| Finding | Effect | Fix |
|---|---|---|
| Correct X and Y extremes accepted the pattern | two right corners and two holes between them passed as "edge margin off" | every hole must sit at a nominal corner |
| Code rules read raw text | a comment containing an old `.rect(...)` changed the label; `# .rect(1..2,3)` crashed the whole analysis | rules read parsed code; `.rect()` arguments come from the syntax tree; an unreadable answer gets "classifier error" and never stops the run |
| Any Python exception counted as CadQuery misuse | `int('abc')` was a "CadQuery API error" | the scorer records where each error was raised; CadQuery misuse needs a CadQuery message or origin; the rest is "Python error in model code" |
| Headline averaged over specs common to all tiers | a run at 50% per tier with stray spec ids headlined 100% | a model is ranked only if every headline tier covers exactly the 30 held-out specs |

Each has a regression case in `scripts/test_failure_modes.py` or
`scripts/test_leaderboard.py`, both run in CI.
