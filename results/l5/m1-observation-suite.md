# L5 observation map: adversarial suite (milestone M1)

Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported from the scorer.

**27 of 27 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.

| Case | Expected verdict | Verdict | Result | Why the case exists |
|---|---|---|---|---|
| `nominal` | ok | ok | pass | the reference part |
| `moved_off_the_origin` | ok | ok | pass | position is not a contract variable in v1 |
| `turned_90_degrees_about_Z` | ok | ok | pass | L is read along X and W along Y: they swap, and a contract on L then fails by design |
| `different_margins_in_X_and_Y` | ok | ok | pass | mx and my are separate variables in L5 |
| `pattern_shifted_1_mm_in_X` | ok | ok | pass | mx is the smallest distance to a side face; an off-centre pattern is seen as such |
| `one_hole_moved_2_mm` | ok | ok | pass | four holes that are not the corners of a rectangle |
| `three_holes` | ok | ok | pass | n is counted, not assumed |
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
| `two_solids` | not_single_solid | not_single_solid | pass | an unfused second body |
| `no_result` | build_error | build_error | pass | the answer binds no part: gate G1, not the map |
