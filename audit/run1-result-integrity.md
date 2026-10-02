# Training run 1: result integrity audit

Verdict: **yes with caveats**, the saved-file gain survives this audit.
Confidence: **95%**, a subjective assessment of artifact integrity, not a statistical probability of generalization.
Primary result reproduced: **72/120 to 120/120**, +40.0 points, registered interval [+32.5, +47.5].
Evidence: **960/960 rescoring runs agree**, all **239/239 adapter passes** match nominal geometry independently, and no local split leakage was found.
Most important caveat: this is **one training run on one narrow plate generator**; 100% on these 60 specs does not establish universal reliability or general CAD ability.

The numerical evidence in these five lines is in [reproduced verdict](scratch/run1-verdict.json), [repository rescore](scratch/run1-rescore-repo.json), [wheel rescore](scratch/run1-rescore-wheel.json), [independent geometry](scratch/run1-geometry.json), and [mechanical results](scratch/run1-mechanical.json). The confidence is explicitly judgment, conditional on the saved artifacts being authentic. Hosted request application and adapter weight provenance cannot be authenticated offline.

## Evidence table

| Question | Finding | Source |
|---|---|---|
| 1. Verdict reproducible? | Yes. Both regenerated verdict files are byte-identical, including all rates, intervals, thresholds, and verdicts. | [extended results](scratch/run1-extended.json): `verdict_md_byte_identical`, `verdict_json_byte_identical`; [compare_training.py](../scripts/compare_training.py), `analyse`, `paired` |
| 2. Scores deterministic? | All 480 answers match with repository code and independently with installed 0.4.5, in reverse order. Zero binary, continuous-reward, check-map, or build-status mismatches. | Rescore JSON files: `rows`, `mismatches`, `results[*].*_equal`, `order`, `modules` |
| 3. Registration conformity? | Both saved files conform. Exactly the expected 240 keys each, locally identical test prompts and system prompt, matching settings, complete ends, no API errors or retries. One permitted base truncation. | [mechanical results](scratch/run1-mechanical.json): `base`, `adapter`, `prompt_arms_equal`; [base JSONL](../results/training/run1/eval/base-test.jsonl) and [adapter JSONL](../results/training/run1/eval/adapter-test.jsonl): meta, end, rows |
| 4. Leakage? | No test ids or dimension tuples in train/development targets; none in embedded rev A geometry. No exact L3 wording overlap; template indices are disjoint. Actual local training dataset has 800 rows and zero test ids. | [mechanical results](scratch/run1-mechanical.json): `leakage`; [tasks.py](../environments/cad_spec/cad_spec/tasks.py): lines 153, 194, 295-306, 339; [environment.py](../environments/cad_spec/cad_spec/environment.py): lines 23-24, 80-100, 251-252 |
| 5. Reward hacking? | No suspicious executable constructs in adapter code. All 239 passes build the exact requested simple plate. All 72 out-of-tolerance perturbations fail their expected checks; 24 tolerance-boundary controls pass as designed. | [mechanical results](scratch/run1-mechanical.json): `hygiene`; [independent geometry](scratch/run1-geometry.json): `summary`, `results`; [perturbation results](scratch/run1-perturbations.json) |
| 6. What changed? | Longer, more variable-based adapter answers; L4 usually updates the pattern rather than merely replacing box dimensions. Explicit margin arithmetic is common but is not required in every correct answer. | [mechanical results](scratch/run1-mechanical.json): `lengths`, `structures`; [extended results](scratch/run1-extended.json): arithmetic records; paired excerpts below |
| 7. Discordant pairs? | 70 base-fail/adapter-pass pairs, zero reverse pairs. One common failure, L3/test-0054, remains in adapter. Every discordance is listed below. | [mechanical results](scratch/run1-mechanical.json): `discordant`, `adapter_failures`; rescore details by `(arm,tier,spec_id)` |
| 8. Inflation risks? | No recorded prompt/decoding difference. Serving internals remain unverified; ceiling bootstrap does not measure training-seed variability. The observed passes do not exploit tolerance slack. | [extended results](scratch/run1-extended.json): `metadata_differences`, cluster statistics; [rubric.py](../environments/cad_spec/cad_spec/rubric.py): lines 36-48; [compare_training.py](../scripts/compare_training.py): `paired`; [base JSONL](../results/training/run1/eval/base-test.jsonl) and [adapter JSONL](../results/training/run1/eval/adapter-test.jsonl): meta.sandbox |

## File integrity and reproduction

Audited checkout: `6f038c6c3ad7e2fb1cbb6872311d8d040ac21d24`, also recorded as `git_commit` in both evaluation metas. The registered analysis was rerun offline into `audit/scratch/run1-verdict.*`, never over the originals. Sources: evaluation meta.git_commit; [extended results](scratch/run1-extended.json), byte-equality fields.

