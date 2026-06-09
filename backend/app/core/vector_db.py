"""Qdrant vector database client and collection management."""

import logging
import uuid
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None
_collection_ready = False


def get_qdrant_client():
    """Return a Qdrant client or None if unavailable."""
    global _client
    if _client is not None:
        return _client

    try:
        from qdrant_client import QdrantClient

        _client = QdrantClient(url=settings.qdrant_url, timeout=10)
        return _client
    except Exception as error:
        logger.warning("Qdrant unavailable: %s", error)
        return None


def ensure_collection() -> bool:
    """Create the materials collection if it does not exist."""
    global _collection_ready
    if _collection_ready:
        return True

    client = get_qdrant_client()
    if client is None:
        return False

    try:
        from qdrant_client.http import models as qmodels

        collections = {item.name for item in client.get_collections().collections}
        if settings.qdrant_collection not in collections:
            client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=qmodels.VectorParams(
                    size=settings.embedding_dimension,
                    distance=qmodels.Distance.COSINE,
                ),
            )
            client.create_payload_index(
                collection_name=settings.qdrant_collection,
                field_name="subject_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD,
            )
            client.create_payload_index(
                collection_name=settings.qdrant_collection,
                field_name="material_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD,
            )
            logger.info("Created Qdrant collection '%s'", settings.qdrant_collection)

        _collection_ready = True
        return True
    except Exception as error:
        logger.warning("Failed to ensure Qdrant collection: %s", error)
        return False


def upsert_chunks(
    chunks: List[Dict[str, Any]],
    vectors: List[List[float]],
) -> bool:
    """Upsert embedded chunks into Qdrant."""
    client = get_qdrant_client()
    if client is None or not ensure_collection():
        return False

    from qdrant_client.http import models as qmodels

    points = []
    for chunk, vector in zip(chunks, vectors):
        points.append(
            qmodels.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=chunk,
            )
        )

    if not points:
        return True

    client.upsert(collection_name=settings.qdrant_collection, points=points)
    return True


def delete_by_material_id(material_id: str) -> None:
    client = get_qdrant_client()
    if client is None:
        return

    from qdrant_client.http import models as qmodels

    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="material_id",
                        match=qmodels.MatchValue(value=material_id),
                    )
                ]
            )
        ),
    )


def delete_by_subject_id(subject_id: str) -> None:
    client = get_qdrant_client()
    if client is None:
        return

    from qdrant_client.http import models as qmodels

    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="subject_id",
                        match=qmodels.MatchValue(value=subject_id),
                    )
                ]
            )
        ),
    )


def search_similar(
    query_vector: List[float],
    subject_id: str,
    top_k: int,
    score_threshold: float,
) -> List[Dict[str, Any]]:
    """Search for similar chunks filtered by subject."""
    client = get_qdrant_client()
    if client is None or not ensure_collection():
        return []

    from qdrant_client.http import models as qmodels

    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        query_filter=qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="subject_id",
                    match=qmodels.MatchValue(value=subject_id),
                )
            ]
        ),
        limit=top_k,
        score_threshold=score_threshold,
    )

    hits = []
    for result in results:
        payload = result.payload or {}
        hits.append(
            {
                "filename": payload.get("source_filename", "unknown"),
                "locator": payload.get("locator", ""),
                "text": payload.get("text", ""),
                "score": float(result.score or 0.0),
            }
        )
    return hits
