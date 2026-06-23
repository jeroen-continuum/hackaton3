"""Company read endpoints: the Rolling 10 list + per-company detail."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Company, Score

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/top10")
def top10(session: Session = Depends(get_session)):
    """Rolling 10: top non-contacted companies by score, rank order."""
    stmt = (
        select(Company, Score)
        .join(Score)
        .where(Score.contacted == False)  # noqa: E712
        .order_by(Score.rank)
        .limit(10)
    )
    rows = session.exec(stmt).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "sector": c.sector,
            "region": c.region,
            "rank": sc.rank,
            "score": sc.total,
            "breakdown": sc.breakdown,
        }
        for c, sc in rows
    ]


@router.get("/{company_id}")
def detail(company_id: int, session: Session = Depends(get_session)):
    """Full company detail incl. score breakdown (heatmap) and enrichment."""
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    return {
        "id": company.id,
        "name": company.name,
        "enterprise_number": company.enterprise_number,
        "sector": company.sector,
        "nace_code": company.nace_code,
        "region": company.region,
        "website": company.website,
        "financials": company.financials,
        "contacts": company.contacts,
        "vacancies": company.vacancies,
        "tech": company.tech,
        "score": company.score,
    }