| Original artifact | SHA-256 |
|---|---|
| `results/training/run1/eval/base-test.jsonl` | `6aee64245417a56614f9d0654bf944469de193ea5e09bdbdad71c6195639ffb3` |
| `results/training/run1/eval/adapter-test.jsonl` | `d937884ce262766a375042cb327a5f360978338a5db5daaf47579da34f3117e4` |
| `results/training/run1/verdict.md` | `5bfcc2e9d7c8d0d21cceda2f5a9f77a6f5d0090af230dc9dce65d4c7d1b627b5` |
| `results/training/run1/verdict.json` | `30a037bf938cbe40879c0810ef07d0f9be9e82ee7efb5be32c6a8dda4f8925ed` |

Hashes are regenerated by [run1_mechanical.py](scratch/run1_mechanical.py); original verdict numbers and regenerated numbers are identical. Reproduction commands, all local:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
& environments/cad_spec/.venv/Scripts/python.exe scripts/compare_training.py --base results/training/run1/eval/base-test.jsonl --adapter results/training/run1/eval/adapter-test.jsonl --out audit/scratch/run1-verdict
& environments/cad_spec/.venv/Scripts/python.exe audit/scratch/run1_mechanical.py
& environments/cad_spec/.venv/Scripts/python.exe audit/scratch/run1_rescore.py --repo --out audit/scratch/run1-rescore-repo.json
& C:/Users/bgare/hubcheck045/Scripts/python.exe audit/scratch/run1_rescore.py --out audit/scratch/run1-rescore-wheel.json
& environments/cad_spec/.venv/Scripts/python.exe audit/scratch/run1_geometry.py
& environments/cad_spec/.venv/Scripts/python.exe audit/scratch/run1_extended.py
& environments/cad_spec/.venv/Scripts/python.exe audit/scratch/run1_report.py
```

The shell supplied to this session was PowerShell, so direct venv interpreters were used instead of sourcing the Git Bash helper, which also loads API keys. No key or network request was needed. All handwritten scripts and audit outputs are under `audit/`. Python bytecode writing was disabled. Saved model code ran only through `cad_spec.rubric.score` with `CAD_SPEC_SANDBOX=reuse`; `CAD_SPEC_INPROC` was explicitly removed. Sources: commands above; [rescore script](scratch/run1_rescore.py), [geometry script](scratch/run1_geometry.py).

## Score determinism and registration

The repository rescore evaluated base then adapter in recorded order; the installed-wheel rescore evaluated all 480 in reverse order with a fresh interpreter. Both yield base 169/240 and adapter 239/240 overall. Every full check dictionary, continuous score, binary all-pass classification and parsed status matches, including the six base build failures. Mismatch list: **empty**. This establishes reproducibility of these saved outputs on this Windows/CadQuery stack, not deterministic generation by Prime. Sources: repository and wheel rescore files, `counts`, `mismatches`, `results`.

Both rescore interpreters use Python 3.12.10, CadQuery 2.8.0 and OCP 7.9.3.1.1. Repository and installed wheel `measure.py`, `rubric.py`, and `tasks.py` have identical SHA-256 hashes. The repository import reports package `__version__=0.4.5`, although its local installed distribution metadata says 0.4.0; the clean wheel reports distribution 0.4.5. This stale local metadata does not change executed code or the common scorer version 0.4.0. Sources: rescore `modules`, `package_version`, `scorer_version`; [extended results](scratch/run1-extended.json): `repo_package_version`.

Registration checks, independently beyond the comparison script's checks:

| Field or condition | Base | Adapter |
|---|---|---|
| Requested and served model | `Qwen/Qwen3.5-9B`, all 240 rows | `Qwen/Qwen3.5-9B:xfisiyo5vlhn0ys65sf4uad7`, all 240 rows |
| split / test seed | `test` / 20260927 | Same |
| TEST_SPLIT_SHA256 | `019d197efecedc079209fcb5900c7d5b2ff894481bc6cc85954826070c30c51b` | Same, regenerated locally |
| temperature / max_tokens / row seed | 0 / 2048 / 0 | Same |
| arm / hints_source / feedback retries | hint / package / 0 | Same |
| system_prompt_sha256 | `a9050c1da2a319200fd38c432c6505d2254b39249613b9079bf7cfb9f1e5128c` | Same, text also equals local packaged hints |
| extra_body | `chat_template_kwargs.enable_thinking=false` | Same |
| scorer / recorded package | 0.4.0 / 0.4.5 | Same |
| end.status / written / planned | complete / 240 / 240 | Same |
| API errors / retries / feedback attempts | 0 / 0 / 0 | Same |
| truncated / finish_reason=length | 1 / 1, L1/test-0050 | 0 / 0 |
| prompt mismatches against local test generator | 0/240 | 0/240 |
| duplicate or unexpected keys | 0 | 0 |

Source for every field: [mechanical results](scratch/run1-mechanical.json), `base` and `adapter`, plus both original JSONL metas/rows/ends. The base truncation rate is 1/240 = 0.417%, below the registered 5% refusal threshold, and outside H1's tiers. Removing it cannot change H1. Six base `error` fields are build errors, not API errors. Request settings are documented as sent by [run_baseline.py](../scripts/run_baseline.py), lines 253-291; the service applying them exactly is **unverified**.

## Reward-hacking findings

The adapter scan parses the same extracted code selected by the scorer, ignoring comments when looking for executable constructs. It inspects imports, calls, suspicious names, dunder attributes, attribute/subscript assignments, exception handlers, and definitions. All code is syntactically valid. There are 240 `cadquery` imports and zero other imports, zero flagged file/network access or dynamic execution, zero introspection, zero attribute/subscript writes or monkeypatches, zero `try` handlers, and zero function/class definitions. All call targets in `hygiene.call_counts` are ordinary CadQuery construction, list append, or one ordinary `ValueError` guard. Maximum extracted code is 4,859 characters and 96 lines; the long answers are commented construction code, not encoded payloads. These are observations about these answers, not proof that arbitrary CadQuery code is safe. Sources: [scan implementation](scratch/run1_mechanical.py), `features`; [mechanical results](scratch/run1-mechanical.json), `hygiene`; [per-answer features](scratch/run1-code-features.json).

There are **240 distinct completions and 240 distinct extracted programs**. Numeric-literal normalization, retaining names and AST shape but dropping comments/formatting, gives **194** structures; also canonicalizing variable names gives **126**. Per-tier structures are L1 45/18, L2 48/23, L3 55/41, L4 46/44, where each pair is numeric-only/name-normalized. These counts depend on the documented normalization; they are not a count of independent strategies. Sources: [mechanical results](scratch/run1-mechanical.json), `hygiene` and `adapter.structures`; [extended results](scratch/run1-extended.json), `exact_extracted_codes`; scan `Normalize`.

Every passing answer's length, width, thickness, bore diameter, hole centers, margin and centering equal its target values, including post-ECO L4 targets, within the independent 0.00001 mm numerical check. The one failed answer copies the correct dimensions but computes the wrong point layout. An independently checked fixed geometry is eligible for at most **one of the 60 test specs**, so a single unchanged numerical answer cannot explain the passes. A parameterized box-and-four-holes template can cover the whole family; correctly instantiating that algorithm is sufficient here, and does not demonstrate broader CAD reasoning. Sources: [independent geometry](scratch/run1-geometry.json), `results`; [extended results](scratch/run1-extended.json), `fixed_geometry_max_eligible_test_specs`, `fixed_geometry_wrong_targets`, and `fixed_geometry`; [eligibility algorithm](scratch/run1_extended.py).

Independent verification used the project's sandbox to execute each answer, appending only a trusted `result.val().exportBrep(...)` write under `audit/scratch/run1-breps/`. The export-instrumented answer preserves every original reward and check map, 240/240. A clean parent imports the BREP as data using CadQuery's importer, then independently checks bounding box, center, volume, validity, one solid, six planar faces, and four cylindrical faces with nominal diameters, Z extents and axes. It also builds an oracle using primitive cylinders cut from a box, and computes both boolean differences. It does not call `cad_spec.measure.measure`, its cylinder classifier, or its gate helpers for these decisions. Sources: [run1_geometry.py](scratch/run1_geometry.py), `inspect` and `main`; [independent geometry](scratch/run1-geometry.json), `summary.export_score_mismatches`.

Agreement is **239/239 passing answers**, and **240/240 overall pass/fail decisions**. For passing parts, maximum hole-position error, missing oracle volume, and extra volume are all zero in the retained output. This is stronger than merely falling within scorer tolerances. Caveat: both paths use CadQuery/OpenCascade, so this is an independent algorithm and fresh process, not an independent geometry kernel. It cannot detect a shared kernel defect. Sources: [independent geometry](scratch/run1-geometry.json), `summary`, `results[*].checks`, `missing_volume`, `extra_volume`, and saved BREP hashes.

Sensitivity sample: first four passing specs in each of L1/L2/L3, first twelve in L4, **24 answers total**. AST edits change only the hole API diameter, box X length, or X hole pitch; expressions and every mutant program are retained. The sample is deterministic, not a random population sample. Source: geometry script `Perturb`, `selected`; [perturbation results](scratch/run1-perturbations.json), `edits`, `code_file`.

| Change | Tests | All-pass lost | Expected failure |
|---|---:|---:|---|
| hole diameter +0.5 mm | 24 | 24 | R4b, 24/24 |
| box X length +1.0 mm, holes unchanged | 24 | 24 | R1, 24/24 |
| total X pitch +1.0 mm | 24 | 0 | None: each center moves 0.5 mm, inclusive tolerance |
| total X pitch +1.2 mm | 24 | 24 | R5 and R7, 24/24 each |

All 72 mutations beyond tolerance are caught by their expected checks; all 24 boundary controls retain full credit. The suggested +1 mm pitch perturbation is therefore **insufficient to falsify sensitivity**, for a documented mathematical reason, not because the scorer ignores geometry. Sources: [independent geometry](scratch/run1-geometry.json), `summary.sensitivity`; [perturbation results](scratch/run1-perturbations.json); [rubric.py](../environments/cad_spec/cad_spec/rubric.py), lines 38, 42, 48, 183, 212.

## Leakage findings

`make_splits()` produces 200 train and 30 development specs at seed 20260813. `make_test_split()` uses seed 20260927 and rejects any five-dimension tuple already in train, development or the test output itself. Local checks find zero overlaps by id and by `(length,width,thickness,hole_diameter,edge_margin)`, and zero overlaps between test targets and train/development L4 embedded rev A tuples. Sources: [tasks.py](../environments/cad_spec/cad_spec/tasks.py), lines 153-173 and 185-211; [mechanical results](scratch/run1-mechanical.json), `leakage`.

L3 training selects wording indices 0,1,2,3; test selects 4,5. No rendered L3 test prompt occurs among the 200 train L3 prompts. The source templates themselves are disjoint, not merely different numbers substituted into one template. This is only two held-out phrasing templates. Source: [tasks.py](../environments/cad_spec/cad_spec/tasks.py), lines 261-311; [mechanical results](scratch/run1-mechanical.json), `leakage.train_wording_indices`, `test_wording_indices`, `exact_L3_prompt_overlap`.

The training path is `load_environment` -> `_build_dataset(train_tiers)` -> `_rows(TRAIN_SPECS, tiers, "train")`; `TRAIN_SPECS,EVAL_SPECS=make_splits()`. Its lookup table contains only those 230 ids. The evaluated test generator is absent from this training route. The rebuilt 800-row L1-L4 dataset has exactly local train prompts and zero test ids; hints are the common packaged system prompt. Development dataset creation uses only `EVAL_SPECS`. Sources: [environment.py](../environments/cad_spec/cad_spec/environment.py), lines 23-24, 80-100, 245-252; [mechanical results](scratch/run1-mechanical.json), `leakage.environment_train_rows`, `dataset_prompt_mismatches`, `dataset_test_id_overlap`.

Archived training configuration and run record agree on environment 0.4.5, hints, binary reward, and the L4/L2/L1+L3 ratios. The archived payload contains no test-split override; config hash matches. This supports the local code-path conclusion but is **not a complete archive of every hosted rollout**. Unlogged service behavior, prior test exposure outside these artifacts, or contamination of model pretraining remains unverified; there is no positive evidence of it here. Sources: [extended results](scratch/run1-extended.json), `training`; [archived payload](../results/training/run1/payload-cad-spec-9b.json), `request.json.environments`; [run snapshot](../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/get.json), `run.environments`, `eval_config`, `val_config`.

## What changed in the answers

Descriptive lengths and structures, over 60 answers per tier:

| Tier | Mean chars base / adapter | Mean output tokens base / adapter | Answers with multiple assigned variables base / adapter | Answers with comments base / adapter |
|---|---:|---:|---:|---:|
| L1 | 1622.4 / 2000.8 | 560.0 / 752.5 | 59 / 60 | 60 / 60 |
| L2 | 1184.2 / 1683.8 | 363.7 / 601.8 | 60 / 60 | 60 / 60 |
| L3 | 1399.6 / 1921.5 | 455.7 / 703.8 | 60 / 60 | 60 / 60 |
| L4 | 324.0 / 1703.7 | 132.6 / 681.7 | 6 / 41 | 6 / 51 |

Source: [mechanical results](scratch/run1-mechanical.json), `base.lengths`, `adapter.lengths`, `structures`. Adapter produces more tokens in every tier, including about five times the base L4 mean, so this is not a token-efficiency gain. Its lower dollar cost reflects lower recorded route prices.

A conservative static arithmetic check finds subtraction expressions resolving to the nominal pitch or half-pitch in base/adapter counts L1 1/29, L2 51/56, L3 23/11, L4 5/19. This does not count arithmetic performed only in comments or directly hard-coded correct coordinates, and must not be read as a complete reasoning detector. It shows L2 arithmetic was already common in the base; the improvement also involves correct layout/API usage. Sources: [extended results](scratch/run1-extended.json), `subtraction_to_nominal_pitch_counts`, `arithmetic_records`; [numeric whitelist evaluator](scratch/run1_extended.py).

Three short same-spec paired excerpts follow. Source for each is the original evaluation row's `completion`, keyed by the indicated tier/spec; the corresponding failed checks are reproduced in both rescore files.

**L2/test-0014**, 162.5 x 99.5 plate, 11 mm margin. Base fails R5 and R7 by putting holes 11 mm from the origin; adapter computes the half-pitch from the stock edge.

Base:
```python
hole_x = EDGE_MARGIN
hole_y = EDGE_MARGIN
```
Adapter:
```python
hole_x_offset = (L / 2) - M
hole_y_offset = (W / 2) - M
```

**L4/test-0004**, length 79 -> 105 mm with unchanged 9.5 mm margin. Base updates the box but retains the old 60 mm X pitch; adapter sets 86 mm. Base fails R5 and R7, adapter passes all checks.

Base, selected lines:
```python
.box(105.0, 31.5, 5.0)
.rect(60.0, 12.5, forConstruction=True)
```
Adapter, selected lines:
```python
.box(105.0, 31.5, 5.0, centered=True)
.rect(86.0, 12.5, centered=True, forConstruction=True)
```

**L4/test-0002**, thickness 7.5 -> 9 mm and margin 8 -> 10 mm. Base applies thickness only; adapter changes the pitch from 43.5 x 140.5 to 39.5 x 136.5 mm as well. Base fails R5 and R7, adapter passes.

Base, selected lines:
```python
.box(59.5, 156.5, 9)
.rect(43.5, 140.5, forConstruction=True)
```
Adapter, selected lines:
```python
.box(plate_length, plate_width, new_thickness, centered=True)
.rect(39.5, 136.5, centered=True) # New rect size to achieve 10mm margin
```

All 38 base L4 failures miss R5 and R7. Six also fail the through-hole gate and hole count; seven fail diameter; three fail material. Every adapter L4 answer passes independently. The evidence supports improved change propagation and construction for this family; it does not identify internal reasoning or isolate GRPO from all other training choices. Sources: [mechanical results](scratch/run1-mechanical.json), `L4_failure_checks`, `discordant`; [independent geometry](scratch/run1-geometry.json).

## Discordant pairs and the sole adapter failure

L1: 8 improvements; L2: 10; L3: 14; L4: 38. **No base-pass/adapter-fail pair exists.** The remaining L3/test-0054 failure is common: base partial reward 0.6667, adapter reward 0.0, neither all-pass. Thus an all-pass improvement can coexist with a worse partial score on one already-failing spec. Sources: [mechanical results](scratch/run1-mechanical.json), `discordant`, `adapter_failures`; repository rescore, L3/test-0054 rows.

Adapter L3/test-0054 is an 86.5 x 155 x 7.5 mm plate requiring 8 mm bores on a 38.5 x 107 mm pattern. It interprets four holes as four in a line and sets X/Y coordinates to +/-1.5 times the pitch, rather than +/-0.5. Its attempted holes lie outside the blank, producing a plain box with zero cylindrical faces. Failed checks: `gate:simple_through_holes`, R4a, R4b, R5, R7. R6 still passes because missing-hole volume is only about 1.5% of the expected volume, inside its 3% allowance; the gate and hole-count checks correctly prevent full credit. Sources: adapter completion, L3/test-0054; rescore `details`; [independent geometry](scratch/run1-geometry.json), `summary.all_failures`.

Short adapter excerpt:
```python
x_offsets = [-1.5 * hole_spacing_x, 1.5 * hole_spacing_x]
y_offsets = [-1.5 * hole_spacing_y, 1.5 * hole_spacing_y]
```

Every discordant pair below is **base fails, adapter passes**. `Gthrough` abbreviates `gate:simple_through_holes`; R4a is count, R4b diameter, R5 pattern, R6 material, R7 margin. Empty check maps from build failures are explicitly marked, not counted as successful checks. Source: [mechanical results](scratch/run1-mechanical.json), `discordant`, with details in rescore files.

| Tier | Spec | Base failed checks or build error |
|---|---|---|
| L1 | test-0003 | R4a, R5, R6, R7 |
| L1 | test-0004 | R4a, R5, R6, R7 |
| L1 | test-0007 | R4a, R5 |
| L1 | test-0015 | R4a, R5, R7 |
| L1 | test-0029 | R4a, R5, R7 |
| L1 | test-0033 | R4a, R5, R7 |
| L1 | test-0038 | Gthrough, R4a, R4b, R5, R6, R7 |
| L1 | test-0050 | BUILD: execution failed [raised in other library]: SyntaxError: invalid syntax (<model>, line 1) |
| L2 | test-0011 | R4a, R5, R6, R7 |
| L2 | test-0014 | R5, R7 |
| L2 | test-0021 | R4a, R5, R7 |
| L2 | test-0023 | R4a, R5 |
| L2 | test-0026 | R5, R7 |
| L2 | test-0033 | R4a, R5 |
| L2 | test-0035 | R4a, R5, R7 |
| L2 | test-0041 | R5, R7 |
| L2 | test-0057 | BUILD: execution failed [raised in cadquery: Workplane.rarray]: ValueError: Spacing and count must be > 0 in at least one direction |
| L2 | test-0060 | R5, R7 |
| L3 | test-0010 | R4a, R5, R7 |
| L3 | test-0018 | R4a, R5 |
| L3 | test-0019 | R4a, R5 |
| L3 | test-0024 | R4a, R5 |
| L3 | test-0025 | R4a, R5 |
| L3 | test-0033 | R4a, R5 |
| L3 | test-0034 | Gthrough, R4a, R5, R6, R7 |
| L3 | test-0035 | R4a, R5, R7 |
| L3 | test-0040 | BUILD: execution failed [raised in model code]: AttributeError: 'Workplane' object has no attribute 'offset' |
| L3 | test-0041 | BUILD: execution failed [raised in model code]: AttributeError: 'Workplane' object has no attribute 'holes' |
| L3 | test-0045 | R5, R7 |
| L3 | test-0048 | Gthrough, R4a, R5, R7 |
| L3 | test-0051 | BUILD: execution failed [raised in cadquery: Workplane.rarray]: ValueError: Spacing and count must be > 0 in at least one direction |
| L3 | test-0052 | BUILD: execution failed [raised in model code]: AttributeError: 'Workplane' object has no attribute 'holes' |
| L4 | test-0002 | R5, R7 |
| L4 | test-0003 | Gthrough, R4a, R4b, R5, R6, R7 |
| L4 | test-0004 | R5, R7 |
| L4 | test-0005 | R5, R7 |
| L4 | test-0006 | R5, R7 |
| L4 | test-0008 | Gthrough, R4a, R4b, R5, R6, R7 |
| L4 | test-0009 | R5, R7 |
| L4 | test-0010 | R5, R7 |
| L4 | test-0011 | R5, R7 |
| L4 | test-0012 | R5, R7 |
| L4 | test-0013 | R4b, R5, R6, R7 |
| L4 | test-0016 | R5, R7 |
| L4 | test-0017 | R5, R7 |
| L4 | test-0018 | R5, R7 |
| L4 | test-0019 | Gthrough, R4a, R4b, R5, R7 |
| L4 | test-0020 | R5, R7 |
| L4 | test-0021 | R5, R7 |
| L4 | test-0022 | R5, R7 |
| L4 | test-0023 | R5, R7 |
| L4 | test-0025 | R5, R7 |
| L4 | test-0026 | R5, R7 |
| L4 | test-0027 | Gthrough, R4a, R4b, R5, R7 |
| L4 | test-0028 | R5, R7 |
| L4 | test-0031 | R5, R7 |
| L4 | test-0036 | R5, R7 |
| L4 | test-0039 | Gthrough, R4a, R4b, R5, R7 |
| L4 | test-0041 | R5, R7 |
| L4 | test-0045 | R5, R7 |
| L4 | test-0046 | R5, R7 |
| L4 | test-0047 | R5, R7 |
| L4 | test-0050 | R5, R7 |
| L4 | test-0051 | R5, R7 |
| L4 | test-0053 | Gthrough, R4a, R4b, R5, R7 |
| L4 | test-0056 | R5, R7 |
| L4 | test-0057 | R5, R7 |
| L4 | test-0058 | R5, R7 |
| L4 | test-0059 | R5, R7 |
| L4 | test-0060 | R5, R7 |

## Other ways the result could be inflated

**Serving comparability is not fully proven.** Both metas name the same Prime Inference endpoint `https://api.pinference.ai/api/v1`, same runtime, prompt token total 135,572, seed, prompt, and requested decoding. The complete meta diff contains only run id, model, price schedule and budget. Every `served_model` matches its requested name. However, the base and LoRA routes could use different weights, quantization, kernels, chat-template application or defaults; no server revision, model-weight hash, backend fingerprint or applied-decoding attestation is retained. Different price is evidence of different commercial routes, not proof of identical or different numerics. Attribution of the entire gain to the adapter rather than a serving-route confound is therefore **conditional and unverified**. Sources: [extended results](scratch/run1-extended.json), `metadata_differences`; original metas and row.served_model; runner lines 264-291.

