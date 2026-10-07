---
name: cad-spec-specification-constraints
description: Read before writing or reviewing cad-spec contract code - typed constraint expressions, holds(), family rules F1-F6, ECO operators (set, require, relax, freeze, release), Contract B, the feasible region, witnesses, MUS/MCS enumeration, allowed_to_move and must_change, infeasible items and near-twins, the item file. Encodes the metrology view of tolerance assessment as feasibility and the rules that keep compiler and grader from disagreeing.
---

# cad-spec-specification-constraints

## Purpose

Make the specification side of cad-spec mathematically unambiguous and
checkable: what a constraint means, what an order does, when a region is
empty, and how to prove it.

## When this skill MUST be used

Any change to `cad_spec/l5/contract.py`, `eco.py`, `item.py`, the offline
compiler (M2b), family rules, constraint kinds, the prompt's printed
contract, or the infeasible-item format.

## When this skill should NOT be used

Measurement of geometry (use cad-spec-geometric-observation); slack values
(cad-spec-uncertainty-and-error).

## Required inputs

The constraint grammar in force; Rev A values; the ECO; the tolerance policy
of the item basis (scorer 0.5.0, observation version).

## Preconditions

Every constraint has a stable ID and one canonical text. Numbers are exact
rationals parsed from text. The family assumptions behind identities
(four-corner centred pattern, containment, non-overlap) are explicit
constraints, not comments.

## Core expert principles

1. **P01** A requirement in words is not a test. Exactly one formal text and
   one evaluator per constraint.
2. **P02** Conformance is the existence of a point in the feasible region;
   grade membership in `R_B`, never closeness to one reference.
3. **P06** Compiler and grader use one meaning (`holds`). Two approximations
   create two verdicts.
4. **P04** Check the specification before checking any answer: Rev A passes
   Contract A, Rev A fails Contract B, a witness exists or the region is
   robustly empty.
5. **P05** One constraint can imply a much tighter hidden one; watch derived
   variables and large coefficients.
6. **P07** Coupled constraints are graded together; per-feature grading is
   an approximation that can be ill-posed.
7. **P31 / EDR-003** A SAT claim carries its witness and is self-certifying.
   An UNSAT claim, every MUS and every MCS needs a certificate or an
   independent check.

## Formal reasoning procedure

1. Parse to the normal form; confirm the canonical text round-trips.
2. Apply the ECO with the fixed operator semantics; the input contract is
   never modified; an ID is targeted once per order and never reused;
   `freeze` refers to a recorded Rev A value.
3. Check exact satisfiability of Contract B (hard) with Rev A values as
   tracked soft equalities.
4. If SAT: choose the witness by the deterministic policy; verify it with
   `holds` in exact arithmetic; enumerate MCSs; derive `allowed_to_move`
   (union) and `must_change` (intersection). `must_change` names variables,
   never values.
5. If UNSAT: re-check with every bound loosened by the robust margin
   (0.01 mm). Still UNSAT: infeasible; enumerate MUSs; attach certificates.
   SAT when loosened: discard and regenerate (neither label is justified).
6. Record decision-rule IDs and the basis (scorer, observation, expression
   versions) in the item.

## Mathematical / geometric operators

```yaml
- operator: holds(constraint, values, slack)
  meaning: and/or tree of linear atoms; slack counted in mm of the variables
  failure_conditions: [variable is None -> False, never skipped]
- operator: apply_eco(contract, eco)
  failure_conditions: [unknown ID, reused ID, two operations on one ID, freeze without Rev A value, edit of a family rule]
- operator: sat(contract, exact)
  output: witness (self-certifying)
- operator: unsat(contract, exact)
  output: certificate (Farkas vector per branch of the min/max split) or independent elimination
- operator: mus_enumerate / mcs_enumerate
  method: exhaustive subsets (amendment 4), each minimality shown by SAT witnesses of every one-smaller subset
```

## Decision rules

`DR-FEAS-STRINGENT-0.01`: infeasible only if UNSAT survives loosening by
0.01 mm and every MUS is that robust; otherwise discard. A structured reject
passes only if the named set equals an accepted MUS (set equality, not
superset).

## Failure modes

FP01 ambiguous specification; FP02 inconsistent or over-tight specification;
FP03 tiny contradiction labelled infeasible; FP04 unverifiable
infeasibility; FP05 witness taken as the answer; FP06 per-feature grading of
coupled constraints; FP20 float leakage; FP21 silent unit conversion.

## Numerical hazards

Floats in parsing (`10.000000001`); scaling a constraint changing what it
accepts (slack must be in mm of the variables, so `2*L == 200` and
`L == 100` accept the same parts); strict inequalities (excluded from the
grammar); large coefficients amplifying slack (P05).

## Out-of-scope cases

Constraints on quantities the observation map does not produce; history
edits ("cancel line N of ECO-1") before L5.2; non-linear constraints beyond
min/max of linear parts.

## Validation requirements

The three owner examples for M2b (many valid answers; plate grows or margins
shrink; several minimal conflicts) plus planted-conflict items whose MUS set
is known by construction. Truth from hand derivation, never from the
enumerator (EDR-005).

## Required evidence

Per item: witness and its exact `holds` check, or certificates; MUS and MCS
lists; decision-rule IDs; basis versions.

## Implementation checklist

- [ ] constraint has ID, unit, canonical text, normal form
- [ ] family assumptions are constraints with IDs (F1 to F6)
- [ ] no float on any exact path
- [ ] witness verified by `holds`, exactly
- [ ] UNSAT and MUS carry certificates; minimality witnesses stored
- [ ] robust-margin re-check before any infeasible label
- [ ] item records rule IDs and basis

## Review checklist

- [ ] could two readings of this constraint give different verdicts?
- [ ] does the grader accept points of the region other than the witness?
- [ ] is every infeasibility claim checkable without Z3?
- [ ] is `must_change` described as variables, never values?

## Tests that must exist

Round trip of canonical text; every refused-order rule; immutability of the
input contract; exact versus measured agreement at limit, limit plus or
minus slack; the three owner examples; planted conflicts; a corrupted
certificate fails; a superset of an MUS fails as a reject.

## Anti-patterns

Grading against the witness; per-variable SAT checks for forcing (miss
either/or couplings, design note §4.2); trusting Z3 output in tests that use
Z3; "infeasible" without the robust re-check.

## Source provenance

F92-GTA §2.4, §3.1, §3.2, §3.5, §4, §8; FM12 §1; PK14 §2.4; design note §3-6;
amendments 4; owner's M2 instructions (7 Oct 2026). Principles P01 to P07,
P23, P31, P32; EDR-002, EDR-003.

## Related skills

cad-spec-conformity-decision, cad-spec-uncertainty-and-error,
cad-spec-numerical-validation.
