---
name: cad-spec-uncertainty-and-error
description: Read before touching any cad-spec number that expresses error, slack or doubt - eps 1e-9 mm, the form tolerance 1e-7 mm, kernel (OCCT) tolerances, the 0.01 mm robust margin, change-detection thresholds, scorer TOLERANCES, item tolerance policy, known kernel biases, and any proposal mentioning uncertainty, confidence, noise, covariance or measurement error. Keeps numerical error, model error, measurement uncertainty, specification looseness and semantic ambiguity apart.
---

# cad-spec-uncertainty-and-error

## Purpose

Stop error kinds from being collapsed into one number, and stop known
biases from being treated as noise.

## When this skill MUST be used

Any change to slack, tolerance or threshold constants; any new field
expressing error; any new input domain; any wording in docs that says
"uncertainty" or "confidence".

## When this skill should NOT be used

Specification tolerances that are contract values (those are constraint
data; see cad-spec-specification-constraints).

## Required inputs

The domain (`exact_brep_analytic`, `mesh`, `measured_points`); the quantity;
the decision it feeds.

## Preconditions

The domain is stated. In the exact domain there is no measurement
uncertainty.

## Core expert principles

1. Five kinds, five treatments, never one field (EDR-006):

| Kind | Exists in L1-L5? | Representation | Treatment |
|---|---|---|---|
| numerical error | yes (about 1e-13 mm noise) | `numerical_slack_mm` (1e-9) | relaxed acceptance by slack, a named rule |
| kernel geometric tolerance | yes (1e-7 mm) | `kernel_tolerance_mm` | form decisions only |
| model error (operator wrong for the geometry) | prevented | refusal reason | `out_of_scope`, never a number |
| measurement uncertainty | no | reserved `measurement_covariance` | only in a measurement domain |
| specification looseness / semantic ambiguity | no number | template defect or refusal | fix the contract text |

2. **P24** Evaluating error is technical; choosing what to do about it is a
   decision rule owned by the project. Keep the two in separate code.
3. **P27** A known bias is not noise: correct it, refuse the case, or apply
   it one-sided (SUMU: `U+ = max(k u_c - delta, 0)`, `U- = max(k u_c + delta, 0)`).
   Never add it in quadrature (RSS with `u_c` overstates, RSS with U
   understates, below 80% achieved for nominal 95% at `delta/u_c = 2`).
4. **P30** Systematic error does not average out; in RL every grader error is
   systematic for the policy.
5. **P14** If a measurement domain ever arrives, never assume iid isotropic
   errors silently; use a structured covariance or flag the assumption.
6. **P32** Bug-free software is still not exact; state every accuracy
   claim with its measure (forward or backward, P33).

## Formal reasoning procedure

1. Name the domain and the error kind of the quantity.
2. If numerical: derive the bound from kernel evidence, pin it to a scorer
   version by name, never copy the value.
3. If it is a known signed effect: choose correct, refuse or one-sided, and
   record which.
4. Hand the value to a named decision rule (cad-spec-conformity-decision).
5. Write the slack in mm of the variables so scaling a constraint does not
   change what it accepts.

## Mathematical / geometric operators

```yaml
slack_check:   accept |lhs - rhs| <= eps in mm-of-variables scaling (M2a holds)
bias_one_sided: limits shifted by the signed bias on one side only
propagate (future): U_b = K U_d K^T ; frame: X = G + K H
```

## Decision rules

`DR-DIM-RELAXED-EPS` (1e-9 mm), `DR-FORM-KERNEL` (1e-7 mm),
`DR-FEAS-STRINGENT-0.01`, `DR-CHANGE-EPS`. A new value is a new rule ID and,
if any score can move, a new scorer version.

## Failure modes

FP19 bias folded into symmetric slack; FP20 float leakage; FP25 systematic
grader error exploited; FP27 assumed Gaussian or isotropic errors.

## Numerical hazards

Spline bounding-box padding (about 2e-7 mm, signed); binary doubles making
two "equal" diameters differ by 1e-9 mm; rounding before a decision;
`U(k=2)` is not `2 x U(k=1)` for biased results.

## Out-of-scope cases

Physical measurement uncertainty, CMM error models, scan noise: deferred
(EDR-009).

## Validation requirements

Boundary cases at each slack (at the limit, just inside, just outside);
evidence for each numerical bound (kernel tests on representative parts).

## Required evidence

For each constant: its kind, its source (scorer basis by name), the rule it
feeds, its boundary tests.

## Implementation checklist

- [ ] no field named `uncertainty`
- [ ] domain stated
- [ ] constants imported by name from the scorer basis
- [ ] signed effects handled explicitly
- [ ] slack in mm of the variables

## Review checklist

- [ ] could this number be read as a measurement uncertainty by a reader?
- [ ] is anything with a known sign treated symmetrically?

## Tests that must exist

Boundary pins for every slack; a non-binary-exact decimal; a scaled
constraint accepting the same parts; a known-bias case on the biased side.

## Anti-patterns

"Add a bit of tolerance" to make a test pass; RSS of a bias; copying a
constant instead of importing it; one `uncertainty` float.

## Source provenance

PEP97 §1-4; PK14 §2.4, §3.2.3, §3.4; F06-BAY §3; F06-FIT §3.7; FM12 §2-3;
scorer `TOLERANCES` docstring; amendments 2 and §3. Principles P14, P24,
P27, P28, P30, P32, P33; EDR-002, EDR-006.

## Related skills

cad-spec-conformity-decision, cad-spec-geometric-observation,
cad-spec-specification-constraints.
