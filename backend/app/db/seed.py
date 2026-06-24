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
    SolutionCase(
        sector="financial_services",
        title="AI-driven credit risk scoring at mid-market bank",
        summary="Replaced manual spreadsheet scoring with ML model reducing decision time from 3 days to 4 hours while improving accuracy by 22%.",
        impact_metric="-85% decision time, +22% accuracy",
    ),
    SolutionCase(
        sector="financial_services",
        title="Automated regulatory reporting for insurance firm",
        summary="Built XBRL/Solvency II reporting pipeline eliminating 40 FTE-hours per quarter of manual data assembly.",
        impact_metric="-40 FTE-hours/quarter",
    ),
    SolutionCase(
        sector="professional_services",
        title="Intelligent contract analysis for legal firm",
        summary="LLM-powered contract review cutting review time by 60% and flagging non-standard clauses automatically.",
        impact_metric="-60% review time",
    ),
    SolutionCase(
        sector="professional_services",
        title="Knowledge management platform for consulting firm",
        summary="RAG-based internal search over 15 years of project deliverables, reducing research time by 70%.",
        impact_metric="-70% research time",
    ),
    SolutionCase(
        sector="logistics",
        title="Predictive maintenance for fleet operator",
        summary="IoT + ML model predicting truck breakdowns 72 hours ahead, reducing unplanned downtime by 35%.",
        impact_metric="-35% unplanned downtime",
    ),
    SolutionCase(
        sector="manufacturing",
        title="AI quality control for food manufacturer",
        summary="Computer vision defect detection on production line achieving 99.2% accuracy vs 94% manual inspection.",
        impact_metric="+5.2pp quality rate",
    ),
]


def seed_solution_cases(session: Session) -> None:
    """Seed WiiPlus solution reference cases for LLM outreach grounding."""
    for case_data in SOLUTION_CASES:
        existing = session.exec(
            select(SolutionCase)
            .where(SolutionCase.sector == case_data.sector)
            .where(SolutionCase.title == case_data.title)
        ).first()
        if existing is None:
            case = SolutionCase(
                sector=case_data.sector,
                title=case_data.title,
                summary=case_data.summary,
                impact_metric=case_data.impact_metric,
            )
            session.add(case)
    session.commit()


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
