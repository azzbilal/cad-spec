# Training run 1: pre-registered verdict

Base `Qwen/Qwen3.5-9B` vs adapter `Qwen/Qwen3.5-9B:xfisiyo5vlhn0ys65sf4uad7`, locked test split, greedy.

| Tier | Base all-pass | Adapter all-pass | Difference (points) | 95% interval |
|---|---|---|---|---|
| L1 | 86.7% | 100.0% | +13.3 | [+5.0, +21.7] |
| L2 | 83.3% | 100.0% | +16.7 | [+8.3, +26.7] |
| L3 | 75.0% | 98.3% | +23.3 | [+13.3, +35.0] |
| L4 | 36.7% | 100.0% | +63.3 | [+51.7, +75.0] |

**H1 (L2 + L4, primary): CONFIRMED.** Difference +40.0 points, 95% interval [+32.5, +47.5], 120 pairs. Worthwhile (registered minimum +10 points).

H2 (L4 alone, secondary): gain, +63.3 points [+51.7, +75.0].

Regression check L1: no regression (+13.3 points; flagged below -10).
Regression check L3: no regression (+23.3 points; flagged below -10).
