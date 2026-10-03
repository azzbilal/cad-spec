"""Independent geometry check of the replication answers (post hoc, not registered).

    python audit/replication1_geometry_check.py --out results/training/replication1/independent-geometry.json

It does not import the scorer (cad_spec.measure, cad_spec.rubric). Each saved
answer is executed again and the solid is tested directly with CadQuery:

- bounding box equal to length x width x thickness and centred on the origin
  (0.5 mm);
- volume equal to the plate minus four through bores (3%);
- point membership: at each of the four expected hole centres, at mid
  thickness, points just inside the nominal radius are empty and points just
  outside are material (0.25 mm either side, 8 directions), and the centre of
  the plate is material.

The expected hole centres come from the spec (edge margin from the two nearest
edges). The verdict of this check is then compared with the recorded all-pass
of every answer, in both directions.

The check is deliberately STRICTER than the scorer on hole position (0.25 mm
against the scorer's inclusive 0.5 mm). For every answer it also measures the
largest distance between an expected hole centre and the nearest cylindrical
face axis, so a disagreement can be read: an answer the scorer passes with a
deviation between 0.25 and 0.5 mm is a "boundary pass", accepted by the
registered tolerance and rejected here. The last section recomputes the
registered L2 + L4 comparison with boundary passes counted as failures, for
the replication split and for the original test split. That is a sensitivity
analysis, not a verdict.
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
        return {"ok": False, "why": f"no solid: {type(exc).__name__}"}
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
    return {"ok": not why, "why": ", ".join(why), "deviation": round(deviation, 4)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    import compare_training as ct
    from cad_spec.tasks import make_test_split
    from replication_split import make_replication_split

    specs = {s.id: s for s in make_replication_split() + make_test_split()}
    report = {"method": "bounding box, volume and point membership; scorer not imported",
              "position_tolerance_mm": {"this_check": RING, "scorer_inclusive": 0.5}, "splits": {}}
    with mp.get_context("fork").Pool(4, maxtasksperchild=40) as pool:
        for split, names in PAIRS.items():
            strict: dict[str, dict] = {}
            files = []
            for role, name in zip(("base", "adapter"), names, strict=True):
                rows = [r for r in map(json.loads, (ROOT / name).open(encoding="utf-8")) if "tier" in r]
                jobs = [(r["completion"], {k: getattr(specs[r["spec_id"]], k) for k in
                                           ("length", "width", "thickness", "hole_diameter", "edge_margin")})
                        for r in rows]
                verdicts = pool.map(check, jobs, chunksize=4)
                table = {"both_pass": 0, "both_fail": 0, "boundary_pass": [], "scorer_pass_check_fail_other": [],
                         "scorer_fail_check_pass": []}
                strict[role] = {}
                for r, v in zip(rows, verdicts, strict=True):
                    scorer = r["reward"] == 1.0
                    key = f"{r['tier']} {r['spec_id']}"
                    strict[role][(r["tier"], r["spec_id"])] = int(scorer and v["ok"])
                    if scorer and v["ok"]:
                        table["both_pass"] += 1
                    elif not scorer and not v["ok"]:
                        table["both_fail"] += 1
                    elif scorer and v["why"] == "holes" and RING <= v["deviation"] <= 0.5 + 1e-6:
                        table["boundary_pass"].append({"task": key, "hole_centre_deviation_mm": v["deviation"]})
                    elif scorer:
                        table["scorer_pass_check_fail_other"].append({"task": key, **v})
                    else:
                        table["scorer_fail_check_pass"].append({"task": key})
                files.append({"file": name, "answers": len(rows), **table})
                print(split, role, {k: (v if isinstance(v, int) else len(v)) for k, v in table.items()})
            sens = ct.paired(strict["base"], strict["adapter"], ct.PRIMARY)
            report["splits"][split] = {"files": files, "l2_l4_with_boundary_passes_as_failures": sens}
            print(split, "L2+L4 strict:", round(100 * sens["difference"], 1), [round(100 * x, 1) for x in sens["ci95"]])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
