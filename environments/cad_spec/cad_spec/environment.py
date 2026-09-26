"""Verifiers wrapper.

This is the only file that depends on the verifiers API, and the only one you
should expect to adjust when versions move.

Everything that carries engineering judgement lives in rubric.py and measure.py,
which are plain Python and testable without verifiers, a model, or an account.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import verifiers as vf
from datasets import Dataset

from .prompts import SYSTEM_PROMPT, system_prompt
from .rubric import Report, score
from .tasks import TIERS, Spec, make_splits, prompt_for

TRAIN_SPECS, EVAL_SPECS = make_splits()
SPECS: dict[str, Spec] = {s.id: s for s in TRAIN_SPECS + EVAL_SPECS}

# SYSTEM_PROMPT is imported from prompts.py, the one copy shared with the runner.
__all__ = ["SYSTEM_PROMPT", "load_environment"]

# Floor awarded to code that executes and yields a solid but satisfies nothing.
# It exists to give a near-zero baseline model a first rung to climb; folding it
# in as a floor (rather than an additive weighted term) keeps the reward scale
# exactly [0, 1] regardless of how any verifiers version combines functions.
PARSE_FLOOR = 0.05


def _completion_text(completion) -> str:
    """Flatten a completion into plain text.

    A rollout may arrive as a plain string, a list of dicts, or a list of
    message OBJECTS (AssistantMessage and friends). Handling only dicts
    silently yields an empty string and scores every rollout zero, which
    looks exactly like a model failure and is not one.
    """
    if isinstance(completion, str):
        return completion
    if completion is None:
        return ""

    parts: list[str] = []
    for message in completion:
        content = message.get("content") if isinstance(message, dict) else getattr(message, "content", None)
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            # content blocks: [{"type": "text", "text": ...}, ...]
            for block in content:
                text = (
                    block.get("text")
                    if isinstance(block, dict)
                    else getattr(block, "text", None)
                )
                if isinstance(text, str):
                    parts.append(text)
    return "\n".join(parts)


def _spec_for(answer, info) -> Spec | None:
    spec_id = (info or {}).get("spec_id", answer)
    return SPECS.get(spec_id)


def _tiers(tier: str | Sequence[str]) -> list[str]:
    tiers = [tier] if isinstance(tier, str) else list(tier)
    for t in tiers:
        if t not in TIERS:
            raise ValueError(f"unknown tier {t!r}; expected one of {TIERS}")
    return tiers


def _rows(specs: Sequence[Spec], tiers: Sequence[str], split: str) -> list[dict]:
    return [
        {
            "question": prompt_for(spec, t, split),
            "answer": spec.id,
            "info": {"spec_id": spec.id, "tier": t},
            "task": f"cad-spec-{t}",
        }
        for t in tiers
        for spec in specs
    ]


def _build_dataset(tiers: Sequence[str] = ("L0",)) -> Dataset:
    return Dataset.from_list(_rows(TRAIN_SPECS, tiers, "train"))


def _build_eval_dataset(tiers: Sequence[str] = ("L0",)) -> Dataset:
    return Dataset.from_list(_rows(EVAL_SPECS, tiers, "eval"))


_STATE_KEY = "_cad_spec_report"


def _report(text: str, spec_id: str, state: Any = None) -> Report:
    """One build per rollout, however many reward/metric functions read it.

    The report is shared through the rollout's own `state` dict, which
    verifiers passes to every reward function of that rollout. Before 0.4.0
    a process-wide cache keyed on (text, spec) was used, so two rollouts that
    produced identical code shared one execution; each rollout is now judged
    on its own build. Without a state dict (direct calls) nothing is cached.
    """
    key = (text, spec_id)
    if isinstance(state, dict):
        cached = state.get(_STATE_KEY)
        if cached is not None and cached[0] == key:
            return cached[1]
    report = score(text, SPECS[spec_id])
    if isinstance(state, dict):
        state[_STATE_KEY] = (key, report)
    return report


def spec_reward(completion, answer="", info=None, **kwargs) -> float:
    """Single reward on a clean [0, 1] scale.

    reward = max(fraction of the 9 requirements met, PARSE_FLOOR if a solid was built)

    1.0    all nine requirements met (R1-R3, R4a, R4b, R5, R6, R7, R8)
    k/9    partial compliance (gates permitting)
    0.05   code that builds a solid but satisfies nothing or fails a gate
           (the floor also reaches gated-out cheats - they DID build)
    0.0    code that does not execute, times out, builds no solid (e.g. only
           a 2D sketch), or no code at all
    """
    spec = _spec_for(answer, info)
    if spec is None:
        return 0.0

    report = _report(_completion_text(completion), spec.id, kwargs.get("state"))
    return max(report.reward, PARSE_FLOOR) if report.parsed else 0.0


def _check_metric(check_name: str) -> Callable[..., float]:
    """Zero-weight diagnostic: 1.0 if the named check passed on this rollout."""

    def metric(completion, answer="", info=None, **kwargs) -> float:
        spec = _spec_for(answer, info)
        if spec is None:
            return 0.0
        report = _report(_completion_text(completion), spec.id, kwargs.get("state"))
        return float(any(c.name == check_name and c.passed for c in report.checks))

    metric.__name__ = "m_" + check_name.replace(":", "_")
    return metric


def built(completion, answer="", info=None, **kwargs) -> float:
    """Zero-weight diagnostic: 1.0 if the code executed and produced a solid."""
    spec = _spec_for(answer, info)
    return float(spec is not None and _report(_completion_text(completion), spec.id, kwargs.get("state")).parsed)


def gates_passed(completion, answer="", info=None, **kwargs) -> float:
    """Zero-weight diagnostic: 1.0 if every anti-hacking gate passed."""
    spec = _spec_for(answer, info)
    if spec is None:
        return 0.0
    report = _report(_completion_text(completion), spec.id, kwargs.get("state"))
    gates = [c for c in report.checks if c.name.startswith("gate:")]
    return float(bool(gates) and all(c.passed for c in gates))


CHECK_NAMES = (
    "R1:length", "R2:width", "R3:thickness", "R4a:hole_count",
    "R4b:hole_diameter", "R5:hole_pattern", "R6:material", "R7:edge_margin",
    "R8:z_datum",
)


def load_environment(
    tier: str | Sequence[str] = "L0",
    eval_tier: str | Sequence[str] | None = None,
    metrics: bool = True,
    hints: bool = False,
    **kwargs,
) -> vf.Environment:
    """Build the environment.

    tier       prompt tier(s) for the training set, see tasks.TIERS.
               Default "L0" reproduces the 0.2 template task.
    eval_tier  prompt tier(s) for the eval set; defaults to `tier`. Pass
               several to get one eval over all of them, each row tagged
               with info["tier"] so results can be split per tier.
    metrics    add zero-weight per-check diagnostics (built, gates, R1..R7).
               They reuse the cached report: no extra builds.
    hints      append the packaged CadQuery cheat-sheet (cad_spec/hints.md) to
               the system prompt, for training AND evaluation alike. It is the
               hint arm of the registered experiment, byte for byte: API facts
               only, no spec numbers, so the reward still measures the design.
    """
    train_tiers = _tiers(tier)
    eval_tiers = _tiers(eval_tier) if eval_tier is not None else train_tiers
    funcs: list[Callable[..., float]] = [spec_reward]
    weights = [1.0]
    if metrics:
        extra = [built, gates_passed] + [_check_metric(n) for n in CHECK_NAMES]
        funcs += extra
        weights += [0.0] * len(extra)
    rubric = vf.Rubric(funcs=funcs, weights=weights)
    kwargs.setdefault("eval_dataset", _build_eval_dataset(eval_tiers))
    return vf.SingleTurnEnv(
        dataset=_build_dataset(train_tiers),
        system_prompt=system_prompt(hints),
        rubric=rubric,
        **kwargs,
    )
