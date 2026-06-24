# 06 — repository-port

**Milestone:** M1  **Depends on:** 03-ports

## Goal
Implement the CompanyRepository port over SQLModel entities, with tests using in-memory SQLite.

## TDD Steps
1. **Red:** Create `backend/app/adapters/persistence/__init__.py` and `company_repo.py`. Write test in `backend/tests/adapters/test_company_repo.py` importing SqlModelCompanyRepository and calling `save_score(company, result)`. Confirm ImportError.
2. **Green:** Implement SqlModelCompanyRepository implementing CompanyRepository protocol with save_score, load, by_id methods. Create in-memory SQLite test database. Write minimal adapter to pass test.
3. **Refactor:** Add error handling, docstrings, and comprehensive CRUD tests.

## Files
- **Created:** backend/app/adapters/persistence/__init__.py, backend/app/adapters/persistence/company_repo.py, backend/tests/adapters/test_company_repo.py

## Acceptance
Run `pytest backend/tests/ -q` and verify all tests pass.
