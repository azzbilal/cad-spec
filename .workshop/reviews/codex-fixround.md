# Codex review of the fix round (working tree against main)

- Command: `codex review --base main -c 'sandbox_mode="read-only"' -c 'approval_policy="never"'`
- codex-cli 0.169.0, model gpt-6.1-sol, reasoning effort high, sandbox read-only, approval never
- Started 2026-11-27T00:52:22Z, finished 2026-11-27T00:53:48Z, exit 0, 86 s wall time
- What it reviewed: nothing was committed on `fix/l5-m1-audit`, so HEAD equals `main` (`ddd4e14`).
  Codex diffed the working tree against `ddd4e14` (`git diff ddd4e14...` in its first commands
  below), which covers every changed tracked file: `CHANGELOG.md`, `CLAUDE.md`,
  `docs/design/L5-amendments.md`, `environments/cad_spec/cad_spec/l5/observation.py`,
  `results/l5/m1-observation-suite.md`, `scripts/test_l5_observation.py`. Untracked files
  (`audit/l5-m1-v4-audit.md`, `.workshop/`) are not part of that diff.
- Codex was not blind: it could read any file in the repository, including earlier audits.
- Coverage: this run saw the working tree at 66 gate cases, before the F1 fix. It did not see
  `_axis_spread`, the cases added after it (70 in the end), or the G3 to G5 changes.
- Verdict, verbatim: "No actionable regressions were found. All 66 adversarial cases, 10 focused
  tests, and lint checks passed; geometry tests ran in in-process mode."
- Findings: none.

Full raw output follows, unedited.

