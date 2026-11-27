# Blind-checker review of commit 4e26d30

- Agent: agent-workshop:blind-checker, fresh context, read-only on the repository
- Started 2026-11-26T23:08:55Z, agent run time 565 s (reported by the harness), 17 tool calls
- Inputs given: the commit diff with `audit/` paths removed
  (`scratchpad/blind-diff-4e26d30.patch`, 157 lines), the design note
  `docs/design/L5-region-graded-change-orders-v1.0.md` with the amendments file
  as part of the spec, and the touched source files for context
- Forbidden: anything under `audit/` or `.workshop/`, any file named `*audit*`,
  and the commit message's references to earlier reviews as evidence
- The brief included a checklist of questions (test geometry by hand
  derivation, the hypot and sin comparison and its edge cases, the same defect
  class elsewhere, scoring impact, doc wording, contradictions with the spec).
  It stated what the commit claims to do. It did not include any earlier
  finding or the triage author's view
- Scratch scripts it wrote: `scratchpad/blind/` (probe_tilt.py, mutant.py,
  pockets.py, breakout.py, suite.md, suite.log)

The report below is the agent's final message. The only edit: math symbols
were written in ASCII (square root, theta, pi, plus-minus and the times sign
became sqrt, theta, pi, +/- and x). Nothing else was changed.

---

# Blind review of commit 4e26d30 (L5 tilt limit applied to the angle)

**Verdict: SHIP** for the code change. There are three doc and process items for the owner (B1 to B3). None of them changes a verdict.

`audit/` was only listed by file name. No file in it was opened.

## Checklist

1. **Goal met: PASS.** `measure.py:583` now reads `math.hypot(d.X(), d.Y()) <= math.sin(STRICT_AXIS_SLACK)`. I ran the case `boundary_diagonal_tilt_1.3e-12_rad_is_refused` against the old predicate (in process, with the old line restored by `exec`):
   - Old predicate: `ok`, off_axis_concave 0.
   - New predicate: `out_of_scope`, off_axis_concave 8.
   - Script: `scratchpad/blind/mutant.py`.
2. **Completeness: PASS.** The gate passes 60/60 (exit 0). A fresh `--out` written to scratch is byte-identical to `results/l5/m1-observation-suite.md`. The CHANGELOG and amendment counts (58 to 60) match.
3. **Branches preserved: PASS.** The skip branch remains; only its condition changed. The new acceptance region (a disk of radius 1e-12) lies strictly inside the old one (a square of side 2e-12). So the change only tightens: nothing that was refused before is now accepted.
4. **Evidence is real: PASS, with B3.** The refused case kills the old predicate, as shown in item 1. The 0.9e-12 case accepts under both predicates, so it pins the lower side only.
5. **Slop patterns: PASS.** `sin(1e-12) == 1e-12` in double, so the `sin` changes no result. It is still the correct form for a unit vector, because hypot(dX, dY) is the sine of the line's angle to Z. No dead code was added.
6. **Irreversible actions: PASS.** No push, deploy, delete or secret.
7. **Codebase fit: PASS, with B2.** `_surface_conformance` (line 533) already uses the same "hypot, not X and Y each on their own allowance" pattern.

## Findings

**B1. Should-fix. `docs/design/L5-amendments.md`, new lines 56 to 65 (the deviation paragraph).**
- The old text recorded the reviewer's agreement "with that condition". The condition was that "a pocket that cuts into a hole ... is refused by the rules above".
- The new text says that pocket is a `form_violation`, which I confirmed by running it. Yet it keeps "The external reviewer chose the same verdict" and drops the condition.
- The doc now reports the reviewer's agreement as unconditional, while the condition it originally recorded is stated not to hold.
- Evidence: `scratchpad/blind/pockets.py`. The `pocket_into_hole` case gives `form_violation | a face is neither a plane of the envelope nor a recognised bore ... | n= 3`.
- Fix: say that the condition is not met and that the deviation awaits the owner. Or, if the third review accepted the narrowed wording, cite it for that.

**B2. Advisory, process. Rules 3 and 5 of CLAUDE.md.**
- (a) `results/l5/m1-observation-suite.md` is rewritten in place. Rule 3 says files under `results/` are never rewritten. Earlier commits 08cc812, b9386f9 and 9c19215 regenerated the same file the same way (`git log -- results/l5/m1-observation-suite.md`).
- (b) `environments/cad_spec/cad_spec/measure.py` changes while the version stays at 0.5.0 (`pyproject.toml:5`), which rule 5 forbids.
- The rubric does not read `off_axis_concave` or `off_axis_bores` (grep of `rubric.py` returns nothing), so no score and no recorded verdict can change.
- Both points are for the owner to rule on, not code defects.

**B3. Advisory. `scripts/test_l5_observation.py:224-238`, and the CHANGELOG / amendments wording "both sides pinned".**
- On the diagonal, the four tilt cases bracket the threshold only to [1.0e-12, 1.3e-12).
- A mutant `hypot <= 1.25e-12` passes all four by arithmetic: 1.0e-12 is accepted, 1.3e-12 is refused, 0.9e-12 is accepted.
- So "exact boundary" overstates it. A case at about 1.05e-12 diagonal (components about 7.4e-13) would pin it.
- Separately, the single-axis 1e-12 case sits on exact floating-point equality (hypot = 1e-12 = sin(1e-12)). That was true before this commit, but it is fragile.

