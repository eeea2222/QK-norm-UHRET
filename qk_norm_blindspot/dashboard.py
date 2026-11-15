"""QK norm BlindSpot Explorer: dashboard JSON + a self-contained static HTML view (data inlined)."""
from __future__ import annotations

import html
import json

from . import paths
from .store import get_store

EXAMPLE_QUESTION = "What limitations have NASA experiments identified in spacecraft smoke detection?"


def _value_str(r: dict) -> str | None:
    v = r.get("value")
    if v is None:
        return None
    if r.get("counts"):
        c = r["counts"]
        return f"{c['n_reaching_2v']}/{c['n_runs']} runs reached 2.0 V"
    return r.get("value_verbatim") or str(v)


def build_dashboard_data(use_llm: bool = False) -> dict:
    from .agent import analyze_blindspots
    from . import side_panels, model_c

    s = get_store()
    by = s.by_id
    verified = [r for r in s.records if r["classification"] == "VERIFIED_LIMITATION"]
    flow = []
    for p in s.priorities:
        probs = [by[i] for i in p["existing_evidence"] if by.get(i, {}).get("classification") == "VERIFIED_LIMITATION"]
        needs = [by[i] for i in p["existing_evidence"] if by.get(i, {}).get("classification") == "EVIDENCE_GAP"]
        flow.append({
            "priority_id": p["priority_id"], "rank": p["rank"],
            "problem": [{"evidence_id": r["evidence_id"], "statement": r["statement"], "value": _value_str(r),
                         "value_kind": r["value_kind"], "source": f"{r['source_title']} ({r['source_year']}), {r['source_location']}"} for r in probs[:2]]
                       or [{"evidence_id": r["evidence_id"], "statement": r["statement"], "value": None, "value_kind": r["value_kind"],
                            "source": f"{r['source_title']} ({r['source_year']}), {r['source_location']}"} for r in needs[:1]],
            "evidence": p["existing_evidence"], "gap": p["evidence_gap"], "question": p["research_question"],
            "criteria_levels": p["criteria_levels"],
        })
    example = analyze_blindspots(EXAMPLE_QUESTION, use_llm=use_llm)
    try:
        a = side_panels.model_a_panel()
    except Exception as e:  # side panel must never break the dashboard
        a = {"model": "model_a", "status": "FAILED", "error": str(e)}
    try:
        b = side_panels.model_b_panel()
    except Exception as e:
        b = {"model": "model_b", "status": "FAILED", "error": str(e)}
    mo = model_c.measured_only()
    measured_rows = [{k: (None if (isinstance(v, float) and v != v) else v) for k, v in row.items()} for row in mo.to_dict("records")]
    docs = json.loads((paths.OUTPUTS / "source_manifest.json").read_text())["documents"]
    models_3d = []
    entries = [
      ("cabin_transport", "Cabin smoke transport", "Ventilation can carry smoke toward a return-mounted detector. The path shown explains the concept; it does not predict arrival time.", "Orange: overheated material · sand: smoke markers · cyan: ventilation guides · green: detector", ["M18-EV-004", "WP21-EV-007"]),
      ("optical_detector", "Optical detector cutaway", "A schematic emitter, aerosol and receiver illustrate why particle properties matter to a light-scattering sensor. Beam directions and geometry are illustrative.", "Cyan: emitter / incident light · sand: aerosol markers · green: receiver", ["M18-EV-002"]),
      ("aging_chamber", "Smoke aging and diagnostics", "A conceptual sample-to-aging-chamber-to-diagnostics chain introduces the SAME/SAME-R measurement approach.", "Orange: sample · silver: chamber cutaway · sand: aerosol markers · green: diagnostics", ["SAMER-EV-001", "SAME-EV-008"]),
    ]
    for key, title, description, legend, ids in entries:
        meshpath = paths.DASHBOARD_DIR / "assets/3d" / (key + ".json")
        if meshpath.exists():
            models_3d.append({"key": key, "title": title, "description": description, "legend": legend,
                              "evidence_ids": [i for i in ids if i in by], "mesh": json.loads(meshpath.read_text())})
    sample_a = json.loads((paths.MODEL_A_DIR / 'artifacts/model_a_v1/sample_request.json').read_text())
    second_a = {**sample_a, 'velocity_cm_s': 6.0}
    units = {'airflow_cm_s':'cm/s','resistance_ratio':'1','heating_s':'s','aging_s':'s','mixing_s':'s'}
    c_presets = []
    for mat in ('Kapton', 'Teflon', 'Silicone', 'Pyrell', 'Lampwick'):
        row = model_c.dashboard_table().query('material == @mat and training_eligible == True').iloc[0]
        inp = {'material':mat, **{k:float(row[k]) for k in units}, 'units':units}
        c_presets.append({'label':f'{mat} · kayıtlı koşul ({row["test_id"]})','input':inp})
    c_presets.append({'label':'Kapton · kapsam dışı (OOD) örneği','input':{'material':'Kapton','airflow_cm_s':0.0,'resistance_ratio':1.22,'heating_s':10.0,'aging_s':1.0,'mixing_s':0.0,'units':units}})
    ai_presets = {
        'a':[{'label':'Yayınlanmış örnek girdi','input':sample_a},{'label':'Hava hızı 6 cm/s · düzenlenmiş deneme','input':second_a}],
        'b':[{'label':'Gerçek Saffire-I örnek karesi','input':{}}],
        'c':c_presets,
        'wt4':[{'label':'Kısa selamlama · hızlı test','input':{'prompt':'Say hello in one short sentence.','max_new_tokens':32}},
               {'label':'Mikro yerçekimini açıkla','input':{'prompt':'Explain microgravity in two short sentences.','max_new_tokens':100}}]}
    from .benchmarks import build_benchmarks
    return {
        "benchmarks": build_benchmarks(),
        "ai_presets": ai_presets,
        "models_3d": models_3d,
        "title": "QK norm BlindSpot Explorer",
        "rag_enabled": False,
        "scientific_validation_status": "DEFERRED_BY_REQUEST",
        "tagline": "NASA's documented problem -> existing evidence -> research question",
        "scope_note": "Scientific validation deferred by request. Existing audit labels are preserved. All gap statements are limited to the examined sources. Not a safety certification or alarm setting.",
        "example_question": EXAMPLE_QUESTION,
        "example_response": example,
        "flow": flow,
        "sections": {
            "verified_findings": [{"evidence_id": r["evidence_id"], "statement": r["statement"], "technical_detail": r["technical_detail"],
                                   "material": r.get("material"), "detector": r.get("detector"), "investigation": r.get("investigation"),
                                   "value": _value_str(r), "value_kind": r["value_kind"], "conditions": r["experimental_conditions"],
                                   "n_independent_tests": r["n_independent_tests"], "source_title": r["source_title"],
                                   "source_year": r["source_year"], "source_location": r["source_location"], "source_url": r["source_url"],
                                   "doi": r.get("doi"), "limitations": r["limitations"]} for r in verified],
            "scientific_comparison": {"comparisons": s.comparisons, "chronology": s.chronology},
            "knowledge_gaps": s.gaps,
            "research_priorities": s.priorities,
            "supporting_evidence": [d for d in docs if d.get("evidence_ids")],
        },
        "side_panels": {
            "model_c_measured_only": {"rows": measured_rows, "value_kind": "derived (fractions) / measured (scatter V)",
                                      "note": "Descriptive fractions of observed primary runs, not alarm probabilities."},
            "model_a": a, "model_b": b,
            "note": "Models A, B and C represent different experiments; they do not form a synchronized fire scenario or a combined hazard score.",
        },
    }


def write_dashboard_data(use_llm: bool = False) -> dict:
    data = build_dashboard_data(use_llm=use_llm)
    paths.DASHBOARD_DIR.mkdir(exist_ok=True)
    (paths.DASHBOARD_DIR / "dashboard_data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n")
    tpl = (paths.PACKAGE_DIR / "dashboard_template.html").read_text()
    blob = json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/")
    (paths.DASHBOARD_DIR / "index.html").write_text(tpl.replace("/*__DATA__*/null", blob).replace("/*__VIEWER3D__*/", (paths.PACKAGE_DIR / "viewer3d.js").read_text()).replace("/*__PLAYGROUND__*/", (paths.PACKAGE_DIR / "playground.js").read_text()).replace("/*__AIVIS__*/", (paths.PACKAGE_DIR / "ai_visual.js").read_text()))
    return {"json": str(paths.DASHBOARD_DIR / "dashboard_data.json"), "html": str(paths.DASHBOARD_DIR / "index.html"),
            "n_verified": len(data["sections"]["verified_findings"]), "n_gaps": len(data["sections"]["knowledge_gaps"]),
            "n_priorities": len(data["sections"]["research_priorities"])}
