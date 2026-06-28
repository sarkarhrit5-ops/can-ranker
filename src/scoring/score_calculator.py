"""
Score calculator module.
Orchestrates the calculation of a candidate's final score by combining
similarities, behavior metrics, and quality metrics into a single result.
"""
import logging
from src.models.match_result import MatchResult
from src.models.score_result import ScoreResult
# Helper scoring modules
from src.scoring.behavior_score import calculate_behavior_score
from src.scoring.quality_score import calculate_quality_score
from src.scoring.final_score import calculate_final_score
logger = logging.getLogger(__name__)
def _clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a numerical value between a minimum and maximum boundary."""
    try:
        return max(min_val, min(max_val, float(value)))
    except (TypeError, ValueError):
        return min_val
def _get_recommendation(score: float) -> str:
    """
    Determine the hiring recommendation based on the total score.
    
    Ranges:
    - 90–100 -> Strong Hire
    - 75–89 -> Hire
    - 60–74 -> Consider
    - 40–59 -> Weak Consider
    - 0–39 -> Reject
    """
    if score >= 90:
        return "Strong Hire"
    if score >= 75:
        return "Hire"
    if score >= 60:
        return "Consider"
    if score >= 40:
        return "Weak Consider"
    return "Reject"
def calculate_score(match: MatchResult) -> ScoreResult:
    """
    Calculate the final candidate score by aggregating semantic similarities,
    behavior scores, and quality scores.
    
    Args:
        match: A MatchResult object containing the preliminary similarities.
        
    Returns:
        ScoreResult containing candidate_id, total_score, ranking,
        recommendation, and reasoning.
    """
    logger.info("Starting candidate score calculation")
    
    candidate_id = getattr(match, "candidate_id", "") if match else ""
    
    # Graceful handling of malformed input
    if not match or (not candidate_id and not hasattr(match, "overall_similarity")):
        logger.error("Invalid or malformed MatchResult provided")
        return ScoreResult(
            candidate_id=candidate_id,
            total_score=0.0,
            ranking=0,
            recommendation="Reject",
            reasoning="Malformed or invalid match input."
        )
        
    try:
        # Utilize helper scoring modules
        b_score = calculate_behavior_score(match)
        q_score = calculate_quality_score(match)
        
        # Produce the aggregated final score
        raw_total = calculate_final_score(match, b_score, q_score)
        
        # Clamp exactly between 0.0 and 100.0
        total_score = _clamp(raw_total, 0.0, 100.0)
        
        recommendation = _get_recommendation(total_score)
        
        reasoning = (
            f"Candidate achieved a total score of {total_score:.1f}/100. "
            f"Resulting recommendation is {recommendation} based on semantic matching, "
            "behavior, and quality heuristics."
        )
        
        logger.info(
            "Score calculation complete: total_score=%.1f, recommendation=%s",
            total_score, recommendation
        )
        
        return ScoreResult(
            candidate_id=candidate_id,
            total_score=total_score,
            ranking=0,
            recommendation=recommendation,
            reasoning=reasoning
        )
        
    except Exception as e:
        logger.exception("Error occurred while calculating final score: %s", e)
        return ScoreResult(
            candidate_id=candidate_id,
            total_score=0.0,
            ranking=0,
            recommendation="Reject",
            reasoning="An internal error occurred during score calculation."
        )