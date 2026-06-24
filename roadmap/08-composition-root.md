# 08 — composition-root

**Milestone:** M1  **Depends on:** 04-scoring-strategy-port, 05-filter-policy-port, 06-repository-port, 07-application-services

## Goal
Create the composition root (dependency injection container) wiring concrete adapters from settings into application services.

## TDD Steps
1. **Red:** Create `backend/app/composition.py` with stub `build_container()`. Write test in `backend/tests/test_composition.py` importing build_container and asserting it returns a container with pipeline. Confirm assertion failure.
2. **Green:** Implement `build_container()` returning a dict/namespace with concrete adapter instances (KboSource, NbbFinancialsProvider, IcpFilterPolicy, WeightedScoringStrategy, SqlModelCompanyRepository, etc.) wired from settings. Inject into RunPipeline service.
3. **Refactor:** Refactor `backend/app/pipeline/run.py` and API routes to import from composition instead of inline instantiation.

## Files
- **Created:** backend/app/composition.py, backend/tests/test_composition.py
- **Modified:** backend/app/pipeline/run.py, backend/app/api/routes/*.py

## Acceptance
Run `pytest backend/tests/ -q` (all green) and `python -m app.pipeline.run` (no import crash).
