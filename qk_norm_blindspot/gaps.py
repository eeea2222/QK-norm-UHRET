"""Deterministic research-gap probes over investigation profiles and evidence records.

Each probe is declared in curation/gap_probes.json and evaluated here by a fixed rule. A probe produces a gap
entry only when its rule fires; every evaluation (including probes that found coverage) is kept in probe_log.
"""
from __future__ import annotations

from .schema import SCOPE_PHRASE


def _detector_profiles(profiles: list[dict], flt: dict | None = None) -> list[dict]:
    out = [p for p in profiles if p.get("smoke_detectors_evaluated")]
    for field, allowed in (flt or {}).items():
        out = [p for p in out if p.get(field) in allowed]
    return out


def _cond(p: dict, key: str):
    c = (p.get("conditions") or {}).get(key)
    if isinstance(c, dict):
        return c
    return None


def probe_profile_condition(probe: dict, profiles: list[dict]) -> dict:
    """Is any detector-evaluating investigation profile tested at the probed condition?

    params: key (conditions key), and one of any_in (list of categorical values), min_ge (number), max_le (number).
    Unknown condition in any detector-evaluating profile -> INSUFFICIENT_INFORMATION (cannot claim a gap).
    """
    prm = probe["params"]
    dps = _detector_profiles(profiles, prm.get("filter"))
    excluded = [p["investigation"] for p in _detector_profiles(profiles) if p not in dps]
    unknown, matched, seen = [], [], []
    for p in dps:
        c = _cond(p, prm["key"])
        if c is None or (c.get("values") is None and c.get("min") is None and c.get("max") is None):
            unknown.append(p["investigation"])
            continue
        seen.append({"investigation": p["investigation"], "condition": c})
        if "any_in" in prm and set(c.get("values") or []) & set(prm["any_in"]):
            matched.append(p["investigation"])
        elif "min_ge" in prm and c.get("max") is not None and c["max"] >= prm["min_ge"]:
            matched.append(p["investigation"])
        elif "max_le" in prm and c.get("min") is not None and c["min"] <= prm["max_le"]:
            matched.append(p["investigation"])
    if unknown:
        cls, fired = "INSUFFICIENT_INFORMATION", True
    elif not matched:
        cls, fired = "EVIDENCE_GAP", True
    else:
        cls, fired = None, False
    return {"fired": fired, "classification": cls,
            "rule_result": {"detector_profiles": [p["investigation"] for p in dps], "condition_unknown_in": unknown,
                            "profiles_matching": matched, "tested_conditions": seen, "filter": prm.get("filter"),
                            "excluded_by_filter": excluded}}


def detector_material_entries(profiles: list[dict], material: str, detector_contains: str | None = None) -> list[dict]:
    out = []
    for p in profiles:
        for t in p.get("detector_material_tests", []):
            if detector_contains and detector_contains.lower() not in t["detector"].lower():
                continue
            if material.lower() in {m.lower() for m in t["materials"]}:
                out.append({"investigation": p["investigation"], **{k: t[k] for k in ("detector", "gravity", "smoke_mode", "alarm_evaluated", "evidence_ids")}})
    return out


def probe_material_untested(probe: dict, profiles: list[dict]) -> dict:
    """INSUFFICIENT_INFORMATION unless the (detector, material) pair was tested in microgravity with an alarm evaluation."""
    prm = probe["params"]
    entries = detector_material_entries(profiles, prm["material"], prm.get("detector_contains"))
    decisive = [e for e in entries if e["gravity"] == "microgravity" and e["alarm_evaluated"] is True]
    fired = not decisive
    return {"fired": fired, "classification": "INSUFFICIENT_INFORMATION" if fired else None,
            "rule_result": {"material": prm["material"], "detector_filter": prm.get("detector_contains"),
                            "related_tests_found": entries, "decisive_tests": decisive}}


