"""DB-backed tech-stack adapter — reads stored TechStack, no external API.

Used when settings.enable_wappalyzer_tech is OFF. The TechProvider port keys on
the website domain, so look up the Company by website, then its TechStack.
"""
from sqlmodel import Session, select

from app.models.entities import Company as _Company, TechStack as _TechStack


class DbTechProvider:
    """Reads tech stack from the DB by website domain; None if absent."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch(self, domain: str) -> dict | None:
        if not domain:
            return None
        row = self._session.exec(
            select(_TechStack)
            .join(_Company, _TechStack.company_id == _Company.id)
            .where(_Company.website == domain)
        ).first()
        if row is None:
            return None
        return {"technologies": row.technologies, "legacy_score": row.legacy_score}
