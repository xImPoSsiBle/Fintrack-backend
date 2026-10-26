import time
import uuid

from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger("app.requests")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        structlog.contextvars.clear_contextvars()
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
                user_id=getattr(request.state, "user_id", None),
            )