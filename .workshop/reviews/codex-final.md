# Codex review, final round (working tree against main)

- Command: `codex review --base main -c 'sandbox_mode="read-only"' -c 'approval_policy="never"'`
- codex-cli 0.169.0, model gpt-6.1-sol, reasoning effort high, sandbox read-only, approval never
- Started 2026-11-27T01:51:17Z (approximately; the blind patch was built at that time and Codex
  started right after), finished 2026-11-27T01:53:42Z, exit 0, 123 s wall time
- What it reviewed: nothing is committed on `fix/l5-m1-audit`, so Codex diffed the working tree
  against `ddd4e14` (= `main`). That is the final change set of every tracked file, including
  `SPREAD_LIMIT_MM`, observation version 2, the 73-case gate and the CLAUDE.md rule exceptions.
  Untracked files (`audit/l5-m1-v4-audit.md`, `.workshop/LOG.md`, `.workshop/reviews/`) are not
  part of that diff.
- Codex was not blind: it could read any file in the repository, including earlier audits.
- Verdict, verbatim: "No actionable regressions were found against the specified merge base. The
  observation gate passed 73/73 cases, observation unit tests passed 10/10, scorer harnesses
  passed 81/81 and 37/37, and lint passed. Linux-specific execution was not verified locally."
- Findings: none.

Full raw output follows, unedited except that its CRLF line endings were converted to LF (CLAUDE.md rule 7).

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
session id: 01a21ab3-7aad-7771-a535-b4b66260f087
--------
user
changes against 'main'
exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-Content C:\\Users\\bgare\\.codex\\skills\\behavioral-verification-review\\SKILL.md; git status --short; git diff --stat ddd4e14601b144db17d17c6b638de99f3b494176; Get-ChildItem -Force -Name" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 389ms:
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
 M .workshop/NOW.md
 M CHANGELOG.md
 M CLAUDE.md
 M audit/README.md
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
warning: in the working copy of '.workshop/NOW.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CHANGELOG.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CLAUDE.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'audit/README.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/design/L5-amendments.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'environments/cad_spec/cad_spec/l5/observation.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'results/l5/m1-observation-suite.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'scripts/test_l5_observation.py', LF will be replaced by CRLF the next time Git touches it
 .workshop/NOW.md                                 |   9 +-
 CHANGELOG.md                                     |  33 +++++-
 CLAUDE.md                                        |  29 ++++--
 audit/README.md                                  |   1 +
 docs/design/L5-amendments.md                     |  78 +++++++++++++--
 environments/cad_spec/cad_spec/l5/observation.py |  75 ++++++++++++--
 results/l5/m1-observation-suite.md               |  17 +++-
 scripts/test_l5_observation.py                   | 122 +++++++++++++++++++++++
 8 files changed, 336 insertions(+), 28 deletions(-)
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
CLAUDE.md
CHANGELOG.md

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command 'git diff ddd4e14601b144db17d17c6b638de99f3b494176; Get-ChildItem -Path . -Recurse -File -Include AGENTS.md,AGENTS.override.md -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName; Get-Content CLAUDE.md; Get-Content orca.yaml' in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 11432ms:
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: in the working copy of '.workshop/NOW.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CHANGELOG.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CLAUDE.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'audit/README.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/design/L5-amendments.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'environments/cad_spec/cad_spec/l5/observation.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'results/l5/m1-observation-suite.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'scripts/test_l5_observation.py', LF will be replaced by CRLF the next time Git touches it
diff --git a/.workshop/NOW.md b/.workshop/NOW.md
index 0f190c6..21d20af 100644
--- a/.workshop/NOW.md
+++ b/.workshop/NOW.md
@@ -29,8 +29,11 @@
 - CI only (Linux): fork sandbox replays, verdict diffs, GL-less scoring, docker sandbox, mutation gate.
 
 ## Open threads
-- L5 M1 is merged (PR #35) but NOT counted as audited: every required finding (R1 to R5, V1, C1,
-  C2) is fixed, but five advisory findings from the first review are still open, and no review
-  ran after the C1 fix. M2 waits. Owner: Bilal.
+- L5 M1 is counted as audited after the fourth round (`audit/l5-m1-v4-audit.md`, 27 November
+  2026), once branch `fix/l5-m1-audit` is merged. M2 may start. Observation version 2. Deferred:
+  scope-scan probe point (M3), order-dependent refusal of D (M3), two scorer-path defects (next
+  scorer version).
+- Rare `worker fault: MemoryError` from the Windows reuse worker on ordinary gate cases (2 of 73
+  in one gate run, none in the reruns). measure.py was not touched; cause unknown. Owner: Bilal.
 - agent-workshop hook bug (session marked edited before the path filter): fix drafted, not
   applied. Owner: Bilal.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b91f242..acd2a09 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -5,6 +5,17 @@ Scores are only comparable within one scorer version
 
 ## Unreleased
 
+### Release plan
+- **L5 M1 ships in the next package release, together with verifiers 0.4
+  support** (owner's ruling, 27 November 2026). Until then the package
+  stays at 0.5.0, although `cad_spec/l5/` and the strict measurement in
+  `measure.py` have changed since that release. No scorer version and no
+  recorded verdict changes. The observation map is at version 2
+  (`OBSERVATION_VERSION`): `centered` and two refusals changed after
+  version 1, so the same part can observe differently, and M2 items will
+  record the version they were compiled against. Version 1 was never
+  released.
+
 ### Agent working notes (no code or scoring change)
 - **`.workshop/`** (agent-workshop plugin, no code or scoring change): `NOW.md`, six confirmed promises in `PROMISES.md`, and `checks.json` (ruff on each edited file; ruff plus a fast pytest subset, 26 to 28 s, at the end of each turn). `CLAUDE.md` state updated to 26 November 2026.
 
@@ -48,10 +59,24 @@ Scores are only comparable within one scorer version
   raised instead of refusing. A final local verification
   (`audit/l5-m1-v3-audit.md`) found one more: the tilt limit was applied to
   the X and Y components separately. It is now on the angle.
-- **Gate:** `scripts/test_l5_observation.py`, 60 hand-built cases, in CI
-  (`results/l5/m1-observation-suite.md`). Every `ok` case states every
-  variable, and the exact boundary of each rule is pinned (tilt, nested
-  cylinders, supported size, equal diameters).
+- **Fourth review** (`audit/l5-m1-v4-audit.md`, 27 November 2026), after
+  which M1 counts as audited. One hole cut as two stacked halves was `ok`
+  with n = 3 when the halves sat on either side of the measurement's
+  rounding key, and `ok` with an mx wrong by 8e-8 mm when they sat 8e-8 mm
+  apart on one side; a hole whose faces disagree on its axis by more than
+  0.5e-9 mm, or fall into two hole groups, is now `out_of_scope`, so px and
+  py stay within 1e-9 mm whichever faces are read. `centered`
+  uses the straight-line distance from the mean hole centre to the plate
+  centre. The diagonal tilt limit stays 1e-12 rad and is now bracketed by
+  a case refused at 1.05e-12 rad. Deferred: the scope-scan probe point
+  (M3), an order-dependent refusal of D (M3), and two scorer-path defects
+  that fail closed (next scorer version).
+- **Gate:** `scripts/test_l5_observation.py`, 73 hand-built cases, in CI.
+  It writes `results/l5/m1-observation-suite.md`, which is generated and
+  rewritten in place (the one file named in the exceptions to CLAUDE.md
+  rules 3 and 8). Every `ok` case states every variable, and the exact boundary
+  of each rule is pinned (tilt, nested cylinders, supported size, equal
+  diameters, centred pattern, one axis per hole).
 - One deviation from the design note, recorded for approval: an extra pocket
   or slot is a `form_violation`, not `out_of_scope`.
 
diff --git a/CLAUDE.md b/CLAUDE.md
index f069110..5a8b2ff 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -12,7 +12,7 @@ Tiers L1 to L4 (L4 is an engineering change order). The owner, Bilal Azzouzi,
 is an aerospace structures and CAD engineer building this as a portfolio
 piece for RL-environment and evaluation work.
 
-## State on 26 November 2026
+## State on 27 November 2026
 
 - Released as `v0.5.0`. Package cad-spec 0.5.0, scorer 0.5.0 (strict
   contract, reviewed in four external rounds before merge). Scorer 0.4.0 is
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
@@ -52,7 +53,11 @@ piece for RL-environment and evaluation work.
    `results/` are records. Never rewrite them. A correction is a dated
    section appended below, with the original text kept. Any change to a
    plan, a budget or an analysis is a dated amendment written before the
-   outcome it could influence.
+   outcome it could influence. One exception (ruled 27 November 2026):
+   `results/l5/m1-observation-suite.md` is generated output of the L5 gate.
+   `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`
+   rewrites it in place, and the file says so in its header. No other file
+   under `results/` is covered.
 4. **Frozen code.** Do not edit `scripts/compare_training.py`,
    `scripts/compare_replication.py`, `scripts/bridge_check.py` or
    `scripts/replication_split.py`. Recorded verdicts are historical: a new
@@ -62,6 +67,12 @@ piece for RL-environment and evaluation work.
    `environments/cad_spec/cad_spec/` unless the task is explicitly a new
    release with a version bump. A scorer change starts with the defect suite
    (`scripts/validate_scorer.py`), committed before the scorer. New evaluation logic goes in `scripts/`.
+   One exception (ruled 27 November 2026): `cad_spec/l5/` (the L5
+   observation map, not yet released) may change before the next package
+   release, which ships it. Each change is listed under "Unreleased" in
+   `CHANGELOG.md`, and a change in meaning bumps `OBSERVATION_VERSION`. The
+   exception does not cover `measure.py`, `rubric.py`, `environment.py`,
+   `tasks.py` or any scorer version.
 6. **Git.** One branch per task, never commit on `main`, never push, merge,
    rebase or force anything. Bilal pushes and opens the pull request. Leave
    these untracked paths alone: `audit/scratch/run1-breps/`,
@@ -70,6 +81,10 @@ piece for RL-environment and evaluation work.
 7. **Text.** No em dashes anywhere: code, comments, docs, commit messages.
    Write files with LF line endings (`newline="\n"` in Python).
 8. **Verification writes to a temporary folder**, never over a tracked file.
+   One exception (ruled 27 November 2026): regenerating
+   `results/l5/m1-observation-suite.md` with the command named in rule 3 is
+   not verification and writes over that file on purpose. Verification runs
+   of the gate write `--out` to a temporary folder.
 
 ## Expert skills (metrology reasoning layer)
 
diff --git a/audit/README.md b/audit/README.md
index ac5dfc0..b486fc1 100644
--- a/audit/README.md
+++ b/audit/README.md
@@ -22,6 +22,7 @@ this folder is applied to the environment, the scripts or the configs.
 | `l5-m1-audit.md` | External review of L5 milestone M1, the observation map: the gate reproduced, 3,161 saved answers compared under both scorer versions (no score change), 180 ordinary constructions on six specs checked to 1e-9 mm, 153 further parts and fixtures | Report, 5 October 2026. Five required changes (tiny tilts, micro-steps, diameter equality, small cross bores, failed scope scan), all made in the same branch and pinned as `review_` cases |
 | `l5-m1-v2-audit.md` | Second review of L5 milestone M1, from source and kernel probes only: the environment held the incremental bundle without the repository, so no repository command could run | Report, 6 October 2026. All five fixes confirmed in the source; no defect found; boundary cases and two wording corrections requested and made. Not an execution-based verification |
 | `l5-m1-v3-audit.md` | Local verification of L5 milestone M1 after its fixes: gate 58 of 58 and the three other suites, 333 earlier parts rerun (no wrong value in an `ok` result), 180 controls to 1e-9 mm, 130 new boundary parts, 3,161 saved answers under both scorer versions (no score change) | Report, 7 October 2026. R2 to R5 resolved. One remaining defect (tilt limit applied per component, a diagonal 1.3e-12 rad tilt accepted) fixed and pinned; three document statements narrowed |
+| `l5-m1-v4-audit.md` | Fourth round on L5 milestone M1, run by the project (not an external audit): a Codex review and a blind fresh-context review of the C1 fix, triage of the five open advisory findings, the owner's rulings, the fix round and its reviews (Codex and two blind checks). Raw review outputs in `.workshop/reviews/` | Record, 27 November 2026. Two wrong values under `ok` found and refused (one hole split across the measurement's grouping, n = 3; faces of one hole 8e-8 mm apart, mx order-dependent); `centered` by straight-line distance; M1 counted as audited |
 | `a7-addendum.md` | Addendum to the external audit: full reading of 28 adapter answers of the replication (24 drawn by seed, 4 special cases) and 6 base answers. No exploitation found in the sample; describes what the adapter does and why two L3 answers were truncated | Report, 3 October 2026. Reflected in the corrections of `docs/experiments/replication-1.md` |
 | `replication1_geometry_check.py` | Second-implementation geometry check of the replication and original evaluation answers: comparison with the independently built ideal part, plus a sparse point test (the scorer is not imported). Output: `results/training/replication1/independent-geometry.json` | Post hoc check by the project (not an external audit), 3 October 2026; rebuilt after the external audit |
 | `guardrails-proposed.patch` | Spend guard, preflight check and related changes | **PROPOSED, NOT APPLIED.** To be reviewed, tested and registered before any future paid run; nothing under `scripts/` or `configs/` uses it |
diff --git a/docs/design/L5-amendments.md b/docs/design/L5-amendments.md
index 270f2ba..2a1c0c9 100644
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
@@ -34,9 +34,18 @@ one is frozen and audited.
 
 ## 3. M1 record: what the observation map does
 
-Code: `cad_spec/l5/observation.py` (observation version 1, built on scorer
-0.5.0 by name). Gate: `scripts/test_l5_observation.py` (60 cases, in CI).
-Result: `results/l5/m1-observation-suite.md`.
+Code: `cad_spec/l5/observation.py` (observation version 2, built on scorer
+0.5.0 by name). Gate: `scripts/test_l5_observation.py` (73 cases, in CI).
+Result: `results/l5/m1-observation-suite.md`, generated by the gate and
+rewritten in place on each run (the one file named in the exceptions to
+rules 3 and 8 of CLAUDE.md).
+
+Observation version 2 (fourth review): `centered` is judged by the
+straight-line distance, and two refusals were added (a hole split across the
+measurement's grouping, faces of one hole that disagree on its axis). The
+same part can therefore observe differently under version 1 and version 2,
+so an item compiled in M2 records the version it was compiled against.
+Version 1 was never released or used to compile an item.
 
 **Four verdicts.** `ok`; `form_violation` (the part has a feature nobody
 asked for); `out_of_scope` (a variable would be a guess); `not_single_solid`.
@@ -62,7 +71,8 @@ of guessing. The scorer does not read those fields.
 |---|---|---|
 | Position | Not a contract variable. A plate moved off the origin measures the same; the bounding-box centre is reported for information | design note 7.2 |
 | Orientation | L along X, W along Y. Turned 90 or 270 degrees about Z, they swap. Turned by any other angle beyond the form tolerance, the form fails (a turn of 1e-10 rad is inside it) | design note 7.2; the form check |
-| What n counts | Recognised Z bores only: open from the bottom face to the top face at the form tolerance, with at least 99% of the cylindrical wall present. A hole that breaks out of a side or overlaps another by a very small amount can therefore still be recognised; rules F1 and F2 remain contract checks. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures |
+| What n counts | Recognised Z bores only: one uninterrupted cylinder, open from the bottom face to the top face at the form tolerance, with at least 99% of the cylindrical wall present. A hole that breaks out of a side or overlaps another by a very small amount can therefore still be recognised; rules F1 and F2 remain contract checks. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures. Design note 7.1 asks for a hole "running through the full thickness"; this row refines it. D and the axis are still read from the exact cylinder, never approximated: 99% is only the threshold for recognising the bore |
+| One hole made of several faces | Faces at most 1e-7 mm apart with diameters within 1e-9 mm are one cylinder. That cylinder is `out_of_scope` when the axes of its faces are more than 0.5e-9 mm apart in a straight line (half the dimension slack, so that px and py, which combine two holes, stay within it; pinned at 0.45e-9, 0.55e-9 and a diagonal 0.57e-9), or when its faces fall into two hole groups of the measurement, which groups by position rounded to 3 decimals and diameter rounded to 4 | found by the fourth review. Two halves of one hole on either side of a rounding key were `ok` with n = 3. Two halves 8e-8 mm apart at a corner were `ok` with mx = 14.99999992 or 15.0 depending on the order of the cuts, because the measurement reads the axis of the first face. Under `ok` a hole's position is right to 0.5e-9 mm and px and py to 1e-9 mm, whichever faces are read (owner's ruling; two-hole gate cases on X and on the diagonal) |
 | px, py | The extent of the hole centres along X and Y. For the four-corner pattern that is the pitch; for any other pattern it is only the extent, and `rectangular` is then False | the design note defines pitch for the family only |
 | Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face. For an accepted axis the two differ by at most (T / 2) x 1e-12: 7e-12 mm for the thickest generated plate (14 mm) | one measurement shared with the scorer |
 | No hole | D, mx, my, px, py are `None`, never zero | a missing variable is not a value |
