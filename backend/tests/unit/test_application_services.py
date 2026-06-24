"""Unit tests for application services using fake adapters from conftest."""
import pytest
from app.domain.models import CompanyProfile, Financials, Signals, ScoreResult
from app.application.scoring import Scorer
from app.application.outreach import GenerateOutreach
from app.application.pipeline import RunPipeline


class TestScorer:
    def test_scorer_delegates_to_strategy(self, fake_scoring_strategy):
        scorer = Scorer(fake_scoring_strategy)
        signals = Signals(buyer_intent=0.8, financial_fit=0.6)
        result = scorer.score(signals)
        assert isinstance(result, ScoreResult)
        assert result.total == pytest.approx(0.5)  # FakeScoringStrategy returns 0.5

    def test_scorer_passes_signals_through(self, fake_scoring_strategy):
        scorer = Scorer(fake_scoring_strategy)
        signals = Signals(buyer_intent=1.0)
        result = scorer.score(signals)
        assert "buyer_intent" in result.breakdown


class TestGenerateOutreach:
    def test_email_delegates_to_generator(self, fake_outreach_generator, fake_company_repository):
        service = GenerateOutreach(fake_outreach_generator, fake_company_repository)
        profile = CompanyProfile(enterprise_number="1", name="Test NV")
        result = service.email(profile, [])
        assert result["subject"] == "Test"
        assert result["body"] == "Test body"

    def test_teaser_delegates_to_generator(self, fake_outreach_generator, fake_company_repository):
        service = GenerateOutreach(fake_outreach_generator, fake_company_repository)
        profile = CompanyProfile(enterprise_number="1", name="Test NV")
        result = service.teaser(profile, [])
        assert result["title"] == "Test"
        assert "preview" in result


class TestRunPipeline:
    @pytest.fixture
    def pipeline(
        self,
        fake_company_source,
        fake_financials_provider,
        fake_filter_policy,
        fake_vacancy_provider,
        fake_tech_provider,
        fake_connection_provider,
        fake_scoring_strategy,
        fake_company_repository,
    ):
        return RunPipeline(
            source=fake_company_source,
            financials=fake_financials_provider,
            filter_policy=fake_filter_policy,
            vacancies=fake_vacancy_provider,
            tech=fake_tech_provider,
            connections=fake_connection_provider,
            scorer=fake_scoring_strategy,
            repo=fake_company_repository,
        )

    def test_pipeline_run_returns_list(self, pipeline):
        result = pipeline.run()
        assert isinstance(result, list)

    def test_pipeline_run_with_empty_pond_returns_empty(self, pipeline):
        result = pipeline.run()
        assert result == []

    def test_pipeline_filters_excluded_companies(
        self,
        fake_company_source,
        fake_financials_provider,
        fake_vacancy_provider,
        fake_tech_provider,
        fake_connection_provider,
        fake_scoring_strategy,
        fake_company_repository,
    ):
        from app.domain.models import Decision

        class RejectAllPolicy:
            def evaluate(self, profile, financials):
                return Decision(passes=False, reason="rejected")

        pipeline = RunPipeline(
            source=fake_company_source,
            financials=fake_financials_provider,
            filter_policy=RejectAllPolicy(),
            vacancies=fake_vacancy_provider,
            tech=fake_tech_provider,
            connections=fake_connection_provider,
            scorer=fake_scoring_strategy,
            repo=fake_company_repository,
        )
        result = pipeline.run()
        assert result == []
