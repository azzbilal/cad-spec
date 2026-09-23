# Roadmap

State of the repository against the September 2026 audit
(`docs/audit-2026-09.md`, pinned at `0a823ed`). Each phase lists its exit
gate and the evidence that meets it.

| Phase | Status | Evidence |
|---|---|---|
| 0 Reproducible claims | **done** | clean-room CI job (cadquery only); `constraints.txt`; provenance in every run file |
| 1 Geometric truth | **done** | P0 regressions in harness (`shifted_stock`, `symmetric_cutter`); mutation suite 0/1,020 disagreements; 0.2.0 comparison |
| 2 Contain generated code | **done on POSIX**, Windows documented as trusted-only | `SECURITY.md`; sandbox tests; Docker CI job |
| 3 Learning value | **tooling done, runs pending** | `run_baseline.py`, `summarize_results.py`, deterministic baselines published |
| 4 Transfer | **partial** | tiers L1 to L4 incl. held-out wording; new part families not started |
| 5 Research-grade release | **partial** | changelog, data card, protocol, license; release tag waits for Phase 3 numbers |

## Next, in order

1. **Model baselines (Phase 3).** Two models, all tiers, 3 rollouts at
   temperature 0.7 plus one greedy pass. Candidates: a small Qwen coder via
   Ollama, one hosted frontier model. Publish `results/baselines.md`.
2. **One training run.** On the tiers with spread (expected L2/L3), Prime
   hosted RL, evaluate base vs adapter per `docs/EVALUATION_PROTOCOL.md`.
3. **Tag v0.3.0** once 1 and 2 are in `results/`; `prime env push`.
4. **Edit-aware L4 metric.** Zero-weight metric: fraction of the *changed*
   requirements met. Candidate L4 training reward if it beats k/8 in an
   ablation.
5. **Breakout scoring ablation.** Score partial bores by position
   (conservative) and compare reward alignment against the current rule.
6. **Windows isolation.** Recycle the reuse-mode worker after each rollout
   behind a flag and measure the cost.
7. **Held-out part families (9/10 track).** Two families with independent
   detectors (candidates: slotted plate; L-bracket with holes on two faces).
   Each requirement ships with positive, negative and reward-hack fixtures.
8. **External comparison.** Run a CADTests-style requirement set against the
   same answers and report agreement.

## Explicitly deferred
Monte Carlo tolerance study, assemblies, FEA, manufacturability checks.
