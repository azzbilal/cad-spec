# Changelog

Scores are only comparable within one scorer version
(`cad_spec.rubric.SCORER_VERSION`).

## 0.4.1 (unreleased): training preparation

Scorer unchanged (0.4.0): every published score stands.

### Hub
- 0.4.0 published to the Prime Environments Hub as `bazzouzi/cad-spec`
  (wheel SHA-256 `c49371e9a9fad83f33fe553dbfd9f740bfce29a7e69c74b8e858bffb1f062691`),
  verified by downloading the served wheel and comparing fingerprints.
- `scripts/verify_hub.py`: re-scores saved answers with an installed copy of
  the package and requires identical rewards and check verdicts; refuses to
  run against the repository's own source.
- Package README (the Hub page): headline results, ranking chart, the
  `hints` option, links to the evidence.

### One prompt, one cheat-sheet
- `cad_spec/prompts.py` holds the system prompt; `cad_spec/hints.md` ships the
  cheat-sheet inside the package. The environment and `run_baseline.py`
  both import them (before, each kept its own copy of the system prompt).
  Tests pin both texts to the fingerprints recorded in the published runs.
- `load_environment(hints=True)`: cheat-sheet in the system prompt of
  training and eval rows alike, byte-identical to the experiment's hint arm.
- `run_baseline.py --hints`: the same text from the package; runs record
  `hints_source` and `system_prompt_sha256`.

### Locked test split
- `make_test_split()`: 60 specs from `TEST_SEED`, disjoint from all 230
  train and eval specs, pinned by `TEST_SPLIT_SHA256`; every spec solvable
  at every tier (tested). L3 uses the held-out wording.
- `run_baseline.py --split test` refuses to run without `--unlock-test`;
  `select_runs` (leaderboard, failure modes, label check) never selects a
  run that is not on the eval split. Regenerated reports are byte-identical.
- `docs/EVALUATION_PROTOCOL.md`: the eval split becomes the development set;
  the training claim is judged once, on the test split, base + cheat-sheet
  versus adapter + cheat-sheet.

### Cost tracking on any provider
- `--price-in` / `--price-out` (USD per 1M tokens): a call's cost is computed
  from its token counts when the provider reports none, so `--budget` binds
  on Prime Inference too. Rows record `cost_source` (provider or computed).
- A missing API key now fails fast for every remote endpoint, not only
  OpenRouter.

### Roadmap
- The six-step training plan replaces the single "one training run" item.

## Unreleased (0.4.0 follow-ups, merged)

### Knowledge or reasoning? Outcome of the pre-registered experiment
- All ten arm runs complete (five models x hint and feedback, 120 answers
  each, $0.18). P1 confirmed 4/4, P2 not confirmed (stacking half 4/4,
  API-error half 1/4), P3 confirmed 10/10. Reproduced on a second machine
  from the committed runs with identical tables and verdicts.
- README section "Knowledge or reasoning?"; Outcome section in the
  pre-registration; exploratory findings labelled as such (retries mostly
  repeat the same error; the cheat-sheet lowered the control model).
- `compare_arms.py`: exploratory feedback-retry counts (retried, built,
  passed, same error again); the exclusion list covers experiment models
  only.
- Failure report: tables and API-error counts cover first-shot answers
  only, with experiment arms in their own section (mixing them had raised
  "solid on the stack" from 108 to 166). The label file keeps every label.

### Hint and feedback arms, amendment 1 (before any run)
- External audit of the analysis, fixed before data: arms restricted to the
  three registered conditions; an arm is judged only if it matches its
  registration (settings, exact condition, clean complete run, exactly the
  30 held-out specs per tier); labels joined by run id, a missing label
  stops the analysis; intervals resample specs as clusters; retry costs
  summed call by call; model table on the analysed 120-answer denominator.
  Recorded as amendment 1 in the pre-registration. `scripts/test_arms.py`
  now runs run files through the real classifier and analysis (14 checks).

### Hint and feedback arms (pre-registered, not yet run)
- `docs/experiments/hint-feedback.md`: question, arms, five models,
  predictions P1 to P3 with thresholds, analysis and budget, committed before
  any run.
- Runner: `--arm`, `--system-prompt-file` (appended to the standard system
  prompt) and `--feedback-retries` (the plain build error, then a retry; only
  for code that does not build; every attempt recorded and its cost added).
  A task-changing run without `--arm` is refused.
- Runs are named by arm ("model [hint]"); the leaderboard ranks first-shot
  runs only. `scripts/compare_arms.py` computes paired changes with bootstrap
  intervals and the pre-registered verdicts. `scripts/test_arms.py` in CI.
- Run files are read as UTF-8 on every platform.

### Label check, seed 20260928 (AI-assisted, 27/30)
- Measurements report `off_axis_bores`: closed concave bores along X, Y or
  any non-Z axis (same concavity and completeness tests as Z bores).
  Diagnostics only, never scored; mutation suite unchanged.
- New label "holes drilled along the wrong axis"; an answer with no Z bore
  whose side-face drilling repeats without moving is "holes stacked at one
  point" (maintainer's ruling).
