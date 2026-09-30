"""0.4.4: the rollout path Hosted Training uses, run through verifiers itself.

Smoke run jvryf7tsn20jw66cfxesbp08 (29 Sep 2026) rejected every rollout:
verifiers' legacy path decodes a top-level string "task" as a JSON task
payload. Unit tests that call the reward functions directly never reached
that code. These tests go through `env.init_state` and `env.rubric` like a
training rollout does, with a stand-in client (no model is called).
"""

import asyncio
import dataclasses
from unittest.mock import MagicMock

import pytest

from cad_spec.environment import EVAL_SPECS, SPECS, load_environment
from cad_spec.tasks import reference_solution

clients = pytest.importorskip("verifiers.legacy.clients")


def _rollout(env, row, answer_code):
    state = asyncio.run(env.init_state(input=dict(row), client=MagicMock(spec=clients.Client), model="m"))
    state["completion"] = [{"role": "assistant", "content": "```python\n" + answer_code + "\n```"}]
    asyncio.run(env.rubric.score_rollout(state))
    return state


@pytest.mark.parametrize("tier", ["L1", "L2", "L3", "L4"])
def test_rows_carry_no_task_route(tier):
    env = load_environment(tier=[tier], hints=True, reward="binary")
    for ds in (env.dataset, env.eval_dataset):
        assert "task" not in ds.column_names
        assert ds[0]["info"]["tier"] == tier  # the tier lives in info


@pytest.mark.parametrize("reward", ["binary", "continuous"])
def test_reference_answer_scores_one_through_verifiers(reward):
    env = load_environment(tier=["L4"], hints=True, reward=reward)
    row = env.dataset[0]
    state = _rollout(env, row, reference_solution(SPECS[row["answer"]]))
    assert state["reward"] == 1.0
    assert state["metrics"]["built"] == 1.0


def test_l4_failure_is_zero_binary_through_verifiers(monkeypatch):
    """New plate, old pitch: 7/9 continuous (logged), 0 binary (trained on)."""
    import cad_spec.environment as env_mod

    base = EVAL_SPECS[0]
    target = dataclasses.replace(base, id="eco-rollout-test", length=base.length + 20)
    monkeypatch.setitem(env_mod.SPECS, target.id, target)
    code = reference_solution(target).replace(
        f".rect({target.pitch_x}, {target.pitch_y}", f".rect({base.pitch_x}, {base.pitch_y}")
    env = load_environment(tier=["L4"], hints=True, reward="binary")
    row = dict(env.dataset[0])
    row["answer"] = target.id
    row["info"] = {"spec_id": target.id, "tier": "L4"}
    state = _rollout(env, row, code)
    assert state["reward"] == 0.0
    assert state["metrics"]["spec_reward"] == pytest.approx(7 / 9, abs=1e-4)


def test_full_rollout_with_a_stand_in_model():
    """env.rollout end to end: prompt built with the cheat-sheet, one model call,
    the answer built, measured and scored, no error recorded."""
    import time
    from unittest.mock import AsyncMock

    types = pytest.importorskip("verifiers.legacy.types")
    env = load_environment(tier=["L2"], hints=True, reward="binary")
    row = dict(env.dataset[0])
    code = reference_solution(SPECS[row["answer"]])
    client = MagicMock(spec=clients.Client)
    client.get_response = AsyncMock(return_value=types.Response(
        id="r1", created=int(time.time()), model="m",
        message=types.ResponseMessage(content="```python\n" + code + "\n```",
                                      finish_reason="stop", is_truncated=False)))
    state = asyncio.run(env.rollout(input=row, client=client, model="m",
                                    sampling_args={"temperature": 0.7, "max_tokens": 2048}))
    asyncio.run(env.rubric.score_rollout(state))
    assert client.get_response.await_count == 1
    call = client.get_response.call_args
    prompt = call.kwargs.get("prompt", call.args[0] if call.args else None)
    assert "CadQuery" in str(prompt)  # the packaged cheat-sheet reached the model
    assert state["reward"] == 1.0 and state.get("error") is None
