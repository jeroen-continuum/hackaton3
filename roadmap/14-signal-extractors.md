# 14 — signal-extractors

**Milestone:** M3  **Depends on:** 02-domain-models

## Goal
Implement pure, unit-testable signal extraction functions converting raw enrichment data into normalized 0-1 scoring dimensions.

## TDD Steps
1. **Red:** Create `backend/app/application/signals.py` with function stubs. Create `backend/tests/unit/test_signals.py` with tests importing buyer_intent_signal, impact_potential_signal, etc. Assert they return floats 0-1. Confirm ImportError.
2. **Green:** Implement pure functions: `buyer_intent_signal(vacancies)`, `impact_potential_signal(tech, financials)`, `financial_fit_signal(financials)`, `sector_fit_signal(company)`, `warm_connection_signal(connections)`. Each returns 0.0-1.0. Pass all tests.
3. **Refactor:** Add boundary tests (edge cases), docstrings explaining calculation logic, optimize for readability.

## Files
- **Created:** backend/app/application/signals.py, backend/tests/unit/test_signals.py

## Acceptance
Run `pytest backend/tests/unit/test_signals.py -q` and verify all tests pass.
