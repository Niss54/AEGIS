"""
AEGIS-CLIMATE Configuration Module
Loads settings from environment variables with production defaults.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "AEGIS-CLIMATE"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    # Service Connections
    MCP_HUB_URL: str = "http://localhost:8001/mcp/invoke"
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql://aegis:aegis_password@localhost:5432/aegis_db"
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8002

    # External APIs
    OPENMETEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Thresholds
    ACUTE_RISK_TRIGGER_THRESHOLD: float = 0.65  # Triggers Agent 2 if risk_score > 0.65
    CHRONIC_DAMAGE_THRESHOLD: float = 0.70      # Triggers Agent 3 for high exposure

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
