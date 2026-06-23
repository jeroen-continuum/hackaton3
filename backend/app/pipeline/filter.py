"""Step 2 — Filter: NBB financials. Keep 100-500 FTE + EBITDA headroom; exclude.

Hard rules live in core/constants.py so they can be tuned centrally.
"""
from app.core import constants
from app.models import Company, FinancialData


def passes_size(fin: FinancialData) -> bool:
    return (
        fin.employees is not None
        and constants.MIN_EMPLOYEES <= fin.employees <= constants.MAX_EMPLOYEES
    )


def passes_financial_fit(fin: FinancialData) -> bool:
    """Project value must be < MAX_PROJECT_TO_EBITDA_RATIO of annual EBITDA."""
    if not fin.ebitda or fin.ebitda <= 0:
        return False
    headroom = fin.ebitda * constants.MAX_PROJECT_TO_EBITDA_RATIO
    return headroom >= constants.PROJECT_VALUE_MIN


def is_excluded(company: Company) -> tuple[bool, str | None]:
    nace = company.nace_code or ""
    for prefix in constants.EXCLUDED_NACE_PREFIXES:
        if nace.startswith(prefix):
            return True, f"excluded NACE prefix {prefix}"
    return False, None
