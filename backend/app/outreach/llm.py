"""Thin Anthropic client wrapper for outreach generation."""
from anthropic import Anthropic

from app.core.config import settings


def complete(system: str, prompt: str, max_tokens: int = 1024) -> str:
    client = Anthropic(api_key=settings.anthropic_api_key)
    msg = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in msg.content if block.type == "text")
