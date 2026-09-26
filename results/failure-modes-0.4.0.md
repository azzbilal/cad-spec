# Failure modes, cad-spec 0.4.0

Tiers L0, L1, L2, L3, L4. Each failed answer gets one label (first match, in column order). Cells are the share of ALL the model's answers; the last column is the all-pass rate.

## Models

| Model | API error | degenerate loop | cut off | syntax error | CadQuery API error | geometry kernel failure | Python error in model code | no part produced | timeout | build failed | change order ignored | change not propagated to pitch | holes stacked at one point | no holes | pattern anchored at a corner | margin applied twice | X and Y swapped | pitch read as coordinates | one axis misplaced | some holes right, some wrong | holes misplaced (other) | gate: simple_through_holes | wrong plate size | off Z datum | wrong hole diameter | wrong hole count | all pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-coder:1.5b |  | 1% |  |  | 21% | 7% | 7% |  | 1% |  |  | 10% | 2% | 19% |  |  |  |  |  |  | 8% |  |  |  |  |  | 25% |
| google/gemma-3-4b-it | 1% | 1% |  |  | 40% | 7% | 1% |  |  |  |  | 13% |  | 8% |  |  |  |  | 1% |  | 3% |  | 1% |  |  |  | 26% |
| meta-llama/llama-3.1-8b-instruct |  | 9% |  | 2% | 35% | 8% | 1% | 1% |  | 1% |  | 11% |  | 3% |  |  |  |  | 1% |  | 2% |  |  |  | 1% |  | 26% |
| google/gemma-3-27b-it |  |  |  |  | 9% | 2% |  |  |  |  |  | 11% | 36% |  |  | 1% |  |  |  | 13% |  |  |  |  |  |  | 29% |
| mistralai/codestral-2508 |  |  |  |  | 14% |  |  |  |  |  |  | 8% | 33% |  |  |  |  |  | 1% | 5% | 9% |  |  |  |  |  | 31% |
| meta-llama/llama-3.3-70b-instruct |  |  |  |  | 37% |  |  |  |  |  |  | 6% | 7% | 5% |  |  |  |  | 1% | 1% | 5% | 3% |  | 1% |  |  | 33% |
| microsoft/phi-4 |  |  |  |  | 18% |  | 1% |  |  |  |  | 13% | 18% | 1% |  |  |  |  |  | 10% | 5% |  | 1% |  |  |  | 33% |
| qwen/qwen3-30b-a3b-instruct-2507 |  |  | 1% |  | 7% |  |  |  |  |  |  | 11% |  | 5% |  |  | 1% |  |  | 18% | 5% | 11% |  | 7% | 1% |  | 33% |
| qwen/qwen3-coder-30b-a3b-instruct |  |  | 1% |  | 1% | 1% |  | 22% |  |  |  | 8% | 1% | 4% |  | 1% |  |  |  | 5% | 17% | 1% |  |  |  |  | 37% |
| mistralai/mistral-small-3.2-24b-instruct |  |  |  |  | 29% |  |  | 2% |  |  |  | 8% | 8% | 3% |  |  | 1% |  | 2% |  | 3% | 1% |  | 1% |  |  | 43% |
| meta-llama/llama-4-maverick |  |  |  |  | 23% |  |  |  |  |  |  | 5% |  | 1% |  |  | 1% |  | 3% |  | 5% |  |  | 15% |  |  | 45% |
| openai/gpt-4o-mini |  |  |  |  |  |  |  | 1% |  |  |  | 12% |  | 1% |  | 13% | 1% |  | 1% | 5% | 9% |  |  |  | 5% |  | 52% |
| qwen/qwen3-235b-a22b-2507 |  |  |  | 1% | 9% |  |  | 1% |  | 1% |  | 9% |  | 1% | 1% |  | 1% |  |  | 4% | 2% | 2% |  |  | 1% | 1% | 67% |
| qwen/qwen3-coder-next |  |  | 1% |  | 4% |  |  | 2% |  |  |  | 7% |  | 8% |  |  | 1% |  |  | 7% | 2% |  |  |  |  |  | 68% |
| openai/gpt-4.1-nano |  |  |  | 3% |  | 1% | 1% |  |  |  |  | 13% |  |  |  |  | 4% |  |  | 7% | 1% |  |  | 1% |  |  | 70% |
| deepseek/deepseek-chat-v3-0324 |  |  |  |  |  |  |  |  |  |  |  | 8% |  |  |  |  |  |  |  | 3% | 3% |  |  | 3% |  |  | 83% |

## Reference programs (no model; they answer only what their rule can parse)

| Model | API error | degenerate loop | cut off | syntax error | CadQuery API error | geometry kernel failure | Python error in model code | no part produced | timeout | build failed | change order ignored | change not propagated to pitch | holes stacked at one point | no holes | pattern anchored at a corner | margin applied twice | X and Y swapped | pitch read as coordinates | one axis misplaced | some holes right, some wrong | holes misplaced (other) | gate: simple_through_holes | wrong plate size | off Z datum | wrong hole diameter | wrong hole count | all pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rev-a |  |  |  |  |  |  |  |  |  |  | 87% | 13% |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0% |
| parser-copy |  |  |  | 60% |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 40% |
| parser-derive |  |  |  | 40% |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 60% |
| parser-template |  |  |  | 20% |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 80% |

## What the CadQuery API errors were (first-shot answers)

