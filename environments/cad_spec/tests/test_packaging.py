"""0.4.3: packaging rules that keep the Hosted Training image intact.

The smoke run of 29 Sep 2026 crashed before any rollout: a pinned verifiers
range made pip replace the platform's own verifiers, which pulled in a
prime-sandboxes release that clashes with the training image. A floor of
0.2.0 or more also made `prime env push` publish this v0 package as v1.
"""

import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _requirements() -> dict[str, str]:
    deps = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["dependencies"]
    out = {}
    for d in deps:
        name = d.split(";")[0].strip()
        base = name.split("[")[0]
        for op in ("==", ">=", "<=", "~=", "!=", ">", "<"):
            base = base.split(op)[0]
        out[base.strip().lower()] = name
    return out


def test_verifiers_is_unpinned():
    """No version on verifiers: the platform's copy is used as it is, and the
    Hub classifies the package as legacy v0 (no floor >= 0.2.0)."""
    assert _requirements()["verifiers"] == "verifiers"


def test_datasets_has_no_upper_bound():
    assert "<" not in _requirements()["datasets"]


def test_cadquery_stays_pinned_to_the_validated_minor():
    """The scorer's numbers were validated on CadQuery 2.8; that pin stays."""
    assert _requirements()["cadquery"] == "cadquery>=2.8,<2.9"
