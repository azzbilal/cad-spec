"""measure.py units: code extraction, exact hole classification, exec timeout."""

import pytest

from cad_spec.measure import (
    AREA_COMPLETENESS_MIN,
    AXIS_TOL,
    COAXIAL_DP,
    PROBE_INSET_FRACTION,
    PROBE_INSET_MIN_MM,
    BuildError,
    build,
    build_and_measure,
    extract_code,
    measure,
)

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

# Regression: hollow geometry used to report 8 phantom bores (four outer
# fillets d=6 whose axes sit in the cavity, four concave inner corner
# fillets d=4 that are locally bore-like). Zero is the correct answer.
SHELLED_FILLETED_BOX = """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 20)
          .edges("|Z").fillet(3)
          .faces(">Z").shell(-1.0))
"""

BOSS_ON_PLATE = """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .circle(8).extrude(10))
"""


def _measure_inproc(monkeypatch, code):
    """Production scoring path minus the worker: as if CAD_SPEC_INPROC=1."""
    monkeypatch.setenv("CAD_SPEC_INPROC", "1")
    return build_and_measure(code)


def test_extract_code_prefers_largest_block():
    completion = "Here is a sketch:\n```python\nresult = 1\n```\nAnd the full answer:\n" + \
        "```python\n" + PLATE + "\n```"
    code = extract_code(completion)
    assert "Workplane" in code
    assert "result = 1" not in code


def test_extract_code_dedents_uniformly_indented_block():
    """A fenced block indented four spaces must come out runnable.

    This is the defect that zeroed most of the 0.2.0 baseline: the old
    `\\s*` after the fence ate the newline AND the first line's indentation,
    leaving line 1 at column zero and every later line indented -> a module
    that raises IndentationError before cadquery is ever touched.
    """
    body = "".join("    " + line + "\n" for line in PLATE.strip().splitlines())
    code = extract_code("```python\n" + body + "```")
    assert code.startswith("import cadquery as cq")
    assert "\n    " not in code.split("(", 1)[0]  # no orphaned indent on line 2
    compile(code, "<test>", "exec")  # the real assertion: it is runnable
    assert measure(build(code)).hole_count == 4


def test_extract_code_leaves_column_zero_block_unchanged():
    code = extract_code("```python\n" + PLATE.strip() + "\n```")
    assert code == PLATE.strip()
    compile(code, "<test>", "exec")


def test_unfenced_half_indented_completion_still_fails():
    """Genuinely broken input, and it must stay broken.

    An unfenced answer whose first line sits at column zero while the rest is
    indented has no common prefix, so textwrap.dedent is correctly a no-op.
    Nothing in extract_code can repair it without guessing at the model's
    intent. The fix lives upstream, in tasks.PROMPT_TEMPLATE, which no longer
    presents the example indented or asks for those exact lines back.
    """
    lines = PLATE.strip().splitlines()
    completion = lines[0] + "\n" + "".join("    " + ln + "\n" for ln in lines[1:])
    code = extract_code(completion)
    with pytest.raises(IndentationError):
        compile(code, "<test>", "exec")
    with pytest.raises(BuildError, match="IndentationError"):
        build(code)


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


def test_shelled_filleted_box_has_no_bores(monkeypatch):
    """Hollow geometry: neither fillet group is a bore.

    Outer fillet walls probe as material just inside their surface (probe
    inset), and the concave inner corner fillets fail the full-cylinder
    area check at ~0.25 coverage.
    """
    assert _measure_inproc(monkeypatch, SHELLED_FILLETED_BOX).holes == []


def test_external_boss_is_not_a_bore(monkeypatch):
    """Convex proud geometry probes as material and stays excluded."""
    assert _measure_inproc(monkeypatch, BOSS_ON_PLATE).holes == []


def test_classifier_constants_are_pinned():
    """Drift guard for the classifier's bare-number contract."""
    assert AXIS_TOL == 1e-6
    assert COAXIAL_DP == 3
    assert PROBE_INSET_FRACTION == 0.05
    assert PROBE_INSET_MIN_MM == 1e-3
    assert AREA_COMPLETENESS_MIN == 0.99


def test_timeout_kills_runaway_code_and_worker_respawns(monkeypatch):
    monkeypatch.setenv("CAD_SPEC_EXEC_TIMEOUT", "2")
    with pytest.raises(BuildError, match="budget"):
        build_and_measure("while True: pass")
    m = build_and_measure(PLATE)
    assert m.solid_count == 1


# --- 0.3.0: datums, merged bore depth, partial bores -------------------------

from cad_spec.measure import _merge_intervals, sandbox_info  # noqa: E402

SYMMETRIC_CUTTER = """
import cadquery as cq
base = cq.Workplane("XY").box(80, 60, 6)
cutters = (cq.Workplane("XY")
           .pushPoints([(-30, -20), (-30, 20), (30, -20), (30, 20)])
           .circle(6.5 / 2).extrude(10, both=True))
result = base.cut(cutters)
"""

