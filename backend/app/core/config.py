"""Application settings, loaded from environment / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_url: str = "sqlite:///./data/app.db"
    data_dir: str = "./data"

    apollo_api_key: str = ""
    hunter_api_key: str = ""
    vdab_api_key: str = ""
    wappalyzer_api_key: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"


settings = Settings()
