# L5 M1 round-2 verification audit

Target: `feat/l5-m1-observation` at `b9386f9`

## 1. Recommendation

**CHANGE FIRST.** [OPINION] Do not merge on the basis of this verification run yet.
[FACT] The supplied bundle is incremental and requires prerequisite commit `1fb9a5139fabc884e297fb3538f7a5f6cbcb0acc`, which is not present in this environment.
[FACT] Because that prerequisite and its unchanged repository data are absent, tasks 1, 2, and 5 cannot be independently reproduced, including the 333-item inventory and 3,161-answer replay.
[FACT] The recoverable `b9386f9` source objects do contain the advertised R1-R5 implementations, the 46-case gate, the revised tests, and the revised amendments.
[OPINION] Reissue a self-contained bundle, then rerun this same audit before M2 starts. No product-code regression claim should be accepted from committed result files alone.

## 2. Required changes and R1-R5 disposition

### Required change V1: make the verification input self-contained

**Label: FACT, verification blocker.**

Small reproducer:

```text
$ git clone /mnt/data/cad-spec-l5-m1-observation-v2.bundle /tmp/cad-spec-audit-l5m1-v2
Cloning into '/tmp/cad-spec-audit-l5m1-v2'...
error: Repository lacks these prerequisite commits:
error: 1fb9a5139fabc884e297fb3538f7a5f6cbcb0acc
fatal: remote transport reported error
```

The bundle header confirms the prerequisite:

```text
# v2 git bundle
-1fb9a5139fabc884e297fb3538f7a5f6cbcb0acc Merge pull request #34 from azzbilal/release/v0.5.0
b9386f9fcb13d40bdc7d3be6cfd8642cc2f2c2a9 refs/heads/feat/l5-m1-observation
```

**Map return:** not applicable. The repository cannot be checked out, so the map cannot be executed from the supplied audit input.

[OPINION] For the next audit artifact, create a bundle that contains the prerequisite history, for example from the source repository:

```text
git bundle create cad-spec-l5-m1-observation-v2-full.bundle main feat/l5-m1-observation
```

or otherwise include the exact prerequisite objects needed to clone and check out both the comparison base and `b9386f9` locally.

### R1: strict off-Z refusal

**Disposition: PARTLY RESOLVED.**

[FACT] The current measurement delta introduces `STRICT_AXIS_SLACK = 1e-12` and treats a cylinder as exactly along Z only when both transverse direction components are at most that slack. The current observation map returns `out_of_scope` when `off_axis_bores` or `off_axis_concave` is nonzero.

[FACT] Independent CadQuery/OCP kernel probes of a cylinder gave:

| nominal tilt | measured transverse component | inside `1e-12` check |
|---:|---:|---|
| `1e-13 rad` | `9.999999999999999e-14` | yes |
| `1e-12 rad` | `1e-12` | yes |
| `1e-11 rad` | `1e-11` | no |
| `1e-9 rad` | `1e-9` | no |

[FACT] Ordinary 180 and 360 degree rotations about X or Y, mirrors, and chained 180/360 degree rotations produced transverse components from `0` to about `2.45e-16`, well inside the slack.

[INFERENCE] Given the recovered measurement change, the 1e-11 and 1e-9 cases should reach `out_of_scope` through R1, while 1e-13 and 1e-12 do not trigger the R1 scope refusal. Full map verdicts are not claimed because the repository cannot be executed.

[FACT] The committed 46-case report records `review_holes_tilted_1e-8_rad` and `review_holes_tilted_1e-6_rad` as `out_of_scope`, but that report was not independently regenerated here.

### R2: unrounded cylinder inventory and nested cylinders

**Disposition: PARTLY RESOLVED.**

[FACT] The recovered observation map calls `_nested(m.scope_axes)` before writing any hole variables. `_nested` ignores duplicate faces only when axes are within `EPS_FORM_MM` and diameters within `EPS_DIM_MM`, then refuses when the axis separation is strictly less than the larger cylinder radius.

[FACT] The recovered measurement delta explicitly appends raw `(x, y, 2 * radius)` data to `scope_axes` before scorer rounding/grouping.

