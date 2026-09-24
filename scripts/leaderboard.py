# ruff: noqa: E402
"""Build the cad-spec leaderboard: a ranked table and three SVG charts.

    python scripts/leaderboard.py results/rescored/0.4.0/*.jsonl \\
        --failures results/failure-modes-0.4.0.json

Writes results/leaderboard/: leaderboard.md, ranking.svg, heatmap.svg and
(with --failures) fingerprints.svg. Charts are plain SVG, no plotting library
needed, and render directly on GitHub.

Headline score (docs/EVALUATION_PROTOCOL.md): the all-requirements pass rate
averaged over tiers L1 to L4. L0 is excluded because a regex solves it. The
95% interval comes from a bootstrap over specs, keeping each spec's four
tiers together (paired). Deterministic programs (parsers, the reference, the
unedited rev A) are drawn as reference lines, never ranked. A model is marked
PROVISIONAL, and drawn hatched, if any tier is incomplete or has over 5% of
answers cut off by the token budget or failed at the API.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from summarize_results import completeness_problems, load, summarize

HEADLINE_TIERS = ("L1", "L2", "L3", "L4")
ALL_TIERS = ("L0", *HEADLINE_TIERS)
DETERMINISTIC = {"reference", "parser-copy", "parser-derive", "parser-template", "rev-a"}
FONT = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"
# Okabe-Ito, colour-blind safe
PALETTE = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#999999"]
FAILURE_GROUPS = {
    "did not finish": ("API error", "degenerate loop", "cut off"),
    "code did not build": ("syntax error", "CadQuery API error", "no part produced", "timeout", "build failed"),
    "holes not bound to positions": ("holes stacked at one point", "no holes"),
    "hole pattern misread": ("pattern anchored at a corner", "margin applied twice", "X and Y swapped",
                             "pitch read as coordinates", "holes misplaced (other)"),
    "change order not applied": ("change order ignored", "change not propagated to pitch"),
    "gate fired": ("gate: single_solid", "gate: clean_solid", "gate: simple_through_holes",
                   "gate: hole_count_sane", "gate: is_plate"),
    "one dimension wrong": ("wrong plate size", "off Z datum", "wrong hole diameter", "wrong hole count",
                            "material off", "edge margin off", "other"),
}


def per_spec_pass(rows: list[dict]) -> dict[str, float]:
    """All-pass rate per spec, averaging rollouts."""
    acc: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        acc[r["spec_id"]].append(float(bool(r["checks"]) and all(r["checks"].values())))
    return {k: statistics.fmean(v) for k, v in acc.items()}


def headline(tier_rows: dict[str, list[dict]], iters: int = 2000) -> tuple[float, float, float] | None:
    if not all(t in tier_rows for t in HEADLINE_TIERS):
        return None
    per_tier = {t: per_spec_pass(tier_rows[t]) for t in HEADLINE_TIERS}
    specs = sorted(set.intersection(*(set(v) for v in per_tier.values())))
    if not specs:
        return None
    per_spec = [statistics.fmean(per_tier[t][s] for t in HEADLINE_TIERS) for s in specs]
    rng = random.Random(0)
    boots = sorted(statistics.fmean(rng.choices(per_spec, k=len(per_spec))) for _ in range(iters))
    return statistics.fmean(per_spec), boots[int(0.025 * iters)], boots[int(0.975 * iters) - 1]


def collect(paths: list[str]) -> tuple[dict[str, dict], dict[str, dict]]:
    """Per model: tier -> rows, headline, notes. Returns (models, references)."""
    metas, groups, ends = load(paths)
    by_model: dict[str, dict] = defaultdict(lambda: {"tiers": {}, "notes": [], "cost": 0.0})
    for (run_id, tier), rows in groups.items():
        meta = metas.get(run_id, {})
        name = meta.get("model", "?")
        entry = by_model[name]
        if tier in entry["tiers"]:
            entry["notes"].append(f"{tier} appears in two runs; the later one is used")
        entry["tiers"][tier] = rows
        s = summarize(rows, meta.get("max_tokens"))
        entry["cost"] += s["cost_usd"]
        problems = completeness_problems(run_id, tier, rows, meta, ends)
        if s["truncated"] + s["api_errors"] > 0.05 * len(rows):
            problems.append(f"{s['truncated']} cut off, {s['api_errors']} API errors")
        entry["notes"] += [f"{tier}: {p}" for p in problems]
    models, refs = {}, {}
    for name, entry in by_model.items():
        entry["score"] = headline(entry["tiers"])
        entry["tier_pass"] = {t: statistics.fmean(per_spec_pass(entry["tiers"][t]).values())
                              for t in ALL_TIERS if t in entry["tiers"]}
        missing = [t for t in HEADLINE_TIERS if t not in entry["tiers"]]
        if missing and name not in DETERMINISTIC:
            entry["notes"].append("missing " + ", ".join(missing))
        (refs if name in DETERMINISTIC else models)[name] = entry
    return models, refs


# --- SVG helpers ------------------------------------------------------------------

def _blend(c0: str, c1: str, t: float) -> str:
    """Linear blend of two #rrggbb colours, t in [0, 1]."""
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b, strict=True))


