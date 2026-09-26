# Hint and feedback arms: results

Pre-registered in [docs/experiments/hint-feedback.md](../../docs/experiments/hint-feedback.md). Shares over each model's 120 answers on L1 to L4; changes are paired by spec against first-shot, with 95% intervals from resampling specs.

## google/gemma-3-27b-it

| Arm | n | all pass | API error | stacked | margin twice | not propagated |
|---|---:|---:|---:|---:|---:|---:|
| first-shot | 120 | 12% | 11% | 45% | 1% | 13% |
| hint | 120 | 68% (+56% [+50%, +62%]) | 0% (-11% [-17%, -5%]) | 0% (-45% [-51%, -40%]) | 0% (-1% [-2%, +0%]) | 13% (+0% [+0%, +0%]) |
| feedback | 120 | 12% (+0% [+0%, +0%]) | 8% (-3% [-10%, +4%]) | 50% (+5% [-1%, +11%]) | 0% (-1% [-2%, +0%]) | 13% (+0% [+0%, +0%]) |

## meta-llama/llama-3.3-70b-instruct

| Arm | n | all pass | API error | stacked | margin twice | not propagated |
|---|---:|---:|---:|---:|---:|---:|
| first-shot | 120 | 16% | 47% | 8% | 0% | 8% |
| hint | 120 | 62% (+47% [+40%, +53%]) | 4% (-42% [-51%, -34%]) | 0% (-8% [-14%, -3%]) | 1% (+1% [+0%, +2%]) | 8% (+0% [-2%, +2%]) |
| feedback | 120 | 13% (-2% [-5%, +0%]) | 40% (-7% [-18%, +3%]) | 6% (-2% [-8%, +3%]) | 0% (+0% [+0%, +0%]) | 8% (+1% [+0%, +2%]) |

## mistralai/codestral-2508

| Arm | n | all pass | API error | stacked | margin twice | not propagated |
|---|---:|---:|---:|---:|---:|---:|
| first-shot | 120 | 13% | 18% | 42% | 0% | 10% |
| hint | 120 | 55% (+42% [+35%, +48%]) | 4% (-13% [-21%, -6%]) | 0% (-42% [-48%, -36%]) | 1% (+1% [+0%, +2%]) | 9% (-1% [-3%, +2%]) |
| feedback | 120 | 12% (-1% [-2%, +0%]) | 10% (-8% [-12%, -3%]) | 42% (+1% [-5%, +7%]) | 0% (+0% [+0%, +0%]) | 11% (+1% [+0%, +2%]) |

## mistralai/mistral-small-3.2-24b-instruct

| Arm | n | all pass | API error | stacked | margin twice | not propagated |
|---|---:|---:|---:|---:|---:|---:|
| first-shot | 120 | 32% | 36% | 10% | 0% | 10% |
| hint | 120 | 83% (+51% [+42%, +59%]) | 0% (-36% [-42%, -29%]) | 0% (-10% [-14%, -6%]) | 0% (+0% [+0%, +0%]) | 8% (-2% [-5%, +2%]) |
| feedback | 120 | 43% (+11% [+2%, +19%]) | 18% (-18% [-26%, -10%]) | 11% (+1% [-3%, +5%]) | 0% (+0% [+0%, +0%]) | 12% (+2% [+0%, +4%]) |

## openai/gpt-4o-mini

| Arm | n | all pass | API error | stacked | margin twice | not propagated |
|---|---:|---:|---:|---:|---:|---:|
| first-shot | 120 | 40% | 0% | 0% | 16% | 15% |
| hint | 120 | 31% (-9% [-18%, +0%]) | 3% (+3% [+1%, +7%]) | 0% (+0% [+0%, +0%]) | 12% (-3% [-8%, +1%]) | 12% (-3% [-7%, -1%]) |
| feedback | 120 | 40% (+0% [-8%, +8%]) | 0% (+0% [+0%, +0%]) | 0% (+0% [+0%, +0%]) | 13% (-2% [-7%, +2%]) | 16% (+1% [-2%, +4%]) |

## Arms excluded from the verdicts

| Model | Arm | Why |
|---|---|---|
| meta-llama/llama-3.1-8b-instruct | first-shot | L1: max_tokens=2048, registered 1024; L2: max_tokens=2048, registered 1024; L3: max_tokens=2048, registered 1024 |
| rev-a | first-shot | tiers present: ['L4'] |

## Pre-registered predictions

| Prediction | Result |
|---|---|
| P1 | confirmed |
| P2 | not confirmed |
| P3 | confirmed |

| Prediction | Model | Verdict | Evidence |
|---|---|---|---|
| P1 | google/gemma-3-27b-it | held | knowledge failures 56% -> 0% |
| P2 | google/gemma-3-27b-it | failed | API errors 11% -> 8%; stacked 45% -> 50% |
| P1 | mistralai/codestral-2508 | held | knowledge failures 59% -> 4% |
| P2 | mistralai/codestral-2508 | failed | API errors 18% -> 10%; stacked 42% -> 42% |
| P1 | meta-llama/llama-3.3-70b-instruct | held | knowledge failures 55% -> 4% |
| P2 | meta-llama/llama-3.3-70b-instruct | failed | API errors 47% -> 40%; stacked 8% -> 6% |
| P1 | mistralai/mistral-small-3.2-24b-instruct | held | knowledge failures 46% -> 0% |
| P2 | mistralai/mistral-small-3.2-24b-instruct | held | API errors 36% -> 18%; stacked 10% -> 11% |
| P3 | google/gemma-3-27b-it [hint] | held | margin applied twice -1%; change not propagated to pitch +0% |
| P3 | google/gemma-3-27b-it [feedback] | held | margin applied twice -1%; change not propagated to pitch +0% |
| P3 | mistralai/codestral-2508 [hint] | held | margin applied twice +1%; change not propagated to pitch -1% |
| P3 | mistralai/codestral-2508 [feedback] | held | margin applied twice +0%; change not propagated to pitch +1% |
| P3 | meta-llama/llama-3.3-70b-instruct [hint] | held | margin applied twice +1%; change not propagated to pitch +0% |
| P3 | meta-llama/llama-3.3-70b-instruct [feedback] | held | margin applied twice +0%; change not propagated to pitch +1% |
| P3 | mistralai/mistral-small-3.2-24b-instruct [hint] | held | margin applied twice +0%; change not propagated to pitch -2% |
| P3 | mistralai/mistral-small-3.2-24b-instruct [feedback] | held | margin applied twice +0%; change not propagated to pitch +2% |
| P3 | openai/gpt-4o-mini [hint] | held | margin applied twice -3%; change not propagated to pitch -3% |
| P3 | openai/gpt-4o-mini [feedback] | held | margin applied twice -2%; change not propagated to pitch +1% |