[FACT] Applying the exact recovered `_nested` rule to CadQuery B-reps gives this boundary:

| geometry | centre distance | larger radius | `_nested` |
|---|---:|---:|---|
| two equal D10 holes just touching | `10.0` | `5.0` | false |
| two equal D10 holes overlapping | `6.0` | `5.0` | false |
| axis exactly on the other D10 rim | `5.0` | `5.0` | false |
| axis just inside the other D10 rim | `4.999` | `5.0` | true |
| coaxial D10/D14 step | `0.0` | `7.0` | true |
| D10/D14 offset step | `6.9` | `7.0` | true |
| D10/D14 axes exactly one large radius apart | `7.0` | `7.0` | false |

[INFERENCE] The map therefore has an intentional sharp semantic boundary: overlap alone is not nested; axis containment is. This matches section 3's wording, "one with its axis inside the other". It should be pinned explicitly in a boundary test because the existing 46-case suite only tests the non-nested equal-hole overlap at 6 mm separation and offset steps well inside the boundary.

[FACT] A rounded-corner blind pocket placed near, but not cutting into, a D10 through hole produced separate cylindrical axes and did not satisfy `_nested`. A separate round blind pocket also did not satisfy `_nested`. These are kernel/B-rep checks, not full map executions.

[FACT] Duplicate tuples with the same axis and diameter are skipped by `_nested`, which is the intended behavior for one cylindrical surface represented by more than one face. Full through-hole reconstruction for a deliberately split cylindrical face could not be executed without the missing measurement module.

### R3: diameter equality at scorer dimension slack

**Disposition: PARTLY RESOLVED.**

[FACT] `EPS_DIM_MM` is pinned to `TOLERANCES["0.5.0"].eps`, and the current map refuses when:

```python
max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_DIM_MM
```

[FACT] CadQuery/OCP cylinder diameters constructed at the requested nominal differences gave:

| requested difference | measured double difference | `> 1e-9` |
|---:|---:|---|
| `5e-10 mm` | `5.000000413701855e-10` | false |
| `1e-9 mm` | `1.000000082740371e-9` | true |
| `2e-9 mm` | `2.000000165480742e-9` | true |

[INFERENCE] A CAD construction written as `10.0` and `10.000000001` is likely refused by the current comparison even though the decimal source values differ by nominally exactly `1e-9`, because the measured binary-double spread is slightly larger than the tolerance. This is not evidence that the comparison uses the wrong constant. It is a boundary effect of double geometry.

[OPINION] Do not change the code solely from this result if scorer 0.5.0 intentionally applies the same tolerance to measured doubles. Do add an executable boundary case and document the observed result, so the benchmark does not imply a decimal-exact equality guarantee that the B-rep cannot provide.

### R4: bounded inward probe, unclear classification, minimum cylinder size

**Disposition: PARTLY RESOLVED.**

[FACT] The current measurement delta contains `_scope_scan`, limits the inward step with the cylinder radius, raises when a cylindrical face cannot be classified clearly, and records the smallest cylindrical-face diameter.

[FACT] The current observation map refuses before hole extraction when `min_cylinder_diameter < 0.01` mm.

[FACT] CadQuery generated cylindrical faces at all three requested nominal diameters without changing their reported diameter:

| feature | 0.009 mm | 0.010 mm | 0.011 mm |
|---|---|---|---|
| Z hole | cylinder D = 0.009 | D = 0.010 | D = 0.011 |
| cross bore | cylinder D = 0.009 | D = 0.010 | D = 0.011 |
| vertical-edge fillet | four cylinders D = 0.009 | D = 0.010 | D = 0.011 |

[INFERENCE] From control-flow order, a 0.009 mm cylinder of any of those types should be `out_of_scope` for size. At 0.010 and 0.011 mm, the size rule no longer fires; the cross bore should still be `out_of_scope` through off-axis detection, and the fillet should proceed to form checking. Full verdicts are not claimed without executing `_scope_scan` and `form_verdict` from the actual repository.

