# cad-spec

An RL environment where a model reads a dimensioned engineering spec and writes
CadQuery to satisfy it. Scoring is not text similarity: the code is executed,
the resulting solid is measured, and each requirement is checked against the
measurement the way an inspection report would check a machined part.

Part family: rectangular mounting plate, four-hole bolt pattern, parameterised
over length, width, thickness, hole diameter and edge margin. 7 training specs,
3 held out for eval (including the size extremes), so eval scores measure
generalization, not memorization.

## Reward

Single function, scale exactly [0, 1]:

```
1.0    every requirement met
k/6    partial compliance (per-requirement PASS/FAIL)
0.05   runnable CadQuery that satisfies nothing or fails a gate
0.0    code that does not execute, or no code at all
```

## Why the scoring is built this way

Dimensional checks alone are trivially gameable — a solid block with no holes
satisfies every overall-dimension requirement. So the rubric has two layers.

**Gates** zero the reward. Each exists because of a specific cheat:

| Gate | Cheat it kills |
|---|---|
| `single_solid` | four loose corner tabs that share the bounding box |
| `through_holes` | blind dimples that measure like fastener holes from above |
| `hole_count_sane` | swiss-cheesing the plate to hit a volume target |
| `is_plate` | a shell, hollow box, or ellipse extrusion with the right bbox |

`is_plate` compares measured volume against volume predicted from the *measured*
geometry, not from the spec. Gating on the spec would zero any dimensional
error and destroy the partial credit RL needs to climb.

**Requirements** give partial credit: reward is the fraction of R1–R5 met.

All of this is enforced by a 16-case adversarial harness
(`scripts/test_rubric.py` in the source repo) covering hand-written correct,
partially-wrong, and deliberately cheating answers — including domain cheats
like counterbored holes where plain through holes were specified, offset
patterns with correct pitch, and parts built in inches.

## Baseline

qwen2.5-coder:1.5b (local, CPU): mean 0.24–0.42 across runs on the held-out
specs, with individual rollouts spanning the full range 0.0 to 1.0 and strong
within-group variance — well inside the trainable band. Dominant failure mode:
the model completes the template correctly, then keeps writing and destroys the
part with invented API calls. Exactly the behavior RL should remove.

## Layout

```
cad_spec/measure.py      build model code, extract geometry. knows nothing about specs
cad_spec/tasks.py        the part family, prompt template, reference solutions
cad_spec/rubric.py       gates and requirements. the file that matters
cad_spec/environment.py  verifiers wrapper. the only API-coupled file
```
