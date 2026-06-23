"""Step 4 — Score: weighted criteria -> total, then rank into the Rolling 10.

Real, testable logic: compute_score() takes per-criterion signals in [0,1] and
returns (total, breakdown). The breakdown IS the heatmap shown in the UI.
"""
from app.core.constants import SCORE_WEIGHTS


def compute_score(signals: dict[str, float]) -> tuple[float, dict[str, float]]:
    """signals: criterion -> normalised value in [0,1]. Missing => 0.

    Returns (weighted_total in [0,1], breakdown dict of clamped signals).
    """
    breakdown: dict[str, float] = {}
    total = 0.0
    weight_sum = sum(SCORE_WEIGHTS.values())
    for criterion, weight in SCORE_WEIGHTS.items():
        value = max(0.0, min(1.0, float(signals.get(criterion, 0.0))))
        breakdown[criterion] = value
        total += weight * value
    return total / weight_sum, breakdown


def rank_scores(scored: list[tuple[int, float]]) -> dict[int, int]:
    """scored: list of (company_id, total). Returns company_id -> rank (1-based)."""
    ordered = sorted(scored, key=lambda x: x[1], reverse=True)
    return {company_id: i + 1 for i, (company_id, _) in enumerate(ordered)}
