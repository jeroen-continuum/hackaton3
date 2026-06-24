# 25 — seed-and-docker

**Milestone:** M7  **Depends on:** 15-pipeline-wiring, 24-outreach-ui

## Goal
Refresh the seed script to populate data using hexagonal models and verify docker compose end-to-end workflow.

## TDD Steps
1. **Red:** Update `backend/app/db/seed.py` to use new domain models (CompanyProfile, Financials, Signals, etc.) and composition-root adapters. Run `docker compose up --build`. Confirm seed fails or data is malformed.
2. **Green:** Refactor seed to load sample KBO companies, fetch financials, assess vacancies/tech/connections, score, persist. Verify populated Rolling 10. Run `docker compose exec backend python -m app.db.seed`. Confirm exit 0 and `/companies/top10` returns 10 companies with non-null scores/breakdown.
3. **Refactor:** Add progress logging, optimize seed performance, add data validation.

## Files
- **Modified:** backend/app/db/seed.py, docker-compose.yml

## Acceptance
Run `docker compose up --build && docker compose exec backend python -m app.db.seed` exits 0; `/companies/top10` returns 10 companies with non-null breakdown.
