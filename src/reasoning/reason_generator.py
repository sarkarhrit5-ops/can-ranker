"""Generate deterministic, human-readable candidate match reasoning."""

import logging

from src.models.match_result import MatchResult
from src.models.score_result import ScoreResult
from src.reasoning.reason_templates import (
    select_concern_template,
    select_match_template,
    select_positive_template,
)


logger = logging.getLogger(__name__)

_GENERATION_ERROR = "Unable to generate reasoning."
_LIMITED_SKILLS = "limited matching skills"
_POSITIVE_SIGNAL = "strong behavioral alignment"


def _first_three_items(value: object) -> list[str]:
    """Return up to three string items from a valid sequence.

    Args:
        value: Potential sequence of skill names.

    Returns:
        Up to the first three items converted to strings. An empty list is
        returned when the value is not a suitable sequence.
    """
    if not isinstance(value, list):
        return []

    return [str(item) for item in value[:3]]


def _extract_strengths(match: MatchResult) -> str:
    """Extract up to three matched skills for use in reasoning.

    Args:
        match: Match result containing the candidate's matched skills.

    Returns:
        A comma-separated list of up to three matched skills, or
        ``"limited matching skills"`` when none are available.
    """
    try:
        strengths = _first_three_items(match.matched_skills)
    except (AttributeError, TypeError):
        logger.warning("Unable to extract matched skills from match result")
        return _LIMITED_SKILLS

    if not strengths:
        return _LIMITED_SKILLS
    return ", ".join(strengths)


def _extract_concerns(match: MatchResult) -> str:
    """Extract up to three missing skills for use as concerns.

    Args:
        match: Match result containing the candidate's missing skills.

    Returns:
        A comma-separated list of up to three missing skills, or an empty
        string when no valid missing skills are available.
    """
    try:
        concerns = _first_three_items(match.missing_skills)
    except (AttributeError, TypeError):
        logger.warning("Unable to extract missing skills from match result")
        return ""

    return ", ".join(concerns)


def _generate_positive_signal(match: MatchResult) -> str:
    """Generate a positive signal from behavior similarity.

    Args:
        match: Match result containing the behavior similarity value.

    Returns:
        ``"strong behavioral alignment"`` when behavior similarity is at
        least ``0.75``; otherwise, an empty string.
    """
    try:
        has_strong_alignment = match.behavior_similarity >= 0.75
    except (AttributeError, TypeError):
        logger.warning("Unable to evaluate behavior similarity")
        return ""

    if has_strong_alignment:
        return _POSITIVE_SIGNAL
    return ""


def generate_reason(match: MatchResult, score: ScoreResult) -> str:
    """Generate deterministic reasoning for a candidate match.

    Args:
        match: Match result containing similarities and skill matches.
        score: Score result containing the overall recommendation.

    Returns:
        A space-separated reasoning statement. If either argument is ``None``
        or required data is malformed, returns
        ``"Unable to generate reasoning."``.
    """
    if match is None or score is None:
        logger.error("Cannot generate reasoning from a null match or score")
        return _GENERATION_ERROR

    try:
        strengths = _extract_strengths(match)
        match_reason = select_match_template(
            match.overall_similarity
        ).format(strengths=strengths)
        sections = [match_reason]

        concerns = _extract_concerns(match)
        if concerns:
            concern_reason = select_concern_template(True).format(
                concerns=concerns
            )
            sections.append(concern_reason)

        positive_signal = _generate_positive_signal(match)
        if positive_signal:
            positive_reason = select_positive_template(True).format(
                signals=positive_signal
            )
            sections.append(positive_reason)

        sections.append(f"Overall recommendation: {score.recommendation}.")
    except (AttributeError, KeyError, TypeError, ValueError):
        logger.exception("Unable to generate reasoning from malformed inputs")
        return _GENERATION_ERROR

    reason = " ".join(sections)
    logger.info(
        "Generated candidate reasoning with %d sections", len(sections)
    )
    return reason