@@ -72,6 +82,9 @@ of guessing. The scorer does not read those fields.
 | Supported size | `out_of_scope` when any cylindrical face is under 0.01 mm in diameter (exactly 0.01 mm is measured). This comes before the form check, so a fillet under that size is a size refusal, not the `form_violation` of amendment 1 | the probe that tells a hole from a boss cannot classify smaller ones; refusing is honest, reporting n = 0 was not |
 | Failed scope scan | `out_of_scope`, with the reason | it used to raise an exception out of the map |
 | Spline surfaces | `form_violation`, with no hole recognised. A known false rejection kept on purpose (scorer review round 3). The kernel pads a spline bounding box by 2e-7 mm, so L, W and T of such a part are not exact | soundness over coverage |
+| Very thin edge wall | A hole whose wall is 1e-7 mm thick at a side face is a `form_violation` (the form check of scorer 0.5.0 refuses it). At 1e-6 mm and more it is `ok` with an exact margin. A known false rejection, like spline faces; changing it needs a new scorer version | soundness over coverage |
+| centered, symmetric, rectangular | `centered`: the straight-line distance from the mean hole centre to the bounding-box centre is at most the form tolerance, 1e-7 mm (pinned at 0.99e-7 and 1.02e-7). `symmetric` and `rectangular` match hole positions coordinate by coordinate at the same tolerance, so a match may be up to 1.41e-7 mm off in a straight line. The `symmetric` match asks that some hole mirrors each hole, not a one-to-one pairing; that is enough because two holes that survive the scope rules are at least 0.005 mm apart, so no hole can mirror two | owner's ruling (fourth review): a 2D offset is judged by its length, as for the tilt limit |
+| Old measurements | None are stored. A measurement made before the strict fields existed reads `strict` as False, and the map raises an error instead of observing it | a loud refusal, not a migration |
 
 **One deviation from the design note, for the owner's approval.** Section
 7.2 lists "extra pocket or slot" as `out_of_scope`. M1 reports it as
@@ -84,7 +97,11 @@ pocket with large rounded corners can be `out_of_scope` (its corner
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
 
@@ -119,6 +136,30 @@ tilt example, pockets and the scope rules), which is done.
 | R4 | A cross bore of 0.2 micron was missed: the inward probe crossed it | probe limited to half a radius, an unclear result is an error, and features under 0.01 mm are refused |
 | R5 | A failed scope scan made the map raise instead of refusing | explicit strict marker on the measurement; failures are `out_of_scope` |
 
+### 3.2 Fourth review of M1 (27 November 2026)
+
+Report: `audit/l5-m1-v4-audit.md`. Codex and an independent blind check
+reviewed the C1 fix, the five advisory findings of the first review were
+triaged, and the owner ruled on each. Changes:
+
+- **A hole made of faces that disagree on its axis is refused** (row
+  above). Adding the residual of the first review's symmetric-matching
+  remark to the gate showed `ok` with n = 3 for one physical hole, through
+  the real answer path. The fix-round blind review then showed `ok` with
+  an mx wrong by 8e-8 mm for two halves on one side of the key. Both are
+  refused, by the owner's rulings.
+- **`centered` uses the straight-line distance** (row above).
+- **Observation version 2** (section 3, opening paragraph).
+- **The diagonal tilt limit (1e-12 rad) is bracketed to [1.0e-12,
+  1.05e-12) rad** by a case refused at 1.05e-12 rad. Before, any threshold
+  below 1.3e-12 passed.
+- **Statements made precise:** what n counts (one uninterrupted
+  cylinder, and how the 99% rule relates to design note 7.1), the pocket
+  deviation, the thin edge wall, old measurements, and the `symmetric`
+  match. Section 4 records the deferred items.
+
+With these changes M1 is counted as audited, and M2 may start.
+
 ## 4. Open for later milestones
 
 - **Family rules F1 and F2 belong to gate G3 (M3).** The map does not
@@ -137,3 +178,28 @@ tilt example, pockets and the scope rules), which is done.
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
+- **Diameter verdict and cut order (M3).** Faces of one hole may differ in
+  diameter by up to 1e-9 mm, and the check that all through holes share one
+  D compares one face per hole. Two holes whose halves differ in opposite
+  directions (10 and 10.0000000009 in one, 10 and 9.9999999991 in the
+  other) are therefore `out_of_scope` in one cut order and `ok` with
+  D = 10.0 in the other (fourth review). The `ok` order reports a D within
+  1e-9 mm of every face, so this is a false refusal in one order, not a
+  wrong value. Deferred to M3 by the owner's ruling (27 November 2026).
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
index e949aca..5d23e1a 100644
--- a/environments/cad_spec/cad_spec/l5/observation.py
+++ b/environments/cad_spec/cad_spec/l5/observation.py
@@ -12,7 +12,8 @@ part?", and it gives one of four verdicts with the numbers:
                     or loose geometry they may not describe the plate.
   out_of_scope      a variable cannot be measured without guessing (a stepped
                     hole, a tilted hole, holes of different diameters, a
-                    feature too small to classify). The map refuses loudly
+                    feature too small to classify, one hole whose faces
+                    disagree on its axis). The map refuses loudly
                     instead of returning a wrong number.
   not_single_solid  zero or several solids: nothing to measure
 
@@ -41,10 +42,10 @@ from collections.abc import Mapping
 from dataclasses import dataclass, field
 from types import MappingProxyType
 
-from ..measure import FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
+from ..measure import COAXIAL_DP, FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
 from ..rubric import TOLERANCES, form_verdict
 
-OBSERVATION_VERSION = "1"
+OBSERVATION_VERSION = "2"  # 2: centered by straight-line distance; split and spread refusals (fourth review)
 SCORER_BASIS = "0.5.0"  # the validated scorer this map is built on; pinned, not "the current one"
 
 # One source of truth: that scorer's own constants.
@@ -56,6 +57,17 @@ EPS_FORM_MM: float = FORM_LINEAR_TOL              # two positions closer than th
 # missing it. The generator's smallest hole is 3 mm.
 MIN_CYLINDER_DIAMETER_MM = 0.01
 
+# The strict measurement groups cylinder faces into holes by axis position
+# rounded to COAXIAL_DP decimals and by diameter rounded to 4 decimals. The 4
+# is a literal in measure._classify_cylinders (no name to import), so it is
+# restated here. The gate cases review_hole_split_across_* pin it, and check
+# that the measurement really splits those parts.
+_DIAMETER_KEY_DP = 4
+
+# The faces of one hole must agree on its axis to half the dimension slack, so
+# that an extent combining two holes (px, py) stays within the slack.
+SPREAD_LIMIT_MM: float = EPS_DIM_MM / 2
+
 OK = "ok"
 FORM_VIOLATION = "form_violation"
 OUT_OF_SCOPE = "out_of_scope"
@@ -71,6 +83,9 @@ class Observation:
 
     `values` (read-only) holds L, W, T (bounding box), n (through holes along
     Z), D, mx, my, px, py, and the booleans rectangular, centered, symmetric.
+    `centered` compares the straight-line distance from the mean hole centre
+    to the bounding-box centre with the form tolerance. `rectangular` and
+    `symmetric` match positions coordinate by coordinate at that tolerance.
     A variable that does not exist (D with no hole) is None. With
     `out_of_scope` only the variables measured before the refusal are present.
     """
@@ -96,6 +111,45 @@ def _same(a: float, b: float) -> bool:
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
+    either side of a rounding key: axes 8e-10 mm apart around x = 20.0005, or
+    diameters 8e-10 mm apart around 10.00005. The measurement then makes two
+    half-depth holes, neither of which is a through hole, and n would be one
+    short under `ok`. The map refuses instead.
+    """
+    return any(_same_cylinder(a, b) and _group_key(*a) != _group_key(*b)
+               for i, a in enumerate(axes) for b in axes[i + 1:])
+
+
+def _axis_spread(axes: list[tuple[float, float, float]]) -> bool:
+    """Do two faces of one cylinder have axes more than half the dimension slack apart?
+
+    The measurement reads a hole's axis from one of its faces, whichever comes
+    first. With faces 8e-8 mm apart at a corner, mx was 14.99999992 or 15.0
+    depending on the order of the cuts. The faces of one hole must agree on
+    its axis to half the dimension slack, 0.5e-9 mm, or the map refuses. Under
+    `ok` each hole's position is then right to 0.5e-9 mm, and px or py, which
+    combine two holes, to 1e-9 mm: every variable is within the slack
+    whichever face is read.
+    """
+    return any(_same_cylinder(a, b) and math.hypot(a[0] - b[0], a[1] - b[1]) > SPREAD_LIMIT_MM
+               for i, a in enumerate(axes) for b in axes[i + 1:])
+
+
 def _nested(axes: list[tuple[float, float, float]]) -> bool:
     """Do two DIFFERENT concave Z cylinders share one hole position?
 
@@ -106,10 +160,9 @@ def _nested(axes: list[tuple[float, float, float]]) -> bool:
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
 
@@ -139,6 +192,12 @@ def observe(m: Measurements) -> Observation:
     if _nested(m.scope_axes):
         return done(OUT_OF_SCOPE, "two different cylinders at one hole position "
                                   "(counterbore, stepped or offset hole)")
+    if _split(m.scope_axes):
+        return done(OUT_OF_SCOPE, "one cylinder split across two hole groups of the measurement "
+                                  "(faces within the tolerances, on either side of a rounding key)")
+    if _axis_spread(m.scope_axes):
+        return done(OUT_OF_SCOPE, f"the faces of one hole have axes more than {SPREAD_LIMIT_MM:g} mm apart: "
+                                  "its position is not one number")
     through = [h for h in m.holes if _through(h, m)]
     values["n"] = len(through)
     if through and max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_DIM_MM:
@@ -153,7 +212,9 @@ def observe(m: Measurements) -> Observation:
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
index 928f95b..f82f748 100644
--- a/results/l5/m1-observation-suite.md
+++ b/results/l5/m1-observation-suite.md
@@ -1,8 +1,10 @@
 # L5 observation map: adversarial suite (milestone M1)
 
+Generated by `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`. Do not edit by hand: rerun the script.
+
 Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported from the scorer.
 
-**60 of 60 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.
+**73 of 73 cases as expected.** Reference part: 100 x 80 x 4 mm plate, four 10 mm through holes, 15 mm from the side faces.
 
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
@@ -64,5 +69,15 @@ Scorer 0.5.0. Dimension slack 1e-09 mm, form tolerance 1e-07 mm, both imported f
 | `boundary_diameters_5e-10_apart` | ok | ok | pass | inside the dimension slack: one D |
 | `boundary_diameters_written_1e-9_apart` | out_of_scope | out_of_scope | pass | written exactly 1e-9 apart, measured 1.00000008e-9 apart: values are binary doubles, so this is refused |
 | `boundary_diameters_2e-9_apart` | out_of_scope | out_of_scope | pass | outside the slack |
+| `review_hole_split_across_position_key` | out_of_scope | out_of_scope | pass | two halves of one hole, axes 8e-10 apart on either side of x = 20.0005: was `ok` with n = 3 |
+| `review_hole_split_across_diameter_key` | out_of_scope | out_of_scope | pass | two halves of one hole, diameters 8e-10 apart on either side of 10.00005: was `ok` with n = 3 |
+| `review_hole_halves_8e-8_apart_at_a_corner` | out_of_scope | out_of_scope | pass | was `ok` with mx = 14.99999992 in this cut order and 15.0 in the other: the axis was the first face's |
+| `review_hole_halves_8e-8_apart_other_order` | out_of_scope | out_of_scope | pass | the same part, other order: the verdict must not depend on it |
+| `boundary_hole_halves_0.45e-9_apart` | ok | ok | pass | inside the spread limit (half the dimension slack, 0.5e-9): the position is right to 0.5e-9 whichever face is read |
+| `boundary_hole_halves_0.55e-9_apart` | out_of_scope | out_of_scope | pass | just outside the spread limit |
+| `boundary_hole_halves_0.57e-9_apart_on_the_diagonal` | out_of_scope | out_of_scope | pass | 4e-10 along X and along Y, each inside the limit; 0.57e-9 in a straight line, outside it |
+| `review_two_holes_with_halves_0.45e-9_apart` | ok | ok | pass | two holes split on X in opposite directions: whichever faces are read, px is within 0.9e-9 of 70 |
+| `review_two_holes_with_halves_0.45e-9_apart_other_order` | ok | ok | pass | the same part, other cut order |
+| `review_two_holes_with_halves_0.49e-9_apart_on_the_diagonal` | ok | ok | pass | opposite corners split outwards by (3.5e-10, 3.5e-10): px and py are each within 0.7e-9 of the nominal |
 | `two_solids` | not_single_solid | not_single_solid | pass | an unfused second body |
 | `no_result` | build_error | build_error | pass | the answer binds no part: gate G1, not the map |
diff --git a/scripts/test_l5_observation.py b/scripts/test_l5_observation.py
index 79f5f5d..9a67e8b 100644
--- a/scripts/test_l5_observation.py
+++ b/scripts/test_l5_observation.py
@@ -10,6 +10,10 @@ Design note section 7.2, plus the counterexamples of the four scorer review
 rounds. Run it on every change to the map or to the measurement:
 
     python scripts/test_l5_observation.py [--out results/l5/m1-observation-suite.md]
+
+results/l5/m1-observation-suite.md is generated: this script rewrites it in
+place and writes a header saying so (CLAUDE.md, rules 3 and 8 name this one
+file). Verification runs write --out to a temporary folder.
 """
 
 from __future__ import annotations
@@ -44,6 +48,35 @@ def holes_at(points: str, extra: str = "") -> str:
             + f'.faces(">Z").workplane().pushPoints({points}).hole(10)\n')
 
 