def svg(width: int, height: int, body: list[str], title: str) -> str:
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' "
            f"viewBox='0 0 {width} {height}' {FONT}>\n<title>{escape(title)}</title>\n"
            "<defs><pattern id='hatch' width='6' height='6' patternUnits='userSpaceOnUse' "
            "patternTransform='rotate(45)'><rect width='6' height='6' fill='#dfe6ee'/>"
            "<line x1='0' y1='0' x2='0' y2='6' stroke='#9aa7b5' stroke-width='2'/></pattern></defs>\n"
            f"<rect width='{width}' height='{height}' fill='#ffffff'/>\n" + "\n".join(body) + "\n</svg>\n")


def text(x: float, y: float, s: str, size: int = 12, anchor: str = "start", weight: str = "normal",
         fill: str = "#1f2933") -> str:
    return (f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' "
            f"font-weight='{weight}' fill='{fill}'>{escape(s)}</text>")


def ranking_svg(ranked: list[tuple[str, dict]], refs: dict[str, dict]) -> str:
    left, right, top, row_h = 250, 60, 96, 26
    width = 900
    plot_w = width - left - right
    height = top + row_h * len(ranked) + 60
    x = lambda v: left + v * plot_w  # noqa: E731
    body = [text(20, 28, "cad-spec leaderboard: all-requirements pass rate, tiers L1 to L4", 17, weight="bold"),
            text(20, 48, "one greedy run per model, 30 held-out specs per tier; whiskers are 95% bootstrap "
                         "intervals; hatched = provisional", 11, fill="#52606d")]
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        body.append(f"<line x1='{x(v):.1f}' y1='{top - 8}' x2='{x(v):.1f}' y2='{height - 45}' "
                    "stroke='#e4e7eb'/>")
        body.append(text(x(v), height - 30, f"{v:.0%}", 11, "middle", fill="#52606d"))
    for i, (name, e) in enumerate(ranked):
        y = top + i * row_h
        mean, lo, hi = e["score"]
        prov = bool(e["notes"])
        fill = "url(#hatch)" if prov else PALETTE[0]
        body.append(text(left - 10, y + 15, name, 12, "end"))
        body.append(f"<rect x='{left}' y='{y + 4}' width='{max(1.0, mean * plot_w):.1f}' height='{row_h - 10}' "
                    f"fill='{fill}' rx='2'/>")
        body.append(f"<line x1='{x(lo):.1f}' y1='{y + 12}' x2='{x(hi):.1f}' y2='{y + 12}' stroke='#1f2933' "
                    "stroke-width='1.5'/>")
        for v in (lo, hi):
            body.append(f"<line x1='{x(v):.1f}' y1='{y + 7}' x2='{x(v):.1f}' y2='{y + 17}' stroke='#1f2933'/>")
        body.append(text(x(hi) + 6, y + 16, f"{mean:.0%}", 11, fill="#1f2933"))
    lx = 20
    body.append(text(lx, 70, "dashed: programs with no model", 11, fill="#52606d"))
    lx += 190
    for name, color in (("parser-copy", PALETTE[4]), ("parser-derive", PALETTE[1]),
                        ("parser-template", PALETTE[3])):
        e = refs.get(name)
        if not e or not e["score"]:
            continue
        v = e["score"][0]
        body.append(f"<line x1='{x(v):.1f}' y1='{top - 8}' x2='{x(v):.1f}' y2='{height - 45}' stroke='{color}' "
                    "stroke-width='1.5' stroke-dasharray='5,4'/>")
        body.append(f"<line x1='{lx}' y1='66' x2='{lx + 22}' y2='66' stroke='{color}' stroke-width='2' "
                    "stroke-dasharray='5,4'/>")
        label = f"{name} {v:.0%}"
        body.append(text(lx + 28, 70, label, 11, fill=color))
        lx += 40 + 7 * len(label)
    return svg(width, height, body, "cad-spec ranking")


