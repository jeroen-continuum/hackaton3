# 04 — scoring-strategy-port

**Milestone:** M1  **Depends on:** 03-ports

## Goal
Wrap the existing scoring pipeline logic behind the ScoringStrategy protocol, creating a hexagonal adapter.

## TDD Steps
1. **Red:** Create `backend/app/adapters/scoring/__init__.py` and `weighted.py`. Write test importing WeightedScoringStrategy and calling `score(signals)`. Confirm ImportError.
2. **Green:** Implement WeightedScoringStrategy wrapping `app.pipeline.score.compute_score` and `rank_scores` behind the ScoringStrategy protocol. Write minimal adapter to pass test.
3. **Refactor:** Migrate existing scoring tests to use the adapter; verify all tests pass. DO NOT delete pipeline/score.py.

## Files
- **Created:** backend/app/adapters/scoring/__init__.py, backend/app/adapters/scoring/weighted.py
- **Modified:** backend/tests/adapters/test_scoring.py (migrate existing tests to use adapter)

## Acceptance
Run `pytest backend/tests/ -q` and verify no test regressions (all green).
