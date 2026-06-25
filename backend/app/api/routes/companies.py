"""Company endpoints — delegates to Rolling10 application service."""
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlmodel import Session, select

from app.adapters.sources.db_source import apply_financial_filters, apply_icp_filters
from app.composition import build_container
from app.core import constants
from app.db.session import get_session
from app.domain.filters import IcpFilter
from app.domain.geo import haversine_km
from app.application.company_brief import CompanyBriefService
from app.models import Company as _C, Score as _S, CompanyBrief as _CB, WebsiteCrawl as _WC

router = APIRouter(prefix="/companies", tags=["companies"])


class FilterRequest(BaseModel):
    """Adjustable ICP filters from the frontend; any omitted field keeps its default."""
    regions: list[str] = Field(default_factory=lambda: list(constants.REGIONS))
    nace_include_prefixes: list[str] = Field(
        default_factory=lambda: list(constants.FOCUS_NACE_PREFIXES)
    )
    nace_exclude_prefixes: list[str] = Field(
        default_factory=lambda: list(constants.EXCLUDED_NACE_PREFIXES)
    )
    min_employees: int = constants.MIN_EMPLOYEES
    max_employees: int = constants.MAX_EMPLOYEES
    min_ebitda: float = constants.MIN_EBITDA
    max_ebitda: Optional[float] = constants.MAX_EBITDA  # None = no upper bound
    apply_size: bool = True
    apply_financial: bool = True
    # When true, keep only companies we have a warm connection to.
    only_warm: bool = False
    # When true, drop companies that are already our clients (any CLIENT tie).
    exclude_clients: bool = False
    # Area filter — all None = no geographic restriction.
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    radius_km: Optional[float] = None

    def to_icp(self) -> IcpFilter:
        return IcpFilter(
            regions=self.regions,
            nace_include_prefixes=self.nace_include_prefixes,
            nace_exclude_prefixes=self.nace_exclude_prefixes,
            min_employees=self.min_employees,
            max_employees=self.max_employees,
            min_ebitda=self.min_ebitda,
            max_ebitda=self.max_ebitda,
            apply_size=self.apply_size,
            apply_financial=self.apply_financial,
            only_warm=self.only_warm,
            exclude_clients=self.exclude_clients,
            center_lat=self.center_lat,
            center_lon=self.center_lon,
            radius_km=self.radius_km,
        )


@router.get("/top10")
def top10(session: Session = Depends(get_session)):
    container = build_container(session)
    return container.rolling10.get_top10_with_scores()


@router.get("/filters/defaults")
def filter_defaults():
    """Default ICP values + available options, for the frontend filter panel."""
    return {
        "regions": list(constants.REGIONS),
        "nace_include_prefixes": list(constants.FOCUS_NACE_PREFIXES),
        "nace_exclude_prefixes": list(constants.EXCLUDED_NACE_PREFIXES),
        "min_employees": constants.MIN_EMPLOYEES,
        "max_employees": constants.MAX_EMPLOYEES,
        "min_ebitda": constants.MIN_EBITDA,
        "max_ebitda": constants.MAX_EBITDA,
        "apply_size": True,
        "apply_financial": True,
        # Map defaults: centred on Belgium, area filter off (null radius).
        "center_lat": constants.MAP_DEFAULT_CENTER[0],
        "center_lon": constants.MAP_DEFAULT_CENTER[1],
        "radius_km": None,
        "available_sectors": sorted(set(constants.NACE_PREFIX_TO_SECTOR.values())),
        "nace_sector_labels": constants.NACE_PREFIX_TO_SECTOR,
    }


@router.post("/rank")
def rank(filters: FilterRequest, session: Session = Depends(get_session)):
    """Re-run selection + scoring with the given ICP filters; return the Rolling 10.

    only_warm / exclude_clients are applied at pond SELECTION time (see
    apply_icp_filters), so the scored set, the top-10, and /stats stay consistent.
    """
    container = build_container(session, filters.to_icp())
    container.pipeline.run()
    return container.rolling10.get_top10_with_scores()


