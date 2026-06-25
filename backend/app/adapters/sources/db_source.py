"""DB-backed company source — implements the CompanySource port.

The full active-company universe is bulk-loaded into the Company table by
app/db/load_kbo.py. This adapter selects the candidate "pond" from that table
applying the adjustable IcpFilter (region + NACE include/exclude) and a hard
LIMIT, so only a bounded set is enriched + scored downstream.
"""
from sqlalchemy import and_, not_, or_
from sqlmodel import Session, select

from app.domain.filters import IcpFilter
from app.domain.geo import bounding_box, haversine_km
from app.domain.models import CompanyProfile
from app.models.entities import Company as _Company, FinancialData as _FinData


def apply_icp_filters(stmt, icp: IcpFilter):
    """Add the ICP region + NACE include/exclude + area bounding-box predicates.

    Shared by the pond selection (DbCompanySource) and the /stats + /density count
    queries so they filter identically. For an area filter this applies only the
    cheap bounding box; the exact haversine circle is enforced by load_pond.
    """
    stmt = stmt.where(_Company.active == True)  # noqa: E712

    if icp.regions:
        stmt = stmt.where(_Company.region.in_(icp.regions))

    if icp.nace_include_prefixes:
        stmt = stmt.where(
            or_(*[_Company.nace_code.like(f"{p}%") for p in icp.nace_include_prefixes])
        )

    if icp.nace_exclude_prefixes:
        stmt = stmt.where(
            and_(*[not_(_Company.nace_code.like(f"{p}%")) for p in icp.nace_exclude_prefixes])
        )

    if icp.has_area:
        lat_min, lat_max, lon_min, lon_max = bounding_box(
            icp.center_lat, icp.center_lon, icp.radius_km
        )
        stmt = stmt.where(
            _Company.latitude.is_not(None),
            _Company.longitude.is_not(None),
            _Company.latitude.between(lat_min, lat_max),
            _Company.longitude.between(lon_min, lon_max),
        )
    return stmt


def apply_financial_filters(stmt, icp: IcpFilter):
    """Join FinancialData and apply the size + EBITDA-range predicates.

    Mirrors IcpFilterPolicy.evaluate for the /stats count: when either
    data-dependent filter is on, a company must have a financial row that
    satisfies it (no row -> dropped, like evaluate's "no financial data").
    No-op when both filters are off, so the count stays a pure Company query.
    """
    if not (icp.apply_size or icp.apply_financial):
        return stmt
    stmt = stmt.join(_FinData, _FinData.company_id == _Company.id)
    if icp.apply_size:
        stmt = stmt.where(
            _FinData.employees.is_not(None),
            _FinData.employees >= icp.min_employees,
            _FinData.employees <= icp.max_employees,
        )
    if icp.apply_financial:
        stmt = stmt.where(
            _FinData.ebitda.is_not(None),
            _FinData.ebitda > 0,
            _FinData.ebitda >= icp.min_ebitda,
        )
        if icp.max_ebitda is not None:
            stmt = stmt.where(_FinData.ebitda <= icp.max_ebitda)
    return stmt


class DbCompanySource:
    """Loads the candidate pond from the Company table, filtered by ICP."""

    def __init__(self, session: Session, icp: IcpFilter | None = None, limit: int = 500) -> None:
        self._session = session
        self._icp = icp or IcpFilter.default()
        self._limit = limit

    def load_pond(self) -> list[CompanyProfile]:
        # Apply the financial filter at SELECTION time, BEFORE the limit — otherwise
        # the limit fills up with low-id companies that fail the financial band and
        # the qualifying ones (often higher ids) never get scored, so /stats and the
        # Rolling 10 disagree. No-op when both data filters are off.
        # ponytail: assumes DB-backed financials (same assumption /stats already makes);
        # if NBB live-fetch is ever the only source, selection-time filtering needs rework.
        # Deterministic ordering so the candidate pool (and thus the scored set)
        # is stable across runs — provisioning relies on selecting the same set.
        stmt = apply_financial_filters(
            apply_icp_filters(select(_Company), self._icp), self._icp
        ).order_by(_Company.id)

        if self._icp.has_area:
            # The bounding box is already applied; enforce the exact circle with
            # haversine BEFORE the limit, so the area is part of candidate
            # selection rather than a post-cap lens.
            rows = self._session.exec(stmt).all()
            rows = [
                c for c in rows
                if haversine_km(
                    self._icp.center_lat, self._icp.center_lon, c.latitude, c.longitude
                ) <= self._icp.radius_km
            ][: self._limit]
        else:
            rows = self._session.exec(stmt.limit(self._limit)).all()

        return [
            CompanyProfile(
                enterprise_number=c.enterprise_number,
                name=c.name,
                region=c.region,
                nace_code=c.nace_code,
                sector=c.sector,
                website=c.website,
                municipality=c.municipality,
                latitude=c.latitude,
                longitude=c.longitude,
            )
            for c in rows
        ]
