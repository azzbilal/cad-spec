"""One part family, five prompt tiers. Not many part types (yet).

Family: a rectangular mounting plate with a 4-hole bolt pattern, holes on a
rectangular pitch, inset from each corner by an equal edge margin.

Tiers are separate tasks over the SAME geometry and the SAME scorer, so a
score difference between tiers isolates how the requirement was stated, not
what was built. Report them separately; never average them together.

  L0 template   fill ??? in a given CadQuery template (numeric copy task)
  L1 spec       requirement table incl. pitch, no template, no operations
  L2 derive     requirement table WITHOUT pitch: derive it from the margin
  L3 prose      free-text request, drawing-note or email style; eval uses
                wording templates that never appear in train (held-out phrasing)
  L4 edit       an existing rev-A model plus an engineering change order;
                output the full rev-B model (controlled edit)
"""

from __future__ import annotations

import math
import random
import zlib
from dataclasses import asdict, dataclass, replace
from typing import Any


@dataclass(frozen=True)
class Spec:
    id: str
    length: float        # mm, X
    width: float         # mm, Y
    thickness: float     # mm, Z
    hole_diameter: float # mm
    edge_margin: float   # mm, hole centre to nearest two edges
    hole_count: int = 4

    @property
    def pitch_x(self) -> float:
        return self.length - 2 * self.edge_margin

    @property
    def pitch_y(self) -> float:
        return self.width - 2 * self.edge_margin

    @property
    def ideal_volume(self) -> float:
        plate = self.length * self.width * self.thickness
        bores = self.hole_count * math.pi * (self.hole_diameter / 2) ** 2 * self.thickness
        return plate - bores

    def to_prompt(self) -> str:
        return PROMPT_TEMPLATE.format(**asdict(self), pitch_x=self.pitch_x, pitch_y=self.pitch_y)


PROMPT_TEMPLATE = """\
Fill in the CadQuery template below so the part meets every requirement.

REQUIREMENTS
  R1  Overall length (X):        {length} mm
  R2  Overall width (Y):         {width} mm
  R3  Plate thickness (Z):       {thickness} mm
  R4  Fastener holes:            {hole_count} off, through, {hole_diameter} mm diameter
  R5  Hole pattern:              rectangular, {pitch_x} mm x {pitch_y} mm centres
  R6  Edge margin:               {edge_margin} mm from hole centre to each nearest edge

TEMPLATE (replace each ??? with the correct number; change nothing else):

import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(???, ???, ???)
    .faces(">Z").workplane()
    .rect(???, ???, forConstruction=True)
    .vertices()
    .hole(???)
)

box() takes (length_x, width_y, thickness_z). rect() takes the hole pattern
centre distances (pitch_x, pitch_y). hole() takes a DIAMETER, not a radius.
The plate is centred on the origin.

The completed template is the ENTIRE answer: a runnable Python module, with
`import` and `result` at column zero exactly as shown above. Substitute the
numbers and change nothing else. Do not add loops, extra holes, extra
features, comments, or any further operations after the closing parenthesis.
"""


TASKS: list[Spec] = [
    Spec("plate-01", 80.0, 60.0, 6.0, 6.5, 10.0),
    Spec("plate-02", 120.0, 80.0, 8.0, 8.5, 12.0),
    Spec("plate-03", 60.0, 60.0, 4.0, 5.5, 8.0),
    Spec("plate-04", 100.0, 40.0, 5.0, 6.5, 9.0),
    Spec("plate-05", 150.0, 100.0, 10.0, 10.5, 15.0),
    Spec("plate-06", 70.0, 50.0, 3.0, 4.5, 7.0),
    Spec("plate-07", 90.0, 90.0, 6.0, 8.5, 12.5),
    Spec("plate-08", 200.0, 120.0, 12.0, 13.0, 20.0),
    Spec("plate-09", 55.0, 45.0, 4.0, 5.0, 7.5),
    Spec("plate-10", 110.0, 70.0, 7.0, 9.0, 11.0),
]


def reference_solution(spec: Spec) -> str:
    """A known-good answer. Used to prove the rubric scores correct work highly."""
    return f"""
import cadquery as cq
result = (
    cq.Workplane("XY")
    .box({spec.length}, {spec.width}, {spec.thickness})
    .faces(">Z").workplane()
    .rect({spec.pitch_x}, {spec.pitch_y}, forConstruction=True)
    .vertices()
    .hole({spec.hole_diameter})
)
"""


