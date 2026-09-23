"""Parametrized wrapper around scripts/test_rubric.py.

The zero-dependency harness stays the single source of truth for rubric
expectations (runnable with nothing but cadquery installed); this wrapper
brings every case into pytest so CI runs them on every push. Each case pins
its reward AND its exact set of failed checks.
"""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "test_rubric.py"
_spec = importlib.util.spec_from_file_location("test_rubric_script", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


@pytest.mark.parametrize("name", sorted(_mod.CASES))
def test_case(name: str):
    ok, msg = _mod.check_case(name, _mod.CASES[name])
    assert ok, msg


def test_harness_has_the_audit_regressions():
    for name in ("shifted_stock", "symmetric_cutter", "whole_part_off_origin", "LIMIT_hole_breakout"):
        assert name in _mod.CASES
