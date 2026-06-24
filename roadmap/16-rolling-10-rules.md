# 16 — rolling-10-rules

**Milestone:** M3  **Depends on:** 06-repository-port, 15-pipeline-wiring

## Goal
Implement Rolling 10 business logic: get top-10 non-contacted companies and mark contacted to trigger re-ranking.

## TDD Steps
1. **Red:** Create `backend/app/application/rolling10.py` with function stubs. Write test in `backend/tests/unit/test_rolling10.py` calling `get_rolling10(repo)` and `mark_contacted(repo, company_id)`. Assert top 10 companies are returned and contacted flag updates. Confirm assertion failure.
2. **Green:** Implement `get_rolling10(repo)` returning top-10 non-contacted companies ordered by score descending. Implement `mark_contacted(repo, company_id)` setting contacted=True and re-ranking. Pass all tests.
3. **Refactor:** Add edge cases (fewer than 10 companies, already-contacted handling), docstrings, performance optimization.

## Files
- **Created:** backend/app/application/rolling10.py, backend/tests/unit/test_rolling10.py

## Acceptance
Run `pytest backend/tests/unit/test_rolling10.py -q` and verify all tests pass.
