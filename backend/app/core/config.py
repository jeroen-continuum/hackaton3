"""Application settings, loaded from environment / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_url: str = "sqlite:///./data/app.db"
    data_dir: str = "./data"

    # Max companies to enrich + score per pipeline run. The DB holds every
    # active company, but NBB/VDAB/Wappalyzer cost one API call each, so the
    # filter-selected candidate set is capped before enrichment.
    max_pond_enrich: int = 500

    # Per-enrichment feature flags. When OFF (default), the pipeline reads that
    # enrichment purely from the DB instead of calling its external API, so
    # /companies/rank does zero outbound HTTP. Flip one ON to re-enable its API.
    enable_nbb_financials: bool = False
    enable_vdab_vacancies: bool = False
    enable_wappalyzer_tech: bool = False
    enable_csv_connections: bool = False
    enable_apollo_contacts: bool = False

    apollo_api_key: str = ""
    hunter_api_key: str = ""
    vdab_api_key: str = ""
    wappalyzer_api_key: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"


settings = Settings()
