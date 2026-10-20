"""
Phase 4 Test Suite: 3-Minute High-Energy Pitch Video Screenplay & Teleprompter
Google Cloud AI Builder Cup — JAPAC Track (Singapore Grand Finale)
"""
import os
import json
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routes.demo import DEMO_ACTS, TOTAL_DEMO_BUDGET_SECONDS
from scripts.demo_screenplay_runner import verify_timing_invariants, export_teleprompter_artifacts

client = TestClient(app)


def test_screenplay_mathematical_budget():
    """Verify that all 4 screenplay acts sum to exactly 180.0 seconds."""
    total_duration = sum(act["duration_seconds"] for act in DEMO_ACTS)
    assert total_duration == 180.0
    assert TOTAL_DEMO_BUDGET_SECONDS == 180.0
    assert len(DEMO_ACTS) == 4


def test_screenplay_temporal_continuity():
    """Verify strictly monotonic, contiguous time progression from 0 to 180s."""
    current_time = 0.0
    for act in DEMO_ACTS:
        assert act["start_seconds"] == current_time
        assert act["end_seconds"] == current_time + act["duration_seconds"]
        assert act["start_seconds"] < act["end_seconds"]
        current_time = act["end_seconds"]
    assert current_time == 180.0


def test_google_cloud_keywords_coverage():
    """Verify that all critical Google Cloud, architecture, and competition tokens are present."""
    metrics = verify_timing_invariants()
    assert metrics["verified"] is True
    assert metrics["total_duration_seconds"] == 180.0
    assert metrics["wpm_pacing"] > 120.0  # High-energy pacing


def test_rest_api_get_screenplay():
    """Verify GET /api/v1/demo/screenplay returns 4 acts with validated budget."""
    res = client.get("/api/v1/demo/screenplay")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["total_duration_seconds"] == 180.0
    assert data["budget_verified"] is True
    assert len(data["acts"]) == 4
    assert "Google Cloud AI Builder Cup" in data["competition"]
    assert len(data["presenter_checklist"]) >= 4


def test_rest_api_get_teleprompter():
    """Verify GET /api/v1/demo/teleprompter returns formatted script text and sections."""
    res = client.get("/api/v1/demo/teleprompter")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["total_seconds"] == 180.0
    assert len(data["sections"]) == 4
    assert "formatted_teleprompter_text" in data
    assert "ACT 1" in data["formatted_teleprompter_text"]
    assert "ACT 4" in data["formatted_teleprompter_text"]


def test_rest_api_get_timeline_cues():
    """Verify GET /api/v1/demo/cues returns markers for video editing software."""
    res = client.get("/api/v1/demo/cues")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["video_duration_seconds"] == 180.0
    assert len(data["markers"]) == 4
    assert data["markers"][0]["start_time"] == "00:00"
    assert data["markers"][-1]["end_time"] == "03:00"


def test_teleprompter_artifact_exporter(tmp_path):
    """Verify teleprompter artifact generator produces valid txt and json files."""
    exported = export_teleprompter_artifacts(str(tmp_path))
    assert os.path.exists(exported["text_file"])
    assert os.path.exists(exported["json_file"])

    with open(exported["json_file"], "r", encoding="utf-8") as f:
        doc = json.load(f)
    assert doc["project"] == "TERRA-SENTINEL"
    assert doc["duration_seconds"] == 180.0
    assert len(doc["acts"]) == 4


def test_demo_script_markdown_file():
    """Verify docs/DEMO_SCRIPT.md exists and contains 180s screenplay."""
    script_path = os.path.join(os.path.dirname(__file__), "..", "docs", "DEMO_SCRIPT.md")
    assert os.path.exists(script_path)
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "180s" in content
    assert "Google Cloud AI Builder Cup" in content
    assert "ACT 1" in content
    assert "ACT 2" in content
    assert "ACT 3" in content
    assert "ACT 4" in content
    assert "Syntrix" in content
