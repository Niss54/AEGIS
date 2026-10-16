"""
Bhasha-AI Multilingual Schemas
Defines language profiles, MRV cryptographic provenance, and localized dispatch payloads.
Supports Turkish, Estonian, Spanish, English, Hindi, Marathi, Assamese, and other regional languages.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class LanguageProfile(BaseModel):
    """Linguistic and regional metadata profile for an affected jurisdiction."""
    code: str = Field(..., description="BCP 47 language tag (e.g. tr-TR, et-EE, hi-IN)")
    short_code: str = Field(..., description="2-letter ISO language code (e.g. tr, et, hi)")
    name: str = Field(..., description="English name of language (e.g. Turkish, Estonian)")
    native_name: str = Field(..., description="Autonym in native script (e.g. Türkçe, Eesti keel, हिन्दी)")
    script: str = Field(default="Latin", description="Writing script (Latin, Devanagari, Assamese, etc.)")
    country_code: str = Field(..., description="ISO 3166-1 alpha-2 country code (TR, EE, US, IN)")
    flag_emoji: str = Field(..., description="National or jurisdiction flag emoji")
    civil_defense_agency: str = Field(..., description="Responsible civic authority (AFAD, Päästeamet, NDMA)")
    primary_tts_engine: str = Field(default="browser", description="Primary TTS provider (sarvam, bhashini, elevenlabs, browser)")
    currency_symbol: str = Field(default="₹", description="Local currency symbol")
    currency_code: str = Field(default="INR", description="Local currency code")


class MRVProvenance(BaseModel):
    """
    Verifiable Measurement, Reporting & Verification (MRV) Provenance Stamp.
    Inspired by Blue-Carbon-MRV and Yale OpenLab OpenClimate cryptographic evidence.
    """
    mrv_registry_type: str = Field(default="Blue-Carbon-MRV-v1", description="MRV schema type")
    bundle_id: str = Field(..., description="Unique telemetry and dispatch bundle identifier")
    jurisdiction_iso: str = Field(..., description="Jurisdiction ISO code (e.g. TR-34, EE-67, US-CA, IN-UP)")
    timestamp_utc: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    sensor_telemetry_digest: str = Field(..., description="0x-prefixed Keccak-256 hash of normalized weather telemetry")
    evidence_digest: str = Field(..., description="0x-prefixed Keccak-256 hash of complete evidence bundle")
    signature_scheme: str = Field(default="Keccak256-RFC8785", description="Cryptographic hashing and canonicalization scheme")
    verification_endpoint: str = Field(default="/api/v2/evidence/verify", description="Audit verifier endpoint")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional verifiable telemetry metadata")


class BhashaDispatchResult(BaseModel):
    """Complete dual-language civic dispatch with cryptographic verification."""
    primary_english: str = Field(..., description="Universal English executive emergency broadcast")
    regional_native: str = Field(..., description="Hyper-localized native language emergency broadcast")
    language_profile: LanguageProfile = Field(..., description="Active language profile")
    mrv_provenance: MRVProvenance = Field(..., description="Cryptographic telemetry and provenance stamp")
    voice_engine_used: str = Field(default="browser_speech", description="Voice synthesis provider used")
    audio_payload: Optional[Dict[str, Any]] = Field(None, description="Synthesized neural audio payload if available")
    audio_fallback: str = Field(default="browser_speech", description="Fallback audio mechanism (Web Speech API)")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
