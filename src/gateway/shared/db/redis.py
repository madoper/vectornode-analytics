__anchor__ = "redis-client"
# schema-ref: project-schema.yaml#/shared_modules/2

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis.asyncio import ConnectionPool, Redis

from backend.shared.settings import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None
        self._redis: Redis | None = None

    async def connect(self) -> None:
        try:
            self._pool = ConnectionPool(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
            )
            self._redis = Redis.from_pool(self._pool)
            await self._redis.ping()
            logger.info(f"redis connected: {settings.redis_host}")
        except Exception as e:
            logger.warning(f"redis unavailable, rate limiting disabled: {e}")
            self._pool = None
            self._redis = None

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()
        if self._pool:
            await self._pool.disconnect()

    async def is_available(self) -> bool:
        if not self._redis:
            return False
        try:
            return await self._redis.ping()
        except Exception:
            return False

    async def incr(self, key: str) -> int:
        if not self._redis:
            return 0
        return await self._redis.incr(key)

    async def expire(self, key: str, seconds: int) -> bool:
        if not self._redis:
            return False
        return await self._redis.expire(key, seconds)

    async def get(self, key: str) -> str | None:
        if not self._redis:
            return None
        val = await self._redis.get(key)
        if isinstance(val, str):
            return val
        return None

    async def ttl(self, key: str) -> int:
        if not self._redis:
            return -2
        return await self._redis.ttl(key)

    async def clear(self) -> None:
        if self._redis:
            await self._redis.flushdb()


redis_client = RedisClient()


@asynccontextmanager
async def redis_lifespan() -> AsyncIterator[None]:
    await redis_client.connect()
    yield
    await redis_client.disconnect()