def heatmap_svg(ranked: list[tuple[str, dict]], refs: dict[str, dict]) -> str:
    rows = ranked + [(n, refs[n]) for n in ("parser-template", "parser-derive", "parser-copy", "rev-a")
                     if n in refs]
    left, top, cell_w, cell_h = 250, 70, 110, 24
    width, height = left + cell_w * len(ALL_TIERS) + 30, top + cell_h * len(rows) + 30
    body = [text(20, 28, "All-requirements pass rate by tier", 17, weight="bold"),
            text(20, 48, "L0 template, L1 table (over-dimensioned), L2 derive pitch, L3 prose, L4 change order",
                 11, fill="#52606d")]
    for j, t in enumerate(ALL_TIERS):
        body.append(text(left + j * cell_w + cell_w / 2, top - 8, t, 12, "middle", "bold"))
    for i, (name, e) in enumerate(rows):
        y = top + i * cell_h
        ref = name in DETERMINISTIC
        body.append(text(left - 10, y + 16, name + ("  (reference)" if ref else ""), 11, "end",
                         fill="#7b8794" if ref else "#1f2933"))
        for j, t in enumerate(ALL_TIERS):
            v = e["tier_pass"].get(t)
            xx = left + j * cell_w
            if v is None:
                body.append(f"<rect x='{xx}' y='{y}' width='{cell_w - 2}' height='{cell_h - 2}' fill='#f5f7fa'/>")
                continue
            color = _blend("#f0f4f8", "#0b4f8a", v)
            body.append(f"<rect x='{xx}' y='{y}' width='{cell_w - 2}' height='{cell_h - 2}' fill='{color}'/>")
            body.append(text(xx + cell_w / 2 - 1, y + 16, f"{v:.0%}", 11, "middle",
                             fill="#ffffff" if v > 0.55 else "#1f2933"))
    return svg(width, height, body, "cad-spec tier heatmap")


