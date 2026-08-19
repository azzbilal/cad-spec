"""One part family, parameter variation. Not many part types.

Family: a rectangular mounting plate with a 4-hole bolt pattern, holes on a
rectangular pitch, inset from each corner by an equal edge margin.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict


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

The completed template is the ENTIRE answer. Output exactly those lines with
numbers substituted. Do not add loops, extra holes, extra features, comments,
or any further operations after the closing parenthesis.
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
