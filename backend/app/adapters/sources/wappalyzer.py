"""Wappalyzer Live API adapter — implements TechProvider Protocol.

Detects technology stack from a domain name and computes a legacy_score
(0..1 float) indicating how much AI transformation room is present.
Higher score = more legacy tech = more impact potential.
"""
import httpx

from app.connectors.base import CachedConnector
from app.core.config import settings

LEGACY_SIGNALS = frozenset([
    "sap", "oracle", "erp", "crm", "sharepoint", "ms access", "cobol",
    "visual basic", "delphi", "lotus", "mainframe", "as/400", "classic asp",
    "jquery", "angularjs", "silverlight", "flash", "coldfusion",
])


def _compute_legacy_score(technologies: list[dict]) -> float:
    """Higher = more legacy tech present = more AI transformation room."""
    if not technologies:
        return 0.0
    names = {t.get("name", "").lower() for t in technologies}
    cats = {
        c.get("name", "").lower()
        for t in technologies
        for c in t.get("categories", [])
    }
    hits = sum(1 for kw in LEGACY_SIGNALS if kw in names or kw in cats)
    return min(1.0, hits / 3)  # 3 hits = score 1.0


class WappalyzerTechProvider(CachedConnector):
    """Calls Wappalyzer Live API to detect technology stack for a domain."""

    name = "wappalyzer_tech"
    BASE_URL = "https://api.wappalyzer.com/v2/lookup/?urls={domain}"

    def fetch(self, domain: str) -> dict | None:
        """Fetch technology data for a domain, with disk cache."""
        cached = self.cache_get(domain)
        if cached is not None:
            return cached

        url = self.BASE_URL.format(domain=domain)
        api_key = getattr(settings, "wappalyzer_api_key", "TEST")
        try:
            resp = httpx.get(url, headers={"x-api-key": api_key}, timeout=10.0)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError):
            return None

        result = self._parse(data)
        if result is not None:
            self.cache_put(domain, result)
        return result

    def _parse(self, data) -> dict | None:
        """Parse Wappalyzer API response into normalised dict."""
        if not data or not isinstance(data, list):
            return None
        technologies = []
        for item in data:
            technologies.extend(item.get("technologies") or [])
        if not technologies:
            return None
        return {
            "technologies": technologies,
            "legacy_score": _compute_legacy_score(technologies),
        }