Recorded prices per million input/output tokens are $0.18/$0.54 base and $0.10/$0.20 adapter. Computed spends are $0.0733923 and $0.0464340, totaling $0.1198263. Summed rounded `usage.cost` fields instead give $0.0764 and $0.0473. The published dollar figures use the runner's configured prices, not an audited billing statement. This cost discrepancy affects the cost claim, not scores. Sources: [mechanical results](scratch/run1-mechanical.json), `computed_cost`, `usage_reported_cost`, meta.price_per_mtok; original rows.cost_source=`computed`.

**Windows trust boundary is weaker than the generic project description.** Both original evaluations and rescoring use `reuse`: code and measurement share a persistent worker, with no state isolation or environment scrubbing. A BREP round-trip alone would not stop malicious code patching measurement state in that mode. Here no such constructs were found, reverse-order rescoring agrees, and independent BREP inspection in the parent confirms the passed geometry. This narrows the concern for these files, but future adversarial audits should use a Linux fork/container boundary. Sources: original meta.sandbox; [SECURITY.md](../SECURITY.md), execution-modes table; [measure.py](../environments/cad_spec/cad_spec/measure.py), lines 937-982, 1071-1091; hygiene and geometry results.

**Statistical strength has a limited scope.** The registered bootstrap samples 60 specs, carrying L2 and L4 together, so it correctly treats the 120 primary pairs as 60 clusters. There are 48 improved pairs spread over 41 specs, seven improved on both tiers and 34 on one; none worsen. An auxiliary sharp-null per-spec sign-flip test gives one-sided `2^-41 = 4.55e-13`, under independent label-exchangeability assumptions. This is evidence against no saved-output difference on these specs, not a replication across training runs or evidence eliminating serving confounds. Sources: [compare_training.py](../scripts/compare_training.py), `paired`; [extended results](scratch/run1-extended.json), primary cluster fields and sign-flip assumption.

