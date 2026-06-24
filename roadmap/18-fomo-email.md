# 18 — fomo-email

**Milestone:** M4  **Depends on:** 03-ports, 17-solution-cases

## Goal
Implement LLM-powered email generator creating personalized outreach with FOMO framing and grounded solution cases.

## TDD Steps
1. **Red:** Create `backend/app/adapters/outreach/llm_email.py` with stub. Write test in `backend/tests/adapters/test_llm_email.py` using respx to mock Claude API. Import LlmEmailGenerator and call `email(company, signals, cases)`. Assert subject starts with "De nieuwe lead voor" and body is non-empty. Confirm ImportError.
2. **Green:** Implement LlmEmailGenerator.email() wrapping `app.outreach.message.generate_email`. Call Claude API with company context + sector solution cases. Parse structured output (subject, body). Subject template: "De nieuwe lead voor [Sector] – [Company]". Body frames FOMO: missed opportunity + tailored case study.
3. **Refactor:** Add response validation, error handling, retry logic, jinja2 templating for subject.

## Files
- **Created:** backend/app/adapters/outreach/llm_email.py, backend/tests/adapters/test_llm_email.py

## Acceptance
Run `pytest backend/tests/adapters/test_llm_email.py -q` and verify all tests pass.
