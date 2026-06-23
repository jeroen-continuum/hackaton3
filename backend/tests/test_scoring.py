from app.pipeline.score import compute_score, rank_scores
from app.pipeline import filter as flt
from app.models import Company, FinancialData


def test_compute_score_perfect():
    signals = {k: 1.0 for k in [
        "buyer_intent", "impact_potential", "financial_fit",
        "sector_fit", "warm_connection",
    ]}
    total, breakdown = compute_score(signals)
    assert total == 1.0
    assert breakdown["buyer_intent"] == 1.0


def test_compute_score_clamps_and_defaults_missing():
    total, breakdown = compute_score({"buyer_intent": 5.0})  # over 1, rest missing
    assert breakdown["buyer_intent"] == 1.0
    assert breakdown["sector_fit"] == 0.0
    assert 0.0 < total < 1.0


def test_rank_scores_orders_desc():
    ranks = rank_scores([(10, 0.5), (20, 0.9), (30, 0.7)])
    assert ranks == {20: 1, 30: 2, 10: 3}


def test_size_filter_bounds():
    assert flt.passes_size(FinancialData(company_id=1, employees=240))
    assert not flt.passes_size(FinancialData(company_id=1, employees=20))
    assert not flt.passes_size(FinancialData(company_id=1, employees=900))


def test_financial_fit_needs_ebitda_headroom():
    # EBITDA 9.5M * 10% = 950k >= 150k project min -> passes
    assert flt.passes_financial_fit(FinancialData(company_id=1, ebitda=9_500_000))
    # EBITDA 1M * 10% = 100k < 150k -> fails
    assert not flt.passes_financial_fit(FinancialData(company_id=1, ebitda=1_000_000))
    assert not flt.passes_financial_fit(FinancialData(company_id=1, ebitda=0))


def test_exclusion_by_nace():
    excluded, reason = flt.is_excluded(Company(enterprise_number="x", name="H", nace_code="8610"))
    assert excluded and "86" in reason
    ok, _ = flt.is_excluded(Company(enterprise_number="y", name="F", nace_code="6419"))
    assert not ok
