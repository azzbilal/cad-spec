# Screening report

## Qwen/Qwen3.5-9B (hint arm, temperature 0.0, 1 sample(s) per spec, max_tokens 1024)

File `results/training/screening/qwen3.5-9b-greedy.jsonl`, split eval, scorer 0.4.0, status complete, spent $0.034399, commit 5749eb4.
Extra body: `{"chat_template_kwargs": {"enable_thinking": false}}`.

### Scores

| Tier | Answers | All-pass | pass@k | Mean reward | Mean reward (finished only) |
|---|---|---|---|---|---|
| L1 | 30 | 80% | 80% | 0.844 | 0.905 |
| L2 | 30 | 63% | 63% | 0.881 | 0.881 |
| L3 | 30 | 87% | 87% | 0.919 | 0.919 |
| L4 | 30 | 43% | 43% | 0.848 | 0.848 |
| All | 120 | 68% | 68% | 0.873 | 0.888 |

### Learning signal (groups of samples of one spec)

| Tier | Groups | With signal | Flat: all solved | Flat: all zero | Flat: same partial | Mean group std | Mean abs advantage |
|---|---|---|---|---|---|---|---|
| L1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| L2 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| L3 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| L4 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| All | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

### Learning signal under the binary training reward (1.0 only when all nine pass)

| Tier | With signal | Mean abs advantage | Mean abs advantage per useful group |
|---|---|---|---|
| L1 | n/a | n/a | n/a |
| L2 | n/a | n/a | n/a |
| L3 | n/a | n/a | n/a |
| L4 | n/a | n/a | n/a |
| All | n/a | n/a | n/a |

### Truncation

| Tier | Truncated | Cut off | Degenerate | Mean reward if truncated | Output tokens of finished answers (p50 / p90 / p99 / max) |
|---|---|---|---|---|---|
| L1 | 7% | 7% | 0% | 0.000 | 446 / 681 / 885 / 885 |
| L2 | 0% | 0% | 0% | n/a | 345 / 416 / 518 / 518 |
| L3 | 0% | 0% | 0% | n/a | 388 / 666 / 705 / 705 |
| L4 | 0% | 0% | 0% | n/a | 93 / 95 / 305 / 305 |
| All | 2% | 2% | 0% | 0.000 | 345 / 544 / 754 / 885 |

## Qwen/Qwen3.5-9B (hint arm, temperature 0.7, 8 sample(s) per spec, max_tokens 2048)

File `results/training/screening/qwen3.5-9b-t0.7-x8-2k.jsonl`, split eval, scorer 0.4.0, status complete, spent $0.310176, commit 47f35ae.
Extra body: `{"chat_template_kwargs": {"enable_thinking": false}, "top_p": 1.0, "top_k": -1, "min_p": 0.0}`.

### Scores

| Tier | Answers | All-pass | pass@k | Mean reward | Mean reward (finished only) |
|---|---|---|---|---|---|
| L1 | 240 | 62% | 100% | 0.719 | 0.725 |
| L2 | 240 | 69% | 100% | 0.809 | 0.809 |
| L3 | 240 | 64% | 100% | 0.737 | 0.749 |
| L4 | 240 | 43% | 63% | 0.850 | 0.850 |
| All | 960 | 59% | 91% | 0.779 | 0.784 |

### Learning signal (groups of samples of one spec)

| Tier | Groups | With signal | Flat: all solved | Flat: all zero | Flat: same partial | Mean group std | Mean abs advantage |
|---|---|---|---|---|---|---|---|
| L1 | 30 | 100% | 0% | 0% | 0% | 0.378 | 0.323 |
| L2 | 30 | 97% | 3% | 0% | 0% | 0.308 | 0.247 |
| L3 | 30 | 100% | 0% | 0% | 0% | 0.373 | 0.319 |
| L4 | 30 | 33% | 33% | 0% | 33% | 0.055 | 0.044 |
| All | 120 | 82% | 9% | 0% | 8% | 0.279 | 0.233 |

