# Gap analysis: expert model against current cad-spec

Basis read on 7 October 2026: `main` at `8e5ce69` (scorer 0.5.0, L5 M1
observation map), the governing design note and amendments, and the M2a
description from the project record (`contract.py`, `eco.py`, `item.py`,
branch `feat/l5-m2a-contract`, unmerged; its code was not re-read here, so
statements about M2a are medium confidence).

Decisions: **KEEP** (expert evidence supports it), **REFINE** (right idea,
needs a stated rule or a field), **REPLACE** (wrong), **ADD** (missing),
**DEFER** (right later), **REJECT** (expert idea that does not fit cad-spec).
Nothing below reopens the L5 architecture; every REFINE and ADD is additive.

## Summary

| # | Concept | Decision | Principles |
|---|---|---|---|
| G1 | Contract as formal constraints with stable IDs | KEEP | P01 P02 |
| G2 | One meaning for compiler and grader (`holds`) | KEEP | P06 |
| G3 | Feasible region instead of one reference Rev B | KEEP | P02 P34 |
| G4 | Observation = scalar values plus a verdict | REFINE | P10 P17 |
| G5 | Exact domain vs measurement domain | REFINE (make explicit) | P19 P44 |
| G6 | Numerical slack 1e-9 mm and form 1e-7 mm | REFINE (name as decision rules) | P23 P24 P25 |
| G7 | Robust infeasibility margin 0.01 mm | KEEP | P03 P23 P29 |
| G8 | Runtime verdicts are binary per gate | KEEP, ADD boundary diagnostic | P03 P29 P30 |
| G9 | Frame by declaration (global axes) | KEEP, REFINE (document as measurand definition) | P19 P21 |
| G10 | Symmetric plate family | KEEP, document | P21 |
| G11 | Change detection threshold | REFINE (already planned) | P23 |
| G12 | Infeasibility and MUS correctness | ADD (certificate or independent check) | P31 P32 |
| G13 | Test truth source | REFINE (rule: never from the code under test) | P31 |
| G14 | Shared measurement code between scorer and map | KEEP, with a stated risk | P06 P31 |
| G15 | Intent probes as a sampling plan | REFINE (detectability check per pattern) | P09 |
| G16 | Computational aims per evaluator | ADD | P37 P38 |
| G17 | Known one-sided kernel effects | REFINE | P27 |
| G18 | Derived-variable sensitivity | ADD (diagnostic) | P05 P20 |
| G19 | A single `uncertainty` field anywhere | REJECT | P14 P27 P30 |
| G20 | Prior- or population-dependent grading | REJECT | P29 P30 |
| G21 | Fitting, datums from features, GD&T zones, scans | DEFER | P08 P11-P16 P18 P42 |
| G22 | Misconception separability and set-valued matching | KEEP | P29 |
| G23 | Minimality in native units, no weights | KEEP | P24 |

## Details

### G1. Contract as formal constraints
EXPERT: formal parameter and form constraints remove the ambiguity of
natural-language tolerances (P01) and define conformance as feasibility (P02).
CURRENT: Contract A and B with IDs, typed expressions over exact rationals,
one canonical text per constraint (M2a). The prompt prints the IDs.
DECISION: KEEP. The expert record is unusually direct support.

### G2. One meaning
EXPERT: supplier and customer disagree when they use different
approximations; agree the method early (P06).
CURRENT: M2a's `holds` is the single meaning for the exact compiler and the
measured grader; they differ only by a slack the tolerance policy controls.
DECISION: KEEP. Add a test that runs `holds` on the same constraint through
both entry points on boundary values (exact limit, limit plus or minus the
slack) so the shared-meaning claim is enforced, not described.

### G3. Region grading
EXPERT: the feasible region (P02); null-space generation shows one answer
corresponds to many inputs (P34, by analogy).
CURRENT: design note §3.4; the owner's correction that `must_change` is a
variable, not a value.
DECISION: KEEP. M2b mandatory example 1 (many valid answers) is the test.

### G4. Observation semantics
EXPERT: a feature value is the output of an association operator in a frame
(P10); variables differ in invariance (P17).
CURRENT: `Observation(status, reason, values, centre)`; the rules live in the
module docstring and `L5-amendments.md` §3. Operators are implicit: L, W, T
from the axis-aligned bounding box; D and the hole axis from the kernel's
analytic cylinder; mx, my as minimum distance from axis to bounding faces.
GAP: the operator, the frame and the invariance class are prose, not data,
and not versioned as one object.
DECISION: REFINE, documentation first. A static observation-definition table
per observation version (operator, frame, invariance class, domain, numerical
bound, refusal rules), not per-instance fields. See EDR-001. Per-instance
fields would bloat every result for information that never varies within a
version.

