import uuid
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        cid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.correlation_id = cid
        # Bind correlation id for all logs in this context
        with logger.contextualize(correlation_id=cid):
            response = await call_next(request)
        response.headers["X-Request-ID"] = cid
        return response

