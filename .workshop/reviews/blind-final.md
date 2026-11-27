# Blind-checker review, final round (working tree against main)

- Agent: agent-workshop:blind-checker, a new fresh-context instance, read-only on the repository
- Started 2026-11-27T01:51:17Z, agent run time 784 s (reported by the harness), 25 tool calls
- Inputs given: `git diff main -- . ':!audit' ':!.workshop'` of the working tree at observation
  version 2 with the 0.5e-9 spread limit and 73 gate cases
  (`scratchpad/fixround/blind-diff-final.patch`, 602 lines), the design note and the amendments
  as the spec, the touched sources for context
- The brief asked for a review of the whole diff with a checklist (claims against code, every
  refusal rule, every gate case derived by hand, the accuracy statements, OBSERVATION_VERSION,
  the rule exceptions in CLAUDE.md rules 3, 5 and 8, documentation, text rules). It gave no
  earlier finding and no view of the triage author
- Forbidden: anything under `audit/` or `.workshop/`, any file named `*audit*`, any write inside
  the repository
- Scratch scripts it wrote: `scratchpad/fixround/blind-final/` (probe1.py, probe2.py, gate.log,
  suite.md)
- What happened next: H1 was confirmed and fixed by the owner's ruling (the D check over every
  face), H2 (CHANGELOG), H3 and H4 were fixed. That change set was re-reviewed separately
  (`blind-delta-final.md`)

The report below is the agent's final message, verbatim.

---

Verdict: SHIP WITH FIXES

Skills consulted:
- cad-spec-metrology-router: the diff changes the L5 observation map and its gate.
- cad-spec-geometric-observation: refusal rules, and topology or construction-order invariance.
- cad-spec-uncertainty-and-error: the slack is numerical slack, not uncertainty.
- cad-spec-numerical-validation: boundary cases, expected values derived by hand.

Relevant principles:
- Geometric-observation procedure step 2: split faces and construction order must give the same value. This is what H1 tests.
- P31: every expectation below was written from construction parameters before running anything.
- P38: the report must name the evaluator version (H4).
- The changed text contains no "uncertainty".

Domain: exact_brep_analytic.

## Checklist

1. **Claims against code: PASS, except H1.**
   - CHANGELOG, the amendments and CLAUDE.md describe the code: the centered hypot rule (observation.py:217), the `_split` and `_axis_spread` refusals (lines 125-150, 195-200), SPREAD_LIMIT = EPS_DIM / 2, 73 cases and the version bump to "2".
   - Probe A, with the new rules monkeypatched off, confirms the "was ok" claims:
     - position-key split: ok with n = 3;
     - diameter-key split: ok with n = 3;
     - 8e-8 corner: ok with mx = 14.99999992 in one cut order and 15.0 in the other.

2. **Refusal rules: PASS.**
   - The `_group_key` rounding matches measure.py:763-764: COAXIAL_DP for position, 4 decimals on the raw `2 * radius` for diameter.
   - All pairs are checked, not a chain, so three faces at 0.3e-9 and 0.3e-9 are still refused.
   - Any group cell is at most 1.41e-3 mm across, which is below d/2 >= 0.005. Every pair of faces in one group is therefore either `_same_cylinder` or refused by `_nested`, which closes the position bound.
   - The `_nested` refactor is behaviour-identical.
   - No false refusals on ordinary parts. Every hole below was cut as two half cylinders at identical centres, and the probe confirmed 8 faces each time. All are `ok` with the hand-derived values:
     - centres exactly on rounding keys (x and y = +-20.0005, +-25.0005);
     - off origin, offset (1234.5675, -777.25);
     - off origin with centres on keys, offset (1234.0005, 0.0005);
     - turned 90 degrees (L = 80, W = 100, px = 50, py = 70);
     - 3 mm holes off origin.
   - `environments/cad_spec/tests/test_l5_observation.py` runs every generated train and dev reference part: 10 passed.

