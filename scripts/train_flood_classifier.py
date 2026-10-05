"""
AEGIS-CLIMATE — Agent 1: Acute Physical Risk ML Training Pipeline
Trains and serializes the Flash Flood Risk Classifier using scikit-learn / Gradient Boosting.
Saves model artifacts to backend/models/flood_classifier.pkl
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, f1_score


def generate_bharat_climate_dataset(n_samples: int = 3000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates synthetic yet scientifically grounded meteorological vectors representing
    Indian climate zones (Mumbai/Konkan coastal monsoon, Assam Brahmaputra basin,
    Deccan semi-arid, Gangetic plains, and Himalayan foothills).
    """
    np.random.seed(random_seed)

    # 1. Soil moisture saturation index [10% to 100%]
    soil_saturation = np.random.beta(a=2.5, b=2.0, size=n_samples) * 90.0 + 10.0

    # 2. 24-hour precipitation [0mm to 280mm] (Heavy tail for monsoon cloudbursts)
    rain_24h_base = np.random.exponential(scale=35.0, size=n_samples)
    rain_24h = np.clip(rain_24h_base, 0.0, 280.0)

    # 3. 7-day antecedent rolling precipitation [0mm to 600mm]
    rain_7d = rain_24h * np.random.uniform(1.8, 3.8, size=n_samples) + np.random.exponential(scale=40.0, size=n_samples)
    rain_7d = np.clip(rain_7d, 0.0, 600.0)

    # 4. Relative humidity [20% to 100%]
    humidity = np.clip(30.0 + (rain_24h * 0.25) + (soil_saturation * 0.45) + np.random.normal(0, 5, n_samples), 20.0, 100.0)

    # 5. Topographical elevation in meters [2m to 1200m]
    # Log-uniform distribution skewed toward low-lying coastal/basin areas
    elevation = np.random.choice([
        np.random.uniform(2.0, 35.0),    # Low coastal/basin (e.g. Mumbai, Chennai, Assam)
        np.random.uniform(35.0, 150.0),  # Urban plain
        np.random.uniform(150.0, 900.0)  # Plateau/Hills (e.g. Bengaluru, Deccan)
    ], p=[0.55, 0.30, 0.15], size=n_samples)

    # 6. Drainage capacity index [10 to 100] (Higher = better drainage infrastructure)
    drainage_capacity = np.random.uniform(20.0, 95.0, size=n_samples)

    df = pd.DataFrame({
        "soil_saturation_pct": np.round(soil_saturation, 1),
        "precipitation_24h_mm": np.round(rain_24h, 1),
        "precipitation_7d_mm": np.round(rain_7d, 1),
        "relative_humidity_pct": np.round(humidity, 1),
        "elevation_m": np.round(elevation, 1),
        "drainage_capacity_index": np.round(drainage_capacity, 1)
    })

    # Ground Truth Physical Hazard Scoring Logic
    # Elevation dampens flood probability; high rain + high saturation amplifies it
    hazard_score = (
        (df["soil_saturation_pct"] / 100.0 * 0.35) +
        (np.clip(df["precipitation_24h_mm"] / 120.0, 0, 1.0) * 0.30) +
        (np.clip(df["precipitation_7d_mm"] / 350.0, 0, 1.0) * 0.15) +
        (np.clip(1.0 - (df["elevation_m"] / 100.0), 0, 1.0) * 0.10) +
        (np.clip(1.0 - (df["drainage_capacity_index"] / 100.0), 0, 1.0) * 0.10)
    )

    # Map to 4 discrete risk tiers
    # 0 = LOW, 1 = MEDIUM, 2 = HIGH, 3 = CRITICAL
    labels = np.zeros(n_samples, dtype=int)
    labels[hazard_score >= 0.40] = 1  # MEDIUM
    labels[hazard_score >= 0.65] = 2  # HIGH
    labels[hazard_score >= 0.80] = 3  # CRITICAL

    df["risk_tier_label"] = labels
    return df


def train_and_export_model():
    """Trains Gradient Boosting Model, logs metrics, and serializes to backend/models/"""
    print(">>> [Phase 2] Generating Bharat Meteorological Dataset...")
    df = generate_bharat_climate_dataset(n_samples=3500)
    print(f"Dataset generated: {len(df)} samples across 6 physical features.")
    print("Class Distribution:")
    class_names = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    for c_idx, count in df["risk_tier_label"].value_counts().sort_index().items():
        print(f"  {class_names[c_idx]}: {count} ({count/len(df)*100:.1f}%)")

    feature_cols = [
        "soil_saturation_pct",
        "precipitation_24h_mm",
        "precipitation_7d_mm",
        "relative_humidity_pct",
        "elevation_m",
        "drainage_capacity_index"
    ]

    X = df[feature_cols]
    y = df["risk_tier_label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    print("\n>>> [Phase 2] Training Gradient Boosting Risk Classifier...")
    model = GradientBoostingClassifier(
        n_estimators=120,
        learning_rate=0.08,
        max_depth=4,
        subsample=0.85,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="f1_macro")

    print(f"Evaluation Results:")
    print(f"  Accuracy: {acc*100:.2f}%")
    print(f"  Macro F1 Score: {f1_macro:.4f}")
    print(f"  5-Fold CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names))

    # Feature Importances
    importances = dict(zip(feature_cols, [round(float(v), 4) for v in model.feature_importances_]))
    print("Feature Importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {feat}: {imp*100:.1f}%")

    # Serialize artifacts
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models"))
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, "flood_classifier.pkl")
    metadata_path = os.path.join(output_dir, "model_metadata.json")

    artifact = {
        "model": model,
        "feature_cols": feature_cols,
        "class_names": class_names,
        "version": "1.0.0"
    }

    with open(model_path, "wb") as f:
        pickle.dump(artifact, f)
    print(f"\n[OK] Model successfully serialized to: {model_path}")

    metadata = {
        "model_type": "GradientBoostingClassifier",
        "n_estimators": 120,
        "max_depth": 4,
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(f1_macro), 4),
        "cv_f1_mean": round(float(cv_scores.mean()), 4),
        "class_names": class_names,
        "feature_names": feature_cols,
        "feature_importances": importances,
        "target_classes": {str(i): name for i, name in enumerate(class_names)}
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[OK] Metadata saved to: {metadata_path}")


if __name__ == "__main__":
    train_and_export_model()
