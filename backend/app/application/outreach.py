"""GenerateOutreach application service — delegates to OutreachGenerator port."""
from app.domain.models import CompanyProfile
from app.domain.ports import OutreachGenerator, CompanyRepository


class GenerateOutreach:
    def __init__(self, generator: OutreachGenerator, repo: CompanyRepository) -> None:
        self._generator = generator
        self._repo = repo

    def email(self, profile: CompanyProfile, cases: list[dict]) -> dict:
        return self._generator.email(profile, cases)

    def teaser(self, profile: CompanyProfile, cases: list[dict]) -> dict:
        return self._generator.teaser(profile, cases)
