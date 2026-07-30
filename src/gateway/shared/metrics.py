__anchor__ = "metrics"

import time

from prometheus_client import Counter, Gauge, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    labelnames=["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

IN_FLIGHT_REQUESTS = Gauge(
    "http_requests_in_flight",
    "Current number of in-flight requests",
)

ACTIVE_TENANTS = Gauge(
    "active_tenants",
    "Number of active tenants",
)

LAST_REQUEST_TIMESTAMP = Gauge(
    "last_request_timestamp_seconds",
    "Timestamp of the last HTTP request",
)


async def metrics_endpoint() -> bytes:
    return generate_latest()


def observe_request(method: str, endpoint: str, status: int, duration: float) -> None:
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)


class MetricsMiddleware:
    def __init__(self, app: callable) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: callable, send: callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/unknown")
        start = time.time()
        IN_FLIGHT_REQUESTS.inc()
        LAST_REQUEST_TIMESTAMP.set_to_current_time()

        status_code = [200]

        async def wrapped_send(message: dict) -> None:
            if message.get("type") == "http.response.start":
                status_code[0] = message.get("status", 500)
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            duration = time.time() - start
            IN_FLIGHT_REQUESTS.dec()
            observe_request(method, path, status_code[0], duration)