At the adapter ceiling, every bootstrap draw inherits zero observed adapter failures; the percentile interval cannot capture unseen adapter failures or training-seed variation. Under an additional iid-spec binomial assumption, 60/60 successes have a two-sided exact 95% lower bound of about **94.0%**, not a demonstrated population rate of 100%. Do not use 120 independent successes for that bound, since the tiers share specs. H2 and L1/L3 are registered secondary/descriptive checks, not four independent primary discoveries; the regression rule only rules out an observed drop over ten points, not all possible regression. Sources: [extended results](scratch/run1-extended.json), `exact_binomial_lower_two_sided_95_for_60_of_60` and script formula; [compare_training.py](../scripts/compare_training.py); [registration](../docs/experiments/training-run-1.md), section 4.

**Mutation validation is finite.** The saved suite has 1,230 mutants, 0 false full credit among 600 wrong parts, 0 false rejection among 600 correct parts, and excludes 30 breakout cases from those agreement counts. It is not a universal adversarial proof. Volume-only material checks can admit some small missing/extra features, surface handling shares OpenCascade, and malicious state changes in Windows reuse are outside that geometry-only suite. The actual adapter passes have exact ideal boolean geometry and do not exploit these holes. Sources: [scorer validation](../results/scorer-validation-0.4.0.md); [validate_scorer.py](../scripts/validate_scorer.py), mutant families; [rubric.py](../environments/cad_spec/cad_spec/rubric.py), material/tolerance checks; [independent geometry](scratch/run1-geometry.json).

