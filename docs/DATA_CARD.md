# Data card: cad-spec 0.4.0

## Contents
One part family: a rectangular plate, 4 through holes on a rectangular
pattern, equal edge margin. Parameters: length 40 to 220 mm, width 30 to
160 mm, thickness 3 to 14 mm, hole diameter 4 to 12.5 mm (the sampler never reaches 13; the fixed legacy `TASKS` include one 13 mm plate), margin 5 to 25 mm,
all on a 0.5 mm grid. Feasibility rules: hole clears each edge by at least
2 mm, at least 4 mm of web between bores, thickness at most a fifth of the
smaller face.

## Generation
Seeded sampler, `SAMPLE_SEED = 20260813`, 230 draws. Eval: 10 smallest, 10
largest and 10 evenly spaced mid-range plates by area; train: the other 200,
shuffled. Every spec is emitted at five tiers (L0 to L4), so each split holds
5 x its spec count prompts. L4 rev-A models change 1 or 2 fields by 10 to 25% before rounding to the
0.5 mm grid (after rounding, up to about 29%), chosen deterministically from
the spec id. Rev A is itself feasible, and at least one change exceeds its
scoring tolerance by 0.25 mm or more, so an unedited model cannot pass.

## Labels
No labels are stored. The reward is computed by executing the answer and
measuring the solid. `reference_solution(spec)` gives a known-correct answer
for every spec; CI verifies it scores 1.0 across seeds.

## Intended use
RL reward and evaluation for CadQuery generation from dimensioned
requirements; measuring the gap between copying numbers (L0/L1), deriving one
(L2), reading prose (L3) and editing an existing model (L4).

## Out of scope
Other part families, tolerances tighter than the published ones, GD&T, fits,
material selection, strength, manufacturability, assemblies. "R6 material" is
a volume-consistency check.

## Known issues
- A hole breaking out through a side wall is not counted (reported as a
  partial bore). Such parts lose count and pattern rather than pattern and
  margin.
- Held-out wording in L3 is two templates; small, written by the same author
  as the training templates, and each states its numbers in a fixed order: a
  parser that knows all six templates scores 100% on L3 (`parser-template`).
- Bores are recognised only as analytic cylinders; NURBS copies of correct
  parts score 0.
- Prompts are English only.
