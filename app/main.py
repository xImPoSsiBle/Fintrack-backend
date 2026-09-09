from fastapi import FastAPI, Request, logger
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from fastapi_csrf_protect.exceptions import CsrfProtectError
from app.core.logging import setup_logging
from app.core.config import settings
from app.core.middleware import LoggingMiddleware

setup_logging(json_logs=settings.json_logs)

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")

app.add_middleware(LoggingMiddleware)

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})