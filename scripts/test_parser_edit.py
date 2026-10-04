"""Self-test for the parser-edit provider in scripts/run_baseline.py (runs in CI, no network).

    python scripts/test_parser_edit.py

Hand-written prompts in the L4 format, numbers chosen by hand and not taken
from any split: one-change orders (length, edge margin, hole diameter),
two-change orders, prompts it must refuse (unknown label, a "from" that does
not match rev A, unequal X and Y margins, a missing .rect() call, no change
listed), and a requirement-table prompt that must get the parser-derive
fallback. Assertions read the numbers out of the returned code, so no
CadQuery build is needed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_baseline as rb  # noqa: E402


def check(ok: bool, what: str) -> bool:
    print(f"[{'ok ' if ok else 'BAD'}] {what}")
    return ok


def rev_a(box: str, rect: str, hole: str) -> str:
    return (
        "import cadquery as cq\nresult = (\n    cq.Workplane(\"XY\")\n"
        f"    .box({box})\n    .faces(\">Z\").workplane()\n"
        f"    .rect({rect}, forConstruction=True)\n    .vertices()\n    .hole({hole})\n)"
    )


def l4_prompt(code: str, changes: list[str]) -> str:
    return (
        "Below is the current CadQuery model of a mounting plate (rev A).\n\n"
        "```python\n" + code + "\n```\n\n"
        "ENGINEERING CHANGE ORDER, rev A -> rev B:\n" + "\n".join(changes) + "\n"
        "Every other characteristic stays exactly as in rev A: four through holes, "
        "one per corner, each hole centre at the stated edge margin from its two "
        "nearest edges, part centred on the origin.\n\n"
        "Return the complete rev B CadQuery module with the part bound to `result`."
    )


# Rev A: 100 x 70 x 8, margin 12 on both axes (pitch 76 x 46), 9 mm holes.
REV_A = rev_a("100.0, 70.0, 8.0", "76.0, 46.0", "9.0")
LENGTH = "overall length (X)"
WIDTH = "overall width (Y)"
THICK = "plate thickness (Z)"
DIA = "hole diameter"
MARGIN = "edge margin (hole centre to nearest edges)"


def change(label: str, old: str, new: str) -> str:
    return f"  - change {label} from {old} mm to {new} mm"


def numbers(answer: str) -> dict[str, tuple[float, ...]] | None:
    """box, rect and hole arguments of the answer's code, or None if it has no code."""
    if "```python" not in answer:
        return None
    out = {}
    for name, regex in rb._REV_A_CALLS.items():
        hits = regex.findall(answer)
        if len(hits) != 1:
            return None
        out[name] = tuple(float(x) for x in (hits[0] if isinstance(hits[0], tuple) else (hits[0],)))
    return out


def expect(prompt: str, box: tuple[float, ...], rect: tuple[float, ...], hole: float, what: str) -> bool:
    got = numbers(rb.parser_edit_answer(prompt))
    return check(got == {"box": box, "rect": rect, "hole": (hole,)}, f"{what}: {got}")


def refuses(prompt: str, reason: str, what: str) -> bool:
    ans = rb.parser_edit_answer(prompt)
    return check("```" not in ans and ans.startswith("I could not apply the change order") and reason in ans,
                 f"{what}: {ans!r}")


