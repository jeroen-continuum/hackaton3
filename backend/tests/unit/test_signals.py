import pytest
from app.application.signals import (
    extract_buyer_intent, extract_impact_potential,
    extract_financial_fit, extract_sector_fit,
    extract_warm_connection, build_signals,
)
from app.domain.models import CompanyProfile, Financials, Signals


def test_buyer_intent_fraction_of_it_roles():
    vacancies = [
        {"title": "Dev", "is_it_role": True},
        {"title": "Accountant", "is_it_role": False},
    ]
    assert extract_buyer_intent(vacancies) == pytest.approx(0.5)


def test_buyer_intent_empty_vacancies():
    assert extract_buyer_intent([]) == 0.0


def test_impact_potential_uses_legacy_score():
    assert extract_impact_potential({"legacy_score": 0.7}) == pytest.approx(0.7)


def test_impact_potential_none_tech():
    assert extract_impact_potential(None) == 0.0


def test_financial_fit_passes():
    # EBITDA 9.5M * 10% = 950k >= 150k => passes
    fin = Financials(employees=200, ebitda=9_500_000)
    assert extract_financial_fit(fin) == pytest.approx(1.0)


def test_financial_fit_fails():
    fin = Financials(employees=200, ebitda=1_000_000)
    assert extract_financial_fit(fin) == pytest.approx(0.0)


def test_financial_fit_no_financials():
    assert extract_financial_fit(None) == 0.0


def test_sector_fit_focus_nace():
    # "7010" starts with "70" which is in FOCUS_NACE_PREFIXES
    profile = CompanyProfile(enterprise_number="x", name="X", nace_code="7010")
    assert extract_sector_fit(profile) == pytest.approx(1.0)


def test_sector_fit_non_focus_nace():
    profile = CompanyProfile(enterprise_number="x", name="X", nace_code="4511")
    assert extract_sector_fit(profile) == pytest.approx(0.5)


def test_sector_fit_no_nace():
    profile = CompanyProfile(enterprise_number="x", name="X")
    assert extract_sector_fit(profile) == 0.0


def test_warm_connection_saturates_at_one():
    # Three current employer ties (weight 1.0 each) -> 3/3 = 1.0, capped.
    ties = [{"type": "EMPLOYER", "end_date": None}] * 3
    assert extract_warm_connection(ties) == pytest.approx(1.0)


def test_warm_connection_partial():
    # One current employer tie: weight 1.0 / saturation 3.0.
    assert extract_warm_connection([{"type": "EMPLOYER", "end_date": None}]) == pytest.approx(1 / 3)


def test_warm_connection_employer_beats_personal():
    same_recency = {"end_date": None}
    employer = extract_warm_connection([{**same_recency, "type": "EMPLOYER"}])
    personal = extract_warm_connection([{**same_recency, "type": "PERSONAL"}])
    assert employer > personal


def test_warm_connection_recent_beats_old():
    from datetime import date
    recent = extract_warm_connection([{"type": "CLIENT", "end_date": date.today().isoformat()}])
    old = extract_warm_connection([{"type": "CLIENT", "end_date": "2005-01-01"}])
    assert recent > old


def test_build_signals_returns_signals_object():
    # "7010" starts with "70" which is in FOCUS_NACE_PREFIXES
    profile = CompanyProfile(enterprise_number="x", name="X", nace_code="7010")
    fin = Financials(employees=200, ebitda=9_500_000)
    vacancies = [{"is_it_role": True}]
    tech = {"legacy_score": 0.5}
    connections = [{}]
    result = build_signals(profile, fin, vacancies, tech, connections)
    assert isinstance(result, Signals)
    assert result.buyer_intent == pytest.approx(1.0)
    assert result.financial_fit == pytest.approx(1.0)
    assert result.sector_fit == pytest.approx(1.0)
