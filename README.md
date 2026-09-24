# cad-spec

[![ci](https://github.com/azzbilal/cad-spec/actions/workflows/ci.yml/badge.svg)](https://github.com/azzbilal/cad-spec/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**An open, inspection-style RL reward environment for dimensioned parametric parts.**

A model reads a mechanical specification and writes CadQuery. The code is
executed in a sandbox, the resulting solid is measured from its exact
boundary representation, and each written requirement is checked against the
measurement the way an inspection report checks a machined part. The reward
is the fraction of requirements met, behind gates that zero known cheats.

What this is, and what it is not:

| Claim | Status |
|---|---|
| Scores a CadQuery part against 9 measurable requirements with partial credit | yes, one part family (4-hole mounting plate) |
| Measures the real geometry, not what the model's objects claim | yes since 0.4.0: model code hands over BREP geometry; a trusted process measures it ([SECURITY.md](SECURITY.md)) |
| Scorer validated against labelled mutants | yes: 1,230 mutants, 0 false full credit on 600 wrong parts, 0 false rejection on 600 correct parts ([results](results/scorer-validation-0.4.0.md)) |
| Separates "copying numbers" from "reading a spec" | partly: five prompt tiers, reported separately; L0 to L2 are solved by simple parsers, and L3 by a parser that knows its wording templates ([baselines](results/baselines-deterministic.md)) |
| Runs untrusted model code safely | per-rollout sandbox on POSIX, container for untrusted scale ([SECURITY.md](SECURITY.md)) |
| Shows that RL training improves a model | **not yet**: tooling is ready, no training run is published |
| Broad text-to-CAD benchmark, new part families | **no**: one family; see [ROADMAP.md](ROADMAP.md) |
| "Material" means alloy, strength, fit, manufacturability | **no**: R6 is volume consistency only |

## Quick start

**Scorer only** (needs nothing but CadQuery, from a plain checkout):

```bash
git clone https://github.com/azzbilal/cad-spec && cd cad-spec
pip install "cadquery==2.8.0"
python scripts/test_rubric.py              # 37 hand-labelled cases
```

**Full environment** (Verifiers, tests, validation):

```bash
cd environments/cad_spec
pip install -c constraints.txt -e ".[dev]"
pytest -q                                  # unit, sandbox, tier and harness tests
cd ../..
python scripts/validate_scorer.py          # mutation validation, ~90 s
```

On Windows use `py` instead of `python` outside a virtual environment.

**Score one answer from the command line:**

```bash
cad-spec prompt gen-0001 --tier L3 --split eval   # print a task
cad-spec score  gen-0001 answer.py                # PASS/FAIL per requirement
cad-spec sandbox                                  # what isolation applies here
```

## The task

Part family: a rectangular plate with a 4-hole bolt pattern, parameterised over
length, width, thickness, hole diameter and edge margin. A seeded sampler
(`tasks.py`, `SAMPLE_SEED = 20260813`) produces 200 train and 30 held-out
specs; the held-out set takes the 10 smallest plates, the 10 largest and 10
mid-range. That separates **parameters**, not part types.

The same specs are posed at five **tiers**. Geometry and scorer are identical
across tiers, so any score difference comes from how the requirement was
stated. Never average tiers together.

| Tier | Prompt | What it tests | Regex copier | Copier + one rule | Template-aware parser |
|---|---|---|---:|---:|---:|
| L0 | template with `???` slots | numeric copying | 100% | 100% | 100% |
| L1 | requirement table, no template | writing the CadQuery yourself | 100% | 100% | 100% |
| L2 | table without the hole pitch | deriving pitch = size - 2 x margin | 0% | 100% | 100% |
| L3 | prose; eval uses wordings never seen in train | robustness to unseen phrasing | 0% | 0% | **100%** |
| L4 | rev A model + engineering change order | a controlled edit | 0% | 0% | 0% |

The three right-hand columns are all-requirements pass rates of deterministic
programs with no model at all ([results](results/baselines-deterministic.md)).
L0 is kept only as a warm-up: a regex solves it.

**L3 caveat.** L3 has four train and two eval wording templates, and each
template states the numbers in a fixed order. A model that saw only the train
wordings cannot know the eval ones, so L3 does measure robustness to unseen
phrasing; but a parser given all six templates reads every eval prompt by
position and scores 100%. L3 is template-structured text, not free prose. A
larger, shuffled wording space is on the roadmap.

**L4 caveat.** Returning rev A unchanged earns a mean reward of 0.774 with 0%
full passes, because most requirements did not change. Partial credit is a
training signal; for L4 the headline metric is the all-requirements pass rate.
Every change order moves at least one value clearly outside its tolerance, so
an unedited model can never pass (checked on all 230 specs).

## Scoring

**Gates** zero the reward. Each exists because of a specific cheat, and each
cheat is a case in `scripts/test_rubric.py`:

| Gate | Cheat it kills |
|---|---|
| `single_solid` | loose pieces that share the bounding box (every shape on the Workplane stack is measured) |
| `clean_solid` | an enclosed cavity (a second shell), loose faces or edges beside the part, or an invalid B-rep: changes that keep the volume in band |
| `simple_through_holes` | blind dimples, counterbores, joggled two-sided holes, and membranes: each bore must be one diameter from the stock's bottom face to its top face, and a rod along its axis must meet no material |
| `hole_count_sane` | swiss-cheesing the plate to hit a volume target |
| `is_plate` | a shell or ellipse with the right bounding box (volume vs volume predicted from the measured geometry, 12% band) |

**Requirements** give partial credit, reward = k/9:

| Check | Tolerance | Referenced to |
|---|---|---|
| R1-R3 length, width, thickness | 0.5 mm | envelope size |
| R4a hole count | exact | closed bores |
| R4b hole diameter | 0.2 mm | each bore |
| R5 hole pattern | 0.5 mm | the **origin** (the prompt fixes the part centred on it) |
| R6 material | 3% | measured envelope minus nominal bores (volume only) |
| R7 edge margin | 0.5 mm | the part's own **edges** |
| R8 Z datum | 0.5 mm | plate mid-plane to **Z = 0** |

Tolerances are inclusive: 6.7 mm is inside 6.5 +/- 0.2 (comparisons carry a
1e-6 mm numerical slack; 0.3.x failed it on floating-point rounding).

Datums on purpose: a plate slid under its holes fails R7 only, a part moved
in X or Y fails R5 only, a part moved in Z fails R8 only. Before 0.3.0 only
sizes were checked, which are translation-invariant; before 0.4.0 Z was not
checked at all. Rotations are not normalised: the prompt fixes the axes.

Prompt numbering (R1-R6 in the task text) is the drawing's; check names are
the scorer's. The prompt's "R6 edge margin" is scored as `R7:edge_margin`;
`R6:material` has no line in the prompt because it is a consistency check.

At the environment level, code that builds a solid but satisfies nothing, or
fails a gate, earns a 0.05 floor so a weak model has a first rung. Code that
does not build a solid (including a bare 2D sketch) earns 0.

### How holes are found

Every Z-parallel cylindrical face is grouped by axis position and diameter.
Two independent tests decide whether a group is a drilled bore: a membership
probe just inside the surface rejects convex cylinders (rounds, bosses, shell
walls), and an area check rejects groups that do not close into a full
cylinder over the **union** of their faces' Z spans (corner fillets). Depth is
that union, so a bore split into stacked faces by a symmetric cutter is one
bore.

**Known limitation:** a hole that breaks out through a side wall does not
close, so it is reported in `Measurements.partial_bores` but not counted. The
part then loses count and pattern, where an inspector would say "4 holes, one
misplaced". Pinned as `LIMIT_hole_breakout`.

**Known limitation:** bores are recognised only as analytic cylinders. The
same correct part converted to NURBS surfaces (`toNURBS()`) scores 0. Models
do not produce this unprompted. Pinned as `LIMIT_nurbs_surfaces`.

## Evidence

| File | What it shows |
|---|---|
| [`results/scorer-validation-0.4.0.md`](results/scorer-validation-0.4.0.md) | 1,230 one-change mutants over the 30 held-out specs (600 wrong parts, 600 correct, 30 documented-limitation cases excluded); ground truth from geometry parameters; 0 false full credit, 0 false rejection, 100% per-check agreement |
| [`results/scorer-validation-0.3.0-under-suite-0.4.0.md`](results/scorer-validation-0.3.0-under-suite-0.4.0.md) | the 0.4.0 suite on the previous scorer: 15.0% false full credit (Z shift, membranes, cavities), 4.7% false rejection (exact-limit diameters). Shows the suite detects the defects the second audit found |
| [`results/scorer-validation-0.2.0.md`](results/scorer-validation-0.2.0.md) | the original suite on 0.2.0: 5.9% false full credit, 12.5% false rejection |
| [`results/baselines-deterministic.md`](results/baselines-deterministic.md) | reference, regex copier, copier + derivation, template-aware parser, and "ignore the change order" baselines per tier |
| [`docs/audit-2026-09.md`](docs/audit-2026-09.md), [`docs/audit-2026-09-reference.md`](docs/audit-2026-09-reference.md) | the two external audits this release responds to |
| `results/runs/*.jsonl` | every rollout behind those tables, with scorer version, git revision and sandbox mode |

No model baseline or training result is published for 0.3.0 yet. The last
model numbers were measured on the 0.2 scorer and are not comparable.

## Running a model

```bash
# any OpenAI-compatible server (Ollama shown)
python scripts/run_baseline.py --provider openai --base-url http://localhost:11434/v1 \
    --model qwen2.5-coder:7b --tiers L0 L1 L2 L3 L4 --rollouts 3 --temperature 0.7
python scripts/summarize_results.py results/runs/*.jsonl --markdown results/baselines.md
```

Hosted models through OpenRouter (one key, hundreds of models), with the
cost of a full run estimated first and a spending threshold (the run stops
before a call that would likely cross it; one call can still overshoot):

```bash
python scripts/openrouter_models.py --max-cost 0.50         # live catalogue + run estimates
export OPENROUTER_API_KEY=sk-or-...
python scripts/run_baseline.py --provider openai --base-url https://openrouter.ai/api/v1 \
    --key-env OPENROUTER_API_KEY --model <model-id> --tiers L0 L1 L2 L3 L4 --budget 0.50
```

Every scoring script checks that CadQuery is importable before doing
anything, and stops with instructions if it is not (typically: the virtual
environment is not active in this terminal). A scorer that cannot run never
records a score.

Reasoning models need `--max-tokens 8000` or more; otherwise they spend the
budget thinking and return nothing. The summary flags any run where that
happened.

The summary reports, per tier: mean reward and all-requirements pass rate with
95% bootstrap intervals over specs, build rate, gate hits, timeouts and the
pass rate of every check. The protocol for a training claim is in
[docs/EVALUATION_PROTOCOL.md](docs/EVALUATION_PROTOCOL.md).

With Prime Intellect:

```python
from cad_spec import load_environment
env = load_environment(tier=["L1", "L2", "L3"], eval_tier=["L0", "L1", "L2", "L3", "L4"])
```

Zero-weight metrics (`built`, `gates_passed`, `m_R1_length` ... `m_R8_z_datum`)
give per-check learning curves; all functions of one rollout share that
rollout's single build through its `state`, and no build is shared between
rollouts.

**Leaderboard and failure fingerprints.** After a board of runs:

```bash
python scripts/failure_modes.py results/rescored/0.4.0/*.jsonl
python scripts/leaderboard.py results/rescored/0.4.0/*.jsonl --failures results/failure-modes-0.4.0.json
```

`results/leaderboard/` then holds a ranked table and three SVG charts. The
failure classifier labels each failed answer from its re-measured geometry
and code (for example "holes stacked at one point": positions computed but
never bound to `.hole()`), so the board shows how each model fails, not only
how often.

**Scorer changes never cost a rerun.** Every run file stores each model's
answer, so `python scripts/rescore.py results/runs/*.jsonl` replays them
through the current scorer into `results/rescored/<version>/`, at no cost.

## Layout

```
environments/cad_spec/cad_spec/
  measure.py      build in a sandbox, measure the B-rep (no spec knowledge)
  rubric.py       gates + requirements -> Report (SCORER_VERSION lives here)
  tasks.py        sampler, splits, the five prompt tiers
  environment.py  the only file that imports verifiers
  __main__.py     the cad-spec CLI
scripts/
  test_rubric.py      37 hand-labelled cases, needs only cadquery
  validate_scorer.py  mutation suite -> results/scorer-validation-*.md
  rescore.py          replay saved answers through the current scorer
  failure_modes.py    label every failed answer (geometry + code)
  leaderboard.py      ranked table + SVG charts
  openrouter_models.py  live model catalogue with run cost estimates
  run_baseline.py     any provider, any tier, JSONL with provenance
  summarize_results.py
docs/                 evaluation protocol, data card
SECURITY.md           threat model and sandbox modes
```

## Related work

Executable CAD tests are not new: CADTests checks B-rep requirements, and
Text2CAD-Bench, MUSE, BenchCAD and CADEngBench evaluate text-to-CAD more
broadly. CAD-Coder and CAD-RL train on CAD-specific feedback. cad-spec's
narrower contribution is a small, mutation-audited, requirement-level reward
built for RL, with tiers that separate copying from interpretation. See the
September 2026 audit in `docs/` for references.

## License

MIT, see [LICENSE](LICENSE).
