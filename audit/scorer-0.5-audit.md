# Scorer 0.5.0 pre-merge audit

## 1. Verdict in five lines

1. **Merge after fixes. Do not merge scorer 0.5.0 as it stands.**
2. **Fact, high confidence:** forbidden pockets, bosses, slots, chamfers, fillets and bore lugs still receive 1.0.
3. **Fact, high confidence:** rounding admits errors beyond 0.1 mm, and equivalent NURBS plates are rejected.
4. **Fact, high confidence:** environments contaminate each other's scorer version; added work can turn a legacy reward into a timeout.
5. **Fact, high confidence:** the finite-suite, replay and sensitivity claims reproduce; they do not establish the universal contract.

Target: branch `feat/scorer-0.5`, HEAD `f5ca73a`, main parent `7c17439`. Audit date 2026-10-05. Runtime: Windows, Python 3.12, CadQuery 2.8.0, default `reuse` sandbox. No paid action, model API, Prime operation, deployment, commit or tracked-file edit occurred. New outputs and scripts are beneath this audit folder. Existing scratch artifacts were present at the start; their runners were read and adapted, then all reported checks were independently rerun from the requested worktree with fresh outputs under `independent/`.

The system Python lacked CadQuery. The supplied cadspec.sh activates the Windows venv in the main checkout and sources credential files. I invoked `C:/Users/bgare/dev/cad-spec-env/environments/cad_spec/.venv/Scripts/python.exe` directly without sourcing those credentials. `PYTHONPATH=C:/Users/bgare/dev/cad-spec-audit/environments/cad_spec`, UTF-8 and `PYTHONDONTWRITEBYTECODE=1` were set. The import check printed `C:\Users\bgare\dev\cad-spec-audit\environments\cad_spec\cad_spec\rubric.py 0.5.0 2.8.0`. WSL only offered docker-desktop; this is not a Linux isolation audit.

Facts are executions or source/history checks; inferences and opinions are labelled. High confidence means independently corroborated locally. Moderate confidence marks extrapolations or proposed designs. Diffs below are reviewable scratch prototypes, not merge-ready certification. Shared patches must be applied once. If 0.5.0 already denotes frozen recorded semantics, behavioral repairs require a new scorer version, rather than silently replacing that version.

## 2. Blocking findings

### B1. The band and residual allowance still give forbidden geometry full credit

**Fact, high:** a large-area pocket passes without spoofing anything:

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

result=result.cut(cq.Workplane("XY").box(50,50,0.0049).translate((0,0,2.99755)))
```

Observed reward **1.0**; failed checks `none`; extra `0.0`, missing `0.0` mm3. Complete code/spec: [A003](#a003).

It removes 12.25 mm3 over a visible 50 x 50 mm area. A shallow boss changes the measured bounding box, and the reconstructed shrunk ideal still lies inside the original plate:

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

result=result.union(cq.Workplane("XY").box(20,20,0.0059).translate((0,0,3.00195)))
```

Observed reward **1.0**; failed checks `none`; extra `0.0`, missing `0.0` mm3. Complete code/spec: [A008](#a008).

The volume allowance also permits a defect much deeper than the band. This square slot passes through the entire 6 mm plate:

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

result=result.cut(cq.Workplane("XY").box(0.0128,0.0128,8))
```

Observed reward **1.0**; failed checks `none`; extra `0.0`, missing `0.000981` mm3. Complete code/spec: [A084](#a084).

On the largest-area train/dev spec, gen-0032 (214 x 150 x 10.5 mm), two pockets each 213.998 x 149.998 x 0.0049 mm remove **312.079069 mm3** analytically, yet score 1.0 with extra=missing=0.0. The value is recomputed as two cutter areas minus the four bore areas, times depth. A 0.001 mm rim keeps the envelope. The thinnest train/dev plate also passes this construction. See the largest_skin rows in section 6.

For this fixed ideal, the excluded ideal boundary layer has volume **362.573112 mm3**, computed as nominal ideal volume minus the shrunken box with expanded bores. This is an upper bound for loss wholly in that layer, not a proved attainable maximum under all detector/gate constraints. I do not know the global maximum. The achieved 312.079069 mm3 loss already disproves any claim that the 0.001 mm3 cutoff bounds total defect volume.

Other observed full-credit forbidden geometry: 0.01 mm top chamfer, residuals 0/0; 0.03 mm corner fillet, missing 0.000735 mm3; 0.05 mm-deep bore lug, extra 0.000018 mm3. Tiny features and broad shallow features are separate loopholes.

**Inference, high:** a measured-envelope ideal absorbs shallow bosses, tabs and lips. A volume comparison with a blind surface band cannot enforce absence of extra features. Merely choosing smaller positive constants still permits sufficiently small wrong parts.

**Opinion, moderate:** add a boundary-support check. Every face must lie on one of six envelope planes or four measured circular bore surfaces, at kernel precision. Keep the solid/shell/validity/loose-geometry gates. Recognise analytical geometry regardless of surface storage representation. Compare an unbanded ideal built from raw bore values as a numerical backstop.

The shared unified diff below implements this approach and the strict raw-measurement and legacy work-policy portions of B2, B4 and B5. The face distance uses twice OCCT Precision.Confusion, 0.0000002 mm on this runtime, to account for observed NURBS bounding-box padding. This is numerical uncertainty, not a 0.005 mm feature allowance. The residual threshold can remain 0.001 mm3 only with a separate form/topology check; it cannot be the contract itself. The band should not decide acceptance.

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ -284,6 +284,7 @@
     # Shape residual (0.5.0), see SHAPE_BAND_MM. Added fields: scorer 0.4.0
     # does not read them. None means the comparison could not be made, which
     # scorer 0.5.0 treats as a failed check, never as a pass.
+    surface_conformance: bool | None = None
     extra_volume: float | None = None     # mm^3 of material outside the ideal part
     missing_volume: float | None = None   # mm^3 of the ideal part that is absent
 
@@ -450,7 +451,65 @@
     return load_brep(build_brep(code))
 
 
-def _z_aligned_cylinders(solid: Any) -> list[tuple[float, float, float, Any]]:
+def _analytic_adaptor(face: Any) -> Any:
+    """Recognise analytic geometry independently of its surface representation."""
+    from OCP.BRep import BRep_Tool
+    from OCP.BRepAdaptor import BRepAdaptor_Surface
+    from OCP.GeomAbs import GeomAbs_SurfaceType
+    from OCP.GeomAdaptor import GeomAdaptor_Surface
+    from OCP.GeomConvert import GeomConvert_SurfToAnaSurf
+    from OCP.Precision import Precision
+
+    adaptor = BRepAdaptor_Surface(face.wrapped)
+    if adaptor.GetType() in (GeomAbs_SurfaceType.GeomAbs_Plane,
+                             GeomAbs_SurfaceType.GeomAbs_Cylinder):
+        return adaptor
+    converter = GeomConvert_SurfToAnaSurf(BRep_Tool.Surface_s(face.wrapped))
+    analytical = converter.ConvertToAnalytical(Precision.Confusion_s())
+    if analytical is None:
+        return None
+    return GeomAdaptor_Surface(analytical)
+
+
+def _surface_conformance(solid: Any, bb: Any, holes: list[Hole]) -> bool:
+    """Every boundary must lie on an envelope plane or a recognised bore."""
+    from OCP.GeomAbs import GeomAbs_SurfaceType
+    from OCP.Precision import Precision
+
+    linear = 2 * Precision.Confusion_s()
+    angular = Precision.Angular_s()
+    limits = ((bb.xmin, bb.xmax), (bb.ymin, bb.ymax), (bb.zmin, bb.zmax))
+    for face in solid.Faces():
+        adaptor = _analytic_adaptor(face)
+        if adaptor is None:
+            return False
+        if adaptor.GetType() == GeomAbs_SurfaceType.GeomAbs_Plane:
+            plane = adaptor.Plane()
+            normal, origin = plane.Axis().Direction(), plane.Location()
+            n = (normal.X(), normal.Y(), normal.Z())
+            p = (origin.X(), origin.Y(), origin.Z())
+            axis = max(range(3), key=lambda k: abs(n[k]))
+            if any(abs(n[k]) > angular for k in range(3) if k != axis):
+                return False
+            if min(abs(p[axis] - edge) for edge in limits[axis]) > linear:
+                return False
+        elif adaptor.GetType() == GeomAbs_SurfaceType.GeomAbs_Cylinder:
+            cylinder = adaptor.Cylinder()
+            axis = cylinder.Axis()
+            direction, origin = axis.Direction(), axis.Location()
+            if abs(direction.X()) > angular or abs(direction.Y()) > angular:
+                return False
+            if not any(abs(origin.X() - h.x) <= linear
+                       and abs(origin.Y() - h.y) <= linear
+                       and abs(2 * cylinder.Radius() - h.diameter) <= linear
+                       for h in holes):
+                return False
+        else:
+            return False
+    return True
+
+
+def _z_aligned_cylinders(solid: Any, *, strict: bool = False) -> list[tuple[float, float, float, Any]]:
     """Exact kernel geometry for every Z-parallel cylindrical face."""
     from OCP.BRepAdaptor import BRepAdaptor_Surface
     from OCP.GeomAbs import GeomAbs_SurfaceType
@@ -458,7 +517,9 @@
     out: list[tuple[float, float, float, Any]] = []
     for face in solid.Faces():
         adaptor = BRepAdaptor_Surface(face.wrapped)
-        if adaptor.GetType() != GeomAbs_SurfaceType.GeomAbs_Cylinder:
+        if strict:
+            adaptor = _analytic_adaptor(face)
+        if adaptor is None or adaptor.GetType() != GeomAbs_SurfaceType.GeomAbs_Cylinder:
             continue
         cylinder = adaptor.Cylinder()
         direction = cylinder.Axis().Direction()
@@ -538,7 +599,7 @@
     return [(lo, hi) for lo, hi in merged]
 
 
-def _classify_cylinders(solid: Any) -> tuple[list[Hole], list[PartialBore]]:
+def _classify_cylinders(solid: Any, *, strict: bool = False) -> tuple[list[Hole], list[PartialBore]]:
     """Closed internal bores, plus rejected concave groups as diagnostics.
 
     Two independent discriminators, because hollow geometry defeats either
@@ -566,7 +627,8 @@
 
     # position -> diameter -> (summed face area mm^2, [Z intervals])
     features: dict[tuple[float, float], dict[float, tuple[list[float], list[tuple[float, float]]]]] = {}
-    for radius, cx, cy, face in _z_aligned_cylinders(solid):
+    raw: dict[tuple, tuple[float, float, float]] = {}
+    for radius, cx, cy, face in _z_aligned_cylinders(solid, strict=strict):
         fbb = face.BoundingBox()
         if fbb.zlen <= 0:
             continue
@@ -577,6 +639,7 @@
             continue  # material immediately inward => convex round/fillet/boss/wall
         key = (round(cx, COAXIAL_DP), round(cy, COAXIAL_DP))
         diameter = round(2 * radius, 4)
+        raw.setdefault((key, diameter), (2 * radius, cx, cy))
         area_acc, intervals = features.setdefault(key, {}).setdefault(diameter, ([0.0], []))
         area_acc[0] += face.Area()
         intervals.append((fbb.zmin, fbb.zmax))
@@ -594,13 +657,14 @@
                 if coverage >= PARTIAL_REPORT_MIN:
                     partial.append(PartialBore(diameter, round(x, 4), round(y, 4), round(coverage, 4)))
                 continue  # partial arc (fillet, breakout), not a closed bore
+            raw_d, raw_x, raw_y = raw[((x, y), diameter)]
             holes.append(Hole(
-                diameter=diameter,
-                x=round(x, 4),
-                y=round(y, 4),
-                depth=round(covered, 4),
-                z_min=round(spans[0][0], 4),
-                z_max=round(spans[-1][1], 4),
+                diameter=raw_d if strict else diameter,
+                x=raw_x if strict else round(x, 4),
+                y=raw_y if strict else round(y, 4),
+                depth=covered if strict else round(covered, 4),
+                z_min=spans[0][0] if strict else round(spans[0][0], 4),
+                z_max=spans[-1][1] if strict else round(spans[-1][1], 4),
                 segments=len(spans),
             ))
     return holes, partial
@@ -684,14 +748,14 @@
         return shape
 
     try:
-        extra = volume(cut(solid.wrapped, ideal(SHAPE_BAND_MM)))
-        missing = volume(cut(ideal(-SHAPE_BAND_MM), solid.wrapped))
+        extra = volume(cut(solid.wrapped, ideal(0.0)))
+        missing = volume(cut(ideal(0.0), solid.wrapped))
     except Exception:  # "could not compare" is a result, reported as None
         return None, None
-    return round(extra, 6), round(missing, 6)
-
-
-def measure(solid: Any) -> Measurements:
+    return extra, missing
+
+
+def measure(solid: Any, *, strict: bool = False) -> Measurements:
     """Extract features from a trusted shape (see load_brep)."""
     from OCP.BRepCheck import BRepCheck_Analyzer
     from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX
@@ -715,23 +779,29 @@
         + _count(topo, TopAbs_EDGE, TopAbs_FACE)
         + _count(topo, TopAbs_VERTEX, TopAbs_EDGE)
     )
-    holes, partial = _classify_cylinders(solid)
+    holes, partial = _classify_cylinders(solid, strict=strict)
     for h in holes:
         h.open = _bore_is_open(solid, h, bb.zmin, bb.zmax)
-    extra_volume, missing_volume = _shape_residual(solid, bb, holes)
+    extra_volume = missing_volume = None
+    surface_conformance = None
+    if strict:
+        extra_volume, missing_volume = _shape_residual(solid, bb, holes)
+        surface_conformance = _surface_conformance(solid, bb, holes)
+    def measured(value: float, digits: int = 4) -> float:
+        return value if strict else round(value, digits)
     return Measurements(
-        length=round(bb.xlen, 4),
-        width=round(bb.ylen, 4),
-        thickness=round(bb.zlen, 4),
-        volume=round(volume, 4),
+        length=measured(bb.xlen),
+        width=measured(bb.ylen),
+        thickness=measured(bb.zlen),
+        volume=measured(volume),
         solid_count=solid_count,
         holes=holes,
-        x_min=round(bb.xmin, 4),
-        x_max=round(bb.xmax, 4),
-        y_min=round(bb.ymin, 4),
-        y_max=round(bb.ymax, 4),
-        z_min=round(bb.zmin, 4),
-        z_max=round(bb.zmax, 4),
+        x_min=measured(bb.xmin),
+        x_max=measured(bb.xmax),
+        y_min=measured(bb.ymin),
+        y_max=measured(bb.ymax),
+        z_min=measured(bb.zmin),
+        z_max=measured(bb.zmax),
         partial_bores=partial,
         shell_count=_count(topo, TopAbs_SHELL),
         loose_count=loose,
@@ -739,12 +809,13 @@
         off_axis_bores=_off_axis_bore_count(solid),
         extra_volume=extra_volume,
         missing_volume=missing_volume,
+        surface_conformance=surface_conformance,
     )
 
 
-def _measure_code(code: str) -> Measurements:
+def _measure_code(code: str, *, strict: bool = False) -> Measurements:
     """Build and measure in THIS process (inproc and reuse modes)."""
-    return measure(load_brep(build_brep(code)))
+    return measure(load_brep(build_brep(code)), strict=strict)
 
 
 # --- isolated execution ------------------------------------------------------
@@ -897,7 +968,7 @@
         os.killpg(pid, signal.SIGKILL)
 
 
-def _run_forked(code: str, budget: float, mem_mb: int) -> tuple[str, Any]:
+def _run_forked(code: str, budget: float, mem_mb: int, *, strict: bool = False) -> tuple[str, Any]:
     """Run one rollout in a disposable forked child. Returns (status, payload).
 
     The child replies with b"O" + BREP bytes or b"E" + UTF-8 error text. The
@@ -995,14 +1066,14 @@
     if tag != b"O":
         return ("error", "rollout process returned a malformed result")
     try:
-        return ("ok", measure(load_brep(body)))
+        return ("ok", measure(load_brep(body), strict=strict))
     except BuildError as exc:
         return ("error", str(exc))
     except Exception as exc:
         return ("error", f"result geometry could not be measured: {type(exc).__name__}")
 
 
-def _run_reused(code: str, budget: float, mem_mb: int) -> tuple[str, Any]:
+def _run_reused(code: str, budget: float, mem_mb: int, *, strict: bool = False) -> tuple[str, Any]:
     """Run one rollout in this (persistent) process, in a fresh temp dir.
 
     `budget` is enforced by the parent, which kills this whole process;
@@ -1015,7 +1086,7 @@
     previous = os.getcwd()
     try:
         os.chdir(workdir)
-        return ("ok", _measure_code(code))
+        return ("ok", _measure_code(code, strict=strict))
     except BuildError as exc:
         return ("error", _clean_error(str(exc)))
     except Exception as exc:
@@ -1042,9 +1113,9 @@
         if kind == "stop":
             conn.send(("ok", None))
             return
-        code, budget, mem_mb = payload
+        code, budget, mem_mb, strict = payload
         try:
-            conn.send(run(code, budget, mem_mb))
+            conn.send(run(code, budget, mem_mb, strict=strict))
         except Exception as exc:  # report faults before dying
             conn.send(("error", f"worker fault: {type(exc).__name__}: {exc}"))
 
@@ -1078,9 +1149,9 @@
     def alive(self) -> bool:
         return self.proc.is_alive()
 
-    def call(self, code: str) -> Measurements:
+    def call(self, code: str, *, strict: bool = False) -> Measurements:
         try:
-            self.conn.send(("measure", (code, _exec_timeout(), _mem_limit_mb())))
+            self.conn.send(("measure", (code, _exec_timeout(), _mem_limit_mb(), strict)))
         except (BrokenPipeError, OSError) as exc:
             raise BuildError(f"scorer pipe broke: {exc}") from exc
         # In fork mode the worker enforces the budget itself and survives;
@@ -1158,7 +1229,7 @@
     return info
 
 
-def build_and_measure(completion: str) -> Measurements:
+def build_and_measure(completion: str, *, strict: bool = False) -> Measurements:
     """Extract code, run it isolated, measure the result.
 
     Raises BuildError when the model's code does not yield a part (a model
@@ -1168,9 +1239,9 @@
     code = extract_code(completion)
     if _inproc_requested():
         require_cadquery()
-        return _measure_code(code)
-    try:
-        return _get_worker().call(code)
+        return _measure_code(code, strict=strict)
+    try:
+        return _get_worker().call(code, strict=strict)
     except (BuildError, ScorerUnavailableError):
         raise
     except Exception as exc:  # anything else means the worker is unwell
```
```diff
--- a/environments/cad_spec/cad_spec/rubric.py
+++ b/environments/cad_spec/cad_spec/rubric.py
@@ -291,7 +291,8 @@
         else:
             checks.append(Check(
                 "R9:no_other_features",
-                extra <= SHAPE_VOLUME_TOL and missing <= SHAPE_VOLUME_TOL,
+                m.surface_conformance is True
+                and extra <= SHAPE_VOLUME_TOL and missing <= SHAPE_VOLUME_TOL,
                 f"{extra:.3f} mm3 extra, {missing:.3f} mm3 missing outside a "
                 f"{SHAPE_BAND_MM} mm band around the ideal plate with bores",
             ))
@@ -304,7 +305,7 @@
     if version not in TOLERANCES:
         raise ValueError(f"unknown scorer version {version!r}; supported: {', '.join(SUPPORTED_VERSIONS)}")
     try:
-        m = build_and_measure(completion)
+        m = build_and_measure(completion, strict=version != "0.4.0")
     except BuildError as exc:
         return Report(reward=0.0, checks=[], error=str(exc), parsed=False)
```

**Fact, high, prototype only:** 78 correct train/dev construction cases had unrounded unbanded extra=missing=0.0 after analytical recovery. All six correct NURBS cases passed. A 134-case smoke run rejected the substantive forbidden geometry and rounding examples included in that run. Passing controls included coincident re-drilling, a one-solid compound and a union entirely inside existing material. A prior slack-edge expectation, length +0.100001, became 0.9 through R1, outside the stated 0.1 mm tolerance. It is explicitly recorded as an unexpected historical expectation in proposal-check.jsonl. The later four rounding observations were not silently included in that 134-case count. These smoke checks are not full CI or compatibility certification.

### B2. Measurement rounding widens the 0.1 mm tolerance

**Fact, high:** scalar and position errors beyond tolerance still score 1.0:

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 6)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.600049)
)
```

Observed reward **1.0**; failed checks `none`; extra `0.0`, missing `0.0` mm3. Complete code/spec: [A129](#a129).

```python
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)
result=result.faces(">Z").workplane().pushPoints([(-30.1004,-20),(-30.1004,20),(30.1004,-20),(30.1004,20)]).hole(6.5)
```

Observed reward **1.0**; failed checks `none`; extra `0.0`, missing `0.0` mm3. Complete code/spec: [A130](#a130).

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

result=result.translate((.060499,.080499,0))
```

