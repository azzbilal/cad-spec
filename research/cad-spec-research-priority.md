# Research priority

What to act on, what to keep for later, what is still unknown. IDs refer to
the principle registry (P), gap analysis (G), failure patterns (FP) and
decision records (EDR).

## Top 10 findings that should change cad-spec now

1. **Conformance is feasibility, and the expert record says so.** L5's region
   grading is Forbes' 1992 formulation of tolerance assessment applied to
   contract variables (P02, G3). Keep it and cite it; it answers "why not one
   reference Rev B" in any review.
2. **One meaning, shared, is the expert answer to disagreeing tools** (P06,
   G2). Add a boundary test that runs `holds` through both the exact and the
   measured entry points on the same values.
3. **UNSAT needs a certificate; SAT carries its own** (EDR-003, FP04). Build
   the certificate checker in M2b, before the enumerator's results are
   trusted anywhere.
4. **Name every acceptance rule** (EDR-002, P23). `eps`, the form tolerance,
   the robust margin and the change threshold become rule IDs recorded in
   items and verdicts.
5. **Separate error kinds; ban a field called `uncertainty`** (EDR-006, G19).
   In the exact domain the only error is numerical.
6. **Write computational aims per evaluator** (EDR-001, P37), starting with
   the observation map v1 (operator, frame, invariance class, domain,
   refusal rules).
7. **Test truth from construction, never from the evaluator** (EDR-005, P31,
   FP22). Make it a written rule now and a self-test in M3.
8. **Plant conflicts with known MUS sets** in the M2b gate (P31, FP04) in
   addition to the owner's three mandatory examples.
9. **Document the frame as the measurand definition** (P19, P21, G9, G10):
   declared axes resolve the symmetric-plate ambiguity that PK14 uses as its
   own cautionary example.
10. **Track invariance classes** (P17, FP16): only frame-bound variables
    need a datum; say which ones are.

## Top 10 findings to preserve for later

1. Minimax (Chebyshev) evaluation is a different, harder problem; never an
   LS fit plus max residual (P16, FP10).
2. Datum strategy changes results once form error exists; compare strategies
   (P19, P43, FP17).
3. Frame constraints redistribute uncertainty; minimum-trace frame (P18).
4. Structured covariance; isotropy assumption can be wrong by 2 to 4 times (P14).
5. Sampling plans can be blind to whole error classes (P09); applies to probes
   now (EDR-007) and to scans later.
6. Short arcs and small patches are ill-conditioned (P20).
7. Known biases go one-sided (SUMU), never in quadrature (P27).
8. Bayesian expected-loss rules with a re-measure option (P29), for a future
   inspection product.
9. Template matching: a fixed CAD shape against data needs only the frame
   (P08); the core of any future scan-against-CAD check.
10. NMI inventory of calculations that need verification (P39): the backlog
    for a GD&T-era test suite.

## Top unresolved questions

1. Exact certificate format for the min/max normal form: one Farkas vector
   per branch, or Fourier-Motzkin on the small system? (EDR-003)
2. Should a spline face get its own reason code (`no_association_operator`)
   distinct from `form_violation`? Changes reporting only. (G5)
3. Answered while writing: the M1 gate pins 90, 180 and 270 degree turns.
   Open: should a 1e-10 rad turn (inside the form tolerance) be pinned too? (G10)
4. Does any current constraint kind amplify the slack (large coefficients)?
   If generator coefficients stay small integers, no; must be checked before
   free coefficients. (G18)
5. Which ISO 14253-1 and JCGM 106 conventions supersede PEP97 and PK14
   details? Not in the corpus. Follow-up reading: ISO 14253-1 (current
   edition), ISO/TR 14253-6, JCGM 106:2012, ASME B89.7.3.1-2001, ISO 10360-6,
   and (not cited by the corpus, our suggestion) ISO 17450 on specification
   and verification operators, ISO 5459 on datums.
6. Was non-vertex Chebyshev reference-data generation solved by TraCIM
   (FM12 §6)? Not in the corpus.

## Top architecture risks

1. A wrong conflict set becomes a systematic grader error that RL exploits (FP04, FP25).
2. Silent widening of `eps` or mixing it with a measurement idea (EDR-002, EDR-006).
3. Observation meaning drifting with code edits, no written aim to check against (EDR-001).
4. Future scan or mesh input entering through the exact-domain path (FP11, G5).
5. Per-feature grading creeping into a coupled contract (FP06).

## Top implementation risks

1. Float leakage into exact parsing (FP20).
2. Rounding before a decision (FP08).
3. Face counting instead of feature counting (FP12).
4. Probe schedule blind to a hardcoding pattern (FP26).
5. Derived variables recomputed instead of measured (design note §5.3).

## Top validation risks

1. Expected values produced by the evaluator under test (FP22).
2. Tests and enumerator sharing Z3 (FP04).
3. Test tolerances looser than the decision they support (FP23).
4. Suite success reported as proof of every verdict (FP24).
5. Hand-labelled cases chosen only where the implementation is known to work
   (selection bias in gate design; mitigated by external reviewers writing
   cases).
