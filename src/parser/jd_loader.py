    try:
        with path.open("r", encoding="utf-8") as job_file:
            return path, json.load(job_file)
    except json.JSONDecodeError as exc:
        logger.error(
            "Invalid JSON in job-description file %s at line %d, column %d: %s",
            path,
            exc.lineno,
            exc.colno,
            exc.msg,
        )
        raise json.JSONDecodeError(
            f"Invalid JSON in job-description file '{path}': {exc.msg}",
            exc.doc,
            exc.pos,
        ) from exc
    except OSError:
        logger.exception("Unable to read job-description file: %s", path)
        raise


def load_job_description(file_path: str) -> dict:
    """Load one valid job description from a JSON file.

    The file must contain a JSON object with every required top-level field.
    Additional fields are preserved.

    Args:
        file_path: Path to a UTF-8 encoded JSON job-description file.

    Returns:
        The validated job-description dictionary.

    Raises:
        FileNotFoundError: If ``file_path`` does not exist or is not a file.
        json.JSONDecodeError: If the file does not contain valid JSON.
        JobDescriptionSchemaError: If the JSON root is not an object or the
            job description is missing a required field.
        OSError: If the file cannot be read for another operating-system
            reason.
    """
    path, job_description = _load_json(file_path)
    if not isinstance(job_description, dict):
        _raise_schema_error(path, "the JSON root must be an object")

    if not validate_job_description(job_description):
        _raise_schema_error(
            path,
            "the job description is missing one or more required fields",
        )

    logger.info("Loaded job description %r from %s", job_description["job_id"], path)
    return job_description


def load_job_descriptions(file_path: str) -> list[dict]:
    """Load valid job descriptions from a JSON file.

    The file must contain a JSON array.  Entries that are not objects or do not
    contain every required top-level field are excluded from the result.

    Args:
        file_path: Path to a UTF-8 encoded JSON job-description file.

    Returns:
        Valid job descriptions in their original order.

    Raises:
        FileNotFoundError: If ``file_path`` does not exist or is not a file.
        json.JSONDecodeError: If the file does not contain valid JSON.
        JobDescriptionSchemaError: If the JSON root is not an array.
        OSError: If the file cannot be read for another operating-system
            reason.
    """
    path, job_descriptions = _load_json(file_path)
    if not isinstance(job_descriptions, list):
        _raise_schema_error(path, "the JSON root must be an array")

    valid_jobs = [
        job
        for job in job_descriptions
        if validate_job_description(job)
    ]
    logger.info(
        "Loaded %d valid job description(s) from %s; discarded %d invalid "
        "record(s)",
        len(valid_jobs),
        path,
        len(job_descriptions) - len(valid_jobs),
    )
    return valid_jobs


def validate_job_description(job_description: dict) -> bool:
    """Check whether a job description has all required top-level fields.

    This function validates structure only.  It does not inspect field values,
    nested structures, or business semantics, and additional fields are
    allowed.

    Args:
        job_description: Job-description record to validate.

    Returns:
        ``True`` if the value is a dictionary containing every required field;
        otherwise ``False``.
    """
    if not isinstance(job_description, dict):
        logger.warning(
            "Rejected job-description record: expected a dictionary, received %s",
            type(job_description).__name__,
        )
        return False

    missing_fields = REQUIRED_FIELDS.difference(job_description)
    if missing_fields:
        logger.warning(
            "Rejected job-description record %r: missing required field(s): %s",
            job_description.get("job_id", "<unknown>"),
            ", ".join(sorted(missing_fields)),
        )
        return False

    return True


def get_job_by_id(
    job_descriptions: list[dict], job_id: str
) -> dict | None:
    """Return the first job description with the requested identifier.

    Args:
        job_descriptions: Job-description records to search.
        job_id: Exact job identifier to match.

    Returns:
        The first matching job-description dictionary, or ``None`` if no match
        is found.  Malformed entries are ignored.
    """
    for job_description in job_descriptions:
        is_match = (
            isinstance(job_description, dict)
            and job_description.get("job_id") == job_id
        )
        if is_match:
            return job_description

    return None


def _raise_schema_error(path: Path, reason: str) -> None:
    """Log and raise a schema error for a job-description file.

    Args:
        path: Path of the file containing the invalid schema.
        reason: Human-readable description of the schema violation.

    Raises:
        JobDescriptionSchemaError: Always raised with file context.
    """
    message = f"Invalid job-description schema in '{path}': {reason}"
    logger.error(message)
    raise JobDescriptionSchemaError(message)
