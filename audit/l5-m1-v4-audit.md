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
  checks, and a conditional verdict.
- **Section 13, the final round.** The owner's last rulings, the 180
  ordinary controls rerun, a final Codex review and two final blind
  reviews, and the final verdict on M1.

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

## 12. Verdict after the fix round (superseded by section 13)

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

## 13. Final round (27 November 2026)

### 13.1 Owner's rulings

| Item | Ruling |
|---|---|
| G1 | Tighten the axis-spread limit to 0.5e-9 mm; bracketing cases on X and on the diagonal; a two-hole case showing px and py stay within 1e-9 mm under `ok` |
| G2 | Document and defer to M3. Superseded by the H1 ruling below |
| F8 | Bump `OBSERVATION_VERSION` to "2"; say why in the amendments and the CHANGELOG release plan |
| F3 | Narrow the rule 3 exception to `results/l5/m1-observation-suite.md` only |
| F2 | Narrow exceptions in rules 5 and 8, with the exact text shown to the owner |
| LOG.md | Commit it |
| H1 (raised by the final blind review) | Asked during the round with the reproduction in hand: compare D over every face of the through holes, now |

Section 10 said the G2 order dependence was only a false refusal. That was
wrong: in one cut order the part was `ok` with D = 10.0000000009 while
another hole had a face at 9.9999999991, 1.8e-9 mm away (H1, reproduced
below). The G2 ruling rested on that wrong statement, so the question went
back to the owner.

### 13.2 What changed

| Item | What changed | Evidence |
|---|---|---|
| G1 | `SPREAD_LIMIT_MM = EPS_DIM_MM / 2` in `observation.py`; `_axis_spread` refuses above it. Cases: 0.45e-9 (ok), 0.55e-9 and a diagonal 0.57e-9 (refused); two holes split on X in both cut orders and two opposite corners split on the diagonal (ok) | Measured: px - 70 = 9.0e-10 in one order and 0 in the other; on the diagonal px - 70 = py - 50 = 7.0e-10. Every case built from separate faces checks that the kernel kept them (5 or 6 faces) |
| H1 | `_through_face_diameters`: the "one D" check runs over every face of the through holes. Cases: the H1 construction in two cut orders (refused) and faces 0.9e-9 apart over two holes (ok) | Before: `ok` with D = 10.0000000009 (1.8e-9 mm from a face), or `ok` with D = 10.0, or `out_of_scope`, depending on order (`probe_h1`). Previous rule stubbed back in: both refusal cases become `ok` (`mut_h`) |
| F8 | `OBSERVATION_VERSION = "2"`; amendments section 3 says what changed and why, and that version 1 was never released; CHANGELOG release plan says the same; the generated file's header names the version (H4) | `git ls-tree v0.5.0` has no `cad_spec/l5/` (checked by the final blind review) |
| F3 | Rule 3 exception names `results/l5/m1-observation-suite.md` only; the gate's docstring, the amendments and the CHANGELOG say the same | CLAUDE.md rule 3 |
| F2 | Narrow exceptions in rules 5 and 8 | CLAUDE.md rules 5 and 8 (exact text below) |
| G2 | Deferral text removed from section 4 of the amendments; the "Holes of different diameters" row now states the all-face check | Superseded by H1 |
| H2 | CHANGELOG release plan names `rubric.py` (`form_verdict` extracted) among the files changed since v0.5.0 | `git diff --stat v0.5.0 -- environments/cad_spec/cad_spec/` |
| H3 | Case `review_hole_split_across_position_key_under_the_spread_limit` (axes 4e-10 apart around 20.0005): only the grouping rule can refuse it | Grouping rule stubbed out: `ok` with n = 3 (`mut_h`) |
| J1, J5, J6 | Docstring of `_through_face_diameters` states its precondition; CHANGELOG line break; module docstring lists the split refusal | Text only |
| LOG.md | In the commit list | |

Exact text of the rule exceptions (CLAUDE.md):

