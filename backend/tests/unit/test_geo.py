"""Unit tests for the pure geo helpers (haversine + bounding box)."""
import math

from app.domain.geo import bounding_box, haversine_km

# Reference coordinates (GeoNames centroids).
BRUSSELS = (50.8504, 4.3488)
ANTWERP = (51.2194, 4.4025)
GHENT = (51.0543, 3.7174)


def test_haversine_same_point_is_zero():
    assert haversine_km(*BRUSSELS, *BRUSSELS) == 0.0


def test_haversine_brussels_antwerp_about_40km():
    # Great-circle distance Brussels <-> Antwerp is ~41 km.
    d = haversine_km(*BRUSSELS, *ANTWERP)
    assert 38.0 <= d <= 44.0


def test_haversine_is_symmetric():
    a = haversine_km(*BRUSSELS, *GHENT)
    b = haversine_km(*GHENT, *BRUSSELS)
    assert math.isclose(a, b, rel_tol=1e-9)


def test_bounding_box_brackets_the_center():
    lat_min, lat_max, lon_min, lon_max = bounding_box(*BRUSSELS, radius_km=20)
    lat, lon = BRUSSELS
    assert lat_min < lat < lat_max
    assert lon_min < lon < lon_max


def test_bounding_box_latitude_span_matches_radius():
    # 1 degree latitude ~= 111 km, so a 111 km radius spans ~1 degree each way.
    lat_min, lat_max, _, _ = bounding_box(*BRUSSELS, radius_km=111)
    assert math.isclose(lat_max - BRUSSELS[0], 1.0, abs_tol=0.02)
    assert math.isclose(BRUSSELS[0] - lat_min, 1.0, abs_tol=0.02)


def test_bounding_box_longitude_widens_with_latitude():
    # Longitude degrees shrink toward the poles, so the lon span must be wider
    # than the lat span at Belgian latitudes.
    lat_min, lat_max, lon_min, lon_max = bounding_box(*BRUSSELS, radius_km=20)
    assert (lon_max - lon_min) > (lat_max - lat_min)
