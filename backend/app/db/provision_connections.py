"""Provision fake employees + warm connections for the demo.

We are a 200-consultant firm. Each consultant may have worked at (EMPLOYER) or
delivered a project to (CLIENT) some prospects, or just know someone there
(PERSONAL). This script invents that history so the warm_connection score and
the "who do we know here" UI have something to show.

Two deliberate touches make the data realistic:
  * Preferential attachment — a ~17% "client set" of companies is far more
    likely to be picked, so clients accumulate several ties while most companies
    have none (rich-get-richer).
  * Ties only land on companies the pipeline actually scores (the ICP candidate
    pool), otherwise the warm signal would never surface on the Rolling 10.

Deterministic (seed 42) and idempotent (wipes Employee/Connection first).

Run: python -m app.db.provision_connections
"""
import random
from datetime import date, timedelta

from sqlalchemy import delete
from sqlmodel import Session, select

from app.adapters.sources.db_source import apply_financial_filters, apply_icp_filters
from app.core.config import settings
from app.db.session import engine, init_db
from app.domain.filters import IcpFilter
from app.models import Company, Connection, Employee

# ponytail: demo-tuned knobs — tweak here, not in the algorithm below.
N_EMPLOYEES = 200
CLIENT_FRACTION = 0.17        # share of the candidate pool treated as clients
CLIENT_PICK_WEIGHT = 10       # how much likelier a client is to be picked vs other
TIES_PER_EMPLOYEE = ([0, 1, 2, 3, 4], [0.15, 0.35, 0.30, 0.15, 0.05])
ONGOING_PROB = 0.15           # a current/ongoing engagement (no end date)

_FIRST = ["Jan", "Sara", "Tom", "Lien", "Karel", "Eva", "Pieter", "Marie", "Bram",
          "Sofie", "Wout", "Nele", "Joris", "Anke", "Bart", "Lotte", "Dries",
          "Femke", "Stijn", "Hanne", "Koen", "Inge", "Maarten", "Elke"]
_LAST = ["Peeters", "Janssens", "Maes", "Jacobs", "Mertens", "Willems", "Claes",
         "Goossens", "Wouters", "De Smet", "Dupont", "Lemmens", "Aerts",
         "Hermans", "Van Damme", "De Clerck", "Coppens", "Vermeulen"]
_TITLES = (["Consultant"] * 5 + ["Senior Consultant"] * 4 + ["Manager"] * 2 + ["Partner"])
_PERSONAL_NOTES = ["Knows the CFO", "Former colleague works there",
                   "University friend on the IT team", "Met at a conference",
                   "Family contact in management"]


def _candidate_company_ids(session: Session) -> list[int]:
    """Company ids the pipeline actually scores under the default ICP.

    Mirrors DbCompanySource.load_pond exactly: the first `max_pond_enrich`
    ICP matches ordered by id, then narrowed to those passing the financial
    filter (the stage that drops the rest). Ties land only on these companies,
    so the warm signal is guaranteed to show on the Rolling 10.
    """
    icp = IcpFilter.default()
    pool_ids = list(
        session.exec(
            apply_icp_filters(select(Company.id), icp)
            .order_by(Company.id)
            .limit(settings.max_pond_enrich)
        ).all()
    )
    scored = set(
        session.exec(
            apply_financial_filters(apply_icp_filters(select(Company.id), icp), icp)
            .where(Company.id.in_(pool_ids))
        ).all()
    )
    return [cid for cid in pool_ids if cid in scored]


def _pick_type(is_client: bool, rng: random.Random) -> str:
    if is_client:
        return rng.choices(["CLIENT", "EMPLOYER", "PERSONAL"], [0.7, 0.2, 0.1])[0]
    return rng.choices(["EMPLOYER", "PERSONAL", "CLIENT"], [0.7, 0.2, 0.1])[0]


def _career_dates(n: int, rng: random.Random, today: date) -> list[tuple]:
    """n non-overlapping (start, end) windows walking backwards from ~now.

    The most recent window may be ongoing (end=None). Each is 1-6 years long,
    separated by a 0-1 year gap.
    """
    windows: list[tuple] = []
    cursor = today - timedelta(days=rng.randint(0, 3 * 365))  # some are between jobs
    for i in range(n):
        end = None if (i == 0 and rng.random() < ONGOING_PROB) else cursor
        duration = timedelta(days=rng.randint(365, 6 * 365))
        ref = end or cursor
        start = ref - duration
        windows.append((start, end))
        cursor = start - timedelta(days=rng.randint(0, 365))  # gap before previous job
    return windows


def provision(session: Session) -> tuple[int, int]:
    rng = random.Random(42)

    # Idempotent: wipe in FK order (connections reference employees).
    session.exec(delete(Connection))
    session.exec(delete(Employee))
    session.commit()

    pool = _candidate_company_ids(session)
    if not pool:
        raise SystemExit("No candidate companies — run the KBO load + seed_financials first.")
    client_set = set(rng.sample(pool, max(1, int(len(pool) * CLIENT_FRACTION))))
    weights = [CLIENT_PICK_WEIGHT if cid in client_set else 1 for cid in pool]

    employees = [
        Employee(
            name=f"{rng.choice(_FIRST)} {rng.choice(_LAST)}",
            email=None,
            title=rng.choice(_TITLES),
        )
        for _ in range(N_EMPLOYEES)
    ]
    session.add_all(employees)
    session.flush()  # populate ids without ending the transaction

    today = date.today()
    n_conns = 0
    for emp in employees:
        n_ties = rng.choices(*TIES_PER_EMPLOYEE)[0]
        if not n_ties:
            continue
        # Distinct target companies for this employee.
        targets: list[int] = []
        guard = 0
        while len(targets) < n_ties and guard < n_ties * 10:
            cid = rng.choices(pool, weights)[0]
            if cid not in targets:
                targets.append(cid)
            guard += 1

        typed = [(cid, _pick_type(cid in client_set, rng)) for cid in targets]
        dated = [t for t in typed if t[1] in ("EMPLOYER", "CLIENT")]
        windows = _career_dates(len(dated), rng, today)

        di = 0
        for cid, ctype in typed:
            if ctype == "PERSONAL":
                conn = Connection(employee_id=emp.id, company_id=cid, type="PERSONAL",
                                  note=rng.choice(_PERSONAL_NOTES))
            else:
                start, end = windows[di]
                di += 1
                conn = Connection(employee_id=emp.id, company_id=cid, type=ctype,
                                  start_date=start, end_date=end)
            session.add(conn)
            n_conns += 1

    session.commit()
    return len(employees), n_conns


if __name__ == "__main__":
    init_db()
    with Session(engine) as s:
        emps, conns = provision(s)
        print(f"Provisioned {emps} employees and {conns} warm connections.")
