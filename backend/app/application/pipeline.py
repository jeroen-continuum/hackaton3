"""RunPipeline application service — orchestrates ingest→filter→enrich→score.

Deliberately thin: all I/O is delegated to injected port adapters.
The pipeline only applies business logic (signal extraction, ranking).
"""
from app.application.signals import build_signals
from app.domain.models import CompanyProfile, Financials, Signals, ScoreResult
from app.domain.ports import (
    CompanySource, FinancialsProvider, FilterPolicy,
    VacancyProvider, TechProvider, ConnectionProvider,
    ScoringStrategy, CompanyRepository,
)


class RunPipeline:
    def __init__(
        self,
        source: CompanySource,
        financials: FinancialsProvider,
        filter_policy: FilterPolicy,
        vacancies: VacancyProvider,
        tech: TechProvider,
        connections: ConnectionProvider,
        scorer: ScoringStrategy,
        repo: CompanyRepository,
    ) -> None:
        self._source = source
        self._financials = financials
        self._filter = filter_policy
        self._vacancies = vacancies
        self._tech = tech
        self._connections = connections
        self._scorer = scorer
        self._repo = repo

    def run(self) -> list[CompanyProfile]:
        """Run full pipeline. Returns scored + ranked top-10."""
        pond = self._source.load_pond()
        passing = []
        for profile in pond:
            fin = self._financials.fetch(profile.enterprise_number)
            decision = self._filter.evaluate(profile, fin)
            if decision.passes:
                passing.append((profile, fin))

        for profile, fin in passing:
            vacancies = self._vacancies.fetch(profile.enterprise_number)
            tech = self._tech.fetch(profile.website or "")
            connections = self._connections.shared(profile.enterprise_number)
            signals = self._extract_signals(profile, fin, vacancies, tech, connections)
            result = self._scorer.score(signals)
            company_id = self._repo.save_company(profile)
            enriched_breakdown = dict(result.breakdown)
            enriched_breakdown["_company_id"] = company_id
            self._repo.save_score(ScoreResult(total=result.total, breakdown=enriched_breakdown))

        self._repo.assign_ranks()
        return self._repo.get_top10()

    def _extract_signals(
        self,
        profile: CompanyProfile,
        fin: Financials | None,
        vacancies: list[dict],
        tech: dict | None,
        connections: list[dict],
    ) -> Signals:
        """Derive normalised [0,1] signals from enrichment data."""
        return build_signals(profile, fin, vacancies, tech, connections)

