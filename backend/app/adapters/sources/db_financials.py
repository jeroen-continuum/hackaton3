"""DB-backed financials adapter — reads stored FinancialData, no external API.

Used when settings.enable_nbb_financials is OFF: returns whatever an offline
enrichment run persisted, so the request path does no outbound HTTP.
"""
from sqlmodel import Session, select

from app.domain.models import Financials
from app.models.entities import Company as _Company, FinancialData as _FinData


class DbFinancialsProvider:
    """Reads financials from the DB by enterprise_number; None if absent."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch(self, enterprise_number: str) -> Financials | None:
        row = self._session.exec(
            select(_FinData)
            .join(_Company, _FinData.company_id == _Company.id)
            .where(_Company.enterprise_number == enterprise_number)
        ).first()
        if row is None:
            return None
        return Financials(
            employees=row.employees,
            revenue=row.revenue,
            ebitda=row.ebitda,
            fiscal_year=row.fiscal_year,
        )
