"""L5 observation map (milestone M1): fast checks. The adversarial gate is scripts/test_l5_observation.py."""

import pytest

from cad_spec.l5 import (
    EPS_DIM_MM,
    EPS_FORM_MM,
    FORM_VIOLATION,
    OK,
    OUT_OF_SCOPE,
    SCORER_BASIS,
    observe,
    observe_code,
)
from cad_spec.measure import FORM_LINEAR_TOL, build_and_measure
from cad_spec.rubric import TOLERANCES, score
from cad_spec.tasks import make_splits, reference_solution

TRAIN, DEV = make_splits()


def test_tolerances_are_those_of_scorer_0_5_0_by_name():
    assert SCORER_BASIS == "0.5.0"  # pinned: a later scorer default must not move L5 silently
    assert TOLERANCES["0.5.0"].eps == EPS_DIM_MM
    assert EPS_FORM_MM == FORM_LINEAR_TOL


@pytest.mark.parametrize("spec", [TRAIN[0], TRAIN[7], DEV[0], DEV[11], DEV[29]], ids=lambda s: s.id)
def test_reference_parts_observe_as_their_spec(spec):
    """The map and the task generator agree on what the reference part is."""
    obs = observe_code(reference_solution(spec))
    assert obs.status == OK, obs.reason
    v = obs.values
    assert (v["L"], v["W"], v["T"], v["n"], v["D"]) == pytest.approx(
        (spec.length, spec.width, spec.thickness, 4, spec.hole_diameter), abs=1e-9)
    assert (v["mx"], v["my"]) == pytest.approx((spec.edge_margin, spec.edge_margin), abs=1e-9)
    assert (v["px"], v["py"]) == pytest.approx(
        (spec.length - 2 * spec.edge_margin, spec.width - 2 * spec.edge_margin), abs=1e-9)
    assert v["rectangular"] and v["centered"] and v["symmetric"]


def test_form_verdict_is_the_scorers_r9():
    """A pocketed plate: the map's form verdict and R9 are one and the same check."""
    spec = DEV[0]
    pocketed = reference_solution(spec) + (
        f'\nresult = result.cut(cq.Workplane("XY").box(4, 4, 1).translate((0, 0, {spec.thickness / 2})))\n')
    obs = observe_code(pocketed)
    r9 = next(c for c in score(pocketed, spec).checks if c.name == "R9:no_other_features")
    assert obs.status == FORM_VIOLATION and not r9.passed and obs.reason == r9.detail
    assert obs.values["n"] == 4  # still measured: measurable does not mean acceptable


def test_a_legacy_measurement_is_refused():
    with pytest.raises(ValueError, match="strict"):
        observe(build_and_measure(reference_solution(DEV[0])))


def test_a_failed_scope_scan_is_a_refusal_not_an_exception(monkeypatch):
    """Review R5: the measurement recorded the failure; the map must refuse, not raise."""
    import cadquery as cq

    import cad_spec.measure as mm

    def broken(_solid):
        raise RuntimeError("synthetic classifier fault")

    monkeypatch.setattr(mm, "_scope_scan", broken)
    m = mm.measure(cq.Workplane("XY").box(100, 80, 4).val(), strict=True)
    assert m.strict and m.scope_error and m.off_axis_concave is None
    obs = observe(m)
    assert obs.status == OUT_OF_SCOPE and "synthetic classifier fault" in obs.reason
    assert not obs.ok and dict(obs.values) == {"L": 100.0, "W": 80.0, "T": 4.0}


def test_values_are_read_only_and_only_ok_allows_a_contract():
    obs = observe_code(reference_solution(DEV[0]))
    assert obs.ok
    with pytest.raises(TypeError):
        obs.values["L"] = 0.0  # type: ignore[index]

