"""Composition root — wires concrete adapters into application services.

This is the ONLY file allowed to import from app.adapters.*
All other application code depends on ports (domain/ports.py) only.
"""
from dataclasses import dataclass

from app.application.pipeline import RunPipeline
from app.application.scoring import Scorer
from app.application.outreach import GenerateOutreach
from app.adapters.scoring.weighted import WeightedScoringStrategy
from app.adapters.filtering.icp_policy import IcpFilterPolicy
from app.adapters.persistence.company_repo import SqlModelCompanyRepository
from app.adapters.sources.kbo import KboSource as _KboSource
from app.adapters.sources.nbb import NbbFinancialsProvider as _NbbProvider

# Source adapters are stubs until Task 09-13 implement real connectors.
# Import from existing connectors as placeholder until replaced.
from app.connectors.kbo import KboConnector
from app.connectors.nbb import NbbConnector
from app.connectors.vdab import VdabConnector
from app.connectors.wappalyzer import WappalyzerConnector
from app.connectors.apollo import ApolloConnector

from app.domain.models import CompanyProfile, Financials, ScoreResult
from app.domain.ports import (
    CompanySource, FinancialsProvider, VacancyProvider,
    TechProvider, ConnectionProvider, OutreachGenerator,
)
from sqlmodel import Session


# --- Stub adapters bridging existing connectors to domain ports ---
# These will be replaced one-by-one in Tasks 09-13.

class _VdabProvider:
    """Stub: returns empty list until Task 11 wires up VDAB API."""
    def fetch(self, enterprise_number: str) -> list[dict]:
        return []

class _WappalyzerProvider:
    """Stub: returns None until Task 12 wires up Wappalyzer API."""
    def fetch(self, domain: str) -> dict | None:
        return None

class _CsvConnectionProvider:
    """Stub: returns empty list until Task 13 wires up warm-connections CSV."""
    def shared(self, enterprise_number: str) -> list[dict]:
        return []

class _LlmOutreachGenerator:
    """Stub: returns empty dicts until Tasks 18-19 wire up LLM adapters."""
    def email(self, company: CompanyProfile, cases: list[dict]) -> dict:
        return {"subject": "", "body": ""}
    def teaser(self, company: CompanyProfile, cases: list[dict]) -> dict:
        return {"title": "", "preview": "", "full": ""}


@dataclass
class Container:
    pipeline: RunPipeline
    scorer: Scorer
    outreach: GenerateOutreach


def build_container(session: Session) -> Container:
    """Wire all concrete adapters and return the application service container."""
    repo = SqlModelCompanyRepository(session)
    scoring_strategy = WeightedScoringStrategy()
    filter_policy = IcpFilterPolicy()

    pipeline = RunPipeline(
        source=_KboSource(),
        financials=_NbbProvider(),
        filter_policy=filter_policy,
        vacancies=_VdabProvider(),
        tech=_WappalyzerProvider(),
        connections=_CsvConnectionProvider(),
        scorer=scoring_strategy,
        repo=repo,
    )
    scorer = Scorer(scoring_strategy)
    outreach_gen = _LlmOutreachGenerator()
    outreach = GenerateOutreach(outreach_gen, repo)

    return Container(pipeline=pipeline, scorer=scorer, outreach=outreach)
