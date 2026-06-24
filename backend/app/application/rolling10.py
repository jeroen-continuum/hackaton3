"""Rolling10 application service — exposes top-10 and mark-contacted use-cases."""
from app.domain.ports import CompanyRepository


class Rolling10:
    def __init__(self, repo: CompanyRepository) -> None:
        self._repo = repo

    def get_top10(self) -> list:
        return self._repo.get_top10()

    def mark_contacted(self, enterprise_number: str) -> None:
        self._repo.mark_contacted(enterprise_number)
