# Blind-checker re-review of the D fix, final round

- Agent: agent-workshop:blind-checker, a new fresh-context instance, read-only on the repository
- Started 2026-11-27T02:20:39Z, agent run time 612 s (reported by the harness), 20 tool calls
- Inputs given: `git diff main -- . ':!audit' ':!.workshop'` of the working tree after the
  all-face D check, the H3 case and the H4 header (`scratchpad/fixround/blind-diff-final2.patch`,
  662 lines), the design note and the amendments as the spec, the touched sources for context
- Focus named in the brief: `_through_face_diameters` and the D check, the four new gate cases,
  the extended `split_holes` helper and their `REASONS` entries, the version in the generated
  header, the documentation of these changes, the text rules. It was told an earlier review
  covered the rest of the diff, without that review's findings or the triage author's view
- Forbidden: anything under `audit/` or `.workshop/`, any file named `*audit*`, any write inside
  the repository. It disclosed one side effect: importing the gate module wrote an ignored
  `scripts/__pycache__/` file
- Scratch scripts it wrote: `scratchpad/fixround/blind-delta-final/` (probe_d_check.py,
  probe_fifth.py, probe_clean.py, gate.log, suite.md)
- What happened next: J1, J5 and J6 (docstring and wording) were fixed after this review and
  not reviewed again. J2, J3 and J4 are listed for the owner

The report below is the agent's final message, verbatim.

---

Verdict: SHIP. Everything I found is advisory or a note; nothing blocks.

I made no edits inside the repository. One side effect: importing the gate module from my scratch script made Python write `scripts/__pycache__/test_l5_observation.cpython-312.pyc` (dated 03:18). That path is ignored by `.gitignore:1 __pycache__/`, so it does not show in git status. I left it alone and did not delete it. Later runs used PYTHONDONTWRITEBYTECODE=1.

Skills consulted:
- cad-spec-metrology-router: the delta changes `l5/observation.py` and a gate.
- cad-spec-geometric-observation: D, the refusal rules, and split faces (FP12). The skill's procedure step 2 says construction order must not change a value, so I added my own cut-order and kernel-merge probes.
- cad-spec-numerical-validation: P31 (truth comes from the construction), P09 (can the suite see the error class), FP24 (a passing suite is not proof). This is why I recomputed every refusal case under the previous rule instead of trusting the why-texts.
- cad-spec-uncertainty-and-error and cad-spec-conformity-decision: read for the slack wording. No changed text calls slack an "uncertainty" (grep came back empty).
- Domain: exact_brep_analytic (P44). The B-rep the kernel hands over is the part. This shapes J3.

Hand derivations. I worked these out from the construction parameters in my notes before the first run; they are written out here afterwards.
- `review_face_diameters_spread_over_two_holes`
  - Faces at (-35,-25) are 10.0 and 10.0000000009; faces at (-35,25) are 9.9999999991 and 10.0; the two plain holes are 10. Six faces.
  - Within each hole the faces are 0.9e-9 apart, so they count as one cylinder, share a key (round(.,4) = 10.0) and pass `_nested` and `_split`.
  - Each hole spans z [-2,0] and [0,2], merged into one segment, so it is through. n = 4.
  - Spread over all faces is 10.0000000009 - 9.9999999991 = 1.8e-9 > 1e-9, so out_of_scope with n present and D absent.
  - Previous rule (one face per hole): the result depends on which face the kernel lists first. If the later cut comes first, the hole reps are 10.0000000009 and 10.0, spread 0.9e-9, so `ok` with D = 10.0000000009.
- `_other_order`: same faces, so out_of_scope. Under the previous rule the reps are 10.0 and 10.0, so `ok` with D = 10.0.
- `boundary_face_diameters_0.9e-9_apart_over_two_holes`: faces from 10 to 10.0000000009, spread 0.9e-9, so `ok` with every NOMINAL value. D is 10.0 or 10.0000000009; `matches()` accepts either only because its tolerance (1e-9) equals the slack.
- `review_hole_split_across_position_key_under_the_spread_limit`:
  - 20.0004999998 rounds to key 20.0 and 20.0005000002 to 20.001. The margin to the key is 2e-10, far larger than float noise (about 4e-15).
  - The axes are 4e-10 apart, so they count as one cylinder, and 4e-10 is under the 5e-10 spread limit.
  - So only `_split` refuses, before n is written. The measurement makes 3 + 2 = 5 holes from 5 faces.
  - Without the grouping rule: two half-depth holes, neither through, so `ok` with n = 3.