+def shifted(s: float) -> str:
+    """The reference pattern moved by (s, s): its centre is s * sqrt(2) from the plate centre."""
+    return holes_at(f"[(-35+{s!r}, -25+{s!r}), (-35+{s!r}, 25+{s!r}), (35+{s!r}, -25+{s!r}), (35+{s!r}, 25+{s!r})]")
+
+
+def split_hole(lower: tuple[float, ...], upper: tuple[float, ...], d: float = 10) -> str:
+    """Three corner holes of diameter d, and a fourth hole cut as two half-depth cylinders,
+    (x, diameter[, y]) = lower for z in [-2, 0] and upper for z in [0, 2] (y is 25 unless
+    given), kept as separate faces (clean=False)."""
+    (xl, dl, yl), (xu, du, yu) = (*lower, 25)[:3], (*upper, 25)[:3]
+    return (HEAD + 'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane()'
+            f'.pushPoints([(-35, -25), (-35, 25), (35, -25)]).hole({d!r})\n'
+            f'result = result.cut(cq.Workplane("XY").workplane(offset=-3).center({xl!r}, {yl!r})'
+            f'.circle({dl / 2!r}).extrude(3), clean=False)\n'
+            f'result = result.cut(cq.Workplane("XY").center({xu!r}, {yu!r})'
+            f'.circle({du / 2!r}).extrude(3), clean=False)\n')
+
+
+def split_holes(plain: str, *halves: tuple[tuple[float, float], tuple[float, float]]) -> str:
+    """10 mm holes at the plain points, and one hole per entry of halves cut as two half-depth
+    cylinders centred at (x, y) = lower for z in [-2, 0] and upper for z in [0, 2] (clean=False)."""
+    code = HEAD + f'result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane().pushPoints({plain}).hole(10)\n'
+    for (xl, yl), (xu, yu) in halves:
+        code += (f'result = result.cut(cq.Workplane("XY").workplane(offset=-3).center({xl!r}, {yl!r})'
+                 f'.circle(5).extrude(3), clean=False)\n'
+                 f'result = result.cut(cq.Workplane("XY").center({xu!r}, {yu!r}).circle(5).extrude(3), clean=False)\n')
+    return code
+
+
 # name -> (code, expected verdict, expected values (a subset is enough), why this case exists)
 CASES: dict[str, tuple[str, str, dict, str]] = {
     # --- parts the map must measure exactly
@@ -236,6 +269,21 @@ CASES: dict[str, tuple[str, str, dict, str]] = {
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
@@ -272,6 +320,42 @@ CASES: dict[str, tuple[str, str, dict, str]] = {
         holes_at("[(-35, -25), (-35, 25), (35, -25)]")
         + 'result = result.faces(">Z").workplane().pushPoints([(35, 25)]).hole(10.000000002)\n',
         "out_of_scope", {**ENVELOPE, "n": 4}, "outside the slack"),
+    # --- found by the fourth review (27 November 2026): one hole made of two faces
+    "review_hole_split_across_position_key": (
+        split_hole((20.0004999996, 10), (20.0005000004, 10)), "out_of_scope", ENVELOPE,
+        "two halves of one hole, axes 8e-10 apart on either side of x = 20.0005: was `ok` with n = 3"),
+    "review_hole_split_across_diameter_key": (
+        split_hole((20, 10.0000499996), (20, 10.0000500004), d=10.00005), "out_of_scope", ENVELOPE,
+        "two halves of one hole, diameters 8e-10 apart on either side of 10.00005: was `ok` with n = 3"),
+    "review_hole_halves_8e-8_apart_at_a_corner": (
+        split_hole((35.0, 10), (35.00000008, 10)), "out_of_scope", ENVELOPE,
+        "was `ok` with mx = 14.99999992 in this cut order and 15.0 in the other: the axis was the first face's"),
+    "review_hole_halves_8e-8_apart_other_order": (
+        split_hole((35.00000008, 10), (35.0, 10)), "out_of_scope", ENVELOPE,
+        "the same part, other order: the verdict must not depend on it"),
+    "boundary_hole_halves_0.45e-9_apart": (
+        split_hole((35.0, 10), (35.00000000045, 10)), "ok", NOMINAL,
+        "inside the spread limit (half the dimension slack, 0.5e-9): the position is right to 0.5e-9 "
+        "whichever face is read"),
+    "boundary_hole_halves_0.55e-9_apart": (
+        split_hole((35.0, 10), (35.00000000055, 10)), "out_of_scope", ENVELOPE, "just outside the spread limit"),
+    "boundary_hole_halves_0.57e-9_apart_on_the_diagonal": (
+        split_hole((35.0, 10, 25.0), (35.0000000004, 10, 25.0000000004)), "out_of_scope", ENVELOPE,
+        "4e-10 along X and along Y, each inside the limit; 0.57e-9 in a straight line, outside it"),
+    "review_two_holes_with_halves_0.45e-9_apart": (
+        split_holes("[(-35, -25), (35, -25)]",
+                    ((-35.0, 25), (-35.00000000045, 25)), ((35.0, 25), (35.00000000045, 25))),
+        "ok", NOMINAL,
+        "two holes split on X in opposite directions: whichever faces are read, px is within 0.9e-9 of 70"),
+    "review_two_holes_with_halves_0.45e-9_apart_other_order": (
+        split_holes("[(-35, -25), (35, -25)]",
+                    ((-35.00000000045, 25), (-35.0, 25)), ((35.00000000045, 25), (35.0, 25))),
+        "ok", NOMINAL, "the same part, other cut order"),
+    "review_two_holes_with_halves_0.49e-9_apart_on_the_diagonal": (
+        split_holes("[(-35, 25), (35, -25)]", ((-35.0, -25.0), (-35.00000000035, -25.00000000035)),
+                    ((35.0, 25.0), (35.00000000035, 25.00000000035))),
+        "ok", NOMINAL,
+        "opposite corners split outwards by (3.5e-10, 3.5e-10): px and py are each within 0.7e-9 of the nominal"),
     # --- nothing to measure
     "two_solids": (
         BASE + 'result = cq.Compound.makeCompound([result.val(), cq.Solid.makeBox(5, 5, 5, cq.Vector(200, 0, 0))])\n',
@@ -281,6 +365,33 @@ CASES: dict[str, tuple[str, str, dict, str]] = {
 }
 
 
+# Cases built from separate faces: the rule their refusal must come from (None
+# for an `ok` case), the number of holes the measurement must make (five for
+# the grouping rule, so the map's copy of the grouping key keeps agreeing with
+# the measurement), and the number of concave cylinder faces the kernel must
+# keep (one more per split hole, or the case would test nothing).
+REASONS: dict[str, tuple[str | None, int | None, int]] = {
+    "review_hole_split_across_position_key": ("two hole groups", 5, 5),
+    "review_hole_split_across_diameter_key": ("two hole groups", 5, 5),
+    "review_hole_halves_8e-8_apart_at_a_corner": ("axes more than", None, 5),
+    "review_hole_halves_8e-8_apart_other_order": ("axes more than", None, 5),
+    "boundary_hole_halves_0.45e-9_apart": (None, None, 5),
+    "boundary_hole_halves_0.55e-9_apart": ("axes more than", None, 5),
+    "boundary_hole_halves_0.57e-9_apart_on_the_diagonal": ("axes more than", None, 5),
+    "review_two_holes_with_halves_0.45e-9_apart": (None, None, 6),
+    "review_two_holes_with_halves_0.45e-9_apart_other_order": (None, None, 6),
+    "review_two_holes_with_halves_0.49e-9_apart_on_the_diagonal": (None, None, 6),
+}
+
+
+def measured(code: str) -> tuple[int, int]:
+    """Holes made by the strict measurement, and concave Z cylinder faces it saw."""
+    from cad_spec.measure import build_and_measure
+
+    m = build_and_measure(code, strict=True)
+    return len(m.holes), len(m.scope_axes or [])
+
+
 def run(code: str) -> tuple[str, dict, str]:
     from cad_spec.l5 import observe_code
     from cad_spec.measure import BuildError
@@ -324,6 +435,15 @@ def main() -> int:
         if verdict == "ok" and set(want) != ALL_KEYS:
             bad.append("an `ok` case must state every variable")
         bad += matches(got, want)
+        if name in REASONS:
+            phrase, holes, faces = REASONS[name]
+            got_holes, got_faces = measured(code)
+            if phrase is not None and phrase not in reason:
+                bad.append(f"reason: expected the rule '{phrase}', got '{reason}'")
+            if holes is not None and got_holes != holes:
+                bad.append(f"the measurement made {got_holes} holes, expected {holes}")
+            if got_faces != faces:
+                bad.append(f"the kernel kept {got_faces} cylinder faces, expected {faces}: the case tests nothing")
         failures += bool(bad)
         print(f"[{'BAD' if bad else 'ok '}] {name:36s} {got_verdict}" + ("".join(f"\n        {b}" for b in bad)))
         rows.append((name, verdict, got_verdict, "pass" if not bad else "FAIL", why))
@@ -334,6 +454,8 @@ def main() -> int:
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

## State on 27 November 2026

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
   `results/l5/m1-observation-suite.md` is generated output of the L5 gate.
   `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`
   rewrites it in place, and the file says so in its header. No other file
   under `results/` is covered.
4. **Frozen code.** Do not edit `scripts/compare_training.py`,
   `scripts/compare_replication.py`, `scripts/bridge_check.py` or
   `scripts/replication_split.py`. Recorded verdicts are historical: a new
   scorer gets a new version, the old one stays selectable in `rubric.py`,
   and a recorded verdict is never replaced.
5. **The package.** Do not change anything under
   `environments/cad_spec/cad_spec/` unless the task is explicitly a new
   release with a version bump. A scorer change starts with the defect suite
   (`scripts/validate_scorer.py`), committed before the scorer. New evaluation logic goes in `scripts/`.
   One exception (ruled 27 November 2026): `cad_spec/l5/` (the L5
   observation map, not yet released) may change before the next package
   release, which ships it. Each change is listed under "Unreleased" in
   `CHANGELOG.md`, and a change in meaning bumps `OBSERVATION_VERSION`. The
   exception does not cover `measure.py`, `rubric.py`, `environment.py`,
   `tasks.py` or any scorer version.
6. **Git.** One branch per task, never commit on `main`, never push, merge,
   rebase or force anything. Bilal pushes and opens the pull request. Leave
   these untracked paths alone: `audit/scratch/run1-breps/`,
   `audit/scratch/run1-perturbations/`, `results/baselines.md`,
   `results/superseded/`.
7. **Text.** No em dashes anywhere: code, comments, docs, commit messages.
   Write files with LF line endings (`newline="\n"` in Python).
8. **Verification writes to a temporary folder**, never over a tracked file.
   One exception (ruled 27 November 2026): regenerating
   `results/l5/m1-observation-suite.md` with the command named in rule 3 is
   not verification and writes over that file on purpose. Verification runs
   of the gate write `--out` to a temporary folder.

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
# Orca workspace config. Docs: https://orca.dev/docs/migrate-from-conductor (scripts.setup)
#
# scripts.setup runs in each new worktree, with the worktree as the current
# directory. On native Windows Orca runs it through cmd.exe, by one of two paths:
#   - the setup runner: each line becomes "call <line>", stop on first failure;
#   - the in-process hook (runHook): the whole script goes to one
#     "cmd.exe /d /s /c", which runs only up to the first newline, and is
#     killed after 120 s.
# A script whose first line is "#!" + a POSIX shell runs under Git Bash
# instead, but only when the terminal is Git Bash. So the script is one line,
# with no "#!", using syntax that cmd.exe and bash both accept: "&&" and
# quoted forward-slash paths.
#
# Each worktree gets its own .venv because the install is editable: a shared
# venv would import cad_spec from whichever checkout installed it last.
# A first install takes 6-7 minutes on this machine, longer than the
# in-process hook's 120 s limit.
scripts:
  setup: |
    py -3.12 -m venv .venv && ".venv/Scripts/python.exe" -m pip install -c environments/cad_spec/constraints.txt -e "environments/cad_spec[dev]"

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "git diff ddd4e14601b144db17d17c6b638de99f3b494176 -- environments/cad_spec/cad_spec/l5/observation.py; Get-Content environments/cad_spec/cad_spec/l5/observation.py; Get-Content CLAUDE.md; Get-Content orca.yaml; git ls-files '*AGENTS*' '*CLAUDE*'; Get-Content C:\\Users\\bgare\\.codex\\skills\\behavioral-verification-review\\references\\source-notes.md" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 275ms:
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: in the working copy of 'environments/cad_spec/cad_spec/l5/observation.py', LF will be replaced by CRLF the next time Git touches it
diff --git a/environments/cad_spec/cad_spec/l5/observation.py b/environments/cad_spec/cad_spec/l5/observation.py
index e949aca..5d23e1a 100644
--- a/environments/cad_spec/cad_spec/l5/observation.py
+++ b/environments/cad_spec/cad_spec/l5/observation.py
@@ -12,7 +12,8 @@ part?", and it gives one of four verdicts with the numbers:
                     or loose geometry they may not describe the plate.
   out_of_scope      a variable cannot be measured without guessing (a stepped
                     hole, a tilted hole, holes of different diameters, a
-                    feature too small to classify). The map refuses loudly
+                    feature too small to classify, one hole whose faces
+                    disagree on its axis). The map refuses loudly
                     instead of returning a wrong number.
   not_single_solid  zero or several solids: nothing to measure
 
@@ -41,10 +42,10 @@ from collections.abc import Mapping
 from dataclasses import dataclass, field
 from types import MappingProxyType
 
-from ..measure import FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
+from ..measure import COAXIAL_DP, FORM_LINEAR_TOL, Hole, Measurements, build_and_measure
 from ..rubric import TOLERANCES, form_verdict
 
-OBSERVATION_VERSION = "1"
+OBSERVATION_VERSION = "2"  # 2: centered by straight-line distance; split and spread refusals (fourth review)
 SCORER_BASIS = "0.5.0"  # the validated scorer this map is built on; pinned, not "the current one"
 
 # One source of truth: that scorer's own constants.
@@ -56,6 +57,17 @@ EPS_FORM_MM: float = FORM_LINEAR_TOL              # two positions closer than th
 # missing it. The generator's smallest hole is 3 mm.
 MIN_CYLINDER_DIAMETER_MM = 0.01
 
+# The strict measurement groups cylinder faces into holes by axis position
+# rounded to COAXIAL_DP decimals and by diameter rounded to 4 decimals. The 4
+# is a literal in measure._classify_cylinders (no name to import), so it is
+# restated here. The gate cases review_hole_split_across_* pin it, and check
+# that the measurement really splits those parts.
+_DIAMETER_KEY_DP = 4
+
+# The faces of one hole must agree on its axis to half the dimension slack, so
+# that an extent combining two holes (px, py) stays within the slack.
+SPREAD_LIMIT_MM: float = EPS_DIM_MM / 2
+
 OK = "ok"
 FORM_VIOLATION = "form_violation"
 OUT_OF_SCOPE = "out_of_scope"
@@ -71,6 +83,9 @@ class Observation:
 
     `values` (read-only) holds L, W, T (bounding box), n (through holes along
     Z), D, mx, my, px, py, and the booleans rectangular, centered, symmetric.
+    `centered` compares the straight-line distance from the mean hole centre
+    to the bounding-box centre with the form tolerance. `rectangular` and
+    `symmetric` match positions coordinate by coordinate at that tolerance.
     A variable that does not exist (D with no hole) is None. With
     `out_of_scope` only the variables measured before the refusal are present.
     """
@@ -96,6 +111,45 @@ def _same(a: float, b: float) -> bool:
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
+    either side of a rounding key: axes 8e-10 mm apart around x = 20.0005, or
+    diameters 8e-10 mm apart around 10.00005. The measurement then makes two
+    half-depth holes, neither of which is a through hole, and n would be one
+    short under `ok`. The map refuses instead.
+    """
+    return any(_same_cylinder(a, b) and _group_key(*a) != _group_key(*b)
+               for i, a in enumerate(axes) for b in axes[i + 1:])
+
+
+def _axis_spread(axes: list[tuple[float, float, float]]) -> bool:
+    """Do two faces of one cylinder have axes more than half the dimension slack apart?
+
+    The measurement reads a hole's axis from one of its faces, whichever comes
+    first. With faces 8e-8 mm apart at a corner, mx was 14.99999992 or 15.0
+    depending on the order of the cuts. The faces of one hole must agree on
+    its axis to half the dimension slack, 0.5e-9 mm, or the map refuses. Under
+    `ok` each hole's position is then right to 0.5e-9 mm, and px or py, which
+    combine two holes, to 1e-9 mm: every variable is within the slack
+    whichever face is read.
+    """
+    return any(_same_cylinder(a, b) and math.hypot(a[0] - b[0], a[1] - b[1]) > SPREAD_LIMIT_MM
+               for i, a in enumerate(axes) for b in axes[i + 1:])
+
+
 def _nested(axes: list[tuple[float, float, float]]) -> bool:
     """Do two DIFFERENT concave Z cylinders share one hole position?
 
@@ -106,10 +160,9 @@ def _nested(axes: list[tuple[float, float, float]]) -> bool:
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
 
@@ -139,6 +192,12 @@ def observe(m: Measurements) -> Observation:
     if _nested(m.scope_axes):
         return done(OUT_OF_SCOPE, "two different cylinders at one hole position "
                                   "(counterbore, stepped or offset hole)")
+    if _split(m.scope_axes):
+        return done(OUT_OF_SCOPE, "one cylinder split across two hole groups of the measurement "
+                                  "(faces within the tolerances, on either side of a rounding key)")
+    if _axis_spread(m.scope_axes):
+        return done(OUT_OF_SCOPE, f"the faces of one hole have axes more than {SPREAD_LIMIT_MM:g} mm apart: "
+                                  "its position is not one number")
     through = [h for h in m.holes if _through(h, m)]
     values["n"] = len(through)
     if through and max(h.diameter for h in through) - min(h.diameter for h in through) > EPS_DIM_MM:
@@ -153,7 +212,9 @@ def observe(m: Measurements) -> Observation:
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
                    feature too small to classify, one hole whose faces
                    disagree on its axis). The map refuses loudly
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

OBSERVATION_VERSION = "2"  # 2: centered by straight-line distance; split and spread refusals (fourth review)
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
# restated here. The gate cases review_hole_split_across_* pin it, and check
# that the measurement really splits those parts.
_DIAMETER_KEY_DP = 4

# The faces of one hole must agree on its axis to half the dimension slack, so
# that an extent combining two holes (px, py) stays within the slack.
SPREAD_LIMIT_MM: float = EPS_DIM_MM / 2

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
    either side of a rounding key: axes 8e-10 mm apart around x = 20.0005, or
    diameters 8e-10 mm apart around 10.00005. The measurement then makes two
    half-depth holes, neither of which is a through hole, and n would be one
    short under `ok`. The map refuses instead.
    """
    return any(_same_cylinder(a, b) and _group_key(*a) != _group_key(*b)
               for i, a in enumerate(axes) for b in axes[i + 1:])


def _axis_spread(axes: list[tuple[float, float, float]]) -> bool:
    """Do two faces of one cylinder have axes more than half the dimension slack apart?

    The measurement reads a hole's axis from one of its faces, whichever comes
    first. With faces 8e-8 mm apart at a corner, mx was 14.99999992 or 15.0
    depending on the order of the cuts. The faces of one hole must agree on
    its axis to half the dimension slack, 0.5e-9 mm, or the map refuses. Under
    `ok` each hole's position is then right to 0.5e-9 mm, and px or py, which
    combine two holes, to 1e-9 mm: every variable is within the slack
    whichever face is read.
    """
    return any(_same_cylinder(a, b) and math.hypot(a[0] - b[0], a[1] - b[1]) > SPREAD_LIMIT_MM
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
    if _axis_spread(m.scope_axes):
        return done(OUT_OF_SCOPE, f"the faces of one hole have axes more than {SPREAD_LIMIT_MM:g} mm apart: "
                                  "its position is not one number")
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

## State on 27 November 2026

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
   `results/l5/m1-observation-suite.md` is generated output of the L5 gate.
   `scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`
   rewrites it in place, and the file says so in its header. No other file
   under `results/` is covered.
4. **Frozen code.** Do not edit `scripts/compare_training.py`,
   `scripts/compare_replication.py`, `scripts/bridge_check.py` or
   `scripts/replication_split.py`. Recorded verdicts are historical: a new
   scorer gets a new version, the old one stays selectable in `rubric.py`,
   and a recorded verdict is never replaced.
5. **The package.** Do not change anything under
   `environments/cad_spec/cad_spec/` unless the task is explicitly a new
   release with a version bump. A scorer change starts with the defect suite
   (`scripts/validate_scorer.py`), committed before the scorer. New evaluation logic goes in `scripts/`.
   One exception (ruled 27 November 2026): `cad_spec/l5/` (the L5
   observation map, not yet released) may change before the next package
   release, which ships it. Each change is listed under "Unreleased" in
   `CHANGELOG.md`, and a change in meaning bumps `OBSERVATION_VERSION`. The
   exception does not cover `measure.py`, `rubric.py`, `environment.py`,
   `tasks.py` or any scorer version.
6. **Git.** One branch per task, never commit on `main`, never push, merge,
   rebase or force anything. Bilal pushes and opens the pull request. Leave
   these untracked paths alone: `audit/scratch/run1-breps/`,
   `audit/scratch/run1-perturbations/`, `results/baselines.md`,
   `results/superseded/`.
7. **Text.** No em dashes anywhere: code, comments, docs, commit messages.
   Write files with LF line endings (`newline="\n"` in Python).
8. **Verification writes to a temporary folder**, never over a tracked file.
   One exception (ruled 27 November 2026): regenerating
   `results/l5/m1-observation-suite.md` with the command named in rule 3 is
   not verification and writes over that file on purpose. Verification runs
   of the gate write `--out` to a temporary folder.

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
# Orca workspace config. Docs: https://orca.dev/docs/migrate-from-conductor (scripts.setup)
#
# scripts.setup runs in each new worktree, with the worktree as the current
# directory. On native Windows Orca runs it through cmd.exe, by one of two paths:
#   - the setup runner: each line becomes "call <line>", stop on first failure;
#   - the in-process hook (runHook): the whole script goes to one
#     "cmd.exe /d /s /c", which runs only up to the first newline, and is
#     killed after 120 s.
# A script whose first line is "#!" + a POSIX shell runs under Git Bash
# instead, but only when the terminal is Git Bash. So the script is one line,
# with no "#!", using syntax that cmd.exe and bash both accept: "&&" and
# quoted forward-slash paths.
#
# Each worktree gets its own .venv because the install is editable: a shared
# venv would import cad_spec from whichever checkout installed it last.
# A first install takes 6-7 minutes on this machine, longer than the
# in-process hook's 120 s limit.
scripts:
  setup: |
    py -3.12 -m venv .venv && ".venv/Scripts/python.exe" -m pip install -c environments/cad_spec/constraints.txt -e "environments/cad_spec[dev]"
CLAUDE.md
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
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-Content .claude/skills/cad-spec-metrology-router/SKILL.md; Get-Content docs/design/L5-amendments.md; Get-Content .github/workflows/ci.yml; Get-Content scripts/test_l5_observation.py | Select-Object -Last 125; Get-ChildItem D:\\AGENTS*,D:\\10_PROJECTS\\AGENTS*,D:\\10_PROJECTS\\cad-engineering\\AGENTS* -ErrorAction SilentlyContinue; Get-ChildItem environments,scripts,docs,results,.workshop,audit -Recurse -File -Filter 'AGENTS*' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 346ms:
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
# L5 v1: implementation amendments and milestone record

The governing specification is
[`L5-region-graded-change-orders-v1.0.md`](L5-region-graded-change-orders-v1.0.md).
Its architecture is not reopened here. This file records the implementation
amendments approved at kickoff (5 October 2026), the milestone order, and
what each milestone decided while it was built. Where this file and the
design note disagree, this file wins, and says so.

## 1. Kickoff amendments (approved 5 October 2026)

| # | Topic | Decision |
|---|---|---|
| 1 | Form preservation | The observation map can measure a part that has fillets or chamfers, but any unrequested feature is a form violation. The strict form check validated in scorer 0.5.0 is reused. Measurable does not mean acceptable |
| 2 | Tolerances | Not duplicated in L5. Imported from scorer 0.5.0: 1e-9 mm slack on dimensions, 1e-7 mm on form |
| 3 | Intent in the prompt | The obligation is stated, the probe values are not. Every prompt says that the declared interface parameters must remain overridable and that, after a rebuild, every still-active Contract B constraint and every inherited behaviour not changed by the order must still hold |
| 4 | MUS and MCS enumeration | Z3 with exact rationals, no MARCO in v1. With about 5 to 10 constraints, every subset is enumerated and checked. Same semantics, much less code to audit |
| 5 | Solver baseline | A baseline that parses the exposed contract and order, solves the system and emits a valid revision is built and reported. L5 claims generalisation and CAD-editing behaviour, not that the family cannot be solved by a program |
| 6 | Probe cost | The rebuild cost is accepted in v1. The compiled probe list is stored per item; rebuild count and p50 and p95 grading latency are reported. Optimisation waits until correctness is frozen |

## 2. Milestones

The build-order figure of the design note did not survive its export. This
order was approved at kickoff. A milestone does not start before the previous
one is frozen and audited.

| Milestone | Builds | Exit gate | Status |
|---|---|---|---|
| M1 Observation and form | observation map, form check, tolerance reuse, adversarial suite, off-origin handling, out-of-scope verdict | every hand-built adversarial model gives the expected observation or an explicit refusal | audited (fourth review, 27 November 2026, section 3.2) |
| M2 Contract compiler | Contract A schema, typed order operators, Contract B, exact-rational encoding, subset enumeration of MUS and MCS, `allowed_to_move`, `forced`, witness, compiled-item schema | items reproduce from their semantic state and compile to correct static artifacts | not started |
| M3 Runtime grader and intent | gates G0 to G5, CQGI parameter interface, change detection, inherited behaviour, sensitivity-filtered probes, structured rejects, accepted-MUS lookup, near-twins | witnesses pass, hardcoded witnesses fail on intent-bearing items, infeasible items accept only minimal conflict sets | not started |
| M4 Diversity, diagnostics, baselines | code and language renderers, equivalence checks, misconception library, separability, the five baselines, the full per-item checklist | every item passes the generator-side checklist and every diagnostic is separable | not started |
| M5 Evaluation protocol | splits, MCD only if the compound count supports it, hidden three-seed schedule, manifest and commitment, sealed set, report format, latency statistics | L5-v1 can be frozen, committed, reproduced after seed release and evaluated identically across models | not started |

## 3. M1 record: what the observation map does

Code: `cad_spec/l5/observation.py` (observation version 2, built on scorer
0.5.0 by name). Gate: `scripts/test_l5_observation.py` (73 cases, in CI).
Result: `results/l5/m1-observation-suite.md`, generated by the gate and
rewritten in place on each run (the one file named in the exceptions to
rules 3 and 8 of CLAUDE.md).

Observation version 2 (fourth review): `centered` is judged by the
straight-line distance, and two refusals were added (a hole split across the
measurement's grouping, faces of one hole that disagree on its axis). The
same part can therefore observe differently under version 1 and version 2,
so an item compiled in M2 records the version it was compiled against.
Version 1 was never released or used to compile an item.

**Four verdicts.** `ok`; `form_violation` (the part has a feature nobody
asked for); `out_of_scope` (a variable would be a guess); `not_single_solid`.
An answer that builds no part raises a build error, which is gate G1's
business.

**Only `ok` lets a contract be evaluated.** Under `form_violation` the
numbers are reported for diagnosis only: with a boss, a spline face or loose
geometry they may not describe the plate. And `ok` is not compliance: it
says the numbers can be trusted. A hole 1 micron from breaking out of a side
is `ok` with an exact margin; rejecting it is the contract's job (section 4).

**Nothing is measured twice.** The numbers come from the strict measurement
of scorer 0.5.0. The form verdict is that scorer's R9, now one function
(`rubric.form_verdict`) that both call. The strict measurement also carries
what the scorer's hole grouping rounds away (`scope_axes`,
`min_cylinder_diameter`, `off_axis_concave`), so the map can refuse instead
of guessing. The scorer does not read those fields.

**Decisions taken in M1** (as revised after the external review, section 3.1)

| Topic | Decision | Why |
|---|---|---|
| Position | Not a contract variable. A plate moved off the origin measures the same; the bounding-box centre is reported for information | design note 7.2 |
| Orientation | L along X, W along Y. Turned 90 or 270 degrees about Z, they swap. Turned by any other angle beyond the form tolerance, the form fails (a turn of 1e-10 rad is inside it) | design note 7.2; the form check |
| What n counts | Recognised Z bores only: one uninterrupted cylinder, open from the bottom face to the top face at the form tolerance, with at least 99% of the cylindrical wall present. A hole that breaks out of a side or overlaps another by a very small amount can therefore still be recognised; rules F1 and F2 remain contract checks. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures. Design note 7.1 asks for a hole "running through the full thickness"; this row refines it. D and the axis are still read from the exact cylinder, never approximated: 99% is only the threshold for recognising the bore |
| One hole made of several faces | Faces at most 1e-7 mm apart with diameters within 1e-9 mm are one cylinder. That cylinder is `out_of_scope` when the axes of its faces are more than 0.5e-9 mm apart in a straight line (half the dimension slack, so that px and py, which combine two holes, stay within it; pinned at 0.45e-9, 0.55e-9 and a diagonal 0.57e-9), or when its faces fall into two hole groups of the measurement, which groups by position rounded to 3 decimals and diameter rounded to 4 | found by the fourth review. Two halves of one hole on either side of a rounding key were `ok` with n = 3. Two halves 8e-8 mm apart at a corner were `ok` with mx = 14.99999992 or 15.0 depending on the order of the cuts, because the measurement reads the axis of the first face. Under `ok` a hole's position is right to 0.5e-9 mm and px and py to 1e-9 mm, whichever faces are read (owner's ruling; two-hole gate cases on X and on the diagonal) |
| px, py | The extent of the hole centres along X and Y. For the four-corner pattern that is the pitch; for any other pattern it is only the extent, and `rectangular` is then False | the design note defines pitch for the family only |
| Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face. For an accepted axis the two differ by at most (T / 2) x 1e-12: 7e-12 mm for the thickest generated plate (14 mm) | one measurement shared with the scorer |
| No hole | D, mx, my, px, py are `None`, never zero | a missing variable is not a value |
| Stepped, counterbored or offset hole | `out_of_scope`: two different cylinders, one with its axis strictly inside the other (two 10 mm holes 5.0 mm apart are not nested; 4.999 mm apart they are). Judged on the unrounded axis and diameter of every concave cylinder face | D is not one number. The scorer's grouping rounds diameters to 1e-4 mm and hid a 1e-6 step |
| Holes of different diameters | `out_of_scope` when the measured diameters differ by more than the dimension slack, 1e-9 mm. Values are binary doubles: holes written 10 and 10.000000001 measure 1.00000008e-9 apart and are refused | D is one number in v1; the verdict must not depend on which hole comes first |
| Tilted or cross hole | `out_of_scope` for any concave cylinder whose axis makes an angle of more than 1e-12 rad with Z (the angle, not its X and Y components separately). On a 4 mm plate with 10 mm holes the kernel reads T = 4.00000000001 at that slack; that is an example at this scale, not a general accuracy bound. The shift between top face and mid-plane grows with T as stated above | a 1e-8 rad tilt was `ok` with a margin wrong by 2e-8 mm |
| Supported size | `out_of_scope` when any cylindrical face is under 0.01 mm in diameter (exactly 0.01 mm is measured). This comes before the form check, so a fillet under that size is a size refusal, not the `form_violation` of amendment 1 | the probe that tells a hole from a boss cannot classify smaller ones; refusing is honest, reporting n = 0 was not |
| Failed scope scan | `out_of_scope`, with the reason | it used to raise an exception out of the map |
| Spline surfaces | `form_violation`, with no hole recognised. A known false rejection kept on purpose (scorer review round 3). The kernel pads a spline bounding box by 2e-7 mm, so L, W and T of such a part are not exact | soundness over coverage |
| Very thin edge wall | A hole whose wall is 1e-7 mm thick at a side face is a `form_violation` (the form check of scorer 0.5.0 refuses it). At 1e-6 mm and more it is `ok` with an exact margin. A known false rejection, like spline faces; changing it needs a new scorer version | soundness over coverage |
| centered, symmetric, rectangular | `centered`: the straight-line distance from the mean hole centre to the bounding-box centre is at most the form tolerance, 1e-7 mm (pinned at 0.99e-7 and 1.02e-7). `symmetric` and `rectangular` match hole positions coordinate by coordinate at the same tolerance, so a match may be up to 1.41e-7 mm off in a straight line. The `symmetric` match asks that some hole mirrors each hole, not a one-to-one pairing; that is enough because two holes that survive the scope rules are at least 0.005 mm apart, so no hole can mirror two | owner's ruling (fourth review): a 2D offset is judged by its length, as for the tilt limit |
| Old measurements | None are stored. A measurement made before the strict fields existed reads `strict` as False, and the map raises an error instead of observing it | a loud refusal, not a migration |

**One deviation from the design note, for the owner's approval.** Section
7.2 lists "extra pocket or slot" as `out_of_scope`. M1 reports it as
`form_violation`, unless one of the cylinder scope rules above applies
first. Reason: a separate pocket does not make any contract variable
ambiguous, amendment 1 already fails every unrequested feature, and telling
"a pocket" from "a fillet" would need feature recognition, which is new code
that no review has seen. The scope rules look only at cylinder axes. So a
pocket with large rounded corners can be `out_of_scope` (its corner
cylinders are nested), and a pocket that cuts into a hole without nesting
its axis is a `form_violation` whose numbers are diagnostic only. The map
does not claim to recognise features. Either verdict fails gate G3. The
first external review chose `form_violation` on one condition: that a
pocket cutting into a hole is refused by the scope rules. That condition
does not hold, as stated above. The third review accepted
`form_violation` as the conservative verdict with this narrowed wording.
The deviation still awaits the owner's approval.

### 3.1 External review of M1 (5 October 2026)

Report: `audit/l5-m1-audit.md`. It reproduced the gate (27 of 27), found no
score change on 3,161 saved answers under either scorer version, checked 180
ordinary constructions to 1e-9 mm, and required five changes. All are made
and pinned as `review_` cases of the gate.

A second review (`audit/l5-m1-v2-audit.md`) read the changes and confirmed
all five in the source, but ran in an environment that held only the
incremental bundle, so it could execute nothing from the repository. Its
boundary probes of the kernel agreed with the rules, and it asked for the
exact boundaries to be pinned and for two statements to be made precise.
Both are done: twelve `boundary_` cases, and the rows above on the hole
centre, on diameters and on the supported size.

A third review (`audit/l5-m1-v3-audit.md`, 7 October 2026) ran everything
locally: the gate and the three other suites pass, its 333 earlier parts
show no wrong value in an `ok` result, the 180 controls agree to 1e-9 mm,
and 3,161 saved answers score the same under both scorer versions. It found
R2 to R5 resolved and R1 partly: the tilt limit was applied to the X and Y
components separately, so a diagonal tilt of 1.3e-12 rad was accepted. The
limit is now on the angle, with both sides pinned in the gate. It also asked
for three statements above to be narrowed (what n counts, the scale of the
tilt example, pockets and the scope rules), which is done.

| # | Finding | Change |
|---|---|---|
| R1 | Holes tilted by 1e-8 rad were `ok` with a wrong margin; tilts up to 1e-6 rad were not refused | any tilt beyond 1e-12 rad is `out_of_scope` |
| R2 | A radius step of 1e-6 mm was reported as `form_violation` with a chosen D, because diameters were grouped after rounding | unrounded cylinder data kept by the strict measurement; nested cylinders refused |
| R3 | Diameters differing by 1e-8 mm were `ok`, with D taken from the first hole | compared at the dimension slack, 1e-9 mm |
| R4 | A cross bore of 0.2 micron was missed: the inward probe crossed it | probe limited to half a radius, an unclear result is an error, and features under 0.01 mm are refused |
| R5 | A failed scope scan made the map raise instead of refusing | explicit strict marker on the measurement; failures are `out_of_scope` |

### 3.2 Fourth review of M1 (27 November 2026)

Report: `audit/l5-m1-v4-audit.md`. Codex and an independent blind check
reviewed the C1 fix, the five advisory findings of the first review were
triaged, and the owner ruled on each. Changes:

- **A hole made of faces that disagree on its axis is refused** (row
  above). Adding the residual of the first review's symmetric-matching
  remark to the gate showed `ok` with n = 3 for one physical hole, through
  the real answer path. The fix-round blind review then showed `ok` with
  an mx wrong by 8e-8 mm for two halves on one side of the key. Both are
  refused, by the owner's rulings.
- **`centered` uses the straight-line distance** (row above).
- **Observation version 2** (section 3, opening paragraph).
- **The diagonal tilt limit (1e-12 rad) is bracketed to [1.0e-12,
  1.05e-12) rad** by a case refused at 1.05e-12 rad. Before, any threshold
  below 1.3e-12 passed.
- **Statements made precise:** what n counts (one uninterrupted
  cylinder, and how the 99% rule relates to design note 7.1), the pocket
  deviation, the thin edge wall, old measurements, and the `symmetric`
  match. Section 4 records the deferred items.

With these changes M1 is counted as audited, and M2 may start.

## 4. Open for later milestones

- **Family rules F1 and F2 belong to gate G3 (M3).** The map does not
  reject a hole that breaks out of the plate or two holes that overlap by
  less than the detector's cut-off; it measures them. The contract must
  carry "hole inside the material" and "holes do not overlap" as checked
  predicates.
- **`None` in predicates (M3).** A predicate on a variable that does not
  exist is false, never skipped.
- **Compiled items pin their basis (M2).** Each item records the observation
  version and the scorer basis it was compiled against.
- **Change detection** (design note 5.3) names 1e-6 mm. Under amendment 2
  the value should come from the scorer; to be fixed when G4 is built (M3).
- **The probe schedule and the prompt sentence of amendment 3** (M3).
- **Whether `form_violation` is folded into G3 or reported as its own gate
  G3a** (M3). The observation already keeps the two apart.
- **Latency (M3).** A plate with 100 holes takes about 8 seconds to observe.
  Intent probes multiply that; build and measurement timeouts stay in place.
- **Scope-scan probe point (M3).** The scan classifies each concave
  cylinder face with one probe placed at the midpoint of the face's
  parameter rectangle. On a trimmed face that point can lie off the face.
  With a tongue of material placed there, four bores tilted by 1e-9 rad
  became `form_violation` instead of `out_of_scope` (fourth review). This
  fails closed on every case tried, because a face that fools the probe
  also fails the form check; that is argued, not proven. The code fix is
  deferred to M3 by the owner's ruling (27 November 2026).
- **Diameter verdict and cut order (M3).** Faces of one hole may differ in
  diameter by up to 1e-9 mm, and the check that all through holes share one
  D compares one face per hole. Two holes whose halves differ in opposite
  directions (10 and 10.0000000009 in one, 10 and 9.9999999991 in the
  other) are therefore `out_of_scope` in one cut order and `ok` with
  D = 10.0 in the other (fourth review). The `ok` order reports a D within
  1e-9 mm of every face, so this is a false refusal in one order, not a
  wrong value. Deferred to M3 by the owner's ruling (27 November 2026).
- **Scorer path, next scorer version.** Two defects sit in frozen scorer
  code and wait for a new scorer version. First, `_z_aligned_cylinders` and
  `_off_axis_bore_count` in `measure.py` compare the X and Y components of
  an axis separately with `AXIS_TOL` = 1e-6, so a diagonal tilt up to
  1.41e-6 rad counts as a Z bore there; the scope scan's docstring has the
  same imprecision. Second, the hole grouping can split one cylinder
  across a rounding key, so scorer 0.5.0 sees one hole too few and fails
  a correct part. Both fail closed for the scorer, and the map refuses
  both cases before it uses those values.
name: ci
on: [push, pull_request]

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.11", "3.12"]
    runs-on: ${{ matrix.os }}
    defaults:
      run:
        working-directory: environments/cad_spec
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      # Pin only verifiers (0.4.1 has no verifiers.Rubric). constraints.txt
      # cannot be used here: its numpy==2.5.3 needs Python 3.12 or later.
      # The full pinned set is tested by the pinned-validation job.
      - run: pip install -e ".[dev]" "verifiers==0.3.1"
      - run: ruff check .
      - name: Lint repo scripts
        working-directory: .
        run: ruff check scripts
      - run: mypy cad_spec
      - run: pytest -q
      - name: Hand-labelled cases for scorer 0.5.0 (strict contract)
        working-directory: .
        run: python scripts/test_rubric_050.py
      - name: Adversarial rubric harness
        working-directory: .
        run: python scripts/test_rubric.py

  # The README promises the harness runs with nothing but cadquery installed,
  # from a plain checkout. Prove it on every push.
  clean-room:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install "cadquery==2.8.0"
      - run: python scripts/test_rubric.py
      - name: verifiers must not have been needed
        run: python -c "import importlib.util, sys; sys.exit(importlib.util.find_spec('verifiers') is not None)"

  # Pinned dependency set used for published results, plus the scorer
  # validation gate: zero false full credit, zero false rejection.
  pinned-validation:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: environments/cad_spec
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -c constraints.txt -e ".[dev]"
      - run: pytest -q
      - name: Failure-mode classifier self-test
        working-directory: .
        run: python scripts/test_failure_modes.py
      - name: Leaderboard ranking rules self-test
        working-directory: .
        run: python scripts/test_leaderboard.py
      - name: Experiment arms self-test (runner feedback, hint, verdict rules)
        working-directory: .
        run: python scripts/test_arms.py
      - name: Screening analysis self-test (learning signal, truncation split)
        working-directory: .
        run: python scripts/test_screening.py
      - name: L4 edit parser self-test (parser-edit provider, refusals, fallback)
        working-directory: .
        run: python scripts/test_parser_edit.py
      - name: L5 observation map, adversarial suite (milestone M1 gate)
        working-directory: .
        run: python scripts/test_l5_observation.py
      - name: Scoring gate with the system GL libraries (reference, L4 failure, full rollout, 64 at once)
        working-directory: .
        run: python scripts/gl_fallback_check.py --expect system --system-gl-note present --out /tmp/gl/system-gl
      - name: Scoring gate WITHOUT system GL/X11 (the Hosted Training image's condition)
        working-directory: .
        run: |
          L=/usr/lib/x86_64-linux-gnu; mkdir -p /tmp/hidden
          for f in $L/libGL.so.1* $L/libGLX.so.0* $L/libGLdispatch.so.0* $L/libX11.so.6* \
                   $L/libxcb.so.1* $L/libXau.so.6* $L/libXdmcp.so.6*; do
            [ -e "$f" ] && sudo mv "$f" /tmp/hidden/
          done
          sudo ldconfig
          status=0
          python scripts/gl_fallback_check.py --expect vendored --system-gl-note hidden --out /tmp/gl/gl-less || status=$?
          sudo mv /tmp/hidden/* "$L"/ && sudo ldconfig
          exit $status
      - name: Evidence manifests verify (any OS line endings)
        working-directory: .
        run: python scripts/verify_manifest.py results/training/run1/snapshots/*/manifest.json results/training/run1/snapshots/*/retry-*/manifest.json
      - name: Replay the run 1 test-split evaluations on Linux (fork sandbox, 0 mismatches)
        working-directory: .
        run: python scripts/replay_eval.py results/training/run1/eval/base-test.jsonl results/training/run1/eval/adapter-test.jsonl
      - name: Replication 1 answers replay on Linux and the committed verdict reproduces
        working-directory: .
        run: |
          python scripts/replay_eval.py results/training/replication1/eval/base-rep-run2.jsonl \
            results/training/replication1/eval/adapter-rep.jsonl results/training/replication1/eval/base-rep.jsonl
          python scripts/compare_replication.py \
            --base results/training/replication1/eval/base-rep-run2.jsonl \
            --adapter results/training/replication1/eval/adapter-rep.jsonl \
            --out /tmp/replication1/verdict > /dev/null
          diff /tmp/replication1/verdict.json results/training/replication1/verdict.json
          diff /tmp/replication1/verdict.md results/training/replication1/verdict.md
      - name: Training analysis self-test (registered verdict rules, refusals)
        working-directory: .
        run: python scripts/test_compare_training.py
      - name: Bridge check self-test and reproduction of the committed result
        working-directory: .
        run: |
          python scripts/test_bridge_check.py
          python scripts/bridge_check.py --out /tmp/bridge/bridge-check > /dev/null
          diff /tmp/bridge/bridge-check.json results/training/run1/bridge-check.json
          diff /tmp/bridge/bridge-check.md results/training/run1/bridge-check.md
      - name: Replication analysis and split self-test (registered rules, refusals, fingerprint, disjointness)
        working-directory: .
        run: python scripts/test_compare_replication.py
      - name: Replication split is solvable and locked (reference 240 of 240, unedited rev A 0 of 60)
        working-directory: .
        run: |
          python scripts/run_baseline.py --provider reference --tiers L1 L2 L3 L4 \
            --split replication --unlock-replication --out /tmp/rep-ref.jsonl --quiet
          python scripts/run_baseline.py --provider rev-a --tiers L4 \
            --split replication --unlock-replication --out /tmp/rep-reva.jsonl --quiet
          python - <<'PY'
          import json

          def rewards(path):
              return [r["reward"] for r in map(json.loads, open(path)) if "tier" in r]

          ref, reva = rewards("/tmp/rep-ref.jsonl"), rewards("/tmp/rep-reva.jsonl")
          assert len(ref) == 240 and min(ref) == 1.0, (len(ref), min(ref))
          assert len(reva) == 60 and max(reva) < 1.0, (len(reva), max(reva))
          print("reference 240/240, rev A 0/60")
          PY
      - name: Release check (every linked evidence file exists)
        working-directory: .
        run: python scripts/check_release.py
      - name: Mutation validation gate
        working-directory: .
        run: python scripts/validate_scorer.py --specs 10 --out /tmp/validation
      - name: Deterministic baselines reproduce
        working-directory: .
        run: |
          python scripts/run_baseline.py --provider parser-copy --tiers L0 L1 L2 --out /tmp/pc.jsonl --quiet
          python scripts/run_baseline.py --provider parser-template --tiers L3 --out /tmp/pt.jsonl --quiet
          python - <<'PY'
          import json

          def load(path):
              lines = [json.loads(l) for l in open(path) if l.strip()]
              end = [l["end"] for l in lines if "end" in l]
              assert end and end[0]["status"] == "complete", (path, end)
              return [l for l in lines if "tier" in l]  # result rows only

          by = {}
          for r in load("/tmp/pc.jsonl") + load("/tmp/pt.jsonl"):
              by.setdefault((r["tier"], r["run_id"]), []).append(r["reward"])
          got = {tier: v for (tier, _), v in by.items()}
          assert min(got["L0"]) == 1.0 and min(got["L1"]) == 1.0, got
          assert max(got["L2"]) == 0.0, got
          assert min(got["L3"]) == 1.0, got  # parser-template solves L3
          print({t: sum(v) / len(v) for t, v in got.items()})
          PY

  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t cad-spec .
      - name: Score the reference answer inside the locked-down container
        run: |
          docker run --rm --entrypoint python cad-spec -c "from cad_spec.tasks import TASKS, reference_solution; print(reference_solution(TASKS[0]))" > answer.py
          docker run --rm --network none --read-only --tmpfs /tmp:size=64m \
            --memory 2g --pids-limit 128 --cap-drop ALL --security-opt no-new-privileges \
            -v "$PWD/answer.py:/in/answer.py:ro" cad-spec score plate-01 /in/answer.py
                    ((-35.0, 25), (-35.00000000045, 25)), ((35.0, 25), (35.00000000045, 25))),
        "ok", NOMINAL,
        "two holes split on X in opposite directions: whichever faces are read, px is within 0.9e-9 of 70"),
    "review_two_holes_with_halves_0.45e-9_apart_other_order": (
        split_holes("[(-35, -25), (35, -25)]",
                    ((-35.00000000045, 25), (-35.0, 25)), ((35.00000000045, 25), (35.0, 25))),
        "ok", NOMINAL, "the same part, other cut order"),
    "review_two_holes_with_halves_0.49e-9_apart_on_the_diagonal": (
        split_holes("[(-35, 25), (35, -25)]", ((-35.0, -25.0), (-35.00000000035, -25.00000000035)),
                    ((35.0, 25.0), (35.00000000035, 25.00000000035))),
        "ok", NOMINAL,
        "opposite corners split outwards by (3.5e-10, 3.5e-10): px and py are each within 0.7e-9 of the nominal"),
    # --- nothing to measure
    "two_solids": (
        BASE + 'result = cq.Compound.makeCompound([result.val(), cq.Solid.makeBox(5, 5, 5, cq.Vector(200, 0, 0))])\n',
        "not_single_solid", {}, "an unfused second body"),
    "no_result": (HEAD + 'plate = cq.Workplane("XY").box(100, 80, 4)\n', "build_error", {},
                  "the answer binds no part: gate G1, not the map"),
}


