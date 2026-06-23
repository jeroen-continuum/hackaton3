"""Step 1 — Pond: load KBO dump, filter region + focus NACE, write Company rows."""
from sqlmodel import Session

from app.connectors.kbo import KboConnector
from app.core import constants


def ingest(session: Session) -> int:
    """Returns number of companies loaded into the pond. TODO: implement."""
    _kbo = KboConnector()
    # rows = _kbo.load_companies()
    # keep rows whose nace_code starts with a FOCUS_NACE_PREFIX and region in REGIONS
    # persist as Company(stage="pond")
    _ = (constants.FOCUS_NACE_PREFIXES, constants.REGIONS)
    raise NotImplementedError("Implement KBO ingest -> Company(stage='pond')")
