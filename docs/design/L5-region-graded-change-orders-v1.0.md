# L5 Region-Graded Change Orders: Final Design Note v1.0

Oct 5, 2026 · @Bilal AZZOUZI

## 1. Summary and decision

L5 grades whether a model's Rev B belongs to the region of valid revisions defined by a revised engineering contract, not whether it matches one reference geometry.

**Final L5 definition.** L5 tests whether a model can propagate a change order through coupled design constraints to any compliant revision, without breaking unaffected obligations or inherited parametric intent, and whether it can reject an impossible order with a minimal, correct reason.

Three architectural commitments carry the design:

1. **The solver runs offline.** Each item is compiled once into a static grading artifact. The runtime grader only builds, measures and evaluates predicates, so the RL\* reward stays fast, deterministic and free of any Z3\* dependency.
2. **Preservation comes from conflict analysis, not hand labels.** A variable may move only if it takes part in some conflict between Rev A and Contract B (the union of all MCSs\*).
3. **Intent is inherited, not authored.** Rev A is probed through CQGI\*; whatever relations it preserves under those probes, Rev B must preserve too.

**Scope of v1:** one part family (rectangular plate, symmetric 4-hole pattern, through holes along Z), CadQuery only, reusing the cq-spec measurement kernel.

**Supersedes:** the template-based L5 draft and the proposal *L5\_Elite\_Grader\_Architecture.md*. Where this note and that proposal disagree, this note wins.

## 2. Decision log

Three review rounds produced the decisions below; each row names what it replaced and why.

| Topic | Final decision | Replaced | Why |
| --- | --- | --- | --- |
| Scoring target | Rev B must lie in the feasible region\* of Contract B | One canonical Rev B, exact match | Forcing uniqueness turned engineering judgment into tie-break arithmetic |
| Item generation | Semantic state + ECO operators + code and language renderers | Hand-written templates | One source of truth; renderers cannot change semantics |
| Frame rule | A variable may move only if it is in the union of MCSs of (Rev A values, Contract B) | "Nothing unmentioned changes", then hand-typed roles | The freeze blocked forced moves; roles duplicated solver work and missed either/or couplings |
| Design intent | Inherited from Rev A probe behavior, filtered by a sensitivity check | Hand-written intent tests | The proposal's example invariants passed hardcoded models on a centred box |
| Parameter interface | Part of Contract A; names frozen | "Behavior, not representation" | CQGI probes need named parameters to override |
| Solver placement | Offline compiler | Inside the runtime grader | Determinism, speed, no solver at reward time |
| Infeasible orders | Structured reject listing constraint IDs; set must equal an MUS\* | Free-text explanation | Supersets passed; free text needs an LLM judge |
| Misconceptions | Predicted-geometry signatures, separability checked at generation, "consistent with" sets | Exact match, confidence scores | Signatures collided; confidences had no calibration |
| Minimality | Metrics only: footprint excess and per-variable overshoot in mm | Weighted normalized edit sum | Weights were arbitrary |
| Coupling depth | Solver-derived, over a variable/constraint graph | Directional dependency chains | Geometric constraints have no direction |
| Splits | MCD\* over coupling structures, only if the compound count supports it | Hand-picked operator pairs | A few operators give a tiny, noisy split |
| Sealing | Versioned hidden seed schedule, 3 seeds, one commitment hash | Fresh random eval per run | Every model must see the same items |
| History edits | "Cancel line N of ECO-1" deferred to after L5.2 | In L5 v1 | Separate capability (document reference resolution) |

## 3. Core model

An ECO edits the engineering contract, not the geometry; CAD revisions are implementations of contracts.

### 3.1 Contract variables (v1 plate family)

| Symbol | Meaning | Unit |
| --- | --- | --- |
| L, W, T | Plate length, width, thickness | mm |
| n, D | Hole count, hole diameter | count, mm |
| mx, my | Hole axis to nearest outer side face, along X and Y | mm |
| px, py | Hole pitch, derived: px = L − 2·mx, py = W − 2·my | mm |

Edge distance is measured **from the hole axis to the outer face** in v1. It is written into every prompt so the definition is never a hidden convention.

