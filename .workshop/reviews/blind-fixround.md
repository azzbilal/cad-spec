# Blind-checker review of the fix round (working tree against main)

- Agent: agent-workshop:blind-checker, fresh context, read-only on the repository
- Started 2026-11-27T00:52:51Z, agent run time 625 s (reported by the harness), 26 tool calls
- Inputs given: `git diff main -- . ':!audit' ':!.workshop'` of the uncommitted working tree
  (`scratchpad/fixround/blind-diff-fixround.patch`, 414 lines), the design note and
  `docs/design/L5-amendments.md` as the spec, and the touched sources for context
- Forbidden: anything under `audit/` or `.workshop/`, any file named `*audit*`, and any write
  inside the repository
- The brief carried a checklist (the claims against the code, the grouping key against
  `measure.py`, the `centered` boundaries derived by hand, each new gate case, rules 3 to 5,
  documentation accuracy, text rules). It gave no earlier finding, no owner ruling beyond what
  the diff itself states, and no view of the triage author
- Scratch scripts it wrote: `scratchpad/fixround/blind/` (old_vs_new.py, observation_main.py,
  mutate_keys.py, extra_probes.py, and their logs)
- What it reviewed is the diff before the F1 fix. The F1, F7 and F9 changes made afterwards
  were re-reviewed separately (`blind-delta-fixround.md`)

The report below is the agent's final message, verbatim.

---

Verdict: SHIP WITH FIXES

The code change is correct, and the gate passes 66/66 (exit 0). Its output matches `results/l5/m1-observation-suite.md` byte for byte. But declaring M1 "audited / M2 may start" is premature. I confirmed a wrong value under `ok` (F1); it is older than this diff, and the diff's new control case is placed to avoid it. Three rule and documentation problems also need the owner (F2 to F4).

## Hand derivations (written before running anything)
- Construction: plate 100 x 80 x 4, bounding-box centre (0,0). `shifted(s)` moves all four holes by (s,s), so the mean hole centre is (s,s).
  - Straight-line distance s*sqrt2: 0.7e-7 gives 0.98995e-7, under 1e-7, so centered=True. 0.72e-7 gives 1.01823e-7, over 1e-7, so centered=False.
  - The old per-axis rule gives True for both (|s| < 1e-7).
  - Mirror of -35+s is 35-s; the nearest hole is at 35+s, off by 2s = 1.4e-7 (1.44e-7), over 1e-7, so symmetric=False in both cases.
  - mx = 50-(35+s) = 15-s, my = 40-(25+s) = 15-s, px = 70, py = 50, rectangular=True.
- Split cases:
  - round(20.00049996,3)=20.0 and round(20.00050004,3)=20.001: axes 8e-8 apart, under 1e-7, so one cylinder in two groups. Expected `out_of_scope`.
  - round(10.0000499996,4)=10.0 and round(10.0000500004,4)=10.0001: diameters 8e-10 apart, under 1e-9. Expected `out_of_scope`.
  - One-side control: 20.0004999 and 20.00049998 are 8e-8 apart and both round to 20.0. So one group, one span, n=4. xs = {-35,-35,~20.0005,35}, so px=70, mx=min(15, 15, 29.9995, 70.0005)=15, my=15, py=50, D=10. Mean x is about -3.75, so centered, symmetric and rectangular are all False.
- Tilt: 6.016056848873644e-11 deg x pi/180 = 1.05e-12 rad. The direction components are 1.05e-12/sqrt2 = 7.42e-13 each.

## Checklist
1. **PASS.** The diff claims three things: the split refusal, `centered` by length, and a 1.05e-12 pin. The code does exactly that: `observation.py:109-130` and `:175-177` (split), `:194` (centered), `test_l5_observation.py:259`. The `_nested` refactor at `:141-147` keeps both branches: same cylinder means skip, axis inside the other means refuse.
2. **PASS for n. A related value defect: F1.**
   - **Same key as measure.py.** At `measure.py:761-764`, `scope_axes` gets `(cx, cy, 2*radius)`, the same floats then keyed as `round(cx,3), round(cy,3), round(2*radius,4)`. `_group_key` applies the same rounding to the same numbers.
   - **Proof by reading that no split slips through.** Take any two concave Z faces whose axes are closer than max(d,e)/2. If they are not the same cylinder, `_nested` refuses. If they are the same cylinder with different keys, `_split` refuses. If they are the same cylinder with the same key, they fall in one group. So no cylinder can be split across groups and still get through.
   - **Cannot refuse a correctly grouped part.** It refuses only when the measurement really split a cylinder: two half-holes, holes=5 in every refused run.
   - **Own constructions:**

     | Construction | Old map | New map |
     |---|---|---|
     | Holes at x=+/-20.0005 | ok n=4 | ok n=4 |
     | Holes with D=10.00005 | ok n=4 | ok n=4 |
     | Two-sided cutter at 20.0005 | ok n=4 | ok n=4 |
     | Stacked halves at the same float 20.0005 | ok n=4 | ok n=4 |
     | Stacked halves one ulp apart around 20.0005 | ok n=3 | out_of_scope |
     | Halves split in y around 25.0005 | ok n=3 | out_of_scope |
