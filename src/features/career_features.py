    """
    if value is None:
        return date.today() if use_today else None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        if 1 <= value <= 9999:
            return date(value, 1, 1)
        return None
    if not isinstance(value, str):
        return None

    normalized_value = value.strip().casefold()
    if normalized_value in _PRESENT_MARKERS:
        return date.today()

    formats = ("%Y-%m-%d", "%Y-%m", "%Y")
    for date_format in formats:
        try:
            return datetime.strptime(normalized_value, date_format).date()
        except ValueError:
            continue

    logger.warning("Ignored unsupported career date value %r", value)
    return None


def _months_between(start_date: date, end_date: date) -> int:
    """Calculate completed calendar months between two dates."""
    months = (
        (end_date.year - start_date.year) * 12
        + end_date.month
        - start_date.month
    )
    if end_date.day < start_date.day:
        months -= 1
    return max(months, 0)


def _normalize_optional_text(value: object) -> str | None:
    """Return normalized nonblank text or ``None``."""
    if not isinstance(value, str):
        return None
    normalized_value = " ".join(value.casefold().split())
    return normalized_value or None


def _extract_nonnegative_number(value: object) -> float | None:
    """Return a finite nonnegative number or ``None``."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric_value = float(value)
    if numeric_value < 0 or numeric_value == float("inf"):
        return None
    if numeric_value != numeric_value:
        return None
    return numeric_value


def _extract_nonnegative_int(value: object) -> int:
    """Return a nonnegative integer count, defaulting to zero."""
    numeric_value = _extract_nonnegative_number(value)
    return int(numeric_value) if numeric_value is not None else 0


def _normalize_title(title: str) -> str:
    """Normalize title punctuation for keyword matching."""
    return " ".join(re.sub(r"[^a-z0-9+#]+", " ", title).split())


def _get_seniority_level(title: str | None) -> str:
    """Map a role title to a deterministic seniority level."""
    if not title:
        return "unknown"

    normalized_title = _normalize_title(title)
    padded_title = f" {normalized_title} "
    for level, keywords in _SENIORITY_KEYWORDS.items():
        if any(f" {keyword} " in padded_title for keyword in keywords):
            return level
    return "mid"


def _seniority_rank(title: str | None) -> int:
    """Return the ordinal rank of a role title's seniority level."""
    return _SENIORITY_LEVELS.index(_get_seniority_level(title))


def _get_highest_seniority(entries: list[_CareerEntry]) -> str:
    """Return the highest recognized seniority across parsed entries."""
    return max(
        (_get_seniority_level(entry.title) for entry in entries),
        key=_SENIORITY_LEVELS.index,
        default="unknown",
    )


def _is_leadership_title(title: str | None) -> bool:
    """Return whether a role title indicates leadership responsibility."""
    return _get_seniority_level(title) in {
        "lead",
        "manager",
        "director",
        "executive",
    }


def _get_explicit_promotion_count(
    candidate: dict,
    entries: list[_CareerEntry],
) -> int:
    """Return the largest available explicit promotion count."""
    entry_count = sum(entry.explicit_promotions for entry in entries)
    candidate_count = _extract_nonnegative_int(candidate.get("promotion_count"))
    return max(entry_count, candidate_count)


def _infer_promotion_count(entries: list[_CareerEntry]) -> int:
    """Infer upward same-company seniority transitions."""
    entries_by_company: dict[str, list[_CareerEntry]] = {}
    for entry in entries:
        if entry.company:
            entries_by_company.setdefault(entry.company, []).append(entry)

    promotion_count = 0
    for company_entries in entries_by_company.values():
        ordered_entries = sorted(company_entries, key=_career_entry_sort_key)
        previous_rank: int | None = None
        for entry in ordered_entries:
            if not entry.title:
                continue
            current_rank = _seniority_rank(entry.title)
            if previous_rank is not None and current_rank > previous_rank:
                promotion_count += 1
            previous_rank = current_rank

    return promotion_count


def _career_entry_sort_key(entry: _CareerEntry) -> tuple[int, int]:
    """Sort dated entries chronologically and preserve undated source order."""
    if entry.start_date is not None:
        return entry.start_date.toordinal(), entry.sequence
    return date.max.toordinal(), entry.sequence


def _calculate_career_growth_score(
    entries: list[_CareerEntry],
    promotion_count: int,
) -> float:
    """Calculate a bounded, descriptive career-progression metric.

    Half of the metric reflects seniority gained from the earliest observed
    role to the highest role, and half reflects up to three promotions.  This
    is a trajectory summary, not a suitability or matching score.
    """
    titled_entries = [entry for entry in entries if entry.title]
    if not titled_entries:
        return 0.0

    ordered_entries = sorted(titled_entries, key=_career_entry_sort_key)
    initial_rank = _seniority_rank(ordered_entries[0].title)
    highest_rank = max(_seniority_rank(entry.title) for entry in titled_entries)
    maximum_gain = max(len(_SENIORITY_LEVELS) - 1 - initial_rank, 1)
    seniority_growth = max(highest_rank - initial_rank, 0) / maximum_gain
    promotion_growth = min(promotion_count / 3, 1.0)
    return round(min((seniority_growth + promotion_growth) / 2, 1.0), 3)


def _empty_career_features() -> CareerFeatures:
    """Return the neutral feature value for missing or malformed history."""
    return CareerFeatures(
        total_years_experience=0.0,
        number_of_companies=0,
        average_tenure_months=0.0,
        longest_tenure_months=0,
        shortest_tenure_months=0,
        leadership_experience=False,
        promotion_count=0,
        seniority_level="unknown",
        career_growth_score=0.0,
    )
