# 05 — filter-policy-port

**Milestone:** M1  **Depends on:** 03-ports

## Goal
Wrap the existing filter pipeline logic behind the FilterPolicy protocol, creating a hexagonal adapter.

## TDD Steps
1. **Red:** Create `backend/app/adapters/filtering/__init__.py` and `icp_policy.py`. Write test importing IcpFilterPolicy and calling `evaluate(company)`. Confirm ImportError.
2. **Green:** Implement IcpFilterPolicy wrapping `app.pipeline.filter` predicates behind the FilterPolicy protocol. Write minimal adapter to pass test.
3. **Refactor:** Migrate existing filter tests to use the adapter; verify all tests pass. DO NOT delete pipeline/filter.py.

## Files
- **Created:** backend/app/adapters/filtering/__init__.py, backend/app/adapters/filtering/icp_policy.py
- **Modified:** backend/tests/adapters/test_filtering.py (migrate existing tests to use adapter)

## Acceptance
Run `pytest backend/tests/ -q` and verify no test regressions (all green).