3. **Gate cases: PASS.** I derived these before running:
   - centered 0.99e-7: hypot(7e-8, 7e-8) = 9.90e-8 is inside the tolerance, so ok. mx = my = 15 - 7e-8. symmetric is False because a mirrored hole is 1.4e-7 off.
   - centered 1.02e-7: hypot(7.2e-8, 7.2e-8) = 1.018e-7, so centered is False. Version 1 said True, so the case tells the two apart.
   - Tilt 1.05e-12: 6.016e-11 degrees is 1.05e-12 rad, components 7.42e-13. Refused, and probe 2 confirms the reason is the tilt rule. Combined with the axis-aligned 1e-12 accept case, this excludes any component-wise rule and brackets the angle limit to [1.0e-12, 1.05e-12).
   - Position-key split: 8e-10 apart, so both new rules would fire. The reason-phrase check pins `_split`.
   - Diameter-key split: zero spread, so only `_split` can fire.
   - 8e-8 cases, both orders: refused by the spread rule.
   - Spread boundary: 0.45e-9 is ok, 0.55e-9 is refused.
   - Diagonal (4e-10, 4e-10): hypot 5.66e-10 is refused although each component is inside. This separates hypot from max-component.
   - Diagonal (3.5e-10, 3.5e-10): hypot 4.95e-10 is ok. This separates hypot from the L1 norm.
   - Two-hole cases: worst-case px = 70 + 9e-10 and 70 + 7e-10.
   - REASONS checks hole and face counts (5 or 6 faces, and 5 holes for the key splits), so the separate-faces claim is verified.
   - Gate run: 73/73, exit 0. The generated file is byte-identical to results/l5/m1-observation-suite.md.
   - Weak spot: no position-key split under 0.5e-9 is in the gate (H3). My probe D (4e-10 apart around 20.0005) was refused by `_split`.

4. **Accuracy statements (positions, px, py): PASS.**
   - Every pair of faces of one hole is within 0.5e-9 in a straight line, so each coordinate is within 0.5e-9 and px, py within 1e-9 whichever faces are read.
   - I found no construction that breaks this.
   - D does not get the same bound (H1).

5. **OBSERVATION_VERSION: PASS.**
   - Bumped to "2", documented in the CHANGELOG, in amendments section 3 and in an inline comment, and exported.
   - "Version 1 never released" holds: the v0.5.0 tag has no l5/ files.
   - The generated record does not carry the version (H4).

6. **Rule exceptions: UNCLEAR on authority, PASS on scope.**
   - The rule 3, 5 and 8 texts are narrow and consistent with each other. Rule 3 names one file and one command; rule 8 refers back to it; rule 5 covers cad_spec/l5/ only.
   - Inside the package the diff touches only l5/observation.py. measure.py, rubric.py, environment.py, tasks.py and the frozen scripts are untouched against main, and the scorer does not import l5.
   - Within the reviewed patch, only the generated file is touched under results/.
   - The "owner's ruling 27 November 2026" behind each exception, and "M1 counts as audited", rest on audit material I may not read. They are unverified. These are edits to "never broken" rules, so Bilal should confirm them himself.

7. **Documentation: FAIL.**
   - H1 is a false statement.
   - H2 covers minor incompleteness.
   - No stale "60 cases" or "awaiting audit" text remains in README, ROADMAP, docs or .github.

8. **Text: PASS.** Python byte counts show 0 CRLF and 0 U+2014 in all six changed files.

9. **Other defects:** H1 to H4.

## Findings

**H1. should-fix.** Files: docs/design/L5-amendments.md:195 ("The `ok` order reports a D within 1e-9 mm of every face, so this is a false refusal in one order, not a wrong value") and environments/cad_spec/cad_spec/l5/observation.py:146-147 ("every variable is within the slack whichever face is read").
- **The claims are false for D.** `_same_cylinder` lets the faces of one hole differ by up to 1e-9 in diameter. The diameter check at observation.py:203 compares only the first face of each hole, and D = through[0].diameter.
- **Construction:** plain 10 mm holes at (35, +-25).
  - Hole A at (-35, -25): lower half 10, upper half 10.0000000009.
  - Hole B at (-35, 25): lower half 9.9999999991, upper half 10.
