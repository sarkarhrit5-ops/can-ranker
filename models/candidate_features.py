"""Domain models for structured candidate features.

These dataclasses are passive data containers. Feature extraction, matching,
ranking, and scoring behavior belongs outside this module.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class SkillFeatures:
    """Normalized and categorized candidate skills.

    Attributes:
        normalized_skills: Unique canonical skills in source order.
        technical_skills: Recognized technical skills in source order.
        soft_skills: Recognized soft skills in source order.
        skill_count: Number of valid source skill entries.
        unique_skill_count: Number of unique canonical skills.
        primary_skill: First canonical skill, if one is available.
    """

    normalized_skills: list[str] = field(default_factory=list)
    technical_skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    skill_count: int = 0
    unique_skill_count: int = 0
    primary_skill: str | None = None


@dataclass(slots=True)
class CareerFeatures:
    """Structured measurements derived from candidate career history.

    Attributes:
        total_years_experience: Summed valid tenure in years.
        number_of_companies: Number of distinct companies.
        average_tenure_months: Average valid role tenure in months.
        longest_tenure_months: Longest valid role tenure in months.
        shortest_tenure_months: Shortest valid role tenure in months.
        leadership_experience: Whether leadership evidence is present.
        promotion_count: Number of explicit or inferred promotions.
        seniority_level: Highest recognized seniority level.
        career_growth_score: Bounded career-progression metric.
    """

    total_years_experience: float = 0.0
    number_of_companies: int = 0
    average_tenure_months: float = 0.0
    longest_tenure_months: int = 0
    shortest_tenure_months: int = 0
    leadership_experience: bool = False
    promotion_count: int = 0
    seniority_level: str = "unknown"
    career_growth_score: float = 0.0

    @property
    def longest_tenure(self) -> int:
        """Return the longest role tenure in months."""
        return self.longest_tenure_months

    @property
    def shortest_tenure(self) -> int:
        """Return the shortest role tenure in months."""
        return self.shortest_tenure_months


@dataclass(slots=True)
class TimelineFeatures:
    """Temporal characteristics of candidate employment history.

    Attributes:
        career_start_date: Earliest reliable employment start date.
        career_end_date: Latest reliable employment end date.
        total_roles: Number of usable roles in the timeline.
        career_span_months: Calendar span covered by the timeline.
        employment_gap_count: Number of detected employment gaps.
        total_gap_months: Combined duration of detected gaps.
        longest_gap_months: Longest detected employment gap.
        overlapping_role_count: Number of roles overlapping another role.
        has_current_role: Whether the timeline contains a current role.
    """

    career_start_date: date | None = None
    career_end_date: date | None = None
    total_roles: int = 0
    career_span_months: int = 0
    employment_gap_count: int = 0
    total_gap_months: int = 0
    longest_gap_months: int = 0
    overlapping_role_count: int = 0
    has_current_role: bool = False


@dataclass(slots=True)
class BehaviorFeatures:
    """Observed behavioral signals without weights or scores.

    Attributes:
        positive_signals: Favorable observed behavioral signals.
        risk_signals: Signals that may require human review.
        leadership_signals: Evidence of leadership behavior.
        collaboration_signals: Evidence of collaboration.
        communication_signals: Evidence of communication.
        adaptability_signals: Evidence of adaptability.
    """

    positive_signals: list[str] = field(default_factory=list)
    risk_signals: list[str] = field(default_factory=list)
    leadership_signals: list[str] = field(default_factory=list)
    collaboration_signals: list[str] = field(default_factory=list)
    communication_signals: list[str] = field(default_factory=list)
    adaptability_signals: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CandidateFeatures:
    """Aggregate feature model for a single candidate.

    Attributes:
        candidate_id: Stable candidate identifier.
        skill_features: Normalized skill features.
        career_features: Career-history features.
        timeline_features: Employment timeline features.
        behavior_features: Observed behavioral signals.
    """

    candidate_id: str
    skill_features: SkillFeatures = field(default_factory=SkillFeatures)
    career_features: CareerFeatures = field(default_factory=CareerFeatures)
    timeline_features: TimelineFeatures = field(default_factory=TimelineFeatures)
    behavior_features: BehaviorFeatures = field(default_factory=BehaviorFeatures)