@router.post("/stats")
def stats(filters: FilterRequest, session: Session = Depends(get_session)):
    """Pond scale + speed: total companies, how many match the ICP, and the query time.

    Pure COUNTs over the indexed Company table (no enrichment) — the honest basis
    for the "we scan 1M+ companies fast" headline. `elapsed_ms` is the DB time only.
    """
    icp = filters.to_icp()
    start = time.perf_counter()
    total = session.exec(
        select(func.count()).select_from(_C).where(_C.active == True)  # noqa: E712
    ).one()

    if icp.has_area:
        # apply_icp_filters only adds the cheap bounding box; trim to the exact
        # haversine circle in Python so the count matches what load_pond selects.
        rows = session.exec(
            apply_financial_filters(
                apply_icp_filters(select(_C.id, _C.latitude, _C.longitude), icp), icp
            )
        ).all()
        matched = sum(
            1 for _id, lat, lon in rows
            if haversine_km(icp.center_lat, icp.center_lon, lat, lon) <= icp.radius_km
        )
    else:
        matched = session.exec(
            apply_financial_filters(
                apply_icp_filters(select(func.count(func.distinct(_C.id))).select_from(_C), icp),
                icp,
            )
        ).one()
    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
    return {
        "total": total,
        "matched": matched,
        "shortlist": min(10, matched),
        "elapsed_ms": elapsed_ms,
    }


@router.get("/density")
def density(session: Session = Depends(get_session)):
    """Company count per geocoded location (zip centroid) — powers the map heat layer.

    Unfiltered on purpose: the whole 1.18M spread across Belgium. ~2.7k points.
    """
    rows = session.exec(
        select(_C.latitude, _C.longitude, func.count())
        .where(_C.latitude.is_not(None), _C.longitude.is_not(None))
        .group_by(_C.latitude, _C.longitude)
    ).all()
    return [{"lat": lat, "lon": lon, "count": count} for lat, lon, count in rows]


def _brief_payload(brief: _CB | None, crawl: _WC | None) -> dict | None:
    """Shape a CompanyBrief (+ its crawl status) for the API, or None if absent."""
    if brief is None:
        return None
    return {
        "why_company": brief.why_company,
        "financial_summary": brief.financial_summary,
        "signals": brief.signals,
        "generated_at": brief.generated_at.isoformat(),
        "crawl_status": crawl.status if crawl else None,
        "crawl_url": crawl.url if crawl else None,
    }


@router.get("/{company_id}")
def detail(company_id: int, session: Session = Depends(get_session)):
    company = session.get(_C, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    score = session.exec(select(_S).where(_S.company_id == company_id)).first()
    brief = session.exec(select(_CB).where(_CB.company_id == company_id)).first()
    crawl = session.exec(select(_WC).where(_WC.company_id == company_id)).first()
    return {
        "id": company.id,
        "name": company.name,
        "enterprise_number": company.enterprise_number,
        "sector": company.sector,
        "nace_code": company.nace_code,
        "region": company.region,
        "website": company.website,
        "address": company.address,
        "municipality": company.municipality,
        "latitude": company.latitude,
        "longitude": company.longitude,
        "rank": score.rank if score else None,
        "score": score.total if score else None,
        "breakdown": score.breakdown if score else {},
        "brief": _brief_payload(brief, crawl),
    }


@router.post("/{company_id}/brief/generate")
async def generate_brief(company_id: int, session: Session = Depends(get_session)):
    """Crawl the company's website (cached after first run) and generate a
    'Why this company' brief: reasons, financial summary, and signals."""
    company = session.get(_C, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    container = build_container(session)
    service = CompanyBriefService(session, container.crawler)
    brief = await service.build(company_id)
    crawl = session.exec(select(_WC).where(_WC.company_id == company_id)).first()
    return _brief_payload(brief, crawl)
