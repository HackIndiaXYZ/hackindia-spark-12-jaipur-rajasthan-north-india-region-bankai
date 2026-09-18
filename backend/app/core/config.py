import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "aquasentinel.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "AquaSentinel Water Monitoring API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"

    # External APIs
    NWIC_API_KEY: Optional[str] = None
    DATA_GOV_IN_API_KEY: Optional[str] = None

    # AI / LLM Configuration
    LLM_PROVIDER: str = "mock"  # default mock for offline hackathon dev
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"

    # Gemini AI Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Hardware (ESP32 FSR402) Configuration
    ESP32_SERIAL_PORT: Optional[str] = None  # Reads ESP32_SERIAL_PORT env var
    ESP32_BAUD_RATE: int = 115200
    ESP32_SENSOR_ID: str = "B2"
    ESP32_ZONE_ID: str = "Zone_B"
    ESP32_SEGMENT_ID: str = "B2-B3"
    ESP32_ALERT_THRESHOLD: int = 50
    ESP32_PRESSURE_MIN: float = 0.0
    ESP32_PRESSURE_MAX: float = 5.0
    ESP32_STALE_THRESHOLD_SEC: float = 5.0


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

