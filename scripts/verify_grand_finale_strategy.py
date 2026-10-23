"""
AEGIS-CLIMATE: Phase 25 Verification & Grand Finale Strategy Export
Script: scripts/verify_grand_finale_strategy.py
Validates TAM/SAM/SOM mathematical invariants, audits docs/PITCH_DECK.md,
and exports the IEEE ClimateChain Global Demonstration Playbook to docs/grand_finale_strategy.json.
"""
import sys
import json
import logging
from pathlib import Path

# Set up project root in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.finale_strategy import (
    evaluate_tam_sam_som_market_opportunity,
    audit_pitch_deck_structure,
    generate_singapore_grand_finale_playbook,
    EXACT_TAM_USD_B,
    EXACT_SAM_USD_B,
    EXACT_SOM_USD_M
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phase25_verifier")


def main():
    logger.info("Initializing AEGIS-CLIMATE Phase 25 Grand Finale Strategy Verification...")

    # 1. Evaluate TAM/SAM/SOM Governing Equation
    market_eval = evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=EXACT_TAM_USD_B,
        sam_usd_b=EXACT_SAM_USD_B,
        som_usd_m=EXACT_SOM_USD_M
    )
    logger.info(f"Market Sizing Gate: {market_eval.verdict} (TAM=${market_eval.tam_usd_b}B, SAM=${market_eval.sam_usd_b}B, SOM=${market_eval.som_usd_m}M)")
    if not market_eval.is_compliant:
        logger.error(f"Governing equation failed: {market_eval.verdict}")
        sys.exit(1)

    # 2. Audit Pitch Deck Document Structure
    deck_audit = audit_pitch_deck_structure()
    logger.info(f"Pitch Deck Audit: {deck_audit.get('verdict')} (Lines: {deck_audit.get('total_lines')}, Words: {deck_audit.get('word_count')})")
    if not deck_audit.get("is_compliant"):
        logger.warning(f"Pitch Deck Audit has warnings: {deck_audit}")

    # 3. Generate IEEE ClimateChain Global Demonstration Playbook
    playbook = generate_singapore_grand_finale_playbook()
    output_path = PROJECT_ROOT / "docs" / "grand_finale_strategy.json"

    export_payload = {
        "phase_id": 25,
        "phase_name": "10-Slide Executive VC Pitch Deck, TAM/SAM/SOM & Grand Finale Strategy",
        "governing_equation": "TAM = $12.8B, SAM = $3.2B, SOM = $480M",
        "market_evaluation": market_eval.model_dump(),
        "pitch_deck_audit": deck_audit,
        "singapore_grand_finale_playbook": playbook
    }

    output_path.write_text(json.dumps(export_payload, indent=2), encoding="utf-8")
    logger.info(f"Exported Grand Finale Strategy to: {output_path}")

    print("\n" + "=" * 55)
    print("  AEGIS-CLIMATE IEEE CLIMATECHAIN GLOBAL DEMONSTRATION READY")
    print(f"  TAM: ${market_eval.tam_usd_b}B | SAM: ${market_eval.sam_usd_b}B | SOM: ${market_eval.som_usd_m}M")
    print(f"  Venue: {playbook['venue']}")
    print(f"  Capital Ask: ${playbook['financial_ask']['target_amount_usd']:,} USD ({playbook['financial_ask']['round']})")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
