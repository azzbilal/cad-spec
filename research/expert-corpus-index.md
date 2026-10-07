# Expert corpus index and reasoning extractions

Status: research record, 7 October 2026. Not a design decision. Nothing here
reopens the L5 architecture (`docs/design/L5-region-graded-change-orders-v1.0.md`);
proposals that touch the code are collected in
[`cad-spec-architecture-review.md`](cad-spec-architecture-review.md) and
[`expert-decisions.md`](expert-decisions.md), for the owner's approval.

## How to read this folder

| File | Holds |
|---|---|
| this file | the eleven documents, their source keys, and one Expert Reasoning Extraction per document |
| [`expert-knowledge-map.md`](expert-knowledge-map.md) | the principle registry (P01 to P44, the single source every skill cites) and the dependency graph over 20 knowledge areas |
| [`cad-spec-gap-analysis.md`](cad-spec-gap-analysis.md) | expert model against current cad-spec, KEEP / REFINE / REPLACE / ADD / DEFER / REJECT |
| [`cad-spec-metrology-glossary.md`](cad-spec-metrology-glossary.md) | formal metrology meaning, cad-spec meaning, and where they differ |
| [`cad-spec-metrology-failure-patterns.md`](cad-spec-metrology-failure-patterns.md) | failure patterns with symptom, cause, detection, mitigation, required test |
| [`expert-decisions.md`](expert-decisions.md) | Expert Decision Records (EDR), all PROPOSED |
| [`cad-spec-research-priority.md`](cad-spec-research-priority.md) | top findings, open questions, risks |
| [`cad-spec-architecture-review.md`](cad-spec-architecture-review.md) | current architecture, expert knowledge, gaps, proposed changes by urgency |
| `.claude/skills/cad-spec-*/SKILL.md` | the operational skills (Claude Code project skills, the repository's native agent format) |

## Provenance discipline

Every claim carries one of four labels. They are never mixed in one sentence.

| Label | Meaning |
|---|---|
| **AS** (author states) | the document says it, in substance, at the cited place |
| **AI** (author implies) | follows directly from what the document shows, but is not written |
| **OI** (our interpretation) | our reading or generalisation; may be wrong |
| **APP** (proposed application) | what we propose for cad-spec; needs the owner's approval |

Citation form: `[KEY, section, printed page (PDF page), equation or figure; confidence]`.
Confidence is `high` (checked against the text), `medium` (paraphrase of a
long argument or OCR text), `low` (inferred from a figure or a damaged scan).
The full YAML provenance block for each document is given once below; claims
then cite the key.

## Source keys

```yaml
- key: PEP97
  author: Phillips, S.D.; Eberhardt, K.R.; Parry, B.
  title: Guidelines for Expressing the Uncertainty of Measurement Results Containing Uncorrected Bias
  venue: J. Res. Natl. Inst. Stand. Technol. 102(5), 577-585 (1997)
  pages: printed 577-585 = PDF 1-9
  file: Measurement_Uncertainty_and_Uncorrected_Bias.pdf
- key: PK14
  author: Phillips, S.D.; Krystek, M.
  title: Assessment of conformity, decision rules and risk analysis
  venue: tm Technisches Messen 81(5), 237-245 (2014)
  pages: printed 237-245 = PDF 1-9
  file: Phillips___Krystek___Assessment_of_Conformity__Decision_Rules_and_Risk_Analysis.pdf
- key: F06-BAY
  author: Forbes, A.B. (NPL)
  title: Measurement uncertainty and optimized conformance assessment
  venue: Measurement 39, 808-814 (2006)
  pages: printed 808-814 = PDF 1-7
  file: Forbes___Measurement_Uncertainty_and_Optimised_Conformance_Assessment.pdf
- key: F06-FIT
  author: Forbes, A.B. (NPL)
  title: Uncertainty evaluation associated with fitting geometric surfaces to coordinate data
  venue: Metrologia 43, S282-S290 (2006)
  pages: printed S282-S290 = PDF 2-10 (PDF 1 is a publisher cover)
  file: Forbes___Uncertainty_Evaluation_Associated_with_Fitting_Geometric_Surfaces_to_Coordinate_Data.pdf
- key: F18-PSS
  author: Forbes, A.B. (NPL)
  title: Uncertainties associated with position, size and shape for point cloud data
  venue: J. Phys.: Conf. Ser. 1065, 142023 (IMEKO XXII, 2018)
  pages: printed 1-4 = PDF 2-5 (PDF 1 is a publisher cover)
  file: Forbes___Uncertainties_Associated_with_Position__Size_and_Shape_for_Point_Cloud_Data.pdf
- key: FWSO13
  author: Forbes, A.B.; Wilson, A.; Saunders, P.; Orchard, N. (NPL, Rolls-Royce)
  title: Effect of form errors in datum features on evaluated geometries
  venue: 16th International Congress of Metrology, paper 08003 (2013)
  pages: 08003-p.1 to p.5 = PDF 1-5
  file: Forbes_et_al____Effect_of_Form_Errors_in_Datum_Features_on_Evaluated_Geometries.pdf
- key: FM12
  author: Forbes, A.B.; Minh, H.D. (NPL)
  title: Generation of numerical artefacts for geometric form and tolerance assessment
  venue: Int. J. Metrol. Qual. Eng. 3, 145-150 (2012)
  pages: printed 145-150 = PDF 1-6
  file: Forbes___Minh___Generation_of_Numerical_Artefacts_for_Geometric_Form_and_Tolerance_Assessment.pdf
- key: F92-GTA
  author: Forbes, A.B. (NPL)
  title: Geometric Tolerance Assessment
  venue: NPL Report DITC 210/92 (edition dated September 1999)
  pages: printed 1-22; PDF page = printed + 4 (title, abstract, copyright, contents precede)
  file: Forbes___Geometric_Tolerance_Assessment.pdf
- key: F89-LSQ
  author: Forbes, A.B. (NPL)
  title: Least-squares best-fit geometric elements
  venue: NPL Report DITC 140/89, revised edition February 1991
  pages: 40 PDF pages, scanned; read through OCR, so page mapping and formulas are medium confidence
  file: Forbes___Least-Squares_Best-Fit_Geometric_Elements.pdf
- key: TRACIM18
  author: Smith, I. (NPL)
  title: Guidance on the use of the TraCIM system at NPL ... using standalone TraCIM clients, v1.0
  venue: EMPIR 15SIP06 ValTraC Deliverable 1 (January 2018)
  pages: printed 1-12 = PDF 1-12
  file: TraCIM___Traceability_for_Computationally-Intensive_Metrology.pdf
- key: TRACIM-DB
  author: Zeleny, V.; Linkeova, I. (eds., Czech Metrology Institute)
  title: NEW06 TraCIM database of applications (79 computational aims, 7 domains)
  venue: EMRP JRP NEW06 working table (undated, 2012-2015 project)
  pages: 6 PDF pages, rows 1-79
  file: TraCIM_-_Database_of_applications.pdf
```

## Relevance summary

Scores 0 to 5. `cur` = current milestone (L5 M2a/M2b, exact nominal B-rep),
`near` = L5 M3 to M5, `long` = L6 families, GD&T, scans. Impact columns:
architecture, implementation, testing, product.

| Key | cur | near | long | arch | impl | test | prod | Class |
|---|---|---|---|---|---|---|---|---|
| F92-GTA | 5 | 5 | 4 | 5 | 3 | 3 | 4 | USE NOW |
| FM12 | 4 | 5 | 5 | 3 | 2 | 5 | 3 | USE NOW |
| PK14 | 3 | 4 | 5 | 4 | 2 | 2 | 5 | USE NOW (terminology), PREPARE (risk) |
| TRACIM18 | 3 | 4 | 4 | 3 | 2 | 5 | 4 | USE NOW (computational aims) |
| F18-PSS | 3 | 3 | 5 | 4 | 1 | 2 | 2 | PREPARE ARCHITECTURE FOR |
| F06-BAY | 2 | 3 | 4 | 3 | 1 | 1 | 4 | PREPARE ARCHITECTURE FOR |
| PEP97 | 2 | 2 | 4 | 2 | 2 | 2 | 2 | PREPARE (kernel biases), DEFER (expanded U) |
| FWSO13 | 1 | 2 | 5 | 3 | 1 | 2 | 3 | DEFER |
| F06-FIT | 1 | 1 | 5 | 3 | 1 | 2 | 2 | DEFER |
| F89-LSQ | 1 | 1 | 5 | 1 | 4 | 3 | 1 | DEFER |
| TRACIM-DB | 1 | 2 | 4 | 1 | 1 | 2 | 3 | RESEARCH FURTHER (evaluator inventory) |

---

## E1. F92-GTA: Geometric Tolerance Assessment

**A. Core problem.** Turn a design-plus-tolerance specification into a
computable test of whether measured points of a part conform, and say how far
inside or outside it is. [F92-GTA, §1-2, p.1-5; high]

**B. Formal objects.** Nominal form `a -> S(a)` as a union of parametrized
elements in one design frame; parameter tolerances `C(a) >= 0` (no data);
form tolerances `F(X; a) >= 0` (involve data X); data set X in the measuring
system's own frame; feasible region in parameter space; transformation
parameters t for template matching; separating surface for part mating.
[§2.1-2.4, p.2-4; §6, p.15; §7, p.16; high]

**C. Operators.**

```yaml
- operator: assess (feasibility)
  inputs: [S(a), C, F, X]
  outputs: [feasible a or none]
  preconditions: [constraints consistent at the ideal a0, X representative]
  failure_conditions: [empty feasible region, ill-posed subproblem, degenerate optimum]
  numerical_issues: [nonlinear constraints, local optima, degeneracy]
- operator: degree_of_conformance (max s)
  inputs: [same]
  outputs: [a*, s*]   # s* >= 0 means conforming; normalised form gives s = 1 for a perfect part
  numerical_issues: [general SQP may be too slow for real time]
- operator: decompose
  inputs: [multi-component problem]
  outputs: [per-feature subproblems + check of the parameter constraints]
  failure_conditions: [approximate; subproblem ill-posed though whole well-posed]
- operator: template_match
  inputs: [fixed template S(a0), X]
  outputs: [frame parameters t, s]
- operator: approximate (linearise, least squares for minimax)
  outputs: [starting point or bound, never the official verdict]
```

**D. Decision logic.** Specification (nominal + parameter + form constraints)
then data X, then frame alignment, then the optimisation `max s`; `s >= 0`
means a feasible point exists, so the part (as represented by X) conforms;
the size of `s*` informs process control. To show nonconformity, the original
(not an approximate) problem must be solved. [§2.5, p.4-5; §3.5, p.10; §8, p.18; high]

**E. Hidden assumptions.** X lies on the surface modulo measurement error
(probe compensation excluded, footnote 1, p.3); the specification is
mathematically complete once formalised; a unique or at least sufficient
local optimum; frames related by a rigid transformation; the measurement
strategy is adequate. [AI]

**F. Edge cases.** Natural-language tolerance with two valid formalisations
giving different problems (circle radius as mean of max and min distance, or
as a band; §3.2, p.6-7). Partial arc: a radius tolerance implies a much
tighter implicit tolerance elsewhere (§3.1, p.6; the text says "±1mm" while
the example uses ±0.1 mm, an internal inconsistency we record as is).
Two-hole problem: maximum-inscribed subproblems ill-posed with three points
each while the coupled problem is well-posed (Fig. 4, p.13). Degenerate
optimum where one feature decides `s` and the others are free (Fig. 3, p.12).
Lobed circle sampled with an even count can miss all lobing (Fig. 1, p.8).

**G. Validation strategy.** Analytical bounds (lobing detection
`cos(pi/2m)`, Table 1, p.8); worked closed-form examples; bounding the
linearised minimum-zone circle against the true one (§8, p.18-19).

**H. Transferable principles.** P01 to P10, P44 (registry).

**I. CAD Spec consequence.** L5's "Rev B lies in the feasible region of
Contract B" is this report's formulation of tolerance assessment, applied to
contract variables instead of measured points. Formalisation removes
ambiguity, and one method must be agreed between parties (here: the compiler
and the grader). Max-slack `s` is a natural diagnostic margin.

**Challenge.** Cites ANSI Y14.5 (1982) and BS 7172 (1989). Later editions of
the GD&T standards exist (as far as we know ASME Y14.5-2018 and ISO 1101:2017);
not reviewed here. The general formulation is not superseded in the corpus;
FM12 and F06-FIT build on it. Applies to measured data; for exact CAD the
form constraints become exact predicates on B-rep faces (OI).

---

## E2. F89-LSQ: Least-squares best-fit geometric elements

**A. Core problem.** Stable, correct algorithms for least-squares fitting of
lines, planes, circles, spheres, cylinders and cones to coordinate data.
[abstract; high]

**B. Formal objects.** Element parameters (position, orientation, size,
shape); signed orthogonal distance `d_i`; sum of squares `E`; Jacobian J;
centroid; SVD.

**C. Operators.**

```yaml
- operator: fit_ls(element)
  inputs: [points, starting estimate]
  outputs: [parameters, residuals]
  preconditions: [m >= minimum points per element, preferably at least twice the minimum, well distributed]
  failure_conditions: [divergence from a poor start, slow convergence on partial arcs, rank-deficient J]
  numerical_issues: [unstable parametrisations (axis (a,b,1) near horizontal), cancellation (tan 2 theta formula), data far from origin]
```

**D. Decision logic.** Translate data to the centroid; for lines and planes
use the SVD (largest or smallest singular vector); for the rest, Gauss-Newton
with the trial element transformed to standard position each iteration
(vertical axis through the origin), convergence judged on three criteria:
change in E, step size, gradient `J^T d`. [§2.2, §8; medium, OCR]

**E. Hidden assumptions.** Errors only in the normal direction, small,
uncorrelated (made explicit later in F06-FIT); representative sampling;
good starting values exist (for cylinders and cones, §9.4 and §11.4 admit no
straightforward method; a general quadric fit is suggested with 9 or more
points).

**F. Edge cases.** Nearly horizontal axis under Rule 1 parametrisation;
partial arcs; sign of direction cosines (the algorithm must not depend on a
sign convention, §3.4 note 2); cone at half-angle near pi/2.

**G. Validation.** Not stated in the scan we read; the report presents
algorithms with numerical-stability arguments.

**H. Principles.** P11, P12, P13.

**I. CAD Spec consequence.** None for the exact analytic B-rep path: there
the cylinder axis and radius are read from the kernel's surface definition,
not fitted. Becomes essential the day a mesh, a faceted STEP or a scan is
accepted (APP: DEFER, but reserve an `association_operator` slot).

**Challenge.** 1989/1991. Algorithms remain standard; ISO 10360-6 (cited by
FM12) later standardised testing of such software. OCR text: formulas not
transcribed, only reasoning used.

---

## E3. FM12: Generation of numerical artefacts

**A. Core problem.** Produce reference data with a known exact answer to test
form and tolerance software, without writing reference software. [§1, p.145; high]

**B. Formal objects.** Computational aim `a = C(x)`; reference pair `<x, a>`;
software under test `a_hat = A(x)`; forward, backward and hybrid accuracy;
null space of `J^T`; KKT conditions; vertex and non-vertex Chebyshev solutions.

**C. Operators.**

```yaml
- operator: generate_ls_reference
  inputs: [exact solution b, points x* on f(u,b), normals n*]
  outputs: [x = x* + e n* with J^T e = 0]
  preconditions: [J full rank]
  numerical_issues: [compact Householder representation for large m]
- operator: customise_deviation
  inputs: [target deviation d0 (form, systematic, correlated)]
  outputs: [projection Q2 Q2^T d0 into the null space]
- operator: generate_chebyshev_vertex
  inputs: [n+1 surface points]
  outputs: [partition I+, I- with lambda >= 0, perturbed points]
  failure_conditions: [only local optimality guaranteed; non-vertex cases open]
```

**D. Decision logic.** Choose the answer first; build input data that the
first-order optimality conditions certify has that answer; run the software;
compare with a stated accuracy measure.

**E. Hidden assumptions.** First-order optimality implies the intended
optimum (true locally for LS; global not guaranteed for Chebyshev, §5.1);
finite-precision rounding of x is small relative to the test tolerance.

**F. Edge cases.** Flatness data sets with order m global minima (§2,
p.146); non-vertex Chebyshev solutions (sphere of smallest radius defined by
4, 3 or 2 points, §5, p.148); finite precision makes an exact reference pair
impossible (§2).

**G. Validation.** First-principles certification of each reference pair by
the optimality conditions, instead of trusting a second implementation.

**H. Principles.** P31 to P36, P40.

**I. CAD Spec consequence.** The strongest single support for keeping the
generator and the grader independent and for building test truth from
construction inputs (APP). The analogue for contracts: build items whose
MUS and MCS are known by construction (planted conflicts) and check the
enumerator against them; a SAT witness is self-certifying by `holds`, an
UNSAT claim needs a certificate (OI, see EDR-003).

**Challenge.** States that non-vertex Chebyshev generation needs further
research and that TraCIM was funded for it (§6). TraCIM ended 2015; whether
the open problem was closed is not in the corpus (RESEARCH FURTHER).

---

## E4. TRACIM18: TraCIM verification guidance

**A. Core problem.** Verify implementations of mathematical calculations
used in metrology, online, against NMI reference data. [§1-2, p.3; high]

**B. Formal objects.** Specification of computational aim (fields:
mathematical model, input parameters, output parameters; what, not how);
reference pair; test results; per-output tolerance supplied by the user;
software identity (name, version, revision, vendor, details); process key;
expiry date; software evaluation report with overall PASS or FAIL and the
list of failing reference data sets. [§2.1-2.2 p.4-5; §3.8 p.9; §4.2-4.4 p.10-11; high]

**C. Operators.** request reference data, run software under test, submit
results with tolerances, compare (server side), report.

**D. Decision logic.** For each reference pair, compare test and reference
results under the tolerances; combine into one figure of merit and an
overall PASS/FAIL (Fig. 1-2, p.4-5).

**E. Hidden assumptions.** Reference results are correct "with an assured
quality"; the declared tolerance is fit for the user's purpose; the software
version tested is the one in use.

**F. Edge cases.** The user chooses the tolerances, so a loose tolerance
passes poor software (AI). Reference data expire, forcing a fresh test.

**G. Validation.** This document is itself the validation protocol.

**H. Principles.** P37, P38.

**I. CAD Spec consequence.** Each evaluator (observation map, `holds`,
`apply_eco`, conflict enumeration, probes) should have a written
computational aim separate from its code, and every validation report should
name the evaluator version and list each failing artefact by ID. The
observation map's rules table (`L5-amendments.md` §3) is already most of a
computational aim (OI).

**Challenge.** Operational guide, 2018. The service details (URLs, keys) are
not relevant; the method is.

---

## E5. TRACIM-DB: database of applications

**A. Core problem.** Inventory computational aims worth verification across
metrology domains (79 aims, 7 domains, 20 applications).

**B/C.** Rows relevant to geometry: least-squares and Chebyshev fits of
standard elements (rows 21, 22, 33, 34), aspheric, gear, quadric and NURBS
fits (35 to 44), actual-nominal max/min deviation for 3D profiles (62),
ISO form for torus, sphere, roundness (64), minimum zone, maximum inscribed
and minimum circumscribed elements (66), form and tolerance assessment for
multi-component features (67), ODR per element (68 to 79). [rows as listed; high]

**D-G.** Not given (a planning table).

**H/I.** NMIs and CMM vendors considered these the calculations that need
verification. When cad-spec adds GD&T or scans, each such evaluator needs a
computational aim and reference pairs before it is trusted (APP, DEFER).

---

## E6. F06-FIT: uncertainty evaluation for fitting geometric surfaces

**A. Core problem.** Fit surfaces to coordinate data in a way that uses the
real (correlated, anisotropic) uncertainty of the coordinates, and propagate
it to the fitted parameters. [abstract, §1, p.S282-S283; high]

**B. Formal objects.** Parametric surface `f(u, b)` with footpoints u; signed
orthogonal and generalised distances; uncertainty matrix `U_xi = B B^T` with
a structured factor (per-point and common effects, eq. 12); position
parameters t and shape parameters s; probe radius offset.

**C. Operators.**

```yaml
- operator: odr_fit
  assumptions: [errors iid, isotropic]           # MLE only then (§2)
- operator: gauss_markov_fit
  inputs: [x, U_xi structured]
  outputs: [b, U_b = (J^T J)^-1]
  numerical_issues: [O(m^3) if naive; O(m) with structure (§3.3, §3.5)]
- operator: propagate
  formula: U_b = K U_d K^T, K = (J^T J)^-1 J^T     # eq. 5, valid for any LS fit
- operator: chebyshev_fit
  numerical_issues: [constrained optimisation, much harder (§2.7)]
```

**D. Decision logic.** Model the measuring system, derive `U_xi`, fit by
maximum likelihood, propagate to `U_b`; Monte Carlo (virtual CMM) when the
fit is not smooth (Chebyshev) (§3.8).

**E. Hidden assumptions.** Multivariate Gaussian effects; accurate data
(second-order term in H dropped, §2.2); a correct model of the instrument.

**F. Edge cases.** Laser-tracker cylinder: isotropic assumption makes `x0`,
`y0` uncertainties optimistic by "a factor of two to nearly four"; ODR radius
uncertainty 8.3 um against 3.5 um for the correlation-aware fit on data set A
(§3.7, Table 1, p.S289).

**G. Validation.** Monte Carlo with 5000 simulations agrees with the
analytic uncertainties (Table 1).

**H. Principles.** P14, P15, P41.

**I. CAD Spec consequence.** Not applicable to exact analytic B-rep. For
any measured input: never assume isotropic uncorrelated errors silently, and
never store one scalar "uncertainty" per value (APP, DEFER).

---

## E7. F18-PSS: position, size and shape decomposition

**A. Core problem.** Split a point-cloud variance matrix into position, size
and shape components, and relate it to how the frame of reference is
specified. [abstract; high]

**B. Formal objects.** `J` (3m x 7) built from translations, small
rotations and scale (eq. 1); projections `P1` (6 position), `P2` (1 size),
`P3` (3m-7 shape); frame constraints `C^T x = c0`.

**C. Operators.** decompose(V); reframe(x, C) with propagated
`V_hat = (I - G (C^T G)^-1 C^T) V (...)^T` (eq. 5, §4).

**D. Decision logic.** Choose the frame constraint; propagate; the choice
`C = G` gives `V_hat = V_ZS`, the minimum trace over all frame choices (§4, p.4).

**E. Hidden assumptions.** First-order (small) transformations; x
approximately satisfies the frame constraints already.

**F. Edge cases.** Uniform scale uncertainty has a position component unless
the data are mean-centred (§3.3, p.3).

**G. Validation.** Algebraic proof (trace inequality, §4).

**H. Principles.** P17, P18.

**I. CAD Spec consequence.** Classify every contract variable by
invariance: distances (L, W, T, D, px, py, and mx, my measured to the part's
own faces) carry no position component; quantities referenced to a global
origin (scorer R5 hole centres to the origin, R8 mid-plane to Z = 0) do. The
first class needs no datum; the second needs a declared frame (APP, USE NOW
as documentation; see the observation skill).

---

## E8. FWSO13: form errors in datum features

**A. Core problem.** Evaluate how datum form error and measuring-system
effects propagate, through the datum frame, to evaluated features.
[§1, p.1; high]

**B. Formal objects.** Point model `x_i = s*_i + f_i n_i + e_i + eps_i`
(form, systematic, random); Gaussian-process form error; frame constraints
`c(a) = c0` (six); rigid transformation `T(x, t)`; sensitivity `X = G + K H`.

**C. Operators.** establish_frame (fit datum features, solve for t such that
the fitted datums meet the constraints); propagate through the frame.

**D. Decision logic.** Datums define the frame; every evaluated feature
inherits frame uncertainty; compare datum strategies by their effect.

**E. Hidden assumptions.** Six constraints fix the frame; Gaussian effects;
nominally orthogonal datum planes (three extra degrees of freedom eliminated
by assuming orthogonality, §4, p.3).

**F. Edge cases.** In the datum frame, the six constrained parameters have
zero uncertainty and the uncertainty is redistributed to the others
(Table 1). A partial arc (scallop) has large uncertainty on x and radius
(Table 3).

**G. Validation.** Numerical example on a Rolls-Royce multi-feature artefact.

**H. Principles.** P19, P20, P42, P43.

**I. CAD Spec consequence.** AS: for ideal geometry and an ideal measuring
system the datum choice does not change subsequent results (§1, p.1). That is
exactly why L5 v1 can fix the frame by declaration (global axes) on exact
B-rep. The day form error exists (scans, meshes), the frame strategy becomes
part of the observation definition (APP, DEFER).

---

## E9. PEP97: uncorrected bias

**A. Core problem.** Express uncertainty when a known bias is deliberately
not corrected, without breaking the link between expanded uncertainty and
confidence. [§1, p.577-578; high]

**B. Formal objects.** Result y, signed bias delta, combined standard
uncertainty `u_c` computed as if corrected, coverage factor k, asymmetric
limits `U+`, `U-`.

**C. Operators.** SUMU: `U+ = max(k u_c - delta, 0)`, `U- = max(k u_c + delta, 0)`
(§2-3, p.579-580). Multiple biases: algebraic sum, overlap estimated and
subtracted, its uncertainty added in RSS (p.580).

**D. Decision logic.** Report `u_c`, the signed bias and `U+/U-`; conformance
zone shrinks asymmetrically (Fig. 3).

**E. Hidden assumptions.** Bias known in sign and magnitude; Gaussian for the
confidence comparison, though SUMU's guarantee holds for any distribution
because its interval contains the corrected one (p.581).

**F. Edge cases.** `delta > k u_c` gives a one-sided interval. `U(k=2)` is
not `2 U(k=1)`. RSS of bias with `u_c` (RSSuc) over-states (near 100%
confidence at `delta/u_c = 2`, k = 2); RSS with `U` (RSSU) under-states
(below 80%) (Fig. 4, p.581).

**G. Validation.** Achieved confidence computed against nominal for k = 1, 2, 3.

**H. Principles.** P27, P28.

**I. CAD Spec consequence.** A geometry kernel has known, signed,
one-sided numerical effects (for example the 2e-7 mm padding of a spline
bounding box recorded in M1). They are biases, not noise: correct them,
refuse the case (what M1 does for splines), or apply them one-sided; never
fold them into the symmetric slack (APP).

**Challenge.** Cites ISO/DIS 14253-1 (1997 draft). Later editions of
ISO 14253-1 and JCGM 106:2012 exist (JCGM 106 is cited by PK14); whether the
SUMU convention was adopted there is not in the corpus (RESEARCH FURTHER).

---

## E10. PK14: conformity, decision rules, risk

**A. Core problem.** Standardised terminology and risk calculation for
accepting and rejecting products under measurement uncertainty. [abstract; high]

**B. Formal objects.** Closed tolerance interval; acceptance and rejection
zones; gauge limits and guard bands; measurement capability index
`C_m = (T_U - T_L) / 2U`; contingency table; production prior; cost matrix;
nonconforming loss metric Lambda.

**C. Operators.** decide(result, U, rule); risk(FA, FR) via the integrals of
Fig. 3; expected profit from the cost matrix.

**D. Decision logic.** Measurement result and U, a stated decision rule
(simple, stringent with x% U guard band, relaxed, multi-outcome), outcome;
risk depends on the prior and the rule; rule choice is economic (§3.4).

**E. Hidden assumptions.** Well-defined measurand (§2.1), Gaussian pdfs
(§3.3), known production distribution for risk.

**F. Edge cases.** Symmetric square plate with a central bore and three
datum planes: datum assignment ambiguous, measurand has several true values;
conforming if any assignment conforms, but poor practice; add a
symmetry-breaking feature (§2.1, p.238). Nonconforming but functional parts go
unreported, so false acceptance is hard to observe (§2.3). Traceability does
not bound risk (§3.2.2). MSA RSS of bias is inconsistent with the GUM (§3.2.3).

**G. Validation.** Worked economic examples (Tables 2 to 6).

**H. Principles.** P21 to P26, P28.

**I. CAD Spec consequence.** cad-spec's family is a symmetric rectangular
plate: the same ambiguity class as the paper's own example, resolved in
cad-spec by declaring the frame in the prompt (APP: write that down as the
measurand definition). Every acceptance in the grader is a decision rule and
should be named as one (EDR-002).

---

## E11. F06-BAY: Bayesian optimised conformance

**A. Core problem.** Choose decisions (accept, reject, re-measure, rework)
that minimise expected loss given partial information. [abstract; high]

**B. Formal objects.** Posterior `p(a | y)`; regions `I_j`; decisions `D_k`;
cost matrix `C_kj`; expected cost `e = C p`; decision rule `R(x)`; aggregate
cost over the process distribution.

**C. Operators.** posterior, expected_cost, argmin decision, aggregate.

**D. Decision logic.** With the Table 1 costs and `sigma_M = 0.5`, accept on
`[-1.87, 1.78]`; adding re-measurement (`sigma_R = 0.2`, cost 1) gives
accept `[-1.41, 1.33]`, reject outside `[-2.42, 2.40]`, re-measure between
(§2.1, Fig. 1-2, p.810-811).

**E. Hidden assumptions.** Costs are known; Gaussian; the decision options
are fixed externally.

**F. Edge cases.** Systematic effects: the expected loss depends only on
`sigma_M`, but the spread of outcomes grows with the systematic share;
with `sigma_C = 0.3` the per-batch exceedance rate ranged 3.55% to 14.2%
around a 4.55% mean (§3, Table 2, p.811-812).

**G. Validation.** Simulation (500 x 500,000 samples).

**H. Principles.** P29, P30.

**I. CAD Spec consequence.** (OI) An RL grader is a decision rule applied
millions of times by one fixed instrument: its errors are systematic, shared
by every rollout, and a policy can find and exploit them; random grader noise
would average out, systematic error does not. This is the decision-theoretic
reason behind "soundness over coverage" and the asymmetric cost of a false
pass. A third outcome (re-measure) is the formal ancestor of INDETERMINATE.
