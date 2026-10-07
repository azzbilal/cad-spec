# Artefact ladder for cad-spec evaluators

Philosophy (FM12 §1, P31): known truth, then the artefact built from it, then
the production evaluator, then comparison with the independently known
result. Never: production code computes the expected value, then passes its
own test.

Each level lists: what it tests, the independent truth source, the expected
outcome type, existing coverage in the repository (7 Oct 2026), and gaps.
"M1 gate" = `scripts/test_l5_observation.py`; "0.5.0 suite" =
`scripts/validate_scorer.py` defect suite; "M2a gate" =
`scripts/test_l5_contract.py` (branch only).

## Level 0. Exact ideal primitives
Tests: the nominal path. Truth: construction parameters of a plate with four
corner holes. Expected: exact values within 1e-9 mm, `ok`.
Coverage: M1 `nominal`; scorer tests on 230 generated specs. Gap: none.

## Level 1. Simple parameter perturbations
Tests: each variable responds to its own parameter only. Truth: perturbed
construction parameters. Expected: changed variable equals the perturbation;
others unchanged (frame-free invariance, P17).
Coverage: M1 `one_hole_moved_2_mm`, `different_margins_in_X_and_Y`,
`pattern_shifted_1_mm_in_X`. Gap: one case per contract variable with every
other variable checked unchanged.

## Level 2. Topological changes preserving geometry
Tests: values depend on geometry, not on topology (FP12). Truth: the same
geometry built differently (construction order, split faces, seam position,
fused coplanar faces, holes cut one by one versus as a pattern).
Expected: identical observations.
Coverage: partial (`measure.py` groups coaxial faces). Gap: explicit cases;
design note V5 makes this an M4 requirement for renderers.

## Level 3. Numerical tolerance cases
Tests: decision rules at their slack (EDR-002). Truth: limit plus or minus
known offsets at 1e-10, 1e-9, 1e-8 mm. Expected: accept at and inside the
slack, reject beyond.
Coverage: M1 `boundary_` cases (tilt, diameters, size, nesting); scorer
0.5.0 docstring example (6.6 against 6.5 +/- 0.1). Gap: the same triplets
for every Contract B constraint kind through `holds` (M2a/M3), and for the
change-detection threshold.

## Level 4. Frame and datum-dependent cases
Tests: invariance classes and declared frame (P17, P21). Truth: rigid motions
of the nominal part. Expected: translation invariant; 90 and 270 degrees swap
L and W; 180 identical; small turns beyond the form tolerance fail form.
Coverage: M1 `moved_off_the_origin`, `turned_90/180/270_degrees_about_Z`,
`turned_10_degrees_about_Z`. Gap: a turn of 1e-10 rad (inside the form
tolerance) giving unchanged frame-free values; mirrored pattern.

## Level 5. GD&T cases (future)
Tests: zone tolerances, datum reference frames. Truth: null-space and KKT
artefacts (FM12 §4-5), lobed features with known minimum zone. Expected:
values to stated accuracy. Coverage: none. DEFER (EDR-009).

## Level 6. Boundary cases of the contract
Tests: parts exactly on a constraint boundary (margin exactly 2 D, hole
tangent to the edge, two holes touching). Truth: hand-derived. Expected:
pass at the limit (closed intervals), fail beyond; family rules F1 and F2
decide breakouts and overlaps, not the map.
Coverage: M1 `hole_1_micron_from_the_edge`, `review_hole_breaking_out_of_a_side`,
`review_two_overlapping_holes` (observation level). Gap: the same at contract
level in M3.

## Level 7. Ambiguous or indeterminate cases
Tests: refusal and discard logic. Truth: designed ambiguity (stepped holes,
two diameters 1e-9 mm apart, contradictions of 1e-10 mm in a contract).
Expected: `out_of_scope` at observation level; "discard and regenerate" at
compile level (FP03).
Coverage: M1 `counterbored_holes`, `holes_of_two_diameters`,
`review_offset_step`, boundary cases. Gap: compile-level near-contradiction
items (M2b).

## Level 8. Out-of-scope cases
Tests: refusal instead of guessing. Truth: geometry outside the operator's
domain. Expected: `out_of_scope` or `form_violation` with the documented
reason. Coverage: M1 `holes_tilted_5_degrees`, `cross_hole_along_X`,
`audit_surfaces_stored_as_splines`, `faceted_holes`, `pocket_in_the_top_face`,
`slot_through_the_plate`. Gap: a distinct reason code for "no association
operator for this surface type" (G5); any mesh input refused at the door.

## Level 9. Adversarial cases
Tests: attempts to obtain a pass without a correct part. Truth: the attack
construction. Expected: fail at the right gate.
Coverage: scorer object-spoofing tests (trust boundary), 0.5.0 defect suite
(notches, pockets, cross bores, clipped corners), M1
`tolerances_inflated_1000_times`, `audit_pocket_5_microns_deep`,
`review_boss_on_top`, `review_closed_cavity`. Gaps for L5: hardcoded witness
against probes (M3), parameter renamed or hardcoded (G2 interface),
answers placed within a few eps of a limit (boundary-margin report,
EDR-004), structured rejects naming a superset of an MUS or every constraint.

## Contract-level artefacts (M2b)

| Artefact | Truth | Expected |
|---|---|---|
| Region sampling | several hand-computed points of `R_B` (vertices and interior) | all pass `holds` exactly |
| Either/or coupling (design note §4.2) | MCS sets {px, L} and {px, mx} derived by hand | both found; L and mx in `allowed_to_move`; T never |
| Several MUS (design note §6.3) | {C2, C5, C7} and {C1, C5, C7} derived by hand | both found; n and symmetry in none |
| Planted conflicts | MUS sets chosen first, numbers solved to realise them | enumerator returns exactly them; certificates verify |
| Near-contradiction | two constraints 1e-10 mm apart | discarded, not infeasible |
| Corrupted certificate | valid certificate with one multiplier changed | checker rejects |
