# Replication 1: pre-registered verdict

Base `Qwen/Qwen3.5-9B` vs adapter `Qwen/Qwen3.5-9B:xfisiyo5vlhn0ys65sf4uad7`, replication split, greedy.

| Tier | Base all-pass | Adapter all-pass | Difference (points) | 95% interval |
|---|---|---|---|---|
| L1 | 70.0% | 100.0% | +30.0 | [+18.3, +41.7] |
| L2 | 83.3% | 100.0% | +16.7 | [+8.3, +26.7] |
| L3 | 78.3% | 96.7% | +18.3 | [+6.7, +30.0] |
| L4 | 36.7% | 98.3% | +61.7 | [+50.0, +73.3] |

**R1 (L2 + L4, primary): REPLICATED.** Difference +39.2 points, 95% interval [+31.7, +46.7], 120 pairs (registered: lower bound above 0 and at least +10 points).

R2 (L4 alone, secondary): gain, +61.7 points [+50.0, +73.3].

R3 (size against the original test split): CONSISTENT. Original +40.0, replication +39.2, difference -0.8 points [-11.7, +10.0].

R4 (specs where the adapter passes both L2 and L4, exact two-sided 95% lower bound): replication 59/60, at least 91.1%; original 60/60, at least 94.0%; pooled 119/120, at least 95.4%.

Regression check L1: no regression (+30.0 points; flagged below -10).
Regression check L3: no regression (+18.3 points; flagged below -10).

Pairs improved 78, worsened 2.

Adapter failures:

- L3 rep-0014: no check recorded (length; base passes)
- L3 rep-0056: no check recorded (length; base passes)
- L4 rep-0020: R5:hole_pattern, R7:edge_margin (stop; base fails too)