### 3.2 Contract A

Every constraint carries a stable ID. The prompt prints these IDs so that infeasible items can be answered by reference.

```yaml
contract: A
parameters: [length, width, thickness, hole_d, margin_x, margin_y]
constraints:
  C1: {expr: "L == 100"}
  C2: {expr: "W == 80"}
  C3: {expr: "T == 4"}
  C4: {expr: "n == 4"}
  C5: {expr: "D == 10"}
  C6: {expr: "symmetric(holes, plate_center)"}
```

### 3.3 Typed ECO diff

Five operators, each with a fixed meaning:

- `set`: replace a constraint's value (`C5: D == 14`).
- `require`: add a new constraint with a new ID.
- `relax`: loosen or remove an existing constraint.
- `freeze`: turn a derived quantity into a hard equality at its Rev A value.
- `release`: remove a freeze.

```yaml
eco: ECO-0147
set:     {C5: "D == 14"}
require: {C7: "min(mx, my) >= 2 * D"}
```

### 3.4 Contract B and the feasible region

Contract B is the diff applied to Contract A. The feasible region is every assignment of contract variables that satisfies it:

```latex
R_B = \{\, x \mid C_B(x) \,\}, \qquad \text{pass} \iff x(M_{\text{model}}) \in R_B \land \text{preservation} \land \text{intent}
```

For ECO-0147, any mx and my of at least 28 mm pass, provided the holes still fit inside the plate. An empty region marks an infeasible item (section 6).

### 3.5 Parameter interface

The `parameters` list in Contract A is part of the contract. Rev B must expose the same top-level names, each overridable through CQGI. Renaming or removing one fails the interface gate. A Rev A renderer with hardcoded coordinates exposes fewer parameters, so its interface, and the intent it can pass on, is smaller.

## 4. Offline item compiler

All solver work happens once per item, at generation time; its output is a static JSON grading artifact that the runtime grader reads.

### 4.1 Compile steps

1. **Sample and render Rev A.** Draw a semantic state, emit it through one code renderer, build it, and confirm it passes Contract A.
2. **Apply the ECO** to get Contract B.
3. **Encode for Z3.** Contract B constraints are hard assertions over exact rationals. Each Rev A value becomes a tracked soft equality, such as `mx == 20`.
4. **Check satisfiability.**
   - SAT: store a witness (the minimal-edit solution from Z3 Optimize), then enumerate all MCSs and MUSs with MARCO\*.
   - UNSAT on the hard constraints alone: the item is infeasible. Enumerate the MUSs over constraint IDs and build its near-twin (section 6).
5. **Derive the frame sets** from the MCS enumeration:
   - `allowed_to_move` = union of all MCSs, meaning every variable that takes part in some conflict.
   - `forced` = variables present in every MCS, meaning the variable cannot keep its Rev A value.
6. **Derive intent** by probing Rev A (section 5.4) and filtering with the sensitivity check.
7. **Compute diagnostics:** coupling depth, minimal footprint, per-variable minimal change, and misconception predictions with the separability check (section 8).
8. **Run the validation checklist** (section 10). Any failure discards and regenerates the item.

### 4.2 Why MCS, not per-variable forcing

Per-variable SAT checks miss either/or couplings. Suppose holes grow to 14 mm and a new rule requires the ligament between holes, px − D, to be at least 70 mm, with length not frozen. Pitch must grow from 70 to 84 mm, so either the plate grows or the margins shrink. Neither L nor mx is forced, yet one of them must change. MCS enumeration returns {px, L} and {px, mx}: L and mx both land in `allowed_to_move`, px lands in `forced`, and thickness never moves.

### 4.3 Compiled item schema