**Stopping and chronology remain qualifications.** There are archived step distributions 1 through 38, a stopped run with registered max_steps=104, and a config hash matching the prelaunch archived payload. Amendment 5 documents stopping at $14.5575 total spend because further batches became unaffordable, before evaluation, using only the final adapter. Cost-driven stopping is correlated with the zero-advantage filter and model behavior; it is not the same as completing a fixed 104-step run. No evidence of test-based checkpoint selection was found in the supplied artifacts, but local files alone cannot authenticate amendment timing, prove absence of undisclosed runs, or certify adapter ancestry. Sources: [extended results](scratch/run1-extended.json), `training`; [registration](../docs/experiments/training-run-1.md), Amendment 5, lines 260-295; archived run/payload.

## Limits that publication must state

State **38 completed steps out of 104**, cost-driven amended stopping, one training run, one model, fixed train/test generator seeds and one greedy evaluation seed (0), one task family, the same cheat-sheet in both arms, 60 unique test specs with 120 correlated primary tier/spec pairs, a near-ceiling adapter, and both Prime routes with their unverified backend comparability. The hosted optimizer RNG seed and effective default training hyperparameters are not established by this audit. L3 means two held-out phrasing templates. R6 checks volume consistency, not alloy or manufacturability. Overall adapter all-pass is 239/240, so **100% applies only to the primary L2+L4 slice**, not every tier. Sources: registration, metas, archived run fields; reproduced verdict; [tasks.py](../environments/cad_spec/cad_spec/tasks.py), prose templates; [rubric.py](../environments/cad_spec/cad_spec/rubric.py), material definition.

