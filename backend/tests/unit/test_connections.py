import os
import pytest
from app.adapters.sources.connections import CsvConnectionProvider
from app.domain.ports import ConnectionProvider


@pytest.fixture
def csv_provider(tmp_path, monkeypatch):
    # Write sample CSV to tmp_path/connections/warm_connections.csv
    conn_dir = tmp_path / "connections"
    conn_dir.mkdir()
    csv_file = conn_dir / "warm_connections.csv"
    csv_file.write_text(
        "enterprise_number,contact_name,contact_title,relationship,strength\n"
        "0123456789,Jan Janssens,CFO,2nd,high\n"
        "0123456789,Marie Peeters,CTO,3rd,medium\n"
        "0987654321,Tom Claes,CEO,2nd,high\n"
    )
    monkeypatch.setattr("app.adapters.sources.connections.settings",
                        type("S", (), {"data_dir": str(tmp_path)})())
    return CsvConnectionProvider()


def test_connections_provider_satisfies_protocol(csv_provider):
    assert isinstance(csv_provider, ConnectionProvider)


def test_shared_returns_matching_connections(csv_provider):
    result = csv_provider.shared("0123456789")
    assert len(result) == 2
    assert result[0]["name"] == "Jan Janssens"
    assert result[0]["relationship"] == "2nd"
    assert result[1]["name"] == "Marie Peeters"


def test_shared_returns_empty_for_unknown_company(csv_provider):
    result = csv_provider.shared("9999999999")
    assert result == []


def test_shared_returns_empty_when_csv_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("app.adapters.sources.connections.settings",
                        type("S", (), {"data_dir": str(tmp_path)})())
    provider = CsvConnectionProvider()
    assert provider.shared("0123456789") == []
