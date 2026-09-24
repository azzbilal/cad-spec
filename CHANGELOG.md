# Changelog

Scores are only comparable within one scorer version
(`cad_spec.rubric.SCORER_VERSION`).

## Unreleased

### Leaderboard and failure analysis (no scoring change)
- `scripts/failure_modes.py`: labels every failed answer from its
  re-measured geometry and code. Modes found on the first 14-model board:
  holes stacked at one point (positions planned but never bound to
  `.hole()`: missing `.vertices()`, unused loop variable, repeated `.hole()`),
  pattern anchored at a corner, edge margin applied twice, X/Y swapped, and on
  L4 "change order ignored" / "change not propagated to the pitch".
  `scripts/test_failure_modes.py` pins one known answer per mode (CI).
- `scripts/leaderboard.py`: ranked table plus SVG charts (ranking with 95%
  paired bootstrap intervals and parser reference lines, model x tier
  heatmap, failure fingerprints). No plotting dependency.
- Runner retries rate limits (429) and 5xx with exponential backoff,
  honouring Retry-After.
- Truncated answers are split: cut off by the budget (a configuration
  problem, counts toward "not publishable") vs degenerate loops (the model
  repeating itself; a model failure). `scripts/degenerate.py` decides from
  the text, so old run files are judged too.

## 0.4.0 (2026-09)

Response to the reference-grounded audit (`docs/audit-2026-09-reference.md`,
finding by finding). Scores from 0.3.0 are not comparable; replay saved runs
with `scripts/rescore.py` (no model calls needed).

### Scoring changes (scores move)
- **Trust boundary.** Model code hands over BREP geometry; a trusted process
  parses and measures it. A fabricated object reporting nominal numbers
  scored 1.0 before (its real geometry was a 1 mm cube). Fork mode no longer
  unpickles anything a rollout produced.
- **New requirement R8, Z datum** (plate mid-plane at Z = 0 +/- 0.5 mm).
  Reward is now k/9. A correct part moved 100 mm in Z scored 1.0 before.
- **New gate `clean_solid`**: valid B-rep, one shell per solid, no loose
  faces/edges/vertices. Sealed cavities and loose faces scored 1.0 before.
- **Open-passage check** in `simple_through_holes`: a rod along each bore
  must meet no material. A 0.005 mm membrane scored 1.0 before.
- **Inclusive tolerances** with 1e-6 mm slack: 6.7 mm is inside 6.5 +/- 0.2
  (0.3.x failed it on floating-point rounding).
- A bare 2D sketch builds no solid and earns 0, not the 0.05 floor.
- Documented limitation: NURBS copies of correct parts score 0.

### Sandbox
- Child closes every inherited descriptor except its result pipe, runs in its
  own process group (killed whole afterwards), and completion is detected on
  child exit, so a lingering descendant cannot stall a finished rollout.
- `CAD_SPEC_MEM_MB` is honoured (it was erased before being read).
- `SECURITY.md` rewritten per mode and platform, requested vs verified.

### Tasks and environment
- Every L4 change order moves a value beyond its tolerance; 5 train prompts
  changed, eval prompts unchanged (verified).
- Reward functions share one build per rollout through verifiers' `state`;
  nothing is shared across rollouts.

### Evaluation tooling
- Mutation suite: sign bug in shrink mutations fixed; build failures now fail
  every check; new families for Z shift, exact limits, membranes, cavities.
  0.4.0: 0/600 false full credit, 0/600 false rejection over 1,230 mutants.
  The same suite finds 15.0% false full credit in 0.3.0.
- `parser-template` baseline: reads L3 by template position, 100% on L3.
- Run files: unique run ids, never overwritten, planned-sample manifest, end
  record, full commit + dirty flag + diff hash, runtime versions, served model,
  prompt per row. Budget is a projected-cost stopping threshold.
- Summary: flags incomplete, interrupted and duplicate runs, judges legacy
  truncation against the run's real token cap, shows the median, warns on
  mixed scorer versions, marks unknown costs.
- `scripts/rescore.py` replays saved answers through the current scorer.
- `openrouter_models.py` hides free routers, `:batch`, `~` aliases and
  non-text models by default.

