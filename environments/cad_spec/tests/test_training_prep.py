"""0.4.1: one shared system prompt, the packaged cheat-sheet, the locked test split."""

from pathlib import Path

import pytest

from cad_spec.prompts import SYSTEM_PROMPT, fingerprint, hints_text, system_prompt
from cad_spec.rubric import score
from cad_spec.tasks import (
    N_TEST,
    TEST_SPLIT_SHA256,
    _params,
    edit_source,
    make_splits,
    make_test_split,
    prompt_for,
    reference_solution,
    split_fingerprint,
)

REPO_HINTS = Path(__file__).resolve().parents[3] / "prompts" / "cadquery-hints.md"

# Fingerprints of the texts actually recorded in the saved runs: every
# leaderboard run and the first-shot/feedback arms used the first, every
# hint-arm run the second. A change to either text breaks comparability with
# all published results, so it must be deliberate and show up here.
LEADERBOARD_PROMPT_SHA256 = "a82834a06ac7a28b00ffe37930dd822cefe86bdf1bf02ba05ceb6f5fcda8f45b"
HINT_ARM_PROMPT_SHA256 = "a9050c1da2a319200fd38c432c6505d2254b39249613b9079bf7cfb9f1e5128c"


def test_system_prompt_is_the_leaderboard_text():
    assert fingerprint(SYSTEM_PROMPT) == LEADERBOARD_PROMPT_SHA256
    assert system_prompt() == SYSTEM_PROMPT


def test_hints_prompt_is_the_experiment_hint_arm():
    assert fingerprint(system_prompt(hints=True)) == HINT_ARM_PROMPT_SHA256


def test_packaged_hints_match_the_registered_file():
    if not REPO_HINTS.exists():  # an install from the Hub has no repository around it
        pytest.skip("not a source checkout")
    assert hints_text() == REPO_HINTS.read_text(encoding="utf-8").strip()


def test_hints_hold_no_spec_numbers():
    # The cheat-sheet may teach the API, never the answer: no spec from any
    # split may have its dimensions in it.
    text = hints_text()
    train, evals = make_splits()
    for spec in [*train, *evals, *make_test_split()]:
        for value in _params(spec):
            if value >= 20:  # small values (3, 5, 10...) appear as generic API examples
                assert f"{value:g}" not in text, (spec.id, value)


def test_test_split_is_locked():
    specs = make_test_split()
    assert split_fingerprint(specs) == TEST_SPLIT_SHA256
    assert len(specs) == N_TEST
    assert [s.id for s in specs] == [f"test-{i:04d}" for i in range(1, N_TEST + 1)]
    assert split_fingerprint(make_test_split()) == TEST_SPLIT_SHA256  # deterministic


def test_test_split_is_disjoint_from_train_and_eval():
    train, evals = make_splits()
    seen = {_params(s) for s in [*train, *evals]}
    test = [_params(s) for s in make_test_split()]
    assert len(set(test)) == len(test)
    assert not set(test) & seen


def test_test_split_uses_held_out_wording():
    for spec in make_test_split():
        assert prompt_for(spec, "L3", "test") == prompt_for(spec, "L3", "eval")


def test_every_test_spec_is_solvable_at_every_tier():
    for spec in make_test_split():
        assert score(reference_solution(spec), spec).reward == pytest.approx(1.0), spec.id
        source = edit_source(spec)  # L4 needs a feasible revision A that differs
        assert source != spec
        for tier in ("L0", "L1", "L2", "L3", "L4"):
            assert prompt_for(spec, tier, "test")


def test_environment_hints_switch():
    pytest.importorskip("verifiers")
    from cad_spec.environment import load_environment

    plain = load_environment(tier="L2", metrics=False)
    hinted = load_environment(tier="L2", metrics=False, hints=True)
    assert plain.system_prompt == system_prompt(False)
    assert hinted.system_prompt == system_prompt(True)
    # Training and evaluation both see the switch: one system prompt per env.
    assert hinted.dataset["prompt"][0][0]["content"] == system_prompt(True)
    assert hinted.eval_dataset["prompt"][0][0]["content"] == system_prompt(True)
