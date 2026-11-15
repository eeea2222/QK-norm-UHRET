"""Shared vocabularies and light-weight schema checks (no external jsonschema dependency)."""
from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "1.0.0"

# Common value-kind vocabulary (spec section 3.3). value_kind != audit_status.
VALUE_KINDS = ("measured", "derived", "source_reported", "predicted", "oof_predicted")
EVIDENCE_VALUE_KINDS = ("measured", "derived", "source_reported")  # predictions are never evidence

# Audit status (spec section 6.1)
AUDIT_STATUSES = ("VERIFIED", "REPORTED_ONLY", "MISSING", "NOT_VERIFIED")

# Finding types (spec section 6.2 lists the first five as the minimum set)
FINDING_TYPES = (
    "missed_alarm",            # detector did not alarm / did not reach its level for a real smoke
    "false_alarm",             # alarm without fire (e.g. ambient dust) - a different event
    "particle_property",       # measured smoke particle property relevant to detection
    "measurement_limitation",  # limitation of the measurement / detection method itself
    "technology_need",         # NASA-stated open engineering need (e.g. 2025 SBIR gaps)
    "research_question",       # NASA-stated open research question (e.g. 2021 white paper)
    "followup_solution",       # later work that addresses part of a limitation
    "context",                 # mission / atmosphere / planned-experiment context; not a limitation claim
)
LIMITATION_TYPES = ("missed_alarm", "false_alarm", "particle_property", "measurement_limitation")
NEED_TYPES = ("technology_need", "research_question")
NON_CLAIM_TYPES = ("context", "followup_solution")  # carry classification = None

# Evidence classes (spec section 6.3)
CLASSES = ("VERIFIED_LIMITATION", "EVIDENCE_GAP", "CONFLICTING_EVIDENCE", "INSUFFICIENT_INFORMATION")

GENERATION_STATUSES = ("LLM_VALIDATED", "FALLBACK_TEMPLATE")
ANALYSIS_STATUSES = ("COMPLETED", "PARTIAL", "NO_EVIDENCE")

SCOPE_PHRASE = "within the examined sources"

CONDITION_KEYS = ("atmosphere_o2_vol_pct", "pressure_kpa", "airflow_cm_s", "gravity", "heating_s", "aging_s")

EVIDENCE_REQUIRED = (
    "evidence_id", "investigation", "psi_id", "hardware_family", "source_title", "source_year",
    "source_url", "source_location", "material", "detector", "finding_type", "value", "value_kind",
    "audit_status", "experimental_conditions", "n_independent_tests", "classification", "limitations",
)

RESPONSE_REQUIRED = (
    "question", "verified_findings", "detection_blindspots", "research_priorities",
    "evidence_references", "model_outputs", "limitations", "generation_status", "analysis_status",
)


class SchemaError(ValueError):
    pass


def check_evidence_record(rec: dict[str, Any]) -> None:
    missing = [k for k in EVIDENCE_REQUIRED if k not in rec]
    if missing:
        raise SchemaError(f"{rec.get('evidence_id')}: missing fields {missing}")
    if rec["finding_type"] not in FINDING_TYPES:
        raise SchemaError(f"{rec['evidence_id']}: bad finding_type {rec['finding_type']}")
    if rec["value_kind"] is not None and rec["value_kind"] not in VALUE_KINDS:
        raise SchemaError(f"{rec['evidence_id']}: bad value_kind {rec['value_kind']}")
    if rec["value_kind"] in ("predicted", "oof_predicted"):
        raise SchemaError(f"{rec['evidence_id']}: predictions are not allowed in the evidence store")
    if rec["audit_status"] not in AUDIT_STATUSES:
        raise SchemaError(f"{rec['evidence_id']}: bad audit_status {rec['audit_status']}")
    if rec["classification"] is not None and rec["classification"] not in CLASSES:
        raise SchemaError(f"{rec['evidence_id']}: bad classification {rec['classification']}")
    if rec["finding_type"] not in NON_CLAIM_TYPES and rec["classification"] is None:
        raise SchemaError(f"{rec['evidence_id']}: non-context record needs a classification")
    cond = rec["experimental_conditions"]
    if not isinstance(cond, dict) or set(CONDITION_KEYS) - set(cond):
        raise SchemaError(f"{rec['evidence_id']}: experimental_conditions must contain {CONDITION_KEYS}")
    if not isinstance(rec["limitations"], list):
        raise SchemaError(f"{rec['evidence_id']}: limitations must be a list")


def check_response(resp: dict[str, Any]) -> None:
    missing = [k for k in RESPONSE_REQUIRED if k not in resp]
    if missing:
        raise SchemaError(f"response missing {missing}")
    if resp["generation_status"] not in GENERATION_STATUSES:
        raise SchemaError(f"bad generation_status {resp['generation_status']}")
    if resp["analysis_status"] not in ANALYSIS_STATUSES:
        raise SchemaError(f"bad analysis_status {resp['analysis_status']}")
    for m in resp["model_outputs"]:
        if m.get("value_kind") not in ("predicted", "oof_predicted"):
            raise SchemaError("model_outputs entries must carry value_kind predicted/oof_predicted")


RESPONSE_JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "analyze_blindspots response",
    "type": "object",
    "required": list(RESPONSE_REQUIRED),
    "properties": {
        "question": {"type": "string"},
        "filters_applied": {"type": "object"},
        "answer": {
            "type": "object",
            "description": "Three-layer answer: summary (one sentence), technical_detail, sources. Every sentence carries evidence_ids.",
            "properties": {
                "summary": {"type": "array", "items": {"$ref": "#/$defs/sentence"}},
                "technical_detail": {"type": "array", "items": {"$ref": "#/$defs/sentence"}},
                "sources": {"type": "array", "items": {"type": "string"}},
            },
        },
        "verified_findings": {"type": "array", "items": {"type": "object"}},
        "detection_blindspots": {"type": "array", "items": {"type": "object"}},
        "research_priorities": {"type": "array", "items": {"type": "object"}},
        "scientific_comparisons": {"type": "array", "items": {"type": "object"}},
        "evidence_references": {"type": "array", "items": {"type": "object"}},
        "model_outputs": {"type": "array", "items": {"type": "object"}},
        "limitations": {"type": "array", "items": {"type": "string"}},
        "generation_status": {"enum": list(GENERATION_STATUSES)},
        "analysis_status": {"enum": list(ANALYSIS_STATUSES)},
        "validation": {"type": "object"},
    },
    "$defs": {
        "sentence": {
            "type": "object",
            "required": ["text", "evidence_ids"],
            "properties": {"text": {"type": "string"}, "evidence_ids": {"type": "array", "items": {"type": "string"}}},
        }
    },
}

REQUEST_JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "analyze_blindspots request",
    "type": "object",
    "required": ["question"],
    "properties": {
        "question": {"type": "string", "minLength": 1},
        "filters": {
            "type": ["object", "null"],
            "properties": {
                "material": {"type": ["string", "array"]},
                "investigation": {"type": ["string", "array"]},
                "classification": {"type": ["string", "array"]},
                "finding_type": {"type": ["string", "array"]},
                "year_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                "model_c_input": {"type": "object", "description": "Exact Model C input (material + five controls + units). Triggers a predicted similar-condition output."},
            },
        },
        "use_llm": {"type": "boolean", "default": False},
    },
}