# Cases built from separate faces: the rule their refusal must come from (None
# for an `ok` case), the number of holes the measurement must make (five for
# the grouping rule, so the map's copy of the grouping key keeps agreeing with
# the measurement), and the number of concave cylinder faces the kernel must
# keep (one more per split hole, or the case would test nothing).
REASONS: dict[str, tuple[str | None, int | None, int]] = {
    "review_hole_split_across_position_key": ("two hole groups", 5, 5),
    "review_hole_split_across_diameter_key": ("two hole groups", 5, 5),
    "review_hole_halves_8e-8_apart_at_a_corner": ("axes more than", None, 5),
    "review_hole_halves_8e-8_apart_other_order": ("axes more than", None, 5),
    "boundary_hole_halves_0.45e-9_apart": (None, None, 5),
    "boundary_hole_halves_0.55e-9_apart": ("axes more than", None, 5),
    "boundary_hole_halves_0.57e-9_apart_on_the_diagonal": ("axes more than", None, 5),
    "review_two_holes_with_halves_0.45e-9_apart": (None, None, 6),
    "review_two_holes_with_halves_0.45e-9_apart_other_order": (None, None, 6),
    "review_two_holes_with_halves_0.49e-9_apart_on_the_diagonal": (None, None, 6),
}


def measured(code: str) -> tuple[int, int]:
    """Holes made by the strict measurement, and concave Z cylinder faces it saw."""
    from cad_spec.measure import build_and_measure

    m = build_and_measure(code, strict=True)
    return len(m.holes), len(m.scope_axes or [])


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
        if name in REASONS:
            phrase, holes, faces = REASONS[name]
            got_holes, got_faces = measured(code)
            if phrase is not None and phrase not in reason:
                bad.append(f"reason: expected the rule '{phrase}', got '{reason}'")
            if holes is not None and got_holes != holes:
                bad.append(f"the measurement made {got_holes} holes, expected {holes}")
            if got_faces != faces:
                bad.append(f"the kernel kept {got_faces} cylinder faces, expected {faces}: the case tests nothing")
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

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$names = '"'cad-spec-geometric-observation','cad-spec-uncertainty-and-error','cad-spec-conformity-decision','cad-spec-datum-gdt-reasoning','cad-spec-numerical-validation'; foreach("'$n in $names) { Get-Content ".claude/skills/$n/SKILL.md" }; Get-Content environments/cad_spec/cad_spec/l5/__init__.py; Select-String -Path environments/cad_spec/cad_spec/measure.py -Pattern '"'def _classify_cylinders|def _scope|scope_axes|COAXIAL_DP|class Hole|class Measurements' -Context 2,8" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 327ms:
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
"""L5, region-graded change orders. Governing design: docs/design/.

Built in milestones. M1 (this package so far): the observation map, which
turns a measured solid into contract variables, with the strict form check of
scorer 0.5.0 and an explicit out-of-scope verdict.
"""

