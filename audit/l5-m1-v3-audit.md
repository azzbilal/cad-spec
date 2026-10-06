Opinion: Change first before merging M1.  
Fact: All four supplied checks pass, including the 58-case observation gate.  
Fact: The 333-case replay has no wrong value in an ok result; all 180 controls pass to 1e-9 mm.  
Fact: A diagonal 1.3e-12 rad bore still returns ok above the stated 1e-12 rad angular limit.  
Opinion: Correct that angular boundary and narrow the document claims; R2 to R5 are resolved for their original findings.

# L5 M1 verification audit, 7 October 2026

**Fact.** Local checkout `C:/Users/bgare/dev/cad-spec-audit`, branch `feat/l5-m1-observation`, HEAD `9c192157b7064fe8f6e7d17c6c7e70b2ba1a8f40`; main `1fb9a5139fabc884e297fb3538f7a5f6cbcb0acc`. Used the existing Python 3.12 virtual environment at `C:/Users/bgare/dev/cad-spec-env/environments/cad_spec/.venv/Scripts/python.exe`, CadQuery 2.8.0, and explicitly imported the audited checkout. No installation, network call, paid service, credential file, or repository edit was needed. Bytecode and pytest cache writes were disabled. All new scripts, snapshots, logs and temporary geometry are under this report's `v2` directory. Repository status was clean before and after.

**Fact. Evidence policy.** Facts below are measured outputs or source observations. Inferences identify interpretation of geometry or expectations. Opinions identify recommendations. For geometric reproductions, pass the shown code to `cad_spec.l5.observe_code(code)`. Original expected verdicts are retained and their mismatches are disclosed, rather than silently replacing the old inventory with a new passing suite.

## 1. Required changes and disposition of R1 to R5

### C1. Apply the limit to the angle, not separately to its two components

**Fact.** `measure._scope_scan`, line 581, accepts an axis when both `abs(dx)` and `abs(dy)` are at most `1e-12`. Around the diagonal axis `(1,1,0)`, a tilt of `1.3e-12` rad has components about `+/-9.192388155e-13`, so neither component trips the check. Independent cylinder interrogation retains those components. The actual tilt exceeds the stated limit by 30%. At `1.414e-12` the map also returns `ok`; at `1.415e-12` it refuses. This is a wrong verdict under the stated angular rule, even though the 4 mm specimen's numeric error is below dimension slack.

**Fact. Reproduction `diagonal_tilt_1.3e-12`:**

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5).extrude(8,both=True).rotate((0,0,0),(1, 1, 0),7.448451336700702e-11).translate((x,y,0))
    result=result.cut(tool)
```

Map returned: `{"status": "ok", "values": {"L": 100.0, "W": 80.0, "T": 4.000000000013, "n": 4, "D": 10.0, "mx": 15.0, "my": 15.0, "px": 70.0, "py": 50.0, "rectangular": true, "centered": true, "symmetric": true}, "reason": "", "centre": [0.0, 0.0, 0.0]}`.

**Opinion.** Preserve the promised angular boundary and add a diagonal boundary case to the gate. Proposed minimal source diff:

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ -541,5 +541,5 @@
 
 
-# A bore axis whose X or Y direction component exceeds this is "not along Z"
+# A bore axis whose tilt from the Z line exceeds this is "not along Z"
 # for the L5 observation map. It is floating-point slack, not a tolerance on
 # tilt: at 1e-12 rad a hole moves 1e-11 mm across a 10 mm plate, a hundred
@@ -579,5 +579,5 @@
         d, loc, r = cylinder.Axis().Direction(), cylinder.Axis().Location(), cylinder.Radius()
         smallest = 2 * r if smallest is None else min(smallest, 2 * r)
-        if abs(d.X()) <= STRICT_AXIS_SLACK and abs(d.Y()) <= STRICT_AXIS_SLACK:
+        if math.hypot(d.X(), d.Y()) <= math.sin(STRICT_AXIS_SLACK):
             continue  # exactly along Z: a hole, or a matter for the form check
         p = adaptor.Value((adaptor.FirstUParameter() + adaptor.LastUParameter()) / 2,
```

**Fact.** The audit-only script `angular_proposal.py` compiled this replacement in memory and checked 27 built parts. Only the three diagonal tilts `1.1e-12`, `1.3e-12`, `1.414e-12` changed from `ok` to `out_of_scope`. All 11 ordinary transformation controls stayed `ok`, and the specified X/Y/diagonal tilts of `1e-13`, `1e-12`, `1e-11`, `1e-9` kept their expected statuses. This is targeted validation, not a full patched scorer regression. No repository patch was applied.