### R5: strict marker and failed scope scan become a refusal

**Disposition: PARTLY RESOLVED.**

[FACT] `observe()` now raises on a non-strict `Measurements`, checks `scope_error`, `off_axis_concave is None`, and `scope_axes is None`, and returns `out_of_scope` with the recorded reason when scope information is unavailable.

[FACT] The recovered pytest adds a monkeypatched `_scope_scan` failure and asserts that the measurement is strict, the error is recorded, `observe()` returns `out_of_scope`, `obs.ok` is false, and only L/W/T remain in the values map.

[FACT] `Observation.values` is now a `MappingProxyType`, and `Observation.ok` is true only for status `ok`.

[INFERENCE] R5 is implemented as requested. It remains only partly verified here because the actual test cannot run without the prerequisite repository.

### Non-blocking document precision changes

[OPINION] These are not reasons to reject the implementation, but the prose should be tightened when the full rerun is made.

```diff
--- a/docs/design/L5-amendments.md
+++ b/docs/design/L5-amendments.md
@@
-| Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face; the two agree within 1e-11 mm because any tilted hole is refused | one measurement shared with the scorer |
+| Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face. For an accepted axis, the XY difference is bounded by `(T / 2) * tan(STRICT_AXIS_SLACK)`; record the maximum for the generated thickness range | one measurement shared with the scorer |
```

Reason: [FACT] the recovered design note does not state a global maximum plate thickness, so an unconditional `1e-11 mm` bound is stronger than the evidence visible in this bundle.

[OPINION] Also add explicit gate cases around the nested boundary, the `0.01 mm` size boundary, and the `EPS_DIM_MM` boundary. The current suite contains representative R1-R4 regressions, but not these exact boundaries.

## 3. Required tables for tasks 1, 2, and 5

### Task 1: reproduction

| Command | Expected | Independent result in this audit | Evidence/status |
|---|---:|---:|---|
| `python scripts/test_l5_observation.py` | 46/46 | **not runnable** | [FACT] script and committed result were recovered; committed result says 46/46, but checkout is impossible from the incremental bundle |
| `pytest -q tests/test_l5_observation.py` | pass | **not runnable** | [FACT] current test blob was recovered and includes scorer pinning, R5, immutability, and `ok` checks |
| `python scripts/test_rubric_050.py` | 81/81 | **not runnable** | [FACT] unchanged script is in the missing prerequisite tree |
| `python scripts/test_rubric.py` | 37/37 | **not runnable** | [FACT] unchanged script is in the missing prerequisite tree |

[FACT] The committed M1 result file contains 46 rows and states `46 of 46 cases as expected` with dimension slack `1e-09 mm` and form tolerance `1e-07 mm`. That is repository evidence, not an independent reproduction.

### Task 2: 333-part/fixture regression and 180 controls

| Requested check | Result |
|---|---|
| every `ok` part with a wrong value | **not verified** |
| every wrong verdict | **not verified** |
| every correct ordinary part refused | **not verified** |
| 180 construction controls within `1e-9 mm` | **not verified** |

[FACT] The 333-part inventory, the 180 controls, their helper code/data, and the base package needed to execute them are unchanged objects beneath the missing prerequisite and are not contained in the supplied bundle.

[FACT] Section 3.1 of the amendments records the previous audit as having checked 180 ordinary constructions and 153 additional parts/fixtures, for 333 total, but round-2 verification cannot substitute that historical statement for a rerun.

### Task 5: no score change over 3,161 saved answers

| Comparison | Required fields | Round-2 mismatches | Time/answer |
|---|---|---:|---:|
| branch vs `main`, scorer `0.5.0`, 3,161 answers | reward, named checks, parsed flag | **not verified** | **not measured** |
| branch vs `main`, scorer `0.4.0`, 3,161 answers | reward, named checks, parsed flag | **not verified** | **not measured** |

[FACT] The current commit message claims no score changes on its local checks, and section 3.1 records the first external audit as 0 score changes over 3,161 saved answers under both scorer versions. Neither claim was replayed here because the saved-answer corpus and comparison base are absent.

