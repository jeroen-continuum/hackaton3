# 15 — pipeline-wiring

**Milestone:** M3  **Depends on:** 07-application-services, 14-signal-extractors

## Goal
Implement the full RunPipeline.run() orchestration: load pond → filter → enrich → signal extraction → scoring → persist → rank.

## TDD Steps
1. **Red:** Write test in `backend/tests/integration/test_pipeline_e2e.py` calling pipeline.run(). Assert pipeline stages execute and persist results. Confirm assertion failure.
2. **Green:** Implement RunPipeline.run() calling in sequence: CompanySource.load_pond() → FilterPolicy.evaluate() → enrichment (FinancialsProvider, VacancyProvider, TechProvider, ConnectionProvider) → signal extraction → ScoringStrategy.score() → CompanyRepository.save_score() → ranking. Persist stage transitions to DB. Return ranked list.
3. **Refactor:** Add logging at each stage, error recovery, persist stage completion metadata.

## Files
- **Modified:** backend/app/application/pipeline.py (implement run() method)

## Acceptance
Run `python -m app.db.seed && python -m app.pipeline.run` and verify ranked Rolling 10 is printed.
