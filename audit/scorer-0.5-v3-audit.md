1. **Change first.** Do not merge `4990743` with the current full-credit contract.
2. **Fact, high confidence:** ordinary CadQuery counterbores N025 and N026 still score **1.0**, despite retained boundary inconsistencies of **8e-7 and 1.2e-6 mm**, beyond the declared 1e-7 mm equivalence.
3. **Fact, high confidence:** V2-B1 and V2-B2 are resolved for their reproductions; V2-B3 is partly resolved because the supporting-surface test does not bound trim consistency.
4. **Fact, high confidence:** all **73 non-spline original correct constructions pass**; the six NURBS constructions fail by design, with other equivalent stored spline controls listed separately.
5. **Fact, high confidence:** all **3,161 legacy rewards, named check verdicts and parsed flags agree** with main; normalized error texts also agree.

# Scorer 0.5.0, round 3 audit

Target: `feat/scorer-0.5`, HEAD `4990743346555b0b93a1865b6a069b14c5ed83d9`. Main: `7c17439a84529417d4516882b4034aa148c86017`. Audit date: 2026-10-05. Facts are executions/source checks; inferences explain implications; opinions are proposals. Confidence is high for local reproductions, moderate for general claims and repair completeness.

The repository remained read only. No tracked edit, commit, push, network request, credential file, paid service or external system was used. All new artifacts are under v3. Runtime: Windows, Python 3.12, CadQuery 2.8.0, reuse sandbox; venv interpreter `C:/Users/bgare/dev/cad-spec-env/environments/cad_spec/.venv/Scripts/python.exe`. PYTHONPATH selects this worktree. The main snapshot's measure.py, rubric.py, tasks.py and __init__.py match `git show main:...` after CRLF normalization. The comparison input is byte-identical to the first audit's 3,161-answer input.

## 1. Required changes: boundary consistency and metric policy

### R3-B1. Allowed supporting surfaces do not imply a boundary consistent to 1e-7 mm

**Fact, high confidence:** N026 is an ordinary CadQuery cut, with no direct kernel construction or manually increased tolerance. It receives **1.0**, no failed checks. It measures as one valid solid, one shell, four open holes, form=True and residual extra/missing **0.0/0.0 mm3**:

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

result=result.cut(cq.Workplane("XY").workplane(offset=2.9999988).center(30,20).circle(3.2500004).extrude(1.0000012))
```

The nominal bore radius is 3.25 mm. This code cuts a radius 3.2500004 mm mouth to depth 1.2e-6 mm. The returned B-rep does not retain a separate shoulder and enlarged wall. Instead, its shared 3D trim edge is a circle of radius **3.2500004 mm** at **Z=2.9999988 mm**, while the adjacent supporting top plane is at **Z=3 mm** and the bore surface radius remains **3.25 mm**. The edge and its curve on the top face differ by **1.2e-6 mm**; on the cylindrical face they differ by about **4e-7 mm**. This is not an unchanged Boolean result. The measured nominal cylindrical wall ends at Z=2.9999988, but the simple-through-hole gate's 0.01 mm endpoint allowance admits it.

OCCT accepts the B-rep using its stored edge tolerance, approximately **1.200012e-6 mm**. The face tolerance remains 1e-7 mm. The scorer checks supporting planes/cylinders, but never requires the trims and adjacent surfaces to agree to its form tolerance. Thus a kernel-valid, tolerance-consistent B-rep can fall outside the scorer's announced equivalence and still receive full credit.

N025 repeats the same failure at depth **8e-7 mm**: score **1.0**, edge-to-top-face disagreement **8e-7 mm**, stored edge tolerance about **8.00008e-7 mm**. Both use only ordinary Workplane modelling calls. Their source snippets are retained in [corpus-rerun.jsonl](scratch/corpus-rerun.jsonl).

The observed geometry is a tolerance-closed trim inconsistency at a requested counterbore, not a certified watertight stepped solid with a separately represented shoulder. It is nevertheless wrong under a contract requiring the whole retained boundary to agree within 1e-7 mm. If such larger kernel inconsistencies are intentionally acceptable, that is a wider equivalence policy which must be stated. They cannot be called features wholly below 1e-7 mm.

A direct diagnostic for an edge on its adjacent face is:

```python
from OCP.BRepAdaptor import BRepAdaptor_Curve
curve = BRepAdaptor_Curve(edge.wrapped)
on_face = BRepAdaptor_Curve(edge.wrapped, face.wrapped)
t = (curve.FirstParameter() + curve.LastParameter()) / 2
print(curve.Value(t).Distance(on_face.Value(t)))
# N026, top-face bore edge: approximately 1.2e-6 mm.
```

[boundary-diagnostics.json](scratch/boundary-diagnostics.json) records curve types, radii, axis locations, surface types, tolerances and nine curve/face comparisons per edge. The diagnostic is direct evaluation of the retained analytic boundary, independent of R9. It supplies a reproducible inconsistency, not a general sampling certificate.

**Inference, high confidence:** BRepCheck_Analyzer validates geometry against tolerances carried by the B-rep. That is a different predicate from consistency to the scorer's fixed 1e-7 mm. The premise that a valid single solid with allowed supports must be the plate requires a matching boundary-consistency condition. The current validity and form checks do not provide it.

**Opinion, high confidence:** retain the stored-type and extent checks, and add a strict boundary check independent of caller/Boolean-produced tolerances. Merely rejecting every shape with a large tolerance would reject harmless metadata-only controls. A useful small repair prototype copies the shape, forces only the copy's tolerances to the declared form tolerance and runs the kernel's exact validity method. This neither repairs nor edits the scored geometry.

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@
-    return Measurements(
+    valid = bool(BRepCheck_Analyzer(topo).IsValid())
+    if strict and valid:
+        from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy
+        from OCP.ShapeFix import ShapeFix_ShapeTolerance
+        try:
+            checked = BRepBuilderAPI_Copy(topo, True, False).Shape()
+            ShapeFix_ShapeTolerance().LimitTolerance(
+                checked, FORM_LINEAR_TOL, FORM_LINEAR_TOL)
+            valid = bool(BRepCheck_Analyzer(checked, True, False, True).IsValid())
+        except Exception as exc:
+            valid = False
+            shape_error = shape_error or (
+                f"strict boundary check failed: {type(exc).__name__}: {exc}"[:200])
+    return Measurements(
@@
-        valid=bool(BRepCheck_Analyzer(topo).IsValid()),
+        valid=valid,
```

**Fact, high confidence:** the scratch implementation of this prototype rejects N025 and N026 at **0.0** through clean_solid, preserves **73/73** non-spline C controls at **1.0**, and preserves all **12/12** correct plates with deliberately inflated face/edge/vertex tolerance metadata at **1.0**. The six NURBS C controls remain rejected by the existing representation policy. [tolerance-prototype.json](scratch/tolerance-prototype.json) contains every result.

**Opinion, moderate confidence:** this is a tested candidate for the observed defect, not a proof that kernel validity catches every malformed boundary. It adds strict-mode work and needs normal release/finite-suite, runtime and Linux verification before integration. The legacy path must retain its original validity semantics. No repository patch was applied.

Add the ordinary counterbore as a regression after the scorer change:

```diff
--- a/scripts/test_rubric_050.py
+++ b/scripts/test_rubric_050.py
@@
+CASES["AUDIT4_tolerance_closed_bore_mouth"] = Case(
+    REF + 'result=result.cut(cq.Workplane("XY").workplane(offset=2.9999988)'
+          '.center(30,20).circle(3.2500004).extrude(1.0000012))
',
+    _f("gate:clean_solid"))
```

That expectation assumes the proposed validity gate. A repair which instead rejects through R9 should pin the corresponding named check rather than assert the prototype's exact check name.

### R3-B2. Metric policy: componentwise bore checks exceed a 1e-7 mm distance bound

**Fact, high confidence:** E003 uses only ordinary CadQuery modelling. It is the same synthetic plate with nominal 2.5 mm bores, cut by cylinders tilted diagonally. Each bore axis component at a plate end shifts about 9.9e-8 mm, so the X/Y tests pass separately. The Euclidean shift is **1.400071427e-7 mm**, above 1e-7 mm. Observed score **1.0**, no failed checks, form=True. E002 similarly passes at **1.272792206e-7 mm**; E004 fails R9 at **1.442497834e-7 mm** when each component exceeds 1e-7.

```python
import cadquery as cq
from cad_spec.tasks import Spec
from cad_spec.rubric import score
s = Spec("synthetic-diagonal", 80, 60, 6, 2.5, 10)
# Submit this code string to score(code, s, version="0.5.0"):
code = """
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)
for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
    cutter=cq.Workplane("XY").circle(1.25).extrude(8,both=True)
    cutter=cutter.rotate((0,0,0),(-1,1,0),2.673939458986605e-06).translate((x,y,0))
    result=result.cut(cutter)
"""
print(score(code, s, version="0.5.0").reward)  # 1.0
```

