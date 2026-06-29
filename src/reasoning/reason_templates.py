"""Provide deterministic text templates for candidate match reasoning."""

HIGH_MATCH_TEMPLATES = (
    "Strong match because of {strengths}.",
    "Candidate aligns well through {strengths}.",
    "Profile demonstrates strong alignment in {strengths}.",
)

MEDIUM_MATCH_TEMPLATES = (
    "Candidate satisfies several important requirements including "
    "{strengths}.",
    "Reasonable alignment through {strengths}.",
)

LOW_MATCH_TEMPLATES = (
    "Candidate has limited alignment with the requested profile.",
    "Only partial overlap with the required qualifications.",
)

CONCERN_TEMPLATES = (
    "Main concern: {concerns}.",
    "Potential limitation: {concerns}.",
)

POSITIVE_SIGNAL_TEMPLATES = (
    "Positive indicators include {signals}.",
    "Additional strengths include {signals}.",
)


def select_match_template(score: float) -> str:
    """Select a deterministic match template for the given normalized score.

    Args:
        score: Normalized match score used to choose a template category.

    Returns:
        The first high-, medium-, or low-match template for the score.
    """
    if score >= 0.80:
        return HIGH_MATCH_TEMPLATES[0]
    if score >= 0.60:
        return MEDIUM_MATCH_TEMPLATES[0]
    return LOW_MATCH_TEMPLATES[0]


def select_concern_template(has_concern: bool) -> str:
    """Return the default concern template when a concern is present.

    Args:
        has_concern: Whether candidate reasoning includes a concern.

    Returns:
        The first concern template when requested; otherwise, an empty string.
    """
    if not has_concern:
        return ""
    return CONCERN_TEMPLATES[0]


def select_positive_template(has_positive_signal: bool) -> str:
    """Return the default positive template when a signal is present.

    Args:
        has_positive_signal: Whether reasoning includes a positive signal.

    Returns:
        The first positive-signal template when requested; otherwise, an
        empty string.
    """
    if not has_positive_signal:
        return ""
    return POSITIVE_SIGNAL_TEMPLATES[0]
