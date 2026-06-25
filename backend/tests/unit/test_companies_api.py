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


def test_density_aggregates_by_location(client_with_engine):
    client, engine = client_with_engine
    _seed_companies(engine)
    points = client.get("/companies/density").json()
    # Two distinct centroids; the shared (50.85, 4.35) point carries 2 companies.
    assert len(points) == 2
    assert sum(p["count"] for p in points) == 3
    assert max(p["count"] for p in points) == 2


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