from .observation import (
    EPS_DIM_MM,
    EPS_FORM_MM,
    FORM_VIOLATION,
    MIN_CYLINDER_DIAMETER_MM,
    NOT_SINGLE_SOLID,
    OBSERVATION_VERSION,
    OK,
    OUT_OF_SCOPE,
    SCORER_BASIS,
    Observation,
    observe,
    observe_code,
)

__all__ = [
    "EPS_DIM_MM",
    "EPS_FORM_MM",
    "FORM_VIOLATION",
    "MIN_CYLINDER_DIAMETER_MM",
    "NOT_SINGLE_SOLID",
    "OBSERVATION_VERSION",
    "OK",
    "OUT_OF_SCOPE",
    "SCORER_BASIS",
    "Observation",
    "observe",
    "observe_code",
]

  environments\cad_spec\cad_spec\measure.py:82:AXIS_TOL = 1e-6
  environments\cad_spec\cad_spec\measure.py:83:# Decimal places used when grouping coaxial cylindrical faces into 
features.
> environments\cad_spec\cad_spec\measure.py:84:COAXIAL_DP = 3
  environments\cad_spec\cad_spec\measure.py:85:# Fraction of the cylinder radius (dimensionless) to back off FROM THE 
SURFACE
  environments\cad_spec\cad_spec\measure.py:86:# before probing membership, floored at PROBE_INSET_MIN_MM so hairline 
