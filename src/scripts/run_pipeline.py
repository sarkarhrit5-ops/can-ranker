"""Run the end-to-end candidate ranking pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

from src.consistency.consistency_engine import analyze_candidate_consistency
from src.exporter.csv_exporter import export_score_results
from src.features.feature_extractor import extract_candidate_features
from src.fraud.fraud_engine import analyze_candidate_fraud
from src.matcher.semantic_matcher import semantic_match
from src.models.score_result import ScoreResult
from src.parser.candidate_loader import validate_candidate
from src.parser.jd_loader import load_job_description
from src.reasoning.reason_generator import generate_reason
from src.scoring.score_calculator import calculate_score


logger = logging.getLogger(__name__)

DEFAULT_JOB_DESCRIPTION_PATH = Path("data/raw/job_description.docx")
DEFAULT_CANDIDATES_PATH = Path("data/raw/candidates.jsonl")
DEFAULT_OUTPUT_PATH = Path("data/output/submission.csv")
TOP_CANDIDATE_LIMIT = 100


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Optional argument sequence. When omitted, ``sys.argv`` is used.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run CAN-Ranker and export the top candidate submission CSV."
    )
    parser.add_argument(
        "--job-description",
        type=Path,
        default=DEFAULT_JOB_DESCRIPTION_PATH,
        help="Path to the job description JSON or DOCX file.",
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES_PATH,
        help="Path to the JSON Lines candidates file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path for the generated submission CSV.",
    )
    return parser.parse_args(argv)


def iter_candidate_jsonl(file_path: Path) -> Iterator[dict[str, Any]]:
    """Yield structurally valid candidates from a JSON Lines file.

    Blank lines are ignored. Malformed JSON lines and structurally invalid
    candidates are logged and skipped.

    Args:
        file_path: Path to the candidate JSONL file.

    Yields:
        Valid candidate dictionaries, one at a time.

    Raises:
        FileNotFoundError: If the candidates file does not exist.
        OSError: If the candidates file cannot be read.
    """
    if not file_path.is_file():
        message = f"Candidate JSONL file does not exist: {file_path}"
        logger.error(message)
        raise FileNotFoundError(message)

    with file_path.open("r", encoding="utf-8") as candidates_file:
        for line_number, line in enumerate(candidates_file, start=1):
            raw_line = line.strip()
            if not raw_line:
                continue

            try:
                candidate = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Skipping malformed JSON candidate at line %d: %s",
                    line_number,
                    exc.msg,
                )
                continue

            if not validate_candidate(candidate):
                logger.warning(
                    "Skipping invalid candidate at line %d", line_number
                )
                continue

            candidate_id = candidate.get("candidate_id")
            if not isinstance(candidate_id, str) or not candidate_id.strip():
                logger.warning(
                    "Skipping candidate at line %d: candidate_id is empty",
                    line_number,
                )
                continue

            yield candidate


def process_candidate(
    candidate: dict[str, Any],
    job_description: dict[str, Any],
) -> ScoreResult:
    """Run one candidate through the existing ranking pipeline.

    Args:
        candidate: Validated candidate record.
        job_description: Parsed job description.

    Returns:
        Score result populated with generated reasoning.
    """
    candidate_id = candidate["candidate_id"]
    candidate_features = extract_candidate_features(candidate)
    match_result = semantic_match(candidate_features, job_description)
    score_result = calculate_score(match_result)
    score_result.reasoning = generate_reason(match_result, score_result)

    fraud_result = analyze_candidate_fraud(candidate)
    if fraud_result.get("fraud_detected"):
        logger.warning("Fraud detected for candidate %s", candidate_id)

    consistency_result = analyze_candidate_consistency(candidate)
    if not consistency_result.get("overall_consistent", True):
        logger.warning("Consistency failed for candidate %s", candidate_id)

    return score_result


def rank_candidates(score_results: list[ScoreResult]) -> list[ScoreResult]:
    """Sort score results, assign ranks, and retain the top candidates.

    Args:
        score_results: Unranked score results.

    Returns:
        The top ranked score results in descending score order.
    """
    sorted_results = sorted(
        score_results,
        key=lambda result: result.total_score,
        reverse=True,
    )
    top_results = sorted_results[:TOP_CANDIDATE_LIMIT]

    for rank, result in enumerate(top_results, start=1):
        result.ranking = rank

    return top_results


def run_pipeline(
    job_description_path: Path = DEFAULT_JOB_DESCRIPTION_PATH,
    candidates_path: Path = DEFAULT_CANDIDATES_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> list[ScoreResult]:
    """Execute the full recruitment ranking pipeline.

    Args:
        job_description_path: Path to the JSON job-description file.
        candidates_path: Path to the JSONL candidates file.
        output_path: Destination submission CSV path.

    Returns:
        The ranked top score results exported to CSV.
    """
    logger.info("Loading job description from %s", job_description_path)
    job_description = load_job_description(job_description_path)

    score_results: list[ScoreResult] = []
    processed_count = 0
    skipped_count = 0

    logger.info("Loading candidates from %s", candidates_path)
    for candidate in iter_candidate_jsonl(candidates_path):
        candidate_id = candidate.get("candidate_id", "<unknown>")
        try:
            score_results.append(process_candidate(candidate, job_description))
            processed_count += 1
            logger.debug("Candidate processed: %s", candidate_id)
        except Exception:
            skipped_count += 1
            logger.exception("Skipping candidate %r after pipeline error", candidate_id)

        if processed_count and processed_count % 1000 == 0:
            logger.info("Candidate processed count: %d", processed_count)

    ranked_results = rank_candidates(score_results)
    export_score_results(ranked_results, output_path)
    logger.info("CSV exported: %s", output_path)

    logger.info(
        "Finished pipeline: processed=%d skipped=%d exported=%d",
        processed_count,
        skipped_count,
        len(ranked_results),
    )
    return ranked_results


def main(argv: Sequence[str] | None = None) -> int:
    """Run the pipeline from the command line.

    Args:
        argv: Optional argument sequence. When omitted, ``sys.argv`` is used.

    Returns:
        Process exit code.
    """
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.setLevel(logging.INFO)
    args = parse_args(argv)
    run_pipeline(args.job_description, args.candidates, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
