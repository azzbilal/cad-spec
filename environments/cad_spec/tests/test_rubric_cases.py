"""Parametrized wrapper around scripts/test_rubric.py.

The zero-dependency harness stays the single source of truth for rubric
expectations (runnable with nothing but cadquery installed); this wrapper
brings the same 19 cases into pytest so CI runs them on every push.
"""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "test_rubric.py"
_spec = importlib.util.spec_from_file_location("test_rubric_script", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def _parse(expr: str) -> float:
    num, _, den = expr.partition("/")
    return float(num) / float(den) if den else float(expr)


@pytest.mark.parametrize("name", sorted(_mod.CASES))
def test_case(name: str):
    expected, code = _mod.CASES[name]
    report = _mod.score(code, _mod.SPEC)
    assert report.reward == pytest.approx(_parse(expected), abs=1e-3), report.summary
