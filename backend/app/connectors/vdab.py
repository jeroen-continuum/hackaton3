"""VDAB / Adzuna — open vacancies. IT roles = buyer-intent signal.

TODO: query developer portal by company; flag IT roles.
"""
from app.connectors.base import CachedConnector


class VdabConnector(CachedConnector):
    name = "vdab"

    def get_vacancies(self, company_name: str) -> list[dict]:
        cached = self.cache_get(company_name)
        if cached:
            return cached["vacancies"]
        # TODO: httpx GET VDAB vacancy API, then cache_put.
        raise NotImplementedError("Wire up VDAB vacancy lookup")
