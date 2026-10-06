"""L5, region-graded change orders. Governing design: docs/design/.

Built in milestones. M1 (this package so far): the observation map, which
turns a measured solid into contract variables, with the strict form check of
scorer 0.5.0 and an explicit out-of-scope verdict.
"""

from .observation import (
    EPS_DIM_MM,
    EPS_FORM_MM,
    FORM_VIOLATION,
    MIN_CYLINDER_DIAMETER_MM,
    NOT_SINGLE_SOLID,
    OBSERVATION_VERSION,
    OK,
    OUT_OF_SCOPE,
    SCORER_BASIS,
    Observation,
    observe,
    observe_code,
)

__all__ = [
    "EPS_DIM_MM",
    "EPS_FORM_MM",
    "FORM_VIOLATION",
    "MIN_CYLINDER_DIAMETER_MM",
    "NOT_SINGLE_SOLID",
    "OBSERVATION_VERSION",
    "OK",
    "OUT_OF_SCOPE",
    "SCORER_BASIS",
    "Observation",
    "observe",
    "observe_code",
]