### C2. Describe scope and form boundaries as implemented

**Fact.** The section 3 promise that a pocket cutting into a hole is refused by the scope rules is too broad. A through hole D=10 and a blind round pocket D=10 at x=7.5 overlap, but neither axis is strictly inside the other cylinder. The map returns `form_violation`, `n=0`, `D=None`, not `out_of_scope`. All 16 such probes, D in {0.01,0.1,1,10} and axis distances {1.1,1.2,1.3,1.5} times the radius, return `form_violation`. These are failures that prevent contract evaluation, not unsafe ok acceptances.

**Fact. Reproduction `intersecting_blind_D10_offset_Rx1.5`:**

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(0, 0)]).hole(10)
result=result.faces(">Z").workplane().pushPoints([(7.5,0)]).hole(10,1)
```

Map returned: `{"status": "form_violation", "values": {"L": 100.0, "W": 80.0, "T": 4.0, "n": 0, "D": null, "mx": null, "my": null, "px": null, "py": null, "rectangular": false, "centered": false, "symmetric": false}, "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 380.245 mm3 missing outside a 0.005 mm band", "centre": [0.0, 0.0, 0.0]}`.

**Fact.** A rounded rectangular pocket can also trigger `out_of_scope` through its own corner-cylinder axes, even when separate from the through hole. With box 30 x 10 and corner radius 4, adjacent corner axes are 2 mm apart inside their radius-4 cylinders. Radius 1 and 3 pockets instead return `form_violation`. This matches the literal new nested predicate, but does not establish recognition of a stepped hole.

**Fact. Reproduction `rounded_pocket_r4_near_separate_hole`:**

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-20, 0)]).hole(2)
result=result.cut(cq.Workplane("XY").box(30,10,2).edges("|Z").fillet(4).translate((0,0,2)))
```

Map returned: `{"status": "out_of_scope", "values": {"L": 100.0, "W": 80.0, "T": 4.0}, "reason": "two different cylinders at one hole position (counterbore, stepped or offset hole)", "centre": [0.0, 0.0, 0.0]}`.

**Opinion.** Keep these conservative verdicts for M1 and correct the narrative instead of adding feature recognition. Proposed document diff:

```diff
--- a/docs/design/L5-amendments.md
+++ b/docs/design/L5-amendments.md
@@ -63,5 +63,5 @@
 | Position | Not a contract variable. A plate moved off the origin measures the same; the bounding-box centre is reported for information | design note 7.2 |
 | Orientation | L along X, W along Y. Turned 90 or 270 degrees about Z, they swap. Turned by any other angle beyond the form tolerance, the form fails (a turn of 1e-10 rad is inside it) | design note 7.2; the form check |
-| What n counts | Through holes along Z only: one open, uninterrupted cylinder from the bottom face to the top face, within the form tolerance. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures |
+| What n counts | Recognised Z bores only: open bottom-to-top at the form tolerance, with cylindrical wall area coverage at least 0.99. Small side breakouts or overlaps can still be recognised; F1 and F2 remain contract checks. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures |
 | px, py | The extent of the hole centres along X and Y. For the four-corner pattern that is the pitch; for any other pattern it is only the extent, and `rectangular` is then False | the design note defines pitch for the family only |
 | Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face. For an accepted axis the two differ by at most (T / 2) x 1e-12: 7e-12 mm for the thickest generated plate (14 mm) | one measurement shared with the scorer |
@@ -69,5 +69,5 @@
 | Stepped, counterbored or offset hole | `out_of_scope`: two different cylinders, one with its axis strictly inside the other (two 10 mm holes 5.0 mm apart are not nested; 4.999 mm apart they are). Judged on the unrounded axis and diameter of every concave cylinder face | D is not one number. The scorer's grouping rounds diameters to 1e-4 mm and hid a 1e-6 step |
 | Holes of different diameters | `out_of_scope` when the measured diameters differ by more than the dimension slack, 1e-9 mm. Values are binary doubles: holes written 10 and 10.000000001 measure 1.00000008e-9 apart and are refused | D is one number in v1; the verdict must not depend on which hole comes first |
-| Tilted or cross hole | `out_of_scope` for any concave cylinder whose axis is not along Z beyond floating-point slack (1e-12 rad). At that slack every variable is still right to about 1e-11 mm (the kernel reads T = 4.00000000001 on a 4 mm plate with 10 mm holes) | a 1e-8 rad tilt was `ok` with a margin wrong by 2e-8 mm |
+| Tilted or cross hole | `out_of_scope` for any concave cylinder whose axis is not along Z beyond floating-point slack (1e-12 rad). On the 4 mm plate with 10 mm holes the kernel reads T = 4.00000000001 at that slack; this is a scale-specific example, not a global accuracy bound. The top-to-mid-plane displacement scales with T as above | a 1e-8 rad tilt was `ok` with a margin wrong by 2e-8 mm |
 | Supported size | `out_of_scope` when any cylindrical face is under 0.01 mm in diameter (exactly 0.01 mm is measured). This comes before the form check, so a fillet under that size is a size refusal, not the `form_violation` of amendment 1 | the probe that tells a hole from a boss cannot classify smaller ones; refusing is honest, reporting n = 0 was not |
 | Failed scope scan | `out_of_scope`, with the reason | it used to raise an exception out of the map |
@@ -76,9 +76,11 @@
 **One deviation from the design note, for the owner's approval.** Section
 7.2 lists "extra pocket or slot" as `out_of_scope`. M1 reports it as
-`form_violation`. Reason: a separate pocket does not make any contract
+`form_violation` unless an earlier cylinder scope rule applies. Reason: a separate pocket does not make any contract
 variable ambiguous, amendment 1 already fails every unrequested feature, and
 telling "a pocket" from "a fillet" would need feature recognition, which is
-new code that no review has seen. A pocket that cuts into a hole does make
-the hole ambiguous and is refused by the rules above. Either verdict fails
+new code that no review has seen. Scope refusal follows the cylinder-axis
+rules above, including cylinders on rounded pocket corners. An intersecting
+pocket whose axes are not nested can instead be a form violation; its
+numbers are diagnostic only. Either verdict fails
 gate G3. The external reviewer chose the same verdict, with that condition.
 
```

