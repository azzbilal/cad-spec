"""The system prompt and the CadQuery cheat-sheet: one source for everything.

The environment (what Prime trains and evaluates on) and scripts/run_baseline.py
(what produced the leaderboard and the hint/feedback experiment) both import
these. Before 0.4.1 each held its own copy of the system prompt; they happened
to be identical, but nothing kept them so. The cheat-sheet ships inside the
package (hints.md), so a copy installed from the Hub has the same text as the
repository, and a test pins both texts by fingerprint.
"""

from __future__ import annotations

import hashlib
from importlib.resources import files

SYSTEM_PROMPT = """\
You are a mechanical design engineer who writes CadQuery.
Return a single Python code block and nothing else.
Import cadquery as cq and bind the finished part to a variable named `result`.
Build solids with the Workplane API, for example cq.Workplane("XY").box(l, w, h).
"""


def hints_text() -> str:
    """The CadQuery cheat-sheet (general API facts, no spec numbers)."""
    return files("cad_spec").joinpath("hints.md").read_text(encoding="utf-8").strip()


def system_prompt(hints: bool = False) -> str:
    """The system prompt, optionally with the cheat-sheet appended.

    With hints=True this is byte-identical to the hint arm of the registered
    experiment (standard prompt, newline, cheat-sheet, newline).
    """
    return SYSTEM_PROMPT + "\n" + hints_text() + "\n" if hints else SYSTEM_PROMPT


def fingerprint(text: str) -> str:
    """SHA-256 of a prompt text, recorded with every run."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
