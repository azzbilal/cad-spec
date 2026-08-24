"""measure.py units: code extraction, exact hole classification, exec timeout."""

import pytest

from cad_spec.measure import BuildError, build, build_and_measure, extract_code, measure

PLATE = """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
"""

FILLETED = """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .edges("|Z").fillet(3)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
"""

COUNTERBORED = """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane().rect(60, 40, forConstruction=True)
          .vertices().cboreHole(6.5, 11, 2))
"""

BLIND_DIMPLES = """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5, depth=1.0))
"""


def test_extract_code_prefers_largest_block():
    completion = "Here is a sketch:\n```python\nresult = 1\n```\nAnd the full answer:\n" + \
        "```python\n" + PLATE + "\n```"
    code = extract_code(completion)
    assert "Workplane" in code
    assert "result = 1" not in code


def test_plain_plate_has_four_bores():
    m = measure(build(PLATE))
    assert len(m.holes) == 4
    assert all(h.diameter == 6.5 for h in m.holes)


def test_fillets_are_not_holes():
    m = measure(build(FILLETED))
    assert len(m.holes) == 4


def test_counterbore_is_two_coaxial_diameters():
    m = measure(build(COUNTERBORED))
    positions = {(h.x, h.y) for h in m.holes}
    assert len(positions) == 4
    for x, y in positions:
        stack = {h.diameter for h in m.holes if h.x == x and h.y == y}
        assert stack == {6.5, 11.0}


def test_blind_hole_depth_recorded():
    m = measure(build(BLIND_DIMPLES))
    assert m.holes
    assert all(abs(h.depth - 1.0) < 1e-6 for h in m.holes)


def test_timeout_kills_runaway_code_and_worker_respawns(monkeypatch):
    monkeypatch.setenv("CAD_SPEC_EXEC_TIMEOUT", "2")
    with pytest.raises(BuildError, match="budget"):
        build_and_measure("while True: pass")
    m = build_and_measure(PLATE)
    assert m.solid_count == 1
