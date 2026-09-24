# Roadmap

State of the repository against the two September 2026 audits
(`docs/audit-2026-09.md` at `0a823ed`; `docs/audit-2026-09-reference.md` at
`221a25a`, with per-finding dispositions). Each phase lists its exit gate and
the evidence that meets it.

| Phase | Status | Evidence |
|---|---|---|
| 0 Reproducible claims | **done** | clean-room CI job (cadquery only); `constraints.txt`; provenance in every run file |
| 1 Geometric truth | **done** | audit regressions in the harness (37 cases); mutation suite 0/600 false full credit, 0/600 false rejection; the same suite finds 15% false full credit in 0.3.0 |
| 2 Contain generated code | **done on POSIX**, Windows documented as trusted-only | BREP trust boundary; `SECURITY.md` per mode; sandbox tests; Docker CI job |
| 3 Learning value | **in progress** | local and OpenRouter model baselines running; `rescore.py` replays them under 0.4.0 |
| 4 Transfer | **partial** | tiers L1 to L4 incl. held-out wording; new part families not started |
| 5 Research-grade release | **partial** | changelog, data card, protocol, license; release tag waits for Phase 3 numbers |

## Next, in order

1. **Model baselines (Phase 3).** A 19-model OpenRouter board plus local
   models, all tiers, greedy; rescored under 0.4.0; published as
   `results/baselines.md` with a leaderboard chart.
2. **One training run.** On the tiers with spread (expected L2/L3), Prime
   hosted RL, evaluate base vs adapter per `docs/EVALUATION_PROTOCOL.md`.
3. **Tag v0.4.0** once 1 and 2 are in `results/`; `prime env push`.
4. **Edit-aware L4 metric.** Zero-weight metric: fraction of the *changed*
   requirements met. Candidate L4 training reward if it beats k/9 in an
   ablation.
5. **L3 wording space.** Many more templates with shuffled number order and
   mixed units, so a template-aware parser no longer solves L3.
6. **Breakout scoring ablation.** Score partial bores by position
   (conservative) and compare reward alignment against the current rule.
7. **Windows isolation.** Recycle the reuse-mode worker after each rollout
   behind a flag and measure the cost.
8. **Held-out part families (9/10 track).** Two families with independent
   detectors (candidates: slotted plate; L-bracket with holes on two faces).
   Each requirement ships with positive, negative and reward-hack fixtures.
9. **External comparison.** Run a CADTests-style requirement set against the
   same answers and report agreement.

## Explicitly deferred
Monte Carlo tolerance study, assemblies, FEA, manufacturability checks.
