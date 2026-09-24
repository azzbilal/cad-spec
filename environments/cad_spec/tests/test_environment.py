"""Environment-level behaviour: splits, completion flattening, reward scale."""

import random

import pytest

from cad_spec.environment import (
    EVAL_SPECS,
    PARSE_FLOOR,
    SPECS,
    TRAIN_SPECS,
    _completion_text,
    load_environment,
    spec_reward,
)
from cad_spec.rubric import score
from cad_spec.tasks import N_EVAL, N_TRAIN, SAMPLE_SEED, make_splits, reference_solution, sample_spec


class _Message:
    def __init__(self, content):
        self.content = content


def test_completion_text_variants():
    assert _completion_text("plain") == "plain"
    assert _completion_text(None) == ""
    assert _completion_text([{"content": "a"}, {"content": "b"}]) == "a\nb"
    assert _completion_text([_Message("obj")]) == "obj"
    blocks = [{"type": "text", "text": "block"}, {"type": "other"}]
    assert _completion_text([{"content": blocks}]) == "block"


def test_dataset_shapes():
    env = load_environment()
    assert len(env.dataset) == N_TRAIN == 200
    assert len(env.eval_dataset) == N_EVAL == 30


def test_splits_are_disjoint_deterministic_and_stratified():
    train_a, eval_a = make_splits()
    train_b, _ = make_splits()
    assert [(s.id, s.length) for s in train_a] == [(s.id, s.length) for s in train_b]
    assert {s.id for s in train_a}.isdisjoint({s.id for s in eval_a})
    assert len(eval_a) == N_EVAL and len(train_a) == N_TRAIN
    areas = sorted(s.length * s.width for s in eval_a)
    pool_areas = sorted(s.length * s.width for s in TRAIN_SPECS + EVAL_SPECS)
    assert areas[0] == pool_areas[0]
    assert areas[-1] == pool_areas[-1]


def test_every_spec_is_in_the_lookup():
    assert set(SPECS) == {s.id for s in TRAIN_SPECS + EVAL_SPECS}


def test_reference_solution_scores_one():
    spec = EVAL_SPECS[0]
    assert spec_reward(reference_solution(spec), spec.id, {"spec_id": spec.id}) == 1.0


def test_gated_but_runnable_earns_floor():
    spec = EVAL_SPECS[0]
    block = "import cadquery as cq\nresult = cq.Workplane('XY').box(80, 60, 6)\n"
    assert spec_reward(block, spec.id, {"spec_id": spec.id}) == pytest.approx(PARSE_FLOOR)


def test_prose_scores_zero():
    spec = EVAL_SPECS[0]
    assert spec_reward("Sure! Here is a plate.", spec.id, {"spec_id": spec.id}) == 0.0


def test_unknown_spec_id_scores_zero():
    spec = EVAL_SPECS[0]
    assert spec_reward(reference_solution(spec), "", {"spec_id": "nope"}) == 0.0


@pytest.mark.slow
@pytest.mark.parametrize("seed", [0, 1, SAMPLE_SEED])
def test_reference_solutions_verify_across_seeds(seed):
    """The sampler must never emit a spec whose reference solution fails.

    Ten specs per seed go through the full isolated build + rubric path;
    any unbuildable or unscoreable parameter combination fails loudly here.
    """
    rng = random.Random(seed)
    for i in range(10):
        spec = sample_spec(rng, i)
        report = score(reference_solution(spec), spec)
        assert report.reward == 1.0, f"{spec.id} {report.summary}"


# --- 0.3.0: tiers and diagnostics --------------------------------------------

from cad_spec.environment import CHECK_NAMES  # noqa: E402
from cad_spec.tasks import TIERS, edit_source, is_feasible, prompt_for  # noqa: E402


def test_every_tier_builds_a_dataset():
    env = load_environment(tier=list(TIERS), eval_tier=list(TIERS))
    assert len(env.dataset) == N_TRAIN * len(TIERS)
    assert len(env.eval_dataset) == N_EVAL * len(TIERS)


def test_unknown_tier_is_rejected():
    with pytest.raises(ValueError):
        load_environment(tier="L9")


def test_l2_hides_the_pitch_and_l1_shows_it():
    spec = EVAL_SPECS[0]
    assert f"{spec.pitch_x} mm x {spec.pitch_y} mm" in prompt_for(spec, "L1")
    assert f"{spec.pitch_x} mm x {spec.pitch_y} mm" not in prompt_for(spec, "L2")
    assert "???" not in prompt_for(spec, "L1")


def test_l3_eval_wording_never_appears_in_train():
    from cad_spec.tasks import _PROSE, _PROSE_EVAL, _PROSE_TRAIN

    assert set(_PROSE_TRAIN).isdisjoint(_PROSE_EVAL)
    heads = {i: _PROSE[i][:40] for i in range(len(_PROSE))}
    train_text = {prompt_for(s, "L3", "train")[:40] for s in TRAIN_SPECS}
    for i in _PROSE_EVAL:
        assert all(not t.startswith(heads[i][:25]) for t in train_text)


def test_l4_rev_a_is_feasible_and_differs():
    for spec in EVAL_SPECS + TRAIN_SPECS[:50]:
        source = edit_source(spec)
        assert is_feasible(source)
        assert (source.length, source.width, source.thickness, source.hole_diameter, source.edge_margin) != (
            spec.length, spec.width, spec.thickness, spec.hole_diameter, spec.edge_margin)


def test_l4_rev_a_code_does_not_score_as_rev_b():
    spec = EVAL_SPECS[0]
    assert score(reference_solution(edit_source(spec)), spec).reward < 1.0


def test_metrics_share_one_build_per_rollout(monkeypatch):
    """All reward/metric functions of ONE rollout share one build; a second
    rollout with identical code gets its own build (audit K2)."""
    import cad_spec.environment as envmod

    calls = []
    real_score = envmod.score

    def counting_score(text, spec):
        calls.append(spec.id)
        return real_score(text, spec)

    monkeypatch.setattr(envmod, "score", counting_score)
    spec = EVAL_SPECS[0]
    env = load_environment()
    code = reference_solution(spec)
    names = env.rubric._get_reward_func_names()
    weights = env.rubric._get_reward_weights()
    ours = [f for f, n in zip(env.rubric._get_reward_funcs(), names, strict=True)
            if n in ("spec_reward", "built", "gates_passed") or n.startswith("m_R")]
    assert len(ours) == 2 + len(CHECK_NAMES) + 1 == 12
    assert weights[names.index("spec_reward")] == 1.0
    assert all(weights[names.index(n)] == 0.0 for n in names if n.startswith("m_R"))

    for rollout in range(2):
        state: dict = {}
        for func in ours:
            assert func(code, spec.id, {"spec_id": spec.id}, state=state) == 1.0
        assert len(calls) == rollout + 1, "one build per rollout, never shared across rollouts"


def test_l4_unedited_rev_a_never_scores_full_marks():
    """Audit F12: every ECO must change something beyond tolerance."""
    for spec in TRAIN_SPECS + EVAL_SPECS:
        assert score(reference_solution(edit_source(spec)), spec).reward < 1.0, spec.id
