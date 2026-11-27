# Codex review of commit 4e26d30

- Command: `codex review --commit 4e26d30 -c 'sandbox_mode="read-only"' -c 'approval_policy="never"'`
- codex-cli 0.169.0, model gpt-6.1-sol, reasoning effort high, sandbox read-only, approval never
- Target: commit 4e26d30 (C1 fix: tilt limit on the angle), reviewed against its parent
- Started 2026-11-26T23:08:39Z, exit 0, 132 s wall time
- Run from branch fix/l5-m1-audit at ddd4e14 (the reviewed source is unchanged since 4e26d30; Codex checked this itself, see the last exec block)
- Codex was not restricted from reading earlier audits; the commit's own diff contains audit/l5-m1-v2-audit.md

## Verdict (Codex, verbatim)

> The change correctly applies the tilt limit to the combined transverse direction rather than each component independently. No actionable regressions were found; verification passed all 60 observation cases, 10 focused pytest tests, and both scorer suites (81 and 37 cases).

Findings: none.

## Full output (stdout and stderr, unedited)

````text
2026-11-26T23:08:45.631389Z ERROR codex_models_manager::manager: failed to refresh available models: request timed out
2026-11-26T23:08:45.714185Z ERROR codex_models_manager::manager: failed to refresh available models: request timed out
OpenAI Codex v0.169.0
--------
workdir: D:\10_PROJECTS\cad-engineering\cad-spec-env
model: gpt-6.1-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a21a1e-4377-7fb3-9713-7be563075f8d
--------
user
commit 4e26d30
2026-11-26T23:08:51.004994Z ERROR codex_models_manager::manager: failed to refresh available models: request timed out
2026-11-26T23:08:59.519289Z ERROR codex_models_manager::manager: failed to refresh available models: request timed out
exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-Content C:\\Users\\bgare\\.codex\\skills\\behavioral-verification-review\\SKILL.md; git status --short; git show --stat --oneline 4e26d30" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 238ms:
---
name: behavioral-verification-review
description: Verify a software change against intended behavior, assess test quality, diagnose failures, and review a concrete diff using project standards. Use for feature verification, regression fixes, CI diagnosis, or agent-written code review; preserve read-only scope when review alone is requested.
---

# Behavioral Verification and Review

Produce evidence that the intended change works and a reviewable account of its remaining risks. Read [source notes](references/source-notes.md) for the source lessons and adaptations.

## Establish the independent acceptance signal

Start from the request, requirement record, bug reproduction, or existing contract. Define what should happen for the central scenario and relevant failures. Do not derive correctness solely from the new implementation.

Locate the project's existing checks and current test boundaries. Separate structural checks, behavior checks, integration/runtime checks, and product judgments. Choose those needed for the change; avoid adding every test category by default.

For a bug, reproduce the observed failure where feasible. For meaningful test-first work, use one failing behavioral check, implement the behavior, then refactor under that check. Confirm why the test is red: a setup error alone does not prove it captures the reported bug.

## Examine whether checks can expose errors

Favor public interfaces and observable outcomes over private implementation structure. Question a test that reads source text instead of exercising a UI, checks that a constant equals its own assigned value, or mocks away the dependency behavior responsible for the failure.

For a proposed test, identify a plausible wrong behavior that would cause it to fail. A focused counterexample or temporary fault experiment can clarify this when warranted; mutation testing is an optional diagnostic, not a mandatory toolchain addition. Verify relevant integration boundaries with real or sufficiently faithful fixtures.

Passing tests provide evidence only within their coverage. Validate required runtime configuration, migrations, and affected user paths when relevant: a service test can pass while the running app lacks a table or calls the wrong endpoint. Assess visual behavior using suitable rendered evidence when that is part of the requirement.

## Use a distinct review pass

Review the concrete diff with the intended behavior, adjacent code, interfaces, and applicable repository standards. Keep required project instructions in force. Long catalogs of optional standards may be loaded at review time to keep implementation context focused; this never permits ignoring required constraints during implementation.

Look for behavioral errors, integration gaps, untested assumptions, and maintainability problems that materially affect the change. Identify evidence for each actionable finding: location, triggering condition, impact, and violated contract or standard. Label uncertainty and avoid speculative findings that manufacture reviewer work.

For a read-only review, return findings without modifying files. When repair is part of the authorized task, fix substantiated issues directly, rerun affected checks, and report the changes. A talk's preference for reviewer commits does not authorize commits or publishing in every task. Do not suppress checks, replace meaningful tests with weaker ones, or claim unrun checks passed.

## Diagnose and repair failures

Determine whether each failure is caused by the change, pre-existing, environmental, or still uncertain. Use a specific hypothesis and a bounded experiment. Rerun the failing check after the fix, then broaden only as the impact or uncertainty warrants.

When repeated attempts produce the same failure without new evidence, change the diagnosis or isolate the dependency. Stop an approach that consumes effort without learning; preserve useful work and identify the exact blocker. Do not redesign unrelated architecture to escape an external service outage.

## Make human review easier

Explain the trigger and before/after behavior, why the approach fits the project, what was checked, and any meaningful limitations. For cross-layer or complex changes, add a small flow diagram, pseudocode, or interface sketch when it helps a reviewer understand the consequence faster.

Assess reversibility and impact when relevant. Reverting code does not undo sent messages, external side effects, or lost data. Call attention to these actual consequences without adding hypothetical risk checklists to routine changes. Apply the user's existing merge and release policy; a low-impact classification is not permission to merge or deploy.

Separate correctness from comprehension: a clear explainer can support human understanding but does not replace checks. If the user needs to learn how the change works, use a focused explanation rather than extending the review with a generic tutorial.

Finish with passed/failed/unrun checks, substantiated findings or repaired issues, and remaining uncertainties. If review exposes a recurring process failure, provide its evidence for a later workflow improvement within the user's scope.
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
?? .workshop/LOG.md
?? .workshop/reviews/
?? audit/scratch/run1-breps/
?? audit/scratch/run1-perturbations/
?? orca.yaml
?? results/baselines.md
?? results/superseded/
4e26d30 fix(l5): tilt limit on the angle, not on its components; narrow three statements
 CHANGELOG.md                              |   6 +-
 audit/README.md                           |   1 +
 audit/l5-m1-v2-audit.md                   | 291 ++++++++++++++++++++++++++++++
 docs/design/L5-amendments.md              |  32 +++-
 environments/cad_spec/cad_spec/measure.py |   6 +-
 results/l5/m1-observation-suite.md        |   4 +-
 scripts/test_l5_observation.py            |  15 ++
 7 files changed, 341 insertions(+), 14 deletions(-)

2026-11-26T23:09:07.566579Z ERROR codex_models_manager::manager: failed to refresh available models: request timed out
exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-ChildItem -Force -Name; Get-ChildItem -Path .. -Filter AGENTS* -Force; git ls-files '*AGENTS*' '*agent*md'; git show 4e26d30 --; Get-Content C:\\Users\\bgare\\.codex\\skills\\behavioral-verification-review\\references\\source-notes.md" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 200ms:
scripts
results
research
prompts
environments
docs
configs
audit
.vibe-wise
.opencode
.github
.git
.claude
.venv
.ruff_cache
.workshop
.dockerignore
.gitattributes
Dockerfile
LICENSE
README.md
ROADMAP.md
SECURITY.md
out.txt
ruff.toml
orca.yaml
.gitignore
CHANGELOG.md
CLAUDE.md
commit 4e26d305d751d5528023e3dabc63880f182f3dc8
Author: azzbilal <azzbilal28@gmail.com>
Date:   Tue Oct 6 23:38:30 2026 +0000

    fix(l5): tilt limit on the angle, not on its components; narrow three statements
    
    Local verification of M1 (audit/l5-m1-v3-audit.md, 7 October 2026): gate and
    suites pass, 333 earlier parts show no wrong value in an ok result, 180
    controls agree to 1e-9 mm, 3,161 saved answers score the same under both
    scorer versions. R2 to R5 resolved. One defect left, fixed here.
    
    - C1: _scope_scan compared the X and Y direction components with the slack
      separately, so a diagonal tilt of 1.3e-12 rad was accepted. The limit is now
      on the angle (hypot of the components against sin(1e-12)). Both sides are
      pinned in the gate (60 cases). The reviewer validated this exact change on
      27 parts: only the three diagonal tilts over the limit changed verdict.
    - C2, documents only: what n counts is stated as the detector's rule (99% of
      the wall, F1 and F2 left to the contract); the 1e-11 mm figure is an example
      at one scale; pockets are form violations unless a cylinder scope rule
      applies first, and the map does not claim to recognise features.
    - audit/l5-m1-v2-audit.md added (the source-only review).
    
    No scoring change: the scan feeds the observation map only. 81 and 37
    hand-labelled scorer cases and the package tests pass.

diff --git a/CHANGELOG.md b/CHANGELOG.md
index ef34670..92682af 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -29,8 +29,10 @@ Scores are only comparable within one scorer version
   changes, all made. A hole tilted by 1e-8 rad was `ok` with a margin wrong
   by 2e-8 mm; a 1e-6 mm radius step and a 1e-8 mm diameter difference were
   not refused; a 0.2 micron cross bore was missed; a failed scope scan
-  raised instead of refusing.
-- **Gate:** `scripts/test_l5_observation.py`, 58 hand-built cases, in CI
+  raised instead of refusing. A final local verification
+  (`audit/l5-m1-v3-audit.md`) found one more: the tilt limit was applied to
+  the X and Y components separately. It is now on the angle.
+- **Gate:** `scripts/test_l5_observation.py`, 60 hand-built cases, in CI
   (`results/l5/m1-observation-suite.md`). Every `ok` case states every
   variable, and the exact boundary of each rule is pinned (tilt, nested
   cylinders, supported size, equal diameters).
diff --git a/audit/README.md b/audit/README.md
index b3b28f8..ac5dfc0 100644
--- a/audit/README.md
+++ b/audit/README.md
@@ -21,6 +21,7 @@ this folder is applied to the environment, the scripts or the configs.
 | `scorer-0.5-v4-audit.md` | Verification of the final scorer 0.5.0 branch: all 473 earlier parts rerun, 180 correct-plate controls (18 ordinary construction styles and 12 tolerance variants on 6 train or dev specs), worker crash and recovery, timing before and after, 3,161-answer legacy comparison, the frozen suite | Report, 5 October 2026. No wrong part at full credit, no correct non-spline part rejected. Recommendation: merge. Its three wording corrections are applied |
 | `l5-m1-audit.md` | External review of L5 milestone M1, the observation map: the gate reproduced, 3,161 saved answers compared under both scorer versions (no score change), 180 ordinary constructions on six specs checked to 1e-9 mm, 153 further parts and fixtures | Report, 5 October 2026. Five required changes (tiny tilts, micro-steps, diameter equality, small cross bores, failed scope scan), all made in the same branch and pinned as `review_` cases |
 | `l5-m1-v2-audit.md` | Second review of L5 milestone M1, from source and kernel probes only: the environment held the incremental bundle without the repository, so no repository command could run | Report, 6 October 2026. All five fixes confirmed in the source; no defect found; boundary cases and two wording corrections requested and made. Not an execution-based verification |
+| `l5-m1-v3-audit.md` | Local verification of L5 milestone M1 after its fixes: gate 58 of 58 and the three other suites, 333 earlier parts rerun (no wrong value in an `ok` result), 180 controls to 1e-9 mm, 130 new boundary parts, 3,161 saved answers under both scorer versions (no score change) | Report, 7 October 2026. R2 to R5 resolved. One remaining defect (tilt limit applied per component, a diagonal 1.3e-12 rad tilt accepted) fixed and pinned; three document statements narrowed |
 | `a7-addendum.md` | Addendum to the external audit: full reading of 28 adapter answers of the replication (24 drawn by seed, 4 special cases) and 6 base answers. No exploitation found in the sample; describes what the adapter does and why two L3 answers were truncated | Report, 3 October 2026. Reflected in the corrections of `docs/experiments/replication-1.md` |
 | `replication1_geometry_check.py` | Second-implementation geometry check of the replication and original evaluation answers: comparison with the independently built ideal part, plus a sparse point test (the scorer is not imported). Output: `results/training/replication1/independent-geometry.json` | Post hoc check by the project (not an external audit), 3 October 2026; rebuilt after the external audit |
 | `guardrails-proposed.patch` | Spend guard, preflight check and related changes | **PROPOSED, NOT APPLIED.** To be reviewed, tested and registered before any future paid run; nothing under `scripts/` or `configs/` uses it |