| Error | Answers | Models with the most |
|---|---:|---|
| operation needs a solid on the stack | 108 | meta-llama/llama-3.3-70b-instruct (38), meta-llama/llama-4-maverick (35), mistralai/codestral-2508 (9) |
| wrong arguments to hole() | 22 | mistralai/codestral-2508 (9), microsoft/phi-4 (5), qwen2.5-coder:1.5b (4) |
| operation needs a sketch or wire | 21 | google/gemma-3-4b-it (19), meta-llama/llama-3.1-8b-instruct (1), qwen/qwen3-30b-a3b-instruct-2507 (1) |
| wrong arguments to rarray() | 18 | mistralai/mistral-small-3.2-24b-instruct (15), mistralai/codestral-2508 (2), microsoft/phi-4 (1) |
| no such method: Workplane.holes | 17 | meta-llama/llama-3.1-8b-instruct (4), meta-llama/llama-3.3-70b-instruct (4), qwen/qwen3-235b-a22b-2507 (4) |
| no such method: Workplane.centered | 16 | microsoft/phi-4 (14), meta-llama/llama-3.1-8b-instruct (2) |
| union needs a solid or shape | 14 | qwen2.5-coder:1.5b (12), google/gemma-3-4b-it (2) |
| wrong arguments to rect() | 14 | mistralai/mistral-small-3.2-24b-instruct (12), qwen/qwen3-235b-a22b-2507 (1), qwen/qwen3-coder-next (1) |
| non-integer count | 13 | mistralai/mistral-small-3.2-24b-instruct (12), mistralai/codestral-2508 (1) |
| TypeError in Solid.makeCylinder() | 11 | google/gemma-3-4b-it (8), qwen2.5-coder:1.5b (2), meta-llama/llama-3.3-70b-instruct (1) |
| ValueError in _NthSelector.filter() | 7 | meta-llama/llama-3.1-8b-instruct (4), google/gemma-3-27b-it (2), mistralai/mistral-small-3.2-24b-instruct (1) |
| ValueError in Workplane._findFromPoint() | 6 | google/gemma-3-4b-it (3), meta-llama/llama-3.3-70b-instruct (2), qwen/qwen3-30b-a3b-instruct-2507 (1) |
| no such method: Workplane.push | 6 | meta-llama/llama-3.3-70b-instruct (6) |
| wrong arguments to center() | 5 | google/gemma-3-4b-it (3), google/gemma-3-27b-it (1), meta-llama/llama-3.1-8b-instruct (1) |
| no such method: Workplane.wrapped | 5 | google/gemma-3-4b-it (5) |

## Experiment arms (not first-shot; see docs/experiments/)

These answers were produced with a changed task (a CadQuery cheat-sheet, or a retry after a build error). They are labelled for the experiment's analysis and kept out of every table above.

| Model | API error | degenerate loop | cut off | syntax error | CadQuery API error | geometry kernel failure | Python error in model code | no part produced | timeout | build failed | change order ignored | change not propagated to pitch | holes stacked at one point | no holes | pattern anchored at a corner | margin applied twice | X and Y swapped | pitch read as coordinates | one axis misplaced | some holes right, some wrong | holes misplaced (other) | gate: simple_through_holes | wrong plate size | off Z datum | wrong hole diameter | wrong hole count | all pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| google/gemma-3-27b-it [feedback] |  |  |  |  | 8% |  |  |  |  |  |  | 13% | 50% |  |  |  |  |  |  | 15% | 2% |  |  |  |  |  | 12% |
| mistralai/codestral-2508 [feedback] |  |  |  |  | 10% | 2% |  |  |  |  |  | 11% | 42% |  |  |  |  |  | 1% | 7% | 15% |  |  |  |  |  | 12% |
| meta-llama/llama-3.3-70b-instruct [feedback] |  |  |  |  | 40% |  |  |  |  |  |  | 8% | 6% | 12% |  |  | 1% |  | 3% | 2% | 8% | 4% |  | 3% |  |  | 13% |
| openai/gpt-4o-mini [hint] |  |  |  |  | 3% |  |  | 1% |  |  |  | 12% |  | 14% |  | 12% |  | 2% | 1% |  | 23% |  | 1% |  |  |  | 31% |
| openai/gpt-4o-mini [feedback] |  |  |  |  |  |  |  |  |  |  |  | 16% |  | 1% |  | 13% | 2% |  | 1% | 6% | 15% |  |  |  | 7% |  | 40% |
| mistralai/mistral-small-3.2-24b-instruct [feedback] |  | 1% |  | 1% | 18% |  |  | 1% |  |  |  | 12% | 11% | 2% |  |  |  |  | 2% |  | 5% | 1% | 1% | 4% |  |  | 43% |
| mistralai/codestral-2508 [hint] |  |  |  |  | 4% |  |  |  |  |  |  | 9% |  | 12% |  | 1% |  |  | 1% | 1% | 16% |  | 1% |  |  |  | 55% |
| meta-llama/llama-3.3-70b-instruct [hint] |  |  |  |  | 4% |  |  |  |  |  |  | 8% |  | 10% | 6% | 1% |  |  | 2% |  | 7% |  |  |  |  |  | 62% |
| google/gemma-3-27b-it [hint] |  |  |  |  |  |  |  |  |  |  |  | 13% |  | 2% |  |  |  |  | 5% | 3% | 9% |  |  |  |  |  | 68% |
| mistralai/mistral-small-3.2-24b-instruct [hint] |  |  |  |  |  |  |  |  |  |  |  | 8% |  |  |  |  | 1% |  | 4% |  | 3% |  |  |  |  |  | 83% |
