"""LLM-powered outreach generator adapter."""
from app.domain.models import CompanyProfile
from app.outreach import prompts
from app.outreach.llm import complete


class LlmOutreachGenerator:
    """Generates personalised outreach assets (email + teaser) using Claude."""

    def email(self, company: CompanyProfile, cases: list[dict]) -> dict:
        """Generate FOMO email for a company based on reference cases.

        Args:
            company: Target company profile
            cases: List of reference success cases

        Returns:
            Dict with "subject" and "body" keys
        """
        case_text = "\n".join(
            f"- {c.get('title', '')}: {c.get('summary', '')} ({c.get('impact_metric', '')})"
            for c in cases
        )
        prompt = prompts.EMAIL_PROMPT.format(
            company=company.name,
            sector=company.sector or "their sector",
            cases=case_text,
        )
        body = complete(prompts.SYSTEM, prompt)
        return {"subject": f"De nieuwe lead voor {company.name}", "body": body}

    def teaser(self, company: CompanyProfile, cases: list[dict]) -> dict:
        """Generate gated teaser content for a company.

        Args:
            company: Target company profile
            cases: List of reference success cases

        Returns:
            Dict with "title", "preview" (800 chars), and "full" keys
        """
        sector = company.sector or "your sector"
        case_text = "\n".join(
            f"- {c.get('title', '')}: {c.get('impact_metric', '')}"
            for c in cases
        )
        full = complete(
            prompts.SYSTEM,
            prompts.TEASER_PROMPT.format(sector=sector, cases=case_text),
            max_tokens=2048,
        )
        preview = full[:800]
        return {
            "title": f"Three things to know about AI in {sector}",
            "preview": preview,
            "full": full,
        }
