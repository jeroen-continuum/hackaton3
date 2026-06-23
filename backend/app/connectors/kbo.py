"""KBO Open Data — the 'pond'. Loads the weekly BE company dump (CSV/XML).

TODO: point load_companies() at the downloaded FOD Economie dump in DATA_DIR.
Returns raw company dicts: enterprise_number, name, nace_code, address, active.
"""
from app.connectors.base import CachedConnector


class KboConnector(CachedConnector):
    name = "kbo"

    def load_companies(self) -> list[dict]:
        # TODO: read CSV dump from settings.data_dir with pandas, filter active.
        raise NotImplementedError("Wire up KBO dump loading")
