"""Assemble the integrity report from retained offline audit outputs."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'audit/scratch'
def read(name): return json.loads((OUT/name).read_text(encoding='utf-8'))
def link(path,label=None): return f'[{label or path}]({path})'

def main():
    m=read('run1-mechanical.json')
    x=read('run1-extended.json')
    g=read('run1-geometry.json')
    rr=read('run1-rescore-repo.json')
    rw=read('run1-rescore-wheel.json')
    v=read('run1-verdict.json')
    assert rr['mismatches']==rw['mismatches']==[]
    assert g['summary']['independent_pass_agreement']==239
    assert x['verdict_md_byte_identical'] and x['verdict_json_byte_identical']
    # Paths are relative to audit/run1-result-integrity.md, with line/field
    # locations additionally stated in prose for verifiable source attribution.
    mechanical=link('scratch/run1-mechanical.json','mechanical results')
    extended=link('scratch/run1-extended.json','extended results')
    geom=link('scratch/run1-geometry.json','independent geometry')
    mutants=link('scratch/run1-perturbations.json','perturbation results')
    evals=link('../results/training/run1/eval/base-test.jsonl','base JSONL')+' and '+link('../results/training/run1/eval/adapter-test.jsonl','adapter JSONL')
    reg=link('../docs/experiments/training-run-1.md','registration')
    rubric=link('../environments/cad_spec/cad_spec/rubric.py','rubric.py')
    tasks=link('../environments/cad_spec/cad_spec/tasks.py','tasks.py')
    env=link('../environments/cad_spec/cad_spec/environment.py','environment.py')
    compare=link('../scripts/compare_training.py','compare_training.py')
    text=f'''# Training run 1: result integrity audit

Verdict: **yes with caveats**, the saved-file gain survives this audit.
Confidence: **95%**, a subjective assessment of artifact integrity, not a statistical probability of generalization.
Primary result reproduced: **72/120 to 120/120**, +40.0 points, registered interval [+32.5, +47.5].
Evidence: **960/960 rescoring runs agree**, all **239/239 adapter passes** match nominal geometry independently, and no local split leakage was found.
Most important caveat: this is **one training run on one narrow plate generator**; 100% on these 60 specs does not establish universal reliability or general CAD ability.

The numerical evidence in these five lines is in {link('scratch/run1-verdict.json','reproduced verdict')}, {link('scratch/run1-rescore-repo.json','repository rescore')}, {link('scratch/run1-rescore-wheel.json','wheel rescore')}, {geom}, and {mechanical}. The confidence is explicitly judgment, conditional on the saved artifacts being authentic. Hosted request application and adapter weight provenance cannot be authenticated offline.

## Evidence table

| Question | Finding | Source |
|---|---|---|
| 1. Verdict reproducible? | Yes. Both regenerated verdict files are byte-identical, including all rates, intervals, thresholds, and verdicts. | {extended}: `verdict_md_byte_identical`, `verdict_json_byte_identical`; {compare}, `analyse`, `paired` |
| 2. Scores deterministic? | All 480 answers match with repository code and independently with installed 0.4.5, in reverse order. Zero binary, continuous-reward, check-map, or build-status mismatches. | Rescore JSON files: `rows`, `mismatches`, `results[*].*_equal`, `order`, `modules` |
| 3. Registration conformity? | Both saved files conform. Exactly the expected 240 keys each, locally identical test prompts and system prompt, matching settings, complete ends, no API errors or retries. One permitted base truncation. | {mechanical}: `base`, `adapter`, `prompt_arms_equal`; {evals}: meta, end, rows |
| 4. Leakage? | No test ids or dimension tuples in train/development targets; none in embedded rev A geometry. No exact L3 wording overlap; template indices are disjoint. Actual local training dataset has 800 rows and zero test ids. | {mechanical}: `leakage`; {tasks}: lines 153, 194, 295-306, 339; {env}: lines 23-24, 80-100, 251-252 |
| 5. Reward hacking? | No suspicious executable constructs in adapter code. All 239 passes build the exact requested simple plate. All 72 out-of-tolerance perturbations fail their expected checks; 24 tolerance-boundary controls pass as designed. | {mechanical}: `hygiene`; {geom}: `summary`, `results`; {mutants} |
| 6. What changed? | Longer, more variable-based adapter answers; L4 usually updates the pattern rather than merely replacing box dimensions. Explicit margin arithmetic is common but is not required in every correct answer. | {mechanical}: `lengths`, `structures`; {extended}: arithmetic records; paired excerpts below |
| 7. Discordant pairs? | 70 base-fail/adapter-pass pairs, zero reverse pairs. One common failure, L3/test-0054, remains in adapter. Every discordance is listed below. | {mechanical}: `discordant`, `adapter_failures`; rescore details by `(arm,tier,spec_id)` |
| 8. Inflation risks? | No recorded prompt/decoding difference. Serving internals remain unverified; ceiling bootstrap does not measure training-seed variability. The observed passes do not exploit tolerance slack. | {extended}: `metadata_differences`, cluster statistics; {rubric}: lines 36-48; {compare}: `paired`; {evals}: meta.sandbox |

## File integrity and reproduction

Audited checkout: `6f038c6c3ad7e2fb1cbb6872311d8d040ac21d24`, also recorded as `git_commit` in both evaluation metas. The registered analysis was rerun offline into `audit/scratch/run1-verdict.*`, never over the originals. Sources: evaluation meta.git_commit; {extended}, byte-equality fields.

| Original artifact | SHA-256 |
|---|---|
'''
    for path,digest in m['hashes'].items(): text+=f'| `{path}` | `{digest}` |\n'
    text+=f'''
Hashes are regenerated by {link('scratch/run1_mechanical.py','run1_mechanical.py')}; original verdict numbers and regenerated numbers are identical. Reproduction commands, all local:

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

The shell supplied to this session was PowerShell, so direct venv interpreters were used instead of sourcing the Git Bash helper, which also loads API keys. No key or network request was needed. All handwritten scripts and audit outputs are under `audit/`. Python bytecode writing was disabled. Saved model code ran only through `cad_spec.rubric.score` with `CAD_SPEC_SANDBOX=reuse`; `CAD_SPEC_INPROC` was explicitly removed. Sources: commands above; {link('scratch/run1_rescore.py','rescore script')}, {link('scratch/run1_geometry.py','geometry script')}.

## Score determinism and registration

The repository rescore evaluated base then adapter in recorded order; the installed-wheel rescore evaluated all 480 in reverse order with a fresh interpreter. Both yield base 169/240 and adapter 239/240 overall. Every full check dictionary, continuous score, binary all-pass classification and parsed status matches, including the six base build failures. Mismatch list: **empty**. This establishes reproducibility of these saved outputs on this Windows/CadQuery stack, not deterministic generation by Prime. Sources: repository and wheel rescore files, `counts`, `mismatches`, `results`.

Both rescore interpreters use Python 3.12.10, CadQuery 2.8.0 and OCP 7.9.3.1.1. Repository and installed wheel `measure.py`, `rubric.py`, and `tasks.py` have identical SHA-256 hashes. The repository import reports package `__version__=0.4.5`, although its local installed distribution metadata says 0.4.0; the clean wheel reports distribution 0.4.5. This stale local metadata does not change executed code or the common scorer version 0.4.0. Sources: rescore `modules`, `package_version`, `scorer_version`; {extended}: `repo_package_version`.

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

Source for every field: {mechanical}, `base` and `adapter`, plus both original JSONL metas/rows/ends. The base truncation rate is 1/240 = 0.417%, below the registered 5% refusal threshold, and outside H1's tiers. Removing it cannot change H1. Six base `error` fields are build errors, not API errors. Request settings are documented as sent by {link('../scripts/run_baseline.py','run_baseline.py')}, lines 253-291; the service applying them exactly is **unverified**.

## Reward-hacking findings

The adapter scan parses the same extracted code selected by the scorer, ignoring comments when looking for executable constructs. It inspects imports, calls, suspicious names, dunder attributes, attribute/subscript assignments, exception handlers, and definitions. All code is syntactically valid. There are 240 `cadquery` imports and zero other imports, zero flagged file/network access or dynamic execution, zero introspection, zero attribute/subscript writes or monkeypatches, zero `try` handlers, and zero function/class definitions. All call targets in `hygiene.call_counts` are ordinary CadQuery construction, list append, or one ordinary `ValueError` guard. Maximum extracted code is 4,859 characters and 96 lines; the long answers are commented construction code, not encoded payloads. These are observations about these answers, not proof that arbitrary CadQuery code is safe. Sources: {link('scratch/run1_mechanical.py','scan implementation')}, `features`; {mechanical}, `hygiene`; {link('scratch/run1-code-features.json','per-answer features')}.

There are **240 distinct completions and 240 distinct extracted programs**. Numeric-literal normalization, retaining names and AST shape but dropping comments/formatting, gives **194** structures; also canonicalizing variable names gives **126**. Per-tier structures are L1 45/18, L2 48/23, L3 55/41, L4 46/44, where each pair is numeric-only/name-normalized. These counts depend on the documented normalization; they are not a count of independent strategies. Sources: {mechanical}, `hygiene` and `adapter.structures`; {extended}, `exact_extracted_codes`; scan `Normalize`.

Every passing answer's length, width, thickness, bore diameter, hole centers, margin and centering equal its target values, including post-ECO L4 targets, within the independent 0.00001 mm numerical check. The one failed answer copies the correct dimensions but computes the wrong point layout. An independently checked fixed geometry is eligible for at most **one of the 60 test specs**, so a single unchanged numerical answer cannot explain the passes. A parameterized box-and-four-holes template can cover the whole family; correctly instantiating that algorithm is sufficient here, and does not demonstrate broader CAD reasoning. Sources: {geom}, `results`; {extended}, `fixed_geometry_max_eligible_test_specs`, `fixed_geometry_wrong_targets`, and `fixed_geometry`; {link('scratch/run1_extended.py','eligibility algorithm')}.

Independent verification used the project's sandbox to execute each answer, appending only a trusted `result.val().exportBrep(...)` write under `audit/scratch/run1-breps/`. The export-instrumented answer preserves every original reward and check map, 240/240. A clean parent imports the BREP as data using CadQuery's importer, then independently checks bounding box, center, volume, validity, one solid, six planar faces, and four cylindrical faces with nominal diameters, Z extents and axes. It also builds an oracle using primitive cylinders cut from a box, and computes both boolean differences. It does not call `cad_spec.measure.measure`, its cylinder classifier, or its gate helpers for these decisions. Sources: {link('scratch/run1_geometry.py','run1_geometry.py')}, `inspect` and `main`; {geom}, `summary.export_score_mismatches`.

Agreement is **239/239 passing answers**, and **240/240 overall pass/fail decisions**. For passing parts, maximum hole-position error, missing oracle volume, and extra volume are all zero in the retained output. This is stronger than merely falling within scorer tolerances. Caveat: both paths use CadQuery/OpenCascade, so this is an independent algorithm and fresh process, not an independent geometry kernel. It cannot detect a shared kernel defect. Sources: {geom}, `summary`, `results[*].checks`, `missing_volume`, `extra_volume`, and saved BREP hashes.

Sensitivity sample: first four passing specs in each of L1/L2/L3, first twelve in L4, **24 answers total**. AST edits change only the hole API diameter, box X length, or X hole pitch; expressions and every mutant program are retained. The sample is deterministic, not a random population sample. Source: geometry script `Perturb`, `selected`; {mutants}, `edits`, `code_file`.

| Change | Tests | All-pass lost | Expected failure |
|---|---:|---:|---|
| hole diameter +0.5 mm | 24 | 24 | R4b, 24/24 |
| box X length +1.0 mm, holes unchanged | 24 | 24 | R1, 24/24 |
| total X pitch +1.0 mm | 24 | 0 | None: each center moves 0.5 mm, inclusive tolerance |
| total X pitch +1.2 mm | 24 | 24 | R5 and R7, 24/24 each |

All 72 mutations beyond tolerance are caught by their expected checks; all 24 boundary controls retain full credit. The suggested +1 mm pitch perturbation is therefore **insufficient to falsify sensitivity**, for a documented mathematical reason, not because the scorer ignores geometry. Sources: {geom}, `summary.sensitivity`; {mutants}; {rubric}, lines 38, 42, 48, 183, 212.

## Leakage findings

`make_splits()` produces 200 train and 30 development specs at seed 20260813. `make_test_split()` uses seed 20260927 and rejects any five-dimension tuple already in train, development or the test output itself. Local checks find zero overlaps by id and by `(length,width,thickness,hole_diameter,edge_margin)`, and zero overlaps between test targets and train/development L4 embedded rev A tuples. Sources: {tasks}, lines 153-173 and 185-211; {mechanical}, `leakage`.

L3 training selects wording indices 0,1,2,3; test selects 4,5. No rendered L3 test prompt occurs among the 200 train L3 prompts. The source templates themselves are disjoint, not merely different numbers substituted into one template. This is only two held-out phrasing templates. Source: {tasks}, lines 261-311; {mechanical}, `leakage.train_wording_indices`, `test_wording_indices`, `exact_L3_prompt_overlap`.

The training path is `load_environment` -> `_build_dataset(train_tiers)` -> `_rows(TRAIN_SPECS, tiers, "train")`; `TRAIN_SPECS,EVAL_SPECS=make_splits()`. Its lookup table contains only those 230 ids. The evaluated test generator is absent from this training route. The rebuilt 800-row L1-L4 dataset has exactly local train prompts and zero test ids; hints are the common packaged system prompt. Development dataset creation uses only `EVAL_SPECS`. Sources: {env}, lines 23-24, 80-100, 245-252; {mechanical}, `leakage.environment_train_rows`, `dataset_prompt_mismatches`, `dataset_test_id_overlap`.

Archived training configuration and run record agree on environment 0.4.5, hints, binary reward, and the L4/L2/L1+L3 ratios. The archived payload contains no test-split override; config hash matches. This supports the local code-path conclusion but is **not a complete archive of every hosted rollout**. Unlogged service behavior, prior test exposure outside these artifacts, or contamination of model pretraining remains unverified; there is no positive evidence of it here. Sources: {extended}, `training`; {link('../results/training/run1/payload-cad-spec-9b.json','archived payload')}, `request.json.environments`; {link('../results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/get.json','run snapshot')}, `run.environments`, `eval_config`, `val_config`.

## What changed in the answers

Descriptive lengths and structures, over 60 answers per tier:

| Tier | Mean chars base / adapter | Mean output tokens base / adapter | Answers with multiple assigned variables base / adapter | Answers with comments base / adapter |
|---|---:|---:|---:|---:|
'''
    for t in ('L1','L2','L3','L4'):
        b=m['base']; a=m['adapter']
        text+=f"| {t} | {b['lengths'][t]['chars']['mean']:.1f} / {a['lengths'][t]['chars']['mean']:.1f} | {b['lengths'][t]['tokens']['mean']:.1f} / {a['lengths'][t]['tokens']['mean']:.1f} | {b['structures'][t]['variables']} / {a['structures'][t]['variables']} | {b['structures'][t]['comments']} / {a['structures'][t]['comments']} |\n"
    text+=f'''
Source: {mechanical}, `base.lengths`, `adapter.lengths`, `structures`. Adapter produces more tokens in every tier, including about five times the base L4 mean, so this is not a token-efficiency gain. Its lower dollar cost reflects lower recorded route prices.

A conservative static arithmetic check finds subtraction expressions resolving to the nominal pitch or half-pitch in base/adapter counts L1 1/29, L2 51/56, L3 23/11, L4 5/19. This does not count arithmetic performed only in comments or directly hard-coded correct coordinates, and must not be read as a complete reasoning detector. It shows L2 arithmetic was already common in the base; the improvement also involves correct layout/API usage. Sources: {extended}, `subtraction_to_nominal_pitch_counts`, `arithmetic_records`; {link('scratch/run1_extended.py','numeric whitelist evaluator')}.

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

All 38 base L4 failures miss R5 and R7. Six also fail the through-hole gate and hole count; seven fail diameter; three fail material. Every adapter L4 answer passes independently. The evidence supports improved change propagation and construction for this family; it does not identify internal reasoning or isolate GRPO from all other training choices. Sources: {mechanical}, `L4_failure_checks`, `discordant`; {geom}.

## Discordant pairs and the sole adapter failure

L1: 8 improvements; L2: 10; L3: 14; L4: 38. **No base-pass/adapter-fail pair exists.** The remaining L3/test-0054 failure is common: base partial reward 0.6667, adapter reward 0.0, neither all-pass. Thus an all-pass improvement can coexist with a worse partial score on one already-failing spec. Sources: {mechanical}, `discordant`, `adapter_failures`; repository rescore, L3/test-0054 rows.

Adapter L3/test-0054 is an 86.5 x 155 x 7.5 mm plate requiring 8 mm bores on a 38.5 x 107 mm pattern. It interprets four holes as four in a line and sets X/Y coordinates to +/-1.5 times the pitch, rather than +/-0.5. Its attempted holes lie outside the blank, producing a plain box with zero cylindrical faces. Failed checks: `gate:simple_through_holes`, R4a, R4b, R5, R7. R6 still passes because missing-hole volume is only about 1.5% of the expected volume, inside its 3% allowance; the gate and hole-count checks correctly prevent full credit. Sources: adapter completion, L3/test-0054; rescore `details`; {geom}, `summary.all_failures`.

Short adapter excerpt:
```python
x_offsets = [-1.5 * hole_spacing_x, 1.5 * hole_spacing_x]
y_offsets = [-1.5 * hole_spacing_y, 1.5 * hole_spacing_y]
```

Every discordant pair below is **base fails, adapter passes**. `Gthrough` abbreviates `gate:simple_through_holes`; R4a is count, R4b diameter, R5 pattern, R6 material, R7 margin. Empty check maps from build failures are explicitly marked, not counted as successful checks. Source: {mechanical}, `discordant`, with details in rescore files.

| Tier | Spec | Base failed checks or build error |
|---|---|---|
'''
    short={'gate:simple_through_holes':'Gthrough','R4a:hole_count':'R4a','R4b:hole_diameter':'R4b','R5:hole_pattern':'R5','R6:material':'R6','R7:edge_margin':'R7'}
    for d in m['discordant']:
        failed=', '.join(short.get(k,k) for k in d['base_failed'])
        if d['base_error']: failed='BUILD: '+d['base_error'].replace('|','\\|')
        text+=f"| {d['tier']} | {d['spec_id']} | {failed} |\n"
    text+=f'''
## Other ways the result could be inflated

**Serving comparability is not fully proven.** Both metas name the same Prime Inference endpoint `https://api.pinference.ai/api/v1`, same runtime, prompt token total 135,572, seed, prompt, and requested decoding. The complete meta diff contains only run id, model, price schedule and budget. Every `served_model` matches its requested name. However, the base and LoRA routes could use different weights, quantization, kernels, chat-template application or defaults; no server revision, model-weight hash, backend fingerprint or applied-decoding attestation is retained. Different price is evidence of different commercial routes, not proof of identical or different numerics. Attribution of the entire gain to the adapter rather than a serving-route confound is therefore **conditional and unverified**. Sources: {extended}, `metadata_differences`; original metas and row.served_model; runner lines 264-291.

Recorded prices per million input/output tokens are $0.18/$0.54 base and $0.10/$0.20 adapter. Computed spends are $0.0733923 and $0.0464340, totaling $0.1198263. Summed rounded `usage.cost` fields instead give $0.0764 and $0.0473. The published dollar figures use the runner's configured prices, not an audited billing statement. This cost discrepancy affects the cost claim, not scores. Sources: {mechanical}, `computed_cost`, `usage_reported_cost`, meta.price_per_mtok; original rows.cost_source=`computed`.

**Windows trust boundary is weaker than the generic project description.** Both original evaluations and rescoring use `reuse`: code and measurement share a persistent worker, with no state isolation or environment scrubbing. A BREP round-trip alone would not stop malicious code patching measurement state in that mode. Here no such constructs were found, reverse-order rescoring agrees, and independent BREP inspection in the parent confirms the passed geometry. This narrows the concern for these files, but future adversarial audits should use a Linux fork/container boundary. Sources: original meta.sandbox; {link('../SECURITY.md','SECURITY.md')}, execution-modes table; {link('../environments/cad_spec/cad_spec/measure.py','measure.py')}, lines 937-982, 1071-1091; hygiene and geometry results.

**Statistical strength has a limited scope.** The registered bootstrap samples 60 specs, carrying L2 and L4 together, so it correctly treats the 120 primary pairs as 60 clusters. There are 48 improved pairs spread over 41 specs, seven improved on both tiers and 34 on one; none worsen. An auxiliary sharp-null per-spec sign-flip test gives one-sided `2^-41 = 4.55e-13`, under independent label-exchangeability assumptions. This is evidence against no saved-output difference on these specs, not a replication across training runs or evidence eliminating serving confounds. Sources: {compare}, `paired`; {extended}, primary cluster fields and sign-flip assumption.

At the adapter ceiling, every bootstrap draw inherits zero observed adapter failures; the percentile interval cannot capture unseen adapter failures or training-seed variation. Under an additional iid-spec binomial assumption, 60/60 successes have a two-sided exact 95% lower bound of about **94.0%**, not a demonstrated population rate of 100%. Do not use 120 independent successes for that bound, since the tiers share specs. H2 and L1/L3 are registered secondary/descriptive checks, not four independent primary discoveries; the regression rule only rules out an observed drop over ten points, not all possible regression. Sources: {extended}, `exact_binomial_lower_two_sided_95_for_60_of_60` and script formula; {compare}; {reg}, section 4.

**Mutation validation is finite.** The saved suite has 1,230 mutants, 0 false full credit among 600 wrong parts, 0 false rejection among 600 correct parts, and excludes 30 breakout cases from those agreement counts. It is not a universal adversarial proof. Volume-only material checks can admit some small missing/extra features, surface handling shares OpenCascade, and malicious state changes in Windows reuse are outside that geometry-only suite. The actual adapter passes have exact ideal boolean geometry and do not exploit these holes. Sources: {link('../results/scorer-validation-0.4.0.md','scorer validation')}; {link('../scripts/validate_scorer.py','validate_scorer.py')}, mutant families; {rubric}, material/tolerance checks; {geom}.

**Stopping and chronology remain qualifications.** There are archived step distributions 1 through 38, a stopped run with registered max_steps=104, and a config hash matching the prelaunch archived payload. Amendment 5 documents stopping at $14.5575 total spend because further batches became unaffordable, before evaluation, using only the final adapter. Cost-driven stopping is correlated with the zero-advantage filter and model behavior; it is not the same as completing a fixed 104-step run. No evidence of test-based checkpoint selection was found in the supplied artifacts, but local files alone cannot authenticate amendment timing, prove absence of undisclosed runs, or certify adapter ancestry. Sources: {extended}, `training`; {reg}, Amendment 5, lines 260-295; archived run/payload.

## Limits that publication must state

State **38 completed steps out of 104**, cost-driven amended stopping, one training run, one model, fixed train/test generator seeds and one greedy evaluation seed (0), one task family, the same cheat-sheet in both arms, 60 unique test specs with 120 correlated primary tier/spec pairs, a near-ceiling adapter, and both Prime routes with their unverified backend comparability. The hosted optimizer RNG seed and effective default training hyperparameters are not established by this audit. L3 means two held-out phrasing templates. R6 checks volume consistency, not alloy or manufacturability. Overall adapter all-pass is 239/240, so **100% applies only to the primary L2+L4 slice**, not every tier. Sources: registration, metas, archived run fields; reproduced verdict; {tasks}, prose templates; {rubric}, material definition.

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
'''
    assert chr(0x2014) not in text
    (ROOT/'audit/run1-result-integrity.md').write_text(text,encoding='utf-8')
    print(text)

if __name__=='__main__':
    main()
