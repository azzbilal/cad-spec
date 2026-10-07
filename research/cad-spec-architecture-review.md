# Architecture review after the metrology research

No production code is changed by this review. Rule 5 of `CLAUDE.md` (the
package) and the frozen L5 architecture both stand. Every change below is
additive and is a proposal for the owner.

## 1. Current architecture

```text
Model answer (CadQuery code)
   -> sandbox build, BREP across the trust boundary           G1
   -> strict measurement (measure.py, scorer 0.5.0)           exact analytic faces
   -> observation map v1 (l5/observation.py)                  ok | form_violation | out_of_scope | not_single_solid
   -> Contract B predicates through holds() (M2a)             exact or measured, slack 1e-9 mm
   -> preservation (allowed_to_move), intent (probes)         M3
   -> strict binary verdict + diagnostics                     M3/M4

Offline compiler (M2a/M2b):
   Contract A + typed ECO -> Contract B -> exact rationals (Z3) -> witness, MUS, MCS,
   allowed_to_move, must_change -> item file l5-item/1 (pinned basis, tolerance policy)
```

Strengths the research confirms: formal contract with IDs, one shared
meaning, region grading, exact arithmetic, refusal over guessing, versioned
basis, hand-labelled gates, external audits.

## 2. What the expert knowledge adds

Conformance as feasibility (P02); one agreed method (P06); computational aims
(P37); independent reference data (P31); decision rules named and separate
from error evaluation (P23, P24); invariance and frames (P17, P19, P21);
systematic error is exploitable (P30); sampling plans can be blind (P09).

## 3. Gaps

See [`cad-spec-gap-analysis.md`](cad-spec-gap-analysis.md): G4, G5, G6, G12,
G13, G15, G16, G17, G18 are actionable; G19 and G20 are guard rails; G21 is
deferred.

## 4. Proposed changes

### Must change now (before M2b is frozen)

**A. Certificates for infeasibility and conflict sets (EDR-003).**
WHY: UNSAT is not self-certifying; a wrong MUS is a systematic grader error.
SOURCE: FM12 §1; P31, P30. BENEFIT: the M2b result is checkable without Z3.
RISK: certificate code is new code to review. COST: small (linear algebra
over Fractions on fewer than ten constraints). MILESTONE: M2b.
TESTING: corrupted certificates and wrong MUS must fail; planted conflicts.

**B. Decision-rule IDs in the item schema (EDR-002).**
WHY: the numbers are rules; unnamed rules drift. SOURCE: PK14 §2.4.
BENEFIT: verdicts cite the rule that produced them. RISK: schema change in
M2a (unmerged, so cheap now, expensive later). COST: small.
MILESTONE: M2a second-round changes or M2b. TESTING: boundary cases per rule.

**C. Error-kind field names and `domain` (EDR-006).**
WHY: prevents mixing numerical slack with uncertainty. SOURCE: P14, P27.
BENEFIT: future measurement domain cannot leak in silently. RISK: none.
COST: renames only. MILESTONE: M2a/M2b. TESTING: schema rejects unknown error fields.

**D. Truth-source rule for tests (EDR-005), as a written rule now.**
WHY: shared code between scorer and map (G14). SOURCE: FM12 §1.
COST: one paragraph in `CLAUDE.md` and the validation skill. MILESTONE: now.

### Should change soon (M3, M4)

**E. Computational aims (EDR-001).** Observation map v1 and `holds` first.
WHY: reviewable meaning. SOURCE: TRACIM18 §2.1. COST: documentation.
TESTING: every aim row cited by a gate case.

**F. Boundary-margin diagnostic (EDR-004).** WHY: detect numerics gaming.
SOURCE: F92-GTA §2.5; F06-BAY §3. COST: small; no reward change.

**G. Probe detectability per pattern (EDR-007).** WHY: sampling blindness.
SOURCE: F92-GTA §3.3. COST: compile-time loop over the misconception library.

**H. Spline reason code (G5).** WHY: distinguish "no operator" from "extra
feature". COST: one reason string; observation version bump if it changes any
recorded output (it changes the reason text, not the status).

**I. Truth-source self-test (EDR-005).** COST: a small static scan.

### Possible future improvement (L6, GD&T, new inputs)

Datum-feature frames with symmetry enumeration (P21, P43); minimax form
evaluation with stated optimality (P16); template matching for CAD against
mesh (P08); one-sided treatment of tessellation bias (P27); structured
covariance for scan inputs (P14, P15).

### Academic but currently unnecessary

Bayesian expected-loss decision rules with production priors (P29) for the
grader (rejected for verdicts, G20); minimum-trace frame selection (P18);
Gaussian-process form simulation (P40) for the exact domain; probe radius
compensation (P41).
