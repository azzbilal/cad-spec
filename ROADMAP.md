# cad-spec Elite Build Roadmap

Goal: take cad-spec-env from **7.5/10** (audit baseline) to **9.5/10** production-grade RL
environment as **v0.2.0**. Full execution blueprint:
[.opencode/plans/cad-spec-elite-v0.2.0.md](.opencode/plans/cad-spec-elite-v0.2.0.md).

## Current State

- Audit complete; all technical risks de-risked against the installed venv
  (OCP exact-cylinder classification validated: bores vs fillets vs counterbores).
- Execution-ready plan drafted — no further research needed.
- Nothing implemented yet.

## Phase 0 — Unlock *(prerequisite)*
- [x] Exit plan mode / approve edit permissions for this workspace

## Phase 1 — Reward Integrity Core *(→ ~8.5)* — **DONE 2026-08-22**
- [x] Rewrite `measure.py`: exact-cylinder hole detection + concavity probe + coaxial grouping
- [x] Worker-process isolation with `CAD_SPEC_EXEC_TIMEOUT` (default 10s), `CAD_SPEC_INPROC=1` escape hatch
- [x] `rubric.py`: strict gates kept; rename through-gate to `simple_through_holes`;
      widen `is_plate` identity band to 12%; add requirement R6 material ±3% → k/7 scale
      *(refinement: R6 compares against measured-envelope minus nominal bores, so R1–R3 own dimensions)*
- [x] `environment.py`: single execution per rollout via `Report.parsed`

**Gate:** ✅ 19/19 green; timeout kill 3.0s; respawn+rebuild ok; side-effects contained in worker tempdir

## Phase 2 — Scaffolding *(→ ~9.0)*
- [ ] Parametric sampler in `tasks.py`: seeded RNG, 200 train / 30 stratified eval specs
- [ ] Wire datasets in `environment.py` (`make_splits()`, delete `EVAL_SPEC_IDS`)
- [ ] pytest suite: canonical-harness wrapper, measure units incl. timeout test,
      env tests, reference-solution auto-verification across seeds
- [ ] pyproject: version 0.2.0, dev extras, ruff + mypy config
- [ ] GitHub Actions CI: ubuntu+windows × py3.11/3.12

**Gate:** `pytest -q`, `ruff check .`, `mypy cad_spec` all green locally

## Phase 3 — Docs Reconciliation *(→ ~9.25)*
- [ ] Root README: k/7 reward table; honest 0.05-floor footnote for gated-but-runnable code;
      updated gate table
- [ ] Env README: parametric dataset description; baseline-refresh marker
- [ ] `eval_local.py`: fix stale "verifiers 0.1.14" docstring → 0.3.x reality

## Phase 4 — Ship *(→ 9.5)*
- [ ] Commit + push → CI green on GitHub
- [ ] `prime env push` v0.2.0 *(scheduled later, per owner)*
- [ ] Baseline rerun (qwen local) pre/post-diff → update README numbers

## Explicitly Deferred
6/8-hole variants · multi-part families · Monte Carlo tolerance study

## Audit Issues This Closes
| # | Issue | Fixed by |
|---|---|---|
| 1 | Fillet false-positive in hole detection | Phase 1 |
| 2 | Gate zeroes all-PASS parts with benign extras | Phase 1 |
| 3 | Unsandboxed model exec | Phase 1 |
| 4 | Double execution cost | Phase 1 |
| 5 | No exec timeout | Phase 1 |
| 6 | Doc drift | Phase 3 |
| 7 | No CI / lint / typecheck / pytest | Phase 2 |
