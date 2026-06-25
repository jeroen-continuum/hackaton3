"""Employees + warm-connection endpoints (the only write surface in the app).

A connection is a tie from one of our consultants to a company. Creating one
re-runs the pipeline so the company's warm_connection score (and Rolling 10
rank) reflect the new tie immediately.
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.application.signals import connection_weight
from app.composition import build_container
from app.db.session import get_session
from app.models import Company, Connection, Employee

router = APIRouter(tags=["connections"])


class EmployeeIn(BaseModel):
    name: str
    email: Optional[str] = None
    title: Optional[str] = None


class ConnectionIn(BaseModel):
    employee_id: int
    company_id: int
    type: str = "EMPLOYER"  # EMPLOYER | CLIENT | PERSONAL
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    note: Optional[str] = None


@router.get("/employees")
def list_employees(session: Session = Depends(get_session)):
    return session.exec(select(Employee).order_by(Employee.name)).all()


@router.post("/employees")
def create_employee(body: EmployeeIn, session: Session = Depends(get_session)):
    emp = Employee(name=body.name, email=body.email, title=body.title)
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@router.get("/companies/{company_id}/connections")
def company_connections(company_id: int, session: Session = Depends(get_session)):
    """Ties for a company, with computed strength; sorted strongest-first.

    The first entry is the best introducer. `is_client` is inferred: true if any
    tie is of type CLIENT.
    """
    rows = session.exec(
        select(Connection, Employee)
        .join(Employee, Connection.employee_id == Employee.id)
        .where(Connection.company_id == company_id)
    ).all()
    today = date.today()
    items = [
        {
            "id": conn.id,
            "employee_id": emp.id,
            "employee_name": emp.name,
            "employee_title": emp.title,
            "type": conn.type,
            "start_date": conn.start_date,
            "end_date": conn.end_date,
            "note": conn.note,
            "strength": round(
                connection_weight(
                    {"type": conn.type, "end_date": conn.end_date}, today
                ),
                3,
            ),
        }
        for conn, emp in rows
    ]
    items.sort(key=lambda i: i["strength"], reverse=True)
    return {
        "connections": items,
        "is_client": any(i["type"] == "CLIENT" for i in items),
    }


@router.post("/connections")
def create_connection(body: ConnectionIn, session: Session = Depends(get_session)):
    if not session.get(Employee, body.employee_id):
        raise HTTPException(404, "Employee not found")
    if not session.get(Company, body.company_id):
        raise HTTPException(404, "Company not found")
    conn = Connection(
        employee_id=body.employee_id,
        company_id=body.company_id,
        type=body.type,
        start_date=body.start_date,
        end_date=body.end_date,
        note=body.note,
    )
    session.add(conn)
    session.commit()
    session.refresh(conn)
    # Live re-score: the detail page reads frozen Score rows, so recompute now.
    build_container(session).pipeline.run()
    return conn


@router.delete("/connections/{connection_id}")
def delete_connection(connection_id: int, session: Session = Depends(get_session)):
    conn = session.get(Connection, connection_id)
    if not conn:
        raise HTTPException(404, "Connection not found")
    session.delete(conn)
    session.commit()
    build_container(session).pipeline.run()
    return {"deleted": connection_id}