Proposed claim:

> In one Qwen3.5-9B LoRA RL run stopped on cost after 38 of 104 planned steps, saved greedy Prime Inference outputs with the same CadQuery cheat-sheet improved all-requirements pass rate on the locked 60-spec mounting-plate test split from 60% to 100% across L2 and L4, a paired gain of 40 points (registered spec-cluster bootstrap 95% interval: 32.5 to 47.5). Offline rescoring and independent BREP geometry checks reproduced the result; generalization beyond this generator and equivalence of the base and adapter serving backends remain unverified.

Source for the proposed claim: reproduced verdict, both rescore files, geometry results, registration Amendment 5, and serving metadata limits above.

## What would falsify the broader interpretation

No follow-up inference or training was performed. Costs below are **rough hypothetical estimates**, derived from the recorded $0.1198263 for 480 paired responses and archived training spend, not current provider quotes or authorization to spend. A failed preregistered replication, route-matched disappearance of the gain, or failure on an independent generator would narrow or falsify the corresponding broader claim, even though the saved-file arithmetic remains true.

| Cheapest next experiment | Falsifier or narrowing result | Rough incremental cost and source |
|---|---|---|
| Retrieve backend/weight/template attestations for these two route ids | Different base weights or decoding explain the comparison | $0 if existing logs/support can supply them; availability unverified |
| New disjoint 60-spec seed, same frozen adapter and settings, one prespecified paired run | Large loss of the registered gain or adapter reliability | About $0.12 for 480 responses at observed lengths/prices; computed totals above |
| Twenty new ECO specs with reordered wording, two-step changes and distracting rev A pitch | Adapter repeats stale pitch or loses advantage | About $0.01 for 40 paired responses by proportional extrapolation; token lengths may change |
| Independent plate generator, varied non-grid dimensions, origin conventions explicitly controlled | Gain depends on half-mm grid or one implementation's templates | About $0.12 per 60-spec, four-tier paired set, plus local oracle development; price extrapolation |
| Match base/adapter serving engines, weights, precision and template, with a new test set | Gain disappears when routes are controlled | Local inference can be $0 in API fees if suitable hardware is already available; hardware availability unverified |
| A second independently seeded training run, new locked final set, no checkpoint selection | Similar training fails to produce a reliable gain | Observed run $13.87 plus smoke $0.69 and evaluation about $0.12, roughly $15; rising batch costs mean this is not a guaranteed budget. Registration Amendment 5 supplies historical spend |
| New part families such as brackets/disks, with an independent oracle and preregistered checks | Improvement does not transfer | Inference order $0.10-$0.50 for a few hundred outputs is a hypothesis from current artifact token costs; oracle/scorer engineering time unestimated |

