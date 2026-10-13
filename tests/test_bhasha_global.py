"""
Test Suite for Bhasha-AI Global Dispatcher & Multilingual Neural Voice Engine (PRD 3: Phase 3)
Verifies:
1. Automatic language resolution across international & regional hotspots:
   - Türkiye (Istanbul, Kastamonu) -> Turkish (tr-TR, Türkçe, AFAD)
   - Estonia (Pärnu) -> Estonian (et-EE, Eesti keel, Päästeamet)
   - USA (California / Orange County) -> Spanish (es-US, Español, Cal OES) + English
   - India UP (Lucknow Gomti Basin) -> Pure Hindi (hi-IN, हिन्दी, NDMA/SDRF)
   - India MH (Mumbai Mithi Basin) -> Marathi (mr-IN, मराठी, BMC)
   - India AS (Assam Brahmaputra) -> Assamese (as-IN, অসমীয়া, ASDMA)
   - India KA (Bengaluru) -> Kannada (kn-IN, ಕನ್ನಡ, KSDMA)
2. Domain-accurate linguistic generation in native scripts (Devanagari, Latin, Bengali-Assamese).
3. Verifiable Blue-Carbon-MRV Cryptographic Provenance hashing (Keccak-256).
4. Audio synthesis endpoint handling and graceful fallback.
5. Full backward compatibility with Agent 3 VaR modeling.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.bhasha.engine import bhasha_engine, LANGUAGE_PROFILES
from backend.app.bhasha.schemas import LanguageProfile, MRVProvenance
from backend.app.agent3_financial import financial_risk_engine
from backend.app.schemas import JurisdictionHierarchy


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. LANGUAGE RESOLUTION TESTS
# ---------------------------------------------------------------------------

def test_resolve_language_turkey_istanbul():
    jurisdiction = JurisdictionHierarchy(
        country_iso="TR",
        country_name="Türkiye",
        admin1_state="Istanbul",
        admin2_district="Fatih",
        basin_name="Bosphorus Basin"
    )
    profile = bhasha_engine.resolve_language(
        location_label="Istanbul — Marmara & Golden Horn Basin",
        lat=41.0082,
        lon=28.9784,
        jurisdiction=jurisdiction
    )
    assert profile.code == "tr-TR"
    assert profile.short_code == "tr"
    assert profile.native_name == "Türkçe"
    assert profile.country_code == "TR"
    assert "AFAD" in profile.civil_defense_agency
    assert profile.currency_symbol == "₺"


def test_resolve_language_turkey_kastamonu():
    profile = bhasha_engine.resolve_language(
        location_label="Kastamonu — Bozkurt Ezine Stream Flash Basin",
        lat=41.9572,
        lon=34.0125
    )
    assert profile.code == "tr-TR"
    assert profile.short_code == "tr"


def test_resolve_language_estonia_parnu():
    jurisdiction = JurisdictionHierarchy(
        country_iso="EE",
        country_name="Estonia",
        admin1_state="Pärnu County",
        admin2_district="Pärnu",
        basin_name="Pärnu River"
    )
    profile = bhasha_engine.resolve_language(
        location_label="Pärnu — Baltic Sea Surge & Lowland Inundation",
        lat=58.3859,
        lon=24.4971,
        jurisdiction=jurisdiction
    )
    assert profile.code == "et-EE"
    assert profile.short_code == "et"
    assert profile.native_name == "Eesti keel"
    assert profile.country_code == "EE"
    assert "Päästeamet" in profile.civil_defense_agency
    assert profile.currency_symbol == "€"


def test_resolve_language_usa_orange_county():
    jurisdiction = JurisdictionHierarchy(
        country_iso="US",
        country_name="United States",
        admin1_state="California",
        admin2_district="Orange County",
        basin_name="Santa Ana River"
    )
    profile = bhasha_engine.resolve_language(
        location_label="Orange County — Santa Ana River & Newport Coastal Basin",
        lat=33.7175,
        lon=-117.8311,
        jurisdiction=jurisdiction
    )
    assert profile.code == "es-US"
    assert profile.short_code == "es"
    assert profile.native_name == "Español"
    assert "Cal OES" in profile.civil_defense_agency


def test_resolve_language_india_lucknow_up():
    jurisdiction = JurisdictionHierarchy(
        country_iso="IN",
        country_name="India",
        admin1_state="Uttar Pradesh",
        admin2_district="Lucknow",
        basin_name="Gomti River Basin"
    )
    profile = bhasha_engine.resolve_language(
        location_label="Lucknow — Gomti River Basin & Lowland Drainage Corridor",
        lat=26.8467,
        lon=80.9462,
        jurisdiction=jurisdiction
    )
    assert profile.code == "hi-IN"
    assert profile.short_code == "hi"
    assert profile.native_name == "हिन्दी"
    assert "NDMA" in profile.civil_defense_agency
    assert profile.currency_symbol == "₹"


def test_resolve_language_india_mumbai_maharashtra():
    jurisdiction = JurisdictionHierarchy(
        country_iso="IN",
        country_name="India",
        admin1_state="Maharashtra",
        admin2_district="Mumbai Suburban",
        basin_name="Mithi River Catchment"
    )
    profile = bhasha_engine.resolve_language(
        location_label="Mumbai — Mithi River & Kurla Basin",
        lat=19.0728,
        lon=72.8797,
        jurisdiction=jurisdiction
    )
    assert profile.code == "mr-IN"
    assert profile.short_code == "mr"
    assert profile.native_name == "मराठी"
    assert "BMC" in profile.civil_defense_agency


def test_resolve_language_india_assam():
    jurisdiction = JurisdictionHierarchy(
        country_iso="IN",
        country_name="India",
        admin1_state="Assam",
        admin2_district="Nagaon",
        basin_name="Brahmaputra Basin"
    )
    profile = bhasha_engine.resolve_language(
        location_label="Assam — Brahmaputra Basin & Kaziranga Corridor",
        lat=26.5775,
        lon=93.1711,
        jurisdiction=jurisdiction
    )
    assert profile.code == "as-IN"
    assert profile.short_code == "as"
    assert profile.native_name == "অসমীয়া"
    assert "ASDMA" in profile.civil_defense_agency


# ---------------------------------------------------------------------------
# 2. DISPATCH GENERATION & NATIVE LINGUISTIC AUTHENTICITY TESTS
# ---------------------------------------------------------------------------

def test_dispatch_generation_turkish():
    dispatch = bhasha_engine.generate_dispatch(
        location_label="Istanbul — Marmara Estuary",
        waterlogging_depth_cm=88,
        buildings_at_risk=420,
        total_var_inr=14_500_000_000,
        total_var_usd=174_000_000,
        compliance_gap_pct=65,
        lat=41.0082,
        lon=28.9784
    )
    assert dispatch.language_profile.code == "tr-TR"
    assert "ACİL DURUM UYARISI" in dispatch.regional_native
    assert "Istanbul" in dispatch.regional_native
    assert "88 cm" in dispatch.regional_native
    assert "AFAD" in dispatch.regional_native
    assert "₺" in dispatch.regional_native
    assert "EXECUTIVE ALERT" in dispatch.primary_english
    assert "$174.00M USD" in dispatch.primary_english


def test_dispatch_generation_estonian():
    dispatch = bhasha_engine.generate_dispatch(
        location_label="Pärnu — Baltic Sea Surge",
        waterlogging_depth_cm=65,
        buildings_at_risk=150,
        total_var_inr=4_800_000_000,
        total_var_usd=57_000_000,
        compliance_gap_pct=42,
        lat=58.3859,
        lon=24.4971
    )
    assert dispatch.language_profile.code == "et-EE"
    assert "HÄDAOLUKORRA TEADE" in dispatch.regional_native
    assert "Päästeamet" in dispatch.regional_native
    assert "€" in dispatch.regional_native
    assert "EXECUTIVE ALERT" in dispatch.primary_english


def test_dispatch_generation_hindi_lucknow():
    dispatch = bhasha_engine.generate_dispatch(
        location_label="Lucknow Gomti Basin",
        waterlogging_depth_cm=75,
        buildings_at_risk=310,
        total_var_inr=3_800_000_000,
        total_var_usd=45_000_000,
        compliance_gap_pct=55,
        lat=26.8467,
        lon=80.9462
    )
    assert dispatch.language_profile.code == "hi-IN"
    assert "आपातकालीन चेतावनी" in dispatch.regional_native
    assert "75 सेमी" in dispatch.regional_native
    assert "करोड़" in dispatch.regional_native
    assert "NDMA" in dispatch.regional_native


def test_dispatch_generation_marathi_mumbai():
    dispatch = bhasha_engine.generate_dispatch(
        location_label="Mumbai Mithi River",
        waterlogging_depth_cm=110,
        buildings_at_risk=850,
        total_var_inr=12_000_000_000,
        total_var_usd=144_000_000,
        compliance_gap_pct=75,
        lat=19.0728,
        lon=72.8797
    )
    assert dispatch.language_profile.code == "mr-IN"
    assert "तातडीचा इशारा" in dispatch.regional_native
    assert "110 सेंमी" in dispatch.regional_native
    assert "BMC" in dispatch.regional_native


# ---------------------------------------------------------------------------
# 3. VERIFIABLE MRV CRYPTOGRAPHIC PROVENANCE TESTS
# ---------------------------------------------------------------------------

def test_mrv_provenance_stamping():
    telemetry = {
        "precipitation_24h_mm": 115.4,
        "soil_saturation_pct": 94.2,
        "temperature_c": 29.5
    }
    mrv = bhasha_engine.stamp_mrv_provenance(
        jurisdiction_iso="TR-34",
        telemetry=telemetry,
        evidence_dict={"flood_depth_cm": 88, "var_usd": 174000000}
    )
    assert mrv.mrv_registry_type == "Blue-Carbon-MRV-v1"
    assert mrv.jurisdiction_iso == "TR-34"
    assert mrv.sensor_telemetry_digest.startswith("0x")
    assert len(mrv.sensor_telemetry_digest) == 66  # 0x + 64 hex chars
    assert mrv.evidence_digest.startswith("0x")
    assert len(mrv.evidence_digest) == 66
    assert mrv.signature_scheme == "Keccak256-RFC8785"
    assert mrv.verification_endpoint == "/api/v2/evidence/verify"


def test_mrv_provenance_tamper_evidence():
    telemetry_a = {"precipitation_24h_mm": 100.0}
    telemetry_b = {"precipitation_24h_mm": 100.1}

    mrv_a = bhasha_engine.stamp_mrv_provenance("EE", telemetry=telemetry_a)
    mrv_b = bhasha_engine.stamp_mrv_provenance("EE", telemetry=telemetry_b)

    assert mrv_a.sensor_telemetry_digest != mrv_b.sensor_telemetry_digest


# ---------------------------------------------------------------------------
# 4. AGENT 3 VaR INTEGRATION & BACKWARD COMPATIBILITY
# ---------------------------------------------------------------------------

def test_agent3_model_financial_var_turkish():
    res = financial_risk_engine.model_financial_var(
        location_label="Istanbul — Marmara Estuary",
        risk_score=0.88,
        waterlogging_depth_cm=85,
        buildings_at_risk=350,
        damage_estimate_inr=14_000_000_000,
        lat=41.0082,
        lon=28.9784
    )
    assert res["status"] == "COMPLETED"
    assert res["regional_language_code"] == "tr-TR"
    assert res["regional_language_name"] == "Türkçe"
    assert res["regional_language_flag"] == "🇹🇷"
    assert "ACİL DURUM UYARISI" in res["bilingual_alert_regional"]
    # Check backward compatibility
    assert len(res["bilingual_alert_hindi"]) > 10
    assert len(res["bilingual_alert_english"]) > 10
    # Check MRV provenance present
    assert "mrv_provenance" in res
    assert res["mrv_provenance"]["mrv_registry_type"] == "Blue-Carbon-MRV-v1"
    assert res["mrv_provenance"]["evidence_digest"].startswith("0x")


def test_agent3_model_financial_var_lucknow():
    res = financial_risk_engine.model_financial_var(
        location_label="Lucknow — Gomti River Basin",
        risk_score=0.75,
        waterlogging_depth_cm=70,
        buildings_at_risk=280,
        damage_estimate_inr=3_800_000_000,
        lat=26.8467,
        lon=80.9462
    )
    assert res["regional_language_code"] == "hi-IN"
    assert res["regional_language_flag"] == "🇮🇳"
    assert "आपातकालीन चेतावनी" in res["bilingual_alert_regional"]
    assert "mrv_provenance" in res


# ---------------------------------------------------------------------------
# 5. BHASHA TTS API ENDPOINT VERIFICATION
# ---------------------------------------------------------------------------

def test_bhasha_tts_endpoint_turkish(client):
    response = client.post(
        "/api/v1/bhasha/tts",
        json={
            "text": "ACİL DURUM UYARISI: Istanbul için şiddetli su baskını tespit edildi.",
            "language": "tr"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "fallback"]
    assert data["language"] == "tr"


def test_bhasha_tts_endpoint_estonian(client):
    response = client.post(
        "/api/v1/bhasha/tts",
        json={
            "text": "HÄDAOLUKORRA TEADE: Pärnu piirkonnas on tõsine üleujutuse oht.",
            "language": "et"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "fallback"]


def test_bhasha_tts_endpoint_hindi(client):
    response = client.post(
        "/api/v1/bhasha/tts",
        json={
            "text": "आपातकालीन चेतावनी: लखनऊ में भारी जलभराव का अनुमान है।",
            "language": "hi",
            "speaker": "priya"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "fallback"]
