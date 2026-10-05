"""Hand-labelled cases for scorer 0.5.0, the strict contract (no model in the loop).

    python scripts/test_rubric_050.py

Contract: one rectangular plate with exactly four through holes and nothing
else; 0.1 mm on every dimension, position, margin, datum and diameter. Ten
requirements (R1 to R8, with R4 split in two, and R9: no other features).

Three groups:

1. The 37 answers of scripts/test_rubric.py, relabelled. That file pins what
   scorer 0.4.0 gave them; this one pins what 0.5.0 gives, and the comment on
   each changed case says why it changed.
2. New answers for the defects 0.4.0 accepted: extra cuts, edge breaks,
   one-grid-step errors.
3. The saved model answer that started it: dev spec gen-0021, a real answer
   with four notches through its edges that 0.4.0 scored 1.0.

Each case pins the exact set of failed checks, not only the total.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))
sys.path.insert(0, str(ROOT / "scripts"))

import test_rubric as legacy  # noqa: E402
from cad_spec.rubric import score  # noqa: E402
from cad_spec.tasks import Spec, make_splits  # noqa: E402

VERSION = "0.5.0"
SPEC = legacy.SPEC  # 80 x 60 x 6, four 6.5 mm holes, 10 mm margin
BUILD = legacy.BUILD
R9 = "R9:no_other_features"


class Case(NamedTuple):
    code: str
    fails: frozenset[str]  # exact set of failed checks (gates only, when a gate fails)
    spec: Spec = SPEC


def _f(*names: str) -> frozenset[str]:
    return frozenset(names)


# --- group 1: the legacy answers under 0.5.0 -----------------------------------
# Unchanged verdicts keep the failed checks 0.4.0 gave them. Changed ones:
CHANGED = {
    # 6.7 and 6.3 mm against 6.5: inside 0.4.0's 0.2 mm, outside 0.1 mm.
    "diameter_upper_limit": _f("R4b:hole_diameter"),
    "diameter_lower_limit": _f("R4b:hole_diameter"),
    # 3 mm corner fillets and a shallow pocket were accepted by 0.4.0 (they
    # stay inside the 3% material band). Nobody asked for them.
    "fillets_r3": _f(R9),
    "pocket_small": _f(R9),
    "pocket_big": _f("R6:material", R9),
    # A hole breaking out through the side wall removes material that is not
    # a bore. 0.4.0 only saw the missing hole.
    "LIMIT_hole_breakout": _f("R4a:hole_count", "R5:hole_pattern", R9),
}
# LIMIT_nurbs_surfaces keeps its 0.4.0 verdict: the correct plate with every
# surface stored as a spline is rejected. A draft of 0.5.0 asked the kernel to
# recover the analytic form and passed it; the third audit showed that the
# same recovery accepts a spline with a 1 mm bump (AUDIT3 cases below). The
# scorer now trusts only true planes and cylinders: a false rejection of an
# exotic representation, never a false acceptance.
CASES: dict[str, Case] = {
    name: Case(case.code, CHANGED.get(name, case.fails)) for name, case in legacy.CASES.items()
}

# --- group 2: defects 0.4.0 accepted -------------------------------------------
REF = legacy.REF
BOX = 'import cadquery as cq\nresult = (cq.Workplane("XY").box({L}, {W}, {T})\n'
HOLES = '          .faces(">Z").workplane().pushPoints({pts}).hole({d}))\n'
NOMINAL_PTS = "[(-30, -20), (-30, 20), (30, -20), (30, 20)]"


def plate(length: float = 80, width: float = 60, thick: float = 6, pts: str = NOMINAL_PTS, d: float = 6.5) -> str:
    return BOX.format(L=length, W=width, T=thick) + HOLES.format(pts=pts, d=d)


CASES["diameter_at_limit_plus"] = Case(plate(d=6.6), _f())    # exactly at the inclusive limit
CASES["diameter_at_limit_minus"] = Case(plate(d=6.4), _f())
CASES["length_one_grid_step"] = Case(plate(length=80.5), _f("R1:length", "R7:edge_margin"))
CASES["thickness_one_grid_step"] = Case(plate(thick=6.5), _f("R3:thickness"))
CASES["one_hole_quarter_mm_off"] = Case(
    plate(pts="[(-30, -20), (-30, 20), (30, -20), (30.25, 20)]"), _f("R5:hole_pattern", "R7:edge_margin"))
CASES["pattern_half_mm_off"] = Case(
    plate(pts="[(-29.5, -20), (-29.5, 20), (30.5, -20), (30.5, 20)]"), _f("R5:hole_pattern", "R7:edge_margin"))
CASES["within_tolerance"] = Case(  # 0.05 mm on a hole and on the length: still the right part
    plate(length=80.05, pts="[(-30, -20), (-30, 20), (30, -20), (30.05, 20)]"), _f())
CASES["z_datum_half_mm"] = Case(REF + "result = result.translate((0, 0, 0.5))\n", _f("R8:z_datum"))
CASES["chamfered_top_edges"] = Case("""
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6).faces(">Z").edges().chamfer(0.3)
          .faces(">Z").workplane().pushPoints([(-30, -20), (-30, 20), (30, -20), (30, 20)]).hole(6.5))
