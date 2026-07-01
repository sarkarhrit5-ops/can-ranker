"""Calculate the weighted final score for a candidate match."""

from __future__ import annotations

import logging
import math
from typing import Any

from src.models.match_result import MatchResult

logger = logging.getLogger(__name__)

_SKILL_WEIGHT = 0.40
_EXPERIENCE_WEIGHT = 0.25
_EDUCATION_WEIGHT = 0.10
_BEHAVIOR_WEIGHT = 0.10
_QUALITY_WEIGHT = 0.15


def _normalize_score(value: Any, component_name: str) -> float:
    """Convert a component to a finite float in [0,1]."""

    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        logger.warning(
            "Using 0.0 for malformed %s",
            component_name,
        )
        return 0.0

    if not math.isfinite(value):
        logger.warning(
            "Using 0.0 for non-finite %s",
            component_name,
        )
        return 0.0

    return max(0.0, min(1.0, value))


def _match_component(match: Any, attribute: str) -> float:
    """Safely read a similarity component."""

    if match is None:
        return 0.0

    return _normalize_score(
        getattr(match, attribute, 0.0),
        attribute,
    )


def calculate_final_score(
    match: MatchResult,
    behavior_score: float,
    quality_score: float,
) -> float:
    """
    Calculate the final normalized score.

    Returns
    -------
    float
        Score in the range [0.0, 1.0].
    """

    logger.info("Starting final score calculation")

    skill = _match_component(match, "skill_similarity")
    experience = _match_component(match, "experience_similarity")
    education = _match_component(match, "education_similarity")
    behavior = _normalize_score(
        behavior_score,
        "behavior_score",
    )
    quality = _normalize_score(
        quality_score,
        "quality_score",
    )

    final_score = (
        skill * _SKILL_WEIGHT
        + experience * _EXPERIENCE_WEIGHT
        + education * _EDUCATION_WEIGHT
        + behavior * _BEHAVIOR_WEIGHT
        + quality * _QUALITY_WEIGHT
    )

    final_score = max(0.0, min(1.0, final_score))

    logger.info(
        "Final normalized score: %.4f",
        final_score,
    )

    return float(final_score*5.5)
