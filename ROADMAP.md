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
| 3 Learning value | **in progress** | 16-model first-shot board; pre-registered hint/feedback experiment; training prepared (0.4.1: Hub copy verified, shared prompt, locked test split), no training run yet |
| 4 Transfer | **partial** | tiers L1 to L4 incl. held-out wording; new part families not started |
| 5 Research-grade release | **partial** | changelog, data card, protocol, license; release tag waits for Phase 3 numbers |

## Next, in order

1. **Model baselines (Phase 3). Done:** 16 models (15 via OpenRouter, 1
   local), all tiers, greedy, rescored under 0.4.0; board, charts and
   failure fingerprints in `results/leaderboard/`, labels checked
   (`docs/label-check.md`: AI-assisted review of three fresh samples,
   28/30, 28/30, 27/30). Still to add: four reasoning models at
   `--max-tokens 8000`.
2. **Knowledge or reasoning? Done** (pre-registered,
   [`docs/experiments/hint-feedback.md`](docs/experiments/hint-feedback.md)).
   P1 confirmed (a CadQuery cheat-sheet removes API misuse and stacked
   drilling), P2 not confirmed (a build error and one retry do not), P3
   confirmed (reasoning failures do not move).
3. **One training run, shaped by step 2.** Training should target what
   prompting cannot fix (change orders not carried into the pitch, margins
   double-counted), so the cheat-sheet goes in the prompt for training and
   evaluation alike. Six steps, in order:
   1. **Runnable and budgeted. Done.** Prime CLI 0.6.21 (`prime train
      <config.toml>`; clear `SSLKEYLOGFILE` if it points at an unreadable
      path); wallet funded with auto top-up off, so the balance is the
      ceiling. A 50-step run at batch 128 is 6,400 training rollouts plus
      evaluations: a real run, not a smoke test.
   2. **Environment prepared and verified. Done (0.4.1).** 0.4.0 pushed to
      the Hub and its wheel verified byte-identical to the push
      (SHA-256 `c49371e9...f062691`); `scripts/verify_hub.py` re-scores saved
      answers with an installed copy and requires identical rewards and
      checks. One shared system prompt and a packaged cheat-sheet
      (`hints=True`, `--hints`), pinned to the published runs' fingerprints.
      Locked 60-spec test split. Token-priced costs so `--budget` binds on
      Prime Inference.
   3. **Screen models on development specs.** Qwen3.5-9B and Qwen3.5-35B-A3B,
      with the cheat-sheet, L1 to L4 on the 30 eval specs, thinking off
      (as the board). Choose by per-tier all-pass, reward variation within
      rollout groups (8 samples at training temperature), failure types and
      measured token cost. Record the serving route: the 9B is served under
      its training id; the 35B only under a lowercase routed id. No useful
      learning signal in either: revise the task or reward before paying for
      RL.
   4. **Register the claim** (`docs/experiments/`): base + cheat-sheet versus
      adapter + the same cheat-sheet, same decoding, scorer and serving
      stack; target tier, minimum worthwhile all-pass gain, paired analysis,
      test-split size checked against that gain, cost ceiling, regression
      checks on every other tier.
   5. **Smoke test, then one capped run.** A few steps to verify loading,
      sandboxed scoring, reward diversity, monitoring and adapter evaluation;
      the longer run's length follows from those observations and the cost
      ceiling. Intermediate validation on development specs only.
   6. **Evaluate once on the locked test split.** Paired per-tier all-pass
      changes with intervals, mean reward, build and gate rates, reasoning
      failure rates, total spend. A gain supports a claim about this plate
      family, not about CAD in general.
4. **Tag v0.4.x** once step 3 is in `results/`; push the tagged version to
   the Hub. Then move the package to the verifiers v1 taskset/harness API
   (the v0 API is being retired on the Hub; training accepts the current
   `load_environment` shape meanwhile).
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