""", _f(R9))
CASES["edge_notch"] = Case(  # half a hole cut into the long edge
    REF + 'result = result.cut(cq.Workplane("XY").center(0, 30).circle(3.25).extrude(10, both=True))\n', _f(R9))
CASES["slot_through"] = Case(
    REF + 'result = result.cut(cq.Workplane("XY").rect(6, 2).extrude(10, both=True))\n', _f(R9))
CASES["cross_bore"] = Case(
    REF + 'result = result.cut(cq.Workplane("YZ").circle(1).extrude(50, both=True))\n', _f(R9))
CASES["clipped_corner"] = Case(
    REF + 'result = result.cut(cq.Workplane("XY").polyline([(41, 31), (38, 31), (38, 30), (40, 28), (41, 28)])'
          '.close().extrude(10, both=True))\n', _f(R9))
# A small lug on the wall of one bore, clear of its axis. On the -Y side the
# bore is still recognised and only R9 sees the lug. On the +X side the lug
# sits where the bore detector probes, so the bore is not recognised at all:
# the part is rejected through the hole checks as well.
CASES["lug_in_bore"] = Case(
    REF + 'result = result.union(cq.Workplane("XY").box(0.3, 0.6, 1.2).translate((30, 16.75, 0)))\n', _f(R9))
CASES["lug_in_bore_at_probe"] = Case(
    REF + 'result = result.union(cq.Workplane("XY").box(0.6, 0.3, 1.2).translate((33.25, 20, 0)))\n',
    _f("R4a:hole_count", "R5:hole_pattern", R9))
# A real fifth bore is a count error (and its margin is wrong), not an "other feature".
CASES["extra_fifth_hole"] = Case(
    REF + 'result = result.faces(">Z").workplane().hole(6.5)\n', _f("R4a:hole_count", "R7:edge_margin"))


# --- group 2b: the counterexamples of the second external audit (5 October 2026)
# The first 0.5.0 draft judged R9 by a volume inside a 0.005 mm band. The audit
# showed what that accepts; every one of these scored 1.0 under that draft.
# They are why R9 now checks the form of the part, face by face.
CASES["AUDIT_pocket_5_microns_deep"] = Case(  # 50 x 50 mm, 12 mm3 removed
    REF + 'result = result.cut(cq.Workplane("XY").box(50, 50, 0.0049).translate((0, 0, 2.99755)))\n', _f(R9))
CASES["AUDIT_boss_5_microns_high"] = Case(  # raises the envelope, which absorbed it
    REF + 'result = result.union(cq.Workplane("XY").box(20, 20, 0.0059).translate((0, 0, 3.00195)))\n', _f(R9))
CASES["AUDIT_slot_13_microns_wide"] = Case(  # through the whole plate, under 0.001 mm3
    REF + 'result = result.cut(cq.Workplane("XY").box(0.0128, 0.0128, 8))\n', _f(R9))
CASES["AUDIT_side_tab_5_microns"] = Case(
    REF + 'result = result.union(cq.Workplane("XY").box(0.0059, 20, 6).translate((40.00195, 0, 0)))\n', _f(R9))
CASES["AUDIT_chamfer_10_microns"] = Case(REF + 'result = result.faces(">Z").edges().chamfer(0.01)\n', _f(R9))
CASES["AUDIT_fillet_30_microns"] = Case(REF + 'result = result.edges("|Z").fillet(0.03)\n', _f(R9))
CASES["AUDIT_lug_50_microns_in_bore"] = Case(
    REF + 'result = result.union(cq.Workplane("XY").box(0.051, 0.02, 0.02).translate((33.2255, 20, 0)))\n', _f(R9))
CASES["AUDIT_countersink_10_microns"] = Case(
    REF + "for x, y in [(-30, -20), (-30, 20), (30, -20), (30, 20)]:\n"
          "    result = result.cut(cq.Solid.makeCone(3.25, 3.26, 0.01, cq.Vector(x, y, 2.99)))\n", _f(R9))
CASES["AUDIT_second_cut_offset_0.4_micron"] = Case(  # a bore that is no longer one cylinder
    REF + 'result = result.cut(cq.Workplane("XY").center(30.0004, 20).circle(3.25).extrude(10, both=True))\n',
    _f(R9))
CASES["AUDIT_turned_0.001_degree_about_Z"] = Case(REF + "result = result.rotate((0, 0, 0), (0, 0, 1), 0.001)\n", _f(R9))
CASES["AUDIT_draft_0.01_degree"] = Case("""
import cadquery as cq
result = cq.Workplane("XY").rect(80, 60).extrude(6, taper=0.01).translate((0, 0, -3))
result = result.faces(">Z").workplane().pushPoints([(-30, -20), (-30, 20), (30, -20), (30, 20)]).hole(6.5)
""", _f(R9))
# Rounding used to widen the 0.1 mm tolerance; values are now compared unrounded.
CASES["AUDIT_diameter_0.100049_over"] = Case(plate(d=6.600049), _f("R4b:hole_diameter"))
CASES["AUDIT_length_0.100049_over"] = Case(
    BOX.format(L=80.100049, W=60, T=6)
    + '          .faces(">Z").workplane().rect(60.100049, 40, forConstruction=True).vertices().hole(6.5))\n',
    _f("R1:length"))
CASES["AUDIT_part_moved_0.1007_diagonally"] = Case(  # rounds to (0.060, 0.080), norm 0.1
    REF + "result = result.translate((0.060499, 0.080499, 0))\n", _f("R5:hole_pattern"))
CASES["AUDIT_z_datum_0.10004"] = Case(REF + "result = result.translate((0, 0, 0.10004))\n", _f("R8:z_datum"))
CASES["AUDIT_at_the_limit_still_passes"] = Case(REF + "result = result.translate((0.1, 0, 0.1))\n", _f())
CASES["AUDIT_plate_thinner_than_the_band"] = Case(plate(thick=0.009), _f("R3:thickness", R9))

# --- group 2c: the counterexamples of the third audit (5 October 2026, on the form check)
# Hand-built kernel objects. Each scored 1.0 under the first form check.
CASES["AUDIT3_spline_top_with_1mm_bump"] = Case("""
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.Geom import Geom_BezierSurface
from OCP.GeomConvert import GeomConvert
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt
poles = TColgp_Array2OfPnt(1, 4, 1, 4)
for i in range(1, 5):
    for j in range(1, 5):
        poles.SetValue(i, j, gp_Pnt(-40 + (i - 1) * 80 / 3, -30 + (j - 1) * 60 / 3, 3))