bores
  environments\cad_spec\cad_spec\measure.py:87:# still probe strictly inside their own air channel. Asking "does 
material
  environments\cad_spec\cad_spec\measure.py:88:# continue immediately inward of this surface" stays correct on hollow 
parts;
  environments\cad_spec\cad_spec\measure.py:89:# probes deeper toward the axis lie there - a shelled box's 
outer-fillet axis
  environments\cad_spec\cad_spec\measure.py:90:# sits in open cavity, so halfway-to-axis air reads as a phantom bore.
  environments\cad_spec\cad_spec\measure.py:91:PROBE_INSET_FRACTION = 0.05
  environments\cad_spec\cad_spec\measure.py:92:# Absolute floor for the surface-inset probe distance, in millimetres.
  environments\cad_spec\cad_spec\measure.py:225:
  environments\cad_spec\cad_spec\measure.py:226:@dataclass
> environments\cad_spec\cad_spec\measure.py:227:class Hole:
  environments\cad_spec\cad_spec\measure.py:228:    """A closed, Z-parallel bore: one diameter at one axis position.
  environments\cad_spec\cad_spec\measure.py:229:
  environments\cad_spec\cad_spec\measure.py:230:    `depth` is the TOTAL axial length the bore wall covers, computed 
as the
  environments\cad_spec\cad_spec\measure.py:231:    union of every coaxial face's Z interval (0.3.0 fix: it used to be 
the
  environments\cad_spec\cad_spec\measure.py:232:    tallest single face, so a bore cut by a symmetric cutter that left 
two
  environments\cad_spec\cad_spec\measure.py:233:    stacked 3 mm faces in a 6 mm plate read as 3 mm deep). 
`z_min`/`z_max`
  environments\cad_spec\cad_spec\measure.py:234:    bound that union; `segments` > 1 means the wall is interrupted 
along Z.
  environments\cad_spec\cad_spec\measure.py:235:    """
  environments\cad_spec\cad_spec\measure.py:266:
  environments\cad_spec\cad_spec\measure.py:267:@dataclass
> environments\cad_spec\cad_spec\measure.py:268:class Measurements:
  environments\cad_spec\cad_spec\measure.py:269:    length: float          # bbox X
  environments\cad_spec\cad_spec\measure.py:270:    width: float           # bbox Y
  environments\cad_spec\cad_spec\measure.py:271:    thickness: float       # bbox Z
  environments\cad_spec\cad_spec\measure.py:272:    volume: float          # mm^3
  environments\cad_spec\cad_spec\measure.py:273:    solid_count: int       # >1 means disconnected pieces
  environments\cad_spec\cad_spec\measure.py:274:    holes: list[Hole] = field(default_factory=list)
  environments\cad_spec\cad_spec\measure.py:275:    # Envelope datums (0.3.0). Sizes alone are translation-invariant, 
which
  environments\cad_spec\cad_spec\measure.py:276:    # let a plate shifted off its hole pattern keep full credit; 
edge-margin
  environments\cad_spec\cad_spec\measure.py:305:    strict: bool = False                   # produced by 
measure(strict=True)
  environments\cad_spec\cad_spec\measure.py:306:    off_axis_concave: int | None = None    # concave cylindrical faces 
whose axis is not exactly along Z
> environments\cad_spec\cad_spec\measure.py:307:    scope_axes: list[tuple[float, float, float]] | None = None  # 
every concave Z cylinder face: x, y, raw diameter
  environments\cad_spec\cad_spec\measure.py:308:    min_cylinder_diameter: float | None = None  # smallest cylindrical 
face of any kind, mm (None: no cylinder)
  environments\cad_spec\cad_spec\measure.py:309:    scope_error: str | None = None         # why the scope information 
could not be collected
  environments\cad_spec\cad_spec\measure.py:310:    extra_volume: float | None = None     # mm^3 of material outside 
the ideal part
  environments\cad_spec\cad_spec\measure.py:311:    missing_volume: float | None = None   # mm^3 of the ideal part 
that is absent
  environments\cad_spec\cad_spec\measure.py:312:    shape_error: str | None = None
  environments\cad_spec\cad_spec\measure.py:313:
  environments\cad_spec\cad_spec\measure.py:314:    @property
  environments\cad_spec\cad_spec\measure.py:315:    def hole_count(self) -> int:
  environments\cad_spec\cad_spec\measure.py:549:
  environments\cad_spec\cad_spec\measure.py:550:
> environments\cad_spec\cad_spec\measure.py:551:def _scope_scan(solid: Any) -> tuple[int, float | None]:
  environments\cad_spec\cad_spec\measure.py:552:    """What the L5 observation map must know before it trusts the 
holes.
  environments\cad_spec\cad_spec\measure.py:553:
  environments\cad_spec\cad_spec\measure.py:554:    Returns (concave cylindrical faces not exactly along Z, smallest 
diameter
  environments\cad_spec\cad_spec\measure.py:555:    of any cylindrical face). The first is a tilted or cross hole, 
whole or
  environments\cad_spec\cad_spec\measure.py:556:    partial: `off_axis_bores` (0.4.0, diagnostics) only counts bores 
that
  environments\cad_spec\cad_spec\measure.py:557:    close into a full cylinder, which a tilted hole through a thin 
plate does
  environments\cad_spec\cad_spec\measure.py:558:    not, and it accepts tilts up to 1e-6 rad. The second lets the map 
refuse
  environments\cad_spec\cad_spec\measure.py:559:    features too small for the inward probe to classify.
  environments\cad_spec\cad_spec\measure.py:690:            t0 = loc.X() * dx + loc.Y() * dy + loc.Z() * dz
  environments\cad_spec\cad_spec\measure.py:691:            base = (loc.X() - t0 * dx, loc.Y() - t0 * dy, loc.Z() - t0 
* dz)
> environments\cad_spec\cad_spec\measure.py:692:            key = (*(round(c, COAXIAL_DP) for c in (dx, dy, dz, 
*base)), round(2 * r, 4))
  environments\cad_spec\cad_spec\measure.py:693:            area, spans = groups.setdefault(key, ([0.0], []))
  environments\cad_spec\cad_spec\measure.py:694:            area[0] += face.Area()
  environments\cad_spec\cad_spec\measure.py:695:            v1, v2 = sorted((ad.FirstVParameter(), 
ad.LastVParameter()))
  environments\cad_spec\cad_spec\measure.py:696:            sense = 1.0 if (d.X(), d.Y(), d.Z()) == (dx, dy, dz) else 
-1.0
  environments\cad_spec\cad_spec\measure.py:697:            spans.append(tuple(sorted((sense * (t0 + v1), sense * (t0 
+ v2)))))
  environments\cad_spec\cad_spec\measure.py:698:        count = 0
  environments\cad_spec\cad_spec\measure.py:699:        for key, (area, spans) in groups.items():
  environments\cad_spec\cad_spec\measure.py:700:            covered = sum(hi - lo for lo, hi in 
_merge_intervals(spans))
  environments\cad_spec\cad_spec\measure.py:717:
  environments\cad_spec\cad_spec\measure.py:718:
> environments\cad_spec\cad_spec\measure.py:719:def _classify_cylinders(solid: Any, *, strict: bool = False, z_ref: 
float | None = None,
> environments\cad_spec\cad_spec\measure.py:720:                        scope_axes: list[tuple[float, float, float]] | 
None = None,
  environments\cad_spec\cad_spec\measure.py:721:                        ) -> tuple[list[Hole], list[PartialBore]]:
  environments\cad_spec\cad_spec\measure.py:722:    """Closed internal bores, plus rejected concave groups as 
diagnostics.
  environments\cad_spec\cad_spec\measure.py:723:
  environments\cad_spec\cad_spec\measure.py:724:    Two independent discriminators, because hollow geometry defeats 
either
  environments\cad_spec\cad_spec\measure.py:725:    alone:
  environments\cad_spec\cad_spec\measure.py:726:
  environments\cad_spec\cad_spec\measure.py:727:    1. Membership probed JUST INSIDE the cylindrical surface: material 
there
  environments\cad_spec\cad_spec\measure.py:728:       means the face is convex - an external round, a boss, or the 
outer
  environments\cad_spec\cad_spec\measure.py:759:        if classifier.State() == TopAbs_State.TopAbs_IN:
  environments\cad_spec\cad_spec\measure.py:760:            continue  # material immediately inward => convex 
round/fillet/boss/wall
> environments\cad_spec\cad_spec\measure.py:761:        if scope_axes is not None:
> environments\cad_spec\cad_spec\measure.py:762:            scope_axes.append((cx, cy, 2 * radius))  # before any 
rounding or grouping
> environments\cad_spec\cad_spec\measure.py:763:        key = (round(cx, COAXIAL_DP), round(cy, COAXIAL_DP))
  environments\cad_spec\cad_spec\measure.py:764:        diameter = round(2 * radius, 4)
  environments\cad_spec\cad_spec\measure.py:765:        raw.setdefault((key, diameter), (2 * radius, cx, cy))
  environments\cad_spec\cad_spec\measure.py:766:        area_acc, intervals = features.setdefault(key, 
{}).setdefault(diameter, ([0.0], []))
  environments\cad_spec\cad_spec\measure.py:767:        area_acc[0] += face.Area()
  environments\cad_spec\cad_spec\measure.py:768:        intervals.append((fbb.zmin, fbb.zmax))
  environments\cad_spec\cad_spec\measure.py:769:
  environments\cad_spec\cad_spec\measure.py:770:    holes: list[Hole] = []
  environments\cad_spec\cad_spec\measure.py:771:    partial: list[PartialBore] = []
  environments\cad_spec\cad_spec\measure.py:910:        + _count(topo, TopAbs_VERTEX, TopAbs_EDGE)
  environments\cad_spec\cad_spec\measure.py:911:    )
> environments\cad_spec\cad_spec\measure.py:912:    scope_axes: list[tuple[float, float, float]] | None = [] if strict 
else None
  environments\cad_spec\cad_spec\measure.py:913:    holes, partial = _classify_cylinders(solid, strict=strict, 
z_ref=(bb.zmin + bb.zmax) / 2,
> environments\cad_spec\cad_spec\measure.py:914:                                         scope_axes=scope_axes)
  environments\cad_spec\cad_spec\measure.py:915:    for h in holes:
  environments\cad_spec\cad_spec\measure.py:916:        h.open = _bore_is_open(solid, h, bb.zmin, bb.zmax)
  environments\cad_spec\cad_spec\measure.py:917:    conformance: bool | None = None
  environments\cad_spec\cad_spec\measure.py:918:    boundary: bool | None = None
  environments\cad_spec\cad_spec\measure.py:919:    off_axis_concave: int | None = None
  environments\cad_spec\cad_spec\measure.py:920:    min_cylinder: float | None = None
  environments\cad_spec\cad_spec\measure.py:921:    scope_error: str | None = None
  environments\cad_spec\cad_spec\measure.py:922:    extra_volume = missing_volume = None
  environments\cad_spec\cad_spec\measure.py:960:        strict=strict,
  environments\cad_spec\cad_spec\measure.py:961:        off_axis_concave=off_axis_concave,
> environments\cad_spec\cad_spec\measure.py:962:        scope_axes=scope_axes,
  environments\cad_spec\cad_spec\measure.py:963:        min_cylinder_diameter=min_cylinder,
  environments\cad_spec\cad_spec\measure.py:964:        scope_error=scope_error,
  environments\cad_spec\cad_spec\measure.py:965:        extra_volume=extra_volume,
  environments\cad_spec\cad_spec\measure.py:966:        missing_volume=missing_volume,
  environments\cad_spec\cad_spec\measure.py:967:        shape_error=shape_error,
  environments\cad_spec\cad_spec\measure.py:968:    )
  environments\cad_spec\cad_spec\measure.py:969:
  environments\cad_spec\cad_spec\measure.py:970:



exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command 'Get-Content .claude/skills/cad-spec-datum-gdt-reasoning/SKILL.md; Get-Content .claude/skills/cad-spec-numerical-validation/artefact-ladder.md; Get-Content environments/cad_spec/cad_spec/measure.py | Select-Object -Skip 719 -First 100; Get-Content environments/cad_spec/cad_spec/l5/observation.py | Select-Object -First 113; Get-ChildItem .venv/Scripts/python*; Get-Content scripts/test_l5_observation.py | Select-Object -First 48' in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 271ms:
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
                    feature too small to classify, one hole whose faces
                    disagree on its axis). The map refuses loudly
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

OBSERVATION_VERSION = "2"  # 2: centered by straight-line distance; split and spread refusals (fourth review)
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
# restated here. The gate cases review_hole_split_across_* pin it, and check
# that the measurement really splits those parts.
_DIAMETER_KEY_DP = 4

