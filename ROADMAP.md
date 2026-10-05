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
| 3 Learning value | **shown on this task, with caveats** | 16-model first-shot board; pre-registered hint/feedback experiment; one pre-registered LoRA run (+40.0 points on L2 + L4) and its pre-registered replication (+39.2); one adapter, serving routes not attested |
| 4 Transfer | **partial** | tiers L1 to L4 incl. held-out wording; new part families not started |
| 5 Research-grade release | **released: v0.5.0** (5 October 2026) | changelog, data card, protocol, license, one-document report (`docs/REPORT.md`); scorer 0.5.0 reviewed externally before merge |

## After the external audit of 3 October 2026

`audit/state-and-roadmap-audit.md` reproduced the training and replication
numbers and found the weak points below. Accepted order of work, free items
first. Both evaluation splits are used and are never a selection set.

1. **Scorer 0.5, a stated contract (free). Done** (4 October 2026, scorer
   0.5.0: suite frozen first, 0 false full credit on 1,646 wrong parts, 0
   false rejection on 720 correct parts; 0.4.0 kept selectable; recorded
   verdicts untouched). The original item: Decide what the part family
   allows (no extra cuts, fillets or pockets unless requested), then reject
   what 0.4.0 accepts: extra edge cuts, slots, cross-bores, clipped corners,
   wall obstructions in a bore. Tolerances below the grid step (hole centres
   sit on a 0.25 mm grid, so 0.1 mm is the starting proposal), comparisons
   on unrounded measurements. A defect suite is frozen before the
   implementation; 0.4.0 and every recorded verdict stay as they are.
2. **A built-in edit-capable L4 parser baseline (free). Done** (4 October
   2026): `parser-edit` in `scripts/run_baseline.py`, self-test
   `scripts/test_parser_edit.py`. Frozen on train and dev, then run once:
   L4 all-pass train 200/200, dev 30/30, test 60/60, replication 60/60
   (`results/baselines-deterministic.md`).
3. **A harder tier on fresh specs (free to build).** Three or four coupled
   edits, several forms of rev A code, two-stage change orders; references
   and an "unedited rev A fails" check for every task; sealed evaluation set.
4. **A true route control (paid, small, only if it can be bounded).** Base
   weights, a verified zero-delta adapter and the trained adapter on one
   serving stack. The 5-step smoke adapter is not a null control.
5. **Transfer set written by hand (paid, small).** New prose, new source
   forms, inside the validated scorer's domain.
6. **A second training experiment** only after 1 to 5, with a hard
   cumulative cap, no refill of solved groups, and a platform chosen after
   Prime's shared LoRA training closes to new runs (5 October 2026).

## Next, in order (state before the audit)

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
      **Done for Qwen3.5-9B (0.4.2).** Greedy: 68% all-pass (L4 43%, L2 63%).
      At temperature 1.0 and 1,024 tokens, L1 to L3 fell to about 40% and
      10% of answers were cut off; at **temperature 0.7 and 2,048 tokens**
      (settable in Hosted Training) truncation fell to 1% and L1 to L3 gave
      signal in 97 to 100% of groups. L4 fails one way (change order not
      propagated to the pitch: R5 and R7 together) and gave signal in 33% of
      groups, 7x weaker than the other tiers under partial credit. Decisions:
      **binary training reward** (`load_environment(reward="binary")`, L4
      signal 2.1x stronger, training reward = the claimed metric) and a mix
      weighted toward L4 and L2. The 35B-A3B was not screened: it is served
      only under a routed third-party id, against the same-serving-stack
      rule, and the 9B already sits inside the useful range.
   4. **Register the claim** (`docs/experiments/`): base + cheat-sheet versus
      adapter + the same cheat-sheet, same decoding, scorer and serving
      stack; target tier, minimum worthwhile all-pass gain, paired analysis,
      test-split size checked against that gain, cost ceiling, regression
      checks on every other tier.
      **Registered (29 Sep 2026):**
      [docs/experiments/training-run-1.md](docs/experiments/training-run-1.md).
      Claim: greedy all-pass on L2 + L4, paired, confirmed if the 95%
      interval is above 0, worthwhile at +10 points (84% power on 60 test
      specs). Configs in `configs/rl/` validated against the Prime CLI 0.8.0
      schema; analysis `scripts/compare_training.py` frozen and tested
      before any data. Ceiling $15; run length from the smoke test's
      measured cost per step.
   5. **Smoke test, then one capped run.** A few steps to verify loading,
      sandboxed scoring, reward diversity, monitoring and adapter evaluation;
      the longer run's length follows from those observations and the cost
      ceiling. Intermediate validation on development specs only.
      **Smoke test passed (30 Sep 2026)** on cad-spec 0.4.5 after three
      platform fixes (Amendments 1 to 3: dependency pin, task field, GL
      libraries); run length 104 steps by the registered rule (Amendment 4).
   6. **Evaluate once on the locked test split.** Paired per-tier all-pass
      changes with intervals, mean reward, build and gate rates, reasoning
      failure rates, total spend. A gain supports a claim about this plate
      family, not about CAD in general.
      **Done (2 October 2026):** H1 confirmed, L2 + L4 60% to 100%, +40
      points [+32.5, +47.5], no regression; integrity audit passed with
      caveats (serving routes not attested, one run, ceiling). Linux fork
      replay of the saved answers: 0 mismatches. Next: a pre-registered
      replication on a new disjoint test split with the frozen adapter,
      then other part families.
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
