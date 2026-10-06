**Opinion, high confidence: change first.** A reproduced `ok` observation contains an incorrect margin.
**Fact, high confidence:** all four requested gates pass; 180 ordinary construction controls match within 1e-9 mm.
**Fact, high confidence:** no reward, named-check or parsed differences on 3,161 answers for either scorer version.
**Inference, high confidence:** rounded cylinder grouping and the angular cutoff lose scope information.
**Opinion, high confidence:** repair L5 scope handling and strict-failure refusal, preserve historical scores, then rerun the gate before M2.

# L5 milestone M1 audit

**Scope/provenance, facts.** Reviewed `feat/l5-m1-observation`, HEAD `08cc812`, against main `1fb9a51` on 5 October 2026. Read the approved design and amendments before source review; their architecture was not reconsidered. All new notes, scripts, local package copies, logs and temporary worker directories are under `C:/Users/bgare/cad-spec-audit-out/l5-m1/`. No network, credentials, paid service, model, external system, tracked edit, commit or push was used. Repository status and tracked diff remained clean.

**Setup, facts.** Used `C:/Users/bgare/dev/cad-spec-env/environments/cad_spec/.venv/Scripts/python.exe`, Python 3.12.10, CadQuery 2.8.0, Windows reuse mode. Set `PYTHONPATH=C:/Users/bgare/dev/cad-spec-audit/environments/cad_spec`, `PYTHONDONTWRITEBYTECODE=1`, `CAD_SPEC_SANDBOX=reuse`; kept TEMP/TMP under the output directory. Confirmed once that `cad_spec.l5.__file__` resolves to this worktree's `environments/cad_spec/cad_spec/l5/__init__.py`. Main was copied using local git show, not checked out in this worktree.

**Labels and confidence.** Facts are local executions/source observations; inferences connect evidence to behavior; opinions are judgments. Confidence is high for finite executions and source comparisons, moderate for generality, tolerance interpretations and unexecuted proposed changes. Expected outcomes are analytical expectations, not independent certification of all CAD topology.

## Required changes and reproductions

### R1. Tiny tilted holes return ok with a wrong margin

**Fact, high confidence.** Four bores tilted by 1e-8 radians return `ok`, `mx=15`. Their actual axes intersect the top plane z=2 at x=nominal x + 2e-8, so the correct minimum margin is `14.99999998`. Independent `BRepAdaptor_Surface` interrogation confirms this, not just the cutter instructions. The error is twenty times the requested 1e-9 mm accuracy. Five additional diameters, 0.001, 0.002, 0.01, 0.1 and 10 mm, reproduce the margin error.


```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-07).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** out_of_scope. **Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0000001, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.


**Fact.** Strict hole positions are measured at mid-thickness. Design section 7.1 requires the top-plane intersection. The new concave-face detector ignores direction components <= `AXIS_TOL=1e-6`. The form check accepts the tiny tilt within its geometric tolerance. At 1e-6 radians the result is instead `form_violation`, still contrary to the recorded unconditional tilt scope rule.

**Opinion, high confidence.** The smallest conservative repair is to detect actual non-Z axes in the new L5 field, retaining only floating-point zero slack. This makes the tilt `out_of_scope`. If tiny tilts are deliberately accepted, carry top-intersection metadata and use it for all margins, pitches and booleans. Do not change historical `Hole.x/y` and alter the existing scorer.

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ _off_axis_concave_faces
-        if abs(d.X()) <= AXIS_TOL and abs(d.Y()) <= AXIS_TOL:
+        if abs(d.X()) <= math.ulp(1.0) and abs(d.Y()) <= math.ulp(1.0):
             continue  # along Z: measured as a hole or judged by the form check
```

**Qualification.** The same D=10 example returns T=4.0000001 although vertices and planar top/bottom are at +/-2. The kernel pads the box of tilted trimmed cylindrical faces. Under the literal rule to use the kernel AABB, this is the specified box value; under an exact physical-thickness interpretation it is another error. I do not count that ambiguity as a separate proven AABB-rule defect. Scope refusal resolves both concerns for this part.

### R2. Raw coaxial diameters must survive the measurement grouping

**Fact, high confidence.** Radius steps 1e-5 and 1e-6 mm survive in the BRep but return `form_violation`, n=4 and a selected D, instead of `out_of_scope`. Strict measurement still groups diameters rounded to four decimals, merging the different walls into one Hole. The map cannot reconstruct lost scope information.


```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(5.000001).extrude(2))
```

**Expected:** out_of_scope. **Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.000002, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.


**Opinion.** Keep existing measurement fields stable for score compatibility and add raw concave-axis metadata in the existing face pass. The following is an integration sketch, not a tested complete patch. It handles distinct radii before rounding while allowing same-radius seam-split faces. Add tests for connected offset steps as well.

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ class Measurements
+    scope_axes: list[tuple[float, float, float]] | None = None  # x, y, raw diameter
@@ def _classify_cylinders(solid: Any, *, strict: bool = False,
-                        z_ref: float | None = None) -> tuple[list[Hole], list[PartialBore]]:
+                        z_ref: float | None = None,
+                        scope_axes: list[tuple[float, float, float]] | None = None
+                        ) -> tuple[list[Hole], list[PartialBore]]:
@@ after material-inside rejection, before rounding
+        if scope_axes is not None:
+            scope_axes.append((cx, cy, 2 * radius))
         key = (round(cx, COAXIAL_DP), round(cy, COAXIAL_DP))
@@ measure
+    scope_axes = [] if strict else None
-    holes, partial = _classify_cylinders(solid, strict=strict, z_ref=(bb.zmin + bb.zmax) / 2)
+    holes, partial = _classify_cylinders(
+        solid, strict=strict, z_ref=(bb.zmin + bb.zmax) / 2, scope_axes=scope_axes)
@@ Measurements constructor
+        scope_axes=scope_axes,
--- a/environments/cad_spec/cad_spec/l5/observation.py
+++ b/environments/cad_spec/cad_spec/l5/observation.py
@@ before groups = _positions(m.holes)
+    if m.scope_axes is None:
+        return refuse("raw cylinder scope information is unavailable")
+    if any(math.hypot(x - u, y - v) <= EPS_FORM_MM and abs(d - e) > EPS_DIM_MM
+           for i, (x, y, d) in enumerate(m.scope_axes)
+           for u, v, e in m.scope_axes[i + 1:]):
+        return refuse("coaxial cylinders with different diameters")
```

**Fact.** The particular radius/depth steps <=1e-7 tested with Boolean cuts are erased by the kernel. Independent inspection finds only the original radius-5 cylinders. Their `ok` outputs are not confirmed stepped-part false acceptances. The original nominal expectations are retained in the inventory with this correction.

### R3. Unequal diameters currently choose an arbitrary single D

**Fact, high confidence.** Actual diameters `[10.00000001,10,10,10]` produce `ok`, D=10.00000001 if the larger hole is first by sorted axis, but D=10 if it is last. A 1e-7 difference also passes. Independent geometry retains both radii; a 1e-6 difference refuses.


```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.faces(">Z").workplane().pushPoints([(-35,-25)]).hole(10.00000001)
```

**Expected:** out_of_scope. **Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.00000001, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.


**Opinion, moderate confidence on the tolerance interpretation.** Section 3 says different diameters are out of scope because D is one number. Using form epsilon permits a spread one hundred times dimensional slack and silently selects one actual hole. I would refuse spreads above EPS_DIM_MM. An alternative representative-under-form-equivalence policy needs an explicit amendment defining the representative and the error accepted by Contract B. The primary suite deliberately tried the permissive interpretation; the extended suite tests the literal single-D scope rule. Both observations are recorded.

```diff
--- a/environments/cad_spec/cad_spec/l5/observation.py
+++ b/environments/cad_spec/cad_spec/l5/observation.py
@@
-    if through and max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_FORM_MM:
+    if through and max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_DIM_MM:
         return refuse("through holes of different diameters: D is not one number")
```

### R4. Bound the new detector's inward probe

**Fact, high confidence.** A real X-directed bore of radius 1e-4 mm is missed by both off-axis counters. The map returns `form_violation` instead of `out_of_scope`. The minimum inset is 1e-3 mm, ten radii, so the probe can cross the axis and exit the air channel. Independent inspection finds the cross cylinder.


```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("YZ").circle(0.0001).extrude(200,both=True))
```

**Expected:** out_of_scope. **Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.


**Opinion.** Cap the new detector's probe to remain inside its radius. Treat ON/UNKNOWN as uncertain evidence, rather than calling every non-IN state concave. Keep the historical detectors unchanged.

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ _off_axis_concave_faces
-        k = max(r * PROBE_INSET_FRACTION, PROBE_INSET_MIN_MM) / r
+        inset = min(max(r * PROBE_INSET_FRACTION, PROBE_INSET_MIN_MM), r / 2)
+        k = inset / r
@@
-        if classifier.State() != TopAbs_State.TopAbs_IN:
-            count += 1  # no material just inward: a concave face, so part of a hole
+        state = classifier.State()
+        if state == TopAbs_State.TopAbs_OUT:
+            count += 1
+        elif state != TopAbs_State.TopAbs_IN:
+            raise RuntimeError("cylindrical-face concavity could not be classified")
```

**Coverage limitation, fact.** Four true Z holes of D=0.0005, 0.0001 and 0.00005 mm are refused with n=0. The D=0.0005 example independently has four valid full-thickness radius-0.00025 cylinders. The probe floor also exists in the old scored detector. Do not silently change it and alter historical 0.5.0 scores. Add observation-only candidates in the same face pass, or explicitly document an unsupported size range and return out_of_scope. The latter is an explicit coverage tradeoff, not accurate hole measurement. No minimum diameter is currently stated.


```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(0.0005)
```

**Expected:** ok with four holes of D=0.0005. **Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.


### R5. Failed strict classification needs explicit refusal

**Fact, high confidence.** `measure(strict=True)` catches a new detector failure, records shape_error and leaves off_axis_concave=None. `observe` mistakes this for a legacy measurement and raises ValueError. Reproduced by fault injection, not a naturally failing built part:

```python
import importlib
import cadquery as cq
from cad_spec.l5 import observe
mm = importlib.import_module("cad_spec.measure")
old = mm._off_axis_concave_faces
try:
    def fail(_):
        raise RuntimeError("synthetic classifier fault")
    mm._off_axis_concave_faces = fail
    m = mm.measure(cq.Workplane("XY").box(100,80,4), strict=True)
    observe(m)
finally:
    mm._off_axis_concave_faces = old
```

**Actual, fact:** `{"off_axis_concave": null, "result": "ValueError('observe() needs a strict measurement: measure(solid, strict=True)')", "shape_error": "form check failed: RuntimeError: synthetic classifier fault"}`.

**Opinion.** Preserve rejection of accidental legacy input, but refuse recorded strict failures. An explicit strict-measurement marker would be better than inferring provenance from an optional result field. Minimum correction:

```diff
--- a/environments/cad_spec/cad_spec/l5/observation.py
+++ b/environments/cad_spec/cad_spec/l5/observation.py
@@
     if m.off_axis_concave is None:
+        if m.shape_error:
+            return refuse(f"strict scope check unavailable: {m.shape_error}")
         raise ValueError("observe() needs a strict measurement: measure(solid, strict=True)")
```

**Required regression additions, opinion.** Add the tiny tilt, small cross bore, micro-radius step, first/last-axis unequal D, small true-hole limitation and strict-fault path to the permanent gate. Assert complete variable sets. Add below/at/above grouping fixtures, since real small parts first encounter a different rounded grouping. None of these proposed source diffs was applied or tested; R2 is explicitly a sketch. The reproduction inventory supplies concrete inputs and current results.

## Reproduction and score preservation

### Task 1

| Requested command | Result | Exit | Wall time |
|---|---|---:|---:|
| `python scripts/test_l5_observation.py` | 27/27 | 0 | 4.339 s |
| `pytest -q tests/test_l5_observation.py` | 8 passed | 0 | 2.650 s |
| `python scripts/test_rubric_050.py` | 81/81 | 0 | 12.531 s |
| `python scripts/test_rubric.py` | 37/37 | 0 | 3.522 s |

**Fact.** Every command used the venv. Pytest ran from environments/cad_spec, with only `-p no:cacheprovider` added to prevent repository cache writes. Other scripts ran from the repository root without output-file options.

### Task 2

**Fact.** Reused the exact earlier 3,161-answer input, SHA-256 `aadd97fcb37734637a14e22f328c28c3c17584e3c4c445b23efb38b3a1b4fc44`: 2,200 distinct train/dev programs and 961 saved evaluation rows. Evaluation rows were used only for the requested score-equivalence/timing check, never to select thresholds or argue for geometry changes. Main and branch each scored both 0.5.0 and 0.4.0 independently, 12,644 calls in total. Compared numeric rewards, complete name-to-verdict mappings and parsed flags. Detail/error strings were not the requested comparison.

| Version | Paired answers | Reward differences | Named-check differences | Parsed differences | Exceptions main/branch |
|---|---:|---:|---:|---:|---:|
| 0.5.0 | 3,161 | 0 | 0 | 0 | 0/0 |
| 0.4.0 | 3,161 | 0 | 0 | 0 | 0/0 |

**Fact.** Complete-run 0.5.0 time per answer includes build, measurement, score, failures and worker startup:

| Revision | Mean/answer | Median/answer | p95/answer | Total for 3,161 |
|---|---:|---:|---:|---:|
| main | 73.883 ms | 77.512 ms | 108.597 ms | 233.544 s |
| branch | 69.948 ms | 77.040 ms | 92.714 ms | 221.107 s |

**Timing qualification, fact.** Main ran first and early portions overlapped synthetic audit jobs. Complete-run latency therefore is not a controlled regression estimate. After the long replay finished, a warm-worker main/branch/branch/main benchmark used the same 79 regularly spaced train/dev saved answers per block, two blocks and 158 timed calls per revision, startup excluded. All four blocks gave equal verdicts.

| Warm scorer 0.5.0 | Mean/answer | Median/answer | p95/answer |
|---|---:|---:|---:|
| main | 60.137 ms | 70.590 ms | 104.652 ms |
| branch | 63.338 ms | 74.215 ms | 105.777 ms |

**Inference, moderate confidence.** Warm mean latency changes by +5.32%. This small local sample cannot establish a robust performance regression. The new strict scan adds work; 0.4.0 does not execute it.

**Fact, source.** form_verdict is a literal extraction of previous R9 logic and details. Legacy measurement does not execute the new detector, although its Measurements payload now has a default-None field. **Inference, high confidence:** ordinary scoring semantics are preserved. The 3,161-pair check is strong sample evidence, not a proof of identical timeout behavior for every possible input.

## Additional parts: task 3

**Fact.** 333 additional records: 180 construction controls, 135 other synthetic records, eight near-breakout/overlap probes, three stress parts and seven direct measurement fixtures. This excludes the requested gate suites and fault injection. All 180 controls return ok and match every numeric variable within 1e-9 mm.

**Fact.** Six specifications: `gen-0001`, `gen-0115`, `gen-0214` from train; `gen-0208`, `gen-0024`, `gen-0037` from dev. Each uses unequal X/Y margins and ten styles, each native/translated/mirrored: pushPoints/hole, rect vertices/hole, rarray/hole, circle/cutThruAll, rect extrusion/cutters, split two-sided uncleaned cutters, bottom drilling, low-level solids, cutBlind across thickness and absolute corner-origin stock.

**Expectations.** Ordinary full dictionaries are calculated from explicit dimensions/coordinates independently of the detector; numeric accuracy is 1e-9 mm, booleans exact, analytical pattern equivalence 1e-7. Nonstandard n uses extent as px/py, matching the current map but requiring documentation. Microscopic nominal-code expectations are qualified after inspecting built geometry. An expectation mismatch is not automatically a map defect.

### (a) Wrong value with ok

| Cases | Known value | Actual | Assessment |
|---|---|---|---|
| Primary 1e-8 tilt and five extended tiny tilts | top mx=14.99999998 | mx=15; ok | Proven R1. Extended tests expected out_of_scope. |
| First-axis diameter difference 1e-8 and 1e-7 | No common diameter accurate to 1e-9 for all four | D=10.00000001 / 10.0000001; ok | Actual unequal surfaces; interpretation of a single equivalent D discussed in R3. |