# The faces of one hole must agree on its axis to half the dimension slack, so
# that an extent combining two holes (px, py) stays within the slack.
SPREAD_LIMIT_MM: float = EPS_DIM_MM / 2

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




    Directory: D:\10_PROJECTS\cad-engineering\cad-spec-env\.venv\Scripts


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----        26/11/2026     18:38         274424 python.exe                                                           
-a----        26/11/2026     18:38         263400 pythonw.exe                                                          
#!/usr/bin/env python3
"""Adversarial suite for the L5 observation map (milestone M1 exit gate).

Each case is a hand-built model with the outcome a careful engineer expects:
the verdict (ok, form_violation, out_of_scope, not_single_solid, build_error)
and, where the part is measurable, the contract variables. The map passes the
gate only if every case gives exactly that.

Design note section 7.2, plus the counterexamples of the four scorer review
rounds. Run it on every change to the map or to the measurement:

    python scripts/test_l5_observation.py [--out results/l5/m1-observation-suite.md]

results/l5/m1-observation-suite.md is generated: this script rewrites it in
place and writes a header saying so (CLAUDE.md, rules 3 and 8 name this one
file). Verification runs write --out to a temporary folder.
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



exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$env:PYTHONDONTWRITEBYTECODE='"'1'; "'$env:PYTHONIOENCODING='"'utf-8'; .venv/Scripts/python.exe -B scripts/test_l5_observation.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '.venv/Scripts/ruff.exe check --no-cache scripts/test_l5_observation.py environments/cad_spec/cad_spec/l5/observation.py; Get-Content audit/l5-m1-v4-audit.md; Get-ChildItem environments/cad_spec/tests -Name; git diff --check ddd4e14601b144db17d17c6b638de99f3b494176' in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 785ms:
All checks passed!
# L5 M1 audit, round 4: review of the C1 fix and triage of the open advisory findings

**Status: FINAL, 27 November 2026.** A record by the project, written in
one session on branch `fix/l5-m1-audit` (from `main` at `ddd4e14`). Unlike
the three earlier files in this folder, it is not an external audit by a
separate agent. It has two parts:

- **Sections 1 to 7, the triage round.** Two reviews of commit `4e26d30`
  (one Codex, one fresh-context Claude agent), a check of every finding they
  raised, and a proposed action for the five advisory findings still open
  from the first review. Nothing was changed in that round. The sections are
  kept as written; section 8 lists what turned out wrong.
- **Sections 8 to 12, the fix round.** The owner's rulings, the changes, a
  Codex review and two blind reviews of the full diff, their triage, the
  checks, and the final verdict on M1.

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
  docstring) needs Bilal's explicit go and a release with a version bump
  (CLAUDE.md rule 5). If it can change a recorded observation it also bumps
  `OBSERVATION_VERSION`. None is proposed for this round.
- Legacy detector lines `measure.py:639` and `:674` are scored code: only a
  new scorer version may change them (rule 4).
- New gate cases (B3) regenerate `results/l5/m1-observation-suite.md`, so
  they wait for the B2a ruling (rule 3).
- `docs/design/L5-amendments.md` is a design record, not a registered
  record under rule 3. The documentation fixes (B1, B6, B7, A1 to A5) can be
  written there on this branch.

## 6. Recommendation

**Yes, M1 can be counted as audited once the fixes proposed above are
applied.** The yes is conditional on four things:

1. Bilal accepts the dispositions that are his to make: carrying A1's code
   fix past the start of M2 (deferred to M3), A3 (per-axis operators), A4
   (known false rejection), the pocket deviation (B1), B7, and the B2a and
   B2b rulings.
2. The documentation fixes (B1, B6, B7, A1 to A5) are written into
   `docs/design/L5-amendments.md`.
3. The B3 gate case is added and the gate rerun green, in whatever form the
   B2a ruling allows.
4. A short blind check of that fix diff finds nothing. It touches only
   documents and one test case, so a full external round is not needed.

Why. Two independent reviews of the C1 fix found no defect in the code. The
local runs agree: gate 60/60, kernel components as derived by hand, scorer
suites unchanged, no scorer path reads the scan. Of the thirteen findings
triaged (Codex's verdict, B1 to B7, A1 to A5), none produces a wrong value
under `ok`, a score change or a changed recorded verdict. The two confirmed
code gaps are A1 and B4. A1 fails closed in the reproduced case, and the
argument in section 4.2 says a fooled probe always needs a face that fails
R9, so it only changes the refusal reason. B4 is outside L5 and in frozen
scorer code. Every other finding is a documentation gap, a test-tightness
gap or an owner ruling.

What would turn this into a no: a construction where a fooled probe (A1)
yields `ok`, or the A2 residual (two surviving faces within 1e-7 mm
straddling a grouping key) giving n too high under `ok`. Neither was
reproduced; the first is argued against, the second is untested.

## 7. Proposed follow-ups (not applied in this round)

- `docs/design/L5-amendments.md`: the B1, B6, B7 and A1 to A5 text above;
  section 2 milestone status for M1 to "audited" once section 6 holds.
- `scripts/test_l5_observation.py`: the B3 diagonal case.
- `audit/README.md`: a row for this file.
- `CLAUDE.md` (State section), `.workshop/NOW.md`, `.workshop/LOG.md`: M1
  audit status once accepted.
- `CHANGELOG.md` "Unreleased": an entry for the document and gate changes.

## Appendix A. Reproductions (constructions and raw output)

Run on 27 November 2026 with the repo `.venv`, `CAD_SPEC_SANDBOX=reuse`, the
package imported from this checkout. `plate(points, d)` is the gate's
reference plate:

```python
import cadquery as cq
result = cq.Workplane("XY").box(100, 80, 4).faces(">Z").workplane().pushPoints(POINTS).hole(D)
```

| Case | POINTS (D = 10 unless stated) | Expected from construction |
|---|---|---|
| A3 shift s | the four corners (+/-35, +/-25), each moved by (+s, +s), s in {0.4e-7, 0.8e-7, 1.2e-7} | centered per axis iff s <= 1e-7; symmetric iff 2s <= 1e-7; mx = my = 15 - s |
| A2 duplicate 5e-8 | the four corners plus (35.00000005, 25) | n = 4 |
| A2 near axis 0.004 | the four corners plus (35.004, 25) | out_of_scope (nested) |
| A2 straddle | (+/-35.00049996, +/-25) plus (35.00050004, 25) | n = 4 (one physical hole per corner) |
| A4 ligament lig | (+/-(45 - lig), +/-25), lig in {1e-7, 1e-6, 1e-5, 1e-3} | ok, mx = 5 + lig |

A1 construction (four bores tilted 1e-9 rad about Y, then a 1 mm cube
centred on the UV-rectangle midpoint of every cylindrical face):

```python
import math, cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_SurfaceType
deg = 1e-9 * 180 / math.pi
part = cq.Workplane("XY").box(100, 80, 4)
for x, y in [(-35, -25), (-35, 25), (35, -25), (35, 25)]:
    tool = cq.Workplane("XY").circle(5).extrude(8, both=True).rotate((0, 0, 0), (0, 1, 0), deg)
    part = part.cut(tool.translate((x, y, 0)))
mids = []
for f in part.val().Faces():
    a = BRepAdaptor_Surface(f.wrapped)
    if a.GetType() == GeomAbs_SurfaceType.GeomAbs_Cylinder:
        q = a.Value((a.FirstUParameter() + a.LastUParameter()) / 2, (a.FirstVParameter() + a.LastVParameter()) / 2)
        mids.append((q.X(), q.Y(), q.Z()))
for q in mids:
    part = part.union(cq.Workplane("XY").box(1, 1, 1).translate(q))
```

A5: a strict `Measurements` of the reference plate with the five L5 fields
removed from its `__dict__`, pickled and unpickled, then passed to
`observe`; and the full strict object round-tripped through pickle.

Raw output, `advisory_repro.py`:

```text
{"case": "A3_pattern_shift_diag_4.0e-08", "expected": "centered per-axis |s|<=1e-7; symmetric iff 2s<=1e-7", "status": "ok", "reason": "", "values": {"n": 4, "D": 10.0, "mx": 14.999999959999997, "my": 14.99999996, "centered": true, "symmetric": true, "rectangular": true}}
{"case": "A3_pattern_shift_diag_8.0e-08", "expected": "centered per-axis |s|<=1e-7; symmetric iff 2s<=1e-7", "status": "ok", "reason": "", "values": {"n": 4, "D": 10.0, "mx": 14.99999992, "my": 14.99999992, "centered": true, "symmetric": false, "rectangular": true}}
{"case": "A3_pattern_shift_diag_1.2e-07", "expected": "centered per-axis |s|<=1e-7; symmetric iff 2s<=1e-7", "status": "ok", "reason": "", "values": {"n": 4, "D": 10.0, "mx": 14.999999879999997, "my": 14.99999988, "centered": false, "symmetric": false, "rectangular": true}}
{"case": "A2_duplicate_axis_5e-8", "expected": "n=4: duplicates collapse to one group", "status": "ok", "reason": "", "values": {"n": 4, "D": 10.0, "mx": 15.0, "my": 15.0, "centered": true, "symmetric": true, "rectangular": true}}
{"case": "A2_near_axis_0.004", "expected": "out_of_scope (nested)", "status": "out_of_scope", "reason": "two different cylinders at one hole position (counterbore, stepped or offset hole)", "values": {"n": null, "D": null, "mx": null, "my": null, "centered": null, "symmetric": null, "rectangular": null}}
{"case": "A4_edge_ligament_1e-07", "expected": "ok, mx=5.0000001", "status": "form_violation", "reason": "the edges do not lie on the faces at the form tolerance; 0.000 mm3 extra, 0.000 mm3 missing outside a 0.005 mm band", "values": {"n": 4, "D": 10.0, "mx": 5.000000100000001, "my": 15.0, "centered": true, "symmetric": true, "rectangular": true}}
{"case": "A4_edge_ligament_1e-06", "expected": "ok, mx=5.000001", "status": "ok", "reason": "", "values": {"n": 4, "D": 10.0, "mx": 5.0000009999999975, "my": 15.0, "centered": true, "symmetric": true, "rectangular": true}}
{"case": "A4_edge_ligament_1e-05", "expected": "ok, mx=5.00001", "status": "ok", "reason": "", "values": {"n": 4, "D": 10.0, "mx": 5.000010000000003, "my": 15.0, "centered": true, "symmetric": true, "rectangular": true}}
{"case": "A4_edge_ligament_1e-03", "expected": "ok, mx=5.001", "status": "ok", "reason": "", "values": {"n": 4, "D": 10.0, "mx": 5.000999999999998, "my": 15.0, "centered": true, "symmetric": true, "rectangular": true}}
{"case": "A5_old_pickle", "strict_attr": false, "scope_axes": null}
{"case": "A5_old_pickle_observe", "result": "ValueError: observe() needs a strict measurement: measure(solid, strict=True)"}
{"case": "A5_strict_roundtrip", "expected": "ok, NOMINAL", "status": "ok", "reason": "", "values": {"n": 4, "D": 10.0, "mx": 15.0, "my": 15.0, "centered": true, "symmetric": true, "rectangular": true}}
{"case": "A1_control_tilt_1e-9", "expected": "out_of_scope (tilt)", "status": "out_of_scope", "reason": "a hole whose axis is not parallel to Z", "values": {"n": null, "D": null, "mx": null, "my": null, "centered": null, "symmetric": null, "rectangular": null}}
{"case": "A1_face_midpoints", "n_faces": 8, "mids": [[-40.0, -25.0, 1.0], [30.0, -25.0, 1.0], [-40.0, 25.0, 1.0], [30.0, 25.0, 1.0], [-40.0, -25.0, -1.0], [30.0, -25.0, -1.0], [-40.0, 25.0, -1.0], [30.0, 25.0, -1.0]]}
{"case": "A1_tongue_scan", "off_axis_concave": 0, "scope_error": null, "faces": 54}
{"case": "A1_tongue_at_midpoint", "expected": "rule: out_of_scope; safe worst case: form_violation", "status": "form_violation", "reason": "a face is neither a plane of the envelope nor a recognised bore; 0.000 mm3 extra, 1249.562 mm3 missing outside a 0.005 mm band", "values": {"n": 0, "D": null, "mx": null, "my": null, "centered": false, "symmetric": false, "rectangular": false}}
```

Raw output, `advisory_repro2.py` (probe state per cylindrical face, and the
straddle case):

```text
{"case": "A1_without_tongue", "faces": [{"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_OUT"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_OUT"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_OUT"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_OUT"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_OUT"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_OUT"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_OUT"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_OUT"}]}
{"case": "A1_with_tongue", "faces": [{"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_IN"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_IN"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_IN"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_IN"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_IN"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_IN"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_IN"}, {"r": 5.0, "tilt": "1.00e-09", "probe_state": "TopAbs_IN"}]}
{"case": "A2_straddle_rounding_key", "expected": "n=4 (one physical hole per corner)", "status": "ok", "reason": "", "n": 4, "symmetric": true, "rectangular": true, "holes": [[-35.00049996, -25.0, 10.0], [-35.00049996, 25.0, 10.0], [35.00049996, -25.0, 10.0], [35.00049996, 25.0, 10.0]], "scope_axes": [[-35.00049996, -25.0, 10.0], [35.00049996, -25.0, 10.0], [-35.00049996, 25.0, 10.0], [35.00049996, 25.0, 10.0]]}
```

## 8. Owner's rulings (27 November 2026) and corrections to sections 1 to 7

Sections 1 to 7 are the triage round as written before the rulings. They are
kept as written. Three statements in them turned out wrong or were overruled:

- **A2 was wrongly rejected.** Section 4.2 called the residual untested and
  guessed that it would give n one too high. Built as a gate case (one hole
  cut as two stacked halves kept as separate faces), it gave n one too low,
  under `ok`, through the real answer path. It is a confirmed defect (section 9).
- **A3: the proposal to keep the per-axis comparison was overruled.**
  `centered` now uses the straight-line distance.
- **Section 6's conditional "yes" is superseded** by the verdict in section 12.

| Finding | Ruling |
|---|---|
| B1, B6, B7, A4, A5 | Document in `L5-amendments.md` as proposed |
| B2a | `results/l5/` is a generated folder. Say so next to rule 3 of CLAUDE.md; files there carry a "generated by, do not edit" header |
| B2b | M1 ships in the next package release, together with verifiers 0.4 support. Recorded under "Unreleased" in CHANGELOG.md. No version bump in this PR |
| B3 | Add the diagonal tilt case at 1.05e-12 rad |
| B4 | Defer to the next scorer version; note it in the amendments |
| A1 | Document it, defer the code fix to M3. M2 may start |
| A2 | Document it, and add the residual as a gate case |
| A2 defect (raised during the fix round) | Refuse in `cad_spec/l5` when one cylinder is split across two hole groups of the measurement |
| A3 | `centered` uses the straight-line distance, implemented in `cad_spec/l5` only, with gate cases at the boundary |
| F1 (raised by the fix-round blind review) | Refuse in `cad_spec/l5` when the faces of one cylinder have axes more than 1e-9 mm apart |

The A2-defect and F1 rulings were asked for during the round, each with the
reproduction in hand, before any code for them was written. Neither needed a
change to `rubric.py`, `environment.py`, `measure.py`, a released scorer
version or a recorded verdict, so the A3 stop condition did not apply.

## 9. Fix round: what changed

```text
Skills consulted (fix round):
- cad-spec-metrology-router: the round changes decision rules of the L5 map
  (centered, two new refusals) and the gate.
- cad-spec-geometric-observation: n, mx, px and centered are observation
  operators; refusal over guessing.
- cad-spec-uncertainty-and-error: 1e-9 mm is numerical slack and 1e-7 mm is
  kernel tolerance; the 2e-9 bound on extents is stated, not hidden.
- cad-spec-datum-gdt-reasoning: centered is frame_bound in the declared XY
  frame.
- cad-spec-numerical-validation: every new gate case and every probe.
- cad-spec-conformity-decision: a refusal is preferred to a wrong number
  under ok.
Relevant principles:
- Geometric-observation procedure step 2 (decide which topology variations
  must give the same value): one hole cut as two faces must give the same n
  and mx as one hole cut in one go. When the measurement cannot guarantee
  that, the map refuses (A2 defect, F1).
- P17 / P19: the offset of the hole pattern from the plate centre is a vector
  in the declared XY frame. Its size is its straight-line length, as for the
  tilt rule. That is the A3 ruling, pinned at 0.99e-7 and 1.02e-7.
- P30 (false pass costs more than false rejection): n = 3 and an mx wrong by
  8e-8 mm under `ok` become `out_of_scope`. No construction was relaxed.
- P27 (a known bias is refused or bounded): faces of one hole up to 1e-9 mm
  apart are accepted, so the docstring and the amendments state that extents
  (px, py) are exact to 2e-9 mm (G1).
- P31 (truth from construction): every expected value of the 10 new cases was
  derived from the construction parameters before the run.
- P09 (can the suite see the error): each case built from separate faces
  checks that the kernel kept five faces, and the grouping cases check that the
  measurement made five holes. A merged case would otherwise pass while
  testing nothing (F5, G4).
Domain: exact_brep_analytic
```

| Finding | Ruling | What changed | Evidence |
|---|---|---|---|
| A3 | Straight-line `centered` | `observation.py`: `centered` = hypot(mean x - cx, mean y - cy) <= 1e-7 | Gate cases `boundary_pattern_0.99e-7_off_centre_is_centered` (ok) and `boundary_pattern_1.02e-7_off_centre_is_not_centered` (ok, centered False). Against main's map the second fails ("centered: expected False, measured True") |
| A2 defect | Refuse a split cylinder | `observation.py`: `_same_cylinder`, `_group_key` (position rounded to `COAXIAL_DP`, imported by name; diameter to 4, a literal in `measure.py` restated as `_DIAMETER_KEY_DP`), `_split`; `_nested` refactored to use `_same_cylinder` | Before: one hole cut as two halves 8e-8 mm apart around x = 20.0005 was `ok` with n = 3; 8e-10 mm apart diameters around 10.00005, the same (Appendix B). Gate cases `review_hole_split_across_position_key` and `review_hole_split_across_diameter_key`, both `out_of_scope` with the reason "two hole groups", both checked to make 5 measured holes. Both fail against main |
| F1 | Refuse an axis spread over 1e-9 | `observation.py`: `_axis_spread` | Before: two halves 8e-8 mm apart at a corner gave `ok` with mx = 14.99999992 in one cut order and 15.0 in the other (Appendix B). Cases at 8e-8 in both orders, 0.9e-9 (ok), 1.1e-9 and a diagonal 1.13e-9 (refused). All four refusal cases fail against main. Mutants (threshold 0.51e-9, threshold 1.9e-9, X and Y compared separately) each fail at least one case |
| A2 | Document | Amendments: the `symmetric` match is existential and why that is enough (distinct holes at least 0.005 mm apart) | Section 4.2 argument; confirmed by the fix-round blind review |
| B3 | 1.05e-12 rad case | Gate case `boundary_diagonal_tilt_1.05e-12_rad_is_refused` (6.016056848873644e-11 degrees about (1,1,0), components 7.42e-13) | The blind review's mutant (`hypot <= 1.25e-12`) now fails this case. It passed all 60 cases before |
| B2a | Generated folder | CLAUDE.md rule 3 exception; the gate writes the header "Generated by ... Do not edit by hand" into `results/l5/m1-observation-suite.md`; the gate's docstring says so | Tracked file regenerated once after the final case list; byte-identical to a scratch run (`cmp`) |
| B2b | Next release, no bump | CHANGELOG "Release plan" under Unreleased | `pyproject.toml` unchanged at 0.5.0 |
| B4 | Defer, note | Amendments section 4, "Scorer path, next scorer version" | No code change |
| A1 | Document, defer to M3 | Amendments section 4, "Scope-scan probe point (M3)" | No code change |
| B1 | Document | Pocket-deviation paragraph: first reviewer's condition, that it does not hold, the third review's acceptance, still awaiting the owner | `audit/l5-m1-audit.md:6139`, `audit/l5-m1-v3-audit.md:80` |
| B6 | Document | "What n counts": "one uninterrupted cylinder" | `observation.py` `_through` (`segments == 1`) |
| B7 | Document | "What n counts" says it refines design note 7.1, and that 99% only recognises the bore | Design note 7.1 |
| A4 | Document | Row "Very thin edge wall" (1e-7 mm refused, 1e-6 mm measured) | Section 4.2 runs |
| A5 | Document | Row "Old measurements" | Section 4.2 runs |
| M1 status | Follows section 12 | Amendments milestone table and section 3.2, CHANGELOG, CLAUDE.md state (dated 27 November), `.workshop/NOW.md`, `audit/README.md` row | This record |

Gate: 60 cases before, 70 after (+1 B3, +2 A3, +7 for the split and spread
rules). The case list is final; `results/l5/m1-observation-suite.md` reads
"70 of 70".

## 10. Fix-round reviews and their triage

| Review | Command or brief | Time | Result | Saved output |
|---|---|---:|---|---|
| Codex | `codex review --base main -c 'sandbox_mode="read-only"' -c 'approval_policy="never"'` | 86 s | No findings. It diffed the working tree against `ddd4e14` (nothing was committed, so that diff was the whole change set at that time) and ran the gate (66/66), the L5 pytest file (10) and ruff. It saw the tree before the F1 fix: not `_axis_spread`, not the G fixes | `.workshop/reviews/codex-fixround.md` |
| Blind checker | agent-workshop:blind-checker: the diff without `audit/` and `.workshop/`, the design note and amendments, the touched sources | 625 s | SHIP WITH FIXES; F1 to F9 | `.workshop/reviews/blind-fixround.md` |
| Blind checker, delta | a new instance on the diff after the F1 fix, focused on the parts changed since | 607 s | SHIP WITH FIXES; G1 to G5 | `.workshop/reviews/blind-delta-fixround.md` |

Codex was run once, as authorised. The delta re-review used only the blind
checker.

| ID | Source | Finding | Verdict | Evidence | Action |
|---|---|---|---|---|---|
| X1 | Codex | No actionable regression | agreed | Section 11 | None |
| F1 | Blind | Two halves 8e-8 mm apart at a corner: `ok`, mx depends on cut order | confirmed | Reproduced: mx = 14.99999992 or 15.0 (Appendix B, `probe_f1`) | Fixed by ruling (section 9) |
| F2 | Blind | `observation.py` changes at package 0.5.0; rule 5 not amended | confirmed (fact) | `pyproject.toml:5` | Covered by ruling B2b. Whether rule 5 needs a written exception like rule 3 is listed for Bilal |
| F3 | Blind | The rule 3 exception covers all of `results/l5/`; rule 8 not amended though `--out results/l5/...` writes over a tracked file | confirmed (fact) | CLAUDE.md rules 3 and 8 | The breadth is ruling B2a's wording. Narrowing to one file or a `generated/` folder, and a rule 8 sentence, are listed for Bilal |
| F4 | Blind | "Audited" written before the round's reviews finished, with F1 open | confirmed at the time | F1 was open | Resolved: F1 fixed and re-reviewed; status rests on section 12 |
| F5 | Blind | The gate pins the map's grouping literal, not its agreement with `measure.py` | confirmed | Mutation check in the blind report | Fixed: grouping cases check the measurement makes 5 holes |
| F6 | Blind | The gate checks verdicts, not reasons | confirmed (for the new cases) | `main()` of the gate | Fixed for the new cases built from separate faces: the 6 refusal cases check their reason phrase, and the 7th (an `ok` case) checks its face count. A reason check for every older case is listed |
| F7 | Blind | CHANGELOG read as if the tilt limit were 1.05e-12 | confirmed | CHANGELOG wording | Fixed |
| F8 | Blind | `OBSERVATION_VERSION` stays "1" after semantic changes | confirmed (fact) | `observation.py:48` | Listed for Bilal. Unreleased, and no compiled item records a version yet |
| F9 | Blind | CLAUDE.md state header dated 26 November | confirmed | CLAUDE.md:15 | Fixed (27 November) |
| G1 | Blind delta | px and py can change with cut order by up to 1.8e-9 mm under `ok` when two holes each have faces up to 1e-9 apart | confirmed | Reproduced: px = 70.0000000018 or 70.0 (Appendix B, `probe_g`) | Bounded and stated: docstring, amendments row and case reason say extents are exact to 2e-9 mm. Tightening the spread limit to 0.5e-9 (so extents stay within 1e-9) changes the ruled threshold: listed for Bilal |
| G2 | Blind delta | The D verdict depends on cut order when diameters inside two holes differ by under 1e-9 in opposite directions | confirmed; already on main | Reproduced: `out_of_scope` in one order, `ok` with D = 10.0 in the other (Appendix B) | Listed for Bilal (proposed: the D check over every face of the through holes). The `ok` order reports a D within 1e-9 of every face; the other order is a false refusal |
| G3 | Blind delta | The 1e-9 rule was bracketed only to [0.5e-9, 2e-9) and only along X | confirmed | Its mutants | Fixed: cases at 0.9e-9 (ok), 1.1e-9 and a diagonal 1.13e-9 (refused). Mutants killed (Appendix B) |
| G4 | Blind delta | The `ok` boundary case does not check that two faces were kept | confirmed | Gate code | Fixed: every case built from separate faces checks 5 kernel faces |
| G5 | Blind delta | "closer than 1e-7" against `<=` in the code | confirmed | `_same_cylinder` | Fixed: "at most 1e-7 mm" |

The G3, G4, G5 fixes and the G1 wording came after the delta review. They
were not reviewed again. They add gate cases and checks and change wording;
the only change to `observation.py` among them is a docstring.

## 11. Checks (final working tree)

| Check | Result |
|---|---|
| L5 gate, `--out` to scratch | 70/70, exit 0; the tracked `results/l5/m1-observation-suite.md` is byte-identical |
| Final gate against main's `observation.py` and `measure.py` | 63/70: exactly the 7 discriminating new cases fail |
| L5 pytest (`tests/test_l5_observation.py`) | 10 passed |
| `scripts/test_rubric_050.py` | 81/81 |
| `scripts/test_rubric.py` | 37/37 |
| `scripts/check_release.py` | all document links resolve |
| Full CLAUDE.md commit checks: `ruff check scripts`; package `ruff check .`, `mypy cad_spec`, `pytest -q`; `test_rubric.py`; every `scripts/test_*.py`; `check_release.py` | All pass. pytest 139 passed, 12 skipped (all Linux-only: fork sandbox, GL fallback). No script in the loop failed. Second run after the last change (173 s): the same results, plus `test_rubric_050` 81/81 and the gate 70/70; 12 scripts in the loop, none failed |
| Files touched in `cad_spec/` | `l5/observation.py` only. `measure.py`, `rubric.py`, `environment.py`, the frozen scripts and every recorded result outside `results/l5/` are unchanged (`git diff --stat main`) |
| Text | No em dash in any changed or new file; LF line endings |

## 12. Final verdict on M1

**Yes, if you accept G1 as stated: M1 is then audited once this branch is
merged.** If you do not accept a 2e-9 mm bound on px and py under `ok`, the
answer is no until the spread limit is 0.5e-9 mm (a one-constant change plus
its boundary cases).

- G1: under `ok`, px and py can move with the cut order by up to 1.8e-9 mm,
  against the 1e-9 mm slack. It is the same class as F1, only smaller. It is
  bounded and stated, not refused.
- G2: the D verdict can depend on cut order. The `ok` order reports a D
  within 1e-9 mm of every face, so it is a false refusal in the other order,
  not a wrong value.

Why:
- Every wrong value under `ok` found in this audit is now refused and pinned
  by gate cases that fail against the previous code:
  - one hole split across the measurement's grouping (n = 3);
  - the faces of one hole disagreeing on its axis (mx off by 8e-8 mm).
- The C1 fix was reviewed by Codex and a blind check. The fix round was
  reviewed by Codex (no findings) and a blind check on the 66-case tree, and
  by a second blind check after the F1 fix. All their confirmed findings
  inside this round's scope are fixed. Review coverage of the final code is
  thinner than that: `_axis_spread` was reviewed by one blind check only, and
  the G3 to G5 changes by none.
- What remains open is bounded or fails closed:
  - G1: extents are exact to 2e-9 mm, stated in the docs.
  - G2: an order-dependent false refusal; the `ok` order reports a D within
    1e-9 of every face.
  - A1: deferred to M3; it fails closed in every case tried.
  - B4 and the scorer-path grouping split: both fail closed for the scorer;
    the map refuses before using those values.
  - Owner decisions: the pocket deviation and the items listed below.

Caveats:
- The last small change set (G3 to G5, and the G1 wording) was not reviewed
  again.
- Linux `fork` mode was not run locally; CI runs it.

Listed for Bilal, not done in this round:
- A second read-only Codex review of the final diff. It would cover
  `_axis_spread` and the G fixes, which Codex has not seen. Not run, because
  the go was for one Codex call.
- G1: tighten the spread limit to 0.5e-9 so extents stay within 1e-9, or keep
  the stated 2e-9.
- G2: run the D check over every face of the through holes.
- F8: bump `OBSERVATION_VERSION`, or state that it stays "1" until release.
- F2, F3: written exceptions in rules 5 and 8, and whether the rule 3
  exception is narrowed to the one generated file.
- F6: reason checks for the older refusal cases of the gate.
- The pocket deviation (design note 7.2) still awaits approval.

## Appendix B. Fix-round reproductions (raw output)

Scripts in the session scratchpad
(`C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/`).
Expected values were written in each script's docstring before the run. The
constructions match the gate helper `split_hole`: three corner holes, and a
fourth hole cut as two half-depth cylinders with `clean=False`.

A2 defect through `observe_code` (`probe5.py`, `probe6.py`; before the fix):

```text
{"case": "straddle_8e-8", "status": "ok", "n": 3, ...}            halves at x 20.00049996 / 20.00050004
{"case": "same_side_8e-8", "status": "ok", "n": 4, ...}           halves at x 20.0004999 / 20.00049998
{"case": "same_axis", "status": "ok", "n": 4, ...}
{"case": "straddle_at_corner_35", "status": "ok", "n": 3, ...}    halves at x 35.00049996 / 35.00050004
{"case": "diameter_key_straddle", "status": "ok", "n": 3, "D": 10.00005, ...}   D 10.0000499996 / 10.0000500004
```

The same part in process, with and without face merging (`probe4.py`): with
`clean=True` the kernel keeps one face and n = 4. With `clean=False` it keeps
two faces (z -2..0 at x 20.00049996, z 0..2 at x 20.00050004). The measurement
makes two half-depth holes, and n = 3.

F1 (`probe_f1.py`; before the F1 fix):

```text
{"case": "lower_35.0", "expected_mx": 14.99999992, "status": "ok", "mx": 14.99999992, "px": 70.00000008, "n": 4}
{"case": "lower_35.00000008", "expected_mx": 14.99999992, "status": "ok", "mx": 15.0, "px": 70.0, "n": 4}
```

G1 and G2 (`probe_g.py`; final code):

```text
{"case": "G1_order0", "status": "ok", "px": 70.0000000018, "mx": 14.999999999099998}
{"case": "G1_order1", "status": "ok", "px": 70.0, "mx": 15.0}
{"case": "G2_order0", "status": "out_of_scope", "reason": "through holes of different diameters: D is not one number", "D": null}
{"case": "G2_order1", "status": "ok", "reason": "", "D": 10.0}
```

Mutants of `_axis_spread` against the three boundary cases (`mut_g3.py`, in process):

```text
shipped all pass
thr_0.51e-9 KILLED ['boundary_hole_halves_0.9e-9_apart']
thr_1.9e-9 KILLED ['boundary_hole_halves_1.1e-9_apart', 'boundary_hole_halves_1.13e-9_apart_on_the_diagonal']
per_axis KILLED ['boundary_hole_halves_1.13e-9_apart_on_the_diagonal']
```

B3 mutant (`measure.py` copy with `hypot <= 1.25e-12`, gate at 66 cases): 65/66, the failing case is
`boundary_diagonal_tilt_1.05e-12_rad_is_refused`.
__pycache__
conftest.py
test_binary_reward.py
test_environment.py
test_gl_fallback.py
test_l5_observation.py
test_measure.py
test_packaging.py
test_rollout_path.py
test_rubric_cases.py
test_scorer_versions.py
test_training_prep.py
warning: unable to access 'C:\Users\bgare/.config/git/ignore': Permission denied
warning: in the working copy of '.workshop/NOW.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CHANGELOG.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CLAUDE.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'audit/README.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/design/L5-amendments.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'environments/cad_spec/cad_spec/l5/observation.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'results/l5/m1-observation-suite.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'scripts/test_l5_observation.py', LF will be replaced by CRLF the next time Git touches it

 succeeded in 17451ms:
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
[ok ] review_hole_halves_8e-8_apart_at_a_corner out_of_scope
[ok ] review_hole_halves_8e-8_apart_other_order out_of_scope
[ok ] boundary_hole_halves_0.45e-9_apart   ok
[ok ] boundary_hole_halves_0.55e-9_apart   out_of_scope
[ok ] boundary_hole_halves_0.57e-9_apart_on_the_diagonal out_of_scope
[ok ] review_two_holes_with_halves_0.45e-9_apart ok
[ok ] review_two_holes_with_halves_0.45e-9_apart_other_order ok
[ok ] review_two_holes_with_halves_0.49e-9_apart_on_the_diagonal ok
[ok ] two_solids                           not_single_solid
[ok ] no_result                            build_error

73/73 cases as expected

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$env:PYTHONDONTWRITEBYTECODE='"'1'; .venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider environments/cad_spec/tests/test_l5_observation.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 7254ms:
..........                                                               [100%]
10 passed in 5.75s

exec
"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$env:PYTHONDONTWRITEBYTECODE='"'1'; "'$env:PYTHONIOENCODING='"'utf-8'; .venv/Scripts/python.exe -B scripts/test_rubric_050.py; .venv/Scripts/python.exe -B scripts/test_rubric.py" in D:\10_PROJECTS\cad-engineering\cad-spec-env
 succeeded in 25541ms:
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

codex
No actionable regressions were found against the specified merge base. The observation gate passed 73/73 cases, observation unit tests passed 10/10, scorer harnesses passed 81/81 and 37/37, and lint passed. Linux-specific execution was not verified locally.
No actionable regressions were found against the specified merge base. The observation gate passed 73/73 cases, observation unit tests passed 10/10, scorer harnesses passed 81/81 and 37/37, and lint passed. Linux-specific execution was not verified locally.
```