Point 1: `_through_face_diameters` (observation.py:153-161, used at :214). Correct and complete for its purpose.
- Argument:
  - Every hole's rep (x, y, diameter) is exactly one entry of `scope_axes`: the group's first face (measure.py:761-765).
  - Two faces with the same key are less than 1.42e-3 mm apart (position rounded to 3 decimals). The smallest accepted diameter is 0.01 mm, so d/2 is at least 0.005. Any two group-mates that are not `_same_cylinder` are therefore already refused by `_nested`. So every face of a through hole's group matches its rep and is compared (no escape).
  - A face that matches a rep but sits under another key is refused earlier by `_split`. So no foreign face is pulled in.
  - Result: under `ok`, the compared set is exactly the faces of the through-hole groups, the spread is at most 1e-9, and D (one of those faces) is within 1e-9 of every face. The verdict no longer depends on face order.
- Evidence: probe_d_check.py and probe_fifth.py results (all matched my predictions).
  - Spread cases: the measured `scope_axes` order shows the later-cut face listed first. Previous rule gave `ok` with D = 10.0000000009 and `ok` with D = 10.0, exactly as the why-texts claim. New rule refuses both.
  - Spread part turned 90 degrees and spread part moved by (37.1, -12.3, 5): refused. The boundary part turned 90 degrees: `ok`.
  - Ordinary parts, all `ok` with no false refusal: holes cut in one go, plate moved by 0.0005 onto the rounding boundary, two-sided equal halves moved onto that boundary, plate turned 90 degrees, a plain fifth hole (n = 5), a fifth split hole spread 0.9e-9 (n = 5).
  - Fifth hole of 10.0000000005 plus a corner split 9.9999999993 / 10.0: refused (previous rule: `ok`).
  - Three stacked faces 10 / 10.0000000009 / 10, the middle face carrying the maximum, plus a hole of 9.9999999995: refused (previous rule: `ok`). Interior faces are included.
  - Holes 12 mm apart, spread 1.4e-9: refused.
  - Blind 5.000000005 hole next to through holes: not counted, not compared. It is a `form_violation` from the form check, not a D refusal.

Point 2: new gate cases. All four have the expected verdicts and values, all keep separate faces, and the refusals fail under the previous rule.
- Face counts measured: 6, 6, 6 and 5; holes = 5 for the split case. These match the REASONS entries.
- Previous rule (`_through_face_diameters` stubbed out): both spread cases `ok`.
- No grouping-key rule (`_split` stubbed out): the under-limit case is `ok` with n = 3. By contrast, the original 8e-10 split case is still caught by the spread rule, which is why the new case was needed.
- The REASONS phrases ("different diameters", "two hole groups") match the reason strings at observation.py:207 and :216.
- `split_holes` builds correctly: plain points and diameters 10 unless given, separate faces kept by clean=False.

Point 3: the generated file matches a fresh run.
- `python scripts/test_l5_observation.py --out <scratch>/suite.md`: exit 0, 77/77.
- `cmp` against `results/l5/m1-observation-suite.md`: IDENTICAL.
- The header names "Observation version 2". The case count is 60 + 17 new = 77.

Point 4: documentation is accurate.
- The "Holes of different diameters" row (amendments:81), section 3.2 (:153-155), the version paragraph (:43-49), the CHANGELOG release plan (:9-20) and the fourth-review bullet (:64-77) all match the code.
- No deferral of the D item is left. The only deferred items are the probe point (M3) and the two scorer-path defects.
- Release facts: `git ls-tree -r v0.5.0` has 0 files under `cad_spec/l5/`, consistent with "version 1 was never released". `pyproject` is at 0.5.0, consistent with "stays at 0.5.0".
- No stale "awaiting audit" or "not yet counted" in README.md, ROADMAP.md, docs/REPORT.md or docs/design.