```json
{
  "item_id": "L5v1-000147",
  "feasible": true,
  "renderer": "named_variables",
  "interface": ["length", "width", "thickness", "hole_d", "margin_x", "margin_y"],
  "contract_b": {"C1": "L == 100", "C2": "W == 80", "C5": "D == 14", "C7": "min(mx, my) >= 2 * D"},
  "rev_a_obs": {"L": 100, "W": 80, "T": 4, "n": 4, "D": 10, "mx": 15, "my": 15, "px": 70, "py": 50},
  "allowed_to_move": ["D", "mx", "my", "px", "py"],
  "forced": ["D", "mx", "my", "px", "py"],
  "intent_probes": [
    {"driver": "length", "delta_mm": -7, "relations": ["mx_const", "C7"]},
    {"driver": "width", "delta_mm": -5, "relations": ["my_const", "C7"]}
  ],
  "accepted_mus": [],
  "misconceptions": {
    "stale_state": {"mx": 20, "my": 20},
    "ignored_rule": {"mx": 15, "my": 15}
  },
  "diagnostics": {"coupling_depth": 1, "min_footprint": 5, "min_change_mm": {"mx": 13, "my": 13}},
  "epsilon_mm": 1e-6
}
```

Values are illustrative. Note that `ignored_rule` only differs from `stale_state` when Rev A's margin sits below twice the old diameter; the separability check enforces that choice of numbers.

## 5. Runtime grader

The runtime grader is pure measurement plus predicate checks against the compiled item; a feasible task passes only if all six gates pass.

### 5.1 Gate order

| Gate | Check | Fails when |
| --- | --- | --- |
| G0 Output type | Code on feasible items, reject on infeasible ones | Model complies with an impossible order, or rejects a possible one |
| G1 Build | CQGI build in an isolated worker with a timeout; exactly one solid | Exception, timeout, zero or several solids |
| G2 Interface | Every name in `interface` exists and is overridable | A parameter was renamed, removed or hardcoded |
| G3 Compliance | Observation map, then every Contract B predicate within epsilon | Any predicate false, or geometry outside the map's scope |
| G4 Preservation | Changed set is a subset of `allowed_to_move` | The model moved something no conflict required |
| G5 Intent | Every compiled probe holds after override, rebuild and measure | A relation Rev A preserved breaks in Rev B |

Gates run in order and stop at the first failure. The report records which gate failed, which feeds the failure profile.

### 5.2 Strict pass rule

```latex
\text{PASS}_{\text{feasible}} = G_0 \land G_1 \land G_2 \land G_3 \land G_4 \land G_5
```

```latex
\text{PASS}_{\text{infeasible}} = G_0 \land (\text{named conflict} \in \text{accepted\_mus})
```

Minimality never enters pass or fail.

### 5.3 Change detection

A variable counts as changed when its measured value differs from `rev_a_obs` by more than `epsilon_mm` (1e-6 mm, matching cq-spec). Derived variables such as px are measured, not recomputed, so a model cannot hide a pitch change behind unchanged parameter names.

### 5.4 Inherited intent

Intent is derived from Rev A's behavior at compile time, so the benchmark author never writes it by hand.

1. **Probe schedule.** Each driver parameter gets deltas of −7, +3 and +11 mm. A probe is kept only if Rev A still builds a valid part under it.
2. **Relation library.** Candidate relations are `mx_const`, `my_const`, `px_const`, `py_const`, `centered`, `symmetric`, `D_const` and `n_const`, plus every Contract B constraint.
3. **Inheritance.** A relation is inherited if Rev A preserves it under every kept probe of that driver. The ECO can override one explicitly; for example, `freeze px` replaces an inherited `mx_const`.
4. **Sensitivity filter.** A (driver, delta, relation) triple is kept only if a **hardcoded witness** violates it. The hardcoded witness is the valid witness with every position baked in as a literal. This removes probes that pass for any model, such as symmetry on a centred box.
5. **Witness check.** The parametric witness must pass every kept triple, which proves the test is fair.

Shrink probes usually do the discriminating work: holes fixed at x = ±22 still pass when the plate grows, but fail when it shrinks. Items where no triple survives are tagged `intent_free` and reported separately, never silently counted as intent passes.

## 6. Infeasible items

About 10% of eval items are infeasible; each is answered with a structured reject that names a minimal conflicting set of constraint IDs.

### 6.1 Reject format

```json
{"verdict": "reject", "conflict": ["C2", "C5", "C7"]}
```

The IDs are the ones printed in the prompt's Contract B. No free-text explanation is graded, so no LLM judge is needed.

