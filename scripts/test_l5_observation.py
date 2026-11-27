#!/usr/bin/env python3
"""Adversarial suite for the L5 observation map (milestone M1 exit gate).

Each case is a hand-built model with the outcome a careful engineer expects:
the verdict (ok, form_violation, out_of_scope, not_single_solid, build_error)
and, where the part is measurable, the contract variables. The map passes the
gate only if every case gives exactly that.

Design note section 7.2, plus the counterexamples of the four scorer review
rounds. Run it on every change to the map or to the measurement:

    python scripts/test_l5_observation.py [--out results/l5/m1-observation-suite.md]

results/l5/m1-observation-suite.md is generated: this script rewrites it in
place and writes a header saying so (CLAUDE.md, rules 3 and 8 name this one
file). Verification runs write --out to a temporary folder.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

HEAD = "import cadquery as cq\n"
CORNERS = "[(-35, -25), (-35, 25), (35, -25), (35, 25)]"
# The reference part: 100 x 80 x 4 plate, four 10 mm through holes, 15 mm from the side faces.
BASE = HEAD + f'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane().pushPoints({CORNERS}).hole(10)\n'
NOMINAL = {"L": 100.0, "W": 80.0, "T": 4.0, "n": 4, "D": 10.0, "mx": 15.0, "my": 15.0, "px": 70.0, "py": 50.0,
           "rectangular": True, "centered": True, "symmetric": True}
ENVELOPE = {"L": 100.0, "W": 80.0, "T": 4.0}
NO_HOLES = {**ENVELOPE, "n": 0, "D": None, "mx": None, "my": None, "px": None, "py": None,
            "rectangular": False, "centered": False, "symmetric": False}
ALL_KEYS = set(NOMINAL)


def full(**changed) -> dict:
    """The reference values with some of them changed: a complete expectation."""
    return {**NOMINAL, **changed}



def holes_at(points: str, extra: str = "") -> str:
    return (HEAD + f'result = cq.Workplane("XY").box(100, 80, 4){extra}'
            + f'.faces(">Z").workplane().pushPoints({points}).hole(10)\n')


def shifted(s: float) -> str:
    """The reference pattern moved by (s, s): its centre is s * sqrt(2) from the plate centre."""
    return holes_at(f"[(-35+{s!r}, -25+{s!r}), (-35+{s!r}, 25+{s!r}), (35+{s!r}, -25+{s!r}), (35+{s!r}, 25+{s!r})]")


def split_hole(lower: tuple[float, ...], upper: tuple[float, ...], d: float = 10) -> str:
    """Three corner holes of diameter d, and a fourth hole cut as two half-depth cylinders,
    (x, diameter[, y]) = lower for z in [-2, 0] and upper for z in [0, 2] (y is 25 unless
    given), kept as separate faces (clean=False)."""
    (xl, dl, yl), (xu, du, yu) = (*lower, 25)[:3], (*upper, 25)[:3]
    return (HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
            f'.pushPoints([(-35, -25), (-35, 25), (35, -25)]).hole({d!r})\n'
            f'result = result.cut(cq.Workplane("XY").workplane(offset=-3).center({xl!r}, {yl!r})'
            f'.circle({dl / 2!r}).extrude(3), clean=False)\n'
            f'result = result.cut(cq.Workplane("XY").center({xu!r}, {yu!r})'
            f'.circle({du / 2!r}).extrude(3), clean=False)\n')


def split_holes(plain: str, *halves: tuple[tuple[float, ...], tuple[float, ...]]) -> str:
    """10 mm holes at the plain points, and one hole per entry of halves cut as two half-depth
    cylinders, (x, y[, diameter]) = lower for z in [-2, 0] and upper for z in [0, 2] (diameter 10
    unless given), kept as separate faces (clean=False)."""
    code = HEAD + f'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane().pushPoints({plain}).hole(10)\n'
    for lower, upper in halves:
        (xl, yl, dl), (xu, yu, du) = (*lower, 10)[:3], (*upper, 10)[:3]
        code += (f'result = result.cut(cq.Workplane("XY").workplane(offset=-3).center({xl!r}, {yl!r})'
                 f'.circle({dl / 2!r}).extrude(3), clean=False)\n'
                 f'result = result.cut(cq.Workplane("XY").center({xu!r}, {yu!r})'
                 f'.circle({du / 2!r}).extrude(3), clean=False)\n')
    return code


# name -> (code, expected verdict, expected values (a subset is enough), why this case exists)
CASES: dict[str, tuple[str, str, dict, str]] = {
    # --- parts the map must measure exactly
    "nominal": (BASE, "ok", NOMINAL, "the reference part"),
    "moved_off_the_origin": (BASE + "result = result.translate((123.5, -40.25, 9))\n", "ok", NOMINAL,
                             "position is not a contract variable in v1"),
    "turned_90_degrees_about_Z": (
        BASE + "result = result.rotate((0, 0, 0), (0, 0, 1), 90)\n", "ok",
        full(L=80.0, W=100.0, px=50.0, py=70.0),
        "L is read along X and W along Y: they swap, and a contract on L then fails by design"),
    "turned_180_degrees_about_Z": (BASE + "result = result.rotate((0, 0, 0), (0, 0, 1), 180)\n", "ok", NOMINAL,
                                   "the same part"),
    "turned_270_degrees_about_Z": (BASE + "result = result.rotate((0, 0, 0), (0, 0, 1), 270)\n", "ok",
                                   full(L=80.0, W=100.0, px=50.0, py=70.0), "swapped, as at 90 degrees"),
    "different_margins_in_X_and_Y": (
        holes_at("[(-30, -25), (-30, 25), (30, -25), (30, 25)]"), "ok",
        full(mx=20.0, px=60.0), "mx and my are separate variables in L5"),
    "pattern_shifted_1_mm_in_X": (
        holes_at("[(-34, -25), (-34, 25), (36, -25), (36, 25)]"), "ok",
        full(mx=14.0, centered=False, symmetric=False),
        "mx is the smallest distance to a side face; an off-centre pattern is seen as such"),
    "one_hole_moved_2_mm": (
        holes_at("[(-35, -25), (-35, 25), (35, -25), (33, 25)]"), "ok",
        full(rectangular=False, centered=False, symmetric=False),
        "four holes that are not the corners of a rectangle"),
    "three_holes": (holes_at("[(-35, -25), (-35, 25), (35, -25)]"), "ok",
                    full(n=3, rectangular=False, centered=False, symmetric=False), "n is counted, not assumed"),
    "one_hole_in_the_middle": (holes_at("[(0, 0)]"), "ok",
                               full(n=1, mx=50.0, my=40.0, px=0.0, py=0.0, rectangular=False),
                               "one hole: the extents are zero, and the pattern is not a rectangle"),
    "two_holes": (holes_at("[(-35, 0), (35, 0)]"), "ok", full(n=2, my=40.0, py=0.0, rectangular=False),
                  "px and py are extents; with two holes py is zero"),
    "six_holes": (holes_at("[(-35, -25), (-35, 25), (0, -25), (0, 25), (35, -25), (35, 25)]"), "ok",
                  full(n=6, rectangular=False),
                  "px is the extent (70), not the spacing (35): `rectangular` is False, so it is not a pitch"),
    "hole_1_micron_from_the_edge": (
        holes_at("[(-44.999, -25), (-44.999, 25), (44.999, -25), (44.999, 25)]"), "ok",
        full(mx=5.001, px=89.998), "a thin but real wall of material is measured normally"),
    "five_holes": (BASE + 'result = result.faces(">Z").workplane().hole(10)\n', "ok",
                   full(n=5, rectangular=False),
                   "an extra through hole is measured (n = 5), not hidden; the contract n == 4 fails it"),
    "no_holes": (HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n', "ok", NO_HOLES,
                 "hole variables do not exist: None, never zero"),
    "tolerances_inflated_1000_times": (
        BASE + "from OCP.ShapeFix import ShapeFix_ShapeTolerance\nshape = result.val()\n"
               "ShapeFix_ShapeTolerance().SetTolerance(shape.wrapped, 1e-3)\nresult = shape\n",
        "ok", NOMINAL, "a correct part with sloppy stored tolerances is still correct"),
    # --- measurable, but with a feature nobody asked for: measurable does not mean acceptable
    "fillets_on_the_vertical_edges": (
        holes_at(CORNERS, '.edges("|Z").fillet(3)'), "form_violation", NOMINAL,
        "bounding box and holes unchanged, so the variables are measured; the fillets fail the form"),
    "chamfers_on_the_top_edges": (
        holes_at(CORNERS, '.faces(">Z").edges().chamfer(0.5)'), "form_violation", NOMINAL,
        "same: measured, not accepted"),
    "pocket_in_the_top_face": (
        BASE + 'result = result.cut(cq.Workplane("XY").box(20, 10, 2).translate((0, 0, 2)))\n',
        "form_violation", NOMINAL, "an extra pocket leaves every variable measurable and fails the form"),
    "slot_through_the_plate": (
        BASE + 'result = result.cut(cq.Workplane("XY").box(20, 4, 10))\n',
        "form_violation", NOMINAL, "an extra slot"),
    "all_holes_blind": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
               f".pushPoints({CORNERS}).hole(10, 2)\n",
        "form_violation", NO_HOLES, "a blind hole is not a through hole: n = 0"),
    "one_hole_blind": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10, 2)\n',
        "form_violation", {"n": 3}, "only through holes are counted"),
    "faceted_holes": (
        HEAD + f'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane().pushPoints({CORNERS})'
               ".polygon(24, 10).cutThruAll()\n",
        "form_violation", NO_HOLES, "a 24-sided cut is not a hole"),
    "turned_10_degrees_about_Z": (BASE + "result = result.rotate((0, 0, 0), (0, 0, 1), 10)\n",
                                  "form_violation", {"T": 4.0, "n": 4}, "side faces off the axes"),
    "audit_pocket_5_microns_deep": (
        BASE + 'result = result.cut(cq.Workplane("XY").box(50, 50, 0.0049).translate((0, 0, 1.99755)))\n',
        "form_violation", NOMINAL, "scorer review round 2"),
    "audit_bore_mouth_cut_1.2e-6_deep": (
        BASE + 'result = result.cut(cq.Workplane("XY").workplane(offset=1.9999988).center(35, 25)'
               ".circle(5.0000004).extrude(1.0000012))\n",
        "form_violation", ENVELOPE, "scorer review round 4: edges off their faces"),
    "audit_surfaces_stored_as_splines": (
        BASE + "result = result.val().toNURBS()\n", "form_violation",
        {"n": 0, "D": None, "mx": None, "px": None},
        "only true planes and cylinders are trusted: a known false rejection, kept on purpose. "
        "(The kernel pads a spline bounding box by 2e-7 mm, so L, W, T are not asserted here)"),
    "cross_hole_along_X": (
        BASE + 'result = result.cut(cq.Workplane("YZ").circle(1).extrude(200, both=True))\n',
        "out_of_scope", ENVELOPE, "a bore along X: not one of the plate's holes"),
    # --- a variable cannot be measured without guessing: the map refuses
    "counterbored_holes": (
        HEAD + f'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane().pushPoints({CORNERS})'
               ".cboreHole(10, 14, 1.5)\n",
        "out_of_scope", ENVELOPE, "two coaxial cylinders: which one is D?"),
    "holes_of_two_diameters": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(12)\n',
        "out_of_scope", {**ENVELOPE, "n": 4}, "D is not one number"),
    "holes_tilted_5_degrees": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               f"for x, y in {CORNERS}:\n"
               '    tool = cq.Workplane("XY").circle(5).extrude(20, both=True).rotate((0, 0, 0), (0, 1, 0), 5)\n'
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "out_of_scope", ENVELOPE, "a hole that is not along Z"),
    # --- found by the external review of this map (5 October 2026)
    "review_holes_tilted_1e-8_rad": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               f"for x, y in {CORNERS}:\n"
               '    tool = cq.Workplane("XY").circle(5).extrude(10, both=True)'
               ".rotate((0, 0, 0), (0, 1, 0), 5.729577951308232e-07)\n"
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "out_of_scope", {"L": 100.0, "W": 80.0},
        "was `ok` with mx = 15: at the top face the real margin is 14.99999998. Any tilt is refused"),
    "review_holes_tilted_1e-6_rad": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               f"for x, y in {CORNERS}:\n"
               '    tool = cq.Workplane("XY").circle(5).extrude(10, both=True)'
               ".rotate((0, 0, 0), (0, 1, 0), 5.729577951308232e-05)\n"
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "out_of_scope", {"L": 100.0, "W": 80.0}, "was form_violation with hole values reported"),
    "review_step_of_1e-6_in_radius": (
        BASE + f'result = result.cut(cq.Workplane("XY").workplane(offset=1).pushPoints({CORNERS})'
               ".circle(5.000001).extrude(2))\n",
        "out_of_scope", ENVELOPE,
        "was form_violation with D = 10.000002: the hole grouping rounds diameters to 1e-4 and hid the step"),
    "review_offset_step": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               'result = result.cut(cq.Workplane("XY").workplane(offset=-3).circle(5).extrude(4))\n'
               'result = result.cut(cq.Workplane("XY").workplane(offset=1).center(0.0011, 0).circle(7).extrude(2))\n',
        "out_of_scope", ENVELOPE, "two cylinders 1.1 micron off axis: still one stepped passage"),
    "review_first_hole_1e-8_larger": (
        holes_at("[(-35, 25), (35, -25), (35, 25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(-35, -25)]).hole(10.00000001)\n',
        "out_of_scope", {**ENVELOPE, "n": 4}, "was `ok` with D taken from whichever hole came first"),
    "review_last_hole_1e-8_larger": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.00000001)\n',
        "out_of_scope", {**ENVELOPE, "n": 4}, "the same part, other order: the verdict must not depend on it"),
    "review_cross_bore_0.2_micron": (
        BASE + 'result = result.cut(cq.Workplane("YZ").circle(0.0001).extrude(200, both=True))\n',
        "out_of_scope", ENVELOPE, "was form_violation: the probe crossed the tiny bore and missed it"),
    "review_holes_of_0.5_micron": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
               f".pushPoints({CORNERS}).hole(0.0005)\n",
        "out_of_scope", ENVELOPE,
        "real holes, too small to classify: below the supported size, so refused, not reported as n = 0"),
    "review_second_cut_0.4_micron_off": (
        BASE + 'result = result.cut(cq.Workplane("XY").center(35.0004, 25).circle(5).extrude(10, both=True))\n',
        "out_of_scope", ENVELOPE, "a hole made of two cylinders 0.4 micron apart"),
    "review_hole_breaking_out_of_a_side": (
        holes_at("[(48, 0)]"), "form_violation", {**ENVELOPE, "n": 0},
        "a partial wall is not a through hole"),
    "review_two_overlapping_holes": (
        holes_at("[(-3, 0), (3, 0)]"), "form_violation", {**ENVELOPE, "n": 0},
        "two separate holes that overlap: a form matter, not a stepped hole"),
    "review_boss_on_top": (
        BASE + 'result = result.union(cq.Workplane("XY").workplane(offset=2).circle(3).extrude(2))\n',
        "form_violation", {"L": 100.0, "W": 80.0, "T": 6.0, "n": 0},
        "the boss raises the envelope: the reported numbers are those of the whole solid, for diagnosis only"),
    "review_closed_cavity": (
        BASE + 'result = result.cut(cq.Workplane("XY").box(4, 4, 1))\n', "form_violation", NOMINAL,
        "a void inside the plate"),
    # --- the exact boundaries of the rules, asked for by the second review
    "boundary_tilt_1e-12_rad_is_accepted": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               f"for x, y in {CORNERS}:\n"
               '    tool = cq.Workplane("XY").circle(5).extrude(10, both=True)'
               ".rotate((0, 0, 0), (0, 1, 0), 5.729577951308232e-11)\n"
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "ok", NOMINAL, "floating-point slack: every variable is still right to 1e-10 mm (T reads 4.00000000001)"),
    "boundary_tilt_1e-11_rad_is_refused": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               f"for x, y in {CORNERS}:\n"
               '    tool = cq.Workplane("XY").circle(5).extrude(10, both=True)'
               ".rotate((0, 0, 0), (0, 1, 0), 5.729577951308232e-10)\n"
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "out_of_scope", {"L": 100.0, "W": 80.0}, "ten times the slack"),
    "boundary_diagonal_tilt_1.3e-12_rad_is_refused": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               f"for x, y in {CORNERS}:\n"
               '    tool = cq.Workplane("XY").circle(5).extrude(8, both=True)'
               ".rotate((0, 0, 0), (1, 1, 0), 7.448451336700702e-11)\n"
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "out_of_scope", {"L": 100.0, "W": 80.0},
        "third review: each direction component is 9.2e-13, under the slack, but the angle is 1.3e-12"),
    "boundary_diagonal_tilt_0.9e-12_rad_is_accepted": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               f"for x, y in {CORNERS}:\n"
               '    tool = cq.Workplane("XY").circle(5).extrude(8, both=True)'
               ".rotate((0, 0, 0), (1, 1, 0), 5.156620156177409e-11)\n"
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "ok", NOMINAL, "the same diagonal tilt inside the slack"),
    "boundary_diagonal_tilt_1.05e-12_rad_is_refused": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
               f"for x, y in {CORNERS}:\n"
               '    tool = cq.Workplane("XY").circle(5).extrude(8, both=True)'
               ".rotate((0, 0, 0), (1, 1, 0), 6.016056848873644e-11)\n"
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "out_of_scope", {"L": 100.0, "W": 80.0},
        "fourth review: components 7.4e-13, angle 1.05e-12; the diagonal limit is bracketed to [1.0e-12, 1.05e-12)"),
    "boundary_pattern_0.99e-7_off_centre_is_centered": (
        shifted(0.7e-7), "ok", full(mx=15 - 0.7e-7, my=15 - 0.7e-7, symmetric=False),
        "pattern moved (7e-8, 7e-8): 0.99e-7 from the centre in a straight line, inside the form tolerance. "
        "A mirrored hole is 1.4e-7 off, so not symmetric"),
    "boundary_pattern_1.02e-7_off_centre_is_not_centered": (
        shifted(0.72e-7), "ok", full(mx=15 - 0.72e-7, my=15 - 0.72e-7, centered=False, symmetric=False),
        "fourth review: 7.2e-8 along each axis, under the tolerance, but 1.02e-7 in a straight line, over it"),
    "boundary_axis_on_the_other_rim": (
        holes_at("[(-2.5, 0), (2.5, 0)]"), "form_violation", {**ENVELOPE, "n": 0},
        "two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole"),
    "boundary_axis_inside_the_other_rim": (
        holes_at("[(-2.4995, 0), (2.4995, 0)]"), "out_of_scope", ENVELOPE,
        "4.999 mm apart: each axis is inside the other cylinder"),
    "boundary_holes_of_0.009_mm": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
               f".pushPoints({CORNERS}).hole(0.009)\n",
        "out_of_scope", ENVELOPE, "just under the supported size"),
    "boundary_holes_of_0.010_mm": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
               f".pushPoints({CORNERS}).hole(0.01)\n",
        "ok", full(D=0.01), "exactly the supported size: measured"),
    "boundary_fillets_of_0.009_mm": (
        holes_at(CORNERS, '.edges("|Z").fillet(0.0045)'), "out_of_scope", ENVELOPE,
        "a fillet under the supported size is refused before the form check can call it a fillet"),
    "boundary_fillets_of_0.011_mm": (
        holes_at(CORNERS, '.edges("|Z").fillet(0.0055)'), "form_violation", NOMINAL,
        "just over it: measured, and the form fails"),
    "boundary_cross_bore_of_0.010_mm": (
        BASE + 'result = result.cut(cq.Workplane("YZ").circle(0.005).extrude(200, both=True))\n',
        "out_of_scope", ENVELOPE, "at the supported size the off-axis rule refuses it"),
    "boundary_diameters_5e-10_apart": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.0000000005)\n',
        "ok", NOMINAL, "inside the dimension slack: one D"),
    "boundary_diameters_written_1e-9_apart": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.000000001)\n',
        "out_of_scope", {**ENVELOPE, "n": 4},
        "written exactly 1e-9 apart, measured 1.00000008e-9 apart: values are binary doubles, so this is refused"),
    "boundary_diameters_2e-9_apart": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.000000002)\n',
        "out_of_scope", {**ENVELOPE, "n": 4}, "outside the slack"),
    # --- found by the fourth review (27 November 2026): one hole made of two faces
    "review_hole_split_across_position_key": (
        split_hole((20.0004999996, 10), (20.0005000004, 10)), "out_of_scope", ENVELOPE,
        "two halves of one hole, axes 8e-10 apart on either side of x = 20.0005: was `ok` with n = 3"),
    "review_hole_split_across_position_key_under_the_spread_limit": (
        split_hole((20.0004999998, 10), (20.0005000002, 10)), "out_of_scope", ENVELOPE,
        "axes 4e-10 apart, inside the spread limit, on either side of x = 20.0005: only the grouping rule refuses it"),
    "review_hole_split_across_diameter_key": (
        split_hole((20, 10.0000499996), (20, 10.0000500004), d=10.00005), "out_of_scope", ENVELOPE,
        "two halves of one hole, diameters 8e-10 apart on either side of 10.00005: was `ok` with n = 3"),
    "review_hole_halves_8e-8_apart_at_a_corner": (
        split_hole((35.0, 10), (35.00000008, 10)), "out_of_scope", ENVELOPE,
        "was `ok` with mx = 14.99999992 in this cut order and 15.0 in the other: the axis was the first face's"),
    "review_hole_halves_8e-8_apart_other_order": (
        split_hole((35.00000008, 10), (35.0, 10)), "out_of_scope", ENVELOPE,
        "the same part, other order: the verdict must not depend on it"),
    "boundary_hole_halves_0.45e-9_apart": (
        split_hole((35.0, 10), (35.00000000045, 10)), "ok", NOMINAL,
        "inside the spread limit (half the dimension slack, 0.5e-9): the position is right to 0.5e-9 "
        "whichever face is read"),
    "boundary_hole_halves_0.55e-9_apart": (
        split_hole((35.0, 10), (35.00000000055, 10)), "out_of_scope", ENVELOPE, "just outside the spread limit"),
    "boundary_hole_halves_0.57e-9_apart_on_the_diagonal": (
        split_hole((35.0, 10, 25.0), (35.0000000004, 10, 25.0000000004)), "out_of_scope", ENVELOPE,
        "4e-10 along X and along Y, each inside the limit; 0.57e-9 in a straight line, outside it"),
    "review_two_holes_with_halves_0.45e-9_apart": (
        split_holes("[(-35, -25), (35, -25)]",
                    ((-35.0, 25), (-35.00000000045, 25)), ((35.0, 25), (35.00000000045, 25))),
        "ok", NOMINAL,
        "two holes split on X in opposite directions: whichever faces are read, px is within 0.9e-9 of 70"),
    "review_two_holes_with_halves_0.45e-9_apart_other_order": (
        split_holes("[(-35, -25), (35, -25)]",
                    ((-35.00000000045, 25), (-35.0, 25)), ((35.00000000045, 25), (35.0, 25))),
        "ok", NOMINAL, "the same part, other cut order"),
    "review_two_holes_with_halves_0.49e-9_apart_on_the_diagonal": (
        split_holes("[(-35, 25), (35, -25)]", ((-35.0, -25.0), (-35.00000000035, -25.00000000035)),
                    ((35.0, 25.0), (35.00000000035, 25.00000000035))),
        "ok", NOMINAL,
        "opposite corners split outwards by (3.5e-10, 3.5e-10): px and py are each within 0.7e-9 of the nominal"),
    "review_face_diameters_spread_over_two_holes": (
        split_holes("[(35, -25), (35, 25)]", ((-35, -25, 10.0), (-35, -25, 10.0000000009)),
                    ((-35, 25, 9.9999999991), (-35, 25, 10.0))),
        "out_of_scope", {**ENVELOPE, "n": 4},
        "faces from 9.9999999991 to 10.0000000009: was `ok` with D = 10.0000000009, "
        "1.8e-9 from a face of the other hole"),
    "review_face_diameters_spread_over_two_holes_other_order": (
        split_holes("[(35, -25), (35, 25)]", ((-35, -25, 10.0000000009), (-35, -25, 10.0)),
                    ((-35, 25, 9.9999999991), (-35, 25, 10.0))),
        "out_of_scope", {**ENVELOPE, "n": 4}, "the same faces, other cut order: was `ok` with D = 10.0"),
    "boundary_face_diameters_0.9e-9_apart_over_two_holes": (
        split_holes("[(35, -25), (35, 25)]", ((-35, -25, 10.0), (-35, -25, 10.0000000009)),
                    ((-35, 25, 10.0), (-35, 25, 10.0000000009))),
        "ok", NOMINAL, "faces from 10 to 10.0000000009, inside the slack: D is right to 1e-9 whichever face is read"),
    # --- nothing to measure
    "two_solids": (
        BASE + 'result = cq.Compound.makeCompound([result.val(), cq.Solid.makeBox(5, 5, 5, cq.Vector(200, 0, 0))])\n',
        "not_single_solid", {}, "an unfused second body"),
    "no_result": (HEAD + 'plate = cq.Workplane("XY").box(100, 80, 4)\n', "build_error", {},
                  "the answer binds no part: gate G1, not the map"),
}


# Cases built from separate faces: the rule their refusal must come from (None
# for an `ok` case), the number of holes the measurement must make (five for
# the grouping rule, so the map's copy of the grouping key keeps agreeing with
# the measurement), and the number of concave cylinder faces the kernel must
# keep (one more per split hole, or the case would test nothing).
REASONS: dict[str, tuple[str | None, int | None, int]] = {
    "review_hole_split_across_position_key": ("two hole groups", 5, 5),
    "review_hole_split_across_position_key_under_the_spread_limit": ("two hole groups", 5, 5),
    "review_hole_split_across_diameter_key": ("two hole groups", 5, 5),
    "review_face_diameters_spread_over_two_holes": ("different diameters", None, 6),
    "review_face_diameters_spread_over_two_holes_other_order": ("different diameters", None, 6),
    "boundary_face_diameters_0.9e-9_apart_over_two_holes": (None, None, 6),
    "review_hole_halves_8e-8_apart_at_a_corner": ("axes more than", None, 5),
    "review_hole_halves_8e-8_apart_other_order": ("axes more than", None, 5),
    "boundary_hole_halves_0.45e-9_apart": (None, None, 5),
    "boundary_hole_halves_0.55e-9_apart": ("axes more than", None, 5),
    "boundary_hole_halves_0.57e-9_apart_on_the_diagonal": ("axes more than", None, 5),
    "review_two_holes_with_halves_0.45e-9_apart": (None, None, 6),
    "review_two_holes_with_halves_0.45e-9_apart_other_order": (None, None, 6),
    "review_two_holes_with_halves_0.49e-9_apart_on_the_diagonal": (None, None, 6),
}


def measured(code: str) -> tuple[int, int]:
    """Holes made by the strict measurement, and concave Z cylinder faces it saw."""
    from cad_spec.measure import build_and_measure

    m = build_and_measure(code, strict=True)
    return len(m.holes), len(m.scope_axes or [])


def run(code: str) -> tuple[str, dict, str]:
    from cad_spec.l5 import observe_code
    from cad_spec.measure import BuildError

    try:
        obs = observe_code(code)
    except BuildError as exc:
        return "build_error", {}, str(exc)[:80]
    return obs.status, dict(obs.values), obs.reason


def matches(got: dict, want: dict) -> list[str]:
    bad = []
    for key, value in want.items():
        have = got.get(key, "absent")
        same = (abs(have - value) <= 1e-9 if isinstance(value, float) and isinstance(have, (int, float))
                and not isinstance(have, bool) else have == value and type(have) is type(value))
        if not same:
            bad.append(f"{key}: expected {value!r}, measured {have!r}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write the result table to this markdown file")
    args = ap.parse_args()

    from cad_spec.l5 import EPS_DIM_MM, EPS_FORM_MM, OBSERVATION_VERSION
    from cad_spec.measure import FORM_LINEAR_TOL
    from cad_spec.rubric import SCORER_VERSION, TOLERANCES

    rows, failures = [], 0
    # The map must use the scorer's own tolerances, not a copy of them.
    tolerance_ok = TOLERANCES[SCORER_VERSION].eps == EPS_DIM_MM and EPS_FORM_MM == FORM_LINEAR_TOL
    failures += not tolerance_ok
    print(f"[{'ok ' if tolerance_ok else 'BAD'}] tolerances are the scorer's: "
          f"dimension slack {EPS_DIM_MM:g} mm, form {EPS_FORM_MM:g} mm (scorer {SCORER_VERSION})")
    for name, (code, verdict, want, why) in CASES.items():
        got_verdict, got, reason = run(code)
        bad = ([f"verdict: expected {verdict}, got {got_verdict} ({reason})"] if got_verdict != verdict else [])
        if verdict == "ok" and set(want) != ALL_KEYS:
            bad.append("an `ok` case must state every variable")
        bad += matches(got, want)
        if name in REASONS:
            phrase, holes, faces = REASONS[name]
            got_holes, got_faces = measured(code)
            if phrase is not None and phrase not in reason:
                bad.append(f"reason: expected the rule '{phrase}', got '{reason}'")
            if holes is not None and got_holes != holes:
                bad.append(f"the measurement made {got_holes} holes, expected {holes}")
            if got_faces != faces:
                bad.append(f"the kernel kept {got_faces} cylinder faces, expected {faces}: the case tests nothing")
        failures += bool(bad)
        print(f"[{'BAD' if bad else 'ok '}] {name:36s} {got_verdict}" + ("".join(f"\n        {b}" for b in bad)))
        rows.append((name, verdict, got_verdict, "pass" if not bad else "FAIL", why))
    case_failures = failures - (not tolerance_ok)
    print(f"\n{len(CASES) - case_failures}/{len(CASES)} cases as expected")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# L5 observation map: adversarial suite (milestone M1)", "",
                 "Generated by `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`. "
                 "Do not edit by hand: rerun the script.", "",
                 f"Observation version {OBSERVATION_VERSION}. Scorer {SCORER_VERSION}. "
                 f"Dimension slack {EPS_DIM_MM:g} mm, form tolerance {EPS_FORM_MM:g} mm, "
                 "both imported from the scorer.", "",
                 f"**{len(CASES) - case_failures} of {len(CASES)} cases as expected.** "
                 "Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.", "",
                 "| Case | Expected verdict | Verdict | Result | Why the case exists |", "|---|---|---|---|---|"]
        lines += [f"| `{n}` | {e} | {g} | {r} | {w} |" for n, e, g, r, w in rows]
        out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {out}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
