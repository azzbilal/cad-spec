"""Prove the reward function works, with no model in the loop.

Every entry below is a hand-written answer with a known correct score AND a
known set of failing checks. Pinning the failing checks, not just the total,
is what catches a scorer that reaches the right number for the wrong reason.
If this file passes, the rubric is trustworthy enough to put a model behind.

Run (needs only cadquery, no verifiers, no install):
    pip install cadquery
    python scripts/test_rubric.py

k/9 scale: 9 requirements (R1-R3 dimensions, R4a/R4b holes, R5 pattern vs
origin, R6 material volume, R7 edge margin, R8 Z datum). Any failed gate zeroes the raw
reward; the environment-level reward then applies a 0.05 parse floor to code
that built. These expectations are raw-rubric scores.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple

# Source checkout: the package lives in environments/cad_spec, not the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "environments" / "cad_spec"))

from cad_spec.rubric import score
from cad_spec.tasks import TASKS, reference_solution


class Case(NamedTuple):
    expected: str                 # "9/9", "7/9", "0.0"
    code: str
    fails: frozenset[str] = frozenset()  # exact set of FAILED check names; gates included


def _f(*names: str) -> frozenset[str]:
    return frozenset(names)


SPEC = TASKS[0]  # 80 x 60 x 6, four 6.5 mm holes, 10 mm margin

ALL_REQS = ("R1:length", "R2:width", "R3:thickness", "R4a:hole_count",
            "R4b:hole_diameter", "R5:hole_pattern", "R6:material", "R7:edge_margin",
            "R8:z_datum")
BUILD = _f("build")  # code did not produce a measurable solid

CASES: dict[str, Case] = {}

CASES["reference"] = Case("9/9", reference_solution(SPEC))

# --- honest partial answers: each loses exactly the requirement(s) it breaks ---

CASES["wrong_thickness"] = Case("8/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 9)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""", _f("R3:thickness"))

CASES["two_holes_only"] = Case("7/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .pushPoints([(-30, -20), (30, 20)]).hole(6.5))
""", _f("R4a:hole_count", "R5:hole_pattern"))

# Oversized bores fail twice, honestly: R4b (diameter) and R6 (3.9% excess
# material removed vs the nominal-bore envelope).
CASES["wrong_hole_diameter"] = Case("7/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(10.0))
""", _f("R4b:hole_diameter", "R6:material"))

# A shifted pattern is wrong against BOTH datums: origin (R5) and edges (R7).
CASES["offset_pattern"] = Case("7/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane().center(5, 0)
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""", _f("R5:hole_pattern", "R7:edge_margin"))

# Every number divided by 25.4. Only the hole COUNT and the Z datum survive
# (the tiny plate is still centred); R6 fails because four nominal 6.5 mm
# bores cannot fit in a 3 mm envelope.
CASES["built_in_inches"] = Case("2/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80/25.4, 60/25.4, 6/25.4)
          .faces(">Z").workplane()
          .rect(60/25.4, 40/25.4, forConstruction=True).vertices().hole(6.5/25.4))
""", frozenset(ALL_REQS) - {"R4a:hole_count", "R8:z_datum"})

# --- 0.3.0 regressions from the September 2026 audit ---------------------------

# P0-1. The plate slides +2 mm in X under holes cut at nominal global positions.
# Left/right margins become 8 and 12 mm. Scored 1.0 before 0.3.0 because only
# translation-invariant sizes were checked. Must lose R7 and nothing else.
CASES["shifted_stock"] = Case("8/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .translate((2, 0, 0))
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""", _f("R7:edge_margin"))

# The whole correct part, translated off the origin datum. Edge margins are
# perfect; only the origin-referenced pattern (R5) is wrong.
CASES["whole_part_off_origin"] = Case("8/9", reference_solution(SPEC).rstrip()
                                      + "\nresult = result.translate((2, 0, 0))\n",
                                      _f("R5:hole_pattern"))

# P0-2. A symmetric cutter leaves each bore wall as two stacked 3 mm faces.
# Same solid as the reference; scored 0.0 before 0.3.0 because depth was the
# tallest single face. Must score exactly like the reference.
CASES["symmetric_cutter"] = Case("9/9", """
import cadquery as cq
base = cq.Workplane("XY").box(80, 60, 6)
cutters = (cq.Workplane("XY")
           .pushPoints([(-30, -20), (-30, 20), (30, -20), (30, 20)])
           .circle(6.5 / 2).extrude(10, both=True))
result = base.cut(cutters)
""")

# Holes drilled from the bottom face: a different operation, the same part.
CASES["drilled_from_bottom"] = Case("9/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces("<Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""")

