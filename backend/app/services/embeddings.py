"""Local embedding generation via FastEmbed."""

import logging
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        _model = TextEmbedding(model_name=settings.embedding_model)
        logger.info("Loaded embedding model %s", settings.embedding_model)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts."""
    if not texts:
        return []

    model = _get_model()
    return [vector.tolist() for vector in model.embed(texts)]


def embed_query(text: str) -> List[float]:
    """Embed a single query string."""
    vectors = embed_texts([text])
    return vectors[0] if vectors else []
