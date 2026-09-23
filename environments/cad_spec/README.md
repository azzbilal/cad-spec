# cad-spec (environment package)

RL reward environment: write CadQuery for a dimensioned mounting plate; the
built solid is measured and scored against 8 requirements behind 4
anti-cheat gates. Full documentation, evidence and limits are in the
[repository README](https://github.com/azzbilal/cad-spec#readme).

## Load

```python
from cad_spec import load_environment

env = load_environment()                                  # L0 template task, as in 0.2
env = load_environment(tier=["L1", "L2", "L3"],           # train on harder tiers
                       eval_tier=["L0", "L1", "L2", "L3", "L4"])
```

| Argument | Default | Meaning |
|---|---|---|
| `tier` | `"L0"` | training tier(s): L0 template, L1 table, L2 derive pitch, L3 prose, L4 change order |
| `eval_tier` | same as `tier` | eval tier(s); rows carry `info["tier"]` so results split per tier |
| `metrics` | `True` | zero-weight diagnostics `built`, `gates_passed`, `m_R1_length` ... `m_R7_edge_margin` |

200 train and 30 held-out specs per tier. L3 eval prompts use wording
templates that never appear in train.

## Reward

```
1.0    all 8 requirements met
k/8    partial compliance, gates permitting
0.05   code builds but fails a gate or meets nothing
0.0    code does not build, times out, or is absent
```

Scorer version: `cad_spec.rubric.SCORER_VERSION` (0.3.0). Scores from
different scorer versions are not comparable.

## Execution

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
