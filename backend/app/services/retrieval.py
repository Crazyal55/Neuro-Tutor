"""Retrieval-augmented generation helpers."""

import logging
from typing import List

from app.core.config import settings
from app.core.vector_db import search_similar
from app.models.subjects import SourceCitation
from app.services.embeddings import embed_query

logger = logging.getLogger(__name__)


def retrieve_context(query: str, subject_id: str) -> tuple[List[dict], List[SourceCitation]]:
    """Retrieve relevant chunks and citation metadata for a query."""
    if not subject_id or not query.strip():
        return [], []

    try:
        query_vector = embed_query(query)
        hits = search_similar(
            query_vector=query_vector,
            subject_id=subject_id,
            top_k=settings.rag_top_k,
            score_threshold=settings.rag_score_threshold,
        )
    except Exception as error:
        logger.warning("Retrieval failed for subject %s: %s", subject_id, error)
        return [], []

    sources = [
        SourceCitation(
            filename=hit["filename"],
            locator=hit["locator"],
            score=hit["score"],
        )
        for hit in hits
    ]
    return hits, sources


def build_rag_prompt_section(hits: List[dict]) -> str:
    """Build the course materials section for the system prompt."""
    if not hits:
        return ""

    excerpts = []
    for hit in hits:
        excerpts.append(
            f"[{hit['filename']} — {hit['locator']}]\n{hit['text']}"
        )

    joined = "\n\n".join(excerpts)
    return (
        "\n\nCOURSE MATERIALS:\n"
        "The student is studying from the excerpts below. Ground your Socratic questions in "
        "these materials when relevant. Reference locators naturally (e.g., 'Looking at slide 12…'). "
        "If the excerpts do not cover the topic, say so and ask what they already know instead of inventing content.\n\n"
        f"{joined}"
    )
