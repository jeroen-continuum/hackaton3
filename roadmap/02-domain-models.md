# 02 — domain-models

**Milestone:** M0  **Depends on:** none

## Goal
Create pure dataclasses representing the core domain: company profiles, financial metrics, scoring signals, and decision results.

## TDD Steps
1. **Red:** Create `backend/app/domain/models.py` with empty class stubs. Create `backend/tests/unit/test_domain_models.py` with a test importing CompanyProfile and asserting it can be instantiated. Run. Confirm ImportError.
2. **Green:** Implement dataclasses: `CompanyProfile(enterprise_number, name, region, nace_code, sector, website)`, `Financials(employees, revenue, ebitda, fiscal_year)`, `Signals(buyer_intent, impact_potential, financial_fit, sector_fit, warm_connection)` with all signal floats 0-1, `ScoreResult(total, breakdown)`, `Decision(passes, reason)`. Run test. Confirm pass.
3. **Refactor:** Add field validators for signal bounds (0.0-1.0), add docstrings, ensure immutability where appropriate.

## Files
- **Created:** backend/app/domain/models.py, backend/tests/unit/test_domain_models.py

## Acceptance
Run `pytest backend/tests/unit/test_domain_models.py -q` and verify all tests pass.
