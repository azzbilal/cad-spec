# ruff: noqa: E402
"""Self-test for scripts/failure_modes.py: one known answer per failure mode.

Each case is a hand-written CadQuery answer with a known failure, scored by
the real scorer and classified by the real classifier. Needs only cadquery:

    python scripts/test_failure_modes.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.rubric import score
from cad_spec.tasks import Spec, edit_source, make_splits, reference_solution
from failure_modes import api_error_kind

CORNERS = ((-1, -1), (-1, 1), (1, -1), (1, 1))
LOOP = "r = (cq.Workplane('XY')\n" + "    .rect(5.0, 5.0)\n" * 80


def fenced(body: str) -> str:
    return f"```python\nimport cadquery as cq\n{body}\n```"


def at_points(s: Spec, pts: list[tuple[float, float]], d: float | None = None, dz: float = 0) -> str:
    return fenced(f"result = (cq.Workplane('XY').box({s.length}, {s.width}, {s.thickness})"
                  f".faces('>Z').workplane().pushPoints({pts}).hole({d or s.hole_diameter}))\n"
                  f"result = result.translate((0, 0, {dz}))")


def stacked(s: Spec) -> str:
    holes = f".hole({s.hole_diameter})" * 4
    return fenced(f"result = cq.Workplane('XY').box({s.length}, {s.width}, {s.thickness})"
                  f".faces('>Z').workplane(){holes}")


def cases() -> list[tuple[str, Spec, str, str | None, dict]]:
    _, evals = make_splits()
    s = next(x for x in evals if x.edge_margin < min(x.pitch_x, x.pitch_y) / 2 - 3)
    hx, hy, m = s.pitch_x / 2, s.pitch_y / 2, s.edge_margin
    nominal = [(a * hx, b * hy) for a, b in CORNERS]
    out = [
        ("L1", s, reference_solution(s), None, {}),
        ("L1", s, stacked(s), "holes stacked at one point", {}),
        ("L1", s, at_points(s, [(0, 0), (2 * hx, 0), (0, 2 * hy), (2 * hx, 2 * hy)]),
         "pattern anchored at a corner", {}),
        ("L1", s, at_points(s, [(a * (hx - m), b * (hy - m)) for a, b in CORNERS]), "margin applied twice", {}),
        ("L1", s, at_points(s, [(a * hy, b * hx) for a, b in CORNERS]), "X and Y swapped", {}),
        ("L1", s, at_points(s, [(a * hx, b * (hy - 2.5)) for a, b in CORNERS]), "one axis misplaced", {}),
        ("L1", s, at_points(s, [*nominal[:2], (hx - 3.1, -hy + 2.2), (hx - 2.2, hy - 3.3)]),
         "some holes right, some wrong", {}),
        ("L1", s, at_points(s, nominal, d=s.hole_diameter + 1), "wrong hole diameter", {}),
        ("L1", s, at_points(s, nominal, dz=3), "off Z datum", {}),
        ("L1", s, fenced("result = cq.Workplane('XY').box(1,2"), "syntax error", {}),
        ("L1", s, fenced("result = cq.Workplane('XY').box(1,1,1).nonexistent()"), "CadQuery API error", {}),
        ("L1", s, LOOP, "degenerate loop", {"finish": "length"}),
        ("L1", s, "", "API error", {"api": "HTTPError 500"}),
    ]
    # Label check, September 2026: real stacked patterns the old rule missed,
    # and a real single-hole answer that is NOT stacked (cumulative offsets).
    d = s.hole_diameter
    box = f"cq.Workplane('XY').box({s.length}, {s.width}, {s.thickness})"
    plate = box + ".faces('>Z').workplane()"
    moves = "".join(f".hole({d}).translate(({a * hx}, {b * hy}))" for a, b in CORNERS)
    out.append(("L1", s, fenced(f"result = ({plate}.center(0, 0){moves})"), "holes stacked at one point", {}))
    redrill = "".join(f".faces('>Z').workplane().hole({d})" for _ in range(4))
    out.append(("L1", s, fenced(f"result = ({box}{redrill})"), "holes stacked at one point", {}))
    g = next(v for v in evals if v.id == "gen-0166")
    sx, sy = g.length / 2 - g.pitch_x / 2, g.width / 2 - g.pitch_y / 2
    offsets = [(-sx, -sy), (g.pitch_x, 0), (0, g.pitch_y), (g.pitch_x, g.pitch_y)]
    cumulative = "".join(f".transformed(offset=({ox}, {oy}, 0)).hole({g.hole_diameter})" for ox, oy in offsets)
    out.append(("L3", g, fenced(f"result = (cq.Workplane('XY').box({g.length}, {g.width}, {g.thickness})"
                                f".faces('>Z').workplane(){cumulative})"), "holes misplaced (other)", {}))

    # Fresh human label check, September 2026 (seed 20260926): the two misses.
    h = next(v for v in evals if v.id == "gen-0212")
    out.append(("L1", h, fenced(f"result = (cq.Workplane('XY').box({h.length}, {h.width}, {h.thickness})"
                                ".faces('>Z').workplane().transformed(location=cq.Location("
                                "cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), cq.Vector(0, 0, 0))).hole(7.0))"),
                "CadQuery API error", {}))
    k = next(v for v in evals if v.id == "gen-0037")
    ka = edit_source(k)
    out.append(("L4", k, fenced(f"result = (cq.Workplane('XY').box({k.length}, {k.width}, {k.thickness})"
                                f".faces('>Z').workplane().rect({ka.pitch_x}, {ka.pitch_y}, forConstruction=True)"
                                f".vertices().hole({k.hole_diameter}))"),
                "change not propagated to pitch", {}))

    # External audit of the publish patch, September 2026: regression cases.
    k2 = next(v for v in evals if v.id == "gen-0037")
    k2a = edit_source(k2)
    bare = f"result = cq.Workplane('XY').box({k2.length}, {k2.width}, {k2.thickness})"
    out.append(("L4", k2, fenced(f"# rev A used .rect({k2a.pitch_x}, {k2a.pitch_y})\n{bare}"), "no holes", {}))
    out.append(("L4", k2, fenced(f"# .rect(1..2,3)\n{bare}"), "no holes", {}))
    diag = [(-hx, -hy), (hx, hy), (-hx / 3, hy / 3), (hx / 3, -hy / 3)]
    out.append(("L1", s, at_points(s, diag), "some holes right, some wrong", {}))
    plain = f"result = cq.Workplane('XY').box({s.length}, {s.width}, {s.thickness})"
    out.append(("L1", s, fenced(f"n = int('abc')\n{plain}"),
                "Python error in model code", {}))
    out.append(("L1", s, fenced(f"result = (cq.Workplane('XY').box({s.length}, {s.width}, {s.thickness})"
                                f".faces('>Z').workplane().rarray(2, 2, {s.pitch_x / 2}, {s.pitch_y / 2}).hole(5))"),
                "CadQuery API error", {}))

    x = next(v for v in evals
             if (edit_source(v).pitch_x, edit_source(v).pitch_y) != (v.pitch_x, v.pitch_y)
             and (edit_source(v).length, edit_source(v).width) != (v.length, v.width))
    rev_a = edit_source(x)
    stale = [(a * rev_a.pitch_x / 2, b * rev_a.pitch_y / 2) for a, b in CORNERS]
    out.append(("L4", x, reference_solution(rev_a), "change order ignored", {}))
    out.append(("L4", x, at_points(x, stale), "change not propagated to pitch", {}))
    return out


def superseded_runs_are_not_counted() -> bool:
    """A failure in an old run, fixed by a later clean rerun, must not be
    counted (the September 2026 board double-counted phi-4's L3 reruns)."""
    _, evals = make_splits()
    s = evals[0]
    bad = score(stacked(s), s)
    good = score(reference_solution(s), s)
    with tempfile.TemporaryDirectory() as tmp:
        for run_id, rep_ in (("20260101T000000Z", bad), ("20260102T000000Z", good)):
            row = {"run_id": run_id, "tier": "L1", "spec_id": s.id, "rollout": 0, "reward": rep_.reward,
                   "built": rep_.parsed, "error": rep_.error, "checks": {c.name: c.passed for c in rep_.checks},
                   "completion": stacked(s) if rep_ is bad else reference_solution(s)}
            meta = {"meta": {"run_id": run_id, "model": "dup"}}
            (Path(tmp) / f"{run_id}.jsonl").write_text("\n".join(json.dumps(x) for x in [meta, row]) + "\n")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "failure_modes.py"),
                               *sorted(str(p) for p in Path(tmp).glob("*.jsonl")), "--out", tmp],
                              check=False, capture_output=True, text=True)
        if proc.returncode:
            print(proc.stderr[-1500:])
            return False
        result = json.loads(next(Path(tmp).glob("failure-modes-*.json")).read_text())
    return result["totals"].get("dup") == 1 and not result["rows"]


