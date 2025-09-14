import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.window_seconds = 60
        self.max_per_window = settings.RATE_LIMIT_PER_MIN
        self.hits: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Skip internal docs, static, and metrics by default
        path = request.url.path
        if path.startswith("/docs") or path.startswith("/openapi") or path.startswith("/static") or path.startswith("/metrics"):
            return await call_next(request)

        ident = request.client.host if request.client else "anonymous"
        now = time.time()
        q = self.hits[ident]
        q.append(now)
        # Drop entries older than window
        cutoff = now - self.window_seconds
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) > self.max_per_window:
            return JSONResponse(status_code=429, content={"error": "rate_limited"})
        return await call_next(request)