## 4. New task-4 boundary parts and results

The table distinguishes actual kernel/B-rep measurements from full map verdicts. No full-map verdict is promoted to fact unless it came from an independently executable repository, which is unavailable here.

### R1 axis boundaries and ordinary transformations

| Case | Kernel result | Source-level consequence | Label |
|---|---|---|---|
| tilt `1e-13 rad` | transverse axis `~1e-13` | does not trigger `STRICT_AXIS_SLACK` | FACT + INFERENCE |
| tilt `1e-12 rad` | transverse axis `1e-12` | equality is accepted by `<=` | FACT + INFERENCE |
| tilt `1e-11 rad` | transverse axis `1e-11` | R1 should refuse | FACT + INFERENCE |
| tilt `1e-9 rad` | transverse axis `1e-9` | R1 should refuse | FACT + INFERENCE |
| rotate 180 deg X | `|dy| ~ 1.22e-16` | no R1 refusal | FACT + INFERENCE |
| rotate 360 deg X | `|dy| ~ 2.45e-16` | no R1 refusal | FACT + INFERENCE |
| rotate 180 deg Y | `|dx| ~ 1.22e-16` | no R1 refusal | FACT + INFERENCE |
| rotate 360 deg Y | `|dx| ~ 2.45e-16` | no R1 refusal | FACT + INFERENCE |
| X180 then Y180 | transverse components `~1.22e-16` | no R1 refusal | FACT + INFERENCE |
| X360 then Y360 | transverse components `~2.45e-16` | no R1 refusal | FACT + INFERENCE |
| mirrors XY/XZ/YZ | transverse components zero or signed zero | no R1 refusal | FACT + INFERENCE |

[INFERENCE] No ordinary 180/360-degree construction tested here comes close to the 1e-12 cutoff. This substantially reduces the false-refusal risk that motivated the boundary test.

### R2 nested, overlapping, pocket, and split-face boundaries

| Case | B-rep / `_nested` result | Expected observation path from recovered code |
|---|---|---|
| equal D10 holes, centres 10 mm apart, tangent | `_nested = false` | not refused as nested |
| equal D10 holes, centres 6 mm apart, overlap | `_nested = false` | form/contract path, not nested refusal |
| equal D10 holes, centres 5 mm apart | `_nested = false` | boundary is not inside because comparison is strict `<` |
| equal D10 holes, centres 4.999 mm apart | `_nested = true` | `out_of_scope` as one axis is inside the other cylinder |
| coaxial D10/D14 step | `_nested = true` | `out_of_scope` |
| D10/D14 offset 6.9 mm | `_nested = true` | `out_of_scope` |
| D10/D14 offset 7.0 mm | `_nested = false` | not refused by nested rule |
| rounded-corner blind pocket separated from hole | `_nested = false` | should continue to form checking |
| round blind pocket separated from holes | `_nested = false` | should continue to form checking |
| duplicate same-axis, same-D cylinder entries | skipped as duplicates by source | intended to tolerate a cylinder represented by several faces |

[FACT] The current gate already records a mild equal-D overlap at 6 mm separation as `form_violation`, a 1.1-micron offset step as `out_of_scope`, and a 0.4-micron second cut as `out_of_scope`. Those are committed outputs, not rerun outputs.

[OPINION] Add at least the 5.0 and 4.999 mm equal-hole cases to the permanent gate. They define the exact semantic boundary introduced by `_nested` and make future refactors auditable.

### R4 size boundary

| Geometry | 0.009 mm | 0.010 mm | 0.011 mm |
|---|---|---|---|
| Z hole | B-rep cylinder is exactly the requested size; source size test should refuse | size test does not refuse | size test does not refuse |
| cross bore | source size test should refuse first | size test passes, off-axis rule should refuse | size test passes, off-axis rule should refuse |
| cylindrical fillet | source size test should refuse first | size test passes, form check should decide | size test passes, form check should decide |

[FACT] The source condition is `< 0.01`, not `<= 0.01`, so exactly 0.010 mm is on the supported side of the size rule.

