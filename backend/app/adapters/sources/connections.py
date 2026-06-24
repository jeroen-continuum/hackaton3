import csv
import os
from app.core.config import settings


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
