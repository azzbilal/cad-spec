"""Detect degenerate model output: repetition loops and whitespace floods.

Only meaningful for answers that hit the token cap (finish_reason "length").
A truncated answer is either CUT OFF (the token budget was too small for a
real answer: a run configuration problem) or DEGENERATE (the model got stuck
repeating itself and would have run past any budget: a model failure).
Doubling the budget does not change the second kind; this module tells them
apart from the text alone, so old run files can be judged too.
"""

from __future__ import annotations

from collections import Counter

TAIL_CHARS = 1500     # only the end of the answer is inspected
MIN_REPEATS = 6       # a line or fragment seen this often in the tail is a loop
WHITESPACE_SHARE = 0.8


def is_degenerate(text: str) -> bool:
    tail = (text or "")[-TAIL_CHARS:]
    if len(tail) < 200:
        return False
    # Whitespace flood: the tail is mostly spaces or newlines.
    if sum(ch.isspace() for ch in tail) >= WHITESPACE_SHARE * len(tail):
        return True
    # Line loop: the same non-trivial line repeated.
    lines = [ln.strip() for ln in tail.splitlines() if len(ln.strip()) >= 6]
    if lines and Counter(lines).most_common(1)[0][1] >= MIN_REPEATS:
        return True
    # In-line loop (one long line repeating a fragment, e.g. chained calls):
    # the last 24 characters recur many times in the tail.
    probe = tail.rstrip()[-24:]
    return len(probe.strip()) >= 12 and tail.count(probe) >= MIN_REPEATS
