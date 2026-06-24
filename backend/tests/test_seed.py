"""Smoke test: seed() runs without error against in-memory SQLite."""
import pytest
from sqlmodel import Session, create_engine, select
from sqlalchemy.pool import StaticPool

from app.db.session import init_db
from app.models.entities import Company, Score, SolutionCase
from app.db.seed import seed_solution_cases, SOLUTION_CASES, DEMO_COMPANIES


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_seed_solution_cases(session):
    seed_solution_cases(session)
    cases = session.exec(select(SolutionCase)).all()
    assert len(cases) == len(SOLUTION_CASES)


def test_seed_solution_cases_idempotent(session):
    seed_solution_cases(session)
    seed_solution_cases(session)
    cases = session.exec(select(SolutionCase)).all()
    assert len(cases) == len(SOLUTION_CASES)


def test_demo_companies_count():
    assert len(DEMO_COMPANIES) == 10


def test_demo_companies_nace_focus():
    FOCUS = ("64", "65", "66", "69", "70", "78")
    for c in DEMO_COMPANIES:
        assert c["nace_code"][:2] in FOCUS, f"{c['name']} has non-focus NACE {c['nace_code']}"


def test_demo_scores_contacted_false():
    from app.db.seed import DEMO_SCORES
    for s in DEMO_SCORES:
        assert s.get("contacted", False) is False
