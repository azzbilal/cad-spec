# Evaluation protocol

What must be true before a number from cad-spec goes into a README, a post,
or a CV. Written against scorer 0.4.0.

## 1. Freeze before training

- Scorer: `SCORER_VERSION` in `rubric.py`. Any change that can move a score
  bumps it. Numbers from different versions are never compared.
- Splits: `make_splits(SAMPLE_SEED)`; 200 train / 30 eval per tier. Eval specs
  are disjoint numeric tuples; L3 eval wordings never occur in train
  (tested in `test_l3_eval_wording_never_appears_in_train`).
- Dependencies: `constraints.txt`. Record its git revision with the run
  (`run_baseline.py` records the revision automatically).

## 2. Calibrate the scorer first

`python scripts/validate_scorer.py` must report 0 false full credit and 0
false rejection outside the `known_limitation` family. CI enforces this on 10
specs; run all 30 before publishing. When adding a requirement, add mutants on
both sides of its tolerance and a benign variant that must keep full credit.

Disputed mutants (oracle and scorer disagree, and it is not obvious which is
right) go to a second reviewer with mechanical design experience before the
expected result is fixed.

## 3. Always run the deterministic baselines

```bash
for p in reference parser-copy parser-derive parser-template; do
  python scripts/run_baseline.py --provider $p --tiers L0 L1 L2 L3 L4; done
python scripts/run_baseline.py --provider rev-a --tiers L4
```

A model result on a tier is only interesting where these fail. A model scoring
100% on L0 has matched a regex; on L3, `parser-template` shows how far a
template-aware shortcut goes.

## 4. Model baselines

- At least two models, identical decoding settings, same system prompt
  (recorded in each run's `meta`).
- Temperature 0 for a point estimate; temperature > 0 with at least 3 rollouts
  per spec (seeds `seed`, `seed+1`, ...) for spread.
- Report per tier, never pooled: all-requirements pass rate and mean reward
  with 95% bootstrap intervals over specs, median reward, build rate, gate hit
  rate, timeouts, API errors, and every per-check pass rate
  (`summarize_results.py` produces all of these).
- For L4, lead with all-requirements pass rate: returning rev A unchanged
  already earns about 0.75 mean reward.
- Keep the JSONL files; they hold the completions for failure analysis and
  let `scripts/rescore.py` replay them under any later scorer at no cost.
- Only complete runs count. The summary flags a run with fewer rows than
  planned, no end record, a non-complete status or duplicates; the eval
  split is ordered by plate size, so a partial run is a biased sample.
- "All-pass" is pass@1: the share of rollouts meeting every requirement. It
  is not pass@k.
- Compare models on the same specs and seeds (paired). With many models on
  one board, state that differences inside overlapping intervals are not
  rankings, and name the comparisons you planned before looking.

## 5. Training claim

- Train only on train-split prompts. Choose tiers where the base model has
  spread (roughly 10% to 80% all-pass); outside that there is no gradient or
  nothing to learn.
- Evaluate the base model and the trained adapter on the frozen eval split,
  all tiers, same decoding, same seeds.
- A gain is claimed only if the intervals do not overlap on the tier trained
  on, and the other tiers are reported alongside (regressions included).
- Ablation for any new reward design: the equal-weight k/8 reward is the
  comparator.

## 6. What the numbers may be called

| Evidence | Allowed wording |
|---|---|
| L0/L1 gains | "improves template completion / CadQuery writing for this plate family" |
| L2 gains | "... including deriving a dimension from a stated margin" |
| L3 gains on held-out wording | "... from paraphrased requirements not seen in training" |
| L4 all-pass gains | "... applying engineering change orders" |
| Any of the above | never "generalises to CAD", never "manufacturable": one part family, volume-only material check |
