"""Unit tests for SolutionCaseRepository."""
import pytest
from sqlmodel import Session, create_engine, SQLModel

from app.application.solution_cases import SolutionCaseRepository
from app.db.seed import seed_solution_cases, SOLUTION_CASES


@pytest.fixture
def session():
    """In-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_seed_inserts_cases(session):
    """Seed should insert all solution cases into the session."""
    seed_solution_cases(session)
    repo = SolutionCaseRepository(session)
    cases = repo.by_sector("financial_services")
    assert len(cases) >= 2


def test_seed_is_idempotent(session):
    """Running seed twice should not duplicate cases."""
    seed_solution_cases(session)
    seed_solution_cases(session)  # second run should not duplicate
    repo = SolutionCaseRepository(session)
    cases = repo.by_sector("financial_services")
    assert len(cases) == 2  # exactly 2, not 4


def test_by_sector_returns_dicts_with_required_keys(session):
    """by_sector should return dicts with title, summary, impact_metric."""
    seed_solution_cases(session)
    repo = SolutionCaseRepository(session)
    cases = repo.by_sector("logistics")
    assert len(cases) == 1
    assert "title" in cases[0]
    assert "summary" in cases[0]
    assert "impact_metric" in cases[0]


def test_by_sector_returns_empty_for_unknown_sector(session):
    """by_sector should return empty list for sectors with no cases."""
    seed_solution_cases(session)
    repo = SolutionCaseRepository(session)
    assert repo.by_sector("unknown_sector") == []
