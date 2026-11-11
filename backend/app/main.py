import hashlib
import time
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from backend.app.api.v1.router import api_router
from backend.app.config import get_settings
from backend.app.logging_config import configure_logging
from backend.app.redis_client import redis_client

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger(__name__)
rate_limit_client = redis_client
_RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return {count, redis.call('TTL', KEYS[1])}
"""

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="KNOWBRIDGE API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


def rate_limit_status(client_host: str, *, is_auth_request: bool) -> tuple[bool, int, int, int]:
    limit = (
        settings.auth_rate_limit_per_minute if is_auth_request else settings.rate_limit_per_minute
    )
    window = int(time.time() // 60)
    address_key = hashlib.sha256(client_host.encode("utf-8")).hexdigest()
    group = "auth" if is_auth_request else "api"
    key = f"knowbridge:ratelimit:{group}:{address_key}:{window}"
    count, ttl = rate_limit_client.eval(_RATE_LIMIT_SCRIPT, 1, key, 60)
    count = int(count)
    return count <= limit, limit, max(limit - count, 0), int(ttl)


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": {
                "code": f"http_{exc.status_code}",
                "message": str(exc.detail),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": [
                    {"location": error["loc"], "message": error["msg"], "type": error["type"]}
                    for error in exc.errors()
                ],
            }
        },
    )


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("request_failed", path=request.url.path, method=request.method)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "An unexpected error occurred"}},
    )


@app.middleware("http")
async def add_request_id(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    request_id = str(uuid4())
    rate_limit_headers: tuple[int, int] | None = None
    if (
        request.method != "OPTIONS"
        and request.url.path.startswith("/api/v1/")
        and request.url.path not in {"/api/v1/health/live", "/api/v1/health/ready"}
    ):
        client_host = request.client.host if request.client is not None else "unknown"
        is_auth_request = request.url.path.startswith("/api/v1/auth/")
        try:
            allowed, limit, remaining, retry_after = rate_limit_status(
                client_host, is_auth_request=is_auth_request
            )
        except RedisError:
            logger.exception("rate_limit_backend_unavailable", path=request.url.path)
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "code": "rate_limit_unavailable",
                        "message": "Request protection is temporarily unavailable",
                    }
                },
                headers={"X-Request-ID": request_id},
            )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {"code": "rate_limit_exceeded", "message": "Too many requests"}
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-Request-ID": request_id,
                },
            )
        rate_limit_headers = (limit, remaining)
    response = await call_next(request)
    if rate_limit_headers is not None:
        response.headers["X-RateLimit-Limit"] = str(rate_limit_headers[0])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_headers[1])
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response


app.include_router(api_router, prefix="/api/v1")
