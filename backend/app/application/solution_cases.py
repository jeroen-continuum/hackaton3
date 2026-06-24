"""Repository for accessing solution case reference data."""
from sqlmodel import Session, select
from app.models.entities import SolutionCase


class SolutionCaseRepository:
    """Fetches WiiPlus solution cases by sector for outreach LLM grounding."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def by_sector(self, sector: str) -> list[dict]:
        """Get solution cases for a given sector, returned as dicts."""
        cases = self._session.exec(
            select(SolutionCase).where(SolutionCase.sector == sector)
        ).all()
        return [
            {
                "title": c.title,
                "summary": c.summary,
                "impact_metric": c.impact_metric,
            }
            for c in cases
        ]
