"""Seed reference data + 10 demo companies (the vertical slice).

Run: python -m app.db.seed
Lets the whole stack be demoed before any real connector exists.
"""
from sqlmodel import Session, select

from app.db.session import engine, init_db
from app.models import (
    Company, Score, SolutionCase,
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

DEMO_COMPANIES = [
    {"enterprise_number": "0411123001", "name": "Argenta Spaarbank NV", "region": "BE", "nace_code": "6419", "sector": "financial_services", "website": "argenta.be"},
    {"enterprise_number": "0411123002", "name": "Belfius Insurance SA", "region": "BE", "nace_code": "6512", "sector": "financial_services", "website": "belfius.be"},
    {"enterprise_number": "0411123003", "name": "AG Real Estate NV", "region": "BE", "nace_code": "6612", "sector": "financial_services", "website": "agrealestate.be"},
    {"enterprise_number": "0411123004", "name": "Deloitte Belgium CVBA", "region": "BE", "nace_code": "6920", "sector": "professional_services", "website": "deloitte.com/be"},
    {"enterprise_number": "0411123005", "name": "PwC Belgium BV", "region": "BE", "nace_code": "6920", "sector": "professional_services", "website": "pwc.be"},
    {"enterprise_number": "0411123006", "name": "McKinsey Belgium SPRL", "region": "BE", "nace_code": "7022", "sector": "professional_services", "website": "mckinsey.com/be-en"},
    {"enterprise_number": "0411123007", "name": "Synergie Belgium NV", "region": "BE", "nace_code": "7810", "sector": "employment", "website": "synergie.be"},
    {"enterprise_number": "0411123008", "name": "Adecco Group Belgium", "region": "BE", "nace_code": "7820", "sector": "employment", "website": "adecco.be"},
    {"enterprise_number": "0411123009", "name": "Acerta Consult NV", "region": "BE", "nace_code": "6910", "sector": "professional_services", "website": "acerta.be"},
    {"enterprise_number": "0411123010", "name": "BNP Paribas Fortis NV", "region": "BE", "nace_code": "6419", "sector": "financial_services", "website": "bnpparibasfortis.be"},
]

DEMO_SCORES = [
    {"rank": 1,  "total": 0.91, "breakdown": {"buyer_intent": 0.95, "impact_potential": 0.90, "financial_fit": 1.0, "sector_fit": 1.0, "warm_connection": 0.7}},
    {"rank": 2,  "total": 0.87, "breakdown": {"buyer_intent": 0.85, "impact_potential": 0.88, "financial_fit": 1.0, "sector_fit": 1.0, "warm_connection": 0.6}},
    {"rank": 3,  "total": 0.83, "breakdown": {"buyer_intent": 0.80, "impact_potential": 0.85, "financial_fit": 0.8, "sector_fit": 1.0, "warm_connection": 0.7}},
    {"rank": 4,  "total": 0.80, "breakdown": {"buyer_intent": 0.75, "impact_potential": 0.82, "financial_fit": 0.8, "sector_fit": 1.0, "warm_connection": 0.8}},
    {"rank": 5,  "total": 0.77, "breakdown": {"buyer_intent": 0.70, "impact_potential": 0.80, "financial_fit": 0.6, "sector_fit": 1.0, "warm_connection": 0.9}},
    {"rank": 6,  "total": 0.74, "breakdown": {"buyer_intent": 0.85, "impact_potential": 0.70, "financial_fit": 0.8, "sector_fit": 1.0, "warm_connection": 0.5}},
    {"rank": 7,  "total": 0.70, "breakdown": {"buyer_intent": 0.65, "impact_potential": 0.75, "financial_fit": 0.8, "sector_fit": 0.5, "warm_connection": 0.6}},
    {"rank": 8,  "total": 0.65, "breakdown": {"buyer_intent": 0.60, "impact_potential": 0.68, "financial_fit": 0.6, "sector_fit": 0.5, "warm_connection": 0.7}},
    {"rank": 9,  "total": 0.61, "breakdown": {"buyer_intent": 0.55, "impact_potential": 0.65, "financial_fit": 0.6, "sector_fit": 0.5, "warm_connection": 0.6}},
    {"rank": 10, "total": 0.57, "breakdown": {"buyer_intent": 0.50, "impact_potential": 0.60, "financial_fit": 0.4, "sector_fit": 1.0, "warm_connection": 0.5}},
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
        seed_solution_cases(s)
        if s.exec(select(Company)).first():
            print("DB already seeded; skipping companies.")
            return
        for i, cd in enumerate(DEMO_COMPANIES):
            company = Company(**cd)
            s.add(company)
            s.flush()  # get company.id
            score_data = DEMO_SCORES[i]
            s.add(Score(
                company_id=company.id,
                total=score_data["total"],
                rank=score_data["rank"],
                breakdown=score_data["breakdown"],
                contacted=False,
            ))
        s.commit()
        print(f"Seeded {len(DEMO_COMPANIES)} demo companies + solution cases.")


if __name__ == "__main__":
    seed()
