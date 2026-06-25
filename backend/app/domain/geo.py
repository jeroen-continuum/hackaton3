"""Pure geographic helpers — great-circle distance and a coarse bounding box.

No I/O, no framework imports (domain-pure). Used by the area filter to select
companies within a radius of a chosen point. Distances are in kilometres.
"""
from __future__ import annotations

import math

_EARTH_RADIUS_KM = 6371.0
# Mean kilometres per degree of latitude (constant); longitude scales by cos(lat).
_KM_PER_DEG = 111.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def bounding_box(
    lat: float, lon: float, radius_km: float
) -> tuple[float, float, float, float]:
    """Lat/lon box that fully contains the radius circle around (lat, lon).

    A coarse, cheap prefilter (usable in a SQL ``BETWEEN``); the exact circle is
    enforced afterwards with :func:`haversine_km`. Returns
    ``(lat_min, lat_max, lon_min, lon_max)``.
    """
    dlat = radius_km / _KM_PER_DEG
    # Guard against cos -> 0 near the poles (irrelevant for Belgium, but safe).
    cos_lat = max(math.cos(math.radians(lat)), 1e-6)
    dlon = radius_km / (_KM_PER_DEG * cos_lat)
    return (lat - dlat, lat + dlat, lon - dlon, lon + dlon)
