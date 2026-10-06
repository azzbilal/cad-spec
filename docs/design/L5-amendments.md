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
| M1 Observation and form | observation map, form check, tolerance reuse, adversarial suite, off-origin handling, out-of-scope verdict | every hand-built adversarial model gives the expected observation or an explicit refusal | built, awaiting audit |
| M2 Contract compiler | Contract A schema, typed order operators, Contract B, exact-rational encoding, subset enumeration of MUS and MCS, `allowed_to_move`, `forced`, witness, compiled-item schema | items reproduce from their semantic state and compile to correct static artifacts | not started |
| M3 Runtime grader and intent | gates G0 to G5, CQGI parameter interface, change detection, inherited behaviour, sensitivity-filtered probes, structured rejects, accepted-MUS lookup, near-twins | witnesses pass, hardcoded witnesses fail on intent-bearing items, infeasible items accept only minimal conflict sets | not started |
| M4 Diversity, diagnostics, baselines | code and language renderers, equivalence checks, misconception library, separability, the five baselines, the full per-item checklist | every item passes the generator-side checklist and every diagnostic is separable | not started |
| M5 Evaluation protocol | splits, MCD only if the compound count supports it, hidden three-seed schedule, manifest and commitment, sealed set, report format, latency statistics | L5-v1 can be frozen, committed, reproduced after seed release and evaluated identically across models | not started |

## 3. M1 record: what the observation map does

Code: `cad_spec/l5/observation.py` (observation version 1, built on scorer
0.5.0 by name). Gate: `scripts/test_l5_observation.py` (58 cases, in CI).
Result: `results/l5/m1-observation-suite.md`.

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
| What n counts | Through holes along Z only: one open, uninterrupted cylinder from the bottom face to the top face, within the form tolerance. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures |
| px, py | The extent of the hole centres along X and Y. For the four-corner pattern that is the pitch; for any other pattern it is only the extent, and `rectangular` is then False | the design note defines pitch for the family only |
| Hole centre | Measured where the axis crosses the mid-plane of the plate. The design note says the top face. For an accepted axis the two differ by at most (T / 2) x 1e-12: 7e-12 mm for the thickest generated plate (14 mm) | one measurement shared with the scorer |
| No hole | D, mx, my, px, py are `None`, never zero | a missing variable is not a value |
| Stepped, counterbored or offset hole | `out_of_scope`: two different cylinders, one with its axis strictly inside the other (two 10 mm holes 5.0 mm apart are not nested; 4.999 mm apart they are). Judged on the unrounded axis and diameter of every concave cylinder face | D is not one number. The scorer's grouping rounds diameters to 1e-4 mm and hid a 1e-6 step |
| Holes of different diameters | `out_of_scope` when the measured diameters differ by more than the dimension slack, 1e-9 mm. Values are binary doubles: holes written 10 and 10.000000001 measure 1.00000008e-9 apart and are refused | D is one number in v1; the verdict must not depend on which hole comes first |
| Tilted or cross hole | `out_of_scope` for any concave cylinder whose axis is not along Z beyond floating-point slack (1e-12 rad). At that slack every variable is still right to about 1e-11 mm (the kernel reads T = 4.00000000001 on a 4 mm plate with 10 mm holes) | a 1e-8 rad tilt was `ok` with a margin wrong by 2e-8 mm |
| Supported size | `out_of_scope` when any cylindrical face is under 0.01 mm in diameter (exactly 0.01 mm is measured). This comes before the form check, so a fillet under that size is a size refusal, not the `form_violation` of amendment 1 | the probe that tells a hole from a boss cannot classify smaller ones; refusing is honest, reporting n = 0 was not |
| Failed scope scan | `out_of_scope`, with the reason | it used to raise an exception out of the map |
| Spline surfaces | `form_violation`, with no hole recognised. A known false rejection kept on purpose (scorer review round 3). The kernel pads a spline bounding box by 2e-7 mm, so L, W and T of such a part are not exact | soundness over coverage |

**One deviation from the design note, for the owner's approval.** Section
7.2 lists "extra pocket or slot" as `out_of_scope`. M1 reports it as
`form_violation`. Reason: a separate pocket does not make any contract
variable ambiguous, amendment 1 already fails every unrequested feature, and
telling "a pocket" from "a fillet" would need feature recognition, which is
new code that no review has seen. A pocket that cuts into a hole does make
the hole ambiguous and is refused by the rules above. Either verdict fails
gate G3. The external reviewer chose the same verdict, with that condition.

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

| # | Finding | Change |
|---|---|---|
| R1 | Holes tilted by 1e-8 rad were `ok` with a wrong margin; tilts up to 1e-6 rad were not refused | any tilt beyond 1e-12 rad is `out_of_scope` |
| R2 | A radius step of 1e-6 mm was reported as `form_violation` with a chosen D, because diameters were grouped after rounding | unrounded cylinder data kept by the strict measurement; nested cylinders refused |
| R3 | Diameters differing by 1e-8 mm were `ok`, with D taken from the first hole | compared at the dimension slack, 1e-9 mm |
| R4 | A cross bore of 0.2 micron was missed: the inward probe crossed it | probe limited to half a radius, an unclear result is an error, and features under 0.01 mm are refused |
| R5 | A failed scope scan made the map raise instead of refusing | explicit strict marker on the measurement; failures are `out_of_scope` |

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
