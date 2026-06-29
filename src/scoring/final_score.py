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
    """Convert a component to a finite float and clamp it to ``[0, 1]``."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError, OverflowError):
        logger.warning(
            "Using 0.0 for malformed %s in final score calculation",
            component_name,
        )
        return 0.0

    if not math.isfinite(numeric_value):
        logger.warning(
            "Using 0.0 for non-finite %s in final score calculation",
            component_name,
        )
        return 0.0

    clamped_value = max(0.0, min(1.0, numeric_value))
    if clamped_value != numeric_value:
        logger.info(
            "Clamped %s from %.3f to %.3f",
            component_name,
            numeric_value,
            clamped_value,
        )

    return clamped_value


def _match_component(match: Any, attribute_name: str) -> float:
    """Read and normalize a similarity component from a match object."""
    try:
        value = getattr(match, attribute_name)
    except (AttributeError, TypeError):
        logger.warning(
            "Using 0.0 because match has no valid %s", attribute_name
        )
        return 0.0

    return _normalize_score(value, attribute_name)


def calculate_final_score(
    match: MatchResult,
    behavior_score: float,
    quality_score: float,
) -> float:
    """Calculate a weighted candidate score on a 0–100 scale.

    Skill, experience, education, behavior, and quality contribute 40%, 25%,
    10%, 10%, and 15%, respectively. Every component is normalized to the
    inclusive range ``[0.0, 1.0]`` before weighting. Missing or malformed
    values safely contribute zero.

    Args:
        match: Candidate-to-job match containing similarity components.
        behavior_score: Previously calculated behavior score.
        quality_score: Previously calculated quality score.

    Returns:
        The weighted final score as a float between 0.0 and 100.0.
    """
    logger.info("Starting final score calculation")

    if match is None:
        logger.error(
            "Malformed MatchResult: similarity components will contribute 0.0"
        )

    skill_similarity = _match_component(match, "skill_similarity")
    experience_similarity = _match_component(
        match, "experience_similarity"
    )
    education_similarity = _match_component(match, "education_similarity")
    normalized_behavior = _normalize_score(behavior_score, "behavior_score")
    normalized_quality = _normalize_score(quality_score, "quality_score")

    weighted_score = (
        skill_similarity * _SKILL_WEIGHT
        + experience_similarity * _EXPERIENCE_WEIGHT
        + education_similarity * _EDUCATION_WEIGHT
        + normalized_behavior * _BEHAVIOR_WEIGHT
        + normalized_quality * _QUALITY_WEIGHT
    )
    final_score = max(0.0, min(100.0, weighted_score * 100.0))

    logger.info(
        "Final score calculation complete: %.2f out of 100", final_score
    )
    return float(final_score)
