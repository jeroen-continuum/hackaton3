"""Tests for DbCompanySource — pond selection from the Company table by ICP."""
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.adapters.sources.db_source import DbCompanySource
from app.domain.filters import IcpFilter
from app.domain.ports import CompanySource
from app.models.entities import Company


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all([
            Company(enterprise_number="1", name="BE Finance", region="BE", nace_code="64190", active=True),
            Company(enterprise_number="2", name="BE Health", region="BE", nace_code="86100", active=True),
            Company(enterprise_number="3", name="NL Finance", region="NL", nace_code="64190", active=True),
            Company(enterprise_number="4", name="BE Prof", region="BE", nace_code="70100", active=True),
            Company(enterprise_number="5", name="BE Inactive", region="BE", nace_code="64190", active=False),
        ])
        s.commit()
        yield s


def test_satisfies_protocol(session):
    assert isinstance(DbCompanySource(session), CompanySource)


# These tests cover region/NACE/geo selection in isolation; the seeded companies
# have no FinancialData, so the data-dependent filters are switched off (they're
# exercised separately in the stats/rank API tests).
_NO_FIN = dict(apply_size=False, apply_financial=False)


def test_default_icp_includes_focus_excludes_health_and_inactive(session):
    pond = DbCompanySource(session, IcpFilter(**_NO_FIN), limit=100).load_pond()
    names = {c.name for c in pond}
    assert names == {"BE Finance", "NL Finance", "BE Prof"}
    assert "BE Health" not in names      # 86 excluded
    assert "BE Inactive" not in names    # inactive


def test_region_filter(session):
    icp = IcpFilter(regions=["BE"], **_NO_FIN)
    names = {c.name for c in DbCompanySource(session, icp, limit=100).load_pond()}
    assert "NL Finance" not in names
    assert "BE Finance" in names


def test_empty_include_returns_all_active_non_excluded(session):
    icp = IcpFilter(nace_include_prefixes=[], **_NO_FIN)
    names = {c.name for c in DbCompanySource(session, icp, limit=100).load_pond()}
    # All active except the excluded 86 health company.
    assert names == {"BE Finance", "NL Finance", "BE Prof"}


def test_limit_caps_result(session):
    pond = DbCompanySource(session, IcpFilter(**_NO_FIN), limit=1).load_pond()
    assert len(pond) == 1


# --- Area / radius filter -------------------------------------------------

BRUSSELS = (50.8504, 4.3488)
ANTWERP = (51.2194, 4.4025)   # ~40 km from Brussels
GHENT = (51.0543, 3.7174)     # ~50 km from Brussels


@pytest.fixture
def geo_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all([
            Company(enterprise_number="b", name="Brussels Co", region="BE",
                    nace_code="64190", latitude=BRUSSELS[0], longitude=BRUSSELS[1]),
            Company(enterprise_number="a", name="Antwerp Co", region="BE",
                    nace_code="64190", latitude=ANTWERP[0], longitude=ANTWERP[1]),
            Company(enterprise_number="g", name="Ghent Co", region="BE",
                    nace_code="64190", latitude=GHENT[0], longitude=GHENT[1]),
            Company(enterprise_number="n", name="Nowhere Co", region="BE",
                    nace_code="64190", latitude=None, longitude=None),
        ])
        s.commit()
        yield s


def test_radius_keeps_in_area_drops_out_of_area(geo_session):
    icp = IcpFilter(center_lat=BRUSSELS[0], center_lon=BRUSSELS[1], radius_km=25, **_NO_FIN)
    names = {c.name for c in DbCompanySource(geo_session, icp, limit=100).load_pond()}
    assert names == {"Brussels Co"}  # Antwerp ~40km, Ghent ~50km excluded


def test_wider_radius_includes_more(geo_session):
    icp = IcpFilter(center_lat=BRUSSELS[0], center_lon=BRUSSELS[1], radius_km=60, **_NO_FIN)
    names = {c.name for c in DbCompanySource(geo_session, icp, limit=100).load_pond()}
    assert names == {"Brussels Co", "Antwerp Co", "Ghent Co"}


def test_null_coords_excluded_when_radius_active(geo_session):
    icp = IcpFilter(center_lat=BRUSSELS[0], center_lon=BRUSSELS[1], radius_km=500, **_NO_FIN)
    names = {c.name for c in DbCompanySource(geo_session, icp, limit=100).load_pond()}
    assert "Nowhere Co" not in names


def test_no_radius_keeps_all_including_null_coords(geo_session):
    # Geo filter off -> behaviour unchanged, null-coord rows still returned.
    names = {c.name for c in DbCompanySource(geo_session, IcpFilter(**_NO_FIN), limit=100).load_pond()}
    assert "Nowhere Co" in names
    assert len(names) == 4


def test_profiles_carry_coordinates(geo_session):
    icp = IcpFilter(center_lat=BRUSSELS[0], center_lon=BRUSSELS[1], radius_km=25, **_NO_FIN)
    pond = DbCompanySource(geo_session, icp, limit=100).load_pond()
    bru = next(c for c in pond if c.name == "Brussels Co")
    assert bru.latitude == BRUSSELS[0]
    assert bru.longitude == BRUSSELS[1]
