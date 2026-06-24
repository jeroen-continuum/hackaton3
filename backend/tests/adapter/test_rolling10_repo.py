"""Adapter integration tests for assign_ranks and mark_contacted."""
import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.adapters.persistence.company_repo import SqlModelCompanyRepository
from app.domain.models import CompanyProfile, ScoreResult


@pytest.fixture
def repo():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield SqlModelCompanyRepository(session)


def test_assign_ranks_orders_by_total(repo):
    p1 = CompanyProfile(enterprise_number="0001", name="Low")
    p2 = CompanyProfile(enterprise_number="0002", name="High")
    id1 = repo.save_company(p1)
    id2 = repo.save_company(p2)
    repo.save_score(ScoreResult(total=0.3, breakdown={"_company_id": id1}))
    repo.save_score(ScoreResult(total=0.9, breakdown={"_company_id": id2}))
    repo.assign_ranks()
    top10 = repo.get_top10()
    assert top10[0].enterprise_number == "0002"  # highest score = rank 1


def test_mark_contacted_removes_from_top10(repo):
    p1 = CompanyProfile(enterprise_number="0001", name="Alpha")
    id1 = repo.save_company(p1)
    repo.save_score(ScoreResult(total=0.8, breakdown={"_company_id": id1}))
    repo.assign_ranks()
    repo.mark_contacted("0001")
    top10 = repo.get_top10()
    assert len(top10) == 0