- **Hand derivation:** A reads 10 or 10.0000000009; B reads 10 or 9.9999999991. D is A's reading. So one part has three outcomes: `ok` with D = 10, `ok` with D = 10.0000000009, or `out_of_scope`.
- **Run (probe1.py, case B):** this order gave `ok` with D = 10.0000000009 while B has a face at 9.9999999991, so max |D - face| = 1.80e-9, above the 1e-9 slack. The other orders gave `ok` with D = 10, or `out_of_scope` ("different diameters").
- This is a wrong value under `ok`, not only a false refusal, and it breaks the design note's 7.2 scope rule ("never measured approximately"). The owner's deferral rests on the false premise.
- **Fix, either:**
  - (a) Check the diameter spread over every face of all through holes (scope_axes faces within EPS_FORM of a through hole's axis), max - min <= EPS_DIM_MM, and add this construction as a gate case; or
  - (b) Correct both texts and put the corrected premise back to the owner for the M3 deferral.

**H2. advisory.** Three documentation gaps:
- CLAUDE.md:30-32 lists the deferred items as "the scope-scan probe point (M3) and two scorer-path defects". It omits the D cut-order item that CHANGELOG:71-73 and amendments section 4 list. Add it, with H1's corrected wording.
- CHANGELOG:11 says only `cad_spec/l5/` and measure.py changed since v0.5.0. `git diff --stat v0.5.0` also shows rubric.py changed (form_verdict extracted; behaviour-preserving by inspection). This predates the diff; mention rubric.py.
- The amendments row "Very thin edge wall" (1e-7 mm is form_violation, 1e-6 mm is ok) has no gate case. I confirmed it by probe: form_violation, and ok with mx = 5.000001. Consider pinning it.

**H3. advisory.** scripts/test_l5_observation.py:323-325. The only position-key split case is 8e-10 apart, above the spread limit, so without `_split` the verdict would still be `out_of_scope`. Only the reason phrase separates the two rules. Add a position-key split under 0.5e-9 (for example 20.0004999998 and 20.0005000002); my probe D shows it is refused only by `_split`.

**H4. advisory.** scripts/test_l5_observation.py:459. The generated record names the scorer version but not OBSERVATION_VERSION (P38). Add it to the header line.

## Checked and found correct
- The `_nested` refactor.
- Key parity between `_group_key` and measure.py.
- Pair-wise completeness of the new rules.
- Refusal order: nested, then split, then spread, all before any hole variable is written.
- symmetric implies centered under the new hypot rule (the mean offset is at most 0.71e-7).
- The `symmetric` non-injectivity argument in the amendments.
- The tilt bracket.
- The REASONS face and hole checks.
- Gate 73/73.
- The unit tests: 10 passed.
- ruff and mypy on l5 and the gate: clean.
- The CI step exists (ci.yml:82).
- No scorer import of l5.
- LF line endings and no em dashes.
- The git status of the repo is unchanged by my runs.

## Not checked
- .workshop/NOW.md, audit/README.md, audit/l5-m1-v4-audit.md and the untracked orca.yaml: forbidden or outside the patch.
- Every owner ruling and "audited" claim: they rest on the audit file.
- The full pre-commit suite (`check_release.py`, every `scripts/test_*`, the full pytest run): only the l5 unit tests and the gate were run.
- The Linux fork mode.

No "worker fault: MemoryError" occurred.

## Scratch files
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-final/probe1.py (version-1 reproductions, the H1 D-order construction, thin wall, position split under the limit, false-refusal probes)
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-final/probe2.py (two-face holes on keys, off origin, turned 90 degrees, 3 mm; diameter-key version 1; tilt reason)
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-final/gate.log
- C:/Users/bgare/AppData/Local/Temp/claude/5263f15eea5c4961/9c349acf-951f-4801-b3a3-034b2b5b3627/scratchpad/fixround/blind-final/suite.md
