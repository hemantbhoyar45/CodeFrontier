from fastapi import APIRouter, HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.db.session import engine
from backend.app.redis_client import redis_client

router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Check whether the API process is running")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", summary="Check whether the API can reach required services")
def readiness() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        redis_client.ping()
    except (SQLAlchemyError, RedisError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A required service is unavailable",
        ) from exc
    return {"status": "ok", "database": "ok", "redis": "ok"}
