# cad-spec 0.5.0: report

One document, in order: what was built, what was measured, what it showed,
and what it does not show. Every number below comes from a file in this
repository; the links go to the evidence. Written for release v0.5.0, 5
October 2026.

## Summary

cad-spec is a reinforcement-learning reward environment for one family of
mechanical parts. A model reads a specification, writes CadQuery, and is
scored by measuring the solid it built.

| Question | Result |
|---|---|
| Can current models do the task? | Not reliably. The best of 16 scores 78% [72, 85]; a regex that knows the wording templates scores 75% |
| Why do they fail? | Mostly missing CadQuery knowledge. Seven lines of general facts lift four models by 42 to 56 points. Reasoning failures do not move |
| Does training on this reward fix the reasoning? | On this task, yes. One LoRA run moved the two reasoning tiers from 60% to 100% (+40.0 points), and a replication on fresh specs gave +39.2 |
| Can the reward be trusted? | Scorer 0.5.0 gives full credit to 0 of 1,646 wrong parts and rejects 0 of 720 correct parts in a suite frozen beforehand. Four external review rounds broke three drafts before it was merged |
| What does it not show? | Anything beyond one plate family, one trained adapter and one closed grammar of change orders |

## 1. The environment

**Task.** A rectangular plate with four corner holes, parameterised over
length, width, thickness, hole diameter and edge margin. A seeded generator
gives 200 training specs and 30 held-out development specs, plus two sets of
60 specs used once each: a locked test split and a replication split
([data card](DATA_CARD.md), [protocol](EVALUATION_PROTOCOL.md)).

**Tiers.** The same specs are posed five ways, and the geometry and the
scorer are identical across them, so a score difference comes from how the
requirement was stated.

| Tier | Prompt | What it tests |
|---|---|---|
| L0 | template with slots | copying numbers (warm-up) |
| L1 | requirement table | writing the CadQuery |
| L2 | table without the hole pitch | deriving pitch = size - 2 x margin |
| L3 | prose, with evaluation wordings unseen in training | unseen phrasing |
| L4 | a rev A model plus an engineering change order | a controlled edit |

