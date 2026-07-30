__anchor__ = "idempotency"

import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

IDEMPOTENCY_TTL = 3600


class IdempotencyKeyMiddleware(BaseHTTPMiddleware):
    """Middleware for Idempotency-Key support on POST/PUT/PATCH endpoints.

    Stores response for 1 hour. Same key + same request body = same response.
    """

    def __init__(self, app: Any, backend: dict[str, Any] | None = None) -> None:
        super().__init__(app)
        self._cache: dict[str, dict[str, Any]] = backend or {}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method not in {"POST", "PUT", "PATCH"}:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        body = await request.body()
        body_hash = hashlib.sha256(body).hexdigest()
        cache_key = f"{idempotency_key}:{request.url.path}:{body_hash}"

        cached = self._get(cache_key)
        if cached is not None:
            return JSONResponse(
                content=cached["content"],
                status_code=cached["status_code"],
                headers={"Idempotency-Replay": "true", **cached.get("headers", {})},
            )

        response = await call_next(request)

        if response.status_code < 500:
            resp_body = b""
            async for chunk in response.body_iterator:
                resp_body += chunk
            content_type = response.headers.get("content-type", "")
            headers = dict(response.headers)

            self._set(cache_key, {
                "content": json.loads(resp_body) if "json" in content_type else resp_body.decode(),
                "status_code": response.status_code,
                "headers": headers,
            })

            return JSONResponse(
                content=json.loads(resp_body) if "json" in content_type else resp_body.decode(),
                status_code=response.status_code,
                headers=headers,
            )

        return response

    def _get(self, key: str) -> dict[str, Any] | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None
        return entry

    def _set(self, key: str, value: dict[str, Any]) -> None:
        self._cache[key] = {
            **value,
            "expires_at": time.time() + IDEMPOTENCY_TTL,
        }
