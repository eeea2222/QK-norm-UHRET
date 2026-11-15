"""Unit tests for the deterministic parts (no WT4 needed)."""
import json

import pytest

from qk_norm_blindspot import paths
from qk_norm_blindspot.classify import classify_record
from qk_norm_blindspot.gaps import probe_material_untested, probe_profile_condition
from qk_norm_blindspot.catalog import apply_filters
from qk_norm_blindspot.sources import anchor_found, normalize
from qk_norm_blindspot.validator import validate_sentences

BASE = {"finding_type": "missed_alarm", "audit_status": "VERIFIED", "observed_directly": True, "value_kind": "source_reported"}


# ---------------- classification rules -------------------------------------------------------
def test_verified_limitation_rule():
    assert classify_record(dict(BASE)) == ("VERIFIED_LIMITATION", "R2-verified-limitation")


def test_unverified_limitation_is_insufficient():
    assert classify_record(dict(BASE, audit_status="NOT_VERIFIED"))[0] == "INSUFFICIENT_INFORMATION"
    assert classify_record(dict(BASE, observed_directly=False))[0] == "INSUFFICIENT_INFORMATION"


def test_stated_need_is_gap_not_failure():
    assert classify_record(dict(BASE, finding_type="technology_need"))[0] == "EVIDENCE_GAP"


def test_conflict_rule_and_context():
    assert classify_record(dict(BASE, conflict={"kind": "source_internal"}))[0] == "CONFLICTING_EVIDENCE"
    assert classify_record(dict(BASE, finding_type="context"))[0] is None


# ---------------- validator ------------------------------------------------------------------
STORE = {
    "A": {"evidence_id": "A", "finding_type": "missed_alarm", "classification": "VERIFIED_LIMITATION", "value": 0.5,
          "value_kind": "source_reported", "statement": "The ISS detector did not alarm in half of Kapton tests (9 of 21)."},
    "G": {"gap_id": "G", "classification": "EVIDENCE_GAP", "statement": "No partial-gravity data within the examined sources."},
    "P": {"output_id": "P", "value_kind": "predicted", "nearest_distance": 10.029009, "ood_threshold": 9.321957},
}


def v(text, ids, provided=("A", "G", "P")):
    return validate_sentences([{"text": text, "evidence_ids": ids}], STORE, set(provided))


def test_validator_accepts_grounded_sentence():
    assert v("In SAME, 9 of 21 Kapton runs are cited and half of the tests had no alarm.", ["A"])["valid"]


def test_validator_rejects_injected_number():
    r = v("The detector failed in 73% of tests.", ["A"])
    assert not r["valid"] and r["errors"][0]["rule"] == "V3"


def test_validator_percent_fraction_equivalence():
    assert v("About 50% of the Kapton tests had no alarm.", ["A"])["valid"]


def test_validator_rejects_unknown_id_and_missing_ids():
    assert v("Text.", ["Z"])["errors"][0]["rule"] == "V2"
    assert validate_sentences([{"text": "x", "evidence_ids": []}], STORE, {"A"})["errors"][0]["rule"] == "V2"


def test_validator_requires_scope_for_gaps():
    assert v("No partial-gravity data exist.", ["G"])["errors"][0]["rule"] == "V5"
    assert v("No partial-gravity data exist within the examined sources.", ["G"])["valid"]


def test_validator_prediction_rules():
    assert not v("Model C measured that Kapton reaches the level.", ["P"])["valid"]
    assert v("Model C predicts the level is reached (distance 10.029 vs threshold 9.322).", ["P"])["valid"]


def test_validator_forbidden_overclaim():
    assert v("NASA could not solve the problem in half of the tests.", ["A"])["errors"][0]["rule"] == "V6"


def test_validator_missed_vs_false_alarm():
    r = v("These were false alarms in half of the tests.", ["A"])
    assert any(e["rule"] == "V7" for e in r["errors"])


def test_validator_malformed():
    assert validate_sentences(None, STORE, {"A"})["errors"][0]["rule"] == "V1"


