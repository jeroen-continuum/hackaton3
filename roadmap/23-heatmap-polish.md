# 23 — heatmap-polish

**Milestone:** M6  **Depends on:** 14-signal-extractors, 22-dashboard-rolling10

## Goal
Enhance the heatmap visualization to show all five signal dimensions (buyer intent, impact potential, financial fit, sector fit, warm connection) with labels and numeric values.

## TDD Steps
1. **Red:** Write test in `backend/tests/unit/test_signals.py` or new heatmap test asserting heatmap renders 5 bars. Create heatmap component test asserting bars render. Confirm assertion failure.
2. **Green:** Implement heatmap component with 5 bars (one per signal). Each bar: label, visual fill (0-100%), numeric value. Bind to company.signals from detail view. Render all 5 dimensions. Pass test.
3. **Refactor:** Add color coding (green=high, yellow=medium, red=low), tooltips, responsive layout.

## Files
- **Modified:** frontend/src/app/shared/heatmap/ (enhance with 5-bar layout), frontend/src/app/features/company-detail/ (wire heatmap component)

## Acceptance
Run `npx ng build` succeeds; heatmap component test asserts 5 bars render with correct labels and values.
