# Changelog

Scores are only comparable within one scorer version
(`cad_spec.rubric.SCORER_VERSION`).

## Unreleased

### Baseline tooling
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

## 0.2.0 (2026-08)
Two-discriminator hole detection, worker isolation with timeout, k/7 reward
with material requirement R6, seeded 200/30 sampler, pytest and CI.
