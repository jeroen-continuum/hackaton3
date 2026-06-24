"""End-to-end pipeline test: pond → filter → enrich → score → rank → top10."""
import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from app.application.pipeline import RunPipeline
from app.adapters.persistence.company_repo import SqlModelCompanyRepository
from app.domain.models import CompanyProfile


def make_engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def make_companies(n: int) -> list[CompanyProfile]:
    return [
        CompanyProfile(
            enterprise_number=f"04111230{i:02d}",
            name=f"Company {i}",
            region="BE",
            nace_code="6419",
            sector="financial_services",
            website=f"company{i}.be",
        )
        for i in range(1, n + 1)
    ]


@pytest.fixture
def session():
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


# Import fakes from conftest by re-defining inline (conftest fakes not importable directly)
class _FakeSource:
    def __init__(self, companies):
        self._companies = companies

    def load_pond(self):
        return self._companies


class _FakeFinancials:
    def fetch(self, enterprise_number):
        return None


class _FakeVacancies:
    def fetch(self, enterprise_number):
        return []


class _FakeTech:
    def fetch(self, domain):
        return None


class _FakeConnections:
    def shared(self, enterprise_number):
        return []


class _FakeFilter:
    def evaluate(self, profile, financials):
        from app.domain.models import Decision
        return Decision(passes=True, reason=None)


class _FakeScorer:
    def score(self, signals):
        from app.domain.models import ScoreResult
        return ScoreResult(
            total=0.5,
            breakdown={
                "buyer_intent": signals.buyer_intent,
                "impact_potential": signals.impact_potential,
                "financial_fit": signals.financial_fit,
                "sector_fit": signals.sector_fit,
                "warm_connection": signals.warm_connection,
            },
        )


def make_pipeline(session, companies):
    repo = SqlModelCompanyRepository(session)
    source = _FakeSource(companies)
    return RunPipeline(
        source=source,
        financials=_FakeFinancials(),
        filter_policy=_FakeFilter(),
        vacancies=_FakeVacancies(),
        tech=_FakeTech(),
        connections=_FakeConnections(),
        scorer=_FakeScorer(),
        repo=repo,
    ), repo


def test_pipeline_returns_top10(session):
    companies = make_companies(12)
    pipeline, repo = make_pipeline(session, companies)
    top10 = pipeline.run()
    assert len(top10) == 10


def test_pipeline_all_scores_persisted(session):
    companies = make_companies(12)
    pipeline, repo = make_pipeline(session, companies)
    pipeline.run()
    top10 = repo.get_top10_with_scores()
    assert len(top10) == 10
    for item in top10:
        assert item["score"] is not None
        assert item["breakdown"] is not None
        assert len(item["breakdown"]) == 5


def test_pipeline_ranks_assigned(session):
    companies = make_companies(5)
    pipeline, repo = make_pipeline(session, companies)
    pipeline.run()
    top10 = repo.get_top10_with_scores()
    ranks = [item["rank"] for item in top10]
    assert sorted(ranks) == list(range(1, len(top10) + 1))


def test_pipeline_empty_pond(session):
    pipeline, repo = make_pipeline(session, [])
    top10 = pipeline.run()
    assert top10 == []


def test_pipeline_fewer_than_10(session):
    companies = make_companies(3)
    pipeline, repo = make_pipeline(session, companies)
    top10 = pipeline.run()
    assert len(top10) == 3
