"""Prompt templates for outreach generation. Kept here so copy can be tuned freely."""

SYSTEM = (
    "You write sharp B2B outreach for a consulting firm selling AI/digital "
    "transformation projects to mid-market companies in Belgium and the Netherlands. "
    "Tone: credible, concrete, no fluff. Always ground claims in the reference cases "
    "provided. Write in Dutch unless told otherwise."
)

EMAIL_PROMPT = (
    "Write a short outreach email to {company} (sector: {sector}).\n"
    "Do NOT hard-sell. Open with what peers in their sector already achieved, then "
    "the efficiency/revenue % they risk missing (FOMO). 120 words max.\n\n"
    "Reference cases:\n{cases}"
)

TEASER_PROMPT = (
    "Write a mini-report titled 'Three things to know about AI in {sector}'.\n"
    "Three crisp insights, each with a concrete metric. Executive tone, ~1.5 pages.\n\n"
    "Reference cases:\n{cases}"
)
