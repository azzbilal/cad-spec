---
name: cad-spec-geometric-fitting
description: Read before any cad-spec work that fits ideal geometry to points or facets - meshes, STL, faceted STEP, tessellation, scans or CMM data, best-fit planes, circles, cylinders, cones, minimum-zone (Chebyshev) form, maximum-inscribed or minimum-circumscribed features, template matching of a CAD shape to data. Not used by the exact analytic B-rep path of L1 to L5; this skill defines what must exist before such inputs are accepted.
---

# cad-spec-geometric-fitting

## Purpose

Prevent the most common errors when cad-spec leaves the exact domain:
wrong criterion, unstable parametrisation, unrepresentative data, assumed
isotropic errors, and minimax problems treated as least squares.

## When this skill MUST be used

Any proposal to accept a mesh, STL, faceted STEP, point cloud or measured
data; any "best fit" or "form error" computation; any future GD&T form
evaluation.

## When this skill should NOT be used

Reading analytic planes and cylinders from a B-rep (no fit happens there).

## Required inputs

The criterion demanded by the specification (least squares, minimax,
inscribed, circumscribed); the data and its domain; the error model if any.

## Preconditions

A computational aim for the fit (P37) naming the criterion; at least the
minimum point count per element, preferably twice the minimum, well
distributed (F89-LSQ); a starting-value method.

## Core expert principles

1. **P10 / P16** The criterion is part of the meaning. Least squares (mean
   behaviour, maximum likelihood under iid errors) and minimax (zone, the
   GD&T form definition) answer different questions. Least squares
   over-estimates a minimum zone (F92-GTA §8).
2. **P11** Parametrise for stability: translate to the centroid; direction
   `(a, b, 1)` only near vertical, otherwise rotate to standard position each
   iteration; no `tan 2 theta` formulas; no dependence on normal sign.
3. **P12** Gauss-Newton needs good starts and representative data; partial
   arcs and small patches converge slowly, diverge or make J rank deficient.
4. **P13** Linearised fits are starting values or bounds, not verdicts.
5. **P14** ODR is maximum likelihood only for iid isotropic errors; real
   instruments are correlated and anisotropic; the isotropy assumption can
   misstate parameter uncertainty by factors of two to four.
6. **P16 / P36** Minimax has local minima, degeneracy, vertex and non-vertex
   solutions; a claim of the minimum zone needs a stated optimality
   guarantee.
7. **P08** With a fixed CAD template, only the rigid (and optional scale)
   transformation is fitted; symmetry fixes some parameters (a cylinder needs
   four).

## Formal reasoning procedure

1. Name the criterion from the specification; refuse if unstated.
2. Check data adequacy (count, coverage, arc fraction); refuse below limits.
3. Centre and orient; fit; check the three convergence criteria (change in
   objective, step size, gradient `J^T d`).
4. Check J rank and conditioning; refuse when rank deficient or
   ill-conditioned (P20).
5. For minimax, verify KKT conditions at the solution and state whether
   global optimality is guaranteed.
6. Propagate uncertainty with the sensitivity matrix (P15) if the domain has
   one; otherwise state that only numerical error is reported.

## Mathematical / geometric operators

```yaml
ls_fit:        min sum d_i^2; U_b = (J^T J)^-1 J^T U_d J (J^T J)^-T (P15)
gauss_markov:  min e^T U^-1 e with structured U = B B^T; O(m) with structure (F06-FIT §3.5)
chebyshev:     min e s.t. -e <= d_i <= e; up to n+1 active constraints at a vertex
inscribed / circumscribed: one-sided constraints on distances to centre or axis
template_match: rows [-n*_i, x*_i x n*_i, -(x*_i)^T n*_i] for translation, rotation, scale
```

## Decision rules

No fitted value may enter a verdict without its criterion, its adequacy
checks and its numerical accuracy statement.

## Failure modes

FP10 wrong criterion; FP18 conditioning and multiple optima; FP27 assumed
iid isotropic errors; FP17 datum form error.

## Numerical hazards

Data far from the origin (loss of accuracy); near-horizontal axes under
`(a, b, 1)`; partial arcs; degenerate minimax solutions; convergence
tolerances that suit one data set and not another (FM12 §2).

## Out-of-scope cases

Everything in L1 to L5 today. Probe radius compensation (P41) unless CMM
data are accepted.

## Validation requirements

Reference pairs built from known answers (FM12): null-space perturbations
for least squares (`J^T e = 0`), KKT-partition data for Chebyshev vertex
solutions; correlated form error from a Gaussian-process kernel for realism
(P40); the TraCIM inventory (P39) as the list of fits that need verification.

## Required evidence

Criterion, point count and coverage, convergence record, rank, residual
statistics, accuracy measure (forward or backward, P33).

## Implementation checklist

- [ ] computational aim with criterion
- [ ] adequacy refusal rules
- [ ] stable parametrisation and centring
- [ ] rank and conditioning checks
- [ ] reference pairs from known answers

## Review checklist

- [ ] is the criterion the one the specification means?
- [ ] what happens on a 30 degree arc?
- [ ] what happens with an even point count on a lobed feature (P09)?

## Tests that must exist

Null-space LS artefacts (same fit, different deviations); a lobed circle
where LS and minimum-zone differ by a known amount; partial-arc refusal;
near-horizontal axis stability; Chebyshev vertex artefact.

## Anti-patterns

LS fit plus maximum residual reported as flatness or cylindricity; default
isotropic weighting without saying so; a fitted value with no criterion.

## Source provenance

F89-LSQ (abstract, §2.2, §3.4, §6.4, §8, §9.4, §11.4; OCR, medium
confidence on page mapping); F92-GTA §5, §6, §8; F06-FIT §2-4; FM12 §2-5;
TRACIM-DB rows 21-22, 33-44, 60-79. Principles P08, P10 to P16, P20, P33 to
P36, P39 to P41.

## Related skills

cad-spec-geometric-observation, cad-spec-uncertainty-and-error,
cad-spec-datum-gdt-reasoning, cad-spec-numerical-validation.
