"""Tests for the KBO ETL parsing/transform (DB-independent)."""
import pytest

from app.db import load_kbo

ENTERPRISE = """\
"EnterpriseNumber","Status","JuridicalSituation","TypeOfEnterprise","JuridicalForm","JuridicalFormCAC","StartDate"
"0100.000.001","AC","000","2","016",,01-01-2000
"0100.000.002","AC","000","1","",,01-01-2000
"0100.000.003","ST","000","2","016",,01-01-2000
"0100.000.004","AC","000","2","016",,01-01-2000
"""

ACTIVITY = """\
"EntityNumber","ActivityGroup","NaceVersion","NaceCode","Classification"
"0100.000.001","006","2008","64190","MAIN"
"0100.000.001","006","2025","64200","MAIN"
"0100.000.001","006","2008","70220","SECO"
"0100.000.004","006","2008","86100","MAIN"
"""

DENOMINATION = """\
"EntityNumber","Language","TypeOfDenomination","Denomination"
"0100.000.001","1","001","Banque FR"
"0100.000.001","2","001","Bank NL"
"0100.000.001","2","002","Bank Trade"
"0100.000.003","2","001","Stopped NV"
"""

CONTACT = """\
"EntityNumber","EntityContact","ContactType","Value"
"0100.000.001","ENT","WEB","bank.be"
"0100.000.001","ENT","EMAIL","x@bank.be"
"""

ADDRESS = """\
"EntityNumber","TypeOfAddress","CountryNL","CountryFR","Zipcode","MunicipalityNL","MunicipalityFR","StreetNL","StreetFR","HouseNumber","Box","ExtraAddressInfo","DateStrikingOff"
"0100.000.001","ABBR",,,"2000","Antwerpen","Anvers","Meir","Meir","1","","",
"0100.000.001","REGO",,,"1000","Brussel","Bruxelles","Wetstraat","Rue de la Loi","16","","",
"0100.000.004","REGO",,,"9999","Nergens","Nulle part","Straat","Rue","1","","",
"""

# Centroid table the loader joins zipcode -> (lat, lon) against. 9999 is absent.
CENTROIDS = {"1000": (50.8504, 4.3488), "2000": (51.2199, 4.4023)}


@pytest.fixture
def kbo_dir(tmp_path):
    d = tmp_path / "kbo"
    d.mkdir()
    (d / "enterprise.csv").write_text(ENTERPRISE)
    (d / "activity.csv").write_text(ACTIVITY)
    (d / "denomination.csv").write_text(DENOMINATION)
    (d / "contact.csv").write_text(CONTACT)
    (d / "address.csv").write_text(ADDRESS)
    return d


def test_active_legal_entities_only(kbo_dir):
    active = load_kbo.active_enterprise_numbers(kbo_dir)
    # 001 + 004 are active legal entities; 002 is a natural person, 003 stopped.
    assert active == {"0100000001", "0100000004"}


def test_main_nace_prefers_2008(kbo_dir):
    active = load_kbo.active_enterprise_numbers(kbo_dir)
    naces = load_kbo.pick_main_nace(kbo_dir, active)
    assert naces["0100000001"] == "64190"  # 2008 wins over 2025
    assert naces["0100000004"] == "86100"  # SECO ignored, MAIN kept


def test_name_prefers_dutch_and_social_denomination(kbo_dir):
    active = load_kbo.active_enterprise_numbers(kbo_dir)
    names = load_kbo.pick_names(kbo_dir, active)
    assert names["0100000001"] == "Bank NL"  # NL over FR, type 001 over 002
    assert "0100000003" not in names  # stopped, not in active set


def test_websites_from_web_contact(kbo_dir):
    active = load_kbo.active_enterprise_numbers(kbo_dir)
    web = load_kbo.pick_websites(kbo_dir, active)
    assert web == {"0100000001": "bank.be"}


def test_build_frame_skips_nameless_and_derives_sector(kbo_dir):
    active = load_kbo.active_enterprise_numbers(kbo_dir)
    naces = load_kbo.pick_main_nace(kbo_dir, active)
    names = load_kbo.pick_names(kbo_dir, active)
    web = load_kbo.pick_websites(kbo_dir, active)
    df = load_kbo.build_company_frame(active, naces, names, web)

    # 004 has a NACE but no name -> dropped. Only 001 remains.
    assert len(df) == 1
    row = df.iloc[0]
    assert row["enterprise_number"] == "0100000001"
    assert row["name"] == "Bank NL"
    assert row["nace_code"] == "64190"
    assert row["sector"] == "financial_services"
    assert row["website"] == "bank.be"
    assert bool(row["active"]) is True
    assert row["stage"] == "pond"


def test_pick_addresses_uses_registered_seat(kbo_dir):
    active = load_kbo.active_enterprise_numbers(kbo_dir)
    addrs = load_kbo.pick_addresses(kbo_dir, active)
    # REGO row wins over the ABBR row for 001.
    a = addrs["0100000001"]
    assert a["zipcode"] == "1000"
    assert a["municipality"] == "Brussel"
    assert a["street"] == "Wetstraat"
    assert a["house"] == "16"


def test_build_frame_fills_address_and_centroid(kbo_dir):
    active = load_kbo.active_enterprise_numbers(kbo_dir)
    naces = load_kbo.pick_main_nace(kbo_dir, active)
    names = load_kbo.pick_names(kbo_dir, active)
    web = load_kbo.pick_websites(kbo_dir, active)
    addrs = load_kbo.pick_addresses(kbo_dir, active)
    df = load_kbo.build_company_frame(active, naces, names, web, addrs, CENTROIDS)

    row = df.iloc[0]
    assert row["zipcode"] == "1000"
    assert row["municipality"] == "Brussel"
    assert "Wetstraat 16" in row["address"]
    assert "1000 Brussel" in row["address"]
    assert row["latitude"] == 50.8504
    assert row["longitude"] == 4.3488


def test_build_frame_unknown_zip_has_no_coords(kbo_dir):
    # An entity whose zip is absent from the centroid table gets null coords.
    active = {"0100000004"}
    names = {"0100000004": "Nameless Co"}  # force-keep it for this check
    addrs = load_kbo.pick_addresses(kbo_dir, {"0100000004"})
    df = load_kbo.build_company_frame(active, {}, names, {}, addrs, CENTROIDS)
    row = df.iloc[0]
    assert row["zipcode"] == "9999"
    assert row["latitude"] is None
    assert row["longitude"] is None