Observed reward **1.0**; failed checks `none`; extra `0.0`, missing `0.0` mm3. Complete code/spec: [A127](#a127).

The diagonal raw displacement is **0.100698649455 mm**, but rounded (0.060, 0.080) has norm exactly 0.1 mm. An axial 0.10049 mm shift also passes; 0.1005 mm fails R5 in the tested example. Diameter and length +0.100049 pass; +0.1001 fails their corresponding checks. Datum +0.10004 passes; +0.1001 fails R8. Exact +0.1 passes all tested scalar fields.

The 0.0001 mm rounding grid allows approximately another 0.00005 mm on dimensions/diameters; the 0.001 mm centre grid allows approximately another 0.0005 mm per coordinate. Binary representation and tie-to-even rounding affect endpoint ties. Position error can grow by at most sqrt(2) x 0.0005 mm beyond the rounded comparison boundary, plus numerical epsilon. That is a bound, not a proved attained supremum. The observed diagonal extension is 0.000698649455 mm. The explicit NUM_EPS=1e-6 is a further much smaller numerical allowance.

**Opinion, high:** strict acceptance must compare raw geometric values; display rounding should not affect it. Keep legacy grouping, rounding and checks intact. The B1 shared patch stores a raw representative axis and diameter per group and threads the strict policy through measurement. Relevant excerpts from that same unified diff, not a second patch to apply:

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ -577,6 +639,7 @@
             continue  # material immediately inward => convex round/fillet/boss/wall
         key = (round(cx, COAXIAL_DP), round(cy, COAXIAL_DP))
         diameter = round(2 * radius, 4)
+        raw.setdefault((key, diameter), (2 * radius, cx, cy))
         area_acc, intervals = features.setdefault(key, {}).setdefault(diameter, ([0.0], []))
         area_acc[0] += face.Area()
         intervals.append((fbb.zmin, fbb.zmax))
@@ -594,13 +657,14 @@
                 if coverage >= PARTIAL_REPORT_MIN:
                     partial.append(PartialBore(diameter, round(x, 4), round(y, 4), round(coverage, 4)))
                 continue  # partial arc (fillet, breakout), not a closed bore
+            raw_d, raw_x, raw_y = raw[((x, y), diameter)]
             holes.append(Hole(
-                diameter=diameter,
-                x=round(x, 4),
-                y=round(y, 4),
-                depth=round(covered, 4),
-                z_min=round(spans[0][0], 4),
-                z_max=round(spans[-1][1], 4),
+                diameter=raw_d if strict else diameter,
+                x=raw_x if strict else round(x, 4),
+                y=raw_y if strict else round(y, 4),
+                depth=covered if strict else round(covered, 4),
+                z_min=spans[0][0] if strict else round(spans[0][0], 4),
+                z_max=spans[-1][1] if strict else round(spans[-1][1], 4),
                 segments=len(spans),
             ))
     return holes, partial
@@ -715,23 +779,29 @@
         + _count(topo, TopAbs_EDGE, TopAbs_FACE)
         + _count(topo, TopAbs_VERTEX, TopAbs_EDGE)
     )
-    holes, partial = _classify_cylinders(solid)
+    holes, partial = _classify_cylinders(solid, strict=strict)
     for h in holes:
         h.open = _bore_is_open(solid, h, bb.zmin, bb.zmax)
