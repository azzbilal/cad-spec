---
name: cad-spec-metrology-router
description: MUST be consulted first, before designing, implementing, modifying, testing or reviewing any cad-spec work that touches geometry measurement, the L5 observation map, contracts and change orders, the scorer or its tolerances, decision rules, feasibility or conflict sets, intent probes, synthetic test parts, datums, GD&T, uncertainty, meshes, STEP or point clouds. Classifies the task and names the cad-spec expert skills that must be read before any code is written.
---

# cad-spec-metrology-router

## Purpose

Decide which cad-spec expert skills apply to a task, make the agent read them
before acting, and make the consultation visible in the report. Distilled
from the research in `research/` (principle IDs P01 to P44 are in
`research/expert-knowledge-map.md`).

## When this skill MUST be used

At the start of any task in this repository that changes or reviews: files
under `environments/cad_spec/cad_spec/` (`measure.py`, `rubric.py`,
`tasks.py`, `l5/`), gate or self-test scripts (`scripts/test_*`,
`scripts/validate_scorer.py`), the L5 design or amendments, item generation,
grading, tolerances, or any proposal involving datums, GD&T, meshes, STEP or
scans.

## When this skill should NOT be used

Pure money, release-process, CI-plumbing, prompt-wording or experiment-
registration tasks with no effect on what is measured, compared or decided.
Then report `Skills consulted: none` with the reason.

## Required inputs

The task statement; the list of files it will touch; the milestone (L5 M2a,
M2b, M3...).

## Preconditions

The task is stated precisely enough to list the files it touches. If not,
read the repository until it is (`CLAUDE.md`, "Working with Bilal").

## Formal reasoning procedure

1. Classify the task with the trigger table. Several triggers may fire.
2. Read every selected `SKILL.md` in full before writing code or a review.
3. Before the first substantial decision, write:

```text
Skills consulted:
- <skill>: <one line on why it applies>
Relevant principles:
- <P-id or FP-id>: <the rule as it applies here>
Domain: exact_brep_analytic | mesh | measured_points
```

4. For each principle, show the chain in the plan or the PR description:
   principle -> engineering decision -> code or test consequence.
5. If no skill applies: `Skills consulted: none. Reason: ...`

## Trigger table

```yaml
triggers:
  observation_or_measurement:      # measure.py, l5/observation.py, new variables, scope rules
    use: [cad-spec-geometric-observation, cad-spec-uncertainty-and-error]
  contract_or_change_order:        # contract.py, eco.py, holds, operators, family rules
    use: [cad-spec-specification-constraints]
  feasibility_mus_mcs_witness:     # compiler, Z3, subset enumeration, item file
    use: [cad-spec-specification-constraints, cad-spec-numerical-validation, cad-spec-conformity-decision]
  tolerance_slack_threshold:       # eps, form tolerance, robust margin, change detection
    use: [cad-spec-uncertainty-and-error, cad-spec-conformity-decision]
  verdict_gate_reward:             # rubric.py, gates G0-G5, pass rule, diagnostics
    use: [cad-spec-conformity-decision, cad-spec-geometric-observation]
  frame_orientation_datum:         # position, rotation, symmetry, origin, datums
    use: [cad-spec-datum-gdt-reasoning, cad-spec-geometric-observation]
  gdt_or_tolerance_zone:           # flatness, position, profile, minimum zone
    use: [cad-spec-datum-gdt-reasoning, cad-spec-geometric-fitting, cad-spec-conformity-decision]
  fitting_mesh_stepfacets_scan:    # any non-analytic geometry, point data, best fit
    use: [cad-spec-geometric-fitting, cad-spec-uncertainty-and-error, cad-spec-geometric-observation]
  tests_suites_artefacts:          # gates, adversarial parts, generators, planted conflicts
    use: [cad-spec-numerical-validation]
  intent_probes_misconceptions:    # probe schedule, sensitivity filter, signatures
    use: [cad-spec-numerical-validation, cad-spec-conformity-decision]
```

## Mathematical / geometric operators

None of its own. The router applies the dependency graph: for the quantity
the task touches, walk down its `requires` edges and load the skill of every
area that is not already settled for this case.

## Core expert principles

- Nothing at a higher level is decided before its lower levels are settled
  (dependency graph in `research/expert-knowledge-map.md`, Part 2): a verdict
  needs a formal predicate, a defined observation, a named decision rule and
  a known error kind.
- Exact nominal CAD and physical measurement are different domains; state
  which one the task is in before anything else.

## Decision rules

A task that changes what is measured, compared or decided without a
`Skills consulted` statement is incomplete. A reviewer may reject it on that
ground alone.

## Numerical hazards

A task that "only changes a constant" (slack, threshold, margin) is a
decision-rule change: it fires `tolerance_slack_threshold`, not none.

## Failure modes

Opening a skill and not applying it (no principle-to-code chain); selecting
only the obviously named skill and missing the cross-cutting ones
(uncertainty, validation); treating a mesh input as exact geometry.

## Out-of-scope cases

Questions about money, Prime, registration and splits are governed by
`CLAUDE.md` rules 1 to 3, not by these skills.

## Validation requirements

The selected skills' tests exist and pass before the task is reported done.

## Required evidence

The `Skills consulted` block, the principle-to-decision chain, and the tests
each selected skill requires, named in the report.

## Implementation checklist

- [ ] triggers classified from the files touched, not only the task title
- [ ] every selected skill read in full before code
- [ ] `Skills consulted` block written before the first substantial decision
- [ ] at least one principle per skill traced to a code or test consequence

## Review checklist

- [ ] every fired trigger has its skills listed
- [ ] each listed principle visibly changed a decision or a test
- [ ] the domain (exact, mesh, measured) is stated

## Tests that must exist

None for the router itself; the selected skills list theirs.

## Anti-patterns

"Skills consulted: all" with no principles named. Coding first and adding
the block afterwards.

## Source provenance

`research/expert-decisions.md` EDR-008; dependency graph in
`research/expert-knowledge-map.md`.

## Related skills

All `cad-spec-*` skills in `.claude/skills/`.
