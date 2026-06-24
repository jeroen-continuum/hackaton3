# 09 — kbo-source

**Milestone:** M2  **Depends on:** 03-ports, 08-composition-root

## Goal
Implement KboSource adapter reading Belgian company data from KBO CSV/XML dumps, filtering by region and NACE code.

## TDD Steps
1. **Red:** Create `backend/app/adapters/sources/kbo.py` with KboSource stub. Write test in `backend/tests/adapters/test_kbo_source.py` with a 5-row sample CSV fixture. Assert `load_pond()` returns companies. Confirm ImportError.
2. **Green:** Implement KboSource.load_pond() reading CSV/XML from `settings.data_dir/kbo/`. Filter active companies in `REGIONS` with NACE starting with `FOCUS_NACE_PREFIXES`. Exclude `EXCLUDED_NACE_PREFIXES`. Return list of CompanyProfile. Run test. Confirm pass.
3. **Refactor:** Add error handling for malformed CSV, add docstrings, optimize filtering logic.

## Files
- **Created:** backend/app/adapters/sources/kbo.py, backend/tests/adapters/test_kbo_source.py, backend/tests/fixtures/kbo_sample.csv

## Acceptance
Run `pytest backend/tests/adapters/test_kbo_source.py -q` and verify all tests pass.
