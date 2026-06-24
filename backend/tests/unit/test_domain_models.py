"""Tests for pure domain value objects."""
import pytest
from dataclasses import FrozenInstanceError

from app.domain.models import (
    CompanyProfile,
    Financials,
    Signals,
    ScoreResult,
    Decision,
)


class TestCompanyProfile:
    """Tests for CompanyProfile immutability and creation."""

    def test_company_profile_is_immutable(self):
        """CompanyProfile is frozen — mutating raises FrozenInstanceError."""
        company = CompanyProfile(
            enterprise_number="0123456789",
            name="Acme Corp",
        )
        with pytest.raises(FrozenInstanceError):
            company.name = "Acme Inc"


class TestFinancials:
    """Tests for Financials value object."""

    def test_financials_all_none_is_valid(self):
        """Financials with all None fields is valid."""
        financials = Financials()
        assert financials.employees is None
        assert financials.revenue is None
        assert financials.ebitda is None
        assert financials.fiscal_year is None


class TestSignals:
    """Tests for Signals normalization and validation."""

    def test_signals_all_zero_is_valid(self):
        """Signals with all 0.0 is valid."""
        signals = Signals()
        assert signals.buyer_intent == 0.0
        assert signals.impact_potential == 0.0
        assert signals.financial_fit == 0.0
        assert signals.sector_fit == 0.0
        assert signals.warm_connection == 0.0

    def test_signals_value_greater_than_one_raises_error(self):
        """Signals with a value > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="buyer_intent must be in"):
            Signals(buyer_intent=1.1)

    def test_signals_value_less_than_zero_raises_error(self):
        """Signals with a value < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="financial_fit must be in"):
            Signals(financial_fit=-0.1)


class TestScoreResult:
    """Tests for ScoreResult value object."""

    def test_score_result_stores_values_correctly(self):
        """ScoreResult(total=0.75, breakdown={...}) stores values correctly."""
        breakdown = {"buyer_intent": 0.8}
        result = ScoreResult(total=0.75, breakdown=breakdown)
        assert result.total == 0.75
        assert result.breakdown == {"buyer_intent": 0.8}


class TestDecision:
    """Tests for Decision value object."""

    def test_decision_passes_true_has_no_reason(self):
        """Decision(passes=True) has reason=None by default."""
        decision = Decision(passes=True)
        assert decision.passes is True
        assert decision.reason is None

    def test_decision_passes_false_with_reason(self):
        """Decision(passes=False, reason=...) stores reason correctly."""
        decision = Decision(passes=False, reason="excluded NACE 86")
        assert decision.passes is False
        assert decision.reason == "excluded NACE 86"