```text
CURRENT                                 BETTER (static, versioned)
values["mx"] = 15.0                     OBS_DEF_V1["mx"] = {
                                          operator: "min over through bores of distance
                                                     from analytic axis to AABB side planes",
                                          frame: "declared global axes; position free",
                                          invariance: "frame_free",
                                          domain: "exact_brep_analytic",
                                          numerical_bound_mm: <from kernel tests>,
                                          refuse_when: [tilt > 1e-12 rad, nested cylinders, ...] }
```

### G5. Exact domain vs measurement domain
EXPERT: data only speak about data (P44); with ideal geometry datum choice
is immaterial (P19).
CURRENT: implicitly exact: analytic planes and cylinders only; splines are a
`form_violation` (a known false rejection kept on purpose).
DECISION: REFINE by stating the domain in every observation definition and
item (`domain: exact_brep_analytic`), and by giving "no association operator
is defined for this surface type" its own reason code, distinct from "an
unrequested feature". Today a spline face is reported under the same verdict
as a boss.

### G6. Numerical slack as a decision rule
EXPERT: every acceptance is a stated decision rule (P23); uncertainty is
technical, the rule is a choice (P24).
CURRENT: dimension slack `eps = 1e-9 mm` (scorer 0.5.0), form tolerance
`1e-7 mm` (kernel confusion), robust margin 0.01 mm, all inclusive.
GAP: in metrology terms, accepting `value <= limit + eps` is a *relaxed
acceptance* rule whose zone extends past the tolerance limit by the numerical
bound. That is correct for the exact domain (the true value of an exact
B-rep is its definition; eps covers kernel noise near 1e-13 mm), but it is
not named, so a future change could silently mix it with a measurement
uncertainty.
DECISION: REFINE (EDR-002): give each rule an ID and record it in items and
verdicts: `DR-DIM-RELAXED-EPS`, `DR-FORM-KERNEL`, `DR-FEAS-STRINGENT-0.01`.

### G7. Robust infeasibility
EXPERT: report the margin (P03); stringent rules protect the costly error
(P23); a third decision exists (P29).
CURRENT: an item is infeasible only if it stays infeasible when loosened by
0.01 mm and every minimal conflict is that robust; otherwise the item is
discarded and regenerated.
DECISION: KEEP. It is a stringent rule with a guard band, plus a "neither"
outcome handled by regeneration. Exactly what the literature recommends
when false classification is expensive.

### G8. Binary runtime verdict
EXPERT: in the measurement domain, results inside `[limit - U, limit + U]`
are where decision errors live (P25); a third decision is legitimate (P29).
CURRENT: gates pass or fail; observation can refuse (`out_of_scope`).
GAP: none for correctness in the exact domain (the band is about 1e-9 mm
wide). The risk is RL exploitation of the boundary (P30): a policy that
learns to land within a few eps of a limit is gaming numerics, not
engineering.
DECISION: KEEP binary pass/fail for the reward. ADD a diagnostic
`boundary_margin_mm` per predicate and a report count of answers within
`10 x eps` of any active limit. No effect on reward. See EDR-004.

### G9. Frame by declaration
EXPERT: exact geometry makes the datum choice immaterial (P19); invariance
classes (P17).
CURRENT: L along X, W along Y; position free; rotation by 90 swaps L and W
and fails, any other rotation fails the form.
DECISION: KEEP. REFINE the documentation: the declared axes *are* the datum
reference frame, established by declaration, and only `frame_bound`
variables depend on it.

### G10. Symmetric family
EXPERT: symmetric parts have ambiguous datums; several true values (P21).
CURRENT: the same plate family as the paper's example; resolved by the
declared frame. A plate turned 180 degrees measures the same, which is
correct because the family is symmetric under that turn.
DECISION: KEEP. Document. The M1 gate already pins turns of 90, 180 and 270
degrees about Z (`turned_*_degrees_about_Z`); missing is a turn of 1e-10 rad,
inside the form tolerance, with unchanged frame-free values.

### G11. Change detection
EXPERT: thresholds are decision rules (P23).
CURRENT: design note says 1e-6 mm; amendment says it should come from the
scorer; M2a settles it at the dimension slack.
DECISION: REFINE as planned; give it a rule ID under EDR-002.

