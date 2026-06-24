"""Unit tests for Rolling10 application service."""
import pytest
from app.application.rolling10 import Rolling10
from app.domain.models import CompanyProfile, ScoreResult


def test_get_top10_delegates_to_repo(fake_company_repository):
    fake_company_repository._companies = [
        CompanyProfile(enterprise_number="0001", name="Acme"),
        CompanyProfile(enterprise_number="0002", name="Beta"),
    ]
    service = Rolling10(fake_company_repository)
    result = service.get_top10()
    assert len(result) == 2


def test_mark_contacted_calls_repo(fake_company_repository):
    called_with = []
    fake_company_repository.mark_contacted = lambda en: called_with.append(en)
    service = Rolling10(fake_company_repository)
    service.mark_contacted("0001")
    assert called_with == ["0001"]


def test_assign_ranks_called_after_pipeline_run(fake_company_repository):
    from tests.conftest import FakeCompanySource, FakeScoringStrategy, FakeFilterPolicy
    from app.application.pipeline import RunPipeline
    from tests.conftest import FakeVacancyProvider, FakeTechProvider, FakeConnectionProvider, FakeFinancialsProvider

    ranks_assigned = []
    fake_company_repository.assign_ranks = lambda: ranks_assigned.append(True)
    source = FakeCompanySource()
    source._companies = [CompanyProfile(enterprise_number="0001", name="Acme")]
    pipeline = RunPipeline(
        source=source,
        financials=FakeFinancialsProvider(),
        filter_policy=FakeFilterPolicy(),
        vacancies=FakeVacancyProvider(),
        tech=FakeTechProvider(),
        connections=FakeConnectionProvider(),
        scorer=FakeScoringStrategy(),
        repo=fake_company_repository,
    )
    pipeline.run()
    assert len(ranks_assigned) == 1
