# 03 — ports

**Milestone:** M0  **Depends on:** 02-domain-models

## Goal
Define all domain port (Protocol) interfaces that adapters and services will implement.

## TDD Steps
1. **Red:** Create `backend/app/domain/ports.py` with empty Protocol stubs. Create test importing CompanySource. Run. Confirm ImportError.
2. **Green:** Implement `typing.Protocol` interfaces: CompanySource (load_pond), FinancialsProvider (financials), VacancyProvider (vacancies), TechProvider (tech_stack), ContactProvider (contacts), ConnectionProvider (warm_connections), ScoringStrategy (score), FilterPolicy (evaluate), OutreachGenerator (email, teaser), CompanyRepository (save_score, load, by_id). Update `backend/tests/conftest.py` fakes to explicitly implement each Protocol. Run `pytest backend/tests/ -q`. Confirm pass.
3. **Refactor:** Add docstrings to each Protocol method, verify mypy compliance.

## Files
- **Created:** backend/app/domain/ports.py
- **Modified:** backend/tests/conftest.py (update fakes to implement Protocols explicitly)

## Acceptance
Run `pytest backend/tests/ -q` (all tests pass) and `mypy backend/app/domain/` (clean output).
