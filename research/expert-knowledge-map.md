# CAD Spec metrology knowledge map

Two parts. Part 1 is the **principle registry**: every principle extracted
from the corpus, with its provenance layers and relevance. Skills and
decision records cite these IDs. Part 2 is the **knowledge graph**: 20
areas, what each requires before it may be used, and which principles live
there.

Labels: AS author states, AI author implies, OI our interpretation, APP
proposed application (see [`expert-corpus-index.md`](expert-corpus-index.md)).
Relevance `cur/near/long` and impact `arch/impl/test/prod` are 0 to 5.

## Part 1. Principle registry

### Specification semantics

**P01. A tolerance written in words is not yet a test.**
AS: one natural-language tolerance (circle radius 50 +/- 0.05 with
circularity 0.02) admits two formalisations that define different assessment
problems; formal parameter and form constraints remove the ambiguity and
allow automatic generation of assessment software. [F92-GTA §3.2, p.6-7; high]
OI: the ambiguity is semantic, not numerical; no amount of precision fixes it.
APP: every cad-spec requirement has exactly one canonical formal text and one
evaluator (M2a's normal form and `holds` already do this).
Relevance 5/5/4. Impact 5/3/3/4. USE NOW.

**P02. Conformance is the existence of a feasible point.**
AS: tolerance assessment = find parameters a with `C(a) >= 0` and
`F(X; a) >= 0`; the constraints split parameter space into feasible and
infeasible regions. [F92-GTA §2.4 p.4, §3.5 p.10; high]
OI: L5's "Rev B in the feasible region of Contract B" is this formulation
applied to contract variables.
APP: keep the region semantics; never degrade to "matches one reference".
Relevance 5/5/5. Impact 5/2/3/4. USE NOW.

**P03. Report how far inside, not only inside or outside.**
AS: `max s` subject to `C(a) >= s`, `F(X; a) >= s`; `s* >= 0` conforms, its
size measures how well; a normalised version gives `s = 1` for a perfect
part. [F92-GTA §2.5, p.4-5; high]
APP: per-predicate signed margin as a diagnostic (no pass/fail effect);
robust-feasibility margin in the compiler (M2a's 0.01 mm) is the same idea
on the specification side. Relevance 4/4/4. Impact 3/2/3/3. USE NOW (diagnostic).

**P04. Check the specification before checking the part.**
AS: confirm constraints are consistent by evaluating them at the ideal
parameters over a representative point set; probe how far parameters may
stray (over- and under-tolerancing), at the design stage. [F92-GTA §3.1, p.5-6; high]
APP: compile-time checks V1 (Rev A passes Contract A), V9/V10 (infeasibility
and near-twin slack) are this. Add: report each item's slack per constraint.
Relevance 5/5/3. Impact 4/2/4/3. USE NOW.

**P05. One tolerance can imply a much tighter hidden one.**
AS: a circle through (0, +/-5) with radius tolerance +/-0.1 mm crosses the
x-axis within about +/-0.1 micrometre. [F92-GTA §3.1, p.6; high, with the
"±1mm" wording inconsistency recorded in the corpus index]
OI: derived variables (px = L - 2 mx) amplify or cancel errors; sensitivity
must be checked, not assumed.
APP: the compiler records, per item, the sensitivity of each derived variable
to the measured ones; flag items where a derived predicate's slack is below
`k x` the propagated numerical error. Relevance 3/3/4. Impact 3/2/3/2. PREPARE.

**P06. Two approximations, two verdicts, one dispute.**
AS: supplier and customer may disagree only because they use different
approximations to the assessment problem; the method should be agreed early.
[F92-GTA §8, p.19; high]
APP: the compiler and the grader share one meaning (`holds`); this principle
is the expert reason that M2a design is right. Relevance 5/5/5. Impact 5/3/4/4. USE NOW.

**P07. Per-feature decomposition is approximate and can be ill-posed.**
AS: decomposing a multi-component problem per feature is cheaper and gives
per-feature diagnostics, but the result is approximate; a subproblem can be
ill-posed (two holes, three points each) while the coupled problem is
well-posed; degenerate solutions leave some parameters undefined.
[F92-GTA §4, p.10-13, Fig. 3-4; high]
APP: never grade a coupled Contract B constraint per feature in isolation;
coupling depth is a property of the constraint graph (design note §8.2).
Relevance 4/4/4. Impact 4/3/3/2. USE NOW.

**P44. Hard gauges decide; software assessment talks about data.**
AS: a hard gauge gives an unambiguous answer but is inflexible; software
assessment is flexible but, without more information, only makes statements
about the data set X. [F92-GTA §1, p.1; high]
OI: for exact B-rep the "data" is the part definition itself, so the gap
between X and the part closes; it reopens with tessellation or scanning.
Relevance 2/2/5. Impact 3/1/1/3. PREPARE.

### Observation, association, fitting

**P10. A measured feature is the output of an operator, not a property.**
AI: every fitted element depends on the fit criterion (LS, Chebyshev,
inscribed, circumscribed), on the sampling and on the frame.
[F92-GTA §5 p.13-14; F06-FIT §2, §2.7; F89-LSQ §1.2; medium as a synthesis]
APP: each contract variable has a static observation definition: operator,
reference frame, invariance class, domain, numerical error bound, refusal
rules. Stored once per observation version, not per instance.
Relevance 5/5/5. Impact 5/2/3/3. USE NOW (as a document).

**P11. Parametrise for stability.**
AS: translate data to the centroid; direction `(a, b, 1)` is stable only for
near-vertical axes; transform the trial element to standard position each
iteration; do not use the `tan 2 theta` line formula (loss of accuracy); do
not depend on a sign convention for normals. [F89-LSQ element-fitting introduction (centroid), §3.4 notes 1-2, §8 Rules 1-2, printed p.11-16; medium, OCR]
APP: any future fit or axis comparison code; tests near degenerate
directions. Relevance 1/1/5. Impact 1/4/3/1. DEFER.

**P12. Iterative fits need good starts and representative data.**
AS: Gauss-Newton converges fast only with good starting values and
representative data; partial arcs give slow convergence, divergence or a
rank-deficient Jacobian; use at least twice the minimum point count, well
distributed. [F89-LSQ §2.2 and element-fitting introduction; medium, OCR]
APP: a future fitting operator must return a refusal when J is rank deficient
or the arc coverage is below a stated limit. Relevance 1/1/5. Impact 2/4/3/1. DEFER.

**P13. Linearised models are starts and bounds, not verdicts.**
AS: the linear least-squares circle agrees closely with the nonlinear fit for
accurate data and gives starting values otherwise; the linearised minimum-zone
circle gives an upper bound. [F89-LSQ §6.4; F92-GTA §8, p.18-19; high]
APP: never let an approximate operator issue an official verdict without a
proven bound. Relevance 2/2/4. Impact 2/3/2/2. USE NOW (as a rule).

**P14. Least squares assumes iid isotropic errors.**
AS: ODR is maximum likelihood only for independent, identically distributed,
isotropic errors; real systems are correlated and anisotropic; assuming the
identity matrix can make parameter uncertainties optimistic by a factor of
two to nearly four. [F06-FIT §2, §3.7 Table 1, §4 point 6; high]
APP: the scan/mesh module, if built, takes a structured covariance or states
the isotropy assumption in its output. Relevance 0/1/5. Impact 3/3/3/2. DEFER.

**P15. Uncertainty of fitted parameters comes from a sensitivity matrix.**
AS: `U_b = K U_d K^T` with `K = (J^T J)^-1 J^T` for any LS fit; the variance
decomposes into form, systematic and random parts.
[F06-FIT §2.2 eq. 4-5; FWSO13 §3; high] Relevance 0/1/5. Impact 2/3/2/1. DEFER.

**P16. Minimax is a different, harder problem.**
AS: Chebyshev (minimum zone) fitting is a constrained problem with several
nearby local minima, degeneracy, vertex and non-vertex solutions; data can
have of order m global minima; least squares overestimates the zone.
[F92-GTA §5 p.13-14, §8 p.18; FM12 §2 p.145-146, §5 p.148; F06-FIT §2.7; high]
APP: future GD&T form evaluation (flatness, cylindricity) must not be
implemented as an LS fit plus max residual, and must state its global-optimum
guarantee or refuse. Relevance 0/1/5. Impact 4/4/4/3. DEFER, flag hazard.

**P40. Realistic deviations are spatially correlated.**
AS: form error modelled by a Gaussian-process kernel
`sigma^2 exp(-|s - s'|^2 / 2 lambda^2)` is smoother and more realistic than iid.
[FWSO13 §2; FM12 §4.5, Fig. 4; high]
APP: synthetic perturbed geometry for future scan tests. Relevance 0/1/4.
Impact 1/2/4/1. DEFER.

**P41. Probe radius changes the fitting problem.**
AS: for ODR, a constant subtraction; for generalised distances, an offset
surface whose derivatives involve the normal. [F06-FIT §2.6, §3.4; high]
Relevance 0/0/3. Impact 1/2/2/1. NOT RELEVANT now.

### Frames, datums, invariance

**P17. Position, size and shape are separable.**
AS: a point-cloud variance matrix decomposes into position (6), size (1) and
shape (3m - 7) components that keep the trace; distances carry no position
component; angles depend on shape only. [F18-PSS §2-3.5, p.1-3; high]
APP: tag each contract variable with an invariance class:
`frame_free` (L, W, T, D, px, py, mx, my measured to own faces),
`frame_bound` (scorer R5 to the origin, R8 to Z = 0). Only `frame_bound`
needs a datum. Relevance 3/3/5. Impact 4/1/2/2. USE NOW (as documentation).

**P18. How the frame is fixed changes the uncertainty of everything in it.**
AS: frame constraints `C^T x = c0` redistribute variance; `C = G` minimises
the trace; a 3-2-1 ball-plate frame is one choice among many.
[F18-PSS §4, p.3-4; FWSO13 §4, Table 1; high]
APP: every frame records how it was established. Relevance 2/2/5. Impact 4/2/2/2. PREPARE.

**P19. With exact geometry the datum choice does not matter; with form error it does.**
AS: for ideal geometry and an ideal measuring system, results do not depend
on which six points define the frame; with form error, different datum
strategies give different frames and positions. [FWSO13 §1 p.1, §4 p.3; high]
OI: this is the formal licence for L5 v1 fixing the frame by declaration on
exact B-rep, and the formal warning for any meshed or scanned input.
Relevance 3/3/5. Impact 4/1/2/2. USE NOW (as stated assumption).

**P20. Short arcs and small patches are ill-conditioned.**
AS: a scallop (small arc) has large x and radius uncertainty; partial arcs
slow or break fits; partial-arc tolerancing implies tight hidden tolerances.
[FWSO13 §4.1 Table 3; F89-LSQ §2.2; F92-GTA §3.1; high]
APP: future feature types that are partial (fillet arcs, slots) need a
conditioning check before a variable is reported. Relevance 1/2/5. Impact 2/3/3/1. PREPARE.

**P21. The measurand must be well defined; symmetry breaks it.**
AS: if the measurand is not well defined it has several true values; a
symmetric square plate with a central bore cannot tell which face is datum A;
any assignment that conforms makes the part conforming; better practice is a
symmetry-breaking feature. [PK14 §2.1, p.238; high]
OI: the cad-spec plate is in this class. cad-spec resolves it by declaring
axes in the prompt (L along X, W along Y), which makes the measurand well
defined by convention, not by the part.
APP: state that convention as part of each observation definition; if a
future family uses datum features instead of global axes, enumerate the
symmetric frames and decide explicitly between "any frame conforms" and
"symmetry-breaking feature required". Relevance 4/4/5. Impact 4/2/3/3. USE NOW.

**P42. Frame uncertainty propagates to every derived feature.**
AS: `X = G + K H` propagates uncertainty through the datum alignment; the
six constrained parameters get zero uncertainty, the others absorb it.
[FWSO13 §4, Table 1; high] Relevance 0/1/5. Impact 2/2/2/1. DEFER.

**P43. Compare datum strategies by their effect on evaluated features.**
AS: [FWSO13 §5; high]. APP: when datums arrive, a test compares two datum
strategies on the same exact part (must agree) and on a perturbed part (may
differ; the difference is reported). Relevance 0/1/4. Impact 2/1/3/2. DEFER.

**P08. With a fixed template, only the frame is unknown.**
AS: template matching optimises only the transformation parameters however
complex the shape; fixed CAD shape fits need only points and normals.
[F92-GTA §6, p.15-16; FM12 §4.2, p.146; high]
APP: future "Rev B mesh against Rev B CAD" or scan comparison.
Relevance 0/1/5. Impact 3/2/3/3. DEFER.

**P09. The sampling plan decides what can be seen.**
AS: m uniformly spaced points detect at least `cos(pi/2m)` of q-lobing when
m and q share no factor; six points can miss three-lobing entirely; even
counts are not recommended. [F92-GTA §3.3, p.7-8, Table 1, Fig. 1-2; high]
OI: L5's intent probes are a sampling plan over the design space; a probe
schedule can be blind to a class of hardcoding exactly as six points are
blind to three lobes.
APP: for each misconception and hardcoding pattern, a compile-time check that
some kept probe detects it (V6 does this for the hardcoded witness only).
Relevance 3/5/5. Impact 3/2/5/3. USE NOW (M3).

### Uncertainty, bias, error kinds

**P27. A known bias is not noise.**
AS: do not add an uncorrected bias in quadrature; RSS with `u_c` overstates,
RSS with U understates (below 80% achieved for nominal 95% at
`delta/u_c = 2`); use asymmetric `U+ = max(k u_c - delta, 0)`,
`U- = max(k u_c + delta, 0)`; prefer correcting.
[PEP97 §2-3, p.579-582, Fig. 4; high]
APP: kernel effects with a known sign (bounding-box padding, chordal
tessellation error on convex faces) are corrected, refused, or applied
one-sided; never folded into the symmetric slack. Relevance 2/2/4. Impact 2/2/2/1. PREPARE.

**P28. A bias can be carried by the guard band.**
AS: `G_L = T_L + x% U + delta`, `G_U = T_U - x% U + delta` gives the same
risk as the x% stringent rule on corrected results. [PK14 §2.4, p.240; high]
Relevance 1/1/3. Impact 1/1/1/1. DEFER.

**P30. Systematic error does not average out.**
AS: with the same total uncertainty, a larger systematic share leaves the
expected decision cost unchanged but widens its spread; any subset of
results can be all wrong together. [F06-BAY §3, Table 2, Fig. 3-6; high]
OI: an RL grader is one fixed instrument: every grader bias is systematic
for the policy, which can discover and exploit it; random grader noise would
not be exploitable in the same way.
APP: weigh grader false passes far above false rejections; keep the
"soundness over coverage" rule; audit boundary cases specifically.
Relevance 4/4/4. Impact 4/2/4/4. USE NOW.

### Conformity and decisions

**P22. Conforming is not functional.**
AS: conformity concerns the true value against the tolerance interval;
functionality is different; a nonconforming part may work.
[PK14 §2.3, p.239; high]
APP: cad-spec grades conformance to a written contract; inherited intent
(G5) is behaviour inheritance, not function. Say so in reports.
Relevance 3/3/4. Impact 2/0/0/4. USE NOW (wording).

**P23. Every acceptance is a decision rule, and it is stated.**
AS: a decision rule maps tolerance, result and uncertainty to an outcome;
simple acceptance (acceptance zone = tolerance interval), stringent (guard
band inside), relaxed, multi-outcome; the statement includes the guard band
as % of U and policies on repeats and outliers. [PK14 §2.4, p.239-240; high]
APP: name the grader's rules: dimensions are accepted under a relaxed rule by
numerical slack (+1e-9 mm, scorer 0.5.0); form under +1e-7 mm; feasibility
under a stringent rule (robust margin 0.01 mm). Record rule IDs in items and
verdicts (EDR-002). Relevance 4/4/5. Impact 4/2/3/4. USE NOW.

**P24. Uncertainty is technical, the rule is a business choice.**
AS: [PK14 abstract, §3.4, p.241]. APP: keep numerical error bounds (technical,
from the kernel) separate from acceptance policy (a decision, owned by Bilal).
Relevance 3/3/4. Impact 3/1/1/3. USE NOW.

**P25. Inside the tolerance is not proof of conformity.**
AS: four outcomes (valid and false acceptance, valid and false rejection);
measurement uncertainty causes decision errors. [PK14 §2.2, Table 1, p.238-239; high]
OI: in the exact domain the "uncertainty" is numerical and tiny, so the
contingency collapses to near-certainty except within a few eps of a limit.
Relevance 3/3/5. Impact 3/1/3/3. USE NOW.

**P26. Traceability does not bound risk.**
AS: a traceable result with a large uncertainty and one with a small one
both satisfy traceability. [PK14 §3.2.2, p.240-241; high]
OI: passing a verification suite (TraCIM style) shows the code is right on
the suite, not that every verdict is right. Relevance 2/3/4. Impact 1/0/2/3. USE NOW (wording).

**P29. More than two decisions; asymmetric costs move the limits.**
AS: decisions may include re-measure; the optimal rule minimises expected
cost from a cost matrix; asymmetric costs make the acceptance interval
asymmetric. [F06-BAY §2.1, Table 1, Fig. 1-2, p.809-811; high]
OI: INDETERMINATE (or "re-measure with a better instrument") is a formal
decision, not a failure to decide. APP: keep the compile-time three-way
outcome (feasible, infeasible, discard and regenerate). For runtime, see EDR-004.
Relevance 3/3/5. Impact 4/1/2/3. PREPARE.

### Validation and traceability of software

**P31. Generate the question from the answer.**
AS: reference pairs are better built by choosing the solution and generating
inputs (an inverse problem) than by running reference software, which is
expensive and itself unverified; correctness can then be checked from first
principles. [FM12 §1, p.145; high]
APP: test truth comes from construction inputs, never from the code under
test; planted-conflict items for MUS/MCS (EDR-003, EDR-005).
Relevance 5/5/5. Impact 4/3/5/3. USE NOW.

**P32. Bug-free software still is not exact.**
AS: approximations, convergence tolerances, local optima and finite precision
all prevent exact answers; an exact reference pair cannot be represented in
finite precision. [FM12 §2, p.145-146; high]
APP: every numeric test states its accuracy measure and tolerance; exact
rationals where the problem allows (M2a). Relevance 4/4/4. Impact 2/3/5/1. USE NOW.

**P33. Measure accuracy forward, backward or both.**
AS: forward `D_F` (distance to the true answer), backward `D_I` (input change
that makes the output exact), hybrid `D_H`. [FM12 §3, p.146; high]
APP: for geometric observations, a backward measure ("this answer is exact
for a part within 1e-9 mm of the given one") is often the honest statement.
Relevance 2/2/4. Impact 1/1/4/1. PREPARE.

**P34. Null-space generation gives many data sets with one answer.**
AS: perturbing exact points along normals by `e` with `J^T e = 0` keeps the
LS solution; projection customises form, systematic or correlated errors;
all such sets share the fit and the residual sum. [FM12 §4.1-4.5, Fig. 1-4; high]
OI: the contract analogue is sampling many Rev B witnesses across the
feasible region to prove the grader accepts the region (owner's mandatory
example 1 for M2b). Relevance 3/4/5. Impact 2/2/5/2. USE NOW (by analogy).

**P35. Fixed-shape fit data need only points and normals.**
AS: [FM12 §4.2, p.146; high]. Relevance 0/1/4. Impact 1/2/3/1. DEFER.

**P36. Minimax reference data are only partly solved.**
AS: Chebyshev vertex solutions can be generated by KKT partitions; global
optimality is not guaranteed; non-vertex generation needs research.
[FM12 §5-6, p.148-149; high] Relevance 0/1/4. Impact 1/1/4/1. RESEARCH FURTHER.

**P37. Specify the computational aim apart from the code.**
AS: a computational aim gives a complete, unambiguous statement of what is
calculated (mathematical model, inputs, outputs), not how; it informs both
developer and tester. [TRACIM18 §2.1, p.4; high]
APP: one computational-aim document per evaluator (EDR-001).
Relevance 4/5/5. Impact 4/1/4/3. USE NOW.

**P38. A verification report names the software and every failing case.**
AS: results carry software identity and per-output tolerances; the report
gives overall PASS/FAIL, the tolerances, the date, a process key, and lists
the failing reference data sets. [TRACIM18 §3.8 p.9, §4.3-4.4 p.10-11; high]
APP: gate reports list artefact IDs and evaluator versions (largely done in
`results/l5/`). Relevance 3/4/4. Impact 1/1/4/3. USE NOW.

**P39. NMIs single out which calculations need verification.**
AS: [TRACIM-DB rows 21-22, 33-44, 60-79; high]
APP: inventory for GD&T-era evaluators. Relevance 0/1/4. Impact 1/0/2/2. RESEARCH FURTHER.

## Part 2. Knowledge graph

`A requires B` means A must not be used, implemented or graded until B is
settled for the case at hand. Areas, their principles, and their status in
cad-spec today.

| # | Area | Principles | cad-spec status |
|---|---|---|---|
| 1 | Specification semantics | P01 P02 P04 P05 P06 P07 | strong (contract IR, `holds`) |
| 2 | Geometric representation | P10 P44 | exact analytic B-rep only |
| 3 | Feature association | P10 P13 | implicit (bounding box, kernel cylinder) |
| 4 | Geometric fitting | P11 P12 P13 P14 P16 | not used (exact domain) |
| 5 | Datum systems | P19 P21 P43 | none (frame by declaration) |
| 6 | Reference frames | P17 P18 P19 P21 | global axes, position free, orientation bound |
| 7 | GD&T semantics | P16 P39 | out of scope |
| 8 | Tolerance zones | P02 P03 P05 | contract predicates; no geometric zones |
| 9 | Observation semantics | P10 P17 P25 | observation map v1, four verdicts |
| 10 | Measurement uncertainty | P14 P15 P27 P30 | numerical slack only |
| 11 | Conformity assessment | P22 P23 P25 P26 | strict gates |
| 12 | Decision rules | P23 P24 P28 P29 | implicit; to be named |
| 13 | Numerical optimisation | P11 P12 P16 P36 | exact rationals, exhaustive subsets (M2b) |
| 14 | Validation and traceability | P31 P32 P33 P37 P38 | hand-labelled gates, external audits |
| 15 | Numerical artefacts | P31 P34 P35 P36 P40 | adversarial suite (M1) |
| 16 | Synthetic test design | P09 P31 P34 | generator, probes (M3/M4) |
| 17 | Failure modes | all | `cad-spec-metrology-failure-patterns.md` |
| 18 | Out-of-scope conditions | P10 P12 P20 P21 | `out_of_scope` verdict |
| 19 | Physical measurement | P14 P15 P27 P28 P41 P42 | none |
| 20 | Point-cloud reasoning | P08 P14 P17 P18 P34 P40 | none |

### Dependency graph

```text
CONFORMITY VERDICT (any requirement)
  requires  specification semantics (1)        formal predicate, one meaning
  requires  observation semantics (9)          what each variable is
  requires  decision rule (12)                 named, with its slack or guard band
  requires  error taxonomy (10)                which error kind the slack covers

OBSERVATION of a variable (9)
  requires  geometric representation (2)       exact B-rep, mesh, or points
  requires  feature association (3)            operator that turns geometry into a value
  requires  reference frame (6)                only if the variable is frame_bound (P17)
  requires  scope rules (18)                   when to refuse instead of guess

FEATURE ASSOCIATION on measured or meshed data (3)
  requires  geometric fitting (4)              criterion: LS, minimax, inscribed, circumscribed
  requires  sampling adequacy (16, P09 P12)
  requires  conditioning check (P20)

REFERENCE FRAME from datum features (6)
  requires  datum systems (5)                  which features, which order
  requires  feature association (3)            datum simulators are fitted features
  requires  measurand well defined (P21)       symmetry handling

POSITION TOLERANCE (7, future)
  requires  datum system (5)
  requires  feature association (3)
  requires  nominal geometry (2)
  requires  tolerance-zone definition (8)
  requires  minimax-capable optimisation (13, P16)

FEASIBILITY / INFEASIBILITY claim (1, 13)
  requires  exact arithmetic (P32)
  requires  certificate or independent check (P31; EDR-003)
  requires  robust margin against measurement slack (P03, P23)

MEASUREMENT UNCERTAINTY (10, future)
  requires  physical measurement domain (19)
  requires  instrument model with systematic and random parts (P15 P30)
  requires  bias treatment (P27)

ANY EVALUATOR TRUSTED IN A VERDICT (14)
  requires  computational aim (P37)
  requires  reference pairs independent of the evaluator (P31 P34)
  requires  stated accuracy measure and tolerance (P32 P33)
```

### Domain boundary (mandatory distinction)

```text
EXACT / NOMINAL CAD DOMAIN              PHYSICAL MEASUREMENT DOMAIN
(L1 to L5 today)                        (not in cad-spec)
- part is its own definition            - part known only through data X (P44)
- association = read analytic surface   - association = fit by a criterion (P10, P16)
- error = kernel numerics (1e-13 mm      - error = instrument model + form + sampling
  noise, 1e-7 mm geometric tolerance)     (P14, P15, P30)
- frame by declaration is exact (P19)   - frame from datums carries uncertainty (P18, P42)
- verdict near-binary away from eps      - verdict needs a risk-aware rule (P23, P29)
```

A mesh or a faceted STEP sits between the two: no physical measurement
uncertainty, but association and frame questions return. It is out of scope
until a skill explicitly covers it.
