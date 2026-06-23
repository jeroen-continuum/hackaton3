"""Apollo.io / Hunter.io — buyer-persona contacts (CFO/CEO/director).

TODO: search by company name + role; return name, title, email.
"""
from app.connectors.base import CachedConnector


class ApolloConnector(CachedConnector):
    name = "apollo"

    def find_contacts(self, company_name: str) -> list[dict]:
        cached = self.cache_get(company_name)
        if cached:
            return cached["contacts"]
        # TODO: httpx POST Apollo people search, then cache_put.
        raise NotImplementedError("Wire up Apollo contact search")
