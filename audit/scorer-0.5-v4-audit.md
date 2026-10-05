**Recommendation: merge.** **Opinion:** `0f9119c` resolves the three round-3 findings on the requested local evidence. No scoring change is required before merge by this verification. The optional documentation corrections below do not affect this recommendation.

**Fact:** all **473 earlier parts** across A, C, N, D, S, L, T, V, W, G, Q, J and E were executed again. **No incorrect part receives 1.0**, and **no correct non-spline part is rejected** in this corpus. All **180** additional correct-plate controls pass. All **3,161** legacy comparisons agree on rewards, named check verdicts, parsed flags and address-normalized errors.

# Scorer 0.5.0, round 4 verification

**Fact:** target `feat/scorer-0.5`, HEAD `0f9119c41b0f85c94bb1f86e2661d932e3ba7ef2`. Parent/before: `4990743346555b0b93a1865b6a069b14c5ed83d9`. Main: `7c17439a84529417d4516882b4034aa148c86017`. Date: 2026-10-05. Runtime: Windows, Python 3.12, CadQuery 2.8.0, `CAD_SPEC_SANDBOX=reuse`, default 10-second answer budget. Interpreter: `C:/Users/bgare/dev/cad-spec-env/environments/cad_spec/.venv/Scripts/python.exe`.

Facts below are local executions or source observations. Inferences describe what they support. Opinions are recommendations. Confidence is high for the recorded cases and moderate for conclusions beyond them. Correct means the published dimensional/datum tolerances, explicit numerical slack and form equivalence, rather than exact nominal dimensions. No model was run and no threshold was selected using evaluation answers.

**Fact:** the repository remained read-only; all new files, snapshots, logs and worker temporary directories are under v4. No network, credentials, paid service or external system was used. Final Git status and tracked diff are clean. The before/main package snapshots were obtained with local `git show`; [provenance.json](scratch/provenance.json) contains hashes. The 3,161-answer input has SHA-256 `aadd97fcb37734637a14e22f328c28c3c17584e3c4c445b23efb38b3a1b4fc44` and is byte-identical to the prior comparison input.

## Required changes and small reproductions

**Opinion:** none required for the three requested fixes. There is no newly observed incorrect full-credit part or correct non-spline rejection for which to propose a scorer diff. The reproductions below show the previous defects and their current scores. These are finite verification results, not a proof that every possible B-rep is classified correctly.

### R3-B1: resolved for the observed boundary inconsistency

**Fact:** N025 and N026 now score **0.9**, failing only `R9:no_other_features`. Both still pass `gate:clean_solid`; stored-tolerance validity remains true. `surface_conformance=True`, `boundary_consistent=False`, and extra/missing residuals are both zero. Thus the repair is in R9 as requested, not in the identity gate.

Small reproduction of N026, scored against `Spec("repro", 80, 60, 6, 6.5, 10)`:

```python
from cad_spec.tasks import Spec
from cad_spec.rubric import score
code = """
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
"""
if __name__ == "__main__":
    report = score(code, Spec("repro", 80, 60, 6, 6.5, 10), version="0.5.0")
    print(report.reward)  # 0.9, R9 only
```

**Fact, source:** `_boundary_consistent` makes a geometry copy, forces face/edge/vertex tolerances on that copy to `FORM_LINEAR_TOL`, then uses the exact-method `BRepCheck_Analyzer`. It does not modify the submitted solid. `measure(strict=True)` records the result separately from `valid`; rubric R9 requires it and fails closed on an unavailable result.

**Inference:** this removes the observed path in which a larger stored edge tolerance hid the retained trim mismatch. The metadata-only controls show that the repair does not simply reject every large stored tolerance. This does not certify the kernel analyzer as a general Hausdorff-distance test.

### R3-B2: resolved for the observed bore metric defect

**Fact:** E002 and E003 now score **0.9**, failing only R9. E001, within the distance budget, still scores **1.0**. E004 remains **0.9**. The exact earlier source and specifications were reused.

Small reproduction of E003, scored against `Spec("repro-diagonal", 80, 60, 6, 2.5, 10)`:

```python
from cad_spec.tasks import Spec
from cad_spec.rubric import score
code = """
import cadquery as cq
result=cq.Workplane("XY").box(80,60,6)

for x,y in [(-30,-20),(-30,20),(30,-20),(30,20)]:
 cutter=cq.Workplane("XY").circle(1.25).extrude(8,both=True)
 cutter=cutter.rotate((0,0,0),(-1,1,0),2.673939458986605e-06).translate((x,y,0))
 result=result.cut(cutter)
"""
if __name__ == "__main__":
    report = score(code, Spec("repro-diagonal", 80, 60, 6, 2.5, 10), version="0.5.0")
    print(report.reward)  # 0.9, R9 only
```

**Fact:** the observed score is **0.9**. Its end-axis displacement is approximately **1.400071427e-7 mm**. The code now tests, at both envelope ends,

```python
hypot(x - h.x, y - h.y) + max(
    abs(radius - h.diameter / 2),
    abs(radius / abs(direction.Z()) - h.diameter / 2),
) <= FORM_LINEAR_TOL
```

**Inference:** the center uses one Euclidean displacement; the radius mismatch and tilted-section ellipse consume the same budget. Over the plate interval, the center displacement of a straight axis is bounded by its endpoint maximum. The sum is a conservative surface-distance bound, not a calculation of the exact global boundary maximum.

### Worker fault: resolved for the reproduced crash and lost-connection paths

**Fact:** V071, the earlier inconsistent remote-cylinder part, crashes a native worker in each of three trials with exit code **3221225477** (Windows access violation, hexadecimal `0xC0000005`). In each trial the crash answer scores **0.0** with `scorer worker died while executing model code`; the **immediately following ordinary reference plate scores 1.0** and runs on a different worker PID. No manual shutdown or restart is inserted between the crash and that correct answer.

Small sequence, using the exact extreme source retained in [recovery.json](scratch/recovery.json):

```python
crash = score(extreme_code, spec, version="0.5.0")
next_part = score(reference_solution(spec), spec, version="0.5.0")
print(crash.reward, next_part.reward)
# 0.0 1.0, in all three trials
```

**Fact:** closing a live worker's send connection once exercises `_WorkerLostError` and produces **1.0** on the same ordinary answer after retry. Closing both initial and replacement connections causes exactly two calls and raises **ScorerUnavailableError**, without a model score. The repository's lost-connection regression also passes.

**Inference:** the EOF path kills the crashed worker, `_get_worker` replaces it for the next answer, and an already-lost send retries once. This supports the CHANGELOG claim for these fault paths. It is not a guarantee for arbitrary kernel faults, other OSes or the Linux fork mode.

## Verification tables

### Earlier series and complete exception lists

**Fact:** the rerun preserved every source/specification/ID from the prior reports. The 473 count is 322 original/v2 rows plus 151 v3 rows. Each score and Measurement is saved in [corpus-rerun.jsonl](scratch/corpus-rerun.jsonl). Build errors mean no reliably measured part; they are not interpreted as geometric false rejections.

| Series | Executed | Score 1.0 | Build/worker errors | Incorrect at 1.0 | Correct non-spline rejected |
| --- | --- | --- | --- | --- | --- |
| A | 130 | 8 | 4 | 0 | 0 |
| C | 79 | 73 | 0 | 0 | 0 |
| N | 29 | 6 | 7 | 0 | 0 |
| D | 52 | 3 | 4 | 0 | 0 |
| S | 16 | 0 | 0 | 0 | 0 |
| L | 12 | 0 | 0 | 0 | 0 |
| T | 4 | 0 | 0 | 0 | 0 |
| V | 80 | 35 | 12 | 0 | 0 |
| W | 22 | 14 | 6 | 0 | 0 |
| G | 33 | 2 | 5 | 0 | 0 |
| Q | 6 | 0 | 3 | 0 | 0 |
| J | 6 | 6 | 0 | 0 | 0 |
| E | 4 | 1 | 0 | 0 | 0 |

**Fact: complete list of incorrect parts still at full credit: empty.** Task 6 therefore has no reported incorrect full-credit part to assign an ordinary-CadQuery flag or largest real-boundary distance. Neither a distance of zero nor a sampled maximum is invented for an absent counterexample.

| Incorrect full-credit ID | Only ordinary CadQuery calls? | Largest distance to correct plate, mm | Score |
| --- | --- | --- | --- |
| None | Not applicable | Not applicable | Not applicable |

**Fact: complete list of correct non-spline parts rejected: empty.** The original non-spline C controls are **73/73** at 1.0. Equivalent remote analytic plane controls V053/V055/V057 and J004/J005/J006 pass; J001/J002/J003 ordinary mirrors pass. V077/V078, previously contaminated by broken-pipe errors, now pass; V079/V080 execute and fail R9 for excessive tilt. V059 to V076 edit cylinder supports without corresponding pcurve changes; the rejected or crashing shapes are not equivalent-cylinder correctness controls. Q's orientation/overload failures and W013 to W018's null Boolean results are likewise not constructed correct plates.

The retained spline-policy rejections are listed separately. These are correct geometries rejected for unsupported stored representations, not new non-spline regressions.

