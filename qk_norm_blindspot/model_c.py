"""Model C wrapper (efe-T/nasa-same-model-c, pinned revision).

Model C predictions are ONLY returned as `value_kind: "predicted"` side information with the OOD flag and
the nearest measured experiment. They are never used as limitation evidence.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
from functools import lru_cache

from . import paths
from .sources import sha256_file

CAVEATS = [
    "Target is a derived label (recorded ISS scatter >= 2.0 V), not a recorded operational alarm.",
    "Material identity explains the headline score (material-majority baseline 0.891 vs forest 0.900 balanced accuracy); "
    "no demonstrated extra predictive value from the controlled conditions.",
    "Weak on difficult materials: Kapton held-out positive recall 0.111, Teflon 0.",
    "OOD flag is a same-material condition-distance heuristic, not a calibrated safety boundary; uncertainty is null.",
    "Not an alarm-time prediction, spacecraft risk score, or certification.",
]


def _reg() -> dict:
    return json.loads(paths.MODELS_REGISTRY.read_text())["model_c"]


def artifact_dir():
    reg = _reg()
    return paths.ROOT / reg["local_dir"] / reg["artifact_dir"]


def verify_model_c() -> dict:
    reg = _reg()
    adir = artifact_dir()
    manifest_path = adir / "checksums.json"
    got_manifest = sha256_file(manifest_path)
    report = {"repo": reg["repo"], "revision": reg["revision"],
              "checksum_manifest": {"sha256": got_manifest, "expected": reg["checksum_manifest_sha256"], "ok": got_manifest == reg["checksum_manifest_sha256"]},
              "files": {}}
    if got_manifest != reg["checksum_manifest_sha256"]:
        raise RuntimeError("Model C checksum manifest does not match the pinned value")
    for name, expected in json.loads(manifest_path.read_text()).items():
        got = sha256_file(adir / name)
        report["files"][name] = {"ok": got == expected}
        if got != expected:
            raise RuntimeError(f"Model C artifact checksum mismatch: {name}")
    if json.loads(manifest_path.read_text())["model.joblib"] != reg["model_sha256"]:
        raise RuntimeError("Model C model sha256 differs from the model card value")
    report["all_ok"] = True
    return report


@lru_cache(maxsize=1)
def _inference_module():
    os.environ["MODEL_C_ARTIFACT"] = str(artifact_dir())
    spec = importlib.util.spec_from_file_location("model_c_artifact_inference", artifact_dir() / "inference.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@lru_cache(maxsize=1)
def dashboard_table():
    import pandas as pd

    return pd.read_csv(paths.MODEL_C_DIR / "data" / "processed" / "dashboard_table.csv")


@lru_cache(maxsize=1)
def measured_only():
    import pandas as pd

    return pd.read_csv(paths.MODEL_C_DIR / "data" / "processed" / "dashboard_measured_only.csv")


def _clean(v):
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "item"):
        return v.item()
    return v


def nearest_measured(test_id: str) -> dict | None:
    df = dashboard_table()
    rows = df[df["test_id"] == test_id]
    if rows.empty:
        return None
    r = rows.iloc[0]
    keys = ["test_id", "campaign", "material", "iss_scatter_v", "signal_kind", "alarm_level_reached", "label_rule",
            "derived_label_kind", "airflow_cm_s", "resistance_ratio", "heating_s", "aging_s", "mixing_s", "group_id",
            "iss_saturation_status"]
    out = {k: _clean(r[k]) for k in keys}
    out["iss_scatter_v_value_kind"] = "measured"
    out["alarm_level_reached_value_kind"] = "derived"
    out["source"] = "external/model_c/data/processed/dashboard_table.csv (PSI-101 combined workbook, sheet 'Combined Rslts Copy this sheet')"
    return out


def predict(model_c_input: dict) -> dict:
    """Run the pinned Model C on an exact input dict (see Model C README for the contract)."""
    verify = verify_model_c()
    res = _inference_module().predict_model_c(model_c_input)
    reg = _reg()
    return {
        "model": "model_c",
        "repo": reg["repo"],
        "revision": reg["revision"],
        "value_kind": "predicted",
        "quantity": "recorded ISS scatter reaches 2.0 V (derived threshold label)",
        "predicted_alarm_level_reached": res["predicted_alarm_level_reached"],
        "ood": res["ood"],
        "ood_reason": res["ood_reason"],
        "nearest_distance": res["nearest_distance"],
        "ood_threshold": res["ood_threshold"],
        "uncertainty": res["uncertainty"],
        "nearest_measured_experiment": nearest_measured(res["nearest_training_test_id"]),
        "input": model_c_input,
        "checksums_verified": verify["all_ok"],
        "caveats": CAVEATS,
        "use_as_evidence": False,
    }