**Fact.** No incorrect accepted value among the 180 ordinary controls. AABB padding is qualified in R1. Slight breakouts/overlaps have accurate values, so they are not classified as wrong observations.

### (b) Wrong verdict

| Family | Expected | Actual | Qualification |
|---|---|---|---|
| Tilt 1e-6 radians | out_of_scope | form_violation | Actual non-Z axes; angular cutoff. |
| Radius step 1e-5 / 1e-6 | out_of_scope | form_violation | Independent radii 5 and 5.00001 / 5.000001. |
| Different D by 1e-8 / 1e-7 | out_of_scope under literal one-D scope | ok | Tolerance interpretation explicitly qualified. |
| Cross radius 1e-4 | out_of_scope | form_violation | Actual cross cylinder; inset crosses bore. |
| Connected offset steps, axis offset .001001 / .0011 | out_of_scope | form_violation | Partial cylinders treated separately above grouping cutoff, through set empty; still a multi-diameter passage. |

**Fact.** Nominal sub-resolution counterbores erased by the kernel are excluded from confirmed defects. Isolated grouping fixtures refuse .0009 and .001, separate .001001 and .0011; they replace metadata and are not physically consistent measurements.

### (c) Correct part refused

| Cases | Actual | Evidence/qualification |
|---|---|---|
| Four true Z holes D=.0005, .0001, .00005 | form_violation; n=0; other hole variables None | Independent .0005 control valid with four true cylinders. No stated minimum size. |
| Two disjoint D=.0005 holes, distances .0009,.001,.001001,.0011,.002 | form_violation; n=1 on first two, n=0 on rest | Probe/rounded grouping confound intended distance experiment; .0009 geometry independently valid with two cylinders. |
| Positive edge ligament 1e-7 | form_violation; variables correct | Original/exact-method validity passes; normalized boundary check fails. Precision boundary, not a reason to relax R9. |
| Nominal part converted to NURBS | form_violation; n=0; padded box | Approved intentional false refusal. |

**Opinion.** Small-hole coverage needs explicit scope or separate observation candidates. Spline refusal is justified by known unsound analytic recovery. Edge-boundary behavior warrants documentation/testing. Breakout/overlap BReps can be valid solids but violate family F1/F2; they are not compliant family controls.

### (d) Error or long runtime

**Fact.** No naturally built measurable part made observe throw. Empty compound raises BuildError in bounding-box measurement. Fused skins at 8e-8/1e-7 cause a CadQuery Standard_DomainError, at 1.2e-7 a void box; these are G1 build/measurement failures. R5 is an explicitly fault-injected map exception.

**Fact.** Disjoint hole arrays n=20,50,100 return ok in 0.392,2.039,8.210 seconds. No default 10-second timeout occurred. **Inference, moderate confidence:** Boolean probes/residuals and quadratic matching present a latency surface for repeated M3 intent rebuilds. No unbounded workload was run.

### Complete inventory

Each entry supplies code, original expected verdict/values, actual verdict/reason/values/centre, elapsed time and differences. Partial expected dictionaries apply to unsupported shapes; all ordinary controls specify every variable. Original nominal expectations remain visible even when kernel behavior revised the geometric expectation.

#### 001. gen-0001_pushPoints_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; pushPoints, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 1.733617 s; original verdict match: True. Value differences: `[]`.

#### 002. gen-0001_pushPoints_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; pushPoints, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.076119 s; original verdict match: True. Value differences: `[]`.

#### 003. gen-0001_pushPoints_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; pushPoints, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.075321 s; original verdict match: True. Value differences: `[]`.

#### 004. gen-0001_rect_vertices_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rect_vertices, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(25.5,29.5,forConstruction=True).vertices().hole(D)
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.074144 s; original verdict match: True. Value differences: `[]`.

#### 005. gen-0001_rect_vertices_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rect_vertices, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(25.5,29.5,forConstruction=True).vertices().hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.076729 s; original verdict match: True. Value differences: `[]`.

#### 006. gen-0001_rect_vertices_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rect_vertices, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(25.5,29.5,forConstruction=True).vertices().hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.075156 s; original verdict match: True. Value differences: `[]`.

#### 007. gen-0001_rarray_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rarray, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(25.5,29.5,2,2).hole(D)
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.072096 s; original verdict match: True. Value differences: `[]`.

#### 008. gen-0001_rarray_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rarray, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(25.5,29.5,2,2).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.076505 s; original verdict match: True. Value differences: `[]`.

#### 009. gen-0001_rarray_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rarray, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(25.5,29.5,2,2).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.075804 s; original verdict match: True. Value differences: `[]`.

#### 010. gen-0001_circle_cutThruAll_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; circle_cutThruAll, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.094609 s; original verdict match: True. Value differences: `[]`.

#### 011. gen-0001_circle_cutThruAll_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; circle_cutThruAll, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.097144 s; original verdict match: True. Value differences: `[]`.

#### 012. gen-0001_circle_cutThruAll_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; circle_cutThruAll, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.097442 s; original verdict match: True. Value differences: `[]`.

#### 013. gen-0001_rect_extrude_cut_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rect_extrude_cut, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.098569 s; original verdict match: True. Value differences: `[]`.

#### 014. gen-0001_rect_extrude_cut_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rect_extrude_cut, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.098410 s; original verdict match: True. Value differences: `[]`.

#### 015. gen-0001_rect_extrude_cut_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; rect_extrude_cut, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.101272 s; original verdict match: True. Value differences: `[]`.

#### 016. gen-0001_two_sided_cut_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; two_sided_cut, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.123574 s; original verdict match: True. Value differences: `[]`.

#### 017. gen-0001_two_sided_cut_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; two_sided_cut, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.172242 s; original verdict match: True. Value differences: `[]`.

#### 018. gen-0001_two_sided_cut_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; two_sided_cut, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.169081 s; original verdict match: True. Value differences: `[]`.

#### 019. gen-0001_bottom_hole_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; bottom_hole, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108231 s; original verdict match: True. Value differences: `[]`.

#### 020. gen-0001_bottom_hole_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; bottom_hole, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.109633 s; original verdict match: True. Value differences: `[]`.

#### 021. gen-0001_bottom_hole_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; bottom_hole, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.109785 s; original verdict match: True. Value differences: `[]`.

#### 022. gen-0001_lowlevel_solids_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; lowlevel_solids, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.094488 s; original verdict match: True. Value differences: `[]`.

#### 023. gen-0001_lowlevel_solids_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; lowlevel_solids, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.101723 s; original verdict match: True. Value differences: `[]`.

#### 024. gen-0001_lowlevel_solids_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; lowlevel_solids, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.mirror((1,0,0))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105723 s; original verdict match: True. Value differences: `[]`.

#### 025. gen-0001_cutBlind_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; cutBlind, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.089382 s; original verdict match: True. Value differences: `[]`.

#### 026. gen-0001_cutBlind_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; cutBlind, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105931 s; original verdict match: True. Value differences: `[]`.

#### 027. gen-0001_cutBlind_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; cutBlind, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112782 s; original verdict match: True. Value differences: `[]`.

#### 028. gen-0001_absolute_corner_origin_native

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; absolute_corner_origin, native

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107704 s; original verdict match: True. Value differences: `[]`.

#### 029. gen-0001_absolute_corner_origin_translated

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; absolute_corner_origin, translated

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111731 s; original verdict match: True. Value differences: `[]`.

#### 030. gen-0001_absolute_corner_origin_mirrored

Category: `controls`. Train/dev gen-0001; mx=24.5, my=25.75; absolute_corner_origin, mirrored

