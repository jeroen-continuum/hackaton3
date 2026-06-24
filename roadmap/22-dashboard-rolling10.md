# 22 — dashboard-rolling10

**Milestone:** M6  **Depends on:** 20-companies-api

## Goal
Update the Angular dashboard to display the Rolling 10 list with visual ranking, company info, and scoring summary.

## TDD Steps
1. **Red:** Create `frontend/src/app/features/dashboard/rolling10-list.component.ts` with test. Write Jasmine test importing component and asserting it renders 10 rows. Confirm assertion failure.
2. **Green:** Implement component: bind to `ApiService.top10()`. Render list with columns: rank badge, company name, sector chip, score bar, contact-status indicator. Loop over 10 companies. Pass test.
3. **Refactor:** Add routing to detail view, add status badges (contacted/pending), improve styling.

## Files
- **Created:** frontend/src/app/features/dashboard/rolling10-list.component.ts, frontend/src/app/features/dashboard/rolling10-list.component.html, frontend/src/app/features/dashboard/rolling10-list.component.spec.ts

## Acceptance
Run `npx ng build --configuration production` succeeds; component renders 10 rows in test.
