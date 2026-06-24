"""KBO Open Data source adapter — implements CompanySource Protocol.

Reads the weekly CSV dump from DATA_DIR/kbo/enterprise.csv.
Filters: active, BE region, focus NACE prefixes, excludes blacklisted NACE prefixes.
"""
from pathlib import Path
import pandas as pd

from app.core.config import settings
from app.core.constants import FOCUS_NACE_PREFIXES, EXCLUDED_NACE_PREFIXES
from app.domain.models import CompanyProfile


class KboSource:
    """Loads Belgian companies from the KBO open data CSV dump."""

    def __init__(self, data_dir: str | None = None) -> None:
        self._data_dir = data_dir or settings.data_dir

    def load_pond(self) -> list[CompanyProfile]:
        """Read KBO dump and return companies matching ICP region + NACE criteria."""
        csv_path = Path(self._data_dir) / "kbo" / "enterprise.csv"
        if not csv_path.exists():
            return []

        df = pd.read_csv(csv_path, sep=",", dtype=str, low_memory=False)
        # Normalise column names
        df.columns = df.columns.str.strip()

        # Keep only active companies
        if "Status" in df.columns:
            df = df[df["Status"].str.strip().str.lower() == "active"]

        # Keep only main activity NACE codes
        if "ActivityGroup" in df.columns:
            df = df[df["ActivityGroup"].str.strip().str.lower() == "main"]

        results: list[CompanyProfile] = []
        seen: set[str] = set()

        for _, row in df.iterrows():
            nace = str(row.get("NaceCode", "") or "").strip()
            if not nace:
                continue

            # Exclude blacklisted sectors
            if any(nace.startswith(p) for p in EXCLUDED_NACE_PREFIXES):
                continue

            # Must match at least one focus sector
            if not any(nace.startswith(p) for p in FOCUS_NACE_PREFIXES):
                continue

            ent_num = str(row.get("EnterpriseNumber", "") or "").strip()
            if not ent_num or ent_num in seen:
                continue
            seen.add(ent_num)

            name = str(row.get("Name", "") or "").strip() or ent_num
            results.append(CompanyProfile(
                enterprise_number=ent_num,
                name=name,
                region="BE",
                nace_code=nace,
            ))

        return results