```text
OpenAI Codex v0.169.0
--------
workdir: D:\10_PROJECTS\cad-engineering\cad-spec-env
model: gpt-6.1-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a21a7d-3610-7002-b563-4559f4ea7e48
--------
user
changes against 'main'
exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-Content C:\\Users\\bgare\\.codex\\skills\\behavioral-verification-review\\SKILL.md; git status --short; git diff --stat ddd4e14601b144db17d17c6b638de99f3b494176; Get-ChildItem -Force -Name; Get-ChildItem -Path .. -Filter AGENTS* -Force" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 367ms:
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
 M CHANGELOG.md
 M CLAUDE.md
 M docs/design/L5-amendments.md
 M environments/cad_spec/cad_spec/l5/observation.py
 M results/l5/m1-observation-suite.md
 M scripts/test_l5_observation.py
?? .workshop/LOG.md
?? .workshop/reviews/
?? audit/l5-m1-v4-audit.md
?? audit/scratch/run1-breps/
?? audit/scratch/run1-perturbations/
?? orca.yaml
?? results/baselines.md
?? results/superseded/
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: in the working copy of 'CHANGELOG.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CLAUDE.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/design/L5-amendments.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'environments/cad_spec/cad_spec/l5/observation.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'results/l5/m1-observation-suite.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'scripts/test_l5_observation.py', LF will be replaced by CRLF the next time Git touches it
 CHANGELOG.md                                     | 24 +++++++++--
 CLAUDE.md                                        | 15 ++++---
 docs/design/L5-amendments.md                     | 55 +++++++++++++++++++++---
 environments/cad_spec/cad_spec/l5/observation.py | 50 ++++++++++++++++++---
 results/l5/m1-observation-suite.md               | 10 ++++-
 scripts/test_l5_observation.py                   | 49 +++++++++++++++++++++
 6 files changed, 181 insertions(+), 22 deletions(-)
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
cad-spec-worker-za_ikael
cad-spec-worker-pv7y3aqd
cad-spec-worker-_ljebd_3
cad-spec-worker-bcswvg03
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

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "git diff ddd4e14601b144db17d17c6b638de99f3b494176; rg --files -g AGENTS.md -g AGENTS.override.md -g CLAUDE.md -g '*config*' .codex environments scripts docs results 2>"'$null; Get-Content CLAUDE.md; Get-Content C:'"\\Users\\bgare\\.codex\\config.toml -ErrorAction SilentlyContinue" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 365ms:
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: in the working copy of 'CHANGELOG.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CLAUDE.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/design/L5-amendments.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'environments/cad_spec/cad_spec/l5/observation.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'results/l5/m1-observation-suite.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'scripts/test_l5_observation.py', LF will be replaced by CRLF the next time Git touches it
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b91f242..b569891 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -5,6 +5,13 @@ Scores are only comparable within one scorer version
 
 ## Unreleased
 
+### Release plan
+- **L5 M1 ships in the next package release, together with verifiers 0.4
+  support** (owner's ruling, 27 November 2026). Until then the package
+  stays at 0.5.0, although `cad_spec/l5/` and the strict measurement in
+  `measure.py` have changed since that release. No scorer version and no
+  recorded verdict changes.
+
 ### Agent working notes (no code or scoring change)
 - **`.workshop/`** (agent-workshop plugin, no code or scoring change): `NOW.md`, six confirmed promises in `PROMISES.md`, and `checks.json` (ruff on each edited file; ruff plus a fast pytest subset, 26 to 28 s, at the end of each turn). `CLAUDE.md` state updated to 26 November 2026.
 
@@ -48,10 +55,19 @@ Scores are only comparable within one scorer version
   raised instead of refusing. A final local verification
   (`audit/l5-m1-v3-audit.md`) found one more: the tilt limit was applied to
   the X and Y components separately. It is now on the angle.
-- **Gate:** `scripts/test_l5_observation.py`, 60 hand-built cases, in CI
-  (`results/l5/m1-observation-suite.md`). Every `ok` case states every
-  variable, and the exact boundary of each rule is pinned (tilt, nested
-  cylinders, supported size, equal diameters).
+- **Fourth review** (`audit/l5-m1-v4-audit.md`, 27 November 2026), after
+  which M1 counts as audited: one hole cut as two stacked halves on either
+  side of the measurement's rounding key was `ok` with n = 3 and is now
+  `out_of_scope`; `centered` uses the straight-line distance from the
+  mean hole centre to the plate centre; the diagonal tilt limit is pinned
+  at 1.05e-12 rad. Deferred: the scope-scan probe point (M3) and two
+  scorer-path defects that fail closed (next scorer version).
+- **Gate:** `scripts/test_l5_observation.py`, 66 hand-built cases, in CI.
+  It writes `results/l5/m1-observation-suite.md`, which is generated and
+  rewritten in place (`results/l5/` is a generated folder, CLAUDE.md
+  rule 3). Every `ok` case states every variable, and the exact boundary
+  of each rule is pinned (tilt, nested cylinders, supported size, equal
+  diameters, centred pattern).
 - One deviation from the design note, recorded for approval: an extra pocket
   or slot is a `form_violation`, not `out_of_scope`.
 
diff --git a/CLAUDE.md b/CLAUDE.md
index f069110..b5955f9 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -25,11 +25,12 @@ piece for RL-environment and evaluation work.
   3 October 2026". Items 1 (scorer 0.5) and 2 (L4 parser baseline) are done.
   Item 3 is being built as L5 v1 (region-graded change orders). Governing
   design and amendments: `docs/design/`. Milestone M1 (observation map,
-  `cad_spec/l5/`) is merged (PR #35, after three review rounds in
-  `audit/l5-m1-*.md`) but not yet counted as audited: five advisory
-  findings of the first review are open and no review ran after the last
-  fix (C1). M2 (contract compiler) starts only after M1 is audited. Do not
-  reopen the architecture of the design note.
+  `cad_spec/l5/`) is merged (PR #35) and counted as audited after a fourth
+  review round (`audit/l5-m1-v4-audit.md`, 27 November 2026). M2
+  (contract compiler) may start. Deferred: the scope-scan probe point
+  (M3) and two scorer-path defects (next scorer version), listed in
+  `docs/design/L5-amendments.md` section 4. Do not reopen the
+  architecture of the design note.
 - Since v0.5.0, merged and unreleased: L5 M1 and the metrology reasoning
   layer (`research/`, `.claude/skills/cad-spec-*`, PR #36). See CHANGELOG
   "Unreleased".
@@ -52,7 +53,9 @@ piece for RL-environment and evaluation work.
    `results/` are records. Never rewrite them. A correction is a dated
    section appended below, with the original text kept. Any change to a
    plan, a budget or an analysis is a dated amendment written before the
-   outcome it could influence.
+   outcome it could influence. One exception (ruled 27 November 2026):
+   `results/l5/` is a generated folder. `scripts/test_l5_observation.py
+   --out` rewrites its files in place, and each file says so in a header.
 4. **Frozen code.** Do not edit `scripts/compare_training.py`,
    `scripts/compare_replication.py`, `scripts/bridge_check.py` or
    `scripts/replication_split.py`. Recorded verdicts are historical: a new
diff --git a/docs/design/L5-amendments.md b/docs/design/L5-amendments.md
index 270f2ba..99a8dee 100644
--- a/docs/design/L5-amendments.md
+++ b/docs/design/L5-amendments.md
@@ -26,7 +26,7 @@ one is frozen and audited.
 
 | Milestone | Builds | Exit gate | Status |
 |---|---|---|---|
-| M1 Observation and form | observation map, form check, tolerance reuse, adversarial suite, off-origin handling, out-of-scope verdict | every hand-built adversarial model gives the expected observation or an explicit refusal | built, awaiting audit |
+| M1 Observation and form | observation map, form check, tolerance reuse, adversarial suite, off-origin handling, out-of-scope verdict | every hand-built adversarial model gives the expected observation or an explicit refusal | audited (fourth review, 27 November 2026, section 3.2) |
 | M2 Contract compiler | Contract A schema, typed order operators, Contract B, exact-rational encoding, subset enumeration of MUS and MCS, `allowed_to_move`, `forced`, witness, compiled-item schema | items reproduce from their semantic state and compile to correct static artifacts | not started |
 | M3 Runtime grader and intent | gates G0 to G5, CQGI parameter interface, change detection, inherited behaviour, sensitivity-filtered probes, structured rejects, accepted-MUS lookup, near-twins | witnesses pass, hardcoded witnesses fail on intent-bearing items, infeasible items accept only minimal conflict sets | not started |
 | M4 Diversity, diagnostics, baselines | code and language renderers, equivalence checks, misconception library, separability, the five baselines, the full per-item checklist | every item passes the generator-side checklist and every diagnostic is separable | not started |
@@ -35,8 +35,9 @@ one is frozen and audited.
 ## 3. M1 record: what the observation map does
 
 Code: `cad_spec/l5/observation.py` (observation version 1, built on scorer
-0.5.0 by name). Gate: `scripts/test_l5_observation.py` (60 cases, in CI).
-Result: `results/l5/m1-observation-suite.md`.
+0.5.0 by name). Gate: `scripts/test_l5_observation.py` (66 cases, in CI).
+Result: `results/l5/m1-observation-suite.md`, generated by the gate and
+rewritten in place on each run (`results/l5/` is a generated folder).
 
 **Four verdicts.** `ok`; `form_violation` (the part has a feature nobody
 asked for); `out_of_scope` (a variable would be a guess); `not_single_solid`.
@@ -62,7 +63,8 @@ of guessing. The scorer does not read those fields.
 |---|---|---|
 | Position | Not a contract variable. A plate moved off the origin measures the same; the bounding-box centre is reported for information | design note 7.2 |
 | Orientation | L along X, W along Y. Turned 90 or 270 degrees about Z, they swap. Turned by any other angle beyond the form tolerance, the form fails (a turn of 1e-10 rad is inside it) | design note 7.2; the form check |
-| What n counts | Recognised Z bores only: open from the bottom face to the top face at the form tolerance, with at least 99% of the cylindrical wall present. A hole that breaks out of a side or overlaps another by a very small amount can therefore still be recognised; rules F1 and F2 remain contract checks. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures |
+| What n counts | Recognised Z bores only: one uninterrupted cylinder, open from the bottom face to the top face at the form tolerance, with at least 99% of the cylindrical wall present. A hole that breaks out of a side or overlaps another by a very small amount can therefore still be recognised; rules F1 and F2 remain contract checks. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures. Design note 7.1 asks for a hole "running through the full thickness"; this row refines it. D and the axis are still read from the exact cylinder, never approximated: 99% is only the threshold for recognising the bore |
+| One hole split across the measurement's grouping | `out_of_scope` when two faces are one cylinder by the map's rule (axes within 1e-7 mm, diameters within 1e-9 mm) but fall into two hole groups of the measurement, which groups by position rounded to 3 decimals and diameter rounded to 4 | found by the fourth review: one hole cut as two stacked halves 8e-8 mm apart around x = 20.0005 was `ok` with n = 3 |
 | px, py | The extent of the hole centres along X and Y. For the four-corner pattern that is the pitch; for any other pattern it is only the extent, and `rectangular` is then False | the design note defines pitch for the family only |
 | Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face. For an accepted axis the two differ by at most (T / 2) x 1e-12: 7e-12 mm for the thickest generated plate (14 mm) | one measurement shared with the scorer |
 | No hole | D, mx, my, px, py are `None`, never zero | a missing variable is not a value |
@@ -72,6 +74,9 @@ of guessing. The scorer does not read those fields.
 | Supported size | `out_of_scope` when any cylindrical face is under 0.01 mm in diameter (exactly 0.01 mm is measured). This comes before the form check, so a fillet under that size is a size refusal, not the `form_violation` of amendment 1 | the probe that tells a hole from a boss cannot classify smaller ones; refusing is honest, reporting n = 0 was not |
 | Failed scope scan | `out_of_scope`, with the reason | it used to raise an exception out of the map |
 | Spline surfaces | `form_violation`, with no hole recognised. A known false rejection kept on purpose (scorer review round 3). The kernel pads a spline bounding box by 2e-7 mm, so L, W and T of such a part are not exact | soundness over coverage |
+| Very thin edge wall | A hole whose wall is 1e-7 mm thick at a side face is a `form_violation` (the form check of scorer 0.5.0 refuses it). At 1e-6 mm and more it is `ok` with an exact margin. A known false rejection, like spline faces; changing it needs a new scorer version | soundness over coverage |
+| centered, symmetric, rectangular | `centered`: the straight-line distance from the mean hole centre to the bounding-box centre is at most the form tolerance, 1e-7 mm (pinned at 0.99e-7 and 1.02e-7). `symmetric` and `rectangular` match hole positions coordinate by coordinate at the same tolerance, so a match may be up to 1.41e-7 mm off in a straight line. The `symmetric` match asks that some hole mirrors each hole, not a one-to-one pairing; that is enough because two holes that survive the scope rules are at least 0.005 mm apart, so no hole can mirror two | owner's ruling (fourth review): a 2D offset is judged by its length, as for the tilt limit |
+| Old measurements | None are stored. A measurement made before the strict fields existed reads `strict` as False, and the map raises an error instead of observing it | a loud refusal, not a migration |
 
 **One deviation from the design note, for the owner's approval.** Section
 7.2 lists "extra pocket or slot" as `out_of_scope`. M1 reports it as
@@ -84,7 +89,11 @@ pocket with large rounded corners can be `out_of_scope` (its corner
 cylinders are nested), and a pocket that cuts into a hole without nesting
 its axis is a `form_violation` whose numbers are diagnostic only. The map
 does not claim to recognise features. Either verdict fails gate G3. The
-external reviewer chose the same verdict.
+first external review chose `form_violation` on one condition: that a
+pocket cutting into a hole is refused by the scope rules. That condition
+does not hold, as stated above. The third review accepted
+`form_violation` as the conservative verdict with this narrowed wording.
+The deviation still awaits the owner's approval.
 
 ### 3.1 External review of M1 (5 October 2026)
 
@@ -119,6 +128,25 @@ tilt example, pockets and the scope rules), which is done.
 | R4 | A cross bore of 0.2 micron was missed: the inward probe crossed it | probe limited to half a radius, an unclear result is an error, and features under 0.01 mm are refused |
 | R5 | A failed scope scan made the map raise instead of refusing | explicit strict marker on the measurement; failures are `out_of_scope` |
 
+### 3.2 Fourth review of M1 (27 November 2026)
+
+Report: `audit/l5-m1-v4-audit.md`. Codex and an independent blind check
+reviewed the C1 fix, the five advisory findings of the first review were
+triaged, and the owner ruled on each. Changes:
+
+- **A hole split across the measurement's grouping is refused** (row
+  above). Adding this case to the gate showed `ok` with n = 3 for one
+  physical hole, through the real answer path.
+- **`centered` uses the straight-line distance** (row above).
+- **The diagonal tilt limit is bracketed to [1.0e-12, 1.05e-12) rad**
+  by a case at 1.05e-12 rad. Before, any threshold below 1.3e-12 passed.
+- **Statements made precise:** what n counts (one uninterrupted
+  cylinder, and how the 99% rule relates to design note 7.1), the pocket
+  deviation, the thin edge wall, old measurements, and the `symmetric`
+  match. Section 4 records the deferred items.
+
+With these changes M1 is counted as audited, and M2 may start.
+
 ## 4. Open for later milestones
 
 - **Family rules F1 and F2 belong to gate G3 (M3).** The map does not
@@ -137,3 +165,20 @@ tilt example, pockets and the scope rules), which is done.
   G3a** (M3). The observation already keeps the two apart.
 - **Latency (M3).** A plate with 100 holes takes about 8 seconds to observe.
   Intent probes multiply that; build and measurement timeouts stay in place.
+- **Scope-scan probe point (M3).** The scan classifies each concave
+  cylinder face with one probe placed at the midpoint of the face's
+  parameter rectangle. On a trimmed face that point can lie off the face.
+  With a tongue of material placed there, four bores tilted by 1e-9 rad
+  became `form_violation` instead of `out_of_scope` (fourth review). This
+  fails closed on every case tried, because a face that fools the probe
+  also fails the form check; that is argued, not proven. The code fix is
+  deferred to M3 by the owner's ruling (27 November 2026).
+- **Scorer path, next scorer version.** Two defects sit in frozen scorer
+  code and wait for a new scorer version. First, `_z_aligned_cylinders` and
+  `_off_axis_bore_count` in `measure.py` compare the X and Y components of
+  an axis separately with `AXIS_TOL` = 1e-6, so a diagonal tilt up to
+  1.41e-6 rad counts as a Z bore there; the scope scan's docstring has the
+  same imprecision. Second, the hole grouping can split one cylinder
+  across a rounding key, so scorer 0.5.0 sees one hole too few and fails
+  a correct part. Both fail closed for the scorer, and the map refuses
+  both cases before it uses those values.
diff --git a/environments/cad_spec/cad_spec/l5/observation.py b/environments/cad_spec/cad_spec/l5/observation.py
index e949aca..30e425a 100644
--- a/environments/cad_spec/cad_spec/l5/observation.py
+++ b/environments/cad_spec/cad_spec/l5/observation.py
@@ -12,7 +12,8 @@ part?", and it gives one of four verdicts with the numbers:
                     or loose geometry they may not describe the plate.
   out_of_scope      a variable cannot be measured without guessing (a stepped
                     hole, a tilted hole, holes of different diameters, a
-                    feature too small to classify). The map refuses loudly
+                    feature too small to classify, one hole split across
+                    the measurement's grouping). The map refuses loudly
                     instead of returning a wrong number.
   not_single_solid  zero or several solids: nothing to measure
 
@@ -41,7 +42,7 @@ from collections.abc import Mapping
 from dataclasses import dataclass, field
 from types import MappingProxyType
 
-from ..measure import FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
+from ..measure import COAXIAL_DP, FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
 from ..rubric import TOLERANCES, form_verdict
 
 OBSERVATION_VERSION = "1"
@@ -56,6 +57,12 @@ EPS_FORM_MM: float = FORM_LINEAR_TOL              # two positions closer than th
 # missing it. The generator's smallest hole is 3 mm.
 MIN_CYLINDER_DIAMETER_MM = 0.01
 
+# The strict measurement groups cylinder faces into holes by axis position
+# rounded to COAXIAL_DP decimals and by diameter rounded to 4 decimals. The 4
+# is a literal in measure._classify_cylinders (no name to import), so it is
+# restated here; the gate case review_hole_split_across_diameter_key pins it.
+_DIAMETER_KEY_DP = 4
+
 OK = "ok"
 FORM_VIOLATION = "form_violation"
 OUT_OF_SCOPE = "out_of_scope"
@@ -71,6 +78,9 @@ class Observation:
 
     `values` (read-only) holds L, W, T (bounding box), n (through holes along
     Z), D, mx, my, px, py, and the booleans rectangular, centered, symmetric.
+    `centered` compares the straight-line distance from the mean hole centre
+    to the bounding-box centre with the form tolerance. `rectangular` and
+    `symmetric` match positions coordinate by coordinate at that tolerance.
     A variable that does not exist (D with no hole) is None. With
     `out_of_scope` only the variables measured before the refusal are present.
     """
@@ -96,6 +106,30 @@ def _same(a: float, b: float) -> bool:
     return abs(a - b) <= EPS_FORM_MM
 
 
+def _same_cylinder(a: tuple[float, float, float], b: tuple[float, float, float]) -> bool:
+    """Two concave Z faces of one cylinder: axes within the form tolerance, diameters within the slack."""
+    (x, y, d), (u, v, e) = a, b
+    return math.hypot(x - u, y - v) <= EPS_FORM_MM and abs(d - e) <= EPS_DIM_MM
+
+
+def _group_key(x: float, y: float, d: float) -> tuple[float, float, float]:
+    """The key under which the strict measurement groups a face into a hole."""
+    return (round(x, COAXIAL_DP), round(y, COAXIAL_DP), round(d, _DIAMETER_KEY_DP))
+
+
+def _split(axes: list[tuple[float, float, float]]) -> bool:
+    """Is one cylinder split across two hole groups of the measurement?
+
+    Two faces of one cylinder (by the rule of _same_cylinder) can lie on
+    either side of a rounding key: axes 8e-8 mm apart around x = 20.0005, or
+    diameters 8e-10 mm apart around 10.00005. The measurement then makes two
+    half-depth holes, neither of which is a through hole, and n would be one
+    short under `ok`. The map refuses instead.
+    """
+    return any(_same_cylinder(a, b) and _group_key(*a) != _group_key(*b)
+               for i, a in enumerate(axes) for b in axes[i + 1:])
+
+
 def _nested(axes: list[tuple[float, float, float]]) -> bool:
     """Do two DIFFERENT concave Z cylinders share one hole position?
 
@@ -106,10 +140,9 @@ def _nested(axes: list[tuple[float, float, float]]) -> bool:
     """
     for i, (x, y, d) in enumerate(axes):
         for u, v, e in axes[i + 1:]:
-            distance = math.hypot(x - u, y - v)
-            if distance <= EPS_FORM_MM and abs(d - e) <= EPS_DIM_MM:
+            if _same_cylinder((x, y, d), (u, v, e)):
                 continue
-            if distance < max(d, e) / 2:
+            if math.hypot(x - u, y - v) < max(d, e) / 2:
                 return True
     return False
 
@@ -139,6 +172,9 @@ def observe(m: Measurements) -> Observation:
     if _nested(m.scope_axes):
         return done(OUT_OF_SCOPE, "two different cylinders at one hole position "
                                   "(counterbore, stepped or offset hole)")
+    if _split(m.scope_axes):
+        return done(OUT_OF_SCOPE, "one cylinder split across two hole groups of the measurement "
+                                  "(faces within the tolerances, on either side of a rounding key)")
     through = [h for h in m.holes if _through(h, m)]
     values["n"] = len(through)
     if through and max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_DIM_MM:
@@ -153,7 +189,9 @@ def observe(m: Measurements) -> Observation:
         corners = [(x, y) for x in (xs[0], xs[-1]) for y in (ys[0], ys[-1])]
         values["rectangular"] = len(through) == 4 and all(
             sum(_same(h.x, x) and _same(h.y, y) for h in through) == 1 for x, y in corners)
-        values["centered"] = (_same(sum(xs) / len(xs), centre[0]) and _same(sum(ys) / len(ys), centre[1]))
+        # Straight-line distance from the mean hole centre to the bounding-box
+        # centre, as for the tilt limit: a 2D offset is judged by its length.
+        values["centered"] = math.hypot(sum(xs) / len(xs) - centre[0], sum(ys) / len(ys) - centre[1]) <= EPS_FORM_MM
         values["symmetric"] = all(
             any(_same(o.x, 2 * centre[0] - h.x) and _same(o.y, h.y) for o in through)
             and any(_same(o.x, h.x) and _same(o.y, 2 * centre[1] - h.y) for o in through)
diff --git a/results/l5/m1-observation-suite.md b/results/l5/m1-observation-suite.md
index 928f95b..508ac51 100644
--- a/results/l5/m1-observation-suite.md
+++ b/results/l5/m1-observation-suite.md
@@ -1,8 +1,10 @@
 # L5 observation map: adversarial suite (milestone M1)
 
+Generated by `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`. Do not edit by hand: rerun the script.
+
 Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported from the scorer.
 
-**60 of 60 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.
+**66 of 66 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.
 
 | Case | Expected verdict | Verdict | Result | Why the case exists |
 |---|---|---|---|---|
@@ -54,6 +56,9 @@ Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported f
 | `boundary_tilt_1e-11_rad_is_refused` | out_of_scope | out_of_scope | pass | ten times the slack |
 | `boundary_diagonal_tilt_1.3e-12_rad_is_refused` | out_of_scope | out_of_scope | pass | third review: each direction component is 9.2e-13, under the slack, but the angle is 1.3e-12 |
 | `boundary_diagonal_tilt_0.9e-12_rad_is_accepted` | ok | ok | pass | the same diagonal tilt inside the slack |
+| `boundary_diagonal_tilt_1.05e-12_rad_is_refused` | out_of_scope | out_of_scope | pass | fourth review: components 7.4e-13, angle 1.05e-12; the diagonal limit is bracketed to [1.0e-12, 1.05e-12) |
+| `boundary_pattern_0.99e-7_off_centre_is_centered` | ok | ok | pass | pattern moved (7e-8, 7e-8): 0.99e-7 from the centre in a straight line, inside the form tolerance. A mirrored hole is 1.4e-7 off, so not symmetric |
+| `boundary_pattern_1.02e-7_off_centre_is_not_centered` | ok | ok | pass | fourth review: 7.2e-8 along each axis, under the tolerance, but 1.02e-7 in a straight line, over it |
 | `boundary_axis_on_the_other_rim` | form_violation | form_violation | pass | two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole |
 | `boundary_axis_inside_the_other_rim` | out_of_scope | out_of_scope | pass | 4.999 mm apart: each axis is inside the other cylinder |
 | `boundary_holes_of_0.009_mm` | out_of_scope | out_of_scope | pass | just under the supported size |
@@ -64,5 +69,8 @@ Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported f
 | `boundary_diameters_5e-10_apart` | ok | ok | pass | inside the dimension slack: one D |
 | `boundary_diameters_written_1e-9_apart` | out_of_scope | out_of_scope | pass | written exactly 1e-9 apart, measured 1.00000008e-9 apart: values are binary doubles, so this is refused |
 | `boundary_diameters_2e-9_apart` | out_of_scope | out_of_scope | pass | outside the slack |
+| `review_hole_split_across_position_key` | out_of_scope | out_of_scope | pass | two halves of one hole, axes 8e-8 apart on either side of x = 20.0005: was `ok` with n = 3 |
+| `review_hole_split_across_diameter_key` | out_of_scope | out_of_scope | pass | two halves of one hole, diameters 8e-10 apart on either side of 10.00005: was `ok` with n = 3 |
+| `review_hole_split_on_one_side_of_the_key` | ok | ok | pass | the same two halves on one side of the key: one hole, measured. The fourth hole is inside the pattern, so mx and px do not depend on which half is read |
 | `two_solids` | not_single_solid | not_single_solid | pass | an unfused second body |
 | `no_result` | build_error | build_error | pass | the answer binds no part: gate G1, not the map |
diff --git a/scripts/test_l5_observation.py b/scripts/test_l5_observation.py
index 79f5f5d..58df949 100644
--- a/scripts/test_l5_observation.py
+++ b/scripts/test_l5_observation.py
@@ -10,6 +10,9 @@ Design note section 7.2, plus the counterexamples of the four scorer review
 rounds. Run it on every change to the map or to the measurement:
 
     python scripts/test_l5_observation.py [--out results/l5/m1-observation-suite.md]
+
+results/l5/ is a generated folder: the result file is rewritten in place by
+this script and carries a header saying so (CLAUDE.md, rule 3).
 """
 
 from __future__ import annotations
@@ -44,6 +47,23 @@ def holes_at(points: str, extra: str = "") -> str:
             + f'.faces(">Z").workplane().pushPoints({points}).hole(10)\n')
 
 
+def shifted(s: float) -> str:
+    """The reference pattern moved by (s, s): its centre is s * sqrt(2) from the plate centre."""
+    return holes_at(f"[(-35+{s!r}, -25+{s!r}), (-35+{s!r}, 25+{s!r}), (35+{s!r}, -25+{s!r}), (35+{s!r}, 25+{s!r})]")
+
+
+def split_hole(lower: tuple[float, float], upper: tuple[float, float], d: float = 10) -> str:
+    """Three corner holes of diameter d, and a fourth hole at y = 25 cut as two half-depth
+    cylinders, (x, diameter) = lower for z in [-2, 0] and upper for z in [0, 2], kept as
+    separate faces (clean=False)."""
+    return (HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
+            f'.pushPoints([(-35, -25), (-35, 25), (35, -25)]).hole({d!r})\n'
+            f'result = result.cut(cq.Workplane("XY").workplane(offset=-3).center({lower[0]!r}, 25)'
+            f'.circle({lower[1] / 2!r}).extrude(3), clean=False)\n'
+            f'result = result.cut(cq.Workplane("XY").center({upper[0]!r}, 25)'
+            f'.circle({upper[1] / 2!r}).extrude(3), clean=False)\n')
+
+
 # name -> (code, expected verdict, expected values (a subset is enough), why this case exists)
 CASES: dict[str, tuple[str, str, dict, str]] = {
     # --- parts the map must measure exactly
@@ -236,6 +256,21 @@ CASES: dict[str, tuple[str, str, dict, str]] = {
                ".rotate((0, 0, 0), (1, 1, 0), 5.156620156177409e-11)\n"
                "    result = result.cut(tool.translate((x, y, 0)))\n",
         "ok", NOMINAL, "the same diagonal tilt inside the slack"),
+    "boundary_diagonal_tilt_1.05e-12_rad_is_refused": (
+        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
+               f"for x, y in {CORNERS}:\n"
+               '    tool = cq.Workplane("XY").circle(5).extrude(8, both=True)'
+               ".rotate((0, 0, 0), (1, 1, 0), 6.016056848873644e-11)\n"
+               "    result = result.cut(tool.translate((x, y, 0)))\n",
+        "out_of_scope", {"L": 100.0, "W": 80.0},
+        "fourth review: components 7.4e-13, angle 1.05e-12; the diagonal limit is bracketed to [1.0e-12, 1.05e-12)"),
+    "boundary_pattern_0.99e-7_off_centre_is_centered": (
+        shifted(0.7e-7), "ok", full(mx=15 - 0.7e-7, my=15 - 0.7e-7, symmetric=False),
+        "pattern moved (7e-8, 7e-8): 0.99e-7 from the centre in a straight line, inside the form tolerance. "
+        "A mirrored hole is 1.4e-7 off, so not symmetric"),
+    "boundary_pattern_1.02e-7_off_centre_is_not_centered": (
+        shifted(0.72e-7), "ok", full(mx=15 - 0.72e-7, my=15 - 0.72e-7, centered=False, symmetric=False),
+        "fourth review: 7.2e-8 along each axis, under the tolerance, but 1.02e-7 in a straight line, over it"),
     "boundary_axis_on_the_other_rim": (
         holes_at("[(-2.5, 0), (2.5, 0)]"), "form_violation", {**ENVELOPE, "n": 0},
         "two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole"),
@@ -272,6 +307,18 @@ CASES: dict[str, tuple[str, str, dict, str]] = {
         holes_at("[(-35, -25), (-35, 25), (35, -25)]")
         + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.000000002)\n',
         "out_of_scope", {**ENVELOPE, "n": 4}, "outside the slack"),
+    # --- found by the fourth review (27 November 2026): one cylinder, two hole groups
+    "review_hole_split_across_position_key": (
+        split_hole((20.00049996, 10), (20.00050004, 10)), "out_of_scope", ENVELOPE,
+        "two halves of one hole, axes 8e-8 apart on either side of x = 20.0005: was `ok` with n = 3"),
+    "review_hole_split_across_diameter_key": (
+        split_hole((20, 10.0000499996), (20, 10.0000500004), d=10.00005), "out_of_scope", ENVELOPE,
+        "two halves of one hole, diameters 8e-10 apart on either side of 10.00005: was `ok` with n = 3"),
+    "review_hole_split_on_one_side_of_the_key": (
+        split_hole((20.0004999, 10), (20.00049998, 10)), "ok",
+        full(rectangular=False, centered=False, symmetric=False),
+        "the same two halves on one side of the key: one hole, measured. The fourth hole is inside the pattern, "
+        "so mx and px do not depend on which half is read"),
     # --- nothing to measure
     "two_solids": (
         BASE + 'result = cq.Compound.makeCompound([result.val(), cq.Solid.makeBox(5, 5, 5, cq.Vector(200, 0, 0))])\n',
@@ -334,6 +381,8 @@ def main() -> int:
         out = Path(args.out)
         out.parent.mkdir(parents=True, exist_ok=True)
         lines = ["# L5 observation map: adversarial suite (milestone M1)", "",
+                 "Generated by `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`. "
+                 "Do not edit by hand: rerun the script.", "",
                  f"Scorer {SCORER_VERSION}. Dimension slack {EPS_DIM_MM:g} mm, form tolerance {EPS_FORM_MM:g} mm, "
                  "both imported from the scorer.", "",
                  f"**{len(CASES) - case_failures} of {len(CASES)} cases as expected.** "
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
  `cad_spec/l5/`) is merged (PR #35) and counted as audited after a fourth
  review round (`audit/l5-m1-v4-audit.md`, 27 November 2026). M2
  (contract compiler) may start. Deferred: the scope-scan probe point
  (M3) and two scorer-path defects (next scorer version), listed in
  `docs/design/L5-amendments.md` section 4. Do not reopen the
  architecture of the design note.
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
   outcome it could influence. One exception (ruled 27 November 2026):
   `results/l5/` is a generated folder. `scripts/test_l5_observation.py
   --out` rewrites its files in place, and each file says so in a header.
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
model = "gpt-6.1-sol"
model_reasoning_effort = "high"
service_tier = "priority"
notify = [ "C:\\Program Files\\WindowsApps\\OpenAI.Codex_26.1120.6357.0_x64__2p2nqsd0c76g0\\app\\resources\\cua_node\\bin\\node_modules\\@oai\\sky\\bin\\windows\\codex-computer-use.exe", "turn-ended" ]
[desktop]
followUpQueueMode = "steer"
conversationDetailMode = "STEPS_PROSE"
ambient-suggestions-enabled = true
avatar-overlay-mascot-width-px = 104
appearanceTheme = "system"
agent-usage-reset-enabled = true

[desktop.appearanceLightChromeTheme]
accent = "#3a83f7"
accentSource = "chatgpt"
contrast = 45
ink = "#1a1c1f"
opaqueWindows = false
surface = "#ffffff"

[desktop.appearanceLightChromeTheme.fonts]

[desktop.appearanceLightChromeTheme.semanticColors]
diffAdded = "#00a240"
diffRemoved = "#ba2623"
skill = "#924ff7"

[desktop.preferred-file-viewers]
'["local","jpeg"]' = "default"
'["local","jpg"]' = "default"

[marketplaces.openai-bundled]
source_type = "local"
source = '\\?\C:\Users\bgare\.codex\.tmp\bundled-marketplaces\openai-bundled'

[marketplaces.openai-primary-runtime]
source_type = "local"
source = '\\?\C:\Users\bgare\.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime'

[plugins."codex-app-tools@openai-bundled"]
enabled = true

[plugins."visualize@openai-bundled"]
enabled = true

[plugins."documents@openai-primary-runtime"]
enabled = true

[plugins."pdf@openai-primary-runtime"]
enabled = true

[plugins."spreadsheets@openai-primary-runtime"]
enabled = true

[plugins."presentations@openai-primary-runtime"]
enabled = true

[plugins."template-creator@openai-primary-runtime"]
enabled = true

[plugins."browser@openai-bundled"]
enabled = true

[plugins."unified-computer-use@openai-bundled"]
enabled = true

[plugins."chrome@openai-bundled"]
enabled = true

[plugins."computer-use@openai-bundled"]
enabled = true

[mcp_servers.node_repl]
args = []
command = 'C:\Program Files\WindowsApps\OpenAI.Codex_26.1120.6357.0_x64__2p2nqsd0c76g0\app\resources\cua_node\bin\node_repl.exe'
env_vars = ["BROWSER_USE_ACCESS_EXECUTOR_ID", "BROWSER_USE_ACCESS_PIPE_PATH", "BROWSER_USE_ACCESS_VERIFYING_IDENTITY", "CODEX_WINDOWS_REGISTERED_CORE"]
startup_timeout_sec = 120

[mcp_servers.node_repl.env]
NODE_REPL_NATIVE_PIPE_CONNECT_TIMEOUT_MS = "1000"
NODE_REPL_NODE_MODULE_DIRS = 'C:\Program Files\WindowsApps\OpenAI.Codex_26.1120.6357.0_x64__2p2nqsd0c76g0\app\resources\cua_node\bin\node_modules'
NODE_REPL_NODE_PATH = 'C:\Program Files\WindowsApps\OpenAI.Codex_26.1120.6357.0_x64__2p2nqsd0c76g0\app\resources\cua_node\bin\node.exe'
NODE_REPL_TRUSTED_CODE_PATHS = 'C:\Users\bgare\.codex;C:\Program Files\WindowsApps\OpenAI.Codex_26.1120.6357.0_x64__2p2nqsd0c76g0\app\resources\cua_node\bin\node_modules'
CODEX_HOME = 'C:\Users\bgare\.codex'
BROWSER_USE_AVAILABLE_BACKENDS = "chrome,iab,mcpapps"
BROWSER_USE_TINYSKY_ENABLED = "1"
NODE_REPL_INSTRUCTIONS_USE_CASE_BROWSER = ""
NODE_REPL_INSTRUCTIONS_USE_CASE_CHROME = ""
BROWSER_USE_CODEX_APP_BUILD_FLAVOR = "prod"
BROWSER_USE_CODEX_APP_VERSION = "26.1120.50957"
NODE_REPL_TRUSTED_SERVICES = '{"browser":"C:/Users/bgare/.codex/plugins/cache/openai-bundled/browser/26.1120.50957/scripts/browser-service.mjs","sky":"@oai/sky/service"}'
SKY_CUA_NATIVE_PIPE = "1"
SKY_CUA_NATIVE_PIPE_DIRECTORY = '\\.\pipe\codex-computer-use-a0183c4f-b8a8-47d7-af55-3f219dfb72ed'
CODEX_CLI_PATH = 'C:\Program Files\WindowsApps\OpenAI.Codex_26.1120.6357.0_x64__2p2nqsd0c76g0\app\resources\codex.exe'
NODE_REPL_UNTRUSTED_ENV_ALLOWLIST = "CODEX_WINDOWS_REGISTERED_CORE"
NODE_REPL_LAZY_TRUSTED_WORKER = "0"
NODE_REPL_INSTRUCTIONS_USE_CASE_COMPUTER_USE = ""

[mcp_servers.blender]
command = 'C:\Users\bgare\.local\bin\uvx.exe'
args = ["blender-mcp"]
startup_timeout_sec = 120

[mcp_servers.blender.env]
PYTHONUTF8 = "1"

[mcp_servers.cadquery]
command = 'C:\Users\bgare\.local\bin\uvx.exe'
args = ["--with", "mcp<2", "cadquery-mcp"]
startup_timeout_sec = 120

[mcp_servers.openscad]
command = 'C:\Users\bgare\.local\bin\uv.exe'
args = ["run", "--with", "git+https://github.com/quellant/openscad-mcp.git", "openscad-mcp"]
startup_timeout_sec = 120

[windows]
sandbox = "elevated"

[projects.'c:\users\bgare\documents\codex\2026-09-07\o']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-07\wha']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-07\i-x20']
trust_level = "trusted"

[projects.'c:\users\bgare\blender tutorial learner']
trust_level = "trusted"

[projects.'c:\users\bgare\blender tutorial learner\cadquery & openscad tool']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-13\bas']
trust_level = "trusted"

[projects.'c:\users\bgare\onedrive\documents\learning game']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-13\u']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-15\au']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-17\referenced-chatgpt-conversation-this-is-an']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-21\referenced-chatgpt-conversation-this-is-an']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-22\realtime-voice-chat']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-23\can']
trust_level = "trusted"

[projects.'c:\users\bgare']
trust_level = "trusted"

[projects.'c:\users\bgare\dev\cad-spec-env']
trust_level = "trusted"

[projects.'c:\users\bgare\documents\codex\2026-09-25\referenced-chatgpt-conversation-this-is-an']
trust_level = "trusted"

[projects.'D:\10_PROJECTS\ai-tooling\blender-tutorial-learner']
trust_level = "trusted"

[projects.'C:\Users\bgare\Blender tutorial learner']
trust_level = "trusted"

[projects.'d:\10_projects\ai-tooling\gn-prompt-lab']
trust_level = "trusted"

[tui]
screen_reader_detection_done = true

[tui.model_availability_nux]
gpt-6-astra = 4
"gpt-6.1-sol" = 4

[hooks.state]

[hooks.state.'C:\Users\bgare\.codex\hooks.json:session_start:0:0']
enabled = true
trusted_hash = "sha256:8da13888513c3c9ddfcf2438b73726e2342ec4b241e33558cf7745091c1b6361"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:session_start:0:0']
enabled = true
trusted_hash = "sha256:8da13888513c3c9ddfcf2438b73726e2342ec4b241e33558cf7745091c1b6361"

[hooks.state.'C:\Users\bgare\.codex\hooks.json:user_prompt_submit:0:0']
enabled = true
trusted_hash = "sha256:4ce247208ffbd7aefa06654d9c4e5acf712e1a3296cf392a3c8183573031e31d"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:user_prompt_submit:0:0']
enabled = true
trusted_hash = "sha256:4ce247208ffbd7aefa06654d9c4e5acf712e1a3296cf392a3c8183573031e31d"

[hooks.state.'C:\Users\bgare\.codex\hooks.json:pre_tool_use:0:0']
enabled = true
trusted_hash = "sha256:8beb0c1cf6ba7c74bda422f7ff3f5e8f5efb1a452e9d97af48ef750019076bf9"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:pre_tool_use:0:0']
enabled = true
trusted_hash = "sha256:8beb0c1cf6ba7c74bda422f7ff3f5e8f5efb1a452e9d97af48ef750019076bf9"

[hooks.state.'C:\Users\bgare\.codex\hooks.json:permission_request:0:0']
enabled = true
trusted_hash = "sha256:f82effd864784e4b0a50ec304eb6fcdeed5750c59b9ef2d5ad76848e20401b81"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:permission_request:0:0']
enabled = true
trusted_hash = "sha256:f82effd864784e4b0a50ec304eb6fcdeed5750c59b9ef2d5ad76848e20401b81"

[hooks.state.'C:\Users\bgare\.codex\hooks.json:post_tool_use:0:0']
enabled = true
trusted_hash = "sha256:b50677f17f057cdc8e80065dbef1ab76d8359c3989c7895d9efdbbdcdfaeed47"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:post_tool_use:0:0']
enabled = true
trusted_hash = "sha256:b50677f17f057cdc8e80065dbef1ab76d8359c3989c7895d9efdbbdcdfaeed47"

[hooks.state.'C:\Users\bgare\.codex\hooks.json:subagent_start:0:0']
enabled = true
trusted_hash = "sha256:19e927d4978612d33e0d7bd14153516ab024b9a0c0c74035e59c0965f42b7f51"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:subagent_start:0:0']
enabled = true
trusted_hash = "sha256:19e927d4978612d33e0d7bd14153516ab024b9a0c0c74035e59c0965f42b7f51"

[hooks.state.'C:\Users\bgare\.codex\hooks.json:subagent_stop:0:0']
enabled = true
trusted_hash = "sha256:5bdaa2d94a4096dfadfb1ac813e77dd6a072582f9309d38910b1753128a10fb7"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:subagent_stop:0:0']
enabled = true
trusted_hash = "sha256:5bdaa2d94a4096dfadfb1ac813e77dd6a072582f9309d38910b1753128a10fb7"

[hooks.state.'C:\Users\bgare\.codex\hooks.json:stop:0:0']
enabled = true
trusted_hash = "sha256:970b49fd405fe38b5f79ad142daa3e3277cf9b84570b04eb7e8858d0e402352b"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:stop:0:0']
enabled = true
trusted_hash = "sha256:970b49fd405fe38b5f79ad142daa3e3277cf9b84570b04eb7e8858d0e402352b"

[hooks.state.'C:\Users\bgare\.codex\hooks.json:interrupt:0:0']
enabled = true
trusted_hash = "sha256:3d75d115b14e4ada52439ce3a28495c332633c63998c0b152d863130d297e426"

[hooks.state.'C:/Users/bgare/.codex/hooks.json:interrupt:0:0']
enabled = true
trusted_hash = "sha256:3d75d115b14e4ada52439ce3a28495c332633c63998c0b152d863130d297e426"

[projects."C:\\Users\\bgare\\.orca\\bots\\blal"]
trust_level = "trusted"

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$paths = '"'D:\\AGENTS.md','D:\\AGENTS.override.md','D:\\10_PROJECTS\\AGENTS.md','D:\\10_PROJECTS\\AGENTS.override.md','D:\\10_PROJECTS\\cad-engineering\\AGENTS.md','D:\\10_PROJECTS\\cad-engineering\\AGENTS.override.md'; foreach ("'$p in $paths) { if (Test-Path $p) { Write-Output $p; Get-Content $p } }; rg --files --hidden -g AGENTS.md -g AGENTS.override.md -g CLAUDE.md -g '"'"'!'"\\.git' -g '"'!'"\\.venv' -g '"'!cad-spec-worker-*'"'; Get-Content .claude/skills/cad-spec-metrology-router/SKILL.md; git diff ddd4e14601b144db17d17c6b638de99f3b494176 -- environments/cad_spec/cad_spec/l5/observation.py scripts/test_l5_observation.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 275ms:
CLAUDE.md
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
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: in the working copy of 'environments/cad_spec/cad_spec/l5/observation.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'scripts/test_l5_observation.py', LF will be replaced by CRLF the next time Git touches it
diff --git a/environments/cad_spec/cad_spec/l5/observation.py b/environments/cad_spec/cad_spec/l5/observation.py
index e949aca..30e425a 100644
--- a/environments/cad_spec/cad_spec/l5/observation.py
+++ b/environments/cad_spec/cad_spec/l5/observation.py
@@ -12,7 +12,8 @@ part?", and it gives one of four verdicts with the numbers:
                     or loose geometry they may not describe the plate.
   out_of_scope      a variable cannot be measured without guessing (a stepped
                     hole, a tilted hole, holes of different diameters, a
-                    feature too small to classify). The map refuses loudly
+                    feature too small to classify, one hole split across
+                    the measurement's grouping). The map refuses loudly
                     instead of returning a wrong number.
   not_single_solid  zero or several solids: nothing to measure
 
@@ -41,7 +42,7 @@ from collections.abc import Mapping
 from dataclasses import dataclass, field
 from types import MappingProxyType
 
-from ..measure import FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
+from ..measure import COAXIAL_DP, FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
 from ..rubric import TOLERANCES, form_verdict
 
 OBSERVATION_VERSION = "1"
@@ -56,6 +57,12 @@ EPS_FORM_MM: float = FORM_LINEAR_TOL              # two positions closer than th
 # missing it. The generator's smallest hole is 3 mm.
 MIN_CYLINDER_DIAMETER_MM = 0.01
 
+# The strict measurement groups cylinder faces into holes by axis position
+# rounded to COAXIAL_DP decimals and by diameter rounded to 4 decimals. The 4
+# is a literal in measure._classify_cylinders (no name to import), so it is
+# restated here; the gate case review_hole_split_across_diameter_key pins it.
+_DIAMETER_KEY_DP = 4
+
 OK = "ok"
 FORM_VIOLATION = "form_violation"
 OUT_OF_SCOPE = "out_of_scope"
@@ -71,6 +78,9 @@ class Observation:
 
     `values` (read-only) holds L, W, T (bounding box), n (through holes along
     Z), D, mx, my, px, py, and the booleans rectangular, centered, symmetric.
+    `centered` compares the straight-line distance from the mean hole centre
+    to the bounding-box centre with the form tolerance. `rectangular` and
+    `symmetric` match positions coordinate by coordinate at that tolerance.
     A variable that does not exist (D with no hole) is None. With
     `out_of_scope` only the variables measured before the refusal are present.
     """
@@ -96,6 +106,30 @@ def _same(a: float, b: float) -> bool:
     return abs(a - b) <= EPS_FORM_MM
 
 
+def _same_cylinder(a: tuple[float, float, float], b: tuple[float, float, float]) -> bool:
+    """Two concave Z faces of one cylinder: axes within the form tolerance, diameters within the slack."""
+    (x, y, d), (u, v, e) = a, b
+    return math.hypot(x - u, y - v) <= EPS_FORM_MM and abs(d - e) <= EPS_DIM_MM
+
+
+def _group_key(x: float, y: float, d: float) -> tuple[float, float, float]:
+    """The key under which the strict measurement groups a face into a hole."""
+    return (round(x, COAXIAL_DP), round(y, COAXIAL_DP), round(d, _DIAMETER_KEY_DP))
+
+
+def _split(axes: list[tuple[float, float, float]]) -> bool:
+    """Is one cylinder split across two hole groups of the measurement?
+
+    Two faces of one cylinder (by the rule of _same_cylinder) can lie on
+    either side of a rounding key: axes 8e-8 mm apart around x = 20.0005, or
+    diameters 8e-10 mm apart around 10.00005. The measurement then makes two
+    half-depth holes, neither of which is a through hole, and n would be one
+    short under `ok`. The map refuses instead.
+    """
+    return any(_same_cylinder(a, b) and _group_key(*a) != _group_key(*b)
+               for i, a in enumerate(axes) for b in axes[i + 1:])
+
+
 def _nested(axes: list[tuple[float, float, float]]) -> bool:
     """Do two DIFFERENT concave Z cylinders share one hole position?
 
@@ -106,10 +140,9 @@ def _nested(axes: list[tuple[float, float, float]]) -> bool:
     """
     for i, (x, y, d) in enumerate(axes):
         for u, v, e in axes[i + 1:]:
-            distance = math.hypot(x - u, y - v)
-            if distance <= EPS_FORM_MM and abs(d - e) <= EPS_DIM_MM:
+            if _same_cylinder((x, y, d), (u, v, e)):
                 continue
-            if distance < max(d, e) / 2:
+            if math.hypot(x - u, y - v) < max(d, e) / 2:
                 return True
     return False
 
@@ -139,6 +172,9 @@ def observe(m: Measurements) -> Observation:
     if _nested(m.scope_axes):
         return done(OUT_OF_SCOPE, "two different cylinders at one hole position "
                                   "(counterbore, stepped or offset hole)")
+    if _split(m.scope_axes):
+        return done(OUT_OF_SCOPE, "one cylinder split across two hole groups of the measurement "
+                                  "(faces within the tolerances, on either side of a rounding key)")
     through = [h for h in m.holes if _through(h, m)]
     values["n"] = len(through)
     if through and max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_DIM_MM:
@@ -153,7 +189,9 @@ def observe(m: Measurements) -> Observation:
         corners = [(x, y) for x in (xs[0], xs[-1]) for y in (ys[0], ys[-1])]
         values["rectangular"] = len(through) == 4 and all(
             sum(_same(h.x, x) and _same(h.y, y) for h in through) == 1 for x, y in corners)
-        values["centered"] = (_same(sum(xs) / len(xs), centre[0]) and _same(sum(ys) / len(ys), centre[1]))
+        # Straight-line distance from the mean hole centre to the bounding-box
+        # centre, as for the tilt limit: a 2D offset is judged by its length.
+        values["centered"] = math.hypot(sum(xs) / len(xs) - centre[0], sum(ys) / len(ys) - centre[1]) <= EPS_FORM_MM
         values["symmetric"] = all(
             any(_same(o.x, 2 * centre[0] - h.x) and _same(o.y, h.y) for o in through)
             and any(_same(o.x, h.x) and _same(o.y, 2 * centre[1] - h.y) for o in through)
diff --git a/scripts/test_l5_observation.py b/scripts/test_l5_observation.py
index 79f5f5d..58df949 100644
--- a/scripts/test_l5_observation.py
+++ b/scripts/test_l5_observation.py
@@ -10,6 +10,9 @@ Design note section 7.2, plus the counterexamples of the four scorer review
 rounds. Run it on every change to the map or to the measurement:
 
     python scripts/test_l5_observation.py [--out results/l5/m1-observation-suite.md]
+
+results/l5/ is a generated folder: the result file is rewritten in place by
+this script and carries a header saying so (CLAUDE.md, rule 3).
 """
 
 from __future__ import annotations
@@ -44,6 +47,23 @@ def holes_at(points: str, extra: str = "") -> str:
             + f'.faces(">Z").workplane().pushPoints({points}).hole(10)\n')
 
 
+def shifted(s: float) -> str:
+    """The reference pattern moved by (s, s): its centre is s * sqrt(2) from the plate centre."""
+    return holes_at(f"[(-35+{s!r}, -25+{s!r}), (-35+{s!r}, 25+{s!r}), (35+{s!r}, -25+{s!r}), (35+{s!r}, 25+{s!r})]")
+
+
+def split_hole(lower: tuple[float, float], upper: tuple[float, float], d: float = 10) -> str:
+    """Three corner holes of diameter d, and a fourth hole at y = 25 cut as two half-depth
+    cylinders, (x, diameter) = lower for z in [-2, 0] and upper for z in [0, 2], kept as
+    separate faces (clean=False)."""
+    return (HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
+            f'.pushPoints([(-35, -25), (-35, 25), (35, -25)]).hole({d!r})\n'
+            f'result = result.cut(cq.Workplane("XY").workplane(offset=-3).center({lower[0]!r}, 25)'
+            f'.circle({lower[1] / 2!r}).extrude(3), clean=False)\n'
+            f'result = result.cut(cq.Workplane("XY").center({upper[0]!r}, 25)'
+            f'.circle({upper[1] / 2!r}).extrude(3), clean=False)\n')
+
+
 # name -> (code, expected verdict, expected values (a subset is enough), why this case exists)
 CASES: dict[str, tuple[str, str, dict, str]] = {
     # --- parts the map must measure exactly
@@ -236,6 +256,21 @@ CASES: dict[str, tuple[str, str, dict, str]] = {
                ".rotate((0, 0, 0), (1, 1, 0), 5.156620156177409e-11)\n"
                "    result = result.cut(tool.translate((x, y, 0)))\n",
         "ok", NOMINAL, "the same diagonal tilt inside the slack"),
+    "boundary_diagonal_tilt_1.05e-12_rad_is_refused": (
+        HEAD + 'result = cq.Workplane("XY").box(100, 80, 4)\n'
+               f"for x, y in {CORNERS}:\n"
+               '    tool = cq.Workplane("XY").circle(5).extrude(8, both=True)'
+               ".rotate((0, 0, 0), (1, 1, 0), 6.016056848873644e-11)\n"
+               "    result = result.cut(tool.translate((x, y, 0)))\n",
+        "out_of_scope", {"L": 100.0, "W": 80.0},
+        "fourth review: components 7.4e-13, angle 1.05e-12; the diagonal limit is bracketed to [1.0e-12, 1.05e-12)"),
+    "boundary_pattern_0.99e-7_off_centre_is_centered": (
+        shifted(0.7e-7), "ok", full(mx=15 - 0.7e-7, my=15 - 0.7e-7, symmetric=False),
+        "pattern moved (7e-8, 7e-8): 0.99e-7 from the centre in a straight line, inside the form tolerance. "
+        "A mirrored hole is 1.4e-7 off, so not symmetric"),
+    "boundary_pattern_1.02e-7_off_centre_is_not_centered": (
+        shifted(0.72e-7), "ok", full(mx=15 - 0.72e-7, my=15 - 0.72e-7, centered=False, symmetric=False),
+        "fourth review: 7.2e-8 along each axis, under the tolerance, but 1.02e-7 in a straight line, over it"),
     "boundary_axis_on_the_other_rim": (
         holes_at("[(-2.5, 0), (2.5, 0)]"), "form_violation", {**ENVELOPE, "n": 0},
         "two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole"),
@@ -272,6 +307,18 @@ CASES: dict[str, tuple[str, str, dict, str]] = {
         holes_at("[(-35, -25), (-35, 25), (35, -25)]")
         + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.000000002)\n',
         "out_of_scope", {**ENVELOPE, "n": 4}, "outside the slack"),
+    # --- found by the fourth review (27 November 2026): one cylinder, two hole groups
+    "review_hole_split_across_position_key": (
+        split_hole((20.00049996, 10), (20.00050004, 10)), "out_of_scope", ENVELOPE,
+        "two halves of one hole, axes 8e-8 apart on either side of x = 20.0005: was `ok` with n = 3"),
+    "review_hole_split_across_diameter_key": (
+        split_hole((20, 10.0000499996), (20, 10.0000500004), d=10.00005), "out_of_scope", ENVELOPE,
+        "two halves of one hole, diameters 8e-10 apart on either side of 10.00005: was `ok` with n = 3"),
+    "review_hole_split_on_one_side_of_the_key": (
+        split_hole((20.0004999, 10), (20.00049998, 10)), "ok",
+        full(rectangular=False, centered=False, symmetric=False),
+        "the same two halves on one side of the key: one hole, measured. The fourth hole is inside the pattern, "
+        "so mx and px do not depend on which half is read"),
     # --- nothing to measure
     "two_solids": (
         BASE + 'result = cq.Compound.makeCompound([result.val(), cq.Solid.makeBox(5, 5, 5, cq.Vector(200, 0, 0))])\n',
@@ -334,6 +381,8 @@ def main() -> int:
         out = Path(args.out)
         out.parent.mkdir(parents=True, exist_ok=True)
         lines = ["# L5 observation map: adversarial suite (milestone M1)", "",
+                 "Generated by `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`. "
+                 "Do not edit by hand: rerun the script.", "",
                  f"Scorer {SCORER_VERSION}. Dimension slack {EPS_DIM_MM:g} mm, form tolerance {EPS_FORM_MM:g} mm, "
                  "both imported from the scorer.", "",
                  f"**{len(CASES) - case_failures} of {len(CASES)} cases as expected.** "

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$skills = '"'cad-spec-geometric-observation','cad-spec-uncertainty-and-error','cad-spec-conformity-decision','cad-spec-datum-gdt-reasoning','cad-spec-numerical-validation'; foreach ("'$s in $skills) { Get-Content ".claude/skills/$s/SKILL.md" }; Get-Content C:'"\\Users\\bgare\\.codex\\skills\\behavioral-verification-review\\references\\source-notes.md" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 232ms:
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

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-Content environments/cad_spec/cad_spec/l5/observation.py; rg -n 'COAXIAL_DP|scope_axes|def _classify_cylinders|def _scope|def _z_aligned|def build_and_measure|FORM_LINEAR_TOL' environments/cad_spec/cad_spec/measure.py; Get-Content scripts/test_l5_observation.py | Select-Object -Skip 325; Get-Content .claude/skills/cad-spec-numerical-validation/artefact-ladder.md; Get-Content environments/cad_spec/pyproject.toml; Get-ChildItem .venv -Name" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 289ms:
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
                    feature too small to classify, one hole split across
                    the measurement's grouping). The map refuses loudly
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

from ..measure import COAXIAL_DP, FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
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

# The strict measurement groups cylinder faces into holes by axis position
# rounded to COAXIAL_DP decimals and by diameter rounded to 4 decimals. The 4
# is a literal in measure._classify_cylinders (no name to import), so it is
# restated here; the gate case review_hole_split_across_diameter_key pins it.
_DIAMETER_KEY_DP = 4

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
    `centered` compares the straight-line distance from the mean hole centre
    to the bounding-box centre with the form tolerance. `rectangular` and
    `symmetric` match positions coordinate by coordinate at that tolerance.
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


def _same_cylinder(a: tuple[float, float, float], b: tuple[float, float, float]) -> bool:
    """Two concave Z faces of one cylinder: axes within the form tolerance, diameters within the slack."""
    (x, y, d), (u, v, e) = a, b
    return math.hypot(x - u, y - v) <= EPS_FORM_MM and abs(d - e) <= EPS_DIM_MM


def _group_key(x: float, y: float, d: float) -> tuple[float, float, float]:
    """The key under which the strict measurement groups a face into a hole."""
    return (round(x, COAXIAL_DP), round(y, COAXIAL_DP), round(d, _DIAMETER_KEY_DP))


def _split(axes: list[tuple[float, float, float]]) -> bool:
    """Is one cylinder split across two hole groups of the measurement?

    Two faces of one cylinder (by the rule of _same_cylinder) can lie on
    either side of a rounding key: axes 8e-8 mm apart around x = 20.0005, or
    diameters 8e-10 mm apart around 10.00005. The measurement then makes two
    half-depth holes, neither of which is a through hole, and n would be one
    short under `ok`. The map refuses instead.
    """
    return any(_same_cylinder(a, b) and _group_key(*a) != _group_key(*b)
               for i, a in enumerate(axes) for b in axes[i + 1:])


def _nested(axes: list[tuple[float, float, float]]) -> bool:
    """Do two DIFFERENT concave Z cylinders share one hole position?

    Two faces of the same cylinder (same axis, same diameter) are one
    cylinder. Otherwise, when the axis of one lies inside the other, they form
    a counterbore, a stepped hole or an offset step: D is not one number.
    Two separate holes that merely overlap are not nested (a form matter).
    """
    for i, (x, y, d) in enumerate(axes):
        for u, v, e in axes[i + 1:]:
            if _same_cylinder((x, y, d), (u, v, e)):
                continue
            if math.hypot(x - u, y - v) < max(d, e) / 2:
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
    if _split(m.scope_axes):
        return done(OUT_OF_SCOPE, "one cylinder split across two hole groups of the measurement "
                                  "(faces within the tolerances, on either side of a rounding key)")
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
        # Straight-line distance from the mean hole centre to the bounding-box
        # centre, as for the tilt limit: a 2D offset is judged by its length.
        values["centered"] = math.hypot(sum(xs) / len(xs) - centre[0], sum(ys) / len(ys) - centre[1]) <= EPS_FORM_MM
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
84:COAXIAL_DP = 3
123:FORM_LINEAR_TOL = 1e-7    # mm
301:    boundary_consistent: bool | None = None  # still a valid solid with all tolerances at FORM_LINEAR_TOL
307:    scope_axes: list[tuple[float, float, float]] | None = None  # every concave Z cylinder face: x, y, raw diameter
516:            if not any(all(abs(level - edge) <= FORM_LINEAR_TOL for level in levels)
534:                           + max(abs(radius - h.diameter / 2), abs(section - h.diameter / 2)) <= FORM_LINEAR_TOL
551:def _scope_scan(solid: Any) -> tuple[int, float | None]:
608:    is repeated on a copy whose tolerances are all forced to FORM_LINEAR_TOL.
617:    ShapeFix_ShapeTolerance().LimitTolerance(copy, FORM_LINEAR_TOL, FORM_LINEAR_TOL)
621:def _z_aligned_cylinders(solid: Any, *, z_ref: float | None = None) -> list[tuple[float, float, float, Any]]:
692:            key = (*(round(c, COAXIAL_DP) for c in (dx, dy, dz, *base)), round(2 * r, 4))
719:def _classify_cylinders(solid: Any, *, strict: bool = False, z_ref: float | None = None,
720:                        scope_axes: list[tuple[float, float, float]] | None = None,
761:        if scope_axes is not None:
762:            scope_axes.append((cx, cy, 2 * radius))  # before any rounding or grouping
763:        key = (round(cx, COAXIAL_DP), round(cy, COAXIAL_DP))
912:    scope_axes: list[tuple[float, float, float]] | None = [] if strict else None
914:                                         scope_axes=scope_axes)
962:        scope_axes=scope_axes,
1391:def build_and_measure(completion: str, *, strict: bool = False) -> Measurements:
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
                 "Generated by `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`. "
                 "Do not edit by hand: rerun the script.", "",
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
Include
Lib
Scripts
share
pyvenv.cfg

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-Content environments/cad_spec/cad_spec/measure.py | Select-Object -Skip 615 -First 210; Get-Content environments/cad_spec/cad_spec/measure.py | Select-Object -Skip 1370 -First 100; Get-Content scripts/test_l5_observation.py -First 50; Get-Content .github/workflows/ci.yml | Select-String 'observation' -Context 3,3; Get-Content audit/l5-m1-v4-audit.md -First 180" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 317ms:
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
        if scope_axes is not None:
            scope_axes.append((cx, cy, 2 * radius))  # before any rounding or grouping
        key = (round(cx, COAXIAL_DP), round(cy, COAXIAL_DP))
        diameter = round(2 * radius, 4)
        raw.setdefault((key, diameter), (2 * radius, cx, cy))
        area_acc, intervals = features.setdefault(key, {}).setdefault(diameter, ([0.0], []))
        area_acc[0] += face.Area()
        intervals.append((fbb.zmin, fbb.zmax))

    holes: list[Hole] = []
    partial: list[PartialBore] = []
    for (x, y), diameters in sorted(features.items()):
        for diameter, (area_acc, intervals) in sorted(diameters.items()):
            spans = _merge_intervals(intervals)
            covered = sum(hi - lo for lo, hi in spans)
            if covered <= 0:
                continue
            coverage = area_acc[0] / (math.pi * diameter * covered)
            if coverage < AREA_COMPLETENESS_MIN:
                if coverage >= PARTIAL_REPORT_MIN:
                    partial.append(PartialBore(diameter, round(x, 4), round(y, 4), round(coverage, 4)))
                continue  # partial arc (fillet, breakout), not a closed bore
            raw_d, raw_x, raw_y = raw[((x, y), diameter)]
            holes.append(Hole(
                diameter=raw_d if strict else diameter,
                x=raw_x if strict else round(x, 4),
                y=raw_y if strict else round(y, 4),
                depth=covered if strict else round(covered, 4),
                z_min=spans[0][0] if strict else round(spans[0][0], 4),
                z_max=spans[-1][1] if strict else round(spans[-1][1], 4),
                segments=len(spans),
            ))
    return holes, partial


def _extract_holes(solid: Any) -> list[Hole]:
    """Closed internal bores only (kept for callers of the 0.2 API)."""
    return _classify_cylinders(solid)[0]


def _count(shape: Any, kind: Any, avoid: Any = None) -> int:
    from OCP.TopExp import TopExp_Explorer

    explorer = TopExp_Explorer(shape, kind) if avoid is None else TopExp_Explorer(shape, kind, avoid)
    n = 0
    while explorer.More():
        n += 1
        explorer.Next()
    return n


def _bore_is_open(solid: Any, hole: Hole, z_min: float, z_max: float) -> bool:
    """Does a rod along the bore axis, through the whole stock, meet no material?"""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepGProp import BRepGProp
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.GProp import GProp_GProps

    radius = hole.diameter / 2 * OPEN_PROBE_RADIUS_FRACTION
    axis = gp_Ax2(gp_Pnt(hole.x, hole.y, z_min - 1.0), gp_Dir(0, 0, 1))
    rod = BRepPrimAPI_MakeCylinder(axis, radius, (z_max - z_min) + 2.0).Shape()
    common = BRepAlgoAPI_Common(solid.wrapped, rod)
    common.Build()
    if not common.IsDone():
    if _inproc_requested():
        return {"mode": "inproc", "isolated": False}
    mode = _sandbox_mode()
    info: dict[str, Any] = {
        "mode": mode,
        "exec_timeout_s": _exec_timeout(),
        "per_rollout_process": mode == "fork",
        "state_isolated": mode == "fork",
        "env_scrubbed": mode == "fork",
        # Where geometry is measured: from BREP bytes in the trusted worker
        # (fork) or in the same process that ran the model code (reuse).
        "measured_in": "trusted worker" if mode == "fork" else "rollout process",
    }
    if mode == "fork":
        # Requested limits. Address-space limits apply on Linux only; the
        # namespace (no-network) step is best effort and not verified here.
        info["mem_limit_mb_requested"] = _mem_limit_mb()
    return info


def build_and_measure(completion: str, *, strict: bool = False) -> Measurements:
    """Extract code, run it isolated, measure the result.

    Raises BuildError when the model's code does not yield a part (a model
    failure), ScorerUnavailableError when the scorer cannot run at all (never a
    score).
    """
    code = extract_code(completion)
    if _inproc_requested():
        require_cadquery()
        return _measure_code(code, strict=strict)
    try:
        try:
            return _get_worker().call(code, strict=strict)
        except _WorkerLostError:
            shutdown_worker()  # one retry on a fresh worker
            try:
                return _get_worker().call(code, strict=strict)
            except _WorkerLostError as exc:
                raise ScorerUnavailableError(f"scoring worker could not be restarted: {exc}") from exc
    except (BuildError, ScorerUnavailableError):
        raise
    except Exception as exc:  # anything else means the worker is unwell
        shutdown_worker()
        raise BuildError(f"isolated scorer failed: {type(exc).__name__}: {exc}") from exc
#!/usr/bin/env python3
"""Adversarial suite for the L5 observation map (milestone M1 exit gate).

Each case is a hand-built model with the outcome a careful engineer expects:
the verdict (ok, form_violation, out_of_scope, not_single_solid, build_error)
and, where the part is measurable, the contract variables. The map passes the
gate only if every case gives exactly that.

Design note section 7.2, plus the counterexamples of the four scorer review
rounds. Run it on every change to the map or to the measurement:

    python scripts/test_l5_observation.py [--out results/l5/m1-observation-suite.md]

results/l5/ is a generated folder: the result file is rewritten in place by
this script and carries a header saying so (CLAUDE.md, rule 3).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

HEAD = "import cadquery as cq\n"
CORNERS = "[(-35, -25), (-35, 25), (35, -25), (35, 25)]"
# The reference part: 100 x 80 x 4 plate, four 10 mm through holes, 15 mm from the side faces.
BASE = HEAD + f'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane().pushPoints({CORNERS}).hole(10)\n'
NOMINAL = {"L": 100.0, "W": 80.0, "T": 4.0, "n": 4, "D": 10.0, "mx": 15.0, "my": 15.0, "px": 70.0, "py": 50.0,
           "rectangular": True, "centered": True, "symmetric": True}
ENVELOPE = {"L": 100.0, "W": 80.0, "T": 4.0}
NO_HOLES = {**ENVELOPE, "n": 0, "D": None, "mx": None, "my": None, "px": None, "py": None,
            "rectangular": False, "centered": False, "symmetric": False}
ALL_KEYS = set(NOMINAL)


def full(**changed) -> dict:
    """The reference values with some of them changed: a complete expectation."""
    return {**NOMINAL, **changed}



def holes_at(points: str, extra: str = "") -> str:
    return (HEAD + f'result = cq.Workplane("XY").box(100, 80, 4){extra}'
            + f'.faces(">Z").workplane().pushPoints({points}).hole(10)\n')


def shifted(s: float) -> str:

        - name: L4 edit parser self-test (parser-edit provider, refusals, fallback)
          working-directory: .
          run: python scripts/test_parser_edit.py
>       - name: L5 observation map, adversarial suite (milestone M1 gate)
          working-directory: .
>         run: python scripts/test_l5_observation.py
        - name: Scoring gate with the system GL libraries (reference, L4 failure, full rollout, 64 at once)
          working-directory: .
          run: python scripts/gl_fallback_check.py --expect system --system-gl-note present --out /tmp/gl/system-gl
# L5 M1 audit, round 4: review of the C1 fix and triage of the open advisory findings

**Status: DRAFT, 27 November 2026.** This is a triage record written during
a session on branch `fix/l5-m1-audit` (from `main` at `ddd4e14`). Unlike
the three earlier files in this folder, it is not an external audit by a
separate agent. It records two reviews of commit `4e26d30` (one Codex, one
fresh-context Claude agent), a check of every finding they raised, and a
proposed action for the five advisory findings still open from the first
review. No code, test, registered record or earlier audit file was changed
in this round. Nothing was staged or committed.

## 1. Scope and inputs

- **Commit reviewed:** `4e26d30` "fix(l5): tilt limit on the angle, not on
  its components; narrow three statements" (C1 and C2 of
  `audit/l5-m1-v3-audit.md`). Between `4e26d30` and `ddd4e14`, `git diff
  --stat` over `environments/cad_spec`, `scripts/test_l5_observation.py`,
  `docs/design`, `results/l5` and `CHANGELOG.md` shows only 16 added
  CHANGELOG lines (the `.workshop/` and research entries). The reviewed code,
  gate and documents are as committed.
- **Sources for the advisory findings:** `audit/l5-m1-audit.md` (first
  review), `audit/l5-m1-v2-audit.md`, `audit/l5-m1-v3-audit.md`,
  `docs/design/L5-amendments.md`, `.workshop/LOG.md`.
- **Environment:** Windows 11, Git Bash, repo `.venv` (Python 3.12.10,
  CadQuery 2.8.0), scorer in `reuse` mode. Linux `fork` mode was not run.
- **Domain:** exact_brep_analytic.

```text
Skills consulted:
- cad-spec-metrology-router: the task reviews the L5 observation map and its gate.
- cad-spec-geometric-observation: the commit changes a scope rule of the map
  (tilt refusal); A1, A2, A3 are about observation operators.
