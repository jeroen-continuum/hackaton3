"""Apollo contact adapter — fetches buyer-persona contacts in-memory.

PII constraint: contacts must NEVER be written to DB, cache, or logs.
This adapter does NOT extend CachedConnector.
"""
import httpx
from app.core.config import settings


class ApolloContactProvider:
    """Fetches buyer-persona contacts in-memory. Never cached — PII constraint."""

    BASE_URL = "https://api.apollo.io/v1/mixed_people/search"

    def find_buyer_personas(self, enterprise_number: str) -> list[dict]:
        api_key = getattr(settings, "apollo_api_key", "")
        if not api_key:
            return self._demo_personas(enterprise_number)
        try:
            resp = httpx.post(
                self.BASE_URL,
                headers={"X-Api-Key": api_key},
                json={
                    "q_organization_domains": enterprise_number,
                    "person_titles": ["CFO", "CEO", "CTO", "Director", "Head of"],
                    "per_page": 5,
                },
                timeout=10.0,
            )
            if resp.status_code != 200:
                return []
            people = resp.json().get("people") or []
            return [
                {
                    "name": p.get("name", ""),
                    "title": p.get("title", ""),
                    "email": p.get("email", ""),
                }
                for p in people
            ]
        except (httpx.HTTPError, ValueError):
            return []

    def _demo_personas(self, enterprise_number: str) -> list[dict]:
        """Demo fallback when no API key — returns plausible fixture data."""
        return [
            {"name": "Jan Claes", "title": "CFO", "email": ""},
            {"name": "Marie Goossens", "title": "CTO", "email": ""},
        ]
