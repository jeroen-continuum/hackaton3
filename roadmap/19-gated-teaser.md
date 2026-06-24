# 19 — gated-teaser

**Milestone:** M4  **Depends on:** 03-ports, 17-solution-cases

## Goal
Implement LLM-powered teaser generator creating a gated report with preview (1.5 pages) and full version (multi-page) to drive engagement.

## TDD Steps
1. **Red:** Create `backend/app/adapters/outreach/llm_teaser.py` with stub. Write test in `backend/tests/adapters/test_llm_teaser.py` using respx mock. Import LlmTeaserGenerator and call `teaser(company, signals, cases)`. Assert teaser_preview ≈800 chars, teaser_full > teaser_preview. Confirm ImportError.
2. **Green:** Implement LlmTeaserGenerator.teaser() wrapping `app.outreach.teaser`. Call Claude API with company + sector context. Generate title: "Three things to know about AI in [Sector]". Split into teaser_preview (first 1.5 pages, ≈800 chars) and teaser_full (complete, multi-page). Return both.
3. **Refactor:** Add section structure (intro, three key points, call-to-action), enhance preview cutoff logic, add word-count validation.

## Files
- **Created:** backend/app/adapters/outreach/llm_teaser.py, backend/tests/adapters/test_llm_teaser.py

## Acceptance
Run `pytest backend/tests/adapters/test_llm_teaser.py -q` and verify all tests pass; `len(teaser_preview) < len(teaser_full)`.
