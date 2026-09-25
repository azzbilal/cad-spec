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

30 answers. Every label was a true statement about the part (30/30); 25/30
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
fixes. Checked by a human reviewer (a mechanical engineer), independently of
any prior verdict.

**28/30 in the correct category (93%).**

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
