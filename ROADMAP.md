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
| 3 Learning value | **in progress** | 16-model first-shot board published; failure labels checked by AI-assisted review of three samples; no training run yet |
| 4 Transfer | **partial** | tiers L1 to L4 incl. held-out wording; new part families not started |
| 5 Research-grade release | **partial** | changelog, data card, protocol, license; release tag waits for Phase 3 numbers |

## Next, in order

1. **Model baselines (Phase 3). Done:** 16 models (15 via OpenRouter, 1
   local), all tiers, greedy, rescored under 0.4.0; board, charts and
   failure fingerprints in `results/leaderboard/`, labels checked
   (`docs/label-check.md`: AI-assisted review of three fresh samples,
   28/30, 28/30, 27/30). Still to add: four reasoning models at
   `--max-tokens 8000`.
2. **Knowledge or reasoning? Hint and feedback arms. Pre-registered:**
   [`docs/experiments/hint-feedback.md`](docs/experiments/hint-feedback.md)
   (five models, a CadQuery cheat-sheet arm and a one-retry feedback arm,
   predictions P1 to P3 with thresholds, analysis script committed with it).
   Runs to do; reported separately, never on the first-shot board.
3. **One training run.** On the tiers with spread (expected L2/L3), Prime
   hosted RL, evaluate base vs adapter per `docs/EVALUATION_PROTOCOL.md`.
4. **Tag v0.4.0** once 1 and 3 are in `results/`; `prime env push`.
5. **Edit-aware L4 metric.** Zero-weight metric: fraction of the *changed*
   requirements met. Candidate L4 training reward if it beats k/9 in an
   ablation.
6. **L3 wording space.** Many more templates with shuffled number order and
   mixed units, so a template-aware parser no longer solves L3.
7. **Breakout scoring ablation.** Score partial bores by position
   (conservative) and compare reward alignment against the current rule.
8. **Aim points for off-plate holes.** Record where each `.hole()` call
   aims during the failure-analysis rebuild, so a pattern whose holes mostly
   miss the plate can still be classified (known limitation in
   `docs/label-check.md`).
9. **Windows isolation.** Recycle the reuse-mode worker after each rollout
   behind a flag and measure the cost.
10. **Held-out part families (9/10 track).** Two families with independent
   detectors (candidates: slotted plate; L-bracket with holes on two faces).
   Each requirement ships with positive, negative and reward-hack fixtures.
11. **External comparison.** Run a CADTests-style requirement set against the
   same answers and report agreement.

## Explicitly deferred
Monte Carlo tolerance study, assemblies, FEA, manufacturability checks.
