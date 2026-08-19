"""Step 2 of the plan: prove the reward function works, with no model in the loop.

Every entry below is a hand-written answer with a known correct score.
If this file passes, the rubric is trustworthy enough to put a model behind.
Run:  python scripts/test_rubric.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cad_spec.rubric import score
from cad_spec.tasks import TASKS, reference_solution

SPEC = TASKS[0]  # 80 x 60 x 6, four 6.5 mm holes, 10 mm margin

CASES: dict[str, tuple[str, str]] = {}

CASES["reference"] = ("1.0", reference_solution(SPEC))

CASES["wrong_thickness"] = ("5/6", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 9)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""")

CASES["two_holes_only"] = ("4/6", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .pushPoints([(-30, -20), (30, 20)]).hole(6.5))
""")

CASES["wrong_hole_diameter"] = ("5/6", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(10.0))
""")

CASES["HACK_hollow_shell"] = ("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").shell(-1.0)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""")

CASES["HACK_cylinder_bbox"] = ("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").ellipse(40, 30).extrude(6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""")

# --- the cheats ---

CASES["HACK_solid_block"] = ("0.0", """
import cadquery as cq
result = cq.Workplane("XY").box(80, 60, 6)
""")

CASES["HACK_blind_dimples"] = ("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5, depth=1.0))
""")

CASES["HACK_corner_tabs"] = ("0.0", """
import cadquery as cq
result = (cq.Workplane("XY")
          .pushPoints([(-35, -25), (35, -25), (-35, 25), (35, 25)])
          .box(10, 10, 6, combine=False))
""")

CASES["HACK_swiss_cheese"] = ("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rarray(8, 8, 9, 7).hole(6.5))
""")

# --- domain cheats: parts an inspector would reject on sight ---

CASES["offset_pattern"] = ("5/6", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane().center(5, 0)
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
""")

CASES["built_in_inches"] = ("1/6", """
import cadquery as cq
result = (cq.Workplane("XY").box(80/25.4, 60/25.4, 6/25.4)
          .faces(">Z").workplane()
          .rect(60/25.4, 40/25.4, forConstruction=True).vertices().hole(6.5/25.4))
""")

CASES["HACK_counterbored"] = ("0.0", """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane().rect(60, 40, forConstruction=True)
          .vertices().cboreHole(6.5, 11, 2))
""")

CASES["BROKEN_syntax"] = ("0.0", "result = cq.Workplane('XY'.box(1,2,3)")
CASES["BROKEN_no_result"] = ("0.0", "import cadquery as cq\npart = cq.Workplane('XY').box(1,2,3)")
CASES["BROKEN_prose"] = ("0.0", "Sure! Here is how you would model that plate in CadQuery.")


def main() -> int:
    failures = 0
    for name, (expectation, code) in CASES.items():
        report = score(code, SPEC)
        ok = abs(report.reward - eval(expectation)) < 1e-3  # noqa: S307 - test harness only
        flag = "ok " if ok else "BAD"
        if not ok:
            failures += 1
        print(f"[{flag}] {name:<22} reward={report.reward:<6} expected {eval(expectation):.4f}")
        if not ok:
            print("        " + report.summary.replace("\n", "\n        "))

    print()
    print(f"{len(CASES) - failures}/{len(CASES)} cases behaved as expected")
    print()
    print("Detail for the reference solution:")
    print(score(reference_solution(SPEC), SPEC).summary)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