### Learning signal under the binary training reward (1.0 only when all nine pass)

| Tier | With signal | Mean abs advantage | Mean abs advantage per useful group |
|---|---|---|---|
| L1 | 100% | 0.426 | 0.426 |
| L2 | 97% | 0.393 | 0.406 |
| L3 | 100% | 0.419 | 0.419 |
| L4 | 30% | 0.093 | 0.309 |
| All | 82% | 0.333 | 0.407 |

### Truncation

| Tier | Truncated | Cut off | Degenerate | Mean reward if truncated | Output tokens of finished answers (p50 / p90 / p99 / max) |
|---|---|---|---|---|---|
| L1 | 1% | 1% | 0% | 0.000 | 515 / 889 / 1535 / 1611 |
| L2 | 0% | 0% | 0% | n/a | 361 / 550 / 1035 / 1132 |
| L3 | 2% | 2% | 0% | 0.000 | 430 / 794 / 1917 / 1999 |
| L4 | 0% | 0% | 0% | n/a | 93 / 95 / 296 / 873 |
| All | 1% | 1% | 0% | 0.000 | 379 / 722 / 1589 / 1999 |

## Qwen/Qwen3.5-9B (hint arm, temperature 1.0, 8 sample(s) per spec, max_tokens 1024)

File `results/training/screening/qwen3.5-9b-t1.0-x8.jsonl`, split eval, scorer 0.4.0, status complete, spent $0.339464, commit 5749eb4.
Extra body: `{"chat_template_kwargs": {"enable_thinking": false}}`.

### Scores

| Tier | Answers | All-pass | pass@k | Mean reward | Mean reward (finished only) |
|---|---|---|---|---|---|
| L1 | 240 | 37% | 97% | 0.414 | 0.529 |
| L2 | 240 | 44% | 100% | 0.536 | 0.562 |
| L3 | 240 | 40% | 97% | 0.477 | 0.556 |
| L4 | 240 | 41% | 70% | 0.813 | 0.816 |
| All | 960 | 40% | 91% | 0.560 | 0.624 |

### Learning signal (groups of samples of one spec)

| Tier | Groups | With signal | Flat: all solved | Flat: all zero | Flat: same partial | Mean group std | Mean abs advantage |
|---|---|---|---|---|---|---|---|
| L1 | 30 | 100% | 0% | 0% | 0% | 0.445 | 0.414 |
| L2 | 30 | 100% | 0% | 0% | 0% | 0.437 | 0.403 |
| L3 | 30 | 97% | 0% | 3% | 0% | 0.430 | 0.399 |
| L4 | 30 | 50% | 33% | 0% | 17% | 0.108 | 0.084 |
| All | 120 | 87% | 8% | 1% | 4% | 0.355 | 0.325 |

### Learning signal under the binary training reward (1.0 only when all nine pass)

| Tier | With signal | Mean abs advantage | Mean abs advantage per useful group |
|---|---|---|---|
| L1 | 97% | 0.415 | 0.429 |
| L2 | 100% | 0.426 | 0.426 |
| L3 | 97% | 0.405 | 0.419 |
| L4 | 37% | 0.116 | 0.315 |
| All | 82% | 0.340 | 0.413 |

### Truncation

| Tier | Truncated | Cut off | Degenerate | Mean reward if truncated | Output tokens of finished answers (p50 / p90 / p99 / max) |
|---|---|---|---|---|---|
| L1 | 22% | 22% | 0% | 0.000 | 543 / 856 / 1019 / 1022 |
| L2 | 5% | 4% | 0% | 0.000 | 406 / 695 / 977 / 1009 |
| L3 | 14% | 14% | 0% | 0.000 | 486 / 854 / 994 / 1013 |
| L4 | 0% | 0% | 0% | 0.000 | 93 / 96 / 560 / 898 |
| All | 10% | 10% | 0% | 0.000 | 390 / 758 / 996 / 1022 |
