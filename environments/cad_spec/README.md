# cad-spec (environment package)

RL reward environment: write CadQuery for a dimensioned mounting plate; the
built solid is **measured** and scored against 9 requirements behind 5
anti-cheat gates. Source, evidence and limits:
[github.com/azzbilal/cad-spec](https://github.com/azzbilal/cad-spec#readme).

## What it has shown so far

![16-model ranking](https://raw.githubusercontent.com/azzbilal/cad-spec/main/results/leaderboard/ranking.svg)

- **16 models, one greedy answer per spec, 30 held-out specs per tier.** The
  best (deepseek-chat-v3-0324) passes every requirement on 78% of answers
  [72, 85]; 11 of the 16 are below 35%. No model clearly beats a regex
  template parser (75%).
  [Full leaderboard](https://github.com/azzbilal/cad-spec/blob/main/results/leaderboard/leaderboard.md)
- **Knowledge or reasoning?** A pre-registered experiment: seven lines of
  general CadQuery facts (no spec numbers) lift mistral-small-3.2-24b from
  32% to 83% and gemma-3-27b from 12% to 68%, and remove stacked drilling
  entirely. Reasoning failures (a change order not carried into the hole
  pitch, a margin counted twice) move by less than 5 points with either the
  cheat-sheet or error feedback, in all ten model-arm pairs.
  [Pre-registration and outcome](https://github.com/azzbilal/cad-spec/blob/main/docs/experiments/hint-feedback.md)
- **The scorer is validated against itself:** 1,230 mutants of correct
  answers, 0/600 false full credit, 0/600 false rejection.
  [Validation report](https://github.com/azzbilal/cad-spec/blob/main/results/scorer-validation-0.4.0.md)

## Load

```python
from cad_spec import load_environment

env = load_environment()                                  # L0 template task, as in 0.2
env = load_environment(tier=["L2", "L4"], hints=True)     # cheat-sheet in the system prompt
env = load_environment(tier=["L1", "L2", "L3"],           # train on harder tiers,
                       eval_tier=["L0", "L1", "L2", "L3", "L4"])  # evaluate on all
```

| Argument | Default | Meaning |
|---|---|---|
| `tier` | `"L0"` | training tier(s): L0 template, L1 table, L2 derive pitch, L3 prose, L4 change order |
| `eval_tier` | same as `tier` | eval tier(s); rows carry `info["tier"]` so results split per tier |
| `metrics` | `True` | zero-weight diagnostics `built`, `gates_passed`, `m_R1_length` ... `m_R8_z_datum` |
| `hints` | `False` | append the packaged CadQuery cheat-sheet (`cad_spec/hints.md`) to the system prompt of training AND eval rows; byte-identical to the hint arm of the experiment |

200 train and 30 held-out eval specs per tier. L3 eval prompts use wording
templates that never appear in train. A further **locked test split** (60
specs, `cad_spec.tasks.make_test_split`, pinned by fingerprint) is never
loaded by the environment: it is reserved for one final comparison after
training.

Why `hints`: the experiment showed that missing API knowledge is fixed by a
prompt, not by training. With the cheat-sheet in the prompt, the reward
concentrates on what prompting cannot fix: carrying a change order through,
deriving a dimension from a stated margin.

## Reward

```
1.0    all 9 requirements met
k/9    partial compliance, gates permitting
0.05   code builds a solid but fails a gate or meets nothing
0.0    code does not build a solid, times out, or is absent
```

Scorer version: `cad_spec.rubric.SCORER_VERSION` (0.4.0). Scores from
different scorer versions are not comparable.

## Execution

Model code only hands back BREP geometry, which a trusted process measures.
Each rollout runs in a forked, rlimited, env-scrubbed child on Linux/macOS
(`CAD_SPEC_SANDBOX=fork`, about 60 ms overhead); Windows uses a persistent
worker (`reuse`) that does not isolate state between rollouts.
`CAD_SPEC_EXEC_TIMEOUT` (default 10 s) and `CAD_SPEC_MEM_MB` (default 2048)
bound each rollout. See `SECURITY.md` in the repository before running
untrusted output outside Prime's sandbox.

## Scorer-only use

`import cad_spec` does not import verifiers. With only cadquery installed:

```python
from cad_spec.rubric import score
from cad_spec.tasks import TASKS
print(score(open("answer.py").read(), TASKS[0]).summary)
```
