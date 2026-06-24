"""Tests for NbbFinancialsProvider using respx HTTP mocking."""
import pytest
import respx
import httpx

from app.adapters.sources.nbb import NbbFinancialsProvider
from app.domain.models import Financials
from app.domain.ports import FinancialsProvider

SAMPLE_RESPONSE = {
    "annualAccounts": [
        {
            "fiscalYear": 2023,
            "rubrics": [
                {"code": "9087", "value": 245},
                {"code": "9901", "value": 4500000.0},
            ]
        }
    ]
}


@pytest.fixture
def provider(tmp_path):
    p = NbbFinancialsProvider()
    p._data_dir = str(tmp_path)
    return p


def test_nbb_provider_satisfies_protocol(provider):
    assert isinstance(provider, FinancialsProvider)


@respx.mock
def test_fetch_returns_financials_on_success(provider):
    respx.get(url__regex=r"api\.cbe\.be.*0123456789.*").mock(
        return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
    )
    result = provider.fetch("0123456789")
    assert isinstance(result, Financials)
    assert result.employees == 245
    assert result.ebitda == pytest.approx(4_500_000.0)
    assert result.fiscal_year == 2023


@respx.mock
def test_fetch_returns_none_on_404(provider):
    respx.get(url__regex=r"api\.cbe\.be.*").mock(
        return_value=httpx.Response(404)
    )
    result = provider.fetch("9999999999")
    assert result is None


@respx.mock
def test_fetch_returns_none_on_empty_rubrics(provider):
    respx.get(url__regex=r"api\.cbe\.be.*").mock(
        return_value=httpx.Response(200, json={"annualAccounts": [{"fiscalYear": 2023, "rubrics": []}]})
    )
    result = provider.fetch("0000000000")
    assert result is None


@respx.mock
def test_fetch_returns_consistent_results(provider):
    respx.get(url__regex=r"api\.cbe\.be.*0123456789.*").mock(
        return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
    )
    result = provider.fetch("0123456789")
    assert result is not None
    assert result.employees == 245
    assert result.ebitda == pytest.approx(4_500_000.0)
