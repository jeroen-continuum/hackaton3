"""Tests for IcpFilterPolicy via FilterPolicy port."""
import pytest
from app.domain.models import CompanyProfile, Financials, Decision
from app.domain.ports import FilterPolicy
from app.adapters.filtering.icp_policy import IcpFilterPolicy


@pytest.fixture
def policy():
    return IcpFilterPolicy()


@pytest.fixture
def valid_profile():
    return CompanyProfile(enterprise_number="0123456789", name="Acme NV", nace_code="6419")


@pytest.fixture
def valid_financials():
    return Financials(employees=250, ebitda=9_500_000)


def test_icp_policy_satisfies_protocol(policy):
    assert isinstance(policy, FilterPolicy)


def test_passes_valid_company(policy, valid_profile, valid_financials):
    result = policy.evaluate(valid_profile, valid_financials)
    assert result.passes is True
    assert result.reason is None


def test_fails_excluded_nace(policy, valid_financials):
    profile = CompanyProfile(enterprise_number="1", name="Hospital", nace_code="8610")
    result = policy.evaluate(profile, valid_financials)
    assert result.passes is False
    assert "86" in result.reason


def test_missing_financials_does_not_disqualify(policy, valid_profile):
    # No financial data available -> unknown, not a failure. The size/financial
    # sub-filters are simply not evaluated; the company passes on NACE/region.
    result = policy.evaluate(valid_profile, None)
    assert result.passes is True
    assert result.reason is None


def test_excluded_nace_fails_even_without_financials(policy):
    profile = CompanyProfile(enterprise_number="1", name="Hospital", nace_code="8610")
    result = policy.evaluate(profile, None)
    assert result.passes is False
    assert "86" in result.reason


def test_fails_too_few_employees(policy, valid_profile):
    fin = Financials(employees=20, ebitda=9_500_000)
    result = policy.evaluate(valid_profile, fin)
    assert result.passes is False


def test_fails_too_many_employees(policy, valid_profile):
    fin = Financials(employees=900, ebitda=9_500_000)
    result = policy.evaluate(valid_profile, fin)
    assert result.passes is False


def test_fails_insufficient_ebitda(policy, valid_profile):
    fin = Financials(employees=250, ebitda=1_000_000)
    result = policy.evaluate(valid_profile, fin)
    assert result.passes is False


def test_returns_decision_type(policy, valid_profile, valid_financials):
    result = policy.evaluate(valid_profile, valid_financials)
    assert isinstance(result, Decision)


# --- adjustable IcpFilter ---
from app.domain.filters import IcpFilter


def test_custom_employee_range(valid_profile):
    policy = IcpFilterPolicy(IcpFilter(min_employees=10, max_employees=50))
    fin = Financials(employees=20, ebitda=9_500_000)
    assert policy.evaluate(valid_profile, fin).passes is True


def test_disable_size_and_financial_passes_without_financials(valid_profile):
    policy = IcpFilterPolicy(IcpFilter(apply_size=False, apply_financial=False))
    assert policy.evaluate(valid_profile, None).passes is True


def test_disable_financial_ignores_low_ebitda(valid_profile):
    policy = IcpFilterPolicy(IcpFilter(apply_financial=False))
    fin = Financials(employees=250, ebitda=1_000)  # tiny EBITDA
    assert policy.evaluate(valid_profile, fin).passes is True


def test_custom_exclusion_prefix():
    policy = IcpFilterPolicy(IcpFilter(nace_exclude_prefixes=["64"]))
    profile = CompanyProfile(enterprise_number="1", name="Bank", nace_code="64190")
    result = policy.evaluate(profile, Financials(employees=250, ebitda=9_500_000))
    assert result.passes is False
    assert "64" in result.reason
