"""Build all JSON deliverables from the curated evidence + the downloaded sources.

    python -m qk_norm_blindspot build

Every curated record's anchor quote is re-located on its cited page of the extracted source text; numbers used
in record text must trace to structured fields or the source item; classes come from classify.py rules; gaps
from gaps.py probes; priorities from priority.py. The build fails loudly on any violation.
"""
from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import gaps as gaps_mod
from . import paths, priority
from .classify import RULES, classify_record
from .schema import CONDITION_KEYS, SCHEMA_VERSION, SCOPE_PHRASE, check_evidence_record
from .sources import load_registry, sha256_file, verify_anchor
from .validator import _numbers_in

SECONDARY_KINDS = ("news_release", "context_web", "secondary_summary")


class BuildError(RuntimeError):
    pass


def _load(name: str) -> dict:
    return json.loads((paths.CURATION_DIR / name).read_text())


def _extraction_verdicts() -> dict[str, dict]:
    out: dict[str, dict] = {}
    # unverified extractions first (verdict None -> NOT_VERIFIED), then verified finals override them
    for f in sorted(p for p in paths.EXTRACTED_DIR.glob("*.json") if not p.name.endswith(".final.json")):
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        for it in d.get("items", []):
            out[it["item_id"]] = {"verdict": None, "file": paths.rel(f), "item": it}
    for f in sorted(paths.EXTRACTED_DIR.glob("*.final.json")):
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        for it in d.get("items", []):
            v = (it.get("verification") or {}).get("verdict")
            out[it["item_id"]] = {"verdict": v, "file": paths.rel(f), "item": it}
    return out


def _allowed_numbers(obj) -> set[float]:
    return {round(abs(v), 9) for v, _, _ in _numbers_in(json.dumps(obj, ensure_ascii=False))}


def check_text_numbers(rec: dict, extra: list | None = None) -> list[str]:
    """Numbers in statement/technical_detail must appear in structured fields, anchor, location or source item."""
    struct = {k: v for k, v in rec.items() if k not in ("statement", "technical_detail", "limitations", "keywords")}
    allowed = _allowed_numbers([struct] + (extra or []))
    bad = []
    for field in ("statement", "technical_detail"):
        for v, pct, dec in _numbers_in(rec.get(field) or ""):
            cands = [(abs(v), dec)] + ([(abs(v) / 100, dec + 2)] if pct else [(abs(v) * 100, max(dec - 2, 0))])
            if not any(round(c, 9) in allowed or (d >= 1 and any(round(a, d) == round(c, d) for a in allowed)) for c, d in cands):
                bad.append(f"{field}: {v}{'%' if pct else ''}")
    return bad


