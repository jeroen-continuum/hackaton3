"""Pytest configuration and fake adapters for domain ports."""

import pytest
from app.domain.models import CompanyProfile, Financials, Signals, ScoreResult, Decision


# Port: CompanySource
class FakeCompanySource:
    def __init__(self):
        self._companies = []

    def load_pond(self) -> list[CompanyProfile]:
        """Returns list of CompanyProfile-like dicts or objects."""
        return self._companies


# Port: FinancialsProvider
class FakeFinancialsProvider:
    def fetch(self, enterprise_number: str) -> Financials | None:
        return None


# Port: VacancyProvider
class FakeVacancyProvider:
    def fetch(self, enterprise_number: str) -> list:
        return []


# Port: TechProvider
class FakeTechProvider:
    def fetch(self, domain: str) -> dict | None:
        return None


# Port: ConnectionProvider
class FakeConnectionProvider:
    def shared(self, enterprise_number: str) -> list:
        return []


# Port: ContactProvider
class FakeContactProvider:
    def find_buyer_personas(self, enterprise_number: str) -> list:
        return []


# Port: ScoringStrategy
class FakeScoringStrategy:
    def score(self, signals: Signals) -> ScoreResult:
        breakdown = {
            "buyer_intent": signals.buyer_intent,
            "impact_potential": signals.impact_potential,
            "financial_fit": signals.financial_fit,
            "sector_fit": signals.sector_fit,
            "warm_connection": signals.warm_connection,
        }
        return ScoreResult(total=0.5, breakdown=breakdown)


# Port: FilterPolicy
class FakeFilterPolicy:
    def evaluate(self, profile: CompanyProfile, financials: Financials | None) -> Decision:
        return Decision(passes=True, reason=None)


# Port: OutreachGenerator
class FakeOutreachGenerator:
    def email(self, company: CompanyProfile, cases: list[dict]) -> dict:
        return {"subject": "Test", "body": "Test body"}

    def teaser(self, company: CompanyProfile, cases: list[dict]) -> dict:
        return {"title": "Test", "preview": "Preview", "full": "Full content"}


# Port: CompanyRepository (minimal for now)
class FakeCompanyRepository:
    def __init__(self):
        self._companies = []
        self._scores = []
        self._id_counter = 1

    def save_company(self, company: CompanyProfile) -> int | None:
        self._companies.append(company)
        fake_id = self._id_counter
        self._id_counter += 1
        return fake_id

    def clear_scores(self) -> None:
        self._scores = []

    def save_score(self, score: ScoreResult) -> None:
        self._scores.append(score)

    def get_top10(self) -> list[CompanyProfile]:
        return self._companies[:10]

    def get_top10_with_scores(self) -> list[dict]:
        return []

    def get_by_enterprise_number(self, enterprise_number: str) -> CompanyProfile | None:
        return next((c for c in self._companies if c.enterprise_number == enterprise_number), None)

    def assign_ranks(self) -> None:
        pass

    def mark_contacted(self, enterprise_number: str) -> None:
        pass


# Pytest fixtures

@pytest.fixture
def fake_company_source():
    return FakeCompanySource()


@pytest.fixture
def fake_financials_provider():
    return FakeFinancialsProvider()


@pytest.fixture
def fake_vacancy_provider():
    return FakeVacancyProvider()


@pytest.fixture
def fake_tech_provider():
    return FakeTechProvider()


@pytest.fixture
def fake_connection_provider():
    return FakeConnectionProvider()


@pytest.fixture
def fake_contact_provider():
    return FakeContactProvider()


@pytest.fixture
def fake_scoring_strategy():
    return FakeScoringStrategy()


@pytest.fixture
def fake_filter_policy():
    return FakeFilterPolicy()


@pytest.fixture
def fake_outreach_generator():
    return FakeOutreachGenerator()


@pytest.fixture
def fake_company_repository():
    return FakeCompanyRepository()
