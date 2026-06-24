"""Pytest configuration and fake adapters for domain ports."""

import pytest


# Port: CompanySource
class FakeCompanySource:
    def load_pond(self) -> list:
        """Returns list of CompanyProfile-like dicts or objects."""
        return []


# Port: FinancialsProvider
class FakeFinancialsProvider:
    def fetch(self, enterprise_number: str) -> dict | None:
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
    def score(self, signals: dict) -> dict:
        return {"total": 0.5, "breakdown": signals}


# Port: FilterPolicy
class FakeFilterPolicy:
    def evaluate(self, profile: dict, financials: dict | None) -> dict:
        return {"passes": True, "reason": None}


# Port: OutreachGenerator
class FakeOutreachGenerator:
    def email(self, company: dict, cases: list) -> dict:
        return {"subject": "Test", "body": "Test body"}

    def teaser(self, company: dict, cases: list) -> dict:
        return {"title": "Test", "preview": "Preview", "full": "Full content"}


# Port: CompanyRepository (minimal for now)
class FakeCompanyRepository:
    def __init__(self):
        self._companies = []
        self._scores = []

    def save_company(self, company) -> None:
        self._companies.append(company)

    def save_score(self, score) -> None:
        self._scores.append(score)

    def get_top10(self) -> list:
        return self._companies[:10]


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
