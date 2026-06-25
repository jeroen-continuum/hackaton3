"""WebCrawler adapters.

Crawl4aiCrawler does a real single-page crawl with Crawl4AI (headless Chromium).
NullCrawler is the no-Chromium default: it crawls nothing, so the brief service
falls back to the DB cache + financials. Selected in composition.py by the
`enable_web_crawl` flag.
"""


class Crawl4aiCrawler:
    """Single-page crawl via Crawl4AI. crawl4ai is imported lazily so the
    dependency (and its Chromium browser) is only needed when the flag is on."""

    async def crawl(self, url: str) -> dict | None:
        if not url:
            return None
        from crawl4ai import AsyncWebCrawler  # lazy: only when actually crawling

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
        if not result or not result.success:
            return None
        # crawl4ai markdown can be a str or a MarkdownGenerationResult; coerce.
        md = getattr(result.markdown, "raw_markdown", None) or str(result.markdown or "")
        title = (result.metadata or {}).get("title") if result.metadata else None
        return {"markdown": md, "title": title}


class NullCrawler:
    """No-op crawler used when web crawling is disabled."""

    async def crawl(self, url: str) -> dict | None:
        return None