surface = GeomConvert.SurfaceToBSplineSurface_s(Geom_BezierSurface(poles))
for u in (0.332, 0.333, 0.334):
    surface.InsertUKnot(u, 3, 1e-12)
for v in (0.332, 0.333, 0.334):
    surface.InsertVKnot(v, 3, 1e-12)
p = surface.Pole(6, 6)
surface.SetPole(6, 6, gp_Pnt(p.X(), p.Y(), p.Z() + 5))  # a local bump, almost 1 mm high
top = cq.Face(BRepBuilderAPI_MakeFace(surface, 1e-7).Face())
box = cq.Workplane("XY").box(80, 60, 6).val()
faces = [f for f in box.Faces() if f.Center().z < 2.9] + [top]
result = cq.Workplane(obj=cq.Solid.makeSolid(cq.Shell.makeShell(faces)))
for x, y in [(-30, -20), (-30, 20), (30, -20), (30, 20)]:
    result = result.cut(cq.Workplane("XY").center(x, y).circle(3.25).extrude(10, both=True))
""", _f(R9))
CASES["AUDIT3_pocket_floor_stored_far_away"] = Case(REF + """
result = result.cut(cq.Workplane("XY").box(79.999999, 59.999999, 0.0049).translate((0, 0, 2.99755)))
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepTools import BRepTools_ReShape
from OCP.gp import gp_Dir, gp_Pln, gp_Pnt
from OCP.TopoDS import TopoDS
shape = result.val()
floor = min([f for f in shape.Faces() if f.geomType() == "PLANE" and abs(f.Center().z - 2.9951) < 1e-6],
            key=lambda f: abs(f.Center().z - 2.9951))
# the same floor, stored as a plane through a point 9.8 km away with a tilt of 5e-10 rad
maker = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(-9800000.0, 0, 3), gp_Dir(5e-10, 0, 1)), floor.outerWire().wrapped, True)
for wire in floor.innerWires():
    maker.Add(wire.wrapped)
