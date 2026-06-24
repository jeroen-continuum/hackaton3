# 26 — e2e-smoke

**Milestone:** M7  **Depends on:** 25-seed-and-docker

## Goal
Run full end-to-end pipeline test and confirm all frontend UX flows are visible and functional.

## TDD Steps
1. **Red:** Create `backend/tests/integration/test_pipeline_e2e.py` running full pipeline (pond → top10) against in-memory SQLite. Call all adapters, verify results persisted. Run `cd backend && pytest -q`. Confirm any failures.
2. **Green:** Implement E2E test with fake adapters. Call RunPipeline.run(), verify stage completion, confirm 10 ranked companies persisted with non-null scores + breakdown. Run test. Confirm pass.
3. **Refactor:** Add scenario variations (fewer companies, no vacancies, etc.), improve assertions.

## Files
- **Created:** backend/tests/integration/test_pipeline_e2e.py

## Acceptance
Run `cd backend && pytest -q` fully green. Manual frontend walkthrough: Rolling 10 visible, heatmap visible, outreach editor visible, send-gate visible. Contact-lookup populates personas; email/teaser generate without errors.
