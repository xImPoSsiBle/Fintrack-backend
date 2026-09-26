import time
import uuid

from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger("app.requests")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("unhandled_exception", path=request.url.path)
            raise
        duration = time.perf_counter() - start_time

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=round(duration*1000, 2)
        )
        response.headers["X-Request-ID"] = request_id
        return response