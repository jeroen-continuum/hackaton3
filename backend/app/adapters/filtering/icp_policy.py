"""ICP filter policy adapter — implements FilterPolicy Protocol.

Delegates to the pure predicates in pipeline/filter.py, translating between
domain value objects and the legacy SQLModel entities.
"""
from app.domain.models import CompanyProfile, Financials, Decision
from app.pipeline import filter as _flt
from app.models.entities import Company as _Company, FinancialData as _FinData


class IcpFilterPolicy:
    """ICP filtering: size (100-500 FTE), EBITDA headroom, NACE exclusions."""

    def evaluate(self, profile: CompanyProfile, financials: Financials | None) -> Decision:
        # Build legacy Company for is_excluded check
        legacy_company = _Company(
            enterprise_number=profile.enterprise_number,
            name=profile.name,
            nace_code=profile.nace_code,
        )
        excluded, reason = _flt.is_excluded(legacy_company)
        if excluded:
            return Decision(passes=False, reason=reason)

        if financials is None:
            return Decision(passes=False, reason="no financial data")

        # Build legacy FinancialData for size + financial checks
        legacy_fin = _FinData(
            company_id=0,
            employees=financials.employees,
            ebitda=financials.ebitda,
        )
        if not _flt.passes_size(legacy_fin):
            return Decision(passes=False, reason="employee count out of range")
        if not _flt.passes_financial_fit(legacy_fin):
            return Decision(passes=False, reason="insufficient EBITDA headroom")

        return Decision(passes=True)
