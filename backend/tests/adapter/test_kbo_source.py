"""Tests for KboSource using a sample CSV fixture."""
import pytest
import os
import tempfile
from pathlib import Path
from app.adapters.sources.kbo import KboSource
from app.domain.models import CompanyProfile
from app.domain.ports import CompanySource


SAMPLE_CSV = """EnterpriseNumber,Name,Status,JuridicalSituation,TypeOfEnterprise,NaceVersion,ActivityGroup,NaceCode,JuridicalForm,StartDate
0123456789,Acme Finance NV,Active,,Company,2008,Main,64190,,2010-01-01
0234567890,Beta Industry BV,Active,,Company,2008,Main,70220,,2015-03-15
0345678901,Hospital NV,Active,,Company,2008,Main,86100,,2008-06-01
0456789012,Too Small BVBA,Stopped,,Company,2008,Main,64190,,2005-01-01
0567890123,Secondary Act NV,Active,,Company,2008,Secondary,64190,,2012-01-01
"""


@pytest.fixture
def kbo_data_dir(tmp_path):
    kbo_dir = tmp_path / "kbo"
    kbo_dir.mkdir()
    (kbo_dir / "enterprise.csv").write_text(SAMPLE_CSV)
    return str(tmp_path)


def test_kbo_source_satisfies_protocol(kbo_data_dir):
    assert isinstance(KboSource(kbo_data_dir), CompanySource)


def test_loads_active_focus_nace_companies(kbo_data_dir):
    source = KboSource(kbo_data_dir)
    companies = source.load_pond()
    names = [c.name for c in companies]
    assert "Acme Finance NV" in names
    assert "Beta Industry BV" in names


def test_excludes_blacklisted_nace(kbo_data_dir):
    source = KboSource(kbo_data_dir)
    companies = source.load_pond()
    naces = [c.nace_code for c in companies]
    assert not any(n.startswith("86") for n in naces)


def test_excludes_stopped_companies(kbo_data_dir):
    source = KboSource(kbo_data_dir)
    companies = source.load_pond()
    names = [c.name for c in companies]
    assert "Too Small BVBA" not in names


def test_excludes_secondary_activities(kbo_data_dir):
    source = KboSource(kbo_data_dir)
    companies = source.load_pond()
    names = [c.name for c in companies]
    assert "Secondary Act NV" not in names


def test_returns_company_profiles(kbo_data_dir):
    source = KboSource(kbo_data_dir)
    companies = source.load_pond()
    assert all(isinstance(c, CompanyProfile) for c in companies)
    assert all(c.region == "BE" for c in companies)


def test_empty_result_when_no_csv(tmp_path):
    source = KboSource(str(tmp_path))
    assert source.load_pond() == []