def modelc_measured_records(registry: dict) -> list[dict]:
    """One derived record per material from Model C's measured-only dashboard table (no predictions)."""
    path = paths.MODEL_C_DIR / "data" / "processed" / "dashboard_measured_only.csv"
    text = path.read_text()
    rows = list(csv.DictReader(io.StringIO(text)))
    out = []
    for row in rows:
        n, k = int(row["n_runs"]), int(row["n_reaching_2v"])
        frac = float(row["fraction_reaching_2v"])
        if abs(frac - k / n) > 1e-12:
            raise BuildError(f"Model C fraction inconsistent for {row['material']}")
        line = next(l for l in text.splitlines() if l.startswith(row["material"] + ","))
        anchor = ",".join(line.split(",")[:5])
        limited = k < n
        cond = {"atmosphere_o2_vol_pct": None, "pressure_kpa": None,
                "airflow_cm_s": [float(row["airflow_cm_s_min"]), float(row["airflow_cm_s_max"])],
                "gravity": "microgravity", "heating_s": [float(row["heating_s_min"]), float(row["heating_s_max"])],
                "aging_s": [float(row["aging_s_min"]), float(row["aging_s_max"])]}
        mat = row["material"]
        stmt = (f"In the SAME and SAME-R primary heating runs, {mat} smoke pushed the ISS smoke-detector scatter signal to the "
                f"2.0 V level in {k} of {n} runs" + (f", so in {n - k} runs it stayed below that level." if limited else "."))
        detail = (f"Derived descriptive fraction {k}/{n} over {n} primary runs in {row['n_groups']} conservative sample groups "
                  f"(campaigns {row['campaigns'].replace(';', ', ')}); airflow {row['airflow_cm_s_min']}-{row['airflow_cm_s_max']} cm/s, "
                  f"heater resistance ratio {row['resistance_ratio_min']}-{row['resistance_ratio_max']}, heating "
                  f"{row['heating_s_min']}-{row['heating_s_max']} s, programmed aging {row['aging_s_min']}-{row['aging_s_max']} s, "
                  f"mixing {row['mixing_s_min']}-{row['mixing_s_max']} s; measured ISS scatter "
                  f"{float(row['iss_scatter_v_min']):.3f}-{float(row['iss_scatter_v_max']):.3f} V. The 2.0 V label is a derived "
                  "threshold (Meyer et al. 2018 Figure 9), not a recorded operational alarm, and the fraction is not an alarm probability.")
        rec = {
            "evidence_id": f"MODELC-EV-{mat.upper()}",
            "investigation": "SAME;SAME-R", "investigations": ["SAME", "SAME-R"], "psi_id": "PSI-102;PSI-101",
            "hardware_family": "ISS Microgravity Science Glovebox (MSG) - SAME/SAME-R hardware",
            "doc_id": "modelc_measured_only", "pdf_page": None,
            "source_location": f"external/model_c/data/processed/dashboard_measured_only.csv, row material={mat}",
            "anchor_quote": anchor,
            "material": mat, "materials": [mat],
            "detector": "ISS smoke detector (forward light scattering), scatter channel",
            "finding_type": "missed_alarm" if limited else "context",
            "observed_directly": True,
            "value": frac, "value_unit": "fraction of primary runs reaching 2.0 V ISS scatter",
            "value_kind": "derived",
            "value_definition": row["rule"],
            "label_source": "ISS scatter >= 2.0 V threshold from Meyer et al. 2018, Figure 9 (per Model C label_rule)",
            "counts": {"n_runs": n, "n_groups": int(row["n_groups"]), "n_reaching_2v": k, "n_below_2v": n - k},
            "test_ids": row["test_ids"].split(";"),
            "iss_scatter_v_range_measured": [float(row["iss_scatter_v_min"]), float(row["iss_scatter_v_max"])],
            "control_ranges": {key: [row[f"{key}_min"], row[f"{key}_max"], row[f"{key}_unit"]] for key in
                               ("airflow_cm_s", "resistance_ratio", "heating_s", "aging_s", "mixing_s")},
            "experimental_conditions": cond,
            "n_independent_tests": int(row["n_groups"]),
            "test_set": "SAME + SAME-R primary heating runs (secondary aging and DBP excluded); Model C audited workbook",
            "statement": stmt, "technical_detail": detail,
            "limitations": [
                "Derived 2.0 V threshold label, not a recorded operational alarm.",
                "Descriptive fraction of observed primary runs, not a detection probability for new fires.",
                "Different definition and test set from the 2021 white paper's no-alarm fractions; do not combine.",
                "Sample groups, not runs, are the conservative independent unit (reburns share samples).",
            ],
            "keywords": ["ISS detector", "2.0 V", "Model C", "SAME", "SAME-R", "scatter", "threshold", mat],
            "provenance": {"model": "model_c", "revision": json.loads(paths.MODELS_REGISTRY.read_text())["model_c"]["revision"],
                           "file_sha256": sha256_file(path)},
        }
        out.append(rec)
    return out


MODELC_TABLE = "external/model_c/data/processed/dashboard_table.csv"
BASELINE_RUNS = {"Kapton": ["SAME-R:51", "SAME-R:61", "SAME-R:73", "SAME-R:92"], "Teflon": ["SAME-R:56", "SAME-R:58", "SAME-R:79", "SAME-R:89"]}


