# Blind-checker re-review of the fix round (after the F1 fix)

- Agent: agent-workshop:blind-checker, a new fresh-context instance (not the one that wrote
  `blind-fixround.md`), read-only on the repository
- Started 2026-11-27T01:08:57Z, agent run time 607 s (reported by the harness), 24 tool calls
- Inputs given: `git diff main -- . ':!audit' ':!.workshop'` of the working tree after the F1,
  F7 and F9 changes (`scratchpad/fixround/blind-diff-fixround2.patch`, 493 lines), the design
  note and the amendments as the spec, the touched sources for context
- Focus named in the brief: the new `_axis_spread` refusal, the replaced and added gate cases
  with the `REASONS` check, the documentation of these rules, the text rules. It was told that an
  earlier review covered `centered`, the 1.05e-12 rad case and `_split`, without that review's
  findings or the triage author's view
- Forbidden: anything under `audit/` or `.workshop/`, any file named `*audit*`, any write inside
  the repository
- Scratch scripts it wrote: `scratchpad/fixround/blind2/` (probe_split.py,
  probe_false_refusals.py, probe_flip.py, probe_mutants.py, probe_cross_hole.py, probe_diag.py,
  observation_main.py, gate_run.txt, suite.md)

The report below is the agent's final message, verbatim except that one less-or-equal sign was
written in ASCII as <=.

---

**Verdict: SHIP WITH FIXES.** `_axis_spread` does what it says for a single hole, and I found no false refusals. The gate cases are right and every refusal case fails on `main`. One problem remains: when two holes are split, px and py (and, in code that was already on main, the D verdict) can still change with the cut order by up to 2e-9 mm.

Skills consulted:
- cad-spec-geometric-observation (scope rules, refusal over guessing, P17: px, py, mx and my are frame-free). It led me to check order dependence of the derived variables (px, py, D), not only of each hole's axis. That check found G1 and G2.
- cad-spec-numerical-validation (P31: expected values come from construction; P09: can the suite see each kind of error). Every expectation below was derived by hand before the run. Mutation runs found G3.
- cad-spec-uncertainty-and-error (P27: a known bias is either refused or bounded). This frames the two fix options for G1.

All scratch files are in `C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind2/`:
- `probe_split.py`: the six gate cases, run against the new map and against main's map loaded in memory.
- `probe_false_refusals.py`: 18 ordinary constructions.
- `probe_flip.py`: checks one probe I built wrongly.
- `probe_mutants.py`: changes the threshold in memory.
- `probe_cross_hole.py`: order dependence across two split holes.
- `probe_diag.py`: a mutant that compares X and Y separately, plus a diagonal case.
- `observation_main.py`: a copy of main's map taken with `git show`.
- `gate_run.txt` and `suite.md`: output of the gate runs.

Nothing in the repository was written.

## Point 1: `_axis_spread` (observation.py:134-143)

- **Correct for one hole.**
  - Two faces in one measurement group differ by less than 1.42e-3 mm in position and less than 1e-4 mm in diameter.
  - If they are not the same cylinder, `_nested` refuses them, because 1.42e-3 is less than the smallest supported radius, 0.005.
  - If they are the same cylinder, `_axis_spread` refuses any pair more than 1e-9 apart, checking every pair.
  - So under `ok` each hole's axis and diameter are within 1e-9 of every one of its faces, and mx and my change with face order by at most 1e-9.
  - Run: in the 0.5e-9 case the map reports mx = 14.9999999995.
- **No false refusals.** All 18 ordinary constructions give `ok` with n = 4 (n = 5 for the mirrored part), and in each the widest gap between two faces of one cylinder is exactly 0:
  - holes cut in one go;
  - a two-sided cutter;
  - halves at identical positions, or at positions computed by arithmetic (`0.1*350`, `100/2-15`, `3.5*10+1e-15`);
  - rotated 90 degrees about Z; rotated 37 degrees and back; flipped 180 degrees about X;
  - moved by (1234.567, ...), by 1e5, 1e6 and 1e7;
  - cut after moving; cylinders whose stored location is 500 mm away along the axis;
  - two stacked boxes with the holes cut in one go;
  - faces split at the seam (`ShapeUpgrade_ShapeDivideClosed`);
  - mirrored halves sharing a centre hole.
- **One probe error.** `halves_flip_then_move` came back `out_of_scope` (off-axis), but that was my mistake. CadQuery's `rotate` takes two points, so (3,7,1) to (1,0,0) is a skew axis. With a correct axis the part is `ok` (`probe_flip.py`).
- **Answer to "can mx, my, px or py depend on face order by more than 1e-9 under `ok`": yes for px and py, up to 2e-9.** See G1.

## Point 2: gate cases (all verified by hand, then by run)

| Case | Hand derivation | Run (new) | Run (main) |
|---|---|---|---|
| position_key | 8e-10 apart, keys 20.0 and 20.001, so `_split` fires; 5 measured holes | out_of_scope, two hole groups, 5 holes | ok, n = 3 |
| diameter_key | diameters 8e-10 apart, keys 10.0 and 10.0001; 5 holes | out_of_scope, two hole groups, 5 holes | ok, n = 3 |
| 8e-8 corner | same key, 8e-8 > 1e-9, so "axes more than" | out_of_scope | ok, mx = 14.99999992 |
| 8e-8 other order | same | out_of_scope | ok, mx = 15.0 |
| 0.5e-9 | 5e-10 <= 1e-9, so ok, NOMINAL within 5e-10 | ok, mx = 14.9999999995, px = 70.0000000005 | ok |
| 2e-9 | > 1e-9, so refused | out_of_scope | ok, mx = 14.999999998 |

