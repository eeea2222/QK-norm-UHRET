"""Structured catalog filters only. No search, ranking, embeddings or retrieval engine."""
from __future__ import annotations
import re
from typing import Iterable

def _as_list(v) -> list:
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple, set)) else [v]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def apply_filters(records: Iterable[dict], filters: dict | None) -> list[dict]:
    """Structured filters: material, investigation, classification, finding_type, year_range, doc_id."""
    recs = list(records)
    if not filters:
        return recs
    mats = {_norm(m) for m in _as_list(filters.get("material"))}
    invs = {_norm(i) for i in _as_list(filters.get("investigation"))}
    classes = set(_as_list(filters.get("classification")))
    ftypes = set(_as_list(filters.get("finding_type")))
    docs = set(_as_list(filters.get("doc_id")))
    yr = filters.get("year_range")
    out = []
    for r in recs:
        if mats:
            rm = {_norm(m) for m in (r.get("materials") or [r.get("material")]) if m}
            if not (rm & mats):
                continue
        if invs:
            ri = {_norm(i) for i in (r.get("investigations") or [r.get("investigation")]) if i}
            if not (ri & invs):
                continue
        if classes and r.get("classification") not in classes:
            continue
        if ftypes and r.get("finding_type") not in ftypes:
            continue
        if docs and r.get("doc_id") not in docs:
            continue
        if yr and (r.get("source_year") is None or not (yr[0] <= r["source_year"] <= yr[1])):
            continue
        out.append(r)
    return out



def validate_filters(filters: dict | None) -> None:
    if filters is None:
        return
    if not isinstance(filters, dict):
        raise ValueError('filters must be an object')
    allowed = {'material', 'investigation', 'classification', 'finding_type', 'year_range', 'doc_id', 'model_c_input'}
    unknown = set(filters) - allowed
    if unknown:
        raise ValueError(f'Unknown filters: {sorted(unknown)}')
    for k, v in filters.items():
        if k == 'year_range':
            if not isinstance(v, (list, tuple)) or len(v) != 2 or not all(type(i) is int for i in v) or v[0] > v[1]:
                raise ValueError('year_range must be [start_year, end_year] in ascending order')
        elif k == 'model_c_input':
            if not isinstance(v, dict):
                raise ValueError('model_c_input must be an object')
        elif not (isinstance(v, str) or isinstance(v, list) and all(isinstance(i, str) for i in v)):
            raise ValueError(f'{k} must be a string or list of strings')
