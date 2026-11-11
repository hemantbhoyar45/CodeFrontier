from collections.abc import Generator

import backend.app.db.models  # noqa: F401
import backend.app.main as main_module
import pytest
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def api_client(monkeypatch) -> Generator[TestClient, None, None]:
    class TestRateLimitClient:
        def eval(self, script, key_count, key, expiry):
            return (1, expiry)

    monkeypatch.setattr(main_module, "rate_limit_client", TestRateLimitClient())
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        with test_sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()
