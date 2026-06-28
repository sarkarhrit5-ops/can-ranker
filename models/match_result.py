"""Domain model for candidate-to-job matching results."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class MatchResult:
    """Store component similarities from a completed match operation.

    This model does not calculate similarities; it only transports results
    produced elsewhere.

    Attributes:
        candidate_id: Identifier of the matched candidate.
        overall_similarity: Aggregate similarity value.
        skill_similarity: Skill-specific similarity value.
        experience_similarity: Experience-specific similarity value.
        education_similarity: Education-specific similarity value.
        behavior_similarity: Behavior-specific similarity value.
        matched_skills: Canonical skills shared with job requirements.
        missing_skills: Canonical required skills absent from the candidate.
    """

    candidate_id: str
    overall_similarity: float
    skill_similarity: float
    experience_similarity: float
    education_similarity: float
    behavior_similarity: float
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)