- cad-spec-uncertainty-and-error: STRICT_AXIS_SLACK and FORM_LINEAR_TOL are
  numerical slack and kernel tolerance; A4 is a kernel-tolerance refusal.
- cad-spec-datum-gdt-reasoning: centered and symmetric are frame_bound
  predicates read along the declared axes (A3).
- cad-spec-numerical-validation: the gate cases and every reproduction here.
- cad-spec-conformity-decision: whether a defect can turn into a false `ok`
  decides between "fix now" and "document".
Relevant principles:
- Refusal over guessing (FP07): A1 is judged by whether a fooled probe can
  produce a wrong number under `ok`. It cannot in the reproduced case
  (section 4, A1), so A1 is classed as a refusal-reason defect, not a
  soundness defect.
- P17 / P19: centered and symmetric are frame_bound and read along the
  declared X and Y axes. That is why the per-axis comparison of A3 is
  proposed as the documented rule, rather than a Euclidean one.
- P30 (false pass costs more than false rejection): A4 (1e-7 mm ligament
  refused) is kept as a known false rejection, like spline faces, instead
  of relaxing R9.
- P31 (truth from construction): every expected value in section 4 was
  written from the construction parameters before the run. The diagonal
  angles of the new gate cases were derived by hand (Rodrigues rotation
  about (1,1,0)/sqrt(2): each component is sin(theta)/sqrt(2)) before the
  kernel values were read.