**Opinion.** Also qualify the n-count row as detector recognition, specify that its cylinder completeness cutoff is 0.99, and restrict the approximate 1e-11 mm accuracy statement to the generated plate scale. A 4000 mm thick synthetic plate with a 1e-12 rad tilt returns `ok`, mid-plane `mx=15`; its top intersection margin is `14.999999998`. That is consistent with the amended mid-plane definition, but not a universal 1e-11 mm agreement with the old top-face definition. No new generic thickness restriction is recommended.

**Fact. Reproduction `near_breakout_0.001`:**

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4).faces(">Z").workplane().pushPoints([(-45.001, -25), (-45.001, 25), (45.001, -25), (45.001, 25)]).hole(10)
```

Map returned: `{"status": "ok", "values": {"L": 100.00000000000001, "W": 80.0, "T": 4.0, "n": 4, "D": 10.0, "mx": 4.999000000000009, "my": 15.0, "px": 90.002, "py": 50.0, "rectangular": true, "centered": true, "symmetric": true}, "reason": "", "centre": [0.0, 0.0, 0.0]}`.

**Fact. Reproduction `thick_plate_tilt_1e-12_T4000`:**

```python
import cadquery as cq
result=cq.Workplane("XY").box(100,80,4000)
for x,y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool=cq.Workplane("XY").circle(5).extrude(8000,both=True).rotate((0,0,0),(0, 1, 0),5.729577951308232e-11).translate((x,y,0))
    result=result.cut(tool)
```

Map returned: `{"status": "ok", "values": {"L": 100.0, "W": 80.0, "T": 4000.00000000001, "n": 4, "D": 10.0, "mx": 15.0, "my": 15.0, "px": 70.0, "py": 50.0, "rectangular": true, "centered": true, "symmetric": true}, "reason": "", "centre": [0.0, 0.0, 0.0]}`.

| Finding | Disposition | Evidence |
| --- | --- | --- |
| R1 | Partly resolved | Original 1e-8 and 1e-6 tilts now out_of_scope; ordinary transformations pass. Diagonal angles up to roughly sqrt(2) x 1e-12 remain accepted. C1 fixes the remaining exact-rule mismatch. |
| R2 | Resolved for original finding | Radius steps 1e-5 and 1e-6 mm retain raw diameters and return out_of_scope. Coaxial/offset size probes and seam-split controls confirm the stated axis-inside rule. C2 narrows the broader feature-language promise. |
| R3 | Resolved | Original 1e-8 and 1e-7 mm differences refuse in both orderings; new 5e-10 passes, written 1e-9 and 2e-9 refuse at D=10. Actual doubles are reported below. |
| R4 | Resolved | Original radius-1e-4 mm cross bore now out_of_scope. The off-axis probe is capped at half-radius, unclear state raises, and every cylindrical face below 0.01 mm is refused before form. Supported .01/.011 mm hole and fillet controls behave as recorded. |
| R5 | Resolved | Injected RuntimeError in _scope_scan produces out_of_scope with the fault reason, strict=True and only L/W/T; no escaping exception. Legacy strict=False measurement deliberately raises ValueError. |

**Fact. R5 reproduction:**

```python
import importlib
import cadquery as cq
from cad_spec.l5 import observe
mm = importlib.import_module("cad_spec.measure")
original = mm._scope_scan
try:
    def broken(_):
        raise RuntimeError("synthetic classifier fault")
    mm._scope_scan = broken
    print(observe(mm.measure(cq.Workplane("XY").box(100,80,4).val(), strict=True)))
