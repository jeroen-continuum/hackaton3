"""Load the full KBO Open Data dump into the Company table.

Replaces the demo seed with all *active legal-entity* Belgian companies from the
FOD Economie weekly/monthly Full dump. Drop the unzipped CSVs into
``settings.data_dir/kbo/`` (see data/kbo/README.md), then run::

    python -m app.db.load_kbo

The dump is a set of CSVs linked by enterprise number:
  - enterprise.csv     Status (AC=active), TypeOfEnterprise (2=legal entity)
  - activity.csv       NaceCode per entity, Classification (MAIN), NaceVersion
  - denomination.csv   names (TypeOfDenomination 001 = social name), Language
  - contact.csv        ContactType WEB = website
  - address.csv        registered-seat (REGO) zipcode/municipality/street

The registered-seat postal code is mapped to a lat/lon centroid (GeoNames, see
app/db/zip_centroids.py) so companies can be filtered by area and shown on a map.

No NACE/sector filtering happens here — the whole active universe is loaded so
the ICP filters can be adjusted at query time. Only active legal entities with a
name are imported (natural persons can never meet a 100-500 FTE ICP).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import delete
from sqlmodel import Session

from app.core.config import settings
from app.core.constants import sector_for_nace
from app.db.session import engine, init_db
from app.db.zip_centroids import load_centroids
from app.models import Company, Score

# Prefer NACE 2008 (the version our prefix constants are built on), then the
# newer 2025, then legacy 2003.
_NACE_VERSION_RANK = {"2008": 0, "2025": 1, "2003": 2}
# Prefer Dutch, then French, English, German, unknown.
_LANG_RANK = {"2": 0, "1": 1, "4": 2, "3": 3, "0": 4}
_CHUNK = 500_000


def _norm(num: str | float | None) -> str:
    """Normalise a KBO number ('0200.065.765') to bare digits ('0200065765')."""
    if num is None or (isinstance(num, float) and pd.isna(num)):
        return ""
    return str(num).replace(".", "").replace(" ", "").strip()


def active_enterprise_numbers(kbo_dir: Path) -> set[str]:
    """Normalised numbers of active (AC) legal entities (TypeOfEnterprise=2)."""
    df = pd.read_csv(
        kbo_dir / "enterprise.csv",
        usecols=["EnterpriseNumber", "Status", "TypeOfEnterprise"],
        dtype=str,
    )
    df = df[(df["Status"] == "AC") & (df["TypeOfEnterprise"] == "2")]
    return {_norm(n) for n in df["EnterpriseNumber"]}


def pick_main_nace(kbo_dir: Path, active: set[str], chunksize: int = _CHUNK) -> dict[str, str]:
    """Best MAIN NACE code per active entity, by version preference."""
    best: dict[str, str] = {}
    best_rank: dict[str, int] = {}
    for chunk in pd.read_csv(
        kbo_dir / "activity.csv",
        usecols=["EntityNumber", "NaceVersion", "NaceCode", "Classification"],
        dtype=str,
        chunksize=chunksize,
    ):
        chunk = chunk[chunk["Classification"] == "MAIN"]
        for ent, ver, nace in zip(chunk["EntityNumber"], chunk["NaceVersion"], chunk["NaceCode"]):
            key = _norm(ent)
            if key not in active:
                continue
            rank = _NACE_VERSION_RANK.get(str(ver), 9)
            if key not in best_rank or rank < best_rank[key]:
                best_rank[key] = rank
                best[key] = str(nace)
    return best


def pick_names(kbo_dir: Path, active: set[str], chunksize: int = _CHUNK) -> dict[str, str]:
    """Best social denomination (001) per active entity, by language preference."""
    best: dict[str, str] = {}
    best_rank: dict[str, int] = {}
    for chunk in pd.read_csv(
        kbo_dir / "denomination.csv",
        usecols=["EntityNumber", "Language", "TypeOfDenomination", "Denomination"],
        dtype=str,
        chunksize=chunksize,
    ):
        chunk = chunk[chunk["TypeOfDenomination"] == "001"]
        for ent, lang, name in zip(
            chunk["EntityNumber"], chunk["Language"], chunk["Denomination"]
        ):
            key = _norm(ent)
            if key not in active:
                continue
            rank = _LANG_RANK.get(str(lang), 9)
            if key not in best_rank or rank < best_rank[key]:
                best_rank[key] = rank
                best[key] = str(name)
    return best


def pick_websites(kbo_dir: Path, active: set[str], chunksize: int = _CHUNK) -> dict[str, str]:
    """First WEB contact per active entity."""
    web: dict[str, str] = {}
    for chunk in pd.read_csv(
        kbo_dir / "contact.csv",
        usecols=["EntityNumber", "EntityContact", "ContactType", "Value"],
        dtype=str,
        chunksize=chunksize,
    ):
        chunk = chunk[chunk["ContactType"] == "WEB"]
        for ent, val in zip(chunk["EntityNumber"], chunk["Value"]):
            key = _norm(ent)
            if key in active and key not in web:
                web[key] = str(val)
    return web


def pick_addresses(
    kbo_dir: Path, active: set[str], chunksize: int = _CHUNK
) -> dict[str, dict[str, str]]:
    """Registered-seat (REGO) address per active entity.

    Returns ``{num: {"zipcode", "municipality", "street", "house"}}`` using the
    Dutch municipality/street columns. Only the REGO (registered office) address
    is kept; other address types (e.g. branch/abbreviated) are ignored.
    """
    best: dict[str, dict[str, str]] = {}
    for chunk in pd.read_csv(
        kbo_dir / "address.csv",
        usecols=[
            "EntityNumber", "TypeOfAddress", "Zipcode",
            "MunicipalityNL", "StreetNL", "HouseNumber",
        ],
        dtype=str,
        chunksize=chunksize,
    ):
        chunk = chunk[chunk["TypeOfAddress"] == "REGO"]
        for ent, zc, muni, street, house in zip(
            chunk["EntityNumber"], chunk["Zipcode"], chunk["MunicipalityNL"],
            chunk["StreetNL"], chunk["HouseNumber"],
        ):
            key = _norm(ent)
            if key not in active or key in best:
                continue
            best[key] = {
                "zipcode": _clean(zc),
                "municipality": _clean(muni),
                "street": _clean(street),
                "house": _clean(house),
            }
    return best


def _clean(val: str | float | None) -> str:
    """Empty string for NaN/None; stripped string otherwise."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()


