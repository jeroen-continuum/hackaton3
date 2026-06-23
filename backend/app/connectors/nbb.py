"""NBB (Nationale Bank) Open Data API — financials by enterprise number.

TODO: call the XBRL / Standardized Data API; return FTE count + EBITDA.
"""
from app.connectors.base import CachedConnector


class NbbConnector(CachedConnector):
    name = "nbb"

    def get_financials(self, enterprise_number: str) -> dict:
        cached = self.cache_get(enterprise_number)
        if cached:
            return cached
        # TODO: httpx GET NBB API, parse employees + EBITDA, then cache_put.
        raise NotImplementedError("Wire up NBB financials lookup")