[OPINION] The documentation should make clear that a sub-0.01 mm cylindrical fillet is an `out_of_scope` size refusal before it can become the ordinary `form_violation` used for larger fillets. Section 3 already implies this; kickoff amendment 1 is broader and can otherwise be read as saying all fillets reach the form verdict.

### R3 diameter-difference boundary

| Nominal constructed difference | B-rep measured spread | Source comparison result |
|---:|---:|---|
| `5e-10 mm` | `5.000000413701855e-10` | not greater than `1e-9` |
| `1e-9 mm` | `1.000000082740371e-9` | greater than `1e-9` |
| `2e-9 mm` | `2.000000165480742e-9` | greater than `1e-9` |

[OPINION] Pin these three cases in an executable test. The middle case is especially important because the text "more than 1e-9" and the actual measured-double boundary are not identical for a decimal construction.

## 5. Documents and what could not be verified

### Sections 3, 3.1, and 4 against recoverable code

| Statement | Assessment | Label |
|---|---|---|
| observation version 1 pinned to scorer `0.5.0` by name | matches `OBSERVATION_VERSION = "1"` and `SCORER_BASIS = "0.5.0"` | FACT |
| gate has 46 cases | current script contains 46 cases; committed result contains 46 rows | FACT |
| only `ok` lets a contract be evaluated | matches `Observation.ok` | FACT |
| strict measurement carries `scope_axes`, `min_cylinder_diameter`, `off_axis_concave` | present in recovered current measurement delta | FACT |
| holes of different diameters use 1e-9 dimension slack | matches recovered observation code | FACT |
| sub-0.01 mm cylindrical face is refused | matches recovered observation code | FACT |
| failed scope scan is `out_of_scope` with reason | matches observation code and recovered pytest | FACT |
| "top face" and mid-plane centre agree within `1e-11 mm` | stronger than evidence visible in the bundle unless the allowed thickness range is bounded accordingly | INFERENCE |
| previous audit reproduced 27/27, 3,161 no-score-change replay, 180 controls | historical statement only; cannot be independently verified from this incremental bundle | FACT about verification status |
| F1/F2 are deferred to M3 | matches observation module comments and section 4 | FACT |
| `None` in predicates deferred to M3 | no M3 code is present in recoverable M1 objects | FACT |
| compiled items pin observation/scorer basis in M2 | no M2 code exists yet | FACT |

### Could not verify

1. [FACT] The four requested task-1 commands could not be run against the actual repository because the bundle omits prerequisite `1fb9a513` and unchanged source objects.
2. [FACT] The 333-part/fixture inventory could not be reconstructed or rerun.
3. [FACT] The 180 construction controls could not be rerun through the actual observation map.
4. [FACT] The 3,161 saved answers and the `main` comparison tree are absent, so reward/check/parsed equality and 0.5.0 timing could not be measured.
5. [FACT] The exact current `measure.py` and `rubric.py` files cannot be reconstructed in full from the thin pack because they are stored as deltas against objects in the missing prerequisite. Their newly inserted round-2 sections are visible and were inspected, but that is not equivalent to executing the files.
6. [FACT] New boundary geometry was built with the installed CadQuery/OCP kernel and evaluated against recoverable pure rules such as `_nested` and the explicit thresholds. Those experiments are useful boundary evidence but are not substitutes for end-to-end `observe_code()` results.
7. [FACT] No network, credentials, paid service, or external system was used. The repository source was not modified. Audit scripts and notes were written only under `~/cad-spec-audit-out/l5-m1/v2/`.

## Bottom line

[OPINION] The round-2 implementation looks directionally correct and the five requested fixes are visible in source, but the evidence supplied to this verifier is insufficient for the requested merge-grade regression claim. The next action is not M2. The next action is to provide a self-contained local bundle and rerun this audit unchanged. If that rerun produces the advertised 46/46, 81/81, 37/37, zero 333-inventory regressions, 180 controls within 1e-9 mm, and zero 3,161-answer score diffs for both scorer versions, I would expect the remaining review to concentrate only on the new boundary cases documented above.