diff --git a/audit/l5-m1-v2-audit.md b/audit/l5-m1-v2-audit.md
new file mode 100644
index 0000000..c458812
--- /dev/null
+++ b/audit/l5-m1-v2-audit.md
@@ -0,0 +1,291 @@
+# L5 M1 round-2 verification audit
+
+Target: `feat/l5-m1-observation` at `b9386f9`
+
+## 1. Recommendation
+
+**CHANGE FIRST.** [OPINION] Do not merge on the basis of this verification run yet.
+[FACT] The supplied bundle is incremental and requires prerequisite commit `1fb9a5139fabc884e297fb3538f7a5f6cbcb0acc`, which is not present in this environment.
+[FACT] Because that prerequisite and its unchanged repository data are absent, tasks 1, 2, and 5 cannot be independently reproduced, including the 333-item inventory and 3,161-answer replay.
+[FACT] The recoverable `b9386f9` source objects do contain the advertised R1-R5 implementations, the 46-case gate, the revised tests, and the revised amendments.
+[OPINION] Reissue a self-contained bundle, then rerun this same audit before M2 starts. No product-code regression claim should be accepted from committed result files alone.
+
+## 2. Required changes and R1-R5 disposition
+
+### Required change V1: make the verification input self-contained
+
+**Label: FACT, verification blocker.**
+
+Small reproducer:
+
+```text
+$ git clone /mnt/data/cad-spec-l5-m1-observation-v2.bundle /tmp/cad-spec-audit-l5m1-v2
+Cloning into '/tmp/cad-spec-audit-l5m1-v2'...
+error: Repository lacks these prerequisite commits:
+error: 1fb9a5139fabc884e297fb3538f7a5f6cbcb0acc
+fatal: remote transport reported error
+```
+
+The bundle header confirms the prerequisite:
+
+```text
+# v2 git bundle
+-1fb9a5139fabc884e297fb3538f7a5f6cbcb0acc Merge pull request #34 from azzbilal/release/v0.5.0
+b9386f9fcb13d40bdc7d3be6cfd8642cc2f2c2a9 refs/heads/feat/l5-m1-observation
+```
+
+**Map return:** not applicable. The repository cannot be checked out, so the map cannot be executed from the supplied audit input.
+
+[OPINION] For the next audit artifact, create a bundle that contains the prerequisite history, for example from the source repository:
+
+```text
+git bundle create cad-spec-l5-m1-observation-v2-full.bundle main feat/l5-m1-observation
+```
+
+or otherwise include the exact prerequisite objects needed to clone and check out both the comparison base and `b9386f9` locally.
+
+### R1: strict off-Z refusal
+
+**Disposition: PARTLY RESOLVED.**
+
+[FACT] The current measurement delta introduces `STRICT_AXIS_SLACK = 1e-12` and treats a cylinder as exactly along Z only when both transverse direction components are at most that slack. The current observation map returns `out_of_scope` when `off_axis_bores` or `off_axis_concave` is nonzero.
+
+[FACT] Independent CadQuery/OCP kernel probes of a cylinder gave:
+
+| nominal tilt | measured transverse component | inside `1e-12` check |
+|---:|---:|---|
+| `1e-13 rad` | `9.999999999999999e-14` | yes |
+| `1e-12 rad` | `1e-12` | yes |
+| `1e-11 rad` | `1e-11` | no |
+| `1e-9 rad` | `1e-9` | no |
+
+[FACT] Ordinary 180 and 360 degree rotations about X or Y, mirrors, and chained 180/360 degree rotations produced transverse components from `0` to about `2.45e-16`, well inside the slack.
+
+[INFERENCE] Given the recovered measurement change, the 1e-11 and 1e-9 cases should reach `out_of_scope` through R1, while 1e-13 and 1e-12 do not trigger the R1 scope refusal. Full map verdicts are not claimed because the repository cannot be executed.
+
+[FACT] The committed 46-case report records `review_holes_tilted_1e-8_rad` and `review_holes_tilted_1e-6_rad` as `out_of_scope`, but that report was not independently regenerated here.
+
+### R2: unrounded cylinder inventory and nested cylinders
+
+**Disposition: PARTLY RESOLVED.**
+
+[FACT] The recovered observation map calls `_nested(m.scope_axes)` before writing any hole variables. `_nested` ignores duplicate faces only when axes are within `EPS_FORM_MM` and diameters within `EPS_DIM_MM`, then refuses when the axis separation is strictly less than the larger cylinder radius.
+
+[FACT] The recovered measurement delta explicitly appends raw `(x, y, 2 * radius)` data to `scope_axes` before scorer rounding/grouping.
+
+[FACT] Applying the exact recovered `_nested` rule to CadQuery B-reps gives this boundary:
+
+| geometry | centre distance | larger radius | `_nested` |
+|---|---:|---:|---|
+| two equal D10 holes just touching | `10.0` | `5.0` | false |
+| two equal D10 holes overlapping | `6.0` | `5.0` | false |
+| axis exactly on the other D10 rim | `5.0` | `5.0` | false |
+| axis just inside the other D10 rim | `4.999` | `5.0` | true |
+| coaxial D10/D14 step | `0.0` | `7.0` | true |
+| D10/D14 offset step | `6.9` | `7.0` | true |
+| D10/D14 axes exactly one large radius apart | `7.0` | `7.0` | false |
+
+[INFERENCE] The map therefore has an intentional sharp semantic boundary: overlap alone is not nested; axis containment is. This matches section 3's wording, "one with its axis inside the other". It should be pinned explicitly in a boundary test because the existing 46-case suite only tests the non-nested equal-hole overlap at 6 mm separation and offset steps well inside the boundary.
+
+[FACT] A rounded-corner blind pocket placed near, but not cutting into, a D10 through hole produced separate cylindrical axes and did not satisfy `_nested`. A separate round blind pocket also did not satisfy `_nested`. These are kernel/B-rep checks, not full map executions.
+
+[FACT] Duplicate tuples with the same axis and diameter are skipped by `_nested`, which is the intended behavior for one cylindrical surface represented by more than one face. Full through-hole reconstruction for a deliberately split cylindrical face could not be executed without the missing measurement module.
+
+### R3: diameter equality at scorer dimension slack
+
+**Disposition: PARTLY RESOLVED.**
+
+[FACT] `EPS_DIM_MM` is pinned to `TOLERANCES["0.5.0"].eps`, and the current map refuses when:
+
+```python
+max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_DIM_MM
+```
+
+[FACT] CadQuery/OCP cylinder diameters constructed at the requested nominal differences gave:
+
+| requested difference | measured double difference | `> 1e-9` |
+|---:|---:|---|
+| `5e-10 mm` | `5.000000413701855e-10` | false |
+| `1e-9 mm` | `1.000000082740371e-9` | true |
+| `2e-9 mm` | `2.000000165480742e-9` | true |
+
+[INFERENCE] A CAD construction written as `10.0` and `10.000000001` is likely refused by the current comparison even though the decimal source values differ by nominally exactly `1e-9`, because the measured binary-double spread is slightly larger than the tolerance. This is not evidence that the comparison uses the wrong constant. It is a boundary effect of double geometry.
+
+[OPINION] Do not change the code solely from this result if scorer 0.5.0 intentionally applies the same tolerance to measured doubles. Do add an executable boundary case and document the observed result, so the benchmark does not imply a decimal-exact equality guarantee that the B-rep cannot provide.
+
+### R4: bounded inward probe, unclear classification, minimum cylinder size
+
+**Disposition: PARTLY RESOLVED.**
+
+[FACT] The current measurement delta contains `_scope_scan`, limits the inward step with the cylinder radius, raises when a cylindrical face cannot be classified clearly, and records the smallest cylindrical-face diameter.
+
+[FACT] The current observation map refuses before hole extraction when `min_cylinder_diameter < 0.01` mm.
+
+[FACT] CadQuery generated cylindrical faces at all three requested nominal diameters without changing their reported diameter:
+
+| feature | 0.009 mm | 0.010 mm | 0.011 mm |
+|---|---|---|---|
+| Z hole | cylinder D = 0.009 | D = 0.010 | D = 0.011 |
+| cross bore | cylinder D = 0.009 | D = 0.010 | D = 0.011 |
+| vertical-edge fillet | four cylinders D = 0.009 | D = 0.010 | D = 0.011 |
+
+[INFERENCE] From control-flow order, a 0.009 mm cylinder of any of those types should be `out_of_scope` for size. At 0.010 and 0.011 mm, the size rule no longer fires; the cross bore should still be `out_of_scope` through off-axis detection, and the fillet should proceed to form checking. Full verdicts are not claimed without executing `_scope_scan` and `form_verdict` from the actual repository.
+
+### R5: strict marker and failed scope scan become a refusal
+
+**Disposition: PARTLY RESOLVED.**
+
+[FACT] `observe()` now raises on a non-strict `Measurements`, checks `scope_error`, `off_axis_concave is None`, and `scope_axes is None`, and returns `out_of_scope` with the recorded reason when scope information is unavailable.
+
+[FACT] The recovered pytest adds a monkeypatched `_scope_scan` failure and asserts that the measurement is strict, the error is recorded, `observe()` returns `out_of_scope`, `obs.ok` is false, and only L/W/T remain in the values map.
+
+[FACT] `Observation.values` is now a `MappingProxyType`, and `Observation.ok` is true only for status `ok`.
+
+[INFERENCE] R5 is implemented as requested. It remains only partly verified here because the actual test cannot run without the prerequisite repository.
+
+### Non-blocking document precision changes
+
+[OPINION] These are not reasons to reject the implementation, but the prose should be tightened when the full rerun is made.
+
+```diff
+--- a/docs/design/L5-amendments.md
++++ b/docs/design/L5-amendments.md
+@@
+-| Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face; the two agree within 1e-11 mm because any tilted hole is refused | one measurement shared with the scorer |
++| Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face. For an accepted axis, the XY difference is bounded by `(T / 2) * tan(STRICT_AXIS_SLACK)`; record the maximum for the generated thickness range | one measurement shared with the scorer |
+```
+
+Reason: [FACT] the recovered design note does not state a global maximum plate thickness, so an unconditional `1e-11 mm` bound is stronger than the evidence visible in this bundle.
+
+[OPINION] Also add explicit gate cases around the nested boundary, the `0.01 mm` size boundary, and the `EPS_DIM_MM` boundary. The current suite contains representative R1-R4 regressions, but not these exact boundaries.
+
+## 3. Required tables for tasks 1, 2, and 5
+
+### Task 1: reproduction
+
+| Command | Expected | Independent result in this audit | Evidence/status |
+|---|---:|---:|---|
+| `python scripts/test_l5_observation.py` | 46/46 | **not runnable** | [FACT] script and committed result were recovered; committed result says 46/46, but checkout is impossible from the incremental bundle |
+| `pytest -q tests/test_l5_observation.py` | pass | **not runnable** | [FACT] current test blob was recovered and includes scorer pinning, R5, immutability, and `ok` checks |
+| `python scripts/test_rubric_050.py` | 81/81 | **not runnable** | [FACT] unchanged script is in the missing prerequisite tree |
+| `python scripts/test_rubric.py` | 37/37 | **not runnable** | [FACT] unchanged script is in the missing prerequisite tree |
+
+[FACT] The committed M1 result file contains 46 rows and states `46 of 46 cases as expected` with dimension slack `1e-09 mm` and form tolerance `1e-07 mm`. That is repository evidence, not an independent reproduction.
+
+### Task 2: 333-part/fixture regression and 180 controls
+
+| Requested check | Result |
+|---|---|
+| every `ok` part with a wrong value | **not verified** |
+| every wrong verdict | **not verified** |
+| every correct ordinary part refused | **not verified** |
+| 180 construction controls within `1e-9 mm` | **not verified** |
+
+[FACT] The 333-part inventory, the 180 controls, their helper code/data, and the base package needed to execute them are unchanged objects beneath the missing prerequisite and are not contained in the supplied bundle.
+
+[FACT] Section 3.1 of the amendments records the previous audit as having checked 180 ordinary constructions and 153 additional parts/fixtures, for 333 total, but round-2 verification cannot substitute that historical statement for a rerun.
+
+### Task 5: no score change over 3,161 saved answers
+
+| Comparison | Required fields | Round-2 mismatches | Time/answer |
+|---|---|---:|---:|
+| branch vs `main`, scorer `0.5.0`, 3,161 answers | reward, named checks, parsed flag | **not verified** | **not measured** |
+| branch vs `main`, scorer `0.4.0`, 3,161 answers | reward, named checks, parsed flag | **not verified** | **not measured** |
+
+[FACT] The current commit message claims no score changes on its local checks, and section 3.1 records the first external audit as 0 score changes over 3,161 saved answers under both scorer versions. Neither claim was replayed here because the saved-answer corpus and comparison base are absent.
+
+## 4. New task-4 boundary parts and results
+
+The table distinguishes actual kernel/B-rep measurements from full map verdicts. No full-map verdict is promoted to fact unless it came from an independently executable repository, which is unavailable here.
+
+### R1 axis boundaries and ordinary transformations
+
+| Case | Kernel result | Source-level consequence | Label |
+|---|---|---|---|
+| tilt `1e-13 rad` | transverse axis `~1e-13` | does not trigger `STRICT_AXIS_SLACK` | FACT + INFERENCE |
+| tilt `1e-12 rad` | transverse axis `1e-12` | equality is accepted by `<=` | FACT + INFERENCE |
+| tilt `1e-11 rad` | transverse axis `1e-11` | R1 should refuse | FACT + INFERENCE |
+| tilt `1e-9 rad` | transverse axis `1e-9` | R1 should refuse | FACT + INFERENCE |
+| rotate 180 deg X | `|dy| ~ 1.22e-16` | no R1 refusal | FACT + INFERENCE |
+| rotate 360 deg X | `|dy| ~ 2.45e-16` | no R1 refusal | FACT + INFERENCE |
+| rotate 180 deg Y | `|dx| ~ 1.22e-16` | no R1 refusal | FACT + INFERENCE |
+| rotate 360 deg Y | `|dx| ~ 2.45e-16` | no R1 refusal | FACT + INFERENCE |
+| X180 then Y180 | transverse components `~1.22e-16` | no R1 refusal | FACT + INFERENCE |
+| X360 then Y360 | transverse components `~2.45e-16` | no R1 refusal | FACT + INFERENCE |
+| mirrors XY/XZ/YZ | transverse components zero or signed zero | no R1 refusal | FACT + INFERENCE |
+
+[INFERENCE] No ordinary 180/360-degree construction tested here comes close to the 1e-12 cutoff. This substantially reduces the false-refusal risk that motivated the boundary test.
+
+### R2 nested, overlapping, pocket, and split-face boundaries
+
+| Case | B-rep / `_nested` result | Expected observation path from recovered code |
+|---|---|---|
+| equal D10 holes, centres 10 mm apart, tangent | `_nested = false` | not refused as nested |
+| equal D10 holes, centres 6 mm apart, overlap | `_nested = false` | form/contract path, not nested refusal |
+| equal D10 holes, centres 5 mm apart | `_nested = false` | boundary is not inside because comparison is strict `<` |
+| equal D10 holes, centres 4.999 mm apart | `_nested = true` | `out_of_scope` as one axis is inside the other cylinder |
+| coaxial D10/D14 step | `_nested = true` | `out_of_scope` |
+| D10/D14 offset 6.9 mm | `_nested = true` | `out_of_scope` |
+| D10/D14 offset 7.0 mm | `_nested = false` | not refused by nested rule |
+| rounded-corner blind pocket separated from hole | `_nested = false` | should continue to form checking |
+| round blind pocket separated from holes | `_nested = false` | should continue to form checking |
+| duplicate same-axis, same-D cylinder entries | skipped as duplicates by source | intended to tolerate a cylinder represented by several faces |
+
+[FACT] The current gate already records a mild equal-D overlap at 6 mm separation as `form_violation`, a 1.1-micron offset step as `out_of_scope`, and a 0.4-micron second cut as `out_of_scope`. Those are committed outputs, not rerun outputs.
+
+[OPINION] Add at least the 5.0 and 4.999 mm equal-hole cases to the permanent gate. They define the exact semantic boundary introduced by `_nested` and make future refactors auditable.
+
+### R4 size boundary
+
+| Geometry | 0.009 mm | 0.010 mm | 0.011 mm |
+|---|---|---|---|
+| Z hole | B-rep cylinder is exactly the requested size; source size test should refuse | size test does not refuse | size test does not refuse |
+| cross bore | source size test should refuse first | size test passes, off-axis rule should refuse | size test passes, off-axis rule should refuse |
+| cylindrical fillet | source size test should refuse first | size test passes, form check should decide | size test passes, form check should decide |
+
+[FACT] The source condition is `< 0.01`, not `<= 0.01`, so exactly 0.010 mm is on the supported side of the size rule.
+
+[OPINION] The documentation should make clear that a sub-0.01 mm cylindrical fillet is an `out_of_scope` size refusal before it can become the ordinary `form_violation` used for larger fillets. Section 3 already implies this; kickoff amendment 1 is broader and can otherwise be read as saying all fillets reach the form verdict.
+
+### R3 diameter-difference boundary
+
+| Nominal constructed difference | B-rep measured spread | Source comparison result |
+|---:|---:|---|
+| `5e-10 mm` | `5.000000413701855e-10` | not greater than `1e-9` |
+| `1e-9 mm` | `1.000000082740371e-9` | greater than `1e-9` |
+| `2e-9 mm` | `2.000000165480742e-9` | greater than `1e-9` |
+
+[OPINION] Pin these three cases in an executable test. The middle case is especially important because the text "more than 1e-9" and the actual measured-double boundary are not identical for a decimal construction.
+
+## 5. Documents and what could not be verified
+
+### Sections 3, 3.1, and 4 against recoverable code
+
+| Statement | Assessment | Label |
+|---|---|---|
+| observation version 1 pinned to scorer `0.5.0` by name | matches `OBSERVATION_VERSION = "1"` and `SCORER_BASIS = "0.5.0"` | FACT |
+| gate has 46 cases | current script contains 46 cases; committed result contains 46 rows | FACT |
+| only `ok` lets a contract be evaluated | matches `Observation.ok` | FACT |
+| strict measurement carries `scope_axes`, `min_cylinder_diameter`, `off_axis_concave` | present in recovered current measurement delta | FACT |
+| holes of different diameters use 1e-9 dimension slack | matches recovered observation code | FACT |
+| sub-0.01 mm cylindrical face is refused | matches recovered observation code | FACT |
+| failed scope scan is `out_of_scope` with reason | matches observation code and recovered pytest | FACT |
+| "top face" and mid-plane centre agree within `1e-11 mm` | stronger than evidence visible in the bundle unless the allowed thickness range is bounded accordingly | INFERENCE |
+| previous audit reproduced 27/27, 3,161 no-score-change replay, 180 controls | historical statement only; cannot be independently verified from this incremental bundle | FACT about verification status |
+| F1/F2 are deferred to M3 | matches observation module comments and section 4 | FACT |
+| `None` in predicates deferred to M3 | no M3 code is present in recoverable M1 objects | FACT |
+| compiled items pin observation/scorer basis in M2 | no M2 code exists yet | FACT |
+
+### Could not verify
+
+1. [FACT] The four requested task-1 commands could not be run against the actual repository because the bundle omits prerequisite `1fb9a513` and unchanged source objects.
+2. [FACT] The 333-part/fixture inventory could not be reconstructed or rerun.
+3. [FACT] The 180 construction controls could not be rerun through the actual observation map.
+4. [FACT] The 3,161 saved answers and the `main` comparison tree are absent, so reward/check/parsed equality and 0.5.0 timing could not be measured.
+5. [FACT] The exact current `measure.py` and `rubric.py` files cannot be reconstructed in full from the thin pack because they are stored as deltas against objects in the missing prerequisite. Their newly inserted round-2 sections are visible and were inspected, but that is not equivalent to executing the files.
+6. [FACT] New boundary geometry was built with the installed CadQuery/OCP kernel and evaluated against recoverable pure rules such as `_nested` and the explicit thresholds. Those experiments are useful boundary evidence but are not substitutes for end-to-end `observe_code()` results.
+7. [FACT] No network, credentials, paid service, or external system was used. The repository source was not modified. Audit scripts and notes were written only under `~/cad-spec-audit-out/l5-m1/v2/`.
+
+## Bottom line
+
+[OPINION] The round-2 implementation looks directionally correct and the five requested fixes are visible in source, but the evidence supplied to this verifier is insufficient for the requested merge-grade regression claim. The next action is not M2. The next action is to provide a self-contained local bundle and rerun this audit unchanged. If that rerun produces the advertised 46/46, 81/81, 37/37, zero 333-inventory regressions, 180 controls within 1e-9 mm, and zero 3,161-answer score diffs for both scorer versions, I would expect the remaining review to concentrate only on the new boundary cases documented above.
diff --git a/docs/design/L5-amendments.md b/docs/design/L5-amendments.md
index e6bf773..270f2ba 100644
--- a/docs/design/L5-amendments.md
+++ b/docs/design/L5-amendments.md
@@ -35,7 +35,7 @@ one is frozen and audited.
 ## 3. M1 record: what the observation map does
 
 Code: `cad_spec/l5/observation.py` (observation version 1, built on scorer
-0.5.0 by name). Gate: `scripts/test_l5_observation.py` (58 cases, in CI).
+0.5.0 by name). Gate: `scripts/test_l5_observation.py` (60 cases, in CI).
 Result: `results/l5/m1-observation-suite.md`.
 
 **Four verdicts.** `ok`; `form_violation` (the part has a feature nobody
@@ -62,25 +62,29 @@ of guessing. The scorer does not read those fields.
 |---|---|---|
 | Position | Not a contract variable. A plate moved off the origin measures the same; the bounding-box centre is reported for information | design note 7.2 |
 | Orientation | L along X, W along Y. Turned 90 or 270 degrees about Z, they swap. Turned by any other angle beyond the form tolerance, the form fails (a turn of 1e-10 rad is inside it) | design note 7.2; the form check |
-| What n counts | Through holes along Z only: one open, uninterrupted cylinder from the bottom face to the top face, within the form tolerance. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures |
+| What n counts | Recognised Z bores only: open from the bottom face to the top face at the form tolerance, with at least 99% of the cylindrical wall present. A hole that breaks out of a side or overlaps another by a very small amount can therefore still be recognised; rules F1 and F2 remain contract checks. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures |
 | px, py | The extent of the hole centres along X and Y. For the four-corner pattern that is the pitch; for any other pattern it is only the extent, and `rectangular` is then False | the design note defines pitch for the family only |
 | Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face. For an accepted axis the two differ by at most (T / 2) x 1e-12: 7e-12 mm for the thickest generated plate (14 mm) | one measurement shared with the scorer |
 | No hole | D, mx, my, px, py are `None`, never zero | a missing variable is not a value |
 | Stepped, counterbored or offset hole | `out_of_scope`: two different cylinders, one with its axis strictly inside the other (two 10 mm holes 5.0 mm apart are not nested; 4.999 mm apart they are). Judged on the unrounded axis and diameter of every concave cylinder face | D is not one number. The scorer's grouping rounds diameters to 1e-4 mm and hid a 1e-6 step |
 | Holes of different diameters | `out_of_scope` when the measured diameters differ by more than the dimension slack, 1e-9 mm. Values are binary doubles: holes written 10 and 10.000000001 measure 1.00000008e-9 apart and are refused | D is one number in v1; the verdict must not depend on which hole comes first |
-| Tilted or cross hole | `out_of_scope` for any concave cylinder whose axis is not along Z beyond floating-point slack (1e-12 rad). At that slack every variable is still right to about 1e-11 mm (the kernel reads T = 4.00000000001 on a 4 mm plate with 10 mm holes) | a 1e-8 rad tilt was `ok` with a margin wrong by 2e-8 mm |
+| Tilted or cross hole | `out_of_scope` for any concave cylinder whose axis makes an angle of more than 1e-12 rad with Z (the angle, not its X and Y components separately). On a 4 mm plate with 10 mm holes the kernel reads T = 4.00000000001 at that slack; that is an example at this scale, not a general accuracy bound. The shift between top face and mid-plane grows with T as stated above | a 1e-8 rad tilt was `ok` with a margin wrong by 2e-8 mm |
 | Supported size | `out_of_scope` when any cylindrical face is under 0.01 mm in diameter (exactly 0.01 mm is measured). This comes before the form check, so a fillet under that size is a size refusal, not the `form_violation` of amendment 1 | the probe that tells a hole from a boss cannot classify smaller ones; refusing is honest, reporting n = 0 was not |
 | Failed scope scan | `out_of_scope`, with the reason | it used to raise an exception out of the map |
 | Spline surfaces | `form_violation`, with no hole recognised. A known false rejection kept on purpose (scorer review round 3). The kernel pads a spline bounding box by 2e-7 mm, so L, W and T of such a part are not exact | soundness over coverage |
 
 **One deviation from the design note, for the owner's approval.** Section
 7.2 lists "extra pocket or slot" as `out_of_scope`. M1 reports it as
-`form_violation`. Reason: a separate pocket does not make any contract
-variable ambiguous, amendment 1 already fails every unrequested feature, and
-telling "a pocket" from "a fillet" would need feature recognition, which is
-new code that no review has seen. A pocket that cuts into a hole does make
-the hole ambiguous and is refused by the rules above. Either verdict fails
-gate G3. The external reviewer chose the same verdict, with that condition.
+`form_violation`, unless one of the cylinder scope rules above applies
+first. Reason: a separate pocket does not make any contract variable
+ambiguous, amendment 1 already fails every unrequested feature, and telling
+"a pocket" from "a fillet" would need feature recognition, which is new code
+that no review has seen. The scope rules look only at cylinder axes. So a
+pocket with large rounded corners can be `out_of_scope` (its corner
+cylinders are nested), and a pocket that cuts into a hole without nesting
+its axis is a `form_violation` whose numbers are diagnostic only. The map
+does not claim to recognise features. Either verdict fails gate G3. The
+external reviewer chose the same verdict.
 
 ### 3.1 External review of M1 (5 October 2026)
 
@@ -97,6 +101,16 @@ exact boundaries to be pinned and for two statements to be made precise.
 Both are done: twelve `boundary_` cases, and the rows above on the hole
 centre, on diameters and on the supported size.
 
+A third review (`audit/l5-m1-v3-audit.md`, 7 October 2026) ran everything
+locally: the gate and the three other suites pass, its 333 earlier parts
+show no wrong value in an `ok` result, the 180 controls agree to 1e-9 mm,
+and 3,161 saved answers score the same under both scorer versions. It found
+R2 to R5 resolved and R1 partly: the tilt limit was applied to the X and Y
+components separately, so a diagonal tilt of 1.3e-12 rad was accepted. The
+limit is now on the angle, with both sides pinned in the gate. It also asked
+for three statements above to be narrowed (what n counts, the scale of the
+tilt example, pockets and the scope rules), which is done.
+
 | # | Finding | Change |
 |---|---|---|
 | R1 | Holes tilted by 1e-8 rad were `ok` with a wrong margin; tilts up to 1e-6 rad were not refused | any tilt beyond 1e-12 rad is `out_of_scope` |
diff --git a/environments/cad_spec/cad_spec/measure.py b/environments/cad_spec/cad_spec/measure.py
index 97a24a8..ed80146 100644
--- a/environments/cad_spec/cad_spec/measure.py
+++ b/environments/cad_spec/cad_spec/measure.py
@@ -540,7 +540,7 @@ def _surface_conformance(solid: Any, bb: Any, holes: list[Hole]) -> bool:
     return True
 
 
-# A bore axis whose X or Y direction component exceeds this is "not along Z"
+# A bore axis tilted from the Z line by more than this angle is "not along Z"
 # for the L5 observation map. It is floating-point slack, not a tolerance on
 # tilt: at 1e-12 rad a hole moves 1e-11 mm across a 10 mm plate, a hundred
 # times below the slack on a dimension. Rotations about Z, mirrors and
@@ -578,7 +578,9 @@ def _scope_scan(solid: Any) -> tuple[int, float | None]:
         cylinder = adaptor.Cylinder()
         d, loc, r = cylinder.Axis().Direction(), cylinder.Axis().Location(), cylinder.Radius()
         smallest = 2 * r if smallest is None else min(smallest, 2 * r)
-        if abs(d.X()) <= STRICT_AXIS_SLACK and abs(d.Y()) <= STRICT_AXIS_SLACK:
+        # The tilt ANGLE, not X and Y each on their own allowance: a diagonal
+        # tilt of 1.3e-12 rad passed two separate component checks.
+        if math.hypot(d.X(), d.Y()) <= math.sin(STRICT_AXIS_SLACK):
             continue  # exactly along Z: a hole, or a matter for the form check
         p = adaptor.Value((adaptor.FirstUParameter() + adaptor.LastUParameter()) / 2,
                           (adaptor.FirstVParameter() + adaptor.LastVParameter()) / 2)
diff --git a/results/l5/m1-observation-suite.md b/results/l5/m1-observation-suite.md
index 10cd019..928f95b 100644
--- a/results/l5/m1-observation-suite.md
+++ b/results/l5/m1-observation-suite.md
@@ -2,7 +2,7 @@
 
 Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported from the scorer.
 
-**58 of 58 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.
+**60 of 60 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.
 
 | Case | Expected verdict | Verdict | Result | Why the case exists |
 |---|---|---|---|---|
@@ -52,6 +52,8 @@ Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported f
 | `review_closed_cavity` | form_violation | form_violation | pass | a void inside the plate |
 | `boundary_tilt_1e-12_rad_is_accepted` | ok | ok | pass | floating-point slack: every variable is still right to 1e-10 mm (T reads 4.00000000001) |
 | `boundary_tilt_1e-11_rad_is_refused` | out_of_scope | out_of_scope | pass | ten times the slack |
+| `boundary_diagonal_tilt_1.3e-12_rad_is_refused` | out_of_scope | out_of_scope | pass | third review: each direction component is 9.2e-13, under the slack, but the angle is 1.3e-12 |
+| `boundary_diagonal_tilt_0.9e-12_rad_is_accepted` | ok | ok | pass | the same diagonal tilt inside the slack |
 | `boundary_axis_on_the_other_rim` | form_violation | form_violation | pass | two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole |
 | `boundary_axis_inside_the_other_rim` | out_of_scope | out_of_scope | pass | 4.999 mm apart: each axis is inside the other cylinder |
 | `boundary_holes_of_0.009_mm` | out_of_scope | out_of_scope | pass | just under the supported size |
diff --git a/scripts/test_l5_observation.py b/scripts/test_l5_observation.py
index 81f87fd..79f5f5d 100644
--- a/scripts/test_l5_observation.py
+++ b/scripts/test_l5_observation.py
@@ -221,6 +221,21 @@ CASES: dict[str, tuple[str, str, dict, str]] = {
                ".rotate((0, 0, 0), (0, 1, 0), 5.729577951308232e-10)\n"
                "    result = result.cut(tool.translate((x, y, 0)))\n",
         "out_of_scope", {"L": 100.0, "W": 80.0}, "ten times the slack"),
+    "boundary_diagonal_tilt_1.3e-12_rad_is_refused": (
+        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
+               f"for x, y in {CORNERS}:\n"
+               '    tool = cq.Workplane("XY").circle(5).extrude(8, both=True)'
+               ".rotate((0, 0, 0), (1, 1, 0), 7.448451336700702e-11)\n"
+               "    result = result.cut(tool.translate((x, y, 0)))\n",
+        "out_of_scope", {"L": 100.0, "W": 80.0},
+        "third review: each direction component is 9.2e-13, under the slack, but the angle is 1.3e-12"),
+    "boundary_diagonal_tilt_0.9e-12_rad_is_accepted": (
+        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
+               f"for x, y in {CORNERS}:\n"
+               '    tool = cq.Workplane("XY").circle(5).extrude(8, both=True)'
+               ".rotate((0, 0, 0), (1, 1, 0), 5.156620156177409e-11)\n"
+               "    result = result.cut(tool.translate((x, y, 0)))\n",
+        "ok", NOMINAL, "the same diagonal tilt inside the slack"),
     "boundary_axis_on_the_other_rim": (
         holes_at("[(-2.5, 0), (2.5, 0)]"), "form_violation", {**ENVELOPE, "n": 0},
         "two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole"),
# Source notes: verification and review

Evidence: English auto-generated captions extracted on 2026-10-11. Demos and claimed outcomes were not independently reproduced.

## Practical knowledge

- [Fixing the PR Bottleneck, 2:00�?"8:00](https://www.youtube.com/watch?v=LlgiOCmFG_w&t=120s): deterministic checks, agent review, and human review form distinct layers. Green CI can hide tests that merely restate implementation, inspect source text, or mock away realistic failures. [8:00�?"14:00](https://www.youtube.com/watch?v=LlgiOCmFG_w&t=480s): test through simple public boundaries and give standards-oriented review a focused context. [14:00�?"19:00](https://www.youtube.com/watch?v=LlgiOCmFG_w&t=840s): high-signal repair can reduce comment burden; reversibility and impact affect review attention; pseudocode and small diagrams help a person understand a change.
- [Full coding walkthrough, 64:00�?"70:00](https://www.youtube.com/watch?v=-QFHIoCo-Ko&t=3840s): use a distinct review pass and a single red/green cycle so tests precede the implementation rather than merely explain it afterward. [70:00�?"73:00](https://www.youtube.com/watch?v=-QFHIoCo-Ko&t=4200s): service checks pass, but the exercised app fails because its table is not present. Runtime readiness and QA expose a different boundary.
- [The New Code, 10:00�?"16:30](https://www.youtube.com/watch?v=8rABwKRsec4&t=600s): tie difficult examples to specific intended behavior and use the specification as the target of evaluation.

## Adaptations and limits

The independent acceptance mapping, cause classification, scoped repair loop, and test counterexample are operational adaptations. Test-first work is recommended when it provides a meaningful failure signal, rather than imposed on every reversible change.

Pocock recommends reviewer commits and separating standards from an implementer's always-loaded instructions. Here, repair and commits follow task authorization, and required repository instructions remain binding. A standalone reviewer does not get write authority from the video.

The talks discuss reduced human review for reversible changes. This skill reports actual consequences and applies existing review policy. A low-risk rating, diagram, or successful agent review never grants merge or release permission.

2026-11-26T23:09:14.818107Z ERROR codex_models_manager::manager: failed to refresh available models: request timed out
exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$dirs = @('"'D:\\','D:\\10_PROJECTS','D:\\10_PROJECTS\\cad-engineering','.','environments','environments/cad_spec','environments/cad_spec/cad_spec','scripts','docs','docs/design','audit','results','results/l5'); foreach ("'$d in $dirs) { Get-ChildItem -LiteralPath $d -Force -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -in @('"'AGENTS.override.md','AGENTS.md','CLAUDE.md') } | ForEach-Object { "'$_.FullName; Get-Content -LiteralPath $_.FullName } }; git rev-parse HEAD; Get-Content environments/cad_spec/cad_spec/measure.py | Select-Object -First 100; Get-Content environments/cad_spec/cad_spec/measure.py | Select-Object -Skip 530 -First 230; Get-Content scripts/test_l5_observation.py | Select-Object -Last 115' in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 392ms:
D:\10_PROJECTS\cad-engineering\cad-spec-env\CLAUDE.md
# cad-spec: instructions for Claude Code

Read this before doing anything. It is short on purpose. The details are in
`README.md`, `ROADMAP.md`, `CHANGELOG.md` and `docs/experiments/`.

## What this project is

An RL reward environment. A model writes CadQuery code for a rectangular
mounting plate with four corner holes; the code runs in a sandbox, the solid
is measured in a trusted process and scored on 9 requirements behind 5 gates.
Tiers L1 to L4 (L4 is an engineering change order). The owner, Bilal Azzouzi,
is an aerospace structures and CAD engineer building this as a portfolio
piece for RL-environment and evaluation work.

## State on 26 November 2026

- Released as `v0.5.0`. Package cad-spec 0.5.0, scorer 0.5.0 (strict
  contract, reviewed in four external rounds before merge). Scorer 0.4.0 is
  kept selectable: everything published before 4 October 2026 was scored
  under it. The Prime Hub copy was 0.4.5 on 5 October (not rechecked since).
- Training run 1 (Qwen3.5-9B LoRA) and its replication are done, registered
  and audited: +40.0 and +39.2 points on L2 + L4, under scorer 0.4.0.
- The story in one document: `docs/REPORT.md`.
- Next work is in `ROADMAP.md`, section "After the external audit of
  3 October 2026". Items 1 (scorer 0.5) and 2 (L4 parser baseline) are done.
  Item 3 is being built as L5 v1 (region-graded change orders). Governing
  design and amendments: `docs/design/`. Milestone M1 (observation map,
  `cad_spec/l5/`) is merged (PR #35, after three review rounds in
  `audit/l5-m1-*.md`) but not yet counted as audited: five advisory
  findings of the first review are open and no review ran after the last
  fix (C1). M2 (contract compiler) starts only after M1 is audited. Do not
  reopen the architecture of the design note.
- Since v0.5.0, merged and unreleased: L5 M1 and the metrology reasoning
  layer (`research/`, `.claude/skills/cad-spec-*`, PR #36). See CHANGELOG
  "Unreleased".
- Working notes for agents: `.workshop/NOW.md` (what is true now) and
  `.workshop/PROMISES.md` (confirmed promises), loaded by the agent-workshop
  plugin.

## Rules that are never broken

1. **Money.** Never run anything that can cost money without Bilal's
   explicit go in the same session, after stating a worst-case bound: no
   model API call, no `prime` command that creates, deploys, trains, pushes
   or deletes. Read-only `prime` commands are fine. Deterministic providers
   (`reference`, `rev-a`, `parser-*`) are free.
2. **Used splits.** The test split and the replication split have each been
   evaluated once. Never run a model on them, and never use them to choose a
   prompt, a threshold, a tolerance, a checkpoint or a task. Local
   deterministic code may read them. Develop on train and dev only.
3. **Registered documents and results.** Files under `docs/experiments/` and
   `results/` are records. Never rewrite them. A correction is a dated
   section appended below, with the original text kept. Any change to a
   plan, a budget or an analysis is a dated amendment written before the
   outcome it could influence.
4. **Frozen code.** Do not edit `scripts/compare_training.py`,
   `scripts/compare_replication.py`, `scripts/bridge_check.py` or
   `scripts/replication_split.py`. Recorded verdicts are historical: a new
   scorer gets a new version, the old one stays selectable in `rubric.py`,
   and a recorded verdict is never replaced.
5. **The package.** Do not change anything under
   `environments/cad_spec/cad_spec/` unless the task is explicitly a new
   release with a version bump. A scorer change starts with the defect suite
   (`scripts/validate_scorer.py`), committed before the scorer. New evaluation logic goes in `scripts/`.
6. **Git.** One branch per task, never commit on `main`, never push, merge,
   rebase or force anything. Bilal pushes and opens the pull request. Leave
   these untracked paths alone: `audit/scratch/run1-breps/`,
   `audit/scratch/run1-perturbations/`, `results/baselines.md`,
   `results/superseded/`.
7. **Text.** No em dashes anywhere: code, comments, docs, commit messages.
   Write files with LF line endings (`newline="\n"` in Python).
8. **Verification writes to a temporary folder**, never over a tracked file.

## Expert skills (metrology reasoning layer)

Before modifying or reviewing anything that measures, compares or decides
(measurement, the L5 observation map, contracts and change orders,
feasibility and conflict sets, tolerances and slack, gates and the reward,
tests and artefacts, datums, GD&T, meshes or scans), read
`.claude/skills/cad-spec-metrology-router/SKILL.md` and every skill it
selects. Then state, before the first substantial decision:

```text
Skills consulted:
- <skill>: <why>
Relevant principles:
- <P-id or FP-id>: <how it changes this task>
```

If none applies: `Skills consulted: none. Reason: ...`. A skill counts as
used only if a principle visibly changes a decision, the code or a test.
The research behind the skills is in `research/` (start with
`research/expert-corpus-index.md`). Two rules from it apply to every test
already: expected values come from construction or hand derivation, never
from running the code under test; and no field or doc calls numerical slack
an "uncertainty".

## Environment (Windows, Git Bash)

```bash
source $HOME/cadspec.sh          # cd to the repo, repo-root .venv, CadQuery check
cd /d/10_PROJECTS/cad-engineering/cad-spec-env
export PYTHONIOENCODING=utf-8 PRIME_DISABLE_VERSION_CHECK=1
```

Prefix every `prime` command with `env -u SSLKEYLOGFILE`. Git checks text
files out with CRLF and stores LF. On Windows the scorer runs in `reuse`
mode; the hardened `fork` mode exists only on Linux (CI).

## Checks before every commit

```bash
ruff check scripts
(cd environments/cad_spec && ruff check . && mypy cad_spec && pytest -q)
python scripts/test_rubric.py
for t in scripts/test_*.py; do python "$t" > /dev/null || echo "FAILED $t"; done
python scripts/check_release.py
```

A new script gets a self-test `scripts/test_<name>.py` that uses synthetic
data, and a step in `.github/workflows/ci.yml`. Every user-visible change
gets a `CHANGELOG.md` entry under "Unreleased".

## Map

| Path | What |
|---|---|
| `environments/cad_spec/cad_spec/` | package: `tasks.py` (specs, prompts), `measure.py`, `rubric.py` (scorer), `environment.py` |
| `scripts/run_baseline.py` | evaluation runner and deterministic providers |
| `scripts/replay_eval.py`, `validate_scorer.py`, `test_rubric.py` | re-scoring and scorer validation |
| `docs/experiments/` | pre-registrations, amendments, results |
| `results/` | saved answers and verdicts (about 12,000 answers) |
| `audit/` | external audits; `state-and-roadmap-audit.md` lists the known weaknesses |

## Working with Bilal

- **Fast mode.** Work autonomously inside the rules above. Start each task
  with a plan of at most ten lines, then build without waiting, unless the
  prompt says to stop for a decision. Do not ask questions you can answer by
  reading the repository.
- Stop and ask only when: a rule above would be broken, money would be
  spent, a registered file would have to change, or the task's "Done when"
  list cannot be met.
- He is an expert in CAD geometry, tolerances and engineering drawings.
  Decisions about what a correct part is belong to him.
- Small commits with clear messages. When the task is finished, report in
  this order: what changed (five lines at most), the checks you ran and
  their results, anything that is not done, then the pull-request title and
  description each in its own code block, then the commands he must run to
  push.
- If a request conflicts with a rule above, stop and say so. Do not look for
  a way around the rule.
ddd4e14601b144db17d17c6b638de99f3b494176
"""Build a CadQuery script and extract the measurements a spec can be checked against.

This module is deliberately dumb about specs. It answers one question:
"given a piece of code, what geometry actually came out?"
Everything spec-related lives in rubric.py.

Hole detection uses exact surface geometry, not bounding-box guesses. Two
independent discriminators decide whether a cylindrical face is a drilled
bore, because each alone admits a false-positive class the other exists to
catch:

  * A membership probe placed just inside the surface asks whether material
    continues immediately inward. It rejects CONVEX cylinders - external
    rounds, bosses, the outer wall of a shell - but cannot reject concave
    partial cylinders such as inner corner fillets: those genuinely have
    material on their outside, which is precisely what the probe defines a
    bore to be.
  * An area completeness check asks whether the coaxial group closes into a
    full cylinder (pi*d*h over its Z extent). It rejects concave PARTIAL
    cylinders - an inner corner fillet is a quarter arc covering ~25% of
    its full cylinder - but cannot reject convex geometry: a boss is a
    complete cylinder.

Coaxial faces are grouped by axis position, so counterbores and seam-split
cylinders are handled explicitly rather than by luck.

Known limitation, stated plainly because it shapes scores: the completeness
check drops any bore that does not close into a full cylinder (since 0.3.0
such groups are REPORTED in Measurements.partial_bores, but still not scored) -
a hole intersecting another hole, breaking out through a side wall, or
opening into a pocket is returned as fewer holes, with nothing said. The
scoring consequence is asymmetric: a model that places a hole too close to
an edge is scored as having MISSED that hole rather than misplaced it,
losing hole count as well as position and pattern - two-plus requirements
for one mistake. The check is kept anyway because partial cylinders are
exactly how corner fillets masquerade as bores; anyone comparing model
scores should know the asymmetry is there.

Trust boundary (0.4.0): model code never hands the scorer a Python object.
The untrusted side (build_brep) executes the code, collects the OCCT shapes
bound to `result` and serialises them to BREP, a plain-text geometry format.
The trusted side (load_brep + measure) parses those bytes with the kernel
and measures what they describe. Before 0.4.0 the scorer called methods on
whatever object `result` was, so a class that answered BoundingBox() and
Volume() with nominal numbers scored 1.0 while its real geometry was a 1 mm
cube; and in fork mode the result came back as a pickle, which can execute
code when loaded. Neither path exists any more.

Execution safety: model code never runs in the caller's process. On POSIX
a warm worker forks a disposable, rlimited, env-scrubbed child per rollout
(CAD_SPEC_SANDBOX=fork) and measures the returned BREP itself; on Windows
one persistent worker runs rollouts in fresh temp directories
(CAD_SPEC_SANDBOX=reuse). CAD_SPEC_EXEC_TIMEOUT bounds each build (seconds,
default 10). CAD_SPEC_INPROC=1 disables isolation for debugging. This is
containment, not a security boundary; see SECURITY.md for what each mode
does and does not guarantee.

Windows note: the spawn-based worker requires callers to follow the standard
multiprocessing contract - entry scripts must guard top-level code with
if __name__ == "__main__":
"""

from __future__ import annotations

import atexit
import contextlib
import math
import multiprocessing
import os
import re
import tempfile
import textwrap
from dataclasses import dataclass, field
from typing import Any

# The newline after the fence is REQUIRED and not part of the capture: a bare
# \s* swallows it plus the first code line's leading indentation, which orphans
# every following line and raises IndentationError on otherwise valid code.
CODE_BLOCK = re.compile(r"```(?:python)?[ \t]*\r?\n(.*?)```", re.DOTALL)

# A drilled bore is a cylinder whose axis is parallel to Z.
AXIS_TOL = 1e-6
# Decimal places used when grouping coaxial cylindrical faces into features.
COAXIAL_DP = 3
# Fraction of the cylinder radius (dimensionless) to back off FROM THE SURFACE
# before probing membership, floored at PROBE_INSET_MIN_MM so hairline bores
# still probe strictly inside their own air channel. Asking "does material
# continue immediately inward of this surface" stays correct on hollow parts;
# probes deeper toward the axis lie there - a shelled box's outer-fillet axis
# sits in open cavity, so halfway-to-axis air reads as a phantom bore.
PROBE_INSET_FRACTION = 0.05
# Absolute floor for the surface-inset probe distance, in millimetres.
PROBE_INSET_MIN_MM = 1e-3
# Minimum covered fraction (dimensionless) of a FULL cylinder - summed
# cylindrical face area in mm^2 vs pi * d * h over the group's Z extent -
# for a coaxial group to count as a drilled bore. Separates closed bores
# from concave corner fillets, which probe like bores but cover only ~0.25
# as quarter arcs; seam-split bores still reach ~1.0 across their halves.
AREA_COMPLETENESS_MIN = 0.99
# Minimum coverage (dimensionless) for a rejected concave group to be REPORTED
            radius = cylinder.Radius()
            section = radius / abs(direction.Z())
            if not any(all(math.hypot(x - h.x, y - h.y)
                           + max(abs(radius - h.diameter / 2), abs(section - h.diameter / 2)) <= FORM_LINEAR_TOL
                           for x, y in ends)
                       for h in holes):
                return False
        else:
            return False
    return True


# A bore axis tilted from the Z line by more than this angle is "not along Z"
# for the L5 observation map. It is floating-point slack, not a tolerance on
# tilt: at 1e-12 rad a hole moves 1e-11 mm across a 10 mm plate, a hundred
# times below the slack on a dimension. Rotations about Z, mirrors and
# translations leave a Z axis exactly on Z.
STRICT_AXIS_SLACK = 1e-12


def _scope_scan(solid: Any) -> tuple[int, float | None]:
    """What the L5 observation map must know before it trusts the holes.

    Returns (concave cylindrical faces not exactly along Z, smallest diameter
    of any cylindrical face). The first is a tilted or cross hole, whole or
    partial: `off_axis_bores` (0.4.0, diagnostics) only counts bores that
    close into a full cylinder, which a tilted hole through a thin plate does
    not, and it accepts tilts up to 1e-6 rad. The second lets the map refuse
    features too small for the inward probe to classify.

    The probe goes at most half a radius inward (the 0.4.0 detectors use a
    fixed minimum that can cross a very small bore), and a point that is
    neither clearly inside nor clearly outside the material is an error, not
    a guess. Strict measurement only.
    """
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.GeomAbs import GeomAbs_SurfaceType
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_State

    classifier = BRepClass3d_SolidClassifier(solid.wrapped)
    count, smallest = 0, None
    for face in solid.Faces():
        adaptor = BRepAdaptor_Surface(face.wrapped)
        if adaptor.GetType() != GeomAbs_SurfaceType.GeomAbs_Cylinder:
            continue
        cylinder = adaptor.Cylinder()
        d, loc, r = cylinder.Axis().Direction(), cylinder.Axis().Location(), cylinder.Radius()
        smallest = 2 * r if smallest is None else min(smallest, 2 * r)
        # The tilt ANGLE, not X and Y each on their own allowance: a diagonal
        # tilt of 1.3e-12 rad passed two separate component checks.
        if math.hypot(d.X(), d.Y()) <= math.sin(STRICT_AXIS_SLACK):
            continue  # exactly along Z: a hole, or a matter for the form check
        p = adaptor.Value((adaptor.FirstUParameter() + adaptor.LastUParameter()) / 2,
                          (adaptor.FirstVParameter() + adaptor.LastVParameter()) / 2)
        t = (p.X() - loc.X()) * d.X() + (p.Y() - loc.Y()) * d.Y() + (p.Z() - loc.Z()) * d.Z()
        foot = (loc.X() + t * d.X(), loc.Y() + t * d.Y(), loc.Z() + t * d.Z())
        k = min(max(r * PROBE_INSET_FRACTION, PROBE_INSET_MIN_MM), r / 2) / r
        classifier.Perform(gp_Pnt(p.X() + (foot[0] - p.X()) * k, p.Y() + (foot[1] - p.Y()) * k,
                                  p.Z() + (foot[2] - p.Z()) * k), min(1e-6, r / 4))
        state = classifier.State()
        if state == TopAbs_State.TopAbs_OUT:
            count += 1  # no material just inward: a concave face, so part of a hole
        elif state != TopAbs_State.TopAbs_IN:
            raise RuntimeError("a cylindrical face could not be classified as concave or convex")
    return count, smallest


def _boundary_consistent(topo: Any) -> bool:
    """Is the solid still valid when every stored tolerance is the form tolerance?

    The kernel calls a shape valid when its edges lie on its faces WITHIN THE
    TOLERANCES THE SHAPE CARRIES. A boolean that swallows a feature a
    nanometre deep returns the nominal plane and cylinder joined by an edge
    that sits 1.2e-6 mm off both, and records that as the edge's tolerance:
    valid for the kernel, and every face is an allowed surface. So the check
    is repeated on a copy whose tolerances are all forced to FORM_LINEAR_TOL.
    A correct part whose tolerances were merely inflated still passes: its
    edges do lie on its faces. The scored shape itself is not touched.
    """
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.ShapeFix import ShapeFix_ShapeTolerance

    copy = BRepBuilderAPI_Copy(topo, True, False).Shape()
    ShapeFix_ShapeTolerance().LimitTolerance(copy, FORM_LINEAR_TOL, FORM_LINEAR_TOL)
    return bool(BRepCheck_Analyzer(copy, True, False, True).IsValid())


def _z_aligned_cylinders(solid: Any, *, z_ref: float | None = None) -> list[tuple[float, float, float, Any]]:
    """Exact kernel geometry for every Z-parallel cylindrical face.

    The centre is the stored axis location, as scorer 0.4.0 recorded it. With
    `z_ref` (strict measurement) it is where the axis crosses that height: an
    axis stored far from the part with a slight tilt must be measured at the
    part.
    """
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_SurfaceType

    out: list[tuple[float, float, float, Any]] = []
    for face in solid.Faces():
        adaptor = BRepAdaptor_Surface(face.wrapped)
        if adaptor.GetType() != GeomAbs_SurfaceType.GeomAbs_Cylinder:
            continue
        cylinder = adaptor.Cylinder()
        direction = cylinder.Axis().Direction()
        if abs(direction.X()) > AXIS_TOL or abs(direction.Y()) > AXIS_TOL:
            continue  # horizontal or angled cylinder: not a drilled bore
        location = cylinder.Axis().Location()
        cx, cy = location.X(), location.Y()
        if z_ref is not None:
            t = (z_ref - location.Z()) / direction.Z()
            cx, cy = cx + t * direction.X(), cy + t * direction.Y()
        out.append((cylinder.Radius(), cx, cy, face))
    return out


def _off_axis_bore_count(solid: Any) -> int:
    """Closed concave bores whose axis is not along Z. Diagnostics only.

    Same two discriminators as the Z bores (see _classify_cylinders): a probe
    just inside the surface must find no material (concave, not a round or a
    boss), and the coaxial group must cover a full cylinder over its axial
    extent (a bore, not a fillet arc). Never raises: a diagnostic must not be
    able to break measurement.
    """
    try:
        from OCP.BRepAdaptor import BRepAdaptor_Surface
        from OCP.BRepClass3d import BRepClass3d_SolidClassifier
        from OCP.GeomAbs import GeomAbs_SurfaceType
        from OCP.gp import gp_Pnt
        from OCP.TopAbs import TopAbs_State

        classifier = BRepClass3d_SolidClassifier(solid.wrapped)
        groups: dict[tuple, tuple[list[float], list[tuple[float, float]]]] = {}
        for face in solid.Faces():
            ad = BRepAdaptor_Surface(face.wrapped)
            if ad.GetType() != GeomAbs_SurfaceType.GeomAbs_Cylinder:
                continue
            cyl = ad.Cylinder()
            d = cyl.Axis().Direction()
            if abs(d.X()) <= AXIS_TOL and abs(d.Y()) <= AXIS_TOL:
                continue  # Z bores are measured by _classify_cylinders
            r, loc = cyl.Radius(), cyl.Axis().Location()
            dx, dy, dz = d.X(), d.Y(), d.Z()
            if next(c for c in (dx, dy, dz) if abs(c) > AXIS_TOL) < 0:
                dx, dy, dz = -dx, -dy, -dz  # one key per axis, whatever its sense
            u = (ad.FirstUParameter() + ad.LastUParameter()) / 2
            v = (ad.FirstVParameter() + ad.LastVParameter()) / 2
            p = ad.Value(u, v)
            t = (p.X() - loc.X()) * dx + (p.Y() - loc.Y()) * dy + (p.Z() - loc.Z()) * dz
            foot = (loc.X() + t * dx, loc.Y() + t * dy, loc.Z() + t * dz)
            k = max(r * PROBE_INSET_FRACTION, PROBE_INSET_MIN_MM) / r
            classifier.Perform(gp_Pnt(p.X() + (foot[0] - p.X()) * k, p.Y() + (foot[1] - p.Y()) * k,
                                      p.Z() + (foot[2] - p.Z()) * k), 1e-6)
            if classifier.State() == TopAbs_State.TopAbs_IN:
                continue  # material just inward: convex round or boss
            t0 = loc.X() * dx + loc.Y() * dy + loc.Z() * dz
            base = (loc.X() - t0 * dx, loc.Y() - t0 * dy, loc.Z() - t0 * dz)
            key = (*(round(c, COAXIAL_DP) for c in (dx, dy, dz, *base)), round(2 * r, 4))
            area, spans = groups.setdefault(key, ([0.0], []))
            area[0] += face.Area()
            v1, v2 = sorted((ad.FirstVParameter(), ad.LastVParameter()))
            sense = 1.0 if (d.X(), d.Y(), d.Z()) == (dx, dy, dz) else -1.0
            spans.append(tuple(sorted((sense * (t0 + v1), sense * (t0 + v2)))))
        count = 0
        for key, (area, spans) in groups.items():
            covered = sum(hi - lo for lo, hi in _merge_intervals(spans))
            if covered > 0 and area[0] / (math.pi * key[-1] * covered) >= AREA_COMPLETENESS_MIN:
                count += 1
        return count
    except Exception:  # diagnostics never break measurement
        return 0


def _merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Union of closed Z intervals, merging touching or overlapping ones."""
    merged: list[list[float]] = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1] + INTERVAL_MERGE_TOL:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    return [(lo, hi) for lo, hi in merged]


def _classify_cylinders(solid: Any, *, strict: bool = False, z_ref: float | None = None,
                        scope_axes: list[tuple[float, float, float]] | None = None,
                        ) -> tuple[list[Hole], list[PartialBore]]:
    """Closed internal bores, plus rejected concave groups as diagnostics.

    Two independent discriminators, because hollow geometry defeats either
    alone:

    1. Membership probed JUST INSIDE the cylindrical surface: material there
       means the face is convex - an external round, a boss, or the outer
       wall of a shell - and the face is rejected. Probes deeper toward the
       axis ask "is the axis buried in material", which is the wrong
       question on hollow parts and answers "no" for phantom reasons.
    2. Completeness: a coaxial group must cover AREA_COMPLETENESS_MIN of the
       full cylinder pi*d*L, where L is the length of the UNION of its faces'
       Z intervals. Concave corner fillets pass discriminator 1 honestly yet
       are quarter arcs; only closed-cylinder area separates them.

    Depth is the union length, not the tallest face: a bore whose wall is
    split into stacked faces (symmetric cutter, two-sided cut) is the same
    bore, and the modelling operation must not change its score.
    """
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_State

    classifier = BRepClass3d_SolidClassifier(solid.wrapped)

    # position -> diameter -> (summed face area mm^2, [Z intervals])
    features: dict[tuple[float, float], dict[float, tuple[list[float], list[tuple[float, float]]]]] = {}
    # Unrounded axis and diameter of each group (its first face), for the
    # strict scorer: a tolerance must not be widened by display rounding.
    raw: dict[tuple[tuple[float, float], float], tuple[float, float, float]] = {}
    for radius, cx, cy, face in _z_aligned_cylinders(solid, z_ref=z_ref if strict else None):
        fbb = face.BoundingBox()
        if fbb.zlen <= 0:
            continue
        inset = max(radius * PROBE_INSET_FRACTION, PROBE_INSET_MIN_MM)
        probe = gp_Pnt(cx + (radius - inset), cy, (fbb.zmin + fbb.zmax) / 2)
        classifier.Perform(probe, 1e-6)
        if classifier.State() == TopAbs_State.TopAbs_IN:
            continue  # material immediately inward => convex round/fillet/boss/wall
               '    tool = cq.Workplane("XY").circle(5).extrude(8, both=True)'
               ".rotate((0, 0, 0), (1, 1, 0), 5.156620156177409e-11)\n"
               "    result = result.cut(tool.translate((x, y, 0)))\n",
        "ok", NOMINAL, "the same diagonal tilt inside the slack"),
    "boundary_axis_on_the_other_rim": (
        holes_at("[(-2.5, 0), (2.5, 0)]"), "form_violation", {**ENVELOPE, "n": 0},
        "two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole"),
    "boundary_axis_inside_the_other_rim": (
        holes_at("[(-2.4995, 0), (2.4995, 0)]"), "out_of_scope", ENVELOPE,
        "4.999 mm apart: each axis is inside the other cylinder"),
    "boundary_holes_of_0.009_mm": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
               f".pushPoints({CORNERS}).hole(0.009)\n",
        "out_of_scope", ENVELOPE, "just under the supported size"),
    "boundary_holes_of_0.010_mm": (
        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
               f".pushPoints({CORNERS}).hole(0.01)\n",
        "ok", full(D=0.01), "exactly the supported size: measured"),
    "boundary_fillets_of_0.009_mm": (
        holes_at(CORNERS, '.edges("|Z").fillet(0.0045)'), "out_of_scope", ENVELOPE,
        "a fillet under the supported size is refused before the form check can call it a fillet"),
    "boundary_fillets_of_0.011_mm": (
        holes_at(CORNERS, '.edges("|Z").fillet(0.0055)'), "form_violation", NOMINAL,
        "just over it: measured, and the form fails"),
    "boundary_cross_bore_of_0.010_mm": (
        BASE + 'result = result.cut(cq.Workplane("YZ").circle(0.005).extrude(200, both=True))\n',
        "out_of_scope", ENVELOPE, "at the supported size the off-axis rule refuses it"),
    "boundary_diameters_5e-10_apart": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.0000000005)\n',
        "ok", NOMINAL, "inside the dimension slack: one D"),
    "boundary_diameters_written_1e-9_apart": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.000000001)\n',
        "out_of_scope", {**ENVELOPE, "n": 4},
        "written exactly 1e-9 apart, measured 1.00000008e-9 apart: values are binary doubles, so this is refused"),
    "boundary_diameters_2e-9_apart": (
        holes_at("[(-35, -25), (-35, 25), (35, -25)]")
        + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.000000002)\n',
        "out_of_scope", {**ENVELOPE, "n": 4}, "outside the slack"),
    # --- nothing to measure
    "two_solids": (
        BASE + 'result = cq.Compound.makeCompound([result.val(), cq.Solid.makeBox(5, 5, 5, cq.Vector(200, 0, 0))])\n',
        "not_single_solid", {}, "an unfused second body"),
    "no_result": (HEAD + 'plate = cq.Workplane("XY").box(100, 80, 4)\n', "build_error", {},
                  "the answer binds no part: gate G1, not the map"),
}


def run(code: str) -> tuple[str, dict, str]:
    from cad_spec.l5 import observe_code
    from cad_spec.measure import BuildError

    try:
        obs = observe_code(code)
    except BuildError as exc:
        return "build_error", {}, str(exc)[:80]
    return obs.status, dict(obs.values), obs.reason


def matches(got: dict, want: dict) -> list[str]:
    bad = []
    for key, value in want.items():
        have = got.get(key, "absent")
        same = (abs(have - value) <= 1e-9 if isinstance(value, float) and isinstance(have, (int, float))
                and not isinstance(have, bool) else have == value and type(have) is type(value))
        if not same:
            bad.append(f"{key}: expected {value!r}, measured {have!r}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write the result table to this markdown file")
    args = ap.parse_args()

    from cad_spec.l5 import EPS_DIM_MM, EPS_FORM_MM
    from cad_spec.measure import FORM_LINEAR_TOL
    from cad_spec.rubric import SCORER_VERSION, TOLERANCES

    rows, failures = [], 0
    # The map must use the scorer's own tolerances, not a copy of them.
    tolerance_ok = TOLERANCES[SCORER_VERSION].eps == EPS_DIM_MM and EPS_FORM_MM == FORM_LINEAR_TOL
    failures += not tolerance_ok
    print(f"[{'ok ' if tolerance_ok else 'BAD'}] tolerances are the scorer's: "
          f"dimension slack {EPS_DIM_MM:g} mm, form {EPS_FORM_MM:g} mm (scorer {SCORER_VERSION})")
    for name, (code, verdict, want, why) in CASES.items():
        got_verdict, got, reason = run(code)
        bad = ([f"verdict: expected {verdict}, got {got_verdict} ({reason})"] if got_verdict != verdict else [])
        if verdict == "ok" and set(want) != ALL_KEYS:
            bad.append("an `ok` case must state every variable")
        bad += matches(got, want)
        failures += bool(bad)
        print(f"[{'BAD' if bad else 'ok '}] {name:36s} {got_verdict}" + ("".join(f"\n        {b}" for b in bad)))
        rows.append((name, verdict, got_verdict, "pass" if not bad else "FAIL", why))
    case_failures = failures - (not tolerance_ok)
    print(f"\n{len(CASES) - case_failures}/{len(CASES)} cases as expected")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# L5 observation map: adversarial suite (milestone M1)", "",
                 f"Scorer {SCORER_VERSION}. Dimension slack {EPS_DIM_MM:g} mm, form tolerance {EPS_FORM_MM:g} mm, "
                 "both imported from the scorer.", "",
                 f"**{len(CASES) - case_failures} of {len(CASES)} cases as expected.** "
                 "Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.", "",
                 "| Case | Expected verdict | Verdict | Result | Why the case exists |", "|---|---|---|---|---|"]
        lines += [f"| `{n}` | {e} | {g} | {r} | {w} |" for n, e, g, r, w in rows]
        out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {out}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command 'Get-Content .claude/skills/cad-spec-metrology-router/SKILL.md; git show 4e26d30:CLAUDE.md; Get-Content environments/cad_spec/tests/test_l5_observation.py; Get-Content environments/cad_spec/cad_spec/l5/observation.py' in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 256ms:
---
name: cad-spec-metrology-router
description: MUST be consulted first, before designing, implementing, modifying, testing or reviewing any cad-spec work that touches geometry measurement, the L5 observation map, contracts and change orders, the scorer or its tolerances, decision rules, feasibility or conflict sets, intent probes, synthetic test parts, datums, GD&T, uncertainty, meshes, STEP or point clouds. Classifies the task and names the cad-spec expert skills that must be read before any code is written.
---

# cad-spec-metrology-router

## Purpose

Decide which cad-spec expert skills apply to a task, make the agent read them
before acting, and make the consultation visible in the report. Distilled
from the research in `research/` (principle IDs P01 to P44 are in
`research/expert-knowledge-map.md`).

## When this skill MUST be used

At the start of any task in this repository that changes or reviews: files
under `environments/cad_spec/cad_spec/` (`measure.py`, `rubric.py`,
`tasks.py`, `l5/`), gate or self-test scripts (`scripts/test_*`,
`scripts/validate_scorer.py`), the L5 design or amendments, item generation,
grading, tolerances, or any proposal involving datums, GD&T, meshes, STEP or
scans.

## When this skill should NOT be used

Pure money, release-process, CI-plumbing, prompt-wording or experiment-
registration tasks with no effect on what is measured, compared or decided.
Then report `Skills consulted: none` with the reason.

## Required inputs

The task statement; the list of files it will touch; the milestone (L5 M2a,
M2b, M3...).

## Preconditions

The task is stated precisely enough to list the files it touches. If not,
read the repository until it is (`CLAUDE.md`, "Working with Bilal").

## Formal reasoning procedure

1. Classify the task with the trigger table. Several triggers may fire.
2. Read every selected `SKILL.md` in full before writing code or a review.
3. Before the first substantial decision, write:

```text
Skills consulted:
- <skill>: <one line on why it applies>
Relevant principles:
- <P-id or FP-id>: <the rule as it applies here>
Domain: exact_brep_analytic | mesh | measured_points
```

4. For each principle, show the chain in the plan or the PR description:
   principle -> engineering decision -> code or test consequence.
5. If no skill applies: `Skills consulted: none. Reason: ...`

## Trigger table

```yaml
triggers:
  observation_or_measurement:      # measure.py, l5/observation.py, new variables, scope rules
    use: [cad-spec-geometric-observation, cad-spec-uncertainty-and-error]
  contract_or_change_order:        # contract.py, eco.py, holds, operators, family rules
    use: [cad-spec-specification-constraints]
  feasibility_mus_mcs_witness:     # compiler, Z3, subset enumeration, item file
    use: [cad-spec-specification-constraints, cad-spec-numerical-validation, cad-spec-conformity-decision]
  tolerance_slack_threshold:       # eps, form tolerance, robust margin, change detection
    use: [cad-spec-uncertainty-and-error, cad-spec-conformity-decision]
  verdict_gate_reward:             # rubric.py, gates G0-G5, pass rule, diagnostics
    use: [cad-spec-conformity-decision, cad-spec-geometric-observation]
  frame_orientation_datum:         # position, rotation, symmetry, origin, datums
    use: [cad-spec-datum-gdt-reasoning, cad-spec-geometric-observation]
  gdt_or_tolerance_zone:           # flatness, position, profile, minimum zone
    use: [cad-spec-datum-gdt-reasoning, cad-spec-geometric-fitting, cad-spec-conformity-decision]
  fitting_mesh_stepfacets_scan:    # any non-analytic geometry, point data, best fit
    use: [cad-spec-geometric-fitting, cad-spec-uncertainty-and-error, cad-spec-geometric-observation]
  tests_suites_artefacts:          # gates, adversarial parts, generators, planted conflicts
    use: [cad-spec-numerical-validation]
  intent_probes_misconceptions:    # probe schedule, sensitivity filter, signatures
    use: [cad-spec-numerical-validation, cad-spec-conformity-decision]
```

## Mathematical / geometric operators

None of its own. The router applies the dependency graph: for the quantity
the task touches, walk down its `requires` edges and load the skill of every
area that is not already settled for this case.

## Core expert principles

- Nothing at a higher level is decided before its lower levels are settled
  (dependency graph in `research/expert-knowledge-map.md`, Part 2): a verdict
  needs a formal predicate, a defined observation, a named decision rule and
  a known error kind.
- Exact nominal CAD and physical measurement are different domains; state
  which one the task is in before anything else.

## Decision rules

A task that changes what is measured, compared or decided without a
`Skills consulted` statement is incomplete. A reviewer may reject it on that
ground alone.

## Numerical hazards

A task that "only changes a constant" (slack, threshold, margin) is a
decision-rule change: it fires `tolerance_slack_threshold`, not none.

## Failure modes

Opening a skill and not applying it (no principle-to-code chain); selecting
only the obviously named skill and missing the cross-cutting ones
(uncertainty, validation); treating a mesh input as exact geometry.

## Out-of-scope cases

Questions about money, Prime, registration and splits are governed by
`CLAUDE.md` rules 1 to 3, not by these skills.

## Validation requirements

The selected skills' tests exist and pass before the task is reported done.

## Required evidence

The `Skills consulted` block, the principle-to-decision chain, and the tests
each selected skill requires, named in the report.

## Implementation checklist

- [ ] triggers classified from the files touched, not only the task title
- [ ] every selected skill read in full before code
- [ ] `Skills consulted` block written before the first substantial decision
- [ ] at least one principle per skill traced to a code or test consequence

## Review checklist

- [ ] every fired trigger has its skills listed
- [ ] each listed principle visibly changed a decision or a test
- [ ] the domain (exact, mesh, measured) is stated

## Tests that must exist

None for the router itself; the selected skills list theirs.

## Anti-patterns

"Skills consulted: all" with no principles named. Coding first and adding
the block afterwards.

## Source provenance

`research/expert-decisions.md` EDR-008; dependency graph in
`research/expert-knowledge-map.md`.

## Related skills

All `cad-spec-*` skills in `.claude/skills/`.
# cad-spec: instructions for Claude Code

Read this before doing anything. It is short on purpose. The details are in
`README.md`, `ROADMAP.md`, `CHANGELOG.md` and `docs/experiments/`.

## What this project is

An RL reward environment. A model writes CadQuery code for a rectangular
mounting plate with four corner holes; the code runs in a sandbox, the solid
is measured in a trusted process and scored on 9 requirements behind 5 gates.
Tiers L1 to L4 (L4 is an engineering change order). The owner, Bilal Azzouzi,
is an aerospace structures and CAD engineer building this as a portfolio
piece for RL-environment and evaluation work.

## State on 5 October 2026

- Released as `v0.5.0`. Package cad-spec 0.5.0, scorer 0.5.0 (strict
  contract, reviewed in four external rounds before merge). Scorer 0.4.0 is
  kept selectable: everything published before 4 October 2026 was scored
  under it. The Prime Hub copy is still 0.4.5.
- Training run 1 (Qwen3.5-9B LoRA) and its replication are done, registered
  and audited: +40.0 and +39.2 points on L2 + L4, under scorer 0.4.0.
- The story in one document: `docs/REPORT.md`.
- Next work is in `ROADMAP.md`, section "After the external audit of
  3 October 2026". Items 1 (scorer 0.5) and 2 (L4 parser baseline) are done.
  Item 3 is being built as L5 v1 (region-graded change orders). Governing
  design and amendments: `docs/design/`. Milestone M1 (observation map,
  `cad_spec/l5/`) is built; M2 (contract compiler) starts only after M1 is
  audited and merged. Do not reopen the architecture of the design note.

## Rules that are never broken

1. **Money.** Never run anything that can cost money without Bilal's
   explicit go in the same session, after stating a worst-case bound: no
   model API call, no `prime` command that creates, deploys, trains, pushes
   or deletes. Read-only `prime` commands are fine. Deterministic providers
   (`reference`, `rev-a`, `parser-*`) are free.
2. **Used splits.** The test split and the replication split have each been
   evaluated once. Never run a model on them, and never use them to choose a
   prompt, a threshold, a tolerance, a checkpoint or a task. Local
   deterministic code may read them. Develop on train and dev only.
3. **Registered documents and results.** Files under `docs/experiments/` and
   `results/` are records. Never rewrite them. A correction is a dated
   section appended below, with the original text kept. Any change to a
   plan, a budget or an analysis is a dated amendment written before the
   outcome it could influence.
4. **Frozen code.** Do not edit `scripts/compare_training.py`,
   `scripts/compare_replication.py`, `scripts/bridge_check.py` or
   `scripts/replication_split.py`. Recorded verdicts are historical: a new
   scorer gets a new version, the old one stays selectable in `rubric.py`,
   and a recorded verdict is never replaced.
5. **The package.** Do not change anything under
   `environments/cad_spec/cad_spec/` unless the task is explicitly a new
   release with a version bump. A scorer change starts with the defect suite
   (`scripts/validate_scorer.py`), committed before the scorer. New evaluation logic goes in `scripts/`.
6. **Git.** One branch per task, never commit on `main`, never push, merge,
   rebase or force anything. Bilal pushes and opens the pull request. Leave
   these untracked paths alone: `audit/scratch/run1-breps/`,
   `audit/scratch/run1-perturbations/`, `results/baselines.md`,
   `results/superseded/`.
7. **Text.** No em dashes anywhere: code, comments, docs, commit messages.
   Write files with LF line endings (`newline="\n"` in Python).
8. **Verification writes to a temporary folder**, never over a tracked file.

## Environment (Windows, Git Bash)

```bash
source $HOME/cadspec.sh          # venv, CadQuery check
cd ~/dev/cad-spec-env
export PYTHONIOENCODING=utf-8 PRIME_DISABLE_VERSION_CHECK=1
```

Prefix every `prime` command with `env -u SSLKEYLOGFILE`. Git checks text
files out with CRLF and stores LF. On Windows the scorer runs in `reuse`
mode; the hardened `fork` mode exists only on Linux (CI).

## Checks before every commit

```bash
ruff check scripts
(cd environments/cad_spec && ruff check . && mypy cad_spec && pytest -q)
python scripts/test_rubric.py
for t in scripts/test_*.py; do python "$t" > /dev/null || echo "FAILED $t"; done
python scripts/check_release.py
```

A new script gets a self-test `scripts/test_<name>.py` that uses synthetic
data, and a step in `.github/workflows/ci.yml`. Every user-visible change
gets a `CHANGELOG.md` entry under "Unreleased".

## Map

| Path | What |
|---|---|
| `environments/cad_spec/cad_spec/` | package: `tasks.py` (specs, prompts), `measure.py`, `rubric.py` (scorer), `environment.py` |
| `scripts/run_baseline.py` | evaluation runner and deterministic providers |
| `scripts/replay_eval.py`, `validate_scorer.py`, `test_rubric.py` | re-scoring and scorer validation |
| `docs/experiments/` | pre-registrations, amendments, results |
| `results/` | saved answers and verdicts (about 12,000 answers) |
| `audit/` | external audits; `state-and-roadmap-audit.md` lists the known weaknesses |

## Working with Bilal

- **Fast mode.** Work autonomously inside the rules above. Start each task
  with a plan of at most ten lines, then build without waiting, unless the
  prompt says to stop for a decision. Do not ask questions you can answer by
  reading the repository.
- Stop and ask only when: a rule above would be broken, money would be
  spent, a registered file would have to change, or the task's "Done when"
  list cannot be met.
- He is an expert in CAD geometry, tolerances and engineering drawings.
  Decisions about what a correct part is belong to him.
- Small commits with clear messages. When the task is finished, report in
  this order: what changed (five lines at most), the checks you ran and
  their results, anything that is not done, then the pull-request title and
  description each in its own code block, then the commands he must run to
  push.
- If a request conflicts with a rule above, stop and say so. Do not look for
  a way around the rule.
"""L5 observation map (milestone M1): fast checks. The adversarial gate is scripts/test_l5_observation.py."""

import pytest

from cad_spec.l5 import (
    EPS_DIM_MM,
    EPS_FORM_MM,
    FORM_VIOLATION,
    OK,
    OUT_OF_SCOPE,
    SCORER_BASIS,
    observe,
    observe_code,
)
from cad_spec.measure import FORM_LINEAR_TOL, build_and_measure
from cad_spec.rubric import TOLERANCES, score
from cad_spec.tasks import make_splits, reference_solution

TRAIN, DEV = make_splits()


def test_tolerances_are_those_of_scorer_0_5_0_by_name():
    assert SCORER_BASIS == "0.5.0"  # pinned: a later scorer default must not move L5 silently
    assert TOLERANCES["0.5.0"].eps == EPS_DIM_MM
    assert EPS_FORM_MM == FORM_LINEAR_TOL


@pytest.mark.parametrize("spec", [TRAIN[0], TRAIN[7], DEV[0], DEV[11], DEV[29]], ids=lambda s: s.id)
def test_reference_parts_observe_as_their_spec(spec):
    """The map and the task generator agree on what the reference part is."""
    obs = observe_code(reference_solution(spec))
    assert obs.status == OK, obs.reason
    v = obs.values
    assert (v["L"], v["W"], v["T"], v["n"], v["D"]) == pytest.approx(
        (spec.length, spec.width, spec.thickness, 4, spec.hole_diameter), abs=1e-9)
    assert (v["mx"], v["my"]) == pytest.approx((spec.edge_margin, spec.edge_margin), abs=1e-9)
    assert (v["px"], v["py"]) == pytest.approx(
        (spec.length - 2 * spec.edge_margin, spec.width - 2 * spec.edge_margin), abs=1e-9)
    assert v["rectangular"] and v["centered"] and v["symmetric"]


def test_form_verdict_is_the_scorers_r9():
    """A pocketed plate: the map's form verdict and R9 are one and the same check."""
    spec = DEV[0]
    pocketed = reference_solution(spec) + (
        f'\nresult = result.cut(cq.Workplane("XY").box(4, 4, 1).translate((0, 0, {spec.thickness / 2})))\n')
    obs = observe_code(pocketed)
    r9 = next(c for c in score(pocketed, spec).checks if c.name == "R9:no_other_features")
    assert obs.status == FORM_VIOLATION and not r9.passed and obs.reason == r9.detail
    assert obs.values["n"] == 4  # still measured: measurable does not mean acceptable


def test_a_legacy_measurement_is_refused():
    with pytest.raises(ValueError, match="strict"):
        observe(build_and_measure(reference_solution(DEV[0])))


def test_a_failed_scope_scan_is_a_refusal_not_an_exception(monkeypatch):
    """Review R5: the measurement recorded the failure; the map must refuse, not raise."""
    import cadquery as cq

    import cad_spec.measure as mm

    def broken(_solid):
        raise RuntimeError("synthetic classifier fault")

    monkeypatch.setattr(mm, "_scope_scan", broken)
    m = mm.measure(cq.Workplane("XY").box(100, 80, 4).val(), strict=True)
    assert m.strict and m.scope_error and m.off_axis_concave is None
    obs = observe(m)
    assert obs.status == OUT_OF_SCOPE and "synthetic classifier fault" in obs.reason
    assert not obs.ok and dict(obs.values) == {"L": 100.0, "W": 80.0, "T": 4.0}


def test_values_are_read_only_and_only_ok_allows_a_contract():
    obs = observe_code(reference_solution(DEV[0]))
    assert obs.ok
    with pytest.raises(TypeError):
        obs.values["L"] = 0.0  # type: ignore[index]

"""L5 observation map: a measured solid -> contract variables.

Design note, section 7 (docs/design/L5-region-graded-change-orders-v1.0.md),
with the implementation amendments (docs/design/L5-amendments.md).

The map answers one question: "what are L, W, T, n, D, mx, my, px, py of this
part?", and it gives one of four verdicts with the numbers:

  ok                the variables are measured and the part has no other face
  form_violation    the part has a feature nobody asked for. The numbers are
                    reported for diagnosis only: with a boss, a spline face
                    or loose geometry they may not describe the plate.
  out_of_scope      a variable cannot be measured without guessing (a stepped
                    hole, a tilted hole, holes of different diameters, a
                    feature too small to classify). The map refuses loudly
                    instead of returning a wrong number.
  not_single_solid  zero or several solids: nothing to measure

Only `ok` lets a contract be evaluated. `ok` is not compliance: it says the
numbers can be trusted, and the contract (including the family rules that a
hole lies inside the plate and that holes do not overlap) is the next gate.

Nothing is re-measured here. The numbers come from the strict measurement of
scorer 0.5.0 (measure(strict=True)) and the form verdict IS that scorer's R9
(rubric.form_verdict). Tolerances are imported from scorer 0.5.0 by name,
never copied and never following a later default.

Position is not a contract variable in L5 v1: a plate moved off the origin
measures the same. Orientation is: L is read along X and W along Y, so a
plate turned 90 degrees about Z has L and W swapped.

px and py are the extent of the hole centres along X and Y. For the family's
four-corner pattern that is the pitch; for any other pattern it is only the
extent, and `rectangular` says which case applies.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from ..measure import FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
from ..rubric import TOLERANCES, form_verdict

OBSERVATION_VERSION = "1"
SCORER_BASIS = "0.5.0"  # the validated scorer this map is built on; pinned, not "the current one"

# One source of truth: that scorer's own constants.
EPS_DIM_MM: float = TOLERANCES[SCORER_BASIS].eps  # two dimensions closer than this are the same dimension
EPS_FORM_MM: float = FORM_LINEAR_TOL              # two positions closer than this are the same position

# Supported size. The inward probe that tells a hole from a boss cannot
# classify a cylinder much smaller than this, so the map refuses instead of
# missing it. The generator's smallest hole is 3 mm.
MIN_CYLINDER_DIAMETER_MM = 0.01

OK = "ok"
FORM_VIOLATION = "form_violation"
OUT_OF_SCOPE = "out_of_scope"
NOT_SINGLE_SOLID = "not_single_solid"

Value = float | int | bool | None
_NO_VALUES: Mapping[str, Value] = MappingProxyType({})


@dataclass(frozen=True)
class Observation:
    """Contract variables of one part, with the verdict on how far to trust them.

    `values` (read-only) holds L, W, T (bounding box), n (through holes along
    Z), D, mx, my, px, py, and the booleans rectangular, centered, symmetric.
    A variable that does not exist (D with no hole) is None. With
    `out_of_scope` only the variables measured before the refusal are present.
    """

    status: str
    reason: str = ""
    values: Mapping[str, Value] = field(default_factory=lambda: _NO_VALUES)
    centre: tuple[float, float, float] | None = None  # bounding-box centre, for information

    @property
    def ok(self) -> bool:
        """May a contract be evaluated on `values`? Only then."""
        return self.status == OK


def _through(hole: Hole, m: Measurements) -> bool:
    """One uninterrupted, open cylinder from the bottom face to the top face."""
    return (hole.open and hole.segments == 1
            and abs(hole.z_min - m.z_min) <= EPS_FORM_MM and abs(hole.z_max - m.z_max) <= EPS_FORM_MM)


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= EPS_FORM_MM


def _nested(axes: list[tuple[float, float, float]]) -> bool:
    """Do two DIFFERENT concave Z cylinders share one hole position?

    Two faces of the same cylinder (same axis, same diameter) are one
    cylinder. Otherwise, when the axis of one lies inside the other, they form
    a counterbore, a stepped hole or an offset step: D is not one number.
    Two separate holes that merely overlap are not nested (a form matter).
    """
    for i, (x, y, d) in enumerate(axes):
        for u, v, e in axes[i + 1:]:
            distance = math.hypot(x - u, y - v)
            if distance <= EPS_FORM_MM and abs(d - e) <= EPS_DIM_MM:
                continue
            if distance < max(d, e) / 2:
                return True
    return False


def observe(m: Measurements) -> Observation:
    """Map a STRICT measurement (measure(strict=True)) to contract variables."""
    if not m.strict:
        raise ValueError("observe() needs a strict measurement: measure(solid, strict=True)")
    if m.solid_count != 1:
        return Observation(NOT_SINGLE_SOLID, f"{m.solid_count} solids, exactly one is required")

    centre = ((m.x_min + m.x_max) / 2, (m.y_min + m.y_max) / 2, (m.z_min + m.z_max) / 2)
    values: dict[str, Value] = {"L": m.length, "W": m.width, "T": m.thickness}

    def done(status: str, reason: str = "") -> Observation:
        return Observation(status, reason, MappingProxyType(dict(values)), centre)

    # Scope: anything that would make a hole variable a guess. Refusals come
    # before any hole variable is written.
    if m.scope_error or m.off_axis_concave is None or m.scope_axes is None:
        return done(OUT_OF_SCOPE, f"the scope checks could not be completed ({m.scope_error or 'no detail'})")
    if m.min_cylinder_diameter is not None and m.min_cylinder_diameter < MIN_CYLINDER_DIAMETER_MM:
        return done(OUT_OF_SCOPE, f"a cylindrical face under {MIN_CYLINDER_DIAMETER_MM} mm in diameter: "
                                  "below the supported size")
    if m.off_axis_bores or m.off_axis_concave:
        return done(OUT_OF_SCOPE, "a hole whose axis is not parallel to Z")
    if _nested(m.scope_axes):
        return done(OUT_OF_SCOPE, "two different cylinders at one hole position "
                                  "(counterbore, stepped or offset hole)")
    through = [h for h in m.holes if _through(h, m)]
    values["n"] = len(through)
    if through and max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_DIM_MM:
        return done(OUT_OF_SCOPE, "through holes of different diameters: D is not one number")

    if through:
        xs, ys = sorted(h.x for h in through), sorted(h.y for h in through)
        values["D"] = through[0].diameter
        values["mx"] = min(min(h.x - m.x_min, m.x_max - h.x) for h in through)
        values["my"] = min(min(h.y - m.y_min, m.y_max - h.y) for h in through)
        values["px"], values["py"] = xs[-1] - xs[0], ys[-1] - ys[0]
        corners = [(x, y) for x in (xs[0], xs[-1]) for y in (ys[0], ys[-1])]
        values["rectangular"] = len(through) == 4 and all(
            sum(_same(h.x, x) and _same(h.y, y) for h in through) == 1 for x, y in corners)
        values["centered"] = (_same(sum(xs) / len(xs), centre[0]) and _same(sum(ys) / len(ys), centre[1]))
        values["symmetric"] = all(
            any(_same(o.x, 2 * centre[0] - h.x) and _same(o.y, h.y) for o in through)
            and any(_same(o.x, h.x) and _same(o.y, 2 * centre[1] - h.y) for o in through)
            for h in through)
    else:
        values.update({"D": None, "mx": None, "my": None, "px": None, "py": None,
                       "rectangular": False, "centered": False, "symmetric": False})

    # Form: measurable does not mean acceptable. Same verdict as scorer 0.5.0.
    if not (m.valid and m.shell_count == 1 and m.loose_count == 0):
        return done(FORM_VIOLATION, "not one clean, valid, single-shell solid")
    passed, why = form_verdict(m)
    return done(OK) if passed else done(FORM_VIOLATION, why)


def observe_code(completion: str) -> Observation:
    """Build an answer in the sandbox, measure it strictly, and observe it.

    Raises BuildError when the code yields no part (gate G1's business) and
    ScorerUnavailableError when the scorer itself cannot run.
    """
    return observe(build_and_measure(completion, strict=True))

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$skills = @('"'cad-spec-geometric-observation','cad-spec-uncertainty-and-error','cad-spec-conformity-decision','cad-spec-numerical-validation','cad-spec-datum-gdt-reasoning'); foreach ("'$s in $skills) { Get-Content ".claude/skills/$s/SKILL.md" }; Get-ChildItem .venv/Scripts/python*; git diff 4e26d30 HEAD -- environments/cad_spec/cad_spec/measure.py scripts/test_l5_observation.py environments/cad_spec/cad_spec/l5/observation.py; Get-Content .github/workflows/ci.yml | Select-String -Pattern '"'observation' -Context 3" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 409ms:
---
name: cad-spec-geometric-observation
description: Read before adding, changing or reviewing anything that turns a cad-spec solid into numbers - measure.py, the L5 observation map (l5/observation.py), hole detection, bounding-box dimensions, margins, pitches, scope rules and verdicts (ok, form_violation, out_of_scope, not_single_solid). Defines what an observation is (operator, frame, invariance class, domain), when to refuse instead of measuring, and how new variables must be specified.
---

# cad-spec-geometric-observation

## Purpose

Guarantee that every number the grader evaluates is the output of a stated
operator in a stated frame on a stated domain, and that anything else is
refused.

## When this skill MUST be used

Changes to `measure.py`, `l5/observation.py`, the form verdict, new contract
variables, new part families, new feature types (slots, counterbores,
fillets as requested features), or any input other than a CadQuery solid.

## When this skill should NOT be used

Pure contract logic over already-observed values.

## Required inputs

The variable's definition (or the proposed one), the domain of the input,
the observation version and scorer basis.

## Preconditions

Input is a single solid built in the sandbox and serialised as BREP across
the trust boundary. The strict measurement is used (`measure(strict=True)`).

## Core expert principles

1. **P10** A value is the output of an association operator, not a property
   of the part. Name the operator for every variable.
2. **P44 / domain** On exact analytic B-rep the part is its own definition:
   association is reading the analytic surface. On meshes, faceted STEP or
   points, association is a fit by a criterion and this skill alone is not
   enough (load cad-spec-geometric-fitting).
3. **P17** Classify each variable: `frame_free` (L, W, T, D, px, py, mx, my
   measured to the part's own faces) or `frame_bound` (positions to the
   origin, mid-plane to Z = 0, anything read along a declared axis).
4. **P19 / P21** The declared global axes are the datum reference frame. They
   make the measurand well defined on a symmetric plate. Write that down.
5. **Refusal over guessing** (M1, FP07): if a variable would be a guess,
   return `out_of_scope` with a reason. Measurable does not mean acceptable
   (amendment 1): unrequested features are `form_violation`.
6. Only `ok` lets a contract be evaluated; `ok` is not compliance.

## Formal reasoning procedure (new or changed variable)

1. Write its definition row (EDR-001): operator, frame, invariance class,
   domain, numerical bound, refusal rules, known kernel biases.
2. Decide what topology variations must give the same value (split faces,
   seams, construction order) and what must change it.
3. Decide the refusal boundary and pin it on both sides with gate cases.
4. Decide `None` semantics: a variable that does not exist is `None`, never 0.
5. Implement on unrounded kernel data; never round before a decision.
6. Add adversarial and boundary cases whose expected values come from
   construction parameters.

## Mathematical / geometric operators (v1, exact domain)

```yaml
L, W, T:   axis-aligned bounding box of the single solid; frame_bound in orientation (L along X)
D:         2 x analytic cylinder radius of recognised through bores; frame_free
n:         count of distinct recognised Z through-bore axes (99% wall present)
hole centre: axis crossing the plate mid-plane (not the top face; differs by <= (T/2) x 1e-12 mm)
mx, my:    min distance from bore axes to the bounding side planes; frame_free
px, py:    extent of hole centres along X and Y; equals pitch only when rectangular is True
centered, symmetric: within the form tolerance 1e-7 mm
```

## Decision rules

Scope refusals come before any hole variable is written. Tilt above 1e-12
rad (angle, not components), nested cylinders, diameters differing by more
than 1e-9 mm, any cylindrical face under 0.01 mm: `out_of_scope`.

## Failure modes

FP07 silent wrong number; FP08 rounding hides a feature; FP09 detector blind
spot; FP10 wrong operator; FP11 unknown surface type treated as known; FP12
topological fragmentation; FP13 object spoofing; FP14 integral checks pass
extra features; FP15 ambiguous frame; FP16 frame-bound compared as
frame-free.

## Numerical hazards

Kernel noise near 1e-13 mm; kernel tolerances (1e-7 mm) are geometric gaps,
not specification tolerances; spline bounding boxes padded by about 2e-7 mm
(a signed bias: refuse or correct, never absorb, P27).

## Out-of-scope cases

Spline and offset surfaces, tilted or cross bores, counterbores and stepped
holes, blind holes (not counted), features under 0.01 mm, any mesh or point
input (needs a new observation version and the fitting skill).

## Validation requirements

The M1 gate style: hand-built parts, expected outcome written by hand,
boundary pairs at each limit, translated and turned plates (90 swaps L and W;
180 must measure the same), different construction orders giving identical
observations (design note V5).

## Required evidence

Observation version, scorer basis, status, reason, values; for a new
variable, its definition row and the gate cases citing it.

## Implementation checklist

- [ ] definition row written before code
- [ ] invariance class stated
- [ ] refusal rule pinned on both sides
- [ ] no rounding before decisions
- [ ] `None` for missing variables
- [ ] observation version bumped if any recorded output can change

## Review checklist

- [ ] could the same geometry built another way give another value?
- [ ] is there a geometry where this returns a plausible but wrong number?
- [ ] are expected values in the tests independent of `measure`?

## Tests that must exist

Per variable: nominal part, translated part, rotated parts, split-face and
seam variants, both sides of each refusal boundary, a part where the
variable does not exist.

## Anti-patterns

Approximating instead of refusing; counting faces; reading values from an
untrusted object; adding a variable without a definition row.

## Source provenance

F92-GTA ��1, ��5; F89-LSQ ��1.2; F18-PSS ��3.4-3.5; FWSO13 ��1; PK14 ��2.1;
TRACIM18 ��2.1; L5 amendments ��3 (M1 record and review findings R1 to R5).
Principles P10, P17, P19, P21, P27, P37, P44; EDR-001, EDR-006.

## Related skills

cad-spec-uncertainty-and-error, cad-spec-datum-gdt-reasoning,
cad-spec-geometric-fitting, cad-spec-numerical-validation.
---
name: cad-spec-uncertainty-and-error
description: Read before touching any cad-spec number that expresses error, slack or doubt - eps 1e-9 mm, the form tolerance 1e-7 mm, kernel (OCCT) tolerances, the 0.01 mm robust margin, change-detection thresholds, scorer TOLERANCES, item tolerance policy, known kernel biases, and any proposal mentioning uncertainty, confidence, noise, covariance or measurement error. Keeps numerical error, model error, measurement uncertainty, specification looseness and semantic ambiguity apart.
---

# cad-spec-uncertainty-and-error

## Purpose

Stop error kinds from being collapsed into one number, and stop known
biases from being treated as noise.

## When this skill MUST be used

Any change to slack, tolerance or threshold constants; any new field
expressing error; any new input domain; any wording in docs that says
"uncertainty" or "confidence".

## When this skill should NOT be used

Specification tolerances that are contract values (those are constraint
data; see cad-spec-specification-constraints).

## Required inputs

The domain (`exact_brep_analytic`, `mesh`, `measured_points`); the quantity;
the decision it feeds.

## Preconditions

The domain is stated. In the exact domain there is no measurement
uncertainty.

## Core expert principles

1. Five kinds, five treatments, never one field (EDR-006):

| Kind | Exists in L1-L5? | Representation | Treatment |
|---|---|---|---|
| numerical error | yes (about 1e-13 mm noise) | `numerical_slack_mm` (1e-9) | relaxed acceptance by slack, a named rule |
| kernel geometric tolerance | yes (1e-7 mm) | `kernel_tolerance_mm` | form decisions only |
| model error (operator wrong for the geometry) | prevented | refusal reason | `out_of_scope`, never a number |
| measurement uncertainty | no | reserved `measurement_covariance` | only in a measurement domain |
| specification looseness / semantic ambiguity | no number | template defect or refusal | fix the contract text |

2. **P24** Evaluating error is technical; choosing what to do about it is a
   decision rule owned by the project. Keep the two in separate code.
3. **P27** A known bias is not noise: correct it, refuse the case, or apply
   it one-sided (SUMU: `U+ = max(k u_c - delta, 0)`, `U- = max(k u_c + delta, 0)`).
   Never add it in quadrature (RSS with `u_c` overstates, RSS with U
   understates, below 80% achieved for nominal 95% at `delta/u_c = 2`).
4. **P30** Systematic error does not average out; in RL every grader error is
   systematic for the policy.
5. **P14** If a measurement domain ever arrives, never assume iid isotropic
   errors silently; use a structured covariance or flag the assumption.
6. **P32** Bug-free software is still not exact; state every accuracy
   claim with its measure (forward or backward, P33).

## Formal reasoning procedure

1. Name the domain and the error kind of the quantity.
2. If numerical: derive the bound from kernel evidence, pin it to a scorer
   version by name, never copy the value.
3. If it is a known signed effect: choose correct, refuse or one-sided, and
   record which.
4. Hand the value to a named decision rule (cad-spec-conformity-decision).
5. Write the slack in mm of the variables so scaling a constraint does not
   change what it accepts.

## Mathematical / geometric operators

```yaml
slack_check:   accept |lhs - rhs| <= eps in mm-of-variables scaling (M2a holds)
bias_one_sided: limits shifted by the signed bias on one side only
propagate (future): U_b = K U_d K^T ; frame: X = G + K H
```

## Decision rules

`DR-DIM-RELAXED-EPS` (1e-9 mm), `DR-FORM-KERNEL` (1e-7 mm),
`DR-FEAS-STRINGENT-0.01`, `DR-CHANGE-EPS`. A new value is a new rule ID and,
if any score can move, a new scorer version.

## Failure modes

FP19 bias folded into symmetric slack; FP20 float leakage; FP25 systematic
grader error exploited; FP27 assumed Gaussian or isotropic errors.

## Numerical hazards

Spline bounding-box padding (about 2e-7 mm, signed); binary doubles making
two "equal" diameters differ by 1e-9 mm; rounding before a decision;
`U(k=2)` is not `2 x U(k=1)` for biased results.

## Out-of-scope cases

Physical measurement uncertainty, CMM error models, scan noise: deferred
(EDR-009).

## Validation requirements

Boundary cases at each slack (at the limit, just inside, just outside);
evidence for each numerical bound (kernel tests on representative parts).

## Required evidence

For each constant: its kind, its source (scorer basis by name), the rule it
feeds, its boundary tests.

## Implementation checklist

- [ ] no field named `uncertainty`
- [ ] domain stated
- [ ] constants imported by name from the scorer basis
- [ ] signed effects handled explicitly
- [ ] slack in mm of the variables

## Review checklist

- [ ] could this number be read as a measurement uncertainty by a reader?
- [ ] is anything with a known sign treated symmetrically?

## Tests that must exist

Boundary pins for every slack; a non-binary-exact decimal; a scaled
constraint accepting the same parts; a known-bias case on the biased side.

## Anti-patterns

"Add a bit of tolerance" to make a test pass; RSS of a bias; copying a
constant instead of importing it; one `uncertainty` float.

## Source provenance

PEP97 ��1-4; PK14 ��2.4, ��3.2.3, ��3.4; F06-BAY ��3; F06-FIT ��3.7; FM12 ��2-3;
scorer `TOLERANCES` docstring; amendments 2 and ��3. Principles P14, P24,
P27, P28, P30, P32, P33; EDR-002, EDR-006.

## Related skills

cad-spec-conformity-decision, cad-spec-geometric-observation,
cad-spec-specification-constraints.
---
name: cad-spec-conformity-decision
description: Read before implementing or reviewing how cad-spec turns observations into verdicts - scorer requirements and gates, L5 gates G0-G5, the strict pass rule, structured rejects, the RL reward, verdict states (PASS, FAIL, INFEASIBLE, OUT_OF_SCOPE, INDETERMINATE), acceptance at a tolerance limit, guard bands, diagnostics and failure reports. Applies decision-rule and conformity-assessment practice (simple, stringent, relaxed acceptance; false accept versus false reject) to an exact-geometry RL grader.
---

# cad-spec-conformity-decision

## Purpose

Make every verdict the output of a stated decision rule on trustworthy
observations, with the asymmetric cost of a false pass in an RL setting
built in.

## When this skill MUST be used

Changes to `rubric.py`, the L5 runtime grader, gate order, pass rules,
reward shape, report format, diagnostics, or any new verdict state.

## When this skill should NOT be used

Pure measurement changes with no decision effect.

## Required inputs

Observation (status and values); the item (predicates, decision-rule IDs,
accepted MUS); the gate in question.

## Preconditions

Observation status is `ok` before any predicate is evaluated. Predicates are
formal (cad-spec-specification-constraints). The error kind of every slack
is known (cad-spec-uncertainty-and-error).

## Core expert principles

1. **P23** A verdict = tolerance + result + error bound + a stated rule.
   cad-spec's dimension check is relaxed acceptance by numerical slack
   (`DR-DIM-RELAXED-EPS`); name it.
2. **P25** Inside the interval is not proof of conformity; in the exact
   domain the doubt is limited to the slack band (C_m about 1e7), which is
   why binary verdicts are defensible here and nowhere else.
3. **P22** Conformance to the written contract is not functionality; G5 tests
   inherited behaviour, not function. Say so in reports.
4. **P29** Decisions can have more than two outcomes. cad-spec has them:
   PASS, FAIL (with the failing gate), INFEASIBLE expected (structured
   reject), OUT_OF_SCOPE (observation refused), and at compile time
   "discard and regenerate". INDETERMINATE is reserved; it is not a runtime
   verdict in L5 v1 (EDR-004).
5. **P30** False pass costs far more than false rejection in RL: a
   systematic false pass is learned and amplified. Prefer soundness over
   coverage and keep known false rejections documented (spline faces).
6. **P24 / G20** Verdicts depend only on the answer and the item, never on a
   population prior or the policy's own output distribution.
7. **P03** Report the margin, not only the verdict (diagnostic only).

## Formal reasoning procedure

1. G0 output type; G1 build; then observation: not `ok` stops evaluation
   (`out_of_scope` and `form_violation` fail G3 with their reason).
2. Evaluate each predicate with `holds` and the named rule; record the
   signed margin in mm of the variables.
3. Apply gates in order; stop at the first failure; record which gate.
4. For infeasible items: the named conflict must equal an accepted MUS.
5. Emit the verdict with its evidence (below).

## Mathematical / geometric operators

```yaml
pass_feasible:   G0 and G1 and G2 and G3 and G4 and G5
pass_infeasible: G0 and set(named) in accepted_mus     # equality, not superset
margin:          signed distance to the active limit, mm of the variables (diagnostic)
```

## Decision rules

Rule IDs (EDR-002): `DR-DIM-RELAXED-EPS`, `DR-FORM-KERNEL`,
`DR-FEAS-STRINGENT-0.01`, `DR-CHANGE-EPS`. Training reward: strict binary,
same as evaluation (design note ��12 default). Minimality and misconception
labels never change pass or fail.

## Failure modes

FP05 witness as answer; FP06 per-feature grading; FP14 integral checks;
FP24 suite success as proof; FP25 systematic grader error exploited.

## Numerical hazards

Answers clustering within a few eps of a limit (gaming numerics); `None`
variables silently skipped (must be false).

## Out-of-scope cases

Risk-based acceptance with production priors (PK14 ��3, F06-BAY ��2): useful
for an inspection product, rejected for the grader (G20).

## Validation requirements

Per gate: a part passing only that gate's predecessors; boundary cases at
each rule; witnesses pass; hardcoded witnesses fail G5 on intent-bearing
items; supersets and non-conflicts fail as rejects; always-reject and
always-comply baselines score as the design predicts.

## Required evidence

Item ID, observation version, scorer basis, rule IDs, failing gate, failing
predicate ID and margin, misconception set ("consistent with"), artefact
file. Enough to reproduce the verdict without the model.

## Implementation checklist

- [ ] no predicate evaluated on a non-`ok` observation
- [ ] every acceptance cites a rule ID
- [ ] margins recorded, never used for pass/fail
- [ ] verdict independent of population statistics

## Review checklist

- [ ] which wrong answer could pass this gate? (write it as a test)
- [ ] which right answer could fail it? (document if kept on purpose)

## Tests that must exist

Gate-order tests; rule boundary tests; reject set-equality tests; baseline
expectations (unchanged Rev A 0%, always reject about 10%, compiled oracle
100%).

## Anti-patterns

Partial credit per gate in the L5 reward; "close enough" acceptance outside
a named rule; adding INDETERMINATE to the reward; confidence scores on
misconceptions.

## Source provenance

PK14 ��2.1-2.4, ��3.1-3.4, ��4; F06-BAY ��2-3; F92-GTA ��2.5, ��3.5; PEP97 ��1;
design note ��5, ��6, ��8, ��12. Principles P03, P22 to P26, P29, P30; EDR-002,
EDR-004.

## Related skills

cad-spec-uncertainty-and-error, cad-spec-specification-constraints,
cad-spec-geometric-observation, cad-spec-numerical-validation.
---
name: cad-spec-numerical-validation
description: Read before writing or reviewing any cad-spec test, gate suite, defect suite, adversarial part, synthetic artefact, item generator check, planted conflict, intent probe schedule, misconception separability check, baseline, or validation report - and before claiming that an evaluator (measure, observation map, holds, apply_eco, conflict enumeration) is correct. Enforces generator-grader independence, test truth from construction, stated accuracy, and the artefact ladder in artefact-ladder.md.
---

# cad-spec-numerical-validation

## Purpose

Make every claim "this evaluator is correct" rest on reference data whose
truth does not come from the evaluator, with a stated accuracy, and with
failing cases named.

## When this skill MUST be used

New or changed gate suites, defect suites, adversarial parts, generator
checklists (V1 to V12), probe schedules, baselines, reports of a review.

## When this skill should NOT be used

Registered experiment analysis (governed by the pre-registration rules in
`CLAUDE.md`).

## Required inputs

The evaluator's computational aim (or the definition being tested); the
decision the test supports; the artefact level (artefact-ladder.md).

## Preconditions

A computational aim exists or is written first (P37, EDR-001).

## Core expert principles

1. **P31** Generate the question from the answer: build inputs from chosen
   truth (construction parameters, hand derivation, planted conflicts),
   never compute the expected value with the code under test (EDR-005).
2. **P32** Bug-free code is still not exact; every numeric expectation states
   its accuracy measure and tolerance, chosen against the decision it
   supports (not looser).
3. **P33** Prefer a backward statement when exactness is impossible: "exact
   for a part within 1e-9 mm of this one".
4. **P34** Show the grader accepts a region: many different correct answers,
   not one.
5. **EDR-003** SAT is self-certifying; UNSAT and MUS need certificates;
   tests must not share the solver they test.
6. **P09** A test set is a sampling plan; check it can see each error class
   (probe detectability per pattern, EDR-007).
7. **P38** Reports name the evaluator version, the tolerances, and every
   failing artefact by ID.
8. **P26** Passing a suite is evidence about the suite's coverage, not proof
   of every verdict; report known false-rejection classes.

## Formal reasoning procedure

1. Write the truth first (construction parameters or derivation).
2. Choose the artefact level and its expected outcome (value, verdict or
   refusal) before running anything.
3. For each boundary: one case at the limit, one just inside, one just
   outside, at the slack scale.
4. For generators: verify every output against the checklist (V1 to V12),
   discard and regenerate on failure, log discards.
5. Run; compare with the stated accuracy; list failures by artefact ID.

## Mathematical / geometric operators

```yaml
reference_pair:     (input built from truth, expected result)
null_space (fits):  x = x* + e n*, J^T e = 0 keeps the LS solution (FM12 ��4.1)
planted_conflict:   choose MUS sets first, then numbers that realise exactly them
region_sampling:    several witnesses spread over R_B (vertices and interior)
detectability:      for each pattern p, exists kept probe q with relation broken by p
```

## Decision rules

A suite passes only if every artefact passes; one failure is listed, not
averaged into a figure of merit.

## Failure modes

FP22 shared bug between generator and grader; FP23 loose test tolerance;
FP24 suite success as proof; FP26 probe set blind to a pattern; FP04 tests
sharing the solver.

## Numerical hazards

Expected values typed as floats that are not binary-exact; expected values
copied from a previous run's output.

## Out-of-scope cases

Statistical claims about models (registered experiments, not this skill).

## Validation requirements

The artefact ladder (`artefact-ladder.md`): each evaluator has artefacts at
every level that applies to it.

## Required evidence

Truth source per case (construction or derivation), expected outcome,
accuracy measure, evaluator version, failing IDs.

## Implementation checklist

- [ ] truth written before running
- [ ] boundary triplets at each limit
- [ ] no expected value produced by the evaluator under test
- [ ] certificates checked without the solver
- [ ] report lists failing IDs and versions

## Review checklist

- [ ] where did each expected value come from?
- [ ] which wrong implementation would still pass this suite?

## Tests that must exist

A self-test that flags gate cases whose expected values come from calling
the evaluator; a corrupted-certificate test; region-sampling tests; blind
probe schedule flagged.

## Anti-patterns

Snapshot tests of evaluator output used as truth; one witness as the only
accepted answer; widening a tolerance to make a test pass.

## Source provenance

FM12 ��1-6; TRACIM18 ��2-4; TRACIM-DB; F92-GTA ��3.3; PK14 ��3.2.2; design note
��10; amendments ��3. Principles P09, P26, P31 to P38; EDR-003, EDR-005,
EDR-007.

## Related skills

All other cad-spec skills; this one is cross-cutting.
---
name: cad-spec-datum-gdt-reasoning
description: Read before any cad-spec work involving where a part is or how it is oriented - origin, position checks (scorer R5, R8), rotation and axis conventions (L along X), symmetry of the plate family, datums, datum reference frames, 3-2-1 frames, and any GD&T (position, flatness, perpendicularity, profile, tolerance zones). Covers today's frame-by-declaration and the conditions a datum-based or GD&T feature must meet before it is implemented.
---

# cad-spec-datum-gdt-reasoning

## Purpose

Keep every frame-dependent quantity well defined: today by declaration, in
future by datum features, with symmetry and form error handled explicitly.

## When this skill MUST be used

Changes involving the origin, axes, rotation or translation handling;
position-type requirements; new part families with a different symmetry;
any GD&T callout; any frame derived from features.

## When this skill should NOT be used

Frame-free variables only (diameters, distances between the part's own
features), unless their invariance is in question.

## Required inputs

The variable or tolerance; its invariance class; the frame definition in
force; the symmetry group of the part family.

## Preconditions

The frame is either declared (global axes, as in L1 to L5) or built from
named datum features in a stated order with a stated association criterion.

## Core expert principles

1. **P17** Distances carry no position component; angles depend only on
   shape. Only `frame_bound` variables need a datum. Classify first.
2. **P19** With exact geometry the datum choice does not change results;
   with form error it does. Exact B-rep may use a declared frame; any mesh
   or scan may not.
3. **P21** A measurand must be well defined. A symmetric plate has several
   valid datum assignments (PK14's own example is a square plate with a
   central bore). Resolve by declaration (cad-spec today), by a
   symmetry-breaking feature, or by an explicit rule ("conforming if any
   symmetric frame conforms"), never silently.
4. **P18 / P42** How the frame is fixed redistributes uncertainty to every
   feature located in it; record how each frame was established.
5. **P16** GD&T form and zone tolerances are minimax problems, not
   least-squares ones.
6. **P43** Compare datum strategies by their effect on evaluated features.

## Formal reasoning procedure

1. Classify the quantity (`frame_free` or `frame_bound`, in translation and
   in rotation).
2. If `frame_bound`, cite the frame: declared (which axes, which origin,
   which plane) or datum-based (features, order, association criterion,
   degrees of freedom removed).
3. Enumerate the family's symmetry operations; decide for each whether the
   requirement is invariant, swapped (90 degrees: L and W) or violated.
4. For GD&T: write the tolerance-zone definition, the datum reference frame,
   the association criterion of each datum simulator and of the toleranced
   feature, and the material condition modifiers if any; then load
   cad-spec-geometric-fitting.
5. Pin each symmetry case with a gate test.

## Mathematical / geometric operators

```yaml
declare_frame:   global X, Y, Z; L along X, W along Y; position free in L5 v1
datum_frame:     fit datum features, solve rigid t with c(a_hat(x, t)) = c0 (six constraints)
propagate:       X = G + K H for uncertainty through the frame (measurement domain)
symmetry_check:  apply each symmetry g; compare observations; expect invariant or a documented swap
```

## Decision rules

L5 v1: a plate turned 90 degrees about Z has L and W swapped and fails by
design; turned by any other angle beyond the form tolerance it fails form;
translated, it measures the same; turned 180 it should measure the same.
Scorer 0.5.0: R5 references hole centres to the origin, R7 to the part's
own edges, R8 the mid-plane to Z = 0.

## Failure modes

FP15 underconstrained or ambiguous frame; FP16 frame-bound compared as
frame-free; FP17 datum form error ignored.

## Numerical hazards

Rotations within 1e-10 rad are inside the form tolerance and must not change
any frame-free value; near-symmetric parts (one hole off by 1e-9 mm) where
a symmetry decision flips.

## Out-of-scope cases

Datum features, material condition modifiers, composite tolerances,
profile tolerances: not implemented. A request for them gets a design note
first, not code.

## Validation requirements

For every symmetry operation of the family, a gate case with the expected
outcome written by hand. For a datum-based frame (future): two datum
strategies agree on an exact part and their difference is reported on a
perturbed part.

## Required evidence

Frame definition, invariance class, symmetry table, gate cases.

## Implementation checklist

- [ ] invariance class stated
- [ ] frame cited (declared or datum-based)
- [ ] symmetry table with expected outcomes
- [ ] GD&T: zone, datums, criteria, modifiers written before code

## Review checklist

- [ ] does any requirement change if the part is moved rigidly?
- [ ] is there a symmetric reading in which the verdict changes?

## Tests that must exist

Translated plate; plate turned 90, 180, 270 degrees; turn of 1e-10 rad;
mirrored hole pattern; (future) datum strategy comparison.

## Anti-patterns

Normalising rotations silently; inventing a datum order; implementing a GD&T
zone as a scalar band on a least-squares parameter.

## Source provenance

F18-PSS ��3-4; FWSO13 ��1, ��4-5; PK14 ��2.1; F92-GTA ��5, ��6; scorer docstring
(datums R5, R7, R8); design note ��7.2; amendments ��3. Principles P16 to P21,
P42, P43.

## Related skills

cad-spec-geometric-observation, cad-spec-geometric-fitting,
cad-spec-conformity-decision.


    Directory: D:\10_PROJECTS\cad-engineering\cad-spec-env\.venv\Scripts


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----        26/11/2026     18:38         274424 python.exe                                                           
-a----        26/11/2026     18:38         263400 pythonw.exe                                                          

IgnoreCase : True
LineNumber : 80
Line       :       - name: L5 observation map, adversarial suite (milestone M1 gate)
Filename   : InputStream
Path       : InputStream
Pattern    : observation
Context    : Microsoft.PowerShell.Commands.MatchInfoContext
Matches    : {0}


IgnoreCase : True
LineNumber : 82
Line       :         run: python scripts/test_l5_observation.py
Filename   : InputStream
Path       : InputStream
Pattern    : observation
Context    : Microsoft.PowerShell.Commands.MatchInfoContext
Matches    : {0}




exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$env:PYTHONDONTWRITEBYTECODE='"'1'; "'$env:PYTHONIOENCODING='"'utf-8'; .\\.venv\\Scripts\\python.exe scripts/test_l5_observation.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "git ls-tree -r --name-only 4e26d30 audit; Get-Content .claude/skills/cad-spec-numerical-validation/artefact-ladder.md; Get-Content environments/cad_spec/cad_spec/measure.py | Select-String -Pattern '_scope_scan|scope_error|strict' -Context 2 | Select-Object -Last 24; Get-Content environments/cad_spec/pyproject.toml | Select-Object -First 85; git log -5 --oneline 4e26d30" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 517ms:
audit/README.md
audit/a7-addendum.md
audit/extra-analysis.json
audit/gl-bundle-review.md
audit/guardrails-proposed.patch
audit/l5-m1-v2-audit.md
audit/reconstructed-tables.md
audit/reconstruction.json
audit/replication1_geometry_check.py
audit/run-steps.csv
audit/run1-cost-report-prefix.md
audit/run1-cost-report-suffix.md
audit/run1-cost-report.md
audit/run1-result-integrity.md
audit/scorer-0.5-audit.md
audit/scorer-0.5-v2-audit.md
audit/scorer-0.5-v3-audit.md
audit/scorer-0.5-v4-audit.md
audit/scratch/assemble.sh
audit/scratch/assemble_report.py
audit/scratch/check.sh
audit/scratch/check_report.py
audit/scratch/extra.sh
audit/scratch/extra_analysis.py
audit/scratch/fetch.sh
audit/scratch/fetch_sources.py
audit/scratch/inspect.sh
audit/scratch/inspect_metrics.py
audit/scratch/preflight_candidate.py
audit/scratch/quick_totals.py
audit/scratch/reconstruct.sh
audit/scratch/reconstruct_cost.py
audit/scratch/run1-code-features.json
audit/scratch/run1-extended.json
audit/scratch/run1-final-verification.json
audit/scratch/run1-geometry.json
audit/scratch/run1-mechanical.json
audit/scratch/run1-perturbations.json
audit/scratch/run1-rescore-repo.json
audit/scratch/run1-rescore-wheel.json
audit/scratch/run1-verdict.json
audit/scratch/run1-verdict.md
audit/scratch/run1_extended.py
audit/scratch/run1_geometry.py
audit/scratch/run1_mechanical.py
audit/scratch/run1_report.py
audit/scratch/run1_rescore.py
audit/scratch/run1_verify_report.py
audit/scratch/spend_guard_candidate.py
audit/scratch/test_guard_offline.py
audit/scratch/totals.sh
audit/scratch/verify_offline.sh
audit/smoke-steps.csv
audit/smoke3-report.md
audit/sources/advanced-configs.md
audit/sources/full-finetuning.md
audit/sources/installed-api-billing.py
audit/sources/installed-api-rl.py
audit/sources/installed-cli-rl.py
audit/sources/installed-cli-usage.py
audit/sources/manifest.json
audit/sources/models-and-pricing.md
audit/sources/prime-rl-commit.json
audit/sources/registered-grpo.py
audit/sources/registered-orchestrator-config.py
audit/sources/registered-orchestrator.py
audit/sources/registered-train-sink.py
audit/sources/update-user-limits.md
audit/sources/update-user-wallet-settings.md
audit/sources/upstream-concurrency.py
audit/sources/upstream-orchestrator-config.py
audit/sources/upstream-orchestrator.py
audit/sources/upstream-train-sink.py
audit/state-and-roadmap-audit.md
# Artefact ladder for cad-spec evaluators

Philosophy (FM12 ��1, P31): known truth, then the artefact built from it, then
the production evaluator, then comparison with the independently known
result. Never: production code computes the expected value, then passes its
own test.

Each level lists: what it tests, the independent truth source, the expected
outcome type, existing coverage in the repository (7 Oct 2026), and gaps.
"M1 gate" = `scripts/test_l5_observation.py`; "0.5.0 suite" =
`scripts/validate_scorer.py` defect suite; "M2a gate" =
`scripts/test_l5_contract.py` (branch only).

## Level 0. Exact ideal primitives
Tests: the nominal path. Truth: construction parameters of a plate with four
corner holes. Expected: exact values within 1e-9 mm, `ok`.
Coverage: M1 `nominal`; scorer tests on 230 generated specs. Gap: none.

## Level 1. Simple parameter perturbations
Tests: each variable responds to its own parameter only. Truth: perturbed
construction parameters. Expected: changed variable equals the perturbation;
others unchanged (frame-free invariance, P17).
Coverage: M1 `one_hole_moved_2_mm`, `different_margins_in_X_and_Y`,
`pattern_shifted_1_mm_in_X`. Gap: one case per contract variable with every
other variable checked unchanged.

## Level 2. Topological changes preserving geometry
Tests: values depend on geometry, not on topology (FP12). Truth: the same
geometry built differently (construction order, split faces, seam position,
fused coplanar faces, holes cut one by one versus as a pattern).
Expected: identical observations.
Coverage: partial (`measure.py` groups coaxial faces). Gap: explicit cases;
design note V5 makes this an M4 requirement for renderers.

## Level 3. Numerical tolerance cases
Tests: decision rules at their slack (EDR-002). Truth: limit plus or minus
known offsets at 1e-10, 1e-9, 1e-8 mm. Expected: accept at and inside the
slack, reject beyond.
Coverage: M1 `boundary_` cases (tilt, diameters, size, nesting); scorer
0.5.0 docstring example (6.6 against 6.5 +/- 0.1). Gap: the same triplets
for every Contract B constraint kind through `holds` (M2a/M3), and for the
change-detection threshold.

## Level 4. Frame and datum-dependent cases
Tests: invariance classes and declared frame (P17, P21). Truth: rigid motions
of the nominal part. Expected: translation invariant; 90 and 270 degrees swap
L and W; 180 identical; small turns beyond the form tolerance fail form.
Coverage: M1 `moved_off_the_origin`, `turned_90/180/270_degrees_about_Z`,
`turned_10_degrees_about_Z`. Gap: a turn of 1e-10 rad (inside the form
tolerance) giving unchanged frame-free values; mirrored pattern.

## Level 5. GD&T cases (future)
Tests: zone tolerances, datum reference frames. Truth: null-space and KKT
artefacts (FM12 ��4-5), lobed features with known minimum zone. Expected:
values to stated accuracy. Coverage: none. DEFER (EDR-009).

## Level 6. Boundary cases of the contract
Tests: parts exactly on a constraint boundary (margin exactly 2 D, hole
tangent to the edge, two holes touching). Truth: hand-derived. Expected:
pass at the limit (closed intervals), fail beyond; family rules F1 and F2
decide breakouts and overlaps, not the map.
Coverage: M1 `hole_1_micron_from_the_edge`, `review_hole_breaking_out_of_a_side`,
`review_two_overlapping_holes` (observation level). Gap: the same at contract
level in M3.

## Level 7. Ambiguous or indeterminate cases
Tests: refusal and discard logic. Truth: designed ambiguity (stepped holes,
two diameters 1e-9 mm apart, contradictions of 1e-10 mm in a contract).
Expected: `out_of_scope` at observation level; "discard and regenerate" at
compile level (FP03).
Coverage: M1 `counterbored_holes`, `holes_of_two_diameters`,
`review_offset_step`, boundary cases. Gap: compile-level near-contradiction
items (M2b).

## Level 8. Out-of-scope cases
Tests: refusal instead of guessing. Truth: geometry outside the operator's
domain. Expected: `out_of_scope` or `form_violation` with the documented
reason. Coverage: M1 `holes_tilted_5_degrees`, `cross_hole_along_X`,
`audit_surfaces_stored_as_splines`, `faceted_holes`, `pocket_in_the_top_face`,
`slot_through_the_plate`. Gap: a distinct reason code for "no association
operator for this surface type" (G5); any mesh input refused at the door.

## Level 9. Adversarial cases
Tests: attempts to obtain a pass without a correct part. Truth: the attack
construction. Expected: fail at the right gate.
Coverage: scorer object-spoofing tests (trust boundary), 0.5.0 defect suite
(notches, pockets, cross bores, clipped corners), M1
`tolerances_inflated_1000_times`, `audit_pocket_5_microns_deep`,
`review_boss_on_top`, `review_closed_cavity`. Gaps for L5: hardcoded witness
against probes (M3), parameter renamed or hardcoded (G2 interface),
answers placed within a few eps of a limit (boundary-margin report,
EDR-004), structured rejects naming a superset of an MUS or every constraint.

## Contract-level artefacts (M2b)

| Artefact | Truth | Expected |
|---|---|---|
| Region sampling | several hand-computed points of `R_B` (vertices and interior) | all pass `holds` exactly |
| Either/or coupling (design note ��4.2) | MCS sets {px, L} and {px, mx} derived by hand | both found; L and mx in `allowed_to_move`; T never |
| Several MUS (design note ��6.3) | {C2, C5, C7} and {C1, C5, C7} derived by hand | both found; n and symmetry in none |
| Planted conflicts | MUS sets chosen first, numbers solved to realise them | enumerator returns exactly them; certificates verify |
| Near-contradiction | two constraints 1e-10 mm apart | discarded, not infeasible |
| Corrupted certificate | valid certificate with one multiplier changed | checker rejects |

>     results and its running time are unchanged. strict=True (scorer 0.5.0)
      keeps unrounded values, measures each bore where its axis crosses the
      part, and adds the form check and the shape residual.
          + _count(topo, TopAbs_VERTEX, TopAbs_EDGE)
      )
>     scope_axes: list[tuple[float, float, float]] | None = [] if strict else None
>     holes, partial = _classify_cylinders(solid, strict=strict, z_ref=(bb.zmin + bb.zmax) / 2,
                                           scope_axes=scope_axes)
      for h in holes:
      off_axis_concave: int | None = None
      min_cylinder: float | None = None
>     scope_error: str | None = None
      extra_volume = missing_volume = None
      shape_error: str | None = None
>     if strict:
          try:
              conformance = _surface_conformance(solid, bb, holes)
          shape_error = shape_error or residual_error
          try:  # on its own: a failed scope scan must not disturb the form verdict
>             off_axis_concave, min_cylinder = _scope_scan(solid)
          except Exception as exc:
>             scope_error = f"{type(exc).__name__}: {exc}"[:200]
  
      def kept(value: float) -> float:
>         return value if strict else round(value, 4)
  
      return Measurements(
          surface_conformance=conformance,
          boundary_consistent=boundary,
>         strict=strict,
          off_axis_concave=off_axis_concave,
          scope_axes=scope_axes,
          min_cylinder_diameter=min_cylinder,
>         scope_error=scope_error,
          extra_volume=extra_volume,
          missing_volume=missing_volume,
  
  
> def _measure_code(code: str, *, strict: bool = False) -> Measurements:
      """Build and measure in THIS process (inproc and reuse modes)."""
>     return measure(load_brep(build_brep(code)), strict=strict)
  
  
  
  
> def _run_forked(code: str, budget: float, mem_mb: int, *, strict: bool = False) -> tuple[str, Any]:
      """Run one rollout in a disposable forked child. Returns (status, payload).
  
          return ("error", "rollout process returned a malformed result")
      try:
>         return ("ok", measure(load_brep(body), strict=strict))
      except BuildError as exc:
          return ("error", str(exc))
  
  
> def _run_reused(code: str, budget: float, mem_mb: int, *, strict: bool = False) -> tuple[str, Any]:
      """Run one rollout in this (persistent) process, in a fresh temp dir.
  
      try:
          os.chdir(workdir)
>         return ("ok", _measure_code(code, strict=strict))
      except BuildError as exc:
          return ("error", _clean_error(str(exc)))
              conn.send(("ok", None))
              return
>         code, budget, mem_mb, strict = payload
          try:
>             conn.send(run(code, budget, mem_mb, strict=strict))
          except Exception as exc:  # report faults before dying
              conn.send(("error", f"worker fault: {type(exc).__name__}: {exc}"))
          return self.proc.is_alive()
  
>     def call(self, code: str, *, strict: bool = False) -> Measurements:
          try:
>             self.conn.send(("measure", (code, _exec_timeout(), _mem_limit_mb(), strict)))
          except (BrokenPipeError, OSError) as exc:
              # The worker died earlier (an earlier answer crashed the kernel).
  
  
> def build_and_measure(completion: str, *, strict: bool = False) -> Measurements:
      """Extract code, run it isolated, measure the result.
  
      if _inproc_requested():
          require_cadquery()
>         return _measure_code(code, strict=strict)
      try:
          try:
>             return _get_worker().call(code, strict=strict)
          except _WorkerLostError:
              shutdown_worker()  # one retry on a fresh worker
              try:
>                 return _get_worker().call(code, strict=strict)
              except _WorkerLostError as exc:
                  raise ScorerUnavailableError(f"scoring worker could not be restarted: {exc}") from exc
[project]
name = "cad-spec"
description = "RL reward environment: write CadQuery from a dimensioned plate spec, scored by measuring the built B-rep in a trusted process. 9 requirements (dimensions, holes, pattern and Z datums, material volume, edge margin) behind 5 anti-reward-hacking gates; sandboxed per-rollout execution; five prompt tiers; mutation-validated scorer (0 false full credit over 1,230 mutants). 200 train / 30 held-out specs per tier."
tags = ["cad", "engineering", "code-generation", "cadquery", "geometry", "train", "eval"]
version = "0.5.0"
requires-python = ">=3.11"
license = { text = "MIT" }
# verifiers/datasets stay in the core set because `prime env push` installs the
# package's own dependencies. The scorer itself needs only cadquery, and
# `import cad_spec` no longer imports verifiers (see cad_spec/__init__.py).
#
# verifiers is deliberately UNPINNED (0.4.3), like Prime's own legacy example
# environments. cad-spec uses only the v0 core API (Rubric, SingleTurnEnv),
# which the platform provides. A version range made pip replace Hosted
# Training's own verifiers, dragging in a prime-sandboxes release that clashes
# with the training image (smoke run of 29 Sep 2026 crashed at startup), and a
# floor >= 0.2.0 made `prime env push` label this v0 package as v1.
# Reproducible local installs: pip install -c constraints.txt (verifiers==0.3.1).
dependencies = [
    "verifiers",
    "cadquery>=2.8,<2.9",
    "datasets>=2",
]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.8", "mypy>=1.11"]

[project.scripts]
cad-spec = "cad_spec.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["cad_spec"]

[tool.verifiers.eval]
num_examples = 3
rollouts_per_example = 5

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM", "RUF"]

[tool.mypy]
# Parse target 3.12: current numpy/py3.12 stubs use `type` statements that a
# 3.11 parser rejects; package code itself stays 3.11-compatible.
python_version = "3.12"
platform = "linux"
ignore_missing_imports = true
check_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["slow: long-running geometry checks"]
4e26d30 fix(l5): tilt limit on the angle, not on its components; narrow three statements
9c19215 test(l5): pin the exact boundary of each observation rule; make three statements precise
b9386f9 fix(l5): M1 after the external review: refuse tilts, micro-steps and what cannot be classified
08cc812 feat(l5): milestone M1, observation map with the strict form check
1fb9a51 Merge pull request #34 from azzbilal/release/v0.5.0



 succeeded in 24766ms:
[ok ] tolerances are the scorer's: dimension slack 1e-09 mm, form 1e-07 mm (scorer 0.5.0)
[ok ] nominal                              ok
[ok ] moved_off_the_origin                 ok
[ok ] turned_90_degrees_about_Z            ok
[ok ] turned_180_degrees_about_Z           ok
[ok ] turned_270_degrees_about_Z           ok
[ok ] different_margins_in_X_and_Y         ok
[ok ] pattern_shifted_1_mm_in_X            ok
[ok ] one_hole_moved_2_mm                  ok
[ok ] three_holes                          ok
[ok ] one_hole_in_the_middle               ok
[ok ] two_holes                            ok
[ok ] six_holes                            ok
[ok ] hole_1_micron_from_the_edge          ok
[ok ] five_holes                           ok
[ok ] no_holes                             ok
[ok ] tolerances_inflated_1000_times       ok
[ok ] fillets_on_the_vertical_edges        form_violation
[ok ] chamfers_on_the_top_edges            form_violation
[ok ] pocket_in_the_top_face               form_violation
[ok ] slot_through_the_plate               form_violation
[ok ] all_holes_blind                      form_violation
[ok ] one_hole_blind                       form_violation
[ok ] faceted_holes                        form_violation
[ok ] turned_10_degrees_about_Z            form_violation
[ok ] audit_pocket_5_microns_deep          form_violation
[ok ] audit_bore_mouth_cut_1.2e-6_deep     form_violation
[ok ] audit_surfaces_stored_as_splines     form_violation
[ok ] cross_hole_along_X                   out_of_scope
[ok ] counterbored_holes                   out_of_scope
[ok ] holes_of_two_diameters               out_of_scope
[ok ] holes_tilted_5_degrees               out_of_scope
[ok ] review_holes_tilted_1e-8_rad         out_of_scope
[ok ] review_holes_tilted_1e-6_rad         out_of_scope
[ok ] review_step_of_1e-6_in_radius        out_of_scope
[ok ] review_offset_step                   out_of_scope
[ok ] review_first_hole_1e-8_larger        out_of_scope
[ok ] review_last_hole_1e-8_larger         out_of_scope
[ok ] review_cross_bore_0.2_micron         out_of_scope
[ok ] review_holes_of_0.5_micron           out_of_scope
[ok ] review_second_cut_0.4_micron_off     out_of_scope
[ok ] review_hole_breaking_out_of_a_side   form_violation
[ok ] review_two_overlapping_holes         form_violation
[ok ] review_boss_on_top                   form_violation
[ok ] review_closed_cavity                 form_violation
[ok ] boundary_tilt_1e-12_rad_is_accepted  ok
[ok ] boundary_tilt_1e-11_rad_is_refused   out_of_scope
[ok ] boundary_diagonal_tilt_1.3e-12_rad_is_refused out_of_scope
[ok ] boundary_diagonal_tilt_0.9e-12_rad_is_accepted ok
[ok ] boundary_axis_on_the_other_rim       form_violation
[ok ] boundary_axis_inside_the_other_rim   out_of_scope
[ok ] boundary_holes_of_0.009_mm           out_of_scope
[ok ] boundary_holes_of_0.010_mm           ok
[ok ] boundary_fillets_of_0.009_mm         out_of_scope
[ok ] boundary_fillets_of_0.011_mm         form_violation
[ok ] boundary_cross_bore_of_0.010_mm      out_of_scope
[ok ] boundary_diameters_5e-10_apart       ok
[ok ] boundary_diameters_written_1e-9_apart out_of_scope
[ok ] boundary_diameters_2e-9_apart        out_of_scope
[ok ] two_solids                           not_single_solid
[ok ] no_result                            build_error

60/60 cases as expected

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$env:PYTHONDONTWRITEBYTECODE='"'1'; "'$env:PYTHONIOENCODING='"'utf-8'; .\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider environments/cad_spec/tests/test_l5_observation.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 8100ms:
..........                                                               [100%]
10 passed in 6.31s

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$env:PYTHONDONTWRITEBYTECODE='"'1'; "'$env:PYTHONIOENCODING='"'utf-8'; .\\.venv\\Scripts\\python.exe scripts/test_rubric_050.py; .\\.venv\\Scripts\\python.exe scripts/test_rubric.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 27887ms:
[ok ] reference                    reward=1.0   
[ok ] wrong_thickness              reward=0.9   
[ok ] two_holes_only               reward=0.8   
[ok ] wrong_hole_diameter          reward=0.8   
[ok ] offset_pattern               reward=0.8   
[ok ] built_in_inches              reward=0.3   
[ok ] shifted_stock                reward=0.9   
[ok ] whole_part_off_origin        reward=0.9   
[ok ] symmetric_cutter             reward=1.0   
[ok ] drilled_from_bottom          reward=1.0   
[ok ] two_sided_meeting            reward=1.0   
[ok ] HACK_two_sided_misaligned    reward=0.0   
[ok ] LIMIT_hole_breakout          reward=0.7   
[ok ] part_off_z                   reward=0.9   
[ok ] HACK_fake_result_object      reward=0.0   
[ok ] HACK_membrane                reward=0.0   
[ok ] HACK_hidden_cavity           reward=0.0   
[ok ] HACK_loose_face              reward=0.0   
[ok ] diameter_upper_limit         reward=0.9   
[ok ] diameter_lower_limit         reward=0.9   
[ok ] LIMIT_nurbs_surfaces         reward=0.0   
[ok ] BROKEN_sketch_only           reward=0.0   
[ok ] fillets_r3                   reward=0.9   
[ok ] pocket_small                 reward=0.9   
[ok ] pocket_big                   reward=0.8   
[ok ] HACK_solid_block             reward=0.0   
[ok ] HACK_blind_dimples           reward=0.0   
[ok ] HACK_corner_tabs             reward=0.0   
[ok ] HACK_swiss_cheese            reward=0.0   
[ok ] HACK_hollow_shell            reward=0.0   
[ok ] HACK_cylinder_bbox           reward=0.0   
[ok ] HACK_counterbored            reward=0.0   
[ok ] shelled_filleted_box         reward=0.0   
[ok ] fenced_and_indented          reward=1.0   
[ok ] BROKEN_syntax                reward=0.0   
[ok ] BROKEN_no_result             reward=0.0   
[ok ] BROKEN_prose                 reward=0.0   
[ok ] diameter_at_limit_plus       reward=1.0   
[ok ] diameter_at_limit_minus      reward=1.0   
[ok ] length_one_grid_step         reward=0.8   
[ok ] thickness_one_grid_step      reward=0.9   
[ok ] one_hole_quarter_mm_off      reward=0.8   
[ok ] pattern_half_mm_off          reward=0.8   
[ok ] within_tolerance             reward=1.0   
[ok ] z_datum_half_mm              reward=0.9   
[ok ] chamfered_top_edges          reward=0.9   
[ok ] edge_notch                   reward=0.9   
[ok ] slot_through                 reward=0.9   
[ok ] cross_bore                   reward=0.9   
[ok ] clipped_corner               reward=0.9   
[ok ] lug_in_bore                  reward=0.9   
[ok ] lug_in_bore_at_probe         reward=0.7   
[ok ] extra_fifth_hole             reward=0.8   
[ok ] AUDIT_pocket_5_microns_deep  reward=0.9   
[ok ] AUDIT_boss_5_microns_high    reward=0.9   
[ok ] AUDIT_slot_13_microns_wide   reward=0.9   
[ok ] AUDIT_side_tab_5_microns     reward=0.9   
[ok ] AUDIT_chamfer_10_microns     reward=0.9   
[ok ] AUDIT_fillet_30_microns      reward=0.9   
[ok ] AUDIT_lug_50_microns_in_bore reward=0.9   
[ok ] AUDIT_countersink_10_microns reward=0.9   
[ok ] AUDIT_second_cut_offset_0.4_micron reward=0.9   
[ok ] AUDIT_turned_0.001_degree_about_Z reward=0.9   
[ok ] AUDIT_draft_0.01_degree      reward=0.9   
[ok ] AUDIT_diameter_0.100049_over reward=0.9   
[ok ] AUDIT_length_0.100049_over   reward=0.9   
[ok ] AUDIT_part_moved_0.1007_diagonally reward=0.9   
[ok ] AUDIT_z_datum_0.10004        reward=0.9   
[ok ] AUDIT_at_the_limit_still_passes reward=1.0   
[ok ] AUDIT_plate_thinner_than_the_band reward=0.8   
[ok ] AUDIT3_spline_top_with_1mm_bump reward=0.9   
[ok ] AUDIT3_pocket_floor_stored_far_away reward=0.9   
[ok ] AUDIT3_pocket_1_nanometre_deep reward=0.9   
[ok ] AUDIT3_diameter_0.100001_over reward=0.9   
[ok ] AUDIT3_z_datum_0.100001      reward=0.9   
[ok ] AUDIT4_bore_mouth_cut_1.2e-6_deep reward=0.9   
[ok ] AUDIT4_bore_mouth_cut_8e-7_deep reward=0.9   
[ok ] AUDIT4_bores_tilted_on_the_diagonal reward=0.9   
[ok ] AUDIT4_correct_plate_with_inflated_tolerances reward=1.0   
[ok ] SAVED_dev_answer_gen_0021    reward=0.9   
[ok ] the saved gen-0021 answer still scores 1.0 under 0.4.0 (kept for replay)

81/81 cases behaved as expected
[ok ] reference                  reward=1.0    expected 1.0000
[ok ] wrong_thickness            reward=0.8889 expected 0.8889
[ok ] two_holes_only             reward=0.7778 expected 0.7778
[ok ] wrong_hole_diameter        reward=0.7778 expected 0.7778
[ok ] offset_pattern             reward=0.7778 expected 0.7778
[ok ] built_in_inches            reward=0.2222 expected 0.2222
[ok ] shifted_stock              reward=0.8889 expected 0.8889
[ok ] whole_part_off_origin      reward=0.8889 expected 0.8889
[ok ] symmetric_cutter           reward=1.0    expected 1.0000
[ok ] drilled_from_bottom        reward=1.0    expected 1.0000
[ok ] two_sided_meeting          reward=1.0    expected 1.0000
[ok ] HACK_two_sided_misaligned  reward=0.0    expected 0.0000
[ok ] LIMIT_hole_breakout        reward=0.7778 expected 0.7778
[ok ] part_off_z                 reward=0.8889 expected 0.8889
[ok ] HACK_fake_result_object    reward=0.0    expected 0.0000
[ok ] HACK_membrane              reward=0.0    expected 0.0000
[ok ] HACK_hidden_cavity         reward=0.0    expected 0.0000
[ok ] HACK_loose_face            reward=0.0    expected 0.0000
[ok ] diameter_upper_limit       reward=1.0    expected 1.0000
[ok ] diameter_lower_limit       reward=1.0    expected 1.0000
[ok ] LIMIT_nurbs_surfaces       reward=0.0    expected 0.0000
[ok ] BROKEN_sketch_only         reward=0.0    expected 0.0000
[ok ] fillets_r3                 reward=1.0    expected 1.0000
[ok ] pocket_small               reward=1.0    expected 1.0000
[ok ] pocket_big                 reward=0.8889 expected 0.8889
[ok ] HACK_solid_block           reward=0.0    expected 0.0000
[ok ] HACK_blind_dimples         reward=0.0    expected 0.0000
[ok ] HACK_corner_tabs           reward=0.0    expected 0.0000
[ok ] HACK_swiss_cheese          reward=0.0    expected 0.0000
[ok ] HACK_hollow_shell          reward=0.0    expected 0.0000
[ok ] HACK_cylinder_bbox         reward=0.0    expected 0.0000
[ok ] HACK_counterbored          reward=0.0    expected 0.0000
[ok ] shelled_filleted_box       reward=0.0    expected 0.0000
[ok ] fenced_and_indented        reward=1.0    expected 1.0000
[ok ] BROKEN_syntax              reward=0.0    expected 0.0000
[ok ] BROKEN_no_result           reward=0.0    expected 0.0000
[ok ] BROKEN_prose               reward=0.0    expected 0.0000

37/37 cases behaved as expected

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command 'git diff --quiet 4e26d30 HEAD -- environments/cad_spec/cad_spec environments/cad_spec/tests/test_l5_observation.py scripts/test_rubric.py scripts/test_rubric_050.py; Write-Output "Reviewed-source comparison exit: $LASTEXITCODE"; git status --short' in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 646ms:
Reviewed-source comparison exit: 0
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
?? .workshop/LOG.md
?? .workshop/reviews/
?? audit/scratch/run1-breps/
?? audit/scratch/run1-perturbations/
?? orca.yaml
?? results/baselines.md
?? results/superseded/

codex
The change correctly applies the tilt limit to the combined transverse direction rather than each component independently. No actionable regressions were found; verification passed all 60 observation cases, 10 focused pytest tests, and both scorer suites (81 and 37 cases).
The change correctly applies the tilt limit to the combined transverse direction rather than each component independently. No actionable regressions were found; verification passed all 60 observation cases, 10 focused pytest tests, and both scorer suites (81 and 37 cases).
````