```text
Rule 3: One exception (ruled 27 November 2026):
`results/l5/m1-observation-suite.md` is generated output of the L5 gate.
`scripts/test_l5_observation.py --out results/l5/m1-observation-suite.md`
rewrites it in place, and the file says so in its header. No other file
under `results/` is covered.

Rule 5: One exception (ruled 27 November 2026): `cad_spec/l5/` (the L5
observation map, not yet released) may change before the next package
release, which ships it. Each change is listed under "Unreleased" in
`CHANGELOG.md`, and a change in meaning bumps `OBSERVATION_VERSION`. The
exception does not cover `measure.py`, `rubric.py`, `environment.py`,
`tasks.py` or any scorer version.

Rule 8: One exception (ruled 27 November 2026): regenerating
`results/l5/m1-observation-suite.md` with the command named in rule 3 is
not verification and writes over that file on purpose. Verification runs
of the gate write `--out` to a temporary folder.
```

Gate: 70 cases before this round, 77 after (G1: 3 bracket cases replaced by
3, plus 3 two-hole cases; H1: 3; H3: 1).

### 13.3 The 180 ordinary-construction controls

The 180 controls of the first review (`audit/l5-m1-audit.md`, category
`controls`: six train and dev specifications, ten construction styles, each
native, translated and mirrored) were parsed from that file with their
expected verdicts and all twelve expected values, and rerun through
`observe_code` (`controls.py`).

| Run | Code | Checked | `ok` as expected | Newly refused | Wrong values | Largest difference | Largest axis spread between faces of one cylinder |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | observation version 2, spread limit 0.5e-9, before the H1 fix | 180 | 180 | 0 | 0 | 7.105e-15 mm | 0 |
| 2 | final code (with the all-face D check) | 180 | 180 | 0 | 0 | 7.105e-15 mm | 0 |

No ordinary part is refused by the split rule, the spread rule, the
straight-line `centered` or the all-face D check. The first attempt at run 1
stopped on a reuse-worker fault (below); the runner was then given one retry
on a fresh worker per call, and neither completed run needed it.

### 13.4 Reviews

| Review | Time | Result | Saved output |
|---|---:|---|---|
| Codex, `codex review --base main -c 'sandbox_mode="read-only"' -c 'approval_policy="never"'` | 123 s | No findings. Ran the gate (73/73), the L5 pytest file (10/10), test_rubric_050 (81/81), test_rubric (37/37) and lint. It saw the 73-case tree: version 2 and the 0.5e-9 limit, but not the H1 fix, H3, H4 or J1, J5, J6 | `.workshop/reviews/codex-final.md` |
| Blind checker, whole diff | 784 s | SHIP WITH FIXES; H1 to H4 | `.workshop/reviews/blind-final.md` |
| Blind checker, delta after the H1 fix | 612 s | SHIP; J1 to J6 (advisory and notes) | `.workshop/reviews/blind-delta-final.md` |

| ID | Source | Finding | Verdict | Action |
|---|---|---|---|---|
| X2 | Codex | No actionable regression | agreed | None |
| H1 | Blind | Under `ok`, D can be 1.8e-9 mm from a face of another hole; the G2 text was false | confirmed (`probe_h1`) | Fixed by ruling (13.2) |
| H2 | Blind | CLAUDE.md deferred list omits the D item; CHANGELOG omits `rubric.py`; no gate case for the thin edge wall | confirmed | The D item is no longer deferred, so CLAUDE.md is right; `rubric.py` added. The thin-wall case is listed for the owner |
| H3 | Blind | No position-key split under the spread limit | confirmed | Fixed (13.2) |
| H4 | Blind | The generated file does not name the observation version | confirmed | Fixed |
| J1 | Blind delta | Precondition of `_through_face_diameters` not stated; the extra term is redundant | confirmed | Docstring states it; the term is kept and labelled a guard |
| J2 | Blind delta | `split_hole` and `split_holes` take tuples in different orders | confirmed | Listed for the owner (a test-helper refactor) |
| J3 | Blind delta | A later cut with the default `clean` merges split halves into one face, which the map then measures exactly | note | Listed: one sentence in the amendments, if wanted |
| J4 | Blind delta | The "was `ok`" text of the other-order D case depends on the kernel's face order | note | Listed |
| J5 | Blind delta | CHANGELOG line break | confirmed | Fixed |
| J6 | Blind delta | Module docstring omits the split refusal | confirmed | Fixed |

The fix-round blind review's F2 and F3 were closed by the owner's rulings
(13.1). F6 (reason checks for the older refusal cases) stays listed.

### 13.5 Checks (final working tree)