def modelc_table_records() -> list[dict]:
    """Per-campaign split and baseline-run voltages computed directly from Model C's observation table (measured/derived)."""
    import pandas as pd

    path = paths.ROOT / MODELC_TABLE
    df = pd.read_csv(path)
    prim = df[df["training_eligible"] == True]  # noqa: E712  (primary heating runs, per Model C definition)
    rev = json.loads(paths.MODELS_REGISTRY.read_text())["model_c"]["revision"]
    out = []
    for mat in ("Kapton", "Teflon"):
        g = prim[prim["material"] == mat]
        per = {}
        for camp in ("SAME", "SAME-R"):
            c = g[g["campaign"] == camp]
            per[camp] = {"n_runs": int(len(c)), "n_reaching_2v": int(c["alarm_level_reached"].sum()),
                         "iss_scatter_v_min": round(float(c["iss_scatter_v"].min()), 3), "iss_scatter_v_max": round(float(c["iss_scatter_v"].max()), 3)}
        a, b = per["SAME"], per["SAME-R"]
        base = df[df["test_id"].isin(BASELINE_RUNS[mat])]
        bvals = sorted(round(float(v), 3) for v in base["iss_scatter_v"])
        settings = base.iloc[0]
        rec_c = {
            "evidence_id": f"MODELC-EV-{mat.upper()}-CAMPAIGNS",
            "investigation": "SAME;SAME-R", "investigations": ["SAME", "SAME-R"], "psi_id": "PSI-102;PSI-101",
            "hardware_family": "ISS Microgravity Science Glovebox (MSG) - SAME/SAME-R hardware",
            "doc_id": "modelc_dashboard_table", "pdf_page": None,
            "source_location": f"{MODELC_TABLE}, primary rows material={mat} grouped by campaign",
            "anchor_quote": BASELINE_RUNS[mat][0],
            "material": mat, "materials": [mat], "detector": "ISS smoke detector (forward light scattering), scatter channel",
            "finding_type": "missed_alarm", "observed_directly": True,
            "value": None, "value_unit": "runs reaching 2.0 V per campaign", "value_kind": "derived",
            "campaign_counts": per,
            "experimental_conditions": {"atmosphere_o2_vol_pct": None, "pressure_kpa": None, "airflow_cm_s": None,
                                        "gravity": "microgravity", "heating_s": None, "aging_s": None},
            "n_independent_tests": None,
            "conflict": {"kind": "between_campaigns", "with": [f"MODELC-EV-{mat.upper()}"],
                         "note": "Same material and hardware, different campaign (SAME 2007 vs SAME-R 2010); the sources examined give no explanation for the different detector response."},
            "statement": (f"The ISS detector's response to {mat} smoke differed between campaigns: {mat} reached the 2.0 V level in "
                          f"{a['n_reaching_2v']} of {a['n_runs']} SAME runs but in {b['n_reaching_2v']} of {b['n_runs']} SAME-R runs."),
            "technical_detail": (f"Measured ISS scatter: SAME {a['iss_scatter_v_min']}-{a['iss_scatter_v_max']} V, SAME-R {b['iss_scatter_v_min']}-"
                                 f"{b['iss_scatter_v_max']} V. The cause (campaign hardware state, sample batch, temperature control or "
                                 "other) is not resolved within the examined sources; the 2.0 V label is derived, not an alarm record."),
            "limitations": ["Derived 2.0 V threshold label, not a recorded alarm.", "Small per-campaign counts; cause of the difference unresolved."],
            "keywords": ["campaign", "SAME", "SAME-R", "2007", "2010", mat, "ISS detector", "conflict"],
            "provenance": {"model": "model_c", "revision": rev, "file_sha256": sha256_file(path)},
        }
        rec_b = {
            "evidence_id": f"MODELC-EV-{mat.upper()}-BASELINE",
            "investigation": "SAME-R", "investigations": ["SAME-R"], "psi_id": "PSI-101",
            "hardware_family": "ISS Microgravity Science Glovebox (MSG) - SAME/SAME-R hardware",
            "doc_id": "modelc_dashboard_table", "pdf_page": None,
            "source_location": f"{MODELC_TABLE}, rows {', '.join(BASELINE_RUNS[mat])} (unaged baseline runs averaged in the 2012 Table 1)",
            "anchor_quote": BASELINE_RUNS[mat][1],
            "material": mat, "materials": [mat], "detector": "ISS smoke detector (forward light scattering), scatter channel",
            "finding_type": "missed_alarm", "observed_directly": True,
            "value": None, "value_unit": "V (measured ISS scatter)", "value_kind": "measured",
            "measured_iss_scatter_v": bvals, "test_ids": BASELINE_RUNS[mat], "threshold_v": 2.0,
            "settings": {"airflow_cm_s": float(settings["airflow_cm_s"]), "resistance_ratio": float(settings["resistance_ratio"]),
                         "heating_s": float(settings["heating_s"]), "aging_s": float(settings["aging_s"]), "mixing_s": float(settings["mixing_s"])},
            "experimental_conditions": {"atmosphere_o2_vol_pct": None, "pressure_kpa": None, "airflow_cm_s": float(settings["airflow_cm_s"]),
                                        "gravity": "microgravity", "heating_s": float(settings["heating_s"]), "aging_s": float(settings["aging_s"])},
            "n_independent_tests": len(BASELINE_RUNS[mat]),
            "statement": (f"At the SAME-R baseline setting, all {len(bvals)} unaged {mat} runs kept the ISS detector scatter signal below 2.0 V "
                          f"({bvals[0]}-{bvals[-1]} V measured)."),
            "technical_detail": (f"Runs {', '.join(BASELINE_RUNS[mat])}: airflow {settings['airflow_cm_s']} cm/s, heater resistance ratio "
                                 f"{settings['resistance_ratio']}, heating {settings['heating_s']} s, aging {settings['aging_s']} s, mixing "
                                 f"{settings['mixing_s']} s, microgravity (ISS). These are the runs averaged in the 2012 Table 1 particle-size row. "
                                 "Measured voltages; the 2.0 V comparison level is a derived threshold, not an alarm record."),
            "limitations": ["Four runs at one setting; not a detection probability.", "2.0 V is a derived threshold from Meyer et al. 2018 Figure 9."],
            "keywords": ["baseline", "unaged", mat, "ISS detector", "measured", "below 2.0 V"],
            "provenance": {"model": "model_c", "revision": rev, "file_sha256": sha256_file(path)},
        }
        out += [rec_c, rec_b]
    return out