```python
import cadquery as cq
L,W,T,D=74.5,81.0,4.5,10.5
points=[(-12.75, -14.75), (-12.75, 14.75), (12.75, -14.75), (12.75, 14.75)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.5, "L": 74.5, "T": 4.5, "W": 81.0, "centered": true, "mx": 24.5, "my": 25.75, "n": 4, "px": 25.5, "py": 29.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.114619 s; original verdict match: True. Value differences: `[]`.

#### 031. gen-0115_pushPoints_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; pushPoints, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108444 s; original verdict match: True. Value differences: `[]`.

#### 032. gen-0115_pushPoints_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; pushPoints, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.106129 s; original verdict match: True. Value differences: `[]`.

#### 033. gen-0115_pushPoints_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; pushPoints, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.115363 s; original verdict match: True. Value differences: `[]`.

#### 034. gen-0115_rect_vertices_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rect_vertices, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(142.0,42.0,forConstruction=True).vertices().hole(D)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105462 s; original verdict match: True. Value differences: `[]`.

#### 035. gen-0115_rect_vertices_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rect_vertices, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(142.0,42.0,forConstruction=True).vertices().hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113642 s; original verdict match: True. Value differences: `[]`.

#### 036. gen-0115_rect_vertices_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rect_vertices, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(142.0,42.0,forConstruction=True).vertices().hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112593 s; original verdict match: True. Value differences: `[]`.

#### 037. gen-0115_rarray_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rarray, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(142.0,42.0,2,2).hole(D)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.100175 s; original verdict match: True. Value differences: `[]`.

#### 038. gen-0115_rarray_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rarray, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(142.0,42.0,2,2).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.096736 s; original verdict match: True. Value differences: `[]`.

#### 039. gen-0115_rarray_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rarray, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(142.0,42.0,2,2).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111178 s; original verdict match: True. Value differences: `[]`.

#### 040. gen-0115_circle_cutThruAll_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; circle_cutThruAll, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.139574 s; original verdict match: True. Value differences: `[]`.

#### 041. gen-0115_circle_cutThruAll_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; circle_cutThruAll, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.145912 s; original verdict match: True. Value differences: `[]`.

#### 042. gen-0115_circle_cutThruAll_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; circle_cutThruAll, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.146034 s; original verdict match: True. Value differences: `[]`.

#### 043. gen-0115_rect_extrude_cut_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rect_extrude_cut, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.139227 s; original verdict match: True. Value differences: `[]`.

#### 044. gen-0115_rect_extrude_cut_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rect_extrude_cut, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.145202 s; original verdict match: True. Value differences: `[]`.

#### 045. gen-0115_rect_extrude_cut_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; rect_extrude_cut, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.149376 s; original verdict match: True. Value differences: `[]`.

#### 046. gen-0115_two_sided_cut_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; two_sided_cut, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.160854 s; original verdict match: True. Value differences: `[]`.

#### 047. gen-0115_two_sided_cut_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; two_sided_cut, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.175276 s; original verdict match: True. Value differences: `[]`.

#### 048. gen-0115_two_sided_cut_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; two_sided_cut, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.172938 s; original verdict match: True. Value differences: `[]`.

#### 049. gen-0115_bottom_hole_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; bottom_hole, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.104796 s; original verdict match: True. Value differences: `[]`.

#### 050. gen-0115_bottom_hole_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; bottom_hole, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113988 s; original verdict match: True. Value differences: `[]`.

#### 051. gen-0115_bottom_hole_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; bottom_hole, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113432 s; original verdict match: True. Value differences: `[]`.

#### 052. gen-0115_lowlevel_solids_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; lowlevel_solids, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.102564 s; original verdict match: True. Value differences: `[]`.

#### 053. gen-0115_lowlevel_solids_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; lowlevel_solids, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105456 s; original verdict match: True. Value differences: `[]`.

#### 054. gen-0115_lowlevel_solids_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; lowlevel_solids, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.mirror((1,0,0))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108785 s; original verdict match: True. Value differences: `[]`.

#### 055. gen-0115_cutBlind_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; cutBlind, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.099622 s; original verdict match: True. Value differences: `[]`.

#### 056. gen-0115_cutBlind_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; cutBlind, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105332 s; original verdict match: True. Value differences: `[]`.

#### 057. gen-0115_cutBlind_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; cutBlind, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.100901 s; original verdict match: True. Value differences: `[]`.

#### 058. gen-0115_absolute_corner_origin_native

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; absolute_corner_origin, native

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112126 s; original verdict match: True. Value differences: `[]`.

#### 059. gen-0115_absolute_corner_origin_translated

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; absolute_corner_origin, translated

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.109306 s; original verdict match: True. Value differences: `[]`.

#### 060. gen-0115_absolute_corner_origin_mirrored

Category: `controls`. Train/dev gen-0115; mx=21.5, my=22.75; absolute_corner_origin, mirrored

```python
import cadquery as cq
L,W,T,D=185.0,87.5,10.0,6.0
points=[(-71.0, -21.0), (-71.0, 21.0), (71.0, -21.0), (71.0, 21.0)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 185.0, "T": 10.0, "W": 87.5, "centered": true, "mx": 21.5, "my": 22.75, "n": 4, "px": 142.0, "py": 42.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.106507 s; original verdict match: True. Value differences: `[]`.

#### 061. gen-0214_pushPoints_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; pushPoints, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110315 s; original verdict match: True. Value differences: `[]`.

#### 062. gen-0214_pushPoints_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; pushPoints, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.117004 s; original verdict match: True. Value differences: `[]`.

#### 063. gen-0214_pushPoints_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; pushPoints, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.109199 s; original verdict match: True. Value differences: `[]`.

#### 064. gen-0214_rect_vertices_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rect_vertices, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(164.0,111.0,forConstruction=True).vertices().hole(D)
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.093250 s; original verdict match: True. Value differences: `[]`.

#### 065. gen-0214_rect_vertices_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rect_vertices, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(164.0,111.0,forConstruction=True).vertices().hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111389 s; original verdict match: True. Value differences: `[]`.

#### 066. gen-0214_rect_vertices_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rect_vertices, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(164.0,111.0,forConstruction=True).vertices().hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.116334 s; original verdict match: True. Value differences: `[]`.

#### 067. gen-0214_rarray_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rarray, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(164.0,111.0,2,2).hole(D)
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.104097 s; original verdict match: True. Value differences: `[]`.

#### 068. gen-0214_rarray_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rarray, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(164.0,111.0,2,2).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110530 s; original verdict match: True. Value differences: `[]`.

#### 069. gen-0214_rarray_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rarray, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(164.0,111.0,2,2).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108829 s; original verdict match: True. Value differences: `[]`.

#### 070. gen-0214_circle_cutThruAll_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; circle_cutThruAll, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.749999999999993, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113235 s; original verdict match: True. Value differences: `[]`.

#### 071. gen-0214_circle_cutThruAll_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; circle_cutThruAll, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.749999999999993, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.114109 s; original verdict match: True. Value differences: `[]`.

#### 072. gen-0214_circle_cutThruAll_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; circle_cutThruAll, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.749999999999993, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.146098 s; original verdict match: True. Value differences: `[]`.

#### 073. gen-0214_rect_extrude_cut_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rect_extrude_cut, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.119378 s; original verdict match: True. Value differences: `[]`.

#### 074. gen-0214_rect_extrude_cut_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rect_extrude_cut, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.141380 s; original verdict match: True. Value differences: `[]`.

#### 075. gen-0214_rect_extrude_cut_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; rect_extrude_cut, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.142350 s; original verdict match: True. Value differences: `[]`.

#### 076. gen-0214_two_sided_cut_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; two_sided_cut, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.176755 s; original verdict match: True. Value differences: `[]`.

#### 077. gen-0214_two_sided_cut_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; two_sided_cut, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.170083 s; original verdict match: True. Value differences: `[]`.

#### 078. gen-0214_two_sided_cut_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; two_sided_cut, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.175297 s; original verdict match: True. Value differences: `[]`.

#### 079. gen-0214_bottom_hole_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; bottom_hole, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107729 s; original verdict match: True. Value differences: `[]`.

#### 080. gen-0214_bottom_hole_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; bottom_hole, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107991 s; original verdict match: True. Value differences: `[]`.

#### 081. gen-0214_bottom_hole_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; bottom_hole, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108764 s; original verdict match: True. Value differences: `[]`.

#### 082. gen-0214_lowlevel_solids_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; lowlevel_solids, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.103161 s; original verdict match: True. Value differences: `[]`.

#### 083. gen-0214_lowlevel_solids_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; lowlevel_solids, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.104049 s; original verdict match: True. Value differences: `[]`.

#### 084. gen-0214_lowlevel_solids_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; lowlevel_solids, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.mirror((1,0,0))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.098114 s; original verdict match: True. Value differences: `[]`.

#### 085. gen-0214_cutBlind_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; cutBlind, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.102019 s; original verdict match: True. Value differences: `[]`.

#### 086. gen-0214_cutBlind_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; cutBlind, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111228 s; original verdict match: True. Value differences: `[]`.

#### 087. gen-0214_cutBlind_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; cutBlind, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.096421 s; original verdict match: True. Value differences: `[]`.

#### 088. gen-0214_absolute_corner_origin_native

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; absolute_corner_origin, native

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108402 s; original verdict match: True. Value differences: `[]`.

#### 089. gen-0214_absolute_corner_origin_translated

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; absolute_corner_origin, translated

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.117960 s; original verdict match: True. Value differences: `[]`.

#### 090. gen-0214_absolute_corner_origin_mirrored

Category: `controls`. Train/dev gen-0214; mx=9.5, my=10.75; absolute_corner_origin, mirrored

```python
import cadquery as cq
L,W,T,D=183.0,132.5,3.0,4.5
points=[(-82.0, -55.5), (-82.0, 55.5), (82.0, -55.5), (82.0, 55.5)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 4.5, "L": 183.0, "T": 3.0, "W": 132.5, "centered": true, "mx": 9.5, "my": 10.75, "n": 4, "px": 164.0, "py": 111.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.116944 s; original verdict match: True. Value differences: `[]`.

#### 091. gen-0208_pushPoints_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; pushPoints, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110236 s; original verdict match: True. Value differences: `[]`.

#### 092. gen-0208_pushPoints_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; pushPoints, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108621 s; original verdict match: True. Value differences: `[]`.

#### 093. gen-0208_pushPoints_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; pushPoints, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105256 s; original verdict match: True. Value differences: `[]`.

#### 094. gen-0208_rect_vertices_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rect_vertices, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(29.0,19.5,forConstruction=True).vertices().hole(D)
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105359 s; original verdict match: True. Value differences: `[]`.

#### 095. gen-0208_rect_vertices_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rect_vertices, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(29.0,19.5,forConstruction=True).vertices().hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.114205 s; original verdict match: True. Value differences: `[]`.

#### 096. gen-0208_rect_vertices_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rect_vertices, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(29.0,19.5,forConstruction=True).vertices().hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.121136 s; original verdict match: True. Value differences: `[]`.

#### 097. gen-0208_rarray_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rarray, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(29.0,19.5,2,2).hole(D)
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.114014 s; original verdict match: True. Value differences: `[]`.

#### 098. gen-0208_rarray_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rarray, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(29.0,19.5,2,2).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112474 s; original verdict match: True. Value differences: `[]`.

#### 099. gen-0208_rarray_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rarray, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(29.0,19.5,2,2).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111264 s; original verdict match: True. Value differences: `[]`.

#### 100. gen-0208_circle_cutThruAll_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; circle_cutThruAll, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.249999999999998, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.140478 s; original verdict match: True. Value differences: `[]`.

#### 101. gen-0208_circle_cutThruAll_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; circle_cutThruAll, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.143335 s; original verdict match: True. Value differences: `[]`.

#### 102. gen-0208_circle_cutThruAll_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; circle_cutThruAll, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.249999999999998, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.140363 s; original verdict match: True. Value differences: `[]`.

#### 103. gen-0208_rect_extrude_cut_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rect_extrude_cut, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.148312 s; original verdict match: True. Value differences: `[]`.

#### 104. gen-0208_rect_extrude_cut_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rect_extrude_cut, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.147673 s; original verdict match: True. Value differences: `[]`.

#### 105. gen-0208_rect_extrude_cut_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; rect_extrude_cut, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.135852 s; original verdict match: True. Value differences: `[]`.

#### 106. gen-0208_two_sided_cut_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; two_sided_cut, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.176887 s; original verdict match: True. Value differences: `[]`.

#### 107. gen-0208_two_sided_cut_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; two_sided_cut, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.162985 s; original verdict match: True. Value differences: `[]`.

#### 108. gen-0208_two_sided_cut_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; two_sided_cut, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.166433 s; original verdict match: True. Value differences: `[]`.

#### 109. gen-0208_bottom_hole_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; bottom_hole, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.101104 s; original verdict match: True. Value differences: `[]`.

#### 110. gen-0208_bottom_hole_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; bottom_hole, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113709 s; original verdict match: True. Value differences: `[]`.

#### 111. gen-0208_bottom_hole_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; bottom_hole, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.114615 s; original verdict match: True. Value differences: `[]`.

#### 112. gen-0208_lowlevel_solids_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; lowlevel_solids, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.103256 s; original verdict match: True. Value differences: `[]`.

#### 113. gen-0208_lowlevel_solids_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; lowlevel_solids, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107499 s; original verdict match: True. Value differences: `[]`.

#### 114. gen-0208_lowlevel_solids_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; lowlevel_solids, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.mirror((1,0,0))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.100353 s; original verdict match: True. Value differences: `[]`.

#### 115. gen-0208_cutBlind_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; cutBlind, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.102835 s; original verdict match: True. Value differences: `[]`.

#### 116. gen-0208_cutBlind_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; cutBlind, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110616 s; original verdict match: True. Value differences: `[]`.

#### 117. gen-0208_cutBlind_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; cutBlind, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108507 s; original verdict match: True. Value differences: `[]`.

#### 118. gen-0208_absolute_corner_origin_native

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; absolute_corner_origin, native

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110520 s; original verdict match: True. Value differences: `[]`.

#### 119. gen-0208_absolute_corner_origin_translated

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; absolute_corner_origin, translated

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112041 s; original verdict match: True. Value differences: `[]`.

#### 120. gen-0208_absolute_corner_origin_mirrored

Category: `controls`. Train/dev gen-0208; mx=7.0, my=8.25; absolute_corner_origin, mirrored

```python
import cadquery as cq
L,W,T,D=43.0,36.0,6.5,8.5
points=[(-14.5, -9.75), (-14.5, 9.75), (14.5, -9.75), (14.5, 9.75)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 8.5, "L": 43.0, "T": 6.5, "W": 36.0, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 29.0, "py": 19.5, "rectangular": true, "symmetric": true}}`.

Elapsed 0.123967 s; original verdict match: True. Value differences: `[]`.

#### 121. gen-0024_pushPoints_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; pushPoints, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107276 s; original verdict match: True. Value differences: `[]`.

#### 122. gen-0024_pushPoints_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; pushPoints, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.101312 s; original verdict match: True. Value differences: `[]`.

#### 123. gen-0024_pushPoints_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; pushPoints, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110431 s; original verdict match: True. Value differences: `[]`.

#### 124. gen-0024_rect_vertices_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rect_vertices, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(172.5,128.0,forConstruction=True).vertices().hole(D)
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.109162 s; original verdict match: True. Value differences: `[]`.

#### 125. gen-0024_rect_vertices_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rect_vertices, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(172.5,128.0,forConstruction=True).vertices().hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.115566 s; original verdict match: True. Value differences: `[]`.

#### 126. gen-0024_rect_vertices_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rect_vertices, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(172.5,128.0,forConstruction=True).vertices().hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.115237 s; original verdict match: True. Value differences: `[]`.

#### 127. gen-0024_rarray_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rarray, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(172.5,128.0,2,2).hole(D)
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.106735 s; original verdict match: True. Value differences: `[]`.

#### 128. gen-0024_rarray_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rarray, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(172.5,128.0,2,2).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110039 s; original verdict match: True. Value differences: `[]`.

#### 129. gen-0024_rarray_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rarray, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(172.5,128.0,2,2).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111604 s; original verdict match: True. Value differences: `[]`.

#### 130. gen-0024_circle_cutThruAll_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; circle_cutThruAll, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.137977 s; original verdict match: True. Value differences: `[]`.

#### 131. gen-0024_circle_cutThruAll_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; circle_cutThruAll, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.146679 s; original verdict match: True. Value differences: `[]`.

#### 132. gen-0024_circle_cutThruAll_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; circle_cutThruAll, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.142861 s; original verdict match: True. Value differences: `[]`.

#### 133. gen-0024_rect_extrude_cut_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rect_extrude_cut, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.119418 s; original verdict match: True. Value differences: `[]`.

#### 134. gen-0024_rect_extrude_cut_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rect_extrude_cut, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.126375 s; original verdict match: True. Value differences: `[]`.

#### 135. gen-0024_rect_extrude_cut_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; rect_extrude_cut, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.144121 s; original verdict match: True. Value differences: `[]`.

#### 136. gen-0024_two_sided_cut_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; two_sided_cut, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.171440 s; original verdict match: True. Value differences: `[]`.

#### 137. gen-0024_two_sided_cut_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; two_sided_cut, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.186773 s; original verdict match: True. Value differences: `[]`.

#### 138. gen-0024_two_sided_cut_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; two_sided_cut, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.182983 s; original verdict match: True. Value differences: `[]`.

#### 139. gen-0024_bottom_hole_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; bottom_hole, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112044 s; original verdict match: True. Value differences: `[]`.

#### 140. gen-0024_bottom_hole_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; bottom_hole, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.116587 s; original verdict match: True. Value differences: `[]`.

#### 141. gen-0024_bottom_hole_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; bottom_hole, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.117685 s; original verdict match: True. Value differences: `[]`.

#### 142. gen-0024_lowlevel_solids_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; lowlevel_solids, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.092811 s; original verdict match: True. Value differences: `[]`.

#### 143. gen-0024_lowlevel_solids_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; lowlevel_solids, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108442 s; original verdict match: True. Value differences: `[]`.

#### 144. gen-0024_lowlevel_solids_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; lowlevel_solids, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.mirror((1,0,0))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108273 s; original verdict match: True. Value differences: `[]`.

#### 145. gen-0024_cutBlind_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; cutBlind, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107549 s; original verdict match: True. Value differences: `[]`.

#### 146. gen-0024_cutBlind_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; cutBlind, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.114809 s; original verdict match: True. Value differences: `[]`.

#### 147. gen-0024_cutBlind_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; cutBlind, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111532 s; original verdict match: True. Value differences: `[]`.

#### 148. gen-0024_absolute_corner_origin_native

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; absolute_corner_origin, native

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110748 s; original verdict match: True. Value differences: `[]`.

#### 149. gen-0024_absolute_corner_origin_translated

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; absolute_corner_origin, translated

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113443 s; original verdict match: True. Value differences: `[]`.

#### 150. gen-0024_absolute_corner_origin_mirrored

Category: `controls`. Train/dev gen-0024; mx=7.0, my=8.25; absolute_corner_origin, mirrored

```python
import cadquery as cq
L,W,T,D=186.5,144.5,12.0,5.0
points=[(-86.25, -64.0), (-86.25, 64.0), (86.25, -64.0), (86.25, 64.0)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 5.0, "L": 186.5, "T": 12.0, "W": 144.5, "centered": true, "mx": 7.0, "my": 8.25, "n": 4, "px": 172.5, "py": 128.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111996 s; original verdict match: True. Value differences: `[]`.

#### 151. gen-0037_pushPoints_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; pushPoints, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.098165 s; original verdict match: True. Value differences: `[]`.

#### 152. gen-0037_pushPoints_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; pushPoints, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113150 s; original verdict match: True. Value differences: `[]`.

#### 153. gen-0037_pushPoints_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; pushPoints, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.109989 s; original verdict match: True. Value differences: `[]`.

#### 154. gen-0037_rect_vertices_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rect_vertices, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(177.0,61.0,forConstruction=True).vertices().hole(D)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107873 s; original verdict match: True. Value differences: `[]`.

#### 155. gen-0037_rect_vertices_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rect_vertices, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(177.0,61.0,forConstruction=True).vertices().hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.116428 s; original verdict match: True. Value differences: `[]`.

#### 156. gen-0037_rect_vertices_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rect_vertices, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rect(177.0,61.0,forConstruction=True).vertices().hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.122989 s; original verdict match: True. Value differences: `[]`.

#### 157. gen-0037_rarray_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rarray, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(177.0,61.0,2,2).hole(D)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.091921 s; original verdict match: True. Value differences: `[]`.

#### 158. gen-0037_rarray_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rarray, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(177.0,61.0,2,2).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.083976 s; original verdict match: True. Value differences: `[]`.

#### 159. gen-0037_rarray_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rarray, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().rarray(177.0,61.0,2,2).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.114902 s; original verdict match: True. Value differences: `[]`.

#### 160. gen-0037_circle_cutThruAll_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; circle_cutThruAll, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.141745 s; original verdict match: True. Value differences: `[]`.

#### 161. gen-0037_circle_cutThruAll_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; circle_cutThruAll, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.145720 s; original verdict match: True. Value differences: `[]`.

#### 162. gen-0037_circle_cutThruAll_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; circle_cutThruAll, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutThruAll()
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.146913 s; original verdict match: True. Value differences: `[]`.

#### 163. gen-0037_rect_extrude_cut_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rect_extrude_cut, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.145484 s; original verdict match: True. Value differences: `[]`.

#### 164. gen-0037_rect_extrude_cut_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rect_extrude_cut, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.146372 s; original verdict match: True. Value differences: `[]`.

#### 165. gen-0037_rect_extrude_cut_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; rect_extrude_cut, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").rect(L,W).extrude(T).translate((0,0,-T/2))
for x,y in points:
    result=result.cut(cq.Workplane("XY").center(x,y).circle(D/2).extrude(T*2,both=True))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.142550 s; original verdict match: True. Value differences: `[]`.

#### 166. gen-0037_two_sided_cut_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; two_sided_cut, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.170026 s; original verdict match: True. Value differences: `[]`.

#### 167. gen-0037_two_sided_cut_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; two_sided_cut, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.174718 s; original verdict match: True. Value differences: `[]`.

#### 168. gen-0037_two_sided_cut_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; two_sided_cut, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T)
for x,y in points:
    tool=cq.Workplane("XY").center(x,y).circle(D/2).extrude(T,clean=False)
    tool=tool.union(cq.Workplane("XY").center(x,y).circle(D/2).extrude(-T,clean=False),clean=False)
    result=result.cut(tool,clean=False)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.179002 s; original verdict match: True. Value differences: `[]`.

#### 169. gen-0037_bottom_hole_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; bottom_hole, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.106769 s; original verdict match: True. Value differences: `[]`.

#### 170. gen-0037_bottom_hole_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; bottom_hole, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112255 s; original verdict match: True. Value differences: `[]`.

#### 171. gen-0037_bottom_hole_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; bottom_hole, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces("<Z").workplane().pushPoints(points).hole(D)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112317 s; original verdict match: True. Value differences: `[]`.

#### 172. gen-0037_lowlevel_solids_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; lowlevel_solids, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.089791 s; original verdict match: True. Value differences: `[]`.

#### 173. gen-0037_lowlevel_solids_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; lowlevel_solids, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107704 s; original verdict match: True. Value differences: `[]`.

#### 174. gen-0037_lowlevel_solids_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; lowlevel_solids, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Solid.makeBox(L,W,T,cq.Vector(-L/2,-W/2,-T/2))
for x,y in points:
    result=result.cut(cq.Solid.makeCylinder(D/2,T*3,cq.Vector(x,y,-T*1.5),cq.Vector(0,0,1)))
result=result.mirror((1,0,0))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.106892 s; original verdict match: True. Value differences: `[]`.

#### 175. gen-0037_cutBlind_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; cutBlind, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.102117 s; original verdict match: True. Value differences: `[]`.

#### 176. gen-0037_cutBlind_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; cutBlind, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113307 s; original verdict match: True. Value differences: `[]`.

#### 177. gen-0037_cutBlind_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; cutBlind, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T).faces(">Z").workplane().pushPoints(points).circle(D/2).cutBlind(-T)
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105536 s; original verdict match: True. Value differences: `[]`.

#### 178. gen-0037_absolute_corner_origin_native

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; absolute_corner_origin, native

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111777 s; original verdict match: True. Value differences: `[]`.

#### 179. gen-0037_absolute_corner_origin_translated

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; absolute_corner_origin, translated

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.translate((123.5,-40.25,9))
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [123.5, -40.25, 9.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.118553 s; original verdict match: True. Value differences: `[]`.

#### 180. gen-0037_absolute_corner_origin_mirrored

Category: `controls`. Train/dev gen-0037; mx=15.0, my=16.25; absolute_corner_origin, mirrored

```python
import cadquery as cq
L,W,T,D=207.0,93.5,3.0,6.0
points=[(-88.5, -30.5), (-88.5, 30.5), (88.5, -30.5), (88.5, 30.5)]
result=cq.Workplane("XY").box(L,W,T,centered=False).faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(D).translate((-L/2,-W/2,-T/2))
result=result.mirror("YZ")
```

**Expected:** `ok`; values `{"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 6.0, "L": 207.0, "T": 3.0, "W": 93.5, "centered": true, "mx": 15.0, "my": 16.25, "n": 4, "px": 177.0, "py": 61.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.105375 s; original verdict match: True. Value differences: `[]`.

#### 181. count_1

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(0, 0)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 50.0, "my": 40.0, "n": 1, "px": 0, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 50.0, "my": 40.0, "n": 1, "px": 0.0, "py": 0.0, "rectangular": false, "symmetric": true}}`.

Elapsed 0.052407 s; original verdict match: True. Value differences: `[]`.

#### 182. count_2

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, 0), (35, 0)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 40.0, "n": 2, "px": 70, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 40.0, "n": 2, "px": 70.0, "py": 0.0, "rectangular": false, "symmetric": true}}`.

Elapsed 0.068026 s; original verdict match: True. Value differences: `[]`.

#### 183. count_3

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": false, "mx": 15.0, "my": 15.0, "n": 3, "px": 70, "py": 50, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 15.0, "my": 15.0, "n": 3, "px": 70.0, "py": 50.0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.091424 s; original verdict match: True. Value differences: `[]`.

#### 184. count_5

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25), (0, 0)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 5, "px": 70, "py": 50, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 5, "px": 70.0, "py": 50.0, "rectangular": false, "symmetric": true}}`.

