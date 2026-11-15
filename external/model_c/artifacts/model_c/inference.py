"""CPU inference. This module has no dependency on acquisition or training code."""
import hashlib
import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

FEATURES = ["material", "airflow_cm_s", "resistance_ratio", "heating_s", "aging_s", "mixing_s"]
NUMERIC = FEATURES[1:]
UNITS = {"airflow_cm_s": "cm/s", "resistance_ratio": "1", "heating_s": "s", "aging_s": "s", "mixing_s": "s"}


def load_bundle(path=None):
    path = Path(path or os.environ.get("MODEL_C_ARTIFACT", "artifacts/model_c"))
    manifest = json.loads((path / "checksums.json").read_text())
    for name, expected in manifest.items():
        if hashlib.sha256((path / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Artifact checksum mismatch: {name}")
    return joblib.load(path / "model.joblib"), json.loads((path / "domain.json").read_text())


def predict_model_c(input_data: dict) -> dict:
    """Predict recorded ISS scatter >=2 V for tested material/condition ranges."""
    model, domain = load_bundle()
    required = set(FEATURES) | {"units"}
    if set(input_data) != required:
        raise ValueError(f"Expected exactly {sorted(required)}")
    if input_data["material"] not in domain["materials"]:
        raise ValueError("Unsupported material")
    if input_data["units"] != UNITS:
        raise ValueError(f"Required units: {UNITS}")
    values = []
    for key in NUMERIC:
        value = input_data[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value):
            raise ValueError(f"{key} must be a finite number")
        low, high = domain["ranges"][key]
        if not low <= value <= high:
            raise ValueError(f"{key} outside training range [{low}, {high}]")
        values.append(value)
    rows = [r for r in domain["training_conditions"] if r["material"] == input_data["material"]]
    arr = np.array([[r[k] for k in NUMERIC] for r in rows])
    distance = np.sqrt(np.sum(((arr - values) / domain["scale"]) ** 2, axis=1))
    nearest = int(np.argmin(distance))
    threshold = domain["ood_threshold"]
    frame = pd.DataFrame([{k: input_data[k] for k in FEATURES}])
    prediction = int(model.predict(frame)[0])
    ood = bool(distance[nearest] > threshold)
    return {
        "predicted_alarm_level_reached": bool(prediction), "value_kind": "predicted",
        "target": "recorded ISS scatter >= 2.0 V", "units": "boolean",
        "model_version": domain["model_version"],
        "applicable_domain": {"materials": domain["materials"], "ranges": domain["ranges"], "campaigns": domain["campaigns"]},
        "ood": ood, "ood_reason": "Sparse same-material condition coverage" if ood else "Within empirical condition-distance threshold",
        "nearest_distance": float(distance[nearest]), "ood_threshold": threshold,
        "nearest_training_test_id": rows[nearest]["test_id"],
        "uncertainty": None,
        "interpretation": "Experimental response estimate; no alarm timing or operational safety guarantee.",
    }
