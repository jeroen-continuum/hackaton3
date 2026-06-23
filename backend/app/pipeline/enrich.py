"""Step 3 — Enrich the shortlist: contacts (Apollo), vacancies (VDAB), tech (Wappalyzer)."""
from sqlmodel import Session

from app.connectors.apollo import ApolloConnector
from app.connectors.vdab import VdabConnector
from app.connectors.wappalyzer import WappalyzerConnector


def enrich(session: Session) -> int:
    """Enrich all filtered companies. Returns count enriched. TODO: implement."""
    _apollo, _vdab, _wap = ApolloConnector(), VdabConnector(), WappalyzerConnector()
    # for each Company(stage="filtered"): add Contact/Vacancy/TechStack, set stage="enriched"
    raise NotImplementedError("Implement enrichment over filtered companies")