Point 5: text rules hold.
- Byte count on all six changed files: 0 CRLF, 0 em dash (U+2014), 0 en dash.
- `git ls-files --eol`: i/lf w/lf for all six.
- My first `grep $'\r'` count was wrong: Git Bash grep misreports line endings. Ignore it.

Checklist
1. Goal met: PASS. D is order-independent and within 1e-9 of every through face under `ok` (probes above).
2. Completeness: PASS. All 4 new cases are present, in REASONS and in the generated file. 77 = 60 + 17.
3. Branches preserved: PASS. The previous rep diameters are still included (`+ [h.diameter ...]`). `_nested`, `_split` and `_axis_spread` come before the D check and are unchanged in order.
4. Evidence is real: PASS. Fresh gate run, byte-identical output, and the previous rules recomputed by stubbing.
5. Slop patterns: FAIL (advisory only), J1 and J2.
6. Irreversible actions: PASS. None in the change. My stray .pyc is disclosed above.
7. Codebase fit: PASS. The code reuses `_same_cylinder` and the scorer constants (COAXIAL_DP).

Findings
- J1 (advisory) observation.py:153-161 and :214.
  - `_through_face_diameters` decides membership with `_same_cylinder` against the rep. That equals group membership only because `_nested` and `_split` have already run; the docstring does not say so.
  - The `+ [h.diameter for h in through]` term is redundant: every rep is itself a `scope_axes` entry.
  - Fix: add "valid only after _nested and _split" to the docstring, and either drop the redundant term or label it a guard.
- J2 (advisory) scripts/test_l5_observation.py:56 and :69.
  - `split_hole` takes tuples as (x, d[, y]) and `split_holes` takes (x, y[, d]). They are near-duplicates with conflicting tuple orders, an easy misuse.
  - Fix: write `split_hole` in terms of `split_holes`, or give them the same order.
- J3 (note), modelling order upstream of the map.
  - A later cut with default clean (`.hole()` or `.clean()`) merges split halves into one face that keeps one of the two radii.
  - With a 7e-10 step, probe_d_check (fifth-hole construction) saw 5 faces and `ok`. probe_fifth, same cuts with no later clean, refused.
  - probe_clean: merging happens for steps of 7e-10, 2e-9 and 1e-8, but not 1e-6. Merged parts refuse or accept on the merged B-rep's own exact radius.
  - Under P44 the merged B-rep is a different exact part, so this is not a defect of the map. The order-independence guarantee holds for the faces the kernel keeps. The amendments could say so in one sentence.
- J4 (note), discriminating power of the other_order case.
  - That the `_other_order` spread case fails under the previous rule depends on this kernel listing the later-cut face first (seen in `scope_axes`).
  - If OCC's face order changes, the "was `ok`" why-texts could go stale. The new-rule verdicts stay pinned whatever the order.
- J5 (cosmetic) CHANGELOG.md:17-18. A ragged line break: "and M2 items will" / "record the version...".
- J6 (cosmetic) observation.py:13-16. The module docstring's out_of_scope list leaves out the split-across-hole-groups refusal.

Checked and found correct
- Completeness of the D comparison and no pulled-in faces (argument plus probes).
- Order independence. Moved, turned, fifth-hole, near-hole, blind-hole, three-stack and key-boundary parts.
- Hand-derived verdicts and values of the 4 new cases. Separate faces. Failure under the previous rule and under the no-grouping rule.
- Generated file byte-identical to a fresh run. Version header.
- Doc rows and sections against the code. Release-plan facts against the v0.5.0 tag.
- LF and no em dash on the six changed files.

Not checked
- `.workshop/NOW.md`, `audit/README.md` and `audit/l5-m1-v4-audit.md` (forbidden to me), so I could not verify the claims that cite the audit report.
- The full CI check list (ruff, mypy, pytest, the other `scripts/test_*.py`, `check_release.py`): not run.
- Linux fork mode.
- Hole faces split around the circumference (seam-split with different radii): I could not build one cleanly in CadQuery.

Scratch files (all in C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-delta-final/):
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-delta-final/probe_d_check.py
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-delta-final/probe_fifth.py
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-delta-final/probe_clean.py
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-delta-final/gate.log
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-delta-final/suite.md

No MemoryError worker faults and no reruns were needed.