| Correct geometry ID | Stored representation | Current score | Failed checks |
| --- | --- | --- | --- |
| A044 | nurbs_exact | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C013 | nurbs_exact | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C026 | nurbs_exact | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C039 | nurbs_exact | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C052 | nurbs_exact | 0.0 | gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C065 | nurbs_exact | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C078 | nurbs_exact | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| S001 | sewn_bezier_plate_0 | 0.9 | R9:no_other_features |
| S009 | revolved_bezier_bore_0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| L001 | local_spline_0.123_0.001_1e-05 | 0.9 | R9:no_other_features |
| L002 | local_spline_0.123_0.001_0.001 | 0.9 | R9:no_other_features |
| L003 | local_spline_0.123_0.001_0.004 | 0.9 | R9:no_other_features |
| L004 | local_spline_0.127_0.0001_1e-05 | 0.9 | R9:no_other_features |
| L005 | local_spline_0.127_0.0001_0.001 | 0.9 | R9:no_other_features |
| L006 | local_spline_0.127_0.0001_0.004 | 0.9 | R9:no_other_features |

### Full-credit controls and their interpretation

**Fact:** these are all full-credit groups, apart from the 73 C controls. **Inference:** their accepted geometry fits the published tolerances/equivalence, or an intended extra operation leaves the nominal geometry unchanged. A requested feature name alone does not establish a retained incorrect boundary. These classifications carry forward the geometric diagnostics and ground truth from the earlier reviews; scores and Measurements were rerun here.

| IDs | Why these are correct/accepted controls |
| --- | --- |
| A001, A048, A055, A058 | Nominal, coincident cut, lug absorbed into existing material, one-solid compound |
| A063 to A065, A075 | Inclusive dimensional/datum/position endpoints |
| N006 to N011 | Tiny rotations within extent-based form equivalence |
| D045, D049, D053 | Whole bore enlargement within dimensional tolerance, not a retained counterbore |
| V001 to V012 | Correct geometry with tolerance metadata changed |
| V014, V016, V018 | Sub-tolerance boss controls supported by the earlier retained-boundary diagnostic |
| V025 to V027 | Tiny rotations within form equivalence |
| V029 to V040 | Inclusive endpoints and explicit 1e-9 dimensional slack |
| V053, V055, V057 | Same top plane stored at remote origins with correct orientation |
| V077, V078, G030, G031 | Ordinary tilted bores within the combined form distance allowance |
| W001 to W012 | Consistently constructed analytic remote-axis cutters, both axis senses |
| W019, W020 | Center shifts within dimensional/position tolerance and explicit slack |
| J001 to J006 | Ordinary mirrors and correctly oriented equivalent remote planes |
| E001 | Diagonal bore end displacement about 8.485281374e-8 mm, within 1e-7 |

### Fix verdicts

**Fact:** the following table is based on the executions and source observations above.

| Finding | Verdict | Evidence |
| --- | --- | --- |
| R3-B1 | Resolved for its reproductions | N025/N026: 1.0 -> 0.9; R9 only; clean_solid passes; boundary_consistent=False |
| R3-B2 | Resolved for its reproductions | E002/E003: 1.0 -> 0.9; E001 stays 1.0; one axis-plus-radius/ellipse budget in source |
| Worker fault | Resolved for its reproductions | Three native crashes followed immediately by correct 1.0; one lost send retries; two lost sends raise scorer fault |

### Correct-plate boundary checks

**Fact:** **18 ordinary CadQuery styles x 6 specifications = 108/108 at 1.0**. This covers the 12 original ordinary C styles, arc-circle bores, all three whole-part mirror planes, a one-solid compound and a redundant coincident cut. **12 tolerance variants x 6 specifications = 72/72 at 1.0**: face, edge, vertex and all tolerances, each at 1e-6, 0.001 and 0.1 mm. Every strict Measurement in these 180 answers reports `boundary_consistent=True`.

[control-input.jsonl](scratch/control-input.jsonl) holds the sources and specs; [controls.jsonl](scratch/controls.jsonl) holds fresh reports and Measurements. All six specs belong to train or dev.

| Spec | Split | L x W x T, mm | Bore diameter / margin, mm | Ordinary pass/total | Metadata pass/total |
| --- | --- | --- | --- | --- | --- |
| gen-0215 | train | 168.0 x 78.5 x 3.0 | 8.0 / 21.5 | 18/18 | 12/12 |
| gen-0065 | train | 147.5 x 32.5 x 5.5 | 4.0 / 5.0 | 18/18 | 12/12 |
| gen-0032 | dev | 214.0 x 150.0 x 10.5 | 9.0 / 8.0 | 18/18 | 12/12 |
| gen-0208 | dev | 43.0 x 36.0 x 6.5 | 8.5 / 7.0 | 18/18 | 12/12 |
| gen-0001 | train | 74.5 x 81.0 x 4.5 | 10.5 / 24.5 | 18/18 | 12/12 |
| gen-0037 | dev | 207.0 x 93.5 x 3.0 | 6.0 / 15.0 | 18/18 | 12/12 |

| Ordinary construction | Pass/total | Correct rejected |
| --- | --- | --- |
| Sketch | 6/6 | none |
| Solid_primitives | 6/6 | none |
| arc_circle | 6/6 | none |
| clean | 6/6 | none |
| coincident_bore | 6/6 | none |
| compound_one | 6/6 | none |
| cutThruAll | 6/6 | none |
| explicit_depth | 6/6 | none |
| float_coordinates | 6/6 | none |
| imprinted_halves | 6/6 | none |
| mirror | 6/6 | none |
| mirror_XY | 6/6 | none |
| mirror_XZ | 6/6 | none |
| mirror_YZ | 6/6 | none |
| polyline | 6/6 | none |
| reference | 6/6 | none |
| translate_chain | 6/6 | none |
| union_halves | 6/6 | none |

| Inflated metadata | Tolerance, mm | Pass/total | Correct rejected |
| --- | --- | --- | --- |
| face | 1e-6 | 6/6 | none |
| face | 0.001 | 6/6 | none |
| face | 0.1 | 6/6 | none |
| edge | 1e-6 | 6/6 | none |
| edge | 0.001 | 6/6 | none |
| edge | 0.1 | 6/6 | none |
| vertex | 1e-6 | 6/6 | none |
| vertex | 0.001 | 6/6 | none |
| vertex | 0.1 | 6/6 | none |
| all | 1e-6 | 6/6 | none |
| all | 0.001 | 6/6 | none |
| all | 0.1 | 6/6 | none |

### Version 0.5.0 time per answer, before and after

**Fact:** the parent and current commit independently scored the exact same 180 correct answers **four times each**, 720 timed answers per implementation. Five untimed warmup answers precede each implementation. Wall-clock timing surrounds the public `score` call, including build, BREP serialization, measurement and IPC; worker startup is excluded. The benchmark jobs ran sequentially, after the corpus, recovery and compatibility jobs completed; no other audit geometry jobs overlapped them. All 1,440 timed results are 1.0.

These are local elapsed measurements, not portable speed guarantees. Order was parent then current, so system drift is a limitation. The difference includes all changes in `0f9119c`, not just the isolated cost of the boundary analyzer. The last after-round is visibly slower than its earlier rounds; the observed mean increase should not be read as a precise measurement of analyzer overhead. Raw trials: [bench-before.json](scratch/bench-before.json), [bench-branch.json](scratch/bench-branch.json).

| Answers | Before mean / median / p95, ms | After mean / median / p95, ms | Mean change |
| --- | --- | --- | --- |
| all | 83.095 / 78.274 / 109.691 | 91.387 / 84.961 / 132.599 | +8.293 ms (+10.0%) |
| ordinary | 82.182 / 77.343 / 110.188 | 91.318 / 84.263 / 131.754 | +9.136 ms (+11.1%) |
| metadata | 84.464 / 80.537 / 109.433 | 91.492 / 85.748 / 133.012 | +7.028 ms (+8.3%) |

| Timed round | Before mean, ms/answer | After mean, ms/answer |
| --- | --- | --- |
| 1 | 82.036 | 83.759 |
| 2 | 83.538 | 90.073 |
| 3 | 83.846 | 85.755 |
| 4 | 82.959 | 105.962 |

### Legacy comparison against main

**Fact:** separate processes independently executed all 3,161 answers, selecting the local main snapshot or the current worktree's explicit `version="0.4.0"`. The input remains the original 2,200 stable-hash-selected, AST-deduplicated train/dev programs plus all 961 saved evaluation rows. No cross-answer result cache was used. "Checks" below means the full mapping of check names to Boolean verdicts, matching the earlier comparison. Measurement dataclasses and check explanation strings are not the requested legacy equality target.

| Compared field | Answers compared | Differences |
| --- | --- | --- |
| reward | 3161 | 0 |
| checks | 3161 | 0 |
| parsed | 3161 | 0 |
| exception | 3161 | 0 |
| error | 3161 | 0 |
| Raw error texts, separately recorded | 3161 | 1 |

**Fact:** raw error differences occur at indices `[1362]`. Normalizing hexadecimal memory addresses with `0x[0-9a-fA-F]+` removes those differences; no other error-text normalization was applied. Main timeouts: `[648]`; branch timeouts: `[648]`. Summed elapsed times: main **119.205 s**, branch **107.773 s**. These legacy times are descriptive, not the 0.5.0 before/after benchmark.

