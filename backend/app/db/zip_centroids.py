"""Belgian postal-code -> centroid (lat/lon) lookup.

KBO addresses carry only a postal code + municipality, no coordinates. We map
each postal code to a representative point using a static table derived from the
GeoNames open postal dataset (``data/geo/zipcode_centroids.csv``). Accuracy is
municipality-level (~1-3 km) — enough for radius / "within X km" filtering.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

from app.core.config import settings


def _csv_path() -> Path:
    return Path(settings.data_dir) / "geo" / "zipcode_centroids.csv"


@lru_cache(maxsize=1)
def load_centroids() -> dict[str, tuple[float, float]]:
    """Map postal code (string) -> (latitude, longitude). Cached after first read."""
    path = _csv_path()
    centroids: dict[str, tuple[float, float]] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                centroids[row["zipcode"].strip()] = (
                    float(row["latitude"]),
                    float(row["longitude"]),
                )
            except (KeyError, ValueError):
                continue
    return centroids
