"""Weighted scoring adapter — implements ScoringStrategy Protocol.

Delegates to the existing compute_score() pure function in pipeline/score.py.
Wraps dict-based internals into domain value objects.
"""
from app.domain.models import Signals, ScoreResult
from app.pipeline.score import compute_score


class WeightedScoringStrategy:
    """Default scoring: weighted sum of normalised signals, normalised to [0,1]."""

    def score(self, signals: Signals) -> ScoreResult:
        signals_dict = {
            "buyer_intent": signals.buyer_intent,
            "impact_potential": signals.impact_potential,
            "financial_fit": signals.financial_fit,
            "sector_fit": signals.sector_fit,
            "warm_connection": signals.warm_connection,
        }
        total, breakdown = compute_score(signals_dict)
        return ScoreResult(total=total, breakdown=breakdown)
