"""Answer text: deterministic template, or WT4 constrained to the selected records + citation validator."""
from __future__ import annotations

import json
import re
from typing import Any, Callable

from .schema import SCOPE_PHRASE
from .validator import validate_sentences

SYSTEM_PROMPT = (
    "You write short factual answers for spacecraft fire-safety researchers. Use ONLY the evidence items provided. "
    "Every sentence must list the ids of the items it uses in evidence_ids. Copy numbers exactly as they appear in the "
    "items and never compute or invent new numbers. When an item says something was not found or is a gap, write the "
    f"words '{SCOPE_PHRASE}' in that sentence. A missed alarm (detector did not alarm for real smoke) and a false alarm "
    "(alarm without fire, e.g. from dust) are different events. Model predictions must be called predictions. Never say "
    "that NASA failed or could not solve the problem, and never give safety certifications or alarm settings. "
    "Answer with JSON only."
)


# ------------------------------------------------------------------------------------------------
def choose_mode(intents: set[str], numeric_missing: bool, verified, blindspots, comparisons, priorities, model_outputs) -> str:
    if model_outputs and any("error" not in m for m in model_outputs) and "prediction" in intents:
        return "prediction"
    if numeric_missing:
        return "numeric_missing"
    if blindspots and blindspots[0].get("dynamic"):
        return "material_gap"
    if comparisons and "modelc_compare" in intents:
        return "comparison"
    if comparisons and "chronology" in intents:
        return "chronology"
    if blindspots and ({"lunar_gravity", "lunar_atmosphere", "lunar", "gap_vs_failure"} & intents):
        return "gap"
    if priorities and "priority" in intents:
        return "priority"
    if verified:
        return "verified"
    if blindspots:
        return "gap"
    if priorities:
        return "priority"
    return "none"


def context_ids(mode, verified, blindspots, comparisons, priorities, model_outputs, hits, k: int = 6) -> list[str]:
    ids: list[str] = []

    def add(i):
        if i and i not in ids:
            ids.append(i)

    if mode == "prediction":
        for m in model_outputs:
            add(m.get("output_id"))
    if mode in ("material_gap", "gap"):
        for g in blindspots[:3]:
            add(g["gap_id"])
    if mode in ("comparison", "chronology"):
        for c in comparisons[:2]:
            add(c["comparison_id"])
            for e in c.get("evidence_ids", [])[:3]:
                add(e)
    if mode == "priority":
        for p in priorities[:2]:
            add(p["priority_id"])
            for e in p.get("existing_evidence", [])[:2]:
                add(e)
    for r in verified:
        if len(ids) >= k:
            break
        add(r["evidence_id"])
    if mode in ("verified", "gap", "material_gap"):
        for g in blindspots[:2]:
            if len(ids) < k:
                add(g["gap_id"])
    if mode == "numeric_missing" or len(ids) < 2:
        for r in hits[:3]:
            if len(ids) < k:
                add(r["evidence_id"])
    return ids[:k]


# ------------------------------------------------------------------------------------------------
def _sent(text: str, ids: list[str]) -> dict:
    return {"text": text, "evidence_ids": ids}


def _item_detail(item: dict) -> str | None:
    for key in ("technical_detail", "detail", "statement"):
        if item.get(key):
            return item[key]
    return None


