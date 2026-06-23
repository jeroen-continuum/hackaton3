"""Wappalyzer / BuiltWith — tech stack from a domain. Legacy tech = high AI impact.

TODO: send domain, return technologies list + derive a legacy_score.
"""
from app.connectors.base import CachedConnector


class WappalyzerConnector(CachedConnector):
    name = "wappalyzer"

    def get_tech(self, domain: str) -> dict:
        cached = self.cache_get(domain)
        if cached:
            return cached
        # TODO: httpx GET API, then cache_put.
        raise NotImplementedError("Wire up Wappalyzer tech lookup")
