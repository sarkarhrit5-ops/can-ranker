"""Generate concise candidate reasoning."""

import logging

from src.models.match_result import MatchResult
from src.models.score_result import ScoreResult

logger = logging.getLogger(__name__)

AI_SKILLS = {
    "python",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "nlp",
    "llm",
    "llms",
    "transformers",
    "bert",
    "gpt",
    "rag",
    "retrieval",
    "ranking",
    "embeddings",
    "embedding",
    "vector search",
    "vector database",
    "milvus",
    "faiss",
    "weaviate",
    "pinecone",
    "qdrant",
    "langchain",
    "llamaindex",
    "lora",
    "qlora",
    "fine-tuning",
    "huggingface",
    "scikit-learn",
    "mlflow",
    "kubeflow",
    "airflow",
    "spark",
}


def _profile(candidate: dict) -> dict:
    return candidate.get("profile", {})


def _years(candidate: dict) -> float:
    try:
        return float(_profile(candidate).get("years_of_experience", 0))
    except Exception:
        return 0.0


def _title(candidate: dict) -> str:
    return (
        _profile(candidate).get("current_title")
        or _profile(candidate).get("headline")
        or "Candidate"
    )


def _response_rate(candidate: dict) -> float:
    signals = candidate.get("redrob_signals", {})
    try:
        return float(signals.get("recruiter_response_rate", 0))
    except Exception:
        return 0.0


def _ai_skill_count(candidate: dict) -> int:
    skills = candidate.get("skills", [])

    count = 0

    for skill in skills:

        if isinstance(skill, dict):
            name = skill.get("name", "").lower()

        elif isinstance(skill, str):
            name = skill.lower()

        else:
            continue

        for ai in AI_SKILLS:
            if ai in name:
                count += 1
                break

    return count


def generate_reason(
    candidate: dict,
    match: MatchResult,
    score: ScoreResult,
) -> str:

    try:

        title = _title(candidate)

        years = _years(candidate)

        ai = _ai_skill_count(candidate)

        response = _response_rate(candidate)

        return (
            f"{title} with {years:.1f} yrs; "
            f"{ai} AI core skills; "
            f"response rate {response:.2f}."
        )

    except Exception:

        logger.exception("Reason generation failed")

        return "Candidate profile evaluated."