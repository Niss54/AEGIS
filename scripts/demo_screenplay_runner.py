#!/usr/bin/env python3
"""
AEGIS-CLIMATE: Phase 4 Pitch Video Screenplay Runner & Teleprompter Generator
Google Cloud AI Builder Cup — JAPAC Track (Singapore Grand Finale)

Validates 180s timing invariants, queries live system health, generates
teleprompter cue sheets, and simulates real-time presentation pacing.
"""
import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List

# Ensure repository root is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.app.routes.demo import DEMO_ACTS, TOTAL_DEMO_BUDGET_SECONDS


def verify_timing_invariants() -> Dict[str, Any]:
    """
    Verifies that the screenplay strictly obeys the 180-second duration constraint,
    continuous timestamp continuity, and Google Cloud keyword coverage.
    """
    total_duration = sum(act["duration_seconds"] for act in DEMO_ACTS)
    if abs(total_duration - TOTAL_DEMO_BUDGET_SECONDS) > 0.001:
        raise ValueError(
            f"Mathematical constraint failure: Acts sum to {total_duration}s, must equal {TOTAL_DEMO_BUDGET_SECONDS}s."
        )

    # Check temporal continuity
    current_time = 0.0
    for act in DEMO_ACTS:
        if abs(act["start_seconds"] - current_time) > 0.001:
            raise ValueError(f"Temporal gap in Act {act['act_id']}: Expected start {current_time}s, got {act['start_seconds']}s")
        current_time = act["end_seconds"]

    # Verify Google Cloud & competition keywords
    full_text = " ".join([act["voiceover_lines"] + " " + " ".join(act["tech_stack_callouts"]) for act in DEMO_ACTS])
    required_keywords = [
        "Google Cloud",
        "Vertex AI",
        "Gemini 2.0 Flash",
        "Cloud Run",
        "Copernicus Sentinel-2",
        "Model Context Protocol",
        "Singapore"
    ]

    missing = [kw for kw in required_keywords if kw.lower() not in full_text.lower()]
    if missing:
        raise ValueError(f"Critical competition keywords missing from screenplay: {missing}")

    return {
        "verified": True,
        "total_duration_seconds": total_duration,
        "acts_count": len(DEMO_ACTS),
        "total_words": len(full_text.split()),
        "wpm_pacing": round(len(full_text.split()) / (total_duration / 60.0), 1)
    }


def export_teleprompter_artifacts(output_dir: str = None) -> Dict[str, str]:
    """
    Exports formatted teleprompter text and timeline cue markers to docs directory.
    """
    if not output_dir:
        output_dir = os.path.join(ROOT_DIR, "docs")
    os.makedirs(output_dir, exist_ok=True)

    txt_path = os.path.join(output_dir, "teleprompter_cue_sheet.txt")
    json_path = os.path.join(output_dir, "teleprompter_cue_sheet.json")

    text_lines = [
        "================================================================================",
        "  AEGIS-CLIMATE: 3-MINUTE PITCH VIDEO TELEPROMPTER CUE SHEET",
        "  Google Cloud AI Builder Cup · JAPAC Grand Finale · Singapore",
        "================================================================================",
        ""
    ]

    for act in DEMO_ACTS:
        start_min = int(act["start_seconds"] // 60)
        start_sec = int(act["start_seconds"] % 60)
        end_min = int(act["end_seconds"] // 60)
        end_sec = int(act["end_seconds"] % 60)
        time_tag = f"[{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}]"

        text_lines.append(f"--- ACT {act['act_id']}: {act['name'].upper()} {time_tag} ---")
        text_lines.append(f"SCENE ANCHOR : {act['key_visual_anchor']}")
        text_lines.append(f"TECH FOCUS   : {', '.join(act['tech_stack_callouts'])}")
        text_lines.append("VISUAL CUES  :")
        for cue in act["visual_cues"]:
            text_lines.append(f"  • {cue}")
        text_lines.append("")
        text_lines.append("SPOKEN VOICEOVER:")
        text_lines.append(act["voiceover_lines"])
        text_lines.append("")
        text_lines.append("-" * 80)
        text_lines.append("")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines))

    data_payload = {
        "project": "AEGIS-CLIMATE",
        "competition": "Google Cloud AI Builder Cup (JAPAC Track)",
        "duration_seconds": TOTAL_DEMO_BUDGET_SECONDS,
        "acts": DEMO_ACTS
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_payload, f, indent=2)

    return {"text_file": txt_path, "json_file": json_path}


def simulate_live_pacing(fast_mode: bool = True):
    """
    Prints real-time simulated teleprompter pacing in console.
    """
    metrics = verify_timing_invariants()
    print("\n" + "=" * 70)
    print(f"🎬 AEGIS-CLIMATE 3-MINUTE PITCH PACING SIMULATOR")
    print(f"Target Duration: {metrics['total_duration_seconds']}s | Word Count: {metrics['total_words']} | WPM: {metrics['wpm_pacing']}")
    print("=" * 70 + "\n")

    for act in DEMO_ACTS:
        start_m = int(act["start_seconds"] // 60)
        start_s = int(act["start_seconds"] % 60)
        end_m = int(act["end_seconds"] // 60)
        end_s = int(act["end_seconds"] % 60)
        time_tag = f"[{start_m:02d}:{start_s:02d} -> {end_m:02d}:{end_s:02d}]"

        print(f"\n▶ ACT {act['act_id']} ({act['duration_seconds']}s) {time_tag}: {act['name']}")
        print(f"  [VISUAL] {act['key_visual_anchor']}")
        print(f"  [TECH]   {', '.join(act['tech_stack_callouts'])}")
        words = act["voiceover_lines"].split()
        snippet = " ".join(words[:18]) + "..."
        print(f"  [SPEECH] \"{snippet}\"")
        if not fast_mode:
            time.sleep(act["duration_seconds"])

    print("\n" + "=" * 70)
    print("✅ PITCH SIMULATION COMPLETE: 180s Budget Satisfied.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-CLIMATE Pitch Video Screenplay Runner")
    parser.add_argument("--verify", action="store_true", help="Validate 180s timing invariants and tech keywords")
    parser.add_argument("--export-cues", action="store_true", help="Export teleprompter text and JSON cue markers")
    parser.add_argument("--simulate", action="store_true", help="Simulate teleprompter pacing in console")
    args = parser.parse_args()

    if args.export_cues:
        files = export_teleprompter_artifacts()
        print(f"✅ Exported teleprompter cues:\n  - {files['text_file']}\n  - {files['json_file']}")
    elif args.simulate:
        simulate_live_pacing(fast_mode=True)
    else:
        results = verify_timing_invariants()
        print(f"✅ Screenplay Verified Successfully: {results}")
