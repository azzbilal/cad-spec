# A7 addendum: full reading of saved adapter answers

**Scope (fact, high confidence).** At commit 35039b8, I first reproduced the four draws with random.Random(20261004), sampling six IDs sequentially for L1, L2, L3, L4. Sorting each draw matches every supplied list ([seed check](C:/Users/bgare/cad-spec-audit-out/scratch/a7-sample-confirmation.json:1)). I read all 28 authorized adapter answers and six base contrasts in full. This is descriptive review only: no selection or tuning, no paid calls, no tracked-file changes.

## 1. Task solving or scorer exploitation?

**Fact, high.** All 24 randomly sampled adapter programs construct nominal plates: local Boolean comparison against independently constructed box-minus-four-cylinder targets gives zero symmetric-difference volume. All 34 reviewed answers retain their recorded rewards on replay ([task-by-task evidence](C:/Users/bgare/cad-spec-audit-out/scratch/a7-verification.json:1)). Coverage: L1 rep-{0004,0012,0018,0020,0026,0049}; L2 rep-{0013,0034,0043,0046,0048,0053}; L3 rep-{0009,0010,0024,0026,0031,0039}; L4 IDs below.

**Fact, high.** The special **L1 rep-0038** passes without the exact requested geometry. It asserts centers “(+/- 55.25, +/- 28.75)” and hard-codes them, although 160.5/2 - 24.5 = **55.75**. All four X-coordinate magnitudes are 0.5 mm too small. The inclusive tolerance accepts this; it is not a hidden feature or execution bypass ([answer](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-special.txt:279)).

**Inference, medium.** The reviewed text supports ordinary construction plus an arithmetic mistake, not deliberate reward exploitation. None of the 28 adapter answers accesses the scorer, forges measurements, or avoids ordinary CadQuery construction. This observation cannot establish intent or exclude exploitation outside this sample.

## 2. What changes relative to the base?

**Fact, high.** In L4 **rep-0007,0014,0016,0018,0060**, the base updates directly specified literals but retains the old hole rectangle, failing pattern and margin. The adapter derives the margin and regenerates dependent pitches. Both pass **rep-0012**, whose thickness/diameter changes leave pitch unchanged ([six base answers](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-base.txt:1)).

The adapter states the governing distinction in **rep-0007**: “the margin distance is the invariant characteristic.” In **rep-0060**, it derives new coordinates and emits rect(94.0, 71.0). Across these six answers, final pitches are literal numbers, not an executed reusable update function ([adapter answers](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-L4.txt:1)).

**Fact, high: manual arithmetic check.** I checked both axes in each answer. M is the retained or newly ordered margin; all lengths are mm. Each final code rectangle matches these calculations ([cross-check](C:/Users/bgare/cad-spec-audit-out/scratch/a7-manual-arithmetic.json:1)).

| L4 task | Margin check | Required X pitch | Required Y pitch |
|---|---|---|---|
| rep-0007 | (79-50)/2 = (110-81)/2 = 14.5 | 72-29 = 43 | 110-29 = 81 |
| rep-0012 | (147.5-127.5)/2 = (96-76)/2 = 10 | 147.5-20 = 127.5 | 96-20 = 76 |
| rep-0014 | (91.5-52.5)/2 = (109-70)/2 = 19.5 | 91.5-39 = 52.5 | 136.5-39 = 97.5 |
| rep-0016 | (135-102)/2 = (48.5-15.5)/2 = 16.5 | 169-33 = 136 | 48.5-33 = 15.5 |
| rep-0018 | (209-174)/2 = (106-71)/2 = 17.5 | 209-35 = 174 | 92-35 = 57 |
| rep-0060 | (136-104)/2 = (113-81)/2 = 16; new M=21 | 136-42 = 94 | 113-42 = 71 |

## 3. Do the comments do useful work?

**Fact, high.** They contain correct intermediate values subsequently used in code, as the six rows demonstrate. They also contain redundancy and errors. **L4 rep-0018** initially mistakes the 17.5 mm margin for the original center coordinates, then corrects itself to (87,35.5). **L3 rep-0031** writes an unused opposite-edge distance as 60.45 instead of 60.5. **L1 rep-0012** calculates X_h/Y_h but then uses literal coordinates ([L4](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-L4.txt:246), [L3](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-L3.txt:255), [L1](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-L1.txt:69)).

**Inference, medium.** These are useful worked derivations mixed with repeated checking, not merely decorative prose. Text-code agreement does not prove the comments caused success or faithfully expose internal reasoning.

## 4. Why the two L3 truncations?

**Fact, high.** **L3 rep-0014 and rep-0056** both begin with “With 4 holes, there are 3 gaps,” treating four holes as a linear array. They repeatedly investigate impossible spans, swapped axes and alternative interpretations before reaching the correct 2×2 geometry. Both end at 2,048 tokens without closing the fence or completing a drilled result ([full answers](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-special.txt:1)).

**rep-0014** reaches correct ±26.25, ±48.75 coordinates and a point list, but no result assignment. **rep-0056** reaches correct ±26.25, ±20 in comments, yet begins its unfinished point list with plate_length/2 - 52.5/2, which equals **16**, not 26.25. Thus more tokens would not automatically repair it.

The broader hesitation/rechecking pattern also appears without truncation in **L3 rep-0026** and **L4 rep-0018**. **L3 rep-0009** recognizes 2×2 promptly. The specific four-in-a-line detour is absent from the 24 random answers ([L3](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-L3.txt:1), [L4](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-L4.txt:246)).

## 5. Result-section consistency

**Fact, high.** No reviewed outcome contradicts the Result. **L4 rep-0020** explicitly keeps margin_X=16.5 while applying margin_Y=20.5, exactly the reported dependency failure ([answer](C:/Users/bgare/cad-spec-audit-out/scratch/a7-full-special.txt:220)).

**Opinion, high confidence.** Tighten [Result lines 310-314](C:/Users/bgare/dev/cad-spec-audit/docs/experiments/replication-1.md:310): both L3 answers reconsider interpretation; only rep-0056 actually starts constructing the plate again. Their failure is more than an absent closing fence: rep-0014 lacks drilling, and rep-0056 contains unfinished code plus an emerging coordinate error. This qualifies the explanation, not the score. No appended corrections were present in the inspected Result; unseen revisions were not assessed.

A7 closed
