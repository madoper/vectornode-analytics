"""Async Neo4j driver wrapper with connection pooling and graceful fallback."""

from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase

from backend.shared.logging import logger
from backend.shared.settings import settings

__anchor__ = "neo4j-client"
# schema-ref: project-schema.yaml#/shared_modules/6


class Neo4jClient:
    """Async Neo4j client wrapper.

    When Neo4j is unavailable (e.g. on 1 GB VPS), available property
    returns False and callers handle graceful fallback.
    """

    def __init__(self) -> None:
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        if self._driver:
            return
        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_pool_size=10,
                connection_timeout=5,
            )
            await self._driver.verify_connectivity()
            logger.info("neo4j connected", uri=settings.neo4j_uri, anchor="neo4j-client")
        except Exception as exc:
            logger.warning("neo4j unavailable, falling back", error=str(exc), anchor="neo4j-client")
            self._driver = None

    @property
    def available(self) -> bool:
        return self._driver is not None

    async def run(
        self, query: str, parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if not self._driver:
            msg = "Neo4j is not connected"
            raise RuntimeError(msg)
        async with self._driver.session() as session:
            result = await session.run(query, parameters or {})
            return [dict(r) for r in await result.data()]

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            self._driver = None