### 6.2 Grading

The compiler enumerates every MUS of Contract B and stores them in `accepted_mus`. At runtime the named set passes only if it **equals** one of them, which is a plain set lookup.

- Naming every constraint is a conflict but not a minimal one, so it fails.
- Naming two constraints that are jointly satisfiable fails.
- Any one of several valid MUSs passes.
- A correct reject with a non-minimal set is logged as `over_blamed` in diagnostics.

### 6.3 Example

Plate frozen at 100 × 70 mm (C1, C2), holes set to 30 mm (C5), edge distance at least 2·D = 60 mm (C7). The 70 mm width allows at most 35 mm from hole axis to side face, and the 100 mm length at most 50 mm. So {C2, C5, C7} and {C1, C5, C7} are both MUSs, and either one passes. Hole count and symmetry take no part in any conflict, so naming them fails.

Family geometry rules, such as holes inside the material and no overlapping holes, also carry IDs (F1, F2) so they can appear in an MUS. Without them, some conflicts would have no nameable cause.

### 6.4 Near-twins

Every infeasible item has a feasible twin with the same text and one number changed, so the region is non-empty with 0.5 mm of slack. The twin enters the feasible pool. An always-reject policy therefore scores at most the infeasible share, about 10%, and an always-comply policy scores zero on infeasible items.

## 7. Observation map

The observation map turns a measured B-rep\* into contract variables, and it is the most likely place for the grader to be wrong. It is specified explicitly and tested adversarially before any model is evaluated.

### 7.1 v1 measurement rules

| Variable | Measured as |
| --- | --- |
| L, W, T | Axis-aligned bounding box of the single solid |
| Holes | Cylindrical faces, axis parallel to Z, running through the full thickness |
| D, n | 2 × cylinder radius; number of distinct hole axes |
| Hole centre | Intersection of the hole axis with the top face plane |
| mx, my | Minimum perpendicular distance from any hole axis to the outer side planes, per axis |
| px, py | Distance between hole axes along X and along Y |
| centered, symmetric | Hole-centre centroid on the bounding-box centre, and the pattern mirror-symmetric about both mid-planes, within epsilon |

**Scope rule.** Geometry the map cannot measure unambiguously fails G3 with reason `out_of_scope`. It is never measured approximately. The grader prefers a loud refusal to a silent wrong number.

### 7.2 Adversarial suite

Each case is a hand-built model with a known expected outcome. The suite runs in CI\* on every change to the map.

| Case | Expected outcome |
| --- | --- |
| Plate translated off the origin | Measured correctly |
| Plate rotated 90° about Z | L and W are read along X and Y, so they swap and fail G3, by design |
| Fillets on the four vertical edges | Measured correctly; bounding box unchanged |
| Chamfers on top edges | Measured correctly |
| Counterbored holes (two coaxial cylinders) | `out_of_scope` in v1 |
| Blind holes | Not counted as holes; fails n |
| Faceted holes (polygon cut) | Not counted as holes; fails n |
| Extra pocket or slot | `out_of_scope` |
| Two solids, or an unfused tool body | Fails G1 |
| Holes tilted off Z | `out_of_scope` |

## 8. Diagnostics

Diagnostics explain failures and grade judgment, but none of them changes pass or fail.

### 8.1 Misconception signatures

Each misconception is a function that predicts the observation vector a model holding it would produce. The library is reused across all items.

| ID | What the model got wrong |
| --- | --- |
| `stale_state` | Applied the new rule to the old value (2 × old D) |
| `ignored_rule` | Changed D but left the margins at their Rev A values |
| `radius_for_diameter` | Used a radius where a diameter was meant, or the reverse |
| `per_side_vs_total` | Applied a dimension change to each side instead of overall, or the reverse |
| `axis_vs_rim` | Measured edge distance to the hole rim instead of the axis (adds D/2) |
| `wrong_propagation` | Moved a contract-fixed variable instead of the free one |
| `hardcoded_positions` | Correct static geometry, but positions baked in as literals (caught by G5) |
| `false_reject` | Rejected a feasible order |

