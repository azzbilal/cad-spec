"""cad-spec: an RL reward environment for dimensioned CadQuery parts.

The scorer (measure, rubric, tasks) needs only cadquery. The Verifiers
environment is imported lazily, so `from cad_spec.rubric import score` works
without verifiers or datasets installed.
"""

from __future__ import annotations

from typing import Any

__version__ = "0.4.0"
__all__ = ["__version__", "load_environment"]


def __getattr__(name: str) -> Any:
    if name == "load_environment":
        from .environment import load_environment

        return load_environment
    raise AttributeError(f"module 'cad_spec' has no attribute {name!r}")
