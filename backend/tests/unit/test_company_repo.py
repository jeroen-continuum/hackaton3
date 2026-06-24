"""Tests for SqlModelCompanyRepository using in-memory SQLite."""
import pytest
from sqlmodel import Session, create_engine, SQLModel

from app.domain.models import CompanyProfile, ScoreResult
from app.domain.ports import CompanyRepository
from app.adapters.persistence.company_repo import SqlModelCompanyRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    # Import entities so tables are registered
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def repo(session):
    return SqlModelCompanyRepository(session)


@pytest.fixture
def profile():
    return CompanyProfile(enterprise_number="0123456789", name="Acme NV", nace_code="6419", region="BE")


def test_repo_satisfies_protocol(repo):
    assert isinstance(repo, CompanyRepository)


def test_save_and_retrieve_company(repo, session, profile):
    repo.save_company(profile)
    from app.models.entities import Company
    from sqlmodel import select
    row = session.exec(select(Company).where(Company.enterprise_number == "0123456789")).first()
    assert row is not None
    assert row.name == "Acme NV"


def test_save_company_upserts(repo, session, profile):
    repo.save_company(profile)
    updated = CompanyProfile(enterprise_number="0123456789", name="Acme BV", nace_code="6419", region="NL")
    repo.save_company(updated)
    from app.models.entities import Company
    from sqlmodel import select, func
    count = session.exec(select(func.count()).select_from(Company).where(Company.enterprise_number == "0123456789")).one()
    assert count == 1


def test_save_score_persists(repo, session, profile):
    repo.save_company(profile)
    from app.models.entities import Company
    from sqlmodel import select
    company = session.exec(select(Company).where(Company.enterprise_number == profile.enterprise_number)).first()
    score = ScoreResult(total=0.75, breakdown={"buyer_intent": 0.9, "_company_id": company.id})
    repo.save_score(score)
    from app.models.entities import Score
    db_score = session.exec(select(Score).where(Score.company_id == company.id)).first()
    assert db_score is not None
    assert db_score.total == pytest.approx(0.75)
    assert "_company_id" not in db_score.breakdown


def test_save_score_without_company_id_raises(repo):
    score = ScoreResult(total=0.5, breakdown={"buyer_intent": 0.5})
    with pytest.raises(ValueError, match="_company_id"):
        repo.save_score(score)


def test_get_top10_returns_list(repo):
    result = repo.get_top10()
    assert isinstance(result, list)
