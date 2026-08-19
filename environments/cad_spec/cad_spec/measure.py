"""Build a CadQuery script and extract the measurements a spec can be checked against.

This module is deliberately dumb about specs. It answers one question:
"given a piece of code, what geometry actually came out?"
Everything spec-related lives in rubric.py.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any


CODE_BLOCK = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)


class BuildError(Exception):
    """Model code did not produce a usable solid."""


@dataclass
class Hole:
    diameter: float
    x: float
    y: float
    depth: float


@dataclass
class Measurements:
    length: float          # bbox X
    width: float           # bbox Y
    thickness: float       # bbox Z
    volume: float          # mm^3
    solid_count: int       # >1 means disconnected pieces
    holes: list[Hole] = field(default_factory=list)

    @property
    def hole_count(self) -> int:
        return len(self.holes)


def extract_code(completion: str) -> str:
    """Pull python out of a model response. Falls back to the raw text."""
    blocks = CODE_BLOCK.findall(completion)
    if blocks:
        return max(blocks, key=len).strip()
    return completion.strip()


def build(code: str) -> Any:
    """Exec model code and return the object bound to `result`.

    Not a security boundary. Prime's sandbox provides isolation; this only
    stops a bad model response from taking down the rollout.
    """
    import cadquery as cq

    namespace: dict[str, Any] = {"cq": cq, "cadquery": cq, "math": math}
    try:
        exec(compile(code, "<model>", "exec"), namespace)
    except Exception as exc:  # noqa: BLE001 - any failure is a build failure
        raise BuildError(f"execution failed: {type(exc).__name__}: {exc}") from exc

    obj = namespace.get("result")
    if obj is None:
        raise BuildError("code did not define `result`")

    try:
        solid = obj.val() if hasattr(obj, "val") else obj
    except Exception as exc:  # noqa: BLE001
        raise BuildError(f"could not resolve result to a shape: {exc}") from exc

    if not hasattr(solid, "Volume"):
        raise BuildError(f"`result` is not a shape (got {type(obj).__name__})")

    return solid


def measure(solid: Any) -> Measurements:
    """Extract features from a built solid."""
    try:
        bb = solid.BoundingBox()
        volume = solid.Volume()
        solids = solid.Solids()
    except Exception as exc:  # noqa: BLE001
        raise BuildError(f"shape could not be measured: {exc}") from exc

    if volume <= 0:
        raise BuildError("shape has zero or negative volume")

    holes: list[Hole] = []
    for face in solid.Faces():
        if face.geomType() != "CYLINDER":
            continue
        fbb = face.BoundingBox()
        # A full internal bore spans 2r in both X and Y; a fillet or an
        # external round spans less than that in one direction.
        if not math.isclose(fbb.xlen, fbb.ylen, rel_tol=0.02):
            continue
        centre = face.Center()
        holes.append(
            Hole(
                diameter=round((fbb.xlen + fbb.ylen) / 2, 4),
                x=round(centre.x, 4),
                y=round(centre.y, 4),
                depth=round(fbb.zlen, 4),
            )
        )

    return Measurements(
        length=round(bb.xlen, 4),
        width=round(bb.ylen, 4),
        thickness=round(bb.zlen, 4),
        volume=round(volume, 4),
        solid_count=len(solids),
        holes=holes,
    )


def build_and_measure(completion: str) -> Measurements:
    return measure(build(extract_code(completion)))
