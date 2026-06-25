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
from app.models.entities import Company as _Company


class DbCompanySource:
    """Loads the candidate pond from the Company table, filtered by ICP."""

    def __init__(self, session: Session, icp: IcpFilter | None = None, limit: int = 500) -> None:
        self._session = session
        self._icp = icp or IcpFilter.default()
        self._limit = limit

    def load_pond(self) -> list[CompanyProfile]:
        stmt = select(_Company).where(_Company.active == True)  # noqa: E712

        if self._icp.regions:
            stmt = stmt.where(_Company.region.in_(self._icp.regions))

        if self._icp.nace_include_prefixes:
            stmt = stmt.where(
                or_(*[_Company.nace_code.like(f"{p}%") for p in self._icp.nace_include_prefixes])
            )

        if self._icp.nace_exclude_prefixes:
            stmt = stmt.where(
                and_(*[not_(_Company.nace_code.like(f"{p}%")) for p in self._icp.nace_exclude_prefixes])
            )

        if self._icp.has_area:
            # Coarse bounding-box prefilter in SQL (cheap, index-backed); the exact
            # circle is enforced with haversine below, BEFORE the limit, so the area
            # is part of candidate selection rather than a post-cap lens.
            lat_min, lat_max, lon_min, lon_max = bounding_box(
                self._icp.center_lat, self._icp.center_lon, self._icp.radius_km
            )
            stmt = stmt.where(
                _Company.latitude.is_not(None),
                _Company.longitude.is_not(None),
                _Company.latitude.between(lat_min, lat_max),
                _Company.longitude.between(lon_min, lon_max),
            )
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
