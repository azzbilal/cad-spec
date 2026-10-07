# Expert Decision Records

An EDR records an architectural consequence of the research. Status values:
PROPOSED (needs the owner's approval), ACCEPTED, REJECTED, SUPERSEDED. A
decision is never rewritten; a change is a dated section below the original,
as for registered documents. None of these reopens the L5 design note: each
is additive (documentation, an extra field, an extra test or diagnostic).
Milestone tags say where the work would land.

---

## EDR-001. Computational aims and static observation definitions

- **Status:** PROPOSED, 7 Oct 2026. Milestone: now (documentation), M3 (code).
- **Problem:** the meaning of each observation (operator, frame, scope) is
  spread over a docstring, the design note and the amendments. A reviewer
  cannot check an evaluator against a statement of what it should compute.
- **Expert principle:** P37 (computational aim: what, not how, complete and
  unambiguous), P10 (a value is the output of an operator), P17 (invariance).
- **Source:** TRACIM18 §2.1 p.4; F18-PSS §3.4-3.5; F92-GTA §5.
- **Current implementation:** `cad_spec/l5/observation.py`, prose rules.
- **Risk if unchanged:** a future change moves an operator (for example the
  hole centre from mid-plane to top face) without a visible change of meaning;
  reviewers argue about intent instead of checking a specification.
- **Decision:** add `docs/aims/` with one page per evaluator: observation map
  v1, `holds`, `apply_eco`, conflict enumeration (M2b), probe evaluation (M3).
  For the map, a table per variable: operator, frame, invariance class,
  domain, numerical bound, refusal rules, known kernel biases. Versioned with
  `OBSERVATION_VERSION`.
- **Alternatives rejected:** per-instance provenance fields on every
  `Observation` (bloats results with constant information); leaving the
  docstring as the specification (it is code-adjacent and edited with code).
- **Implementation consequence:** documentation only now; later a frozen
  dict mirroring the table, with a test that the dict and the doc agree.
- **Tests required:** each row of the aim has at least one gate case citing it;
  a self-test fails if a variable has no aim row.

## EDR-002. Every acceptance is a named decision rule

- **Status:** PROPOSED. Milestone: M2a review or M2b; M3 for verdicts.
- **Problem:** `eps = 1e-9 mm`, the form tolerance `1e-7 mm`, the robust
  margin `0.01 mm` and the change threshold are decision rules in metrology
  terms but are recorded as bare numbers.
- **Expert principle:** P23 (state the rule), P24 (rule choice is separate
  from error evaluation), P25.
- **Source:** PK14 §2.4 p.239-240, §3.4 p.241.
- **Current implementation:** scorer `TOLERANCES`, M2a tolerance policy in
  `item.py` (pinned to scorer 0.5.0).
- **Risk:** a later edit treats `eps` as measurement uncertainty, or widens it
  for convenience, and verdicts change meaning without a version bump.
- **Decision:** give each rule an ID and a one-line definition, recorded in
  every compiled item and every verdict report:
  `DR-DIM-RELAXED-EPS` (accept `value <= limit + 1e-9 mm`; relaxed acceptance
  by numerical slack), `DR-FORM-KERNEL` (form at 1e-7 mm),
  `DR-FEAS-STRINGENT-0.01` (infeasible only if still infeasible loosened by
  0.01 mm; otherwise discard), `DR-CHANGE-EPS` (changed when
  `|delta| > 1e-9 mm`).
- **Alternatives rejected:** adding a measurement-uncertainty term (no
  physical meaning for exact B-rep); a stringent guard band at runtime (would
  reject exact-limit parts that are correct by construction; C_m about 1e7
  makes it pointless).
- **Implementation consequence:** a small constant table in `item.py` or a
  sibling module; item schema field `decision_rules`.
- **Tests required:** each rule has boundary cases at limit, limit plus or
  minus the slack, and just beyond; a changed rule value without an ID
  change fails a pinning test.

## EDR-003. Infeasibility and conflict sets carry certificates

- **Status:** PROPOSED. Milestone: M2b.
- **Problem:** a SAT result is checkable (substitute the witness into `holds`
  with exact rationals). An UNSAT result, and every MUS and MCS derived from
  satisfiability checks, is trusted on the solver's word. Tests that use the
  same solver cannot catch a wrong conflict set.
- **Expert principle:** P31 (certify reference results from first
  principles), P32, P04.
- **Source:** FM12 §1 p.145, §4.1 (optimality-condition certification).
- **Current implementation:** planned Z3 over exact rationals, exhaustive
  subset enumeration.
- **Risk:** a wrong `accepted_mus` rejects correct structured rejects or
  accepts wrong ones, at scale, as a systematic grader error (P30).
- **Decision:** (a) every SAT claim stores its witness and is re-checked by
  `holds` in exact arithmetic; (b) every UNSAT claim on a linear system stores
  a Farkas certificate (non-negative multipliers combining the constraints
  into `0 >= c > 0`), verified by exact rational arithmetic independent of
  Z3; with `min`/`max`, the normal form is an and/or of linear atoms, so the
  certificate is one Farkas vector per branch of the case split, or the claim
  is checked by an independent second method (for example exact Fourier-
  Motzkin elimination on the small system); (c) minimality of an MUS is
  shown by a witness for each subset with one constraint removed (SAT, so
  self-certifying); (d) planted-conflict items whose MUS set is known by
  construction are in the M2b gate.
- **Alternatives rejected:** trusting Z3 plus spot checks; a second SMT
  solver only (shares the problem class, not independent enough in failure).
- **Implementation consequence:** a certificate checker module with no Z3
  import; item schema keeps certificates in the solver block.
- **Tests required:** a corrupted certificate fails; a deliberately wrong MUS
  fails; a non-minimal set fails its minimality witnesses; the three owner
  examples for M2b pass with certificates.
- **Note:** this is OI applied to a metrology principle; the corpus does not
  discuss SMT solvers.

## EDR-004. Boundary-margin diagnostic, no INDETERMINATE in the reward

- **Status:** PROPOSED. Milestone: M3.
- **Problem:** the RL reward must be binary and deterministic, yet a policy
  can learn to land within a few nanometres of a limit (numerics gaming).
- **Expert principle:** P03 (report how far inside), P29 (third decision),
  P30 (systematic error is exploitable).
- **Source:** F92-GTA §2.5; F06-BAY §2.1, §3.
- **Decision:** keep PASS/FAIL per gate for the reward. Add, per active
  predicate, the signed margin in mm of the variables (the same scaling M2a
  uses for slack), and report the share of answers within `10 x eps` of an
  active limit. No INDETERMINATE runtime verdict in L5 v1: in the exact
  domain the indeterminate band is the slack itself.
- **Alternatives rejected:** an INDETERMINATE verdict in the reward (would add
  a third reward value with no physical meaning here); a stringent runtime
  guard band (see EDR-002).
- **Tests required:** margin sign and size on hand-built parts at, inside and
  outside a limit; margin is reported but never changes a verdict.

## EDR-005. Test truth never comes from the code under test

- **Status:** PROPOSED. Milestone: now (rule), M3/M4 (self-test).
- **Problem:** the observation map reuses the scorer's measurement by design;
  a test whose expected value came from `measure` or `observe` would pass any
  bug in both.
- **Expert principle:** P31, P34.
- **Source:** FM12 §1; TRACIM18 §2.2.
- **Decision:** expected values in gate suites come from construction
  parameters or hand derivation, written in the test file; a self-test scans
  gate files for expected values produced by calling the evaluator.
- **Tests required:** the self-test itself, with a synthetic offending file.

## EDR-006. Error kinds are separate fields; domain is explicit

- **Status:** PROPOSED. Milestone: M2a/M2b schema review.
- **Problem:** "uncertainty" is used loosely; mixing error kinds breaks
  decision rules (P27) and misstates confidence (P14).
- **Decision:** never a field named `uncertainty`. Exact domain fields:
  `numerical_slack_mm`, `robust_margin_mm`, `kernel_tolerance_mm`. Every
  observation definition and compiled item names its `domain`
  (`exact_brep_analytic` today). Reserved names for a future measurement
  domain: `measurement_covariance`, `bias_mm` (signed), `model_error`.
  Semantic ambiguity is never a number: it is a template defect or an
  `out_of_scope`.
- **Tests required:** schema test that rejects an unknown error field name.

## EDR-007. Probe detectability per pattern

- **Status:** PROPOSED. Milestone: M3 (probes), M4 (misconception library).
- **Problem:** a probe schedule is a sampling plan and can be blind to a
  class of wrong answers.
- **Expert principle:** P09.
- **Source:** F92-GTA §3.3, Table 1, Fig. 1.
- **Decision:** for every (item, hardcoding pattern or misconception) pair
  the compiler records whether some kept probe detects it; undetected pairs
  are reported per item, never assumed covered.
- **Tests required:** a deliberately blind schedule (growth-only probes on a
  centred pattern) must be flagged.

## EDR-008. An expert reasoning layer that agents must consult

- **Status:** PROPOSED in the pull request that adds this file.
- **Problem:** the research must change behaviour, not sit in a folder.
- **Decision:** project skills under `.claude/skills/cad-spec-*` (the
  repository's native agent format, Claude Code), a router skill, and a rule
  in `CLAUDE.md` requiring a "Skills consulted" statement before substantial
  work on observation, contracts, grading, tolerances or validation.
- **Alternatives rejected:** one large skill (fragmented triggers, too long to
  read each time); research documents only (not consulted in practice).
- **Tests required:** none automated; reviewers check the statement in each
  PR description.

## EDR-009. Measurement-domain machinery is deferred, with reserved slots

- **Status:** PROPOSED.
- **Decision:** no fitting, datum-feature frames, GD&T zones or covariance in
  L5 v1. Reserve `operator` and `domain` in observation definitions so they
  can be added in a new observation version without changing old meanings.
- **Source:** P08, P11 to P16, P18, P42; G21.
