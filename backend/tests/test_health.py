import backend.app.api.v1.health as health
from backend.app.main import app
from fastapi.testclient import TestClient
from redis.exceptions import RedisError
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

client = TestClient(app)


def test_liveness_returns_ok_and_request_id() -> None:
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-request-id"]


def test_openapi_documents_versioned_health_routes() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/health/live" in response.json()["paths"]
    assert "/api/v1/health/ready" in response.json()["paths"]


def test_readiness_checks_database_connectivity(monkeypatch) -> None:
    class AvailableRedis:
        def ping(self) -> bool:
            return True

    monkeypatch.setattr(health, "engine", create_engine("sqlite://"))
    monkeypatch.setattr(health, "redis_client", AvailableRedis())

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "redis": "ok"}


def test_readiness_returns_service_unavailable_when_database_fails(monkeypatch) -> None:
    class UnavailableEngine:
        def connect(self):
            raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(health, "engine", UnavailableEngine())
    monkeypatch.setattr(health, "redis_client", object())

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["error"]["message"] == "A required service is unavailable"


def test_readiness_returns_service_unavailable_when_redis_fails(monkeypatch) -> None:
    class UnavailableRedis:
        def ping(self) -> None:
            raise RedisError("redis unavailable")

    monkeypatch.setattr(health, "engine", create_engine("sqlite://"))
    monkeypatch.setattr(health, "redis_client", UnavailableRedis())

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["error"]["message"] == "A required service is unavailable"
