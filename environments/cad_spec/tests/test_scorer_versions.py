"""Scorer versions live side by side (0.5.0).

0.4.0 must keep scoring exactly as recorded, because result files are replayed
under the version they were recorded with. 0.5.0 is the strict contract.
"""

from __future__ import annotations

import pytest

from cad_spec.environment import EVAL_SPECS, load_environment, spec_reward
from cad_spec.measure import Hole
from cad_spec.rubric import SCORER_VERSION, SUPPORTED_VERSIONS, TOLERANCES, _one_to_one, score
from cad_spec.tasks import reference_solution

SPEC = EVAL_SPECS[0]
# The reference part with a small extra cut at the centre: a wrong part under
# the strict contract, full credit under 0.4.0 (inside its 3% material band).
POCKETED = reference_solution(SPEC).rstrip() + (
    "\nresult = result.cut(cq.Workplane('XY').rect(2, 2).extrude(100))\n")


def _requirements(report):
    return [c.name for c in report.checks if not c.name.startswith("gate:")]


def test_current_version_is_strict_and_legacy_is_kept():
    assert SCORER_VERSION == "0.5.0"
    assert SUPPORTED_VERSIONS == ("0.4.0", "0.5.0")
    assert TOLERANCES["0.4.0"].linear == 0.5 and TOLERANCES["0.4.0"].hole == 0.2
    assert set(vars(TOLERANCES["0.5.0"]).values()) == {0.1}


def test_reference_passes_both_versions_with_9_and_10_requirements():
    old, new = score(reference_solution(SPEC), SPEC, "0.4.0"), score(reference_solution(SPEC), SPEC)
    assert old.reward == new.reward == 1.0
    assert len(_requirements(old)) == 9 and "R9:no_other_features" not in _requirements(old)
    assert len(_requirements(new)) == 10 and _requirements(new)[-1] == "R9:no_other_features"


def test_extra_cut_is_full_credit_under_legacy_and_fails_r9_now():
    assert score(POCKETED, SPEC, "0.4.0").reward == 1.0
    new = score(POCKETED, SPEC, "0.5.0")
    assert [c.name for c in new.checks if not c.passed] == ["R9:no_other_features"]
    assert new.reward == pytest.approx(0.9)


def test_unknown_version_is_refused():
    with pytest.raises(ValueError, match="unknown scorer version"):
        score(reference_solution(SPEC), SPEC, "0.3.0")
    with pytest.raises(ValueError, match="scorer_version must be one of"):
        load_environment(scorer_version="0.3.0")


def _named(env, name):
    """The reward function an environment registered under this name (verifiers wraps the rubric)."""
    return next(f for f, n in zip(env.rubric._get_reward_funcs(), env.rubric._get_reward_func_names(), strict=True)
                if n == name)


def test_each_environment_owns_its_scorer_version():
    """Second audit, B3: loading a second environment must not change the first one."""
    old = load_environment(scorer_version="0.4.0")
    old_reward = _named(old, "spec_reward")
    assert old_reward(POCKETED, SPEC.id, {"spec_id": SPEC.id}) == 1.0
    new = load_environment()  # current scorer, loaded afterwards in the same process
    new_reward = _named(new, "spec_reward")
    assert (old.scorer_version, new.scorer_version) == ("0.4.0", SCORER_VERSION)
    assert new_reward(POCKETED, SPEC.id, {"spec_id": SPEC.id}) == pytest.approx(0.9)
    assert old_reward(POCKETED, SPEC.id, {"spec_id": SPEC.id}) == 1.0  # unchanged by the later load
    # a report cached by one scorer is never served to the other
    state: dict = {}
    assert old_reward(POCKETED, SPEC.id, {"spec_id": SPEC.id}, state=state) == 1.0
    assert new_reward(POCKETED, SPEC.id, {"spec_id": SPEC.id}, state=state) == pytest.approx(0.9)
    assert old_reward(POCKETED, SPEC.id, {"spec_id": SPEC.id}, state=state) == 1.0
    # the module-level function, called directly, uses the current scorer
    assert spec_reward(POCKETED, SPEC.id, {"spec_id": SPEC.id}) == pytest.approx(0.9)


def test_legacy_measurement_does_none_of_the_new_work():
    """Second audit, B5: scorer 0.4.0 gets the measurement it was recorded with."""
    from cad_spec.measure import build_and_measure

    code = reference_solution(SPEC)
    legacy, strict = build_and_measure(code), build_and_measure(code, strict=True)
    assert (legacy.surface_conformance, legacy.extra_volume, legacy.missing_volume) == (None, None, None)
    assert strict.surface_conformance is True and strict.extra_volume == 0.0 and strict.missing_volume == 0.0
    assert legacy.length == round(legacy.length, 4)


def test_tolerance_is_not_widened_by_rounding():
    """Second audit, B2: 0.100049 mm over used to round to 0.1000 and pass."""
    over = reference_solution(SPEC).replace(f".hole({SPEC.hole_diameter})", f".hole({SPEC.hole_diameter + 0.100049})")
    assert over != reference_solution(SPEC)
    assert [c.name for c in score(over, SPEC).checks if not c.passed] == ["R4b:hole_diameter"]
    at_limit = reference_solution(SPEC).replace(f".hole({SPEC.hole_diameter})", f".hole({SPEC.hole_diameter + 0.1})")
    assert score(at_limit, SPEC).reward == 1.0


def test_hole_pattern_is_matched_one_to_one():
    one = [Hole(diameter=5.0, x=0.05, y=0.0, depth=5.0)]
    both_near = [(0.0, 0.0), (0.1, 0.0)]
    assert _one_to_one(both_near, one, 0.1) == 1       # one hole cannot satisfy two positions
    two = [*one, Hole(diameter=5.0, x=0.12, y=0.0, depth=5.0)]
    assert _one_to_one(both_near, two, 0.1) == 2
    # the assignment is found even when the nearest-first choice would block it
    crossed = [Hole(diameter=5.0, x=0.1, y=0.0, depth=5.0), Hole(diameter=5.0, x=0.2, y=0.0, depth=5.0)]
    assert _one_to_one([(0.15, 0.0), (0.05, 0.0)], crossed, 0.1) == 2
    assert _one_to_one(both_near, [], 0.1) == 0
    # many candidate holes: the answer comes at once (the first draft enumerated every combination)
    crowd = [Hole(diameter=5.0 + i * 1e-4, x=x, y=0.0, depth=5.0) for x in (0.0, 10.0, 20.0, 30.0) for i in range(60)]
    assert _one_to_one([(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0)], crowd, 0.1) == 4
