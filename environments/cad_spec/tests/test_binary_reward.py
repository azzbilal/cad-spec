"""0.4.2: the binary training reward (1.0 only when all nine requirements pass)."""

import dataclasses

import pytest

import cad_spec.environment as env_mod
from cad_spec.environment import EVAL_SPECS, all_pass_reward, load_environment, spec_reward
from cad_spec.rubric import score
from cad_spec.tasks import reference_solution


def _rubric(env):
    """(name, weight) of every reward function, parser rubric included."""
    names = env.rubric._get_reward_func_names()
    weights = env.rubric._get_reward_weights()
    return list(zip(names, weights, strict=True))


def _weighted(env):
    return [(n, w) for n, w in _rubric(env) if w != 0.0]


def test_default_is_unchanged():
    env = load_environment()
    assert _weighted(env) == [("spec_reward", 1.0)]
    assert "all_pass_reward" not in dict(_rubric(env))  # same rubric as 0.4.1


def test_binary_mode_trains_on_all_pass_and_logs_continuous():
    env = load_environment(reward="binary")
    assert _weighted(env) == [("all_pass_reward", 1.0)]
    assert dict(_rubric(env))["spec_reward"] == 0.0  # still logged, zero weight


def test_binary_without_metrics_has_one_weighted_function():
    env = load_environment(reward="binary", metrics=False)
    assert _weighted(env) == [("all_pass_reward", 1.0)]
    assert "spec_reward" not in dict(_rubric(env))


def test_unknown_reward_is_refused():
    with pytest.raises(ValueError):
        load_environment(reward="shaped")


def test_reference_scores_one_in_both_modes():
    spec = EVAL_SPECS[0]
    code = reference_solution(spec)
    assert spec_reward(code, spec.id, {"spec_id": spec.id}) == 1.0
    assert all_pass_reward(code, spec.id, {"spec_id": spec.id}) == 1.0


def test_the_l4_failure_is_8_of_10_continuous_and_0_binary(monkeypatch):
    """Change order: plate 20 mm longer, same margin. The typical failure
    resizes the plate but keeps the old hole pitch along the length."""
    base = EVAL_SPECS[0]
    target = dataclasses.replace(base, id="eco-test", length=base.length + 20)
    monkeypatch.setitem(env_mod.SPECS, target.id, target)
    code = reference_solution(target).replace(
        f".rect({target.pitch_x}, {target.pitch_y}",
        f".rect({base.pitch_x}, {base.pitch_y}")  # new plate, old pitch
    assert f".rect({base.pitch_x}," in code
    rep = score(code, target)
    failed = sorted(c.name for c in rep.checks if not c.passed)
    assert failed == ["R5:hole_pattern", "R7:edge_margin"]
    # the scorer rounds rewards to 4 decimals
    assert spec_reward(code, target.id, {"spec_id": target.id}) == pytest.approx(8 / 10, abs=1e-4)
    # the same answer under the scorer run 1 was trained with: 7 of 9
    assert score(code, target, "0.4.0").reward == pytest.approx(7 / 9, abs=1e-4)
    assert all_pass_reward(code, target.id, {"spec_id": target.id}) == 0.0


def test_binary_is_all_pass_of_the_same_report():
    spec = EVAL_SPECS[0]
    for code in (reference_solution(spec), "this is not code",
                 "import cadquery as cq\nresult = cq.Workplane('XY')"):
        rep = score(code, spec)
        cont = spec_reward(code, spec.id, {"spec_id": spec.id})
        binr = all_pass_reward(code, spec.id, {"spec_id": spec.id})
        assert binr == (1.0 if rep.parsed and rep.reward == 1.0 else 0.0)
        assert binr <= cont
