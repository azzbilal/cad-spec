"""Second-implementation geometry check of the evaluation answers (post hoc, not registered).

    python audit/replication1_geometry_check.py --out results/training/replication1/independent-geometry.json

It does not import the scorer (cad_spec.measure, cad_spec.rubric). Each saved
answer of the replication and of the original evaluation is executed again
and the solid is tested in two ways:

1. **Comparison with the ideal part.** The nominal plate (box minus four
   through bores at the spec's hole centres) is built independently and the
   volume of the symmetric difference with the answer is measured. An answer
   is NOMINAL when that volume is at most 0.001 mm3: it is the requested
   part, with no extra or missing feature.
2. **Sparse point test.** Bounding box and centring (0.5 mm), volume (3%),
   and point membership at mid thickness around each expected hole centre:
   points 0.25 mm inside the nominal radius must be empty and points 0.25 mm
   outside must be material, in 8 directions.

What this is not. It is a second implementation, not a stricter scorer: it
shares CadQuery and the OpenCascade kernel with the scorer, it takes the
target from the same spec, the point test alone misses things the scorer
catches (a thin membrane in a bore, a second solid, a diameter 0.4 mm too
large) and its 0.25 mm rings are not an exact bound on hole-centre error.
The comparison with the ideal part is the strong test; it says whether a
part is nominal, not whether a non-nominal part should pass. Code is
executed with normal process privileges, so only run it on saved answers
that the project sandbox has already executed.

An answer the scorer passes that is not nominal is listed with its
symmetric-difference volume and its largest hole-centre deviation (distance
from an expected centre to the nearest cylindrical face centre, which is a
face centroid and only equals the axis for a complete bore). The last
section recomputes the registered L2 + L4 comparison counting only nominal
passes, for both splits. That is a sensitivity analysis, not a verdict.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

PAIRS = {
    "replication": ("results/training/replication1/eval/base-rep-run2.jsonl",
                    "results/training/replication1/eval/adapter-rep.jsonl"),
    "original": ("results/training/run1/eval/base-test.jsonl",
                 "results/training/run1/eval/adapter-test.jsonl"),
}
BOX_TOL, VOL_TOL, RING = 0.5, 0.03, 0.25
NOMINAL_MM3 = 0.001


def code_of(completion: str) -> str:
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", completion, flags=re.S)
    return blocks[-1] if blocks else completion


def check(job: tuple[str, dict]) -> dict:
    completion, s = job
    import cadquery as cq

    ns: dict = {"show_object": lambda *a, **k: None, "__name__": "__model__"}
    try:
        exec(compile(code_of(completion), "<answer>", "exec"), ns)
        result = ns.get("result")
        solid = result.val() if isinstance(result, cq.Workplane) else result
        if not hasattr(solid, "isInside"):
            solid = result.findSolid()
        bb = solid.BoundingBox()
    except BaseException as exc:
        return {"ok": False, "why": f"no solid: {type(exc).__name__}", "nominal": False}
    length, width, thick, dia, margin = s["length"], s["width"], s["thickness"], s["hole_diameter"], s["edge_margin"]
    why = []
    if max(abs(bb.xlen - length), abs(bb.ylen - width), abs(bb.zlen - thick)) > BOX_TOL:
        why.append("bounding box")
    if max(abs(bb.center.x), abs(bb.center.y), abs(bb.center.z)) > BOX_TOL:
        why.append("not centred")
    expected = length * width * thick - 4 * math.pi * (dia / 2) ** 2 * thick
    if abs(solid.Volume() - expected) > VOL_TOL * expected:
        why.append("volume")
    z = bb.center.z
    if not solid.isInside(cq.Vector(bb.center.x, bb.center.y, z)):
        why.append("plate centre is empty")
    hx, hy = length / 2 - margin, width / 2 - margin
    bad_hole = False
    for sx in (-1, 1):
        for sy in (-1, 1):
            for k in range(8):
                a = k * math.pi / 4
                for r, material in ((dia / 2 - RING, False), (dia / 2 + RING, True)):
                    p = cq.Vector(sx * hx + r * math.cos(a), sy * hy + r * math.sin(a), z)
                    if solid.isInside(p) != material:
                        bad_hole = True
    if bad_hole:
        why.append("holes")
    axes = [(f.Center().x, f.Center().y) for f in solid.Faces() if f.geomType() == "CYLINDER"]
    deviation = max(
        min((math.dist((sx * hx, sy * hy), a) for a in axes), default=float("inf"))
         for sx in (-1, 1) for sy in (-1, 1)
    )
    ideal = (
        cq.Workplane("XY").box(length, width, thick).faces(">Z").workplane()
        .pushPoints([(sx * hx, sy * hy) for sx in (-1, 1) for sy in (-1, 1)]).hole(dia).val()
    )
    try:
        sym = solid.cut(ideal).Volume() + ideal.cut(solid).Volume()
    except BaseException:
        sym = float("inf")
    return {"ok": not why, "why": ", ".join(why), "deviation": round(deviation, 4),
            "nominal": sym <= NOMINAL_MM3, "symmetric_difference_mm3": round(sym, 4)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    import compare_training as ct
    from cad_spec.tasks import make_test_split
    from replication_split import make_replication_split

    specs = {s.id: s for s in make_replication_split() + make_test_split()}
    report = {
        "method": "comparison with the independently built ideal part, plus a sparse point test; scorer not imported",
        "nominal_tolerance_mm3": NOMINAL_MM3,
        "point_test_mm": {"ring_offset": RING, "scorer_position_tolerance_inclusive": 0.5},
        "splits": {},
    }
    with mp.get_context("fork").Pool(4, maxtasksperchild=40) as pool:
        for split, names in PAIRS.items():
            nominal_only: dict[str, dict] = {}
            files = []
            for role, name in zip(("base", "adapter"), names, strict=True):
                rows = [r for r in map(json.loads, (ROOT / name).open(encoding="utf-8")) if "tier" in r]
                jobs = [(r["completion"], {k: getattr(specs[r["spec_id"]], k) for k in
                                           ("length", "width", "thickness", "hole_diameter", "edge_margin")})
                        for r in rows]
                verdicts = pool.map(check, jobs, chunksize=4)
                table = {"scorer_pass": 0, "scorer_pass_nominal": 0, "scorer_pass_not_nominal": [],
                         "scorer_fail": 0, "scorer_fail_but_nominal": [],
                         "point_test_agrees": 0, "point_test_disagrees": []}
                nominal_only[role] = {}
                for r, v in zip(rows, verdicts, strict=True):
                    scorer = r["reward"] == 1.0
                    key = f"{r['tier']} {r['spec_id']}"
                    nominal_only[role][(r["tier"], r["spec_id"])] = int(scorer and v["nominal"])
                    if scorer:
                        table["scorer_pass"] += 1
                        if v["nominal"]:
                            table["scorer_pass_nominal"] += 1
                        else:
                            table["scorer_pass_not_nominal"].append({
                                "task": key, "symmetric_difference_mm3": v.get("symmetric_difference_mm3"),
                                "hole_centre_deviation_mm": v.get("deviation")})
                    else:
                        table["scorer_fail"] += 1
                        if v["nominal"]:
                            table["scorer_fail_but_nominal"].append({"task": key})
                    if scorer == v["ok"]:
                        table["point_test_agrees"] += 1
                    else:
                        table["point_test_disagrees"].append({"task": key, "scorer": scorer, "why": v["why"]})
                files.append({"file": name, "answers": len(rows), **table})
                print(split, role, {k: (v if isinstance(v, int) else len(v)) for k, v in table.items()})
            sens = ct.paired(nominal_only["base"], nominal_only["adapter"], ct.PRIMARY)
            report["splits"][split] = {"files": files, "l2_l4_counting_only_nominal_passes": sens}
            print(split, "L2+L4 nominal only:", round(100 * sens["difference"], 1),
                  [round(100 * x, 1) for x in sens["ci95"]])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
