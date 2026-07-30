__anchor__ = "logging"

import logging
import sys
import uuid

import structlog


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
            if sys.stderr.isatty()
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)


logger = structlog.get_logger()


class RequestLoggingMiddleware:
    """ASGI middleware that adds trace_id to request scope and logs each request."""

    def __init__(self, app: callable) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: callable, send: callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        trace_id = str(uuid.uuid4())[:8]
        scope["trace_id"] = trace_id

        async def wrapped_send(message: dict) -> None:
            if message.get("type") == "http.response.start":
                status = message.get("status", 500)
                logger.info(
                    "http_request",
                    trace_id=trace_id,
                    method=scope.get("method"),
                    path=scope.get("path"),
                    status=status,
                )
            await send(message)

        await self.app(scope, receive, wrapped_send)