Raw outputs: [compat-main.jsonl](scratch/compat-main.jsonl), [compat-branch.jsonl](scratch/compat-branch.jsonl); normalized errors: [compat-normalized-errors.jsonl](scratch/compat-normalized-errors.jsonl); summary: [compat-summary.json](scratch/compat-summary.json).

### README and CHANGELOG compared with implementation

**Fact:** source review covers the 0.5.0 scoring, tolerance, form, recovery and recorded-results statements. The existing 2,366-mutant suite was also rerun: **0 false full credit on 1646 wrong parts; 0 false rejection on 720 correct parts**. Exact failed-check agreement is **98.9%**, not 100%; the documented bore-lug classification limitation remains. [Fresh validation](scratch/validation/scorer-validation-0.5.0.md).

| Statement | Evidence / assessment |
| --- | --- |
| README 118 to 167, CHANGELOG 9 to 23: strict plate, 0.1 dimensional allowances, analytic supports, edge consistency, one bore budget | Matches code and requested reproductions. R9 uses 1e-7 with no dimensional eps addition; dimensional checks use 1e-9 slack. |
| CHANGELOG 22 to 23: unqualified values compared with 1e-9 slack | Clarify that this is dimensional slack. R9 form and residual thresholds do not add it. Optional wording correction, not an observed scoring defect. |
| README 168 to 171, CHANGELOG 20 to 22: measured envelope/bores and residual second look | Matches strict measure and rubric: 0.005 mm band, 0.001 mm3 extra/missing limit; residual can add failure only. |
| README 186 to 189: no proof that no wrong part passes | Appropriately scoped. Finite reruns support observed cases only. |
| README 36 and 552: 81 hand-labelled cases | Count agrees: test_rubric_050.py reports 81 cases including its legacy saved-answer check. |
| README 188 to 190: every review case pinned as a test | Too broad if read literally: the 473 external audit rows are not all individual in-repository tests. Major defect reproductions are pinned. Optional correction. |
| CHANGELOG 24 to 39: three broken drafts, AUDIT_/AUDIT3_/AUDIT4_ fixes | The cited scorer reports represent three pre-verification drafts; README also counts the earlier saved-answer discovery. This is consistent when the scopes are distinguished. |
| CHANGELOG 40 to 43: lost worker replacement and single retry; failed recovery is scorer fault | Supported by the native-crash sequence and both connection-loss injections. A crash during model execution remains a model BuildError; only already-lost sends are retried. |
| README 109 to 116, CHANGELOG 54 to 59: legacy remains selectable and recorded results preserved | Source and 3,161 comparisons support legacy geometry/scoring preservation, including normalized errors. The worker recovery change is shared by both versions, so exactly as it was is not literal for infrastructure-fault behavior. No historical evaluation verdict file is edited. Optional wording correction. |
| README 20 and 417, CHANGELOG 47 to 53: finite-suite zero false credit/rejection counts | Supported by fresh 2,366-mutant validation. Does not imply exact per-check agreement or a universal guarantee. |
| README 230 to 234, CHANGELOG 66 to 69: correct NURBS plates still rejected deliberately | Supported by all six C NURBS controls plus the other stored-spline controls; not a new boundary-check false rejection. |
| README 404 to 407, CHANGELOG 60 to 63: six changed sensitivity verdicts, gains +41.7/+40.8 | Fresh offline sensitivity rerun agrees with the checked-in sensitivity JSON; primary recorded results remain unchanged. |
| README/CHANGELOG calling the check sound | The former soundness claim is removed. Remaining statements describe tested behavior and expressly deny a proof. |

**Opinion:** apply the following optional wording correction. No repository edit was made.

```diff
--- a/README.md
+++ b/README.md
@@ -107,7 +107,7 @@
 ## Scoring
 
 **Two scorer versions live side by side.** 0.5.0 is the current one and
-judges every new run. 0.4.0 is kept exactly as it was, because **every
+judges every new run. 0.4.0 keeps its original geometry and tolerance policy, because **every
 result on this page recorded before 4 October 2026 (the leaderboard, the
 hint experiment, training run 1 and its replication) was scored under 0.4.0**
 and result files are replayed under the version they record. A recorded
@@ -185,9 +185,9 @@
    as the nominal faces joined by an edge lying off both, and scored 1.0
    (`AUDIT4_`).
 
-This is not a proof that no wrong part can pass. It is a scorer that handles
-every case four rounds of review could build, with each case pinned as a
-test.
+This is not a proof that no wrong part can pass. The major defects found
+in those reviews have pinned reproducing tests; the full external audit
+corpus is larger than the in-repository regression suite.
 
 Tolerances are inclusive: 6.6 mm is inside 6.5 +/- 0.1. Scorer 0.5.0
 compares unrounded measurements with 1e-9 mm of numerical slack, so
```

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -19,7 +19,7 @@
   tolerance. That tolerance is the kernel's resolution, 1e-7 mm, stated as
   a numerical equivalence. A volume comparison with the ideal part (0.001
   mm3 outside a 0.005 mm band) runs as a second look and can only add a
