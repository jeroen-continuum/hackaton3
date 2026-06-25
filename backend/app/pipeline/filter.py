"""Step 2 — Filter: NBB financials. Keep 100-500 FTE + EBITDA headroom; exclude.

Thresholds come from an IcpFilter (defaulting to the requirement values in
core/constants.py) so they can be tuned per request without code changes.
"""
from app.domain.filters import IcpFilter
from app.models import Company, FinancialData


def passes_size(fin: FinancialData, icp: IcpFilter | None = None) -> bool:
    icp = icp or IcpFilter.default()
    if not icp.apply_size:
        return True
    return (
        fin.employees is not None
        and icp.min_employees <= fin.employees <= icp.max_employees
    )


def passes_financial_fit(fin: FinancialData, icp: IcpFilter | None = None) -> bool:
    """Project value must be < max_project_to_ebitda_ratio of annual EBITDA."""
    icp = icp or IcpFilter.default()
    if not icp.apply_financial:
        return True
    if not fin.ebitda or fin.ebitda <= 0:
        return False
    headroom = fin.ebitda * icp.max_project_to_ebitda_ratio
    return headroom >= icp.project_value_min


def is_excluded(company: Company, icp: IcpFilter | None = None) -> tuple[bool, str | None]:
    icp = icp or IcpFilter.default()
    nace = company.nace_code or ""
    for prefix in icp.nace_exclude_prefixes:
        if nace.startswith(prefix):
            return True, f"excluded NACE prefix {prefix}"
    return False, None
