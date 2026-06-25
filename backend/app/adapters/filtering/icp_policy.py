"""ICP filter policy adapter — implements FilterPolicy Protocol.

Delegates to the pure predicates in pipeline/filter.py, translating between
domain value objects and the legacy SQLModel entities. The IcpFilter passed in
makes thresholds + exclusions adjustable per request.
"""
from app.domain.filters import IcpFilter
from app.domain.models import CompanyProfile, Financials, Decision
from app.pipeline import filter as _flt
from app.models.entities import Company as _Company, FinancialData as _FinData


class IcpFilterPolicy:
    """ICP filtering: size (default 100-500 FTE), EBITDA headroom, NACE exclusions."""

    def __init__(self, icp: IcpFilter | None = None) -> None:
        self._icp = icp or IcpFilter.default()

    def evaluate(self, profile: CompanyProfile, financials: Financials | None) -> Decision:
        # Build legacy Company for is_excluded check
        legacy_company = _Company(
            enterprise_number=profile.enterprise_number,
            name=profile.name,
            nace_code=profile.nace_code,
        )
        excluded, reason = _flt.is_excluded(legacy_company, self._icp)
        if excluded:
            return Decision(passes=False, reason=reason)

        # Size + financial filters need NBB data. When it's absent: if either
        # data-dependent filter is switched ON, the company can't satisfy it, so
        # it's dropped. If both are OFF, NACE/region already passed and the
        # company stays a candidate.
        if financials is None:
            if self._icp.apply_size or self._icp.apply_financial:
                return Decision(passes=False, reason="no financial data")
            return Decision(passes=True)

        legacy_fin = _FinData(
            company_id=0,
            employees=financials.employees,
            ebitda=financials.ebitda,
        )
        if not _flt.passes_size(legacy_fin, self._icp):
            return Decision(passes=False, reason="employee count out of range")
        if not _flt.passes_financial_fit(legacy_fin, self._icp):
            return Decision(passes=False, reason="insufficient EBITDA headroom")

        return Decision(passes=True)
