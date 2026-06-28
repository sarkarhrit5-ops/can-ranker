def normalize_skill(skill: str) -> str:
    """Normalize a skill name and resolve known aliases.

    Args:
        skill: Skill name or abbreviation.

    Returns:
        The canonical skill name when an alias is known; otherwise the
        normalized input.

    Raises:
        TypeError: If ``skill`` is not a string.
    """
    normalized_skill = normalize_text(skill)
    canonical_skill = SKILL_ALIASES.get(normalized_skill, normalized_skill)
    _log_change("skill", skill, canonical_skill)
    return canonical_skill


def normalize_skill_list(skills: list[str]) -> list[str]:
    """Normalize and deduplicate skill names while preserving order.

    The first occurrence of each canonical skill is retained.  Comparisons are
    made after normalization, so aliases of an earlier skill are removed as
    duplicates.

    Args:
        skills: Skill names to normalize.

    Returns:
        A new list of unique canonical skill names in first-seen order.

    Raises:
        TypeError: If ``skills`` is not a list or an item is not a string.
    """
    if not isinstance(skills, list):
        message = "skills must be a list"
        logger.error(message)
        raise TypeError(message)

    normalized_skills: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        normalized_skill = normalize_skill(skill)
        if normalized_skill not in seen:
            seen.add(normalized_skill)
            normalized_skills.append(normalized_skill)

    return normalized_skills


def normalize_degree(degree: str) -> str:
    """Normalize a degree name and expand common abbreviations.

    Args:
        degree: Degree name or abbreviation.

    Returns:
        The canonical degree name when an abbreviation is known; otherwise the
        normalized input.

    Raises:
        TypeError: If ``degree`` is not a string.
    """
    normalized_degree = normalize_text(degree)
    canonical_degree = DEGREE_ALIASES.get(normalized_degree, normalized_degree)
    _log_change("degree", degree, canonical_degree)
    return canonical_degree


def normalize_company(company: str) -> str:
    """Normalize a company name and remove known legal suffixes.

    Suffix matching is case-insensitive because text is normalized first.
    Separating punctuation left before a removed suffix is also discarded.

    Args:
        company: Company name to normalize.

    Returns:
        The normalized company name without recognized legal suffixes.

    Raises:
        TypeError: If ``company`` is not a string.
    """
    normalized_company = normalize_text(company)
    suffixes = sorted(COMPANY_SUFFIX_ALIASES, key=len, reverse=True)

    suffix_removed = True
    while normalized_company and suffix_removed:
        suffix_removed = False
        for suffix in suffixes:
            if normalized_company == suffix:
                normalized_company = COMPANY_SUFFIX_ALIASES[suffix]
                suffix_removed = True
                break

            suffix_with_separator = f" {suffix}"
            if normalized_company.endswith(suffix_with_separator):
                normalized_company = normalized_company[
                    :-len(suffix_with_separator)
                ].rstrip(" ,.-")
                suffix_removed = True
                break

    _log_change("company", company, normalized_company)
    return normalized_company


def _ensure_string(value: object, *, parameter_name: str) -> None:
    """Raise a meaningful error when a normalization input is not text.

    Args:
        value: Value to validate.
        parameter_name: Public parameter name used in the error message.

    Raises:
        TypeError: If ``value`` is not a string.
    """
    if not isinstance(value, str):
        message = f"{parameter_name} must be a string"
        logger.error(message)
        raise TypeError(message)


def _log_change(value_type: str, original: str, normalized: str) -> None:
    """Log a normalization change at debug level.

    Args:
        value_type: Human-readable category of the normalized value.
        original: Value before normalization.
        normalized: Value after normalization.
    """
    if original != normalized:
        logger.debug("Normalized %s %r to %r", value_type, original, normalized)
