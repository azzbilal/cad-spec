1. **Change first. Do not merge scorer 0.5.0 at `8066480`.**
2. **Fact, high confidence:** a valid retained spline face protrudes **0.986720900 mm** and scores **1.0**.
3. **Fact, high confidence:** a remote-origin plane hides a **0.005 mm** pocket removing **159.227645 mm3**, also scoring **1.0**.
4. **Fact, high confidence:** all **79 original correct constructions pass**; the original extra-feature attacks now fail, with two nominal-limit slack cases still scoring 1.0.
5. **Fact, high confidence:** 3,161 legacy rewards/checks/parsed flags agree; one raw error-address mismatch and six first-run deadline differences are reported, not discarded.

# Scorer 0.5.0, v2 audit

Target: `feat/scorer-0.5`, HEAD `806648032f9d212d69e99c2a889a3d16bda0d6be`, including `08c3588`. Main: `7c17439a84529417d4516882b4034aa148c86017`. Date 2026-10-05. Facts are executions/source checks; inferences explain implications; opinions propose changes. Confidence is high for local observations and moderate for generalizations/proposals.

The repository was read only: no tracked edits, commit, push, credential access, network, paid service or external action. All new scripts/notes are beneath v2. Pre-existing v2 scratch results were not counted as fresh evidence. Required runs are in `fresh/`. Runtime: Windows, Python 3.12, CadQuery 2.8.0, reuse sandbox. Interpreter: `C:/Users/bgare/dev/cad-spec-env/environments/cad_spec/.venv/Scripts/python.exe`, with this worktree selected through PYTHONPATH. The main snapshot's measure.py, rubric.py, tasks.py and __init__.py match `git show main:...` after CRLF normalization.

## 1. Required changes, with reproductions

### V2-B1. Approximate analytic recovery misses a retained localized spline bump

**Fact, high confidence:** T004 is one valid solid, one shell, four open bores, no loose geometry. `_analytic_adaptor` recovers its nonplanar retained top as a plane. Observed reward **1.0**, no failed checks, form **True**, extra/missing **0.0/0.0 mm3**, reported thickness **6.0000001 mm**. The actual retained face contains `(-13.386,-10.0395,3.986720899658206)`, almost 1 mm above the nominal top. UV `(0.332675,0.332675)` is `TopAbs_IN` according to `BRepClass_FaceClassifier`, away from every hole. Reproduction:

```python
import cadquery as cq
from OCP.Geom import Geom_BezierSurface
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
poles=TColgp_Array2OfPnt(1,4,1,4)
for i in range(1,5):
 for j in range(1,5):
  poles.SetValue(i,j,gp_Pnt(-40+(i-1)*80/3,-30+(j-1)*60/3,3+(0 if i in (2,3) and j in (2,3) else 0)))

from OCP.GeomConvert import GeomConvert
surface=GeomConvert.SurfaceToBSplineSurface_s(Geom_BezierSurface(poles))
for u in [0.332,0.333,0.334]:surface.InsertUKnot(u,3,1e-12)
for u in [0.332,0.333,0.334]:surface.InsertVKnot(u,3,1e-12)
p=surface.Pole(6,6)
surface.SetPole(6,6,gp_Pnt(p.X(),p.Y(),p.Z()+5))
top=cq.Face(BRepBuilderAPI_MakeFace(surface,1e-7).Face())

box=cq.Workplane("XY").box(80,60,6).val()
faces=[f for f in box.Faces() if f.Center().z<2.9]+[top]
solid=cq.Solid.makeSolid(cq.Shell.makeShell(faces))
result=cq.Workplane(obj=solid)
for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 result=result.cut(cq.Workplane("XY").center(x,y).circle(3.25).extrude(10,both=True))
```

To inspect the retained face, evaluate `BRep_Tool.Surface_s(face.wrapped).Value(0.332675,0.332675)` on the top spline. [trim-certificate.json](fresh/scratch/trim-certificate.json) records the point, UV membership and validity. Pole amplitudes 0.01, 0.1, 1 and 5 mm all score 1.0, attaining surface heights approximately 0.00197344, 0.0197344, 0.197344 and 0.986721 mm. These are attained heights, not a proved maximum.

**Inference, high confidence:** `ConvertToAnalytical(Precision.Confusion_s())` is approximate recognition, not a certificate over the retained surface. The kernel's bounding box and volume calculation also miss the bump. Even the solid point classifier reports a point under the protrusion as outside; it is not an independent geometric certificate here. Direct retained-boundary evaluation plus UV trim membership establishes the difference. Kernel-reported validity does not establish part compliance.

**Opinion, high confidence:** require a conservative whole-face certificate before trusting recovery. A recovered plane stored as a positive-weight Bezier/B-spline can be conservatively bounded by its control points. Finite samples and the same sampled bounding box cannot certify it. Exact rational NURBS cylinders need a different certified bound: their control points do not lie on the cylinder. The following limited plane guard addresses the observed retained-spline failure; it is not a general cylinder solution.

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@
-        analytical = GeomConvert_SurfToAnaSurf(BRep_Tool.Surface_s(face.wrapped)).ConvertToAnalytical(
+        surface = BRep_Tool.Surface_s(face.wrapped)
+        analytical = GeomConvert_SurfToAnaSurf(surface).ConvertToAnalytical(
             Precision.Confusion_s())
@@
     recovered = GeomAdaptor_Surface(analytical)
+    if recovered.GetType() == GeomAbs_SurfaceType.GeomAbs_Plane:
+        if not hasattr(surface, "NbUPoles"):
+            return None  # certify other recovered representations before accepting them
+        plane = recovered.Plane()
+        if any(plane.Distance(surface.Pole(i, j)) > Precision.Confusion_s()
+               for i in range(1, surface.NbUPoles() + 1)
+               for j in range(1, surface.NbVPoles() + 1)):
+            return None
     return recovered if recovered.GetType() in wanted else None
```

A production implementation must explicitly handle locations, trimmed surfaces, weights, and recovered cylinders. This prototype is proposed, not applied.

### V2-B2. A stored plane origin can conceal a displaced pocket floor

**Fact, high confidence:** N022 is a 0.0049 mm pocket. Its floor normal has X component `5e-10`, within the angular tolerance, but the plane's arbitrary origin is X=-9,800,000 mm, Z=3 mm. The actual trimmed floor lies near Z=2.9951 mm. `_surface_conformance` compares the origin's Z, not the actual face support. The 5e-7 mm rim puts its sidewalls within the linear tolerance too. Observed score **1.0**, no failed checks, valid=True, form=True, residual **0.0/0.0 mm3**:

```python
import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 6)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)

result=result.cut(cq.Workplane("XY").box(79.999999,59.999999,0.0049).translate((0,0,2.99755)))
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepTools import BRepTools_ReShape
from OCP.gp import gp_Pln,gp_Pnt,gp_Dir
from OCP.TopoDS import TopoDS
shape=result.val()
face=min([f for f in shape.Faces() if f.geomType()=="PLANE" and abs(f.Center().z-2.9951)<1e-6],key=lambda f:abs(f.Center().z-2.9951))
plane=gp_Pln(gp_Pnt(-9800000.0,0,3),gp_Dir(5e-10,0,1))
maker=BRepBuilderAPI_MakeFace(plane,face.outerWire().wrapped,True)
for wire in face.innerWires():maker.Add(wire.wrapped)
new_face=TopoDS.Face_s(maker.Face().Oriented(face.wrapped.Orientation()))
change=BRepTools_ReShape()
change.Replace(face.wrapped,new_face)
result=cq.Shape.cast(change.Apply(shape.wrapped))
```

D055 applies this construction to gen-0032, the largest-area train/dev plate, 214 x 150 x 10.5 mm, at depth 0.005 mm. It scores **1.0** and removes **159.227644915 mm3** compared with nominal volume. D056, depth 0.0051 mm, still passes form but scores **0.9**, failing the residual. The band matters when form is fooled.

**Inference, high confidence:** angular error multiplied by arbitrary parameter-origin distance has no useful geometric bound. A smaller angular tolerance alone does not fix the test. **Opinion, high confidence:** compare actual certified trimmed-face support, independently of parameter origin. A conservative coordinate bound suffices for the observed planar floor. Certify recovered planes first, because the spline bounding box missed V2-B1.

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@
-            if min(abs(p[axis] - edge) for edge in limits[axis]) > FORM_LINEAR_TOL:
+            fbb = face.BoundingBox()
+            lo, hi = ((fbb.xmin, fbb.xmax), (fbb.ymin, fbb.ymax),
+                      (fbb.zmin, fbb.zmax))[axis]
+            if not any(max(abs(lo - edge), abs(hi - edge)) <= FORM_LINEAR_TOL + 1e-12
+                       for edge in limits[axis]):
                 return False
```

