# 24 — outreach-ui

**Milestone:** M6  **Depends on:** 21-outreach-api

## Goal
Build the outreach UI with editable draft email, gated teaser preview, and send confirmation gate.

## TDD Steps
1. **Red:** Create `frontend/src/app/features/outreach/` component. Write Jasmine test asserting send-gate button is visible. Confirm assertion failure.
2. **Green:** Implement component with sections: (1) Editable AI draft textarea (email body). (2) "↺ Reset to AI draft" button. (3) Gated teaser preview section (first 1.5 pages visible). (4) "Full report unlocks on reply or expert call" gate message. (5) "Mark as sent · human verifies & sends" button. (6) Contact-lookup trigger (calls endpoint, shows personas). Pass test.
3. **Refactor:** Add save draft functionality, improve UX flow, add analytics.

## Files
- **Created:** frontend/src/app/features/outreach/outreach-editor.component.ts, frontend/src/app/features/outreach/outreach-editor.component.html, frontend/src/app/features/outreach/outreach-editor.component.spec.ts

## Acceptance
Run `npx ng build` succeeds; component test verifies send-gate button is visible and clickable.
