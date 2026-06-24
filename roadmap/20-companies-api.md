# 20 — companies-api

**Milestone:** M5  **Depends on:** 08-composition-root, 16-rolling-10-rules

## Goal
Refactor the companies API routes to use hexagonal application services instead of inline SQLModel queries.

## TDD Steps
1. **Red:** Write test in `backend/tests/integration/test_api_companies.py` calling `GET /companies/top10`. Assert response matches CompanyListItem shape. Confirm mismatch or failure.
2. **Green:** Refactor `backend/app/api/routes/companies.py` to call `build_container()` application services. Query services return domains models; serialize to JSON. Response shapes: CompanyListItem (id, name, sector, rank, score), CompanyDetail (full profile + signals breakdown). Ensure compatibility with `frontend/src/app/core/models.ts`.
3. **Refactor:** Add error handling, pagination, response caching if needed.

## Files
- **Modified:** backend/app/api/routes/companies.py

## Acceptance
Run `pytest backend/tests/ -q` (all green); manual `GET /companies/top10` returns correct JSON shape with 10 companies.
