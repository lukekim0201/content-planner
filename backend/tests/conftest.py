"""Test fixtures.

Runs against an in-memory SQLite database via SQLAlchemy's StaticPool, so
the whole suite is self-contained — no Postgres server required. Point
DATABASE_URL at real Postgres if you want to test against it directly.
"""
import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_session
from app import models  # noqa: F401 register tables

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _isolate_local_uploads(tmp_path, monkeypatch):
    """Route local-disk asset uploads to a throwaway temp dir instead of the
    real backend/uploads/ folder, so running the suite never leaves files
    behind in the repo."""
    from app import storage

    monkeypatch.setattr(storage, "LOCAL_UPLOAD_DIR", str(tmp_path))


def auth_headers(client, email, password="testpass123"):
    client.post("/signup", json={"email": email, "password": password})
    login_response = client.post("/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