-  failure. Values are compared unrounded, with 1e-9 mm of slack. The hole
+  failure. Dimensional values are compared unrounded, with 1e-9 mm of slack. The hole
   pattern is matched one hole per position. Ten requirements.
 - **Three external audit rounds broke three drafts before merge** (5 October
   2026; `audit/scorer-0.5-audit.md`, `scorer-0.5-v2-audit.md`,
```

### Additional existing checks

**Fact:** `scripts/test_rubric_050.py`: **81/81 cases behaved as expected**. Targeted scorer-version tests: `10 passed in 10.72s`. The finite mutant validation and saved-answer sensitivity also completed successfully. [Commands and exit codes](scratch/commands.jsonl) and per-job logs retain execution evidence. The first control-driver attempt encountered a UTF-8 BOM in the inherited generator before scoring any control; BOM handling was corrected under v4 and the complete 180-answer control job reran successfully.

### Every earlier part, fresh score and failed-check evidence

**Fact:** this appendix lists all 473 IDs. Before is the prior report's observed score, not a new parent execution of the entire attack corpus. The performance benchmark does execute the parent independently. A before-score of zero on V077 to V080 came from a lost worker, so their new results are recovery evidence, not relaxed geometry rules. A083 still exceeds the 10-second budget. Error text in the table may be abbreviated for readability; raw complete records are linked above.

#### A series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| A001 | synthetic | nominal | 1.0 | 1.0 | none |
| A002 | synthetic | broad_pocket_0.001 | 0.9 | 0.9 | R9:no_other_features |
| A003 | synthetic | broad_pocket_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| A004 | synthetic | broad_pocket_0.005 | 0.9 | 0.9 | R9:no_other_features |
| A005 | synthetic | broad_pocket_0.0051 | 0.9 | 0.9 | R9:no_other_features |
| A006 | synthetic | broad_pocket_0.006 | 0.9 | 0.9 | R9:no_other_features |
| A007 | synthetic | broad_pocket_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A008 | synthetic | boss_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| A009 | synthetic | boss_0.0051 | 0.9 | 0.9 | R9:no_other_features |
| A010 | synthetic | boss_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A011 | synthetic | boss_0.1 | 0.0 | 0.0 | gate:simple_through_holes, R9:no_other_features |
| A012 | synthetic | edge_notch_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| A013 | synthetic | edge_notch_0.0051 | 0.9 | 0.9 | R9:no_other_features |
| A014 | synthetic | edge_notch_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A015 | synthetic | small_pocket_0.005 | 0.9 | 0.9 | R9:no_other_features |
| A016 | synthetic | small_pocket_0.02 | 0.9 | 0.9 | R9:no_other_features |
| A017 | synthetic | small_pocket_0.1 | 0.9 | 0.9 | R9:no_other_features |
| A018 | synthetic | deep_narrow_slot_0.039 | 0.0 | 0.0 | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |
| A019 | synthetic | deep_narrow_slot_0.041 | 0.0 | 0.0 | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |
| A020 | synthetic | deep_narrow_slot_0.05 | 0.0 | 0.0 | execution failed [raised in other library]: SyntaxError: unmatched ')' (<model>, line 11) |
| A021 | synthetic | side_tab_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| A022 | synthetic | top_lip_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| A023 | synthetic | side_tab_0.0051 | 0.9 | 0.9 | R9:no_other_features |
| A024 | synthetic | top_lip_0.0051 | 0.9 | 0.9 | R9:no_other_features |
| A025 | synthetic | side_tab_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A026 | synthetic | top_lip_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A027 | synthetic | rotate_Z_0.0001 | 0.9 | 0.9 | R9:no_other_features |
| A028 | synthetic | rotate_X_0.0001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A029 | synthetic | rotate_Z_0.001 | 0.9 | 0.9 | R9:no_other_features |
| A030 | synthetic | rotate_X_0.001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A031 | synthetic | rotate_Z_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A032 | synthetic | rotate_X_0.01 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A033 | synthetic | rotate_Z_0.05 | 0.9 | 0.9 | R9:no_other_features |
| A034 | synthetic | rotate_X_0.05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A035 | synthetic | draft_0.001 | 0.9 | 0.9 | R9:no_other_features |
| A036 | synthetic | draft_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A037 | synthetic | draft_0.1 | 0.9 | 0.9 | R9:no_other_features |
| A038 | synthetic | sheared_0.004 | 0.9 | 0.9 | R9:no_other_features |
| A039 | synthetic | sheared_0.02 | 0.9 | 0.9 | R9:no_other_features |
| A040 | synthetic | cone_0.001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A041 | synthetic | cone_0.01 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A042 | synthetic | ellipse | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A043 | synthetic | polygon_128 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A044 | synthetic | nurbs_exact | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| A045 | synthetic | countersink_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| A046 | synthetic | countersink_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A047 | synthetic | fifth_bore | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin |
| A048 | synthetic | coincident_bore | 1.0 | 1.0 | none |
| A049 | synthetic | overlap_bore_0.0004 | 0.9 | 0.9 | R9:no_other_features |
| A050 | synthetic | overlap_bore_0.004 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features |
| A051 | synthetic | overlap_bore_0.01 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features |
| A052 | synthetic | coaxial_step | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| A053 | synthetic | probe_lug_y0_d0.004 | 0.9 | 0.9 | R9:no_other_features |
| A054 | synthetic | probe_lug_y0_d0.05 | 0.9 | 0.9 | R9:no_other_features |
| A055 | synthetic | probe_lug_y0.3_d0.004 | 1.0 | 1.0 | none |
| A056 | synthetic | probe_lug_y0.3_d0.05 | 0.9 | 0.9 | R9:no_other_features |
| A057 | synthetic | probe_notch | 0.9 | 0.9 | R9:no_other_features |
| A058 | synthetic | compound_one | 1.0 | 1.0 | none |
| A059 | synthetic | second_solid_bore | 0.0 | 0.0 | gate:single_solid, gate:simple_through_holes, R9:no_other_features |
| A060 | synthetic | second_solid_outside | 0.0 | 0.0 | gate:single_solid, R1:length, R7:edge_margin, R9:no_other_features |
| A061 | synthetic | loose_face | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| A062 | synthetic | loose_edge | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| A063 | synthetic | length_0.1 | 1.0 | 1.0 | none |
| A064 | synthetic | diameter_0.1 | 1.0 | 1.0 | none |
| A065 | synthetic | z_datum_0.1 | 1.0 | 1.0 | none |
| A066 | synthetic | length_0.100001 | 0.9 | 0.9 | R1:length |
| A067 | synthetic | diameter_0.100001 | 0.9 | 0.9 | R4b:hole_diameter |
| A068 | synthetic | z_datum_0.100001 | 0.9 | 0.9 | R8:z_datum |
| A069 | synthetic | length_0.10004 | 0.9 | 0.9 | R1:length |
| A070 | synthetic | diameter_0.10004 | 0.9 | 0.9 | R4b:hole_diameter |
| A071 | synthetic | z_datum_0.10004 | 0.9 | 0.9 | R8:z_datum |
| A072 | synthetic | length_0.1001 | 0.9 | 0.9 | R1:length |
| A073 | synthetic | diameter_0.1001 | 0.9 | 0.9 | R4b:hole_diameter |
| A074 | synthetic | z_datum_0.1001 | 0.9 | 0.9 | R8:z_datum |
| A075 | synthetic | centres_0.1 | 1.0 | 1.0 | none |
| A076 | synthetic | centres_0.1004 | 0.9 | 0.9 | R5:hole_pattern |
| A077 | synthetic | centres_0.10049 | 0.9 | 0.9 | R5:hole_pattern |
| A078 | synthetic | centres_0.1005 | 0.9 | 0.9 | R5:hole_pattern |
| A079 | synthetic | centres_0.101 | 0.9 | 0.9 | R5:hole_pattern |
| A080 | synthetic | residual_None_thin | 0.8 | 0.8 | R3:thickness, R9:no_other_features |
| A081 | synthetic | many_bores_16 | 0.0 | 0.0 | gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin |
| A082 | synthetic | many_bores_64 | 0.0 | 0.0 | gate:hole_count_sane, R4a:hole_count, R4b:hole_diameter, R7:edge_margin |
| A083 | synthetic | many_bores_144 | 0.0 | 0.0 | model code exceeded 10s execution budget |
| A084 | synthetic | threshold_through_slot_0.0128 | 0.9 | 0.9 | R9:no_other_features |
| A085 | synthetic | threshold_through_slot_0.01295 | 0.9 | 0.9 | R9:no_other_features |
| A086 | synthetic | threshold_through_slot_0.013 | 0.9 | 0.9 | R9:no_other_features |
| A087 | synthetic | threshold_through_slot_0.0131 | 0.9 | 0.9 | R9:no_other_features |
| A088 | synthetic | two_broad_pockets_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| A089 | synthetic | two_broad_pockets_0.005 | 0.9 | 0.9 | R9:no_other_features |
| A090 | synthetic | six_skin_pockets | 0.0 | 0.0 | gate:single_solid, R9:no_other_features |
| A091 | synthetic | actual_probe_lug_0.163 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features |
| A092 | synthetic | actual_probe_lug_0.17 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features |
| A093 | synthetic | actual_probe_lug_0.2 | 0.7 | 0.7 | R4a:hole_count, R5:hole_pattern, R9:no_other_features |
| A094 | synthetic | tiny_fifth_0.005 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin |
| A095 | synthetic | hidden_fifth_0.005 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A096 | synthetic | tiny_fifth_0.006 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin |
| A097 | synthetic | hidden_fifth_0.006 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A098 | synthetic | tiny_fifth_0.007 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin |
| A099 | synthetic | hidden_fifth_0.007 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A100 | synthetic | tiny_fifth_0.01 | 0.7 | 0.7 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin |
| A101 | synthetic | hidden_fifth_0.01 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A102 | synthetic | bore_annular_membrane | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features |
| A103 | synthetic | top_chamfer_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| A104 | synthetic | top_chamfer_0.0051 | 0.9 | 0.9 | R9:no_other_features |
| A105 | synthetic | top_chamfer_0.01 | 0.9 | 0.9 | R9:no_other_features |
| A106 | synthetic | corner_fillet_0.001 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| A107 | synthetic | corner_fillet_0.005 | 0.9 | 0.9 | R9:no_other_features |
| A108 | synthetic | corner_fillet_0.02 | 0.9 | 0.9 | R9:no_other_features |
| A109 | synthetic | fixed_deep_slot_0.039 | 0.9 | 0.9 | R9:no_other_features |
| A110 | synthetic | fixed_deep_slot_0.041 | 0.9 | 0.9 | R9:no_other_features |
| A111 | synthetic | fixed_deep_slot_0.05 | 0.9 | 0.9 | R9:no_other_features |
| A112 | synthetic | hide_fifth_r0.003_h0.02 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A113 | synthetic | hide_fifth_r0.003_h0.1 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A114 | synthetic | hide_fifth_r0.005_h0.02 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A115 | synthetic | hide_fifth_r0.005_h0.1 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A116 | synthetic | hide_fifth_r0.007_h0.02 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A117 | synthetic | hide_fifth_r0.007_h0.1 | 0.6 | 0.6 | R4a:hole_count, R4b:hole_diameter, R7:edge_margin, R9:no_other_features |
| A118 | gen-0032 | largest_skin_gen-0032 | 0.9 | 0.9 | R9:no_other_features |
| A119 | gen-0215 | largest_skin_gen-0215 | 0.9 | 0.9 | R9:no_other_features |
| A120 | synthetic | fillet_0.025 | 0.9 | 0.9 | R9:no_other_features |
| A121 | synthetic | fillet_0.03 | 0.9 | 0.9 | R9:no_other_features |
| A122 | synthetic | fillet_0.04 | 0.9 | 0.9 | R9:no_other_features |
| A123 | synthetic | fillet_0.05 | 0.9 | 0.9 | R9:no_other_features |
| A124 | synthetic | annular_bridge_2e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features |
| A125 | synthetic | annular_bridge_3e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features |
| A126 | synthetic | annular_bridge_4e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R9:no_other_features |
| A127 | synthetic | diagonal_rounding | 0.9 | 0.9 | R5:hole_pattern |
| A128 | synthetic | length_0.100049 | 0.9 | 0.9 | R1:length |
| A129 | synthetic | diameter_0.100049 | 0.9 | 0.9 | R4b:hole_diameter |
| A130 | synthetic | margin_0.1004 | 0.8 | 0.8 | R5:hole_pattern, R7:edge_margin |

#### C series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| C001 | gen-0215 | reference | 1.0 | 1.0 | none |
| C002 | gen-0215 | Sketch | 1.0 | 1.0 | none |
| C003 | gen-0215 | polyline | 1.0 | 1.0 | none |
| C004 | gen-0215 | cutThruAll | 1.0 | 1.0 | none |
| C005 | gen-0215 | explicit_depth | 1.0 | 1.0 | none |
| C006 | gen-0215 | union_halves | 1.0 | 1.0 | none |
| C007 | gen-0215 | imprinted_halves | 1.0 | 1.0 | none |
| C008 | gen-0215 | mirror | 1.0 | 1.0 | none |
| C009 | gen-0215 | translate_chain | 1.0 | 1.0 | none |
| C010 | gen-0215 | Solid_primitives | 1.0 | 1.0 | none |
| C011 | gen-0215 | clean | 1.0 | 1.0 | none |
| C012 | gen-0215 | float_coordinates | 1.0 | 1.0 | none |
| C013 | gen-0215 | nurbs_exact | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C014 | gen-0065 | reference | 1.0 | 1.0 | none |
| C015 | gen-0065 | Sketch | 1.0 | 1.0 | none |
| C016 | gen-0065 | polyline | 1.0 | 1.0 | none |
| C017 | gen-0065 | cutThruAll | 1.0 | 1.0 | none |
| C018 | gen-0065 | explicit_depth | 1.0 | 1.0 | none |
| C019 | gen-0065 | union_halves | 1.0 | 1.0 | none |
| C020 | gen-0065 | imprinted_halves | 1.0 | 1.0 | none |
| C021 | gen-0065 | mirror | 1.0 | 1.0 | none |
| C022 | gen-0065 | translate_chain | 1.0 | 1.0 | none |
| C023 | gen-0065 | Solid_primitives | 1.0 | 1.0 | none |
| C024 | gen-0065 | clean | 1.0 | 1.0 | none |
| C025 | gen-0065 | float_coordinates | 1.0 | 1.0 | none |
| C026 | gen-0065 | nurbs_exact | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C027 | gen-0032 | reference | 1.0 | 1.0 | none |
| C028 | gen-0032 | Sketch | 1.0 | 1.0 | none |
| C029 | gen-0032 | polyline | 1.0 | 1.0 | none |
| C030 | gen-0032 | cutThruAll | 1.0 | 1.0 | none |
| C031 | gen-0032 | explicit_depth | 1.0 | 1.0 | none |
| C032 | gen-0032 | union_halves | 1.0 | 1.0 | none |
| C033 | gen-0032 | imprinted_halves | 1.0 | 1.0 | none |
| C034 | gen-0032 | mirror | 1.0 | 1.0 | none |
| C035 | gen-0032 | translate_chain | 1.0 | 1.0 | none |
| C036 | gen-0032 | Solid_primitives | 1.0 | 1.0 | none |
| C037 | gen-0032 | clean | 1.0 | 1.0 | none |
| C038 | gen-0032 | float_coordinates | 1.0 | 1.0 | none |
| C039 | gen-0032 | nurbs_exact | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C040 | gen-0208 | reference | 1.0 | 1.0 | none |
| C041 | gen-0208 | Sketch | 1.0 | 1.0 | none |
| C042 | gen-0208 | polyline | 1.0 | 1.0 | none |
| C043 | gen-0208 | cutThruAll | 1.0 | 1.0 | none |
| C044 | gen-0208 | explicit_depth | 1.0 | 1.0 | none |
| C045 | gen-0208 | union_halves | 1.0 | 1.0 | none |
| C046 | gen-0208 | imprinted_halves | 1.0 | 1.0 | none |
| C047 | gen-0208 | mirror | 1.0 | 1.0 | none |
| C048 | gen-0208 | translate_chain | 1.0 | 1.0 | none |
| C049 | gen-0208 | Solid_primitives | 1.0 | 1.0 | none |
| C050 | gen-0208 | clean | 1.0 | 1.0 | none |
| C051 | gen-0208 | float_coordinates | 1.0 | 1.0 | none |
| C052 | gen-0208 | nurbs_exact | 0.0 | 0.0 | gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C053 | gen-0001 | reference | 1.0 | 1.0 | none |
| C054 | gen-0001 | Sketch | 1.0 | 1.0 | none |
| C055 | gen-0001 | polyline | 1.0 | 1.0 | none |
| C056 | gen-0001 | cutThruAll | 1.0 | 1.0 | none |
| C057 | gen-0001 | explicit_depth | 1.0 | 1.0 | none |
| C058 | gen-0001 | union_halves | 1.0 | 1.0 | none |
| C059 | gen-0001 | imprinted_halves | 1.0 | 1.0 | none |
| C060 | gen-0001 | mirror | 1.0 | 1.0 | none |
| C061 | gen-0001 | translate_chain | 1.0 | 1.0 | none |
| C062 | gen-0001 | Solid_primitives | 1.0 | 1.0 | none |
| C063 | gen-0001 | clean | 1.0 | 1.0 | none |
| C064 | gen-0001 | float_coordinates | 1.0 | 1.0 | none |
| C065 | gen-0001 | nurbs_exact | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C066 | gen-0037 | reference | 1.0 | 1.0 | none |
| C067 | gen-0037 | Sketch | 1.0 | 1.0 | none |
| C068 | gen-0037 | polyline | 1.0 | 1.0 | none |
| C069 | gen-0037 | cutThruAll | 1.0 | 1.0 | none |
| C070 | gen-0037 | explicit_depth | 1.0 | 1.0 | none |
| C071 | gen-0037 | union_halves | 1.0 | 1.0 | none |
| C072 | gen-0037 | imprinted_halves | 1.0 | 1.0 | none |
| C073 | gen-0037 | mirror | 1.0 | 1.0 | none |
| C074 | gen-0037 | translate_chain | 1.0 | 1.0 | none |
| C075 | gen-0037 | Solid_primitives | 1.0 | 1.0 | none |
| C076 | gen-0037 | clean | 1.0 | 1.0 | none |
| C077 | gen-0037 | float_coordinates | 1.0 | 1.0 | none |
| C078 | gen-0037 | nurbs_exact | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| C079 | synthetic | arc_circle | 1.0 | 1.0 | none |

#### N series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| N001 | synthetic | full_face_pocket_3e-07 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| N002 | synthetic | full_face_pocket_5e-07 | 0.0 | 0.0 | gate:single_solid, R9:no_other_features |
| N003 | synthetic | full_face_pocket_8e-07 | 0.9 | 0.9 | R9:no_other_features |
| N004 | synthetic | full_face_pocket_1.2e-06 | 0.9 | 0.9 | R9:no_other_features |
| N005 | synthetic | full_face_pocket_2e-06 | 0.9 | 0.9 | R9:no_other_features |
| N006 | synthetic | rotation_Z_3e-10_rad | 1.0 | 1.0 | none |
| N007 | synthetic | rotation_X_3e-10_rad | 1.0 | 1.0 | none |
| N008 | synthetic | rotation_Z_8e-10_rad | 1.0 | 1.0 | none |
| N009 | synthetic | rotation_X_8e-10_rad | 1.0 | 1.0 | none |
| N010 | synthetic | rotation_Z_1.2e-09_rad | 1.0 | 1.0 | none |
| N011 | synthetic | rotation_X_1.2e-09_rad | 1.0 | 1.0 | none |
| N012 | synthetic | rotation_Z_2e-09_rad | 0.9 | 0.9 | R9:no_other_features |
| N013 | synthetic | rotation_X_2e-09_rad | 0.9 | 0.9 | R9:no_other_features |
| N014 | synthetic | warped_spline_pole_1e-08 | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRep.BRep_Builder, F: OCP.OCP.TopoDS.TopoDS_Face, S: OCP.OCP.Geom.Geom_Surf |
| N015 | synthetic | warped_spline_pole_5e-08 | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRep.BRep_Builder, F: OCP.OCP.TopoDS.TopoDS_Face, S: OCP.OCP.Geom.Geom_Surf |
| N016 | synthetic | warped_spline_pole_1e-07 | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRep.BRep_Builder, F: OCP.OCP.TopoDS.TopoDS_Face, S: OCP.OCP.Geom.Geom_Surf |
| N017 | synthetic | warped_spline_pole_2e-07 | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRep.BRep_Builder, F: OCP.OCP.TopoDS.TopoDS_Face, S: OCP.OCP.Geom.Geom_Surf |
| N018 | synthetic | warped_spline_pole_1e-05 | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRep.BRep_Builder, F: OCP.OCP.TopoDS.TopoDS_Face, S: OCP.OCP.Geom.Geom_Surf |
| N019 | synthetic | warped_spline_pole_0.001 | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: UpdateFace(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRep.BRep_Builder, F: OCP.OCP.TopoDS.TopoDS_Face, S: OCP.OCP.Geom.Geom_Surf |
| N020 | synthetic | far_origin_pocket_0.001 | 0.9 | 0.9 | R9:no_other_features |
| N021 | synthetic | far_origin_pocket_0.004 | 0.9 | 0.9 | R9:no_other_features |
| N022 | synthetic | far_origin_pocket_0.0049 | 0.9 | 0.9 | R9:no_other_features |
| N023 | synthetic | far_origin_pocket_0.006 | 0.9 | 0.9 | R9:no_other_features |
| N024 | synthetic | micro_counterbore_5e-07 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| N025 | synthetic | micro_counterbore_8e-07 | 1.0 | 0.9 | R9:no_other_features |
| N026 | synthetic | micro_counterbore_1.2e-06 | 1.0 | 0.9 | R9:no_other_features |
| N027 | synthetic | loose_envelope_face | 0.0 | 0.0 | gate:clean_solid, gate:is_plate, R2:width, R6:material, R7:edge_margin, R9:no_other_features |
| N028 | synthetic | second_coincident_solid | 0.0 | 0.0 | gate:single_solid, gate:is_plate, R6:material |
| N029 | gen-0032 | largest_micro_pocket | 0.9 | 0.9 | R9:no_other_features |

#### D series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| D001 | synthetic | warped_spline_pole_1e-08_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D002 | synthetic | warped_spline_pole_5e-08_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D003 | synthetic | warped_spline_pole_1e-07_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D004 | synthetic | warped_spline_pole_2e-07_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D005 | synthetic | warped_spline_pole_1e-05_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D006 | synthetic | warped_spline_pole_0.001_fixed | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D007 | synthetic | spline_degree4_amp1e-07 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D008 | synthetic | spline_degree4_amp1e-05 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D009 | synthetic | spline_degree4_amp0.001 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D010 | synthetic | spline_degree4_amp0.004 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D011 | synthetic | spline_degree8_amp1e-07 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D012 | synthetic | spline_degree8_amp1e-05 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D013 | synthetic | spline_degree8_amp0.001 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D014 | synthetic | spline_degree8_amp0.004 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D015 | synthetic | spline_degree16_amp1e-07 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D016 | synthetic | spline_degree16_amp1e-05 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D017 | synthetic | spline_degree16_amp0.001 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D018 | synthetic | spline_degree16_amp0.004 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| D019 | synthetic | spline_degree32_amp1e-07 | 0.0 | 0.0 | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value |
| D020 | synthetic | spline_degree32_amp1e-05 | 0.0 | 0.0 | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value |
| D021 | synthetic | spline_degree32_amp0.001 | 0.0 | 0.0 | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value |
| D022 | synthetic | spline_degree32_amp0.004 | 0.0 | 0.0 | execution failed [raised in model code]: Standard_ConstructionError: Geom_BSplineSurface::IncreaseDegree: bad U degree value |
| D023 | synthetic | cylinder_spline_warp1e-08 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| D024 | synthetic | cylinder_spline_warp1e-07 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| D025 | synthetic | cylinder_spline_warp1e-06 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| D026 | synthetic | cylinder_spline_warp1e-05 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| D027 | synthetic | cylinder_spline_warp0.001 | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| D032 | synthetic | micro_pocket_depth8e-07 | 0.9 | 0.9 | R9:no_other_features |
| D033 | synthetic | micro_pocket_depth9.9e-07 | 0.9 | 0.9 | R9:no_other_features |
| D034 | synthetic | micro_pocket_depth1e-06 | 0.9 | 0.9 | R9:no_other_features |
| D035 | synthetic | micro_pocket_depth1.01e-06 | 0.9 | 0.9 | R9:no_other_features |
| D036 | synthetic | micro_pocket_depth1.2e-06 | 0.9 | 0.9 | R9:no_other_features |
| D037 | synthetic | micro_pocket_depth0.0049 | 0.9 | 0.9 | R9:no_other_features |
| D038 | synthetic | counterbore_dr4e-07_depth0.0049 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| D039 | synthetic | counterbore_dr4e-07_depth0.006 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| D040 | synthetic | counterbore_dr4e-07_depth3 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| D041 | synthetic | counterbore_dr4e-07_depth6 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| D042 | synthetic | counterbore_dr4.9e-07_depth0.0049 | 0.9 | 0.9 | R9:no_other_features |
| D043 | synthetic | counterbore_dr4.9e-07_depth0.006 | 0.9 | 0.9 | R9:no_other_features |
| D044 | synthetic | counterbore_dr4.9e-07_depth3 | 0.9 | 0.9 | R9:no_other_features |
| D045 | synthetic | counterbore_dr4.9e-07_depth6 | 1.0 | 1.0 | none |
| D046 | synthetic | counterbore_dr6e-07_depth0.0049 | 0.9 | 0.9 | R9:no_other_features |
| D047 | synthetic | counterbore_dr6e-07_depth0.006 | 0.9 | 0.9 | R9:no_other_features |
| D048 | synthetic | counterbore_dr6e-07_depth3 | 0.9 | 0.9 | R9:no_other_features |
| D049 | synthetic | counterbore_dr6e-07_depth6 | 1.0 | 1.0 | none |
| D050 | synthetic | counterbore_dr1e-06_depth0.0049 | 0.9 | 0.9 | R9:no_other_features |
| D051 | synthetic | counterbore_dr1e-06_depth0.006 | 0.9 | 0.9 | R9:no_other_features |
| D052 | synthetic | counterbore_dr1e-06_depth3 | 0.9 | 0.9 | R9:no_other_features |
| D053 | synthetic | counterbore_dr1e-06_depth6 | 1.0 | 1.0 | none |
| D054 | gen-0032 | large_far_origin_depth0.0049 | 0.9 | 0.9 | R9:no_other_features |
| D055 | gen-0032 | large_far_origin_depth0.005 | 0.9 | 0.9 | R9:no_other_features |
| D056 | gen-0032 | large_far_origin_depth0.0051 | 0.9 | 0.9 | R9:no_other_features |

#### S series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| S001 | synthetic | sewn_bezier_plate_0 | 0.9 | 0.9 | R9:no_other_features |
| S002 | synthetic | sewn_bezier_plate_1e-08 | 0.9 | 0.9 | R9:no_other_features |
| S003 | synthetic | sewn_bezier_plate_5e-08 | 0.9 | 0.9 | R9:no_other_features |
| S004 | synthetic | sewn_bezier_plate_1e-07 | 0.9 | 0.9 | R9:no_other_features |
| S005 | synthetic | sewn_bezier_plate_2e-07 | 0.9 | 0.9 | R9:no_other_features |
| S006 | synthetic | sewn_bezier_plate_8e-07 | 0.9 | 0.9 | R9:no_other_features |
| S007 | synthetic | sewn_bezier_plate_1e-05 | 0.9 | 0.9 | R9:no_other_features |
| S008 | synthetic | sewn_bezier_plate_0.001 | 0.9 | 0.9 | R9:no_other_features |
| S009 | synthetic | revolved_bezier_bore_0 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| S010 | synthetic | revolved_bezier_bore_1e-08 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| S011 | synthetic | revolved_bezier_bore_5e-08 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| S012 | synthetic | revolved_bezier_bore_1e-07 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| S013 | synthetic | revolved_bezier_bore_2e-07 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| S014 | synthetic | revolved_bezier_bore_8e-07 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| S015 | synthetic | revolved_bezier_bore_1e-05 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |
| S016 | synthetic | revolved_bezier_bore_0.001 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R7:edge_margin, R9:no_other_features |

#### L series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| L001 | synthetic | local_spline_0.123_0.001_1e-05 | 0.9 | 0.9 | R9:no_other_features |
| L002 | synthetic | local_spline_0.123_0.001_0.001 | 0.9 | 0.9 | R9:no_other_features |
| L003 | synthetic | local_spline_0.123_0.001_0.004 | 0.9 | 0.9 | R9:no_other_features |
| L004 | synthetic | local_spline_0.127_0.0001_1e-05 | 0.9 | 0.9 | R9:no_other_features |
| L005 | synthetic | local_spline_0.127_0.0001_0.001 | 0.9 | 0.9 | R9:no_other_features |
| L006 | synthetic | local_spline_0.127_0.0001_0.004 | 0.9 | 0.9 | R9:no_other_features |
| L007 | synthetic | local_spline_0.333_0.001_1e-05 | 0.9 | 0.9 | R9:no_other_features |
| L008 | synthetic | local_spline_0.333_0.001_0.001 | 0.9 | 0.9 | R9:no_other_features |
| L009 | synthetic | local_spline_0.333_0.001_0.004 | 0.9 | 0.9 | R9:no_other_features |
| L010 | synthetic | local_spline_0.501_0.0001_1e-05 | 0.9 | 0.9 | R9:no_other_features |
| L011 | synthetic | local_spline_0.501_0.0001_0.001 | 0.9 | 0.9 | R9:no_other_features |
| L012 | synthetic | local_spline_0.501_0.0001_0.004 | 0.9 | 0.9 | R9:no_other_features |

#### T series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| T001 | synthetic | local_spline_scale_0.01 | 0.9 | 0.9 | R9:no_other_features |
| T002 | synthetic | local_spline_scale_0.1 | 0.9 | 0.9 | R9:no_other_features |
| T003 | synthetic | local_spline_scale_1 | 0.9 | 0.9 | R9:no_other_features |
| T004 | synthetic | local_spline_scale_5 | 0.9 | 0.9 | R9:no_other_features |

#### V series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| V001 | synthetic-v3 | large_tolerance_face_1e-06 | 1.0 | 1.0 | none |
| V002 | synthetic-v3 | large_tolerance_face_0.001 | 1.0 | 1.0 | none |
| V003 | synthetic-v3 | large_tolerance_face_0.1 | 1.0 | 1.0 | none |
| V004 | synthetic-v3 | large_tolerance_edge_1e-06 | 1.0 | 1.0 | none |
| V005 | synthetic-v3 | large_tolerance_edge_0.001 | 1.0 | 1.0 | none |
| V006 | synthetic-v3 | large_tolerance_edge_0.1 | 1.0 | 1.0 | none |
| V007 | synthetic-v3 | large_tolerance_vertex_1e-06 | 1.0 | 1.0 | none |
| V008 | synthetic-v3 | large_tolerance_vertex_0.001 | 1.0 | 1.0 | none |
| V009 | synthetic-v3 | large_tolerance_vertex_0.1 | 1.0 | 1.0 | none |
| V010 | synthetic-v3 | large_tolerance_all_1e-06 | 1.0 | 1.0 | none |
| V011 | synthetic-v3 | large_tolerance_all_0.001 | 1.0 | 1.0 | none |
| V012 | synthetic-v3 | large_tolerance_all_0.1 | 1.0 | 1.0 | none |
| V013 | synthetic-v3 | ordinary_pocket_depth5e-08 | 0.0 | 0.0 | execution failed [raised in cadquery: Solid.makeBox]: Standard_DomainError:  |
| V014 | synthetic-v3 | ordinary_boss_height5e-08 | 1.0 | 1.0 | none |
| V015 | synthetic-v3 | ordinary_pocket_depth9e-08 | 0.0 | 0.0 | execution failed [raised in cadquery: Solid.makeBox]: Standard_DomainError:  |
| V016 | synthetic-v3 | ordinary_boss_height9e-08 | 1.0 | 1.0 | none |
| V017 | synthetic-v3 | ordinary_pocket_depth9.9e-08 | 0.0 | 0.0 | execution failed [raised in cadquery: Solid.makeBox]: Standard_DomainError:  |
| V018 | synthetic-v3 | ordinary_boss_height9.9e-08 | 1.0 | 1.0 | none |
| V019 | synthetic-v3 | ordinary_pocket_depth1.01e-07 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| V020 | synthetic-v3 | ordinary_boss_height1.01e-07 | 0.9 | 0.9 | R9:no_other_features |
| V021 | synthetic-v3 | ordinary_pocket_depth2e-07 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| V022 | synthetic-v3 | ordinary_boss_height2e-07 | 0.9 | 0.9 | R9:no_other_features |
| V023 | synthetic-v3 | ordinary_pocket_depth3e-07 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| V024 | synthetic-v3 | ordinary_boss_height3e-07 | 0.9 | 0.9 | R9:no_other_features |
| V025 | synthetic-v3 | ordinary_rotation_Z_deg1e-10 | 1.0 | 1.0 | none |
| V026 | synthetic-v3 | ordinary_rotation_Z_deg1e-09 | 1.0 | 1.0 | none |
| V027 | synthetic-v3 | ordinary_rotation_Z_deg1e-08 | 1.0 | 1.0 | none |
| V028 | synthetic-v3 | ordinary_rotation_Z_deg1e-07 | 0.9 | 0.9 | R9:no_other_features |
| V029 | synthetic-v3 | diameter_boundary_plus0 | 1.0 | 1.0 | none |
| V030 | synthetic-v3 | z_datum_boundary_plus0 | 1.0 | 1.0 | none |
| V031 | synthetic-v3 | length_boundary_plus0 | 1.0 | 1.0 | none |
| V032 | synthetic-v3 | pattern_boundary_plus0 | 1.0 | 1.0 | none |
| V033 | synthetic-v3 | diameter_boundary_plus5e-10 | 1.0 | 1.0 | none |
| V034 | synthetic-v3 | z_datum_boundary_plus5e-10 | 1.0 | 1.0 | none |
| V035 | synthetic-v3 | length_boundary_plus5e-10 | 1.0 | 1.0 | none |
| V036 | synthetic-v3 | pattern_boundary_plus5e-10 | 1.0 | 1.0 | none |
| V037 | synthetic-v3 | diameter_boundary_plus9e-10 | 1.0 | 1.0 | none |
| V038 | synthetic-v3 | z_datum_boundary_plus9e-10 | 1.0 | 1.0 | none |
| V039 | synthetic-v3 | length_boundary_plus9e-10 | 1.0 | 1.0 | none |
| V040 | synthetic-v3 | pattern_boundary_plus9e-10 | 1.0 | 1.0 | none |
| V041 | synthetic-v3 | diameter_boundary_plus1.1e-09 | 0.9 | 0.9 | R4b:hole_diameter |
| V042 | synthetic-v3 | z_datum_boundary_plus1.1e-09 | 0.9 | 0.9 | R8:z_datum |
| V043 | synthetic-v3 | length_boundary_plus1.1e-09 | 0.9 | 0.9 | R1:length |
| V044 | synthetic-v3 | pattern_boundary_plus1.1e-09 | 0.9 | 0.9 | R5:hole_pattern |
| V045 | synthetic-v3 | diameter_boundary_plus2e-09 | 0.9 | 0.9 | R4b:hole_diameter |
| V046 | synthetic-v3 | z_datum_boundary_plus2e-09 | 0.9 | 0.9 | R8:z_datum |
| V047 | synthetic-v3 | length_boundary_plus2e-09 | 0.9 | 0.9 | R1:length |
| V048 | synthetic-v3 | pattern_boundary_plus2e-09 | 0.9 | 0.9 | R5:hole_pattern |
| V049 | synthetic-v3 | diameter_boundary_plus1e-08 | 0.9 | 0.9 | R4b:hole_diameter |
| V050 | synthetic-v3 | z_datum_boundary_plus1e-08 | 0.9 | 0.9 | R8:z_datum |
| V051 | synthetic-v3 | length_boundary_plus1e-08 | 0.9 | 0.9 | R1:length |
| V052 | synthetic-v3 | pattern_boundary_plus1e-08 | 0.9 | 0.9 | R5:hole_pattern |
| V053 | synthetic-v3 | plane_origin_10000.0_reverseFalse | 1.0 | 1.0 | none |
| V054 | synthetic-v3 | plane_origin_10000.0_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:is_plate, R6:material, R9:no_other_features |
| V055 | synthetic-v3 | plane_origin_100000000.0_reverseFalse | 1.0 | 1.0 | none |
| V056 | synthetic-v3 | plane_origin_100000000.0_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:is_plate, R6:material, R9:no_other_features |
| V057 | synthetic-v3 | plane_origin_1000000000000.0_reverseFalse | 1.0 | 1.0 | none |
| V058 | synthetic-v3 | plane_origin_1000000000000.0_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:is_plate, R6:material, R9:no_other_features |
| V059 | synthetic-v3 | remote_cylinder_-1000000.0_dx0_reverseFalse | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V060 | synthetic-v3 | remote_cylinder_-1000000.0_dx0_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V061 | synthetic-v3 | remote_cylinder_-1000000.0_dx1e-09_reverseFalse | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V062 | synthetic-v3 | remote_cylinder_-1000000.0_dx1e-09_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V063 | synthetic-v3 | remote_cylinder_-1000000.0_dx3e-08_reverseFalse | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V064 | synthetic-v3 | remote_cylinder_-1000000.0_dx3e-08_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V065 | synthetic-v3 | remote_cylinder_1000000.0_dx0_reverseFalse | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V066 | synthetic-v3 | remote_cylinder_1000000.0_dx0_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V067 | synthetic-v3 | remote_cylinder_1000000.0_dx1e-09_reverseFalse | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V068 | synthetic-v3 | remote_cylinder_1000000.0_dx1e-09_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V069 | synthetic-v3 | remote_cylinder_1000000.0_dx3e-08_reverseFalse | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V070 | synthetic-v3 | remote_cylinder_1000000.0_dx3e-08_reverseTrue | 0.0 | 0.0 | gate:clean_solid, gate:simple_through_holes, gate:is_plate, R4a:hole_count, R4b:hole_diameter, R5:hole_pattern, R6:material, R7:edge_margin, R9:no_other_features |
| V071 | synthetic-v3 | remote_cylinder_-1000000000000.0_dx0_reverseFalse | 0.0 | 0.0 | scorer worker died while executing model code |
| V072 | synthetic-v3 | remote_cylinder_-1000000000000.0_dx0_reverseTrue | 0.0 | 0.0 | scorer worker died while executing model code |
| V073 | synthetic-v3 | remote_cylinder_-1000000000000.0_dx1e-09_reverseFalse | 0.0 | 0.0 | scorer worker died while executing model code |
| V074 | synthetic-v3 | remote_cylinder_-1000000000000.0_dx1e-09_reverseTrue | 0.0 | 0.0 | scorer worker died while executing model code |
| V075 | synthetic-v3 | remote_cylinder_-1000000000000.0_dx3e-08_reverseFalse | 0.0 | 0.0 | scorer worker died while executing model code |
| V076 | synthetic-v3 | remote_cylinder_-1000000000000.0_dx3e-08_reverseTrue | 0.0 | 0.0 | scorer worker died while executing model code |
| V077 | synthetic-v3 | ordinary_bore_tilt_rad1e-09 | 0.0 | 1.0 | none |
| V078 | synthetic-v3 | ordinary_bore_tilt_rad3e-08 | 0.0 | 1.0 | none |
| V079 | synthetic-v3 | ordinary_bore_tilt_rad4e-08 | 0.0 | 0.9 | R9:no_other_features |
| V080 | synthetic-v3 | ordinary_bore_tilt_rad1e-06 | 0.0 | 0.9 | R9:no_other_features |

#### W series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| W001 | synthetic-v3 | far_cut_1000.0_dx0_sign-1 | 1.0 | 1.0 | none |
| W002 | synthetic-v3 | far_cut_1000.0_dx0_sign1 | 1.0 | 1.0 | none |
| W003 | synthetic-v3 | far_cut_1000.0_dx1e-09_sign-1 | 1.0 | 1.0 | none |
| W004 | synthetic-v3 | far_cut_1000.0_dx1e-09_sign1 | 1.0 | 1.0 | none |
| W005 | synthetic-v3 | far_cut_1000.0_dx3e-08_sign-1 | 1.0 | 1.0 | none |
| W006 | synthetic-v3 | far_cut_1000.0_dx3e-08_sign1 | 1.0 | 1.0 | none |
| W007 | synthetic-v3 | far_cut_1000000.0_dx0_sign-1 | 1.0 | 1.0 | none |
| W008 | synthetic-v3 | far_cut_1000000.0_dx0_sign1 | 1.0 | 1.0 | none |
| W009 | synthetic-v3 | far_cut_1000000.0_dx1e-09_sign-1 | 1.0 | 1.0 | none |
| W010 | synthetic-v3 | far_cut_1000000.0_dx1e-09_sign1 | 1.0 | 1.0 | none |
| W011 | synthetic-v3 | far_cut_1000000.0_dx3e-08_sign-1 | 1.0 | 1.0 | none |
| W012 | synthetic-v3 | far_cut_1000000.0_dx3e-08_sign1 | 1.0 | 1.0 | none |
| W013 | synthetic-v3 | far_cut_10000000000.0_dx0_sign-1 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| W014 | synthetic-v3 | far_cut_10000000000.0_dx0_sign1 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| W015 | synthetic-v3 | far_cut_10000000000.0_dx1e-09_sign-1 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| W016 | synthetic-v3 | far_cut_10000000000.0_dx1e-09_sign1 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| W017 | synthetic-v3 | far_cut_10000000000.0_dx3e-08_sign-1 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| W018 | synthetic-v3 | far_cut_10000000000.0_dx3e-08_sign1 | 0.0 | 0.0 | execution failed [raised in cadquery: shapetype]: ValueError: Null TopoDS_Shape object |
| W019 | synthetic-v3 | far_axis_center_shift0.05 | 1.0 | 1.0 | none |
| W020 | synthetic-v3 | far_axis_center_shift0.1000000005 | 1.0 | 1.0 | none |
| W021 | synthetic-v3 | far_axis_center_shift0.100000002 | 0.8 | 0.8 | R5:hole_pattern, R7:edge_margin |
| W022 | synthetic-v3 | far_axis_center_shift0.2 | 0.8 | 0.8 | R5:hole_pattern, R7:edge_margin |

#### G series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| G001 | synthetic-v3 | counterbore_dr4e-07_depth0.0001_tolNone | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| G002 | synthetic-v3 | counterbore_dr4e-07_depth0.0001_tol0.1 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| G003 | synthetic-v3 | counterbore_dr4e-07_depth0.0049_tolNone | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| G004 | synthetic-v3 | counterbore_dr4e-07_depth0.0049_tol0.1 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| G005 | synthetic-v3 | counterbore_dr4e-07_depth0.0099_tolNone | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| G006 | synthetic-v3 | counterbore_dr4e-07_depth0.0099_tol0.1 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| G007 | synthetic-v3 | counterbore_dr4e-07_depth0.02_tolNone | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| G008 | synthetic-v3 | counterbore_dr4e-07_depth0.02_tol0.1 | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| G009 | synthetic-v3 | counterbore_dr9e-07_depth0.0001_tolNone | 0.9 | 0.9 | R9:no_other_features |
| G010 | synthetic-v3 | counterbore_dr9e-07_depth0.0001_tol0.1 | 0.9 | 0.9 | R9:no_other_features |
| G011 | synthetic-v3 | counterbore_dr9e-07_depth0.0049_tolNone | 0.9 | 0.9 | R9:no_other_features |
| G012 | synthetic-v3 | counterbore_dr9e-07_depth0.0049_tol0.1 | 0.9 | 0.9 | R9:no_other_features |
| G013 | synthetic-v3 | counterbore_dr9e-07_depth0.0099_tolNone | 0.9 | 0.9 | R9:no_other_features |
| G014 | synthetic-v3 | counterbore_dr9e-07_depth0.0099_tol0.1 | 0.9 | 0.9 | R9:no_other_features |
| G015 | synthetic-v3 | counterbore_dr9e-07_depth0.02_tolNone | 0.9 | 0.9 | R9:no_other_features |
| G016 | synthetic-v3 | counterbore_dr9e-07_depth0.02_tol0.1 | 0.9 | 0.9 | R9:no_other_features |
| G017 | synthetic-v3 | counterbore_dr0.0001_depth0.0001_tolNone | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| G018 | synthetic-v3 | counterbore_dr0.0001_depth0.0001_tol0.1 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| G019 | synthetic-v3 | counterbore_dr0.0001_depth0.0049_tolNone | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| G020 | synthetic-v3 | counterbore_dr0.0001_depth0.0049_tol0.1 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| G021 | synthetic-v3 | counterbore_dr0.0001_depth0.0099_tolNone | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| G022 | synthetic-v3 | counterbore_dr0.0001_depth0.0099_tol0.1 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| G023 | synthetic-v3 | counterbore_dr0.0001_depth0.02_tolNone | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| G024 | synthetic-v3 | counterbore_dr0.0001_depth0.02_tol0.1 | 0.0 | 0.0 | gate:simple_through_holes, R4a:hole_count, R9:no_other_features |
| G025 | synthetic-v3 | fresh_remote_cylinder_-1000000000000.0_dx0_reverseTrue | 0.0 | 0.0 | scorer worker died while executing model code |
| G026 | synthetic-v3 | fresh_remote_cylinder_-1000000000000.0_dx1e-09_reverseFalse | 0.0 | 0.0 | scorer worker died while executing model code |
| G027 | synthetic-v3 | fresh_remote_cylinder_-1000000000000.0_dx1e-09_reverseTrue | 0.0 | 0.0 | scorer worker died while executing model code |
| G028 | synthetic-v3 | fresh_remote_cylinder_-1000000000000.0_dx3e-08_reverseFalse | 0.0 | 0.0 | scorer worker died while executing model code |
| G029 | synthetic-v3 | fresh_remote_cylinder_-1000000000000.0_dx3e-08_reverseTrue | 0.0 | 0.0 | scorer worker died while executing model code |
| G030 | synthetic-v3 | fresh_ordinary_bore_tilt_rad1e-09 | 1.0 | 1.0 | none |
| G031 | synthetic-v3 | fresh_ordinary_bore_tilt_rad3e-08 | 1.0 | 1.0 | none |
| G032 | synthetic-v3 | fresh_ordinary_bore_tilt_rad4e-08 | 0.9 | 0.9 | R9:no_other_features |
| G033 | synthetic-v3 | fresh_ordinary_bore_tilt_rad1e-06 | 0.9 | 0.9 | R9:no_other_features |

#### Q series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| Q001 | synthetic-v3 | plane_origin_10000.0_reverseTrue_inner_flipFalse | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| Q002 | synthetic-v3 | plane_origin_10000.0_reverseTrue_inner_flipTrue | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: Add(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRepBuilderAPI.BRepBuilderAPI_MakeFace, W: OCP.OCP.TopoDS.TopoDS_Wire) -> None  In |
| Q003 | synthetic-v3 | plane_origin_100000000.0_reverseTrue_inner_flipFalse | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| Q004 | synthetic-v3 | plane_origin_100000000.0_reverseTrue_inner_flipTrue | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: Add(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRepBuilderAPI.BRepBuilderAPI_MakeFace, W: OCP.OCP.TopoDS.TopoDS_Wire) -> None  In |
| Q005 | synthetic-v3 | plane_origin_1000000000000.0_reverseTrue_inner_flipFalse | 0.0 | 0.0 | gate:clean_solid, R9:no_other_features |
| Q006 | synthetic-v3 | plane_origin_1000000000000.0_reverseTrue_inner_flipTrue | 0.0 | 0.0 | execution failed [raised in model code]: TypeError: Add(): incompatible function arguments. The following argument types are supported:     1. (self: OCP.OCP.BRepBuilderAPI.BRepBuilderAPI_MakeFace, W: OCP.OCP.TopoDS.TopoDS_Wire) -> None  In |

#### J series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| J001 | synthetic-v3 | ordinary_mirror_XY | 1.0 | 1.0 | none |
| J002 | synthetic-v3 | ordinary_mirror_XZ | 1.0 | 1.0 | none |
| J003 | synthetic-v3 | ordinary_mirror_YZ | 1.0 | 1.0 | none |
| J004 | synthetic-v3 | typed_plane_origin_10000.0_reverseTrue_inner_flipTrue | 1.0 | 1.0 | none |
| J005 | synthetic-v3 | typed_plane_origin_100000000.0_reverseTrue_inner_flipTrue | 1.0 | 1.0 | none |
| J006 | synthetic-v3 | typed_plane_origin_1000000000000.0_reverseTrue_inner_flipTrue | 1.0 | 1.0 | none |

#### E series

| ID | Specification | Part | Before | Now | Failed checks / build error |
| --- | --- | --- | --- | --- | --- |
| E001 | synthetic-diagonal | diagonal_bore_axis_component2e-08 | 1.0 | 1.0 | none |
| E002 | synthetic-diagonal | diagonal_bore_axis_component3e-08 | 1.0 | 0.9 | R9:no_other_features |
| E003 | synthetic-diagonal | diagonal_bore_axis_component3.3e-08 | 1.0 | 0.9 | R9:no_other_features |
| E004 | synthetic-diagonal | diagonal_bore_axis_component3.4e-08 | 0.9 | 0.9 | R9:no_other_features |