- Every case keeps two separate faces for the fourth hole: `scope_axes` has 5 entries each time.
- The split cases sit at 8e-10, under the threshold, so they exercise only `_split`. That is good design.
- The reason phrases match the code strings, and the five-hole check holds.
- Gate run: 69 of 69 as expected, exit 0. A second run with `--out` into the scratch folder is identical to the tracked `results/l5/m1-observation-suite.md`.
- ruff on both changed Python files passes.

## Point 3: documentation

- **Accurate:**
  - The amendments row, against `COAXIAL_DP` = 3 and the literal 4 at measure.py:764.
  - The mx = 14.99999992 or 15.0 claim (confirmed above).
  - The CHANGELOG fourth-review bullet.
- **Overstated:** the CHANGELOG gate bullet (CHANGELOG.md:71) says "the exact boundary of each rule is pinned (... one axis per hole)". It is not; see G3.
- **Wording too broad:** the 0.5e-9 case says "every variable right to 1e-9 whichever face is read". That holds for one split hole, not for two; see G1.
- **CLAUDE.md state header:** the text matches the amendments. The "audited" status rests on `audit/l5-m1-v4-audit.md`, which I may not read and which was untracked at the start; see "Not checked".

## Point 4: text rules

- No U+2014 em dash in the six changed files or in the diff.
- `git ls-files --eol` shows i/lf and w/lf for all six, and none contains a carriage return.

## Findings

**G1 (should-fix), observation.py:142 and 204.** px and py can change with face order by 1.8e-9 under `ok`.
- Evidence (`probe_cross_hole.py`): split the left hole into halves at -35 and -35.0000000009, and the right hole into halves at 35 and 35.0000000009.
  - Each hole's spread is 0.9e-9, so both cut orders are `ok`.
  - The run gives px = 70.0000000018 (mx = 14.9999999991) in one order and px = 70.0 (mx = 15.0) in the other. This matches the hand derivation; the measurement reads the face of the later cut.
- Fix, owner's choice:
  - (a) refuse an axis spread above `EPS_DIM_MM / 2`, so the extents stay within 1e-9; or
  - (b) state in the amendments row and the docstring that px and py are exact to 2e-9 when holes have several faces.

**G2 (should-fix, already on main, outside the named focus), observation.py:113 with 196 and 201.** The D verdict depends on cut order.
- Evidence: hole A has halves of 10 and 10.0000000009; hole B has halves of 10 and 9.9999999991.
  - In one order: `out_of_scope`, "through holes of different diameters".
  - In the other order: `ok`, D = 10.0.
- Cause: `_same_cylinder` lets the diameters inside one hole differ by 1e-9, and the check across holes compares only the first face of each hole.
- This is the same "verdict must not depend on order" problem the new case names.
- Fix: run the D-consistency check over every face of the through holes, or tighten the diameter tolerance inside one hole to `EPS_DIM_MM / 2`.

**G3 (should-fix), test_l5_observation.py:323-327 and CHANGELOG.md:71.** The 1e-9 axis rule is bracketed only to [0.5e-9, 2e-9), and only along X.
- Evidence (`probe_mutants.py`, `probe_diag.py`): three changed versions of `_axis_spread` pass all six gate cases:
  - a threshold of 0.51e-9;
  - a threshold of 1.9e-9;
  - comparing |dx| and |dy| separately instead of the straight-line distance. That version accepts a diagonal offset of (0.8e-9, 0.8e-9), which is 1.13e-9 apart; the shipped code refuses it.
- The same mistake (comparing X and Y separately) was already found for the tilt rule and for `centered`.
- Construction distances for the fix:
  - 35.0000000009 is 9.00002e-10 from 35;
  - 35.0000000011 is 1.09999e-9;
  - "written 1e-9" (35.000000001) is 9.99997e-10, so it is accepted, unlike the diameter case.
- Fix: add cases at 0.9e-9 (ok), 1.1e-9 (refused) and the diagonal (0.8e-9, 0.8e-9) (refused), or soften the "exact boundary" claim.

**G4 (advisory), test_l5_observation.py:340-346.** The `ok` case `boundary_hole_halves_0.5e-9_apart` does not check that the kernel kept two faces.
- If a future kernel merged them, the case would pass and test nothing. The refusal cases check themselves; this one does not.
- Today it does keep two faces (5 entries, from my run).
- Fix: assert `len(scope_axes) == 5`, or add the case to `REASONS` with a face count.

**G5 (note), L5-amendments.md:67.** The row says "Faces closer than 1e-7 mm", but the code uses `<=` 1e-7. Write "at most 1e-7 mm".

## Checked and found correct

- The order of the refusals: nested, then split, then spread.
- `_same_cylinder` is used the same way in `_nested`.
- The `_DIAMETER_KEY_DP` comment matches measure.py:764.
- Pairwise checking leaves no gap through a chain of faces.
- Hole axes are evaluated at the mid-plane `z_ref`, so a cylinder stored far along its axis gives no false spread.
- Each refusal case fails on main, and each case keeps two faces.
- The `REASONS` mechanism, and that the results file regenerates byte-identical.
- LF line endings and no em dashes.

## Not checked

- `audit/l5-m1-v4-audit.md` (forbidden): so not the "counted as audited" status, the owner's rulings, or whether that file will be committed alongside the CLAUDE.md, CHANGELOG and amendments references to it.
- The full pre-commit checks: package pytest, mypy, `check_release.py`, every `scripts/test_*.py`.
- Linux `fork` mode.
- The items the earlier review already covered: `centered`, the 1.05e-12 tilt case, `_split`.
- Other sections of CLAUDE.md, including the new rule-3 exception for `results/l5/`.
