"""NBB Open Data financials adapter — implements FinancialsProvider Protocol.

Calls the NBB annual accounts API and extracts employees + EBITDA from XBRL codes.
Results are cached to disk via CachedConnector to survive rate limits.
"""
import httpx

from app.connectors.base import CachedConnector
from app.domain.models import Financials


class NbbFinancialsProvider(CachedConnector):
    """Fetches annual account financials from the NBB Open Data API."""
    name = "nbb_financials"
    BASE_URL = "https://api.cbe.be/company/v1/companies/{}/annualaccounts/latest"

    def fetch(self, enterprise_number: str) -> Financials | None:
        cached = self.cache_get(enterprise_number)
        if cached:
            return Financials(**cached)

        url = self.BASE_URL.format(enterprise_number)
        try:
            resp = httpx.get(url, timeout=10.0)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError):
            return None

        financials = self._parse(data)
        if financials:
            self.cache_put(enterprise_number, {
                "employees": financials.employees,
                "revenue": financials.revenue,
                "ebitda": financials.ebitda,
                "fiscal_year": financials.fiscal_year,
            })
        return financials

    def _parse(self, data: dict) -> Financials | None:
        # XBRL social balance: 9087=FTE, 9901=operating result (proxy for EBITDA)
        accounts = data.get("annualAccounts") or data.get("accounts") or []

        employees = None
        ebitda = None
        fiscal_year = None

        for account in accounts:
            fiscal_year = fiscal_year or account.get("fiscalYear") or account.get("closingDate", "")[:4] or None
            if fiscal_year:
                try:
                    fiscal_year = int(str(fiscal_year)[:4])
                except (ValueError, TypeError):
                    fiscal_year = None

            rubrics = account.get("rubrics") or account.get("items") or []
            for rubric in rubrics:
                code = str(rubric.get("code", "") or "").strip()
                value = rubric.get("value") if "value" in rubric else rubric.get("amount")
                try:
                    value = float(value) if value is not None else None
                except (TypeError, ValueError):
                    value = None

                if code == "9087" and value is not None:
                    employees = int(value)
                elif code == "9901" and value is not None:
                    ebitda = value

        if employees is None and ebitda is None:
            return None

        return Financials(
            employees=employees,
            ebitda=ebitda,
            fiscal_year=fiscal_year,
        )
