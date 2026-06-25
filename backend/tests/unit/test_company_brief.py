"""CompanyBriefService: crawl caching + brief generation + JSON fallback.

Async port driven via asyncio.run so no pytest-asyncio is needed.
"""
import asyncio

import pytest
from sqlmodel import SQLModel, Session, create_engine, select

from app.application import company_brief as cb_mod
from app.application.company_brief import CompanyBriefService, normalise_url
from app.models.entities import Company, CompanyBrief, WebsiteCrawl


class FakeCrawler:
    """Counts calls so we can prove the cache hit skips the crawl."""

    def __init__(self, markdown="Wij bouwen legacy software en zoeken 5 IT'ers."):
        self.calls = 0
        self.markdown = markdown

    async def crawl(self, url: str) -> dict | None:
        self.calls += 1
        return {"markdown": self.markdown, "title": "Acme"}


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def _seed_company(session) -> int:
    c = Company(enterprise_number="0123456789", name="Acme", website="acme.be")
    session.add(c)
    session.commit()
    session.refresh(c)
    return c.id


def _stub_complete(monkeypatch, payload):
    monkeypatch.setattr(cb_mod, "complete", lambda *a, **k: payload)


def test_build_crawls_once_and_persists(session, monkeypatch):
    cid = _seed_company(session)
    _stub_complete(
        monkeypatch,
        '{"why_company": ["Legacy stack"], "financial_summary": "Gezond", "signals": ["5 IT-vacatures"]}',
    )
    crawler = FakeCrawler()

    brief = asyncio.run(CompanyBriefService(session, crawler).build(cid))

    assert crawler.calls == 1
    assert brief.why_company == ["Legacy stack"]
    assert brief.signals == ["5 IT-vacatures"]
    # crawl payload cached in DB
    row = session.exec(select(WebsiteCrawl).where(WebsiteCrawl.company_id == cid)).first()
    assert row is not None and row.status == "ok" and row.markdown


def test_second_build_uses_cache(session, monkeypatch):
    cid = _seed_company(session)
    _stub_complete(monkeypatch, '{"why_company": [], "financial_summary": "", "signals": []}')
    crawler = FakeCrawler()
    svc = CompanyBriefService(session, crawler)

    asyncio.run(svc.build(cid))
    asyncio.run(svc.build(cid))

    assert crawler.calls == 1  # second build hit the cache, did not re-crawl


def test_malformed_json_falls_back(session, monkeypatch):
    cid = _seed_company(session)
    _stub_complete(monkeypatch, "not json at all")
    brief = asyncio.run(CompanyBriefService(session, FakeCrawler()).build(cid))
    assert len(brief.why_company) == 1  # fallback reason, no raise
    assert brief.signals == []


def test_normalise_url():
    assert normalise_url("acme.be") == "https://acme.be"
    assert normalise_url("https://acme.be") == "https://acme.be"
    assert normalise_url(None) is None
    assert normalise_url("") is None
