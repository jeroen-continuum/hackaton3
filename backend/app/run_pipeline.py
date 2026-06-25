"""Run the scoring pipeline over the loaded company pond.

Selects candidates from the Company table (filtered by the default ICP, capped
at settings.max_pond_enrich), enriches + scores them, and ranks the Rolling 10::

    python -m app.run_pipeline

Run `python -m app.db.load_kbo` first to populate the company universe.
"""
from sqlmodel import Session

from app.composition import build_container
from app.db.session import engine, init_db


def main() -> None:
    init_db()
    with Session(engine) as session:
        container = build_container(session)
        top = container.pipeline.run()
        print(f"Scored pipeline complete. Rolling 10:")
        for i, c in enumerate(top, start=1):
            print(f"  {i:>2}. {c.name} ({c.enterprise_number}) — {c.sector or '?'}")


if __name__ == "__main__":
    main()
