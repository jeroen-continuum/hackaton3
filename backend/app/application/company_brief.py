"""CompanyBrief use-case: crawl-or-cache the website, then generate a grounded
'Why this company' brief (reasons + financial summary + signals) via the LLM.

The website crawl is cached in the WebsiteCrawl table so we crawl once, not per
view. Crawling itself is delegated to the WebCrawler port (NullCrawler when the
enable_web_crawl flag is off — the brief then falls back to financials/profile).
"""
import json

from sqlmodel import Session, select

from app.domain.ports import WebCrawler
from app.models.entities import (
    Company as _Company,
    CompanyBrief as _Brief,
    FinancialData as _Financials,
    WebsiteCrawl as _Crawl,
)
from app.outreach import prompts
from app.outreach.llm import complete

_MARKDOWN_LIMIT = 6000   # chars of site text fed to the LLM


def normalise_url(website: str | None) -> str | None:
    """KBO stores bare domains (argenta.be, deloitte.com/be). Make a fetchable URL."""
    if not website:
        return None
    w = website.strip()
    if not w:
        return None
    return w if w.startswith(("http://", "https://")) else f"https://{w}"


def _financials_text(fin: _Financials | None) -> str:
    if fin is None:
        return "geen financiële gegevens beschikbaar"
    parts = []
    if fin.employees is not None:
        parts.append(f"{fin.employees} medewerkers")
    if fin.revenue is not None:
        parts.append(f"omzet €{fin.revenue:,.0f}")
    if fin.ebitda is not None:
        parts.append(f"EBITDA €{fin.ebitda:,.0f}")
    if fin.fiscal_year is not None:
        parts.append(f"boekjaar {fin.fiscal_year}")
    return ", ".join(parts) or "geen financiële gegevens beschikbaar"


class CompanyBriefService:
    def __init__(self, session: Session, crawler: WebCrawler) -> None:
        self._session = session
        self._crawler = crawler

    async def get_or_crawl(self, company: _Company) -> _Crawl | None:
        """Return the cached crawl, crawling once on a miss. None if no website."""
        existing = self._session.exec(
            select(_Crawl).where(_Crawl.company_id == company.id)
        ).first()
        if existing:
            return existing

        url = normalise_url(company.website)
        if url is None:
            return None

        try:
            result = await self._crawler.crawl(url)
        except Exception:
            result = None

        if result is None:
            # NullCrawler / no browser / fetch failed: record an empty row so we
            # don't re-attempt every call. status distinguishes the two cases only
            # loosely — good enough for the demo.
            row = _Crawl(company_id=company.id, url=url, markdown=None, status="empty")
        else:
            md = result.get("markdown")
            row = _Crawl(
                company_id=company.id,
                url=url,
                markdown=md,
                title=result.get("title"),
                status="ok" if md else "empty",
            )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return row

    async def build(self, company_id: int) -> _Brief | None:
        """Build + persist the brief for a company. None if the company is unknown."""
        company = self._session.get(_Company, company_id)
        if company is None:
            return None

        crawl = await self.get_or_crawl(company)
        markdown = (crawl.markdown if crawl else None) or ""
        fin = self._session.exec(
            select(_Financials).where(_Financials.company_id == company_id)
        ).first()

        prompt = prompts.BRIEF_PROMPT.format(
            company=company.name,
            sector=company.sector or "onbekend",
            financials=_financials_text(fin),
            website=markdown[:_MARKDOWN_LIMIT] or "(geen website-tekst)",
        )
        raw = complete(prompts.BRIEF_SYSTEM, prompt, max_tokens=1024)
        parsed = _parse_brief(raw, company.name)

        existing = self._session.exec(
            select(_Brief).where(_Brief.company_id == company_id)
        ).first()
        if existing:
            existing.why_company = parsed["why_company"]
            existing.financial_summary = parsed["financial_summary"]
            existing.signals = parsed["signals"]
            self._session.add(existing)
            brief = existing
        else:
            brief = _Brief(
                company_id=company_id,
                why_company=parsed["why_company"],
                financial_summary=parsed["financial_summary"],
                signals=parsed["signals"],
            )
            self._session.add(brief)
        self._session.commit()
        self._session.refresh(brief)
        return brief


def _parse_brief(raw: str, company_name: str) -> dict:
    """Parse the LLM JSON; tolerate fences/garbage so the endpoint never 500s."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    start, end = text.find("{"), text.rfind("}")
    try:
        data = json.loads(text[start:end + 1])
        return {
            "why_company": list(data.get("why_company") or []),
            "financial_summary": data.get("financial_summary") or "",
            "signals": list(data.get("signals") or []),
        }
    except (ValueError, TypeError):
        return {
            "why_company": [f"{company_name} past binnen het ICP (zie score)."],
            "financial_summary": "",
            "signals": [],
        }