Elapsed 0.140344 s; original verdict match: True. Value differences: `[]`.

#### 185. count_6

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (0, -25), (0, 25), (35, -25), (35, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 6, "px": 70, "py": 50, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 6, "px": 70.0, "py": 50.0, "rectangular": false, "symmetric": true}}`.

Elapsed 0.161525 s; original verdict match: True. Value differences: `[]`.

#### 186. count_0

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
```

**Expected:** `ok`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.021910 s; original verdict match: True. Value differences: `[]`.

#### 187. rotation_90

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.rotate((0,0,0),(0,0,1),90)
```

**Expected:** `ok`; values `{"D": 10, "L": 80, "T": 4, "W": 100, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 50, "py": 70, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 80.00000000000001, "T": 4.0, "W": 100.00000000000001, "centered": true, "mx": 15.000000000000004, "my": 15.000000000000007, "n": 4, "px": 50.00000000000001, "py": 70.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.114536 s; original verdict match: True. Value differences: `[]`.

#### 188. rotation_180

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.rotate((0,0,0),(0,0,1),180)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.00000000000001, "T": 4.0, "W": 80.00000000000001, "centered": true, "mx": 15.000000000000007, "my": 15.000000000000007, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113547 s; original verdict match: True. Value differences: `[]`.

#### 189. rotation_270

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.rotate((0,0,0),(0,0,1),270)
```

**Expected:** `ok`; values `{"D": 10, "L": 80, "T": 4, "W": 100, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 50, "py": 70, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, -3.552713678800501e-15, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 80.00000000000003, "T": 4.0, "W": 100.00000000000003, "centered": true, "mx": 15.000000000000007, "my": 15.0, "n": 4, "px": 50.000000000000014, "py": 70.00000000000001, "rectangular": true, "symmetric": true}}`.

Elapsed 0.096672 s; original verdict match: True. Value differences: `[]`.

#### 190. edge_ligament_1

Category: `synthetic`. Positive ligament; no breakout intended.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-44, -25), (-44, 25), (44, -25), (44, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 6.0, "my": 15.0, "n": 4, "px": 88, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 6.0, "my": 15.0, "n": 4, "px": 88.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.110395 s; original verdict match: True. Value differences: `[]`.

#### 191. edge_ligament_0.001

Category: `synthetic`. Positive ligament; no breakout intended.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-44.999, -25), (-44.999, 25), (44.999, -25), (44.999, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 5.000999999999998, "my": 15.0, "n": 4, "px": 89.998, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 5.000999999999998, "my": 15.0, "n": 4, "px": 89.998, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.119827 s; original verdict match: True. Value differences: `[]`.

#### 192. edge_ligament_1e-06

Category: `synthetic`. Positive ligament; no breakout intended.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-44.999999, -25), (-44.999999, 25), (44.999999, -25), (44.999999, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 5.0000009999999975, "my": 15.0, "n": 4, "px": 89.999998, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 5.0000009999999975, "my": 15.0, "n": 4, "px": 89.999998, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107190 s; original verdict match: True. Value differences: `[]`.

#### 193. edge_ligament_1e-07

Category: `synthetic`. Positive ligament; no breakout intended.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-44.9999999, -25), (-44.9999999, 25), (44.9999999, -25), (44.9999999, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 5.000000100000001, "my": 15.0, "n": 4, "px": 89.9999998, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "the edges do not lie on the faces at the form tolerance; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 5.000000100000001, "my": 15.0, "n": 4, "px": 89.9999998, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.137111 s; original verdict match: False. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0], vertex Z extrema=[-2.0, 2.0].

#### 194. side_breakout

Category: `synthetic`. Valid BRep, violates family containment F1; incomplete cylindrical wall is not a recognised hole.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(48, 0)]).hole(10)
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [3.552713678800501e-15, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 234.122 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.041975 s; original verdict match: True. Value differences: `[]`.

#### 195. overlap

Category: `synthetic`. Valid BRep, violates family non-overlap F2; recogniser sees partial cylinders.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-3, 0), (3, 0)]).hole(10)
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 537.512 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.050035 s; original verdict match: True. Value differences: `[]`.

#### 196. small_diameter_0.1

Category: `synthetic`. Four disjoint true cylindrical holes; small positive diameter.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(0.1)
```

**Expected:** `ok`; values `{"D": 0.1, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.1, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.102576 s; original verdict match: True. Value differences: `[]`.

#### 197. small_diameter_0.01

Category: `synthetic`. Four disjoint true cylindrical holes; small positive diameter.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(0.01)
```

**Expected:** `ok`; values `{"D": 0.01, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.01, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.081368 s; original verdict match: True. Value differences: `[]`.

#### 198. small_diameter_0.002

Category: `synthetic`. Four disjoint true cylindrical holes; small positive diameter.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(0.002)
```

**Expected:** `ok`; values `{"D": 0.002, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.002, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.076888 s; original verdict match: True. Value differences: `[]`.

#### 199. small_diameter_0.001

Category: `synthetic`. Four disjoint true cylindrical holes; small positive diameter.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(0.001)
```

**Expected:** `ok`; values `{"D": 0.001, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.001, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.079946 s; original verdict match: True. Value differences: `[]`.

#### 200. small_diameter_0.0005

Category: `synthetic`. Four disjoint true cylindrical holes; small positive diameter.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(0.0005)
```

**Expected:** `ok`; values `{"D": 0.0005, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.049628 s; original verdict match: False. Value differences: `[{"actual": 0, "expected": 4, "key": "n"}, {"actual": null, "expected": 0.0005, "key": "D"}, {"actual": null, "expected": 15.0, "key": "mx"}, {"actual": null, "expected": 15.0, "key": "my"}, {"actual": null, "expected": 70, "key": "px"}, {"actual": null, "expected": 50, "key": "py"}, {"actual": false, "expected": true, "key": "rectangular"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[0.00025], vertex Z extrema=[-2.0, 2.0].

#### 201. small_diameter_0.0001

Category: `synthetic`. Four disjoint true cylindrical holes; small positive diameter.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(0.0001)
```

**Expected:** `ok`; values `{"D": 0.0001, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.053347 s; original verdict match: False. Value differences: `[{"actual": 0, "expected": 4, "key": "n"}, {"actual": null, "expected": 0.0001, "key": "D"}, {"actual": null, "expected": 15.0, "key": "mx"}, {"actual": null, "expected": 15.0, "key": "my"}, {"actual": null, "expected": 70, "key": "px"}, {"actual": null, "expected": 50, "key": "py"}, {"actual": false, "expected": true, "key": "rectangular"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

#### 202. small_diameter_5e-05

Category: `synthetic`. Four disjoint true cylindrical holes; small positive diameter.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(5e-05)
```

**Expected:** `ok`; values `{"D": 5e-05, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.057716 s; original verdict match: False. Value differences: `[{"actual": 0, "expected": 4, "key": "n"}, {"actual": null, "expected": 5e-05, "key": "D"}, {"actual": null, "expected": 15.0, "key": "mx"}, {"actual": null, "expected": 15.0, "key": "my"}, {"actual": null, "expected": 70, "key": "px"}, {"actual": null, "expected": 50, "key": "py"}, {"actual": false, "expected": true, "key": "rectangular"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

#### 203. centred_shift_1e-08

Category: `synthetic`. Translate pattern, leave plate fixed. Booleans use form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-34.99999999, -25), (-34.99999999, 25), (35.00000001, -25), (35.00000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.99999999, "my": 15.0, "n": 4, "px": 70.0, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.99999999, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.104089 s; original verdict match: True. Value differences: `[]`.

#### 204. corner_shift_1e-08

Category: `synthetic`. One moved corner tests rectangular and symmetry tolerances.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35.00000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.99999999, "my": 15.0, "n": 4, "px": 70.00000001000001, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.99999999, "my": 15.0, "n": 4, "px": 70.00000001000001, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.108849 s; original verdict match: True. Value differences: `[]`.

#### 205. centred_shift_9e-08

Category: `synthetic`. Translate pattern, leave plate fixed. Booleans use form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-34.99999991, -25), (-34.99999991, 25), (35.00000009, -25), (35.00000009, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.99999991, "my": 15.0, "n": 4, "px": 70.0, "py": 50, "rectangular": true, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.99999991, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": false}}`.

Elapsed 0.103320 s; original verdict match: True. Value differences: `[]`.

#### 206. corner_shift_9e-08

Category: `synthetic`. One moved corner tests rectangular and symmetry tolerances.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35.00000009, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.99999991, "my": 15.0, "n": 4, "px": 70.00000009, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.99999991, "my": 15.0, "n": 4, "px": 70.00000009, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107932 s; original verdict match: True. Value differences: `[]`.

#### 207. centred_shift_1e-07

Category: `synthetic`. Translate pattern, leave plate fixed. Booleans use form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-34.9999999, -25), (-34.9999999, 25), (35.0000001, -25), (35.0000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": false, "mx": 14.999999899999999, "my": 15.0, "n": 4, "px": 70.0, "py": 50, "rectangular": true, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 14.999999899999999, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": false}}`.

Elapsed 0.107015 s; original verdict match: True. Value differences: `[]`.

#### 208. corner_shift_1e-07

Category: `synthetic`. One moved corner tests rectangular and symmetry tolerances.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35.0000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.999999899999999, "my": 15.0, "n": 4, "px": 70.0000001, "py": 50, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.999999899999999, "my": 15.0, "n": 4, "px": 70.0000001, "py": 50.0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.107784 s; original verdict match: True. Value differences: `[]`.

#### 209. centred_shift_1.1e-07

Category: `synthetic`. Translate pattern, leave plate fixed. Booleans use form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-34.99999989, -25), (-34.99999989, 25), (35.00000011, -25), (35.00000011, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": false, "mx": 14.999999889999998, "my": 15.0, "n": 4, "px": 70.0, "py": 50, "rectangular": true, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 14.999999889999998, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": false}}`.

Elapsed 0.104829 s; original verdict match: True. Value differences: `[]`.

#### 210. corner_shift_1.1e-07

Category: `synthetic`. One moved corner tests rectangular and symmetry tolerances.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35.00000011, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.999999889999998, "my": 15.0, "n": 4, "px": 70.00000011, "py": 50, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.999999889999998, "my": 15.0, "n": 4, "px": 70.00000011, "py": 50.0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.113400 s; original verdict match: True. Value differences: `[]`.

#### 211. centred_shift_1e-06

Category: `synthetic`. Translate pattern, leave plate fixed. Booleans use form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-34.999999, -25), (-34.999999, 25), (35.000001, -25), (35.000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": false, "mx": 14.999999000000003, "my": 15.0, "n": 4, "px": 70.0, "py": 50, "rectangular": true, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 14.999999000000003, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": false}}`.

Elapsed 0.114817 s; original verdict match: True. Value differences: `[]`.

#### 212. corner_shift_1e-06

Category: `synthetic`. One moved corner tests rectangular and symmetry tolerances.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35.000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": false, "mx": 14.999999000000003, "my": 15.0, "n": 4, "px": 70.000001, "py": 50, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 14.999999000000003, "my": 15.0, "n": 4, "px": 70.000001, "py": 50.0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.102299 s; original verdict match: True. Value differences: `[]`.

#### 213. diameter_difference_1e-08

Category: `synthetic`. Within form epsilon D=10 is an equivalence representative; above epsilon one D is ambiguous.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25)]).hole(10)
result=result.faces(">Z").workplane().pushPoints([(35,25)]).hole(10.00000001)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.115446 s; original verdict match: True. Value differences: `[]`.

#### 214. diameter_difference_1e-07

Category: `synthetic`. Within form epsilon D=10 is an equivalence representative; above epsilon one D is ambiguous.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25)]).hole(10)
result=result.faces(">Z").workplane().pushPoints([(35,25)]).hole(10.0000001)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.113564 s; original verdict match: True. Value differences: `[]`.

#### 215. diameter_difference_1e-06

Category: `synthetic`. Within form epsilon D=10 is an equivalence representative; above epsilon one D is ambiguous.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25)]).hole(10)
result=result.faces(">Z").workplane().pushPoints([(35,25)]).hole(10.000001)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80, "n": 4}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "through holes of different diameters: D is not one number", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0, "n": 4}}`.

Elapsed 0.112980 s; original verdict match: True. Value differences: `[]`.

#### 216. tilt_radians_1e-08

Category: `synthetic`. Expected centres are axis intersections with top plane z=2. Tiny tilt stays within form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-07).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.999999979999998, "my": 15.0, "n": 4, "px": 70.0, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0000001, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.147213 s; original verdict match: True. Value differences: `[{"actual": 4.0000001, "expected": 4, "key": "T"}, {"actual": 15.0, "expected": 14.999999979999998, "key": "mx"}]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0], vertex Z extrema=[-2.0, 2.0].

#### 217. tilt_radians_1e-06

Category: `synthetic`. Expected centres are axis intersections with top plane z=2. Tiny tilt stays within form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-05).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.169206 s; original verdict match: False. Value differences: `[]`.

#### 218. tilt_radians_0.0001

Category: `synthetic`. Expected centres are axis intersections with top plane z=2. Tiny tilt stays within form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.005729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 1.5543122344752192e-15], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0000000000000036, "W": 80.0}}`.

Elapsed 0.102630 s; original verdict match: True. Value differences: `[]`.

#### 219. tilt_radians_0.01

Category: `synthetic`. Expected centres are axis intersections with top plane z=2. Tiny tilt stays within form epsilon.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.5729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.107757 s; original verdict match: True. Value differences: `[]`.

#### 220. plate_small_rotation_1e-10

Category: `synthetic`. Exact bounding box; non-axis planes beyond form epsilon fail form.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.rotate((0,0,0),(0,0,1),5.729577951308233e-09)
```

**Expected:** `ok`; values `{"D": 10, "L": 100.000000008, "T": 4, "W": 80.00000001, "n": 4}`.

**Actual, fact:** `{"centre": [0.0, 3.552713678800501e-15, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.000000008, "T": 4.0, "W": 80.00000001000001, "centered": true, "mx": 15.000000001499998, "my": 15.000000001499998, "n": 4, "px": 70.000000005, "py": 50.000000007, "rectangular": true, "symmetric": true}}`.

Elapsed 0.109810 s; original verdict match: True. Value differences: `[]`.

#### 221. plate_small_rotation_1e-08

Category: `synthetic`. Exact bounding box; non-axis planes beyond form epsilon fail form.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.rotate((0,0,0),(0,0,1),5.729577951308232e-07)
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100.0000008, "T": 4, "W": 80.000001, "n": 4}`.

**Actual, fact:** `{"centre": [-3.552713678800501e-15, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.00000080000001, "T": 4.0, "W": 80.000001, "centered": true, "mx": 15.000000149999998, "my": 15.000000149999998, "n": 4, "px": 70.0000005, "py": 50.0000007, "rectangular": false, "symmetric": false}}`.

Elapsed 0.111826 s; original verdict match: True. Value differences: `[]`.

