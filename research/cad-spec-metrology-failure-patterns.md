# CAD Spec metrology failure patterns

Each pattern: **Symptom**, **Cause**, **Why naive software misses it**,
**Detection**, **Mitigation**, **Required test**, **Source**. Sources are
corpus keys (see the corpus index) or "cad-spec history" when the pattern
already happened here. FP IDs are stable; skills cite them.

## Specification and semantics

**FP01. Ambiguous specification.**
Symptom: two tools, or compiler and grader, disagree on the same part.
Cause: a requirement admits two formalisations. Missed because each tool is
internally consistent. Detection: hand-labelled cases at the ambiguous
reading; diff of verdicts between entry points. Mitigation: one canonical
formal text, one evaluator (`holds`). Test: for every constraint kind, a part
that passes under one reading and fails under the other, with the expected
verdict written by hand. Source: F92-GTA §3.2, §8.

**FP02. Inconsistent or over-tight specification.**
Symptom: no part can pass, or a hidden implied tolerance is far tighter than
intended. Cause: constraints conflict or amplify (partial arc). Missed
because each constraint looks reasonable alone. Detection: evaluate at the
ideal design; compute slack per constraint; sensitivity of derived
quantities. Mitigation: compile-time V1 and slack report. Test: an item with
a planted inconsistency must be flagged before any model sees it.
Source: F92-GTA §3.1.

**FP03. Tiny contradiction called infeasible while both sides pass at runtime.**
Symptom: compiler says "reject", but a built part satisfies every predicate
within slack. Cause: exact reasoning without the measurement slack.
Missed because each component is correct in its own arithmetic. Detection:
loosen by the robust margin and re-solve. Mitigation: robust infeasibility
(0.01 mm) and discard of near-boundary items. Test: two constraints
contradictory by 1e-10 mm: the item must be discarded, not labelled
infeasible. Source: owner's M2 instruction, 7 Oct 2026; P23.

**FP04. Unverifiable infeasibility.**
Symptom: an infeasible label or an MUS that is wrong, accepted by every test
because the tests use the same solver. Cause: UNSAT is not self-certifying.
Detection: certificate check or second method. Mitigation: EDR-003. Test:
planted-conflict items with known MUS sets; a deliberately wrong MUS must be
rejected by the certificate checker. Source: FM12 §1 (OI).

**FP05. Witness taken as the answer.**
Symptom: correct alternative revisions fail. Cause: grader compares with the
witness. Missed because the witness itself passes. Detection: sample several
points of the region. Mitigation: region predicates only. Test: owner's M2b
example 1 (many valid answers). Source: design note §3.4; P34 by analogy.

**FP06. Per-feature grading of coupled constraints.**
Symptom: either/or repairs judged wrong, or a subproblem undefined. Cause:
decomposition. Detection: coupling-depth > 0 items in the gate. Mitigation:
evaluate Contract B as a whole. Test: owner's M2b example 2 (plate grows or
margins shrink): both repairs pass. Source: F92-GTA §4, Fig. 4.

## Observation and association

**FP07. Silent wrong number instead of refusal.**
Symptom: `ok` with a slightly wrong variable. Cause: the operator applied
outside its domain (tilted bore read as vertical). Missed because the value
is plausible. Detection: scope rules on the unrounded data. Mitigation:
`out_of_scope`. Test: boundary pairs on each scope limit. Source: cad-spec
history, M1 review R1 (1e-8 rad tilt accepted with a margin wrong by 2e-8 mm).

**FP08. Rounding hides a feature.**
Symptom: a 1e-6 mm radius step reported as one diameter. Cause: grouping
after rounding. Missed because rounded values look clean. Detection: compare
unrounded values. Mitigation: never round before a decision. Test: steps
just above and below the slack. Source: cad-spec history, M1 review R2/R3.

**FP09. Probe or detector blind spot.**
Symptom: a cross bore of 0.2 micron missed. Cause: the inward probe stepped
across it. Detection: features below a supported size. Mitigation: refuse
below 0.01 mm. Test: size boundary. Source: cad-spec history, M1 review R4.

**FP10. Wrong association operator for the job.**
Symptom: form error under-reported (LS fit residual used as a zone), or
mating judged wrong. Cause: least squares where minimax, inscribed or
circumscribed is meant. Missed because LS is the default everywhere.
Detection: computational aim names the criterion. Mitigation: operator in
the observation definition. Test (future): a lobed circle where LS and
minimum-zone circularity differ by a known amount. Source: F92-GTA §5, §8;
F06-FIT §2.7.

**FP11. Unknown surface type treated as a known one.**
Symptom: spline or faceted geometry measured with plane/cylinder logic.
Cause: no association operator for the type. Mitigation: refuse with a
specific reason code (G5). Test: spline-face plate, faceted bore. Source:
cad-spec history (spline false rejection kept on purpose); P10.

