"""'McKinsey/Gartner' pull mini-report: "Three things to know about AI in [Sector]".

Returns a short preview (~1.5 pages) plus the gated full body. The web app shows
the preview; the rest unlocks once the prospect leaves contact details.
"""
from app.models import Company, SolutionCase
from app.outreach import prompts
from app.outreach.llm import complete


def generate_teaser(company: Company, cases: list[SolutionCase]) -> dict:
    """Returns {title, preview, full}. TODO: split preview/full deterministically."""
    sector = company.sector or "your sector"
    case_text = "\n".join(f"- {c.title}: {c.impact_metric}" for c in cases)
    full = complete(
        prompts.SYSTEM,
        prompts.TEASER_PROMPT.format(sector=sector, cases=case_text),
        max_tokens=2048,
    )
    preview = full[:800]  # first ~1.5 pages; gate the remainder
    return {
        "title": f"Three things to know about AI in {sector}",
        "preview": preview,
        "full": full,
    }