This bound is a prototype after plane certification. Do not use an uncertified spline bounding box as a substitute for the certificate.

### V2-B3. Positive numerical allowances accept actual extra features

**Fact, high confidence:** a broad 9.9e-7 mm-deep pocket, approximately 80 x 60 mm, is valid and scores **1.0**, form=True, residual 0/0, no failed checks. At 1.01e-6 mm it scores **0.9**. Reproduction:

```python
import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 6)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)

result=result.cut(cq.Workplane("XY").box(79.999999,59.999999,9.9e-07).translate((0,0,2.999999505)))
```

The accepted 8e-7 mm pocket on the largest plate spans nearly 214 x 150 mm and removes about 0.02548 mm3. The synthetic 9.9e-7 mm pocket removes about 0.004625 mm3. Thus 1e-6 mm is a real feature allowance under the literal no-other-features contract, regardless of its engineering significance. Ordinary X/Z rotations of 8e-10 rad score 1.0; 1.2e-9 rad fail R9. At the largest train/dev half-diagonal, about 130.66 mm, 1e-9 rad moves an ordinary rotated point by about 1.31e-7 mm. This does not bound the remote-origin or recovery failure.

**Opinion, high confidence:** define a numerical equivalence policy and document it honestly. Any positive tolerance admits sufficiently small geometric changes. If these pockets are wrong, reduce the tolerance and add their regressions. If they are intentionally equivalent, remove the claim that every feature at any size fails.

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@
-FORM_LINEAR_TOL = 1e-6
+FORM_LINEAR_TOL = 2e-7
```

The reduction rejects the tested broad pockets and inset sidewalls; it does not certify recovered splines or eliminate every possible extra feature. A067 (diameter 6.600001 mm) and A068 (Z=0.100001 mm) also still score 1.0 because the separately documented NUM_EPS=1e-6 extends the nominal 0.1 mm dimension/datum limit. They are listed explicitly below.

### V2-B4. Compatibility differences must be retained

**Fact, high confidence:** the 3,161-answer comparison has one raw error-string mismatch at index 1362: both scorers return 0.0, parsed=False, no checks, and the same Vector.multiply TypeError, but `gp_Vec object at 0x...` has a different address. Three repeats on main itself yield three different addresses; branch repeats do too. After address-only normalization, errors agree. The original comparator included raw errors, so this is a literal difference, not omitted as a zero-mismatch result.

```python
import json
from pathlib import Path
from cad_spec.rubric import score
from cad_spec.tasks import Spec
row = json.loads(Path("fresh/scratch/compat-input.jsonl").read_text().splitlines()[1362])
for _ in range(3):
    r = score(row["completion"], Spec(**row["spec"]), version="0.4.0")
    print(r.reward, r.parsed, r.error)
# 0.0, False, same TypeError with a varying object address.
```

**Fact, high confidence:** the first deadline run has six paired differences. Main times out on four 0.1 s attempts and two 0.075 s attempts, while branch legacy passes. Both pass all four 0.05 s attempts. Main initially takes 0.44 to 0.66 s even at the 10 s budget, then recovers to about 0.03 s. This direction is the reverse of the original B5 regression. Your initial rule makes any difference blocking, so all six are retained as an acceptance failure. **Inference, moderate confidence:** transient scheduling/load is plausible; this pattern alone does not establish code-induced legacy overhead. The exact source skips all new work for strict=False. Counterbalanced follow-up results, if completed, are reported separately, not substituted for this run.

```python
import os
from cad_spec.tasks import Spec, reference_solution
from cad_spec.rubric import score
from cad_spec.measure import _get_worker
s = Spec("synth", 80, 60, 6, 6.5, 10)
os.environ["CAD_SPEC_EXEC_TIMEOUT"] = "0.1"
_get_worker()  # exclude startup from the execution-budget probe
for _ in range(4):
    print(score(reference_solution(s), s, version="0.4.0").reward)
