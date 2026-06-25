"""Integration tests for /companies endpoints using TestClient + in-memory SQLite."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine, SQLModel

from app.main import app as fastapi_app
from app.db.session import get_session
import app.models  # noqa: F401 — registers SQLModel table metadata


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = override_session
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def client_with_engine():
    """Like `client`, but also hands back the engine so tests can seed rows."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = override_session
    yield TestClient(fastapi_app), engine
    fastapi_app.dependency_overrides.clear()


def test_top10_returns_list(client):
    response = client.get("/companies/top10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_company_detail_404_for_unknown(client):
    response = client.get("/companies/9999")
    assert response.status_code == 404


def test_top10_empty_when_no_data(client):
    response = client.get("/companies/top10")
    assert response.json() == []


def test_filter_defaults_returns_requirement_icp(client):
    response = client.get("/companies/filters/defaults")
    assert response.status_code == 200
    body = response.json()
    assert body["regions"] == ["BE", "NL"]
    assert "64" in body["nace_include_prefixes"]
    assert "86" in body["nace_exclude_prefixes"]
    assert body["min_employees"] == 100
    assert body["max_employees"] == 500
    assert "financial_services" in body["available_sectors"]


def test_rank_with_filters_returns_list(client):
    response = client.post("/companies/rank", json={
        "regions": ["BE"],
        "nace_include_prefixes": ["64"],
        "nace_exclude_prefixes": ["86"],
        "min_employees": 50,
        "max_employees": 1000,
        "apply_size": False,
        "apply_financial": False,
    })
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_rank_uses_defaults_for_empty_body(client):
    response = client.post("/companies/rank", json={})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# --- Area / map ----------------------------------------------------------

def test_filter_request_maps_area_fields_into_icp():
    from app.api.routes.companies import FilterRequest

    icp = FilterRequest(center_lat=50.85, center_lon=4.35, radius_km=25).to_icp()
    assert icp.center_lat == 50.85
    assert icp.center_lon == 4.35
    assert icp.radius_km == 25
    assert icp.has_area is True


def test_filter_request_defaults_have_no_area():
    from app.api.routes.companies import FilterRequest

    assert FilterRequest().to_icp().has_area is False


def test_rank_accepts_area_params(client):
    response = client.post("/companies/rank", json={
        "center_lat": 51.05, "center_lon": 3.72, "radius_km": 20,
    })
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filter_defaults_include_map_center(client):
    body = client.get("/companies/filters/defaults").json()
    assert "center_lat" in body and "center_lon" in body
    assert "radius_km" in body  # null = area filter off by default
    assert 49 <= body["center_lat"] <= 52  # somewhere in Belgium


def _seed_companies(engine):
    """Three active companies: two NACE 64 (one geocoded at the same point), one NACE 70."""
    from app.models.entities import Company
    with Session(engine) as s:
        s.add(Company(enterprise_number="0100000001", name="Fin A", region="BE",
                      nace_code="64190", latitude=50.85, longitude=4.35))
        s.add(Company(enterprise_number="0100000002", name="Fin B", region="BE",
                      nace_code="64200", latitude=50.85, longitude=4.35))
        s.add(Company(enterprise_number="0100000003", name="Prof C", region="BE",
                      nace_code="70220", latitude=51.05, longitude=3.72))
        s.commit()


def test_stats_counts_total_and_matched(client_with_engine):
    client, engine = client_with_engine
    _seed_companies(engine)
    # Only NACE 64 included → 2 of the 3 companies match. Data-dependent filters
    # off: these rows have no FinancialData, so size/financial would drop them.
    body = client.post("/companies/stats", json={
        "nace_include_prefixes": ["64"], "nace_exclude_prefixes": [],
        "apply_size": False, "apply_financial": False,
    }).json()
    assert body["total"] == 3
    assert body["matched"] == 2
    assert body["shortlist"] == 2
    assert isinstance(body["elapsed_ms"], (int, float))


def test_stats_matched_shrinks_with_narrower_filter(client_with_engine):
    client, engine = client_with_engine
    _seed_companies(engine)
    wide = client.post("/companies/stats", json={
        "nace_include_prefixes": ["64", "70"], "nace_exclude_prefixes": [],
        "apply_size": False, "apply_financial": False,
    }).json()["matched"]
    narrow = client.post("/companies/stats", json={
        "nace_include_prefixes": ["70"], "nace_exclude_prefixes": [],
        "apply_size": False, "apply_financial": False,
    }).json()["matched"]
    assert wide == 3 and narrow == 1


def _seed_with_financials(engine):
    """Two active NACE-64 companies, each with one FinancialData row."""
    from app.models.entities import Company, FinancialData
    with Session(engine) as s:
        big = Company(enterprise_number="0100000001", name="Big Fin", region="BE", nace_code="64190")
        small = Company(enterprise_number="0100000002", name="Small Fin", region="BE", nace_code="64200")
        s.add(big)
        s.add(small)
        s.commit()
        s.refresh(big)
        s.refresh(small)
        # Big: 250 FTE + ample EBITDA. Small: 10 FTE + tiny EBITDA.
        s.add(FinancialData(company_id=big.id, employees=250, ebitda=9_500_000))
        s.add(FinancialData(company_id=small.id, employees=10, ebitda=100_000))
        s.commit()


def test_stats_matched_respects_employee_filter(client_with_engine):
    client, engine = client_with_engine
    _seed_with_financials(engine)
    body = client.post("/companies/stats", json={
        "nace_include_prefixes": ["64"], "nace_exclude_prefixes": [],
        "min_employees": 100, "max_employees": 500,
        "apply_size": True, "apply_financial": False,
    }).json()
    assert body["total"] == 2
    assert body["matched"] == 1  # only Big Fin (250 FTE) is in the 100–500 range


def test_stats_matched_respects_financial_filter(client_with_engine):
    client, engine = client_with_engine
    _seed_with_financials(engine)
    body = client.post("/companies/stats", json={
        "nace_include_prefixes": ["64"], "nace_exclude_prefixes": [],
        "apply_size": False, "apply_financial": True,
    }).json()
    assert body["matched"] == 1  # only Big Fin clears the default EBITDA floor


def test_stats_matched_ignores_data_filters_when_off(client_with_engine):
    client, engine = client_with_engine
    _seed_with_financials(engine)
    body = client.post("/companies/stats", json={
        "nace_include_prefixes": ["64"], "nace_exclude_prefixes": [],
        "apply_size": False, "apply_financial": False,
    }).json()
    assert body["matched"] == 2  # both NACE-64 companies, no data-dependent filtering


def _add_connection(engine, enterprise_number, conn_type="EMPLOYER"):
    """Attach a warm tie of the given type to the company with this enterprise nr."""
    from sqlmodel import select as _select
    from app.models.entities import Company, Employee, Connection
    with Session(engine) as s:
        emp = Employee(name="Consultant")
        s.add(emp)
        s.commit()
        s.refresh(emp)
        cid = s.exec(
            _select(Company.id).where(Company.enterprise_number == enterprise_number)
        ).one()
        s.add(Connection(employee_id=emp.id, company_id=cid, type=conn_type))
        s.commit()


def test_stats_matched_respects_only_warm(client_with_engine):
    client, engine = client_with_engine
    _seed_companies(engine)  # 2 NACE-64 companies match
    _add_connection(engine, "0100000001")  # warm tie to exactly one of them
    base = {"nace_include_prefixes": ["64"], "nace_exclude_prefixes": [],
            "apply_size": False, "apply_financial": False}
    all_matched = client.post("/companies/stats", json=base).json()["matched"]
    warm_matched = client.post(
        "/companies/stats", json={**base, "only_warm": True}
    ).json()["matched"]
    assert all_matched == 2
    assert warm_matched == 1  # only the connected company survives


def test_stats_matched_respects_exclude_clients(client_with_engine):
    client, engine = client_with_engine
    _seed_companies(engine)  # 2 NACE-64 companies match
    _add_connection(engine, "0100000001", conn_type="CLIENT")  # one is a client
    base = {"nace_include_prefixes": ["64"], "nace_exclude_prefixes": [],
            "apply_size": False, "apply_financial": False}
    all_matched = client.post("/companies/stats", json=base).json()["matched"]
    no_clients = client.post(
        "/companies/stats", json={**base, "exclude_clients": True}
    ).json()["matched"]
    assert all_matched == 2
    assert no_clients == 1  # the client company is dropped


def test_density_aggregates_by_location(client_with_engine):
    client, engine = client_with_engine
    _seed_companies(engine)
    points = client.get("/companies/density").json()
    # Two distinct centroids; the shared (50.85, 4.35) point carries 2 companies.
    assert len(points) == 2
    assert sum(p["count"] for p in points) == 3
    assert max(p["count"] for p in points) == 2


# --- stats / rank consistency (the count must match what gets displayed) ----

def _add_company_with_financials(s, enr, nace, lat, lon, employees, ebitda):
    from app.models.entities import Company, FinancialData
    c = Company(enterprise_number=enr, name=enr, region="BE", nace_code=nace,
                latitude=lat, longitude=lon)
    s.add(c)
    s.commit()
    s.refresh(c)
    s.add(FinancialData(company_id=c.id, employees=employees, ebitda=ebitda))
    s.commit()
    return c.id


def test_stats_matched_equals_rank_count_inside_circle(client_with_engine):
    """A company inside the lat/lon bounding box but OUTSIDE the radius circle
    must not be counted by /stats — otherwise the headline over-reports vs the
    Rolling 10, which selects on the exact circle.
    """
    from app.domain.geo import bounding_box, haversine_km
    client, engine = client_with_engine
    clat, clon, radius = 51.05, 3.72, 10.0
    lat_min, lat_max, lon_min, lon_max = bounding_box(clat, clon, radius)
    # Corner-ish point: inside the box on both axes, but past the circle.
    corner_lat = clat + (lat_max - clat) * 0.9
    corner_lon = clon + (lon_max - clon) * 0.9
    assert haversine_km(clat, clon, corner_lat, corner_lon) > radius  # sanity

    with Session(engine) as s:
        _add_company_with_financials(s, "0100000001", "64190", clat, clon, 250, 9_500_000)
        _add_company_with_financials(s, "0100000002", "64200", corner_lat, corner_lon, 250, 9_500_000)

    filters = {
        "nace_include_prefixes": ["64"], "nace_exclude_prefixes": [],
        "min_employees": 100, "max_employees": 500, "apply_size": True, "apply_financial": True,
        "center_lat": clat, "center_lon": clon, "radius_km": radius,
    }
    matched = client.post("/companies/stats", json=filters).json()["matched"]
    ranked = client.post("/companies/rank", json=filters).json()
    assert matched == len(ranked)        # both should see exactly the 1 in-circle company
    assert len(ranked) == 1


def test_stats_matched_equals_rank_count_when_pond_limited(client_with_engine, monkeypatch):
    """Financially-qualifying companies must not be dropped just because lower-id
    non-qualifying companies fill the pond limit first. The candidate limit must
    be applied AFTER the financial filter, so /stats and /rank agree.
    """
    from app.core import config
    monkeypatch.setattr(config.settings, "max_pond_enrich", 1)

    client, engine = client_with_engine
    with Session(engine) as s:
        # Low id, fails the financial band (would fill the limit-1 pond).
        _add_company_with_financials(s, "0100000001", "64190", 51.0, 3.7, 10, 100_000)
        # Higher id, the only company that actually qualifies.
        _add_company_with_financials(s, "0100000002", "64200", 51.0, 3.7, 250, 9_500_000)

    filters = {
        "nace_include_prefixes": ["64"], "nace_exclude_prefixes": [],
        "min_employees": 100, "max_employees": 500, "apply_size": True, "apply_financial": True,
    }
    matched = client.post("/companies/stats", json=filters).json()["matched"]
    ranked = client.post("/companies/rank", json=filters).json()
    assert matched == len(ranked)
    assert len(ranked) == 1


def _seed_scored_company(engine, **coords):
    from app.models.entities import Company, Score
    with Session(engine) as s:
        c = Company(enterprise_number="0100000001", name="Geo Co", region="BE",
                    nace_code="64190", sector="financial_services", **coords)
        s.add(c)
        s.commit()
        s.refresh(c)
        s.add(Score(company_id=c.id, total=0.9, rank=1, contacted=False, breakdown={}))
        s.commit()
        return c.id


def test_detail_returns_coordinates():
    engine = create_engine("sqlite:///:memory:",
                           connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    cid = _seed_scored_company(engine, latitude=50.8504, longitude=4.3488,
                               municipality="Brussel")

    def override_session():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = override_session
    try:
        body = TestClient(fastapi_app).get(f"/companies/{cid}").json()
        assert body["latitude"] == 50.8504
        assert body["longitude"] == 4.3488
        assert body["municipality"] == "Brussel"
    finally:
        fastapi_app.dependency_overrides.clear()


def test_top10_items_carry_coordinates():
    engine = create_engine("sqlite:///:memory:",
                           connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    _seed_scored_company(engine, latitude=50.8504, longitude=4.3488, municipality="Brussel")

    def override_session():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = override_session
    try:
        items = TestClient(fastapi_app).get("/companies/top10").json()
        assert items and items[0]["latitude"] == 50.8504
        assert items[0]["longitude"] == 4.3488
    finally:
        fastapi_app.dependency_overrides.clear()
