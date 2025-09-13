import time
from typing import Optional

from fastapi import Request
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)


def _route_path(scope) -> Optional[str]:
    route = scope.get("route")
    if route and getattr(route, "path", None):
        return route.path
    return scope.get("path")


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = _route_path(request.scope) or "unknown"
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        REQUEST_COUNT.labels(method=method, path=path, status=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(elapsed)
        return response

