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
