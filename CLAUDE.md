# cad-spec: instructions for Claude Code

Read this before doing anything. It is short on purpose. The details are in
`README.md`, `ROADMAP.md`, `CHANGELOG.md` and `docs/experiments/`.

## What this project is

An RL reward environment. A model writes CadQuery code for a rectangular
mounting plate with four corner holes; the code runs in a sandbox, the solid
is measured in a trusted process and scored on 9 requirements behind 5 gates.
Tiers L1 to L4 (L4 is an engineering change order). The owner, Bilal Azzouzi,
is an aerospace structures and CAD engineer building this as a portfolio
piece for RL-environment and evaluation work.

## State on 5 October 2026

- Released as `v0.5.0`. Package cad-spec 0.5.0, scorer 0.5.0 (strict
  contract, reviewed in four external rounds before merge). Scorer 0.4.0 is
  kept selectable: everything published before 4 October 2026 was scored
  under it. The Prime Hub copy is still 0.4.5.
- Training run 1 (Qwen3.5-9B LoRA) and its replication are done, registered
  and audited: +40.0 and +39.2 points on L2 + L4, under scorer 0.4.0.
- The story in one document: `docs/REPORT.md`.
- Next work is in `ROADMAP.md`, section "After the external audit of
  3 October 2026". Items 1 (scorer 0.5) and 2 (L4 parser baseline) are done.
  Item 3 is being built as L5 v1 (region-graded change orders). Governing
  design and amendments: `docs/design/`. Milestone M1 (observation map,
  `cad_spec/l5/`) is built; M2 (contract compiler) starts only after M1 is
  audited and merged. Do not reopen the architecture of the design note.

## Rules that are never broken

1. **Money.** Never run anything that can cost money without Bilal's
   explicit go in the same session, after stating a worst-case bound: no
   model API call, no `prime` command that creates, deploys, trains, pushes
   or deletes. Read-only `prime` commands are fine. Deterministic providers
   (`reference`, `rev-a`, `parser-*`) are free.
2. **Used splits.** The test split and the replication split have each been
   evaluated once. Never run a model on them, and never use them to choose a
   prompt, a threshold, a tolerance, a checkpoint or a task. Local
   deterministic code may read them. Develop on train and dev only.
3. **Registered documents and results.** Files under `docs/experiments/` and
   `results/` are records. Never rewrite them. A correction is a dated
   section appended below, with the original text kept. Any change to a
   plan, a budget or an analysis is a dated amendment written before the
   outcome it could influence.
4. **Frozen code.** Do not edit `scripts/compare_training.py`,
   `scripts/compare_replication.py`, `scripts/bridge_check.py` or
   `scripts/replication_split.py`. Recorded verdicts are historical: a new
   scorer gets a new version, the old one stays selectable in `rubric.py`,
   and a recorded verdict is never replaced.
5. **The package.** Do not change anything under
   `environments/cad_spec/cad_spec/` unless the task is explicitly a new
   release with a version bump. A scorer change starts with the defect suite
   (`scripts/validate_scorer.py`), committed before the scorer. New evaluation logic goes in `scripts/`.
6. **Git.** One branch per task, never commit on `main`, never push, merge,
   rebase or force anything. Bilal pushes and opens the pull request. Leave
   these untracked paths alone: `audit/scratch/run1-breps/`,
   `audit/scratch/run1-perturbations/`, `results/baselines.md`,
   `results/superseded/`.
7. **Text.** No em dashes anywhere: code, comments, docs, commit messages.
   Write files with LF line endings (`newline="\n"` in Python).
8. **Verification writes to a temporary folder**, never over a tracked file.

## Environment (Windows, Git Bash)

```bash
source $HOME/cadspec.sh          # venv, CadQuery check
cd ~/dev/cad-spec-env
export PYTHONIOENCODING=utf-8 PRIME_DISABLE_VERSION_CHECK=1
```

Prefix every `prime` command with `env -u SSLKEYLOGFILE`. Git checks text
files out with CRLF and stores LF. On Windows the scorer runs in `reuse`
mode; the hardened `fork` mode exists only on Linux (CI).

## Checks before every commit

```bash
ruff check scripts
(cd environments/cad_spec && ruff check . && mypy cad_spec && pytest -q)
python scripts/test_rubric.py
for t in scripts/test_*.py; do python "$t" > /dev/null || echo "FAILED $t"; done
python scripts/check_release.py
```

A new script gets a self-test `scripts/test_<name>.py` that uses synthetic
data, and a step in `.github/workflows/ci.yml`. Every user-visible change
gets a `CHANGELOG.md` entry under "Unreleased".

## Map

| Path | What |
|---|---|
| `environments/cad_spec/cad_spec/` | package: `tasks.py` (specs, prompts), `measure.py`, `rubric.py` (scorer), `environment.py` |
| `scripts/run_baseline.py` | evaluation runner and deterministic providers |
| `scripts/replay_eval.py`, `validate_scorer.py`, `test_rubric.py` | re-scoring and scorer validation |
| `docs/experiments/` | pre-registrations, amendments, results |
| `results/` | saved answers and verdicts (about 12,000 answers) |
| `audit/` | external audits; `state-and-roadmap-audit.md` lists the known weaknesses |

## Working with Bilal

- **Fast mode.** Work autonomously inside the rules above. Start each task
  with a plan of at most ten lines, then build without waiting, unless the
  prompt says to stop for a decision. Do not ask questions you can answer by
  reading the repository.
- Stop and ask only when: a rule above would be broken, money would be
  spent, a registered file would have to change, or the task's "Done when"
  list cannot be met.
- He is an expert in CAD geometry, tolerances and engineering drawings.
  Decisions about what a correct part is belong to him.
- Small commits with clear messages. When the task is finished, report in
  this order: what changed (five lines at most), the checks you ran and
  their results, anything that is not done, then the pull-request title and
  description each in its own code block, then the commands he must run to
  push.
- If a request conflicts with a rule above, stop and say so. Do not look for
  a way around the rule.
