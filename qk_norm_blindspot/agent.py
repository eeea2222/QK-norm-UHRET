"""Structured catalog API with deterministic templates. RAG removed by user request."""
from __future__ import annotations

import copy
import json
import re
from typing import Any

from . import generation
from .catalog import apply_filters, validate_filters
from .schema import SCOPE_PHRASE, check_response
from .store import EvidenceStore, get_store

GLOBAL_LIMITATIONS = [
    "Results describe the cited experiments and documents only; they are not ISS fire-incident statistics or general detector failure rates.",
    "Outputs are research-prioritisation aids, not a safety certification, alarm setting, or operational instruction.",
    f"Every gap statement is limited to the sources examined by this module ('{SCOPE_PHRASE}'); absence in this collection does not mean NASA never studied the topic.",
    "Model A (BASS-II flame spread) and Model B (Saffire-I ridge position) do not predict detector performance; no detection result is inferred from them.",
    "Model C outputs are predictions of a derived 2.0 V threshold label (value_kind 'predicted'), never limitation evidence.",
]

KNOWN_MATERIALS = [
    "kapton", "teflon", "ptfe", "silicone", "lampwick", "pyrell", "dbp", "pmma", "nomex", "cotton", "polyethylene",
    "polystyrene", "polyurethane", "paper", "sibal", "ultem", "delrin", "nylon", "polycarbonate", "lithium-ion",
    "lithium ion", "battery", "fabric", "wire insulation",
]

INTENTS = {
    "lunar_gravity": r"\b(lunar gravity|moon gravity|partial[- ]gravity|lunar[- ]g\b|reduced gravity|mars|martian|ay yer|kısmi yer)",
    "lunar_atmosphere": r"(oxygen|\bo2\b|o₂|atmospher|\bpsi\b|pressure|habitat|rover|exploration atmosphere|lunar base|ay üss)",
    "lunar": r"\b(lunar|moon|artemis|ay\b)",
    "false_alarm": r"(false alarm|nuisance|\bdust\b|ambient particle|\bdaft|toz|yanlış alarm)",
    "numeric_rate": r"(\brate\b|percent|percentage|%|how often|probability|failure rate|oran)",
    "priority": r"(priorit|recommend|which research|research question|öncelik)",
    "chronology": r"(2018|2021|2025|chronolog|timeline|later documents|still open|since then|kronoloj)",
    "conditions": r"(condition|limited to|specific experimental|koşul)",
    "gap_vs_failure": r"((gap|boşluk).*(fail|başarısız)|(fail|başarısız).*(gap|boşluk)|confus|conflat|karış)",
    "modelc_compare": r"((model c|2\.0 ?v|\b2 ?v\b|threshold).*(white paper|combin|merg|compar|birleş))|((white paper|combin|merg|birleş).*(model c|2\.0 ?v))",
    "prediction": r"(predict|model c output|tahmin)",
    "sources_for": r"(which (?:stud|source|paper|document)|based on|rest on|rely on|supported by|dayan|destekl)",
    "verified_list": r"(what limitations|which .*limitations|documented|reported|identified|limitation)",
}


def _intents(q: str) -> set[str]:
    ql = q.lower()
    return {k for k, pat in INTENTS.items() if re.search(pat, ql)}


def _materials_in(q: str) -> list[str]:
    ql = q.lower()
    found = []
    for m in KNOWN_MATERIALS:
        if re.search(rf"(?<![a-z]){re.escape(m)}(?![a-z])", ql):
            found.append(m)
    return found


def _canon_material(m: str) -> str:
    return {"ptfe": "teflon", "lithium ion": "lithium-ion"}.get(m, m)


def parse_question(question: str, filters: dict | None) -> dict:
    f = copy.deepcopy(filters) if filters else {}
    intents = _intents(question)
    mats = [_canon_material(m) for m in _materials_in(question)]
    if "material" not in f and mats:
        f["_question_materials"] = mats
    return {"intents": sorted(intents), "filters": f, "question_materials": mats}


def _ref(item: dict) -> dict:
    keys = ("source_title", "source_year", "source_url", "source_location", "doi", "ntrs_id", "psi_id", "pmc_id")
    return {k: item.get(k) for k in keys if item.get(k) is not None}


def _brief_record(r: dict) -> dict:
    keep = ("evidence_id", "investigation", "psi_id", "material", "materials", "detector", "finding_type", "value", "value_unit",
            "value_kind", "audit_status", "classification", "statement", "technical_detail", "experimental_conditions",
            "n_independent_tests", "source_title", "source_year", "source_url", "source_location", "limitations")
    return {k: r.get(k) for k in keep}