### G12. Infeasibility and MUS correctness
EXPERT: certify reference results from first principles (P31); finite
precision limits (P32).
CURRENT: Z3 over exact rationals, exhaustive subset enumeration (M2b plan).
GAP: a satisfiable claim is self-certifying (substitute the witness into
`holds`, exactly). An unsatisfiable claim, and therefore every MUS and MCS,
is only as good as the solver run.
DECISION: ADD (EDR-003): every UNSAT and MUS claim carries an independently
checkable certificate (a Farkas certificate for the linear case, one per
branch of the min/max case split), or is checked by a second, independent
method. Plus planted-conflict items whose MUS set is known by construction.

### G13. Test truth source
EXPERT: generate inputs from known answers (P31).
CURRENT: M1 cases are hand-built with known expected outcomes; the M2a gate
is hand-labelled.
DECISION: REFINE as a written rule: an expected value in a test may come from
construction parameters or hand derivation, never from running the evaluator
under test. A lint-style self-test can flag test files that call
`observe`/`measure` to produce expected values.

### G14. Shared measurement between scorer and map
EXPERT: one method (P06) and independent validation (P31) pull in opposite
directions.
CURRENT: "nothing is measured twice": the map reuses scorer 0.5.0's strict
measurement and form verdict.
DECISION: KEEP (it removes a whole class of disagreement), and state the
accepted risk: a bug in `measure` reaches both. The mitigation is G13 plus the
adversarial suite, whose truth is independent of `measure`.

### G15. Probes as a sampling plan
EXPERT: a sampling plan can be blind to a whole error class (P09).
CURRENT: probe schedule -7, +3, +11 mm; sensitivity filter against the
hardcoded witness (V6).
DECISION: REFINE (M3): for each misconception and each hardcoding pattern in
the library, check at compile time that at least one kept probe detects it;
report undetectable pairs instead of assuming coverage.

### G16. Computational aims
EXPERT: a complete statement of what is calculated, separate from the code
(P37); reports with identity and failing cases (P38).
CURRENT: rules are spread across docstrings, the design note and amendments.
DECISION: ADD (EDR-001): `docs/aims/` with one page per evaluator. Start with
the observation map v1 and `holds`.

### G17. Kernel biases
EXPERT: known biases are not noise (P27).
CURRENT: spline bounding-box padding of 2e-7 mm is known and avoided by
refusal.
DECISION: REFINE: list known signed kernel effects in the observation
definition with their treatment (corrected, refused, one-sided).

### G18. Derived-variable sensitivity
EXPERT: hidden tight tolerances (P05); short arcs (P20).
CURRENT: px and py are measured, not recomputed (good); no sensitivity
diagnostic.
DECISION: ADD as a compile-time diagnostic when constraint coefficients
become large (a constraint like `100 * mx - 99 * L >= c` turns 1e-9 mm of
slack into a large relative error). Not needed for today's small integer
coefficients; required before free-form coefficients are allowed.

### G19. One `uncertainty` field
EXPERT: numerical error, model error, measurement uncertainty, specification
looseness and semantic ambiguity are different things with different
treatments (P14, P24, P27, P30).
DECISION: REJECT any single field named `uncertainty`. Use
`numerical_slack_mm`, `robust_margin_mm` and, if the measurement domain ever
arrives, a structured covariance. See the uncertainty skill.

### G20. Prior-dependent grading
EXPERT: risk calculations use the production prior (PK14 §3.3, F06-BAY §2).
DECISION: REJECT for the grader. An RL verdict must depend on the answer and
the item only; using the policy's own output distribution as a prior would
make the reward depend on the policy. Population risk belongs in evaluation
reports, not in a verdict.

### G21. Measurement-domain machinery
DECISION: DEFER fitting operators, datum-feature frames, GD&T zones,
covariance propagation, scan input. PREPARE: the observation definition has
an `operator` and a `domain` field so these can be added without changing
what existing versions mean.

### G22. Misconceptions
EXPERT: decisions under ambiguity are sets or explicit "re-measure" options,
not invented confidences (P29, by analogy).
CURRENT: set-valued "consistent with" labels, separability 0.5 mm, matching
0.05 mm, no confidence.
DECISION: KEEP.

### G23. Minimality metrics
EXPERT: the choice of weights is a business decision (P24).
CURRENT: native units, no weights, never in pass/fail.
DECISION: KEEP.