SHIFTED_STOCK = """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6).translate((2, 0, 0))
          .faces(">Z").workplane()
          .rect(60, 40, forConstruction=True).vertices().hole(6.5))
"""

BREAKOUT = """
import cadquery as cq
result = (cq.Workplane("XY").box(80, 60, 6)
          .faces(">Z").workplane()
          .pushPoints([(38.5, -20), (-30, -20), (-30, 20), (30, 20)]).hole(6.5))
"""


def test_merge_intervals():
    assert _merge_intervals([(0, 3), (-3, 0)]) == [(-3, 3)]
    assert _merge_intervals([(0, 1), (2, 3)]) == [(0, 1), (2, 3)]
    assert _merge_intervals([(0, 2), (1, 3), (3, 4)]) == [(0, 4)]
    assert _merge_intervals([]) == []


def test_split_bore_wall_measures_full_depth():
    """P0-2: two stacked 3 mm faces are ONE 6 mm through bore."""
    m = measure(build(SYMMETRIC_CUTTER))
    assert len(m.holes) == 4
    for h in m.holes:
        assert h.depth == 6.0 and h.segments == 1
        assert (h.z_min, h.z_max) == (-3.0, 3.0)


def test_blind_bore_is_one_short_segment():
    m = measure(build(BLIND_DIMPLES))
    assert all(h.segments == 1 and h.z_max == 3.0 and h.z_min == 2.0 for h in m.holes)


def test_envelope_datums_are_recorded():
    """P0-1: sizes are translation-invariant; datums are not."""
    m = measure(build(SHIFTED_STOCK))
    assert (m.x_min, m.x_max) == (-38.0, 42.0)
    assert m.centre == (2.0, 0.0, 0.0)
    assert m.length == 80.0


def test_breakout_is_reported_not_silently_dropped():
    m = measure(build(BREAKOUT))
    assert m.hole_count == 3
    assert len(m.partial_bores) == 1
    pb = m.partial_bores[0]
    assert (pb.x, pb.y) == (38.5, -20.0)
    assert 0.3 < pb.coverage < 0.99


def test_fillets_are_not_reported_as_partial_bores():
    """Quarter-arc fillets sit below PARTIAL_REPORT_MIN: noise, not bores."""
    assert measure(build(FILLETED)).partial_bores == []


def test_whole_workplane_stack_is_measured():
    """Four loose tabs on the stack are four solids, not one tab."""
    code = """
import cadquery as cq
result = (cq.Workplane("XY")
          .pushPoints([(-35, -25), (35, -25), (-35, 25), (35, 25)])
          .box(10, 10, 6, combine=False))
"""
    m = measure(build(code))
    assert m.solid_count == 4
    assert (m.length, m.width) == (80.0, 60.0)


# --- 0.3.0: sandbox -----------------------------------------------------------

posix_only = pytest.mark.skipif(sandbox_info().get("mode") != "fork", reason="fork sandbox is POSIX-only")

TINY = "import cadquery as cq\nresult = cq.Workplane('XY').box(1, 1, 1)\n"


@posix_only
def test_rollouts_cannot_leak_python_state():
    """Rollout A sabotages cadquery; rollout B must not inherit it."""
    with pytest.raises(BuildError):
        build_and_measure("import cadquery as cq\ncq.Workplane.box = None\n" + TINY)
    assert build_and_measure(PLATE).hole_count == 4


@posix_only
def test_rollout_environment_is_scrubbed(monkeypatch):
    from cad_spec.measure import shutdown_worker

    monkeypatch.setenv("CAD_SPEC_TEST_SECRET", "hunter2")
    shutdown_worker()  # respawn so the worker inherits the secret
    try:
        build_and_measure("import os\nassert 'CAD_SPEC_TEST_SECRET' not in os.environ\n" + TINY)
    finally:
        shutdown_worker()


@posix_only
def test_relative_writes_land_in_a_deleted_temp_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    build_and_measure("open('side_effect.txt', 'w').write('x')\n" + TINY)
    assert not (tmp_path / "side_effect.txt").exists()


@posix_only
def test_memory_bomb_is_contained():
    with pytest.raises(BuildError, match=r"MemoryError|memory|crashed"):
        build_and_measure("x = bytearray(64 * 1024 ** 3)\n")
    assert build_and_measure(PLATE).hole_count == 4


@posix_only
def test_file_size_limit():
    with pytest.raises(BuildError):
        build_and_measure("open('big.bin', 'wb').write(b'0' * (64 << 20))\n" + TINY)


def test_sandbox_info_describes_mode(monkeypatch):
    monkeypatch.setenv("CAD_SPEC_INPROC", "1")
    assert sandbox_info() == {"mode": "inproc", "isolated": False}
