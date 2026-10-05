#!/usr/bin/env python3
"""Adversarial suite for the L5 observation map (milestone M1 exit gate).

Each case is a hand-built model with the outcome a careful engineer expects:
the verdict (ok, form_violation, out_of_scope, not_single_solid, build_error)
and, where the part is measurable, the contract variables. The map passes the
gate only if every case gives exactly that.

Design note section 7.2, plus the counterexamples of the four scorer review
rounds. Run it on every change to the map or to the measurement:

    python scripts/test_l5_observation.py [--out results/l5/m1-observation-suite.md]
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
NO_HOLES = {**ENVELOPE, "n": 0, "D": None, "mx": None, "my": None, "px": None, "py": None}


def holes_at(points: str, extra: str = "") -> str:
    return (HEAD + f'result = cq.Workplane("XY").box(100, 80, 4){extra}'
            + f'.faces(">Z").workplane().pushPoints({points}).hole(10)\n')


# name -> (code, expected verdict, expected values (a subset is enough), why this case exists)
CASES: dict[str, tuple[str, str, dict, str]] = {
    # --- parts the map must measure exactly
    "nominal": (BASE, "ok", NOMINAL, "the reference part"),
    "moved_off_the_origin": (BASE + "result = result.translate((123.5, -40.25, 9))\n", "ok", NOMINAL,
                             "position is not a contract variable in v1"),
    "turned_90_degrees_about_Z": (
        BASE + "result = result.rotate((0, 0, 0), (0, 0, 1), 90)\n", "ok",
        {"L": 80.0, "W": 100.0, "mx": 15.0, "my": 15.0, "px": 50.0, "py": 70.0, "n": 4},
        "L is read along X and W along Y: they swap, and a contract on L then fails by design"),
    "different_margins_in_X_and_Y": (
        holes_at("[(-30, -25), (-30, 25), (30, -25), (30, 25)]"), "ok",
        {**NOMINAL, "mx": 20.0, "px": 60.0}, "mx and my are separate variables in L5"),
    "pattern_shifted_1_mm_in_X": (
        holes_at("[(-34, -25), (-34, 25), (36, -25), (36, 25)]"), "ok",
        {"mx": 14.0, "my": 15.0, "px": 70.0, "py": 50.0, "n": 4,
         "rectangular": True, "centered": False, "symmetric": False},
        "mx is the smallest distance to a side face; an off-centre pattern is seen as such"),
    "one_hole_moved_2_mm": (
        holes_at("[(-35, -25), (-35, 25), (35, -25), (33, 25)]"), "ok",
        {"n": 4, "mx": 15.0, "px": 70.0, "rectangular": False, "symmetric": False},
        "four holes that are not the corners of a rectangle"),
    "three_holes": (holes_at("[(-35, -25), (-35, 25), (35, -25)]"), "ok",
                    {"n": 3, "D": 10.0, "rectangular": False, "symmetric": False}, "n is counted, not assumed"),
    "five_holes": (BASE + 'result = result.faces(">Z").workplane().hole(10)\n', "ok",
                   {"n": 5, "D": 10.0, "mx": 15.0, "px": 70.0, "rectangular": False, "centered": True,
                    "symmetric": True},
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
    # --- nothing to measure
    "two_solids": (
        BASE + 'result = cq.Compound.makeCompound([result.val(), cq.Solid.makeBox(5, 5, 5, cq.Vector(200, 0, 0))])\n',
        "not_single_solid", {}, "an unfused second body"),
    "no_result": (HEAD + 'plate = cq.Workplane("XY").box(100, 80, 4)\n', "build_error", {},
                  "the answer binds no part: gate G1, not the map"),
}


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

    from cad_spec.l5 import EPS_DIM_MM, EPS_FORM_MM
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
        bad += matches(got, want)
        failures += bool(bad)
        print(f"[{'BAD' if bad else 'ok '}] {name:36s} {got_verdict}" + ("".join(f"\n        {b}" for b in bad)))
        rows.append((name, verdict, got_verdict, "pass" if not bad else "FAIL", why))
    case_failures = failures - (not tolerance_ok)
    print(f"\n{len(CASES) - case_failures}/{len(CASES)} cases as expected")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# L5 observation map: adversarial suite (milestone M1)", "",
                 f"Scorer {SCORER_VERSION}. Dimension slack {EPS_DIM_MM:g} mm, form tolerance {EPS_FORM_MM:g} mm, "
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
