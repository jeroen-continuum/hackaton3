"""Synthetic financials adapter — implements FinancialsProvider Protocol.

Hackathon stand-in for real NBB data: we have no time to load financials for
every company, so this generates realistic, weighted dummy figures instead.

Values are NOT uniform-random. Employee count and EBITDA margin are drawn from
probability-weighted buckets, and revenue/EBITDA are correlated
(revenue = headcount x per-FTE, ebitda = revenue x margin). Output is
deterministic per company (seeded from the enterprise number) so repeated
requests and re-runs return the same numbers.

Buckets are tuned against the ICP thresholds in core/constants.py: a healthy
share of companies land in the 100-500 FTE band and clear the ~EUR 1.5M EBITDA
bar (PROJECT_VALUE_MIN / MAX_PROJECT_TO_EBITDA_RATIO), while thin-margin and
out-of-band companies fail — giving the demo a believable spread.
"""
import hashlib
import random

from app.domain.models import Financials

# (low, high, weight) — bucket picked by weight, then a value drawn within it.
_EMPLOYEE_BUCKETS = [
    (10, 100, 35),      # too small for ICP
    (100, 500, 45),     # ICP sweet spot
    (500, 2000, 15),
    (2000, 8000, 5),
]
_MARGIN_BUCKETS = [
    (-0.05, 0.03, 15),  # thin / loss-making
    (0.03, 0.08, 35),
    (0.08, 0.15, 35),
    (0.15, 0.30, 15),
]
_FISCAL_YEARS = [(2024, 60), (2023, 30), (2022, 10)]

_MISSING_RATE = 0.08  # fraction of companies with no filed accounts


def _weighted_choice(rng: random.Random, buckets: list):
    """Return a bucket from (..., weight) tuples, chosen by its weight."""
    total = sum(b[-1] for b in buckets)
    pick = rng.uniform(0, total)
    upto = 0.0
    for bucket in buckets:
        upto += bucket[-1]
        if pick <= upto:
            return bucket
    return buckets[-1]


class FakeFinancialsProvider:
    """Generates realistic, weighted synthetic financials per company."""

    def fetch(self, enterprise_number: str) -> Financials | None:
        seed = int(hashlib.sha256(enterprise_number.encode()).hexdigest()[:16], 16)
        rng = random.Random(seed)

        if rng.random() < _MISSING_RATE:
            return None  # mimic a company with no filed accounts

        lo, hi, _ = _weighted_choice(rng, _EMPLOYEE_BUCKETS)
        employees = rng.randint(lo, hi)

        revenue = round(employees * rng.uniform(120_000, 350_000), -3)

        m_lo, m_hi, _ = _weighted_choice(rng, _MARGIN_BUCKETS)
        ebitda = round(revenue * rng.uniform(m_lo, m_hi), -3)

        fiscal_year, _ = _weighted_choice(rng, _FISCAL_YEARS)

        return Financials(
            employees=employees,
            revenue=revenue,
            ebitda=ebitda,
            fiscal_year=fiscal_year,
        )


if __name__ == "__main__":
    # ponytail: self-check — determinism + distribution sanity, no test framework.
    provider = FakeFinancialsProvider()

    # (a) deterministic per company
    assert provider.fetch("0123456789") == provider.fetch("0123456789")
    # (b) different companies differ (overwhelmingly)
    assert provider.fetch("0123456789") != provider.fetch("0987654321")

    # (c) distribution lands realistically vs the ICP thresholds
    EBITDA_BAR = 150_000 / 0.10  # PROJECT_VALUE_MIN / MAX_PROJECT_TO_EBITDA_RATIO
    n = 2000
    results = [provider.fetch(str(1_000_000_000 + i)) for i in range(n)]
    present = [f for f in results if f is not None]
    in_icp = [f for f in present if 100 <= f.employees <= 500]
    pass_fin = [f for f in present if f.ebitda and f.ebitda >= EBITDA_BAR]

    missing_pct = 100 * (n - len(present)) / n
    print(f"missing:        {missing_pct:.1f}%")
    print(f"100-500 FTE:    {100*len(in_icp)/len(present):.1f}% of present")
    print(f"pass EBITDA bar:{100*len(pass_fin)/len(present):.1f}% of present")

    assert 3 < missing_pct < 14, missing_pct
    assert len(in_icp) / len(present) > 0.30
    assert len(pass_fin) / len(present) > 0.30
    print("OK")