def template_sentences(question: str, mode: str, ctx: list[str], store: dict[str, dict]) -> list[dict]:
    items = [(i, store[i]) for i in ctx if i in store]
    out: list[dict] = []
    if not items:
        return out
    if mode == "numeric_missing":
        near = [i for i, it in items if "evidence_id" in it][:3] or [items[0][0]]
        out.append(_sent("The requested rate is not reported " + SCOPE_PHRASE + "; the closest documented records are listed instead.", near))
        for i in near:
            st = store[i].get("statement")
            if st:
                out.append(_sent(st, [i]))
        return out
    if mode == "prediction":
        pid, p = items[0]
        verdict = "reaches" if p["predicted_alarm_level_reached"] else "does not reach"
        ood = "outside" if p["ood"] else "inside"
        out.append(_sent(f"Model C predicts that the selected {p['material']} condition {verdict} the 2.0 V scatter level; this is a "
                         f"prediction, not an alarm record, and the condition is {ood} the model's empirical coverage "
                         f"(distance {p['nearest_distance']:.3f} vs threshold {p['ood_threshold']:.3f}).", [pid]))
        n = p.get("nearest_measured_experiment") or {}
        if n:
            out.append(_sent(f"For comparison, the nearest training experiment {n['test_id']} ({n['campaign']}) has an ISS scatter value of "
                             f"{n['iss_scatter_v']} V in the source table; the model prediction itself carries no uncertainty estimate.", [pid]))
        for i, it in items[1:3]:
            if it.get("statement"):
                out.append(_sent(it["statement"], [i]))
        return out
    first_id, first = items[0]
    summary = first.get("statement") or first.get("research_question")
    if mode == "priority" and first.get("research_question"):
        summary = "The highest-ranked research priority " + SCOPE_PHRASE + " is: " + first["research_question"].rstrip(".") + "."
        out.append(_sent(summary, [first_id] + first.get("existing_evidence", [])[:3]))
    else:
        out.append(_sent(summary, [first_id]))
    for i, it in items[1:5]:
        d = _item_detail(it) if mode != "priority" else (it.get("research_question") or _item_detail(it))
        if d:
            out.append(_sent(d, [i]))
    if mode in ("verified", "comparison", "chronology") and _item_detail(first) and _item_detail(first) != summary:
        out.insert(1, _sent(_item_detail(first), [first_id]))
    return out[:6]


# ------------------------------------------------------------------------------------------------
def parse_llm_json(text: str) -> Any:
    """Extract {"sentences": [...]} from model text; returns the sentence list or None."""
    start = text.find("{")
    while start != -1:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[start:])
            if isinstance(obj, dict) and isinstance(obj.get("sentences"), list):
                return obj["sentences"]
            if isinstance(obj, list):
                return obj
        except json.JSONDecodeError:
            pass
        start = text.find("{", start + 1)
    # salvage: model stopped mid-JSON -> try closing brackets
    for tail in ("\"]}]}", "]}]}", "\"]}", "]}", "}]}"):
        try:
            obj = json.loads(text[text.find("{"):] + tail)
            if isinstance(obj, dict) and isinstance(obj.get("sentences"), list):
                return obj["sentences"]
        except (json.JSONDecodeError, ValueError):
            continue
    return None


def compose(question: str, mode: str, ctx: list[str], store: dict[str, dict], use_llm: bool = True,
            generator: Any = None) -> tuple[dict, str, dict]:
    sources = sorted({f"{store[i].get('source_title')} ({store[i].get('source_year')}), {store[i].get('source_location')}"
                      + (f", {store[i].get('source_url')}" if store[i].get('source_url') else "")
                      for i in ctx if i in store and store[i].get("source_title")})
    template = template_sentences(question, mode, ctx, store)
    # Scope inherited gap records, then fail closed on invalid template sentences.
    for sentence in template:
        cited = [store[i] for i in sentence["evidence_ids"] if i in store]
        if any(r.get("classification") in ("EVIDENCE_GAP", "INSUFFICIENT_INFORMATION") for r in cited):
            if SCOPE_PHRASE not in sentence["text"].lower():
                sentence["text"] = "Within the examined sources, " + sentence["text"][0].lower() + sentence["text"][1:]
    rejected = []
    accepted = []
    for sentence in template:
        check = validate_sentences([sentence], store, set(ctx))
        (accepted if check["valid"] else rejected).append(sentence)
    template = accepted
    tcheck = validate_sentences(template, store, set(ctx)) if template else {"valid": True, "errors": [], "n_sentences": 0}
    validation: dict = {"template_check": tcheck, "attempts": [], "rejected_template_sentences": rejected}

    def as_answer(sents: list[dict]) -> dict:
        return {"summary": sents[:1], "technical_detail": sents[1:], "sources": sources}

    validation["fallback_reason"] = "structured catalog mode; RAG removed"
    return as_answer(template), "FALLBACK_TEMPLATE", validation
