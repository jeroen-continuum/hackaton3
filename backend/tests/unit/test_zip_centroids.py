"""Tests for the Belgian postal-code centroid loader."""
from app.db.zip_centroids import load_centroids


def test_load_centroids_returns_zip_to_latlon():
    centroids = load_centroids()
    # Brussels 1000 is a well-known reference point.
    lat, lon = centroids["1000"]
    assert 50.7 <= lat <= 51.0
    assert 4.2 <= lon <= 4.5


def test_load_centroids_keys_are_strings():
    centroids = load_centroids()
    assert all(isinstance(k, str) for k in centroids)
    # Belgium has ~1100+ postal codes.
    assert len(centroids) > 1000


def test_load_centroids_is_cached_same_object():
    # Cheap repeated access should not re-read the file each call.
    assert load_centroids() is load_centroids()
