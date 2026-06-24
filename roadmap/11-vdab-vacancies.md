# 11 — vdab-vacancies

**Milestone:** M2  **Depends on:** 03-ports, 08-composition-root

## Goal
Implement VdabVacancyProvider adapter calling the VDAB (Flemish Employment Service) API to identify IT talent demand.

## TDD Steps
1. **Red:** Create `backend/app/adapters/sources/vdab.py` with VdabVacancyProvider stub. Write test in `backend/tests/adapters/test_vdab.py` using respx to mock one VDAB response. Assert `vacancies(sector)` returns vacancy list with is_it_role field. Confirm ImportError.
2. **Green:** Implement VdabVacancyProvider.vacancies() calling VDAB API by sector. Flag IT roles (is_it_role) based on job title/code patterns. Return list of vacancy objects. Run test. Confirm pass.
3. **Refactor:** Add IT role detection heuristics, error handling, pagination if needed.

## Files
- **Created:** backend/app/adapters/sources/vdab.py, backend/tests/adapters/test_vdab.py

## Acceptance
Run `pytest backend/tests/adapters/test_vdab.py -q` and verify all tests pass.
