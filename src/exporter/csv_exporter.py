"""CSV exporter for ranked candidate score results."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Iterable

from src.models.score_result import ScoreResult


logger = logging.getLogger(__name__)

CSV_HEADER = ("candidate_id", "rank", "score", "reasoning")


def export_score_results(
    score_results: Iterable[ScoreResult],
    output_path: str | Path,
) -> None:
    """Export ranked score results to a UTF-8 CSV file.

    Args:
        score_results: Ranked score results to export.
        output_path: Destination CSV path.

    Raises:
        OSError: If the output file cannot be written.
    """
    path = Path(output_path)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(CSV_HEADER)

        for result in score_results:
            writer.writerow(
                (
                    result.candidate_id,
                    result.ranking,
                    f"{result.total_score:.4f}",
                    result.reasoning,
                )
            )
            rows_written += 1

    logger.info("Exported %d ranked candidate(s) to %s", rows_written, path)
