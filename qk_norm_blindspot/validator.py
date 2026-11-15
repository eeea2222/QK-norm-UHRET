"""Citation validator for generated (WT4) or templated answer sentences.

Rejects:
  V1 malformed output (not a non-empty list of {text, evidence_ids});
  V2 a sentence without evidence_ids, or citing an evidence_id that does not exist / was not provided;
  V3 any number in a sentence that does not occur in the cited records;
  V4 a predicted / oof_predicted value presented as evidence (no 'predict' wording, or evidential wording);
  V5 a gap / absence claim without the 'within the examined sources' scope;
  V6 forbidden overclaims (e.g. 'NASA could not solve', certification, operational alarm settings);
  V7 missed-alarm vs false-alarm conflation (wording not backed by the cited record type).
"""
from __future__ import annotations

import json
import re
from typing import Any

from .schema import SCOPE_PHRASE

_NUM = re.compile(r"(?<![A-Za-z0-9.])[-+]?\d+(?:[.,]\d+)?(?:\s?%)?")
_ID_IN_TEXT = re.compile(r"\[[^\]]*\]")
_GAP_CUE = re.compile(
    r"\b(no (?:data|evidence|tests?|measurements?|studies|experiments?|results?)\b|not (?:been )?(?:tested|measured|studied|"
    r"examined|available|found|reported|evaluated)\b|lack(?:s|ing)?\b|gap\b|gaps\b|untested\b|absence of\b|insufficient\b|"
    r"unknown\b|remains? open\b|unanswered\b)", re.I)
_SCOPE = re.compile(r"(within|in) the examined sources|examined sources|incelenen kaynaklar", re.I)
_FORBIDDEN = re.compile(
    r"(could not solve|couldn't solve|cannot solve|no solution (?:exists|yet)|still no solution|unsolved by nasa|nasa failed|"
    r"certif(?:y|ies|ied|ication)|guarantee|is safe\b|are safe\b|safe to use|operational (?:alarm )?(?:setting|threshold|instruction)|"
    r"alarm threshold should|should set the alarm|real-time iss (?:fire )?alarm)", re.I)
_PRED_WORD = re.compile(r"\bpredict(?:s|ed|ion|ions)?\b|\bmodel estimate\b|\bestimated by model c\b", re.I)
_EVIDENTIAL = re.compile(r"\b(measured|recorded|observed|verified|alarm record|experimental result|proves?|demonstrates?)\b", re.I)
_FALSE_ALARM = re.compile(r"\b(false|nuisance) alarms?\b", re.I)
_MISSED = re.compile(r"\b(did not alarm|didn't alarm|no alarm|failed to (?:alarm|detect|respond)|missed alarm|not detect(?:ed)?|did not (?:detect|respond))\b", re.I)


def _numbers_in(text: str) -> list[tuple[float, bool, int]]:
    """(value, is_percent, n_decimals) for every number token in text."""
    out = []
    for m in _NUM.finditer(text):
        raw = m.group(0).replace(" ", "")
        pct = raw.endswith("%")
        raw = raw.rstrip("%")
        if "," in raw:
            head, tail = raw.split(",", 1)
            raw = head + tail if (len(tail) == 3 and "." not in tail) else head + "." + tail
        dec = len(raw.split(".")[1]) if "." in raw else 0
        try:
            out.append((float(raw), pct, dec))
        except ValueError:
            continue
    return out


def allowed_numbers(records: list[dict]) -> set[float]:
    vals: set[float] = set()
    for r in records:
        for v, _, _ in _numbers_in(json.dumps(r, ensure_ascii=False)):
            vals.add(round(abs(v), 9))
    return vals


def _num_ok(v: float, pct: bool, dec: int, allowed: set[float]) -> bool:
    """Exact match, percent<->fraction equivalence, or the text printing a cited value rounded to `dec` decimals.

    Integers must match exactly (no rounding tolerance)."""
    v = abs(v)
    cands = [(v, dec)]
    if pct:
        cands.append((v / 100, dec + 2))
    else:
        cands.append((v * 100, max(dec - 2, 0)))
    for c, d in cands:
        if round(c, 9) in allowed:
            return True
        if d >= 1 and any(round(a, d) == round(c, d) for a in allowed):
            return True
    return False


def _text_of(rec: dict) -> str:
    return json.dumps(rec, ensure_ascii=False).lower()


def validate_sentences(sentences: Any, store: dict[str, dict], provided_ids: set[str]) -> dict:
    errors: list[dict] = []
    if not isinstance(sentences, list) or not sentences:
        return {"valid": False, "errors": [{"sentence": None, "rule": "V1", "detail": "output is not a non-empty list of sentences"}], "n_sentences": 0}
    for i, s in enumerate(sentences):
        if not isinstance(s, dict) or not isinstance(s.get("text"), str) or not s["text"].strip():
            errors.append({"sentence": i, "rule": "V1", "detail": "sentence must be an object with non-empty text"})
            continue
        ids = s.get("evidence_ids")
        if not isinstance(ids, list) or not ids or not all(isinstance(x, str) for x in ids):
            errors.append({"sentence": i, "rule": "V2", "detail": "sentence has no evidence_ids"})
            continue
        bad = [x for x in ids if x not in store or x not in provided_ids]
        if bad:
            errors.append({"sentence": i, "rule": "V2", "detail": f"unknown or not-provided evidence_ids {bad}"})
            continue
        cited = [store[x] for x in ids]
        text = s["text"]
        scan = _ID_IN_TEXT.sub(" ", text)
        for x in ids:
            scan = scan.replace(x, " ")
        allowed = allowed_numbers(cited)
        for v, pct, dec in _numbers_in(scan):
            if not _num_ok(v, pct, dec, allowed):
                errors.append({"sentence": i, "rule": "V3", "detail": f"number {v}{'%' if pct else ''} not found in cited records {ids}"})
        if any(r.get("value_kind") in ("predicted", "oof_predicted") for r in cited):
            if not _PRED_WORD.search(text) or _EVIDENTIAL.search(text):
                errors.append({"sentence": i, "rule": "V4", "detail": "predicted value must be labelled as a prediction and not described as measured/verified evidence"})
        gapish = any(r.get("classification") in ("EVIDENCE_GAP", "INSUFFICIENT_INFORMATION") for r in cited)
        if (_GAP_CUE.search(text) or gapish) and not _SCOPE.search(text):
            errors.append({"sentence": i, "rule": "V5", "detail": f"gap/absence statement lacks the scope '{SCOPE_PHRASE}'"})
        if _FORBIDDEN.search(text):
            errors.append({"sentence": i, "rule": "V6", "detail": f"forbidden overclaim: {_FORBIDDEN.search(text).group(0)!r}"})
        if _FALSE_ALARM.search(text) and not any(r.get("finding_type") == "false_alarm" or "false alarm" in _text_of(r) or "nuisance" in _text_of(r) for r in cited):
            errors.append({"sentence": i, "rule": "V7", "detail": "mentions false alarms but no cited record concerns false alarms"})
        if _MISSED.search(text) and not any(r.get("finding_type") == "missed_alarm" or "alarm" in _text_of(r) or "detect" in _text_of(r) for r in cited):
            errors.append({"sentence": i, "rule": "V7", "detail": "mentions a missed alarm but no cited record concerns detector response"})
    return {"valid": not errors, "errors": errors, "n_sentences": len(sentences)}
