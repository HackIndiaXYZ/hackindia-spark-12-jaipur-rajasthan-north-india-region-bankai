import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AquaSentinel Water Monitoring API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./aquasentinel.db"

    # External APIs
    NWIC_API_KEY: Optional[str] = None
    DATA_GOV_IN_API_KEY: Optional[str] = None

    # AI / LLM Configuration
    LLM_PROVIDER: str = "mock"  # default mock for offline hackathon dev
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