# ---------------- anchors / retrieval ---------------------------------------------------------
def test_anchor_normalisation():
    assert normalize("detec‐tor  \n  test") == "detec-tor test"
    assert anchor_found("detector test", "the detec- tor test was")


def test_filters_and_rank():
    recs = [{"evidence_id": "1", "material": "Kapton", "investigation": "SAME", "classification": "VERIFIED_LIMITATION",
             "finding_type": "missed_alarm", "source_year": 2018, "statement": "Kapton smoke ISS detector"},
            {"evidence_id": "2", "material": "Teflon", "investigation": "SAME-R", "classification": "EVIDENCE_GAP",
             "finding_type": "technology_need", "source_year": 2025, "statement": "Teflon smoke"}]
    assert [r["evidence_id"] for r in apply_filters(recs, {"material": "teflon"})] == ["2"]
    assert [r["evidence_id"] for r in apply_filters(recs, {"year_range": [2018, 2021]})] == ["1"]
    assert [r["evidence_id"] for r in apply_filters(recs, {"investigation": ["SAME"]})] == ["1"]
    assert apply_filters(recs, {"material": "absent"}) == []


# ---------------- gap probes ------------------------------------------------------------------
PROFILES = [{"investigation": "SAME", "smoke_detectors_evaluated": ["ISS"], "materials_tested": ["Kapton", "Teflon"],
             "conditions": {"o2_vol_pct": {"min": 21, "max": 21}, "gravity": {"values": ["microgravity"]}},
             "detector_material_tests": [{"detector": "ISS smoke detector", "materials": ["Kapton", "Teflon"], "gravity": "microgravity",
                                          "smoke_mode": "pyrolysis", "alarm_evaluated": True, "evidence_ids": []}]},
            {"investigation": "GASP-2020", "smoke_detectors_evaluated": ["ISS"], "materials_tested": ["PMMA"], "smoke_generation_mode": "pyrolysis",
             "conditions": {"o2_vol_pct": {"min": 21, "max": 21}, "gravity": {"values": ["1 g"]}},
             "detector_material_tests": [{"detector": "ISS smoke detector", "materials": ["PMMA"], "gravity": "1 g",
                                          "smoke_mode": "pyrolysis", "alarm_evaluated": False, "evidence_ids": []}]},
            {"investigation": "ACME", "smoke_detectors_evaluated": [], "materials_tested": [],
             "conditions": {"o2_vol_pct": {"min": 10, "max": 40}}}]


def test_probe_condition_gap_and_unknown():
    r = probe_profile_condition({"params": {"key": "o2_vol_pct", "min_ge": 30}}, PROFILES)
    assert r["classification"] == "EVIDENCE_GAP"          # ACME reaches 40% but evaluated no detector
    r = probe_profile_condition({"params": {"key": "pressure_kpa", "max_le": 70.3}}, PROFILES)
    assert r["classification"] == "INSUFFICIENT_INFORMATION"  # unknown pressure -> cannot claim a gap
    r = probe_profile_condition({"params": {"key": "gravity", "any_in": ["microgravity"]}}, PROFILES)
    assert not r["fired"]


def test_probe_material():
    r = probe_material_untested({"params": {"material": "PMMA", "detector_contains": "ISS"}}, PROFILES)
    assert r["classification"] == "INSUFFICIENT_INFORMATION"          # only a 1 g test without alarm evaluation
    assert r["rule_result"]["related_tests_found"] and not r["rule_result"]["decisive_tests"]
    assert not probe_material_untested({"params": {"material": "kapton", "detector_contains": "ISS"}}, PROFILES)["fired"]


# ---------------- registry --------------------------------------------------------------------
def test_models_registry_pins_all_four():
    reg = json.loads(paths.MODELS_REGISTRY.read_text())
    for k in ("model_a", "model_b", "model_c", "wt4"):
        assert len(reg[k]["revision"]) == 40
    assert reg["wt4"]["base_revision"] == "d1671a178705bcab7644806d23c535517f35723b"