#### 222. plate_small_rotation_1e-06

Category: `synthetic`. Exact bounding box; non-axis planes beyond form epsilon fail form.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.rotate((0,0,0),(0,0,1),5.729577951308232e-05)
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100.00007999994999, "T": 4, "W": 80.00009999996, "n": 4}`.

**Actual, fact:** `{"centre": [7.105427357601002e-15, 7.105427357601002e-15, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.00007999995, "T": 4.0, "W": 80.00009999996001, "centered": true, "mx": 15.000014999992494, "my": 15.000014999992501, "n": 4, "px": 70.000049999965, "py": 50.000069999975, "rectangular": false, "symmetric": false}}`.

Elapsed 0.109194 s; original verdict match: True. Value differences: `[]`.

#### 223. plate_small_rotation_0.0001

Category: `synthetic`. Exact bounding box; non-axis planes beyond form epsilon fail form.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.rotate((0,0,0),(0,0,1),0.005729577951308232)
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100.00799949998667, "T": 4, "W": 80.00999959998333, "n": 4}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 1.356 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.00799949998667, "T": 4.0, "W": 80.00999959998333, "centered": true, "mx": 15.001499924997496, "my": 15.0014999249975, "n": 4, "px": 70.00499964999167, "py": 50.00699974998833, "rectangular": false, "symmetric": false}}`.

Elapsed 0.120551 s; original verdict match: True. Value differences: `[]`.

#### 224. blind_membrane_5e-08

Category: `synthetic`. Nominal stopping short; inspect built topology at kernel precision. At <= form epsilon equivalence permits through.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10,3.99999995)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.106809 s; original verdict match: True. Value differences: `[]`.

#### 225. blind_membrane_1e-07

Category: `synthetic`. Nominal stopping short; inspect built topology at kernel precision. At <= form epsilon equivalence permits through.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10,3.9999999)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.107316 s; original verdict match: True. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0], vertex Z extrema=[-2.0, 2.0].

#### 226. blind_membrane_1.1e-07

Category: `synthetic`. Nominal stopping short; inspect built topology at kernel precision. At <= form epsilon equivalence permits through.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10,3.99999989)
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "the edges do not lie on the faces at the form tolerance; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.105078 s; original verdict match: True. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0], vertex Z extrema=[-2.0, 2.0].

#### 227. blind_membrane_5e-07

Category: `synthetic`. Nominal stopping short; inspect built topology at kernel precision. At <= form epsilon equivalence permits through.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10,3.9999995)
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 30743.363 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.124345 s; original verdict match: True. Value differences: `[]`.

#### 228. blind_membrane_1e-06

Category: `synthetic`. Nominal stopping short; inspect built topology at kernel precision. At <= form epsilon equivalence permits through.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10,3.999999)
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.129662 s; original verdict match: True. Value differences: `[]`.

#### 229. blind_membrane_1e-05

Category: `synthetic`. Nominal stopping short; inspect built topology at kernel precision. At <= form epsilon equivalence permits through.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10,3.99999)
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.003 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.129978 s; original verdict match: True. Value differences: `[]`.

#### 230. counterbore_radius_step_2

Category: `synthetic`. Nominal two diameters, stepped hole; kernel may erase sub-resolution step.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.211234 s; original verdict match: True. Value differences: `[]`.

#### 231. counterbore_radius_step_0.001

Category: `synthetic`. Nominal two diameters, stepped hole; kernel may erase sub-resolution step.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(5.001).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.203638 s; original verdict match: True. Value differences: `[]`.

#### 232. counterbore_radius_step_1e-05

Category: `synthetic`. Nominal two diameters, stepped hole; kernel may erase sub-resolution step.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(5.00001).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.00002, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.136987 s; original verdict match: False. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0, 5.00001], vertex Z extrema=[-2.0, 2.0].

#### 233. counterbore_radius_step_1e-06

Category: `synthetic`. Nominal two diameters, stepped hole; kernel may erase sub-resolution step.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(5.000001).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.000002, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.133449 s; original verdict match: False. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0, 5.000001], vertex Z extrema=[-2.0, 2.0].

#### 234. counterbore_radius_step_1e-07

Category: `synthetic`. Nominal two diameters, stepped hole; kernel may erase sub-resolution step.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(5.0000001).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.119127 s; original verdict match: False. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0], vertex Z extrema=[-2.0, 2.0].

**Qualification:** only original cylinders remain; kernel erased the step, so ok is appropriate for the actual built geometry.

#### 235. counterbore_radius_step_1e-08

Category: `synthetic`. Nominal two diameters, stepped hole; kernel may erase sub-resolution step.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(5.00000001).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.122222 s; original verdict match: False. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0], vertex Z extrema=[-2.0, 2.0].

**Qualification:** only original cylinders remain; kernel erased the step, so ok is appropriate for the actual built geometry.

#### 236. counterbore_depth_1.5

Category: `synthetic`. Step depth boundary; inspect built topology for swallowed feature.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=0.5).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.205094 s; original verdict match: True. Value differences: `[]`.

#### 237. counterbore_depth_0.0001

Category: `synthetic`. Step depth boundary; inspect built topology for swallowed feature.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1.9999).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.204927 s; original verdict match: True. Value differences: `[]`.

#### 238. counterbore_depth_1e-06

Category: `synthetic`. Step depth boundary; inspect built topology for swallowed feature.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1.999999).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.210966 s; original verdict match: True. Value differences: `[]`.

#### 239. counterbore_depth_1e-07

Category: `synthetic`. Step depth boundary; inspect built topology for swallowed feature.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1.9999999).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.118588 s; original verdict match: False. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0], vertex Z extrema=[-2.0, 2.0].

**Qualification:** only original cylinders remain; kernel erased the step, so ok is appropriate for the actual built geometry.

#### 240. counterbore_depth_1e-08

Category: `synthetic`. Step depth boundary; inspect built topology for swallowed feature.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").workplane(offset=1.99999999).pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.121477 s; original verdict match: False. Value differences: `[]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[5.0], vertex Z extrema=[-2.0, 2.0].

**Qualification:** only original cylinders remain; kernel erased the step, so ok is appropriate for the actual built geometry.

#### 241. close_distinct_axes_0.0009

Category: `synthetic`. Two disjoint cylinders, radius .00025; expected two distinct axes even below the counterbore grouping distance.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-0.00045, 0), (0.00045, 0)]).hole(0.0005)
```

**Expected:** `ok`; values `{"D": 0.0005, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 49.99955, "my": 40.0, "n": 2, "px": 0.0009, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 0.0005, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 49.99955, "my": 40.0, "n": 1, "px": 0.0, "py": 0.0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.043828 s; original verdict match: False. Value differences: `[{"actual": 1, "expected": 2, "key": "n"}, {"actual": 0.0, "expected": 0.0009, "key": "px"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

**Independent geometry, fact:** valid=True, exact-method valid=True, radii=[0.00025], vertex Z extrema=[-2.0, 2.0].

#### 242. close_distinct_axes_0.001

Category: `synthetic`. Two disjoint cylinders, radius .00025; expected two distinct axes even below the counterbore grouping distance.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-0.0005, 0), (0.0005, 0)]).hole(0.0005)
```

**Expected:** `ok`; values `{"D": 0.0005, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 49.9995, "my": 40.0, "n": 2, "px": 0.001, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 0.0005, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 49.9995, "my": 40.0, "n": 1, "px": 0.0, "py": 0.0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.045388 s; original verdict match: False. Value differences: `[{"actual": 1, "expected": 2, "key": "n"}, {"actual": 0.0, "expected": 0.001, "key": "px"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

#### 243. close_distinct_axes_0.001001

Category: `synthetic`. Two disjoint cylinders, radius .00025; expected two distinct axes even below the counterbore grouping distance.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-0.0005005, 0), (0.0005005, 0)]).hole(0.0005)
```

**Expected:** `ok`; values `{"D": 0.0005, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 49.9994995, "my": 40.0, "n": 2, "px": 0.001001, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.038798 s; original verdict match: False. Value differences: `[{"actual": 0, "expected": 2, "key": "n"}, {"actual": null, "expected": 0.0005, "key": "D"}, {"actual": null, "expected": 49.9994995, "key": "mx"}, {"actual": null, "expected": 40.0, "key": "my"}, {"actual": null, "expected": 0.001001, "key": "px"}, {"actual": null, "expected": 0, "key": "py"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

#### 244. close_distinct_axes_0.0011

Category: `synthetic`. Two disjoint cylinders, radius .00025; expected two distinct axes even below the counterbore grouping distance.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-0.00055, 0), (0.00055, 0)]).hole(0.0005)
```

**Expected:** `ok`; values `{"D": 0.0005, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 49.99945, "my": 40.0, "n": 2, "px": 0.0011, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.036852 s; original verdict match: False. Value differences: `[{"actual": 0, "expected": 2, "key": "n"}, {"actual": null, "expected": 0.0005, "key": "D"}, {"actual": null, "expected": 49.99945, "key": "mx"}, {"actual": null, "expected": 40.0, "key": "my"}, {"actual": null, "expected": 0.0011, "key": "px"}, {"actual": null, "expected": 0, "key": "py"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

#### 245. close_distinct_axes_0.002

Category: `synthetic`. Two disjoint cylinders, radius .00025; expected two distinct axes even below the counterbore grouping distance.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-0.001, 0), (0.001, 0)]).hole(0.0005)
```

**Expected:** `ok`; values `{"D": 0.0005, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 49.999, "my": 40.0, "n": 2, "px": 0.002, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.041136 s; original verdict match: False. Value differences: `[{"actual": 0, "expected": 2, "key": "n"}, {"actual": null, "expected": 0.0005, "key": "D"}, {"actual": null, "expected": 49.999, "key": "mx"}, {"actual": null, "expected": 40.0, "key": "my"}, {"actual": null, "expected": 0.002, "key": "px"}, {"actual": null, "expected": 0, "key": "py"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

#### 246. offset_step_axes_0.0009

Category: `synthetic`. Connected stepped passage, offset axes, lower cylinder from bottom to z=1 and larger upper cylinder.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
result=result.cut(cq.Workplane("XY").workplane(offset=-3).circle(5).extrude(4))
result=result.cut(cq.Workplane("XY").workplane(offset=1).center(0.0009,0).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.068256 s; original verdict match: True. Value differences: `[]`.

#### 247. offset_step_axes_0.001

Category: `synthetic`. Connected stepped passage, offset axes, lower cylinder from bottom to z=1 and larger upper cylinder.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
result=result.cut(cq.Workplane("XY").workplane(offset=-3).circle(5).extrude(4))
result=result.cut(cq.Workplane("XY").workplane(offset=1).center(0.001,0).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.081551 s; original verdict match: True. Value differences: `[]`.

#### 248. offset_step_axes_0.001001

Category: `synthetic`. Connected stepped passage, offset axes, lower cylinder from bottom to z=1 and larger upper cylinder.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
result=result.cut(cq.Workplane("XY").workplane(offset=-3).circle(5).extrude(4))
result=result.cut(cq.Workplane("XY").workplane(offset=1).center(0.001001,0).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 225.535 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.077980 s; original verdict match: False. Value differences: `[]`.

#### 249. offset_step_axes_0.0011

Category: `synthetic`. Connected stepped passage, offset axes, lower cylinder from bottom to z=1 and larger upper cylinder.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
result=result.cut(cq.Workplane("XY").workplane(offset=-3).circle(5).extrude(4))
result=result.cut(cq.Workplane("XY").workplane(offset=1).center(0.0011,0).circle(7).extrude(2))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 225.535 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.075867 s; original verdict match: False. Value differences: `[]`.

#### 250. fillet_vertical

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).edges("|Z").fillet(2).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 13.396 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.140681 s; original verdict match: True. Value differences: `[]`.

#### 251. chamfer_top

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").edges().chamfer(.5).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [-3.552713678800501e-15, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 43.056 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.128709 s; original verdict match: True. Value differences: `[]`.

#### 252. pocket_rect

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").box(20,10,2).translate((0,0,2)))
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 199.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.124339 s; original verdict match: True. Value differences: `[]`.

#### 253. pocket_round

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.faces(">Z").workplane().circle(3).cutBlind(-1)
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 84.540 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.145432 s; original verdict match: True. Value differences: `[]`.

#### 254. slot_rect

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").box(20,4,10))
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 319.200 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.112531 s; original verdict match: True. Value differences: `[]`.

#### 255. slot_round

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.faces(">Z").workplane().slot2D(20,4).cutThruAll()
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 305.500 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.139276 s; original verdict match: True. Value differences: `[]`.

#### 256. boss

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.union(cq.Workplane("XY").workplane(offset=2).circle(3).extrude(2))
```

**Expected:** `form_violation`; values `{"L": 100, "T": 6, "W": 80, "n": 0}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 1.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 15272.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 6.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.134470 s; original verdict match: True. Value differences: `[]`.

#### 257. blind

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10,2)
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 627.063 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.129192 s; original verdict match: True. Value differences: `[]`.

#### 258. faceted

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).polygon(24,10).cutThruAll()
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 7.105427357601002e-15], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 1239.226 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.000000000000014, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.481483 s; original verdict match: True. Value differences: `[]`.

#### 259. cross_X

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("YZ").circle(1).extrude(200,both=True))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.099645 s; original verdict match: True. Value differences: `[]`.

#### 260. cross_Y

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XZ").circle(1).extrude(200,both=True))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.107756 s; original verdict match: True. Value differences: `[]`.

#### 261. two_solids

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=cq.Compound.makeCompound([result.val(),cq.Solid.makeBox(5,5,5,cq.Vector(200,0,0))])
```

**Expected:** `not_single_solid`; values `{}`.

**Actual, fact:** `{"centre": null, "reason": "2 solids, exactly one is required", "status": "not_single_solid", "values": {}}`.

Elapsed 0.126125 s; original verdict match: True. Value differences: `[]`.

#### 262. empty_compound

Category: `synthetic`. observe_code raises BuildError before observe, as recorded.

```python
import cadquery as cq
result=cq.Compound.makeCompound([])
```

**Expected:** `build_error`; values `{}`.

**Actual, fact:** `{"error": "BuildError('shape could not be measured: Bnd_Box is void')", "status": "build_error"}`.

Elapsed 0.006627 s; original verdict match: True. Value differences: `[]`.

#### 263. loose_face

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=cq.Compound.makeCompound([result.val(),cq.Face.makePlane(5,5,cq.Vector(200,0,0))])
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [76.25, 0.0, 0.0], "reason": "not one clean, valid, single-shell solid", "status": "form_violation", "values": {"D": 10.0, "L": 252.5, "T": 4.0, "W": 80.0, "centered": false, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": false}}`.

Elapsed 0.105269 s; original verdict match: True. Value differences: `[{"actual": 252.5, "expected": 100, "key": "L"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

**Qualification:** expected numbers refer to the plate solid, but the map measures the whole compound. The remote loose face expands L/centre and changes booleans. Clean-solid refusal is correct; accompanying plate variables are unsuitable.

#### 264. internal_cavity

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("XY").box(4,4,1))
```

**Expected:** `form_violation`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "not one clean, valid, single-shell solid", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.111063 s; original verdict match: True. Value differences: `[]`.

#### 265. NURBS

Category: `synthetic`. Approved known false refusal.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.val().toNURBS()
```

**Expected:** `form_violation`; values `{"D": null, "n": 0}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 1264.973 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0000002, "T": 4.0000002, "W": 80.0000002, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.414601 s; original verdict match: True. Value differences: `[]`.

#### 266. extended_tilt_D0.001_r1e-08

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.0005).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-07).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.001, "L": 100.0, "T": 4.00000000001, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 2.919855 s; original verdict match: False. Value differences: `[]`.

#### 267. extended_tilt_D0.001_r1e-06

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.0005).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-05).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 0.001, "L": 100.0, "T": 4.000000001, "W": 80.0, "centered": false, "mx": 15.0, "my": 15.0, "n": 2, "px": 0.0, "py": 50.0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.145987 s; original verdict match: False. Value differences: `[{"actual": 4.000000001, "expected": 4, "key": "T"}]`.

#### 268. extended_tilt_D0.001_r0.0001

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.0005).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.005729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.000000099999999, "W": 80.0}}`.

Elapsed 0.144359 s; original verdict match: True. Value differences: `[{"actual": 4.000000099999999, "expected": 4, "key": "T"}]`.

#### 269. extended_tilt_D0.001_r0.01

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.0005).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.5729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 4.440892098500626e-16], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.000000000000001, "W": 80.0}}`.

