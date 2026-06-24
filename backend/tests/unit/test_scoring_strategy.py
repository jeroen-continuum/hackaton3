"""Tests for WeightedScoringStrategy via ScoringStrategy port."""
import pytest
from app.domain.models import Signals, ScoreResult
from app.domain.ports import ScoringStrategy
from app.adapters.scoring.weighted import WeightedScoringStrategy


def test_weighted_strategy_satisfies_protocol():
    assert isinstance(WeightedScoringStrategy(), ScoringStrategy)


def test_perfect_signals_score_one():
    strategy = WeightedScoringStrategy()
    signals = Signals(
        buyer_intent=1.0,
        impact_potential=1.0,
        financial_fit=1.0,
        sector_fit=1.0,
        warm_connection=1.0,
    )
    result = strategy.score(signals)
    assert result.total == 1.0


def test_zero_signals_score_zero():
    strategy = WeightedScoringStrategy()
    result = strategy.score(Signals())
    assert result.total == 0.0


def test_partial_signals_score_between_zero_and_one():
    strategy = WeightedScoringStrategy()
    result = strategy.score(Signals(buyer_intent=1.0))
    assert 0.0 < result.total < 1.0


def test_returns_breakdown_with_all_criteria():
    strategy = WeightedScoringStrategy()
    result = strategy.score(Signals(buyer_intent=0.8, financial_fit=0.6))
    assert set(result.breakdown.keys()) == {
        "buyer_intent", "impact_potential", "financial_fit",
        "sector_fit", "warm_connection",
    }
    assert result.breakdown["buyer_intent"] == pytest.approx(0.8)
    assert result.breakdown["sector_fit"] == 0.0


def test_score_result_is_score_result_type():
    strategy = WeightedScoringStrategy()
    result = strategy.score(Signals(buyer_intent=0.5))
    assert isinstance(result, ScoreResult)