# First measured run: main [0,0,0,0], branch [1,1,1,1].
```

**Opinion, moderate confidence:** do not change frozen legacy rewards based on this timing observation. Investigate and repeat on a controlled machine with alternating branch order. For literal reproducible error text, normalize diagnostic addresses identically in the baseline and new code, or explicitly compare a separately normalized field. Raw evidence must remain available.

### Proposed supplemental regressions and documentation correction

**Opinion, high confidence:** keep the frozen suite and add the retained spline, remote-origin pocket and numerical-equivalence boundaries to the hand-labelled regressions. A proposed addition, requiring helpers containing the constructions above, is:

```diff
--- a/scripts/test_rubric_050.py
+++ b/scripts/test_rubric_050.py
@@
+CASES["AUDIT_local_spline_retained_bump"] = Case(
+    localized_spline_plate(pole_lift=5.0, knot_center=0.333), _f(R9))
+CASES["AUDIT_remote_plane_origin"] = Case(
+    remote_origin_pocket(depth=0.0049), _f(R9))
+CASES["AUDIT_broad_submicron_pocket"] = Case(
+    REF + 'result=result.cut(cq.Workplane("XY").box(79.999999,59.999999,8e-7)'
+          '.translate((0,0,2.9999996)))
', _f(R9))
```

The third expectation assumes the proposed stricter equivalence policy. This is a design diff, not a complete standalone patch.

```diff
--- a/README.md
+++ b/README.md
@@
-so every face must lie on one of them (within 1e-6 mm and 1e-9 rad, which is
-kernel noise, not a feature allowance). A notch, slot, pocket, boss,
-cross-bore, chamfer, fillet, draft, a lug in a bore or a plate turned off
-its axes each adds a face that lies on none of them, whatever its size.
+The current implementation tests recovered support at numerical tolerances
+and checks volume outside a 0.005 mm band, allowing 0.001 mm3 residual.
+Sufficiently small geometric changes can pass. Approximate recovery and
+stored plane origins do not certify the whole trimmed face; the v2 audit
+provides counterexamples requiring further fixes.
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@
-  a correct plate stored as splines scored 0. All fixed before merge, and
+  a correct plate stored as splines scored 0. The original reproductions
+  are fixed; further form and recovery bypasses remain, and
@@
-  fail R9 at any size: nobody asked for them. A correct plate converted to
+  fail R9 in the pinned cases. Numerical equivalence limits are not a proof
+  that no extra feature passes. A correct plate converted to
```

## 2. Original corpus and backward-compatibility tables

### Original corpus summary

**Fact, high confidence:** all 130 A cases and 79 C cases were rerun in the original ID order, from attacks.jsonl, attacks-extra.jsonl, focused.jsonl and rounding-extra.jsonl. All **79/79 correct constructions score 1.0**, including all six former exact-NURBS rejections. There are eleven full-score A rows, listed exhaustively below. Nine are correct controls; two are outside the nominal 0.1 mm but inside its separately documented 1e-6 mm slack. No original wrong extra-feature case remains full credit. If correctness means literal 0.1 mm with no slack, A067 and A068 are still wrong full-credit parts. Under the documented operational contract they are explicit numerical-limit controls.

| Full-score A row | Case | Score | Classification |
|---|---|---:|---|

| A001 | nominal | 1.0 | correct control |

| A044 | nurbs_exact | 1.0 | correct control |

| A048 | coincident_bore | 1.0 | correct control |

| A055 | probe_lug_y0.3_d0.004 | 1.0 | correct control |

| A058 | compound_one | 1.0 | correct control |

| A063 | length_0.1 | 1.0 | correct control |

| A064 | diameter_0.1 | 1.0 | correct control |

| A065 | z_datum_0.1 | 1.0 | correct control |

| A067 | diameter_0.100001 | 1.0 | nominal tolerance exceeded by documented NUM_EPS |

| A068 | z_datum_0.100001 | 1.0 | nominal tolerance exceeded by documented NUM_EPS |

| A075 | centres_0.1 | 1.0 | correct control |

A055 unions wholly within existing material and changes nothing. A048 re-drills a coincident bore. A058 is a one-solid compound. A063 to A065 and A075 are inclusive endpoints. A044 is an equivalent NURBS part. A067 drills 6.600001 mm bores; A068 moves the Z datum to 0.100001 mm. These differ from the larger raw-value rounding wedges, which now fail.

**No correct C part is rejected.** Three initial deep_narrow_slot snippets contain an extra closing parenthesis; their syntax failures are retained as harness errors, not evidence of rejecting the intended geometry. Corrected slot cases also remain in the corpus and fail R9.

### A001 to A130, every row

[corpus-rerun.jsonl](fresh/scratch/corpus-rerun.jsonl) contains full code/spec, old report, fresh report and Measurements. None means unavailable. A zero reward with no named checks and a build error is not full credit.

| ID | Case | Before | Fresh score | Failed checks | Form | Extra / missing mm3 | Error |
|---|---|---:|---:|---|---|---|---|

| A001 | nominal | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A002 | broad_pocket_0.001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A003 | broad_pocket_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A004 | broad_pocket_0.005 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A005 | broad_pocket_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.24999999999941738 |  |

| A006 | broad_pocket_0.006 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 2.500000000000835 |  |

| A007 | broad_pocket_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 12.499999999999734 |  |

| A008 | boss_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A009 | boss_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.42654590892095434 |  |

| A010 | boss_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 21.32729544590755 |  |

| A011 | boss_0.1 | 0.0 | 0.0 | gate:simple_through_holes, R9:no_other_features | False | 0.0 / 405.2186134722508 |  |

| A012 | edge_notch_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A013 | edge_notch_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.04192999999890917 |  |

| A014 | edge_notch_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 2.096500000000576 |  |

| A015 | small_pocket_0.005 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 1.2375000000003403e-05 |  |

| A016 | small_pocket_0.02 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0001980000000000105 |  |

| A017 | small_pocket_0.1 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.004949999999999969 |  |

| A018 | deep_narrow_slot_0.039 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |

| A019 | deep_narrow_slot_0.041 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |

| A020 | deep_narrow_slot_0.05 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |

| A021 | side_tab_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A022 | top_lip_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A023 | side_tab_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.02395400999795847 |  |

| A024 | top_lip_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.4585869039211642 |  |

| A025 | side_tab_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 1.1977004999991943 |  |

| A026 | top_lip_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 22.92934519590751 |  |

| A027 | rotate_Z_0.0001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A028 | rotate_X_0.0001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.0803144817107 |  |

| A029 | rotate_Z_0.001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A030 | rotate_X_0.001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.2054117173273 |  |

| A031 | rotate_Z_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 3.783666131189786 |  |

| A032 | rotate_X_0.01 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 809.6802844372207 |  |

| A033 | rotate_Z_0.05 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 44.22307048173275 |  |

| A034 | rotate_X_0.05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 1001.9542050570437 |  |

| A035 | draft_0.001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A036 | draft_0.01 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A037 | draft_0.1 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 2.393697342440646 |  |

| A038 | sheared_0.004 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A039 | sheared_0.02 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 4.040385646198465 |  |

| A040 | cone_0.001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.3110756787678 |  |

| A041 | cone_0.01 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 797.5152799843921 |  |

| A042 | ellipse | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 797.5127838275253 |  |

| A043 | polygon_128 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 794.7471583742455 |  |

| A044 | nurbs_exact | 0.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A045 | countersink_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A046 | countersink_0.01 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A047 | fifth_bore | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A048 | coincident_bore | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A049 | overlap_bore_0.0004 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A050 | overlap_bore_0.004 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 198.92234368738826 |  |

| A051 | overlap_bore_0.01 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 199.15595354362756 |  |

| A052 | coaxial_step | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | False | 0.0 / 0.0 |  |

| A053 | probe_lug_y0_d0.004 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A054 | probe_lug_y0_d0.05 | 1.0 | 0.9 | R9:no_other_features | False | 1.7997945554340325e-05 / 0.0 |  |

| A055 | probe_lug_y0.3_d0.004 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A056 | probe_lug_y0.3_d0.05 | 1.0 | 0.9 | R9:no_other_features | False | 1.2439020103472529e-05 / 0.0 |  |

| A057 | probe_notch | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 4.002048133976605e-06 |  |

| A058 | compound_one | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A059 | second_solid_bore | 0.0 | 0.0 | gate:single_solid, gate:simple_through_holes, R9:no_other_features | False | 0.0003141592653589902 / 0.0 |  |

| A060 | second_solid_outside | 0.0 | 0.0 | gate:single_solid, R1:length, R7:edge_margin, R9:no_other_features | False | 0.0 / 361.13679999999925 |  |

| A061 | loose_face | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | False | None / None |  |

| A062 | loose_edge | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | True | None / None |  |

| A063 | length_0.1 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A064 | diameter_0.1 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A065 | z_datum_0.1 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A066 | length_0.100001 | 1.0 | 0.9 | R1:length | True | 0.0 / 0.0 |  |

| A067 | diameter_0.100001 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A068 | z_datum_0.100001 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A069 | length_0.10004 | 1.0 | 0.9 | R1:length | True | 0.0 / 0.0 |  |

| A070 | diameter_0.10004 | 1.0 | 0.9 | R4b:hole_diameter | True | 0.0 / 0.0 |  |

| A071 | z_datum_0.10004 | 1.0 | 0.9 | R8:z_datum | True | 0.0 / 0.0 |  |

| A072 | length_0.1001 | 0.9 | 0.9 | R1:length | True | 0.0 / 0.0 |  |

| A073 | diameter_0.1001 | 0.9 | 0.9 | R4b:hole_diameter | True | 0.0 / 0.0 |  |

| A074 | z_datum_0.1001 | 0.9 | 0.9 | R8:z_datum | True | 0.0 / 0.0 |  |

| A075 | centres_0.1 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A076 | centres_0.1004 | 1.0 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A077 | centres_0.10049 | 1.0 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A078 | centres_0.1005 | 0.9 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A079 | centres_0.101 | 0.9 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A080 | residual_None_thin | 0.8 | 0.8 | R3:thickness, R9:no_other_features | True | None / None |  |

| A081 | many_bores_16 | 0.0 | 0.0 | gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A082 | many_bores_64 | 0.0 | 0.0 | gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A083 | many_bores_144 | 0.0 | 0.0 | none | None | None / None | model code exceeded 10s execution budget |

| A084 | threshold_through_slot_0.0128 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0009814015999999467 |  |

| A085 | threshold_through_slot_0.01295 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0010045379750001854 |  |

| A086 | threshold_through_slot_0.013 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0010123100000003584 |  |

| A087 | threshold_through_slot_0.0131 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0010279438999998725 |  |

| A088 | two_broad_pockets_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A089 | two_broad_pockets_0.005 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A090 | six_skin_pockets | 0.0 | 0.0 | gate:single_solid, R9:no_other_features | False | 0.0 / 0.0 |  |

| A091 | actual_probe_lug_0.163 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 198.7665384992689 |  |

| A092 | actual_probe_lug_0.17 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 198.76653569926896 |  |

| A093 | actual_probe_lug_0.2 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 198.76652369926896 |  |

| A094 | tiny_fifth_0.005 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A095 | hidden_fifth_0.005 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A096 | tiny_fifth_0.006 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A097 | hidden_fifth_0.006 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A098 | tiny_fifth_0.007 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A099 | hidden_fifth_0.007 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A100 | tiny_fifth_0.01 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A101 | hidden_fifth_0.01 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A102 | bore_annular_membrane | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features | False | 0.00019787321328163258 / 0.0 |  |

| A103 | top_chamfer_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A104 | top_chamfer_0.0051 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A105 | top_chamfer_0.01 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A106 | corner_fillet_0.001 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | False | 0.0 / 0.0 |  |

| A107 | corner_fillet_0.005 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A108 | corner_fillet_0.02 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 3.6011597542728735e-05 |  |

| A109 | fixed_deep_slot_0.039 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.009110790000000183 |  |

| A110 | fixed_deep_slot_0.041 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.01006918999999983 |  |

| A111 | fixed_deep_slot_0.05 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.01497499999999993 |  |

| A112 | hide_fifth_r0.003_h0.02 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A113 | hide_fifth_r0.003_h0.1 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A114 | hide_fifth_r0.005_h0.02 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A115 | hide_fifth_r0.005_h0.1 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A116 | hide_fifth_r0.007_h0.02 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A117 | hide_fifth_r0.007_h0.1 | 0.7 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A118 | largest_skin_gen-0032 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A119 | largest_skin_gen-0215 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A120 | fillet_0.025 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.00027109974786697827 |  |

| A121 | fillet_0.03 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0007351040829427555 |  |

| A122 | fillet_0.04 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0023760532789156527 |  |

| A123 | fillet_0.05 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0049913409920744195 |  |

| A124 | annular_bridge_2e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features | False | 0.0004946830332089784 / 0.0 |  |

| A125 | annular_bridge_3e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features | False | 0.0007420245498281586 / 0.0 |  |

| A126 | annular_bridge_4e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features | False | 0.0009893660664375447 / 0.0 |  |

| A127 | diagonal_rounding | 1.0 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A128 | length_0.100049 | 1.0 | 0.9 | R1:length | True | 0.0 / 0.0 |  |

| A129 | diameter_0.100049 | 1.0 | 0.9 | R4b:hole_diameter | True | 0.0 / 0.0 |  |

| A130 | margin_0.1004 | 1.0 | 0.8 | R5:hole_pattern, R7:edge_margin | True | 0.0 / 0.0 |  |

### C001 to C079, every row

| ID | Correct construction | Spec | Before | Fresh score | Failed checks |
|---|---|---|---:|---:|---|

| C001 | reference | gen-0215 | 1.0 | 1.0 | none |

| C002 | Sketch | gen-0215 | 1.0 | 1.0 | none |

| C003 | polyline | gen-0215 | 1.0 | 1.0 | none |

| C004 | cutThruAll | gen-0215 | 1.0 | 1.0 | none |

| C005 | explicit_depth | gen-0215 | 1.0 | 1.0 | none |

| C006 | union_halves | gen-0215 | 1.0 | 1.0 | none |

| C007 | imprinted_halves | gen-0215 | 1.0 | 1.0 | none |

| C008 | mirror | gen-0215 | 1.0 | 1.0 | none |

| C009 | translate_chain | gen-0215 | 1.0 | 1.0 | none |

| C010 | Solid_primitives | gen-0215 | 1.0 | 1.0 | none |

| C011 | clean | gen-0215 | 1.0 | 1.0 | none |

| C012 | float_coordinates | gen-0215 | 1.0 | 1.0 | none |

| C013 | nurbs_exact | gen-0215 | 0.0 | 1.0 | none |

| C014 | reference | gen-0065 | 1.0 | 1.0 | none |

| C015 | Sketch | gen-0065 | 1.0 | 1.0 | none |

| C016 | polyline | gen-0065 | 1.0 | 1.0 | none |

| C017 | cutThruAll | gen-0065 | 1.0 | 1.0 | none |

| C018 | explicit_depth | gen-0065 | 1.0 | 1.0 | none |

| C019 | union_halves | gen-0065 | 1.0 | 1.0 | none |

| C020 | imprinted_halves | gen-0065 | 1.0 | 1.0 | none |

| C021 | mirror | gen-0065 | 1.0 | 1.0 | none |

| C022 | translate_chain | gen-0065 | 1.0 | 1.0 | none |

| C023 | Solid_primitives | gen-0065 | 1.0 | 1.0 | none |

| C024 | clean | gen-0065 | 1.0 | 1.0 | none |

| C025 | float_coordinates | gen-0065 | 1.0 | 1.0 | none |

| C026 | nurbs_exact | gen-0065 | 0.0 | 1.0 | none |

| C027 | reference | gen-0032 | 1.0 | 1.0 | none |

| C028 | Sketch | gen-0032 | 1.0 | 1.0 | none |

| C029 | polyline | gen-0032 | 1.0 | 1.0 | none |

| C030 | cutThruAll | gen-0032 | 1.0 | 1.0 | none |

| C031 | explicit_depth | gen-0032 | 1.0 | 1.0 | none |

| C032 | union_halves | gen-0032 | 1.0 | 1.0 | none |

| C033 | imprinted_halves | gen-0032 | 1.0 | 1.0 | none |

| C034 | mirror | gen-0032 | 1.0 | 1.0 | none |

| C035 | translate_chain | gen-0032 | 1.0 | 1.0 | none |

| C036 | Solid_primitives | gen-0032 | 1.0 | 1.0 | none |

| C037 | clean | gen-0032 | 1.0 | 1.0 | none |

| C038 | float_coordinates | gen-0032 | 1.0 | 1.0 | none |

| C039 | nurbs_exact | gen-0032 | 0.0 | 1.0 | none |

| C040 | reference | gen-0208 | 1.0 | 1.0 | none |

| C041 | Sketch | gen-0208 | 1.0 | 1.0 | none |

| C042 | polyline | gen-0208 | 1.0 | 1.0 | none |

| C043 | cutThruAll | gen-0208 | 1.0 | 1.0 | none |

| C044 | explicit_depth | gen-0208 | 1.0 | 1.0 | none |

| C045 | union_halves | gen-0208 | 1.0 | 1.0 | none |

| C046 | imprinted_halves | gen-0208 | 1.0 | 1.0 | none |

| C047 | mirror | gen-0208 | 1.0 | 1.0 | none |

| C048 | translate_chain | gen-0208 | 1.0 | 1.0 | none |

| C049 | Solid_primitives | gen-0208 | 1.0 | 1.0 | none |

| C050 | clean | gen-0208 | 1.0 | 1.0 | none |

| C051 | float_coordinates | gen-0208 | 1.0 | 1.0 | none |

| C052 | nurbs_exact | gen-0208 | 0.0 | 1.0 | none |

| C053 | reference | gen-0001 | 1.0 | 1.0 | none |

| C054 | Sketch | gen-0001 | 1.0 | 1.0 | none |

| C055 | polyline | gen-0001 | 1.0 | 1.0 | none |

| C056 | cutThruAll | gen-0001 | 1.0 | 1.0 | none |

| C057 | explicit_depth | gen-0001 | 1.0 | 1.0 | none |

| C058 | union_halves | gen-0001 | 1.0 | 1.0 | none |

| C059 | imprinted_halves | gen-0001 | 1.0 | 1.0 | none |

| C060 | mirror | gen-0001 | 1.0 | 1.0 | none |

| C061 | translate_chain | gen-0001 | 1.0 | 1.0 | none |

| C062 | Solid_primitives | gen-0001 | 1.0 | 1.0 | none |

| C063 | clean | gen-0001 | 1.0 | 1.0 | none |

| C064 | float_coordinates | gen-0001 | 1.0 | 1.0 | none |

| C065 | nurbs_exact | gen-0001 | 0.0 | 1.0 | none |

| C066 | reference | gen-0037 | 1.0 | 1.0 | none |

| C067 | Sketch | gen-0037 | 1.0 | 1.0 | none |

| C068 | polyline | gen-0037 | 1.0 | 1.0 | none |

| C069 | cutThruAll | gen-0037 | 1.0 | 1.0 | none |

| C070 | explicit_depth | gen-0037 | 1.0 | 1.0 | none |

| C071 | union_halves | gen-0037 | 1.0 | 1.0 | none |

| C072 | imprinted_halves | gen-0037 | 1.0 | 1.0 | none |

| C073 | mirror | gen-0037 | 1.0 | 1.0 | none |

| C074 | translate_chain | gen-0037 | 1.0 | 1.0 | none |

| C075 | Solid_primitives | gen-0037 | 1.0 | 1.0 | none |

| C076 | clean | gen-0037 | 1.0 | 1.0 | none |

| C077 | float_coordinates | gen-0037 | 1.0 | 1.0 | none |

| C078 | nurbs_exact | gen-0037 | 0.0 | 1.0 | none |

| C079 | arc_circle | synthetic | 1.0 | 1.0 | none |

### 3,161 saved answers against main

**Fact, high confidence:** compat-input.jsonl is byte-identical to the original selected input: 2,200 stable-hash-selected AST-deduplicated train/dev programs and all 961 saved evaluation rows. Evaluation answers were deterministically replayed only, with no model calls and no parameter selection using those splits. Each implementation uses a separate process/worker; no cross-answer geometry cache.

| Compared field | Answers | Differences |
|---|---:|---:|

| reward | 3161 | 0 |

| checks | 3161 | 0 |

| parsed | 3161 | 0 |

| exception | 3161 | 0 |

| error | 3161 | 1 |

| error after address-only normalization | 3161 | 0 |

Main and branch both timeout at index 648, as before; no newly timed-out selected answer. Raw mismatch index 1362 is explained above. Main summed time **149.402243 s**, branch **616.910526 s**. Other audit jobs overlapped parts of this run, so these timings are not a controlled performance comparison and do not establish code overhead. Evidence: [compat-main.jsonl](fresh/scratch/compat-main.jsonl), [compat-branch.jsonl](fresh/scratch/compat-branch.jsonl), [compat-summary.json](fresh/scratch/compat-summary.json), [error-repeat.json](fresh/scratch/error-repeat.json).

### Short-deadline probe, every paired attempt

The original nominal 80 x 60 x 6 mm plate and four 6.5 mm bores were used. Four attempts at each budget, warmed worker before timing, main and branch sequentially. Optional geometry jobs had ended or were stopped before this run; ordinary system scheduling was not controlled.

| Budget s | Attempt | Main score | Branch legacy score | Main seconds | Branch seconds | Payload differences |
|---:|---:|---:|---:|---:|---:|---|

| 10 | 0 | 1.0 | 1.0 | 0.660596 | 0.041747 | none |

| 10 | 1 | 1.0 | 1.0 | 0.512606 | 0.031757 | none |

| 10 | 2 | 1.0 | 1.0 | 0.492796 | 0.032480 | none |

| 10 | 3 | 1.0 | 1.0 | 0.443019 | 0.032218 | none |

| 0.1 | 0 | 0.0 | 1.0 | 0.519337 | 0.034203 | reward, checks, error |

| 0.1 | 1 | 0.0 | 1.0 | 0.609013 | 0.031598 | reward, checks, error |

| 0.1 | 2 | 0.0 | 1.0 | 0.194591 | 0.030607 | reward, checks, error |

| 0.1 | 3 | 0.0 | 1.0 | 0.375198 | 0.030965 | reward, checks, error |

| 0.075 | 0 | 0.0 | 1.0 | 0.318825 | 0.030546 | reward, checks, error |

| 0.075 | 1 | 0.0 | 1.0 | 0.132027 | 0.030536 | reward, checks, error |

| 0.075 | 2 | 1.0 | 1.0 | 0.041929 | 0.033833 | none |

| 0.075 | 3 | 1.0 | 1.0 | 0.032937 | 0.031261 | none |

| 0.05 | 0 | 1.0 | 1.0 | 0.035652 | 0.030414 | none |

| 0.05 | 1 | 1.0 | 1.0 | 0.036581 | 0.030453 | none |

| 0.05 | 2 | 1.0 | 1.0 | 0.032336 | 0.030512 | none |

| 0.05 | 3 | 1.0 | 1.0 | 0.032278 | 0.030542 | none |

**Fact, high confidence:** 6 payload differences, all main timeouts versus branch full credit. Each changed reward, empty versus all-passing named checks, and timeout error versus None. These differences are blocking under the user's literal acceptance rule and are not overwritten by follow-up runs. The original systematic branch-only 0.05-second regression did not recur. Both implementations pass every 0.05-second attempt in this first run. [deadline-main.jsonl](fresh/scratch/deadline-main.jsonl) and [deadline-branch.jsonl](fresh/scratch/deadline-branch.jsonl) retain full payloads.

The follow-up ran branch first, then main, with the same budgets and four attempts. It is an investigation of the first-run differences, not a replacement.

| Budget s | Attempt | Repeat main | Repeat branch | Main seconds | Branch seconds | Difference |
|---:|---:|---:|---:|---:|---:|---|

| 10 | 0 | 1.0 | 1.0 | 0.035926 | 0.036988 | none |

| 10 | 1 | 1.0 | 1.0 | 0.026743 | 0.026364 | none |

| 10 | 2 | 1.0 | 1.0 | 0.026433 | 0.026813 | none |

| 10 | 3 | 1.0 | 1.0 | 0.026756 | 0.027278 | none |

| 0.1 | 0 | 1.0 | 1.0 | 0.026938 | 0.026873 | none |

| 0.1 | 1 | 1.0 | 1.0 | 0.026093 | 0.025761 | none |

| 0.1 | 2 | 1.0 | 1.0 | 0.025077 | 0.026009 | none |

| 0.1 | 3 | 1.0 | 1.0 | 0.026544 | 0.026756 | none |

| 0.075 | 0 | 1.0 | 1.0 | 0.025537 | 0.027079 | none |

| 0.075 | 1 | 1.0 | 1.0 | 0.026787 | 0.027450 | none |

| 0.075 | 2 | 1.0 | 1.0 | 0.025667 | 0.027293 | none |

| 0.075 | 3 | 1.0 | 1.0 | 0.026684 | 0.028394 | none |

| 0.05 | 0 | 1.0 | 1.0 | 0.026608 | 0.027621 | none |

| 0.05 | 1 | 1.0 | 1.0 | 0.026534 | 0.027052 | none |

| 0.05 | 2 | 1.0 | 1.0 | 0.025558 | 0.028534 | none |

| 0.05 | 3 | 1.0 | 1.0 | 0.025313 | 0.027404 | none |

Reverse-order repeat: **0** payload differences. Evidence: [repeat-main](fresh/scratch/deadline-repeat-main.jsonl), [repeat-branch](fresh/scratch/deadline-repeat-branch.jsonl). The recorded first-run differences remain. No claim of universally identical execution deadlines is made.

## 3. New form, recovery and tolerance tests

**Fact, high confidence:** new geometry runs use score(..., version="0.5.0") and the production BREP round-trip. Diagnostic monkeypatches are separate trusted tests, not claims of a model mutating the scorer.

N014 to N019 used an incorrect UpdateFace overload and are harness failures. D001 to D006 correct the overload, but produce invalid B-reps rejected by clean_solid. Degree-32 attempts exceed the kernel-supported degree and are construction failures. Sewn surfaces supply valid recovery tests.

L001 to L006 place their nonplanar patch wholly inside a removed bore, so the actual retained geometry is unchanged. The peak UV has `TopAbs_OUT`. They are correct controls, not wrong accepted parts. L007 to L012 and all T cases retain the bump; L009, L012 and T004 were separately confirmed `TopAbs_IN`. Finding a nonplanar pole alone does not establish a wrong trimmed part.

N027 adds a loose envelope face; N028 duplicates the coincident solid. They fail topology/identity gates even when support is allowed. No tested valid wrong part whose **actual whole retained boundary** lies exactly on the allowed supports received 1.0. Successes exploit tolerance or uncertified support. **Inference, moderate confidence:** exact certified supports plus the intended occupied topology should determine the plate; this audit is not a proof over all B-reps.

### Every additional test result

| ID | Construction | Score | Valid in scored measurement | Form | Extra / missing mm3 | Failed checks / error | Classification |
|---|---|---:|---|---|---|---|---|

| N001 | full_face_pocket_3e-07 | 0.0 | None | None | None / None | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | test geometry |

| N002 | full_face_pocket_5e-07 | 0.0 | True | True | 0.0 / 0.0 | gate:single_solid | test geometry |

| N003 | full_face_pocket_8e-07 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N004 | full_face_pocket_1.2e-06 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| N005 | full_face_pocket_2e-06 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| N006 | rotation_Z_3e-10_rad | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N007 | rotation_X_3e-10_rad | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N008 | rotation_Z_8e-10_rad | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N009 | rotation_X_8e-10_rad | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N010 | rotation_Z_1.2e-09_rad | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| N011 | rotation_X_1.2e-09_rad | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| N012 | rotation_Z_2e-09_rad | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| N013 | rotation_X_2e-09_rad | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| N014 | warped_spline_pole_1e-08 | 0.0 | None | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP | construction error |

| N015 | warped_spline_pole_5e-08 | 0.0 | None | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP | construction error |

| N016 | warped_spline_pole_1e-07 | 0.0 | None | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP | construction error |

| N017 | warped_spline_pole_2e-07 | 0.0 | None | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP | construction error |

| N018 | warped_spline_pole_1e-05 | 0.0 | None | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP | construction error |

| N019 | warped_spline_pole_0.001 | 0.0 | None | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP | construction error |

| N020 | far_origin_pocket_0.001 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N021 | far_origin_pocket_0.004 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N022 | far_origin_pocket_0.0049 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N023 | far_origin_pocket_0.006 | 0.9 | True | True | 0.0 / 4.665458908595533 | R9:no_other_features | test geometry |

| N024 | micro_counterbore_5e-07 | 0.0 | True | True | 0.0 / 0.0 | gate:clean_solid | test geometry |

| N025 | micro_counterbore_8e-07 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N026 | micro_counterbore_1.2e-06 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| N027 | loose_envelope_face | 0.0 | True | False | None / None | gate:clean_solid, gate:is_plate, R2:width, R6:material, R7:edge_margin, R9:no_other_features | test geometry |

| N028 | second_coincident_solid | 0.0 | True | True | 0.0 / 0.0 | gate:single_solid, gate:is_plate, R6:material | test geometry |

| N029 | largest_micro_pocket | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| D001 | warped_spline_pole_1e-08_fixed | 0.0 | False | True | 23457.475377400297 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D002 | warped_spline_pole_5e-08_fixed | 0.0 | False | True | 23457.47537809547 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D003 | warped_spline_pole_1e-07_fixed | 0.0 | False | True | 23457.47537896444 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D004 | warped_spline_pole_2e-07_fixed | 0.0 | False | True | 23457.475380702384 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D005 | warped_spline_pole_1e-05_fixed | 0.0 | False | False | 23457.475551020692 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D006 | warped_spline_pole_0.001_fixed | 0.0 | False | False | 23457.49275664575 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D007 | spline_degree4_amp1e-07 | 0.0 | False | True | 23457.475378739946 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D008 | spline_degree4_amp1e-05 | 0.0 | False | False | 23457.47552856992 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D009 | spline_degree4_amp0.001 | 0.0 | False | False | 23457.490511567034 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D010 | spline_degree4_amp0.004 | 0.0 | False | False | 23457.53591458858 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D011 | spline_degree8_amp1e-07 | 0.0 | False | True | 23457.47537736272 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D012 | spline_degree8_amp1e-05 | 0.0 | False | False | 23457.4753908497 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D013 | spline_degree8_amp0.001 | 0.0 | False | False | 23457.476739547536 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D014 | spline_degree8_amp0.004 | 0.0 | False | False | 23457.480826510677 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D015 | spline_degree16_amp1e-07 | 0.0 | False | True | 23457.475377227365 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D016 | spline_degree16_amp1e-05 | 0.0 | False | True | 23457.47537731257 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D017 | spline_degree16_amp0.001 | 0.0 | False | False | 23457.475385833037 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D018 | spline_degree16_amp0.004 | 0.0 | False | False | 23457.47541165264 / 0.0 | gate:clean_solid, R9:no_other_features | test geometry |

| D019 | spline_degree32_amp1e-07 | 0.0 | None | None | None / None | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value | construction error |

| D020 | spline_degree32_amp1e-05 | 0.0 | None | None | None / None | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value | construction error |

| D021 | spline_degree32_amp0.001 | 0.0 | None | None | None / None | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value | construction error |

| D022 | spline_degree32_amp0.004 | 0.0 | None | None | None / None | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value | construction error |

| D023 | cylinder_spline_warp1e-08 | 0.0 | False | False | None / None | gate:clean_solid, gate:is_plate, R4a:hole_count, R5:hole_pattern, R6:material, R9:no_other_features | test geometry |

| D024 | cylinder_spline_warp1e-07 | 0.0 | False | False | None / None | gate:clean_solid, gate:is_plate, R4a:hole_count, R5:hole_pattern, R6:material, R9:no_other_features | test geometry |

| D025 | cylinder_spline_warp1e-06 | 0.0 | False | False | None / None | gate:clean_solid, gate:is_plate, R4a:hole_count, R5:hole_pattern, R6:material, R9:no_other_features | test geometry |

| D026 | cylinder_spline_warp1e-05 | 0.0 | False | False | None / None | gate:clean_solid, gate:is_plate, R4a:hole_count, R5:hole_pattern, R6:material, R9:no_other_features | test geometry |

| D027 | cylinder_spline_warp0.001 | 0.0 | False | False | None / None | gate:clean_solid, gate:is_plate, R4a:hole_count, R5:hole_pattern, R6:material, R9:no_other_features | test geometry |

| D032 | micro_pocket_depth8e-07 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| D033 | micro_pocket_depth9.9e-07 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| D034 | micro_pocket_depth1e-06 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D035 | micro_pocket_depth1.01e-06 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D036 | micro_pocket_depth1.2e-06 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D037 | micro_pocket_depth0.0049 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D038 | counterbore_dr4e-07_depth0.0049 | 0.0 | True | True | 0.0 / 0.0 | gate:clean_solid | test geometry |

| D039 | counterbore_dr4e-07_depth0.006 | 0.0 | True | True | 0.0 / 0.0 | gate:clean_solid | test geometry |

| D040 | counterbore_dr4e-07_depth3 | 0.0 | True | True | 0.0 / 0.0 | gate:clean_solid | test geometry |

| D041 | counterbore_dr4e-07_depth6 | 0.0 | True | True | 0.0 / 0.0 | gate:clean_solid | uniform bore enlargement; correct control |

| D042 | counterbore_dr4.9e-07_depth0.0049 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D043 | counterbore_dr4.9e-07_depth0.006 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D044 | counterbore_dr4.9e-07_depth3 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D045 | counterbore_dr4.9e-07_depth6 | 1.0 | True | True | 0.0 / 0.0 | none | uniform bore enlargement; correct control |

| D046 | counterbore_dr6e-07_depth0.0049 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D047 | counterbore_dr6e-07_depth0.006 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D048 | counterbore_dr6e-07_depth3 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D049 | counterbore_dr6e-07_depth6 | 1.0 | True | True | 0.0 / 0.0 | none | uniform bore enlargement; correct control |

| D050 | counterbore_dr1e-06_depth0.0049 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D051 | counterbore_dr1e-06_depth0.006 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D052 | counterbore_dr1e-06_depth3 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| D053 | counterbore_dr1e-06_depth6 | 1.0 | True | True | 0.0 / 0.0 | none | uniform bore enlargement; correct control |

| D054 | large_far_origin_depth0.0049 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| D055 | large_far_origin_depth0.005 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| D056 | large_far_origin_depth0.0051 | 0.9 | True | True | 0.0 / 3.184132050712844 | R9:no_other_features | test geometry |

| S001 | sewn_bezier_plate_0 | 1.0 | True | True | 0.0 / 0.0 | none | exact spline control |

| S002 | sewn_bezier_plate_1e-08 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| S003 | sewn_bezier_plate_5e-08 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| S004 | sewn_bezier_plate_1e-07 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| S005 | sewn_bezier_plate_2e-07 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| S006 | sewn_bezier_plate_8e-07 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| S007 | sewn_bezier_plate_1e-05 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| S008 | sewn_bezier_plate_0.001 | 0.9 | True | False | 0.0 / 0.0 | R9:no_other_features | test geometry |

| S009 | revolved_bezier_bore_0 | 1.0 | True | True | 0.0 / 0.0 | none | exact spline control |

| S010 | revolved_bezier_bore_1e-08 | 0.0 | None | None | None / None | model code exceeded 10s execution budget | test geometry |

| S011 | revolved_bezier_bore_5e-08 | 1.0 | True | True | 0.0 / 0.0 | none | test geometry |

| S012 | revolved_bezier_bore_1e-07 | 0.7 | True | False | 0.0 / 596.2998841264496 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | test geometry |

| S013 | revolved_bezier_bore_2e-07 | 0.0 | True | False | 0.0 / 795.066521485359 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | test geometry |

| S014 | revolved_bezier_bore_8e-07 | 0.0 | True | False | 0.0 / 795.0667479826454 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | test geometry |

| S015 | revolved_bezier_bore_1e-05 | 0.0 | True | False | 0.0 / 795.0693935744066 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | test geometry |

| S016 | revolved_bezier_bore_0.001 | 0.0 | True | False | 0.0 / 795.3649635025527 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | test geometry |

| L001 | local_spline_0.123_0.001_1e-05 | 1.0 | True | True | 0.0 / 0.0 | none | bump removed by bore; correct control |

| L002 | local_spline_0.123_0.001_0.001 | 1.0 | True | True | 0.0 / 0.0 | none | bump removed by bore; correct control |

| L003 | local_spline_0.123_0.001_0.004 | 1.0 | True | True | 0.0 / 0.0 | none | bump removed by bore; correct control |

| L004 | local_spline_0.127_0.0001_1e-05 | 1.0 | True | True | 0.0 / 0.0 | none | bump removed by bore; correct control |

| L005 | local_spline_0.127_0.0001_0.001 | 1.0 | True | True | 0.0 / 0.0 | none | bump removed by bore; correct control |

| L006 | local_spline_0.127_0.0001_0.004 | 1.0 | True | True | 0.0 / 0.0 | none | bump removed by bore; correct control |

| L007 | local_spline_0.333_0.001_1e-05 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| L008 | local_spline_0.333_0.001_0.001 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| L009 | local_spline_0.333_0.001_0.004 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| L010 | local_spline_0.501_0.0001_1e-05 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| L011 | local_spline_0.501_0.0001_0.001 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| L012 | local_spline_0.501_0.0001_0.004 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| T001 | local_spline_scale_0.01 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| T002 | local_spline_scale_0.1 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| T003 | local_spline_scale_1 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

| T004 | local_spline_scale_5 | 1.0 | True | True | 0.0 / 0.0 | none | retained bump; wrong part |

Full code/specs/raw reports: [form-attacks.jsonl](fresh/scratch/form-attacks.jsonl), [deep-attacks.jsonl](fresh/scratch/deep-attacks.jsonl), [spline-attacks.jsonl](fresh/scratch/spline-attacks.jsonl), [local-spline-attacks.jsonl](fresh/scratch/local-spline-attacks.jsonl), [scaled-spline-attacks.jsonl](fresh/scratch/scaled-spline-attacks.jsonl).

Exact planar Bezier plates and straight revolved Bezier bores pass as correct controls. Small nonzero deviations also recover as planes/cylinders and can score 1.0; larger smooth deviations in these families fail recovery/form. `_analytic_adaptor` therefore does not recognize exact forms only. The retained localized bump is a stronger counterexample because its height is far above kernel confusion and both form tolerances.

### Attained sizes and boundaries

| Family | Accepted wrong construction | Rejected neighbor | Established scope |
|---|---|---|---|
| broad ordinary pocket | 9.9e-7 mm deep, nearly 80 x 60 mm | 1.01e-6 mm gives 0.9 | actual broad feature fits linear tolerance |
| largest-area micro-pocket | 8e-7 mm, nearly 214 x 150 mm | 2e-7 form variant rejects it | achieved loss about 0.02548 mm3 |
| remote-origin pocket | 0.005 mm, nearly 214 x 150 mm | 0.0051 mm gives 0.9 from residual | achieved loss 159.227645 mm3 |
| ordinary centered rotation | 8e-10 rad about X/Z | 1.2e-9 rad gives 0.9 | observed angular cutoff for this construction |
| localized retained spline | pole lift 5 mm, retained height 0.986720900 mm | no larger lift tested | attained height, not maximum |

**Inference, moderate confidence:** the localized recovery failure has no useful height bound from the stated 1e-6 mm/1e-9 rad constants. No global maximum was proved. The numerical volume integrator returns near-nominal values on these bumps, so reported volume is not an independent exact certificate.

### None, failure and exception paths

| Condition | Score | Observed result |
|---|---:|---|
| trusted conformance returns None | 0.9 | R9 fails |
| trusted conformance returns False | 0.9 | R9 fails |
| trusted conformance raises RuntimeError | 0.9 | R9 fails; stage/type/message retained |
| A080, 0.009 mm plate, ideal thinner than band | 0.8 | R3/R9 fail, residual None, shape_error retained |
| tested recovery returns None on nonanalytic faces | 0.9 or 0.0 | form/bores/gates fail as shown |

**Fact, high confidence:** no tested None/exception path yields 1.0. The rubric explicitly rejects unavailable form or residual results. Conversion exceptions become None; exceptions outside that catch can become build failures in reuse mode. This is not proof that every kernel exception is handled in every mode. [fix-checks.json](fresh/scratch/fix-checks.json) preserves the injected tests. No model-origin monkeypatch was used.

### The two design choices

**Fact, high confidence:** both choices allow wrong parts through in this implementation. The larger linear tolerance accepts the broad micro-pocket floor and sidewalls; the 0.005 mm band blinds the second look to those pockets and the remote-origin floor. The following trusted in-memory variants change only those measure constants; residual cutoff stays 0.001 mm3. No tracked code was changed.

| Construction | Current | 2e-7 form, band kept | Unbanded, form kept | Both |
|---|---:|---:|---:|---:|

| full_face_pocket_8e-07 | 1.0 | 0.9 | 0.9 | 0.9 |

| far_origin_pocket_0.0049 | 1.0 | 0.9 | 0.9 | 0.9 |

| largest_micro_pocket | 1.0 | 0.9 | 0.9 | 0.9 |

| large_far_origin_depth0.005 | 1.0 | 0.9 | 0.9 | 0.9 |

| sewn_bezier_plate_0 | 1.0 | 1.0 | 1.0 | 1.0 |

| sewn_bezier_plate_5e-08 | 1.0 | 1.0 | 1.0 | 1.0 |

| revolved_bezier_bore_5e-08 | 1.0 | 1.0 | 1.0 | 1.0 |

The unbanded large remote-origin case reports 159.227659980 mm3 missing and fails R9. The unbanded largest micro-pocket reports 0.025476425 mm3 missing and fails R9. Tiny recovered smooth deviations still pass both variants. Neither choice alone certifies localized spline geometry.

**Opinion, moderate confidence:** a band can remain if an independently sound whole-face certificate enforces the form policy; it hides known failures here. An unbanded backstop needs correct-representation and runtime validation. The optional in-process unbanded repair prototype stalled on C039's large-area exact NURBS after its first 38 correct controls passed, and was stopped. That is a prototype limitation, not an unchanged-branch timeout or proof that every unbanded design hangs. Its partial success does not make it merge-ready.

### Earlier findings, B1 to B5 and R1 to R4

| Finding | Status | Fresh evidence |
|---|---|---|
| B1, volume band/residual accepts extra geometry | partly resolved | original pockets/bosses/slots/chamfers/lugs fail; N003/N029, N020 to N022, D054/D055 and retained spline bumps still score 1.0 |
| B2, rounding widens nominal tolerance | resolved for the original finding | raw-value rounding wedges fail; A067/A068 use the separately documented NUM_EPS allowance, not display rounding |
| B3, global environment version and versionless cache | resolved | actual old/new/old callbacks with shared state give 1.0/0.9/1.0; instance versions 0.4.0/0.5.0; cache includes scorer version |
| B4, exact NURBS false rejection | resolved for the original finding | C013/C026/C039/C052/C065/C078 and A044 all score 1.0 on unchanged branch; recovery soundness is a separate new issue |
| B5, legacy pays for new work | partly resolved under the strict acceptance rule | source confines new work to strict=True; 3,161 reward/check/parsed results agree; original branch-only 0.05 s slowdown gone, but first probe has six main-only timeouts; reverse-order repeat has zero differences |
| R1, exhaustive matching explosion | resolved | augmenting matching finds four matches among 4,000 injected candidates in about 0.0021 s; no n-choose-4 enumeration |
| R2, loss of residual exception diagnostics | resolved | A080 retains envelope-thinner-than-band RuntimeError; injected form exception retains stage/type/message; missing values fail R9 |
| R3, recorded version mandatory in analysis | resolved for inspected local paths | failure_modes refuses missing metadata, uses strict tolerance; label_check refuses mixed versions and checks label version; replay requires one supported recorded version; verify_hub passes recorded version and rejects absent metadata |
| R4, supplemental families and narrow claims | partly resolved | 17 AUDIT_ regressions added; 72/72 hand-labelled cases pass; finite-suite claims narrowed, but remote origins, localized spline recovery and at-any-size assertions remain uncovered |

Environment and matching probes are trusted tests, not geometry-origin exploits. Metadata fixture subprocess exits: missing version 1, known strict version 0, mixed label versions 1. Source inspections of replay_eval.py and verify_hub.py were local; no hosted Hub was accessed. The fixed original B2/B4 reproductions do not establish a universal absence of rounding/recovery problems.

### Documentation reviewed against the current code and observations

| Location | Statement | Assessment |
|---|---|---|
| README 18, 118 onward; CHANGELOG 9 to 13 | plate, four holes, nothing else within 0.1 mm | intended contract is clear; observed recovery/origin counterexamples violate it; NUM_EPS extends nominal limits |
| README 150 to 157 | 1e-6 mm and 1e-9 rad are kernel noise, not a feature allowance; features fail whatever their size | too strong and false under literal geometric correctness: broad micro-pockets and nearly 1 mm retained spline bump pass |
| README 156 to 158 | measured envelope/bores isolate shape from dimension errors | true for ordinary controls; envelope calculation can miss localized geometry, so it is not an independent support certificate |
| README 159 to 161; CHANGELOG 16 to 18 | residual is a second look that can only add failure | true conjunction; README's explanation omits the blind 0.005 mm layer and 0.001 mm3 residual allowance |
| CHANGELOG 25 to 27 | all fixed before merge | supported if restricted to original reproduced cases; mechanism-level absence of other features is only partly fixed |
| CHANGELOG 51 to 52 | shallow pockets fail R9 at any size | disproved by N003/N029 and the accepted 9.9e-7 mm pocket |
| README 171 to 173 | unrounded measurement, 6.600049 mm rejected, 1e-6 mm numerical slack | supported; A067/A068 demonstrate the declared remaining allowance |
| README 206 to 210; CHANGELOG 52 | exact NURBS plate now passes | supported by all original NURBS controls; does not prove only exact analytic surfaces recover |
| README 109 to 115; CHANGELOG 37 to 44 | legacy selectable; recorded-version replay; none of new work | source and saved semantic results support it; raw errors include pre-existing varying addresses; universal identical-deadline interpretation is not established |
| README 20/392; CHANGELOG 32 to 37 | 2,366 mutants, zero false full credit on 1,646 wrong, zero false rejection on 720 correct | matches committed result records and is now qualified as finite cases; optional fresh full-suite rerun did not complete, so v2 does not independently reproduce those counts |
| README 36/527 | 72 hand-labelled cases | independently reproduced: 72/72, including legacy saved-answer control |
| README 164 to 168; CHANGELOG 35 to 37 | finite validation is not a proof that no wrong part passes | appropriately narrowed and supported |

## 4. What could not be verified

- **Fact, high confidence:** Linux fork isolation/hardening and GL fallback were not exercised. All required executions used Windows reuse mode.
- **Fact, high confidence:** no live hosted Hub, remote serialization, deployment, remote worker or paid model was accessed.
- **Fact, high confidence:** the optional 2,366-case validation rerun did not complete after more than twelve minutes and was stopped before the deadline probe. Its runner buffers results until completion, so no completed fresh artifact was produced. Published counts were checked against committed records, not certified as rerun in v2.
- **Fact, high confidence:** an optional in-process unbanded prototype stalled at exact-NURBS C039 and was stopped. Its first 38 correct controls passed. That is not a timeout of the unchanged branch; no unbanded merge-readiness claim is made.
- **Inference, moderate confidence:** no global maximum hidden feature height/volume was established. Achieved values are 0.986720900 mm retained protrusion and 159.227645 mm3 removed pocket material. Stated tolerances do not bound the observed recovery failure.
- **Opinion, high confidence:** proposed guards need general recovered-cylinder certificates, representation handling, finite-suite/package checks and Linux verification before merge. No diff was applied.

**Fact, high confidence:** the first bounded guard prototype passed 73/79 correct constructions and rejected six exact NURBS controls. It rejected N003, N022, D055, L009 and T004 at 0.9. This is an unfinished proposal, not a fix to apply blindly. [guard-prototype-results.json](fresh/scratch/guard-prototype-results.json).

A scratch follow-up adds only 1e-12 mm to the certified face-bound comparison to account for floating-point error at the 2e-7 endpoint: 79/79 original correct constructions pass. Reproduced wrong-case scores: N003=0.9; N022=0.9; D055=0.9; L009=0.9; T004=0.9. The report diff should include that endpoint allowance if adopting this prototype. It does not establish a general certificate. [guard-prototype-float-results.json](fresh/scratch/guard-prototype-float-results.json).

All reproduction drivers and evidence are under [fresh/scratch](fresh/scratch/). The required drivers are rerun_corpus.py, run_compat.py and deadline_probe.py. Additional drivers are form_attacks.py, deep_attacks.py, spline_attacks.py, local_spline_attacks.py, scaled_spline.py, trim_certificate.py, check_fixes.py and design_choices.py. Use the venv interpreter stated above. The comparison uses the exact original input file rather than a newly selected sample.