Elapsed 0.150840 s; original verdict match: True. Value differences: `[]`.

#### 270. extended_tilt_D0.002_r1e-08

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.001).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-07).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.002, "L": 100.0, "T": 4.00000000002, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.165785 s; original verdict match: False. Value differences: `[]`.

#### 271. extended_tilt_D0.002_r1e-06

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.001).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-05).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 0.002, "L": 100.0, "T": 4.000000002, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.183100 s; original verdict match: False. Value differences: `[{"actual": 4.000000002, "expected": 4, "key": "T"}]`.

#### 272. extended_tilt_D0.002_r0.0001

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.001).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.005729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0000002, "W": 80.0}}`.

Elapsed 0.150293 s; original verdict match: True. Value differences: `[{"actual": 4.0000002, "expected": 4, "key": "T"}]`.

#### 273. extended_tilt_D0.002_r0.01

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.001).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.5729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, -2.220446049250313e-16], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.163825 s; original verdict match: True. Value differences: `[]`.

#### 274. extended_tilt_D0.01_r1e-08

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.005).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-07).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.01, "L": 100.0, "T": 4.0000000001, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.186266 s; original verdict match: False. Value differences: `[]`.

#### 275. extended_tilt_D0.01_r1e-06

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.005).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-05).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 0.01, "L": 100.0, "T": 4.00000001, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.179439 s; original verdict match: False. Value differences: `[{"actual": 4.00000001, "expected": 4, "key": "T"}]`.

#### 276. extended_tilt_D0.01_r0.0001

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.005).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.005729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, -8.881784197001252e-16], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.000000000000002, "W": 80.0}}`.

Elapsed 0.155242 s; original verdict match: True. Value differences: `[]`.

#### 277. extended_tilt_D0.01_r0.01

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.005).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.5729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 2.220446049250313e-16], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.159070 s; original verdict match: True. Value differences: `[]`.

#### 278. extended_tilt_D0.1_r1e-08

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.05).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-07).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.1, "L": 100.0, "T": 4.000000001, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.200011 s; original verdict match: False. Value differences: `[{"actual": 4.000000001, "expected": 4, "key": "T"}]`.

#### 279. extended_tilt_D0.1_r1e-06

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.05).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-05).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 0.1, "L": 100.0, "T": 4.0000001, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.208325 s; original verdict match: False. Value differences: `[{"actual": 4.0000001, "expected": 4, "key": "T"}]`.

#### 280. extended_tilt_D0.1_r0.0001

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.05).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.005729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 1.7763568394002505e-15], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0000000000000036, "W": 80.0}}`.

Elapsed 0.153414 s; original verdict match: True. Value differences: `[]`.

#### 281. extended_tilt_D0.1_r0.01

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(0.05).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.5729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 2.220446049250313e-16], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.165222 s; original verdict match: True. Value differences: `[]`.

#### 282. extended_tilt_D10_r1e-08

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-07).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0000001, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.199386 s; original verdict match: False. Value differences: `[{"actual": 4.0000001, "expected": 4, "key": "T"}]`.

#### 283. extended_tilt_D10_r1e-06

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),5.729577951308232e-05).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.211677 s; original verdict match: False. Value differences: `[]`.

#### 284. extended_tilt_D10_r0.0001

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.005729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 1.5543122344752192e-15], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0000000000000036, "W": 80.0}}`.

Elapsed 0.163426 s; original verdict match: True. Value differences: `[]`.

#### 285. extended_tilt_D10_r0.01

Category: `synthetic`. Scope expectation: actual non-Z cylindrical axis, also tests tiny concave-face probe.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5.0).extrude(10,both=True).rotate((0,0,0),(0,1,0),0.5729577951308232).translate((x,y,0))
    result=result.cut(tool)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.169247 s; original verdict match: True. Value differences: `[]`.

#### 286. outer_horizontal_fillet_r3

Category: `synthetic`. Convex horizontal rounds, not cross holes.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.edges("|X").fillet(1.5)
```

**Expected:** `form_violation`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 187.459 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.193279 s; original verdict match: True. Value differences: `[]`.

#### 287. outer_horizontal_fillet_r0.1

Category: `synthetic`. Convex horizontal rounds, not cross holes.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.edges("|X").fillet(0.1)
```

**Expected:** `form_violation`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.552 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.181187 s; original verdict match: True. Value differences: `[]`.

#### 288. outer_horizontal_fillet_r0.001

Category: `synthetic`. Convex horizontal rounds, not cross holes.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.edges("|X").fillet(0.001)
```

**Expected:** `form_violation`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "not one clean, valid, single-shell solid", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.175709 s; original verdict match: True. Value differences: `[]`.

#### 289. outer_horizontal_fillet_r0.0005

Category: `synthetic`. Convex horizontal rounds, not cross holes.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.edges("|X").fillet(0.0005)
```

**Expected:** `form_violation`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.159516 s; original verdict match: True. Value differences: `[]`.

#### 290. outer_horizontal_fillet_r0.0001

Category: `synthetic`. Convex horizontal rounds, not cross holes.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.edges("|X").fillet(0.0001)
```

**Expected:** `form_violation`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.166397 s; original verdict match: True. Value differences: `[]`.

#### 291. different_D_first_axis_1e-08

Category: `synthetic`. Unequal actual radii. Single D should refuse when dimension differences exceed 1e-9, rather than pick first hole.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.faces(">Z").workplane().pushPoints([(-35,-25)]).hole(10.00000001)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80, "n": 4}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.00000001, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.147427 s; original verdict match: False. Value differences: `[]`.

#### 292. different_D_first_axis_1e-07

Category: `synthetic`. Unequal actual radii. Single D should refuse when dimension differences exceed 1e-9, rather than pick first hole.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.faces(">Z").workplane().pushPoints([(-35,-25)]).hole(10.0000001)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80, "n": 4}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0000001, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.132762 s; original verdict match: False. Value differences: `[]`.

#### 293. different_D_first_axis_1e-06

Category: `synthetic`. Unequal actual radii. Single D should refuse when dimension differences exceed 1e-9, rather than pick first hole.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.faces(">Z").workplane().pushPoints([(-35,-25)]).hole(10.000001)
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80, "n": 4}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "through holes of different diameters: D is not one number", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0, "n": 4}}`.

Elapsed 0.148289 s; original verdict match: True. Value differences: `[]`.

#### 294. isolated_positions_distance_0.0009

Category: `measurement_fixture`. Direct Measurement fixture below isolates grouping from kernel grouping/probe floor.

```python
import dataclasses
from cad_spec.measure import build_and_measure
from cad_spec.l5 import observe
m=build_and_measure("import cadquery as cq\nresult=cq.Workplane('XY').box(100,80,4).faces('>Z').workplane().pushPoints([(-35,-25),(-35,25),(35,-25),(35,25)]).hole(.002)\n",strict=True)
h=m.holes[0]
m.holes=[dataclasses.replace(h,x=0,y=0),dataclasses.replace(h,x=0.0009,y=0)]
obs=observe(m)
```

**Expected:** `ok`; values `{"n": 2}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.077961 s; original verdict match: False. Value differences: `[{"actual": "ABSENT", "expected": 2, "key": "n"}]`.

**Qualification:** deliberately replaced metadata; no physical geometry claim.

#### 295. isolated_positions_distance_0.001

Category: `measurement_fixture`. Direct Measurement fixture below isolates grouping from kernel grouping/probe floor.

```python
import dataclasses
from cad_spec.measure import build_and_measure
from cad_spec.l5 import observe
m=build_and_measure("import cadquery as cq\nresult=cq.Workplane('XY').box(100,80,4).faces('>Z').workplane().pushPoints([(-35,-25),(-35,25),(35,-25),(35,25)]).hole(.002)\n",strict=True)
h=m.holes[0]
m.holes=[dataclasses.replace(h,x=0,y=0),dataclasses.replace(h,x=0.001,y=0)]
obs=observe(m)
```

**Expected:** `ok`; values `{"n": 2}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "two or more coaxial cylinders at one hole position (counterbore or stepped hole)", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.076354 s; original verdict match: False. Value differences: `[{"actual": "ABSENT", "expected": 2, "key": "n"}]`.

**Qualification:** deliberately replaced metadata; no physical geometry claim.

#### 296. isolated_positions_distance_0.001001

Category: `measurement_fixture`. Direct Measurement fixture below isolates grouping from kernel grouping/probe floor.

```python
import dataclasses
from cad_spec.measure import build_and_measure
from cad_spec.l5 import observe
m=build_and_measure("import cadquery as cq\nresult=cq.Workplane('XY').box(100,80,4).faces('>Z').workplane().pushPoints([(-35,-25),(-35,25),(35,-25),(35,25)]).hole(.002)\n",strict=True)
h=m.holes[0]
m.holes=[dataclasses.replace(h,x=0,y=0),dataclasses.replace(h,x=0.001001,y=0)]
obs=observe(m)
```

**Expected:** `ok`; values `{"n": 2}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.002, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 49.998999, "my": 40.0, "n": 2, "px": 0.001001, "py": 0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.075520 s; original verdict match: True. Value differences: `[]`.

**Qualification:** deliberately replaced metadata; no physical geometry claim.

#### 297. isolated_positions_distance_0.0011

Category: `measurement_fixture`. Direct Measurement fixture below isolates grouping from kernel grouping/probe floor.

```python
import dataclasses
from cad_spec.measure import build_and_measure
from cad_spec.l5 import observe
m=build_and_measure("import cadquery as cq\nresult=cq.Workplane('XY').box(100,80,4).faces('>Z').workplane().pushPoints([(-35,-25),(-35,25),(35,-25),(35,25)]).hole(.002)\n",strict=True)
h=m.holes[0]
m.holes=[dataclasses.replace(h,x=0,y=0),dataclasses.replace(h,x=0.0011,y=0)]
obs=observe(m)
```

**Expected:** `ok`; values `{"n": 2}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 0.002, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": 49.9989, "my": 40.0, "n": 2, "px": 0.0011, "py": 0, "rectangular": false, "symmetric": false}}`.

Elapsed 0.073794 s; original verdict match: True. Value differences: `[]`.

**Qualification:** deliberately replaced metadata; no physical geometry claim.

#### 298. small_cross_radius_1

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("YZ").circle(1).extrude(200,both=True))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.159703 s; original verdict match: True. Value differences: `[]`.

#### 299. small_cross_radius_0.001

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("YZ").circle(0.001).extrude(200,both=True))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.158118 s; original verdict match: True. Value differences: `[]`.

#### 300. small_cross_radius_0.0005

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("YZ").circle(0.0005).extrude(200,both=True))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a hole whose axis is not parallel to Z", "status": "out_of_scope", "values": {"L": 100.0, "T": 4.0, "W": 80.0}}`.

Elapsed 0.158515 s; original verdict match: True. Value differences: `[]`.

#### 301. small_cross_radius_0.0001

Category: `synthetic`. 

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.cut(cq.Workplane("YZ").circle(0.0001).extrude(200,both=True))
```

**Expected:** `out_of_scope`; values `{"L": 100, "T": 4, "W": 80}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70.0, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.146579 s; original verdict match: False. Value differences: `[]`.

#### 302. centred_nonrect_1e-08

Category: `synthetic`. Centroid zero; mirror X breaks beyond EPS_FORM; rectangular checks extrema separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25.00000001), (-35, 25.00000001), (35, -24.99999999), (35, 24.99999999)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 14.99999999, "n": 4, "px": 70, "py": 50.00000002, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 14.99999999, "n": 4, "px": 70.0, "py": 50.00000002, "rectangular": true, "symmetric": true}}`.

Elapsed 0.068620 s; original verdict match: True. Value differences: `[]`.

#### 303. symmetric_pitch_1e-08

Category: `synthetic`. Centred mirror symmetry control while pitch/margins change.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35.00000001, -25), (-35.00000001, 25), (35.00000001, -25), (35.00000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.99999999, "my": 15.0, "n": 4, "px": 70.00000002, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.99999999, "my": 15.0, "n": 4, "px": 70.00000002, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.069921 s; original verdict match: True. Value differences: `[]`.

#### 304. centred_nonrect_9e-08

Category: `synthetic`. Centroid zero; mirror X breaks beyond EPS_FORM; rectangular checks extrema separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25.00000009), (-35, 25.00000009), (35, -24.99999991), (35, 24.99999991)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 14.99999991, "n": 4, "px": 70, "py": 50.00000018, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 14.99999991, "n": 4, "px": 70.0, "py": 50.00000018, "rectangular": false, "symmetric": false}}`.

Elapsed 0.070026 s; original verdict match: True. Value differences: `[]`.

#### 305. symmetric_pitch_9e-08

Category: `synthetic`. Centred mirror symmetry control while pitch/margins change.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35.00000009, -25), (-35.00000009, 25), (35.00000009, -25), (35.00000009, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.99999991, "my": 15.0, "n": 4, "px": 70.00000018, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.99999991, "my": 15.0, "n": 4, "px": 70.00000018, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.071416 s; original verdict match: True. Value differences: `[]`.

#### 306. centred_nonrect_1e-07

Category: `synthetic`. Centroid zero; mirror X breaks beyond EPS_FORM; rectangular checks extrema separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25.0000001), (-35, 25.0000001), (35, -24.9999999), (35, 24.9999999)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 14.999999899999999, "n": 4, "px": 70, "py": 50.0000002, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 14.999999899999999, "n": 4, "px": 70.0, "py": 50.0000002, "rectangular": false, "symmetric": false}}`.

Elapsed 0.069394 s; original verdict match: True. Value differences: `[]`.

#### 307. symmetric_pitch_1e-07

Category: `synthetic`. Centred mirror symmetry control while pitch/margins change.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35.0000001, -25), (-35.0000001, 25), (35.0000001, -25), (35.0000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.999999899999999, "my": 15.0, "n": 4, "px": 70.0000002, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.999999899999999, "my": 15.0, "n": 4, "px": 70.0000002, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.069656 s; original verdict match: True. Value differences: `[]`.

#### 308. centred_nonrect_1.1e-07

Category: `synthetic`. Centroid zero; mirror X breaks beyond EPS_FORM; rectangular checks extrema separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25.00000011), (-35, 25.00000011), (35, -24.99999989), (35, 24.99999989)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 14.999999890000002, "n": 4, "px": 70, "py": 50.00000022, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 14.999999890000002, "n": 4, "px": 70.0, "py": 50.00000022, "rectangular": false, "symmetric": false}}`.

Elapsed 0.067328 s; original verdict match: True. Value differences: `[]`.

#### 309. symmetric_pitch_1.1e-07

Category: `synthetic`. Centred mirror symmetry control while pitch/margins change.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35.00000011, -25), (-35.00000011, 25), (35.00000011, -25), (35.00000011, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.999999889999998, "my": 15.0, "n": 4, "px": 70.00000022, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.999999889999998, "my": 15.0, "n": 4, "px": 70.00000022, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.067268 s; original verdict match: True. Value differences: `[]`.

#### 310. centred_nonrect_1e-06

Category: `synthetic`. Centroid zero; mirror X breaks beyond EPS_FORM; rectangular checks extrema separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25.000001), (-35, 25.000001), (35, -24.999999), (35, 24.999999)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 14.999998999999999, "n": 4, "px": 70, "py": 50.000002, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 15.0, "my": 14.999998999999999, "n": 4, "px": 70.0, "py": 50.000002, "rectangular": false, "symmetric": false}}`.

Elapsed 0.066677 s; original verdict match: True. Value differences: `[]`.

#### 311. symmetric_pitch_1e-06

Category: `synthetic`. Centred mirror symmetry control while pitch/margins change.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35.000001, -25), (-35.000001, 25), (35.000001, -25), (35.000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 14.999999000000003, "my": 15.0, "n": 4, "px": 70.000002, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 14.999999000000003, "my": 15.0, "n": 4, "px": 70.000002, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.066039 s; original verdict match: True. Value differences: `[]`.

#### 312. fused_bottom_skin_8e-08

Category: `synthetic`. Union of a skin closing all hole bottoms; at kernel precision the union may fail or erase it.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.union(cq.Workplane("XY").box(100,80,8e-08).translate((0,0,-1.99999996)))
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"error": "BuildError('execution failed [raised in cadquery: Solid.makeBox]: Standard_DomainError: ')", "status": "build_error"}`.

