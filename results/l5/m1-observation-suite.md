# L5 observation map: adversarial suite (milestone M1)

Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported from the scorer.

**58 of 58 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.

| Case | Expected verdict | Verdict | Result | Why the case exists |
|---|---|---|---|---|
| `nominal` | ok | ok | pass | the reference part |
| `moved_off_the_origin` | ok | ok | pass | position is not a contract variable in v1 |
| `turned_90_degrees_about_Z` | ok | ok | pass | L is read along X and W along Y: they swap, and a contract on L then fails by design |
| `turned_180_degrees_about_Z` | ok | ok | pass | the same part |
| `turned_270_degrees_about_Z` | ok | ok | pass | swapped, as at 90 degrees |
| `different_margins_in_X_and_Y` | ok | ok | pass | mx and my are separate variables in L5 |
| `pattern_shifted_1_mm_in_X` | ok | ok | pass | mx is the smallest distance to a side face; an off-centre pattern is seen as such |
| `one_hole_moved_2_mm` | ok | ok | pass | four holes that are not the corners of a rectangle |
| `three_holes` | ok | ok | pass | n is counted, not assumed |
| `one_hole_in_the_middle` | ok | ok | pass | one hole: the extents are zero, and the pattern is not a rectangle |
| `two_holes` | ok | ok | pass | px and py are extents; with two holes py is zero |
| `six_holes` | ok | ok | pass | px is the extent (70), not the spacing (35): `rectangular` is False, so it is not a pitch |
| `hole_1_micron_from_the_edge` | ok | ok | pass | a thin but real wall of material is measured normally |
| `five_holes` | ok | ok | pass | an extra through hole is measured (n = 5), not hidden; the contract n == 4 fails it |
| `no_holes` | ok | ok | pass | hole variables do not exist: None, never zero |
| `tolerances_inflated_1000_times` | ok | ok | pass | a correct part with sloppy stored tolerances is still correct |
| `fillets_on_the_vertical_edges` | form_violation | form_violation | pass | bounding box and holes unchanged, so the variables are measured; the fillets fail the form |
| `chamfers_on_the_top_edges` | form_violation | form_violation | pass | same: measured, not accepted |
| `pocket_in_the_top_face` | form_violation | form_violation | pass | an extra pocket leaves every variable measurable and fails the form |
| `slot_through_the_plate` | form_violation | form_violation | pass | an extra slot |
| `all_holes_blind` | form_violation | form_violation | pass | a blind hole is not a through hole: n = 0 |
| `one_hole_blind` | form_violation | form_violation | pass | only through holes are counted |
| `faceted_holes` | form_violation | form_violation | pass | a 24-sided cut is not a hole |
| `turned_10_degrees_about_Z` | form_violation | form_violation | pass | side faces off the axes |
| `audit_pocket_5_microns_deep` | form_violation | form_violation | pass | scorer review round 2 |
| `audit_bore_mouth_cut_1.2e-6_deep` | form_violation | form_violation | pass | scorer review round 4: edges off their faces |
| `audit_surfaces_stored_as_splines` | form_violation | form_violation | pass | only true planes and cylinders are trusted: a known false rejection, kept on purpose. (The kernel pads a spline bounding box by 2e-7 mm, so L, W, T are not asserted here) |
| `cross_hole_along_X` | out_of_scope | out_of_scope | pass | a bore along X: not one of the plate's holes |
| `counterbored_holes` | out_of_scope | out_of_scope | pass | two coaxial cylinders: which one is D? |
| `holes_of_two_diameters` | out_of_scope | out_of_scope | pass | D is not one number |
| `holes_tilted_5_degrees` | out_of_scope | out_of_scope | pass | a hole that is not along Z |
| `review_holes_tilted_1e-8_rad` | out_of_scope | out_of_scope | pass | was `ok` with mx = 15: at the top face the real margin is 14.99999998. Any tilt is refused |
| `review_holes_tilted_1e-6_rad` | out_of_scope | out_of_scope | pass | was form_violation with hole values reported |
| `review_step_of_1e-6_in_radius` | out_of_scope | out_of_scope | pass | was form_violation with D = 10.000002: the hole grouping rounds diameters to 1e-4 and hid the step |
| `review_offset_step` | out_of_scope | out_of_scope | pass | two cylinders 1.1 micron off axis: still one stepped passage |
| `review_first_hole_1e-8_larger` | out_of_scope | out_of_scope | pass | was `ok` with D taken from whichever hole came first |
| `review_last_hole_1e-8_larger` | out_of_scope | out_of_scope | pass | the same part, other order: the verdict must not depend on it |
| `review_cross_bore_0.2_micron` | out_of_scope | out_of_scope | pass | was form_violation: the probe crossed the tiny bore and missed it |
| `review_holes_of_0.5_micron` | out_of_scope | out_of_scope | pass | real holes, too small to classify: below the supported size, so refused, not reported as n = 0 |
| `review_second_cut_0.4_micron_off` | out_of_scope | out_of_scope | pass | a hole made of two cylinders 0.4 micron apart |
| `review_hole_breaking_out_of_a_side` | form_violation | form_violation | pass | a partial wall is not a through hole |
| `review_two_overlapping_holes` | form_violation | form_violation | pass | two separate holes that overlap: a form matter, not a stepped hole |
| `review_boss_on_top` | form_violation | form_violation | pass | the boss raises the envelope: the reported numbers are those of the whole solid, for diagnosis only |
| `review_closed_cavity` | form_violation | form_violation | pass | a void inside the plate |
| `boundary_tilt_1e-12_rad_is_accepted` | ok | ok | pass | floating-point slack: every variable is still right to 1e-10 mm (T reads 4.00000000001) |
| `boundary_tilt_1e-11_rad_is_refused` | out_of_scope | out_of_scope | pass | ten times the slack |
| `boundary_axis_on_the_other_rim` | form_violation | form_violation | pass | two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole |
| `boundary_axis_inside_the_other_rim` | out_of_scope | out_of_scope | pass | 4.999 mm apart: each axis is inside the other cylinder |
| `boundary_holes_of_0.009_mm` | out_of_scope | out_of_scope | pass | just under the supported size |
| `boundary_holes_of_0.010_mm` | ok | ok | pass | exactly the supported size: measured |
| `boundary_fillets_of_0.009_mm` | out_of_scope | out_of_scope | pass | a fillet under the supported size is refused before the form check can call it a fillet |
| `boundary_fillets_of_0.011_mm` | form_violation | form_violation | pass | just over it: measured, and the form fails |
| `boundary_cross_bore_of_0.010_mm` | out_of_scope | out_of_scope | pass | at the supported size the off-axis rule refuses it |
| `boundary_diameters_5e-10_apart` | ok | ok | pass | inside the dimension slack: one D |
| `boundary_diameters_written_1e-9_apart` | out_of_scope | out_of_scope | pass | written exactly 1e-9 apart, measured 1.00000008e-9 apart: values are binary doubles, so this is refused |
| `boundary_diameters_2e-9_apart` | out_of_scope | out_of_scope | pass | outside the slack |
| `two_solids` | not_single_solid | not_single_solid | pass | an unfused second body |
| `no_result` | build_error | build_error | pass | the answer binds no part: gate G1, not the map |
