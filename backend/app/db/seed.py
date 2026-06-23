"""Seed reference data + one fully-worked demo company (the vertical slice).

Run: python -m app.db.seed
Lets the whole stack be demoed before any real connector exists.
"""
from sqlmodel import Session, select

from app.db.session import engine, init_db
from app.models import (
    Company, FinancialData, Contact, Vacancy, TechStack, Score,
    OutreachAsset, SolutionCase,
)

SOLUTION_CASES = [
    SolutionCase(sector="Finance", title="Claims triage automation",
                 summary="AI-assisted document intake cut manual handling.",
                 impact_metric="-30% manual work"),
    SolutionCase(sector="Professional Services", title="Proposal generation copilot",
                 summary="Generative drafting of client proposals from templates.",
                 impact_metric="+18% throughput"),
    SolutionCase(sector="Industry", title="Predictive maintenance",
                 summary="Sensor data models predicting line downtime.",
                 impact_metric="-22% downtime"),
]


def seed() -> None:
    init_db()
    with Session(engine) as s:
        if s.exec(select(Company)).first():
            print("DB already seeded; skipping.")
            return

        for sc in SOLUTION_CASES:
            s.add(sc)

        demo = Company(
            enterprise_number="0123456789", name="Demo Finance NV", region="BE",
            nace_code="6419", sector="Finance", website="demo-finance.be",
            address="Brussels, BE", stage="scored",
        )
        s.add(demo)
        s.commit()
        s.refresh(demo)

        s.add(FinancialData(company_id=demo.id, employees=240, revenue=85_000_000,
                            ebitda=9_500_000, fiscal_year=2024))
        s.add(Contact(company_id=demo.id, name="Jane Peeters", title="CFO",
                      email="jane.peeters@demo-finance.be", is_buyer_persona=True))
        s.add(Vacancy(company_id=demo.id, title="IT Manager (m/v)",
                      url="https://vdab.be/x", is_it_role=True))
        s.add(TechStack(company_id=demo.id,
                        technologies=["AS400", "On-prem Exchange", "Excel macros"],
                        legacy_score=0.8))
        s.add(Score(company_id=demo.id, total=0.87, rank=1, breakdown={
            "buyer_intent": 0.9, "impact_potential": 0.85, "financial_fit": 0.8,
            "sector_fit": 1.0, "warm_connection": 0.7,
        }))
        s.add(OutreachAsset(
            company_id=demo.id,
            email_subject="De nieuwe lead voor Demo Finance NV",
            email_body="Hi Jane, peers in finance cut 30% manual claims work with AI...",
            teaser_title="Three things to know about AI in Finance",
            teaser_preview="1. Claims triage is being automated end-to-end...",
            teaser_full="(full report unlocked after contact details)",
        ))
        s.commit()
        print(f"Seeded reference cases + demo company id={demo.id}")


if __name__ == "__main__":
    seed()