### Baseline tooling (first shipped after 0.3.0)
- `run_baseline.py` records `finish_reason` and a `truncated` flag per rollout,
  the exact USD cost per call on OpenRouter, and the serving provider.
  Found by the first qwen3:4b run: 131 of 150 answers were empty because the
  model spent the whole 4,096-token budget thinking; nothing in the output
  showed it.
- `--budget USD` hard stop; abort after 5 consecutive API errors (exit 3);
  `--extra-body` for provider parameters (e.g. reasoning effort); live
  progress line with spend and ETA.
- `summarize_results.py` adds Truncated, API errors and Cost columns, and
  lists any (model, tier) with over 5% truncated or failed calls as not
  publishable. Legacy rows are checked too (empty answer at the token cap).
- `openrouter_models.py`: live OpenRouter catalogue with the cost of a full
  cad-spec run estimated from the real prompt sizes.

## 0.3.0 (2026-09)

Response to the September 2026 audit (`docs/audit-2026-09.md`).

### Scoring changes (scores move)
- **New requirement R7 edge margin**, measured from the part's actual
  envelope. Reward scale is now k/8 (was k/7). A plate shifted under nominal
  holes scored 1.0 before; it now loses R7 only.
- **Bore depth is the union of coaxial face spans**, not the tallest face. A
  bore cut by a symmetric cutter (two stacked faces) scored 0.0 before; it now
  scores like the reference.
- `simple_through_holes` now requires one uninterrupted bore from the stock's
  bottom face to its top face (datum check), per position.
- **Every object on the Workplane stack is measured.** Before, only `.val()`
  was, so loose pieces built with `combine=False` were scored as one piece
  and the `single_solid` gate never fired. `HACK_corner_tabs` had been
  passing for the wrong reason.

### Measurement
- `Measurements` gains envelope coordinates (`x_min` ... `z_max`, `centre`)
  and `partial_bores`: concave groups that do not close (side-wall
  breakouts), reported instead of silently dropped. Still not scored.
- `Hole` gains `z_min`, `z_max`, `segments`.

### Execution
- POSIX: a fresh forked child per rollout with scrubbed environment, rlimits
  on CPU, memory, file size and open files, best-effort network namespace,
  and a deleted temp dir. Python state can no longer leak between rollouts.
- Windows: persistent worker, fresh temp dir per rollout; documented as
  trusted-only.
- `Dockerfile` for untrusted output at scale. `SECURITY.md` threat model.
- Timeout budget is sent with each request (changing
  `CAD_SPEC_EXEC_TIMEOUT` after the worker started was ignored).

### Tasks and environment
- Five prompt tiers (L0 to L4); `load_environment(tier=..., eval_tier=...)`.
- Zero-weight per-check metrics, one cached build per rollout.

### Evidence and tooling
- `scripts/validate_scorer.py`: labelled mutation suite with an independent
  geometry oracle. 0.3.0: 0/1,020 disagreements outside the documented
  limitation. 0.2.0 on the same suite: 5.9% false full credit, 12.5% false
  rejection.
- `scripts/run_baseline.py`, `scripts/summarize_results.py`: provenance per
  rollout, per-tier tables with bootstrap intervals.
- Harness now pins each case's failed-check set; 28 cases (was 21).
- `cad-spec` CLI.

### Packaging
- `import cad_spec` no longer imports verifiers; the harness runs from a
  plain checkout with only cadquery (verified in CI).
- `constraints.txt` pins the verified dependency set; dependency ranges
  bounded in `pyproject.toml`.
- CI: clean-room job, pinned job with the validation gate, Docker job.
- MIT license, real CI badge.

Correction (0.4.0): the validation agreement above covers 990 of the 1,020
mutants (30 documented-limitation cases excluded); false full credit was
measured on 510 wrong parts and false rejection on 480 correct ones.

## 0.2.0 (2026-08)
Two-discriminator hole detection, worker isolation with timeout, k/7 reward
with material requirement R6, seeded 200/30 sampler, pytest and CI.
