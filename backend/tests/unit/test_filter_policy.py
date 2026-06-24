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


def test_fails_no_financials(policy, valid_profile):
    result = policy.evaluate(valid_profile, None)
    assert result.passes is False
    assert "financial" in result.reason.lower()


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