# Two blind 3 mm holes meeting from both faces on one axis: a through bore.
CASES["two_sided_meeting"] = Case("9/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5, depth=3)
          .faces("<Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5, depth=3))
""")

# Same idea but the two halves miss each other by 0.5 mm: a joggled passage,
# not a drilled through hole. Gate, not partial credit.
CASES["HACK_two_sided_misaligned"] = Case("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5, depth=3)
          .faces("<Z").workplane().center(0.5, 0)
          .rect(60, 40, forConstruction=True).vertices().hole(6.5, depth=3))
""", _f("gate:simple_through_holes"))

# KNOWN LIMITATION, pinned so any change to it is deliberate: one hole moved
# to x=38.5 breaks out through the side wall. It no longer closes into a full
# cylinder, so it is reported as a partial bore and NOT counted: the part
# loses count AND pattern (asymmetric vs a misplaced interior hole, which
# would lose pattern and margin). See measure.py module docstring.
CASES["LIMIT_hole_breakout"] = Case("7/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .pushPoints([(38.5, -20), (-30, -20), (-30, 20), (30, 20)]).hole(6.5))
""", _f("R4a:hole_count", "R5:hole_pattern"))

# --- 0.4.0 regressions from the September 2026 reference-grounded audit ------

REF = reference_solution(SPEC).rstrip() + "\n"

# K1. The correct part floating in Z. Scored 1.0 before 0.4.0.
CASES["part_off_z"] = Case("8/9", REF + "result = result.translate((0, 0, 2))\n", _f("R8:z_datum"))

# F03. A hand-made object that REPORTS nominal geometry while its kernel
# shape is a 1 mm cube. Scored 1.0: the scorer trusted the object's methods.
# The scorer now measures only the serialised kernel geometry: a 1 mm cube.
CASES["HACK_fake_result_object"] = Case("0.0", """
import cadquery as cq, math
class Result:
    wrapped = cq.Workplane("XY").box(1, 1, 1).val().wrapped
    def BoundingBox(self):
        return cq.Workplane("XY").box(80, 60, 6).val().BoundingBox()
    def Volume(self):
        return 80 * 60 * 6 - 4 * math.pi * 3.25 ** 2 * 6
    def Solids(self):
        return [cq.Shape.cast(self.wrapped)]
    def Faces(self):
        return [f for x in (-30, 30) for y in (-20, 20)
                for f in cq.Solid.makeCylinder(3.25, 6, cq.Vector(x, y, -3)).Faces()]
result = Result()
""", _f("gate:simple_through_holes"))

# F04. Holes stopping 0.005 mm short leave a membrane: nothing passes through.
# Endpoints sit inside DEPTH_TOL, so 0.3.x called them "through".
CASES["HACK_membrane"] = Case("0.0", REF.replace(".hole(6.5)", ".hole(6.5, depth=5.995)"),
                              _f("gate:simple_through_holes"))

# F05. An enclosed cavity (a second shell) and a loose face beside the part.
CASES["HACK_hidden_cavity"] = Case("0.0", REF + 'result = result.cut(cq.Workplane("XY").box(10, 10, 2))\n',
                                   _f("gate:clean_solid"))
CASES["HACK_loose_face"] = Case("0.0", REF + """face = cq.Face.makePlane(5, 5, cq.Vector(0, 0, 0))
result = cq.Compound.makeCompound([result.val(), face])
""", _f("gate:clean_solid"))

# F07. 6.7 and 6.3 are exactly on the 6.5 +/- 0.2 limit: inside, inclusive.
CASES["diameter_upper_limit"] = Case("9/9", REF.replace(".hole(6.5)", ".hole(6.7)"))
CASES["diameter_lower_limit"] = Case("9/9", REF.replace(".hole(6.5)", ".hole(6.3)"))

# F06, KNOWN LIMITATION pinned so a change is deliberate: the same correct
# part converted to NURBS surfaces. Bores are recognised only as analytic
# cylinders, so it scores 0. Models do not produce this unprompted.
CASES["LIMIT_nurbs_surfaces"] = Case("0.0", REF + "result = result.val().toNURBS()\n",
                                     _f("gate:simple_through_holes"))

# A 2D sketch is not a part: no solid, no floor credit (0.3.x gave it 0.05).
CASES["BROKEN_sketch_only"] = Case("0.0", "import cadquery as cq\nresult = cq.Sketch().rect(80, 60)\n", BUILD)

# --- benign extras: real parts that must keep full marks ---------------------

# Corner fillets are external rounds, not bores.
CASES["fillets_r3"] = Case("9/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .edges("|Z").fillet(3)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""")

# A shallow engraving pocket stays inside the R6 material band.
CASES["pocket_small"] = Case("9/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane().rect(30, 20).cutBlind(-1.0)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""")

# A deeper pocket removes >3% of expected material: loses R6 only.
CASES["pocket_big"] = Case("8/9", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane().rect(30, 20).cutBlind(-3.0)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""", _f("R6:material"))

# --- cheats: each must trip the gate built for it ----------------------------

CASES["HACK_solid_block"] = Case("0.0", """
import cadquery as cq
result = cq.Workplane("XY").box(80, 60, 6)
""", _f("gate:simple_through_holes"))

CASES["HACK_blind_dimples"] = Case("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5, depth=1.0))
""", _f("gate:simple_through_holes"))

CASES["HACK_corner_tabs"] = Case("0.0", """
import cadquery as cq
result = (cq.Workplane("XY")
          .pushPoints([(-35, -25), (35, -25), (-35, 25), (35, 25)])
          .box(10, 10, 6, combine=False))
""", _f("gate:single_solid", "gate:simple_through_holes", "gate:is_plate"))

CASES["HACK_swiss_cheese"] = Case("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rarray(8, 8, 9, 7).hole(6.5))
""", _f("gate:hole_count_sane"))

CASES["HACK_hollow_shell"] = Case("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").shell(-1.0)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""", _f("gate:simple_through_holes", "gate:is_plate"))

CASES["HACK_cylinder_bbox"] = Case("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").ellipse(40, 30).extrude(6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""", _f("gate:simple_through_holes", "gate:is_plate"))

CASES["HACK_counterbored"] = Case("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane().rect(60, 40, forConstruction=True)
          .vertices().cboreHole(6.5, 11, 2))
""", _f("gate:simple_through_holes"))

# Hollow geometry keeps the hole DETECTOR honest: no phantom bores from the
# outer fillets (axes in the cavity) or the concave inner corner fillets.
CASES["shelled_filleted_box"] = Case("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 20)
          .edges("|Z").fillet(3)
          .faces(">Z").shell(-1.0))
""", _f("gate:simple_through_holes", "gate:is_plate"))

# --- extraction and broken output --------------------------------------------

# A fenced block indented four spaces, the way a model echoes an indented
# template. The 0.2.0 baseline lost 59 rollouts to exactly this.
CASES["fenced_and_indented"] = Case(
    "9/9",
    "Here you go:\n\n```python\n"
    + "".join("    " + line + "\n" for line in reference_solution(SPEC).strip().splitlines())
    + "```\n",
)

CASES["BROKEN_syntax"] = Case("0.0", "result = cq.Workplane('XY'.box(1,2,3)", BUILD)
CASES["BROKEN_no_result"] = Case("0.0", "import cadquery as cq\npart = cq.Workplane('XY').box(1,2,3)", BUILD)
CASES["BROKEN_prose"] = Case("0.0", "Sure! Here is how you would model that plate in CadQuery.", BUILD)


def parse_expectation(expr: str) -> float:
    """'8/8' -> 1.0, '1/8' -> 0.125, '0.0' -> 0.0. No eval."""
    num, _, den = expr.partition("/")
    return float(num) / float(den) if den else float(expr)


def failed_checks(report) -> frozenset[str]:
    """Gated parts are pinned by their failed GATES; others by failed requirements."""
    if report.error:
        return BUILD
    gates = {c.name for c in report.checks if c.name.startswith("gate:") and not c.passed}
    if gates:
        return frozenset(gates)
    return frozenset(c.name for c in report.checks if not c.passed)


def check_case(name: str, case: Case) -> tuple[bool, str]:
    report = score(case.code, SPEC)
    expected = parse_expectation(case.expected)
    got = failed_checks(report)
    ok = abs(report.reward - expected) < 1e-3 and got == case.fails
    msg = f"reward={report.reward:<6} expected {expected:.4f}"
    if got != case.fails:
        msg += f"\n        failed {sorted(got)}\n        wanted {sorted(case.fails)}"
    if not ok:
        msg += "\n        " + report.summary.replace("\n", "\n        ")
    return ok, msg


def main() -> int:
    failures = 0
    for name, case in CASES.items():
        ok, msg = check_case(name, case)
        failures += not ok
        print(f"[{'ok ' if ok else 'BAD'}] {name:<26} {msg}")
    print()
    print(f"{len(CASES) - failures}/{len(CASES)} cases behaved as expected")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
