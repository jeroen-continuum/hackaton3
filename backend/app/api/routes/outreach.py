"""Outreach endpoints — generate LLM content, fetch contacts (in-memory, no persist), mark contacted."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.composition import build_container
from app.db.session import get_session
from app.models import Company as _C, OutreachAsset as _OA

router = APIRouter(prefix="/companies", tags=["outreach"])


@router.get("/{company_id}/outreach")
def get_outreach(company_id: int, session: Session = Depends(get_session)):
    asset = session.exec(select(_OA).where(_OA.company_id == company_id)).first()
    if not asset:
        raise HTTPException(404, "No outreach asset generated for this company")
    return {
        "email_subject": asset.email_subject,
        "email_body": asset.email_body,
        "teaser_title": asset.teaser_title,
        "teaser_preview": asset.teaser_preview,
    }


@router.post("/{company_id}/outreach/generate")
def generate_outreach(company_id: int, session: Session = Depends(get_session)):
    company = session.get(_C, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    container = build_container(session)
    sector = company.sector or "general"
    cases = container.solution_cases.by_sector(sector)
    from app.domain.models import CompanyProfile
    profile = CompanyProfile(
        enterprise_number=company.enterprise_number,
        name=company.name,
        region=company.region,
        nace_code=company.nace_code,
        sector=company.sector,
        website=company.website,
    )
    email_result = container.outreach.email(profile, cases)
    teaser_result = container.outreach.teaser(profile, cases)
    # Persist to OutreachAsset
    existing = session.exec(select(_OA).where(_OA.company_id == company_id)).first()
    if existing:
        existing.email_subject = email_result["subject"]
        existing.email_body = email_result["body"]
        existing.teaser_title = teaser_result["title"]
        existing.teaser_preview = teaser_result["preview"]
        existing.teaser_full = teaser_result["full"]
        session.add(existing)
    else:
        asset = _OA(
            company_id=company_id,
            email_subject=email_result["subject"],
            email_body=email_result["body"],
            teaser_title=teaser_result["title"],
            teaser_preview=teaser_result["preview"],
            teaser_full=teaser_result["full"],
        )
        session.add(asset)
    session.commit()
    return {"status": "generated", "company_id": company_id}


@router.get("/{company_id}/contacts")
def get_contacts(company_id: int, session: Session = Depends(get_session)):
    """Fetch buyer personas in-memory. PII: never persisted."""
    company = session.get(_C, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    container = build_container(session)
    personas = container.contacts.find_buyer_personas(company.enterprise_number)
    return {"contacts": personas, "persisted": False}


@router.post("/{company_id}/mark-contacted")
def mark_contacted(company_id: int, session: Session = Depends(get_session)):
    company = session.get(_C, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    container = build_container(session)
    container.rolling10.mark_contacted(company.enterprise_number)
    return {"status": "marked", "company_id": company_id}
