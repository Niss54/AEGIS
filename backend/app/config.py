"""
AEGIS-CLIMATE Configuration Module
Loads settings from environment variables with production defaults.
"""
from typing import List, Any
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
    ALLOWED_ORIGINS: Any = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    # Service Connections
    MCP_HUB_URL: str = "http://localhost:8001/mcp/invoke"
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql://aegis:aegis_password@localhost:5432/aegis_db"
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8002

    # External APIs & LLM Providers
    OPENMETEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    OPENMETEO_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    MAPBOX_API_TOKEN: str = ""
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    SARVAM_API_KEY: str = ""

    # Thresholds
    ACUTE_RISK_TRIGGER_THRESHOLD: float = 0.65  # Triggers Agent 2 if risk_score > 0.65
    CHRONIC_DAMAGE_THRESHOLD: float = 0.70      # Triggers Agent 3 for high exposure

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_api_status(self) -> dict:
        """Returns live status of configured external AI and geospatial services."""
        return {
            "gemini": {
                "name": "Google Gemini 1.5",
                "configured": bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip()),
                "role": "Agent 3 Policy RAG & Devanagari Civic Alerts"
            },
            "groq": {
                "name": "Groq Llama-3-70B",
                "configured": bool(self.GROQ_API_KEY and self.GROQ_API_KEY.strip()),
                "role": "Sub-500ms Thought Trace Monologue"
            },
            "open_meteo": {
                "name": "Open-Meteo Weather API",
                "configured": True,  # Free tier active by default
                "commercial_key": bool(self.OPENMETEO_API_KEY and self.OPENMETEO_API_KEY.strip()),
                "role": "15-Minute Meteorological Telemetry"
            },
            "mapbox": {
                "name": "Mapbox Vector & Terrain",
                "configured": bool(self.MAPBOX_API_TOKEN and self.MAPBOX_API_TOKEN.strip()),
                "role": "3D High-Res Satellite Rasters"
            },
            "elevenlabs": {
                "name": "ElevenLabs Voice Synthesis",
                "configured": bool(self.ELEVENLABS_API_KEY and self.ELEVENLABS_API_KEY.strip()),
                "role": "Bhasha-AI Vernacular Voice Dispatch"
            },
            "sarvam_ai": {
                "name": "Sarvam AI (Indic Speech)",
                "configured": bool(self.SARVAM_API_KEY and self.SARVAM_API_KEY.strip()),
                "role": "Bhasha-AI Hindi & Regional Neural Speech"
            }
        }


settings = Settings()
