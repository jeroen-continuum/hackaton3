"""Composition root — wires concrete adapters into application services.

This is the ONLY file allowed to import from app.adapters.*
All other application code depends on ports (domain/ports.py) only.
"""
from dataclasses import dataclass

from app.application.pipeline import RunPipeline
from app.application.scoring import Scorer
from app.application.outreach import GenerateOutreach
from app.application.rolling10 import Rolling10
from app.application.solution_cases import SolutionCaseRepository
from app.adapters.scoring.weighted import WeightedScoringStrategy
from app.adapters.filtering.icp_policy import IcpFilterPolicy
from app.adapters.persistence.company_repo import SqlModelCompanyRepository
from app.adapters.sources.db_source import DbCompanySource as _DbCompanySource
from app.adapters.sources.nbb import NbbFinancialsProvider as _NbbProvider
from app.adapters.sources.vdab import VdabVacancyProvider as _VdabProvider
from app.adapters.sources.wappalyzer import WappalyzerTechProvider as _WappalyzerProvider
from app.adapters.sources.connections import (
    CsvConnectionProvider as _CsvConnectionProvider,
    NullConnectionProvider as _NullConnectionProvider,
)
from app.adapters.sources.db_financials import DbFinancialsProvider as _DbFinancials
from app.adapters.sources.fake_financials import FakeFinancialsProvider as _FakeFinancials
from app.adapters.sources.db_vacancies import DbVacancyProvider as _DbVacancies
from app.adapters.sources.db_tech import DbTechProvider as _DbTech
from app.adapters.outreach.llm_outreach import LlmOutreachGenerator as _LlmOutreachGenerator
from app.adapters.sources.apollo import ApolloContactProvider
from app.core.config import settings
from app.domain.filters import IcpFilter

from sqlmodel import Session


@dataclass
class Container:
    pipeline: RunPipeline
    scorer: Scorer
    outreach: GenerateOutreach
    rolling10: Rolling10
    solution_cases: SolutionCaseRepository
    contacts: ApolloContactProvider


def build_container(session: Session, icp: IcpFilter | None = None) -> Container:
    """Wire all concrete adapters and return the application service container.

    `icp` is the adjustable customer profile (defaults to the requirement values);
    it drives both the candidate selection (DbCompanySource) and the ICP filter.
    """
    icp = icp or IcpFilter.default()
    repo = SqlModelCompanyRepository(session)
    scoring_strategy = WeightedScoringStrategy()
    filter_policy = IcpFilterPolicy(icp)

    # Per-enrichment flags: external API when ON, DB-backed (no HTTP) when OFF.
    if settings.enable_nbb_financials:
        financials = _NbbProvider()
    elif settings.use_fake_financials:
        financials = _FakeFinancials()
    else:
        financials = _DbFinancials(session)
    vacancies = _VdabProvider() if settings.enable_vdab_vacancies else _DbVacancies(session)
    tech = _WappalyzerProvider() if settings.enable_wappalyzer_tech else _DbTech(session)
    connections = (
        _CsvConnectionProvider() if settings.enable_csv_connections
        else _NullConnectionProvider()
    )

    pipeline = RunPipeline(
        source=_DbCompanySource(session, icp, settings.max_pond_enrich),
        financials=financials,
        filter_policy=filter_policy,
        vacancies=vacancies,
        tech=tech,
        connections=connections,
        scorer=scoring_strategy,
        repo=repo,
    )
    scorer = Scorer(scoring_strategy)
    outreach_gen = _LlmOutreachGenerator()
    outreach = GenerateOutreach(outreach_gen, repo)

    rolling10 = Rolling10(repo=repo)
    solution_cases = SolutionCaseRepository(session=session)
    contacts = ApolloContactProvider(enabled=settings.enable_apollo_contacts)
    return Container(
        pipeline=pipeline,
        scorer=scorer,
        outreach=outreach,
        rolling10=rolling10,
        solution_cases=solution_cases,
        contacts=contacts,
    )
