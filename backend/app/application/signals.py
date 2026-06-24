"""Pure signal extraction functions — map enriched data to Signals values in [0, 1].

All functions are side-effect-free and fully unit-testable.
"""
from app.core.constants import FOCUS_NACE_PREFIXES
from app.domain.models import CompanyProfile, Financials, Signals
from app.pipeline.filter import passes_financial_fit


def extract_buyer_intent(vacancies: list[dict]) -> float:
    """Fraction of IT roles among all open vacancies; 0.0 if none."""
    if not vacancies:
        return 0.0
    it_count = sum(1 for v in vacancies if v.get("is_it_role"))
    return min(1.0, it_count / len(vacancies))


def extract_impact_potential(tech: dict | None) -> float:
    """Legacy score from tech enrichment; 0.0 if no tech data."""
    if not tech:
        return 0.0
    return float(tech.get("legacy_score", 0.0))


def extract_financial_fit(financials: Financials | None) -> float:
    """1.0 if company passes financial ICP filter, else 0.0."""
    if financials is None:
        return 0.0
    # Bridge domain Financials to SQLModel FinancialData to reuse filter predicate.
    from app.models import FinancialData
    fd = FinancialData(company_id=0, employees=financials.employees, ebitda=financials.ebitda)
    return 1.0 if passes_financial_fit(fd) else 0.0


def extract_sector_fit(profile: CompanyProfile) -> float:
    """1.0 if NACE prefix is in focus list, 0.5 if NACE present but not focus, 0.0 if absent."""
    nace = profile.nace_code or ""
    if not nace:
        return 0.0
    for prefix in FOCUS_NACE_PREFIXES:
        if nace.startswith(prefix):
            return 1.0
    return 0.5


def extract_warm_connection(connections: list[dict]) -> float:
    """min(1.0, count / 3) — 3 or more shared connections saturates the signal."""
    return min(1.0, len(connections) / 3)


def build_signals(
    profile: CompanyProfile,
    financials: Financials | None,
    vacancies: list[dict],
    tech: dict | None,
    connections: list[dict],
) -> Signals:
    """Aggregate all extractors into a single Signals value object."""
    return Signals(
        buyer_intent=extract_buyer_intent(vacancies),
        impact_potential=extract_impact_potential(tech),
        financial_fit=extract_financial_fit(financials),
        sector_fit=extract_sector_fit(profile),
        warm_connection=extract_warm_connection(connections),
    )
