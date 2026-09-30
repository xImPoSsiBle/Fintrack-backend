from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import structlog
from app.api.v1.router import api_router
from fastapi_csrf_protect.exceptions import CsrfProtectError
from app.core.logging import setup_logging
from app.core.config import settings
from app.core.middleware import LoggingMiddleware

CORS_ORIGINS = settings.cors_origins.split(",")
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
ALLOWED_HEADERS = ["Content-Type", "Authorization", "X-CSRF-Token"]


setup_logging(json_logs=settings.json_logs)

logger = structlog.get_logger(__name__)

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS
    )

app.add_middleware(LoggingMiddleware)

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})