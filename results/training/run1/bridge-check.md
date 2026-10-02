# Serving-route bridge check (training run 1)

Frozen rule: `scripts/bridge_check.py`, step 1, seed 20261002, 10,000 draws. Reference: `results/training/screening/qwen3.5-9b-t0.7-x8-2k.jsonl` (base route, temperature 0.7, 8 samples per spec, 2,048 tokens, thinking off, cheat-sheet).

**Verdict: BRIDGED** (L4 of the training run). Corroboration agrees: yes.

| Run | Environment | Prompts | Answers | Training stack, step 1 | Base route | 95% interval | Position |
|---|---|---|---|---|---|---|---|
| `mk9qcuq2dsckzrf68gycyqls` (primary) | cad-spec-L4 | 11 | 88 | 28.4% | 42.9% | [18.2%, 69.3%] | BRIDGED |
| `mk9qcuq2dsckzrf68gycyqls` (primary) | cad-spec-L2 | 11 | 88 | 59.1% | 68.8% | [60.2%, 76.1%] | STACKS_DIFFER_NOT_INFLATING |
| `mk9qcuq2dsckzrf68gycyqls` (primary) | cad-spec-L1-L3 | 2 | 16 | 75.0% | 63.1% | [43.8%, 81.2%] | BRIDGED |
| `k3rwpbbk5sio4936onuai7ok` (second sample) | cad-spec-L4 | 12 | 96 | 32.3% | 42.9% | [18.8%, 67.7%] | BRIDGED |
| `k3rwpbbk5sio4936onuai7ok` (second sample) | cad-spec-L2 | 11 | 88 | 59.1% | 68.8% | [60.2%, 76.1%] | STACKS_DIFFER_NOT_INFLATING |
| `k3rwpbbk5sio4936onuai7ok` (second sample) | cad-spec-L1-L3 | 2 | 16 | 62.5% | 63.1% | [43.8%, 81.2%] | BRIDGED |
| both runs pooled | cad-spec-L4 | 23 | 184 | 30.4% | 42.9% | [25.5%, 61.4%] | BRIDGED |

Counts: every observed rate is a whole number of passing answers.