**Reward.** The model's code runs in a sandbox and hands back geometry; a
separate trusted process measures it from the exact boundary representation.
Ten requirements are checked and the reward is the fraction met, behind gates
that zero known cheats. A binary all-pass reward is used for training
([README, Scoring](../README.md#scoring), [SECURITY.md](../SECURITY.md)).

## 2. The scorer, and why it has two versions

Every result recorded before 4 October 2026 was scored under **0.4.0**, which
is kept selectable so those results replay exactly (961 saved evaluation
answers, 0 mismatches). New runs use **0.5.0**.

The change came from an external audit that found a saved model answer with
four notches cut through its edges scoring 1.0. Scorer 0.5.0 states a strict
contract: one plate, four through holes, nothing else, 0.1 mm on every
dimension.

The order of work was fixed to keep it honest:

1. A defect suite of 2,366 labelled parts was written and committed **before**
   any scorer change. Under 0.4.0 it gives full credit to 1,320 of 1,646
   wrong parts ([before](../results/scorer-validation-0.4.0-under-suite-0.5.0.md)).
2. The scorer was changed. Result: 0 of 1,646 wrong parts at full credit, 0
   of 720 correct parts rejected ([after](../results/scorer-validation-0.5.0.md)).
3. An independent reviewer tried to break it. It did, three times.

| Round | What passed that should not have | Fix |
|---|---|---|
| 1 | A 5 micron pocket over 50 x 50 mm, a 13 micron slot, a 10 micron chamfer; 0.100049 mm inside a 0.1 mm tolerance | Check the form of the part face by face instead of a volume; compare unrounded values |
| 2 | A spline face with a 1 mm bump "recovered" as a plane; a pocket floor stored as a plane through a point 9.8 km away | Accept only true planes and cylinders; judge each surface where it lies across the part |
| 3 | An ordinary cut 1.2e-6 mm deep at a bore mouth, returned by the kernel as nominal faces joined by an edge lying off both | Require edges to lie on faces at the form tolerance; one distance budget per bore |
| 4 | Nothing: 473 parts rerun, 180 further correct plates passed | Recommendation: merge |

The reports are in [`audit/`](../audit/README.md) and every counterexample is
a pinned test in `scripts/test_rubric_050.py` (81 cases).

**What this is and is not.** It is validation on finite cases, reviewed
adversarially. It is not a proof that no wrong part can pass. One known false
rejection is kept on purpose: a correct part converted to spline surfaces is
rejected, because accepting it reopened the round 2 hole.

## 3. Baselines with no model

Before judging models, the tiers were measured with deterministic programs
([results](../results/baselines-deterministic.md)).

| Program | L0 | L1 | L2 | L3 | L4 |
|---|---:|---:|---:|---:|---:|
| Regex copier | 100% | 100% | 0% | 0% | 0% |
| Copier plus one derivation rule | 100% | 100% | 100% | 0% | 0% |
| Parser that knows the wording templates | 100% | 100% | 100% | 100% | 0% |
| Change-order parser (`parser-edit`) | | | | | 100% |

The last row matters for reading every L4 number below. `parser-edit` reads
only the prompt text and passes every L4 task (train 200/200, development
30/30, test 60/60, replication 60/60; frozen on train and development before
the other two were run). **L4 is a closed grammar.** A model that passes it
has learned to carry out this edit grammar, not change orders in general.

Returning rev A unchanged earns a mean reward of 0.774 on L4 with 0% full
passes, which is why the headline metric is the all-requirements pass rate.

## 4. Sixteen models, first shot

One greedy answer per spec, no hints, no retries, 30 held-out specs per tier,
scored under 0.4.0 ([leaderboard](../results/leaderboard/leaderboard.md)).
About $0.27 of API calls.

- The best model, deepseek-chat-v3-0324, scores 78% [72, 85] averaged over
  L1 to L4. The template-aware regex scores 75%. No model clearly beats it.
- The most common failure is not geometry. It is CadQuery's stack semantics:
  drilling repeatedly at one spot because positions were computed but never
  bound to the drilling call.
- Failure labels were checked by AI-assisted review of three fresh random
  samples: 28/30, 28/30 and 27/30 correct ([method](label-check.md)).

## 5. Experiment 1: knowledge or reasoning?

Pre-registered ([plan and outcome](experiments/hint-feedback.md)). Five models,
the same 120 tasks, three arms: first shot, the same prompt plus seven lines
of general CadQuery facts, and one retry after a build error. Cost $0.18.

| Model | First shot | Plus cheat-sheet | Plus error and retry |
|---|---:|---:|---:|
| mistral-small-3.2-24b | 32% | 83% | 43% |
| gemma-3-27b | 12% | 68% | 12% |
| llama-3.3-70b | 16% | 62% | 13% |
| codestral-2508 | 13% | 55% | 12% |
| gpt-4o-mini (control) | 40% | 31% | 40% |

- **Confirmed:** the CadQuery failures are knowledge failures. The
  cheat-sheet cut API misuse and stacked drilling from 46 to 59% of answers
  to 0 to 4%.
- **Not confirmed:** an error message does not replace documentation. One
  retry halved API errors for one model of four.
- **Confirmed:** reasoning failures (margin applied twice, change orders not
  carried to the hole pitch) moved by at most 3 points under either arm.

Prompting does not fix the reasoning failures. The next experiment asked
whether training does.

## 6. Experiment 2: reinforcement learning on the measured reward

Pre-registered, with five dated amendments
([plan, amendments, result](experiments/training-run-1.md)).

**Setup.** Qwen3.5-9B, LoRA, GRPO on the binary all-pass reward, cheat-sheet
in the prompt, training split only. Stopped on cost after 38 of 104
registered steps. Evaluated once on the locked 60-spec test split, greedy,
against the same model untrained.

| Tier | Base | Adapter | Difference [95% interval] |
|---|---:|---:|---|
| L1 | 86.7% | 100.0% | +13.3 [+5.0, +21.7] |
| L2 | 83.3% | 100.0% | +16.7 [+8.3, +26.7] |
| L3 | 75.0% | 98.3% | +23.3 [+13.3, +35.0] |
| L4 | 36.7% | 100.0% | +63.3 [+51.7, +75.0] |

**Registered hypothesis confirmed:** on L2 + L4, 60% to 100%, +40.0 points
[+32.5, +47.5], against a registered minimum of +10. Seventy pairs improved
and none worsened.

**Replication.** The same frozen adapter on 60 fresh, disjoint specs, also
pre-registered ([plan and result](experiments/replication-1.md)).

| Tier | Base | Adapter | Difference [95% interval] |
|---|---:|---:|---|
| L1 | 70.0% | 100.0% | +30.0 [+18.3, +41.7] |
| L2 | 83.3% | 100.0% | +16.7 [+8.3, +26.7] |
| L3 | 78.3% | 96.7% | +18.3 [+6.7, +30.0] |
| L4 | 36.7% | 98.3% | +61.7 [+50.0, +73.3] |

L2 + L4: **+39.2 points [+31.7, +46.7]**. The registered consistency rule is
met (difference from the original gain -0.8 points [-11.7, +10.0]); that is
a wide interval, not a proof of equal effects. Pooled, the adapter passes
both tiers on 119 of 120 specs (lower bound 95.4%).

**Checks on the result.**

- *Integrity.* An independent audit found no reward hacking and no leakage;
  perturbed answers fail (`audit/run1-result-integrity.md`).
- *Exactness.* A second implementation compared every passing answer with
  the ideal part: 800 of 806 are nominal, six have a hole centre off by 0.25
  or 0.5 mm, which 0.4.0 accepted.
- *Stricter scorer.* Re-scoring both evaluations under 0.5.0 changes those
  six verdicts and gives +41.7 and +40.8 points
  ([table](../results/training/scorer-0.5-sensitivity.md)). Descriptive only:
  it replaces no registered verdict.
- *Serving route.* Base and adapter were served on different routes. A free
  bridge check shows the training stack with untrained weights scores no
  higher than the base route on L4 (28.4% against 42.9%), so "the stack
  serves the same weights better" is not supported. The adapter route itself
  is not attested.

**Where the adapter failed.** Two L3 answers ran past the 2,048-token limit,
and one L4 change order that alters the width and the edge margin together
was solved wrongly.

**Cost.** $13.87 for the run, of which about $7 paid for answers the filter
discarded once most prompts were solved (`audit/run1-cost-report.md`).
$0.1271 for the replication.

## 7. What this does not show

Stated plainly, because the numbers above are large:

- **One part family.** A plate with four holes. Nothing here says the method
  transfers to other parts.
- **One adapter.** One training run, replicated on new specs but never
  retrained. Run-to-run variance is unmeasured.
- **L4 is a closed grammar** that a short parser solves completely. The
  gains of +63.3 and +61.7 points on L4 show that training taught the model
  this grammar.
- **Ceiling.** The adapter is at or near 100% on both splits, so the size of
  the effect above "very large" cannot be read off.
- **Serving routes** are bridged but not attested.
- **The scorer** is validated on finite cases, on one part family.
- **"Material"** means volume consistency only: no alloy, strength, fit or
  manufacturability.

## 8. How the work was kept honest

- **Pre-registration.** Both experiments and the replication were written
  down, with thresholds and analysis, before the data existed. Changes are
  dated amendments made before the outcome they could influence.
- **Frozen first.** The locked test split, the replication split, the
  comparison scripts, the L4 parser and the scorer's defect suite were each
  committed before the run they judge.
- **Used once.** The test split and the replication split were each
  evaluated once and are never used to select or tune anything.
- **Recorded results are not edited.** Corrections are dated sections that
  keep the original text. Old results replay under the scorer they record.
- **External review.** Every audit report is kept in
  [`audit/`](../audit/README.md), including the ones that found faults.
- **Cost.** The four paid items above sum to about $14.45.

## 9. Reproduce

```bash
git clone https://github.com/azzbilal/cad-spec && cd cad-spec
pip install "cadquery==2.8.0"
python scripts/test_rubric_050.py      # 81 hand-labelled cases, scorer 0.5.0
python scripts/test_rubric.py          # 37 cases pinning scorer 0.4.0
python scripts/validate_scorer.py      # the 2,366-part suite, about ten minutes
python scripts/replay_eval.py results/training/run1/eval/adapter-test.jsonl
```

The last command re-scores a saved evaluation under the scorer it recorded
and reports mismatches; the expected count is zero. No API key and no paid
service is needed for any of these.

## 10. Next

In order, from the [roadmap](../ROADMAP.md): a harder edit tier on fresh
specs that a parser does not solve, a true serving-route control, a transfer
set written by hand, and only then a second training experiment with a hard
cost cap.