3. **PASS.** The run matches the hand values: centered True/False, mx 14.99999993 and 14.999999928, symmetric False.
4. **PASS.**
   - Every expected value derives from construction (above).
   - Old observe (main's `observation.py`) against new, on the same measurement:
     - These distinguish old from new: `review_hole_split_across_position_key` and `review_hole_split_across_diameter_key` (old ok n=3, new out_of_scope), and `boundary_pattern_1.02e-7` (old centered=True, new False).
     - These give the same result under both, so they are pins or controls, not discriminators: `boundary_diagonal_tilt_1.05e-12` (the threshold is in measure.py), `boundary_pattern_0.99e-7`, and `review_hole_split_on_one_side`.
   - Mutation check (constants patched in-process): `_DIAMETER_KEY_DP` set to 3 or 5 fails the diameter case; `COAXIAL_DP` set to 2 or 4 fails the position case. A `_split` that ignores the key would fail the one-side control.
5. **UNCLEAR, pending the owner.**
   - **No scorer verdict changes.** `l5` is imported only by `scripts/test_l5_observation.py:332,358`; `measure.py` and `rubric.py` are not in the diff; the frozen scripts are untouched.
   - **Rule 5 (F2).** The package file `l5/observation.py` changes with no version bump.
   - **Rule 3 (F3).** `results/l5/m1-observation-suite.md` is rewritten in place, allowed only by an amendment made in the same diff.
6. **Mostly accurate, with exceptions F1, F3, F4 and F7.** I checked these claims by running them:
   - Thin wall: 1e-7 mm gives `form_violation` (edges off the faces); 1e-6 mm gives ok with mx=5.000001.
   - "Both fail closed for the scorer" holds under 0.5.0. A diagonal tilt of 1.2e-6 rad gives reward 0.9 (R9 fails). The corner split across the key gives reward 0 (`simple_through_holes` and `R4a` fail). Controls give 1.0.
   - The per-component `AXIS_TOL` claim matches `measure.py:637,674`.
   - The `symmetric` argument (distinct holes at least 0.005 apart because of the 0.01 mm size floor and `_nested`) is correct.
   - The tilt bracket [1.0e-12, 1.05e-12) is supported: single-axis 1e-12 accepted, diagonal 1.05e-12 refused, the same hypot rule.
   - No contradiction with design note 7.1/7.2 beyond the pocket deviation, which is already declared.
7. **PASS.** All six files are LF only (CRLF count 0, checked byte-wise in Python) and contain 0 U+2014 characters; the patch has 0 en/em-dash variants. ruff (scripts and package) and mypy pass.
8. See F5 to F9.

## Findings
**F1. should-fix, older than this diff, but the "audited" status rests on it.**
- **Where:** `observation.py:143` (`_nested` skips same-cylinder pairs) and `:186-188`; `measure.py:765` (`raw.setdefault`: the first face's axis wins); `test_l5_observation.py:317-321`; `L5-amendments.md:66`.
- **What is wrong:** a hole cut as two halves on the same side of the key, axes 8e-8 apart, at a corner, is `ok`, and mx/px depend on the order of the halves.
- **Evidence:**
  - `split_hole((35.0,10),(35.00000008,10))` gives ok with mx=14.99999992, px=70.00000008.
  - Swapping the halves gives ok with mx=15.0, px=70.0.
  - By construction the true minimum margin is 50-35.00000008 = 14.99999992. One order reports a value wrong by 8e-8, which is over the 1e-9 slack. That is the same class as R1 (2e-8), which was a required change.
  - The new control is placed inside the pattern "so mx and px do not depend on which half is read", which works around the problem rather than pinning it.
  - The amendments claim "D and the axis are still read from the exact cylinder, never approximated" is false for groups with more than one face.
- **Fix:** refuse a group whose faces' raw axes differ by more than float slack (for example over EPS_DIM_MM), or report the worst face. Otherwise record it as a known limitation with an owner ruling. Either way, add a corner case with the expected value derived as above.

**F2. should-fix (rule).**
- **Where:** `CLAUDE.md:64` (rule 5).
- **What is wrong:** `environments/cad_spec/cad_spec/l5/observation.py` changes with the package still at 0.5.0 (`pyproject.toml:5`). The diff does not amend rule 5; the only cover is the CHANGELOG "owner's ruling", which I cannot verify.
- **Fix:** record the exception in rule 5, as was done for rule 3, after the owner confirms. `OBSERVATION_VERSION` also stays "1" although the meaning of `centered` and the set of refusals changed (see F8).

**F3. should-fix (rule).**
- **Where:** `CLAUDE.md:56-58` against `CLAUDE.md:75`.
- **What is wrong:** the rule 3 exception is written in the same diff that uses it, and it covers the whole `results/l5/` folder. Any future registered L5 result placed there (M3/M4 model runs) would become rewritable. Rule 8 ("never over a tracked file") is not amended, yet the documented `--out results/l5/...` does exactly that.
- **Fix:** narrow the exception to `results/l5/m1-observation-suite.md`, or to a `generated/` subfolder; add the matching exception to rule 8; have the owner confirm the ruling.

**F4. should-fix (status claim).**
- **Where:** `CLAUDE.md:28-31`; `L5-amendments.md` table row M1 and the closing line of 3.2.
- **What is wrong:** M1 is declared "audited, M2 may start" in the same diff that adds code made after the fourth review. The text being replaced disqualified M1 for exactly that ("no review ran after the last fix"). The claim rests on `audit/l5-m1-v4-audit.md`, which I may not open, so it is unverified. F1 is also open.
- **Fix:** declare audited only after this round, with F1 resolved.

**F5. advisory.**
- **Where:** `observation.py:60-64`.
- **What is wrong:** the comment says the "gate case pins it". It pins the map's literal (the mutation check confirms that), but not its agreement with measure.py's literal. If measure.py moved to a finer diameter key, the map would under-refuse and the gate would stay green.
- **Fix:** in the split cases, also assert that the measurement produced 5 holes (`m.holes`), or share one named constant at the next scorer version.

**F6. advisory.**
- **Where:** `test_l5_observation.py:369-372` (`main`).
- **What is wrong:** the gate checks the verdict, not the reason, so a split case could later pass through a different refusal. Today the reason is the split, as confirmed in my run.
- **Fix:** assert a substring of the reason for `out_of_scope` cases.

**F7. note.**
- **Where:** `CHANGELOG.md:62`.
- **What is wrong:** "diagonal tilt limit is pinned at 1.05e-12 rad" reads as if the limit were 1.05e-12. The limit is 1e-12, bracketed by a case refused at 1.05e-12.
- **Fix:** reword along those lines.

**F8. note.** `observation.py:48`: `OBSERVATION_VERSION="1"` is unchanged though the semantics changed. It is unreleased, so either say so or bump it.

**F9. note.** `CLAUDE.md:15`: the header says "State on 26 November 2026" while the body cites rulings of 27 November.

## Checked and found correct
- `_group_key` and measure.py grouping agree on the same floats.
- Split refusal: complete for n by the proof above; no false refusal on 6 constructions of my own.
- `_nested` refactor preserves both branches.
- `centered` hypot and all boundary values; `symmetric` injectivity argument.
- Tilt bracket and component values.
- All expected values of the 6 new cases; gate 66/66 exit 0, output identical to the committed results file.
- Thin-wall claims; the two "fail closed" claims under scorer 0.5.0.
- AXIS_TOL claims.
- LF line endings, no em dashes; ruff and mypy clean.
- No change to `rubric.py`, `measure.py` or the frozen scripts.

## Not checked
- The full `pytest -q`, `test_rubric.py`, the `scripts/test_*.py` loop and `check_release.py` were not run.
- Every claim that rests on the audit file: the five advisory findings triaged, the Codex review, the scope-scan probe-point counterexample ("tongue of material", "fails closed on every case tried"), and the first review's condition on the pocket deviation.
- Whether the owner's rulings dated 27 November exist.
- Scorer 0.4.0 behaviour on the new constructions.
- Linux `fork` mode.

## Scratch files (all under `C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind/`)
- `old_vs_new.py`, `old_vs_new.log`: old against new observe.
- `observation_main.py`: copy of main's version, via `git show`.
- `mutate_keys.py`: constant mutations.
- `extra_probes.py`, `extra_probes.log`: corner split, thin walls, scorer 0.5.0 probes.
- `gate.log`, `suite.md`: gate run with `--out` pointed here.

No file in the repository was written.
