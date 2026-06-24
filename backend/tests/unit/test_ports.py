"""Verify that all fake adapters satisfy their port Protocols at runtime."""
import pytest
from app.domain import ports
from app.domain.models import CompanyProfile, Financials, Signals, ScoreResult, Decision


def test_fake_company_source_satisfies_protocol(fake_company_source):
    assert isinstance(fake_company_source, ports.CompanySource)

def test_fake_financials_provider_satisfies_protocol(fake_financials_provider):
    assert isinstance(fake_financials_provider, ports.FinancialsProvider)

def test_fake_vacancy_provider_satisfies_protocol(fake_vacancy_provider):
    assert isinstance(fake_vacancy_provider, ports.VacancyProvider)

def test_fake_tech_provider_satisfies_protocol(fake_tech_provider):
    assert isinstance(fake_tech_provider, ports.TechProvider)

def test_fake_connection_provider_satisfies_protocol(fake_connection_provider):
    assert isinstance(fake_connection_provider, ports.ConnectionProvider)

def test_fake_contact_provider_satisfies_protocol(fake_contact_provider):
    assert isinstance(fake_contact_provider, ports.ContactProvider)

def test_fake_scoring_strategy_satisfies_protocol(fake_scoring_strategy):
    assert isinstance(fake_scoring_strategy, ports.ScoringStrategy)

def test_fake_filter_policy_satisfies_protocol(fake_filter_policy):
    assert isinstance(fake_filter_policy, ports.FilterPolicy)

def test_fake_outreach_generator_satisfies_protocol(fake_outreach_generator):
    assert isinstance(fake_outreach_generator, ports.OutreachGenerator)

def test_fake_company_repository_satisfies_protocol(fake_company_repository):
    assert isinstance(fake_company_repository, ports.CompanyRepository)
