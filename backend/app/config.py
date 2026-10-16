"""
AEGIS-CLIMATE Configuration Module
Loads settings from environment variables with production defaults.
Conforms to PRD 2: E-008 Typed configuration, validation, and secret hygiene.
"""
from typing import List, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import os


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "AEGIS-CLIMATE"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"  # development | test | staging | production
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS Settings - Strict origins for production readiness
    ALLOWED_ORIGINS: Any = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
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

    # Blockchain Settings (Polygon Amoy Testnet & Local EVM)
    POLYGON_AMOY_RPC: str = "https://rpc-amoy.polygon.technology"
    LOCAL_CHAIN_RPC: str = "http://127.0.0.1:8545"
    CHAIN_RPC_URL: str = "https://rpc-amoy.polygon.technology"
    CHAIN_ID: int = 80002  # Polygon Amoy
    LOCAL_CHAIN_ID: int = 31337  # Hardhat / Anvil
    ALLOWED_CHAIN_IDS: List[int] = [80002, 31337, 1337]
    CONFIRMATION_BLOCKS: int = 2
    AEGIS_RISK_LEDGER_ADDRESS: str = "0x89C57973B8e72faFE2c510D12E6B1D0bB5d8C971"
    EVIDENCE_REGISTRY_ADDRESS: str = "0x89C57973B8e72faFE2c510D12E6B1D0bB5d8C971"
    REGISTRY_CONTRACT_ADDRESS: str = "0x89C57973B8e72faFE2c510D12E6B1D0bB5d8C971"
    DISASTER_BOND_ADDRESS: str = "0x4b7868D9C0632a6773F2f89D5276B8E00B29b87B"
    CARBON_FLOOD_CREDIT_ADDRESS: str = "0x16b04D2e2051664C72B9a221f7B5A795eA0A8F25"
    BACKEND_WALLET_PRIVATE_KEY: Optional[str] = None
    BACKEND_WALLET_ADDRESS: str = "0x356345B6522c06F48fAc339CAbCfe7fe88f8d95D"

    # IPFS Pinata Settings
    PINATA_JWT: Optional[str] = None
    PINATA_API_KEY: Optional[str] = None
    PINATA_SECRET_KEY: Optional[str] = None
    IPFS_GATEWAY_URL: str = "https://gateway.pinata.cloud/ipfs/"

    # Evidence & Cryptographic Verification Settings
    EVIDENCE_SCHEMA_VERSION: str = "1.0.0"
    CANONICALIZATION_VERSION: str = "aegis-canonical-json-v1"
    HASH_ALGORITHM: str = "keccak256"

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
            },
            "blockchain": {
                "name": "Polygon Amoy Testnet",
                "configured": bool(self.CHAIN_RPC_URL),
                "chain_id": self.CHAIN_ID,
                "role": "On-chain Risk & Evidence Anchoring"
            }
        }


settings = Settings()
