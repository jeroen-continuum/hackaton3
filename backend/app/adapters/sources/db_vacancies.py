"""DB-backed vacancy adapter — reads stored Vacancy rows, no external API.

Used when settings.enable_vdab_vacancies is OFF.
"""
from sqlmodel import Session, select

from app.models.entities import Company as _Company, Vacancy as _Vacancy


class DbVacancyProvider:
    """Reads vacancies from the DB by enterprise_number; [] if none."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch(self, enterprise_number: str) -> list[dict]:
        rows = self._session.exec(
            select(_Vacancy)
            .join(_Company, _Vacancy.company_id == _Company.id)
            .where(_Company.enterprise_number == enterprise_number)
        ).all()
        return [
            {"title": v.title, "url": v.url, "is_it_role": v.is_it_role}
            for v in rows
        ]
