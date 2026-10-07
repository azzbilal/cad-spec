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

F92-GTA §1, §5; F89-LSQ §1.2; F18-PSS §3.4-3.5; FWSO13 §1; PK14 §2.1;
TRACIM18 §2.1; L5 amendments §3 (M1 record and review findings R1 to R5).
Principles P10, P17, P19, P21, P27, P37, P44; EDR-001, EDR-006.

## Related skills

cad-spec-uncertainty-and-error, cad-spec-datum-gdt-reasoning,
cad-spec-geometric-fitting, cad-spec-numerical-validation.
