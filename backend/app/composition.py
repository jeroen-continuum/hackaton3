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
from app.adapters.sources.kbo import KboSource as _KboSource
from app.adapters.sources.nbb import NbbFinancialsProvider as _NbbProvider
from app.adapters.sources.vdab import VdabVacancyProvider as _VdabProvider
from app.adapters.sources.wappalyzer import WappalyzerTechProvider as _WappalyzerProvider
from app.adapters.sources.connections import CsvConnectionProvider as _CsvConnectionProvider
from app.adapters.outreach.llm_outreach import LlmOutreachGenerator as _LlmOutreachGenerator
from app.adapters.sources.apollo import ApolloContactProvider

from sqlmodel import Session


@dataclass
class Container:
    pipeline: RunPipeline
    scorer: Scorer
    outreach: GenerateOutreach
    rolling10: Rolling10
    solution_cases: SolutionCaseRepository
    contacts: ApolloContactProvider


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

    rolling10 = Rolling10(repo=repo)
    solution_cases = SolutionCaseRepository(session=session)
    contacts = ApolloContactProvider()
    return Container(
        pipeline=pipeline,
        scorer=scorer,
        outreach=outreach,
        rolling10=rolling10,
        solution_cases=solution_cases,
        contacts=contacts,
    )
