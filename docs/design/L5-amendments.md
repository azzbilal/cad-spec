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

Code: `cad_spec/l5/observation.py`. Gate: `scripts/test_l5_observation.py`
(27 cases, in CI). Result: `results/l5/m1-observation-suite.md`.

**Four verdicts.** `ok`; `form_violation` (the variables are measured, the
part has a feature nobody asked for); `out_of_scope` (a variable would be a
guess); `not_single_solid`. An answer that builds no part raises a build
error, which is gate G1's business.

**Nothing is measured twice.** The numbers come from the strict measurement
of scorer 0.5.0. The form verdict is that scorer's R9, now one function
(`rubric.form_verdict`) that both call.

**Decisions taken in M1**

| Topic | Decision | Why |
|---|---|---|
| Position | Not a contract variable. A plate moved off the origin measures the same; the bounding-box centre is reported for information | design note 7.2 |
| Orientation | L along X, W along Y. Turned 90 degrees about Z, they swap. Turned by any other angle, the side faces leave the axes and the form fails | design note 7.2; the form check |
| What n counts | Through holes along Z only: one open, uninterrupted cylinder from the bottom face to the top face, within the form tolerance. A blind hole is not counted. A fifth hole is counted (n = 5), not hidden | the contract decides, the map only measures |
| No hole | D, mx, my, px, py are `None`, never zero | a missing variable is not a value |
| Stepped or counterbored hole | `out_of_scope` | two coaxial cylinders: which one is D? |
| Holes of different diameters | `out_of_scope` | D is one number in v1 |
| Tilted or cross hole | `out_of_scope`. A new strict measurement, `off_axis_concave`, counts every concave cylindrical face not along Z; the existing diagnostic missed a tilted hole through a thin plate | the map must not ignore a hole it cannot measure |
| Spline surfaces | `form_violation`, with no hole recognised. A known false rejection kept on purpose (scorer review round 3). The kernel pads a spline bounding box by 2e-7 mm, so L, W and T of such a part are not exact | soundness over coverage |

**One deviation from the design note, for approval.** Section 7.2 lists
"extra pocket or slot" as `out_of_scope`. M1 reports it as `form_violation`
with all variables measured. Reason: a pocket does not make any contract
variable ambiguous, amendment 1 already fails every unrequested feature, and
telling "a pocket" from "a fillet" would need feature recognition, which is
new code that no review has seen. `out_of_scope` is kept for the cases where
a number would be a guess. Either verdict fails gate G3. If the owner
prefers the note's wording, the change is one line.

## 4. Open for later milestones

- Change detection (design note 5.3) names 1e-6 mm. Under amendment 2 the
  value should come from the scorer; to be fixed when G4 is built (M3).
- The probe schedule and the exact prompt sentence of amendment 3 (M3).
- Whether `form_violation` is folded into G3 or reported as its own gate G3a
  (M3). The observation already keeps the two apart.
