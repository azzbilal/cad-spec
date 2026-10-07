---
name: cad-spec-conformity-decision
description: Read before implementing or reviewing how cad-spec turns observations into verdicts - scorer requirements and gates, L5 gates G0-G5, the strict pass rule, structured rejects, the RL reward, verdict states (PASS, FAIL, INFEASIBLE, OUT_OF_SCOPE, INDETERMINATE), acceptance at a tolerance limit, guard bands, diagnostics and failure reports. Applies decision-rule and conformity-assessment practice (simple, stringent, relaxed acceptance; false accept versus false reject) to an exact-geometry RL grader.
---

# cad-spec-conformity-decision

## Purpose

Make every verdict the output of a stated decision rule on trustworthy
observations, with the asymmetric cost of a false pass in an RL setting
built in.

## When this skill MUST be used

Changes to `rubric.py`, the L5 runtime grader, gate order, pass rules,
reward shape, report format, diagnostics, or any new verdict state.

## When this skill should NOT be used

Pure measurement changes with no decision effect.

## Required inputs

Observation (status and values); the item (predicates, decision-rule IDs,
accepted MUS); the gate in question.

## Preconditions

Observation status is `ok` before any predicate is evaluated. Predicates are
formal (cad-spec-specification-constraints). The error kind of every slack
is known (cad-spec-uncertainty-and-error).

## Core expert principles

1. **P23** A verdict = tolerance + result + error bound + a stated rule.
   cad-spec's dimension check is relaxed acceptance by numerical slack
   (`DR-DIM-RELAXED-EPS`); name it.
2. **P25** Inside the interval is not proof of conformity; in the exact
   domain the doubt is limited to the slack band (C_m about 1e7), which is
   why binary verdicts are defensible here and nowhere else.
3. **P22** Conformance to the written contract is not functionality; G5 tests
   inherited behaviour, not function. Say so in reports.
4. **P29** Decisions can have more than two outcomes. cad-spec has them:
   PASS, FAIL (with the failing gate), INFEASIBLE expected (structured
   reject), OUT_OF_SCOPE (observation refused), and at compile time
   "discard and regenerate". INDETERMINATE is reserved; it is not a runtime
   verdict in L5 v1 (EDR-004).
5. **P30** False pass costs far more than false rejection in RL: a
   systematic false pass is learned and amplified. Prefer soundness over
   coverage and keep known false rejections documented (spline faces).
6. **P24 / G20** Verdicts depend only on the answer and the item, never on a
   population prior or the policy's own output distribution.
7. **P03** Report the margin, not only the verdict (diagnostic only).

## Formal reasoning procedure

1. G0 output type; G1 build; then observation: not `ok` stops evaluation
   (`out_of_scope` and `form_violation` fail G3 with their reason).
2. Evaluate each predicate with `holds` and the named rule; record the
   signed margin in mm of the variables.
3. Apply gates in order; stop at the first failure; record which gate.
4. For infeasible items: the named conflict must equal an accepted MUS.
5. Emit the verdict with its evidence (below).

## Mathematical / geometric operators

```yaml
pass_feasible:   G0 and G1 and G2 and G3 and G4 and G5
pass_infeasible: G0 and set(named) in accepted_mus     # equality, not superset
margin:          signed distance to the active limit, mm of the variables (diagnostic)
```

## Decision rules

Rule IDs (EDR-002): `DR-DIM-RELAXED-EPS`, `DR-FORM-KERNEL`,
`DR-FEAS-STRINGENT-0.01`, `DR-CHANGE-EPS`. Training reward: strict binary,
same as evaluation (design note §12 default). Minimality and misconception
labels never change pass or fail.

## Failure modes

FP05 witness as answer; FP06 per-feature grading; FP14 integral checks;
FP24 suite success as proof; FP25 systematic grader error exploited.

## Numerical hazards

Answers clustering within a few eps of a limit (gaming numerics); `None`
variables silently skipped (must be false).

## Out-of-scope cases

Risk-based acceptance with production priors (PK14 §3, F06-BAY §2): useful
for an inspection product, rejected for the grader (G20).

## Validation requirements

Per gate: a part passing only that gate's predecessors; boundary cases at
each rule; witnesses pass; hardcoded witnesses fail G5 on intent-bearing
items; supersets and non-conflicts fail as rejects; always-reject and
always-comply baselines score as the design predicts.

## Required evidence

Item ID, observation version, scorer basis, rule IDs, failing gate, failing
predicate ID and margin, misconception set ("consistent with"), artefact
file. Enough to reproduce the verdict without the model.

## Implementation checklist

- [ ] no predicate evaluated on a non-`ok` observation
- [ ] every acceptance cites a rule ID
- [ ] margins recorded, never used for pass/fail
- [ ] verdict independent of population statistics

## Review checklist

- [ ] which wrong answer could pass this gate? (write it as a test)
- [ ] which right answer could fail it? (document if kept on purpose)

## Tests that must exist

Gate-order tests; rule boundary tests; reject set-equality tests; baseline
expectations (unchanged Rev A 0%, always reject about 10%, compiled oracle
100%).

## Anti-patterns

Partial credit per gate in the L5 reward; "close enough" acceptance outside
a named rule; adding INDETERMINATE to the reward; confidence scores on
misconceptions.

## Source provenance

PK14 §2.1-2.4, §3.1-3.4, §4; F06-BAY §2-3; F92-GTA §2.5, §3.5; PEP97 §1;
design note §5, §6, §8, §12. Principles P03, P22 to P26, P29, P30; EDR-002,
EDR-004.

## Related skills

cad-spec-uncertainty-and-error, cad-spec-specification-constraints,
cad-spec-geometric-observation, cad-spec-numerical-validation.
