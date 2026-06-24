"""SQLModel implementation of CompanyRepository port.

Translates between domain value objects (CompanyProfile, ScoreResult) and
the persistence entities (Company, Score) in models/entities.py.
"""
from sqlmodel import Session, select

from app.domain.models import CompanyProfile, ScoreResult
from app.domain.ports import CompanyRepository
from app.models.entities import Company as _Company, Score as _Score


class SqlModelCompanyRepository:
    """CompanyRepository backed by SQLModel + SQLite/Postgres."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save_company(self, profile: CompanyProfile) -> None:
        """Upsert a company (insert or update by enterprise_number)."""
        existing = self._session.exec(
            select(_Company).where(_Company.enterprise_number == profile.enterprise_number)
        ).first()
        if existing:
            existing.name = profile.name
            existing.region = profile.region
            existing.nace_code = profile.nace_code
            existing.sector = profile.sector
            existing.website = profile.website
            self._session.add(existing)
        else:
            company = _Company(
                enterprise_number=profile.enterprise_number,
                name=profile.name,
                region=profile.region,
                nace_code=profile.nace_code,
                sector=profile.sector,
                website=profile.website,
            )
            self._session.add(company)
        self._session.commit()

    def save_score(self, score: ScoreResult) -> None:
        """Persist a score result — requires company_id in score.breakdown['_company_id']."""
        company_id = score.breakdown.get("_company_id")
        if company_id is None:
            raise ValueError("ScoreResult.breakdown must contain '_company_id' key")
        # Build a clean breakdown without the internal key
        breakdown = {k: v for k, v in score.breakdown.items() if k != "_company_id"}
        existing = self._session.exec(
            select(_Score).where(_Score.company_id == company_id)
        ).first()
        if existing:
            existing.total = score.total
            existing.breakdown = breakdown
            self._session.add(existing)
        else:
            db_score = _Score(
                company_id=company_id,
                total=score.total,
                breakdown=breakdown,
            )
            self._session.add(db_score)
        self._session.commit()

    def get_top10(self) -> list[CompanyProfile]:
        """Return top 10 non-contacted companies ordered by score rank."""
        rows = self._session.exec(
            select(_Company, _Score)
            .join(_Score)
            .where(_Score.contacted == False)  # noqa: E712
            .order_by(_Score.rank)
            .limit(10)
        ).all()
        return [
            CompanyProfile(
                enterprise_number=c.enterprise_number,
                name=c.name,
                region=c.region,
                nace_code=c.nace_code,
                sector=c.sector,
                website=c.website,
            )
            for c, _ in rows
        ]
