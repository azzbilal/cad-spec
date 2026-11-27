# Log (what happened)
<!-- Append-only, dated, one line per event. Not loaded at session start.
     Types: decision, correction, incident, sweep, release, retired. -->

- 2026-11-26 decision: initialised agent-workshop (promise-keeping mode; NOW.md, PROMISES.md with DRAFT promises, checks.json)
- 2026-11-26 decision: end-of-turn hook is a light check (ruff over CI lint scope, pytest not-slow minus test_environment and test_training_prep, 26 to 28 s); full commit checks stay manual
- 2026-11-26 decision: L5 M1 not counted as audited (4 advisory findings open, no review after C1)
- 2026-11-26 decision: machine-specific notes moved to .workshop/local.md (git-ignored); checks.json uses bash from PATH
- 2026-11-26 correction: the open advisory M1 findings are five, not four (probe point, symmetric matching, centred epsilon, edge-ligament refusal, Measurements migration)
- 2026-11-26 decision: promises P-01 to P-06 confirmed by Bilal.
- 2026-11-27 decision: L5 M1 counted as audited after round 4 (audit/l5-m1-v4-audit.md), once fix/l5-m1-audit is merged; M2 may start
- 2026-11-27 finding: two wrong values under ok found and refused in cad_spec/l5 (one hole split across the measurement grouping gave n = 3; faces of one hole 8e-8 mm apart gave an order-dependent mx); centered now by straight-line distance
- 2026-11-27 decision: results/l5/ is a generated folder (CLAUDE.md rule 3); M1 ships in the next package release with verifiers 0.4 support, no bump in this PR
- 2026-11-27 decision: axis-spread limit 0.5e-9 mm so px and py stay within 1e-9 (G1); D order dependence documented, deferred to M3 (G2); OBSERVATION_VERSION 2
- 2026-11-27 correction: the generated-file exception covers results/l5/m1-observation-suite.md only (not the folder); narrow exceptions written in CLAUDE.md rules 5 and 8
- 2026-11-27 finding: 180 ordinary controls rerun against observation version 2: 180 ok, 0 refused, largest difference 7.1e-15 mm
- 2026-11-27 finding: rare worker fault MemoryError in Windows reuse mode on ordinary gate cases (2 of 73 in one run); not reproduced on rerun
- 2026-11-27 correction: G2 is not only a false refusal; one cut order gave ok with D 1.8e-9 mm from a face (final blind review, H1). Owner ruled: D check over every face of the through holes, now in observation version 2
- 2026-11-27 decision: final verdict, M1 audited once fix/l5-m1-audit is merged (audit/l5-m1-v4-audit.md section 13)
- 2026-11-27 decision: pocket deviation (extra pocket or slot is form_violation, not out_of_scope) approved by Bilal; 12 pocket variants probed, none ok
