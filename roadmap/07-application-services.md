# 07 — application-services

**Milestone:** M1  **Depends on:** 03-ports, 06-repository-port

## Goal
Create application-layer services (RunPipeline, Scorer, GenerateOutreach) that depend only on domain ports, not concrete adapters.

## TDD Steps
1. **Red:** Create `backend/app/application/pipeline.py`, `scoring.py`, `outreach.py`. Write unit tests in `backend/tests/unit/test_pipeline.py` importing RunPipeline and calling `run()` with injected fakes. Confirm ImportError or assertion failure.
2. **Green:** Implement RunPipeline (injecting CompanySource, FinancialsProvider, FilterPolicy, VacancyProvider, TechProvider, ConnectionProvider, ScoringStrategy, CompanyRepository), Scorer service, GenerateOutreach service. All depend only on protocols. Write minimal implementations to pass tests.
3. **Refactor:** Add error handling, logging, and comprehensive unit tests using fake adapters from conftest.

## Files
- **Created:** backend/app/application/pipeline.py, backend/app/application/scoring.py, backend/app/application/outreach.py, backend/tests/unit/test_pipeline.py

## Acceptance
Run `pytest backend/tests/unit/ -q` and verify all green.
