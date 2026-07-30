__anchor__ = "vector-indexer"
# schema-ref: project-schema.yaml#/services/8

from typing import Any

from qdrant_client.models import PointStruct

from backend.apps.vector_indexer.app.services.embedding_service import (
    EmbeddingService,
)
from backend.shared.db.qdrant import DEFAULT_COLLECTION, QdrantClient


class IndexerService:
    """Orchestrates embedding generation and Qdrant indexing."""

    def __init__(self, qdrant: QdrantClient | None = None) -> None:
        self._qdrant = qdrant or QdrantClient()
        self._embedder = EmbeddingService()
        self._connected = False

    async def ensure_connected(self) -> bool:
        if self._connected:
            return True
        try:
            await self._qdrant.connect()
            self._connected = True
            return True
        except Exception:
            return False

    async def index_fragments(
        self,
        fragments: list[dict[str, Any]],
        collection: str = DEFAULT_COLLECTION,
    ) -> int:
        if not await self.ensure_connected():
            return 0
        texts = [f.get("fragment_text", "") for f in fragments]
        vectors = await self._embedder.embed_batch(texts)
        points = []
        for f, vec in zip(fragments, vectors, strict=False):
            points.append(PointStruct(
                id=f["fragment_id"],
                vector=vec,
                payload={
                    "document_title": f.get("document_title"),
                    "fragment_text": f.get("fragment_text", ""),
                    "citation_label": f.get("citation_label"),
                    "tier": f.get("tier", 1),
                    "source_domain": f.get("source_domain"),
                },
            ))
        await self._qdrant.upsert_points(points, collection=collection)
        return len(points)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        collection: str = DEFAULT_COLLECTION,
    ) -> list[dict[str, Any]]:
        if not await self.ensure_connected():
            return []
        vector = await self._embedder.embed(query)
        hits = await self._qdrant.search_points(
            vector=vector,
            top_k=top_k,
            collection=collection,
        )
        results = []
        for h in hits:
            payload = h.get("payload", {})
            results.append({
                "fragment_id": h["fragment_id"],
                "score": h["score"],
                "document_title": payload.get("document_title"),
                "fragment_text": payload.get("fragment_text"),
                "citation_label": payload.get("citation_label"),
                "tier": payload.get("tier", 1),
                "source_domain": payload.get("source_domain"),
            })
        return results

    async def delete_fragments(
        self,
        fragment_ids: list[str],
        collection: str = DEFAULT_COLLECTION,
    ) -> int:
        if not await self.ensure_connected():
            return 0
        await self._qdrant.delete_points(fragment_ids, collection=collection)
        return len(fragment_ids)
