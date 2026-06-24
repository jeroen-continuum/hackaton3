import pytest
from unittest.mock import patch
from app.adapters.outreach.llm_outreach import LlmOutreachGenerator
from app.domain.models import CompanyProfile
from app.domain.ports import OutreachGenerator

SAMPLE_CASES = [
    {
        "title": "AI at bank",
        "summary": "Cut decisions by 80%.",
        "impact_metric": "-80% time",
    }
]


@pytest.fixture
def generator():
    return LlmOutreachGenerator()


@pytest.fixture
def company():
    return CompanyProfile(
        enterprise_number="0001",
        name="Acme NV",
        sector="financial_services",
    )


def test_llm_generator_satisfies_protocol(generator):
    assert isinstance(generator, OutreachGenerator)


def test_email_returns_subject_and_body(generator, company):
    with patch("app.adapters.outreach.llm_outreach.complete", return_value="Email body text"):
        result = generator.email(company, SAMPLE_CASES)
    assert result["subject"] == "De nieuwe lead voor Acme NV"
    assert result["body"] == "Email body text"


def test_email_subject_contains_company_name(generator, company):
    with patch("app.adapters.outreach.llm_outreach.complete", return_value="body"):
        result = generator.email(company, SAMPLE_CASES)
    assert "Acme NV" in result["subject"]


def test_teaser_returns_title_preview_full(generator, company):
    full_text = "A" * 1200  # longer than 800 chars preview cutoff
    with patch("app.adapters.outreach.llm_outreach.complete", return_value=full_text):
        result = generator.teaser(company, SAMPLE_CASES)
    assert "title" in result
    assert "preview" in result
    assert "full" in result
    assert result["full"] == full_text
    assert result["preview"] == full_text[:800]


def test_teaser_preview_is_truncated_to_800_chars(generator, company):
    full_text = "X" * 1200
    with patch("app.adapters.outreach.llm_outreach.complete", return_value=full_text):
        result = generator.teaser(company, SAMPLE_CASES)
    assert len(result["preview"]) == 800
    assert len(result["full"]) == 1200
