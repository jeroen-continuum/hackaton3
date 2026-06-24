"""Tests for VdabVacancyProvider using respx HTTP mocking."""
import pytest
import respx
import httpx

from app.adapters.sources.vdab import VdabVacancyProvider, _is_it_role
from app.domain.ports import VacancyProvider

SAMPLE_RESPONSE = {
    "results": [
        {"title": "Senior Software Engineer", "redirect_url": "https://example.com/1"},
        {"title": "Accountant", "redirect_url": "https://example.com/2"},
        {"title": "SAP Consultant", "redirect_url": "https://example.com/3"},
    ]
}


@pytest.fixture
def provider():
    return VdabVacancyProvider()


def test_vdab_provider_satisfies_protocol(provider):
    assert isinstance(provider, VacancyProvider)


@respx.mock
def test_fetch_returns_vacancies_on_success(provider):
    respx.get(url__regex=r"api\.adzuna\.com.*").mock(
        return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
    )
    result = provider.fetch("Acme Corp")
    assert len(result) == 3
    assert result[0]["title"] == "Senior Software Engineer"
    assert result[0]["is_it_role"] is True
    assert result[1]["is_it_role"] is False   # Accountant
    assert result[2]["is_it_role"] is True    # SAP Consultant


@respx.mock
def test_fetch_returns_empty_list_on_404(provider):
    respx.get(url__regex=r"api\.adzuna\.com.*").mock(
        return_value=httpx.Response(404)
    )
    assert provider.fetch("Unknown Corp") == []


@respx.mock
def test_fetch_returns_empty_list_on_empty_results(provider):
    respx.get(url__regex=r"api\.adzuna\.com.*").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    assert provider.fetch("Empty Corp") == []


def test_is_it_role_detects_keywords():
    assert _is_it_role("Cloud Platform Engineer")
    assert _is_it_role("SAP ERP Consultant")
    assert not _is_it_role("Office Manager")
    assert not _is_it_role("Sales Representative")
