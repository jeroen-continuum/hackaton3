# 21 — outreach-api

**Milestone:** M5  **Depends on:** 18-fomo-email, 19-gated-teaser, 16-rolling-10-rules

## Goal
Implement outreach API endpoints: fetch email/teaser, perform ephemeral contact lookup, and mark companies as contacted.

## TDD Steps
1. **Red:** Write test in `backend/tests/integration/test_api_outreach.py` calling `GET /companies/{id}/outreach`, `POST /companies/{id}/contact-lookup`, `POST /scoring/{id}/contacted`. Assert correct responses and no DB side effects for contact-lookup. Confirm ImportError or assertion failures.
2. **Green:** Implement three endpoints: (1) GET returns email + teaser for company. (2) POST contact-lookup calls ContactProvider in-memory, returns personas list, does NOT write to DB. (3) POST contacted calls rolling10.mark_contacted(repo, id). Return updated Rolling 10 list.
3. **Refactor:** Add input validation, error handling, ensure contact-lookup is ephemeral (no persistence).

## Files
- **Created:** backend/app/api/routes/outreach.py, backend/tests/integration/test_api_outreach.py

## Acceptance
Run `pytest backend/tests/ -q` (all green); contact-lookup does not appear in any DB table after call.