def _format_address(addr: dict[str, str]) -> str | None:
    """'Wetstraat 16, 1000 Brussel' from the address parts (None if empty)."""
    line1 = " ".join(p for p in (addr.get("street"), addr.get("house")) if p)
    line2 = " ".join(p for p in (addr.get("zipcode"), addr.get("municipality")) if p)
    full = ", ".join(p for p in (line1, line2) if p)
    return full or None


def build_company_frame(
    active: set[str],
    naces: dict[str, str],
    names: dict[str, str],
    websites: dict[str, str],
    addresses: dict[str, dict[str, str]] | None = None,
    centroids: dict[str, tuple[float, float]] | None = None,
) -> pd.DataFrame:
    """Assemble the Company rows — only active entities that have a name."""
    addresses = addresses or {}
    centroids = centroids or {}
    rows = []
    for num in active:
        name = names.get(num)
        if not name:
            continue  # skip nameless entities (nothing to show)
        nace = naces.get(num)
        addr = addresses.get(num, {})
        zipcode = addr.get("zipcode") or None
        lat, lon = centroids.get(zipcode, (None, None)) if zipcode else (None, None)
        rows.append(
            {
                "enterprise_number": num,
                "name": name,
                "region": "BE",
                "nace_code": nace,
                "sector": sector_for_nace(nace),
                "website": websites.get(num),
                "address": _format_address(addr),
                "zipcode": zipcode,
                "municipality": addr.get("municipality") or None,
                "latitude": lat,
                "longitude": lon,
                "active": True,
                "stage": "pond",
                "excluded": False,
            }
        )
    return pd.DataFrame(rows)


def load_kbo(data_dir: str | None = None) -> int:
    """Parse the KBO dump and bulk-replace the Company table. Returns row count."""
    kbo_dir = Path(data_dir or settings.data_dir) / "kbo"
    if not (kbo_dir / "enterprise.csv").exists():
        raise FileNotFoundError(
            f"No KBO dump found in {kbo_dir}. See data/kbo/README.md for the download."
        )

    init_db()
    print(f"Reading active legal entities from {kbo_dir} ...")
    active = active_enterprise_numbers(kbo_dir)
    print(f"  {len(active):,} active legal entities")
    naces = pick_main_nace(kbo_dir, active)
    print(f"  {len(naces):,} with a MAIN NACE code")
    names = pick_names(kbo_dir, active)
    print(f"  {len(names):,} with a name")
    websites = pick_websites(kbo_dir, active)
    print(f"  {len(websites):,} with a website")
    addresses = pick_addresses(kbo_dir, active)
    print(f"  {len(addresses):,} with a registered-seat address")
    centroids = load_centroids()

    df = build_company_frame(active, naces, names, websites, addresses, centroids)
    geocoded = int(df["latitude"].notna().sum()) if len(df) else 0
    print(f"Inserting {len(df):,} companies ({geocoded:,} with map coordinates) ...")

    # Clear any prior companies/scores (demo seed or earlier load).
    with Session(engine) as s:
        s.exec(delete(Score))
        s.exec(delete(Company))
        s.commit()

    # chunksize keeps params (rows * cols) under the SQLite variable limit too.
    df.to_sql("company", engine, if_exists="append", index=False, chunksize=3000, method="multi")
    print(f"Loaded {len(df):,} companies into the Company table.")
    return len(df)


if __name__ == "__main__":
    load_kbo()