def _material_gap(material: str, store: EvidenceStore) -> dict:
    tested = sorted(store.tested_materials)
    prof_ids = sorted({i for p in store.profiles if p.get("smoke_detectors_evaluated") for i in p.get("evidence_ids", [])})
    return {
        "gap_id": f"GAP-MATERIAL-{material.upper().replace(' ', '-')}",
        "topic": f"Smoke-detector response to {material} smoke",
        "classification": "INSUFFICIENT_INFORMATION",
        "rule": "material not in materials_tested of any investigation profile that evaluated spacecraft smoke detectors",
        "rule_result": {"material": material, "materials_tested_with_detectors": tested},
        "statement": (f"Within the examined sources, no spacecraft smoke-detector test with {material} smoke was found; "
                      f"the detector-evaluating investigations used {', '.join(tested)} smoke, so the detector response to "
                      f"{material} smoke cannot be stated."),
        "evidence_ids": prof_ids,
        "scope": SCOPE_PHRASE,
        "dynamic": True,
    }


def _select_gaps(store: EvidenceStore, intents: set[str], mats: list[str], hit_ids: set[str]) -> list[dict]:
    want_dims = set()
    if "lunar_gravity" in intents or ("lunar" in intents and "lunar_atmosphere" not in intents):
        want_dims.add("gravity")
    if "lunar_atmosphere" in intents:
        want_dims |= {"oxygen", "pressure"}
    if "false_alarm" in intents:
        want_dims.add("dust")
    out = [g for g in store.gaps if g.get("dimension") in want_dims]
    if not out and not want_dims:
        out = [g for g in store.gaps if set(g.get("evidence_ids", [])) & hit_ids]
    if mats:
        out += [g for g in store.gaps if any(m in json.dumps(g).lower() for m in mats) and g not in out]
    return out


