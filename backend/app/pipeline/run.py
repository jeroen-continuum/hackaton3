"""Batch orchestrator: ingest -> filter -> enrich -> score -> rank.

Run: python -m app.pipeline.run
Populates the DB; the web app then only reads. While connectors are stubs,
use `python -m app.db.seed` to demo the stack end-to-end.
"""
from sqlmodel import Session

from app.db.session import engine, init_db
from app.composition import build_container


def run() -> None:
    init_db()
    with Session(engine) as session:
        container = build_container(session)
        print("Running pipeline (ingest → filter → enrich → score → rank)...")
        top10 = container.pipeline.run()
        print(f"\nRolling 10 ({len(top10)} companies):")
        for i, profile in enumerate(top10, 1):
            print(f"  #{i:>2}  {profile.name:<30} [{profile.enterprise_number}]")


if __name__ == "__main__":
    run()