**Separability check (compile time).** For every pair of misconceptions that apply to an item, the predicted observation vectors must differ by at least 0.5 mm on some variable. Otherwise the item is regenerated with different numbers. For example, `stale_state` and `ignored_rule` only separate when Rev A's margin sits below twice the old diameter.

**Matching (runtime).** A failed output is labelled with every signature its observations match within 0.05 mm. The report shows the result as a set, such as "consistent with {stale\_state}", or `unexplained` when nothing matches. It never shows a confidence score.

### 8.2 Coupling depth

Build the bipartite graph\* of Contract B: variables on one side, constraints on the other. Coupling depth is the largest number of constraint hops from a directly edited variable to a forced variable. Depth 0 is a plain edit. Depth 1 is a diameter change that forces the margins. Depth 2 adds a frozen pitch that pushes the change on into the plate length.

### 8.3 Minimality metrics

- **Footprint excess** = number of changed variables − `min_footprint`. Zero means the model's changed set is itself an MCS.
- **Overshoot** per variable, in mm = |model change| − `min_change_mm`. A model that sets the margin to 30 mm where 28 mm suffices overshoots by 2.0 mm.

Both stay in native units with no cross-variable weights. They are reported as distributions, never summed into a single score.

## 9. Splits, sealing and reporting

Every model is scored on the same hidden, versioned item set and reported on four headline dimensions, never one number.

### 9.1 Splits

- **Atoms** are ECO operator types and constraint kinds (`set D`, `require edge_min`, `freeze px`, and so on).
- **Compounds** are canonical hashes of the 2-hop constraint-graph neighbourhood around each edited variable, using a Weisfeiler-Lehman\* hash.
- **Gate:** run MCD only if the generator yields at least 50 distinct compounds. Otherwise use a random split over compounds and state plainly that compositional claims wait for L6 and more part families.
- Always report the achieved atom and compound divergence, not just the method's name.

### 9.2 Sealing

```text
L5-v1 manifest
  generator_commit   git SHA
  config_sha256      hidden split config
  seed_schedule      3 seeds (hashed while sealed)
  prompts_root       Merkle root of prompts
  items_root         Merkle root of compiled items

commitment = SHA256(generator_commit || config_sha256 || seeds_sha256 || prompts_root || items_root)
```

The commitment is published before the first model is scored. When L5-v1 retires, its seeds and config are released so anyone can rebuild and check it, and L5-v2 starts with new hidden coupling structures.

### 9.3 Report format

```text
L5-v1  model: <name>  seeds: 3  items/seed: 300

Compliance      82.1 ± 1.4 %
Preservation    94.0 ± 0.8 %
Intent          71.3 ± 2.2 %   (intent_free items excluded)
Rejection       64.0 ± 5.1 %   (infeasible items only)
STRICT PASS     66.7 ± 1.9 %

By coupling depth   d0 97%   d1 78%   d2 52%
By renderer         named 74%   fluent 69%   coords 61%
Failure profile     41% stale_state, 23% axis_vs_rim, 18% hardcoded_positions, 18% other
Minimality          footprint excess median 0, overshoot p90 1.8 mm
```

The numbers above are placeholders that show the shape of a report, not results.

### 9.4 Baselines

| Baseline | Expected strict pass | What it shows |
| --- | --- | --- |
| Unchanged Rev A | 0% | Every item is non-trivial |
| Number substitution (edit only named values) | Near 0% on depth 1 and above | Coupling is required |
| Train-template parser | High on train, low on held-out compounds | The split has teeth |
| Always reject | About 10% | Near-twins work |
| Compiled oracle | 100% | The pipeline is consistent; this is not evidence of difficulty |

## 10. Per-item validation checklist

An item enters the benchmark only if every applicable check passes at compile time; any failure discards and regenerates it.

