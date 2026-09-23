"""Command line: score an answer or print a prompt, no verifiers needed.

    python -m cad_spec prompt gen-0001 --tier L3 --split eval
    python -m cad_spec score gen-0001 answer.py          # human-readable report
    python -m cad_spec score gen-0001 answer.py --json   # machine-readable
    python -m cad_spec sandbox                            # what isolation applies

Exit codes: 0 full credit, 1 partial or zero credit, 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .measure import sandbox_info
from .rubric import SCORER_VERSION, score
from .tasks import TASKS, TIERS, make_splits, prompt_for


def _spec(spec_id: str):
    train, evals = make_splits()
    table = {s.id: s for s in [*train, *evals, *TASKS]}
    if spec_id not in table:
        raise SystemExit(f"unknown spec id {spec_id!r} (e.g. {evals[0].id}, {TASKS[0].id})")
    return table[spec_id]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m cad_spec")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("spec_id")
    p.add_argument("--tier", default="L0", choices=list(TIERS))
    p.add_argument("--split", default="train", choices=["train", "eval"])
    s = sub.add_parser("score")
    s.add_argument("spec_id")
    s.add_argument("answer", help="file with the model's answer, or - for stdin")
    s.add_argument("--json", action="store_true")
    sub.add_parser("sandbox")
    args = ap.parse_args(argv)

    if args.cmd == "prompt":
        print(prompt_for(_spec(args.spec_id), args.tier, args.split))
        return 0
    if args.cmd == "sandbox":
        print(json.dumps(sandbox_info(), indent=2))
        return 0
    text = sys.stdin.read() if args.answer == "-" else Path(args.answer).read_text(encoding="utf-8")
    report = score(text, _spec(args.spec_id))
    if args.json:
        print(json.dumps({"scorer_version": SCORER_VERSION, **asdict(report)}, indent=2))
    else:
        print(report.summary)
    return 0 if report.reward >= 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