def main() -> int:
    rows, want = [], []
    for tier, spec, text, label, extra in cases():
        r = score(text, spec)
        rows.append({"run_id": "T", "tier": tier, "spec_id": spec.id, "rollout": len(rows), "reward": r.reward,
                     "built": r.parsed, "error": r.error, "checks": {c.name: c.passed for c in r.checks},
                     "completion": text, "finish_reason": extra.get("finish", "stop"),
                     "truncated": extra.get("finish") == "length", "api_error": extra.get("api")})
        if label:
            want.append((len(rows) - 1, label))
    meta = {"meta": {"run_id": "T", "model": "synthetic", "max_tokens": 1024}}
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp) / "run.jsonl"
        run.write_text("\n".join(json.dumps(r) for r in [meta, *rows]) + "\n")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "failure_modes.py"), str(run), "--out", tmp],
                              check=False, capture_output=True, text=True)
        if proc.returncode:
            print(proc.stderr[-2000:])
            return 1
        result = json.loads(next(Path(tmp).glob("failure-modes-*.json")).read_text())
    by_rollout = {r["rollout"]: r["label"] for r in result["rows"]}  # match by answer, not by order
    api = [r.get("api_kind") for r in result["rows"] if r["label"] == "CadQuery API error"]
    if sorted(api) != ["no matching signature for Location()", "no such method: Workplane.nonexistent",
                       "non-integer count"]:
        print(f"[BAD] API error kind: {api}")
        return 1
    print("[ok ] API error kinds: no such method, no matching signature")
    kinds = {
        "execution failed: ValueError: No pending wires present": "operation needs a sketch or wire",
        "execution failed: TypeError: 'float' object cannot be interpreted as an integer": "non-integer count",
        "execution failed: ValueError: Do not know how to handle until argument of type <class 'str'>":
            "invalid extrude or cut argument",
    }
    for err, want_kind in kinds.items():
        got_kind = api_error_kind(err)
        if got_kind != want_kind:
            print(f"[BAD] {err!r} -> {got_kind!r}, want {want_kind!r}")
            return 1
    print("[ok ] API error kinds from the label check: wires, integer counts, extrude arguments")
    bad = 0
    for rollout, w in want:
        g = by_rollout.get(rollout, "(not classified)")
        bad += w != g
        print(f"[{'ok ' if w == g else 'BAD'}] want {w:32s} got {g}")
    print(f"\n{len(want) - bad}/{len(want)} failure modes classified correctly")
    dedup = superseded_runs_are_not_counted()
    print(f"[{'ok ' if dedup else 'BAD'}] a failure superseded by a clean rerun is not counted")
    return 1 if bad or not dedup else 0


if __name__ == "__main__":
    raise SystemExit(main())