- Mistake patterns (corner, margin twice, swapped, pitch as coordinates) must
  place every measured hole on the grid they predict; matching extremes is
  no longer enough.
- Method stated: labels are checked by AI-assisted review of three fresh
  samples (28/30, 28/30, 27/30); no human-validated figure is claimed. Holes
  that land off the plate are a documented limitation.

### Label check, seed 20260927 (AI-assisted, 28/30)
- Error origin tag moved to the start of the error text: the 300-character
  cap on sandbox error text cut an end tag from long messages, so 11 answers
  of CadQuery misuse were labelled "build failed". The tag also names the
  innermost CadQuery function (`[raised in cadquery: Workplane.rect]`), and
  generic errors are reported as "TypeError in Workplane.rect()". Only the
  scorer writes the prefix, so model code cannot forge it. Tested through
  the real sandbox, cap included. Rescore saved runs with `--force`.
- New label "geometry kernel failure": kernel refusals of valid calls (a
  fillet too large for its edge) are no longer counted as API misuse.
- "Cannot union type" is a named API error kind.

### External audit of the publish patch (fixed before release)
- Headline inflation: a model is ranked only if every headline tier covers
  exactly the 30 held-out specs (derived from the sampler, not the run file);
  run summaries check spec-by-spec coverage against the run plan and no
  longer crash on a plan without spec ids. `scripts/test_leaderboard.py`.
- Classifier: every hole must sit at a nominal corner before a pattern is
  accepted; code rules read parsed code, so comments cannot change a label;
  L4 stale-pitch evidence comes from the syntax tree; one unreadable answer
  gets "classifier error" instead of aborting the analysis.
- New label "Python error in model code": the scorer now tags each execution
  error with where it was raised (`[raised in model code|cadquery|other
  library]`); CadQuery misuse needs a CadQuery message or origin. Scores are
  unchanged; rescore saved runs with `--force` to refresh error texts.
- `scripts/check_release.py` in CI: every relative link in the docs must
  resolve, so a claim cannot ship without its evidence file.
- Attribution corrected: the 28/30 label check was AI-assisted, not a human
  validation; a human check on a new seed is on the roadmap.

### Leaderboard published
- README: ranking chart, 16-model table, what the board shows (stack
  semantics, change-order propagation, invented methods, scale), how the
  labels were checked, and the lower-bound caveats. The results (rescored
  runs, leaderboard, failure analysis) are committed in the same pull
  request; the release check fails CI if any linked file is missing.
- `docs/label-check.md`: method and both label checks. Fresh AI-assisted
  sample (seed 20260926): 28/30 labels in the correct category.
- Fixes from that check: `DispatchError` is a CadQuery API error; an L4
  answer whose code keeps rev A's pitch on a rev B plate is "change not
  propagated" even when no hole lands on the plate. Three more named API
  error kinds. Self-test: 19 modes.

### Human label check (30 random failed answers, September 2026)
- Result on the first sample: every label was a true statement about the
  geometry (30/30); 25/30 named the right category. All 5 misses were
  answers drilling repeatedly at one spot (.hole() calls separated by
  .translate(), .faces().workplane() or mirror calls) filed as "other".
- Stacked rule rewritten: two or more .hole() calls (or one in a loop that
  never uses its variable) with nothing that sets a new position
  (transformed, moveTo, pushPoints, vertices, rarray, polarArray, a non-zero
  center). Answers whose holes were really placed apart but mostly landed
  off the plate (cumulative .transformed() offsets) stay "other".
- One shared run selection (`select_runs`) for the leaderboard, the failure
  analysis and the label check: superseded reruns are no longer
  double-counted in the failure table.
- `scripts/label_check.py`: writes the review file keyed by run id (the
  hand-made first version mixed two phi-4 runs and showed one run's code
  beside the other's measurements), with the correct hole centres worked out,
  the plate's global position, and the full prompt and code; refuses to show
  code it cannot match to one answer. Use a new --seed for every check.
- Failure details record the plate's bounding box; self-test now 17 modes
  plus a superseded-run check.

### A scorer that cannot run never scores
- New `ScorerUnavailableError` (not a `BuildError`): raised when CadQuery is
  not importable or the scorer worker cannot start, and never caught by
  `score()`. Every scoring script checks CadQuery first and exits with the
  fix ("activate the environment") instead of recording zeros. Found when a
  session without the virtualenv scored a whole llama run as unbuildable.

### Leaderboard fixes
- A (model, tier) rerun several times uses the latest run with no problems;
  notes describe only the run used, plus a count of superseded runs.
- Failure table: reference programs (parsers, rev A) listed separately from
  models; every labelled answer keeps its evidence (error text, measured hole
  positions, plate size); CadQuery API errors broken down by kind (no such
  method, wrong arguments, empty stack, kernel refusal...); two new pattern
  labels, "some holes right, some wrong" and "one axis misplaced", shrink
  the unexplained bucket. Self-test: 14 modes plus the API-kind breakdown.

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
