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
validation (see "Method" below).

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

## Sample 3 (seed 20260927, AI-assisted)

30 answers drawn after the audit fixes. Reviewed by an AI agent, like sample
2; planned as the human check, it is recorded for what it was.

**28/30 in the correct category (93%), AI-assisted.**

| Entry | Label given | Correct label | Why it was missed |
|---|---|---|---|
| 6 | build failed | CadQuery API error | `.hole(11.0, "through")`: the error was raised inside CadQuery, but the scorer put the origin tag at the END of the error text, and the 300-character cap on error text (a sandbox safety limit) cut it from long messages. 11 answers had this pattern |
| 10 | CadQuery API error | geometry kernel failure | a fillet too large for its edge is a valid call on impossible geometry; kernel refusals were filed as API misuse |

Fixed afterwards: the origin tag now comes first, where the cap cannot reach
it, and names the CadQuery function that raised the error (so a generic
`TypeError` reads "TypeError in Workplane.rect()"); kernel refusals have their
own label, "geometry kernel failure"; "Cannot union type" is a named kind. The
tag test now runs through the real sandbox, cap included; the earlier test
called the inner function directly and could not see the cap.

Independence rule: a reviewer must not have seen another reviewer's verdicts
on the same sample, so a sample reviewed once is not reviewed "fresh" again.

## Sample 4 (seed 20260928, AI-assisted)

30 answers. Reviewed by an AI agent; the maintainer then reviewed and
confirmed its three disagreements. The maintainer had seen the AI verdicts, so
this is a confirmation, not an independent human check.

**27/30 in the correct category (90%), AI-assisted, disagreements confirmed
by the maintainer.**

| Entry | Label given | Correct label | Why it was missed |
|---|---|---|---|
| 1 | no holes | holes stacked at one point | the model drilled four times into the plate's SIDE, along X, without using its computed positions; the scorer measures Z bores only (as the spec requires), so it saw no hole |
| 13 | pattern anchored at a corner | some holes right, some wrong | two holes exactly right, two between them: the extremes had the span of a corner-anchored rectangle, and the mistake patterns checked only extremes |
| 14 | holes misplaced (other) | pattern anchored at a corner | a correct pattern started at the origin; three of its four holes fell off the plate, and holes that were never cut leave no geometry to classify |

Fixed afterwards: the measurement counts closed concave bores along other
axes (reported, never scored), and an answer with no Z bore but a side bore is
"holes stacked at one point" when its drilling repeats without moving,
otherwise "holes drilled along the wrong axis"; every mistake pattern (corner,
margin twice, swapped, pitch as coordinates) must now place every measured
hole on the grid it predicts. #14 is a known limitation (below).

## Method

The failure labels are checked by AI-assisted review of independent random
samples (seeds 20260926, 20260927, 20260928: 28/30, 28/30, 27/30), each
drawn fresh and reviewed without access to earlier verdicts on it. The
maintainer rules on taxonomy questions the reviews raise. No human-validated
accuracy figure is claimed. Every figure is reported as measured before the
fixes it prompted.

## Known limitations

- **Holes that land off the plate.** When most of a pattern falls outside
  the plate, only the holes that were actually cut can be classified, so a
  correct but misplaced pattern can read as "holes misplaced (other)"
  (sample 4, #14). The proper fix is to record where each `.hole()` call
  aims during the rebuild; it is on the roadmap.

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
