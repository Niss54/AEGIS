"""
Agent 1: Acute Physical Risk ML Engine
Handles feature matrix ingestion, model inference via serialized GradientBoostingClassifier,
and dominant hazard driver attribution.
"""
import os
import json
import pickle
import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger("aegis.agent1_ml")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "flood_classifier.pkl")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "model_metadata.json")


class FloodRiskMLModel:
    def __init__(self):
        self.model = None
        self.feature_cols = [
            "soil_saturation_pct",
            "precipitation_24h_mm",
            "precipitation_7d_mm",
            "relative_humidity_pct",
            "elevation_m",
            "drainage_capacity_index"
        ]
        self.class_names = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        self.metadata = {}
        self._load()

    def _load(self):
        """Attempts to load pre-trained model and metadata."""
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    data = pickle.load(f)
                    self.model = data["model"]
                    self.feature_cols = data.get("feature_cols", self.feature_cols)
                    self.class_names = data.get("class_names", self.class_names)
                logger.info(f"Loaded trained flood model from {MODEL_PATH}")
            except Exception as e:
                logger.warning(f"Could not load pickle model: {e}")

        if os.path.exists(METADATA_PATH):
            try:
                with open(METADATA_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                pass

    def is_trained(self) -> bool:
        return self.model is not None

    def predict(
        self,
        soil_saturation_pct: float,
        precipitation_24h_mm: float,
        precipitation_7d_mm: float,
        relative_humidity_pct: float,
        elevation_m: float,
        drainage_capacity_index: float = 65.0
    ) -> Dict[str, Any]:
        """
        Runs ML model inference or calibrated physical formula fallback.
        Returns risk score [0.0 - 1.0], risk tier, class probabilities, and dominant factor.
        """
        features_vec = [
            float(soil_saturation_pct),
            float(precipitation_24h_mm),
            float(precipitation_7d_mm),
            float(relative_humidity_pct),
            float(elevation_m),
            float(drainage_capacity_index)
        ]

        # Determine dominant contributing factor
        # Compare normalized weights of input values
        normalized_contributions = {
            "soil_saturation": (soil_saturation_pct / 100.0) * 0.35,
            "precipitation_24h": min(1.0, precipitation_24h_mm / 120.0) * 0.30,
            "antecedent_rainfall": min(1.0, precipitation_7d_mm / 350.0) * 0.15,
            "topographical_depression": max(0.0, 1.0 - (elevation_m / 80.0)) * 0.10,
            "drainage_choke": max(0.0, 1.0 - (drainage_capacity_index / 100.0)) * 0.10
        }
        dominant_factor = max(normalized_contributions.items(), key=lambda x: x[1])[0]

        if self.model is not None:
            try:
                import pandas as pd
                X = pd.DataFrame([features_vec], columns=self.feature_cols)
                probs = self.model.predict_proba(X)[0]
                # Probabilities across [LOW, MEDIUM, HIGH, CRITICAL]
                prob_dict = {name: round(float(p), 4) for name, p in zip(self.class_names, probs)}
                
                # Weighted expectation for smooth continuous risk score [0.0 - 1.0]
                # weights: LOW=0.15, MEDIUM=0.52, HIGH=0.78, CRITICAL=0.96
                continuous_score = (
                    (prob_dict.get("LOW", 0.0) * 0.15) +
                    (prob_dict.get("MEDIUM", 0.0) * 0.52) +
                    (prob_dict.get("HIGH", 0.0) * 0.78) +
                    (prob_dict.get("CRITICAL", 0.0) * 0.96)
                )
                continuous_score = round(min(1.0, max(0.05, continuous_score)), 3)

                pred_class_idx = int(np.argmax(probs))
                predicted_tier = self.class_names[pred_class_idx]

                # Ensure tier reflects score thresholds
                if continuous_score >= 0.80:
                    predicted_tier = "CRITICAL"
                elif continuous_score >= 0.65:
                    predicted_tier = "HIGH"
                elif continuous_score >= 0.40:
                    predicted_tier = "MEDIUM"
                else:
                    predicted_tier = "LOW"

                return {
                    "risk_score": continuous_score,
                    "risk_tier": predicted_tier,
                    "dominant_factor": dominant_factor,
                    "probabilities": prob_dict,
                    "engine": "GradientBoostingClassifier (scikit-learn)",
                    "feature_contributions": {k: round(v, 4) for k, v in normalized_contributions.items()}
                }
            except Exception as e:
                logger.error(f"Inference error in trained model: {e}")

        # Calibrated fallback formula
        raw_score = sum(normalized_contributions.values())
        raw_score = round(min(1.0, max(0.05, raw_score)), 3)
        if raw_score >= 0.80:
            tier = "CRITICAL"
        elif raw_score >= 0.65:
            tier = "HIGH"
        elif raw_score >= 0.40:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        return {
            "risk_score": raw_score,
            "risk_tier": tier,
            "dominant_factor": dominant_factor,
            "probabilities": {tier: 1.0},
            "engine": "Calibrated Hydro-Meteorological Heuristic",
            "feature_contributions": {k: round(v, 4) for k, v in normalized_contributions.items()}
        }


# Singleton model instance
flood_ml_engine = FloodRiskMLModel()
