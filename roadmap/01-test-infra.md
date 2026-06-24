# 01 — test-infra

**Milestone:** M0  **Depends on:** none

## Goal
Set up pytest with markers, add respx HTTP mocking library, and create fake adapters implementing all domain ports.

## TDD Steps
1. **Red:** Add `respx>=0.22` to `requirements.txt`. Create `backend/tests/conftest.py`. Write test importing FakeCompanySource and attempting to call `load_pond()`. Confirm ImportError.
2. **Green:** Implement fake adapters (FakeCompanySource, FakeFinancialsProvider, FakeVacancyProvider, FakeTechProvider, FakeConnectionProvider, FakeScoringStrategy, FakeFilterPolicy) in conftest.py satisfying each domain port protocol signature. Run test. Confirm pass.
3. **Refactor:** Organize fakes into separate classes with consistent naming and docstrings.

## Files
- **Created:** backend/tests/conftest.py
- **Modified:** requirements.txt (add respx>=0.22), pytest.ini (add markers: unit, adapter)

## Acceptance
Run `pytest backend/tests/ -m unit -q` and verify all tests pass.