change = BRepTools_ReShape()
change.Replace(floor.wrapped, TopoDS.Face_s(maker.Face().Oriented(floor.wrapped.Orientation())))
result = cq.Shape.cast(change.Apply(shape.wrapped))
""", _f(R9))
CASES["AUDIT3_pocket_1_nanometre_deep"] = Case(  # 9.9e-7 mm over the whole top face
    REF + 'result = result.cut(cq.Workplane("XY").box(79.999999, 59.999999, 9.9e-07)'
          '.translate((0, 0, 2.999999505)))\n', _f(R9))
CASES["AUDIT3_diameter_0.100001_over"] = Case(plate(d=6.600001), _f("R4b:hole_diameter"))
CASES["AUDIT3_z_datum_0.100001"] = Case(REF + "result = result.translate((0, 0, 0.100001))\n", _f("R8:z_datum"))

# --- group 2d: the fourth audit (5 October 2026). Ordinary CadQuery this time.
# A cut 1.2e-6 mm deep at the mouth of a bore. The boolean swallows it and
# returns the nominal plane and cylinder joined by an edge that sits off both,
# recording the gap as the edge's tolerance: valid for the kernel, every face
# allowed, 1.0 under the previous form check.
CASES["AUDIT4_bore_mouth_cut_1.2e-6_deep"] = Case(
    REF + 'result = result.cut(cq.Workplane("XY").workplane(offset=2.9999988).center(30, 20)'
          '.circle(3.2500004).extrude(1.0000012))\n', _f(R9))
CASES["AUDIT4_bore_mouth_cut_8e-7_deep"] = Case(
    REF + 'result = result.cut(cq.Workplane("XY").workplane(offset=2.9999992).center(30, 20)'
          '.circle(3.2500004).extrude(1.0000008))\n', _f(R9))
# Bores tilted on the diagonal: each end moves 9.9e-8 mm in X and in Y, which
# passed two separate allowances, but 1.4e-7 mm in distance.
CASES["AUDIT4_bores_tilted_on_the_diagonal"] = Case("""
import cadquery as cq
result = cq.Workplane("XY").box(80, 60, 6)
for x, y in [(-30, -20), (-30, 20), (30, -20), (30, 20)]:
    cutter = cq.Workplane("XY").circle(3.25).extrude(8, both=True)
    cutter = cutter.rotate((0, 0, 0), (-1, 1, 0), 2.673939458986605e-06).translate((x, y, 0))
    result = result.cut(cutter)
""", _f(R9))
# Control: a correct plate whose stored tolerances are inflated a thousand
# times is still a correct plate. Its edges do lie on its faces.
CASES["AUDIT4_correct_plate_with_inflated_tolerances"] = Case(REF + """
from OCP.ShapeFix import ShapeFix_ShapeTolerance
shape = result.val()
ShapeFix_ShapeTolerance().SetTolerance(shape.wrapped, 1e-3)
result = shape
""", _f())

# --- group 3: the saved answer that 0.4.0 scored 1.0 ----------------------------
def saved_gen_0021() -> Case:
    path = ROOT / "results" / "training" / "screening" / "qwen3.5-9b-t0.7-x8-2k.jsonl"
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if '"tier"' in x]
    row = next(r for r in rows if r["tier"] == "L3" and r["spec_id"] == "gen-0021" and r["rollout"] == 0)
    train, dev = make_splits()
    spec = next(s for s in train + dev if s.id == "gen-0021")
    return Case(row["completion"], _f(R9), spec)


CASES["SAVED_dev_answer_gen_0021"] = saved_gen_0021()


def check_case(name: str, case: Case) -> tuple[bool, str]:
    report = score(case.code, case.spec, VERSION)
    got = legacy.failed_checks(report)
    reqs = [c for c in report.checks if not c.name.startswith("gate:")]
    gated = any(c.name.startswith("gate:") and not c.passed for c in report.checks)
    expected = 0.0 if (case.fails == BUILD or gated) else 1 - len(case.fails) / max(1, len(reqs))
    ok = got == case.fails and abs(report.reward - expected) < 1e-3
    msg = f"reward={report.reward:<6}"
    if not ok:
        msg += f"\n        failed {sorted(got)}\n        wanted {sorted(case.fails)}"
        msg += "\n        " + report.summary.replace("\n", "\n        ")
    return ok, msg


def main() -> int:
    failures = 0
    for name, case in CASES.items():
        ok, msg = check_case(name, case)
        failures += not ok
        print(f"[{'ok ' if ok else 'BAD'}] {name:<28} {msg}")
    # The same saved answer under 0.4.0: full credit. That is the defect 0.5.0 fixes.
    saved = CASES["SAVED_dev_answer_gen_0021"]
    old = score(saved.code, saved.spec, "0.4.0").reward
    ok = old == 1.0
    failures += not ok
    print(f"[{'ok ' if ok else 'BAD'}] the saved gen-0021 answer still scores {old} under 0.4.0 (kept for replay)")
    print()
    print(f"{len(CASES) + 1 - failures}/{len(CASES) + 1} cases behaved as expected")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
