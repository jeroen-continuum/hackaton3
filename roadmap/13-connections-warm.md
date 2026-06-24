# 13 — connections-warm

**Milestone:** M2  **Depends on:** 03-ports, 08-composition-root

## Goal
Implement CsvConnectionProvider adapter reading warm (already-known) connections from a CSV file to boost company scores.

## TDD Steps
1. **Red:** Create `backend/app/adapters/sources/connections.py` with CsvConnectionProvider stub. Write test in `backend/tests/adapters/test_connections.py` with a 3-row CSV fixture containing enterprise_number, connection_name, degree. Assert `warm_connections(enterprise_number)` returns list of connections. Confirm ImportError.
2. **Green:** Implement CsvConnectionProvider.warm_connections() reading from `settings.data_dir/connections/warm_connections.csv`. Parse columns: enterprise_number, connection_name, degree. Return list of connection objects. Run test. Confirm pass.
3. **Refactor:** Add CSV validation, error handling, degree interpretation.

## Files
- **Created:** backend/app/adapters/sources/connections.py, backend/tests/adapters/test_connections.py, backend/tests/fixtures/warm_connections.csv

## Acceptance
Run `pytest backend/tests/adapters/test_connections.py -q` and verify all tests pass.
