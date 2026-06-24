"""Integration tests for /companies endpoints using TestClient + in-memory SQLite."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine, SQLModel

from app.main import app as fastapi_app
from app.db.session import get_session
import app.models  # noqa: F401 — registers SQLModel table metadata


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = override_session
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


def test_top10_returns_list(client):
    response = client.get("/companies/top10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_company_detail_404_for_unknown(client):
    response = client.get("/companies/9999")
    assert response.status_code == 404


def test_top10_empty_when_no_data(client):
    response = client.get("/companies/top10")
    assert response.json() == []