**B4. Note. The same defect class remains outside L5. `measure.py:639` (`_z_aligned_cylinders`) and `measure.py:674` (`_off_axis_bore_count`).**
- Both compare X and Y separately against `AXIS_TOL = 1e-6`, so a diagonal tilt up to about 1.41e-6 rad counts as a Z bore.
- Both are on the frozen scorer path, so this is a note for a future scorer version, not for this commit.
- The two predicates are exact complements, so no face falls between them.
- L5 is not affected, because `_scope_scan` now refuses any concave face tilted beyond 1e-12 before those values are used.
- The `_scope_scan` docstring ("accepts tilts up to 1e-6 rad", line 558) has the same imprecision.
- `l5/observation.py` has no angular comparison. Its per-axis `EPS_FORM_MM` checks are on linear variables, so they are fine.

**B5. Note. CHANGELOG line 12 and amendments line 104 cite `audit/l5-m1-v3-audit.md`.**
- That file is not in the tree at 4e26d30 (`git ls-tree -r --name-only 4e26d30 -- audit | grep -c l5-m1-v3` returns 0). It is tracked at HEAD.
- At this commit the reference does not resolve. `check_release.py` passes at HEAD only.
- The commit also adds `audit/README.md` and `audit/l5-m1-v2-audit.md`, which the patch I was given leaves out.

**B6. Note. The "What n counts" row (amendments line 65) drops a condition.**
- The old row said "one ... uninterrupted cylinder". The code still requires `hole.segments == 1` (`observation.py:91`).
- The new row does not mention that condition. Nothing in it is false, but it is less complete.

## Checked and found correct

- **Test geometry, derived by hand.**
  - Rodrigues formula with k = (1,1,0)/sqrt(2): rotating z by theta gives (sin(theta)/sqrt(2), -sin(theta)/sqrt(2), cos(theta)). So the angle is theta and each component is sin(theta)/sqrt(2).
  - CadQuery `Shape.rotate` applies `radians(angleDegrees)` (I read the source with `inspect`).
  - 1.3e-12 x 180/pi = 7.448451336700702e-11 degrees. Each component is 9.19e-13, as the test description says.
  - 0.9e-12 x 180/pi = 5.156620156177409e-11 degrees. Each component is 6.36e-13.
  - Corroboration, run after the derivation: OCCT stores d = (9.19238815542512e-13, -9.19238815542512e-13, +/-1.0), with hypot 1.3000000000000003e-12.
- **Edge cases.**
  - `gp_Dir` is always a unit vector.
  - hypot does not depend on sign, so axes pointing -Z and reversed cylinders give the same result. The probe shows d.Z = -1.0 faces handled.
  - The line angle lies in [0, pi/2], where sin increases, so `hypot <= sin(slack)` is equivalent to angle <= slack.
- **Scoring.** `_scope_scan` feeds only `off_axis_concave` and `min_cylinder_diameter`, and the rubric reads neither. `min_cylinder` is computed before the changed condition, so it is unchanged.
- **Doc claims I reproduced.**
  - A pocket with large rounded corners is `out_of_scope` ("nested"): a 6 x 6 pocket with R2.5 corners.
  - A pocket cutting into a hole is `form_violation`.
  - A hole breaking out of a side by 0.001 mm (axis 4.999 mm from the face) is recognised. The result is `ok` with n=4 and mx=4.999, leaving F1 to the contract as amendment line 124 says. Script: `scratchpad/blind/breakout.py`.
- **Wording.** No "uncertainty" anywhere. The code comment calls 1e-12 "floating-point slack, not a tolerance on tilt". No em dashes in the patch (grep for U+2014 returns 0).
- **Other checks.**
  - `ruff check scripts`: clean.
  - `ruff check .` and `mypy cad_spec` in `environments/cad_spec`: clean.
  - `pytest -q tests/test_l5_observation.py`: 10 passed.
  - `check_release.py`: "all document links resolve".
  - The CI step exists (`ci.yml:82`).
- **Spec.** The design note says "Holes tilted off Z: `out_of_scope`" (7.2), and the change strengthens that.
  - Declared deviations: pocket or slot is `form_violation` instead of `out_of_scope` (7.2), pending the owner. The hole centre is measured at the mid-plane rather than the top face (7.1).
  - Undeclared tension: the 99% wall rule versus 7.1 "running through the full thickness" and the scope rule "never measured approximately". It predates this commit but is now stated openly.

## Not checked

- These amendment claims rest on `audit/` files, which I was not allowed to read, so I could not check them: 333 parts, 180 controls, 3,161 answers, "R2 to R5 resolved", and what the third review asked for. They need the audit files or a rerun of those suites.
- Linux CI in fork mode. I only ran Windows in reuse and in-process modes.
- The two audit files in the commit that the patch leaves out.
- The full pre-commit loop (`scripts/test_*.py`, `test_rubric.py`, the full package pytest). I ran only the L5 gate, the L5 pytest file, ruff, mypy and `check_release`.

Scratch scripts (all in `C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/blind/`): `probe_tilt.py`, `mutant.py`, `pockets.py`, `breakout.py`, `suite.md`, `suite.log`.
