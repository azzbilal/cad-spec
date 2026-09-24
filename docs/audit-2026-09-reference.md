# Audit 2 (reference-grounded) and its disposition

**Audited revision:** `221a25a` (scorer 0.3.0), read-only, September 2026.
**Method:** an AI reviewer acting as a metrology / ML-evaluation / security
panel, with 12 reference repositories cloned locally for comparison
(CADTestBench, BenchCAD, Hugging Face cadgenbench, CadQuery, human-eval,
EvalPlus, bigcode-evaluation-harness, SWE-bench, inspect_ai,
lm-evaluation-harness, verifiers, prime-environments). Every finding had to
cite a file and line and, where possible, a reproduced probe.
**Verdict at 221a25a:** 4/10 overall (D1 scoring 3, D2 metrology 4, D3 safety
2, D4 validity 5, D5 statistics 6, D6 claims 4).

The five geometry findings were independently reproduced before fixing
(fake result object 1.0, 0.005 mm membrane 1.0, sealed cavity 1.0, NURBS copy
of a correct part 0.0, 6.7 mm hole failing 6.5 +/- 0.2).

## Findings and what was done

| ID | Sev. | Finding | Disposition in 0.4.0 | Pinned by |
|---|---|---|---|---|
| F01 | Critical | Fork child's result was unpickled in the persistent worker; child inherited the worker's control pipe | Child returns a status byte + BREP bytes or capped error text; no pickle crosses from a rollout. All inherited descriptors closed except the result pipe | `test_child_cannot_reach_the_worker_pipe`, `test_fake_result_object_through_the_sandbox` |
| F02 | Critical | Deadline did not cover receipt and cleanup; descendants survived | Child runs in its own process group, SIGKILLed after every rollout; completion is detected by child exit, so a descendant holding the pipe cannot stall a finished rollout; worker kill escalates terminate to kill | `test_descendants_are_killed_with_the_rollout` |
| F03 | High | A fabricated object reporting nominal geometry scored 1.0 | Scorer measures only the kernel shape serialised to BREP; the object's methods are never called. A bare Sketch no longer earns the 0.05 floor | `HACK_fake_result_object`, `BROKEN_sketch_only`, `test_fake_result_object_is_measured_by_its_real_geometry` |
| F04 | High | Blind holes leaving a 0.005 mm membrane passed as "through" | Open-passage probe: a rod along each bore axis must meet no material (detects 0.00001 mm) | `HACK_membrane`, `test_membrane_is_not_open`, validation family `membrane` |
| F05 | High | Internal cavities and loose faces kept full credit | New gate `clean_solid`: valid B-rep, one shell per solid, no loose sub-shapes | `HACK_hidden_cavity`, `HACK_loose_face`, validation family `cavity` |
| F06 | High | NURBS copy of a correct part scored 0 | Documented limitation: bores are recognised as analytic cylinders only | `LIMIT_nurbs_surfaces` |
| F07 | High | Exact tolerance limits failed on float rounding | All comparisons inclusive with 1e-6 mm slack | `diameter_upper_limit`, `diameter_lower_limit`, validation family `exact_limit` |
| F08 | High | `CAD_SPEC_MEM_MB` erased before being read | Budget captured by the trusted parent and passed in | `test_memory_limit_setting_is_honoured` |
| F09 | High | SECURITY.md over-promised | Rewritten per mode and platform; requested vs verified stated | `SECURITY.md` |
| F10 | Medium | Validator moved holes the wrong way on shrink mutations | Sign fixed | `validate_scorer.py` |
| F11 | Medium | Build failures read as passes in per-check statistics | A build failure fails every check | `validate_scorer.py` |
| F12 | Medium | Some train change orders stayed within tolerance | Every ECO moves at least one field beyond its tolerance + 0.25; eval prompts unchanged (verified) | `test_l4_unedited_rev_a_never_scores_full_marks` |
| F13 | Medium | A positional parser solves the L3 eval prompts | Published as the `parser-template` baseline (100% on L3); README restates L3 as robustness to unseen phrasing, not unshortcuttable reading | `results/baselines-deterministic.md` |
| F14 | Medium | Incomplete runs looked complete | Runs record the planned manifest and an end record; the summary flags partial, interrupted and duplicate runs | `summarize_results.py` |
| F15 | Medium | Legacy truncation used a fixed 1,000-token threshold | Uses the run's recorded `max_tokens` | `summarize_results.py` |
| F16 | Medium | Provenance insufficient | Full commit, dirty flag including staged changes, diff hash, runtime versions, served model, and the prompt on every row | `run_baseline.py` |
| F17 | High | "Hard spending cap" was post-call accounting | Now a projected-cost stopping threshold, documented as such; unreported costs counted and flagged | `run_baseline.py`, `README.md` |
| F18 | High | Doc numbers diverged from code | Corrected: validation denominators, sampled diameter range, ECO change range, median reported, dependency bounds, stack wording | `README.md`, `docs/DATA_CARD.md` |
| K1 | High | Z placement unscored | New requirement `R8:z_datum` (0.5 mm); reward is now k/9 | `part_off_z`, validation family `part_dz` |
| K2 | Medium | Report cache shared across rollouts | Shared per rollout through verifiers' `state` only | `test_metrics_share_one_build_per_rollout` |
| K3 | Medium | Run ids at 1 s resolution; output overwritten | Microsecond id + random suffix; output opened exclusively; summary refuses duplicate run ids | `run_baseline.py`, `summarize_results.py` |
| K4 | | Side-wall breakout not counted | Unchanged, documented | `LIMIT_hole_breakout` |
| K5 | | Windows reuse mode does not isolate state | Unchanged, documented | `SECURITY.md` |
| K6 | | One part family | Unchanged, on the roadmap | `ROADMAP.md` |

## Evidence the fixes work

The 0.4.0 mutation suite, run against the unchanged 0.3.0 scorer, reports
15.0% false full credit (every Z-shift, membrane and cavity mutant on all 30
specs) and 4.7% false rejection (exact-limit diameters). Against 0.4.0 it
reports 0% and 0% over 1,230 mutants. Both files are in `results/`.

## Reference comparisons worth keeping

- **cadgenbench** checks B-rep validity, watertightness and internal voids in
  a separate validity pipeline; `clean_solid` follows the same idea.
- **BenchCAD** executes CadQuery in a subprocess with a timeout but no
  resource limits, and normalises pose and scale before voxel IoU; cad-spec
  deliberately does not normalise pose, because the prompt fixes the datums.
- **inspect_ai** and **lm-evaluation-harness** record task versions, package
  versions, sample identities and original versus effective sample counts;
  the run file schema now carries the equivalent fields.
- **verifiers** passes a per-rollout `state` to every reward function; the
  report is now shared through it, the documented pattern in
  prime-environments.
