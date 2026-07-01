"""
Score calculator module.
Orchestrates the calculation of a candidate's final normalized score.
"""

import logging

from src.models.match_result import MatchResult
from src.models.score_result import ScoreResult

from src.scoring.behavior_score import calculate_behavior_score
from src.scoring.quality_score import calculate_quality_score
from src.scoring.final_score import calculate_final_score

logger = logging.getLogger(__name__)


def _clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a numerical value between two bounds."""
    try:
        return max(min_val, min(max_val, float(value)))
    except (TypeError, ValueError):
        return min_val


def _get_recommendation(score: float) -> str:
    """
    Determine recommendation from normalized score.
    """

    if score >= 0.90:
        return "Strong Hire"
    if score >= 0.75:
        return "Hire"
    if score >= 0.60:
        return "Consider"
    if score >= 0.40:
        return "Weak Consider"
    return "Reject"


def calculate_score(match: MatchResult) -> ScoreResult:
    """
    Calculate the final normalized score.

    Returns
    -------
    ScoreResult
        Final score in the range [0.0, 1.0].
    """

    logger.info("Starting candidate score calculation")

    candidate_id = getattr(match, "candidate_id", "") if match else ""

    if (
        match is None
        or (
            not candidate_id
            and not hasattr(match, "overall_similarity")
        )
    ):
        logger.error("Invalid MatchResult provided")

        return ScoreResult(
            candidate_id=candidate_id,
            total_score=0.0,
            ranking=0,
            recommendation="Reject",
            reasoning="Malformed or invalid match input.",
        )

    try:

        behavior_score = calculate_behavior_score(match)
        quality_score = calculate_quality_score(match)

        total_score = calculate_final_score(
            match,
            behavior_score,
            quality_score,
        )

        total_score = _clamp(total_score, 0.0, 1.0)

        recommendation = _get_recommendation(total_score)

        reasoning = (
            f"Normalized score {total_score:.4f}. "
            f"Recommendation: {recommendation}."
        )

        logger.info(
            "Score calculation complete: %.4f (%s)",
            total_score,
            recommendation,
        )

        return ScoreResult(
            candidate_id=candidate_id,
            total_score=total_score,
            ranking=0,
            recommendation=recommendation,
            reasoning=reasoning,
        )

    except Exception:
        logger.exception("Failed during score calculation")

        return ScoreResult(
            candidate_id=candidate_id,
            total_score=0.0,
            ranking=0,
            recommendation="Reject",
            reasoning="Internal scoring error.",
        )