def autofill_from_item(rec: dict, verdicts: dict) -> dict:
    """Fill doc_id / pdf_page / source_location / anchor_quote from the verified extraction item when not curated."""
    item = verdicts.get(rec.get("extraction_item") or "")
    if not item:
        return rec
    it = item["item"]
    rec.setdefault("doc_id", it.get("doc_id"))
    rec.setdefault("pdf_page", it.get("pdf_page"))
    rec.setdefault("anchor_quote", it.get("anchor_quote"))
    if "source_location" not in rec:
        loc = it.get("location") or ""
        page = f"PDF p. {it['pdf_page']}" if it.get("pdf_page") else None
        rec["source_location"] = ", ".join(x for x in (page, loc) if x)
    return rec


def finalize_record(rec: dict, registry: dict, verdicts: dict) -> dict:
    rec = autofill_from_item(rec, verdicts)
    doc = registry.get(rec["doc_id"])
    if doc is None:
        raise BuildError(f"{rec['evidence_id']}: unknown doc_id {rec['doc_id']}")
    rec.setdefault("investigations", [rec["investigation"]] if rec.get("investigation") else [])
    rec.setdefault("materials", [rec["material"]] if rec.get("material") else [])
    rec["source_title"] = doc.get("title")
    rec["source_year"] = doc.get("year")
    rec["source_url"] = doc.get("url")
    ids = doc.get("identifiers") or {}
    for k, alt in (("doi", "doi"), ("ntrs_id", "ntrs"), ("psi_id_doc", "psi"), ("pmc_id", "pmc")):
        val = doc.get(k) or ids.get(alt)
        if val:
            rec[k if k != "psi_id_doc" else "source_psi_id"] = val
    rec["source_kind"] = doc.get("kind")
    for k in CONDITION_KEYS:
        rec["experimental_conditions"].setdefault(k, None)

    check = verify_anchor(rec["doc_id"], rec.get("pdf_page"), rec["anchor_quote"], doc.get("text_file"))
    rec["anchor_check"] = check
    item = verdicts.get(rec.get("extraction_item") or "")
    rec["extraction_verification"] = ({"item_id": rec["extraction_item"], "verdict": item["verdict"], "file": item["file"]}
                                      if item else ({"item_id": rec.get("extraction_item"), "verdict": None} if rec.get("extraction_item") else None))
    if not doc.get("accessible", True):
        audit = "MISSING"
    elif not check["found"] or (item and item["verdict"] in ("REJECTED", None)):
        audit = "NOT_VERIFIED"
    elif doc.get("kind") in SECONDARY_KINDS:
        audit = "REPORTED_ONLY"
    else:
        audit = "VERIFIED"
    rec["audit_status"] = audit
    cls, rule = classify_record(rec)
    rec["classification"], rec["classification_rule"] = cls, rule

    extra = [item["item"]] if item else []
    bad = check_text_numbers(rec, extra)
    if bad:
        raise BuildError(f"{rec['evidence_id']}: numbers in text not traceable to fields/source: {bad}")
    check_evidence_record(rec)
    return rec


