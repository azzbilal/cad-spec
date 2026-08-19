# cad-spec

An RL environment where a model reads a dimensioned engineering spec and writes
CadQuery to satisfy it. Scoring is not text similarity: the code is executed,
the resulting solid is measured, and each requirement is checked against the
measurement the way an inspection report would check a machined part.

Part family: rectangular mounting plate, four-hole bolt pattern, parameterised
over length, width, thickness, hole diameter and edge margin.

## Why the scoring is built this way

Dimensional checks alone are trivially gameable. A solid block with no holes
satisfies every overall-dimension requirement. So the rubric has two layers:

**Gates** zero the reward. Each one exists because of a specific cheat:

| Gate | Cheat it kills |
|---|---|
| `single_solid` | four loose corner tabs that share the bounding box |
| `through_holes` | blind dimples that measure like fastener holes from above |
| `hole_count_sane` | swiss-cheesing the plate to hit a volume target |
| `is_plate` | a shell, hollow box, or ellipse extrusion with the right bbox |

`is_plate` compares measured volume against volume predicted from the *measured*
geometry, not from the spec. That distinction is load-bearing: gating on the
spec means any dimensional error also zeroes the score, which destroys the
partial credit RL needs to climb. This was a real bug caught by the test
harness, not a hypothetical.

**Requirements** give partial credit: reward is the fraction of R1 to R5 met.

Resulting reward shape, all verified in `scripts/test_rubric.py`:

```
reference solution        1.000
one wrong dimension       0.833
two holes instead of four 0.667
every cheat above         0.000
unrunnable code           0.000
```

## Walkthrough

### 1. Prove the rubric before involving a model

```bash
pip install cadquery
py scripts/test_rubric.py
```

13 hand-written answers with known-correct scores. No model, no API key, no
account, no cost. If you change a tolerance or add a requirement, this file is
what tells you whether you broke the reward. Add a case every time you think of
a new way to cheat it.

### 2. Scaffold into a Prime environment

```bash
cd ~/dev/prime-lab
prime env init cad-spec
```

Copy `cad_spec/` and `pyproject.toml` into the generated folder, then reconcile
`environment.py` against the scaffold's own `load_environment` signature. That
file is the one piece here written against the verifiers API rather than plain
Python, so treat the scaffold as authoritative if they disagree.

### 3. Evaluate locally, for free

```bash
ollama pull qwen3:4b
py scripts/eval_local.py --model qwen3:4b --num-examples 5
```

Read the spread, not the mean. All-identical scores mean the rubric is not
discriminating. All zeros mean the task is out of reach for that model or the
code parser is rejecting valid answers. Both are environment bugs, and both are
free to find at this stage.

### 4. Publish

```bash
uv pip install -e .
prime env push
```

This is the portfolio artifact. It exists whether or not you ever train.

### 5. Baseline, then train

```bash
prime eval run <your-handle>/cad-spec -m Qwen/Qwen3.5-0.8B -p prime -n 20 -r 1
```

Only proceed if the baseline lands roughly between 10% and 80%. Below that
there is no signal to learn from; above it there is nothing left to teach.

```toml
# configs/rl/cad-spec.toml
model = "Qwen/Qwen3.5-0.8B"
max_steps = 50
batch_size = 128
rollouts_per_example = 8

[sampling]
max_tokens = 512

[[env]]
id = "<your-handle>/cad-spec"
```

```bash
prime train run configs/rl/cad-spec.toml
prime train logs <run-id> -f
```

Then re-run the step 5 eval against the trained adapter and diff the scores.
Baseline vs trained, with the reward curve, is the deliverable.

## Scope discipline

One part family. Five requirements. Four gates. The Monte Carlo tolerance study
and the multi-part assemblies do not belong in v1. Ship this, then extend.

## Layout

```
cad_spec/measure.py      build model code, extract geometry. knows nothing about specs
cad_spec/tasks.py        the part family, prompt template, reference solutions
cad_spec/rubric.py       gates and requirements. the file that matters
cad_spec/environment.py  verifiers wrapper. the only API-coupled file
scripts/test_rubric.py   adversarial test harness, no model required
scripts/eval_local.py    run against Ollama or any OpenAI-compatible endpoint
```
