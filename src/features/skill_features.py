    "pandas": "library",
    "php": "programming_language",
    "postgresql": "database",
    "pytorch": "machine_learning",
    "python": "programming_language",
    "r": "programming_language",
    "react": "framework",
    "redis": "database",
    "ruby": "programming_language",
    "rust": "programming_language",
    "scala": "programming_language",
    "scikit-learn": "machine_learning",
    "spark": "data",
    "spring": "framework",
    "sql": "database",
    "swift": "programming_language",
    "tensorflow": "machine_learning",
    "terraform": "devops",
    "typescript": "programming_language",
    "vue.js": "framework",
}

SOFT_SKILLS: Final[dict[str, str]] = {
    "adaptability": "personal_effectiveness",
    "attention to detail": "personal_effectiveness",
    "collaboration": "interpersonal",
    "communication": "interpersonal",
    "conflict resolution": "interpersonal",
    "creativity": "cognitive",
    "critical thinking": "cognitive",
    "decision making": "leadership",
    "emotional intelligence": "interpersonal",
    "interpersonal skills": "interpersonal",
    "leadership": "leadership",
    "mentoring": "leadership",
    "negotiation": "interpersonal",
    "organization": "personal_effectiveness",
    "presentation": "communication",
    "problem solving": "cognitive",
    "teamwork": "interpersonal",
    "time management": "personal_effectiveness",
}


def extract_skill_features(candidate: dict) -> dict:
    """Extract structured, normalized skill features from a candidate.

    String skill entries are normalized and deduplicated in first-seen order.
    Blank and non-string entries are ignored.  Recognized skills are placed in
    technical and soft-skill lists; unrecognized skills remain available in
    ``normalized_skills`` without being assigned an arbitrary category.

    ``skill_count`` is the number of valid, nonblank source entries before
    deduplication.  ``unique_skill_count`` is the number of canonical skills
    after deduplication.

    Args:
        candidate: Candidate record containing a list-valued ``skills`` field.

    Returns:
        A dictionary containing normalized skills, categorized skill lists,
        source and unique counts, and the first normalized skill as the primary
        skill.  Empty features are returned for malformed input.
    """
    if not isinstance(candidate, dict):
        logger.warning(
            "Cannot extract skill features: expected a dictionary, received %s",
            type(candidate).__name__,
        )
        return _empty_skill_features()

    raw_skills = candidate.get("skills", [])
    if not isinstance(raw_skills, list):
        logger.warning(
            "Cannot extract skill features for candidate %r: skills must be a "
            "list",
            candidate.get("candidate_id", "<unknown>"),
        )
        return _empty_skill_features()

    valid_skills = _get_valid_skill_entries(raw_skills)
    normalized_skills = [
        skill for skill in normalize_skill_list(valid_skills) if skill
    ]
    technical_skills = [
        skill for skill in normalized_skills if skill in TECHNICAL_SKILLS
    ]
    soft_skills = [
        skill for skill in normalized_skills if skill in SOFT_SKILLS
    ]

    features = {
        "normalized_skills": normalized_skills,
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "skill_count": len(valid_skills),
        "unique_skill_count": len(normalized_skills),
        "primary_skill": normalized_skills[0] if normalized_skills else None,
    }
    logger.info(
        "Extracted %d unique skill(s) from %d valid source entries for "
        "candidate %r",
        len(normalized_skills),
        len(valid_skills),
        candidate.get("candidate_id", "<unknown>"),
    )
    return features


def _get_valid_skill_entries(skills: list[object]) -> list[str]:
    """Return nonblank string skill entries in their original order.

    Args:
        skills: Raw values from a candidate's skill collection.

    Returns:
        String skill values that contain at least one non-whitespace character.
    """
    valid_skills = [
        skill
        for skill in skills
        if isinstance(skill, str) and skill.strip()
    ]
    ignored_count = len(skills) - len(valid_skills)
    if ignored_count:
        logger.warning("Ignored %d invalid or blank skill value(s)", ignored_count)

    return valid_skills


def _empty_skill_features() -> dict:
    """Create an empty feature dictionary matching the public contract.

    Returns:
        A new dictionary containing empty skill lists, zero counts, and no
        primary skill.
    """
    return {
        "normalized_skills": [],
        "technical_skills": [],
        "soft_skills": [],
        "skill_count": 0,
        "unique_skill_count": 0,
        "primary_skill": None,
    }
