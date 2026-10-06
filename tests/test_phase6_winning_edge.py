"""
Phase 6 Winning Edge Verification Suite for AEGIS-CLIMATE
Validates Executive Briefing JSON and HTML endpoints, What-If stress simulation extremes,
Bhasha-AI bilingual verification, and submission documentation artifacts.
"""
import sys
import os
import re
from pathlib import Path
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_phase6_executive_briefing_json():
    """Verify C-Suite Executive Briefing JSON endpoint returns complete structured report."""
    # First trigger an analysis event
    res_ana = client.post("/api/v1/analyze", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai — Mithi River & Kurla Basin",
        "radius_km": 10.0,
        "simulated_additional_rain_mm": 95.0,
        "simulated_saturation_pct_override": 88.0
    })
    assert res_ana.status_code == 200
    evt = res_ana.json()
    event_id = evt["event_id"]

    # Now request the executive briefing for this event
    res = client.get(f"/api/v1/events/{event_id}/executive-briefing")
    assert res.status_code == 200
    briefing = res.json()

    assert briefing["event_id"] == event_id
    assert "briefing_id" in briefing
    assert "prepared_for" in briefing
    assert "executive_summary" in briefing
    assert "physical_risk" in briefing
    assert "geospatial_exposure" in briefing
    assert "financial_var" in briefing
    assert "bilingual_alerts" in briefing
    assert len(briefing["recommended_actions"]) >= 1


def test_phase6_executive_briefing_html_printable():
    """Verify printable A4 PDF/HTML executive briefing endpoint."""
    res = client.get("/api/v1/events/latest/executive-briefing/html")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    html_content = res.text

    assert "<!DOCTYPE html>" in html_content
    assert "AEGIS-CLIMATE EXECUTIVE BRIEFING" in html_content
    assert "@page { size: A4; margin: 20mm; }" in html_content
    assert "window.print()" in html_content
    assert "Team Syntrix" in html_content


def test_phase6_what_if_stress_comparison():
    """Verify system differentiates between nominal dry weather and cloudburst anomaly."""
    # Test Nominal Dry Scenario
    res_dry = client.post("/api/v1/analyze", json={
        "lat": 26.9124,
        "lon": 75.7873,
        "location_name": "Jaipur Semi-Arid Zone",
        "simulated_additional_rain_mm": 0.0,
        "simulated_saturation_pct_override": 20.0
    })
    assert res_dry.status_code == 200
    data_dry = res_dry.json()
    assert data_dry["agent1"]["risk_score"] < 0.65
    assert data_dry["agent1"]["triggered_chronic"] is False

    # Test Cloudburst Catastrophe Scenario
    res_surge = client.post("/api/v1/analyze", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai — Mithi River & Kurla Basin",
        "simulated_additional_rain_mm": 140.0,
        "simulated_saturation_pct_override": 96.0
    })
    assert res_surge.status_code == 200
    data_surge = res_surge.json()
    assert data_surge["agent1"]["risk_score"] > 0.75
    assert data_surge["agent1"]["triggered_chronic"] is True
    assert data_surge["agent2"] is not None
    assert data_surge["agent3"] is not None


def test_phase6_bhasha_ai_devanagari_verification():
    """Verify Bhasha-AI alerts contain genuine Devanagari script for Hindi responders."""
    res = client.post("/api/v1/analyze", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai — Mithi River & Kurla Basin",
        "simulated_additional_rain_mm": 110.0,
        "simulated_saturation_pct_override": 95.0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["agent3"] is not None

    hindi_alert = data["agent3"]["bilingual_alert_hindi"]
    english_alert = data["agent3"]["bilingual_alert_english"]

    assert hindi_alert is not None
    assert english_alert is not None

    # Check for Devanagari Unicode block (\u0900 to \u097F)
    has_devanagari = bool(re.search(r"[\u0900-\u097F]", hindi_alert))
    assert has_devanagari, f"Expected Devanagari text in Hindi alert, got: {hindi_alert}"


def test_phase6_submission_artifacts():
    """Verify Pitch Deck and Video Demo Script exist and have all required sections."""
    pitch_deck = Path("docs/PITCH_DECK.md")
    demo_script = Path("docs/DEMO_SCRIPT.md")

    assert pitch_deck.exists(), "docs/PITCH_DECK.md is missing!"
    assert demo_script.exists(), "docs/DEMO_SCRIPT.md is missing!"

    pd_text = pitch_deck.read_text(encoding="utf-8")
    assert "SLIDE 1: Title & Vision" in pd_text
    assert "SLIDE 2: The Problem" in pd_text
    assert "SLIDE 3: The Architecture" in pd_text
    assert "SLIDE 4: Technical Depth" in pd_text
    assert "SLIDE 5: Market Opportunity" in pd_text

    ds_text = demo_script.read_text(encoding="utf-8")
    assert "SCENE 1: The Hook & The Problem" in ds_text
    assert "SCENE 3: The Autonomous 3-Agent Cascade in Action" in ds_text
    assert "SCENE 4: Bhasha-AI Voice Dispatch" in ds_text


if __name__ == "__main__":
    test_phase6_executive_briefing_json()
    print("[PASS] test_phase6_executive_briefing_json")
    test_phase6_executive_briefing_html_printable()
    print("[PASS] test_phase6_executive_briefing_html_printable")
    test_phase6_what_if_stress_comparison()
    print("[PASS] test_phase6_what_if_stress_comparison")
    test_phase6_bhasha_ai_devanagari_verification()
    print("[PASS] test_phase6_bhasha_ai_devanagari_verification")
    test_phase6_submission_artifacts()
    print("[PASS] test_phase6_submission_artifacts")
    print("\n[PASS] ALL PHASE 6 WINNING EDGE TESTS PASSED 100%!")
