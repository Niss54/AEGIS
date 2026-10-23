"""
Phase 5 Test Suite: Executive VC Documentation, Pitch Deck & Global Climate Scaling Strategy
IEEE ClimateChain 2026 — Track 4 (Global Planetary Resilience)
"""
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_executive_vc_memo_document_integrity():
    """Verify docs/EXECUTIVE_VC_MEMO.md exists with all institutional VC investment sections."""
    memo_path = Path("docs/EXECUTIVE_VC_MEMO.md")
    assert memo_path.exists(), "docs/EXECUTIVE_VC_MEMO.md is missing!"

    text = memo_path.read_text(encoding="utf-8")
    assert "Series Seed" in text
    assert "$2.5M USD" in text
    assert "$34.2B" in text  # TAM
    assert "$4.8B" in text   # SAM
    assert "$180M" in text   # SOM
    assert "$120,000 / year" in text  # Unit economics ACV
    assert "91.5%" in text   # Gross margin
    assert "Google Cloud Run" in text
    assert "Google Vertex AI" in text
    assert "Gemini 2.0 Flash" in text
    assert "Marina Barrage" in text
    assert "IEEE ClimateChain Global Demonstration" in text
    assert "Team Syntrix" in text


def test_pitch_deck_slides_count_and_google_cloud_elevation():
    """Verify docs/PITCH_DECK.md contains all 11 slides including Google Cloud & Singapore."""
    deck_path = Path("docs/PITCH_DECK.md")
    assert deck_path.exists(), "docs/PITCH_DECK.md is missing!"

    text = deck_path.read_text(encoding="utf-8")
    assert "Slides:** 11" in text
    assert "SLIDE 1: Title & Vision" in text
    assert "SLIDE 2: The Problem" in text
    assert "SLIDE 3: The Architecture" in text
    assert "SLIDE 4: Technical Depth" in text
    assert "SLIDE 5: Market Opportunity" in text
    assert "SLIDE 6 — THE INTELLIGENCE LAYER" in text
    assert ("SLIDE 7 — WHAT MAKES AEGIS-CLIMATE DIFFERENT" in text or "SLIDE 7 — WHAT MAKES AEGIS-CLIMATE DIFFERENT" in text)
    assert "SLIDE 8 — IMPACT & SCALABILITY" in text
    assert "SLIDE 9 — CLOSING (The Future)" in text
    assert "SLIDE 10: Google Cloud Decisive Advantage & Hackathon Edge" in text
    assert "SLIDE 11: Global Climate Scaling Strategy & JAPAC Expansion Roadmap" in text


def test_rest_api_get_vc_memo():
    """Verify GET /api/v1/executive/vc-memo returns institutional investment metrics."""
    res = client.get("/api/v1/executive/vc-memo")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert data["company_name"] in ["AEGIS-CLIMATE Inc.", "AEGIS-CLIMATE Inc."]
    assert "Series Seed" in data["funding_round"]
    assert data["market_sizing"]["tam_global_climate_risk_usd_billions"] == 34.2
    assert data["market_sizing"]["sam_japac_municipal_usd_billions"] == 4.8
    assert data["market_sizing"]["som_year_1_to_3_usd_millions"] == 180.0
    assert data["unit_economics"]["annual_contract_value_usd"] == 120000
    assert data["unit_economics"]["gross_profit_margin_pct"] == 91.5
    assert len(data["competitive_moats"]) >= 5
    assert "google_cloud_run" in data["google_cloud_alignment"]
    assert "google_vertex_ai" in data["google_cloud_alignment"]
    assert len(data["regulatory_tailwinds"]) >= 3
    assert len(data["singapore_grand_finale_playbook"]) >= 3


def test_rest_api_get_pitch_deck():
    """Verify GET /api/v1/executive/pitch-deck returns 11 slides metadata."""
    res = client.get("/api/v1/executive/pitch-deck")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert data["total_slides"] == 11
    assert data["format"] == "16:9 Widescreen"
    assert len(data["slides"]) == 11
    assert data["slides"][9]["slide_number"] == 10
    assert "Google Cloud" in data["slides"][9]["title"]
    assert data["slides"][10]["slide_number"] == 11
    assert "Singapore" in data["slides"][10]["title"]


def test_rest_api_get_singapore_strategy():
    """Verify GET /api/v1/executive/singapore-strategy returns Marina Barrage live plan."""
    res = client.get("/api/v1/executive/singapore-strategy")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert "Singapore" in data["venue"]
    assert data["live_demo_location"]["name"] == "Singapore — Marina Barrage Catchment"
    assert data["live_demo_location"]["lat"] == 1.2800
    assert data["live_demo_location"]["lon"] == 103.8636
    assert data["live_demo_location"]["simulated_rainfall_mm"] == 150.0
    assert len(data["four_minute_pitch_arc"]) == 4
