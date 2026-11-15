import copy
import itertools
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from model_c.data import acquire, measurement, number, preprocess, WORKBOOK_SHA, sha
from model_c.inference import FEATURES, NUMERIC, UNITS, load_bundle, predict_model_c


@pytest.fixture
def request_data():
    return json.loads(Path("reports/sample_inference.json").read_text())["request"]


@pytest.mark.parametrize("value", [None, "n/a", "NA", "#VALUE!", float("nan"), float("inf")])
def test_missing_not_zero(value):
    assert number(value)[0] is None


def test_detection_limit_and_saturation_distinct():
    assert measurement(0)[0] == 0
    assert measurement(.01, below_limit=True) == (None, "below_detection_limit")
    assert measurement(9, saturated=True) == (None, "saturated")
    assert measurement(None)[1] not in ["saturated", "below_detection_limit"]


def test_source_integrity():
    assert sha(acquire()) == WORKBOOK_SHA


def test_preprocessing_reproducible(tmp_path):
    a = preprocess(acquire(), tmp_path)
    b = pd.read_csv("data/processed/observations.csv")
    assert a.source_row.tolist() == b.source_row.tolist()
    np.testing.assert_allclose(a.iss_scatter_v, b.iss_scatter_v)
    assert set(a.campaign) == {"SAME", "SAME-R"}
    assert "DBP" not in set(a.material)
    assert a[a.source_test_id.str.contains(r"\d+\s*a", case=False, regex=True)].training_eligible.sum() == 0


def test_no_group_leakage():
    metrics = json.loads(Path("reports/metrics.json").read_text())
    for fold in metrics["outer_folds"]:
        assert not set(fold["train_groups"]) & set(fold["test_groups"])
    df = pd.read_csv("data/processed/observations.csv")
    assert df.groupby("run_id").group_id.nunique().max() == 1
    assert df.groupby("sample_id").group_id.nunique().max() == 1


def test_harmonization_units_and_label():
    df = pd.read_csv("data/processed/observations.csv")
    np.testing.assert_array_equal(df.alarm_level_reached, (df.iss_scatter_v >= 2).astype(int))
    assert set(df.label_provenance) == {"derived"}
    assert not set(FEATURES) & {"iss_scatter_v", "alarm_level_reached", "m0_source", "m1_mm_cm3"}
    d = json.loads(Path("data/processed/harmonization.json").read_text())
    assert d["controls"]["N"] == "airflow_cm_s"


def test_export_round_trip_and_shape(tmp_path, request_data):
    model, domain = load_bundle()
    joblib.dump(model, tmp_path / "roundtrip.joblib")
    loaded = joblib.load(tmp_path / "roundtrip.joblib")
    x = pd.DataFrame([{k: request_data[k] for k in FEATURES}])
    assert model.predict(x).shape == (1,)
    np.testing.assert_array_equal(loaded.predict(x), model.predict(x))
    assert predict_model_c(request_data)["value_kind"] == "predicted"


@pytest.mark.parametrize("field", FEATURES + ["units"])
def test_missing_fields_rejected(field, request_data):
    request_data.pop(field)
    with pytest.raises(ValueError):
        predict_model_c(request_data)


@pytest.mark.parametrize("bad", [None, float("nan"), float("inf"), "8", True])
def test_invalid_numeric(bad, request_data):
    request_data["airflow_cm_s"] = bad
    with pytest.raises(ValueError):
        predict_model_c(request_data)


def test_unseen_material(request_data):
    request_data["material"] = "PMMA"
    with pytest.raises(ValueError, match="material"):
        predict_model_c(request_data)


def test_wrong_units(request_data):
    request_data["units"] = dict(UNITS, airflow_cm_s="m/s")
    with pytest.raises(ValueError, match="units"):
        predict_model_c(request_data)


@pytest.mark.parametrize("key", NUMERIC)
def test_out_of_range(key, request_data):
    _, domain = load_bundle()
    request_data[key] = domain["ranges"][key][1] + 1
    with pytest.raises(ValueError, match="outside"):
        predict_model_c(request_data)


def test_accepted_ood_exists():
    example = json.loads(Path("reports/ood_example.json").read_text())
    response = predict_model_c(example["request"])
    assert response["ood"] is True
    assert response["nearest_distance"] > response["ood_threshold"]


def test_ood_threshold_different_group():
    _, domain = load_bundle()
    df = pd.DataFrame(domain["training_conditions"])
    maximum = 0
    for _, row in df.iterrows():
        other = df[(df.material == row.material) & (df.group_id != row.group_id)]
        distances = np.linalg.norm((other[NUMERIC].to_numpy() - row[NUMERIC].to_numpy(dtype=float)) / domain["scale"], axis=1)
        maximum = max(maximum, distances.min())
    assert domain["ood_threshold"] == pytest.approx(maximum)


def test_scientific_formula_agreement():
    metrics = json.loads(Path("reports/metrics.json").read_text())
    assert metrics["scientific_checks"]["workbook_moment_ratio_max_absolute_error_um"] < 1e-12


def test_external_source_discrepancy_preserved():
    df = pd.read_csv("reports/external_checks.csv")
    failures = df[df.agreement_status == "unresolved_source_table_inconsistency"]
    assert list(zip(failures.material, failures.state)) == [("Teflon", "unaged")]
    assert failures.iloc[0].source_count_um == .101
    assert failures.iloc[0].calculated_count_um > .11


def test_dashboard_has_all_observations():
    a = pd.read_csv("data/processed/observations.csv")
    b = pd.read_csv("data/processed/dashboard_table.csv")
    assert len(a) == len(b)
    assert set(b.derived_label_kind) == {"derived"}
    assert b[b.training_eligible].oof_predicted.notna().all()
    assert b[~b.training_eligible].predicted_alarm_level_reached.isna().all()
