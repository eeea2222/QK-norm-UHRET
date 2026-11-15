"""Deterministic evidence classification (no LLM).

Rules are applied in order; the first matching rule wins and its id is stored in the record
(`classification_rule`) so every class can be traced back to an explicit condition.
"""
from __future__ import annotations

from .schema import EVIDENCE_VALUE_KINDS, LIMITATION_TYPES, NEED_TYPES, NON_CLAIM_TYPES

RULES = [
    ("R0-context",
     "finding_type in {'context','followup_solution'} -> no class (context or later-solution record, not a limitation claim)"),
    ("R1-conflict",
     "conflict.kind in {'source_internal','between_sources','between_campaigns'} and audit_status == 'VERIFIED' -> CONFLICTING_EVIDENCE"),
    ("R2-verified-limitation",
     "finding_type in LIMITATION_TYPES and observed_directly and audit_status == 'VERIFIED' and value_kind in "
     "{measured, derived, source_reported} -> VERIFIED_LIMITATION"),
    ("R3-unverified-limitation",
     "finding_type in LIMITATION_TYPES but audit_status != 'VERIFIED' or not observed_directly -> INSUFFICIENT_INFORMATION"),
    ("R4-stated-need",
     "finding_type in {technology_need, research_question} and audit_status == 'VERIFIED' -> EVIDENCE_GAP "
     "(open need stated by NASA; not proof that a detector failed)"),
    ("R6-default",
     "anything else -> INSUFFICIENT_INFORMATION"),
]


def classify_record(rec: dict) -> tuple[str | None, str]:
    ft = rec["finding_type"]
    audit = rec["audit_status"]
    if ft in NON_CLAIM_TYPES:
        return None, "R0-context"
    conflict = rec.get("conflict") or {}
    if conflict.get("kind") in ("source_internal", "between_sources", "between_campaigns") and audit == "VERIFIED":
        return "CONFLICTING_EVIDENCE", "R1-conflict"
    if ft in LIMITATION_TYPES:
        if rec.get("observed_directly") and audit == "VERIFIED" and rec.get("value_kind") in EVIDENCE_VALUE_KINDS + (None,):
            return "VERIFIED_LIMITATION", "R2-verified-limitation"
        return "INSUFFICIENT_INFORMATION", "R3-unverified-limitation"
    if ft in NEED_TYPES:
        if audit == "VERIFIED":
            return "EVIDENCE_GAP", "R4-stated-need"
        return "INSUFFICIENT_INFORMATION", "R6-default"
    return "INSUFFICIENT_INFORMATION", "R6-default"