- Numerical-validation boundary triplets: the diagonal boundary has one case
  on each side but neither is tight. Hence B3 is confirmed.
- No field or sentence in this record calls numerical slack an
  "uncertainty".
```

## 2. Reviews run

| Review | Command or brief | Wall time | Result | Saved output |
|---|---|---:|---|---|
| Codex | `codex review --commit 4e26d30 -c 'sandbox_mode="read-only"' -c 'approval_policy="never"'` (codex-cli 0.169.0, reasoning effort high) | 132 s | No findings. Ran the gate (60/60), the L5 pytest file (10), test_rubric_050 (81/81), test_rubric (37/37) | `.workshop/reviews/codex-4e26d30.md` |
| Blind checker | agent-workshop:blind-checker, given only the diff without `audit/` paths, the design note and amendments as the spec, and the touched sources; forbidden to open `audit/` or `.workshop/` | 565 s | Verdict SHIP for the code; findings B1 to B6 (one should-fix, two advisory, three notes) | `.workshop/reviews/blind-4e26d30.md` |

Disclosures. Codex was not restricted from reading earlier audits; the
commit's own diff contains `audit/l5-m1-v2-audit.md`. The blind checker
received a checklist of questions and a one-paragraph statement of what the
commit claims, including the old per-component condition. It received no
audit file and no view of the triage author. It was not fully blind to
earlier reviews: the diff it was given still carries their summaries (the
new section 3.1 paragraph of the amendments, the CHANGELOG entry, and the
gate's reason string "third review: ...").

The two saved review files live under `.workshop/reviews/`, which is
untracked. They must be committed with this file, or copied next to it, for
the record to be complete.

## 3. Verification run in this round (not taken from either reviewer)

| Check | Result |
|---|---|
| `python scripts/test_l5_observation.py` | 60/60, exit 0, 10 s. Both diagonal cases present and passing |
| `pytest -q tests/test_l5_observation.py` (package) | 10 passed |
| `python scripts/test_rubric_050.py` | 81/81 |
| `python scripts/test_rubric.py` | 37/37 |
| `python scripts/check_release.py` | all document links resolve (at HEAD) |
| grep of `rubric.py` and `environment.py` for `off_axis_concave`, `scope_axes`, `min_cylinder_diameter`, `scope_error`, `_scope_scan` | no hit (exit 1): the scope scan feeds the L5 map only |
| Hand derivation of the gate angles | 7.448451336700702e-11 deg = 1.3000e-12 rad; 5.156620156177409e-11 deg = 9.000e-13 rad. Kernel then read dX = -dY = 9.1924e-13 (hypot 1.3000e-12, refused) and 6.3640e-13 (hypot 9.0e-13, accepted) |
| Grep for per-component axis checks in the package | `measure.py:639` and `measure.py:674` (legacy `AXIS_TOL = 1e-6`, scored code); `measure.py:583` is the only L5 one and is now on the angle |
| `git status --short`, `git diff --stat` after all runs | no tracked change |

Scratch reproductions: `advisory_repro.py`, `advisory_repro2.py` and their
`.out` files in the session scratchpad
(`C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/`).
They are not part of the repository; Appendix A reproduces their constructions and raw output.

## 4. Findings and verdicts

Verdicts: **confirmed** (the claim holds, with evidence), **rejected** (the
claim does not hold or is not a defect, with evidence), **unclear** (the
facts are confirmed but whether they are a defect is a ruling for the
owner).

### 4.1 Findings of the two reviews

| ID | Source | Finding | Verdict | Evidence | Proposed action |
|---|---|---|---|---|---|
| X0 | Codex | No actionable finding; the angle check is correct | confirmed (agree) | Section 3: gate 60/60, kernel components and hypot as derived, scorer suites unchanged | None |
| B1 | Blind | The deviation paragraph of the amendments now reports the first reviewer's agreement as unconditional ("The external reviewer chose the same verdict"), while the condition that reviewer set (a pocket intersecting a bore should be `out_of_scope`) is stated not to hold | confirmed | `git diff 4e26d30^ 4e26d30 -- docs/design/L5-amendments.md` removes "with that condition". First review: `audit/l5-m1-audit.md:6139` ("It is conditional: a pocket intersecting a bore ... should be out_of_scope"). The third review's own proposed diff kept "with that condition" after deleting the condition (`audit/l5-m1-v3-audit.md`, C2 proposed diff), and its opinion was "keep these conservative verdicts for M1 and correct the narrative". So the commit's narrative is now wrong in the other direction | Fix now, document only: rewrite the last sentence to say the first reviewer's condition does not hold, that the third review accepted `form_violation` for an intersecting pocket as conservative (both fail G3), and that the deviation still awaits the owner. File: `docs/design/L5-amendments.md` (not a registered record under rule 3) |
| B2a | Blind | `results/l5/m1-observation-suite.md` is rewritten in place by every gate run with `--out`, against the literal rule 3 | unclear | The hunk in `4e26d30` changes "58 of 58" to "60 of 60" and adds two rows (`git diff 4e26d30^ 4e26d30 -- results/l5/m1-observation-suite.md`). The same file was regenerated in `08cc812`, `b9386f9`, `9c19215`. It is generated gate output, not a pre-registered result, but it sits under `results/` | Ruling for Bilal: either declare `results/l5/` a regenerated artefact folder (one sentence in the amendments and in CLAUDE.md rule 3), or make future gate runs append dated sections. This ruling decides how B3 is applied |
| B2b | Blind | `measure.py` changed while the package version stays 0.5.0, against the literal rule 5 | confirmed (fact); no scoring impact | `environments/cad_spec/pyproject.toml:5` `version = "0.5.0"`; the M1 entry is under `CHANGELOG.md` "Unreleased" (line 6, heading at line 24). No scorer field reads the scope scan (grep above); 81/81 and 37/37 unchanged | Ruling for Bilal. Proposed: no action now; release M1 as a package version bump (with the observation map) before any recorded L5 output depends on it |
| B3 | Blind | The diagonal tilt boundary is not tight: any threshold in [1.0e-12, 1.3e-12) passes all tilt cases, so "both sides pinned" and "exact boundary" overstate it. The single-axis 1e-12 case sits on exact floating-point equality | confirmed | Arithmetic on the gate's tilt cases (`scripts/test_l5_observation.py:210-238`): single-axis 1e-12 accepted, 1e-11 refused, diagonal 0.9e-12 accepted, 1.3e-12 refused. A mutant `hypot <= 1.25e-12` passes all four. `sin(1e-12) == 1e-12` in double. The equality case predates `4e26d30` | Fix now (gate only, `scripts/`): add a diagonal case at 1.05e-12 rad (components 7.42e-13, refused), angle in degrees derived by hand. Correct "exact boundary" in the amendments. Applying it regenerates the `results/l5` file, so it waits for the B2a ruling |
| B4 | Blind | The same per-component defect class remains in the legacy detectors (`AXIS_TOL = 1e-6` on X and Y separately), and the `_scope_scan` docstring says "accepts tilts up to 1e-6 rad" | confirmed (note); no L5 effect | `measure.py:639`, `measure.py:674`, docstring at `measure.py:558`. L5: `observation.py:137` refuses on `off_axis_concave` before any hole is used (`observation.py:142`), and the scan counts any concave face beyond 1e-12 rad (section 3). These lines are scored code (rule 4: a change needs a new scorer version) | Defer: record for the next scorer version; fix the docstring at the next package release (rule 5) |
| B5 | Blind | CHANGELOG and amendments in `4e26d30` cite `audit/l5-m1-v3-audit.md`, which was not in the tree at that commit | confirmed (fact); not a defect at HEAD | `git ls-tree -r --name-only 4e26d30 -- audit` lists only `l5-m1-v2-audit.md`; the v3 file was added in `de41a4c`. `check_release.py` passes at HEAD | None. Mention in this record only |
| B6 | Blind | The "What n counts" row dropped "uninterrupted", but the code still requires one segment | confirmed | `observation.py:91` (`hole.segments == 1`); old and new row in the `4e26d30` diff of the amendments | Fix now, document only: add "in one uninterrupted segment" to the row |
| B7 | Blind (Spec section) | Undeclared tension: the 99% wall rule against design note 7.1 ("cylindrical faces, axis parallel to Z, running through the full thickness") and its scope rule "never measured approximately". The amendments header says the amendments win "and say so", but the n-count row does not say it refines 7.1 | unclear | Design note lines 233 to 245. The 99% figure is a recognition threshold on wall coverage, not an approximation of a value: D and the axis are still read from the analytic cylinder, and a breakout keeps an exact margin (blind checker: axis 4.999 mm from the side gives `ok`, mx = 4.999). Whether recognising a 99%-wall bore is "measured approximately" is a reading of the design note, so it is the owner's ruling | Document: one clause in the n-count row saying it refines design note 7.1, with the reason (F1 and F2 reject breakouts at the contract). Owner ruling |

No finding of either review shows a wrong value under `ok`, a changed score
or a changed recorded verdict.

### 4.2 The five advisory findings of the first review (A1 to A5)

The labels A1 to A5 are given in this record. No earlier file uses them.
The list comes from `.workshop/LOG.md` (26 November 2026: "probe point,
symmetric matching, centred epsilon, edge-ligament refusal, Measurements
migration"), and each item is traced below to the first review. Section 4.3
checks that every other advisory remark of that review is resolved, so that
these five are the only ones open.

| ID | Source | Finding | Verdict | Evidence | Proposed action |
|---|---|---|---|---|---|
| A1 | First review, Task 6 (`audit/l5-m1-audit.md:6176`) | The scope scan probes at the midpoint of the face's UV rectangle, which need not lie on the trimmed face; one probe cannot establish concavity for every topology | confirmed (gap); fails closed in the reproduced case | Construction: four bores tilted 1e-9 rad (refused by rule) with a 1 mm material tongue centred on each face's UV midpoint. Without the tongue, all 8 faces probe `TopAbs_OUT` and the part is `out_of_scope`. With the tongue, all 8 probe `TopAbs_IN`, `off_axis_concave = 0`, and the verdict is `form_violation` ("a face is neither a plane of the envelope nor a recognised bore") instead of `out_of_scope`. Argument (inference, not a proof): a false `ok` needs a part that passes R9, and every face of such a part is an envelope plane or a recognised Z bore, and the tilt must be one the legacy detector still calls Z (per component at most 1e-6; at 1e-6 rad the first review recorded `form_violation`). On such a part each bore face is a connected U-interval times a band in V whose top and bottom edges vary by at most r x 1.42e-6. That is far less than T/2, so the UV midpoint lies on the face. A full-height cut by another bore or a side plane splits the face or trims its U-interval; it cannot leave a hole in the middle of one face. So a fooled probe needs a face that fails R9, and the outcome is a wrong refusal reason, not a false `ok` | Document in the amendments now (the probe point, the reproduction, why it fails closed). Defer the code fix to M3 (a point found inside the trimmed face with a face classifier): it is in `measure.py`, so rule 5 needs a release with a version bump |
| A2 | First review, Task 5 (`audit/l5-m1-audit.md:6153`) and Task 6 | `symmetric` matching is existential, not bijective, so duplicate or chained positions could match twice | rejected as a defect | `_nested` (`observation.py:99-114`) refuses any two concave Z axes closer than D/2 unless they are within 1e-7 mm with equal D, and sizes under 0.01 mm are refused. Any two surviving holes are therefore at least 0.005 mm apart, far above 2 x 1e-7, so each hole matches at most one mirror partner and the existential test is a bijection. Runs: a duplicate 5e-8 mm away gives n = 4, `ok`. A duplicate 8e-8 mm away straddling the 3-decimal grouping key (35.00049996 and 35.00050004) gives n = 4, and the kernel kept only 4 axes in `scope_axes`. Two holes 0.004 mm apart are `out_of_scope` (nested). The first review's `_positions` grouping no longer exists (grep of `observation.py`: no hit). Residual: the exemption branch of `_nested` (two faces within 1e-7 mm with equal D count as one cylinder) combined with the 3-decimal grouping key of `_classify_cylinders` was not exercised. In the straddle run the kernel merged the cuts, so the grouping path never saw two faces. Two surviving faces 5e-8 mm apart on either side of a key (for example half-cylinders built separately) could give two `Hole` objects and n one too high. This was not reproduced | Document one sentence in the amendments (why the existential match is a bijection on every measured part). Try the residual case as a gate case (`scripts/`, low-level half-cylinder faces straddling a key); if it builds and gives n too high, it becomes a required fix |
| A3 | First review, Task 5 (`audit/l5-m1-audit.md:6152`) | `centered` uses a per-axis comparison at 1e-7 mm; the norm is not specified | confirmed (spec gap) | `observation.py:156` (per axis); design note section 7 says only "within epsilon"; the amendments say the form tolerance. Pattern shifted diagonally by s: s = 0.8e-7 (Euclidean 1.13e-7) gives `centered` True; s = 1.2e-7 gives False. A second effect: `symmetric` compares each hole with its reflection, so it flips at s > 0.5e-7. At s = 0.8e-7 the part is `centered` but not `symmetric`. mx and my see the shift at 1e-9 mm in all three runs | Document now: state both operators (per axis, along the declared X and Y, P17/P19) and their different effective limits. Which norm is right is Bilal's decision; the proposal is to keep per-axis. Pin both boundaries in the gate when M2 compiles predicates on `centered` or `symmetric` |
| A4 | First review, Task 3 inventory (`audit/l5-m1-audit.md:278`); third review table | A hole whose edge ligament to the side is 1e-7 mm is refused as `form_violation` although the geometry is exact and intended | confirmed (known false rejection) | Holes D10 at x = +/-(45 - lig): lig 1e-7 gives `form_violation` ("the edges do not lie on the faces at the form tolerance"), mx = 5.0000001 correct. lig 1e-6, 1e-5, 1e-3 give `ok` with mx = 5 + lig. The refusal is R9's boundary check of scorer 0.5.0, shared through `rubric.form_verdict` | Document in the amendments as a known false rejection next to spline faces, with the boundary (1e-7 refused, 1e-6 measured). No code change: a change would be a new scorer version (rule 4), and soundness is preferred over coverage (P30) |
| A5 | First review, Task 6 Linux/Windows (`audit/l5-m1-audit.md:6178`) | Older stored `Measurements` objects have no explicit migration to the new fields | rejected as a defect | No `Measurements` is persisted. Grep of the package and the non-test `scripts/` for `pickle` and `asdict(` finds two `asdict` calls. One prints the scorer's `Report` to stdout (`__main__.py:55`), the other formats a task spec (`tasks.py:53`); neither serialises a `Measurements`. `git ls-files` lists no `.pkl` or `.pickle` file. Fork mode sends BRep bytes (`measure.py:994`), and reuse mode pickles in memory between two processes of the same code. An object with the pre-M1 field set, pickled and unpickled, reads the class defaults (`strict` False, `scope_axes` None), and `observe` raises `ValueError` ("needs a strict measurement"): a loud refusal, never a misread. A strict object round-tripped through pickle observes `ok` with the nominal values | Document one line in the amendments. No code change |

### 4.3 Sweep: the other advisory remarks of the first review

| Remark (first review) | Status now | Evidence |
|---|---|---|
| A 1e-10 rad turn stays inside epsilon, so "any other angle fails" is not literal | resolved | Amendments, Orientation row ("a turn of 1e-10 rad is inside it") |
| Rounded keys and the probe floor can merge or miss true axes | resolved | R2 (`scope_axes`, unrounded) and R4 (probe bounded, sizes under 0.01 mm refused): `measure.py:589`, `observation.py:134` |
| Hole centre at mid-thickness, not the top face | resolved as a declared deviation | Amendments, Hole centre row, with the (T/2) x 1e-12 bound |
| Strict-scan faults escaped as ValueError | resolved | R5; `observation.py:132`; pytest `test_a_failed_scope_scan_is_a_refusal_not_an_exception` |
| Pocket or slot as `form_violation` | open as an owner decision | Amendments deviation paragraph; see B1 |
| 99% wall, gap merge and open probe are extra rules | resolved (stated) | Amendments, What n counts row (C2); see B6 |
| px and py are the extent outside the four-corner family | resolved (stated) | Amendments, px, py row |
| `centered` per axis vs Euclidean | open | A3 |
| `symmetric` existential | closed by evidence | A2 |
| EPS_DIM exported but unused; a later scorer default could move L5 constants | resolved | `observation.py:48-52` pins the scorer basis by name; EPS_DIM is used at `observation.py:110` and `:144`; pytest `test_tolerances_are_those_of_scorer_0_5_0_by_name` |
| Direct zero-solid `observe` untested | residual, minor | `observation.py:121` handles `solid_count != 1`; the gate covers two solids (`scripts/test_l5_observation.py:278`) and no-result as a build error; no direct zero-solid case. Not a wrong-value path |
| `_positions` first-member grouping, order dependence | resolved | `_positions` removed (grep: no hit) |
| Frozen `Observation` holds a mutable dict | resolved | `MappingProxyType` (`observation.py:65`, `:128`); pytest `test_values_are_read_only_and_only_ok_allows_a_contract` |
| The scope detector shared the form try block | resolved | Separate try for the scope scan (`measure.py:932`), `scope_error` |
| UV midpoint probe point | open | A1 |
| Older stored `Measurements` | closed by evidence | A5 |
| Edge ligament 1e-7 refused | open, documented as false rejection | A4 |
| M2/M3 implications (F1, F2, None, basis pinning, latency) | recorded for later milestones | Amendments section 4 |
| Task 3 (b) wrong verdicts: tilt 1e-6, radius steps, cross radius 1e-4, connected offset steps | resolved | R1, R2, R4 and C1; third review found R2 to R5 resolved; gate `review_` and `boundary_` cases |
| Task 3 (c) correct part refused: holes under 0.01 mm | resolved as a stated size refusal | Amendments, Supported size row; `boundary_holes_of_0.009_mm` and `boundary_holes_of_0.010_mm` |
| Task 3 (c) breakout and overlap valid but violating F1, F2 | recorded for M3 | Amendments section 4 |
| Task 3 (d) latency of repeated rebuilds, quadratic matching | recorded for M3 | Amendments section 4, Latency |
| Second review: hole-centre bound, boundary cases at nested, 0.01 mm and EPS_DIM | resolved | Hole centre row; 14 `boundary_` cases in the gate, including the rim, size and diameter boundaries |
| Third review, document table: every row other than C1 and C2 | resolved | Rows covered by C1 and C2 (`4e26d30`); the missing audit paths resolve at HEAD (`check_release.py`) |

This sweep covered the first review's findings, Task 3 summary tables and
Task 4 to 6 sections (lines 1 to 292 and 6100 onward; the inventory between
them was not reread case by case), the second review's recommendation,
document requests and statement table, and the third review's C1, C2 and
document table. Within that coverage, A1 to A5 (and the pocket decision)
are the only advisory items still open.

## 5. Constraints on the proposed fixes

- Anything under `environments/cad_spec/cad_spec/` (A1's code fix, B4's



exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "rg -n 'INPROC|inproc|tempfile|Temporary|mkdtemp|WORKER' environments/cad_spec/cad_spec/measure.py; Get-Content environments/cad_spec/tests/test_l5_observation.py; Get-Content .venv/pyvenv.cfg; git diff ddd4e14601b144db17d17c6b638de99f3b494176 -- results/l5/m1-observation-suite.md; git log -3 --oneline" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 281ms:
54:default 10). CAD_SPEC_INPROC=1 disables isolation for debugging. This is
71:import tempfile
428:    workdir = tempfile.mkdtemp(prefix="cad-spec-brep-")
453:    workdir = tempfile.mkdtemp(prefix="cad-spec-load-")
972:    """Build and measure in THIS process (inproc and reuse modes)."""
1040:def _inproc_requested() -> bool:
1041:    return os.environ.get("CAD_SPEC_INPROC", "") == "1"
1137:    workdir = tempfile.mkdtemp(prefix="cad-spec-rollout-")
1240:    workdir = tempfile.mkdtemp(prefix="cad-spec-rollout-")
1255:    os.chdir(tempfile.mkdtemp(prefix="cad-spec-worker-"))
1371:    if _inproc_requested():
1372:        return {"mode": "inproc", "isolated": False}
1399:    if _inproc_requested():
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

home = C:\Users\bgare\AppData\Local\Programs\Python\Python312
include-system-site-packages = false
version = 3.12.10
executable = C:\Users\bgare\AppData\Local\Programs\Python\Python312\python.exe
command = C:\Users\bgare\AppData\Local\Programs\Python\Python312\python.exe -m venv D:\10_PROJECTS\cad-engineering\cad-spec-env\.venv
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: in the working copy of 'results/l5/m1-observation-suite.md', LF will be replaced by CRLF the next time Git touches it
diff --git a/results/l5/m1-observation-suite.md b/results/l5/m1-observation-suite.md
index 928f95b..508ac51 100644
--- a/results/l5/m1-observation-suite.md
+++ b/results/l5/m1-observation-suite.md
@@ -1,8 +1,10 @@
 # L5 observation map: adversarial suite (milestone M1)
 
+Generated by `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`. Do not edit by hand: rerun the script.
+
 Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported from the scorer.
 
-**60 of 60 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.
+**66 of 66 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.
 
 | Case | Expected verdict | Verdict | Result | Why the case exists |
 |---|---|---|---|---|
@@ -54,6 +56,9 @@ Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported f
 | `boundary_tilt_1e-11_rad_is_refused` | out_of_scope | out_of_scope | pass | ten times the slack |
 | `boundary_diagonal_tilt_1.3e-12_rad_is_refused` | out_of_scope | out_of_scope | pass | third review: each direction component is 9.2e-13, under the slack, but the angle is 1.3e-12 |
 | `boundary_diagonal_tilt_0.9e-12_rad_is_accepted` | ok | ok | pass | the same diagonal tilt inside the slack |
+| `boundary_diagonal_tilt_1.05e-12_rad_is_refused` | out_of_scope | out_of_scope | pass | fourth review: components 7.4e-13, angle 1.05e-12; the diagonal limit is bracketed to [1.0e-12, 1.05e-12) |
+| `boundary_pattern_0.99e-7_off_centre_is_centered` | ok | ok | pass | pattern moved (7e-8, 7e-8): 0.99e-7 from the centre in a straight line, inside the form tolerance. A mirrored hole is 1.4e-7 off, so not symmetric |
+| `boundary_pattern_1.02e-7_off_centre_is_not_centered` | ok | ok | pass | fourth review: 7.2e-8 along each axis, under the tolerance, but 1.02e-7 in a straight line, over it |
 | `boundary_axis_on_the_other_rim` | form_violation | form_violation | pass | two 10 mm holes 5.0 mm apart: each axis is ON the other rim, not inside it, so not a stepped hole |
 | `boundary_axis_inside_the_other_rim` | out_of_scope | out_of_scope | pass | 4.999 mm apart: each axis is inside the other cylinder |
 | `boundary_holes_of_0.009_mm` | out_of_scope | out_of_scope | pass | just under the supported size |
@@ -64,5 +69,8 @@ Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported f
 | `boundary_diameters_5e-10_apart` | ok | ok | pass | inside the dimension slack: one D |
 | `boundary_diameters_written_1e-9_apart` | out_of_scope | out_of_scope | pass | written exactly 1e-9 apart, measured 1.00000008e-9 apart: values are binary doubles, so this is refused |
 | `boundary_diameters_2e-9_apart` | out_of_scope | out_of_scope | pass | outside the slack |
+| `review_hole_split_across_position_key` | out_of_scope | out_of_scope | pass | two halves of one hole, axes 8e-8 apart on either side of x = 20.0005: was `ok` with n = 3 |
+| `review_hole_split_across_diameter_key` | out_of_scope | out_of_scope | pass | two halves of one hole, diameters 8e-10 apart on either side of 10.00005: was `ok` with n = 3 |
+| `review_hole_split_on_one_side_of_the_key` | ok | ok | pass | the same two halves on one side of the key: one hole, measured. The fourth hole is inside the pattern, so mx and px do not depend on which half is read |
 | `two_solids` | not_single_solid | not_single_solid | pass | an unfused second body |
 | `no_result` | build_error | build_error | pass | the answer binds no part: gate G1, not the map |
ddd4e14 Merge pull request #37 from azzbilal/chore/agent-workshop-init
d0ecdb7 Merge branch 'main' into chore/agent-workshop-init
8d5a84a Merge pull request #38 from azzbilal/ci/pin-verifiers-in-test-job

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command 'Get-Content environments/cad_spec/cad_spec/measure.py | Select-Object -Skip 965 -First 50; $env:PYTHONDONTWRITEBYTECODE='"'1'; "'$env:PYTHONUTF8='"'1'; "'$env:CAD_SPEC_INPROC='"'1'; .\\.venv\\Scripts\\python.exe -B scripts/test_l5_observation.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 15351ms:
        missing_volume=missing_volume,
        shape_error=shape_error,
    )


def _measure_code(code: str, *, strict: bool = False) -> Measurements:
    """Build and measure in THIS process (inproc and reuse modes)."""
    return measure(load_brep(build_brep(code)), strict=strict)


# --- isolated execution ------------------------------------------------------
#
# One persistent worker process owns the cadquery import and serves build
# requests over a pipe. Per-call timeouts kill hung rollouts; crashes respawn
# the worker on the next call. Spawn context keeps Windows and CI identical.
#
# Sandbox modes (CAD_SPEC_SANDBOX), see SECURITY.md for the threat model:
#
#   fork   (default on POSIX) the warm worker forks a FRESH child per rollout.
#          The child gets its own temp directory (deleted afterwards), its
#          own process group (killed whole afterwards, descendants included),
#          a scrubbed environment (no API keys or tokens inherited), every
#          inherited file descriptor closed except its result pipe, stdout
#          and stderr sent to /dev/null, and rlimits on CPU time, file size,
#          open files and (Linux only) address space. It is best-effort moved
#          into new user + network namespaces. The child sends back ONLY a
#          status byte plus either BREP geometry bytes or a short error text;
#          the worker parses the geometry with the kernel and measures it.
#          No object from the child is ever unpickled. Nothing a rollout does
#          to Python state survives into the next rollout, because the child
#          exits.
#   reuse  (default on Windows, which has no fork) one persistent process runs
#          every rollout, each in a fresh temp directory. State CAN leak
#          between rollouts. Trusted debugging and Windows dev only.
#
# Neither mode is a hard security boundary against deliberately malicious
# code: the child still runs as your user and can read files your user can
# read. For untrusted output at scale, run the scorer inside the provided
# container (Dockerfile) or Prime's sandbox.


def _exec_timeout() -> float:
    return float(os.environ.get("CAD_SPEC_EXEC_TIMEOUT", "10"))


def _mem_limit_mb() -> int:
    return int(os.environ.get("CAD_SPEC_MEM_MB", "2048"))


def _sandbox_mode() -> str:
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
[ok ] boundary_diagonal_tilt_1.05e-12_rad_is_refused out_of_scope
[ok ] boundary_pattern_0.99e-7_off_centre_is_centered ok
[ok ] boundary_pattern_1.02e-7_off_centre_is_not_centered ok
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
[ok ] review_hole_split_across_position_key out_of_scope
[ok ] review_hole_split_across_diameter_key out_of_scope
[ok ] review_hole_split_on_one_side_of_the_key ok
[ok ] two_solids                           not_single_solid
[ok ] no_result                            build_error

66/66 cases as expected

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$env:PYTHONDONTWRITEBYTECODE='"'1'; "'$env:PYTHONUTF8='"'1'; "'$env:CAD_SPEC_INPROC='"'1'; "'$env:PYTHONPATH="$PWD'"\\environments\\cad_spec\"; .\\.venv\\Scripts\\python.exe -B -m pytest -q -p no:cacheprovider environments/cad_spec/tests/test_l5_observation.py; .\\.venv\\Scripts\\ruff.exe check --no-cache environments/cad_spec/cad_spec/l5/observation.py scripts/test_l5_observation.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 4727ms:
..........                                                               [100%]
10 passed in 3.22s
All checks passed!

codex
No actionable regressions were found. All 66 adversarial cases, 10 focused tests, and lint checks passed; geometry tests ran in in-process mode.
No actionable regressions were found. All 66 adversarial cases, 10 focused tests, and lint checks passed; geometry tests ran in in-process mode.
```
