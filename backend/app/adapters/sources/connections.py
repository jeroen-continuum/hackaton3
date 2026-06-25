import csv
import os
from sqlmodel import Session, select

from app.core.config import settings
from app.models.entities import Company as _Company, Connection as _Conn, Employee as _Emp


class DbConnectionProvider:
    """Reads warm connections from the DB by enterprise_number.

    Returns one dict per Employee->Company tie, with the fields the
    warm_connection signal needs (type, end_date) plus display info.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def shared(self, enterprise_number: str) -> list[dict]:
        rows = self._session.exec(
            select(_Conn, _Emp)
            .join(_Company, _Conn.company_id == _Company.id)
            .join(_Emp, _Conn.employee_id == _Emp.id)
            .where(_Company.enterprise_number == enterprise_number)
        ).all()
        return [
            {
                "id": conn.id,
                "employee_id": emp.id,
                "name": emp.name,
                "title": emp.title or "",
                "type": conn.type,
                "relationship": conn.type,
                "start_date": conn.start_date,
                "end_date": conn.end_date,
                "note": conn.note,
            }
            for conn, emp in rows
        ]


class CsvConnectionProvider:
    def shared(self, enterprise_number: str) -> list[dict]:
        path = os.path.join(settings.data_dir, "connections", "warm_connections.csv")
        if not os.path.exists(path):
            return []
        results = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("enterprise_number") == enterprise_number:
                    results.append({
                        "name": row.get("contact_name", ""),
                        "title": row.get("contact_title", ""),
                        "relationship": row.get("relationship", ""),
                        "strength": row.get("strength", ""),
                    })
        return results


class NullConnectionProvider:
    """No-op connections — used when enable_csv_connections is OFF."""
    def shared(self, enterprise_number: str) -> list[dict]:
        return []
