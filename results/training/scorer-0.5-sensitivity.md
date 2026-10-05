# Scorer 0.5.0 sensitivity of the two registered evaluations

**Descriptive, not a verdict.** The registered results were recorded under scorer 0.4.0 and are
unchanged. Here the same saved answers are re-scored under 0.5.0 (strict contract, 0.1 mm
tolerances). Run on the final scorer 0.5.0 (5 October 2026). Two earlier runs, on two drafts
that external audits then broke with synthetic parts, changed the same verdicts; the reworks
were driven by those synthetic counterexamples, not by these answers.

## Original test split

| Tier | Base 0.4.0 | Base 0.5.0 | Adapter 0.4.0 | Adapter 0.5.0 |
|---|---:|---:|---:|---:|
| L1 | 52/60 | 52/60 | 60/60 | 60/60 |
| L2 | 50/60 | 50/60 | 60/60 | 60/60 |
| L3 | 45/60 | 45/60 | 59/60 | 59/60 |
| L4 | 22/60 | 20/60 | 60/60 | 60/60 |

L2 + L4 gain: recorded +40.0 points [+32.5, +47.5]; under 0.5.0 +41.7 points [+34.2, +49.2].

Base: 2 verdict(s) change:
- L4 test-0007: pass to fail (R5:hole_pattern, R7:edge_margin)
- L4 test-0043: pass to fail (R5:hole_pattern, R7:edge_margin)
Adapter: no verdict changes.

## Replication split

| Tier | Base 0.4.0 | Base 0.5.0 | Adapter 0.4.0 | Adapter 0.5.0 |
|---|---:|---:|---:|---:|
| L1 | 42/60 | 41/60 | 60/60 | 59/60 |
| L2 | 50/60 | 50/60 | 60/60 | 60/60 |
| L3 | 47/60 | 47/60 | 58/60 | 58/60 |
| L4 | 22/60 | 20/60 | 59/60 | 59/60 |

L2 + L4 gain: recorded +39.2 points [+31.7, +46.7]; under 0.5.0 +40.8 points [+33.3, +48.3].

Base: 3 verdict(s) change:
- L1 rep-0037: pass to fail (R5:hole_pattern, R7:edge_margin)
- L4 rep-0005: pass to fail (R5:hole_pattern, R7:edge_margin)
- L4 rep-0034: pass to fail (R5:hole_pattern, R7:edge_margin)
Adapter: 1 verdict(s) change:
- L1 rep-0038: pass to fail (R5:hole_pattern, R7:edge_margin)
