"""
TERRA-SENTINEL: Phase 5 Verification Suite
VC Investment Memo, Pitch Deck, and Singapore Grand Finale Strategy
Incorporating Google Research Hydrology & DeepMind DGMR Nowcasting Moats
"""
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_vc_memo_includes_deep_innovations():
    """Verify VC memo API and document include Google Research and DeepMind DGMR moats."""
    res = client.get("/api/v1/executive/vc-memo")
    assert res.status_code == 200
    data = res.json()

    # Check moats
    moat_str = " ".join(data["competitive_moats"])
    assert "Google Research State-Handoff LSTM" in moat_str
    assert "DeepMind DGMR" in moat_str
    assert "Open Climate Fix Quartz" in moat_str
    assert "Zero-shot physical transfer" in moat_str

    # Check cloud alignment
    alignment = data["google_cloud_alignment"]
    assert "google_research_hydrology" in alignment
    assert "deepmind_dgmr_nowcasting" in alignment
    assert "openclimatefix_quartz" in alignment

    # Check document integrity
    memo_file = Path("docs/EXECUTIVE_VC_MEMO.md")
    assert memo_file.exists()
    memo_text = memo_file.read_text(encoding="utf-8")
    assert "Google Research State-Handoff LSTM" in memo_text
    assert "DeepMind DGMR Exceedance Matrix" in memo_text
    assert "Quartz 0h-48h Scrubber" in memo_text


def test_pitch_deck_includes_deep_innovations():
    """Verify pitch deck includes DeepMind and Google Research on Slide 10."""
    res = client.get("/api/v1/executive/pitch-deck")
    assert res.status_code == 200
    data = res.json()
    assert data["total_slides"] == 11

    deck_file = Path("docs/PITCH_DECK.md")
    assert deck_file.exists()
    deck_text = deck_file.read_text(encoding="utf-8")
    assert "Google Research LSTM" in deck_text
    assert "DeepMind DGMR Nowcasting" in deck_text
    assert "Open Climate Fix Quartz" in deck_text


def test_singapore_grand_finale_strategy():
    """Verify Singapore Marina Barrage live stress test playbook."""
    res = client.get("/api/v1/executive/singapore-strategy")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "Singapore" in data["venue"]
    assert data["live_demo_location"]["name"] == "Singapore — Marina Barrage Catchment"
    assert data["live_demo_location"]["lat"] == 1.2800
    assert data["live_demo_location"]["lon"] == 103.8636
    assert len(data["four_minute_pitch_arc"]) == 4
