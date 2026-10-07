---
name: cad-spec-numerical-validation
description: Read before writing or reviewing any cad-spec test, gate suite, defect suite, adversarial part, synthetic artefact, item generator check, planted conflict, intent probe schedule, misconception separability check, baseline, or validation report - and before claiming that an evaluator (measure, observation map, holds, apply_eco, conflict enumeration) is correct. Enforces generator-grader independence, test truth from construction, stated accuracy, and the artefact ladder in artefact-ladder.md.
---

# cad-spec-numerical-validation

## Purpose

Make every claim "this evaluator is correct" rest on reference data whose
truth does not come from the evaluator, with a stated accuracy, and with
failing cases named.

## When this skill MUST be used

New or changed gate suites, defect suites, adversarial parts, generator
checklists (V1 to V12), probe schedules, baselines, reports of a review.

## When this skill should NOT be used

Registered experiment analysis (governed by the pre-registration rules in
`CLAUDE.md`).

## Required inputs

The evaluator's computational aim (or the definition being tested); the
decision the test supports; the artefact level (artefact-ladder.md).

## Preconditions

A computational aim exists or is written first (P37, EDR-001).

## Core expert principles

1. **P31** Generate the question from the answer: build inputs from chosen
   truth (construction parameters, hand derivation, planted conflicts),
   never compute the expected value with the code under test (EDR-005).
2. **P32** Bug-free code is still not exact; every numeric expectation states
   its accuracy measure and tolerance, chosen against the decision it
   supports (not looser).
3. **P33** Prefer a backward statement when exactness is impossible: "exact
   for a part within 1e-9 mm of this one".
4. **P34** Show the grader accepts a region: many different correct answers,
   not one.
5. **EDR-003** SAT is self-certifying; UNSAT and MUS need certificates;
   tests must not share the solver they test.
6. **P09** A test set is a sampling plan; check it can see each error class
   (probe detectability per pattern, EDR-007).
7. **P38** Reports name the evaluator version, the tolerances, and every
   failing artefact by ID.
8. **P26** Passing a suite is evidence about the suite's coverage, not proof
   of every verdict; report known false-rejection classes.

## Formal reasoning procedure

1. Write the truth first (construction parameters or derivation).
2. Choose the artefact level and its expected outcome (value, verdict or
   refusal) before running anything.
3. For each boundary: one case at the limit, one just inside, one just
   outside, at the slack scale.
4. For generators: verify every output against the checklist (V1 to V12),
   discard and regenerate on failure, log discards.
5. Run; compare with the stated accuracy; list failures by artefact ID.

## Mathematical / geometric operators

```yaml
reference_pair:     (input built from truth, expected result)
null_space (fits):  x = x* + e n*, J^T e = 0 keeps the LS solution (FM12 §4.1)
planted_conflict:   choose MUS sets first, then numbers that realise exactly them
region_sampling:    several witnesses spread over R_B (vertices and interior)
detectability:      for each pattern p, exists kept probe q with relation broken by p
```

## Decision rules

A suite passes only if every artefact passes; one failure is listed, not
averaged into a figure of merit.

## Failure modes

FP22 shared bug between generator and grader; FP23 loose test tolerance;
FP24 suite success as proof; FP26 probe set blind to a pattern; FP04 tests
sharing the solver.

## Numerical hazards

Expected values typed as floats that are not binary-exact; expected values
copied from a previous run's output.

## Out-of-scope cases

Statistical claims about models (registered experiments, not this skill).

## Validation requirements

The artefact ladder (`artefact-ladder.md`): each evaluator has artefacts at
every level that applies to it.

## Required evidence

Truth source per case (construction or derivation), expected outcome,
accuracy measure, evaluator version, failing IDs.

## Implementation checklist

- [ ] truth written before running
- [ ] boundary triplets at each limit
- [ ] no expected value produced by the evaluator under test
- [ ] certificates checked without the solver
- [ ] report lists failing IDs and versions

## Review checklist

- [ ] where did each expected value come from?
- [ ] which wrong implementation would still pass this suite?

## Tests that must exist

A self-test that flags gate cases whose expected values come from calling
the evaluator; a corrupted-certificate test; region-sampling tests; blind
probe schedule flagged.

## Anti-patterns

Snapshot tests of evaluator output used as truth; one witness as the only
accepted answer; widening a tolerance to make a test pass.

## Source provenance

FM12 §1-6; TRACIM18 §2-4; TRACIM-DB; F92-GTA §3.3; PK14 §3.2.2; design note
§10; amendments §3. Principles P09, P26, P31 to P38; EDR-003, EDR-005,
EDR-007.

## Related skills

All other cad-spec skills; this one is cross-cutting.
