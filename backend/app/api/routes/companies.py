"""Company endpoints — delegates to Rolling10 application service."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.composition import build_container
from app.core import constants
from app.db.session import get_session
from app.domain.filters import IcpFilter
from app.models import Company as _C, Score as _S

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
    apply_size: bool = True
    apply_financial: bool = True
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
            apply_size=self.apply_size,
            apply_financial=self.apply_financial,
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
    """Re-run selection + scoring with the given ICP filters; return the Rolling 10."""
    container = build_container(session, filters.to_icp())
    container.pipeline.run()
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
        "address": company.address,
        "municipality": company.municipality,
        "latitude": company.latitude,
        "longitude": company.longitude,
        "rank": score.rank if score else None,
        "score": score.total if score else None,
        "breakdown": score.breakdown if score else {},
    }
