"""Populate FinancialData with synthetic figures so the size/financial filters work.

Reuses FakeFinancialsProvider (the same weighted, deterministic generator the
request path uses) and bulk-inserts one FinancialData row per company. Companies
the generator marks as "no filed accounts" (returns None) get no row, so those
still exercise the missing-financials path.

Run: python -m app.db.seed_financials          # no-op if financials already exist
     python -m app.db.seed_financials --force   # wipe + regenerate all rows
"""
import sys

from sqlalchemy import delete, insert
from sqlmodel import Session, func, select

from app.adapters.sources.fake_financials import FakeFinancialsProvider
from app.db.session import engine, init_db
from app.models import Company, FinancialData

_BATCH = 5000  # rows per executemany insert


def seed_financials(session: Session, force: bool = False) -> int:
    """Bulk-insert synthetic FinancialData for every company. Returns rows written."""
    existing = session.exec(select(func.count()).select_from(FinancialData)).one()
    if existing and not force:
        print(f"FinancialData already has {existing} rows; use --force to rebuild.")
        return 0
    if existing:
        session.exec(delete(FinancialData))
        session.commit()

    provider = FakeFinancialsProvider()
    # Only the two columns the generator needs — avoids loading full ORM rows.
    companies = session.exec(select(Company.id, Company.enterprise_number)).all()

    batch: list[dict] = []
    written = 0
    for cid, enterprise_number in companies:
        fin = provider.fetch(enterprise_number)
        if fin is None:
            continue  # generator says "no filed accounts" — leave it missing
        batch.append({
            "company_id": cid,
            "employees": fin.employees,
            "revenue": fin.revenue,
            "ebitda": fin.ebitda,
            "fiscal_year": fin.fiscal_year,
        })
        if len(batch) >= _BATCH:
            session.execute(insert(FinancialData), batch)
            session.commit()
            written += len(batch)
            batch.clear()
    if batch:
        session.execute(insert(FinancialData), batch)
        session.commit()
        written += len(batch)

    return written


if __name__ == "__main__":
    init_db()
    with Session(engine) as s:
        n = seed_financials(s, force="--force" in sys.argv)
        print(f"Wrote synthetic financials for {n} companies.")
