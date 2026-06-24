# 10 — nbb-financials

**Milestone:** M2  **Depends on:** 03-ports, 08-composition-root

## Goal
Implement NbbFinancialsProvider adapter calling the NBB (National Bank of Belgium) Open Data API for financial metrics.

## TDD Steps
1. **Red:** Create `backend/app/adapters/sources/nbb.py` with NbbFinancialsProvider stub. Write test in `backend/tests/adapters/test_nbb.py` using respx to mock one sample NBB response. Assert `financials(enterprise_number)` returns Financials. Confirm ImportError.
2. **Green:** Implement NbbFinancialsProvider.financials() calling NBB API by enterprise_number. Parse employees and EBITDA from XBRL/JSON response. Handle missing data gracefully. Return Financials(employees, revenue, ebitda, fiscal_year). Run test. Confirm pass.
3. **Refactor:** Add timeout handling, error logging, response validation.

## Files
- **Created:** backend/app/adapters/sources/nbb.py, backend/tests/adapters/test_nbb.py

## Acceptance
Run `pytest backend/tests/adapters/test_nbb.py -q` and verify all tests pass.
