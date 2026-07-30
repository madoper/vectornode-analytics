__anchor__ = "db-clients"
# schema-ref: project-schema.yaml#/shared_modules/2

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from qdrant_client import AsyncQdrantClient as _AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    UpdateResult,
    VectorParams,
)

from backend.shared.settings import settings

DEFAULT_COLLECTION = "podft_fragments"
VECTOR_SIZE = 384


class QdrantClient:
    """Async Qdrant client wrapper.

    Provides high-level methods for collection management, point indexing,
    and vector search. Wraps the official qdrant-client AsyncQdrantClient.
    """

    def __init__(self) -> None:
        self._client: _AsyncQdrantClient | None = None

    @property
    def _inner(self) -> _AsyncQdrantClient:
        if self._client is None:
            msg = "QdrantClient not connected. Call connect() first."
            raise RuntimeError(msg)
        return self._client

    async def connect(self) -> None:
        self._client = _AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            prefer_grpc=False,
            timeout=10,
        )
        await self._ensure_collection()

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None

    async def _ensure_collection(self, collection: str = DEFAULT_COLLECTION) -> None:
        client = self._inner
        collections = await client.get_collections()
        names = [c.name for c in collections.collections]
        if collection not in names:
            await client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )

    async def upsert_points(
        self,
        points: list[PointStruct],
        collection: str = DEFAULT_COLLECTION,
    ) -> UpdateResult:
        client = self._inner
        return await client.upsert(
            collection_name=collection,
            points=points,
        )

    async def search_points(
        self,
        vector: list[float],
        top_k: int = 10,
        score_threshold: float | None = None,
        collection: str = DEFAULT_COLLECTION,
    ) -> list[dict[str, Any]]:
        client = self._inner
        hits = await client.query_points(
            collection_name=collection,
            query=vector,
            limit=top_k,
            score_threshold=score_threshold,
        )
        return [
            {
                "fragment_id": p.id,
                "score": p.score,
                "payload": p.payload or {},
            }
            for p in hits.points
        ]

    async def delete_points(
        self,
        point_ids: list[str],
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        client = self._inner
        await client.delete(
            collection_name=collection,
            points_selector=point_ids,  # type: ignore[arg-type]
        )

    async def scroll_points(
        self,
        limit: int = 100,
        offset: int = 0,
        collection: str = DEFAULT_COLLECTION,
    ) -> list[dict[str, Any]]:
        client = self._inner
        records, _ = await client.scroll(
            collection_name=collection,
            limit=limit,
            offset=offset,
        )
        return [
            {
                "fragment_id": p.id,
                "payload": p.payload or {},
            }
            for p in records
        ]

    async def delete_collection(self, collection: str = DEFAULT_COLLECTION) -> None:
        client = self._inner
        await client.delete_collection(collection_name=collection)


@asynccontextmanager
async def get_qdrant() -> AsyncIterator[QdrantClient]:
    client = QdrantClient()
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()
