"""VDAB vacancy adapter — fetches open vacancies via Adzuna API."""
import httpx

from app.connectors.base import CachedConnector
from app.core.config import settings


IT_KEYWORDS = frozenset([
    "developer", "engineer", "architect", "data", "cloud",
    "devops", "it", "software", "tech", "digital",
    "cyber", "infra", "platform", "sap", "erp",
])


class VdabVacancyProvider(CachedConnector):
    name = "vdab_vacancies"
    BASE_URL = (
        "https://api.adzuna.com/v1/api/jobs/be/search/1"
        "?app_id={app_id}&app_key={app_key}"
        "&what=&where=&company={company_name}"
        "&results_per_page=20&content-type=application/json"
    )

    def fetch(self, enterprise_number: str) -> list[dict]:
        cached = self.cache_get(enterprise_number)
        if cached is not None:
            return cached

        url = self.BASE_URL.format(
            app_id=getattr(settings, "vdab_app_id", "TEST"),
            app_key=getattr(settings, "vdab_app_key", "TEST"),
            company_name=enterprise_number,
        )
        try:
            resp = httpx.get(url, timeout=10.0)
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError):
            return []

        vacancies = self._parse(data)
        self.cache_put(enterprise_number, vacancies)
        return vacancies

    def _parse(self, data: dict) -> list[dict]:
        results = data.get("results") or []
        vacancies = []
        for item in results:
            title = item.get("title") or ""
            vacancies.append({
                "title": title,
                "url": item.get("redirect_url"),
                "is_it_role": _is_it_role(title),
            })
        return vacancies


def _is_it_role(title: str) -> bool:
    lower = title.lower()
    return any(kw in lower for kw in IT_KEYWORDS)
