"""Hexagonal architecture port definitions.

These Protocols define the boundary of the domain.
All I/O lives in adapters; all use-cases depend only on these interfaces.
"""
from typing import Protocol, runtime_checkable
from app.domain.models import CompanyProfile, Financials, Signals, ScoreResult, Decision


@runtime_checkable
class CompanySource(Protocol):
    """Loads the initial pond of candidate companies (e.g. from KBO dump)."""
    def load_pond(self) -> list[CompanyProfile]: ...


@runtime_checkable
class FinancialsProvider(Protocol):
    """Fetches financial data for one company by enterprise number."""
    def fetch(self, enterprise_number: str) -> Financials | None: ...


@runtime_checkable
class VacancyProvider(Protocol):
    """Fetches open job vacancies for one company."""
    def fetch(self, enterprise_number: str) -> list[dict]: ...


@runtime_checkable
class TechProvider(Protocol):
    """Detects technology stack from a domain name."""
    def fetch(self, domain: str) -> dict | None: ...


@runtime_checkable
class ConnectionProvider(Protocol):
    """Returns warm connections between the sales team and a company."""
    def shared(self, enterprise_number: str) -> list[dict]: ...


@runtime_checkable
class ContactProvider(Protocol):
    """Finds buyer personas for a company (in-memory only, never persisted)."""
    def find_buyer_personas(self, enterprise_number: str) -> list[dict]: ...


@runtime_checkable
class ScoringStrategy(Protocol):
    """Scores a company given normalised signals. Pluggable algorithm."""
    def score(self, signals: Signals) -> ScoreResult: ...


@runtime_checkable
class FilterPolicy(Protocol):
    """Evaluates whether a company passes ICP criteria."""
    def evaluate(self, profile: CompanyProfile, financials: Financials | None) -> Decision: ...


@runtime_checkable
class OutreachGenerator(Protocol):
    """Generates personalised outreach assets using an LLM."""
    def email(self, company: CompanyProfile, cases: list[dict]) -> dict: ...
    def teaser(self, company: CompanyProfile, cases: list[dict]) -> dict: ...


@runtime_checkable
class CompanyRepository(Protocol):
    """Persists and retrieves pipeline state."""
    def save_company(self, company: CompanyProfile) -> int | None: ...
    def save_score(self, score: ScoreResult) -> None: ...
    def get_top10(self) -> list[CompanyProfile]: ...
    def get_top10_with_scores(self) -> list[dict]: ...
    def get_by_enterprise_number(self, enterprise_number: str) -> CompanyProfile | None: ...
    def assign_ranks(self) -> None: ...
    def mark_contacted(self, enterprise_number: str) -> None: ...