Elapsed 0.011653 s; original verdict match: False. Value differences: `[{"actual": "ABSENT", "expected": 100, "key": "L"}, {"actual": "ABSENT", "expected": 80, "key": "W"}, {"actual": "ABSENT", "expected": 4, "key": "T"}, {"actual": "ABSENT", "expected": 4, "key": "n"}, {"actual": "ABSENT", "expected": 10, "key": "D"}, {"actual": "ABSENT", "expected": 15.0, "key": "mx"}, {"actual": "ABSENT", "expected": 15.0, "key": "my"}, {"actual": "ABSENT", "expected": 70, "key": "px"}, {"actual": "ABSENT", "expected": 50, "key": "py"}, {"actual": "ABSENT", "expected": true, "key": "rectangular"}, {"actual": "ABSENT", "expected": true, "key": "centered"}, {"actual": "ABSENT", "expected": true, "key": "symmetric"}]`.

#### 313. fused_bottom_skin_1e-07

Category: `synthetic`. Union of a skin closing all hole bottoms; at kernel precision the union may fail or erase it.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.union(cq.Workplane("XY").box(100,80,1e-07).translate((0,0,-1.99999995)))
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 15.0, "my": 15.0, "n": 4, "px": 70, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"error": "BuildError('execution failed [raised in cadquery: Solid.makeBox]: Standard_DomainError: ')", "status": "build_error"}`.

Elapsed 0.011689 s; original verdict match: False. Value differences: `[{"actual": "ABSENT", "expected": 100, "key": "L"}, {"actual": "ABSENT", "expected": 80, "key": "W"}, {"actual": "ABSENT", "expected": 4, "key": "T"}, {"actual": "ABSENT", "expected": 4, "key": "n"}, {"actual": "ABSENT", "expected": 10, "key": "D"}, {"actual": "ABSENT", "expected": 15.0, "key": "mx"}, {"actual": "ABSENT", "expected": 15.0, "key": "my"}, {"actual": "ABSENT", "expected": 70, "key": "px"}, {"actual": "ABSENT", "expected": 50, "key": "py"}, {"actual": "ABSENT", "expected": true, "key": "rectangular"}, {"actual": "ABSENT", "expected": true, "key": "centered"}, {"actual": "ABSENT", "expected": true, "key": "symmetric"}]`.

#### 314. fused_bottom_skin_1.2e-07

Category: `synthetic`. Union of a skin closing all hole bottoms; at kernel precision the union may fail or erase it.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.union(cq.Workplane("XY").box(100,80,1.2e-07).translate((0,0,-1.99999994)))
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"error": "BuildError('shape could not be measured: Bnd_Box is void')", "status": "build_error"}`.

Elapsed 0.023031 s; original verdict match: False. Value differences: `[{"actual": "ABSENT", "expected": 100, "key": "L"}, {"actual": "ABSENT", "expected": 80, "key": "W"}, {"actual": "ABSENT", "expected": 4, "key": "T"}, {"actual": "ABSENT", "expected": 0, "key": "n"}, {"actual": "ABSENT", "expected": null, "key": "D"}, {"actual": "ABSENT", "expected": null, "key": "mx"}, {"actual": "ABSENT", "expected": null, "key": "my"}, {"actual": "ABSENT", "expected": null, "key": "px"}, {"actual": "ABSENT", "expected": null, "key": "py"}, {"actual": "ABSENT", "expected": false, "key": "rectangular"}, {"actual": "ABSENT", "expected": false, "key": "centered"}, {"actual": "ABSENT", "expected": false, "key": "symmetric"}]`.

#### 315. fused_bottom_skin_1e-06

Category: `synthetic`. Union of a skin closing all hole bottoms; at kernel precision the union may fail or erase it.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.union(cq.Workplane("XY").box(100,80,1e-06).translate((0,0,-1.9999995)))
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.101386 s; original verdict match: True. Value differences: `[]`.

#### 316. fused_bottom_skin_1e-05

Category: `synthetic`. Union of a skin closing all hole bottoms; at kernel precision the union may fail or erase it.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-35, -25), (-35, 25), (35, -25), (35, 25)]).hole(10)
result=result.union(cq.Workplane("XY").box(100,80,1e-05).translate((0,0,-1.999995)))
```

**Expected:** `form_violation`; values `{"D": null, "L": 100, "T": 4, "W": 80, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.003 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.101196 s; original verdict match: True. Value differences: `[]`.

#### 317. solid_no_holes_XY

Category: `synthetic`. Plain axis-aligned boxes; no hole has a D or pitch.

```python
import cadquery as cq
result=cq.Workplane("XY").rect(10,10).extrude(2)
```

**Expected:** `ok`; values `{"D": null, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 1.0], "reason": "", "status": "ok", "values": {"D": null, "L": 10.0, "T": 2.0, "W": 10.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.016335 s; original verdict match: True. Value differences: `[]`.

#### 318. solid_no_holes_XZ

Category: `synthetic`. Plain axis-aligned boxes; no hole has a D or pitch.

```python
import cadquery as cq
result=cq.Workplane("XZ").rect(10,10).extrude(2)
```

**Expected:** `ok`; values `{"D": null, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [0.0, -1.0, 0.0], "reason": "", "status": "ok", "values": {"D": null, "L": 10.0, "T": 10.0, "W": 2.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.014833 s; original verdict match: True. Value differences: `[]`.

#### 319. solid_no_holes_YZ

Category: `synthetic`. Plain axis-aligned boxes; no hole has a D or pitch.

```python
import cadquery as cq
result=cq.Workplane("YZ").rect(10,10).extrude(2)
```

**Expected:** `ok`; values `{"D": null, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}`.

**Actual, fact:** `{"centre": [1.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": null, "L": 2.0, "T": 10.0, "W": 10.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.015704 s; original verdict match: True. Value differences: `[]`.

#### 320. solid_count_fixture_0

Category: `measurement_fixture`. Direct map fixture, no geometry execution.

```python
import dataclasses
from cad_spec.measure import build_and_measure
from cad_spec.l5 import observe
m=build_and_measure("import cadquery as cq\nresult=cq.Workplane('XY').box(100,80,4)\n",strict=True)
obs=observe(dataclasses.replace(m,solid_count=0))
```

**Expected:** `not_single_solid`; values `{}`.

**Actual, fact:** `{"centre": null, "reason": "0 solids, exactly one is required", "status": "not_single_solid", "values": {}}`.

Elapsed 0.000000 s; original verdict match: True. Value differences: `[]`.

**Qualification:** deliberately replaced metadata; no physical geometry claim.

#### 321. solid_count_fixture_2

Category: `measurement_fixture`. Direct map fixture, no geometry execution.

```python
import dataclasses
from cad_spec.measure import build_and_measure
from cad_spec.l5 import observe
m=build_and_measure("import cadquery as cq\nresult=cq.Workplane('XY').box(100,80,4)\n",strict=True)
obs=observe(dataclasses.replace(m,solid_count=2))
```

**Expected:** `not_single_solid`; values `{}`.

**Actual, fact:** `{"centre": null, "reason": "2 solids, exactly one is required", "status": "not_single_solid", "values": {}}`.

Elapsed 0.000000 s; original verdict match: True. Value differences: `[]`.

**Qualification:** deliberately replaced metadata; no physical geometry claim.

#### 322. solid_count_fixture_3

Category: `measurement_fixture`. Direct map fixture, no geometry execution.

```python
import dataclasses
from cad_spec.measure import build_and_measure
from cad_spec.l5 import observe
m=build_and_measure("import cadquery as cq\nresult=cq.Workplane('XY').box(100,80,4)\n",strict=True)
obs=observe(dataclasses.replace(m,solid_count=3))
```

**Expected:** `not_single_solid`; values `{}`.

**Actual, fact:** `{"centre": null, "reason": "3 solids, exactly one is required", "status": "not_single_solid", "values": {}}`.

Elapsed 0.000000 s; original verdict match: True. Value differences: `[]`.

**Qualification:** deliberately replaced metadata; no physical geometry claim.

#### 323. near_breakout_1e-06

Category: `taxonomy`. Geometric axes/radii still known. Family F1 must reject mx < D/2; whether partial wall is a form failure is reviewed separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-45.000001, -25), (-45.000001, 25), (45.000001, -25), (45.000001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 4.9999990000000025, "my": 15.0, "n": 4, "px": 90.000002, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.00000000000003, "T": 4.0, "W": 80.0, "centered": true, "mx": 4.999999000000017, "my": 15.0, "n": 4, "px": 90.000002, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 1.692368 s; original verdict match: True. Value differences: `[]`.

#### 324. near_breakout_0.0001

Category: `taxonomy`. Geometric axes/radii still known. Family F1 must reject mx < D/2; whether partial wall is a form failure is reviewed separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-45.0001, -25), (-45.0001, 25), (45.0001, -25), (45.0001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 4.999899999999997, "my": 15.0, "n": 4, "px": 90.0002, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.00000000000013, "T": 4.0, "W": 80.0, "centered": true, "mx": 4.999900000000061, "my": 15.0, "n": 4, "px": 90.0002, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.094796 s; original verdict match: True. Value differences: `[]`.

#### 325. near_breakout_0.001

Category: `taxonomy`. Geometric axes/radii still known. Family F1 must reject mx < D/2; whether partial wall is a form failure is reviewed separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-45.001, -25), (-45.001, 25), (45.001, -25), (45.001, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 4.999000000000002, "my": 15.0, "n": 4, "px": 90.002, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.00000000000001, "T": 4.0, "W": 80.0, "centered": true, "mx": 4.999000000000009, "my": 15.0, "n": 4, "px": 90.002, "py": 50.0, "rectangular": true, "symmetric": true}}`.

Elapsed 0.091507 s; original verdict match: True. Value differences: `[]`.

#### 326. near_breakout_0.01

Category: `taxonomy`. Geometric axes/radii still known. Family F1 must reject mx < D/2; whether partial wall is a form failure is reviewed separately.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-45.01, -25), (-45.01, 25), (45.01, -25), (45.01, 25)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 4.990000000000002, "my": 15.0, "n": 4, "px": 90.02, "py": 50, "rectangular": true, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 1253.372 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.00000000000004, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.048110 s; original verdict match: False. Value differences: `[{"actual": 0, "expected": 4, "key": "n"}, {"actual": null, "expected": 10, "key": "D"}, {"actual": null, "expected": 4.990000000000002, "key": "mx"}, {"actual": null, "expected": 15.0, "key": "my"}, {"actual": null, "expected": 90.02, "key": "px"}, {"actual": null, "expected": 50, "key": "py"}, {"actual": false, "expected": true, "key": "rectangular"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

**Qualification:** the 99% wall-completeness cutoff removes clipped candidates. This is coverage discontinuity, not a wrong value returned with ok.

#### 327. near_overlap_1e-06

Category: `taxonomy`. Geometric axes/radii still known. Family F2 must reject axis separation < D; map alone is not a complete compliance gate.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-4.9999995, 0), (4.9999995, 0)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 45.0000005, "my": 40.0, "n": 2, "px": 9.999999, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 45.0000005, "my": 40.0, "n": 2, "px": 9.999999, "py": 0.0, "rectangular": false, "symmetric": true}}`.

Elapsed 0.056575 s; original verdict match: True. Value differences: `[]`.

#### 328. near_overlap_0.0001

Category: `taxonomy`. Geometric axes/radii still known. Family F2 must reject axis separation < D; map alone is not a complete compliance gate.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-4.99995, 0), (4.99995, 0)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 45.00005, "my": 40.0, "n": 2, "px": 9.9999, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 45.00005, "my": 40.0, "n": 2, "px": 9.9999, "py": 0.0, "rectangular": false, "symmetric": true}}`.

Elapsed 0.054335 s; original verdict match: True. Value differences: `[]`.

#### 329. near_overlap_0.001

Category: `taxonomy`. Geometric axes/radii still known. Family F2 must reject axis separation < D; map alone is not a complete compliance gate.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-4.9995, 0), (4.9995, 0)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 45.0005, "my": 40.0, "n": 2, "px": 9.999, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 10.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 45.0005, "my": 40.0, "n": 2, "px": 9.999, "py": 0.0, "rectangular": false, "symmetric": true}}`.

Elapsed 0.055780 s; original verdict match: True. Value differences: `[]`.

#### 330. near_overlap_0.01

Category: `taxonomy`. Geometric axes/radii still known. Family F2 must reject axis separation < D; map alone is not a complete compliance gate.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-4.995, 0), (4.995, 0)]).hole(10)
```

**Expected:** `ok`; values `{"D": 10, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 45.005, "my": 40.0, "n": 2, "px": 9.99, "py": 0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 626.736 mm3 missing outside a 0.005 mm band", "status": "form_violation", "values": {"D": null, "L": 100.0, "T": 4.0, "W": 80.0, "centered": false, "mx": null, "my": null, "n": 0, "px": null, "py": null, "rectangular": false, "symmetric": false}}`.

Elapsed 0.034025 s; original verdict match: False. Value differences: `[{"actual": 0, "expected": 2, "key": "n"}, {"actual": null, "expected": 10, "key": "D"}, {"actual": null, "expected": 45.005, "key": "mx"}, {"actual": null, "expected": 40.0, "key": "my"}, {"actual": null, "expected": 9.99, "key": "px"}, {"actual": null, "expected": 0, "key": "py"}, {"actual": false, "expected": true, "key": "centered"}, {"actual": false, "expected": true, "key": "symmetric"}]`.

**Qualification:** the 99% wall-completeness cutoff removes clipped candidates. This is coverage discontinuity, not a wrong value returned with ok.

#### 331. stress_count_20

Category: `stress`. Disjoint equal-diameter holes; bounded 10-second default answer budget, no deliberately unbounded workload.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-40.0, -30.0), (-40.0, -10.0), (-40.0, 10.0), (-40.0, 30.0), (-20.0, -30.0), (-20.0, -10.0), (-20.0, 10.0), (-20.0, 30.0), (0.0, -30.0), (0.0, -10.0), (0.0, 10.0), (0.0, 30.0), (20.0, -30.0), (20.0, -10.0), (20.0, 10.0), (20.0, 30.0), (40.0, -30.0), (40.0, -10.0), (40.0, 10.0), (40.0, 30.0)]).hole(1)
```

**Expected:** `ok`; values `{"D": 1, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 10.0, "my": 10.0, "n": 20, "px": 80.0, "py": 60.0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 1.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 10.0, "my": 10.0, "n": 20, "px": 80.0, "py": 60.0, "rectangular": false, "symmetric": true}}`.

Elapsed 0.391884 s; original verdict match: True. Value differences: `[]`.

#### 332. stress_count_50

Category: `stress`. Disjoint equal-diameter holes; bounded 10-second default answer budget, no deliberately unbounded workload.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-40.0, -30.0), (-40.0, -15.0), (-40.0, 0.0), (-40.0, 15.0), (-40.0, 30.0), (-31.11111111111111, -30.0), (-31.11111111111111, -15.0), (-31.11111111111111, 0.0), (-31.11111111111111, 15.0), (-31.11111111111111, 30.0), (-22.22222222222222, -30.0), (-22.22222222222222, -15.0), (-22.22222222222222, 0.0), (-22.22222222222222, 15.0), (-22.22222222222222, 30.0), (-13.333333333333332, -30.0), (-13.333333333333332, -15.0), (-13.333333333333332, 0.0), (-13.333333333333332, 15.0), (-13.333333333333332, 30.0), (-4.444444444444443, -30.0), (-4.444444444444443, -15.0), (-4.444444444444443, 0.0), (-4.444444444444443, 15.0), (-4.444444444444443, 30.0), (4.444444444444443, -30.0), (4.444444444444443, -15.0), (4.444444444444443, 0.0), (4.444444444444443, 15.0), (4.444444444444443, 30.0), (13.333333333333336, -30.0), (13.333333333333336, -15.0), (13.333333333333336, 0.0), (13.333333333333336, 15.0), (13.333333333333336, 30.0), (22.22222222222222, -30.0), (22.22222222222222, -15.0), (22.22222222222222, 0.0), (22.22222222222222, 15.0), (22.22222222222222, 30.0), (31.111111111111114, -30.0), (31.111111111111114, -15.0), (31.111111111111114, 0.0), (31.111111111111114, 15.0), (31.111111111111114, 30.0), (40.0, -30.0), (40.0, -15.0), (40.0, 0.0), (40.0, 15.0), (40.0, 30.0)]).hole(1)
```

