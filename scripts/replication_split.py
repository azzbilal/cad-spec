"""The replication split of training run 1 (docs/experiments/replication-1.md).

    python scripts/replication_split.py          # summary and fingerprint check

Sixty fresh mounting-plate specs drawn with a new seed from the same
generator as every other split, disjoint by parameters from the train split,
the dev split and the locked test split (which was used once, for the
registered evaluation of run 1, and must not become a selection set). Ids are
rep-0001 upwards, so L4 change orders and L3 wordings are derived afresh.

It lives in scripts/, not in the package, so the published cad-spec 0.4.5
wheel stays byte-identical to the one the adapter was trained with. The seed
was fixed before the split was generated and the split was generated once: no
seed was tried and discarded.

Prompts use the held-out L3 wordings, exactly like the test split: build them
with `prompt_split("replication")`, never with the bare split name.
"""

from __future__ import annotations

import random
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "environments" / "cad_spec"))

from cad_spec.tasks import (  # noqa: E402
    Spec,
    make_splits,
    make_test_split,
    sample_spec,
    split_fingerprint,
)

REPLICATION_SEED = 20261003
N_REPLICATION = 60
REPLICATION_SPLIT_SHA256 = "01ac4bde217e879653c1227760e4abde3d06c0034d16b2a200b0394d7bc14bdd"


def _params(spec: Spec) -> tuple[float, ...]:
    return (spec.length, spec.width, spec.thickness, spec.hole_diameter, spec.edge_margin)


def make_replication_split(seed: int = REPLICATION_SEED, n: int = N_REPLICATION) -> list[Spec]:
    """`n` feasible specs sharing parameters with no train, dev or test spec, nor with each other."""
    train, dev = make_splits()
    seen = {_params(s) for s in train + dev + make_test_split()}
    rng = random.Random(seed)
    out: list[Spec] = []
    i = 0
    while len(out) < n:
        spec = sample_spec(rng, i)
        i += 1
        if _params(spec) in seen:
            continue
        seen.add(_params(spec))
        out.append(replace(spec, id=f"rep-{len(out) + 1:04d}"))
    return out


def locked_replication_split() -> list[Spec]:
    """The split, or SystemExit if it no longer matches its fingerprint."""
    specs = make_replication_split()
    if split_fingerprint(specs) != REPLICATION_SPLIT_SHA256:
        raise SystemExit("cad-spec: the replication split no longer matches its locked fingerprint")
    return specs


def prompt_split(split: str) -> str:
    """The split name to pass to `prompt_for`: replication specs get the held-out wording."""
    return "test" if split == "replication" else split


def main() -> int:
    specs = make_replication_split()
    got = split_fingerprint(specs)
    areas = sorted(s.length * s.width for s in specs)
    print(f"replication split: {len(specs)} specs, seed {REPLICATION_SEED}")
    print(f"fingerprint {got}")
    print(f"locked      {REPLICATION_SPLIT_SHA256}")
    print(f"face area mm2: min {areas[0]:.0f}, median {areas[len(areas) // 2]:.0f}, max {areas[-1]:.0f}")
    return 0 if got == REPLICATION_SPLIT_SHA256 else 1


if __name__ == "__main__":
    raise SystemExit(main())
