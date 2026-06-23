"""Scoring actions: mark a company contacted so the next rolls into the top 10."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Score

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/{company_id}/contacted")
def mark_contacted(company_id: int, session: Session = Depends(get_session)):
    score = session.exec(
        select(Score).where(Score.company_id == company_id)
    ).first()
    if not score:
        raise HTTPException(404, "No score for company")
    score.contacted = True
    session.add(score)
    session.commit()
    return {"company_id": company_id, "contacted": True}
