"""Scorer application service — delegates to ScoringStrategy port."""
from app.domain.models import Signals, ScoreResult
from app.domain.ports import ScoringStrategy


class Scorer:
    def __init__(self, strategy: ScoringStrategy) -> None:
        self._strategy = strategy

    def score(self, signals: Signals) -> ScoreResult:
        return self._strategy.score(signals)
