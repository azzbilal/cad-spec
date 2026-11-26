# Promises register
<!-- Brownfield promises: properties we must not regress. Titles (## P-xx) are loaded at
     session start. A promise without a measurement is a wish.
     Standing instruction: the same, but faster, cheaper, safer. Never trade one for another.
     Every promise below was confirmed by Bilal on 2026-11-26. Each one restates a gate or a rule
     that already exists in CI or CLAUDE.md; none adds a new threshold. P-04 is the only new
     measurement: a git command that checks rules 3 and 4 of CLAUDE.md. -->

## P-01 The mutation suite (10 specs) finds no false full credit and no false rejection
Measure: `python scripts/validate_scorer.py --specs 10 --out <temp dir>` (CI job pinned-validation, "Mutation validation gate")
Current: not measured on 2026-11-26 (CI only)    Floor: 0 false full credit, 0 false rejection
Loop: CI on every push and PR; a breach blocks the merge. A scorer change starts with this defect suite, committed before the scorer (CLAUDE.md rule 5).
Owner (human): Bilal    Last verified: not yet

## P-02 Hand-labelled and adversarial scorer cases keep their expected verdicts
Measure: `python scripts/test_rubric_050.py` (81 hand-labelled cases, scorer 0.5.0) and `python scripts/test_rubric.py` (adversarial harness)
Current: exit 0 for both on Windows, `.venv` Python 3.12.10 (test_rubric_050.py 14 s, test_rubric.py 4 s)    Floor: exit 0 for both
Loop: the manual full CLAUDE.md commit checks before every commit (both scripts run there; the light end-of-turn hook does not run them); CI test matrix (Ubuntu and Windows, Python 3.11 and 3.12).
Owner (human): Bilal    Last verified: 2026-11-26

## P-03 Recorded verdicts reproduce byte for byte, and published scores stay reproducible
Measure: CI pinned-validation steps: run 1 test-split replay with 0 mismatches; replication 1 replay and `diff` of verdict.json / verdict.md empty; bridge check `diff` empty. Scorer 0.4.0 stays selectable: `score(..., version="0.4.0")` in rubric.py.
Current: not measured on 2026-11-26 (Linux fork sandbox, CI only)    Floor: 0 mismatches, empty diffs, "0.4.0" key present in TOLERANCES
Loop: CI on every push and PR. A new scorer gets a new version; a recorded verdict is never replaced (CLAUDE.md rule 4).
Owner (human): Bilal    Last verified: not yet

## P-04 Registered records and frozen scripts are never rewritten on a branch
Measure: `git diff --numstat main...HEAD -- docs/experiments results` (deleted-lines column) and `git diff --quiet main...HEAD -- scripts/compare_training.py scripts/compare_replication.py scripts/bridge_check.py scripts/replication_split.py`
Current: 0 deleted lines, frozen-scripts diff exit 0 (run on main at 6fa44c5, so main...HEAD is empty)    Floor: 0 deleted lines under docs/experiments and results; frozen scripts unchanged (exit 0)
Loop: by hand before every PR (no hook or CI step checks this yet). Corrections are dated sections appended below the original (CLAUDE.md rule 3).
Owner (human): Bilal    Last verified: 2026-11-26 (on main only; first real test is the next branch)

## P-05 The scorer runs from a plain checkout with nothing but CadQuery installed
Measure: CI job clean-room: `pip install "cadquery==2.8.0"`, `python scripts/test_rubric.py`, and `verifiers` must not be importable
Current: not measured on 2026-11-26 (CI only)    Floor: job green
Loop: CI on every push and PR (README, "Scorer only").
Owner (human): Bilal    Last verified: not yet

## P-06 The Docker image scores the reference answer with every lockdown flag on
Measure: CI job docker: the reference answer scores inside `docker run --network none --read-only --memory 2g --pids-limit 128 --cap-drop ALL --security-opt no-new-privileges`
Current: not measured on 2026-11-26 (CI only; Windows runs `reuse` mode, the hardened `fork` mode is Linux only)    Floor: job green with every flag above kept
Loop: CI on every push and PR. Removing a flag is a security regression, not a cleanup.
Owner (human): Bilal    Last verified: not yet
