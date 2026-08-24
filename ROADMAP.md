# cad-spec Elite Build Roadmap

Goal: take cad-spec-env from **7.5/10** (audit baseline) to **9.5/10** production-grade RL
environment as **v0.2.0**. Full execution blueprint:
[.opencode/plans/cad-spec-elite-v0.2.0.md](.opencode/plans/cad-spec-elite-v0.2.0.md).

## Current State

- Phases 0–2 implemented and committed; Phase 3 docs reconciliation done.
- Hole detection runs TWO independent discriminators, validated against the
  installed venv; neither alone is sufficient:
  - *surface-inset membership probe* — rejects CONVEX cylinders (external
    rounds, bosses, shell outer walls) by asking whether material continues
    immediately inward of the surface. Cannot catch inner corner fillets:
    those genuinely are concave cylinders with material outside them.
  - *full-cylinder area completeness check* — rejects concave PARTIAL
    cylinders (inner corner fillets ≈ quarter arcs, ~25% coverage) by asking
    whether the coaxial group closes into a full bore. Cannot catch convex
    bosses: a boss is a complete cylinder.
- Adversarial harness (`scripts/test_rubric.py`): **20 cases**, including a
  hollow-geometry fixture pinning that shelled parts score 0.0 raw.

## Phase 0 — Unlock *(prerequisite)*
- [x] Exit plan mode / approve edit permissions for this workspace

## Phase 1 — Reward Integrity Core *(→ ~8.5)* — **DONE 2026-08-22**
- [x] Rewrite `measure.py`: exact-cylinder hole detection + concavity probe + coaxial grouping
- [x] Worker-process isolation with `CAD_SPEC_EXEC_TIMEOUT` (default 10s), `CAD_SPEC_INPROC=1` escape hatch
- [x] `rubric.py`: strict gates kept; rename through-gate to `simple_through_holes`;
      widen `is_plate` identity band to 12%; add requirement R6 material ±3% → k/7 scale
      *(refinement: R6 compares against measured-envelope minus nominal bores, so R1–R3 own dimensions)*
- [x] `environment.py`: single execution per rollout via `Report.parsed`

**Gate:** ✅ 19/19 green at the time (harness has since grown to 20 cases — see Current State); timeout kill 3.0s; respawn+rebuild ok; side-effects contained in worker tempdir

## Phase 2 — Scaffolding *(→ ~9.0)* — **DONE 2026-08-24**
- [x] Parametric sampler in `tasks.py`: seeded RNG, 200 train / 30 stratified eval specs
- [x] Wire datasets in `environment.py` (`make_splits()`, delete `EVAL_SPEC_IDS`)
- [x] pytest suite: canonical-harness wrapper, measure units incl. timeout test,
      env tests, reference-solution auto-verification across seeds
- [x] pyproject: version 0.2.0, dev extras, ruff + mypy config
- [x] GitHub Actions CI: ubuntu+windows × py3.11/3.12

**Gate:** ✅ `pytest -q` 36/36; `ruff check .` clean; `mypy cad_spec` clean.
Refinements vs blueprint: worker now announces readiness *after* warming the kernel, so
`CAD_SPEC_EXEC_TIMEOUT` measures model code only (tight budgets usable right after respawn);
sampler margin grid uses an inclusive ceil/floor half-mm range (no empty-`randrange` edge);
mypy parse target 3.12 (numpy stubs use `type` statements a 3.11 parser rejects).

## Phase 3 — Docs Reconciliation *(→ ~9.25)* — **DONE 2026-08-24**
- [x] Root README: k/7 reward table; honest 0.05-floor footnote for gated-but-runnable code;
      updated gate table
- [x] Env README: parametric dataset description; baseline-refresh marker
- [x] `eval_local.py`: fix stale "verifiers 0.1.14" docstring → 0.3.x reality

**Gate:** ✅ harness 20/20 (added `shelled_filleted_box`, the hollow-geometry detector guard);
`pytest -q` 40 passed; `ruff check .` clean; `mypy cad_spec` clean.
Beyond plan §9: two-discriminator detection structure written into both READMEs + roadmap
Current State (inset probe catches convex, cannot catch corner fillets; area completeness
catches partial cylinders, cannot catch bosses); measure.py module docstring now names the
silent-drop limitation (intersecting/breakout/pocket bores are scored as MISSED, not misplaced);
harness-count quotes updated everywhere (19→20); `.gitignore` covers `.opencode/ out.txt probe_check.py`.

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
