# 17 — solution-cases

**Milestone:** M4  **Depends on:** 06-repository-port

## Goal
Populate the database with WiiPlus SolutionCases (success stories) grouped by sector, and expose a repository to fetch them.

## TDD Steps
1. **Red:** Create `backend/app/domain/models.py:SolutionCase` dataclass. Update `backend/app/db/seed.py` to populate ≥2 cases per focus sector. Write test importing SolutionCaseRepository and calling `by_sector("Finance")`. Confirm ImportError.
2. **Green:** Implement SolutionCaseRepository with `by_sector(sector)` method. Populate seed.py with representative cases (Finance, Professional Services, Industry, Social Secretariats). Run test. Confirm ≥1 case returned per sector.
3. **Refactor:** Add detailed case narratives, sector categorization validation, caching if performance needed.

## Files
- **Created:** backend/app/adapters/persistence/solution_case_repo.py, backend/tests/adapters/test_solution_case_repo.py
- **Modified:** backend/app/domain/models.py (add SolutionCase), backend/app/db/seed.py

## Acceptance
Run `python -m app.db.seed` exits 0; `SolutionCaseRepository.by_sector("Finance")` returns ≥1 case.
