import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from model_c.evaluate_followup import majority_predictions, measured_summary, within_material


def followup():
    return json.loads(Path("reports/followup_metrics.json").read_text())


def test_protected_artifact_unchanged():
    assert followup()["protected_artifact_sha256"]["artifacts/model_c/model.joblib"] == "1d0a63fe5f51b89df6710e5d2c49632964af7457d67204337dbc3e4eb02f6e01"
    for name, digest in followup()["protected_artifact_sha256"].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest


def test_material_majority_uses_training_only_and_fixed_ties():
    train = pd.DataFrame({"material": ["Kapton", "Kapton", "Teflon", "Teflon", "Teflon"], "alarm_level_reached": [0, 1, 1, 1, 0]})
    test = pd.DataFrame({"material": ["Kapton", "Teflon", "unknown"], "alarm_level_reached": [1, 0, 0]})
    pred, mapping, fallback = majority_predictions(train, test)
    assert mapping == {"Kapton": 0, "Teflon": 1} and fallback == 1
    np.testing.assert_array_equal(pred, [0, 1, 1])
    test.alarm_level_reached = 1 - test.alarm_level_reached
    np.testing.assert_array_equal(majority_predictions(train, test)[0], pred)


def test_original_folds_and_paired_differences():
    old = json.loads(Path("reports/metrics.json").read_text())
    result = followup()["baseline_comparison"]
    for before, after in zip(old["outer_folds"], result["folds"]):
        for key in ["fold", "train_groups", "test_groups"]:
            assert before[key] == after[key]
        assert not set(after["train_groups"]) & set(after["test_groups"])
        assert after["forest_minus_material_majority"] == pytest.approx(after["fixed_forest"]["balanced_accuracy"] - after["material_majority"]["balanced_accuracy"])
        assert after["original_nested_selection"]["balanced_accuracy"] == before["model"]["balanced_accuracy"]
        for inner in after["inner_material_majority_comparison_only"]:
            assert not set(inner["train_groups"]) & set(inner["test_groups"])


def test_baseline_oof_recomputed_from_training_groups():
    train = pd.read_csv("data/processed/training.csv")
    oof = pd.read_csv("reports/material_majority_oof.csv").set_index("test_id")
    assert oof.index.is_unique and set(oof.index) == set(train.test_id)
    for fold in followup()["baseline_comparison"]["folds"]:
        a = train[train.group_id.isin(fold["train_groups"])]
        b = train[train.group_id.isin(fold["test_groups"])]
        pred, _, _ = majority_predictions(a, b)
        np.testing.assert_array_equal(pred, oof.loc[b.test_id].material_majority)


@pytest.mark.parametrize("material", ["Kapton", "Teflon"])
def test_per_material_counts_and_heldout_predictions(material):
    data = pd.read_csv("data/processed/training.csv")
    part = data[data.material == material]
    result = followup()["within_material"][material]
    assert result["n_runs"] == len(part)
    assert result["n_groups"] == part.group_id.nunique()
    for label in [0, 1]:
        rows = part[part.alarm_level_reached == label]
        assert result["class_balance"][str(label)] == {"runs": len(rows), "groups": rows.group_id.nunique()}
    if result["status"] == "TESTED_LOCALLY":
        assert min(c["groups"] for c in result["class_balance"].values()) >= 3
        oof = pd.read_csv(f"reports/{material.lower()}_logistic_oof.csv")
        assert oof.test_id.is_unique and set(oof.test_id) == set(part.test_id)
        for fold in result["folds"]:
            assert not set(fold["train_groups"]) & set(fold["test_groups"])


def test_insufficient_data_does_not_fit():
    data = pd.read_csv("data/processed/training.csv")
    part = data[data.material == "Kapton"]
    scarce = pd.concat([part[part.alarm_level_reached == 0], part[part.alarm_level_reached == 1].head(2)])
    result, predictions = within_material(scarce)
    assert result["status"] == "insufficient data" and predictions.empty


def test_measured_only_dashboard_exact_and_no_predictions():
    data = pd.read_csv("data/processed/training.csv", float_precision="round_trip")
    actual = pd.read_csv("data/processed/dashboard_measured_only.csv", float_precision="round_trip", dtype={"resistance_ratio_unit": str})
    expected = measured_summary(data)
    pd.testing.assert_frame_equal(actual, expected)
    assert not any("predict" in name for name in actual.columns)
    assert set(actual.value_kind) == {"derived"}
    assert actual.n_runs.sum() == len(data)
