"""Integration tests on the real artifacts: pinned models, built evidence store, analyze_blindspots (template mode)."""
import json

import pytest

from qk_norm_blindspot import paths
from qk_norm_blindspot.schema import CLASSES, check_evidence_record, check_response

OUT = paths.OUTPUTS
needs_build = pytest.mark.skipif(not (OUT / "evidence_records.json").exists(), reason="run `python -m qk_norm_blindspot build` first")


def test_model_c_checksums_and_prediction_is_labelled():
    from qk_norm_blindspot import model_c
    assert model_c.verify_model_c()["all_ok"]
    out = model_c.predict({"material": "Kapton", "airflow_cm_s": 0.0, "resistance_ratio": 1.22, "heating_s": 10.0, "aging_s": 1.0,
                           "mixing_s": 0.0, "units": {"airflow_cm_s": "cm/s", "resistance_ratio": "1", "heating_s": "s", "aging_s": "s", "mixing_s": "s"}})
    assert out["value_kind"] == "predicted" and out["use_as_evidence"] is False
    assert out["ood"] is True  # README's documented OOD example (distance 10.029 > 9.322)
    assert out["nearest_measured_experiment"]["iss_scatter_v_value_kind"] == "measured"


def test_model_c_rejects_unseen_material():
    from qk_norm_blindspot import model_c
    with pytest.raises(ValueError):
        model_c.predict({"material": "PMMA", "airflow_cm_s": 8.0, "resistance_ratio": 1.3, "heating_s": 60.0, "aging_s": 11.0,
                         "mixing_s": 8.0, "units": {"airflow_cm_s": "cm/s", "resistance_ratio": "1", "heating_s": "s", "aging_s": "s", "mixing_s": "s"}})


def test_model_a_reproduces_published_sample():
    from qk_norm_blindspot import side_panels
    a = side_panels.model_a_panel()
    sample = json.loads((paths.MODEL_A_DIR / "artifacts/model_a_v1/sample_response.json").read_text())
    assert a["response"]["predicted_flame_spread_rate"] == sample["predicted_flame_spread_rate"]


def test_wt4_patch_files_verified():
    from qk_norm_blindspot import wt4
    rep = wt4.verify_wt4_files(check_base_weights=False)
    assert rep["checks"]["patch.safetensors"]["ok"] and rep["checks"]["wt4.json"]["ok"]


@needs_build
def test_every_record_valid_and_anchored():
    recs = json.loads((OUT / "evidence_records.json").read_text())["records"]
    assert recs
    for r in recs:
        check_evidence_record(r)
        assert r["value_kind"] not in ("predicted", "oof_predicted")
        if r["audit_status"] == "VERIFIED":
            assert r["anchor_check"]["found"], r["evidence_id"]
        if r["classification"] == "VERIFIED_LIMITATION":
            assert r["audit_status"] == "VERIFIED" and r["observed_directly"]


@needs_build
def test_gaps_scoped_and_classified():
    gaps = json.loads((OUT / "research_gaps.json").read_text())["gaps"]
    for g in gaps:
        assert g["classification"] in CLASSES and g["classification"] != "VERIFIED_LIMITATION"
        assert "within the examined sources" in g["statement"].lower()


@needs_build
def test_priorities_deterministic_and_justified():
    a = json.loads((OUT / "research_priorities.json").read_text())["priorities"]
    for p in a:
        assert set(p["priority_rationale"]) == {"crewed_mission_relevance", "documented_limitation", "evidence_thinness",
                                                "unexplored_condition_space", "comparability", "information_gain"}
        assert p["existing_evidence"] and p["source_references"]
    ranks = [p["rank"] for p in a]
    assert ranks == sorted(ranks)


@needs_build
def test_analyze_template_mode_schema():
    from qk_norm_blindspot import analyze_blindspots
    r = analyze_blindspots("Which spacecraft smoke detection limitations are documented?", use_llm=False)
    check_response(r)
    assert r["generation_status"] == "FALLBACK_TEMPLATE"
    assert r["validation"]["template_check"]["valid"], r["validation"]["template_check"]
    assert r["verified_findings"]


@needs_build
def test_filters_examples_from_spec():
    from qk_norm_blindspot import analyze_blindspots
    for f in ({"material": "Teflon"}, {"investigation": ["SAME", "SAME-R"]}, {"classification": "EVIDENCE_GAP"}, {"year_range": [2018, 2025]}):
        r = analyze_blindspots("What is documented?", f, use_llm=False)
        check_response(r)
        assert r["validation"]["template_check"]["valid"] or not r["answer"]["summary"]
