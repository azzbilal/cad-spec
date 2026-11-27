# What is true now
<!-- Loaded into every Claude Code session by agent-workshop. Keep under 60 lines.
     Current truth only. History goes to LOG.md. Rewrite, do not append.
     CLAUDE.md is loaded too: its rules and state are not repeated here.
     Machine-specific details live in .workshop/local.md (git-ignored, not loaded). -->

## Product and mode
- Mode: promise-keeping. Released v0.5.0; the promises in PROMISES.md were confirmed by Bilal on 2026-11-26.
- Users: Bilal only, for now. Later: CadQuery and OCCT users, and people building CAD
  benchmarks (Gauge).

## Decisions not visible in the code
- The end-of-turn hook runs a light check (under 30 s). The full CLAUDE.md commit checks are
  a manual step before every commit, not a hook (2026-11-26).

## Environment quirks
- The working venv is `.venv/` at the repo root (Python 3.12.10, CadQuery 2.8.0, ruff, mypy,
  pytest). The system `py -3.12` has no CadQuery. `~/cadspec.sh` activates `.venv`.
- `.workshop/checks.json` runs through `bash` found on PATH (Git Bash on Windows) and puts
  `.venv/Scripts` on PATH itself.

## How to verify
- Per edited file (onEdit hook): `ruff check --force-exclude <file>` under `scripts/` and
  `environments/cad_spec/`.
- End of turn (onStop hook, 26 to 28 s): ruff over the CI lint scope, then pytest `-m "not slow"`
  without `tests/test_environment.py` and `tests/test_training_prep.py`. Those two files and the
  3 slow tests only run in the full checks.
- Before a commit (manual, about 135 to 155 s): the "Checks before every commit" block of CLAUDE.md.
- CI only (Linux): fork sandbox replays, verdict diffs, GL-less scoring, docker sandbox, mutation gate.

## Open threads
- L5 M1 is counted as audited after the fourth round (`audit/l5-m1-v4-audit.md`, 27 November
  2026), once branch `fix/l5-m1-audit` is merged. M2 may start. Observation version 2. Deferred:
  scope-scan probe point (M3), two scorer-path defects (next scorer version).
- Rare `worker fault: MemoryError` from the Windows reuse worker on ordinary gate cases (2 of 73
  in one gate run, none in the reruns). measure.py was not touched; cause unknown. Owner: Bilal.
- agent-workshop hook bug (session marked edited before the path filter): fix drafted, not
  applied. Owner: Bilal.
