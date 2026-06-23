"""FOMO outreach email — grounded in WiiPlus solution-catalog cases for the sector.

Subject grabs attention (e.g. "De nieuwe lead voor [Bedrijfsnaam]"); body is a
pull, not a pitch: what peers already do and the % efficiency they are missing.
"""
from app.models import Company, SolutionCase
from app.outreach import prompts
from app.outreach.llm import complete


def generate_email(company: Company, cases: list[SolutionCase]) -> dict:
    """Returns {subject, body}. TODO: refine prompt + parse structured output."""
    case_text = "\n".join(f"- {c.title}: {c.summary} ({c.impact_metric})" for c in cases)
    prompt = prompts.EMAIL_PROMPT.format(
        company=company.name, sector=company.sector or "their sector", cases=case_text,
    )
    body = complete(prompts.SYSTEM, prompt)
    return {"subject": f"De nieuwe lead voor {company.name}", "body": body}