**FP12. Topological fragmentation.**
Symptom: one geometric cylinder split into several faces (seam, split
faces) counted as several holes or rejected as partial. Cause: counting
faces instead of geometric features. Mitigation: group coaxial faces of the
same radius before counting (`measure.py` does). Test: same part built by
different construction orders, split faces, fused coplanar faces: identical
observations (design note V5). Source: `measure.py` docstring; P10.

**FP13. Object spoofing across the trust boundary.**
Symptom: perfect score for a tiny cube. Cause: the grader asked the untrusted
object for its own measurements. Mitigation: serialise geometry, measure on
the trusted side. Test: a class answering `BoundingBox()` with nominal
numbers. Source: cad-spec history, scorer 0.4.0 trust boundary.

**FP14. Volume-only or envelope-only check passes extra features.**
Symptom: notches, pockets, bosses accepted. Cause: integral measures hide
local features. Mitigation: face-level form verdict (R9). Test: the 0.5.0
defect suite. Source: cad-spec history, audit of 3 Oct 2026.

## Frames and datums

**FP15. Underconstrained or ambiguous frame.**
Symptom: verdict changes with an arbitrary choice (which face is datum A).
Cause: symmetric part, or fewer than six independent constraints. Missed
because one choice is silently taken. Detection: enumerate symmetric frames.
Mitigation: declared frame (today) or explicit rule. Test: plate turned 180
degrees about Z measures identically; turned 90 swaps L and W.
Source: PK14 §2.1; FWSO13 §4.

**FP16. Frame-bound variable compared as if frame-free.**
Symptom: correct shape fails (or wrong position passes) after a rigid move.
Cause: invariance class not tracked. Detection: translate and rotate the same
part; frame-free variables must not change. Test: translated plate
(design note 7.2). Source: F18-PSS §3.4-3.5.

**FP17. Datum form error ignored (future).**
Symptom: positions depend on which datum points were used. Cause: frame from
non-ideal datum features. Mitigation: datum strategy in the observation
definition; compare strategies. Source: FWSO13 §1, §4.

## Numerics

**FP18. Poor conditioning or multiple optima.**
Symptom: unstable outputs, different answers from different starts. Cause:
short arcs, near-horizontal axis parametrisation, Chebyshev local minima.
Detection: rank and condition checks; multiple starts. Mitigation: refuse,
or prove global optimality. Source: F89-LSQ §2.2, §8; FM12 §2, §5.

**FP19. Known signed bias folded into symmetric slack.**
Symptom: acceptance too loose on one side, too strict on the other. Cause:
RSS of a bias. Mitigation: correct, refuse, or one-sided. Test: a part on the
biased side of a limit. Source: PEP97 §3; PK14 §3.2.3.

**FP20. Float leakage into exact reasoning.**
Symptom: MUS/MCS results flaky near boundaries; `10.000000001` read as
another number. Cause: parsing through float. Mitigation: exact rationals
read from text (M2a). Test: decimal literals that are not binary-exact.
Source: design note §12 (exact arithmetic); FM12 §2.

**FP21. Silent unit conversion.**
Symptom: radius used as diameter, inch values in mm. Cause: unitless
numbers. Mitigation: explicit units in the expression model (M2a);
`radius_for_diameter` misconception. Test: mixed-unit expressions refused.
Source: design note §8.1; general practice.

## Validation

**FP22. Generator and grader share the same bug.**
Symptom: everything passes; a defect is invisible. Cause: expected values
produced by the code under test. Missed because tests are green. Detection:
audit where expected values come from. Mitigation: truth from construction
or hand derivation (G13); planted artefacts. Test: a self-test that rejects
gate cases whose expected values were computed with `observe` or `measure`.
Source: FM12 §1; TRACIM18 §2.2.

**FP23. Test tolerance hides an error.**
Symptom: software passes verification but is wrong at the scale that
matters. Cause: the tester chooses a loose tolerance. Mitigation: state each
output tolerance against the decision it supports. Source: TRACIM18 §4.3 (AI).

**FP24. Passing a suite taken as proof of every verdict.**
Symptom: overclaiming in reports. Cause: traceability or verification
confused with risk control. Mitigation: report suite coverage and known
false-rejection classes. Source: PK14 §3.2.2.

**FP25. Systematic grader error exploited by RL.**
Symptom: rising reward with no rise in real quality; answers cluster at a
boundary or in one construction style. Cause: a systematic grader error is
shared by every rollout. Missed because average error looks small.
Detection: boundary-margin distribution (EDR-004), construction-style
breakdown, periodic external audit. Mitigation: soundness over coverage.
Source: F06-BAY §3 (OI).

**FP26. Probe set blind to a hardcoding pattern.**
Symptom: a hardcoded answer passes intent. Cause: probes chosen where the
hardcoding happens to agree (centred box, growth-only probes). Detection:
per-pattern detectability check (G15). Source: F92-GTA §3.3 (by analogy);
design note §5.4.

**FP27. Assumed Gaussian, independent or isotropic errors (future).**
Symptom: uncertainty misstated by factors of two to four. Cause: identity
covariance. Mitigation: structured covariance or an explicit assumption flag.
Source: F06-FIT §3.7, Table 1.
