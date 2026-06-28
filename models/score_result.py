"""Domain model for externally produced candidate score results."""

from dataclasses import dataclass


@dataclass(slots=True)
class ScoreResult:
    """Store a completed candidate scoring and ranking result.

    This passive model does not calculate scores, rankings, recommendations, or
    explanations.

    Attributes:
        candidate_id: Identifier of the scored candidate.
        total_score: Aggregate score produced by an external scoring service.
        ranking: Candidate's resulting rank.
        recommendation: Human-readable recommendation category.
        reasoning: Human-readable explanation accompanying the result.
    """

    candidate_id: str
    total_score: float
    ranking: int
    recommendation: str
    reasoning: str