def analyze_blindspots(question: str, filters: dict | None = None, use_llm: bool = False,
                       store: EvidenceStore | None = None, generator: Any = None) -> dict:
    """Answer a detection-blindspot question from the audited evidence store.

    filters: material, investigation, classification, finding_type, year_range, doc_id, model_c_input.
    use_llm: deprecated compatibility parameter; catalog responses always use templates.
    generator: optional callable(system, user) -> raw text, replacing WT4 (used by tests).
    """
    validate_filters(filters)
    store = store or get_store()
    parsed = parse_question(question, filters)
    intents = set(parsed["intents"])
    f = parsed["filters"]
    qmats = parsed["question_materials"]
    tested = store.tested_materials

    # Catalog selection uses explicit filters only; the question never ranks or retrieves records.
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")
    struct = {k: v for k, v in f.items() if k in ("material", "investigation", "classification", "finding_type", "year_range", "doc_id")}
    hits = sorted(apply_filters(store.records, struct), key=lambda r: r["evidence_id"])

    verified = [r for r in hits if r.get("classification") == "VERIFIED_LIMITATION"]
    if "false_alarm" in intents:
        verified = sorted(verified, key=lambda r: r["finding_type"] != "false_alarm")
    if "chronology" in intents:
        verified = sorted(verified, key=lambda r: (r.get("source_year") or 0, r["evidence_id"]))
    verified = verified[:10]

    untested = [m for m in qmats if m not in tested and m not in ("battery", "fabric")]
    blindspots = [_material_gap(m, store) for m in untested]
    blindspots += _select_gaps(store, intents, qmats, {r["evidence_id"] for r in hits[:15]})
    if "gap_vs_failure" in intents or f.get("classification") in ("EVIDENCE_GAP", "INSUFFICIENT_INFORMATION", "CONFLICTING_EVIDENCE"):
        blindspots += [g for g in store.gaps if g not in blindspots]
    blindspots = [g for i, g in enumerate(blindspots) if g["gap_id"] not in {x["gap_id"] for x in blindspots[:i]}]

    comparisons = []
    if "modelc_compare" in intents or ("sources_for" in intents and any(m in ("kapton", "teflon") for m in qmats)):
        comparisons += [c for c in store.comparisons if c.get("kind") == "definition_difference"]
    if "chronology" in intents:
        comparisons += [c for c in store.comparisons if c.get("kind") == "chronology"]

    priorities = []
    if "priority" in intents or "sources_for" in intents or not (verified or blindspots or comparisons):
        gap_ids = {g["gap_id"] for g in blindspots}
        hit_ids = {r["evidence_id"] for r in hits[:15]}
        priorities = [p for p in store.priorities if set(p.get("gap_ids", [])) & gap_ids or set(p["existing_evidence"]) & hit_ids]
        priorities = sorted(priorities or store.priorities, key=lambda p: p["rank"])[:5]

    # Explicit filters constrain all linked sections as well as the record table.
    if struct:
        selected_ids = {r["evidence_id"] for r in hits}
        blindspots = [g for g in blindspots if set(g.get("evidence_ids", [])) & selected_ids]
        comparisons = [c for c in comparisons if set(c.get("evidence_ids", [])) & selected_ids]
        priorities = [p for p in priorities if set(p.get("existing_evidence", [])) & selected_ids]
        if not hits:
            verified, blindspots, comparisons, priorities = [], [], [], []

    # ---- numeric request that the sources cannot answer ------------------------------------------
    numeric_missing = False
    if "numeric_rate" in intents:
        want_type = "false_alarm" if "false_alarm" in intents else None
        numeric = [r for r in hits if r.get("value") is not None and (want_type is None or r["finding_type"] == want_type)]
        if qmats:
            numeric = [r for r in numeric if (r.get("material") or "").lower() in qmats]
        if not numeric or untested:
            numeric_missing = True

    # ---- model outputs (Model C only when an exact material + condition is selected) --------------
    model_outputs = []
    if f.get("model_c_input"):
        from . import model_c

        try:
            model_outputs.append(model_c.predict(f["model_c_input"]))
        except (ValueError, RuntimeError) as e:
            model_outputs.append({"model": "model_c", "value_kind": "predicted", "error": str(e), "use_as_evidence": False})

    # ---- citable context for the answer text -----------------------------------------------------
    overlay = dict(store.by_id)
    for g in blindspots:
        overlay[g["gap_id"]] = g
    for i, m in enumerate(model_outputs):
        if "error" not in m:
            pid = f"MODEL-C-PRED-{i + 1}"
            m["output_id"] = pid
            overlay[pid] = {"output_id": pid, "value_kind": "predicted", "target": "recorded ISS scatter >= 2.0 V", "predicted_alarm_level_reached": m["predicted_alarm_level_reached"],
                            "ood": m["ood"], "nearest_distance": m["nearest_distance"], "ood_threshold": m["ood_threshold"],
                            "nearest_measured_experiment": m["nearest_measured_experiment"], "material": m["input"]["material"]}
    mode = generation.choose_mode(intents, numeric_missing, verified, blindspots, comparisons, priorities, model_outputs)
    context_ids = generation.context_ids(mode, verified, blindspots, comparisons, priorities, model_outputs, hits)
    answer, gen_status, validation = generation.compose(question, mode, context_ids, overlay, use_llm=False)

    cited = set(context_ids) | {r["evidence_id"] for r in hits}
    for r in verified:
        cited.add(r["evidence_id"])
    for g in blindspots:
        cited |= set(g.get("evidence_ids", []))
    for c in comparisons:
        cited |= set(c.get("evidence_ids", []))
    for p in priorities:
        cited |= set(p.get("existing_evidence", []))
    refs = []
    for i in sorted(cited):
        r = store.by_id.get(i)
        if r and "evidence_id" in r:
            refs.append({"evidence_id": i, **_ref(r)})

    limitations = list(GLOBAL_LIMITATIONS)
    for r in verified:
        for lim in r.get("limitations", []):
            if lim not in limitations:
                limitations.append(lim)
    if any(m == "pmma" for m in qmats):
        limitations.append("Model A concerns PMMA flame-spread rate in BASS-II; it gives no information about smoke-detector response to PMMA smoke and was not used to infer one.")
    for m in model_outputs:
        for c in m.get("caveats", []):
            if c not in limitations:
                limitations.append(c)

    if not (verified or blindspots or comparisons or priorities or model_outputs):
        status = "NO_EVIDENCE"
    elif numeric_missing or any(g["classification"] == "INSUFFICIENT_INFORMATION" for g in blindspots[:1]):
        status = "PARTIAL"
    else:
        status = "COMPLETED"

    resp = {
        "question": question,
        "engine": "STRUCTURED_CATALOG",
        "rag_enabled": False,
        "scientific_validation_status": "DEFERRED_BY_REQUEST",
        "filters_applied": {k: v for k, v in f.items() if k != "model_c_input"} | ({"model_c_input": True} if f.get("model_c_input") else {}),
        "intents": sorted(intents),
        "answer": answer,
        "catalog_records": [_brief_record(r) for r in hits],
        "verified_findings": [_brief_record(r) for r in verified],
        "detection_blindspots": blindspots,
        "research_priorities": priorities,
        "scientific_comparisons": comparisons,
        "evidence_references": refs,
        "model_outputs": model_outputs,
        "limitations": limitations,
        "generation_status": gen_status,
        "analysis_status": status,
        "validation": validation,
    }
    if numeric_missing:
        resp["requested_value_found"] = False
    if use_llm:
        resp["limitations"].append("RAG generation has been removed; use /models/wt4/generate for standalone text generation.")
    check_response(resp)
    return resp


def export_findings(path=None) -> dict:
    """Export every record, gap, priority, comparison and profile as one JSON document."""
    from . import paths

    s = get_store()
    doc = {"evidence_records": s.records, "research_gaps": s.gaps, "research_priorities": s.priorities,
           "scientific_comparisons": s.comparisons, "chronology": s.chronology, "investigation_profiles": s.profiles}
    out = path or (paths.OUTPUTS / "all_findings.json")
    with open(out, "w") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
    return {"path": str(out), "n_records": len(s.records), "n_gaps": len(s.gaps), "n_priorities": len(s.priorities)}
