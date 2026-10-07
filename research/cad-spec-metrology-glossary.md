# CAD Spec metrology glossary

For each term: **Formal** (standard metrology meaning, with its source; terms
not defined in the corpus are marked "general usage, not from the corpus"),
**cad-spec** (what the word means in this repository), **Difference** (what
must never be confused). Rule: a cad-spec word that collides with a formal
word gets a qualifier in code and docs (`numerical_slack`, not `tolerance`).

## The three "tolerances" (read first)

| Word in the wild | What it is | Owner | Typical value |
|---|---|---|---|
| specification tolerance | permitted variation of a characteristic, from the contract | the designer (contract) | 0.1 mm |
| numerical slack (`eps`) | decision-rule extension covering kernel numerics | the grader (scorer basis) | 1e-9 mm |
| kernel tolerance (OCCT `Precision::Confusion`, edge/vertex tolerance) | geometric gap the kernel treats as coincident | the B-rep data | 1e-7 mm |

Writing "tolerance" alone in new code or docs is not allowed when more than
one of these is in play.

## Terms

**Actual feature.** Formal: the real feature of the workpiece (general GPS
usage, not from the corpus). cad-spec: does not exist separately; the exact
B-rep is both the nominal of the answer and its "actual". Difference: in
cad-spec a model's Rev B is a design, not a manufactured part.

**Nominal feature / nominal form.** Formal: `a -> S(a)` in the design frame
[F92-GTA §2.1]. cad-spec: the contract's intended part (Contract A or B) and,
separately, the geometry the model wrote. Difference: cad-spec has two
nominals (the contract's and the answer's); conformance compares the answer's
observations with the contract.

**Extracted feature / data set X.** Formal: points gathered on the surface by
a measuring system [F92-GTA §2.3]. cad-spec: not used; the B-rep is read
directly. Becomes relevant with meshes or scans.

**Associated feature.** Formal: an ideal feature fitted to extracted data by
a criterion (least squares, minimax, inscribed, circumscribed) [F92-GTA §5;
F89-LSQ]. cad-spec: the kernel's analytic surface (plane, cylinder) read from
the B-rep, plus the axis-aligned bounding box. Difference: in cad-spec the
association is exact and criterion-free for analytic faces; it is undefined
for spline faces (refused).

**Association operator.** Formal: the rule that produces an associated
feature (general GPS usage, ISO 17450 concept, not from the corpus).
cad-spec: the `operator` entry of an observation definition (EDR-001).

**Least-squares (Gaussian) association.** Formal: minimise the sum of squared
orthogonal distances; maximum likelihood for iid isotropic errors
[F06-FIT §2; F89-LSQ §1.2]. cad-spec: not used today.

**Minimum-zone (Chebyshev) association.** Formal: minimise the maximum
absolute distance; defines straightness, flatness, circularity,
cylindricity zones [F92-GTA §5]. cad-spec: not used; the form check is an
exact face-type test, not a zone.

**Datum.** Formal: a reference established from a datum feature to locate
other features (general GD&T usage; datum features fix six degrees of
freedom [FWSO13 §4]). cad-spec: none. The frame is declared: global axes,
L along X, W along Y, plate mid-plane at Z = 0 for scorer R8, origin for R5.

**Datum feature.** Formal: a real feature used to establish a datum
[FWSO13 §4]. cad-spec: none.

**Datum simulator.** Formal: the ideal geometry (physical or computed) that
contacts or is associated with a datum feature (general GD&T usage, not from
the corpus). cad-spec: none.

**Reference frame / frame of reference.** Formal: coordinate system in which
features are expressed; may be set by constraints such as 3-2-1 or by
minimum-trace choice [F18-PSS §4]. cad-spec: the declared global frame.
Difference: cad-spec frames carry no uncertainty because they are declared,
not derived from features.