def main() -> int:
    results = [
        # One change: the margin is held, only the pitch on the changed axis moves.
        expect(l4_prompt(REV_A, [change(LENGTH, "100", "85")]),
               (85, 70, 8), (61, 46), 9, "length 100 -> 85 keeps margin 12, pitch_x 61, pitch_y 46"),
        expect(l4_prompt(REV_A, [change(MARGIN, "12", "15.5")]),
               (100, 70, 8), (69, 39), 9, "margin 12 -> 15.5 moves both pitches"),
        expect(l4_prompt(REV_A, [change(DIA, "9", "7.5")]),
               (100, 70, 8), (76, 46), 7.5, "hole diameter 9 -> 7.5 leaves the pattern alone"),
        expect(l4_prompt(REV_A, [change(THICK, "8", "10")]),
               (100, 70, 10), (76, 46), 9, "thickness 8 -> 10"),
        # Two changes, applied in order; margin after a size change, and the reverse.
        expect(l4_prompt(REV_A, [change(WIDTH, "70", "60"), change(MARGIN, "12", "10")]),
               (100, 60, 8), (80, 40), 9, "width 70 -> 60 then margin 12 -> 10"),
        expect(l4_prompt(REV_A, [change(LENGTH, "100", "120.5"), change(DIA, "9", "11")]),
               (120.5, 70, 8), (96.5, 46), 11, "length 100 -> 120.5 and diameter 9 -> 11"),
        # Same field twice: the second "from" must be the value after the first change.
        expect(l4_prompt(REV_A, [change(LENGTH, "100", "90"), change(LENGTH, "90", "95")]),
               (95, 70, 8), (71, 46), 9, "length changed twice, in order"),
        # Refusals: never a guess.
        refuses(l4_prompt(REV_A, ["  - change plate colour from 1 mm to 2 mm"]),
                "unrecognised change line", "unknown label"),
        refuses(l4_prompt(REV_A, [change(LENGTH, "110", "85")]),
                "is 100 mm before this change, not 110 mm", "'from' value does not match rev A"),
        refuses(l4_prompt(REV_A, [change(LENGTH, "100", "90"), change(LENGTH, "100", "95")]),
                "is 90 mm before this change, not 100 mm", "second change of a field checked against the first"),
        refuses(l4_prompt(rev_a("100.0, 70.0, 8.0", "76.0, 50.0", "9.0"), [change(LENGTH, "100", "85")]),
                "edge margin differs between X (12) and Y (10)", "rev A margins disagree"),
        refuses(l4_prompt(REV_A.replace("    .rect(76.0, 46.0, forConstruction=True)\n", ""),
                          [change(LENGTH, "100", "85")]),
                "expected one .rect() call in rev A, found 0", "rev A has no .rect() call"),
        refuses(l4_prompt(REV_A, []), "lists no change", "empty change order"),
        refuses(l4_prompt(REV_A, [change(LENGTH, "100", "85")]).replace("```python", "```"),
                "no rev A code block", "code block without the python fence"),
    ]
    # Not an L4 prompt: the parser-derive fallback, byte for byte.
    table = ("REQUIREMENTS\n  R1  Overall length (X):        90.0 mm\n  R2  Overall width (Y):         50.0 mm\n"
             "  R3  Plate thickness (Z):       5.0 mm\n  R4  Fastener holes:            4 off, through, 6.5 mm "
             "diameter\n  R5  Hole pattern:              rectangular, one hole near each corner\n"
             "  R6  Edge margin:               9.0 mm from hole centre to each nearest edge\n")
    results.append(check(rb.parser_edit_answer(table) == rb.parser_answer(table, derive=True),
                         "requirement table: same answer as parser-derive"))
    derived = {"box": (90, 50, 5), "rect": (72, 32), "hole": (6.5,)}
    results.append(check(numbers(rb.parser_edit_answer(table)) == derived,
                         "requirement table: pitch derived from the margin"))
    prose = "I need a flat mounting plate, 80 by 60 mm and 6 mm thick."
    results.append(check(rb.parser_edit_answer(prose) == rb.parser_answer(prose, derive=True)
                         and "```" not in rb.parser_edit_answer(prose), "prose: the fallback's refusal"))
    # The provider reads the prompt only: answer() never passes it the Spec.
    src = Path(rb.__file__).read_text(encoding="utf-8")
    results.append(check(re.search(r'"parser-edit":\s+return parser_edit_answer\(prompt\), local', src) is not None,
                         "answer() calls parser_edit_answer(prompt) with the prompt alone"))
    failed = results.count(False)
    print(f"{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
