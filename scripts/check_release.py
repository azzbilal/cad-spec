"""Release check (runs in CI): every relative link in the published docs
resolves to a file in the repository.

    python scripts/check_release.py

The first publish patch linked a leaderboard, a chart and a failure report
that were not in the tree (external audit, September 2026). A claim without
its evidence file now fails CI instead of shipping.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["README.md", "ROADMAP.md", "SECURITY.md", "CHANGELOG.md",
        *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs").glob("*.md"))]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")


def main() -> int:
    missing = []
    for doc in DOCS:
        path = ROOT / doc
        if not path.exists():
            continue
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).resolve().exists():
                missing.append(f"{doc}: {target}")
    for m in missing:
        print(f"MISSING  {m}")
    print(f"{len(missing)} broken link(s)" if missing else "all document links resolve")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