SAMPLE_SEED = 20260813
N_TRAIN = 200
N_EVAL = 30


def sample_spec(rng: random.Random, idx: int) -> Spec:
    """Draw one feasible plate from the family distribution, on a half-mm grid.

    Feasibility rules keep every sampled spec buildable and plate-like:
    bores clear the edges (margin >= radius + 2 mm, capped at 25 mm), the
    pitch always leaves >= 4 mm of web between bore walls and the rim, and
    stock is at most a fifth of the smaller face dimension. The margin range
    uses an inclusive half-mm grid that can never collapse to an empty
    randrange() call.
    """
    for _ in range(200):
        length = rng.randrange(80, 441) / 2.0        # 40..220 mm, 0.5 grid
        width = rng.randrange(60, 321) / 2.0         # 30..160 mm
        thickness = rng.randrange(6, 29) / 2.0       # 3..14 mm
        d_max = min(13.0, width / 2 - 6)
        hole_diameter = rng.randrange(8, int(d_max * 2)) / 2.0
        m_min = max(5.0, hole_diameter / 2 + 2)
        m_max = min(25.0, (length - hole_diameter - 4) / 2, (width - hole_diameter - 4) / 2)
        if m_max < m_min or thickness > min(length, width) / 5:
            continue
        lo = math.ceil(m_min * 2 - 1e-9)
        hi = math.floor(m_max * 2 + 1e-9)
        if hi < lo:
            continue
        margin = rng.randrange(lo, hi + 1) / 2.0
        return Spec(f"gen-{idx:04d}", length, width, thickness, hole_diameter, margin)
    raise RuntimeError("infeasible sampler run")