| # | Check | Proves | Applies to |
| --- | --- | --- | --- |
| V1 | Rev A builds and passes Contract A | Valid starting design | All |
| V2 | Rev A fails Contract B | Task is non-trivial | Feasible |
| V3 | Witness builds and passes G1 to G5 | At least one passing answer exists | Feasible |
| V4 | Every semantic ablation of the ECO fails Contract B | Each operation is necessary | Multi-op feasible |
| V5 | All renderers of Rev A build identical observations | Code form does not change meaning | All |
| V6 | Hardcoded witness fails G5 on at least one kept probe | Intent test has teeth | Feasible, unless `intent_free` |
| V7 | Every applicable misconception fails Contract B | Item discriminates known errors | All |
| V8 | Misconception predictions are pairwise ≥ 0.5 mm apart | Diagnosis is identifiable | All |
| V9 | Contract B is UNSAT and `accepted_mus` is non-empty | Reject is fair and gradeable | Infeasible |
| V10 | Near-twin has a witness with ≥ 0.5 mm slack | Always-reject is punished | Infeasible |
| V11 | Every observation of witness and misconceptions is inside the map's scope | The grader can measure the answer | All |
| V12 | English rendering comes from a human-approved template family | No reading permits a misconception | All |

## 11. Build order

L5 v1 ships in five milestones; each ends at a gate that must pass before the next one starts.

&#91;embedded content: L5 v1 build order · 5 milestones, each closed by a gate\]

M1 reuses the cq-spec measurement kernel, so the observation map and the cq-spec checker stay one code base. L5.2 (sequential and non-commuting ECOs) and L6 (new part families) start only after the L5-v1 commitment is published.

## 12. Open questions and risks

Each item below carries a default, so building can start now; tick it once confirmed or changed.

- [ ] **Training reward shape.** Default: the same strict binary as eval, with difficulty ramped by coupling depth instead of partial credit. Partial credit per gate invites reward hacking on the easy gates.
- [ ] **Leniency of G4.** The union-of-MCS rule lets a model move both L and mx when one would do; that shows up only as footprint excess. Default: keep G4 lenient, since tightening it to "changed set is an MCS" would fail engineers who make a defensible larger edit.
- [ ] **Probe schedule.** Default: absolute deltas of −7, +3 and +11 mm. Small plates may need deltas relative to size, as a percentage, so shrink probes don't break Rev A itself.
- [ ] **Observation map scope.** Counterbores and pockets are `out_of_scope` in v1. If models add them often, the out-of-scope rate becomes a headline number of its own.
- [ ] **Human audit budget.** Default: about 10 English template families at roughly 20 minutes each. More families raise surface diversity and audit cost together.
- [ ] **MCD feasibility.** One part family may give fewer than 50 compounds. If so, v1 makes no compositional claim (section 9.1).
- [ ] **Exact arithmetic.** The compiler uses exact rationals in Z3, and tolerance is applied only at measurement. Mixing floats into the compiler would make MUS and MCS results flaky near boundaries.
- [ ] **Hole axis assumption.** The current cq-spec hole detector assumes holes along Z. That is fine for v1 but blocks L6 families until it is generalized.

## 13. Glossary

Terms marked with \* in the text.

| Term | Meaning |
| --- | --- |
| B-rep | Boundary representation: how CAD kernels store a solid, as faces, edges and vertices |
| Bipartite graph | A graph with two kinds of nodes, here variables and constraints, where edges only join one kind to the other |
| CI | Continuous integration: tests that run automatically on every code change |
| CQGI | CadQuery Gateway Interface: lets external code override a script's top-level parameters and rebuild the model |
| Feasible region | The set of every design that satisfies all constraints of a contract |
| MARCO | A standard algorithm that enumerates all MUSs and MCSs of a constraint system |
| MCD | Maximum Compound Divergence: a split method from the CFQ benchmark that keeps building blocks familiar while making their combinations new |
| MCS | Minimal correction set: a smallest set of constraints whose removal makes the rest satisfiable; here, a minimal set of Rev A values that must change |
| MUS | Minimal unsatisfiable subset: constraints that cannot all hold, where dropping any one makes them satisfiable |
| RL | Reinforcement learning: training a model from a reward signal, here the grader's pass or fail |
| Weisfeiler-Lehman hash | A fast way to give structurally identical graphs the same fingerprint |
| Z3 | Microsoft's open-source SMT solver, used here to check satisfiability and enumerate conflicts |