**Invariance class (cad-spec term, from F18-PSS).** `frame_free`: the value
does not change under rigid motion of the part (distances, diameters, margins
to the part's own faces). `frame_bound`: depends on the declared frame
(positions relative to the origin, mid-plane to Z = 0). Orientation-bound
values (L read along X) are frame_bound with respect to rotation.

**Tolerance interval.** Formal: closed set of permissible values
[PK14 §2.1]. cad-spec: the satisfying set of a contract predicate; closed
because predicates are non-strict (M2a grammar has no strict inequality).

**Tolerance zone.** Formal: a geometric region (between two planes,
cylinders...) where a feature must lie (general GD&T usage). cad-spec: not
used; predicates are on scalar contract variables. Difference: a geometric
zone tolerance is not reducible to scalar predicates without an association
operator.

**Feasible region.** Formal: parameters satisfying all constraints
[F92-GTA §3.5]. cad-spec: the set of contract-variable assignments that
satisfy Contract B (design note §3.4). Same concept, different variables
(contract variables, not fitted element parameters).

**Conformity.** Formal: the true value lies in the tolerance interval
[PK14 §2.1]. cad-spec: the observed contract variables satisfy every Contract
B predicate within the dimension slack, with observation verdict `ok`.

**Conformance zone / acceptance zone.** Formal: region of measured values
leading to acceptance; equals the tolerance interval under simple acceptance,
lies inside it under stringent acceptance [PK14 §2.4; PEP97 Fig. 1].
cad-spec: the tolerance interval extended by `eps` (relaxed acceptance by
numerical slack). Difference: it is wider than the interval, by 1e-9 mm.

**Guard band.** Formal: offset between tolerance limit and gauge limit
[PK14 §2.4]. cad-spec: the 0.01 mm robust margin is a guard band on the
compiler's feasibility decision, not on part acceptance.

**Decision rule.** Formal: rule mapping tolerance, result and uncertainty to
an outcome; includes policies on repeats and outliers [PK14 §2.4]. cad-spec:
gate logic plus slack values; to be given IDs (EDR-002).

**Measurement uncertainty.** Formal: parameter characterising the dispersion
of values reasonably attributed to the measurand (GUM, general usage; used
throughout PEP97, PK14). cad-spec: **does not exist** in the exact domain.
What exists is numerical error of the kernel. Never call `eps` an
uncertainty.

**Coverage interval / expanded uncertainty U.** Formal: interval with stated
coverage probability; U = k u_c [PEP97 §2; PK14 §2.4]. cad-spec: none.

**Bias (systematic error).** Formal: known or estimated systematic offset;
correct it, or treat it asymmetrically [PEP97]. cad-spec: known signed kernel
effects (spline bounding-box padding); refused today.

**Numerical error / numerical slack.** Formal: error of the computation, not
of the measurand [FM12 §2]. cad-spec: `eps` (1e-9 mm) and kernel noise
(about 1e-13 mm observed). The only error kind present in L1 to L5.

**Specification uncertainty / semantic ambiguity.** Formal: ambiguity of the
specification itself (F92-GTA §3.2 shows the mechanism; the term is general
usage). cad-spec: removed by the contract's canonical form; any residual
(for example a prompt sentence that admits two readings) is a template
defect (design note V12), not a numeric error.

**Observation.** Formal: no single standard term; closest is "measurement
result" (general usage). cad-spec: the output of the observation map:
status, reason, values, centre. Difference: an observation with status other
than `ok` carries numbers that must not be evaluated.

**Evidence.** Formal: not defined in the corpus. cad-spec: what a verdict
cites so it can be reproduced: item ID, observation version, scorer basis,
decision-rule IDs, the failing predicate and its margin, the artefact file.

**Predicate.** Formal: not a metrology term. cad-spec: a contract constraint
in normal form, evaluated by `holds`.

**Constraint.** Formal: parameter or form constraint [F92-GTA §2.2].
cad-spec: a contract constraint with a stable ID (C1, C7) or a locked family
rule (F1 to F6).

**MUS / MCS.** Formal (constraint satisfaction, not metrology): minimal
unsatisfiable subset; minimal correction set. cad-spec: as in the design
note glossary.

**must_change (note's "forced").** cad-spec: a variable that cannot keep its
Rev A value. Not a value. Owner's correction, 7 October 2026.

**Witness.** cad-spec: one assignment in the feasible region, chosen by a
deterministic policy. Never the only accepted answer.

**Reference pair.** Formal: reference input data and the corresponding
reference results [TRACIM18 §2.2; FM12 §1]. cad-spec: a built part (or a
contract) with independently known expected observations or verdicts.

**Numerical artefact.** Formal: synthetic reference data built to test
software [FM12]. cad-spec: hand-built CadQuery parts and contracts in the
gate suites; planned planted-conflict items.

**Computational aim.** Formal: complete, unambiguous statement of what is
calculated, independent of how [TRACIM18 §2.1]. cad-spec: to be written per
evaluator (EDR-001).

**Traceability.** Formal: result related to a reference through a documented
unbroken chain of calibrations, each contributing to the uncertainty (VIM, as
quoted in PK14 §3.2.2). cad-spec: version pinning (scorer basis, observation
version, expression version) plus registered records. Difference: not a
calibration chain; and like formal traceability it does not bound decision
risk [PK14 §3.2.2].

**Measurement capability index C_m.** Formal: `(T_U - T_L) / 2U` [PK14 §2.4].
cad-spec: for 0.1 mm tolerances and 1e-9 mm slack, C_m is of order 1e7; this
is why binary grading is defensible in the exact domain.

**Out of scope.** cad-spec: the observation map refuses because a variable
would be a guess. Formal analogue: an ill-posed or undefined measurand
[PK14 §2.1].

**Indeterminate (cad-spec proposal).** A verdict that neither PASS nor FAIL
is justified. Formal analogue: the re-measure decision [F06-BAY §2.1]. Not a
runtime grader verdict in L5 v1 (EDR-004).

**Infeasible.** cad-spec: Contract B has an empty region, robustly (0.01 mm).
Different from FAIL: the expected answer is a structured reject.