| Check | Result |
|---|---|
| L5 gate | 77/77; tracked `results/l5/m1-observation-suite.md` byte-identical to a scratch run |
| L5 pytest | 10 passed |
| `test_rubric_050` | 81/81 |
| `test_rubric` | 37/37 |
| `check_release` | all document links resolve |
| Full CLAUDE.md commit checks (238 s) | ruff scripts, package ruff, mypy: clean. pytest 139 passed, 12 skipped (Linux-only: fork sandbox, GL fallback). All 12 `scripts/test_*.py` pass |
| After J1, J5, J6 (text only) | ruff, mypy, L5 pytest 10, gate 77/77 (identical file), `check_release` |
| Files in `cad_spec/` changed against `main` | `l5/observation.py` only. `measure.py`, `rubric.py`, `environment.py`, the frozen scripts and every recorded result other than the one generated file are unchanged |
| Text | No em dash, LF only, in every file of the commit list (checked byte-wise) |

**Reuse-worker fault, observed and not explained.** In one gate run during
this round, two unchanged cases (`review_second_cut_0.4_micron_off`,
`boundary_diameters_5e-10_apart`) came back as build errors with "worker
fault: MemoryError". Two immediate reruns, and every later run, gave every case
as expected. The first controls attempt stopped on the same fault. 19 GB of
RAM was free and the commit charge was 46 of 62 GB. `measure.py`, which owns
the worker, was not touched. In a scored run on Windows this fault would turn
a correct answer into a build error. Listed for the owner.

### 13.6 Final verdict on M1

**Yes: M1 is audited once this branch is merged.**

- Four wrong values under `ok` were found in this audit. Each is now refused,
  and gate cases pin each refusal; they fail against the previous rules:
  - one hole split across the measurement's grouping (n = 3);
  - faces of one hole disagreeing on its axis (mx off by 8e-8 mm);
  - px and py off by up to 1.8e-9 mm (spread limit now 0.5e-9 mm);
  - D off by up to 1.8e-9 mm (all-face check).
- Under `ok`, each hole position is within 0.5e-9 mm, and px, py and D are
  within 1e-9 mm, whichever faces the measurement reads. The final blind
  reviews found no construction that breaks this.
- The 180 ordinary controls: all `ok`, no refusal, largest difference
  7.1e-15 mm.
- Every full check passes.
- What stays open fails closed or is a note:
  - A1, the probe point: deferred to M3.
  - The two scorer-path defects: deferred to the next scorer version.
  - The pocket deviation: still awaits approval.
  - J2 to J4, F6, the thin-wall case and the worker fault are listed below.

Caveats:
- Codex did not see the H1 fix. The blind check of the H1 fix said SHIP.
- J1, J5 and J6 (text only) were not reviewed again.
- Linux `fork` mode was not run locally.
- The rule exceptions rest on the owner's rulings in this session. The
  final blind review could not verify them and asked that the owner confirm
  them himself.

Listed for Bilal:
- J2: unify the tuple order of the two gate helpers.
- J3: a sentence on kernel merging of split faces, if wanted.
- J4: the other-order D case's "was `ok`" text depends on the kernel's face
  order.
- F6: reason checks for the older refusal cases.
- H2: a gate case for the thin edge wall (1e-7 mm refused, 1e-6 mm
  measured).
- The reuse-worker `MemoryError` fault.
- Approval of the pocket deviation.
- Optional: a read-only Codex review of the H1 fix.

### 13.7 Pocket deviation approved (27 November 2026, after section 13.6)

The owner asked whether the pocket deviation (design note 7.2 says
`out_of_scope`; the map says `form_violation`) can ever give a wrong value
under `ok`. A probe of twelve variants through `observe_code`
(`probe_pocket.py`) gave no `ok`:
- `form_violation`: top and bottom rectangular pockets, round blind pockets
  of 6 and 10 mm, a through slot, edge and corner notches, a pocket cutting
  into a hole, a pocket 5 microns deep.
- `out_of_scope`: a pocket with R2.5 corners (nested corner cylinders).
- Not tested: pockets 2e-7 and 5e-8 mm deep, which CadQuery refused to
  build. A pocket shallower than the form tolerance would be the nominal
  part within that tolerance anyway.

The deviation changes only which refusal is reported, never a value under
`ok`. The owner approved it on 27 November 2026. It is recorded in the
amendments (deviation paragraph), the CHANGELOG and `.workshop/LOG.md`. The
"awaits approval" items in sections 12 and 13.6 are closed by this.