finally:
    mm._scope_scan = original
```

Map returned: `{"status": "out_of_scope", "reason": "the scope checks could not be completed (RuntimeError: synthetic classifier fault)", "values": {"L": 100.0, "W": 80.0, "T": 4.0}}`. This checks an injected scope-scan failure, not every possible CAD kernel exception.

## 2. Task 1: supplied checks

| Command | Result | Exit | Wall seconds |
| --- | --- | --- | --- |
| observation_gate | 58/58 | 0 | 6.459 |
| observation_pytest | 10 tests passed | 0 | 4.445 |
| rubric050 | 81/81 | 0 | 10.408 |
| rubric040 | 37/37 | 0 | 3.344 |

**Fact.** Commands were `python scripts/test_l5_observation.py`, `python -m pytest -q -p no:cacheprovider tests/test_l5_observation.py` from `environments/cad_spec`, `python scripts/test_rubric_050.py`, and `python scripts/test_rubric.py`. `gates.json` and the four named logs retain complete output. The pytest cache-provider flag only enforces the read-only ground rule. Source inspection confirms 58 gate cases, twelve `boundary_` cases, complete expected variable keys for every `ok` gate case, pinned `SCORER_BASIS="0.5.0"`, `Observation.ok`, and read-only returned values.

## 3. Task 2: complete 333-case regression

| Population | Cases | ok | out_of_scope | form_violation | not_single_solid | build_error |
| --- | --- | --- | --- | --- | --- | --- |
| controls | 180 | 180 | 0 | 0 | 0 | 0 |
| synthetic | 135 | 44 | 60 | 26 | 1 | 4 |
| taxonomy | 8 | 6 | 0 | 2 | 0 | 0 |
| measurement_fixture | 7 | 0 | 4 | 0 | 3 | 0 |
| stress | 3 | 3 | 0 | 0 | 0 | 0 |
| Total | 333 | 233 | 64 | 28 | 4 | 4 |

**Fact. (a) Every ok result with a wrong value:** none in the original 333 cases, using absolute 1e-9 mm numeric comparison and exact counts/booleans/None. All 233 ok rows match all saved expected values. This does not prove the omitted geometric properties of every non-family shape.

**Fact. 180 construction controls:** all twelve variables were compared: L/W/T/n/D/mx/my/px/py plus rectangular/centered/symmetric. Maximum numeric error `7.105427357601002e-15` mm; counts and booleans exact. Six train/dev specifications, ten construction styles, three transforms per style. All are `ok`.

**Fact. (b) Every mismatch against the old expected verdict:** 30, enumerated below. **Inference.** None is a new proved unsafe acceptance under the revised, literal M1 rules. The new diagonal-angle wrong verdict is C1 outside this original inventory. The 1e-7 mm positive-ligament refusal remains a coverage issue for exact intended geometry, not a new branch regression. No mismatch has been hidden by relabeling the saved input.

| Case | Old expectation | Observed | Assessment (inference) |
| --- | --- | --- | --- |
| edge_ligament_1e-07 | ok | form_violation | Boundary check fails at 1e-7; pre-existing kernel-scale coverage refusal. |
| small_diameter_0.002 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| small_diameter_0.001 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| small_diameter_0.0005 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| small_diameter_0.0001 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| small_diameter_5e-05 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| diameter_difference_1e-08 | ok | out_of_scope | Old permissive diameter expectation superseded by 1e-9 rule. |
| diameter_difference_1e-07 | ok | out_of_scope | Old permissive diameter expectation superseded by 1e-9 rule. |
| tilt_radians_1e-08 | ok | out_of_scope | Old tilt expectation superseded by strict axis rule. |
| counterbore_radius_step_1e-07 | out_of_scope | ok | Nominal feature erased by kernel; independent BRep has only original D=10 cylinders. |
| counterbore_radius_step_1e-08 | out_of_scope | ok | Nominal feature erased by kernel; independent BRep has only original D=10 cylinders. |
| counterbore_depth_1e-07 | out_of_scope | ok | Nominal feature erased by kernel; independent BRep has only original D=10 cylinders. |
| counterbore_depth_1e-08 | out_of_scope | ok | Nominal feature erased by kernel; independent BRep has only original D=10 cylinders. |
| close_distinct_axes_0.0009 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| close_distinct_axes_0.001 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| close_distinct_axes_0.001001 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| close_distinct_axes_0.0011 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| close_distinct_axes_0.002 | ok | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| outer_horizontal_fillet_r0.001 | form_violation | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| outer_horizontal_fillet_r0.0005 | form_violation | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| outer_horizontal_fillet_r0.0001 | form_violation | out_of_scope | Now explicitly below supported cylinder size; revised rule. |
| isolated_positions_distance_0.0009 | ok | out_of_scope | Artificial fixture retains sub-size geometry/scope fields; now refuses before invented hole positions. |
| isolated_positions_distance_0.001 | ok | out_of_scope | Artificial fixture retains sub-size geometry/scope fields; now refuses before invented hole positions. |
| isolated_positions_distance_0.001001 | ok | out_of_scope | Artificial fixture retains sub-size geometry/scope fields; now refuses before invented hole positions. |
| isolated_positions_distance_0.0011 | ok | out_of_scope | Artificial fixture retains sub-size geometry/scope fields; now refuses before invented hole positions. |
| fused_bottom_skin_8e-08 | ok | build_error | No measurable solid: kernel construction or bounding-box error; no map verdict. |
| fused_bottom_skin_1e-07 | ok | build_error | No measurable solid: kernel construction or bounding-box error; no map verdict. |
| fused_bottom_skin_1.2e-07 | form_violation | build_error | No measurable solid: kernel construction or bounding-box error; no map verdict. |
| near_breakout_0.01 | ok | form_violation | Detector cutoff reached: form fails; smaller tested overlap/breakout remains ok for M3 to reject. |
| near_overlap_0.01 | ok | form_violation | Detector cutoff reached: form fails; smaller tested overlap/breakout remains ok for M3 to reject. |

**Fact. (c) Every correct ordinary part refused:** none of the 180 construction controls, and none of the 11 new ordinary-transform controls. For the wider synthetic inventory the following intended plain plates have known coverage refusals:

| Part | Map verdict | Why |
| --- | --- | --- |
| edge_ligament_1e-07 | form_violation | Positive nominal ligament 1e-7 mm, boundary_consistent=False; precise BRep limitations. |
| small_diameter_0.002 | out_of_scope | Four analytic holes D below 0.01 mm; explicit coverage limit. |
| small_diameter_0.001 | out_of_scope | Four analytic holes D below 0.01 mm; explicit coverage limit. |
| small_diameter_0.0005 | out_of_scope | Four analytic holes D below 0.01 mm; explicit coverage limit. |
| small_diameter_0.0001 | out_of_scope | Four analytic holes D below 0.01 mm; explicit coverage limit. |
| small_diameter_5e-05 | out_of_scope | Four analytic holes D below 0.01 mm; explicit coverage limit. |
| close_distinct_axes_0.0009 | out_of_scope | Two disjoint holes D=0.0005 mm; explicit coverage limit. |
| close_distinct_axes_0.001 | out_of_scope | Two disjoint holes D=0.0005 mm; explicit coverage limit. |
| close_distinct_axes_0.001001 | out_of_scope | Two disjoint holes D=0.0005 mm; explicit coverage limit. |
| close_distinct_axes_0.0011 | out_of_scope | Two disjoint holes D=0.0005 mm; explicit coverage limit. |
| close_distinct_axes_0.002 | out_of_scope | Two disjoint holes D=0.0005 mm; explicit coverage limit. |
| NURBS | form_violation | Same physical plate represented with spline surfaces; intentional inherited false rejection. |

**Inference.** These twelve are refusals of correct intended geometry, not twelve rule violations: ten are outside the newly supported size, one is the known spline limitation, and one is kernel-scale boundary inconsistency. The NURBS row reports padded L/W/T and n=0 diagnostically, as documented. Near-overlap/breakout samples are not correct ordinary parts under family F1/F2. The four artificial position fixtures are inconsistent Measurements, not constructed parts. Three skin failures and the empty-compound failure yield no observation.

**Fact. Evidence:** `regression-results.jsonl` contains all 333 code snippets, previous outputs, current values/reasons and strict diagnostics. `independent-confirmations.json` confirms the four erased microsteps have only D=10 cylinders and the nominal edge-ligament solid is kernel-valid despite its stricter boundary failure. No per-row executable input was dropped.

## 4. Task 5: scorer compatibility and latency

| Scorer | Answers on each revision | Reward differences | Named-check differences | Parsed differences | Escaping exceptions |
| --- | --- | --- | --- | --- | --- |
| 0.5.0 | 3161 | 0 | 0 | 0 | main 0; branch 0 |
| 0.4.0 | 3161 | 0 | 0 | 0 | main 0; branch 0 |

**Fact.** Compared exact reward, each named check's passed flag, and parsed flag for both versions on all 3,161 identical saved completions/specifications, against main 1fb9a51. No differences. Main snapshot contents were independently verified against all 25 extracted main files. Saved input SHA-256: `aadd97fcb37734637a14e22f328c28c3c17584e3c4c445b23efb38b3a1b4fc44`; byte-identical to the earlier audit input. Evidence: `compat-main.jsonl`, `compat-branch.jsonl`, `compat-summary.json`, `verification-provenance.json`. No L5 verdict is substituted for historical scorer behavior.

| 0.5.0 measurement | Revision | Answers/timed calls | Mean ms/answer | Median ms/answer | p95 ms/answer |
| --- | --- | --- | --- | --- | --- |
| Full saved replay | main | 3161 | 64.152 | 67.979 | 102.752 |
| Full saved replay | branch | 3161 | 71.434 | 77.111 | 101.258 |
| Sequential paired control | main | 158 | 61.566 | 71.144 | 101.523 |
| Sequential paired control | branch | 158 | 61.497 | 69.906 | 104.708 |

**Fact.** Full replay timings include worker startup and use alternating scorer order per answer. The full replays overlapped some other local geometry checks, so use their raw timings descriptively. The paired control ran after geometry probes finished, sequentially main/branch/branch/main, using 79 saved train/dev answers per run, worker warmup before timing, 158 calls per revision. All paired verdicts match. Mode: local Windows persistent-worker `reuse`, not Linux `fork`; wall time includes code execution, kernel construction, measurement and score. The corpus includes non-parsed answers, so its overall average is lower than a successful geometry-only latency.

**Inference.** The paired mean ratio is 0.999 (branch/main). Two paired runs are descriptive evidence, not a hardware-independent overhead guarantee. The additional scope scan does execute in strict scoring even though its fields do not change rewards.

## 5. Task 4: newly tested rule boundaries

**Fact.** 130 built synthetic probes: 97 in `new-results.jsonl`, 19 in `supplemental-results.jsonl`, 14 in `precision-results.jsonl`. Each retains code, map status/values/reason, strict scope metadata, and independently interrogated cylindrical faces. All 130 yielded an observation. Their labels are descriptive and their original probe expectations remain visible, including expectations contradicted by the results.

### Tilt and ordinary transformations

| Part | Cases | Actual result | Values/evidence |
| --- | --- | --- | --- |
| Tilts about X, Y, diagonal (1,1,0), 1e-13 rad | 3 | ok | n=4, D=10, mx=my=15; T=4.000000000001 |
| Same axes, 1e-12 rad | 3 | ok | Same hole values; T=4.00000000001 |
| Same axes, 1e-11 rad | 3 | out_of_scope | Only envelope; reason non-Z hole axis |
| Same axes, 1e-9 rad | 3 | out_of_scope | Only envelope; reason non-Z hole axis |
| Diagonal 1.1e-12, 1.3e-12, 1.414e-12 | 3 | ok | Boundary defect C1 |
| Diagonal 1.415e-12 | 1 | out_of_scope | Components exceed 1e-12 |
| X/Y rotations 180 and 360 degrees | 4 | ok | All twelve ordinary values within 1e-9 |
| Mirrors XY/XZ/YZ | 3 | ok | All twelve ordinary values exact |
| 2, 10, 100 chains of X180 then Y180 | 3 | ok | All twelve ordinary values within 1e-9 |
| 37 then -37 degrees about (1,2,3) | 1 | ok | All twelve ordinary values within 1e-9 |
| T=4000 mm, 1e-12 rad about Y | 1 | ok | Mid-plane mx=15; top mx=14.999999998; amended definition qualification |

**Fact.** No tested correct ordinary part is refused by the tightened axis slack. Largest numeric drift across these eleven transformations is about 1.14e-13 mm. That observation does not cover arbitrarily long rotation chains.

### Nested cylinders, overlap, pockets and face splits

| Construction | Sizes/positions | Actual result |
| --- | --- | --- |
| Coaxial upper step: through D, upper diameter 1.2D | D=0.01,0.1,1,10 (4 cases) | out_of_scope; no hole variables |
| Same upper step offset by s times original radius | D=0.01,0.1,1,10; s=0,0.1,0.99,1,1.01 (20 cases) | out_of_scope; axis lies inside larger upper cylinder |
| Same upper step offset by 1.5 times original radius | Same four D (4 cases) | form_violation; n=0, D/margins/pitches=None |
| Two equal holes tangent, axis distance 2R | Same four D (4 cases) | ok; n=2, D preserved; F2 compliance left to contract |
| Two equal holes, axis distance 1.9R | Same four D (4 cases) | form_violation; n=0 |
| Two equal holes, axis distance exactly R | Same four D (4 cases) | form_violation; strict-inside nested predicate is false |
| Two equal holes, axis distance 0.999R | Same four D (4 cases) | out_of_scope; strict-inside predicate true |
| Separate 30 x 10 x 2 rounded pocket near D=2 hole at (-20,0) | Corner radii 1,3 (2 cases) | form_violation, diagnostic n=1, D=2 |
| Same rounded pocket, corner radius 4 | 1 case | out_of_scope due to pocket corner cylinders, C2 |
| Separate round blind pocket D=8, depth 2, plus D=2 through hole | 1 case | form_violation; n=1, D=2 |
| Round blind pocket alone D=8, depth 2 | 1 case | form_violation; n=0, D=None |
| Through hole split axially with clean=False | 1 case | ok; 2 faces, n=1, D=10 |
| Through hole split with half-cylinder cutters, clean=False | 1 case | ok; 6 cylinder faces, n=1, D=10 |
| Intersecting blind round pocket D, depth 1 | D=0.01,0.1,1,10; distance=1.1R,1.2R,1.3R,1.5R (16 cases) | form_violation; n=0; neither axis is nested, C2 |
| Counterbore radius increment 1e-6 | 4 standard holes (1 case) | out_of_scope; both radii survive |
| Counterbore radius increment 1e-7 and 1e-8 | 4 standard holes (2 cases) | ok; only original cylinders remain in actual BRep |
| Equal-D upper or full-depth cutter offset from one standard hole | Offsets 5e-10,2e-9,1e-8,5e-8,1e-7,1.1e-7 mm (12 cases) | ok; kernel erases cutter offset, actual shape retains only four original cylinders |
| Same equal-D offset 1e-6 mm | Upper and full-depth cutter (2 cases) | out_of_scope; fifth raw cylindrical face survives |

**Inference.** Nested-axis tests are conservative geometry rules, not complete recognition of connected hole features. Rounded corners can trip them and intersecting pockets outside the strict-inside boundary can reach form instead. None of the form diagnostics should be evaluated as a contract observation.

### Minimum size

| Measured cylinder diameter (mm) | Four Z holes | X cross bore | Vertical fillets (radius D/2) | Horizontal fillets (radius D/2) |
| --- | --- | --- | --- | --- |
| 0.009 | out_of_scope: below size | out_of_scope: below size | out_of_scope: below size | out_of_scope: below size |
| 0.010 | ok: n=4, D=.01 | out_of_scope: off-axis | form_violation | form_violation |
| 0.011 | ok: n=4, D=.011 | out_of_scope: off-axis | form_violation | form_violation |

**Fact.** All twelve size probes retain the requested cylinder diameter in the actual BRep. Hole values at .010 and .011 are L=100, W=80, T=4, n=4, mx=my=15, px=70, py=50, all three booleans True. Size refusal has only L/W/T and comes before axis or form; supported cross bores instead report the non-Z-axis reason. Supported convex horizontal fillets do not get mislabeled as concave cross bores.

### Diameter slack and ordering

| Written diameter difference (mm) | Actual double difference (mm) | Larger hole first by sorted axis | Larger hole last |
| --- | --- | --- | --- |
| 5e-10 | 5.000000413701855e-10 | ok, D=10.0000000005 | ok, D=10 |
| 1e-09 | 1.000000082740371e-09 | out_of_scope | out_of_scope |
| 2e-09 | 2.000000165480742e-09 | out_of_scope | out_of_scope |

**Fact.** The written 1e-9 boundary is slightly above the comparison slack at this magnitude, exactly as the amendment records. The 5e-10 case still picks the first sorted through-hole diameter, but every diameter is within 1e-9 of it. All six cases have n=4; refused diameter cases retain L/W/T/n and omit D/margins/pitches. This is an inclusive test of the actual measured double range, not decimal input strings.

## 6. Task 6: documents compared with code

| Statement | Assessment | Correction or qualification |
| --- | --- | --- |
| Section 3 tilted-hole row and section 3.1 R1: any tilt beyond 1e-12 rad | Wrong exact boundary | C1: componentwise square permits diagonal angles up to about sqrt(2) x slack. Use angular norm. |
| Section 3: pocket cutting into a hole is refused by scope rules | Wrong unconditional statement | C2: 16 non-nested intersecting blind-pocket probes reach form_violation. |
| Section 3: extra pocket or slot is form_violation | Too broad as a categorical claim | Rounded radius-4 pocket is out_of_scope under the explicit nested predicate; state scope precedence. |
| Section 3 n-count row: one open uninterrupted cylinder | Stronger than detector geometry | The detector accepts area coverage >=0.99; near breakouts/overlaps can be ok, as section 4 acknowledges. Describe recognized cylinder and F1/F2 checks. |
| Section 3 tilted-hole row: every variable right to about 1e-11 mm at slack | Requires scale qualification | Top-vs-mid margin discrepancy scales with T. T=4000 yields 2e-9 mm. Envelope padding also depends on cylinder scale. |
| Section 3 hole-centre row: at most (T/2) x 1e-12 per coordinate, 7e-12 for T=14 | Consistent as per-coordinate approximation | With C1 applied, Euclidean angular bound also matches. Mid-plane definition is a recorded deviation from design top-plane. |
| Section 3.1: all five required changes are made | Incomplete as a verification conclusion | Source repairs exist, but R1 exact angular boundary remains partly resolved. |
| Sections 3 and 3.1 referenced audit/l5-m1-audit.md and audit/l5-m1-v2-audit.md | Paths absent from this checkout | Earlier first audit is available outside repository; the referenced second report was not supplied here. Correct locations or include reports when maintaining documentation. |
| Section 3 by-name scorer basis, strict values, read-only values, no-hole None, size rule, diameter-double example, raw step rule, scope failure | Consistent with inspected code and executed checks | No additional required change. Scope_axes is additional strict metadata, historical hole grouping remains rounded internally. |
| Section 4 F1/F2 deferred, None predicates, basis pins, change detection and intent probes deferred | Consistent with M1 boundary | Near breakout/overlap <=.001 mm samples are ok; .01 mm reaches form. M2/M3 behavior itself is not implemented or verified here. |
| Section 4: 100-hole observation about 8 seconds | Machine-dependent, no contradiction established | This replay's stress_count_100 was 5.151 seconds; timings are workload/machine specific. |

**Opinion.** Treat C1 and C2 as pre-merge corrections. Do not reopen the recorded architecture, change historical scorer tolerances, or add M2/M3 behavior to make M1's numbers appear to enforce family compliance.

## 7. What could not be verified

- **Fact:** None of tasks 1, 2, 4 or 5 was blocked by missing earlier executable files. The original 333 cases and 3,161 saved answers were available and rerun; no bundle clone was needed.
- **Fact:** The second audit cited at `audit/l5-m1-v2-audit.md` is absent, so its historical claim of an incremental-bundle-only environment and unexecuted repository tests cannot be checked. This report describes this checkout and this execution only.
- **Fact:** The proposed C1 source change received targeted in-memory validation only. The full 3,161-answer replay and supplied gates tested the submitted branch, not a patched branch.
- **Fact:** Linux fork sandbox behavior and CI were not exercised. No live service or model was run. The local Windows reuse environment is the test environment reported above.
- **Fact:** R5 was tested through an injected scope-scan fault. This does not establish refusal for arbitrary earlier build, measurement or kernel failures; those can still be build errors.
- **Fact:** Three nominal membrane constructions failed before observation. The four kernel-erased microsteps and twelve erased equal-D offsets cannot test real surviving stepped or offset geometry at those scales.
- **Fact:** The saved compatibility corpus includes 2,200 gen-* train/dev specifications, 480 test-* and 481 rep-* specifications. The latter were replayed only for the explicitly requested frozen historical-score comparison. All new parts, geometry experiments and latency-control selections used synthetic or train/dev inputs; no held-out specification informed a rule, tolerance or prompt change.
- **Fact:** All twelve variables were checked on the 180 controls. Non-control cases retain the earlier inventory's expected-value subsets; independent face inspection supplements changed scope cases. The no-wrong-value finding means no error identified by those checks, not a proof of every diagnostic value on every refused shape.
- **Inference:** Finite controls cannot prove all supported solids, all CAD construction methods, or arbitrarily accumulated floating-point transformations. No incorrect ordinary refusal was found within the specified 180 controls and eleven new transform controls.
- **Fact:** M2 contract compilation and M3 family predicates, runtime intent/probes and gates remain outside this verification. An ok observation alone cannot establish compliance.