A new inference run at temperature 0 is a useful serving-determinism test but would be a new experiment, not a repeat chosen to replace this registered result. The already-used locked split should not become a checkpoint-selection set. Source: registration section 6.4 and evaluation protocol sections 1, 5.

## Open questions and the cheapest way to settle them

| Unverified question | Cheapest resolution |
|---|---|
| Are the base and adapter routes numerically comparable, and were thinking/temperature applied? | Existing request/response logs plus server revision, weight lineage, chat-template and decoding attestations; $0 if already retained |
| Can the complete hosted rollout history rule out external test exposure? | Inspect a full prompt-id/archive and dataset fingerprints from the service; local dataset checks already pass, but the complete history is absent |
| Was only this final adapter ever evaluated, and were amendments truly recorded before results? | External timestamped registration/history plus adapter deployment/evaluation ledger; local file contents alone do not prove negative history |
| Does the result reproduce across training seeds? | One fresh preregistered training run, controlled seed and backend, cost estimate above |
| Is a reusable plate recipe all that improved, or is there useful transfer? | A frozen new generator and then independently scored new families; avoid interpreting code comments as thoughts |
| Are scores robust to OS/kernel changes and malicious state persistence? | Free local Linux fork/container replay of these saved answers with pinned versions and reversed order; no additional inference needed. This Windows-only audit did not perform it |
| Does binary reward specifically explain the gain? | Matched continuous k/9 training ablation with equal budget/seeds, as required by evaluation protocol section 5; not identifiable from this single run |
| Are the cost figures actual charged amounts for evaluation? | Compare retained billing usage against configured-price estimates and rounded response costs; score conclusions do not depend on it |

These questions are hypotheses or missing provenance, not discovered leakage or reward hacks. The supported finding is that the registered saved-output gain is numerically reproducible and its passing adapter parts are geometrically correct for the requested test specs.
