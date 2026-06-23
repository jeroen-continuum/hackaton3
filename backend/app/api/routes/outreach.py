"""Outreach read endpoint: precomputed email + gated teaser for a company."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import OutreachAsset

router = APIRouter(prefix="/companies", tags=["outreach"])


@router.get("/{company_id}/outreach")
def get_outreach(company_id: int, session: Session = Depends(get_session)):
    asset = session.exec(
        select(OutreachAsset).where(OutreachAsset.company_id == company_id)
    ).first()
    if not asset:
        raise HTTPException(404, "No outreach asset generated for this company")
    return asset
