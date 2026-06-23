"""Batch orchestrator: ingest -> filter -> enrich -> score -> rank.

Run: python -m app.pipeline.run
Populates the DB; the web app then only reads. While connectors are stubs,
use `python -m app.db.seed` to demo the stack end-to-end.
"""
from sqlmodel import Session, select

from app.db.session import engine, init_db
from app.models import Company, Score
from app.pipeline import ingest, enrich
from app.pipeline.score import rank_scores


def run() -> None:
    init_db()
    with Session(engine) as session:
        print("Step 1/4 — ingest (pond)")
        ingest.ingest(session)

        print("Step 2/4 — filter (NBB size/EBITDA + exclusions)")
        # filter.py provides pure predicates; apply them over pond companies here.

        print("Step 3/4 — enrich (Apollo / VDAB / Wappalyzer)")
        enrich.enrich(session)

        print("Step 4/4 — score + rank")
        scored = session.exec(select(Score.company_id, Score.total)).all()
        ranks = rank_scores([(cid, total) for cid, total in scored])
        for cid, rank in ranks.items():
            score = session.exec(select(Score).where(Score.company_id == cid)).first()
            if score:
                score.rank = rank
                session.add(score)
        session.commit()

        top = session.exec(
            select(Company, Score).join(Score).order_by(Score.rank).limit(10)
        ).all()
        print("\nRolling 10:")
        for c, sc in top:
            print(f"  #{sc.rank:>2}  {c.name:<30} {sc.total:.2f}")


if __name__ == "__main__":
    run()