def probe_detector_test_absent(probe: dict, profiles: list[dict]) -> dict:
    """EVIDENCE_GAP when no profile has a detector test matching detector_contains + smoke_mode + gravity."""
    prm = probe["params"]
    hits, related = [], []
    for p in profiles:
        for t in p.get("detector_material_tests", []):
            if t.get("smoke_mode") == prm["smoke_mode"] and t.get("gravity") == prm["gravity"]:
                (hits if prm["detector_contains"].lower() in t["detector"].lower() else related).append(
                    {"investigation": p["investigation"], "detector": t["detector"], "materials": t["materials"]})
    fired = not hits
    return {"fired": fired, "classification": "EVIDENCE_GAP" if fired else None,
            "rule_result": {"criteria": prm, "matching_tests": hits, "related_tests_other_detectors": related}}


def probe_records_absent(probe: dict, records: list[dict]) -> dict:
    """Fires (EVIDENCE_GAP) when no record matches all `match` criteria (field -> allowed values / substring)."""
    m = probe["params"]["match"]
    hits = []
    for r in records:
        ok = True
        for field, want in m.items():
            if field == "text_any":
                blob = " ".join(str(r.get(k, "")) for k in ("statement", "technical_detail", "material", "detector")).lower()
                ok = any(w.lower() in blob for w in want)
            elif isinstance(want, list):
                ok = r.get(field) in want
            else:
                ok = r.get(field) == want
            if not ok:
                break
        if ok:
            hits.append(r["evidence_id"])
    fired = not hits
    return {"fired": fired, "classification": "EVIDENCE_GAP" if fired else None,
            "rule_result": {"criteria": m, "matching_records": hits}}


def probe_conflicts(probe: dict, records: list[dict]) -> dict:
    hits = [r["evidence_id"] for r in records if r.get("classification") == "CONFLICTING_EVIDENCE"
            and (not probe["params"].get("ids") or r["evidence_id"] in probe["params"]["ids"])]
    return {"fired": bool(hits), "classification": "CONFLICTING_EVIDENCE" if hits else None,
            "rule_result": {"conflicting_records": hits}}


PROBES = {
    "profile_condition_absent": lambda pr, recs, profs: probe_profile_condition(pr, profs),
    "material_untested": lambda pr, recs, profs: probe_material_untested(pr, profs),
    "records_absent": lambda pr, recs, profs: probe_records_absent(pr, recs),
    "detector_test_absent": lambda pr, recs, profs: probe_detector_test_absent(pr, profs),
    "conflicts": lambda pr, recs, profs: probe_conflicts(pr, recs),
}


def evaluate(probes: list[dict], records: list[dict], profiles: list[dict]) -> tuple[list[dict], list[dict]]:
    gaps, log = [], []
    rec_ids = {r["evidence_id"] for r in records}
    for pr in probes:
        res = PROBES[pr["type"]](pr, records, profiles)
        log.append({"gap_id": pr["gap_id"], "type": pr["type"], "fired": res["fired"], "classification": res["classification"],
                    "rule_result": res["rule_result"]})
        if not res["fired"]:
            continue
        stmt = pr["statement"].get(res["classification"]) if isinstance(pr["statement"], dict) else pr["statement"]
        if SCOPE_PHRASE not in stmt.lower():
            raise ValueError(f"{pr['gap_id']}: gap statement must contain '{SCOPE_PHRASE}'")
        missing = [i for i in pr.get("evidence_ids", []) if i not in rec_ids]
        if missing:
            raise ValueError(f"{pr['gap_id']}: unknown evidence_ids {missing}")
        ev = list(pr.get("evidence_ids", []))
        if pr["type"] == "conflicts":
            ev += [i for i in res["rule_result"]["conflicting_records"] if i not in ev]
        gaps.append({
            "gap_id": pr["gap_id"], "topic": pr["topic"], "dimension": pr.get("dimension"),
            "classification": res["classification"], "rule": pr["rule_text"], "rule_result": res["rule_result"],
            "statement": stmt, "detail": pr.get("detail"), "evidence_ids": ev,
            "expected_future_sources": pr.get("expected_future_sources", []), "scope": SCOPE_PHRASE,
            "not_a_detector_failure": res["classification"] != "CONFLICTING_EVIDENCE",
            "keywords": pr.get("keywords", []),
        })
    return gaps, log
