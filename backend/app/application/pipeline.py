"""RunPipeline application service — orchestrates ingest→filter→enrich→score.

Deliberately thin: all I/O is delegated to injected port adapters.
The pipeline only applies business logic (signal extraction, ranking).
"""
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

        scored = []
        for profile, fin in passing:
            vacancies = self._vacancies.fetch(profile.enterprise_number)
            tech = self._tech.fetch(profile.website or "")
            connections = self._connections.shared(profile.enterprise_number)
            signals = self._extract_signals(profile, fin, vacancies, tech, connections)
            result = self._scorer.score(signals)
            self._repo.save_company(profile)
            scored.append((profile, result))

        return self._rank(scored)

    def _extract_signals(
        self,
        profile: CompanyProfile,
        fin: Financials | None,
        vacancies: list[dict],
        tech: dict | None,
        connections: list[dict],
    ) -> Signals:
        """Derive normalised [0,1] signals from enrichment data.

        Placeholder logic — Task 14 replaces this with proper signal extractors.
        """
        it_vac = sum(1 for v in vacancies if v.get("is_it_role")) if vacancies else 0
        return Signals(
            buyer_intent=min(1.0, it_vac / 3.0),
            impact_potential=(tech or {}).get("legacy_score", 0.0) if tech else 0.0,
            financial_fit=1.0 if fin and fin.ebitda and fin.ebitda > 1_500_000 else 0.0,
            sector_fit=0.5,  # placeholder; Task 14 uses NACE lookup
            warm_connection=min(1.0, len(connections) / 2.0) if connections else 0.0,
        )

    def _rank(self, scored: list[tuple[CompanyProfile, ScoreResult]]) -> list[CompanyProfile]:
        """Sort by total score descending, return top-10 profiles."""
        ordered = sorted(scored, key=lambda x: x[1].total, reverse=True)
        return [profile for profile, _ in ordered[:10]]