The exact angle and measured part are preserved in [diagonal-cases.jsonl](scratch/diagonal-cases.jsonl). **Inference, high confidence:** independent X/Y allowances define a box in axis-error space. They permit a diagonal norm up to sqrt(2) times the tolerance. Diameter and center error also spend separate allowances. Thus the current code does not enforce a single 1e-7 mm geometric-distance budget on the bore surface.

**Opinion, high confidence:** if the numerical equivalence means geometric distance, combine center and radius error in one bound. If it means separate coordinate tolerances, state that explicitly instead of implying a global distance bound. This metric issue is a contract clarification when coordinatewise tolerance is intentional; it does not justify calling accepted diagonal parts outside that explicitly defined policy.

A conservative cylinder bound uses the maximum ellipse-radius difference at a horizontal section as well as the Euclidean center displacement:

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@
-                       and all(abs(x - h.x) <= FORM_LINEAR_TOL and abs(y - h.y) <= FORM_LINEAR_TOL
+                       and all(math.hypot(x - h.x, y - h.y)
+                               + max(abs(cylinder.Radius() - h.diameter / 2),
+                                     abs(cylinder.Radius() / abs(direction.Z()) - h.diameter / 2))
+                               <= FORM_LINEAR_TOL
                                for x, y in ends)
```

This is a proposed distance policy, not a repository edit. The existing diameter guard can remain as an additional restriction. The scratch version applies this bound after the current form check; results are summarized below.


## 2. Earlier corpus rerun

**Fact, high confidence:** all **322** earlier parts were rerun: A001 to A130, C001 to C079, and every N/D/S/L/T row from v2, preserving their IDs and exact source/specification. Complete fresh reports and Measurements are in [corpus-rerun.jsonl](scratch/corpus-rerun.jsonl). None means unavailable, not an implicit pass. A zero reward with no checks and a build error is not a compliant part.

### Every incorrect earlier part still receiving full credit

| ID | Part | Score | Evidence |
|---|---|---:|---|
| N025 | 8e-7 mm deep bore-mouth cut | 1.0 | retained edge/top-face gap 8e-7 mm, radius discrepancy about 4e-7 mm, larger stored edge tolerance |
| N026 | 1.2e-6 mm deep bore-mouth cut | 1.0 | retained edge/top-face gap 1.2e-6 mm, radius discrepancy about 4e-7 mm, larger stored edge tolerance |

These are the two full-credit earlier shapes outside the stated whole-boundary numerical equivalence. Other full-score rows below are unchanged/correct controls or fit the explicitly declared equivalence. Nominal-outside-limit values within the documented 1e-9 slack are accepted by policy, not silently counted as hidden errors.

### Every full-score non-C row, including controls

| ID | Case | Score | Classification |
|---|---|---:|---|

| A001 | nominal | 1.0 | correct unchanged geometry or inclusive-limit control |

| A048 | coincident_bore | 1.0 | correct unchanged geometry or inclusive-limit control |

| A055 | probe_lug_y0.3_d0.004 | 1.0 | correct unchanged geometry or inclusive-limit control |

| A058 | compound_one | 1.0 | correct unchanged geometry or inclusive-limit control |

| A063 | length_0.1 | 1.0 | correct unchanged geometry or inclusive-limit control |

| A064 | diameter_0.1 | 1.0 | correct unchanged geometry or inclusive-limit control |

| A065 | z_datum_0.1 | 1.0 | correct unchanged geometry or inclusive-limit control |

| A075 | centres_0.1 | 1.0 | correct unchanged geometry or inclusive-limit control |

| N006 | rotation_Z_3e-10_rad | 1.0 | tiny rotation within extent-based form equivalence |

| N007 | rotation_X_3e-10_rad | 1.0 | tiny rotation within extent-based form equivalence |

| N008 | rotation_Z_8e-10_rad | 1.0 | tiny rotation within extent-based form equivalence |

| N009 | rotation_X_8e-10_rad | 1.0 | tiny rotation within extent-based form equivalence |

| N010 | rotation_Z_1.2e-09_rad | 1.0 | tiny rotation within extent-based form equivalence |

| N011 | rotation_X_1.2e-09_rad | 1.0 | tiny rotation within extent-based form equivalence |

| N025 | micro_counterbore_8e-07 | 1.0 | wrong boundary outside 1e-7 equivalence; blocking |

| N026 | micro_counterbore_1.2e-06 | 1.0 | wrong boundary outside 1e-7 equivalence; blocking |

| D045 | counterbore_dr4.9e-07_depth6 | 1.0 | entire bore enlarged within dimension tolerance; correct control |

| D049 | counterbore_dr6e-07_depth6 | 1.0 | entire bore enlarged within dimension tolerance; correct control |

| D053 | counterbore_dr1e-06_depth6 | 1.0 | entire bore enlarged within dimension tolerance; correct control |

### Correct parts rejected, with intentional representations marked separately

**Fact, high confidence:** no non-spline C construction is rejected: **73/73** score 1.0. The six C exact-NURBS cases are intentional rejections. A044 is another exact-NURBS control. S001 is an exact planar Bezier top, and S009 has straight revolved Bezier bore profiles; their geometry is correct but their stored representation is unsupported. L001 to L006 are also correct geometry: the localized nonplanar portion is wholly inside a removed bore and absent from the retained face. All are listed separately as representation-policy rejections, not newly discovered non-spline false rejections.

| Correct ID | Construction | Score | Rejection classification |
|---|---|---:|---|

| A044 | nurbs_exact | 0.0 | stored spline/Bezier or spline-generated surface; rejected by design |

| C013 | nurbs_exact | 0.0 | stored spline/Bezier or spline-generated surface; rejected by design |

| C026 | nurbs_exact | 0.0 | stored spline/Bezier or spline-generated surface; rejected by design |

| C039 | nurbs_exact | 0.0 | stored spline/Bezier or spline-generated surface; rejected by design |

| C052 | nurbs_exact | 0.0 | stored spline/Bezier or spline-generated surface; rejected by design |

| C065 | nurbs_exact | 0.0 | stored spline/Bezier or spline-generated surface; rejected by design |

| C078 | nurbs_exact | 0.0 | stored spline/Bezier or spline-generated surface; rejected by design |

| S001 | sewn_bezier_plate_0 | 0.9 | stored spline/Bezier or spline-generated surface; rejected by design |

| S009 | revolved_bezier_bore_0 | 0.0 | stored spline/Bezier or spline-generated surface; rejected by design |

| L001 | local_spline_0.123_0.001_1e-05 | 0.9 | stored spline/Bezier or spline-generated surface; rejected by design |

| L002 | local_spline_0.123_0.001_0.001 | 0.9 | stored spline/Bezier or spline-generated surface; rejected by design |

| L003 | local_spline_0.123_0.001_0.004 | 0.9 | stored spline/Bezier or spline-generated surface; rejected by design |

| L004 | local_spline_0.127_0.0001_1e-05 | 0.9 | stored spline/Bezier or spline-generated surface; rejected by design |

| L005 | local_spline_0.127_0.0001_0.001 | 0.9 | stored spline/Bezier or spline-generated surface; rejected by design |

| L006 | local_spline_0.127_0.0001_0.004 | 0.9 | stored spline/Bezier or spline-generated surface; rejected by design |

The policy is surface representation dependence, not only refusal of the literal `toNURBS()` call. Near-planar Bezier cases S002 to S004 and near-cylindrical spline profiles are also excluded irrespective of their small deviation. Those are not exact-geometry plate controls; under a pure distance-only equivalence some would be equivalent, but the new stored-type policy intentionally takes priority. Their scores are in the complete table. Exact SurfaceOfRevolution/Bezier-generated bores are also outside the accepted stored-type policy. No claim that these geometrically correct parts become incorrect is made.

Original A deep_narrow_slot syntax errors, N014 to N019's wrong UpdateFace overload, and D019 to D022's unsupported degree-32 construction are retained harness errors. Their zeros do not establish geometric rejection. The malformed directly edited spline B-reps also do not prove valid-part rejection. The v2 distinction between L001 to L006's removed patch and L007 to L012's retained patch is preserved.

### A001 to A130, all rows

| ID | Case | v2 score | v3 score | Failed checks | Form | Extra / missing mm3 | Error |
|---|---|---:|---:|---|---|---|---|

| A001 | nominal | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A002 | broad_pocket_0.001 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A003 | broad_pocket_0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A004 | broad_pocket_0.005 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A005 | broad_pocket_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.24999999999941738 |  |

| A006 | broad_pocket_0.006 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 2.500000000000835 |  |

| A007 | broad_pocket_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 12.499999999999734 |  |

| A008 | boss_0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A009 | boss_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.42654590892095434 |  |

| A010 | boss_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 21.32729544590755 |  |

| A011 | boss_0.1 | 0.0 | 0.0 | gate:simple_through_holes, R9:no_other_features | False | 0.0 / 405.2186134722508 |  |

| A012 | edge_notch_0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A013 | edge_notch_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.04192999999890917 |  |

| A014 | edge_notch_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 2.096500000000576 |  |

| A015 | small_pocket_0.005 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 1.2375000000003403e-05 |  |

| A016 | small_pocket_0.02 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0001980000000000105 |  |

| A017 | small_pocket_0.1 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.004949999999999969 |  |

| A018 | deep_narrow_slot_0.039 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |

| A019 | deep_narrow_slot_0.041 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |

| A020 | deep_narrow_slot_0.05 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |

| A021 | side_tab_0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A022 | top_lip_0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A023 | side_tab_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.02395400999795847 |  |

| A024 | top_lip_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.4585869039211642 |  |

| A025 | side_tab_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 1.1977004999991943 |  |

| A026 | top_lip_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 22.92934519590751 |  |

| A027 | rotate_Z_0.0001 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A028 | rotate_X_0.0001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.0803144817107 |  |

| A029 | rotate_Z_0.001 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A030 | rotate_X_0.001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.2054117173273 |  |

| A031 | rotate_Z_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 3.783666131189786 |  |

| A032 | rotate_X_0.01 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 809.6802844372207 |  |

| A033 | rotate_Z_0.05 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 44.22307048173275 |  |

| A034 | rotate_X_0.05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 1001.9542050570437 |  |

| A035 | draft_0.001 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A036 | draft_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A037 | draft_0.1 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 2.393697342440646 |  |

| A038 | sheared_0.004 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A039 | sheared_0.02 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 4.040385646198465 |  |

| A040 | cone_0.001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.3110756787678 |  |

| A041 | cone_0.01 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 797.5152799843921 |  |

| A042 | ellipse | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 797.5127838275253 |  |

| A043 | polygon_128 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 794.7471583742455 |  |

| A044 | nurbs_exact | 1.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3860467275696 |  |

| A045 | countersink_0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A046 | countersink_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A047 | fifth_bore | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A048 | coincident_bore | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A049 | overlap_bore_0.0004 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A050 | overlap_bore_0.004 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 198.92234368738826 |  |

| A051 | overlap_bore_0.01 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 199.15595354362756 |  |

| A052 | coaxial_step | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | False | 0.0 / 0.0 |  |

| A053 | probe_lug_y0_d0.004 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A054 | probe_lug_y0_d0.05 | 0.9 | 0.9 | R9:no_other_features | False | 1.7997945554340325e-05 / 0.0 |  |

| A055 | probe_lug_y0.3_d0.004 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A056 | probe_lug_y0.3_d0.05 | 0.9 | 0.9 | R9:no_other_features | False | 1.2439020103472529e-05 / 0.0 |  |

| A057 | probe_notch | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 4.002048133976605e-06 |  |

| A058 | compound_one | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A059 | second_solid_bore | 0.0 | 0.0 | gate:single_solid, gate:simple_through_holes, R9:no_other_features | False | 0.0003141592653589902 / 0.0 |  |

| A060 | second_solid_outside | 0.0 | 0.0 | gate:single_solid, R1:length, R7:edge_margin, R9:no_other_features | False | 0.0 / 361.13679999999925 |  |

| A061 | loose_face | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | False | None / None |  |

| A062 | loose_edge | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | True | None / None |  |

| A063 | length_0.1 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A064 | diameter_0.1 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A065 | z_datum_0.1 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A066 | length_0.100001 | 0.9 | 0.9 | R1:length | True | 0.0 / 0.0 |  |

| A067 | diameter_0.100001 | 1.0 | 0.9 | R4b:hole_diameter | True | 0.0 / 0.0 |  |

| A068 | z_datum_0.100001 | 1.0 | 0.9 | R8:z_datum | True | 0.0 / 0.0 |  |

| A069 | length_0.10004 | 0.9 | 0.9 | R1:length | True | 0.0 / 0.0 |  |

| A070 | diameter_0.10004 | 0.9 | 0.9 | R4b:hole_diameter | True | 0.0 / 0.0 |  |

| A071 | z_datum_0.10004 | 0.9 | 0.9 | R8:z_datum | True | 0.0 / 0.0 |  |

| A072 | length_0.1001 | 0.9 | 0.9 | R1:length | True | 0.0 / 0.0 |  |

| A073 | diameter_0.1001 | 0.9 | 0.9 | R4b:hole_diameter | True | 0.0 / 0.0 |  |

| A074 | z_datum_0.1001 | 0.9 | 0.9 | R8:z_datum | True | 0.0 / 0.0 |  |

| A075 | centres_0.1 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| A076 | centres_0.1004 | 0.9 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A077 | centres_0.10049 | 0.9 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A078 | centres_0.1005 | 0.9 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A079 | centres_0.101 | 0.9 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A080 | residual_None_thin | 0.8 | 0.8 | R3:thickness, R9:no_other_features | True | None / None |  |

| A081 | many_bores_16 | 0.0 | 0.0 | gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A082 | many_bores_64 | 0.0 | 0.0 | gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A083 | many_bores_144 | 0.0 | 0.0 | none | None | None / None | model code exceeded 10s execution budget |

| A084 | threshold_through_slot_0.0128 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0009814015999999467 |  |

| A085 | threshold_through_slot_0.01295 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0010045379750001854 |  |

| A086 | threshold_through_slot_0.013 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0010123100000003584 |  |

| A087 | threshold_through_slot_0.0131 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0010279438999998725 |  |

| A088 | two_broad_pockets_0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A089 | two_broad_pockets_0.005 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A090 | six_skin_pockets | 0.0 | 0.0 | gate:single_solid, R9:no_other_features | False | 0.0 / 0.0 |  |

| A091 | actual_probe_lug_0.163 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 198.7665384992689 |  |

| A092 | actual_probe_lug_0.17 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 198.76653569926896 |  |

| A093 | actual_probe_lug_0.2 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | False | 0.0 / 198.76652369926896 |  |

| A094 | tiny_fifth_0.005 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A095 | hidden_fifth_0.005 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A096 | tiny_fifth_0.006 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A097 | hidden_fifth_0.006 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A098 | tiny_fifth_0.007 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A099 | hidden_fifth_0.007 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A100 | tiny_fifth_0.01 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | True | 0.0 / 0.0 |  |

| A101 | hidden_fifth_0.01 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A102 | bore_annular_membrane | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features | False | 0.00019787321328163258 / 0.0 |  |

| A103 | top_chamfer_0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A104 | top_chamfer_0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A105 | top_chamfer_0.01 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A106 | corner_fillet_0.001 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | False | 0.0 / 0.0 |  |

| A107 | corner_fillet_0.005 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A108 | corner_fillet_0.02 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 3.6011597542728735e-05 |  |

| A109 | fixed_deep_slot_0.039 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.009110790000000183 |  |

| A110 | fixed_deep_slot_0.041 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.01006918999999983 |  |

| A111 | fixed_deep_slot_0.05 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.01497499999999993 |  |

| A112 | hide_fifth_r0.003_h0.02 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A113 | hide_fifth_r0.003_h0.1 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A114 | hide_fifth_r0.005_h0.02 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A115 | hide_fifth_r0.005_h0.1 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A116 | hide_fifth_r0.007_h0.02 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A117 | hide_fifth_r0.007_h0.1 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features | False | 0.0 / 0.0 |  |

| A118 | largest_skin_gen-0032 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A119 | largest_skin_gen-0215 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| A120 | fillet_0.025 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.00027109974786697827 |  |

| A121 | fillet_0.03 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0007351040829427555 |  |

| A122 | fillet_0.04 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0023760532789156527 |  |

| A123 | fillet_0.05 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0049913409920744195 |  |

| A124 | annular_bridge_2e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features | False | 0.0004946830332089784 / 0.0 |  |

| A125 | annular_bridge_3e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features | False | 0.0007420245498281586 / 0.0 |  |

| A126 | annular_bridge_4e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features | False | 0.0009893660664375447 / 0.0 |  |

| A127 | diagonal_rounding | 0.9 | 0.9 | R5:hole_pattern | True | 0.0 / 0.0 |  |

| A128 | length_0.100049 | 0.9 | 0.9 | R1:length | True | 0.0 / 0.0 |  |

| A129 | diameter_0.100049 | 0.9 | 0.9 | R4b:hole_diameter | True | 0.0 / 0.0 |  |

| A130 | margin_0.1004 | 0.8 | 0.8 | R5:hole_pattern, R7:edge_margin | True | 0.0 / 0.0 |  |

### C001 to C079, all rows

| ID | Construction | Spec | v2 score | v3 score | Failed checks | Policy |
|---|---|---|---:|---:|---|---|

| C001 | reference | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C002 | Sketch | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C003 | polyline | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C004 | cutThruAll | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C005 | explicit_depth | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C006 | union_halves | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C007 | imprinted_halves | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C008 | mirror | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C009 | translate_chain | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C010 | Solid_primitives | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C011 | clean | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C012 | float_coordinates | gen-0215 | 1.0 | 1.0 | none | ordinary correct construction |

| C013 | nurbs_exact | gen-0215 | 1.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | spline rejected by design |

| C014 | reference | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C015 | Sketch | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C016 | polyline | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C017 | cutThruAll | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C018 | explicit_depth | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C019 | union_halves | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C020 | imprinted_halves | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C021 | mirror | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C022 | translate_chain | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C023 | Solid_primitives | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C024 | clean | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C025 | float_coordinates | gen-0065 | 1.0 | 1.0 | none | ordinary correct construction |

| C026 | nurbs_exact | gen-0065 | 1.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | spline rejected by design |

| C027 | reference | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C028 | Sketch | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C029 | polyline | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C030 | cutThruAll | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C031 | explicit_depth | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C032 | union_halves | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C033 | imprinted_halves | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C034 | mirror | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C035 | translate_chain | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C036 | Solid_primitives | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C037 | clean | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C038 | float_coordinates | gen-0032 | 1.0 | 1.0 | none | ordinary correct construction |

| C039 | nurbs_exact | gen-0032 | 1.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | spline rejected by design |

| C040 | reference | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C041 | Sketch | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C042 | polyline | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C043 | cutThruAll | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C044 | explicit_depth | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C045 | union_halves | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C046 | imprinted_halves | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C047 | mirror | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C048 | translate_chain | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C049 | Solid_primitives | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C050 | clean | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C051 | float_coordinates | gen-0208 | 1.0 | 1.0 | none | ordinary correct construction |

| C052 | nurbs_exact | gen-0208 | 1.0 | 0.0 | gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | spline rejected by design |

| C053 | reference | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C054 | Sketch | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C055 | polyline | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C056 | cutThruAll | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C057 | explicit_depth | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C058 | union_halves | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C059 | imprinted_halves | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C060 | mirror | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C061 | translate_chain | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C062 | Solid_primitives | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C063 | clean | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C064 | float_coordinates | gen-0001 | 1.0 | 1.0 | none | ordinary correct construction |

| C065 | nurbs_exact | gen-0001 | 1.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | spline rejected by design |

| C066 | reference | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C067 | Sketch | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C068 | polyline | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C069 | cutThruAll | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C070 | explicit_depth | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C071 | union_halves | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C072 | imprinted_halves | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C073 | mirror | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C074 | translate_chain | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C075 | Solid_primitives | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C076 | clean | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C077 | float_coordinates | gen-0037 | 1.0 | 1.0 | none | ordinary correct construction |

| C078 | nurbs_exact | gen-0037 | 1.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | spline rejected by design |

| C079 | arc_circle | synthetic | 1.0 | 1.0 | none | ordinary correct construction |

### Earlier N, D, S, L and T cases, all rows

| ID | Case | v2 score | v3 score | Failed checks | Form | Extra / missing mm3 | Error |
|---|---|---:|---:|---|---|---|---|

| N001 | full_face_pocket_3e-07 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |

| N002 | full_face_pocket_5e-07 | 0.0 | 0.0 | gate:single_solid, R9:no_other_features | False | 0.0 / 0.0 |  |

| N003 | full_face_pocket_8e-07 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| N004 | full_face_pocket_1.2e-06 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| N005 | full_face_pocket_2e-06 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| N006 | rotation_Z_3e-10_rad | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| N007 | rotation_X_3e-10_rad | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| N008 | rotation_Z_8e-10_rad | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| N009 | rotation_X_8e-10_rad | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| N010 | rotation_Z_1.2e-09_rad | 0.9 | 1.0 | none | True | 0.0 / 0.0 |  |

| N011 | rotation_X_1.2e-09_rad | 0.9 | 1.0 | none | True | 0.0 / 0.0 |  |

| N012 | rotation_Z_2e-09_rad | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| N013 | rotation_X_2e-09_rad | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| N014 | warped_spline_pole_1e-08 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1.  |

| N015 | warped_spline_pole_5e-08 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1.  |

| N016 | warped_spline_pole_1e-07 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1.  |

| N017 | warped_spline_pole_2e-07 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1.  |

| N018 | warped_spline_pole_1e-05 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1.  |

| N019 | warped_spline_pole_0.001 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1.  |

| N020 | far_origin_pocket_0.001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| N021 | far_origin_pocket_0.004 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| N022 | far_origin_pocket_0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| N023 | far_origin_pocket_0.006 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 4.665458908595533 |  |

| N024 | micro_counterbore_5e-07 | 0.0 | 0.0 | gate:clean_solid | True | 0.0 / 0.0 |  |

| N025 | micro_counterbore_8e-07 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| N026 | micro_counterbore_1.2e-06 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| N027 | loose_envelope_face | 0.0 | 0.0 | gate:clean_solid, gate:is_plate, R2:width, R6:material, R7:edge_margin, R9:no_other_features | False | None / None |  |

| N028 | second_coincident_solid | 0.0 | 0.0 | gate:single_solid, gate:is_plate, R6:material | True | 0.0 / 0.0 |  |

| N029 | largest_micro_pocket | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D001 | warped_spline_pole_1e-08_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3860469869553 |  |

| D002 | warped_spline_pole_5e-08_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3860480244979 |  |

| D003 | warped_spline_pole_1e-07_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3860493214253 |  |

| D004 | warped_spline_pole_2e-07_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3860519152817 |  |

| D005 | warped_spline_pole_1e-05_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3863113285782 |  |

| D006 | warped_spline_pole_0.001_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.4125068283938 |  |

| D007 | spline_degree4_amp1e-07 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3860490725573 |  |

| D008 | spline_degree4_amp1e-05 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3862851373739 |  |

| D009 | spline_degree4_amp0.001 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.4098877080014 |  |

| D010 | spline_degree4_amp0.004 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.481410649297 |  |

| D011 | spline_degree8_amp1e-07 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3859950681041 |  |

| D012 | spline_degree8_amp1e-05 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3860992731502 |  |

| D013 | spline_degree8_amp0.001 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3966188050697 |  |

| D014 | spline_degree8_amp0.004 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.4284931736958 |  |

| D015 | spline_degree16_amp1e-07 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3860208929326 |  |

| D016 | spline_degree16_amp1e-05 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.386072510546 |  |

| D017 | spline_degree16_amp0.001 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.3912649048841 |  |

| D018 | spline_degree16_amp0.004 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 802.4069985049076 |  |

| D019 | spline_degree32_amp1e-07 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value |

| D020 | spline_degree32_amp1e-05 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value |

| D021 | spline_degree32_amp0.001 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value |

| D022 | spline_degree32_amp0.004 | 0.0 | 0.0 | none | None | None / None | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value |

| D023 | cylinder_spline_warp1e-08 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | False | None / None |  |

| D024 | cylinder_spline_warp1e-07 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | False | None / None |  |

| D025 | cylinder_spline_warp1e-06 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | False | None / None |  |

| D026 | cylinder_spline_warp1e-05 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | False | None / None |  |

| D027 | cylinder_spline_warp0.001 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | False | None / None |  |

| D032 | micro_pocket_depth8e-07 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D033 | micro_pocket_depth9.9e-07 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D034 | micro_pocket_depth1e-06 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D035 | micro_pocket_depth1.01e-06 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D036 | micro_pocket_depth1.2e-06 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D037 | micro_pocket_depth0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D038 | counterbore_dr4e-07_depth0.0049 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | False | 0.0 / 0.0 |  |

| D039 | counterbore_dr4e-07_depth0.006 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | False | 0.0 / 0.0 |  |

| D040 | counterbore_dr4e-07_depth3 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features | False | 0.0 / 0.0 |  |

| D041 | counterbore_dr4e-07_depth6 | 0.0 | 0.0 | gate:clean_solid | True | 0.0 / 0.0 |  |

| D042 | counterbore_dr4.9e-07_depth0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D043 | counterbore_dr4.9e-07_depth0.006 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D044 | counterbore_dr4.9e-07_depth3 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D045 | counterbore_dr4.9e-07_depth6 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| D046 | counterbore_dr6e-07_depth0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D047 | counterbore_dr6e-07_depth0.006 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D048 | counterbore_dr6e-07_depth3 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D049 | counterbore_dr6e-07_depth6 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| D050 | counterbore_dr1e-06_depth0.0049 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D051 | counterbore_dr1e-06_depth0.006 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D052 | counterbore_dr1e-06_depth3 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D053 | counterbore_dr1e-06_depth6 | 1.0 | 1.0 | none | True | 0.0 / 0.0 |  |

| D054 | large_far_origin_depth0.0049 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D055 | large_far_origin_depth0.005 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| D056 | large_far_origin_depth0.0051 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 3.184132050712844 |  |

| S001 | sewn_bezier_plate_0 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| S002 | sewn_bezier_plate_1e-08 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| S003 | sewn_bezier_plate_5e-08 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| S004 | sewn_bezier_plate_1e-07 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| S005 | sewn_bezier_plate_2e-07 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| S006 | sewn_bezier_plate_8e-07 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| S007 | sewn_bezier_plate_1e-05 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| S008 | sewn_bezier_plate_0.001 | 0.9 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| S009 | revolved_bezier_bore_0 | 1.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.0665073187052 |  |

| S010 | revolved_bezier_bore_1e-08 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.0663643308584 |  |

| S011 | revolved_bezier_bore_5e-08 | 1.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.0664134792754 |  |

| S012 | revolved_bezier_bore_1e-07 | 0.7 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.0665313503044 |  |

| S013 | revolved_bezier_bore_2e-07 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.066521485359 |  |

| S014 | revolved_bezier_bore_8e-07 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.0667479826454 |  |

| S015 | revolved_bezier_bore_1e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.0693935744066 |  |

| S016 | revolved_bezier_bore_0.001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | False | 0.0 / 795.3649635025527 |  |

| L001 | local_spline_0.123_0.001_1e-05 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L002 | local_spline_0.123_0.001_0.001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L003 | local_spline_0.123_0.001_0.004 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L004 | local_spline_0.127_0.0001_1e-05 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L005 | local_spline_0.127_0.0001_0.001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L006 | local_spline_0.127_0.0001_0.004 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L007 | local_spline_0.333_0.001_1e-05 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L008 | local_spline_0.333_0.001_0.001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L009 | local_spline_0.333_0.001_0.004 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L010 | local_spline_0.501_0.0001_1e-05 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L011 | local_spline_0.501_0.0001_0.001 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| L012 | local_spline_0.501_0.0001_0.004 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| T001 | local_spline_scale_0.01 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| T002 | local_spline_scale_0.1 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| T003 | local_spline_scale_1 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

| T004 | local_spline_scale_5 | 1.0 | 0.9 | R9:no_other_features | False | 0.0 / 0.0 |  |

## 3. V2 findings and new changed-code tests

### Status of V2-B1 to V2-B3

| Finding | Status | Evidence |
|---|---|---|
| V2-B1, approximate spline recovery accepts a localized bump | resolved for the observed mechanism | recovery is removed; every retained L007 to L012 and T001 to T004 bump fails R9; all exact spline controls are explicitly rejected by design |
| V2-B2, arbitrary stored plane origin hides displaced support | resolved for the reproductions and new origin controls | N020 to N023 and D054 to D056 fail form; valid equivalent planes at origins up to 1e12 mm pass, including reversed senses with corrected topology; valid near/far cylinder axes and mid-plane limits pass as detailed below |
| V2-B3, positive allowances accept more than stated | partly resolved | broad 8e-7/9.9e-7 mm pockets now fail; A067/A068 fail with new 1e-9 slack; N025/N026 still pass with larger trim gaps, and diagonal bore endpoint components can exceed 1e-7 in Euclidean distance |

**Fact, high confidence:** the changed stored-type policy, four-corner plane evaluation and mid-plane axis measurement are real improvements. This table does not conflate the deliberately restored spline false rejection with an unreported regression. The remaining defect is the missing consistency between trim geometry and supporting surfaces at the same declared tolerance.

### New-test construction methods and harness distinctions

Every new part's table below marks **ordinary** CadQuery modelling or **kernel** object construction/editing. V001 to V012 only inflate tolerance metadata; the geometry is the correct plate. They all pass, showing that large metadata by itself is not evidence of wrong geometry. The proposed tolerance-limited copy also preserves them.

V053/V055/V057 replace the top by an equivalent plane stored far away and pass. V054/V056/V058 initially reverse the surface normal without correctly adapting all topology and are malformed controls. Q001/Q003/Q005 correct only part of that orientation; Q002/Q004/Q006 have a typed-wire overload error. J004 to J006 correctly type/reverse the inner wires and face orientation, producing valid equivalent parts which score 1.0. J001 to J003 are ordinary mirrored plates with different surface senses, all correct and all 1.0. Earlier malformed attempts are not reported as correct-part rejections.

V059 to V076 directly change bore surfaces without matching the shifted pcurves. They are intentionally inconsistent kernel metadata tests, not valid equivalent-cylinder controls. At extreme Z=-1e12 mm the worker dies; later V072 to V080 receive a broken-pipe error before reliable geometry evaluation. G025 to G029 rerun those extreme edits with fresh workers and again produce worker deaths. G030/G031 rerun the ordinary tilted-bore parts after recovery and pass; G032/G033 fail R9 because their tilt exceeds the declared coordinate allowance. Do not count the original V077/V078 pipe failures as geometric false rejection. These worker failures never receive full credit; this audit does not prove robust immediate recovery after every native-kernel crash.

W001 to W012 instead make genuine Boolean cuts with remote analytic cylinders, so their parameter curves are generated consistently. Axes starting 1,000 or 1,000,000 mm away, both Z senses and small tilts, pass. W019's 0.05 mm center shift and W020's 0.1000000005 mm shift pass; W021/W022's larger shifts fail pattern/margin. The first W harness had the compensation sign reversed, generating shifted geometry. That evidence is retained in far-cases-initial.jsonl; the table uses the corrected and freshly rerun far-cases.jsonl. It is not interpreted as a scorer precision defect.

W013 to W018's extreme 1e10 mm cutters do not yield the intended valid plate; the returned geometry/build failures are not correct-part rejections. No claim of arbitrarily large origin invariance is made.

### Sub-resolution and exact-limit results

Ordinary boxes below kernel confusion fail construction in the pocket attempt. Broad bosses protruding 5e-8, 9e-8 or 9.9e-8 mm return the original nominal supporting geometry after the Boolean operation and score 1.0. Direct boundary inspection confirms no retained boss faces; these are Boolean no-ops, not accepted visible bosses. At 1.01e-7, 2e-7 and 3e-7 mm, the boss is retained and fails R9. Ordinary tiny rotations and tilted bores fitting the coordinate tolerance also pass as the stated equivalence.

The exact diameter, length, pattern and Z-datum endpoints all score 1.0. Each passes with an additional 5e-10 or 9e-10 mm, and fails its owning check at 1.1e-9, 2e-9 and 1e-8 mm. This directly verifies the tighter 1e-9 slack on these dimensions. The new raw and matching paths use the per-version epsilon; version 0.4.0 retains 1e-6 slack.

### Every new test part

| ID | Construction | Method | Score | Failed checks / error | Intent or limitation |
|---|---|---|---:|---|---|

| V001 | large_tolerance_face_1e-06 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V002 | large_tolerance_face_0.001 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V003 | large_tolerance_face_0.1 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V004 | large_tolerance_edge_1e-06 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V005 | large_tolerance_edge_0.001 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V006 | large_tolerance_edge_0.1 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V007 | large_tolerance_vertex_1e-06 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V008 | large_tolerance_vertex_0.001 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V009 | large_tolerance_vertex_0.1 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V010 | large_tolerance_all_1e-06 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V011 | large_tolerance_all_0.001 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V012 | large_tolerance_all_0.1 | kernel | 1.0 | none | correct geometry; changed metadata only |

| V013 | ordinary_pocket_depth5e-08 | ordinary | 0.0 | execution failed [raised in cadquery: Solid.makeBox]: Standard_DomainError:  | extra pocket if boolean retains it |

| V014 | ordinary_boss_height5e-08 | ordinary | 1.0 | none | extra boss if boolean retains it |

| V015 | ordinary_pocket_depth9e-08 | ordinary | 0.0 | execution failed [raised in cadquery: Solid.makeBox]: Standard_DomainError:  | extra pocket if boolean retains it |

| V016 | ordinary_boss_height9e-08 | ordinary | 1.0 | none | extra boss if boolean retains it |

| V017 | ordinary_pocket_depth9.9e-08 | ordinary | 0.0 | execution failed [raised in cadquery: Solid.makeBox]: Standard_DomainError:  | extra pocket if boolean retains it |

| V018 | ordinary_boss_height9.9e-08 | ordinary | 1.0 | none | extra boss if boolean retains it |

| V019 | ordinary_pocket_depth1.01e-07 | ordinary | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | extra pocket if boolean retains it |

| V020 | ordinary_boss_height1.01e-07 | ordinary | 0.9 | R9:no_other_features | extra boss if boolean retains it |

| V021 | ordinary_pocket_depth2e-07 | ordinary | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | extra pocket if boolean retains it |

| V022 | ordinary_boss_height2e-07 | ordinary | 0.9 | R9:no_other_features | extra boss if boolean retains it |

| V023 | ordinary_pocket_depth3e-07 | ordinary | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | extra pocket if boolean retains it |

| V024 | ordinary_boss_height3e-07 | ordinary | 0.9 | R9:no_other_features | extra boss if boolean retains it |

| V025 | ordinary_rotation_Z_deg1e-10 | ordinary | 1.0 | none | rotated within form equivalence if entire support fits |

| V026 | ordinary_rotation_Z_deg1e-09 | ordinary | 1.0 | none | rotated within form equivalence if entire support fits |

| V027 | ordinary_rotation_Z_deg1e-08 | ordinary | 1.0 | none | rotated within form equivalence if entire support fits |

| V028 | ordinary_rotation_Z_deg1e-07 | ordinary | 0.9 | R9:no_other_features | rotated within form equivalence if entire support fits |

| V029 | diameter_boundary_plus0 | ordinary | 1.0 | none | correct nominal endpoint |

| V030 | z_datum_boundary_plus0 | ordinary | 1.0 | none | correct nominal endpoint |

| V031 | length_boundary_plus0 | ordinary | 1.0 | none | correct nominal endpoint |

| V032 | pattern_boundary_plus0 | ordinary | 1.0 | none | correct nominal endpoint |

| V033 | diameter_boundary_plus5e-10 | ordinary | 1.0 | none | documented slack |

| V034 | z_datum_boundary_plus5e-10 | ordinary | 1.0 | none | documented slack |

| V035 | length_boundary_plus5e-10 | ordinary | 1.0 | none | documented slack |

| V036 | pattern_boundary_plus5e-10 | ordinary | 1.0 | none | documented slack |

| V037 | diameter_boundary_plus9e-10 | ordinary | 1.0 | none | documented slack |

| V038 | z_datum_boundary_plus9e-10 | ordinary | 1.0 | none | documented slack |

| V039 | length_boundary_plus9e-10 | ordinary | 1.0 | none | documented slack |

| V040 | pattern_boundary_plus9e-10 | ordinary | 1.0 | none | documented slack |

| V041 | diameter_boundary_plus1.1e-09 | ordinary | 0.9 | R4b:hole_diameter | outside allowed slack |

| V042 | z_datum_boundary_plus1.1e-09 | ordinary | 0.9 | R8:z_datum | outside allowed slack |

| V043 | length_boundary_plus1.1e-09 | ordinary | 0.9 | R1:length | outside allowed slack |

| V044 | pattern_boundary_plus1.1e-09 | ordinary | 0.9 | R5:hole_pattern | outside allowed slack |

| V045 | diameter_boundary_plus2e-09 | ordinary | 0.9 | R4b:hole_diameter | outside allowed slack |

| V046 | z_datum_boundary_plus2e-09 | ordinary | 0.9 | R8:z_datum | outside allowed slack |

| V047 | length_boundary_plus2e-09 | ordinary | 0.9 | R1:length | outside allowed slack |

| V048 | pattern_boundary_plus2e-09 | ordinary | 0.9 | R5:hole_pattern | outside allowed slack |

| V049 | diameter_boundary_plus1e-08 | ordinary | 0.9 | R4b:hole_diameter | outside allowed slack |

| V050 | z_datum_boundary_plus1e-08 | ordinary | 0.9 | R8:z_datum | outside allowed slack |

| V051 | length_boundary_plus1e-08 | ordinary | 0.9 | R1:length | outside allowed slack |

| V052 | pattern_boundary_plus1e-08 | ordinary | 0.9 | R5:hole_pattern | outside allowed slack |

| V053 | plane_origin_10000.0_reverseFalse | kernel | 1.0 | none | same support; orientation must also be preserved |

| V054 | plane_origin_10000.0_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:is_plate, R6:material, R9:no_other_features | same support; orientation must also be preserved |

| V055 | plane_origin_100000000.0_reverseFalse | kernel | 1.0 | none | same support; orientation must also be preserved |

| V056 | plane_origin_100000000.0_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:is_plate, R6:material, R9:no_other_features | same support; orientation must also be preserved |

| V057 | plane_origin_1000000000000.0_reverseFalse | kernel | 1.0 | none | same support; orientation must also be preserved |

| V058 | plane_origin_1000000000000.0_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:is_plate, R6:material, R9:no_other_features | same support; orientation must also be preserved |

| V059 | remote_cylinder_-1000000.0_dx0_reverseFalse | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V060 | remote_cylinder_-1000000.0_dx0_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V061 | remote_cylinder_-1000000.0_dx1e-09_reverseFalse | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V062 | remote_cylinder_-1000000.0_dx1e-09_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V063 | remote_cylinder_-1000000.0_dx3e-08_reverseFalse | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V064 | remote_cylinder_-1000000.0_dx3e-08_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V065 | remote_cylinder_1000000.0_dx0_reverseFalse | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V066 | remote_cylinder_1000000.0_dx0_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V067 | remote_cylinder_1000000.0_dx1e-09_reverseFalse | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V068 | remote_cylinder_1000000.0_dx1e-09_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V069 | remote_cylinder_1000000.0_dx3e-08_reverseFalse | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V070 | remote_cylinder_1000000.0_dx3e-08_reverseTrue | kernel | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features | potentially inconsistent pcurves; validity decides |

| V071 | remote_cylinder_-1000000000000.0_dx0_reverseFalse | kernel | 0.0 | scorer worker died while executing model code | potentially inconsistent pcurves; validity decides |

| V072 | remote_cylinder_-1000000000000.0_dx0_reverseTrue | kernel | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | potentially inconsistent pcurves; validity decides |

| V073 | remote_cylinder_-1000000000000.0_dx1e-09_reverseFalse | kernel | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | potentially inconsistent pcurves; validity decides |

| V074 | remote_cylinder_-1000000000000.0_dx1e-09_reverseTrue | kernel | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | potentially inconsistent pcurves; validity decides |

| V075 | remote_cylinder_-1000000000000.0_dx3e-08_reverseFalse | kernel | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | potentially inconsistent pcurves; validity decides |

| V076 | remote_cylinder_-1000000000000.0_dx3e-08_reverseTrue | kernel | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | potentially inconsistent pcurves; validity decides |

| V077 | ordinary_bore_tilt_rad1e-09 | ordinary | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | tilted bore within equivalence only if ends fit |

| V078 | ordinary_bore_tilt_rad3e-08 | ordinary | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | tilted bore within equivalence only if ends fit |

| V079 | ordinary_bore_tilt_rad4e-08 | ordinary | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | tilted bore within equivalence only if ends fit |

| V080 | ordinary_bore_tilt_rad1e-06 | ordinary | 0.0 | scorer pipe broke: [WinError 232] The pipe is being closed | tilted bore within equivalence only if ends fit |

| W001 | far_cut_1000.0_dx0_sign-1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W002 | far_cut_1000.0_dx0_sign1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W003 | far_cut_1000.0_dx1e-09_sign-1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W004 | far_cut_1000.0_dx1e-09_sign1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W005 | far_cut_1000.0_dx3e-08_sign-1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W006 | far_cut_1000.0_dx3e-08_sign1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W007 | far_cut_1000000.0_dx0_sign-1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W008 | far_cut_1000000.0_dx0_sign1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W009 | far_cut_1000000.0_dx1e-09_sign-1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W010 | far_cut_1000000.0_dx1e-09_sign1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W011 | far_cut_1000000.0_dx3e-08_sign-1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W012 | far_cut_1000000.0_dx3e-08_sign1 | kernel | 1.0 | none | same nominal mid-plane bore centers; small tilt |

| W013 | far_cut_10000000000.0_dx0_sign-1 | kernel | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | same nominal mid-plane bore centers; small tilt |

| W014 | far_cut_10000000000.0_dx0_sign1 | kernel | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | same nominal mid-plane bore centers; small tilt |

| W015 | far_cut_10000000000.0_dx1e-09_sign-1 | kernel | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | same nominal mid-plane bore centers; small tilt |

| W016 | far_cut_10000000000.0_dx1e-09_sign1 | kernel | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | same nominal mid-plane bore centers; small tilt |

| W017 | far_cut_10000000000.0_dx3e-08_sign-1 | kernel | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | same nominal mid-plane bore centers; small tilt |

| W018 | far_cut_10000000000.0_dx3e-08_sign1 | kernel | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object | same nominal mid-plane bore centers; small tilt |

| W019 | far_axis_center_shift0.05 | kernel | 1.0 | none | correct .05 shift or boundary/outside shift as indicated |

| W020 | far_axis_center_shift0.1000000005 | kernel | 1.0 | none | correct .05 shift or boundary/outside shift as indicated |

| W021 | far_axis_center_shift0.100000002 | kernel | 0.8 | R5:hole_pattern, R7:edge_margin | correct .05 shift or boundary/outside shift as indicated |

| W022 | far_axis_center_shift0.2 | kernel | 0.8 | R5:hole_pattern, R7:edge_margin | correct .05 shift or boundary/outside shift as indicated |

| G001 | counterbore_dr4e-07_depth0.0001_tolNone | ordinary | 0.0 | gate:clean_solid, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G002 | counterbore_dr4e-07_depth0.0001_tol0.1 | kernel | 0.0 | gate:clean_solid, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G003 | counterbore_dr4e-07_depth0.0049_tolNone | ordinary | 0.0 | gate:clean_solid, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G004 | counterbore_dr4e-07_depth0.0049_tol0.1 | kernel | 0.0 | gate:clean_solid, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G005 | counterbore_dr4e-07_depth0.0099_tolNone | ordinary | 0.0 | gate:clean_solid, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G006 | counterbore_dr4e-07_depth0.0099_tol0.1 | kernel | 0.0 | gate:clean_solid, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G007 | counterbore_dr4e-07_depth0.02_tolNone | ordinary | 0.0 | gate:clean_solid, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G008 | counterbore_dr4e-07_depth0.02_tol0.1 | kernel | 0.0 | gate:clean_solid, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G009 | counterbore_dr9e-07_depth0.0001_tolNone | ordinary | 0.9 | R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G010 | counterbore_dr9e-07_depth0.0001_tol0.1 | kernel | 0.9 | R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G011 | counterbore_dr9e-07_depth0.0049_tolNone | ordinary | 0.9 | R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G012 | counterbore_dr9e-07_depth0.0049_tol0.1 | kernel | 0.9 | R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G013 | counterbore_dr9e-07_depth0.0099_tolNone | ordinary | 0.9 | R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G014 | counterbore_dr9e-07_depth0.0099_tol0.1 | kernel | 0.9 | R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G015 | counterbore_dr9e-07_depth0.02_tolNone | ordinary | 0.9 | R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G016 | counterbore_dr9e-07_depth0.02_tol0.1 | kernel | 0.9 | R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G017 | counterbore_dr0.0001_depth0.0001_tolNone | ordinary | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G018 | counterbore_dr0.0001_depth0.0001_tol0.1 | kernel | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G019 | counterbore_dr0.0001_depth0.0049_tolNone | ordinary | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G020 | counterbore_dr0.0001_depth0.0049_tol0.1 | kernel | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G021 | counterbore_dr0.0001_depth0.0099_tolNone | ordinary | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G022 | counterbore_dr0.0001_depth0.0099_tol0.1 | kernel | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G023 | counterbore_dr0.0001_depth0.02_tolNone | ordinary | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G024 | counterbore_dr0.0001_depth0.02_tol0.1 | kernel | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features | forbidden counterbore; verify actual returned geometry |

| G025 | fresh_remote_cylinder_-1000000000000.0_dx0_reverseTrue | kernel | 0.0 | scorer worker died while executing model code | potentially inconsistent pcurves; validity decides |

| G026 | fresh_remote_cylinder_-1000000000000.0_dx1e-09_reverseFalse | kernel | 0.0 | scorer worker died while executing model code | potentially inconsistent pcurves; validity decides |

| G027 | fresh_remote_cylinder_-1000000000000.0_dx1e-09_reverseTrue | kernel | 0.0 | scorer worker died while executing model code | potentially inconsistent pcurves; validity decides |

| G028 | fresh_remote_cylinder_-1000000000000.0_dx3e-08_reverseFalse | kernel | 0.0 | scorer worker died while executing model code | potentially inconsistent pcurves; validity decides |

| G029 | fresh_remote_cylinder_-1000000000000.0_dx3e-08_reverseTrue | kernel | 0.0 | scorer worker died while executing model code | potentially inconsistent pcurves; validity decides |

| G030 | fresh_ordinary_bore_tilt_rad1e-09 | ordinary | 1.0 | none | tilted bore within equivalence only if ends fit |

| G031 | fresh_ordinary_bore_tilt_rad3e-08 | ordinary | 1.0 | none | tilted bore within equivalence only if ends fit |

| G032 | fresh_ordinary_bore_tilt_rad4e-08 | ordinary | 0.9 | R9:no_other_features | tilted bore within equivalence only if ends fit |

| G033 | fresh_ordinary_bore_tilt_rad1e-06 | ordinary | 0.9 | R9:no_other_features | tilted bore within equivalence only if ends fit |

| Q001 | plane_origin_10000.0_reverseTrue_inner_flipFalse | kernel | 0.0 | gate:clean_solid, R9:no_other_features | reverse plane normal with corrected face orientation |

| Q002 | plane_origin_10000.0_reverseTrue_inner_flipTrue | kernel | 0.0 | execution failed [raised in model code]: TypeError: Add(): incompatible function arguments. The following argument types are supported:     1. (self:  | reverse plane normal with corrected face orientation |

| Q003 | plane_origin_100000000.0_reverseTrue_inner_flipFalse | kernel | 0.0 | gate:clean_solid, R9:no_other_features | reverse plane normal with corrected face orientation |

| Q004 | plane_origin_100000000.0_reverseTrue_inner_flipTrue | kernel | 0.0 | execution failed [raised in model code]: TypeError: Add(): incompatible function arguments. The following argument types are supported:     1. (self:  | reverse plane normal with corrected face orientation |

| Q005 | plane_origin_1000000000000.0_reverseTrue_inner_flipFalse | kernel | 0.0 | gate:clean_solid, R9:no_other_features | reverse plane normal with corrected face orientation |

| Q006 | plane_origin_1000000000000.0_reverseTrue_inner_flipTrue | kernel | 0.0 | execution failed [raised in model code]: TypeError: Add(): incompatible function arguments. The following argument types are supported:     1. (self:  | reverse plane normal with corrected face orientation |

| J001 | ordinary_mirror_XY | ordinary | 1.0 | none | correct identical plate; changed surface senses |

| J002 | ordinary_mirror_XZ | ordinary | 1.0 | none | correct identical plate; changed surface senses |

| J003 | ordinary_mirror_YZ | ordinary | 1.0 | none | correct identical plate; changed surface senses |

| J004 | typed_plane_origin_10000.0_reverseTrue_inner_flipTrue | kernel | 1.0 | none | attempted reverse support; validity must be checked |

| J005 | typed_plane_origin_100000000.0_reverseTrue_inner_flipTrue | kernel | 1.0 | none | attempted reverse support; validity must be checked |

| J006 | typed_plane_origin_1000000000000.0_reverseTrue_inner_flipTrue | kernel | 1.0 | none | attempted reverse support; validity must be checked |

| E001 | diagonal_bore_axis_component2e-08 | ordinary | 1.0 | none | endpoint norm 8.48528137424e-08 mm; coordinatewise versus Euclidean equivalence |

| E002 | diagonal_bore_axis_component3e-08 | ordinary | 1.0 | none | endpoint norm 1.27279220614e-07 mm; coordinatewise versus Euclidean equivalence |

| E003 | diagonal_bore_axis_component3.3e-08 | ordinary | 1.0 | none | endpoint norm 1.40007142675e-07 mm; coordinatewise versus Euclidean equivalence |

| E004 | diagonal_bore_axis_component3.4e-08 | ordinary | 0.9 | R9:no_other_features | endpoint norm 1.44249783362e-07 mm; coordinatewise versus Euclidean equivalence |

All complete sources, specifications, raw reports and measurement captures: [new-cases.jsonl](scratch/new-cases.jsonl), [far-cases.jsonl](scratch/far-cases.jsonl), [gap-cases.jsonl](scratch/gap-cases.jsonl), [reverse-cases.jsonl](scratch/reverse-cases.jsonl), [supplement-cases.jsonl](scratch/supplement-cases.jsonl), [diagonal-cases.jsonl](scratch/diagonal-cases.jsonl). Q rows did not capture Measurements, so validity is not inferred from absence of a field.

The larger-radius and deeper counterbore variants G001 to G024 do not receive 1.0, even after explicit tolerance inflation; either form or identity fails. The successful N025/N026 remain the achieved trim-gap counterexamples. No global maximum inconsistent feature size is established.

**Fact, high confidence:** the scratch distance-bound prototype preserves 73/73 non-spline C controls and 12/12 valid remote-axis controls. Diagonal results: E001=1.0; E002=0.9; E003=0.9; E004=0.9. NURBS rejection remains by design. [norm-prototype.json](scratch/norm-prototype.json). This tests the distance-bound proposal separately from the topology-copy proposal; it does not certify their combined production implementation.

## 4. Legacy comparison, reward/check/parsed and normalized errors

**Fact, high confidence:** both implementations independently executed all 3,161 answers from the exact original input: 2,200 stable-hash-selected AST-deduplicated train/dev programs plus all 961 saved evaluation rows. No model was run and no parameter was selected using evaluation splits. Separate processes select the current worktree or verified main snapshot, with no cross-answer cache.

| Field | Answers compared | Differences |
|---|---:|---:|

| reward | 3161 | 0 |

| checks | 3161 | 0 |

| parsed | 3161 | 0 |

| exception | 3161 | 0 |

| error text, memory addresses normalized | 3161 | 0 |

| error text, raw, separately recorded | 3161 | 1 |

The single raw error difference is index 1362, a CadQuery Vector.multiply TypeError containing a process-specific gp_Vec memory address. Address-only normalization makes it equal. The requested semantic and normalized-error comparisons have **zero differences**. Both implementations timeout at index 648 under the default 10 s budget, as before. Main summed time 133.690748 s; branch 117.764135 s. Other audit jobs overlapped parts of the run, so timing is descriptive, not a throughput or deadline-equivalence claim. No short-deadline rerun was requested in round 3, and none is silently inferred from these times.

Raw payloads: [compat-main.jsonl](scratch/compat-main.jsonl), [compat-branch.jsonl](scratch/compat-branch.jsonl), [compat-summary.json](scratch/compat-summary.json). The original summary includes the one raw diagnostic mismatch; the table above recomputes exactly the fields requested for round 3. [compat-normalized-errors.jsonl](scratch/compat-normalized-errors.jsonl) separately records both normalized error texts and equality for every answer.

## 5. README and CHANGELOG review

| Statement and location | Assessment |
|---|---|
| README 18 and 118 onward; CHANGELOG 9 to 13, plate plus four holes within 0.1 mm | clear intended contract; two tolerance-closed ordinary bore-mouth parts still receive 1.0 outside the stated 1e-7 boundary equivalence |
| README 150 to 162, three rules make the form check sound | stronger than the evidence; allowed supporting surfaces plus stored-tolerance validity do not certify trims at 1e-7 mm |
| README 160 to 162 and CHANGELOG 17 to 18, features shallower than 0.1 nanometre are not seen | correct conversion of 1e-7 mm to 0.1 nm, but not a universal sensitivity floor: unsupported spline surfaces fail even below it, and accepted trim discrepancies can exceed it, as N025/N026 show |
| README R9 table and CHANGELOG 17, every face is an envelope plane/bore within 1e-7 mm | matches supporting-surface coordinate tests, but not the whole trimmed boundary; cylinder X/Y allowances can reach sqrt(2) times that value in Euclidean displacement |
| README 156 to 158 and 218 to 224; CHANGELOG 57 to 58, spline storage rejected deliberately | accurately describes restored representation limitation; exact Bezier and spline-generated revolved forms also fail, not only toNURBS copies |
| README 158 to 159, where a surface lies across the part | original far-origin pocket is fixed; new far-plane/reversed-normal and genuine remote-cylinder controls support the implementation; no proof for arbitrary huge parameter domains |
| README 181 to 185, raw comparisons with 1e-9 slack; 6.600001 outside | supported by A067/A068 and four new endpoint families; only 0.4.0 retains its old rounding and 1e-6 slack |
| CHANGELOG 31 to 33, all earlier draft counterexamples fixed and pinned | true for the prominently pinned large spline, remote-origin pocket and broad-pocket cases; too broad if it means all prior full-credit incorrect rows, because N025/N026 still pass |
| README 165 to 168 and CHANGELOG 18 to 20, residual is a second look and only adds failure | source conjunction supports it; the 0.005 mm band and 0.001 mm3 allowance still need disclosure if explaining how acceptance is bounded |
| README 20/406 and CHANGELOG 38 to 43, zero false full credit on 1,646 wrong and zero rejection on 720 correct | matches committed finite-suite records; the qualified finite-case interpretation is appropriate. The frozen 2,366 suite was not rerun in v3, so those counts are not independently re-certified here |
| README/CHANGELOG sensitivity results, six changed verdicts and gains of 41.7/40.8 percentage points | matches the committed final sensitivity table: five base changes and one adapter change, all R5/R7. These version 0.5.0 evaluation results were checked against the record, not independently rerun in v3 |
| README 36/541, 77 hand-labelled cases | freshly reproduced, 77/77 as expected |
| README 109 to 115 and CHANGELOG 44 to 49, legacy selectable and recorded results preserved | source and all 3,161 requested semantic comparisons support it; normalized errors agree. Not a claim about every future deadline or raw error address |
| README 177 to 179 and CHANGELOG 41 to 43, validation is not proof that no wrong part passes | appropriately narrowed and supported |

**Opinion, high confidence:** update the form explanation to distinguish supporting surfaces from trim consistency. If retaining a coordinatewise bore allowance, name that metric and its combined Euclidean extent. Avoid the unqualified soundness statement until the boundary check matches the declared equivalence.

```diff
--- a/README.md
+++ b/README.md
@@
-adds a face that is none of them. Three rules make the check sound:
+normally adds a supporting surface outside them. The current check tests
+supporting surfaces; kernel validity uses stored tolerances and does not
+yet certify all trims at the same numerical equivalence. The v3 audit's
+tolerance-closed bore mouths require an independent boundary check.
@@
-  numerical equivalence and it is stated as such: a feature shallower than
-  0.1 nanometre is not seen.
+  numerical equivalence. Supporting-plane coordinates are compared at
+  0.1 nanometre; the current bore-axis test compares X and Y separately.
+  This is not yet a global distance bound on the complete boundary.
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@
-  with the envelope (a pocket floor stored 9.8 km away passed). All are
-  fixed and pinned as the `AUDIT_` and `AUDIT3_` cases of
+  with the envelope (a pocket floor stored 9.8 km away passed). The pinned
+  cases are fixed. The v3 audit found tolerance-closed bore trims and a
+  coordinatewise-versus-distance equivalence issue requiring follow-up.
+  The earlier regressions remain in the `AUDIT_` and `AUDIT3_` cases of
```

These are documentation proposals for the current branch. If the boundary and distance patches are integrated, rewrite the wording around the resulting validated policy rather than retaining obsolete limitations.

## 6. Verification limits

- **Fact, high confidence:** Windows reuse mode was exercised. Linux fork hardening, GL fallback and remote environments were not tested.
- **Fact, high confidence:** no hosted Hub, credential, model service or external system was accessed.
- **Fact, high confidence:** the 2,366-mutant frozen suite, packaging, full type/lint suite and a round-3 tight-deadline probe were not run. The requested earlier corpora, legacy comparison and 77 pinned cases were run completely.
- **Fact, high confidence:** extreme inconsistent cylinder edits killed the native worker. Their later pipe-error rows were retained and unrelated ordinary cases were rerun with fresh workers. This audit does not certify immediate persistent-worker recovery after arbitrary native crashes.
- **Inference, moderate confidence:** no maximum kernel-tolerance-closed defect volume or size was proved, and neither proposed patch proves universal soundness. Attained earlier trim gaps are 8e-7 and 1.2e-6 mm; attained diagonal axis displacement is 1.400071427e-7 mm at full credit.
- **Opinion, high confidence:** run the ordinary release checks and finite suite after selecting the boundary and metric policy. Proposed patches were smoke-tested independently in scratch only, never applied to the repository.

Reproduction drivers and raw evidence are under [scratch](scratch/). Use the venv interpreter stated above. rerun_corpus.py covers all 322 earlier rows; run_compat.py uses the exact original 3,161 inputs; new_cases.py, far_cases.py, gap_cases.py, reverse_cases.py, supplement_cases.py and diagonal_cases.py generate the new cases. boundary_diagnostics.py evaluates retained trims. tolerance_prototype.py and norm_prototype.py test the proposed changes in isolated worker processes.
