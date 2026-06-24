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

    def override():
        with Session(engine) as s:
            yield s

    fastapi_app.dependency_overrides[get_session] = override
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


def test_get_outreach_404_when_no_asset(client):
    response = client.get("/companies/999/outreach")
    assert response.status_code == 404


def test_get_contacts_404_for_unknown_company(client):
    response = client.get("/companies/999/contacts")
    assert response.status_code == 404


def test_mark_contacted_404_for_unknown_company(client):
    response = client.post("/companies/999/mark-contacted")
    assert response.status_code == 404