-    extra_volume, missing_volume = _shape_residual(solid, bb, holes)
+    extra_volume = missing_volume = None
+    surface_conformance = None
+    if strict:
+        extra_volume, missing_volume = _shape_residual(solid, bb, holes)
+        surface_conformance = _surface_conformance(solid, bb, holes)
+    def measured(value: float, digits: int = 4) -> float:
+        return value if strict else round(value, digits)
     return Measurements(
-        length=round(bb.xlen, 4),
-        width=round(bb.ylen, 4),
-        thickness=round(bb.zlen, 4),
-        volume=round(volume, 4),
+        length=measured(bb.xlen),
+        width=measured(bb.ylen),
+        thickness=measured(bb.zlen),
+        volume=measured(volume),
         solid_count=solid_count,
         holes=holes,
-        x_min=round(bb.xmin, 4),
-        x_max=round(bb.xmax, 4),
-        y_min=round(bb.ymin, 4),
-        y_max=round(bb.ymax, 4),
-        z_min=round(bb.zmin, 4),
-        z_max=round(bb.zmax, 4),
+        x_min=measured(bb.xmin),
+        x_max=measured(bb.xmax),
+        y_min=measured(bb.ymin),
+        y_max=measured(bb.ymax),
+        z_min=measured(bb.zmin),
+        z_max=measured(bb.zmax),
         partial_bores=partial,
         shell_count=_count(topo, TopAbs_SHELL),
         loose_count=loose,
```

### B3. An environment does not own its scorer, and the report cache omits version

**Fact, high:** loading the second environment changes the first one's registered reward function. Reusing a state returns a stale report from another scorer:

```python
import cad_spec.environment as E
from cad_spec.tasks import reference_solution
s = E.EVAL_SPECS[0]
code = reference_solution(s) + '\nresult=result.cut(cq.Workplane("XY").box(2,2,100))'
old = E.load_environment(scorer_version="0.4.0", metrics=False)
f = E.spec_reward  # function registered with vf.Rubric
state = {}
print(f(code,s.id,{"spec_id":s.id},state=state))  # observed 1.0
new = E.load_environment(scorer_version="0.5.0", metrics=False)
print(f(code,s.id,{"spec_id":s.id}))             # observed 0.9
print(f(code,s.id,{"spec_id":s.id},state=state))  # observed 1.0, cached legacy report
```

Fresh strict scoring returns 0.9, failing R9 only. Legacy scoring returns 1.0 with every legacy check passing. Evidence: review-probes.log. The installed verifier wraps the rubric in a RubricGroup with monitor functions; a bare env.rubric.funcs[0] is not generally the scorer.

**Inference, high:** several same-version tier environments work by accident. A later legacy evaluation environment can change current training callbacks. Invalid tier construction can mutate the global before load fails. Separately imported callbacks or spawn processes can regain the default. The geometry worker here does not choose a rubric version, so it neither solves nor itself causes this selector bug. Verifier per-rollout state sharing is useful, but version must belong to cache identity.

**Opinion, high:** bind version to each environment callback, preserve callback names and include version in the cache key. Expose selected version on the instance. Verify serialization carries the bound callback if a hosted worker imports functions separately. The smallest local design is a named closure:

```diff
--- a/environments/cad_spec/cad_spec/environment.py
+++ b/environments/cad_spec/cad_spec/environment.py
@@ -10,6 +10,7 @@
 from __future__ import annotations
 
 from collections.abc import Callable, Sequence
+from functools import wraps
 from typing import Any
 
 import verifiers as vf
@@ -103,10 +104,9 @@
 _STATE_KEY = "_cad_spec_report"
 # Scorer version used by every reward function of this process. Set by
 # load_environment(scorer_version=...); the default is the current scorer.
-_scorer_version = SCORER_VERSION
-
-
-def _report(text: str, spec_id: str, state: Any = None) -> Report:
+
+
+def _report(text: str, spec_id: str, state: Any = None, version: str = SCORER_VERSION) -> Report:
     """One build per rollout, however many reward/metric functions read it.
 
     The report is shared through the rollout's own `state` dict, which
@@ -115,12 +115,12 @@
     produced identical code shared one execution; each rollout is now judged
     on its own build. Without a state dict (direct calls) nothing is cached.
     """
-    key = (text, spec_id)
+    key = (text, spec_id, version)
     if isinstance(state, dict):
         cached = state.get(_STATE_KEY)
         if cached is not None and cached[0] == key:
             return cached[1]
-    report = score(text, SPECS[spec_id], _scorer_version)
+    report = score(text, SPECS[spec_id], version)
     if isinstance(state, dict):
         state[_STATE_KEY] = (key, report)
     return report
@@ -143,7 +143,7 @@
     if spec is None:
         return 0.0
 
-    report = _report(_completion_text(completion), spec.id, kwargs.get("state"))
+    report = _report(_completion_text(completion), spec.id, kwargs.get("state"), kwargs.get("scorer_version", SCORER_VERSION))
     return max(report.reward, PARSE_FLOOR) if report.parsed else 0.0
 
 
@@ -159,7 +159,7 @@
     spec = _spec_for(answer, info)
     if spec is None:
         return 0.0
-    report = _report(_completion_text(completion), spec.id, kwargs.get("state"))
+    report = _report(_completion_text(completion), spec.id, kwargs.get("state"), kwargs.get("scorer_version", SCORER_VERSION))
     return 1.0 if report.parsed and report.reward == 1.0 else 0.0
 
 
@@ -173,7 +173,7 @@
         spec = _spec_for(answer, info)
         if spec is None:
             return 0.0
-        report = _report(_completion_text(completion), spec.id, kwargs.get("state"))
+        report = _report(_completion_text(completion), spec.id, kwargs.get("state"), kwargs.get("scorer_version", SCORER_VERSION))
         return float(any(c.name == check_name and c.passed for c in report.checks))
 
     metric.__name__ = "m_" + check_name.replace(":", "_")
@@ -183,7 +183,7 @@
 def built(completion, answer="", info=None, **kwargs) -> float:
     """Zero-weight diagnostic: 1.0 if the code executed and produced a solid."""
     spec = _spec_for(answer, info)
-    return float(spec is not None and _report(_completion_text(completion), spec.id, kwargs.get("state")).parsed)
+    return float(spec is not None and _report(_completion_text(completion), spec.id, kwargs.get("state"), kwargs.get("scorer_version", SCORER_VERSION)).parsed)
 
 
 def gates_passed(completion, answer="", info=None, **kwargs) -> float:
@@ -191,7 +191,7 @@
     spec = _spec_for(answer, info)
     if spec is None:
         return 0.0
-    report = _report(_completion_text(completion), spec.id, kwargs.get("state"))
+    report = _report(_completion_text(completion), spec.id, kwargs.get("state"), kwargs.get("scorer_version", SCORER_VERSION))
     gates = [c for c in report.checks if c.name.startswith("gate:")]
     return float(bool(gates) and all(c.passed for c in gates))
 
@@ -236,12 +236,11 @@
                setting is process-wide: all environments loaded in one
                process share it, and the last call decides.
     """
-    global _scorer_version
     if reward not in REWARDS:
         raise ValueError(f"reward must be one of {REWARDS}, got {reward!r}")
     if scorer_version is not None and scorer_version not in SUPPORTED_VERSIONS:
         raise ValueError(f"scorer_version must be one of {SUPPORTED_VERSIONS}, got {scorer_version!r}")
-    _scorer_version = scorer_version or SCORER_VERSION
+    version = scorer_version or SCORER_VERSION
     # Fail fast (0.4.5): if the scorer cannot run, the environment must not
     # load. Hosted Training's verifiers catches reward-function exceptions and
     # substitutes 0.0, so a missing CadQuery otherwise scores every rollout 0
@@ -259,11 +258,20 @@
             extra = [other, *extra]  # continuous stays visible as a diagnostic
         funcs += extra
         weights += [0.0] * len(extra)
-    rubric = vf.Rubric(funcs=funcs, weights=weights)
+    def bind(func):
+        @wraps(func)
+        def bound(*args, **reward_kwargs):
+            reward_kwargs["scorer_version"] = version
+            return func(*args, **reward_kwargs)
+        return bound
+    rubric = vf.Rubric(funcs=[bind(func) for func in funcs], weights=weights)
     kwargs.setdefault("eval_dataset", _build_eval_dataset(eval_tiers))
-    return vf.SingleTurnEnv(
+    environment = vf.SingleTurnEnv(
         dataset=_build_dataset(train_tiers),
         system_prompt=system_prompt(hints),
         rubric=rubric,
         **kwargs,
     )
+    environment.scorer_version = version
+    return environment
+
```

Prototype fact/high: named scorer callbacks in the actual local RubricGroups returned old=1.0, new=0.9 on shared state, then old=1.0 again. Attributes carried the respective versions. This checks installed local verifier behavior, not a remote hosted worker.

### B4. Exact spline representation is rejected as a wrong part

**Fact, high:** converting the correct solid's surfaces to NURBS eliminates detected bores:

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

from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
result=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())
```

Observed reward **0.0**; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `802.386047` mm3. Complete code/spec: [A044](#a044).

The same conversion on six train/dev specs, including the thinnest and smallest-margin plates, gave 0.0 in every case. They failed simple_through_holes, hole count, diameter, pattern, margin and R9; gen-0208 also failed is_plate. Every ordinary construction style for those specs passed.

Independent geometry proof for the synthetic part: original.cut(converted).Volume()=0.0 and converted.cut(original).Volume()=0.0; both valid. Analytical recovery found six planes and four cylinders with maximum reported conversion gap about 1.124e-14 mm. Adaptive integration gave 28003.606254159007 mm3 versus nominal 28003.60626231499, about 8.16e-6 mm3 apart numerically. Default NURBS mass integration was less accurate. Evidence: nurbs-proof.log. Validity alone does not prove exact mass integration.

**Opinion, moderate:** recognise geometry independently of surface storage class, strict-only to preserve 0.4.0. The following B1 helper excerpt is part of the same shared patch:

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ -450,7 +451,65 @@
     return load_brep(build_brep(code))
 
 
-def _z_aligned_cylinders(solid: Any) -> list[tuple[float, float, float, Any]]:
+def _analytic_adaptor(face: Any) -> Any:
+    """Recognise analytic geometry independently of its surface representation."""
+    from OCP.BRep import BRep_Tool
+    from OCP.BRepAdaptor import BRepAdaptor_Surface
+    from OCP.GeomAbs import GeomAbs_SurfaceType
+    from OCP.GeomAdaptor import GeomAdaptor_Surface
+    from OCP.GeomConvert import GeomConvert_SurfToAnaSurf
+    from OCP.Precision import Precision
+
+    adaptor = BRepAdaptor_Surface(face.wrapped)
+    if adaptor.GetType() in (GeomAbs_SurfaceType.GeomAbs_Plane,
+                             GeomAbs_SurfaceType.GeomAbs_Cylinder):
+        return adaptor
+    converter = GeomConvert_SurfToAnaSurf(BRep_Tool.Surface_s(face.wrapped))
+    analytical = converter.ConvertToAnalytical(Precision.Confusion_s())
+    if analytical is None:
+        return None
+    return GeomAdaptor_Surface(analytical)
+
+
+def _surface_conformance(solid: Any, bb: Any, holes: list[Hole]) -> bool:
+    """Every boundary must lie on an envelope plane or a recognised bore."""
+    from OCP.GeomAbs import GeomAbs_SurfaceType
+    from OCP.Precision import Precision
+
+    linear = 2 * Precision.Confusion_s()
+    angular = Precision.Angular_s()
+    limits = ((bb.xmin, bb.xmax), (bb.ymin, bb.ymax), (bb.zmin, bb.zmax))
+    for face in solid.Faces():
+        adaptor = _analytic_adaptor(face)
+        if adaptor is None:
+            return False
+        if adaptor.GetType() == GeomAbs_SurfaceType.GeomAbs_Plane:
+            plane = adaptor.Plane()
+            normal, origin = plane.Axis().Direction(), plane.Location()
+            n = (normal.X(), normal.Y(), normal.Z())
+            p = (origin.X(), origin.Y(), origin.Z())
+            axis = max(range(3), key=lambda k: abs(n[k]))
+            if any(abs(n[k]) > angular for k in range(3) if k != axis):
+                return False
+            if min(abs(p[axis] - edge) for edge in limits[axis]) > linear:
+                return False
+        elif adaptor.GetType() == GeomAbs_SurfaceType.GeomAbs_Cylinder:
+            cylinder = adaptor.Cylinder()
+            axis = cylinder.Axis()
+            direction, origin = axis.Direction(), axis.Location()
+            if abs(direction.X()) > angular or abs(direction.Y()) > angular:
+                return False
+            if not any(abs(origin.X() - h.x) <= linear
+                       and abs(origin.Y() - h.y) <= linear
+                       and abs(2 * cylinder.Radius() - h.diameter) <= linear
+                       for h in holes):
+                return False
+        else:
+            return False
+    return True
+
+
+def _z_aligned_cylinders(solid: Any, *, strict: bool = False) -> list[tuple[float, float, float, Any]]:
     """Exact kernel geometry for every Z-parallel cylindrical face."""
     from OCP.BRepAdaptor import BRepAdaptor_Surface
     from OCP.GeomAbs import GeomAbs_SurfaceType
```

Do not treat arbitrary splines, ellipses or cones as cylinders. Analytical recovery must stay at kernel precision and its resulting boundary must still conform. The six converted NURBS cases score 1.0 with zero raw residual in the prototype. General free-form recognition remains an integration risk.

### B5. Extra shape work changes legacy runtime behavior

**Fact, high:** version 0.4.0 still computes the new residual inside its execution deadline.

```python
import os
from cad_spec.measure import _get_worker, shutdown_worker
from cad_spec.rubric import score
from cad_spec.tasks import Spec, reference_solution
s = Spec("synthetic",80,60,6,6.5,10)
code = reference_solution(s)
os.environ["CAD_SPEC_EXEC_TIMEOUT"]="0.05"
_get_worker()  # warm kernel before the observation
r=score(code,s,version="0.4.0")  # branch; main's score(code,s) uses 0.4.0
print(r.reward,r.error,{c.name:c.passed for c in r.checks})
shutdown_worker()
```

At 0.05 s, separate main imports returned 1.0 with all 14 checks passing on 4/4 attempts, about 0.028 s each. Branch legacy imports returned 0.0, no checks, “model code exceeded 0.05s execution budget” on 4/4. At 0.075 s both passed, branch about 0.066 to 0.069 s. These are artificial stress budgets on a synthetic nominal part, not saved-corpus mismatches at 10 s. Evidence: deadline-main.jsonl and deadline-branch.jsonl.

There are ten new boolean cuts for four holes: four in each of the two ideals and two final differences. “Two more boolean operations” counts only the final comparisons. Constructor/build calls may add more internal work.

**Opinion, high:** transport strictness with each worker request and skip the new work entirely for legacy measurements. Do not add another module-global selector. B1 already threads the policy; the following excerpts are from the same shared diff:

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ -715,23 +779,29 @@
         + _count(topo, TopAbs_EDGE, TopAbs_FACE)
         + _count(topo, TopAbs_VERTEX, TopAbs_EDGE)
     )
-    holes, partial = _classify_cylinders(solid)
+    holes, partial = _classify_cylinders(solid, strict=strict)
     for h in holes:
         h.open = _bore_is_open(solid, h, bb.zmin, bb.zmax)
-    extra_volume, missing_volume = _shape_residual(solid, bb, holes)
+    extra_volume = missing_volume = None
+    surface_conformance = None
+    if strict:
+        extra_volume, missing_volume = _shape_residual(solid, bb, holes)
+        surface_conformance = _surface_conformance(solid, bb, holes)
+    def measured(value: float, digits: int = 4) -> float:
+        return value if strict else round(value, digits)
     return Measurements(
-        length=round(bb.xlen, 4),
-        width=round(bb.ylen, 4),
-        thickness=round(bb.zlen, 4),
-        volume=round(volume, 4),
+        length=measured(bb.xlen),
+        width=measured(bb.ylen),
+        thickness=measured(bb.zlen),
+        volume=measured(volume),
         solid_count=solid_count,
         holes=holes,
-        x_min=round(bb.xmin, 4),
-        x_max=round(bb.xmax, 4),
-        y_min=round(bb.ymin, 4),
-        y_max=round(bb.ymax, 4),
-        z_min=round(bb.zmin, 4),
-        z_max=round(bb.zmax, 4),
+        x_min=measured(bb.xmin),
+        x_max=measured(bb.xmax),
+        y_min=measured(bb.ymin),
+        y_max=measured(bb.ymax),
+        z_min=measured(bb.zmin),
+        z_max=measured(bb.zmax),
         partial_bores=partial,
         shell_count=_count(topo, TopAbs_SHELL),
         loose_count=loose,
@@ -739,12 +809,13 @@
         off_axis_bores=_off_axis_bore_count(solid),
         extra_volume=extra_volume,
         missing_volume=missing_volume,
+        surface_conformance=surface_conformance,
     )
 
 
-def _measure_code(code: str) -> Measurements:
+def _measure_code(code: str, *, strict: bool = False) -> Measurements:
     """Build and measure in THIS process (inproc and reuse modes)."""
-    return measure(load_brep(build_brep(code)))
+    return measure(load_brep(build_brep(code)), strict=strict)
 
 
 # --- isolated execution ------------------------------------------------------
@@ -897,7 +968,7 @@
         os.killpg(pid, signal.SIGKILL)
 
 
-def _run_forked(code: str, budget: float, mem_mb: int) -> tuple[str, Any]:
+def _run_forked(code: str, budget: float, mem_mb: int, *, strict: bool = False) -> tuple[str, Any]:
     """Run one rollout in a disposable forked child. Returns (status, payload).
 
     The child replies with b"O" + BREP bytes or b"E" + UTF-8 error text. The
@@ -995,14 +1066,14 @@
     if tag != b"O":
         return ("error", "rollout process returned a malformed result")
     try:
-        return ("ok", measure(load_brep(body)))
+        return ("ok", measure(load_brep(body), strict=strict))
     except BuildError as exc:
         return ("error", str(exc))
     except Exception as exc:
         return ("error", f"result geometry could not be measured: {type(exc).__name__}")
 
 
-def _run_reused(code: str, budget: float, mem_mb: int) -> tuple[str, Any]:
+def _run_reused(code: str, budget: float, mem_mb: int, *, strict: bool = False) -> tuple[str, Any]:
     """Run one rollout in this (persistent) process, in a fresh temp dir.
 
     `budget` is enforced by the parent, which kills this whole process;
@@ -1042,9 +1113,9 @@
         if kind == "stop":
             conn.send(("ok", None))
             return
-        code, budget, mem_mb = payload
+        code, budget, mem_mb, strict = payload
         try:
-            conn.send(run(code, budget, mem_mb))
+            conn.send(run(code, budget, mem_mb, strict=strict))
         except Exception as exc:  # report faults before dying
             conn.send(("error", f"worker fault: {type(exc).__name__}: {exc}"))
 
@@ -1078,9 +1149,9 @@
     def alive(self) -> bool:
         return self.proc.is_alive()
 
-    def call(self, code: str) -> Measurements:
+    def call(self, code: str, *, strict: bool = False) -> Measurements:
         try:
-            self.conn.send(("measure", (code, _exec_timeout(), _mem_limit_mb())))
+            self.conn.send(("measure", (code, _exec_timeout(), _mem_limit_mb(), strict)))
         except (BrokenPipeError, OSError) as exc:
             raise BuildError(f"scorer pipe broke: {exc}") from exc
         # In fork mode the worker enforces the budget itself and survives;
@@ -1158,7 +1229,7 @@
     return info
 
 
-def build_and_measure(completion: str) -> Measurements:
+def build_and_measure(completion: str, *, strict: bool = False) -> Measurements:
     """Extract code, run it isolated, measure the result.
 
     Raises BuildError when the model's code does not yield a part (a model
```

## 3. Recommended fixes

### R1. Replace exhaustive matching

**Fact, high:** _one_to_one is correct in the tested small assignments, including the crossing-assignment package case. Its proximity scan is O(4n), but its recursive enumeration has worst-case O(n^4) work for four expected positions. It does not stop after finding a full matching. Requirements are evaluated before gate failures return, so hole_count_sane does not protect the search.

Measurement-level stress reproduction, explicitly not an answer-produced B-rep exploit:

```python
from cad_spec.measure import Hole
from cad_spec.rubric import _one_to_one
positions=[(-30,-20),(-30,20),(30,-20),(30,20)]
holes=[Hole(6.5+i*.0001,x,y,6) for x,y in positions for i in range(40)]
print(_one_to_one(positions,holes,.1))  # observed 4
```

cost_probe.py injected these measurements into score. It returned 0.0 after gates failed, but spent 0.583479 s for 160 holes, 0.046620 s for 80 and 0.004083 s for 40. The injected Hole objects defaulted their endpoint fields to zero, so simple_through_holes failed even at n=1. This isolates requirement-path cost; it does not claim those values came from a solid. Real 16- and 64-added-bore attempts scored 0.0; 144 added bores exceeded the geometry deadline. I do not know whether a valid sub-deadline answer can trigger minutes of main-process matching. Many coaxial stepped bores are a plausible source, an inference not established here.

**Opinion, high:** use augmenting-path assignment, with four searches for four expected vertices, instead of enumerating every combination. Keep legacy verdict computation intact. This diff replaces the strict routine only:

```diff
--- a/environments/cad_spec/cad_spec/rubric.py
+++ b/environments/cad_spec/cad_spec/rubric.py
@@ -194,14 +194,19 @@
     """Largest number of expected positions matched to DISTINCT holes within tol."""
     near = [[i for i, h in enumerate(holes) if math.dist((h.x, h.y), e) <= tol + NUM_EPS] for e in expected]
 
-    def best(k: int, used: frozenset[int]) -> int:
-        if k == len(near):
-            return 0
-        skip = best(k + 1, used)
-        take = max((1 + best(k + 1, used | {i}) for i in near[k] if i not in used), default=0)
-        return max(skip, take)
-
-    return best(0, frozenset())
+    owner: dict[int, int] = {}
+
+    def augment(k: int, seen: set[int]) -> bool:
+        for i in near[k]:
+            if i in seen:
+                continue
+            seen.add(i)
+            if i not in owner or augment(owner[i], seen):
+                owner[i] = k
+                return True
+        return False
+
+    return sum(augment(k, set()) for k in range(len(near)))
 
 
 def _requirements(m: Measurements, spec: Spec, version: str) -> list[Check]:
```

### R2. Preserve residual-failure diagnostics

**Fact, high:** None residuals fail R9, not pass it. A 0.009 mm plate forces an ideal thinner than the shrink band. Against the normal 6 mm spec it scores 0.8 through R3 and R9:

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 0.009)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)
```

Observed reward **0.8**; failed checks `R3:thickness, R9:no_other_features`; extra `None`, missing `None` mm3. Complete code/spec: [A080](#a080).

The bare handler hides an explicit “envelope thinner than the band” error here. It also hides boolean failures, OCCT exceptions and programming errors inside its try. Imports above the try and rounding after it are not covered. NaN or positive infinity fails the <= comparison; volume is made absolute. I found no exception/None route to full credit.

**Opinion, high:** fail closed but preserve exception type and stage, preferably in Measurements/report diagnostics. A minimal logging-only patch, keeping reward semantics unchanged, is:

```diff
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ -686,7 +686,9 @@
     try:
         extra = volume(cut(solid.wrapped, ideal(SHAPE_BAND_MM)))
         missing = volume(cut(ideal(-SHAPE_BAND_MM), solid.wrapped))
-    except Exception:  # "could not compare" is a result, reported as None
+    except Exception as exc:  # still fail closed, but preserve the kernel failure
+        import logging
+        logging.getLogger(__name__).warning("shape residual failed: %s: %s", type(exc).__name__, exc)
         return None, None
     return round(extra, 6), round(missing, 6)
```

Default reuse mode bounds booleans through its worker deadline. Fork mode has the budget plus 10 s outer grace. In-process mode has no parent deadline. The “model code exceeded” error also covers trusted measurement work. The 144-hole timeout did not establish which stage took the time. No specifically residual-induced multi-minute hang was observed.

### R3. Make recorded versions mandatory throughout analysis

**Fact, high:** replay_eval selects the recorded supported scorer and refuses missing/unsupported versions. The five evaluations replay properly. It chooses the first meta record; conflicting meta records within one file can therefore be silently assigned the first version.

**Fact, high:** failure_modes still uses TOL=0.5 under 0.5.0 and lacks R5/R9 check-label fallback. This part scores 0.9 through R5 but is labelled “other”:

```python
# Add repository scripts/ to sys.path before importing failure_modes.
from cad_spec.tasks import Spec,reference_solution
from cad_spec.rubric import score
import failure_modes as f
s=Spec("synthetic",80,60,6,6.5,10)
code=reference_solution(s)+'\nresult=result.translate((.25,0,0))'
r=score(code,s,"0.5.0")
row={"completion":code,"tier":"L2","built":True,
     "checks":{c.name:c.passed for c in r.checks},"reward":r.reward}
print(r.reward,f.classify(row,s,None)[0])  # observed 0.9, other
print(f._checks_label({"R9:no_other_features":False}))  # observed other
```

The translation scores 1.0 with all checks passing under 0.4.0. metadata_probes.py wrote a versionless fixture with those legacy checks; failure_modes labelled its report 0.5.0 and exited 0. label_check accepted explicitly mixed 0.4.0/0.5.0 input files, used a supplied strict failure file and exited 0. replay_eval refused the missing-version fixture, exit 1. All fixtures were synthetic, not edited evaluations. Evidence: metadata-probes.log and mixed-label.md.

**Fact, high, source review:** verify_hub accepts explicit files but scores their rows with the installed current default, ignoring recorded metadata. Comparing a legacy file with a current package can report an intentional scorer change as a Hub mismatch. I did not install/download a separate Hub copy or exercise that live path. rescore intentionally updates recorded versions, compare_training pins 0.4.0, and run_baseline records the default it uses. Those choices are appropriate. summarize_results still has a check display list without R9 and aggregates versions rather than enforcing a uniform view; it needs an explicit version/display policy before new-version runs enter the public board.

**Opinion, high:** absent version means unknown; refuse it or require an explicit external override. Refuse mixed versions before making label reports. Use the selected version's classifier tolerance and add R5/R9 labels. Route Hub validation through the recorded version, supporting the older package signature when its current scorer is the requested one. These utility diffs were syntax-checked, not fully integration-tested. The classifier diff uses process-local tolerance for the one-shot CLI; a concurrent reusable classifier should pass it through helpers instead.

```diff
--- a/scripts/replay_eval.py
+++ b/scripts/replay_eval.py
@@ -37,7 +37,10 @@
     # Each file is replayed under the scorer version it was recorded with: a
     # replay asks "does that scorer still give that answer", never "what would
     # a newer scorer say".
-    version = next((r["meta"].get("scorer_version") for r in records if "meta" in r), None)
+    versions = {r["meta"].get("scorer_version") for r in records if "meta" in r}
+    if len(versions) != 1:
+        raise SystemExit(f"{path}: exactly one known scorer version is required")
+    version = next(iter(versions))
     if version not in SUPPORTED_VERSIONS:
         raise SystemExit(f"{path}: recorded scorer {version!r} cannot be replayed (supported: "
                          f"{', '.join(SUPPORTED_VERSIONS)})")
```

```diff
--- a/scripts/failure_modes.py
+++ b/scripts/failure_modes.py
@@ -54,14 +54,14 @@
 sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))
 
 from cad_spec.measure import BuildError, ScorerUnavailableError, build_and_measure, extract_code, require_cadquery
-from cad_spec.rubric import SCORER_VERSION
+from cad_spec.rubric import SCORER_VERSION, TOLERANCES
 from cad_spec.tasks import TASKS, Spec, edit_source, make_splits
 
 DETERMINISTIC = {"reference", "parser-copy", "parser-derive", "parser-template", "rev-a"}
 from degenerate import is_degenerate
 from summarize_results import load, run_arm, select_runs
 
-TOL = 0.5  # mm, same class as the rubric's position tolerance
+TOL = TOLERANCES[SCORER_VERSION].position
 UNFINISHED = ("API error", "degenerate loop", "cut off")
 NOT_BUILT = ("syntax error", "CadQuery API error", "geometry kernel failure", "Python error in model code",
              "no part produced", "timeout", "build failed")
@@ -73,7 +73,7 @@
     "holes misplaced (other)",
     "gate: single_solid", "gate: clean_solid", "gate: simple_through_holes", "gate: hole_count_sane",
     "gate: is_plate", "wrong plate size", "off Z datum", "wrong hole diameter", "wrong hole count",
-    "material off", "edge margin off", "other",
+    "material off", "edge margin off", "unrequested feature", "other",
 )
 # Last: an answer the classifier itself could not read (never silently dropped).
 ORDER = (*ORDER, "classifier error")
@@ -371,7 +371,9 @@
     order = (("R1:length", "wrong plate size"), ("R2:width", "wrong plate size"), ("R3:thickness", "wrong plate size"),
              ("R8:z_datum", "off Z datum"), ("R4b:hole_diameter", "wrong hole diameter"),
              ("R4a:hole_count", "wrong hole count"), ("R6:material", "material off"),
-             ("R7:edge_margin", "edge margin off"))
+             ("R7:edge_margin", "edge margin off"),
+             ("R5:hole_pattern", "holes misplaced (other)"),
+             ("R9:no_other_features", "unrequested feature"))
     for name, label in order:
         if checks.get(name) is False:
             return label
@@ -427,6 +429,7 @@
     ap.add_argument("--tiers", nargs="+", default=["L0", "L1", "L2", "L3", "L4"])
     ap.add_argument("--out", default=str(ROOT / "results"))
     args = ap.parse_args()
+    global TOL
     try:
         require_cadquery()
     except ScorerUnavailableError as exc:
@@ -444,11 +447,16 @@
     # THEIR scorer version, not the version of the scorer installed today.
     versions: set[str] = set()
     metas, groups, ends = load(args.paths)
+    recorded = {m.get("scorer_version") for m in metas.values()}
+    if len(recorded) != 1 or None in recorded or not recorded <= set(TOLERANCES):
+        raise SystemExit("known, identical scorer versions are required in every file")
+    version = next(iter(recorded))
+    TOL = TOLERANCES[version].position
     for (model, tier), run in sorted(select_runs(metas, groups, ends).items()):
         if tier not in args.tiers:
             continue
         arm_of[model] = run_arm(run["meta"])
-        versions.add(run["meta"].get("scorer_version") or SCORER_VERSION)
+        versions.add(run["meta"]["scorer_version"])
         max_tokens = run["meta"].get("max_tokens")
         for row in run["rows"]:
             if row.get("spec_id") not in specs:
```

```diff
--- a/scripts/label_check.py
+++ b/scripts/label_check.py
@@ -30,7 +30,7 @@
 ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))
 
-from cad_spec.rubric import SCORER_VERSION
+from cad_spec.rubric import SUPPORTED_VERSIONS
 from cad_spec.tasks import TASKS, edit_source, make_splits, prompt_for
 from summarize_results import load
 
@@ -53,11 +53,14 @@
     args = ap.parse_args()
 
     metas, _, _ = load(args.paths)
-    recorded = {m.get("scorer_version") for m in metas.values()} - {None}
-    version = recorded.pop() if len(recorded) == 1 else SCORER_VERSION
+    recorded = {m.get("scorer_version") for m in metas.values()}
+    if len(recorded) != 1 or None in recorded or not recorded <= set(SUPPORTED_VERSIONS):
+        raise SystemExit("known, identical scorer versions are required in every file")
+    version = next(iter(recorded))
     failures_path = Path(args.failures) if args.failures else ROOT / "results" / f"failure-modes-{version}.json"
     failures = json.loads(failures_path.read_text())
-    version = failures.get("scorer_version", version)
+    if failures.get("scorer_version") != version:
+        raise SystemExit("failure labels and answers have different or unknown scorer versions")
     pool = [r for r in failures["rows"] if r["label"] not in MECHANICAL and r["model"] not in DETERMINISTIC]
     if "run_id" not in (pool[0] if pool else {"run_id": 1}):
         raise SystemExit("this failure file predates run ids; rerun scripts/failure_modes.py first")
```

```diff
--- a/scripts/verify_hub.py
+++ b/scripts/verify_hub.py
@@ -63,18 +63,28 @@
     except ImportError:  # packages before 0.4.1 have no test split
         pass
 
+    import inspect
     rows, timeouts = [], 0
     for f in files:
         with open(f, encoding="utf-8") as fh:
+            recorded_version = None
             for line in fh:
                 if not line.strip():
                     continue
                 row = json.loads(line)
+                if "meta" in row:
+                    recorded_version = row["meta"].get("scorer_version")
+                    if recorded_version is None:
+                        raise SystemExit(f"{f}: scorer version is unknown")
+                    continue
                 if "meta" in row or "end" in row or row.get("spec_id") not in specs or "checks" not in row:
                     continue
                 if row.get("timeout"):
                     timeouts += 1
                     continue
+                if recorded_version is None:
+                    raise SystemExit(f"{f}: scorer version is unknown")
+                row["_recorded_scorer"] = recorded_version
                 rows.append(row)
     rows.sort(key=lambda r: (r.get("run_id", ""), r["tier"], r["spec_id"], r.get("rollout", 0)))
     if args.n and args.n < len(rows):
@@ -86,7 +96,13 @@
           f"({timeouts} timeout answers skipped)")
     mismatches = []
     for i, row in enumerate(rows, 1):
-        report = score(row.get("completion") or "", specs[row["spec_id"]])
+        version = row["_recorded_scorer"]
+        if "version" in inspect.signature(score).parameters:
+            report = score(row.get("completion") or "", specs[row["spec_id"]], version=version)
+        elif version == SCORER_VERSION:
+            report = score(row.get("completion") or "", specs[row["spec_id"]])
+        else:
+            raise SystemExit(f"installed scorer {SCORER_VERSION} cannot replay {version}")
         checks = {c.name: c.passed for c in report.checks}
         if abs(report.reward - row["reward"]) > 1e-9 or checks != row["checks"]:
             mismatches.append((row, report.reward, checks))
```

### R4. Add supplemental families and narrow the claims

**Fact, high:** the oracle declares independent 0.1 mm constants and labels Geometry parameters rather than importing scorer tolerances/results. That is useful independence. It is not an independent general solid inspector: it shares assumptions about internal closed cylinders, breakout treatment and volume identity. It uses minimum distance rather than independent one-to-one matching. Existing well-separated train/dev corners make that harmless in these generated cases, but the oracle does not validate the general matching algorithm.

The oracle marks R6/is_plate ambiguous for extras, and compares only gates when its own gates fail. Its 0.02 mm boundary guard dwarfs the rounding loophole. Zero false full credit is a correct count for these mutants, not proof about every wrong solid.

Missing families: broad sub-band pockets/bosses; sub-threshold deep slots/lugs; envelope absorption; tiny chamfers/fillets; rotations/draft/shear; scalar and diagonal rounding wedges; exact spline representation; loose geometry/compounds as alternative representations; matching explosions; per-instance scorer selection; deadline-dependent legacy behavior; missing/mixed metadata. Some have older hand-labelled coverage, but are absent from this mutation oracle.

method_sketch_extrude calls Workplane.rect().extrude(), not cq.Sketch. It tests a rectangular wire extrusion. bore_burr is a rectangular lug, not general burr morphology, and its +X placement causes the 26 extra hole-check disagreements. The membrane is a real blind-hole membrane; its name is supported. Clip/slot/pocket/cross-bore cases perform their stated cuts at the fixed sizes. The suite file never changed after its freeze commit.

Reproducing counterexamples to suite completeness: B1's pocket is 1.0, no failed checks, zero residuals despite being wrong; B4's exact conversion is 0.0 despite preserving the right part. Their code is reproduced above and in the appendix.

**Opinion, high:** keep the frozen suite and add a supplemental synthetic regression script and CI gate:

```diff
--- /dev/null
+++ b/scripts/test_scorer_contract.py
@@ -0,0 +1,19 @@
+"""Supplement the frozen suite with synthetic contract regressions."""
+from pathlib import Path
+import sys
+sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "environments/cad_spec"))
+from cad_spec.rubric import score
+from cad_spec.tasks import Spec, reference_solution
+
+S = Spec("synthetic-contract", 80, 60, 6, 6.5, 10)
+BASE = reference_solution(S)
+CASES = [
+    ("pocket", BASE + '\nresult=result.cut(cq.Workplane("XY").box(50,50,.0049).translate((0,0,2.99755)))', False),
+    ("slot", BASE + '\nresult=result.cut(cq.Workplane("XY").box(.0128,.0128,8))', False),
+    ("diagonal tolerance", BASE + '\nresult=result.translate((.060499,.080499,0))', False),
+    ("NURBS", BASE + '\nfrom OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert\nresult=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())', True),
+]
+if __name__ == "__main__":
+    for name, code, correct in CASES:
+        report = score(code, S)
+        assert (report.reward == 1.0) == correct, (name, report.summary)
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -27,6 +27,9 @@
       - name: Hand-labelled cases for scorer 0.5.0 (strict contract)
         working-directory: .
         run: python scripts/test_rubric_050.py
+      - name: Synthetic strict contract regressions
+        working-directory: .
+        run: python scripts/test_scorer_contract.py
       - name: Adversarial rubric harness
         working-directory: .
         run: python scripts/test_rubric.py
```

Documentation claims, checked against their referenced files:

| Location | Statement | Conclusion |
|---|---|---|
| README line 18 and lines 118-120 | Plate, four holes, nothing else within 0.1 mm | Clear product contract; implementation is unsound and incomplete on observed cases. |
| README lines 151-154 | A plate gives zero; every listed extra feature does not | Too strong: B1 gives those extras zero residual; B4 rejects equivalent geometry. |
| README lines 109-115; CHANGELOG lines 27-31 | Legacy kept exactly; measurement changes additive | Default-budget saved verdicts agree; added work can change deadline outcomes. |
| CHANGELOG lines 15-18 | Any material outside band fails; all named features rejected | Omits 0.001 mm3 volume allowance; small listed features still pass. |
| CHANGELOG lines 36-37 | Corner fillets and a shallow pocket now fail R9 | True for pinned sizes; 0.03 mm fillet and 0.0049 mm pocket pass. |
| README lines 20,145,159-162; CHANGELOG lines 23-26 | Finite-suite counts and numeric band/threshold/rounding | Supported as finite observations and actual implementation descriptions. |
| CHANGELOG lines 32-35 | Six changed verdicts; +41.7/+40.8 gains | Recomputed exactly; descriptive, not tuning evidence. |

README's threshold/band table is accurate, but does not make adjacent universal rejection claims true. The motivating saved gen-0021 notch case is fixed at its saved size: the hand-labelled run reports 0.9 through R9. Minimal documentation corrections for the current behavior follow. If repairs are adopted, rewrite around the final boundary check/version rather than publishing these as a stale description:

```diff
--- a/README.md
+++ b/README.md
@@ -149,8 +149,11 @@
 
 R9 builds the ideal part from what was measured (the envelope and the
 bores) and measures the material the answer has in excess and the material
-it lacks. A plate with bores gives exactly zero; a notch, slot, pocket,
-cross-bore, chamfer, fillet or a lug in a bore does not. Because the ideal
+it lacks. The frozen suite found zero residual for its analytic correct
+parts and positive residual for its enumerated extra features. This does
+not prove the strict contract: the band hides shallow features, the
+volume allowance admits small defects, and equivalent NURBS bores are
+not detected by scorer 0.5.0. Because the ideal
 comes from the measurement and not from the spec, a wrong dimension does not
 fail R9: each check still fails for one reason. The case that motivated it
 is a saved model answer with four notches through its edges that 0.4.0
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -13,8 +13,10 @@
   error of one grid step.
 - **New check R9, no other features.** The part is compared with its own
   ideal plate-with-bores, built from the measured envelope and bores; any
-  extra or missing material outside a 0.005 mm band fails it. Notches, slots,
-  pockets, cross-bores, chamfers, fillets and a lug in a bore are rejected.
+  extra or missing material outside a 0.005 mm band fails it only when its
+  measured volume exceeds 0.001 mm3. The frozen suite rejects its listed
+  notches, slots, pockets, cross-bores, chamfers, fillets and bore lugs;
+  smaller examples can still pass.
   The hole pattern is matched one hole per position. Ten requirements.
 - **Why:** the external audit of 3 October 2026 found a saved development
   answer with four notches through its edges that 0.4.0 scored 1.0. It is
```

**Opinion, moderate, constants:** the 0.005 mm comment cites rounding and being below the engineering tolerance; the 0.001 mm3 comment cites the suite's smallest defect around 0.1 mm3. Neither establishes numerical necessity. On 78 train/dev correct constructions with scratch analytical recovery, unbanded raw residuals were exactly zero; spline-conversion gaps were about 1e-14 mm. I would remove the blanket acceptance band and make boundary form decisive at kernel uncertainty. I would initially keep 0.001 mm3 solely as a residual numerical backstop with the independent surface check, then derive any replacement bound from complete train/dev construction and platform/kernel noise evidence. I do not know a universal nonzero volume-only threshold that enforces this contract. No proposed threshold or tolerance used test/replication geometry.

## 4. Reproduction table

All scripts ran from the actual requested worktree. Pytest ran from environments/cad_spec. The absolute venv interpreter, PYTHONPATH override, bytecode suppression, scratch TEMP/TMP, disabled pytest cache and scratch basetemp kept persistent writes under the audit output. Output paths below are under independent/ to preserve pre-existing artifacts.

| Command | Expected | Observed |
|---|---|---|
| `python scripts/test_rubric_050.py` | 55 passing cases | 55/55; exit 0; 8.823 s |
| `python scripts/test_rubric.py` | 37 passing legacy cases | 37/37; exit 0; 7.498 s |
| `(cd environments/cad_spec; python -m pytest -q -p no:cacheprovider --basetemp <scratch>)` | Tests pass | 125 passed, 12 platform skips; exit 0; pytest 55.38 s; command 57.783 s |
| `python scripts/validate_scorer.py --out <audit>/independent/validation` | 0/1646 wrong full credit, 0/720 correct rejected | 2366 rows, every row equal to committed JSON; 26 disagreements; summary 334.7 s vs committed 576.5 s |
| `python scripts/replay_eval.py <all five eval files> --out <audit>/independent/scratch/replay.json` | 961 answers, no mismatches | 961, 0 reward/check mismatches; exit 0; 76.8 s |
| `python scripts/scorer_sensitivity.py --out <audit>/independent/sensitivity` | Six changed verdicts; gains +41.7/+40.8 | Entire JSON equal to committed JSON; exit 0; 81.813 s |
| `CAD_SPEC_PKG=<main-ref>/environments/cad_spec python scripts/validate_scorer.py --out <audit>/independent/validation` | 1320/1646 wrong full credit, 0/720 correct rejected | Every row equal to committed old-scorer JSON; exit 1 expected for false full credit; 125.6 s vs committed 268.3 s |
| Git order and frozen-suite diff | Suite first; scorer second; sensitivity third; suite unchanged | 030fcd8 -> 3fa4296 -> e635d84 -> f5ca73a; suite blob equal at freeze/HEAD |
| Verdict blobs against main | Byte-identical recorded content | All four verdict blobs equal |

**Fact, high:** validation differences are only sandbox metadata and time. Current and old reports were produced under Windows reuse, not Linux fork. Every oracle/scorer reward, failed-check set, agreement flag and aggregate check count is identical. Current exact agreement: 2340/2366; old: 990/2366. Old exit 1 is the intended demonstration that the old scorer violates the strict contract.

The frozen-suite blob is `86fbc8faaa1f2191046e68c9d2dc5242b159af4a` at both 030fcd8 and HEAD. Git history proves commit order and absence of suite edits; it cannot prove an author's private experimentation history.

| Evaluation file | Rows | Recorded-0.4 full credit | Mismatches |
|---|---:|---:|---:|
| `adapter-test.jsonl` | 240 | 239 | 0 |
| `base-test.jsonl` | 240 | 169 | 0 |
| `adapter-rep.jsonl` | 240 | 237 | 0 |
| `base-rep-run2.jsonl` | 240 | 161 | 0 |
| `base-rep.jsonl` | 1 | 1 | 0 |

Run1 and replication verdict MD/JSON blobs respectively: `4aa041809e8e5565a935b9bdf82ec126d495f5b2`, `10f1a092bbef7d279bbd4099043e444e4c6fb8c3`, `b0638297d104a4a5b0c4037174a94e283a3dc904`, `263c3b427f955f89a27e9da80a7d2378c98d260a`. Each is equal at main and HEAD. Blob equality is byte equality of recorded content, regardless of checkout newline conversion.

| Sensitivity split | L2+L4 pairs | Recomputed gain | Changed base | Changed adapter |
|---|---:|---:|---:|---:|
| original test split | 120 | 41.666667 points | 2 | 0 |
| replication split | 120 | 40.833333 points | 3 | 1 |

Test and replication data were read only for deterministic replay/sensitivity/compatibility. They supplied no threshold, tolerance or attack geometry to the proposals.

## 5. Compatibility result

**Fact, high:** there were 4210 distinct train/dev programs after AST canonical deduplication. Stable SHA-256 ordering selected 2200: 109 train and 2091 dev. All 961 evaluation rows were added. Both scorers independently executed **3161** answers with no cross-answer geometry cache. Every reward, named check verdict and parsed flag agreed. No exceptions occurred. Check detail strings were not captured in the comparator payload; the “every check” claim concerns every named verdict, not text formatting.

Both versions timed out at default 10 s on index 648, spec gen-0169, source `results/rescored/0.4.0/20260923T164833Z_qwen2.5-coder_1.5b.jsonl`, canonical-program SHA-256 `281a85a98c7ad0f3b60a3109b52051c0fe157f5bcad17beec4f98dc1c53645dd`. This program stacks over 2000 cylinder shapes instead of drilling. Both returned 0.0 with no checks. No selected saved answer newly timed out or raised.

Time summed per answer: main **133.802679 s**, branch **280.646778 s**. Mean including startup and the shared timeout: **42.329225 ms** vs **88.784175 ms**, factor **2.097468**. Median: **38.974500 ms** vs **101.106900 ms**. Other deterministic checks overlapped this run, so it is observational timing, not a controlled benchmark. B5's sequential warmed synthetic experiment independently confirms the extra-work mechanism.

Selectable legacy reward/check logic agrees on this saved sample. The environment selector and shared measurement deadline prevent the stronger universal claim that legacy behavior is unchanged.

## 6. Attack table

**Fact, high:** every row below is an observed execution on the unmodified branch, version 0.5.0. Complete snippets/specs follow in the appendix. `n/a` means no Measurements returned; None/None means an explicit failed residual comparison. “No failed checks” on a zero reward with a build error is not a passing part. Exact tolerance endpoints, coincident re-drilling, one-solid compounds and harmless unions are controls. NURBS conversion is a correct-geometry control that falsely fails.

Three initial deep_narrow_slot cases contained an extra closing parenthesis. Their syntax-error zeros are retained as harness mistakes. Corrected fixed_deep_slot rows provide the actual geometry results; the invalid snippets are not evidence of rejection of intended geometry.

| Code | Attempt / spec | Reward | Failed checks | Extra mm3 | Missing mm3 | Error or interpretation |
|---|---|---:|---|---:|---:|---|
| [A001](#a001) | `nominal` / synthetic | 1.0 | none | 0.0 | 0.0 | Correct control |
| [A002](#a002) | `broad_pocket_0.001` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A003](#a003) | `broad_pocket_0.0049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A004](#a004) | `broad_pocket_0.005` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A005](#a005) | `broad_pocket_0.0051` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.25 |  |
| [A006](#a006) | `broad_pocket_0.006` / synthetic | 0.9 | R9:no_other_features | 0.0 | 2.5 |  |
| [A007](#a007) | `broad_pocket_0.01` / synthetic | 0.9 | R9:no_other_features | 0.0 | 12.5 |  |
| [A008](#a008) | `boss_0.0049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A009](#a009) | `boss_0.0051` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.426546 |  |
| [A010](#a010) | `boss_0.01` / synthetic | 0.9 | R9:no_other_features | 0.0 | 21.327295 |  |
| [A011](#a011) | `boss_0.1` / synthetic | 0.0 | gate:simple_through_holes, R9:no_other_features | 0.0 | 405.218613 |  |
| [A012](#a012) | `edge_notch_0.0049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A013](#a013) | `edge_notch_0.0051` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.04193 |  |
| [A014](#a014) | `edge_notch_0.01` / synthetic | 0.9 | R9:no_other_features | 0.0 | 2.0965 |  |
| [A015](#a015) | `small_pocket_0.005` / synthetic | 1.0 | none | 0.0 | 1.2e-05 |  |
| [A016](#a016) | `small_pocket_0.02` / synthetic | 1.0 | none | 0.0 | 0.000198 |  |
| [A017](#a017) | `small_pocket_0.1` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.00495 |  |
| [A018](#a018) | `deep_narrow_slot_0.039` / synthetic | 0.0 | none | n/a | n/a | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |
| [A019](#a019) | `deep_narrow_slot_0.041` / synthetic | 0.0 | none | n/a | n/a | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |
| [A020](#a020) | `deep_narrow_slot_0.05` / synthetic | 0.0 | none | n/a | n/a | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |
| [A021](#a021) | `side_tab_0.0049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A022](#a022) | `top_lip_0.0049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A023](#a023) | `side_tab_0.0051` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.023954 |  |
| [A024](#a024) | `top_lip_0.0051` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.458587 |  |
| [A025](#a025) | `side_tab_0.01` / synthetic | 0.9 | R9:no_other_features | 0.0 | 1.1977 |  |
| [A026](#a026) | `top_lip_0.01` / synthetic | 0.9 | R9:no_other_features | 0.0 | 22.929345 |  |
| [A027](#a027) | `rotate_Z_0.0001` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A028](#a028) | `rotate_X_0.0001` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 795.080314 |  |
| [A029](#a029) | `rotate_Z_0.001` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A030](#a030) | `rotate_X_0.001` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 795.205412 |  |
| [A031](#a031) | `rotate_Z_0.01` / synthetic | 0.9 | R9:no_other_features | 0.0 | 3.783666 |  |
| [A032](#a032) | `rotate_X_0.01` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 809.680284 |  |
| [A033](#a033) | `rotate_Z_0.05` / synthetic | 0.9 | R9:no_other_features | 0.0 | 44.22307 |  |
| [A034](#a034) | `rotate_X_0.05` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 1001.954205 |  |
| [A035](#a035) | `draft_0.001` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A036](#a036) | `draft_0.01` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A037](#a037) | `draft_0.1` / synthetic | 0.9 | R9:no_other_features | 0.0 | 2.393697 |  |
| [A038](#a038) | `sheared_0.004` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A039](#a039) | `sheared_0.02` / synthetic | 0.9 | R9:no_other_features | 0.0 | 4.040386 |  |
| [A040](#a040) | `cone_0.001` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 795.311076 |  |
| [A041](#a041) | `cone_0.01` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 797.51528 |  |
| [A042](#a042) | `ellipse` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 797.512784 |  |
| [A043](#a043) | `polygon_128` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 794.747158 |  |
| [A044](#a044) | `nurbs_exact` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features | 0.0 | 802.386047 | Correct geometry control; false rejection |
| [A045](#a045) | `countersink_0.0049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A046](#a046) | `countersink_0.01` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A047](#a047) | `fifth_bore` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A048](#a048) | `coincident_bore` / synthetic | 1.0 | none | 0.0 | 0.0 | Coincident cut; no change |
| [A049](#a049) | `overlap_bore_0.0004` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A050](#a050) | `overlap_bore_0.004` / synthetic | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | 0.0 | 198.922344 |  |
| [A051](#a051) | `overlap_bore_0.01` / synthetic | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | 0.0 | 199.155954 |  |
| [A052](#a052) | `coaxial_step` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count | 0.0 | 0.0 |  |
| [A053](#a053) | `probe_lug_y0_d0.004` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A054](#a054) | `probe_lug_y0_d0.05` / synthetic | 1.0 | none | 1.8e-05 | 0.0 |  |
| [A055](#a055) | `probe_lug_y0.3_d0.004` / synthetic | 1.0 | none | 0.0 | 0.0 | Union inside existing material; no defect |
| [A056](#a056) | `probe_lug_y0.3_d0.05` / synthetic | 1.0 | none | 1.2e-05 | 0.0 |  |
| [A057](#a057) | `probe_notch` / synthetic | 1.0 | none | 0.0 | 4e-06 |  |
| [A058](#a058) | `compound_one` / synthetic | 1.0 | none | 0.0 | 0.0 | Correct one-solid compound |
| [A059](#a059) | `second_solid_bore` / synthetic | 0.0 | gate:single_solid, gate:simple_through_holes | 0.000314 | 0.0 |  |
| [A060](#a060) | `second_solid_outside` / synthetic | 0.0 | gate:single_solid, R1:length, R7:edge_margin, R9:no_other_features | 0.0 | 361.1368 |  |
| [A061](#a061) | `loose_face` / synthetic | 0.0 | gate:clean_solid, R9:no_other_features | None | None |  |
| [A062](#a062) | `loose_edge` / synthetic | 0.0 | gate:clean_solid, R9:no_other_features | None | None |  |
| [A063](#a063) | `length_0.1` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A064](#a064) | `diameter_0.1` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A065](#a065) | `z_datum_0.1` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A066](#a066) | `length_0.100001` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A067](#a067) | `diameter_0.100001` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A068](#a068) | `z_datum_0.100001` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A069](#a069) | `length_0.10004` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A070](#a070) | `diameter_0.10004` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A071](#a071) | `z_datum_0.10004` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A072](#a072) | `length_0.1001` / synthetic | 0.9 | R1:length | 0.0 | 0.0 |  |
| [A073](#a073) | `diameter_0.1001` / synthetic | 0.9 | R4b:hole_diameter | 0.0 | 0.0 |  |
| [A074](#a074) | `z_datum_0.1001` / synthetic | 0.9 | R8:z_datum | 0.0 | 0.0 |  |
| [A075](#a075) | `centres_0.1` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A076](#a076) | `centres_0.1004` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A077](#a077) | `centres_0.10049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A078](#a078) | `centres_0.1005` / synthetic | 0.9 | R5:hole_pattern | 0.0 | 0.0 |  |
| [A079](#a079) | `centres_0.101` / synthetic | 0.9 | R5:hole_pattern | 0.0 | 0.0 |  |
| [A080](#a080) | `residual_None_thin` / synthetic | 0.8 | R3:thickness, R9:no_other_features | None | None |  |
| [A081](#a081) | `many_bores_16` / synthetic | 0.0 | gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A082](#a082) | `many_bores_64` / synthetic | 0.0 | gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A083](#a083) | `many_bores_144` / synthetic | 0.0 | none | n/a | n/a | model code exceeded 10s execution budget |
| [A084](#a084) | `threshold_through_slot_0.0128` / synthetic | 1.0 | none | 0.0 | 0.000981 |  |
| [A085](#a085) | `threshold_through_slot_0.01295` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.001005 |  |
| [A086](#a086) | `threshold_through_slot_0.013` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.001012 |  |
| [A087](#a087) | `threshold_through_slot_0.0131` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.001028 |  |
| [A088](#a088) | `two_broad_pockets_0.0049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A089](#a089) | `two_broad_pockets_0.005` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A090](#a090) | `six_skin_pockets` / synthetic | 0.0 | gate:single_solid | 0.0 | 0.0 |  |
| [A091](#a091) | `actual_probe_lug_0.163` / synthetic | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | 0.0 | 198.766538 |  |
| [A092](#a092) | `actual_probe_lug_0.17` / synthetic | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | 0.0 | 198.766536 |  |
| [A093](#a093) | `actual_probe_lug_0.2` / synthetic | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features | 0.0 | 198.766524 |  |
| [A094](#a094) | `tiny_fifth_0.005` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A095](#a095) | `hidden_fifth_0.005` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A096](#a096) | `tiny_fifth_0.006` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A097](#a097) | `hidden_fifth_0.006` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A098](#a098) | `tiny_fifth_0.007` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A099](#a099) | `hidden_fifth_0.007` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A100](#a100) | `tiny_fifth_0.01` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A101](#a101) | `hidden_fifth_0.01` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A102](#a102) | `bore_annular_membrane` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter | 0.000198 | 0.0 |  |
| [A103](#a103) | `top_chamfer_0.0049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A104](#a104) | `top_chamfer_0.0051` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A105](#a105) | `top_chamfer_0.01` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A106](#a106) | `corner_fillet_0.001` / synthetic | 0.0 | gate:clean_solid | 0.0 | 0.0 |  |
| [A107](#a107) | `corner_fillet_0.005` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A108](#a108) | `corner_fillet_0.02` / synthetic | 1.0 | none | 0.0 | 3.6e-05 |  |
| [A109](#a109) | `fixed_deep_slot_0.039` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.009111 |  |
| [A110](#a110) | `fixed_deep_slot_0.041` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.010069 |  |
| [A111](#a111) | `fixed_deep_slot_0.05` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.014975 |  |
| [A112](#a112) | `hide_fifth_r0.003_h0.02` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A113](#a113) | `hide_fifth_r0.003_h0.1` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A114](#a114) | `hide_fifth_r0.005_h0.02` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A115](#a115) | `hide_fifth_r0.005_h0.1` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A116](#a116) | `hide_fifth_r0.007_h0.02` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A117](#a117) | `hide_fifth_r0.007_h0.1` / synthetic | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin | 0.0 | 0.0 |  |
| [A118](#a118) | `largest_skin_gen-0032` / gen-0032 | 1.0 | none | 0.0 | 0.0 |  |
| [A119](#a119) | `largest_skin_gen-0215` / gen-0215 | 1.0 | none | 0.0 | 0.0 |  |
| [A120](#a120) | `fillet_0.025` / synthetic | 1.0 | none | 0.0 | 0.000271 |  |
| [A121](#a121) | `fillet_0.03` / synthetic | 1.0 | none | 0.0 | 0.000735 |  |
| [A122](#a122) | `fillet_0.04` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.002376 |  |
| [A123](#a123) | `fillet_0.05` / synthetic | 0.9 | R9:no_other_features | 0.0 | 0.004991 |  |
| [A124](#a124) | `annular_bridge_2e-05` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter | 0.000495 | 0.0 |  |
| [A125](#a125) | `annular_bridge_3e-05` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter | 0.000742 | 0.0 |  |
| [A126](#a126) | `annular_bridge_4e-05` / synthetic | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter | 0.000989 | 0.0 |  |
| [A127](#a127) | `diagonal_rounding` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A128](#a128) | `length_0.100049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A129](#a129) | `diameter_0.100049` / synthetic | 1.0 | none | 0.0 | 0.0 |  |
| [A130](#a130) | `margin_0.1004` / synthetic | 1.0 | none | 0.0 | 0.0 |  |

**Fact, high, +X probe:** on the 6.5 mm bore its inset is 0.1625 mm. A 0.163, 0.17 or 0.2 mm lug suppresses the nominal bore, scores 0.7 and fails count, pattern and R9. Missing residual is about 198.7665 mm3 because the reconstructed ideal now fills the omitted bore. Shallow lugs do not touch that probe; tiny lugs/notches pass via the residual allowance. I did not achieve full credit by suppressing a nominal bore or by hiding the tiny fifth bores tried. The attempted fifth bores were counted and lost credit.

Cones, ellipses, polygons, X rotations, second solids and loose faces/edges were rejected. The repeated coincident cut changes no material. A 0.0004 mm overlapping nominal cut changes circular form and passes inside the band. Small Z rotations, draft and shear pass; X rotation as small as 0.0001 degree loses Z-bore recognition. The compound with a loose plane tests zero-thickness sheet geometry; the one-solid compound remains a correct representation.

## 7. False rejections

**Fact, high:** six train/dev specs were selected: global thinnest, smallest margin, largest area, first dev, first train and last dev, removing duplicates. Twelve ordinary construction styles each passed all six; exact NURBS conversion failed all six. An additional two-half-arc circular-hole construction passed. Thus 79 correct-style executions produced 73 full-credit results and six false rejections.

| Spec | L x W x T mm | Bore mm | Margin mm |
|---|---|---:|---:|
| gen-0215 | 168.0 x 78.5 x 3.0 | 8.0 | 21.5 |
| gen-0065 | 147.5 x 32.5 x 5.5 | 4.0 | 5.0 |
| gen-0032 | 214.0 x 150.0 x 10.5 | 9.0 | 8.0 |
| gen-0208 | 43.0 x 36.0 x 6.5 | 8.5 | 7.0 |
| gen-0001 | 74.5 x 81.0 x 4.5 | 10.5 | 24.5 |
| gen-0037 | 207.0 x 93.5 x 3.0 | 6.0 | 15.0 |
| synthetic | 80 x 60 x 6 | 6.5 | 10 |

gen-0215 is the 3.0 mm thinnest plate; gen-0065 has the 5.0 mm smallest edge margin. These are train/dev extremes.

| Style | Cases | Reward(s) | Failed checks |
|---|---:|---|---|
| reference | 6 | 1.0 | none |
| Sketch | 6 | 1.0 | none |
| polyline | 6 | 1.0 | none |
| cutThruAll | 6 | 1.0 | none |
| explicit_depth | 6 | 1.0 | none |
| union_halves | 6 | 1.0 | none |
| imprinted_halves | 6 | 1.0 | none |
| mirror | 6 | 1.0 | none |
| translate_chain | 6 | 1.0 | none |
| Solid_primitives | 6 | 1.0 | none |
| clean | 6 | 1.0 | none |
| float_coordinates | 6 | 1.0 | none |
| nurbs_exact | 6 | 0.0 | R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features, gate:is_plate, gate:simple_through_holes |
| arc_circle | 1 | 1.0 | none |

Sketch here uses actual cq.Sketch().rect(). Polyline extrusion, cutThruAll, explicit-depth hole, union of halves, mirror, translate chains, Solid primitives, clean and 55.749999999 coordinates pass. The imprinted-halves case uses clean=False union/cuts to preserve split planar and bore faces, testing area/interval grouping. cskHole misuse was excluded from correct labels. All code is appended, and B4 contains the independent NURBS equivalence proof.

## 8. What I could not verify

- **Fact, high:** Linux fork hardening, GL fallback and the 12 skipped platform tests were not exercised on Windows. No new Linux environment was installed.
- **Fact, high:** live hosted serialization, separately installed Hub code and remote training workers were not exercised. Local actual verifier callbacks were checked.
- **Inference, moderate:** worst-case matching cost occurs after gates, but the stress case injected Measurements. I do not know whether an answer-produced B-rep reaches minute-scale cost inside the geometry deadline.
- **Fact, high:** 144 extra bores hit 10 s. Its expensive stage was not isolated. No specifically residual-induced multi-minute hang was proved.
- **Fact, high:** the report gives an achieved sub-band defect above 300 mm3 and a fixed-ideal layer bound, not a universal maximum.
- **Opinion, moderate:** scratch proposals need complete frozen-suite, 3161-answer legacy, package, lint/type and Windows/Linux validation after integration. Existing monkeypatched tests need the new strict keyword. Displayed R9 band wording must be changed to the actual unbanded backstop and surface test. No claim of merge-ready fixes is made.
- **Fact, high:** compatibility captured all named verdicts/rewards, not diagnostic-detail byte identity, and is not exhaustive over every possible program. The tight-budget synthetic difference disproves universal runtime compatibility.

## 9. Appendix: commands run, in order

Significant start-order entry points follow. Read-only Get-Content and rg searches occurred between them. Background runs overlapped. Exact reproduction argv, cwd, exit and timing are preserved in independent/scratch/commands.jsonl. All Python commands used the absolute venv executable with -B and the actual worktree cwd.

```powershell
Get-Location
Get-Command python, bash, wsl -ErrorAction SilentlyContinue
git status --short
git log -6 --oneline
rg --files -g AGENTS.md -g '*cadspec*'
python -c "import sys; print(sys.executable); import cadquery"
wsl --list --quiet
Get-Content C:/Users/bgare/cadspec.sh
New-Item -ItemType Directory -Force C:/Users/bgare/cad-spec-audit-out/scorer-0.5/scratch
$env:PYTHONPATH='C:/Users/bgare/dev/cad-spec-audit/environments/cad_spec'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
& C:/Users/bgare/dev/cad-spec-env/environments/cad_spec/.venv/Scripts/python.exe -c "import cad_spec.rubric as r; import cadquery; print(r.__file__,r.SCORER_VERSION,cadquery.__version__)"
git worktree add C:/Users/bgare/cad-spec-audit-out/scorer-0.5/scratch/main-ref 7c17439
# Target already existed; nothing was overwritten or removed.
git -C C:/Users/bgare/cad-spec-audit-out/scorer-0.5/scratch/main-ref rev-parse HEAD
# Verified at 7c17439a84529417d4516882b4034aa148c86017.
```

Scratch scripts, in start order:

```text
independent_run_A.py
independent_run_compat.py
independent_run_attacks.py
independent_run_extra.py
focused.py
review_probes.py       # first callback-index inspection failed
review_probes.py       # corrected registered reward function
nurbs_proof.py
cost_probe.py
deadline_probe.py
make_proposals.py
check_proposals.py     # callback lookup corrected later
metadata_probes.py
check_proposals.py     # located named callback in RubricGroup
recommended_proposals.py
make_proposals.py      # kernel bbox-padding correction
check_proposals.py
rounding_extra.py
proposed_calibration.py
coverage_proposals.py
report_shared.py, report_blockers.py, report_recommendations.py, report_results.py
write_report.py
```

The corrected scripts used for final numbers are preserved. The failed first callback lookups and invalid slot snippets were harness errors, not production failures. An initial single-command report-generator write exceeded the Windows command-length limit and created no file; modular writes then succeeded. Existing original scratch runners were preserved.

History commands, interleaved with the checks above:

```text
git show --stat 030fcd8
git show --stat e635d84
git diff 030fcd8 HEAD -- scripts/validate_scorer.py
git log --format='%h %s' -- scripts/validate_scorer.py
git rev-parse 030fcd8:scripts/validate_scorer.py HEAD:scripts/validate_scorer.py
git diff 7c17439 HEAD -- results/training/run1/verdict.json results/training/run1/verdict.md results/training/replication1/verdict.json results/training/replication1/verdict.md
git rev-parse 7c17439:results/training/run1/verdict.md HEAD:results/training/run1/verdict.md 7c17439:results/training/run1/verdict.json HEAD:results/training/run1/verdict.json 7c17439:results/training/replication1/verdict.md HEAD:results/training/replication1/verdict.md 7c17439:results/training/replication1/verdict.json HEAD:results/training/replication1/verdict.json
git rev-parse --abbrev-ref HEAD
git diff --stat
git status --short
```

Exact reproduction command ledger:

```json

{"name": "import", "cmd": ["C:\\Users\\bgare\\dev\\cad-spec-env\\environments\\cad_spec\\.venv\\Scripts\\python.exe", "-B", "-c", "import cad_spec.rubric as r; import cadquery; print(r.__file__,r.SCORER_VERSION,cadquery.__version__)"], "cwd": "C:\\Users\\bgare\\dev\\cad-spec-audit", "exit": 0, "seconds": 1.943985200006864}

{"name": "test050", "cmd": ["C:\\Users\\bgare\\dev\\cad-spec-env\\environments\\cad_spec\\.venv\\Scripts\\python.exe", "-B", "scripts/test_rubric_050.py"], "cwd": "C:\\Users\\bgare\\dev\\cad-spec-audit", "exit": 0, "seconds": 8.822959900004207}

{"name": "test040", "cmd": ["C:\\Users\\bgare\\dev\\cad-spec-env\\environments\\cad_spec\\.venv\\Scripts\\python.exe", "-B", "scripts/test_rubric.py"], "cwd": "C:\\Users\\bgare\\dev\\cad-spec-audit", "exit": 0, "seconds": 7.497816499992041}

{"name": "pytest", "cmd": ["C:\\Users\\bgare\\dev\\cad-spec-env\\environments\\cad_spec\\.venv\\Scripts\\python.exe", "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp", "C:\\Users\\bgare\\cad-spec-audit-out\\scorer-0.5\\independent\\scratch\\pytest-temp"], "cwd": "C:\\Users\\bgare\\dev\\cad-spec-audit\\environments\\cad_spec", "exit": 0, "seconds": 57.78271549999772}

{"name": "validation", "cmd": ["C:\\Users\\bgare\\dev\\cad-spec-env\\environments\\cad_spec\\.venv\\Scripts\\python.exe", "-B", "scripts/validate_scorer.py", "--out", "C:\\Users\\bgare\\cad-spec-audit-out\\scorer-0.5\\independent\\validation"], "cwd": "C:\\Users\\bgare\\dev\\cad-spec-audit", "exit": 0, "seconds": 337.26903599999787}

{"name": "replay", "cmd": ["C:\\Users\\bgare\\dev\\cad-spec-env\\environments\\cad_spec\\.venv\\Scripts\\python.exe", "-B", "scripts/replay_eval.py", "C:\\Users\\bgare\\dev\\cad-spec-audit\\results\\training\\run1\\eval\\adapter-test.jsonl", "C:\\Users\\bgare\\dev\\cad-spec-audit\\results\\training\\run1\\eval\\base-test.jsonl", "C:\\Users\\bgare\\dev\\cad-spec-audit\\results\\training\\replication1\\eval\\adapter-rep.jsonl", "C:\\Users\\bgare\\dev\\cad-spec-audit\\results\\training\\replication1\\eval\\base-rep-run2.jsonl", "C:\\Users\\bgare\\dev\\cad-spec-audit\\results\\training\\replication1\\eval\\base-rep.jsonl", "--out", "C:\\Users\\bgare\\cad-spec-audit-out\\scorer-0.5\\independent\\scratch\\replay.json"], "cwd": "C:\\Users\\bgare\\dev\\cad-spec-audit", "exit": 0, "seconds": 77.08150259999093}

{"name": "sensitivity", "cmd": ["C:\\Users\\bgare\\dev\\cad-spec-env\\environments\\cad_spec\\.venv\\Scripts\\python.exe", "-B", "scripts/scorer_sensitivity.py", "--out", "C:\\Users\\bgare\\cad-spec-audit-out\\scorer-0.5\\independent\\sensitivity"], "cwd": "C:\\Users\\bgare\\dev\\cad-spec-audit", "exit": 0, "seconds": 81.81331209999917}

{"name": "validation040", "cmd": ["C:\\Users\\bgare\\dev\\cad-spec-env\\environments\\cad_spec\\.venv\\Scripts\\python.exe", "-B", "scripts/validate_scorer.py", "--out", "C:\\Users\\bgare\\cad-spec-audit-out\\scorer-0.5\\independent\\validation"], "cwd": "C:\\Users\\bgare\\dev\\cad-spec-audit", "exit": 1, "seconds": 127.70181820000289}

```

The compatibility driver imports main from scratch/main-ref/environments/cad_spec and branch from the actual requested worktree, in independent subprocesses. It preserves the program manifest, both result streams and summary. Metadata probe command/stdout/stderr/exit records are preserved separately in metadata-probes.log. Benchmark/deadline scripts state their artificial conditions. TEMP/TMP and pytest basetemp were under independent/scratch. Inspection commands read scorer modules, scripts, tests, README, CHANGELOG, CI, prior audit and the installed verifier/kernel source/docstrings; no network calls were used.

### Attack snippets and observed reports

Each completion below is complete code, to score with Spec(**spec), version 0.5.0. These specs are synthetic or train/dev. Results below are from the unmodified branch, not the prototypes.

### A001

`nominal`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A002

`broad_pocket_0.001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(50,50,0.001).translate((0,0,2.9995)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A003

`broad_pocket_0.0049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(50,50,0.0049).translate((0,0,2.99755)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A004

`broad_pocket_0.005`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(50,50,0.005).translate((0,0,2.9975)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A005

`broad_pocket_0.0051`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(50,50,0.0051).translate((0,0,2.99745)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.25` mm3; error `None`.

### A006

`broad_pocket_0.006`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(50,50,0.006).translate((0,0,2.997)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `2.5` mm3; error `None`.

### A007

`broad_pocket_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(50,50,0.01).translate((0,0,2.995)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `12.5` mm3; error `None`.

### A008

`boss_0.0049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(20,20,0.0059).translate((0,0,3.00195)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A009

`boss_0.0051`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(20,20,0.0061).translate((0,0,3.00205)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.426546` mm3; error `None`.

### A010

`boss_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(20,20,0.011).translate((0,0,3.0045)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `21.327295` mm3; error `None`.

### A011

`boss_0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(20,20,0.101).translate((0,0,3.0495)))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R9:no_other_features`; extra `0.0`, missing `405.218613` mm3; error `None`.

### A012

`edge_notch_0.0049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(70,0.0049,8).translate((0,29.99755,0)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A013

`edge_notch_0.0051`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(70,0.0051,8).translate((0,29.99745,0)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.04193` mm3; error `None`.

### A014

`edge_notch_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(70,0.01,8).translate((0,29.995,0)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `2.0965` mm3; error `None`.

### A015

`small_pocket_0.005`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.005,0.005,1).translate((0,0,3)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `1.2e-05` mm3; error `None`.

### A016

`small_pocket_0.02`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.02,0.02,1).translate((0,0,3)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.000198` mm3; error `None`.

### A017

`small_pocket_0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.1,0.1,1).translate((0,0,3)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.00495` mm3; error `None`.

### A018

`deep_narrow_slot_0.039`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.039,0.039,6)))
```

Observed reward `0.0`; failed checks `none`; extra `n/a`, missing `n/a` mm3; error `execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11)`.

### A019

`deep_narrow_slot_0.041`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.041,0.041,6)))
```

Observed reward `0.0`; failed checks `none`; extra `n/a`, missing `n/a` mm3; error `execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11)`.

### A020

`deep_narrow_slot_0.05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.05,0.05,6)))
```

Observed reward `0.0`; failed checks `none`; extra `n/a`, missing `n/a` mm3; error `execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11)`.

### A021

`side_tab_0.0049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.0059,20,6).translate((40.00195,0,0)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A022

`top_lip_0.0049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(80,1,0.0059).translate((0,29.5,3.00195)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A023

`side_tab_0.0051`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.0061,20,6).translate((40.00205,0,0)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.023954` mm3; error `None`.

### A024

`top_lip_0.0051`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(80,1,0.0061).translate((0,29.5,3.00205)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.458587` mm3; error `None`.

### A025

`side_tab_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.011,20,6).translate((40.0045,0,0)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `1.1977` mm3; error `None`.

### A026

`top_lip_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(80,1,0.011).translate((0,29.5,3.0045)))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `22.929345` mm3; error `None`.

### A027

`rotate_Z_0.0001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.rotate((0,0,0),(0,0,1),0.0001)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A028

`rotate_X_0.0001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.rotate((0,0,0),(1,0,0),0.0001)
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `795.080314` mm3; error `None`.

### A029

`rotate_Z_0.001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.rotate((0,0,0),(0,0,1),0.001)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A030

`rotate_X_0.001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.rotate((0,0,0),(1,0,0),0.001)
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `795.205412` mm3; error `None`.

### A031

`rotate_Z_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.rotate((0,0,0),(0,0,1),0.01)
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `3.783666` mm3; error `None`.

### A032

`rotate_X_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.rotate((0,0,0),(1,0,0),0.01)
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `809.680284` mm3; error `None`.

### A033

`rotate_Z_0.05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.rotate((0,0,0),(0,0,1),0.05)
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `44.22307` mm3; error `None`.

### A034

`rotate_X_0.05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.rotate((0,0,0),(1,0,0),0.05)
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `1001.954205` mm3; error `None`.

### A035

`draft_0.001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").rect(80,60).extrude(6,taper=0.001).translate((0,0,-3))
result=result.faces(">Z").workplane().pushPoints([(-30,-20),(-30,20),(30,-20),(30,20)]).hole(6.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A036

`draft_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").rect(80,60).extrude(6,taper=0.01).translate((0,0,-3))
result=result.faces(">Z").workplane().pushPoints([(-30,-20),(-30,20),(30,-20),(30,20)]).hole(6.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A037

`draft_0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").rect(80,60).extrude(6,taper=0.1).translate((0,0,-3))
result=result.faces(">Z").workplane().pushPoints([(-30,-20),(-30,20),(30,-20),(30,20)]).hole(6.5)
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `2.393697` mm3; error `None`.

### A038

`sheared_0.004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").workplane(offset=-3).rect(80,60).workplane(offset=6).center(0.004,0).rect(80,60).loft()
result=result.cut(cq.Workplane("XY").pushPoints([(-30,-20),(-30,20),(30,-20),(30,20)]).circle(3.25).extrude(10,both=True))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A039

`sheared_0.02`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").workplane(offset=-3).rect(80,60).workplane(offset=6).center(0.02,0).rect(80,60).loft()
result=result.cut(cq.Workplane("XY").pushPoints([(-30,-20),(-30,20),(30,-20),(30,20)]).circle(3.25).extrude(10,both=True))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `4.040386` mm3; error `None`.

### A040

`cone_0.001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)
for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 result=result.cut(cq.Solid.makeCone(3.25,3.251,6,cq.Vector(x,y,-3)))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `795.311076` mm3; error `None`.

### A041

`cone_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)
for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 result=result.cut(cq.Solid.makeCone(3.25,3.26,6,cq.Vector(x,y,-3)))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `797.51528` mm3; error `None`.

### A042

`ellipse`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)
for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 result=result.cut(cq.Workplane("XY").center(x,y).ellipse(3.25,3.26).extrude(10,both=True))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `797.512784` mm3; error `None`.

### A043

`polygon_128`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)
for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 result=result.cut(cq.Workplane("XY").center(x,y).polygon(128,6.5).extrude(10,both=True))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `794.747158` mm3; error `None`.

### A044

`nurbs_exact`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
result=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `802.386047` mm3; error `None`.

### A045

`countersink_0.0049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 result=result.cut(cq.Solid.makeCone(3.25,3.2549,0.0049,cq.Vector(x,y,2.9951)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A046

`countersink_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 result=result.cut(cq.Solid.makeCone(3.25,3.26,0.01,cq.Vector(x,y,2.99)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A047

`fifth_bore`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(.02).extrude(10,both=True))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A048

`coincident_bore`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").center(30,20).circle(3.25).extrude(10,both=True))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A049

`overlap_bore_0.0004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").center(30.0004,20).circle(3.25).extrude(10,both=True))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A050

`overlap_bore_0.004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").center(30.004,20).circle(3.25).extrude(10,both=True))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R5:hole_pattern, R9:no_other_features`; extra `0.0`, missing `198.922344` mm3; error `None`.

### A051

`overlap_bore_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").center(30.01,20).circle(3.25).extrude(10,both=True))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R5:hole_pattern, R9:no_other_features`; extra `0.0`, missing `199.155954` mm3; error `None`.

### A052

`coaxial_step`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").workplane(offset=2.999).center(30,20).circle(3.25004).extrude(1))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count`; extra `0.0`, missing `0.0` mm3; error `None`.

### A053

`probe_lug_y0_d0.004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.005,.02,.02).translate((33.2485,20,0)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A054

`probe_lug_y0_d0.05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.051000000000000004,.02,.02).translate((33.2255,20,0)))
```

Observed reward `1.0`; failed checks `none`; extra `1.8e-05`, missing `0.0` mm3; error `None`.

### A055

`probe_lug_y0.3_d0.004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.005,.02,.02).translate((33.2485,20.3,0)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A056

`probe_lug_y0.3_d0.05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.051000000000000004,.02,.02).translate((33.2255,20.3,0)))
```

Observed reward `1.0`; failed checks `none`; extra `1.2e-05`, missing `0.0` mm3; error `None`.

### A057

`probe_notch`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(.03,.02,.02).translate((33.25,20,0)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `4e-06` mm3; error `None`.

### A058

`compound_one`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=cq.Compound.makeCompound([result.val()])
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A059

`second_solid_bore`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=cq.Compound.makeCompound([result.val(),cq.Solid.makeCylinder(.01,1,cq.Vector(30,20,-.5))])
```

Observed reward `0.0`; failed checks `gate:single_solid, gate:simple_through_holes`; extra `0.000314`, missing `0.0` mm3; error `None`.

### A060

`second_solid_outside`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=cq.Compound.makeCompound([result.val(),cq.Solid.makeBox(.01,.01,.01,cq.Vector(41,0,0))])
```

Observed reward `0.0`; failed checks `gate:single_solid, R1:length, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `361.1368` mm3; error `None`.

### A061

`loose_face`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=cq.Compound.makeCompound([result.val(),cq.Face.makePlane(1,1,cq.Vector(0,0,0))])
```

Observed reward `0.0`; failed checks `gate:clean_solid, R9:no_other_features`; extra `None`, missing `None` mm3; error `None`.

### A062

`loose_edge`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=cq.Compound.makeCompound([result.val(),cq.Edge.makeLine((0,0,0),(1,0,0))])
```

Observed reward `0.0`; failed checks `gate:clean_solid, R9:no_other_features`; extra `None`, missing `None` mm3; error `None`.

### A063

`length_0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80.1, 60, 6)
    .faces(">Z").workplane()
    .rect(60.099999999999994, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A064

`diameter_0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 6)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.6)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A065

`z_datum_0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0,0,0.1))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A066

`length_0.100001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80.100001, 60, 6)
    .faces(">Z").workplane()
    .rect(60.100001000000006, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A067

`diameter_0.100001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 6)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.600001)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A068

`z_datum_0.100001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0,0,0.100001))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A069

`length_0.10004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80.10004, 60, 6)
    .faces(">Z").workplane()
    .rect(60.10004000000001, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A070

`diameter_0.10004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 6)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.60004)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A071

`z_datum_0.10004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0,0,0.10004))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A072

`length_0.1001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80.1001, 60, 6)
    .faces(">Z").workplane()
    .rect(60.1001, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)
```

Observed reward `0.9`; failed checks `R1:length`; extra `0.0`, missing `0.0` mm3; error `None`.

### A073

`diameter_0.1001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 6)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.6001)
)
```

Observed reward `0.9`; failed checks `R4b:hole_diameter`; extra `0.0`, missing `0.0` mm3; error `None`.

### A074

`z_datum_0.1001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0,0,0.1001))
```

Observed reward `0.9`; failed checks `R8:z_datum`; extra `0.0`, missing `0.0` mm3; error `None`.

### A075

`centres_0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0.1,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A076

`centres_0.1004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0.1004,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A077

`centres_0.10049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0.10049,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A078

`centres_0.1005`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0.1005,0,0))
```

Observed reward `0.9`; failed checks `R5:hole_pattern`; extra `0.0`, missing `0.0` mm3; error `None`.

### A079

`centres_0.101`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((0.101,0,0))
```

Observed reward `0.9`; failed checks `R5:hole_pattern`; extra `0.0`, missing `0.0` mm3; error `None`.

### A080

`residual_None_thin`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 0.009)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)
```

Observed reward `0.8`; failed checks `R3:thickness, R9:no_other_features`; extra `None`, missing `None` mm3; error `None`.

### A081

`many_bores_16`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

for i in range(16):
 x=-10+(i%12)*1.5
 y=-10+(i//12)*1.5
 result=result.cut(cq.Workplane("XY").center(x,y).circle(.2).extrude(10,both=True))
```

Observed reward `0.0`; failed checks `gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A082

`many_bores_64`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

for i in range(64):
 x=-10+(i%12)*1.5
 y=-10+(i//12)*1.5
 result=result.cut(cq.Workplane("XY").center(x,y).circle(.2).extrude(10,both=True))
```

Observed reward `0.0`; failed checks `gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A083

`many_bores_144`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

for i in range(144):
 x=-10+(i%12)*1.5
 y=-10+(i//12)*1.5
 result=result.cut(cq.Workplane("XY").center(x,y).circle(.2).extrude(10,both=True))
```

Observed reward `0.0`; failed checks `none`; extra `n/a`, missing `n/a` mm3; error `model code exceeded 10s execution budget`.

### A084

`threshold_through_slot_0.0128`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.0128,0.0128,8))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.000981` mm3; error `None`.

### A085

`threshold_through_slot_0.01295`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.01295,0.01295,8))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.001005` mm3; error `None`.

### A086

`threshold_through_slot_0.013`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.013,0.013,8))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.001012` mm3; error `None`.

### A087

`threshold_through_slot_0.0131`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.0131,0.0131,8))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.001028` mm3; error `None`.

### A088

`two_broad_pockets_0.0049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(79.998,59.998,0.0049).translate((0,0,-2.99755)))
result=result.cut(cq.Workplane("XY").box(79.998,59.998,0.0049).translate((0,0,2.99755)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A089

`two_broad_pockets_0.005`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(79.998,59.998,0.005).translate((0,0,-2.9975)))
result=result.cut(cq.Workplane("XY").box(79.998,59.998,0.005).translate((0,0,2.9975)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A090

`six_skin_pockets`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(79.998,59.998,0.0049).translate((0,0,-2.99755)))
result=result.cut(cq.Workplane("XY").box(79.998,59.998,0.0049).translate((0,0,2.99755)))
result=result.cut(cq.Workplane("XY").box(0.0049,59.998,5.998).translate((-39.99755,0,0)))
result=result.cut(cq.Workplane("XY").box(0.0049,59.998,5.998).translate((39.99755,0,0)))
result=result.cut(cq.Workplane("XY").box(79.998,0.0049,5.998).translate((0,-29.99755,0)))
result=result.cut(cq.Workplane("XY").box(79.998,0.0049,5.998).translate((0,29.99755,0)))
```

Observed reward `0.0`; failed checks `gate:single_solid`; extra `0.0`, missing `0.0` mm3; error `None`.

### A091

`actual_probe_lug_0.163`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.164,.02,.02).translate((33.169,20,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R5:hole_pattern, R9:no_other_features`; extra `0.0`, missing `198.766538` mm3; error `None`.

### A092

`actual_probe_lug_0.17`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.171,.02,.02).translate((33.1655,20,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R5:hole_pattern, R9:no_other_features`; extra `0.0`, missing `198.766536` mm3; error `None`.

### A093

`actual_probe_lug_0.2`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").box(0.201,.02,.02).translate((33.1505,20,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R5:hole_pattern, R9:no_other_features`; extra `0.0`, missing `198.766524` mm3; error `None`.

### A094

`tiny_fifth_0.005`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.005).extrude(10,both=True))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A095

`hidden_fifth_0.005`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.005).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.003,.002,.002).translate((0.004,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A096

`tiny_fifth_0.006`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.006).extrude(10,both=True))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A097

`hidden_fifth_0.006`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.006).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.003,.002,.002).translate((0.005,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A098

`tiny_fifth_0.007`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.007).extrude(10,both=True))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A099

`hidden_fifth_0.007`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.007).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.003,.002,.002).translate((0.006,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A100

`tiny_fifth_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.01).extrude(10,both=True))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A101

`hidden_fifth_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.01).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.003,.002,.002).translate((0.009000000000000001,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A102

`bore_annular_membrane`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").workplane(offset=-.000004).center(30,20).circle(3.251).circle(1.63).extrude(.000008))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter`; extra `0.000198`, missing `0.0` mm3; error `None`.

### A103

`top_chamfer_0.0049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.faces(">Z").edges().chamfer(0.0049)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A104

`top_chamfer_0.0051`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.faces(">Z").edges().chamfer(0.0051)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A105

`top_chamfer_0.01`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.faces(">Z").edges().chamfer(0.01)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A106

`corner_fillet_0.001`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.edges("|Z").fillet(0.001)
```

Observed reward `0.0`; failed checks `gate:clean_solid`; extra `0.0`, missing `0.0` mm3; error `None`.

### A107

`corner_fillet_0.005`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.edges("|Z").fillet(0.005)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A108

`corner_fillet_0.02`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.edges("|Z").fillet(0.02)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `3.6e-05` mm3; error `None`.

### A109

`fixed_deep_slot_0.039`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.039,0.039,6))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.009111` mm3; error `None`.

### A110

`fixed_deep_slot_0.041`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.041,0.041,6))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.010069` mm3; error `None`.

### A111

`fixed_deep_slot_0.05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").box(0.05,0.05,6))
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.014975` mm3; error `None`.

### A112

`hide_fifth_r0.003_h0.02`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.003).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.004,.004,0.02).translate((0.002,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A113

`hide_fifth_r0.003_h0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.003).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.004,.004,0.1).translate((0.002,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A114

`hide_fifth_r0.005_h0.02`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.005).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.004,.004,0.02).translate((0.004,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A115

`hide_fifth_r0.005_h0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.005).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.004,.004,0.1).translate((0.004,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A116

`hide_fifth_r0.007_h0.02`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.007).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.004,.004,0.02).translate((0.006,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A117

`hide_fifth_r0.007_h0.1`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.cut(cq.Workplane("XY").circle(0.007).extrude(10,both=True))
result=result.union(cq.Workplane("XY").box(.004,.004,0.1).translate((0.006,0,0)))
```

Observed reward `0.7`; failed checks `R4a:hole_count, R4b:hole_diameter, R7:edge_margin`; extra `0.0`, missing `0.0` mm3; error `None`.

### A118

`largest_skin_gen-0032`

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(214.0, 150.0, 10.5)
    .faces(">Z").workplane()
    .rect(198.0, 134.0, forConstruction=True)
    .vertices()
    .hole(9.0)
)

result=result.cut(cq.Workplane("XY").box(213.998,149.998,0.0049).translate((0,0,-5.24755)))
result=result.cut(cq.Workplane("XY").box(213.998,149.998,0.0049).translate((0,0,5.24755)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A119

`largest_skin_gen-0215`

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(168.0, 78.5, 3.0)
    .faces(">Z").workplane()
    .rect(125.0, 35.5, forConstruction=True)
    .vertices()
    .hole(8.0)
)

result=result.cut(cq.Workplane("XY").box(167.998,78.498,0.0049).translate((0,0,-1.49755)))
result=result.cut(cq.Workplane("XY").box(167.998,78.498,0.0049).translate((0,0,1.49755)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A120

`fillet_0.025`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.edges("|Z").fillet(0.025)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.000271` mm3; error `None`.

### A121

`fillet_0.03`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.edges("|Z").fillet(0.03)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.000735` mm3; error `None`.

### A122

`fillet_0.04`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.edges("|Z").fillet(0.04)
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.002376` mm3; error `None`.

### A123

`fillet_0.05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.edges("|Z").fillet(0.05)
```

Observed reward `0.9`; failed checks `R9:no_other_features`; extra `0.0`, missing `0.004991` mm3; error `None`.

### A124

`annular_bridge_2e-05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").workplane(offset=-1e-05).center(30,20).circle(3.251).circle(1.63).extrude(2e-05))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter`; extra `0.000495`, missing `0.0` mm3; error `None`.

### A125

`annular_bridge_3e-05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").workplane(offset=-1.5e-05).center(30,20).circle(3.251).circle(1.63).extrude(3e-05))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter`; extra `0.000742`, missing `0.0` mm3; error `None`.

### A126

`annular_bridge_4e-05`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.union(cq.Workplane("XY").workplane(offset=-2e-05).center(30,20).circle(3.251).circle(1.63).extrude(4e-05))
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter`; extra `0.000989`, missing `0.0` mm3; error `None`.

### A127

`diagonal_rounding`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

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

result=result.translate((.060499,.080499,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A128

`length_0.100049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80.100049, 60, 6)
    .faces(">Z").workplane()
    .rect(60.100049, 40, forConstruction=True)
    .vertices()
    .hole(6.5)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A129

`diameter_0.100049`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(80, 60, 6)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(6.600049)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### A130

`margin_0.1004`

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)
result=result.faces(">Z").workplane().pushPoints([(-30.1004,-20),(-30.1004,20),(30.1004,-20),(30.1004,20)]).hole(6.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3; error `None`.

### Correct construction snippets

#### C001: gen-0215 / reference

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(168.0, 78.5, 3.0)
    .faces(">Z").workplane()
    .rect(125.0, 35.5, forConstruction=True)
    .vertices()
    .hole(8.0)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C002: gen-0215 / Sketch

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").placeSketch(cq.Sketch().rect(168.0,78.5)).extrude(3.0).translate((0,0,-1.5))
result=result.faces(">Z").workplane().pushPoints([(-62.5, -17.75), (-62.5, 17.75), (62.5, -17.75), (62.5, 17.75)]).hole(8.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C003: gen-0215 / polyline

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").polyline([(-84.0, -39.25), (84.0, -39.25), (84.0, 39.25), (-84.0, 39.25)]).close().extrude(3.0).translate((0,0,-1.5))
result=result.faces(">Z").workplane().pushPoints([(-62.5, -17.75), (-62.5, 17.75), (62.5, -17.75), (62.5, 17.75)]).hole(8.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C004: gen-0215 / cutThruAll

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(168.0,78.5,3.0)
result=result.faces(">Z").workplane().pushPoints([(-62.5, -17.75), (-62.5, 17.75), (62.5, -17.75), (62.5, 17.75)]).circle(4.0).cutThruAll()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C005: gen-0215 / explicit_depth

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(168.0,78.5,3.0)
result=result.faces(">Z").workplane().pushPoints([(-62.5, -17.75), (-62.5, 17.75), (62.5, -17.75), (62.5, 17.75)]).hole(8.0,3.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C006: gen-0215 / union_halves

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(84.0,78.5,3.0).translate((-42.0,0,0)).union(cq.Workplane("XY").box(84.0,78.5,3.0).translate((42.0,0,0)))
result=result.faces(">Z").workplane().pushPoints([(-62.5, -17.75), (-62.5, 17.75), (62.5, -17.75), (62.5, 17.75)]).hole(8.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C007: gen-0215 / imprinted_halves

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(84.0,78.5,3.0).translate((-42.0,0,0)).union(cq.Workplane("XY").box(84.0,78.5,3.0).translate((42.0,0,0)),clean=False)
for x,y in [(-62.5, -17.75), (-62.5, 17.75), (62.5, -17.75), (62.5, 17.75)]:
 result=result.cut(cq.Workplane("XY").center(x,y).circle(4.0).extrude(5.0,both=True),clean=False)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C008: gen-0215 / mirror

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(84.0,78.5,3.0).translate((42.0,0,0)).mirror("YZ",union=True)
result=result.faces(">Z").workplane().pushPoints([(-62.5, -17.75), (-62.5, 17.75), (62.5, -17.75), (62.5, 17.75)]).hole(8.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C009: gen-0215 / translate_chain

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(168.0, 78.5, 3.0)
    .faces(">Z").workplane()
    .rect(125.0, 35.5, forConstruction=True)
    .vertices()
    .hole(8.0)
)

result=result.translate((123.456,-234.567,19.1)).translate((-123.456,234.567,-19.1))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C010: gen-0215 / Solid_primitives

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Solid.makeBox(168.0,78.5,3.0,cq.Vector(-84.0,-39.25,-1.5))
for x,y in [(-62.5, -17.75), (-62.5, 17.75), (62.5, -17.75), (62.5, 17.75)]:
 result=result.cut(cq.Solid.makeCylinder(4.0,3.0,cq.Vector(x,y,-1.5)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C011: gen-0215 / clean

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(168.0, 78.5, 3.0)
    .faces(">Z").workplane()
    .rect(125.0, 35.5, forConstruction=True)
    .vertices()
    .hole(8.0)
)

result=result.clean()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C012: gen-0215 / float_coordinates

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(168.0, 78.5, 3.0)
    .faces(">Z").workplane()
    .rect(125.0, 35.5, forConstruction=True)
    .vertices()
    .hole(8.0)
)

result=result.translate((55.749999999,0,0)).translate((-55.75,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C013: gen-0215 / nurbs_exact

Spec: `{"id": "gen-0215", "length": 168.0, "width": 78.5, "thickness": 3.0, "hole_diameter": 8.0, "edge_margin": 21.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(168.0, 78.5, 3.0)
    .faces(">Z").workplane()
    .rect(125.0, 35.5, forConstruction=True)
    .vertices()
    .hole(8.0)
)

from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
result=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `606.704335` mm3.

#### C014: gen-0065 / reference

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(147.5, 32.5, 5.5)
    .faces(">Z").workplane()
    .rect(137.5, 22.5, forConstruction=True)
    .vertices()
    .hole(4.0)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C015: gen-0065 / Sketch

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").placeSketch(cq.Sketch().rect(147.5,32.5)).extrude(5.5).translate((0,0,-2.75))
result=result.faces(">Z").workplane().pushPoints([(-68.75, -11.25), (-68.75, 11.25), (68.75, -11.25), (68.75, 11.25)]).hole(4.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C016: gen-0065 / polyline

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").polyline([(-73.75, -16.25), (73.75, -16.25), (73.75, 16.25), (-73.75, 16.25)]).close().extrude(5.5).translate((0,0,-2.75))
result=result.faces(">Z").workplane().pushPoints([(-68.75, -11.25), (-68.75, 11.25), (68.75, -11.25), (68.75, 11.25)]).hole(4.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C017: gen-0065 / cutThruAll

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(147.5,32.5,5.5)
result=result.faces(">Z").workplane().pushPoints([(-68.75, -11.25), (-68.75, 11.25), (68.75, -11.25), (68.75, 11.25)]).circle(2.0).cutThruAll()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C018: gen-0065 / explicit_depth

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(147.5,32.5,5.5)
result=result.faces(">Z").workplane().pushPoints([(-68.75, -11.25), (-68.75, 11.25), (68.75, -11.25), (68.75, 11.25)]).hole(4.0,5.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C019: gen-0065 / union_halves

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(73.75,32.5,5.5).translate((-36.875,0,0)).union(cq.Workplane("XY").box(73.75,32.5,5.5).translate((36.875,0,0)))
result=result.faces(">Z").workplane().pushPoints([(-68.75, -11.25), (-68.75, 11.25), (68.75, -11.25), (68.75, 11.25)]).hole(4.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C020: gen-0065 / imprinted_halves

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(73.75,32.5,5.5).translate((-36.875,0,0)).union(cq.Workplane("XY").box(73.75,32.5,5.5).translate((36.875,0,0)),clean=False)
for x,y in [(-68.75, -11.25), (-68.75, 11.25), (68.75, -11.25), (68.75, 11.25)]:
 result=result.cut(cq.Workplane("XY").center(x,y).circle(2.0).extrude(7.5,both=True),clean=False)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C021: gen-0065 / mirror

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(73.75,32.5,5.5).translate((36.875,0,0)).mirror("YZ",union=True)
result=result.faces(">Z").workplane().pushPoints([(-68.75, -11.25), (-68.75, 11.25), (68.75, -11.25), (68.75, 11.25)]).hole(4.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C022: gen-0065 / translate_chain

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(147.5, 32.5, 5.5)
    .faces(">Z").workplane()
    .rect(137.5, 22.5, forConstruction=True)
    .vertices()
    .hole(4.0)
)

result=result.translate((123.456,-234.567,19.1)).translate((-123.456,234.567,-19.1))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C023: gen-0065 / Solid_primitives

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Solid.makeBox(147.5,32.5,5.5,cq.Vector(-73.75,-16.25,-2.75))
for x,y in [(-68.75, -11.25), (-68.75, 11.25), (68.75, -11.25), (68.75, 11.25)]:
 result=result.cut(cq.Solid.makeCylinder(2.0,5.5,cq.Vector(x,y,-2.75)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C024: gen-0065 / clean

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(147.5, 32.5, 5.5)
    .faces(">Z").workplane()
    .rect(137.5, 22.5, forConstruction=True)
    .vertices()
    .hole(4.0)
)

result=result.clean()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C025: gen-0065 / float_coordinates

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(147.5, 32.5, 5.5)
    .faces(">Z").workplane()
    .rect(137.5, 22.5, forConstruction=True)
    .vertices()
    .hole(4.0)
)

result=result.translate((55.749999999,0,0)).translate((-55.75,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C026: gen-0065 / nurbs_exact

Spec: `{"id": "gen-0065", "length": 147.5, "width": 32.5, "thickness": 5.5, "hole_diameter": 4.0, "edge_margin": 5.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(147.5, 32.5, 5.5)
    .faces(">Z").workplane()
    .rect(137.5, 22.5, forConstruction=True)
    .vertices()
    .hole(4.0)
)

from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
result=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `278.496297` mm3.

#### C027: gen-0032 / reference

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(214.0, 150.0, 10.5)
    .faces(">Z").workplane()
    .rect(198.0, 134.0, forConstruction=True)
    .vertices()
    .hole(9.0)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C028: gen-0032 / Sketch

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").placeSketch(cq.Sketch().rect(214.0,150.0)).extrude(10.5).translate((0,0,-5.25))
result=result.faces(">Z").workplane().pushPoints([(-99.0, -67.0), (-99.0, 67.0), (99.0, -67.0), (99.0, 67.0)]).hole(9.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C029: gen-0032 / polyline

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").polyline([(-107.0, -75.0), (107.0, -75.0), (107.0, 75.0), (-107.0, 75.0)]).close().extrude(10.5).translate((0,0,-5.25))
result=result.faces(">Z").workplane().pushPoints([(-99.0, -67.0), (-99.0, 67.0), (99.0, -67.0), (99.0, 67.0)]).hole(9.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C030: gen-0032 / cutThruAll

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(214.0,150.0,10.5)
result=result.faces(">Z").workplane().pushPoints([(-99.0, -67.0), (-99.0, 67.0), (99.0, -67.0), (99.0, 67.0)]).circle(4.5).cutThruAll()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C031: gen-0032 / explicit_depth

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(214.0,150.0,10.5)
result=result.faces(">Z").workplane().pushPoints([(-99.0, -67.0), (-99.0, 67.0), (99.0, -67.0), (99.0, 67.0)]).hole(9.0,10.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C032: gen-0032 / union_halves

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(107.0,150.0,10.5).translate((-53.5,0,0)).union(cq.Workplane("XY").box(107.0,150.0,10.5).translate((53.5,0,0)))
result=result.faces(">Z").workplane().pushPoints([(-99.0, -67.0), (-99.0, 67.0), (99.0, -67.0), (99.0, 67.0)]).hole(9.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C033: gen-0032 / imprinted_halves

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(107.0,150.0,10.5).translate((-53.5,0,0)).union(cq.Workplane("XY").box(107.0,150.0,10.5).translate((53.5,0,0)),clean=False)
for x,y in [(-99.0, -67.0), (-99.0, 67.0), (99.0, -67.0), (99.0, 67.0)]:
 result=result.cut(cq.Workplane("XY").center(x,y).circle(4.5).extrude(12.5,both=True),clean=False)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C034: gen-0032 / mirror

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(107.0,150.0,10.5).translate((53.5,0,0)).mirror("YZ",union=True)
result=result.faces(">Z").workplane().pushPoints([(-99.0, -67.0), (-99.0, 67.0), (99.0, -67.0), (99.0, 67.0)]).hole(9.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C035: gen-0032 / translate_chain

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(214.0, 150.0, 10.5)
    .faces(">Z").workplane()
    .rect(198.0, 134.0, forConstruction=True)
    .vertices()
    .hole(9.0)
)

result=result.translate((123.456,-234.567,19.1)).translate((-123.456,234.567,-19.1))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C036: gen-0032 / Solid_primitives

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Solid.makeBox(214.0,150.0,10.5,cq.Vector(-107.0,-75.0,-5.25))
for x,y in [(-99.0, -67.0), (-99.0, 67.0), (99.0, -67.0), (99.0, 67.0)]:
 result=result.cut(cq.Solid.makeCylinder(4.5,10.5,cq.Vector(x,y,-5.25)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C037: gen-0032 / clean

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(214.0, 150.0, 10.5)
    .faces(">Z").workplane()
    .rect(198.0, 134.0, forConstruction=True)
    .vertices()
    .hole(9.0)
)

result=result.clean()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C038: gen-0032 / float_coordinates

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(214.0, 150.0, 10.5)
    .faces(">Z").workplane()
    .rect(198.0, 134.0, forConstruction=True)
    .vertices()
    .hole(9.0)
)

result=result.translate((55.749999999,0,0)).translate((-55.75,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C039: gen-0032 / nurbs_exact

Spec: `{"id": "gen-0032", "length": 214.0, "width": 150.0, "thickness": 10.5, "hole_diameter": 9.0, "edge_margin": 8.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(214.0, 150.0, 10.5)
    .faces(">Z").workplane()
    .rect(198.0, 134.0, forConstruction=True)
    .vertices()
    .hole(9.0)
)

from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
result=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `2693.858355` mm3.

#### C040: gen-0208 / reference

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(43.0, 36.0, 6.5)
    .faces(">Z").workplane()
    .rect(29.0, 22.0, forConstruction=True)
    .vertices()
    .hole(8.5)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C041: gen-0208 / Sketch

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").placeSketch(cq.Sketch().rect(43.0,36.0)).extrude(6.5).translate((0,0,-3.25))
result=result.faces(">Z").workplane().pushPoints([(-14.5, -11.0), (-14.5, 11.0), (14.5, -11.0), (14.5, 11.0)]).hole(8.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C042: gen-0208 / polyline

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").polyline([(-21.5, -18.0), (21.5, -18.0), (21.5, 18.0), (-21.5, 18.0)]).close().extrude(6.5).translate((0,0,-3.25))
result=result.faces(">Z").workplane().pushPoints([(-14.5, -11.0), (-14.5, 11.0), (14.5, -11.0), (14.5, 11.0)]).hole(8.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C043: gen-0208 / cutThruAll

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(43.0,36.0,6.5)
result=result.faces(">Z").workplane().pushPoints([(-14.5, -11.0), (-14.5, 11.0), (14.5, -11.0), (14.5, 11.0)]).circle(4.25).cutThruAll()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C044: gen-0208 / explicit_depth

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(43.0,36.0,6.5)
result=result.faces(">Z").workplane().pushPoints([(-14.5, -11.0), (-14.5, 11.0), (14.5, -11.0), (14.5, 11.0)]).hole(8.5,6.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C045: gen-0208 / union_halves

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(21.5,36.0,6.5).translate((-10.75,0,0)).union(cq.Workplane("XY").box(21.5,36.0,6.5).translate((10.75,0,0)))
result=result.faces(">Z").workplane().pushPoints([(-14.5, -11.0), (-14.5, 11.0), (14.5, -11.0), (14.5, 11.0)]).hole(8.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C046: gen-0208 / imprinted_halves

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(21.5,36.0,6.5).translate((-10.75,0,0)).union(cq.Workplane("XY").box(21.5,36.0,6.5).translate((10.75,0,0)),clean=False)
for x,y in [(-14.5, -11.0), (-14.5, 11.0), (14.5, -11.0), (14.5, 11.0)]:
 result=result.cut(cq.Workplane("XY").center(x,y).circle(4.25).extrude(8.5,both=True),clean=False)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C047: gen-0208 / mirror

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(21.5,36.0,6.5).translate((10.75,0,0)).mirror("YZ",union=True)
result=result.faces(">Z").workplane().pushPoints([(-14.5, -11.0), (-14.5, 11.0), (14.5, -11.0), (14.5, 11.0)]).hole(8.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C048: gen-0208 / translate_chain

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(43.0, 36.0, 6.5)
    .faces(">Z").workplane()
    .rect(29.0, 22.0, forConstruction=True)
    .vertices()
    .hole(8.5)
)

result=result.translate((123.456,-234.567,19.1)).translate((-123.456,234.567,-19.1))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C049: gen-0208 / Solid_primitives

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Solid.makeBox(43.0,36.0,6.5,cq.Vector(-21.5,-18.0,-3.25))
for x,y in [(-14.5, -11.0), (-14.5, 11.0), (14.5, -11.0), (14.5, 11.0)]:
 result=result.cut(cq.Solid.makeCylinder(4.25,6.5,cq.Vector(x,y,-3.25)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C050: gen-0208 / clean

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(43.0, 36.0, 6.5)
    .faces(">Z").workplane()
    .rect(29.0, 22.0, forConstruction=True)
    .vertices()
    .hole(8.5)
)

result=result.clean()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C051: gen-0208 / float_coordinates

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(43.0, 36.0, 6.5)
    .faces(">Z").workplane()
    .rect(29.0, 22.0, forConstruction=True)
    .vertices()
    .hole(8.5)
)

result=result.translate((55.749999999,0,0)).translate((-55.75,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C052: gen-0208 / nurbs_exact

Spec: `{"id": "gen-0208", "length": 43.0, "width": 36.0, "thickness": 6.5, "hole_diameter": 8.5, "edge_margin": 7.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(43.0, 36.0, 6.5)
    .faces(">Z").workplane()
    .rect(29.0, 22.0, forConstruction=True)
    .vertices()
    .hole(8.5)
)

from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
result=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `1486.646181` mm3.

#### C053: gen-0001 / reference

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(74.5, 81.0, 4.5)
    .faces(">Z").workplane()
    .rect(25.5, 32.0, forConstruction=True)
    .vertices()
    .hole(10.5)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C054: gen-0001 / Sketch

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").placeSketch(cq.Sketch().rect(74.5,81.0)).extrude(4.5).translate((0,0,-2.25))
result=result.faces(">Z").workplane().pushPoints([(-12.75, -16.0), (-12.75, 16.0), (12.75, -16.0), (12.75, 16.0)]).hole(10.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C055: gen-0001 / polyline

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").polyline([(-37.25, -40.5), (37.25, -40.5), (37.25, 40.5), (-37.25, 40.5)]).close().extrude(4.5).translate((0,0,-2.25))
result=result.faces(">Z").workplane().pushPoints([(-12.75, -16.0), (-12.75, 16.0), (12.75, -16.0), (12.75, 16.0)]).hole(10.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C056: gen-0001 / cutThruAll

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(74.5,81.0,4.5)
result=result.faces(">Z").workplane().pushPoints([(-12.75, -16.0), (-12.75, 16.0), (12.75, -16.0), (12.75, 16.0)]).circle(5.25).cutThruAll()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C057: gen-0001 / explicit_depth

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(74.5,81.0,4.5)
result=result.faces(">Z").workplane().pushPoints([(-12.75, -16.0), (-12.75, 16.0), (12.75, -16.0), (12.75, 16.0)]).hole(10.5,4.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C058: gen-0001 / union_halves

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(37.25,81.0,4.5).translate((-18.625,0,0)).union(cq.Workplane("XY").box(37.25,81.0,4.5).translate((18.625,0,0)))
result=result.faces(">Z").workplane().pushPoints([(-12.75, -16.0), (-12.75, 16.0), (12.75, -16.0), (12.75, 16.0)]).hole(10.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C059: gen-0001 / imprinted_halves

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(37.25,81.0,4.5).translate((-18.625,0,0)).union(cq.Workplane("XY").box(37.25,81.0,4.5).translate((18.625,0,0)),clean=False)
for x,y in [(-12.75, -16.0), (-12.75, 16.0), (12.75, -16.0), (12.75, 16.0)]:
 result=result.cut(cq.Workplane("XY").center(x,y).circle(5.25).extrude(6.5,both=True),clean=False)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C060: gen-0001 / mirror

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(37.25,81.0,4.5).translate((18.625,0,0)).mirror("YZ",union=True)
result=result.faces(">Z").workplane().pushPoints([(-12.75, -16.0), (-12.75, 16.0), (12.75, -16.0), (12.75, 16.0)]).hole(10.5)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C061: gen-0001 / translate_chain

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(74.5, 81.0, 4.5)
    .faces(">Z").workplane()
    .rect(25.5, 32.0, forConstruction=True)
    .vertices()
    .hole(10.5)
)

result=result.translate((123.456,-234.567,19.1)).translate((-123.456,234.567,-19.1))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C062: gen-0001 / Solid_primitives

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Solid.makeBox(74.5,81.0,4.5,cq.Vector(-37.25,-40.5,-2.25))
for x,y in [(-12.75, -16.0), (-12.75, 16.0), (12.75, -16.0), (12.75, 16.0)]:
 result=result.cut(cq.Solid.makeCylinder(5.25,4.5,cq.Vector(x,y,-2.25)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C063: gen-0001 / clean

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(74.5, 81.0, 4.5)
    .faces(">Z").workplane()
    .rect(25.5, 32.0, forConstruction=True)
    .vertices()
    .hole(10.5)
)

result=result.clean()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C064: gen-0001 / float_coordinates

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(74.5, 81.0, 4.5)
    .faces(">Z").workplane()
    .rect(25.5, 32.0, forConstruction=True)
    .vertices()
    .hole(10.5)
)

result=result.translate((55.749999999,0,0)).translate((-55.75,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C065: gen-0001 / nurbs_exact

Spec: `{"id": "gen-0001", "length": 74.5, "width": 81.0, "thickness": 4.5, "hole_diameter": 10.5, "edge_margin": 24.5, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(74.5, 81.0, 4.5)
    .faces(">Z").workplane()
    .rect(25.5, 32.0, forConstruction=True)
    .vertices()
    .hole(10.5)
)

from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
result=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `1569.414536` mm3.

#### C066: gen-0037 / reference

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(207.0, 93.5, 3.0)
    .faces(">Z").workplane()
    .rect(177.0, 63.5, forConstruction=True)
    .vertices()
    .hole(6.0)
)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C067: gen-0037 / Sketch

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").placeSketch(cq.Sketch().rect(207.0,93.5)).extrude(3.0).translate((0,0,-1.5))
result=result.faces(">Z").workplane().pushPoints([(-88.5, -31.75), (-88.5, 31.75), (88.5, -31.75), (88.5, 31.75)]).hole(6.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C068: gen-0037 / polyline

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").polyline([(-103.5, -46.75), (103.5, -46.75), (103.5, 46.75), (-103.5, 46.75)]).close().extrude(3.0).translate((0,0,-1.5))
result=result.faces(">Z").workplane().pushPoints([(-88.5, -31.75), (-88.5, 31.75), (88.5, -31.75), (88.5, 31.75)]).hole(6.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C069: gen-0037 / cutThruAll

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(207.0,93.5,3.0)
result=result.faces(">Z").workplane().pushPoints([(-88.5, -31.75), (-88.5, 31.75), (88.5, -31.75), (88.5, 31.75)]).circle(3.0).cutThruAll()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C070: gen-0037 / explicit_depth

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(207.0,93.5,3.0)
result=result.faces(">Z").workplane().pushPoints([(-88.5, -31.75), (-88.5, 31.75), (88.5, -31.75), (88.5, 31.75)]).hole(6.0,3.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C071: gen-0037 / union_halves

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(103.5,93.5,3.0).translate((-51.75,0,0)).union(cq.Workplane("XY").box(103.5,93.5,3.0).translate((51.75,0,0)))
result=result.faces(">Z").workplane().pushPoints([(-88.5, -31.75), (-88.5, 31.75), (88.5, -31.75), (88.5, 31.75)]).hole(6.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C072: gen-0037 / imprinted_halves

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(103.5,93.5,3.0).translate((-51.75,0,0)).union(cq.Workplane("XY").box(103.5,93.5,3.0).translate((51.75,0,0)),clean=False)
for x,y in [(-88.5, -31.75), (-88.5, 31.75), (88.5, -31.75), (88.5, 31.75)]:
 result=result.cut(cq.Workplane("XY").center(x,y).circle(3.0).extrude(5.0,both=True),clean=False)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C073: gen-0037 / mirror

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(103.5,93.5,3.0).translate((51.75,0,0)).mirror("YZ",union=True)
result=result.faces(">Z").workplane().pushPoints([(-88.5, -31.75), (-88.5, 31.75), (88.5, -31.75), (88.5, 31.75)]).hole(6.0)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C074: gen-0037 / translate_chain

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(207.0, 93.5, 3.0)
    .faces(">Z").workplane()
    .rect(177.0, 63.5, forConstruction=True)
    .vertices()
    .hole(6.0)
)

result=result.translate((123.456,-234.567,19.1)).translate((-123.456,234.567,-19.1))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C075: gen-0037 / Solid_primitives

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Solid.makeBox(207.0,93.5,3.0,cq.Vector(-103.5,-46.75,-1.5))
for x,y in [(-88.5, -31.75), (-88.5, 31.75), (88.5, -31.75), (88.5, 31.75)]:
 result=result.cut(cq.Solid.makeCylinder(3.0,3.0,cq.Vector(x,y,-1.5)))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C076: gen-0037 / clean

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(207.0, 93.5, 3.0)
    .faces(">Z").workplane()
    .rect(177.0, 63.5, forConstruction=True)
    .vertices()
    .hole(6.0)
)

result=result.clean()
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C077: gen-0037 / float_coordinates

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(207.0, 93.5, 3.0)
    .faces(">Z").workplane()
    .rect(177.0, 63.5, forConstruction=True)
    .vertices()
    .hole(6.0)
)

result=result.translate((55.749999999,0,0)).translate((-55.75,0,0))
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.

#### C078: gen-0037 / nurbs_exact

Spec: `{"id": "gen-0037", "length": 207.0, "width": 93.5, "thickness": 3.0, "hole_diameter": 6.0, "edge_margin": 15.0, "hole_count": 4}`

```python

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(207.0, 93.5, 3.0)
    .faces(">Z").workplane()
    .rect(177.0, 63.5, forConstruction=True)
    .vertices()
    .hole(6.0)
)

from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
result=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(result.val().wrapped,True).Shape())
```

Observed reward `0.0`; failed checks `gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features`; extra `0.0`, missing `341.265429` mm3.

#### C079: synthetic / arc_circle

Spec: `{"id": "synthetic", "length": 80, "width": 60, "thickness": 6, "hole_diameter": 6.5, "edge_margin": 10, "hole_count": 4}`

```python
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)
for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 cutter=cq.Workplane("XY").center(x,y).moveTo(3.25,0).threePointArc((0,3.25),(-3.25,0)).threePointArc((0,-3.25),(3.25,0)).close().extrude(10,both=True)
 result=result.cut(cutter,clean=False)
```

Observed reward `1.0`; failed checks `none`; extra `0.0`, missing `0.0` mm3.
