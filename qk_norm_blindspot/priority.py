"""Deterministic research-priority engine (no LLM, no weighted risk score).

Each candidate question is scored on the six criteria of the specification with fixed ordinal rules (levels 0-2)
computed from the evidence store, and candidates are ranked LEXICOGRAPHICALLY in criterion order
(1 crewed-mission relevance, 2 documented limitation, 3 evidence thinness, 4 unexplored condition space,
5 comparability, 6 information gain). Ties share a rank. Every level stores its rule and evidence ids.
"""
from __future__ import annotations

from .schema import SCOPE_PHRASE

CRITERIA = [
    ("crewed_mission_relevance",
     "number of distinct crewed-mission contexts (ISS, lunar habitat, pressurized rover, ...) backed by a cited record: 0 -> 0, 1 -> 1, >=2 -> 2"),
    ("documented_limitation",
     "2 if any linked record is VERIFIED_LIMITATION; 1 if only NASA-stated needs (EVIDENCE_GAP via rule R4) are linked; 0 otherwise"),
    ("evidence_thinness",
     "amount/quality of existing experimental evidence on the question (higher = thinner = more to gain): 2 if no linked "
     "experimental record with a known independent-test count; 1 if the summed known independent tests < 50; 0 otherwise"),
    ("unexplored_condition_space",
     "number of linked gap probes that fired (EVIDENCE_GAP / INSUFFICIENT_INFORMATION / CONFLICTING_EVIDENCE): 0 -> 0, 1 -> 1, >=2 -> 2"),
    ("comparability",
     "2 if a study could reuse a hardware family that already produced detector data (SAME/SAME-R protocol); 1 if only a "
     "related hardware family without detector data is available; 0 if none is documented"),
    ("information_gain",
     "2 if the new study would supply data for a condition with zero coverage in the examined sources; 1 if it would add "
     "data to a covered but thin condition; 0 otherwise"),
]


def _lvl_count(n: int) -> int:
    return 0 if n <= 0 else (1 if n == 1 else 2)


def score_candidate(c: dict, by_id: dict[str, dict], gaps_by_id: dict[str, dict], profiles_by_inv: dict[str, dict]) -> dict:
    ev = [by_id[i] for i in c["existing_evidence"] if i in by_id]
    missing = [i for i in c["existing_evidence"] if i not in by_id]
    if missing:
        raise ValueError(f"{c['priority_id']}: unknown evidence ids {missing}")
    gaps = [gaps_by_id[g] for g in c.get("gap_ids", []) if g in gaps_by_id]
    crit: dict[str, dict] = {}

    ctx = [m for m in c.get("mission_contexts", []) if all(i in by_id for i in m["evidence_ids"])]
    crit["crewed_mission_relevance"] = {"level": _lvl_count(len(ctx)), "basis": [m["context"] for m in ctx],
                                        "evidence_ids": sorted({i for m in ctx for i in m["evidence_ids"]})}

    vl = [r["evidence_id"] for r in ev if r.get("classification") == "VERIFIED_LIMITATION"]
    need = [r["evidence_id"] for r in ev if r.get("classification") == "EVIDENCE_GAP"]
    crit["documented_limitation"] = {"level": 2 if vl else (1 if need else 0), "evidence_ids": vl or need}

    exp = [r for r in ev if r.get("finding_type") in ("missed_alarm", "false_alarm", "particle_property", "measurement_limitation")
           and r.get("observed_directly")]
    known = [r["n_independent_tests"] for r in exp if isinstance(r.get("n_independent_tests"), int)]
    total = sum(known)
    lvl3 = 2 if not known else (1 if total < 50 else 0)
    crit["evidence_thinness"] = {"level": lvl3, "known_independent_tests_summed": total if known else None,
                                 "evidence_ids": [r["evidence_id"] for r in exp],
                                 "note": "sum over linked records; records may share tests, so this is an upper bound"}

    fired = [g["gap_id"] for g in gaps]
    crit["unexplored_condition_space"] = {"level": _lvl_count(len(fired)), "gap_ids": fired}

    hw = c.get("comparable_investigations", [])
    with_det = [i for i in hw if profiles_by_inv.get(i, {}).get("smoke_detectors_evaluated")]
    crit["comparability"] = {"level": 2 if with_det else (1 if hw else 0), "investigations": hw,
                             "with_detector_data": with_det}

    zero = [g["gap_id"] for g in gaps if g["classification"] == "EVIDENCE_GAP"]
    thin = [g["gap_id"] for g in gaps if g["classification"] in ("INSUFFICIENT_INFORMATION", "CONFLICTING_EVIDENCE")]
    crit["information_gain"] = {"level": 2 if zero else (1 if thin or (exp and lvl3 >= 1) else 0),
                                "fills_zero_coverage": zero, "adds_to_thin": thin}
    for name, rule in CRITERIA:
        crit[name]["rule"] = rule
    return crit


def rank_candidates(candidates: list[dict], records: list[dict], gaps: list[dict], profiles: list[dict]) -> list[dict]:
    by_id = {r["evidence_id"]: r for r in records}
    gaps_by_id = {g["gap_id"]: g for g in gaps}
    prof = {p["investigation"]: p for p in profiles}
    scored = []
    for c in candidates:
        crit = score_candidate(c, by_id, gaps_by_id, prof)
        key = tuple(crit[n]["level"] for n, _ in CRITERIA)
        scored.append((key, c, crit))
    scored.sort(key=lambda t: (tuple(-k for k in t[0]), t[1]["priority_id"]))
    out, rank, prev = [], 0, None
    for pos, (key, c, crit) in enumerate(scored, start=1):
        if key != prev:
            rank, prev = pos, key
        gap_text = c["evidence_gap"]
        if SCOPE_PHRASE not in gap_text.lower():
            raise ValueError(f"{c['priority_id']}: evidence_gap text must contain '{SCOPE_PHRASE}'")
        refs = []
        for i in c["existing_evidence"]:
            r = by_id[i]
            refs.append(f"{i}: {r.get('source_title')} ({r.get('source_year')}), {r.get('source_location')}")
        out.append({
            "priority_id": c["priority_id"], "rank": rank, "criteria_levels": dict(zip([n for n, _ in CRITERIA], key)),
            "research_question": c["research_question"], "why_it_matters": c["why_it_matters"],
            "existing_evidence": c["existing_evidence"], "gap_ids": c.get("gap_ids", []), "evidence_gap": gap_text,
            "priority_rationale": crit, "source_references": refs, "uncertainty": c["uncertainty"],
            "statement": c["research_question"],
            "not_an_operational_instruction": True,
        })
    return out
