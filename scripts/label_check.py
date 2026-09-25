# ruff: noqa: E402
"""Write a human label-check file: a random sample of classified failures,
each with all the evidence a reviewer needs to agree or disagree.

    python scripts/label_check.py results/rescored/0.4.0/*.jsonl --seed 20260925

Reads the failure labels from results/failure-modes-<version>.json (run
scripts/failure_modes.py first) and the answers from the run files. Every
entry is keyed by its run id, so code and measurements always come from the
same answer (the first, hand-made version of this check mixed two phi-4 runs
and showed one run's code next to the other's measurements).

Each entry shows: the label; the correct hole centres worked out from the
spec; where the plate actually is (global min..max per axis, not just its
size); the measured hole centres; the error, if any; rev A for change orders;
and, folded, the full prompt and the full code.

Use a NEW seed for every check. A sample that was used to fix the rules
cannot measure them afterwards.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.rubric import SCORER_VERSION
from cad_spec.tasks import TASKS, edit_source, make_splits, prompt_for
from summarize_results import load

MECHANICAL = {"API error", "degenerate loop", "cut off", "syntax error", "timeout"}
DETERMINISTIC = {"reference", "parser-copy", "parser-derive", "parser-template", "rev-a"}


def fmt_range(lo_hi: list[float]) -> str:
    return f"{lo_hi[0]:g} .. {lo_hi[1]:g}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="the run files the failure analysis was built from")
    ap.add_argument("--failures", default=str(ROOT / "results" / f"failure-modes-{SCORER_VERSION}.json"))
    ap.add_argument("--seed", type=int, required=True, help="use a new seed for every check")
    ap.add_argument("-n", type=int, default=30)
    ap.add_argument("--out", default="label_check.md")
    args = ap.parse_args()

    failures = json.loads(Path(args.failures).read_text())
    pool = [r for r in failures["rows"] if r["label"] not in MECHANICAL and r["model"] not in DETERMINISTIC]
    if "run_id" not in (pool[0] if pool else {"run_id": 1}):
        raise SystemExit("this failure file predates run ids; rerun scripts/failure_modes.py first")
    sample = random.Random(args.seed).sample(pool, min(args.n, len(pool)))

    _, groups, _ = load(args.paths)
    answers: dict[tuple, dict] = {}
    ambiguous: set[tuple] = set()
    for (run_id, tier), rows in groups.items():
        for r in rows:
            key = (run_id, tier, r["spec_id"], r.get("rollout", 0))
            if key in answers:
                ambiguous.add(key)  # never guess which answer the evidence belongs to
            answers[key] = r
    train, evals = make_splits()
    specs = {s.id: s for s in [*train, *evals, *TASKS]}
    eval_ids = {s.id for s in evals}

    out = [f"# Label check: {len(sample)} random failed answers (seed {args.seed})", "",
           f"Scorer {SCORER_VERSION}. Pool: {len(pool)} failed answers with judgement labels "
           "(mechanical failures such as API errors and syntax errors are left out).", "",
           "For each: does the LABEL name what the code and measurements show? The correct hole "
           "centres are worked out for you: (+/- pitch_x / 2, +/- pitch_y / 2). A plate whose X or Y "
           "range is not centred on 0 has been moved.", ""]
    for i, r in enumerate(sample, 1):
        s = specs[r["spec_id"]]
        key = (r["run_id"], r["tier"], r["spec_id"], r.get("rollout", 0))
        ans = {} if key in ambiguous else answers.get(key, {})
        split = "eval" if s.id in eval_ids else "train"
        prompt = ans.get("prompt") or prompt_for(s, r["tier"], split)
        out += [f"## {i}. {r['label']}",
                f"- model: {r['model']}  tier: {r['tier']}  spec: {s.id}  run: {r['run_id']}",
                f"- spec: plate {s.length} x {s.width} x {s.thickness}, hole {s.hole_diameter}, "
                f"pitch {s.pitch_x} x {s.pitch_y}, margin {s.edge_margin}",
                f"- correct hole centres: (+/-{s.pitch_x / 2:g}, +/-{s.pitch_y / 2:g})"]
        if r["tier"] == "L4":
            a = edit_source(s)
            out.append(f"- rev A (before the change): plate {a.length} x {a.width} x {a.thickness}, "
                       f"hole {a.hole_diameter}, pitch {a.pitch_x} x {a.pitch_y}, margin {a.edge_margin}")
        if "plate_bbox" in r:
            bb = r["plate_bbox"]
            out.append(f"- plate position: X {fmt_range(bb['x'])}   Y {fmt_range(bb['y'])}   Z {fmt_range(bb['z'])}")
        if "holes" in r:
            out.append(f"- measured hole centres: {[tuple(h) for h in r['holes']]}")
        if r.get("api_kind"):
            out.append(f"- API error kind: {r['api_kind']}")
        if r.get("error"):
            out.append(f"- error: {r['error'][:200]}")
        if key in ambiguous:
            out.append("- WARNING: several answers share this run/tier/spec/rollout; code not shown")
        elif not ans:
            out.append("- WARNING: answer not found in the run files given")
        fence = "````"  # answers contain their own ``` fences
        out += ["", "<details><summary>full prompt</summary>", "", fence, prompt.strip(), fence, "</details>", "",
                "<details><summary>full code</summary>", "", fence, (ans.get("completion") or "").strip(), fence,
                "</details>", "", "- [ ] agree   - [ ] disagree   note:", ""]
    Path(args.out).write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {args.out}: {len(sample)} answers from a pool of {len(pool)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