def fingerprint_svg(ranked: list[tuple[str, dict]], failures: dict) -> str:
    groups = list(FAILURE_GROUPS)
    left, top, row_h, width = 250, 100, 26, 900
    plot_w = width - left - 30
    height = top + row_h * len(ranked) + 30
    body = [text(20, 28, "How models fail: share of each model's answers, tiers L1 to L4", 17, weight="bold"),
            text(20, 48, "each failed answer gets one label from its re-measured geometry and code "
                         "(scripts/failure_modes.py); the rest of the bar passed", 11, fill="#52606d")]
    for k, (g, color) in enumerate(zip(groups, PALETTE, strict=False)):
        lx, ly = 20 + (k % 4) * 215, 62 + (k // 4) * 18  # legend in rows of four
        body.append(f"<rect x='{lx}' y='{ly}' width='12' height='12' fill='{color}'/>")
        body.append(text(lx + 16, ly + 10, g, 11))
    per_model_tier = failures.get("per_model_tier", {})
    for i, (name, e) in enumerate(ranked):
        y = top + i * row_h
        body.append(text(left - 10, y + 15, name, 12, "end"))
        counts = defaultdict(int)
        for tier in HEADLINE_TIERS:
            for label, n in per_model_tier.get(name, {}).get(tier, {}).items():
                for g, labels in FAILURE_GROUPS.items():
                    if label in labels:
                        counts[g] += n
        total = sum(len(e["tiers"].get(t, [])) for t in HEADLINE_TIERS) or 1
        xx = float(left)
        for g, color in zip(groups, PALETTE, strict=False):
            w = counts[g] / total * plot_w
            if w > 0:
                body.append(f"<rect x='{xx:.1f}' y='{y + 4}' width='{w:.1f}' height='{row_h - 10}' fill='{color}'/>")
                xx += w
        passed = 1 - sum(counts.values()) / total
        body.append(f"<rect x='{xx:.1f}' y='{y + 4}' width='{max(0.0, passed * plot_w):.1f}' "
                    f"height='{row_h - 10}' fill='#eef2f7'/>")
    return svg(width, height, body, "cad-spec failure fingerprints")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--failures", default="", help="failure-modes JSON from scripts/failure_modes.py")
    ap.add_argument("--out", default=str(ROOT / "results" / "leaderboard"))
    args = ap.parse_args()

    models, refs = collect(args.paths)
    ranked = sorted(((n, e) for n, e in models.items() if e["score"]), key=lambda kv: -kv[1]["score"][0])
    unranked = sorted(n for n, e in models.items() if not e["score"])
    failures = json.loads(Path(args.failures).read_text()) if args.failures else None

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "ranking.svg").write_text(ranking_svg(ranked, refs))
    (out / "heatmap.svg").write_text(heatmap_svg(ranked, refs))
    if failures:
        (out / "fingerprints.svg").write_text(fingerprint_svg(ranked, failures))

    def top_failure(name: str) -> str:
        if not failures:
            return ""
        c: dict[str, int] = defaultdict(int)
        for tier in HEADLINE_TIERS:
            for label, n in failures.get("per_model_tier", {}).get(name, {}).get(tier, {}).items():
                c[label] += n
        return max(c, key=c.get) if c else ""

    md = ["# cad-spec leaderboard", "",
          "Score: all-requirements pass rate averaged over L1 to L4 (L0 excluded, a regex solves it), "
          "one greedy run, 30 held-out specs per tier, 95% bootstrap interval over specs. Ranks inside "
          "overlapping intervals are not meaningful.", "",
          "![ranking](ranking.svg)", "",
          "| # | Model | Score [95% CI] | L0 | L1 | L2 | L3 | L4 | Run cost $ | Most common failure | Notes |",
          "|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for i, (name, e) in enumerate(ranked, 1):
        mean, lo, hi = e["score"]
        tiers = " | ".join(f"{e['tier_pass'][t]:.0%}" if t in e["tier_pass"] else "" for t in ALL_TIERS)
        note = "PROVISIONAL: " + "; ".join(e["notes"]) if e["notes"] else ""
        md.append(f"| {i} | {name} | {mean:.0%} [{lo:.0%}, {hi:.0%}] | {tiers} | {e['cost']:.3f} | "
                  f"{top_failure(name)} | {note} |")
    md += ["", "Reference programs (no model):", "", "| Program | Score | L0 | L1 | L2 | L3 | L4 |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for name in ("reference", "parser-template", "parser-derive", "parser-copy", "rev-a"):
        e = refs.get(name)
        if not e:
            continue
        score = f"{e['score'][0]:.0%}" if e["score"] else "n/a"
        tiers = " | ".join(f"{e['tier_pass'][t]:.0%}" if t in e["tier_pass"] else "" for t in ALL_TIERS)
        md.append(f"| {name} | {score} | {tiers} |")
    if unranked:
        md += ["", "Not ranked (missing tiers): " + ", ".join(unranked)]
    md += ["", "![tiers](heatmap.svg)"] + (["", "![failure fingerprints](fingerprints.svg)"] if failures else [])
    (out / "leaderboard.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[:len(ranked) + 8]))
    print(f"\nwrote {out}/leaderboard.md, ranking.svg, heatmap.svg" + (", fingerprints.svg" if failures else ""),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
