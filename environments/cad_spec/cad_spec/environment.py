"""Verifiers wrapper.

This is the only file that depends on the verifiers API, and the only one you
should expect to adjust when versions move.

Everything that carries engineering judgement lives in rubric.py and measure.py,
which are plain Python and testable without verifiers, a model, or an account.
"""

from __future__ import annotations

from datasets import Dataset

import verifiers as vf

from .rubric import score
from .tasks import TASKS, Spec

SPECS: dict[str, Spec] = {s.id: s for s in TASKS}

SYSTEM_PROMPT = """\
You are a mechanical design engineer who writes CadQuery.
Return a single Python code block and nothing else.
Import cadquery as cq and bind the finished part to a variable named `result`.
Build solids with the Workplane API, for example cq.Workplane("XY").box(l, w, h).
"""

# Floor awarded to code that executes and yields a solid but satisfies nothing.
# It exists to give a near-zero baseline model a first rung to climb; folding it
# in as a floor (rather than an additive weighted term) keeps the reward scale
# exactly [0, 1] regardless of how any verifiers version combines functions.
PARSE_FLOOR = 0.05

# Held-out specs: never trained on, used to measure generalization.
# Chosen to cover the size extremes (largest and smallest plates) and a
# mid-range case.
EVAL_SPEC_IDS = {"plate-08", "plate-09", "plate-10"}


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
        if isinstance(message, dict):
            content = message.get("content")
        else:
            content = getattr(message, "content", None)
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


def _rows(specs) -> list[dict]:
    return [
        {
            "question": spec.to_prompt(),
            "answer": spec.id,
            "info": {"spec_id": spec.id},
        }
        for spec in specs
    ]


def _build_dataset() -> Dataset:
    return Dataset.from_list(_rows(s for s in TASKS if s.id not in EVAL_SPEC_IDS))


def _build_eval_dataset() -> Dataset:
    return Dataset.from_list(_rows(s for s in TASKS if s.id in EVAL_SPEC_IDS))


def spec_reward(completion, answer="", info=None, **kwargs) -> float:
    """Single reward on a clean [0, 1] scale.

    reward = max(fraction of the 7 requirements met, PARSE_FLOOR if code ran)

    1.0    all seven requirements met
    k/7    partial compliance (gates permitting)
    0.05   runnable CadQuery that satisfies nothing or fails a gate
           (the floor also reaches gated-out cheats - they DID build)
    0.0    code that does not execute, times out, or no code at all
    """
    spec = _spec_for(answer, info)
    if spec is None:
        return 0.0

    text = _completion_text(completion)
    report = score(text, spec)
    return max(report.reward, PARSE_FLOOR) if report.parsed else 0.0


def load_environment(**kwargs) -> vf.Environment:
    rubric = vf.Rubric(funcs=[spec_reward], weights=[1.0])
    kwargs.setdefault("eval_dataset", _build_eval_dataset())
    return vf.SingleTurnEnv(
        dataset=_build_dataset(),
        system_prompt=SYSTEM_PROMPT,
        rubric=rubric,
        **kwargs,
    )
