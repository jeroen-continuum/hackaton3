"""Pure signal extraction functions — map enriched data to Signals values in [0, 1].

All functions are side-effect-free and fully unit-testable.
"""
from datetime import date

from app.core.constants import (
    FOCUS_NACE_PREFIXES,
    CONNECTION_TYPE_WEIGHT,
    CONNECTION_RECENCY_FLOOR,
    CONNECTION_RECENCY_SPAN_YEARS,
    CONNECTION_SATURATION,
)
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


def _as_date(value) -> date | None:
    """Accept a date, an ISO string, or None; ignore anything unparseable."""
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def connection_weight(conn: dict, today: date | None = None) -> float:
    """Strength of a single tie = type weight * recency factor.

    EMPLOYER > CLIENT > PERSONAL; a tie decays linearly with age down to a floor.
    An ongoing tie (no end_date) is treated as current.
    """
    today = today or date.today()
    base = CONNECTION_TYPE_WEIGHT.get(conn.get("type", "EMPLOYER"), 0.4)
    ref = _as_date(conn.get("end_date")) or today
    years = max(0.0, (today - ref).days / 365)
    recency = max(CONNECTION_RECENCY_FLOOR, 1 - years / CONNECTION_RECENCY_SPAN_YEARS)
    return base * recency


def extract_warm_connection(connections: list[dict]) -> float:
    """Type+recency weighted sum of ties, saturating at 1.0."""
    today = date.today()
    return min(1.0, sum(connection_weight(c, today) for c in connections) / CONNECTION_SATURATION)


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
