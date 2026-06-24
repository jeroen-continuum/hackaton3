# 12 — wappalyzer-tech

**Milestone:** M2  **Depends on:** 03-ports, 08-composition-root

## Goal
Implement WappalyzerTechProvider adapter calling Wappalyzer API to assess company tech stack legacy score.

## TDD Steps
1. **Red:** Create `backend/app/adapters/sources/wappalyzer.py` with WappalyzerTechProvider stub. Write test in `backend/tests/adapters/test_wappalyzer.py` using respx to mock one Wappalyzer response. Assert `tech_stack(domain)` returns tech object with legacy_score. Confirm ImportError.
2. **Green:** Implement WappalyzerTechProvider.tech_stack() calling Wappalyzer API by domain. Parse technologies and compute `legacy_score` (higher = more legacy = higher AI impact potential). Return tech object with legacy_score. Run test. Confirm pass.
3. **Refactor:** Add technology classification, error handling for invalid domains.

## Files
- **Created:** backend/app/adapters/sources/wappalyzer.py, backend/tests/adapters/test_wappalyzer.py

## Acceptance
Run `pytest backend/tests/adapters/test_wappalyzer.py -q` and verify all tests pass.
