__anchor__ = "rate-limiter"
# schema-ref: project-schema.yaml#/shared_modules/3

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.shared.db.redis import redis_client

DEFAULT_RATE = 100
DEFAULT_WINDOW = 60
RATE_LIMIT_PREFIX = "ratelimit:"


def _key(request: Request) -> str:
    client_ip = request.client.host if request.client else "unknown"
    route = request.url.path
    return f"{RATE_LIMIT_PREFIX}{route}:{client_ip}"


async def check_rate_limit(
    key: str,
    max_requests: int = DEFAULT_RATE,
    window_sec: int = DEFAULT_WINDOW,
) -> tuple[bool, int, int]:
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, window_sec)
    ttl = await redis_client.ttl(key)
    if ttl < 0:
        ttl = window_sec
    limited = count > max_requests
    return limited, count, ttl


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        max_requests: int = DEFAULT_RATE,
        window_sec: int = DEFAULT_WINDOW,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_sec = window_sec

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not await redis_client.is_available():
            return await call_next(request)

        key = _key(request)
        limited, count, ttl = await check_rate_limit(key, self.max_requests, self.window_sec)

        if limited:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after_sec": ttl,
                    "rate_limit": self.max_requests,
                    "window_sec": self.window_sec,
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + ttl)),
                    "Retry-After": str(ttl),
                },
            )

        response = await call_next(request)
        remaining = max(0, self.max_requests - count)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + ttl))
        return response
