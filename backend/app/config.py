from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./pharmacovigilance.db"
    gemini_api_key: Optional[str] = None
    reviewer_secret_key: str = "med_safety_2026"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