def build(write: bool = True) -> dict:
    registry = load_registry()
    verdicts = _extraction_verdicts()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    curated = _load("evidence_curated.json")["records"]
    records = modelc_measured_records(registry) + modelc_table_records() + curated
    ids = [r["evidence_id"] for r in records]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise BuildError(f"duplicate evidence ids {dup}")
    finalized, problems = [], []
    for r in records:
        try:
            finalized.append(finalize_record(dict(r), registry, verdicts))
        except (BuildError, KeyError) as e:
            problems.append(f"{r.get('evidence_id')}: {type(e).__name__}: {e}")
    if problems:
        raise BuildError("record problems:\n  " + "\n  ".join(problems))
    records = finalized
    by_id = {r["evidence_id"]: r for r in records}
    for r in records:
        for rel_id in r.get("related_evidence", []) + list((r.get("conflict") or {}).get("with", [])):
            if rel_id not in by_id:
                raise BuildError(f"{r['evidence_id']}: related id {rel_id} unknown")

    # investigation profiles: verify every supporting anchor
    profiles = _load("profiles_curated.json")["profiles"]
    for p in profiles:
        for s in p.get("sources", []):
            it = verdicts.get(s.get("item") or "")
            if it:
                s.setdefault("doc_id", it["item"].get("doc_id"))
                s.setdefault("pdf_page", it["item"].get("pdf_page"))
                s.setdefault("anchor_quote", it["item"].get("anchor_quote"))
                s["extraction_verdict"] = it["verdict"]
            elif s.get("item"):
                raise BuildError(f"profile {p['investigation']}: extraction item {s['item']} not found in verified extractions")
            doc = registry.get(s["doc_id"], {})
            s["anchor_check"] = verify_anchor(s["doc_id"], s.get("pdf_page"), s["anchor_quote"], doc.get("text_file"))
            s["source_title"], s["source_url"] = doc.get("title"), doc.get("url")
        p["sources_verified"] = all(s["anchor_check"]["found"] and s.get("extraction_verdict") != "REJECTED" for s in p.get("sources", []))
        for i in p.get("evidence_ids", []):
            if i not in by_id:
                raise BuildError(f"profile {p['investigation']}: unknown evidence id {i}")

    probes = _load("gap_probes.json")["probes"]
    gap_list, probe_log = gaps_mod.evaluate(probes, records, profiles)
    for g in gap_list:
        bad = check_text_numbers({"statement": g["statement"], "technical_detail": g.get("detail") or "", "rule_result": g["rule_result"]},
                                 [by_id[i] for i in g["evidence_ids"]])
        if bad:
            raise BuildError(f"{g['gap_id']}: untraceable numbers {bad}")

    cands = _load("priority_candidates.json")["candidates"]
    prios = priority.rank_candidates(cands, records, gap_list, profiles)

    comp = _load("comparisons.json")
    for c in comp["comparisons"]:
        for i in c.get("evidence_ids", []):
            if i not in by_id:
                raise BuildError(f"{c['comparison_id']}: unknown evidence id {i}")
        bad = check_text_numbers({"statement": c["statement"], "technical_detail": c.get("detail", "")}, [by_id[i] for i in c["evidence_ids"]])
        if bad:
            raise BuildError(f"{c['comparison_id']}: untraceable numbers {bad}")
        c["source_title"] = "QK norm cross-source comparison"
        c["source_year"] = None
        c["source_location"] = "computed from " + ", ".join(c["evidence_ids"])

    chronology = {"stages": []}
    for st in comp["chronology"]["stages"]:
        for i in st["evidence_ids"]:
            if i not in by_id:
                raise BuildError(f"chronology {st['year']}: unknown id {i}")
        chronology["stages"].append(st)
    chronology["links"] = comp["chronology"].get("links", [])
    for ln in chronology["links"]:
        for i in ln["from"] + ln["to"]:
            if i not in by_id:
                raise BuildError(f"chronology link unknown id {i}")

    header = {"schema_version": SCHEMA_VERSION, "generated_utc": now, "project": "QK norm - Agent 5 BlindSpot Evidence Agent",
              "scope_note": f"All gap statements are limited to the examined sources ('{SCOPE_PHRASE}')."}
    outputs = {
        "evidence_records.json": header | {"classification_rules": [{"id": i, "rule": t} for i, t in RULES], "records": records},
        "investigation_profiles.json": header | {"profiles": profiles},
        "research_gaps.json": header | {"gaps": gap_list, "probe_log": probe_log,
                                         "record_class_counts": _class_counts(records)},
        "research_priorities.json": header | {"ranking_method": "lexicographic over criteria levels in this order",
                                               "criteria": [{"name": n, "rule": t} for n, t in priority.CRITERIA],
                                               "priorities": prios},
        "scientific_comparisons.json": header | {"comparisons": comp["comparisons"], "chronology": chronology},
        "source_manifest.json": header | {"documents": _manifest(registry, records)},
    }
    if write:
        paths.OUTPUTS.mkdir(parents=True, exist_ok=True)
        for name, doc in outputs.items():
            (paths.OUTPUTS / name).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    return {"n_records": len(records), "classes": _class_counts(records), "n_gaps": len(gap_list),
            "n_priorities": len(prios), "anchor_failures": [r["evidence_id"] for r in records if not r["anchor_check"]["found"]],
            "profile_anchor_failures": [p["investigation"] for p in profiles if not p["sources_verified"]]}


