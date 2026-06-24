"""Unit tests for pipeline wiring: save_score, company_id, repo.get_top10()."""
import pytest
from app.application.pipeline import RunPipeline
from app.domain.models import CompanyProfile, Financials, ScoreResult


def _make_pipeline(source, repo, scorer=None, filter_policy=None, financials=None):
    from tests.conftest import (
        FakeVacancyProvider, FakeTechProvider, FakeConnectionProvider,
        FakeScoringStrategy, FakeFilterPolicy, FakeFinancialsProvider,
    )
    return RunPipeline(
        source=source,
        financials=financials or FakeFinancialsProvider(),
        filter_policy=filter_policy or FakeFilterPolicy(),
        vacancies=FakeVacancyProvider(),
        tech=FakeTechProvider(),
        connections=FakeConnectionProvider(),
        scorer=scorer or FakeScoringStrategy(),
        repo=repo,
    )


def test_pipeline_run_returns_list(fake_company_source, fake_company_repository):
    fake_company_source._companies = [
        CompanyProfile(enterprise_number="0001", name="Acme")
    ]
    fake_company_source.load_pond = lambda: fake_company_source._companies
    pipeline = _make_pipeline(fake_company_source, fake_company_repository)
    result = pipeline.run()
    assert isinstance(result, list)


def test_pipeline_saves_score_with_company_id(fake_company_repository):
    from tests.conftest import FakeCompanySource, FakeScoringStrategy, FakeFilterPolicy
    source = FakeCompanySource()
    source.load_pond = lambda: [CompanyProfile(enterprise_number="0001", name="Acme")]
    pipeline = _make_pipeline(source, fake_company_repository)
    pipeline.run()
    assert len(fake_company_repository._scores) == 1
    assert "_company_id" in fake_company_repository._scores[0].breakdown
    assert fake_company_repository._scores[0].breakdown["_company_id"] == 1


def test_pipeline_calls_save_company_for_each_passing(fake_company_repository):
    from tests.conftest import FakeCompanySource
    source = FakeCompanySource()
    source.load_pond = lambda: [
        CompanyProfile(enterprise_number="0001", name="Acme"),
        CompanyProfile(enterprise_number="0002", name="Beta"),
    ]
    pipeline = _make_pipeline(source, fake_company_repository)
    pipeline.run()
    assert len(fake_company_repository._companies) == 2


def test_pipeline_filters_excluded_companies(fake_company_repository):
    from tests.conftest import FakeCompanySource, FakeFilterPolicy
    from app.domain.models import Decision

    source = FakeCompanySource()
    source.load_pond = lambda: [
        CompanyProfile(enterprise_number="0001", name="Acme"),
        CompanyProfile(enterprise_number="0002", name="Excluded"),
    ]

    class SelectiveFilter:
        def evaluate(self, profile, financials):
            return Decision(passes=(profile.enterprise_number == "0001"))

    pipeline = _make_pipeline(source, fake_company_repository, filter_policy=SelectiveFilter())
    pipeline.run()
    assert len(fake_company_repository._companies) == 1