**Expected:** `ok`; values `{"D": 1, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 10.0, "my": 10.0, "n": 50, "px": 80.0, "py": 60.0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 1.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 10.0, "my": 10.0, "n": 50, "px": 80.0, "py": 60.0, "rectangular": false, "symmetric": true}}`.

Elapsed 2.039397 s; original verdict match: True. Value differences: `[]`.

#### 333. stress_count_100

Category: `stress`. Disjoint equal-diameter holes; bounded 10-second default answer budget, no deliberately unbounded workload.

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-40.0, -30.0), (-40.0, -23.333333333333332), (-40.0, -16.666666666666664), (-40.0, -10.0), (-40.0, -3.333333333333332), (-40.0, 3.3333333333333357), (-40.0, 10.0), (-40.0, 16.666666666666664), (-40.0, 23.333333333333336), (-40.0, 30.0), (-31.11111111111111, -30.0), (-31.11111111111111, -23.333333333333332), (-31.11111111111111, -16.666666666666664), (-31.11111111111111, -10.0), (-31.11111111111111, -3.333333333333332), (-31.11111111111111, 3.3333333333333357), (-31.11111111111111, 10.0), (-31.11111111111111, 16.666666666666664), (-31.11111111111111, 23.333333333333336), (-31.11111111111111, 30.0), (-22.22222222222222, -30.0), (-22.22222222222222, -23.333333333333332), (-22.22222222222222, -16.666666666666664), (-22.22222222222222, -10.0), (-22.22222222222222, -3.333333333333332), (-22.22222222222222, 3.3333333333333357), (-22.22222222222222, 10.0), (-22.22222222222222, 16.666666666666664), (-22.22222222222222, 23.333333333333336), (-22.22222222222222, 30.0), (-13.333333333333332, -30.0), (-13.333333333333332, -23.333333333333332), (-13.333333333333332, -16.666666666666664), (-13.333333333333332, -10.0), (-13.333333333333332, -3.333333333333332), (-13.333333333333332, 3.3333333333333357), (-13.333333333333332, 10.0), (-13.333333333333332, 16.666666666666664), (-13.333333333333332, 23.333333333333336), (-13.333333333333332, 30.0), (-4.444444444444443, -30.0), (-4.444444444444443, -23.333333333333332), (-4.444444444444443, -16.666666666666664), (-4.444444444444443, -10.0), (-4.444444444444443, -3.333333333333332), (-4.444444444444443, 3.3333333333333357), (-4.444444444444443, 10.0), (-4.444444444444443, 16.666666666666664), (-4.444444444444443, 23.333333333333336), (-4.444444444444443, 30.0), (4.444444444444443, -30.0), (4.444444444444443, -23.333333333333332), (4.444444444444443, -16.666666666666664), (4.444444444444443, -10.0), (4.444444444444443, -3.333333333333332), (4.444444444444443, 3.3333333333333357), (4.444444444444443, 10.0), (4.444444444444443, 16.666666666666664), (4.444444444444443, 23.333333333333336), (4.444444444444443, 30.0), (13.333333333333336, -30.0), (13.333333333333336, -23.333333333333332), (13.333333333333336, -16.666666666666664), (13.333333333333336, -10.0), (13.333333333333336, -3.333333333333332), (13.333333333333336, 3.3333333333333357), (13.333333333333336, 10.0), (13.333333333333336, 16.666666666666664), (13.333333333333336, 23.333333333333336), (13.333333333333336, 30.0), (22.22222222222222, -30.0), (22.22222222222222, -23.333333333333332), (22.22222222222222, -16.666666666666664), (22.22222222222222, -10.0), (22.22222222222222, -3.333333333333332), (22.22222222222222, 3.3333333333333357), (22.22222222222222, 10.0), (22.22222222222222, 16.666666666666664), (22.22222222222222, 23.333333333333336), (22.22222222222222, 30.0), (31.111111111111114, -30.0), (31.111111111111114, -23.333333333333332), (31.111111111111114, -16.666666666666664), (31.111111111111114, -10.0), (31.111111111111114, -3.333333333333332), (31.111111111111114, 3.3333333333333357), (31.111111111111114, 10.0), (31.111111111111114, 16.666666666666664), (31.111111111111114, 23.333333333333336), (31.111111111111114, 30.0), (40.0, -30.0), (40.0, -23.333333333333332), (40.0, -16.666666666666664), (40.0, -10.0), (40.0, -3.333333333333332), (40.0, 3.3333333333333357), (40.0, 10.0), (40.0, 16.666666666666664), (40.0, 23.333333333333336), (40.0, 30.0)]).hole(1)
```

**Expected:** `ok`; values `{"D": 1, "L": 100, "T": 4, "W": 80, "centered": true, "mx": 10.0, "my": 10.0, "n": 100, "px": 80.0, "py": 60.0, "rectangular": false, "symmetric": true}`.

**Actual, fact:** `{"centre": [0.0, 0.0, 0.0], "reason": "", "status": "ok", "values": {"D": 1.0, "L": 100.0, "T": 4.0, "W": 80.0, "centered": true, "mx": 10.0, "my": 10.0, "n": 100, "px": 80.0, "py": 60.0, "rectangular": false, "symmetric": true}}`.

Elapsed 8.209699 s; original verdict match: True. Value differences: `[]`.

## Assessment of decisions, design compliance and code

### Task 4: every M1 decision

| Decision | Opinion and confidence | Evidence |
|---|---|---|
| Position is not a contract variable | Agree, high | All translated style/spec controls preserve every variable; centre changes as intended. |
| L along X, W along Y | Agree, high, with numerical qualification | 90/270 swap dimensions, margins and pitches; 180 preserves them. A 1e-10-radian rotation remains within epsilon, so "any other angle fails" is not literal. |
| n counts uninterrupted open Z through holes, including extra holes | Agree with policy, high; implementation incomplete | 0,1,2,3,5,6 and arrays are counted. Blind holes are excluded. Rounded keys/probe floor can merge or miss true axes. Through/open logic also inherits gap/volume thresholds. |
| No holes means None, never zero | Agree, high | Three plain box orientations and the no-hole plate reproduce this. M3 must define predicates on None. |
| Counterbores/steps are out_of_scope | Agree, high; fix implementation | Large steps refuse; actual radius steps 1e-5/1e-6 become form_violation with chosen D. Erased sub-resolution steps are not defects. |
| Different diameters are out_of_scope | Agree, high on policy, moderate on epsilon interpretation | 1e-6 refuses; actual 1e-8/1e-7 variations pass, selecting first-axis D. Use dimensional slack or explicitly amend one-D semantics. |
| Tilt/cross holes are out_of_scope; new concave detector | Agree with need, high; detector needs fixes | Ordinary cross bores and 1e-4/1e-2 tilts refuse. 1e-6 is form_violation, 1e-8 passes with wrong mx, radius-1e-4 cross bore is missed. |
| Spline surfaces deliberately fail form | Agree, high | NURBS control reproduces refusal and 2e-7 box expansion. Recorded analytic-recovery false acceptance justifies coverage loss. |
| Reuse strict measurement, no remeasurement | Agree with principle, high; data are insufficient | Ordinary styles match and R9 is shared. Raw multi-radius/axis information is lost; midpoint centres differ from top centres. Add trusted metadata in the existing face pass. |
| Four verdicts; build errors belong to G1 | Agree, high | Multiple/direct zero-solid fixtures refuse. Empty/no-result fails before observe. Strict scope faults presently escape as ValueError. |

**Pocket/slot deviation, opinion, high confidence.** I choose `form_violation` for an independent pocket or slot when envelope and original through-hole variables remain unambiguous. Rectangular and round pocket/slot probes preserve the original variables and fail R9. This follows amendment 1 and avoids feature taxonomy. It is conditional: a pocket intersecting a bore or an opening that destroys a cylindrical wall can make variables ambiguous and should be out_of_scope. A round blind pocket is not another through hole. "All variables measured" is too broad for every form violation: a boss changes full-solid thickness and empties the through set; splines and remote loose faces return unsuitable plate numbers. Every non-ok verdict must stop G3, but accurate failure classification still matters.

### Task 5: section 7.1, as amended

| Variable/rule | Implementation | Difference, limitation or missing original test |
|---|---|---|
| L, W, T | Kernel AABB of supplied shape | Present, verified on ordinary controls. Tiny tilted trimmed faces pad T; loose geometry expands the compound box. |
| Z through-hole rule | Existing analytic detector, open flag, one merged segment, endpoints within 1e-7 | AXIS_TOL=1e-6 admits tilt; 99% cylinder area admits partial walls; interval gap merge=1e-4 and open probe=1e-6 mm3 are extra inherited rules. Not solely a 1e-7 endpoint test. Original gate lacks these boundaries. |
| n | Number of retained groups | First detector rounds axes to 0.001; map adds Euclidean grouping at 0.001. Original fifth-hole case exists, but 1,2,6, very small holes and grouping boundaries do not. |
| D | First through group's unrounded diameter | Real steps can already be merged; different-D scope uses form rather than dimension epsilon. Original gate only covers large diameter differences and counterbores. |
| Hole centre at top plane | Detector uses mid-thickness | Different, masked by exact-Z controls. No top-intersection datum reaches L5; R1 exposes it. |
| mx, my | Minimum signed distances to AABB X/Y side planes | Correct for contained axis-aligned family; wrong on accepted tiny tilt. For form-failed rotated/filleted parts, these are box diagnostics rather than actual outer-face margins. |
| px, py | max coordinate minus min coordinate | Correct four-corner family. For multi-column/nonrectangular patterns means total extent, not adjacent pitch. That extension is unspecified. Original tests do not cover nonuniform multi-column pitch. |
| centered | Arithmetic centre centroid, coordinate-wise 1e-7 | Present. Original suite lacks epsilon/cancellation boundaries. Coordinate-wise versus Euclidean epsilon is unspecified. |
| symmetric | Reflected centres exist about both midplanes | Present. Matching is existential, not bijective; original suite lacks epsilon/duplicate cases. Ordinary distinct axes make this safe. |
| rectangular | Exactly four centres matching min/max corners | Present extra family diagnostic. Original large moved-hole case exists, but no boundary or degenerate-corner test. |
| Scope refusal | Off-axis and grouped-cylinder checks before form | Incomplete for tiny tilts/cross bores, microsteps, connected offset steps and strict-classifier faults. |
| Unrequested features | Shared R9, plus clean/valid/shell/loose checks | Ordinary features covered. Pocket/slot deviation sensible with measurable-variable qualification. Bosses/internal cavities/remote loose faces added here. |
| Zero/multiple solids | Direct observe returns not_single_solid | Multiple originally tested. Zero reaches G1 BuildError through build API; direct-zero behavior originally untested. |
| Tolerance reuse | EPS_DIM from current scorer; EPS_FORM from measurement | Present identity test. EPS_DIM is exported but unused internally. Future scorer defaults can silently change L5 constants. |

**Fact.** No required dictionary variable is missing on ok/no-hole results. Out-of-scope deliberately returns only earlier fields. Missing information is top-plane centres and raw cylinder scope metadata. Many original adversarial expectations assert only subsets, so 27/27 does not mean every variable was checked on every part.

**M2/M3 implications, inferences and opinions, high confidence unless stated.**

- Pin observation/scorer/tolerance versions in compiled artifacts. Add L5-only trusted metadata without altering recorded 0.5.0/0.4.0 scoring fields.
- Define pitch outside the four-corner family before allowing such compiler states. px=L-2mx holds for a symmetric witness; shifted patterns correctly violate that algebra. Compiler identities must be conditional on family constraints, and G3 must check required rectangular/centered/symmetric predicates.
- Enforce named containment/non-overlap rules F1/F2, not only observation.status. Near breakouts and overlaps of 1e-6, 1e-4 and 1e-3 return ok with accurate margins/pitches. A breakout can retain n=4 and all pattern booleans. This is not another wrong observation; it proves ok is not contract/family compliance. Symmetric-four-corner scalars suffice for F1/F2; general patterns would need per-hole axes or explicit restriction.
- Define None/absent-key handling and stop G3 on every non-ok verdict before predicates. `.measurable` includes form_violation even when spline/loose geometry has untrustworthy numbers. Treat such values as diagnostic, not evidence for passing a contract.
- Intent rebuilds multiply measurement cost. The 100-hole synthetic part takes 8.2 s. Retain build and trusted-measurement timeouts; distinguish classifier failure from model rejection. These are integration requirements, not architectural changes. No M2 compiler or M3 grader was executed here.

### Task 6: code review

**observation.py, facts and opinions.** Ordinary min/max dimensions, margins, extents and centroids are straightforward and verified. Scope-first order handles common ambiguity well. Hidden assumptions include strict provenance, complete analytic cylinder candidates, lossless grouping and the four-corner family for pitch. `_positions` uses the first member of each group, not transitive/equivalence-class grouping, so chained A-B-C positions can partition differently with order. Physical microholes first encounter independent rounded keys; changing `_SAME_AXIS_MM` alone cannot restore identity. `_positions` and symmetry scans are quadratic. The frozen Observation contains a mutable dictionary, so it is not deeply immutable. These are moderate-confidence future maintenance concerns rather than observed ordinary failures.

**form_verdict, facts and opinion.** A faithful extraction of former R9: same missing-data refusal, same conjunction of conformance/boundary/residuals, same details. It intentionally excludes validity/single-shell/loose checks, already handled by gates and observe. Unavailable form input fails closed. NaN residuals do not pass comparisons; corrupted measurement objects are outside the trusted API. Sharing R9 is a sound design. The new strict detector shares the form-check try block; its failure sets shape_error after form/boundary results were populated, so scoring may still work while observe raises. Explicit strict provenance and independent scope diagnostics would improve this path.

**_off_axis_concave_faces, facts and opinion.** It improves ordinary obliquely trimmed-hole coverage compared with the old closed-cylinder area diagnostic. The angular cutoff hides tiny tilts and the probe floor crosses small bores. Its U/V rectangle midpoint is not guaranteed inside the trimmed face domain; one probe and treating OUT/ON/UNKNOWN alike cannot establish concavity for every topology. The trimmed-domain issue is a source-based inference, moderate confidence, not a separately reproduced false acceptance. Use a point inside the trimmed face for generality, bound the inset and report uncertainty explicitly. Preserve historical scored classification separately.

**Linux/Windows, facts and inferences.** New routines use standard math and OCP APIs, without OS-specific subprocess or filesystem logic. Kernel precision, face ordering/parameterization, rounding ties, serialization and OCP versions can affect boundary outcomes. Windows reuse constructs/measures in the worker; Linux fork transports BRep bytes to the trusted parent for measurement. This difference predates M1. The optional dataclass field is pickleable, but older stored Measurements objects have no explicit migration. Source and CI inspection support ordinary portability, not proof of Linux behavior. The 27-part script is wired to pinned Linux CI; Windows/Linux matrix pytest runs the eight fast observation tests.

## What could not be verified

**Facts and limits, high confidence.** No local Linux, Python 3.11 or other CadQuery/OCP-version execution was performed. This Windows venv exercised reuse mode; Linux fork isolation and measurement were reviewed in source only. CI configuration is not evidence that a CI run passed.

**Fact.** Proposed diffs were not applied, integrated, type-checked or tested. Their score preservation and cross-platform behavior need validation after implementation. R2 is an explicit sketch. Timing is local observed latency plus a small balanced warm benchmark, not a throughput study.

**Fact.** No naturally failing strict off-axis classifier was found. Its error path was fault-injected. Kernel-erased microscopic steps and failed skin fusions cannot verify geometry absent from the actual result. No deliberately unbounded workload was run.

**Inference, moderate confidence.** This finite corpus does not prove correctness for arbitrary invalid/non-manifold BReps, huge coordinates, all stored tolerances, every trimmed-face parameterization or all timeout boundaries. Evaluation answers were used only for scorer equivalence/timing, never threshold or geometry tuning.

**Fact.** This Markdown includes every additional part's code, expectations and actual output, all findings, proposed diffs, commands and comparison results. Supporting scripts/logs/JSON remain under the same output directory for reproducibility. Final tracked diff and git status are clean; no tracked edits, commits or pushes were made.