def _class_counts(records: list[dict]) -> dict:
    out: dict[str, int] = {}
    for r in records:
        k = r["classification"] or "none (context / follow-up)"
        out[k] = out.get(k, 0) + 1
    return out


def _manifest(registry: dict, records: list[dict]) -> list[dict]:
    used: dict[str, list[str]] = {}
    for r in records:
        used.setdefault(r["doc_id"], []).append(r["evidence_id"])
    docs = []
    for doc_id, d in sorted(registry.items()):
        lp = d.get("local_path")
        p = (paths.ROOT / lp) if lp else None
        entry = {k: d.get(k) for k in ("doc_id", "title", "year", "authors", "url", "doi", "ntrs_id", "psi_id_doc", "pmc_id",
                                       "kind", "accessible", "access_note", "license_note", "source_audit_status", "source_audit_note")}
        entry["local_path"] = lp
        entry["text_path"] = d.get("text_file") or (paths.rel(paths.TEXT_DIR / f"{doc_id}.txt") if (paths.TEXT_DIR / f"{doc_id}.txt").exists() else None)
        if p and p.exists() and p.is_file():
            entry["sha256_now"] = sha256_file(p)
            entry["bytes"] = p.stat().st_size
            if d.get("sha256") and d["sha256"] != entry["sha256_now"]:
                entry["sha256_mismatch"] = True
        entry["evidence_ids"] = sorted(used.get(doc_id, []))
        docs.append(entry)
    return docs
