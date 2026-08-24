# cad-spec

An RL environment where a model reads a dimensioned engineering spec and writes
CadQuery to satisfy it. Scoring is not text similarity: the code is executed,
the resulting solid is measured, and each requirement is checked against the
measurement the way an inspection report would check a machined part.

Part family: rectangular mounting plate, four-hole bolt pattern, parameterised
over length, width, thickness, hole diameter and edge margin. Specs come from
a seeded parametric sampler (`tasks.py`, `SAMPLE_SEED`): 200 training specs
and 30 held-out for eval, stratified by plate area - the 10 smallest, the 10
largest, and 10 evenly spaced mid-range - so eval scores measure
generalization across the size range, not memorization.

## Reward

Single function, scale exactly [0, 1]:

```
1.0    every requirement met
k/7    partial compliance (R1-R3 dimensions, R4 hole count/diameter,
       R5 pattern position, R6 material volume vs nominal ±3%)
0.05   runnable CadQuery that satisfies nothing or fails a gate
0.0    code that does not execute, or no code at all
```

The 0.05 is exactly what its name says: the reward a runnable-but-gated
script earns. It gives a near-zero baseline model a first rung to climb.

Model code never runs in the trainer process: each rollout executes inside an
isolated worker process with an execution timeout (`CAD_SPEC_EXEC_TIMEOUT`,
default 10 s).

## Why the scoring is built this way

Dimensional checks alone are trivially gameable — a solid block with no holes
satisfies every overall-dimension requirement. So the rubric has two layers.

**Gates** zero the reward. Each exists because of a specific cheat:

| Gate | Cheat it kills |
|---|---|
| `single_solid` | four loose corner tabs that share the bounding box |
| `simple_through_holes` | blind dimples that measure like fastener holes from above; also coaxial steps - counterbores are a different fastener interface than specified plain through holes |
| `hole_count_sane` | swiss-cheesing the plate to hit a volume target |
| `is_plate` | a shell, hollow box, or ellipse extrusion with the right bbox |

`is_plate` compares measured volume against volume predicted from the *measured*
geometry within a wide identity band (±12%), not against the spec volume.
Gating on the spec would zero any dimensional error and destroy the partial
credit RL needs to climb.

Hole detection runs two independent discriminators: a surface-inset
membership probe rejects convex cylinders (external rounds, bosses, shell
outer walls) but cannot reject inner corner fillets, which genuinely are
concave cylinders with material outside them; a full-cylinder area check
rejects those quarter-arc partial cylinders but cannot reject bosses, which
close completely. Neither test alone is sufficient.

**Requirements** give partial credit: reward is the fraction of the seven
requirements met.

All of this is enforced by a 20-case adversarial harness
(`scripts/test_rubric.py` in the source repo) covering hand-written correct,
partially-wrong, and deliberately cheating answers — including domain cheats
like counterbored holes where plain through holes were specified, offset
patterns with correct pitch, parts built in inches, and a hollow-geometry
fixture that keeps the hole detector honest.

## Baseline

qwen2.5-coder:1.5b (local, CPU): mean 0.24–0.42 across runs on the held-out
specs, with individual rollouts spanning the full range 0.0 to 1.0 and strong
within-group variance — well inside the trainable band. Dominant failure mode:
the model completes the template correctly, then keeps writing and destroys the
part with invented API calls. Exactly the behavior RL should remove.

*(Numbers predate v0.2.0 — k/6 reward scale, 10-spec dataset, halfway-probe
hole detection. To be refreshed after 0.2.0.)*

## Layout

```
cad_spec/measure.py      build model code, extract geometry. knows nothing about specs
cad_spec/tasks.py        the part family, prompt template, reference solutions
cad_spec/rubric.py       gates and requirements. the file that matters
cad_spec/environment.py  verifiers wrapper. the only API-coupled file
tests/                   pytest suite: harness wrapper, detector units incl. timeout, cross-seed reference checks
```
