"""Tests for WappalyzerTechProvider using respx HTTP mocking."""
import pytest
import respx
import httpx

from app.adapters.sources.wappalyzer import WappalyzerTechProvider, _compute_legacy_score
from app.domain.ports import TechProvider

SAMPLE_RESPONSE = [
    {
        "technologies": [
            {"name": "SAP", "categories": [{"name": "ERP"}]},
            {"name": "jQuery", "categories": [{"name": "JavaScript libraries"}]},
            {"name": "React", "categories": [{"name": "JavaScript frameworks"}]},
        ]
    }
]


@pytest.fixture
def provider():
    return WappalyzerTechProvider()


def test_wappalyzer_provider_satisfies_protocol(provider):
    assert isinstance(provider, TechProvider)


@respx.mock
def test_fetch_returns_tech_dict_on_success(provider):
    respx.get(url__regex=r"api\.wappalyzer\.com.*").mock(
        return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
    )
    result = provider.fetch("example.com")
    assert result is not None
    assert "technologies" in result
    assert isinstance(result["technologies"], list)
    assert len(result["technologies"]) == 3
    assert "legacy_score" in result
    assert result["legacy_score"] > 0


@respx.mock
def test_fetch_returns_none_on_404(provider):
    respx.get(url__regex=r"api\.wappalyzer\.com.*").mock(
        return_value=httpx.Response(404)
    )
    assert provider.fetch("notfound.com") is None


@respx.mock
def test_fetch_returns_none_on_empty_technologies(provider):
    respx.get(url__regex=r"api\.wappalyzer\.com.*").mock(
        return_value=httpx.Response(200, json=[{"technologies": []}])
    )
    assert provider.fetch("empty.com") is None


def test_compute_legacy_score_sap_and_jquery():
    """SAP + jQuery = 2 legacy keyword hits (no ERP category) → score = 2/3 ≈ 0.667."""
    technologies = [
        {"name": "SAP", "categories": []},
        {"name": "jQuery", "categories": []},
    ]
    score = _compute_legacy_score(technologies)
    # "sap" in names → hit; "jquery" in names → hit; 2 hits → min(1.0, 2/3) ≈ 0.667
    assert score == pytest.approx(2 / 3)
