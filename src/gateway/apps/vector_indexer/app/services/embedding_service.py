__anchor__ = "vector-indexer"
# schema-ref: project-schema.yaml#/services/8

import hashlib
from typing import Any

from backend.shared.db.qdrant import VECTOR_SIZE


class EmbeddingService:
    """Generates text embeddings.

    In dev mode, uses deterministic feature-hashing (character n-grams →
    fixed-size vector). In production, this delegates to an embedding model
    via the LLM provider router.
    """

    def __init__(self, provider_router: Any | None = None) -> None:
        self._router = provider_router
        self._dim = VECTOR_SIZE

    async def embed(self, text: str) -> list[float]:
        if self._router:
            result = await self._router.embed(text)
            return list(result)
        return self._hash_embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if self._router:
            return [await self._router.embed(t) for t in texts]
        return [self._hash_embed(t) for t in texts]

    def _hash_embed(self, text: str) -> list[float]:
        vec = [0.0] * self._dim
        text_lower = text.lower()
        for n in range(2, 5):
            for i in range(len(text_lower) - n + 1):
                ngram = text_lower[i : i + n]
                h = hashlib.md5(ngram.encode(), usedforsecurity=False)
                idx = int(h.hexdigest()[:8], 16) % self._dim
                sign = -1 if int(h.hexdigest()[8:12], 16) % 2 == 0 else 1
                vec[idx] += sign * 1.0

        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec
