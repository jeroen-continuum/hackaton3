"""Company endpoints — delegates to Rolling10 application service."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.composition import build_container
from app.db.session import get_session
from app.models import Company as _C, Score as _S

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/top10")
def top10(session: Session = Depends(get_session)):
    container = build_container(session)
    return container.rolling10.get_top10_with_scores()


@router.get("/{company_id}")
def detail(company_id: int, session: Session = Depends(get_session)):
    company = session.get(_C, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    score = session.exec(select(_S).where(_S.company_id == company_id)).first()
    return {
        "id": company.id,
        "name": company.name,
        "enterprise_number": company.enterprise_number,
        "sector": company.sector,
        "nace_code": company.nace_code,
        "region": company.region,
        "website": company.website,
        "rank": score.rank if score else None,
        "score": score.total if score else None,
        "breakdown": score.breakdown if score else {},
    }