def make_splits(seed: int = SAMPLE_SEED) -> tuple[list[Spec], list[Spec]]:
    """Deterministic train/eval split. Eval stratifies size extremes by area.

    Eval takes the 10 smallest-area specs, the 10 largest, and 10 evenly
    spaced mid-range specs; the remaining 200 form the shuffled train set.
    Same seed in, same splits out - on any platform, any Python.
    """
    rng = random.Random(seed)
    pool = [sample_spec(rng, i) for i in range(N_TRAIN + N_EVAL)]
    pool.sort(key=lambda s: s.length * s.width)
    third = N_EVAL // 3
    eval_specs = (
        pool[:third]
        + pool[-third:]
        + pool[third:-third:N_TRAIN // third][: N_EVAL - 2 * third]
    )
    eval_ids = {s.id for s in eval_specs}
    train_specs = [s for s in pool if s.id not in eval_ids]
    rng.shuffle(train_specs)
    return train_specs, eval_specs


# --- locked test split ---------------------------------------------------------
#
# The 30 eval specs shaped the leaderboard, the failure taxonomy and the
# hint/feedback experiment, so a training claim judged on them would inherit
# those decisions. The test split is drawn with its own seed, disjoint from
# every train and eval spec by parameters, locked by fingerprint BEFORE any
# training, and evaluated once, for the final comparison
# (docs/EVALUATION_PROTOCOL.md). Changing it changes the fingerprint and fails
# the test suite.

TEST_SEED = 20260927
N_TEST = 60
TEST_SPLIT_SHA256 = "019d197efecedc079209fcb5900c7d5b2ff894481bc6cc85954826070c30c51b"


def _params(spec: Spec) -> tuple[float, ...]:
    return (spec.length, spec.width, spec.thickness, spec.hole_diameter, spec.edge_margin)


def make_test_split(seed: int = TEST_SEED, n: int = N_TEST) -> list[Spec]:
    """The locked test split: `n` feasible specs, none sharing parameters with
    any train or eval spec or with each other. Ids are test-0001 upwards."""
    train, evals = make_splits()
    seen = {_params(s) for s in train + evals}
    rng = random.Random(seed)
    out: list[Spec] = []
    i = 0
    while len(out) < n:
        spec = sample_spec(rng, i)
        i += 1
        if _params(spec) in seen:
            continue
        seen.add(_params(spec))
        out.append(replace(spec, id=f"test-{len(out) + 1:04d}"))
    return out


def split_fingerprint(specs: list[Spec]) -> str:
    """SHA-256 over the ids and parameters of a split, in order."""
    import hashlib
    import json

    canon = json.dumps([[s.id, *_params(s)] for s in specs], separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


# --- tiers -------------------------------------------------------------------

TIERS = ("L0", "L1", "L2", "L3", "L4")


def is_feasible(spec: Spec) -> bool:
    """The sampler's own feasibility rules, as a predicate (used for edits)."""
    r = spec.hole_diameter / 2
    return (
        spec.edge_margin >= max(5.0, r + 2) - 1e-9
        and spec.edge_margin <= 25.0 + 1e-9
        and spec.pitch_x - spec.hole_diameter >= 4 - 1e-9
        and spec.pitch_y - spec.hole_diameter >= 4 - 1e-9
        and spec.thickness <= min(spec.length, spec.width) / 5 + 1e-9
        and spec.hole_diameter >= 4.0
    )


def _fmt(x: float) -> str:
    """80.0 -> '80', 6.5 -> '6.5'. Prose reads like a drawing, not a repr."""
    return f"{x:g}"


_SPEC_TABLE = """\
Write a CadQuery Python module that builds the part below and binds the
finished solid to a variable named `result`.

REQUIREMENTS
  R1  Overall length (X):        {length} mm
  R2  Overall width (Y):         {width} mm
  R3  Plate thickness (Z):       {thickness} mm
  R4  Fastener holes:            {hole_count} off, through, {hole_diameter} mm diameter
{pitch_line}  R6  Edge margin:               {edge_margin} mm from hole centre to each nearest edge

The plate is centred on the origin with its thickness along Z.
"""

_PITCH_LINE = "  R5  Hole pattern:              rectangular, {pitch_x} mm x {pitch_y} mm centres\n"
_DERIVE_LINE = "  R5  Hole pattern:              rectangular, one hole near each corner\n"

# Wording templates for L3. Indices in _PROSE_TRAIN never appear in eval and
# vice versa: eval measures unseen PHRASING, not only unseen numbers.
_PROSE = (
    # 0 casual request
    "I need a flat mounting plate, {L} by {W} mm and {T} mm thick. Put a "
    "{D} mm through hole near each of the four corners, with every hole "
    "centre {M} mm in from both of its nearest edges. Keep it centred on the "
    "origin. Write it in CadQuery and assign the part to `result`.",
    # 1 drawing title block + notes
    "DRAWING NOTES\nPLATE {L} x {W} x {T} THK (MM)\n4X \u00d8{D} THRU\n"
    "HOLE CENTRES {M} FROM ADJACENT EDGES, TYP 4 PL\nPART CENTRED ON ORIGIN, "
    "THICKNESS ALONG Z\n\nModel this in CadQuery; the solid must be bound to `result`.",
    # 2 bolt-pattern first
    "Model a rectangular bolt plate in CadQuery. The four holes are {D} mm "
    "clearance holes, drilled all the way through, on a {PX} x {PY} mm "
    "rectangular pattern centred on the origin. The plate itself is {L} mm "
    "along X, {W} mm along Y and {T} mm along Z. Store the solid in `result`.",
    # 3 purchasing-style spec
    "Supplier spec: bracket plate, material thickness {T} mm, blank size "
    "{L} mm (X) x {W} mm (Y). Four plain holes, diameter {D} mm, through all, "
    "one per corner at {M} mm edge distance in both directions. Origin at the "
    "blank centre. Provide CadQuery with the part in `result`.",
    # 4 HELD OUT: email from a colleague, pitch given, margin implied
    "Hi, could you knock up the adapter plate in CadQuery? Stock is {T} mm "
    "plate cut to {W} mm wide (Y) and {L} mm long (X). It needs four {D} mm "
    "holes straight through, spaced {PX} mm apart along the length and {PY} mm "
    "apart across the width, pattern centred on the plate, plate centred on "
    "the origin. Please leave the finished body in a variable called result.",
    # 5 HELD OUT: inspection-sheet style, radius instead of diameter
    "Inspection criteria for part to be modelled in CadQuery (bind to "
    "`result`): envelope {L} x {W} x {T} mm, centred at (0, 0, 0). Qty 4 "
    "through bores of radius {R} mm. Each bore axis lies {M} mm from the two "
    "closest outer edges. No other features.",
)
_PROSE_TRAIN = (0, 1, 2, 3)
_PROSE_EVAL = (4, 5)


def _stable_pick(key: str, choices: tuple[int, ...]) -> int:
    return choices[zlib.crc32(key.encode()) % len(choices)]


def _prose(spec: Spec, split: str) -> str:
    # The locked test split uses the held-out wording too: training never
    # sees it, whichever held-out set a spec belongs to.
    idx = _stable_pick(spec.id, _PROSE_EVAL if split in ("eval", "test") else _PROSE_TRAIN)
    return _PROSE[idx].format(
        L=_fmt(spec.length), W=_fmt(spec.width), T=_fmt(spec.thickness),
        D=_fmt(spec.hole_diameter), R=_fmt(spec.hole_diameter / 2),
        M=_fmt(spec.edge_margin), PX=_fmt(spec.pitch_x), PY=_fmt(spec.pitch_y),
    )


_EDIT_FIELDS = ("length", "width", "thickness", "hole_diameter", "edge_margin")
_EDIT_LABEL = {
    "length": "overall length (X)",
    "width": "overall width (Y)",
    "thickness": "plate thickness (Z)",
    "hole_diameter": "hole diameter",
    "edge_margin": "edge margin (hole centre to nearest edges)",
}


# Scoring tolerance per editable field (mm), mirrored from rubric.py. An ECO
# must move at least one field clearly outside its tolerance, otherwise the
# unedited rev A already scores full marks and "ignore the change order" is
# rewarded (0.3.x had three such train tasks, e.g. thickness 4.5 -> 5.0).
_ECO_TOL = {"length": 0.5, "width": 0.5, "thickness": 0.5, "hole_diameter": 0.2, "edge_margin": 0.5}
_ECO_CLEARANCE = 0.25


def _eco_is_visible(source: Spec, target: Spec) -> bool:
    return any(
        abs(getattr(source, f) - getattr(target, f)) > _ECO_TOL[f] + _ECO_CLEARANCE
        for f in _EDIT_FIELDS
    )


def edit_source(target: Spec) -> Spec:
    """Rev A for an L4 edit task: `target` with one or two fields changed.

    Deterministic per spec id. Rev A is always feasible, so the starting
    model the prompt shows is itself a valid part, and at least one change
    exceeds its scoring tolerance, so the unedited model cannot pass.
    """
    rng = random.Random(zlib.crc32(("edit:" + target.id).encode()))
    for _ in range(200):
        fields = rng.sample(_EDIT_FIELDS, rng.choice((1, 2)))
        changes: dict[str, Any] = {}
        for f in fields:
            base = getattr(target, f)
            step = rng.choice((-1, 1)) * rng.choice((0.1, 0.15, 0.2, 0.25)) * base
            changes[f] = max(0.5, round((base + step) * 2) / 2)
        source = replace(target, id=target.id + "-revA", **changes)
        if is_feasible(source) and _eco_is_visible(source, target):
            return source
    raise RuntimeError(f"no feasible rev A for {target.id}")


def _edit_prompt(target: Spec) -> str:
    source = edit_source(target)
    lines = [
        f"  - change {_EDIT_LABEL[f]} from {_fmt(getattr(source, f))} mm to {_fmt(getattr(target, f))} mm"
        for f in _EDIT_FIELDS
        if getattr(source, f) != getattr(target, f)
    ]
    return (
        "Below is the current CadQuery model of a mounting plate (rev A).\n\n"
        "```python\n" + reference_solution(source).strip() + "\n```\n\n"
        "ENGINEERING CHANGE ORDER, rev A -> rev B:\n" + "\n".join(lines) + "\n"
        "Every other characteristic stays exactly as in rev A: four through holes, "
        "one per corner, each hole centre at the stated edge margin from its two "
        "nearest edges, part centred on the origin.\n\n"
        "Return the complete rev B CadQuery module with the part bound to `result`."
    )


def prompt_for(spec: Spec, tier: str, split: str = "train") -> str:
    """The prompt text for `spec` at `tier`. `split` selects held-out wording (L3)."""
    if tier == "L0":
        return spec.to_prompt()
    if tier in ("L1", "L2"):
        pitch = _PITCH_LINE.format(pitch_x=spec.pitch_x, pitch_y=spec.pitch_y) if tier == "L1" else _DERIVE_LINE
        return _SPEC_TABLE.format(**asdict(spec), pitch_line=pitch)
    if tier == "L3":
        return _prose(spec, split)
    if tier == "L4":
        return _edit_prompt(spec)
    raise ValueError(f"unknown tier {tier!r}; expected one of {TIERS}")
