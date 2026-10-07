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

F18-PSS §3-4; FWSO13 §1, §4-5; PK14 §2.1; F92-GTA §5, §6; scorer docstring
(datums R5, R7, R8); design note §7.2; amendments §3. Principles P16 to P21,
P42, P43.

## Related skills

cad-spec-geometric-observation, cad-spec-geometric-fitting,
cad-spec-conformity-decision.
