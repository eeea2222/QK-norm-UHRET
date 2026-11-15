"""Create text renderings + meta.json for the same_profiles source group.

Reads Model C read-only snapshot; writes only under sources/.
Run with: .venv/bin/python -I make_texts_meta.py
"""
import hashlib, json, os, shutil, datetime

ROOT = "/home/efeai/Desktop/NasaSpaceApps"
MC = f"{ROOT}/external/model_c"
RAW = f"{MC}/data/raw"
SRC = f"{ROOT}/sources"
HF = "https://huggingface.co/efe-T/nasa-same-model-c/blob/91292a40886564d146dc9e9d496b74c2aefaab5c"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def mtime_utc(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- text renderings for non-PDF docs ----
def flatten(x, path="$"):
    out = []
    if isinstance(x, dict):
        for k, v in x.items():
            out += flatten(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            out += flatten(v, f"{path}[{i}]")
    else:
        out.append((path, x))
    return out


def render_meta(src, dst):
    d = json.load(open(src))
    lines = []
    for path, val in flatten(d):
        # keep file inventories short: only names/sizes/subcategory
        if path.startswith(("$.added[", "$.removed[")) and not path.endswith((".file_name", ".subcategory", ".file_size")):
            continue
        if path.startswith("$.experimentalTable[") and not path.endswith((".file_name", ".file_size")):
            continue
        lines.append(f"{path} = {val}")
    open(dst, "w").write("\n".join(lines) + "\n")


os.makedirs(f"{SRC}/text", exist_ok=True)
render_meta(f"{RAW}/PSI-102-metadata.json", f"{SRC}/text/psi102_meta.txt")
render_meta(f"{RAW}/PSI-101-metadata.json", f"{SRC}/text/psi101_meta.txt")
shutil.copyfile(f"{RAW}/PSI-102_Experimental table_SAME.csv", f"{SRC}/text/same_csv.txt")
shutil.copyfile(f"{RAW}/PSI-101_Experimental table_SAME-R.csv", f"{SRC}/text/samer_csv.txt")
shutil.copyfile(f"{MC}/reports/SAME smoke detector evidence.md", f"{SRC}/text/modelc_same_evidence.txt")
shutil.copyfile(f"{MC}/research_notes/SAME smoke detector evidence/references.md", f"{SRC}/text/modelc_refs.txt")
shutil.copyfile(f"{MC}/reports/material_majority_oof.csv", f"{SRC}/text/modelc_material_oof.txt")

manifest = {e["path"]: e for e in json.load(open(f"{RAW}/source_manifest.json"))}

PSI_DL = "https://psi.nasa.gov/geode-py/ws/studies/{s}/download?file={f}&version=4&redirect=false"
docs = [
    dict(doc_id="same_report", title="Smoke Aerosol Measurement Experiment (SAME) - Final Report (Nov 1, 2000 - Apr 14, 2009), dated March 15, 2010, with appended papers (Appendices B-E)",
         year=2010, authors=["David L. Urban", "Gary A. Ruff", "William Sheredy", "Thomas Cleary", "Jiann Yang", "George Mulholland", "Zeng-Guang Yuan"],
         url=PSI_DL.format(s="PSI-102", f="PSI-102_Reports_SAME_Final%20Science%20Report.pdf"),
         src=f"{RAW}/PSI-102_Reports_SAME_Final Science Report.pdf", manifest_key="data/raw/PSI-102_Reports_SAME_Final Science Report.pdf",
         page_count=68, identifiers=dict(doi="10.60555/gd4k-8h62 (PSI-102 investigation DOI, not a DOI of this PDF)", ntrs=None, psi="PSI-102", pmc=None),
         access_note="Read from the audited Model C read-only snapshot (not copied). sha256 matches Model C source_manifest.json. pdfinfo: 68 pages, PDF title 'SAME Final Science report 03 17 10 b no papers attached.docx' although Appendices B-E (2009 ICES, 2009 AIAA, 2008 ICES, 2008 AIAA papers) ARE appended as PDF pages 35-67. Cover date March 15, 2010 (Model C notes cite a NIST-hosted version dated March 5, 2010; not compared here). Text made with plain pdftotext."),
    dict(doc_id="samer_report", title="Smoke Aerosol Measurement Experiment Re-flight (SAMER) - Final Report, June 2, 2014 (with Appendices A-F)",
         year=2014, authors=["David L. Urban", "Gary A. Ruff", "William Sheredy", "Marit Meyer", "Thomas Cleary", "Jiann Yang", "George Mulholland", "Zeng-Guang Yuan"],
         url=PSI_DL.format(s="PSI-101", f="PSI-101_Reports_SAME-R_Final%20Report.pdf"),
         src=f"{RAW}/PSI-101_Reports_SAME-R_Final Report.pdf", manifest_key="data/raw/PSI-101_Reports_SAME-R_Final Report.pdf",
         page_count=89, identifiers=dict(doi="10.60555/2np7-jv14 (PSI-101 investigation DOI, not a DOI of this PDF)", ntrs=None, psi="PSI-101", pmc=None),
         access_note="Read from the audited Model C read-only snapshot (not copied). sha256 matches Model C source_manifest.json. 89 pages; PDF page 50 (Appendix B) is blank apart from its heading; PDF page 85 contains only the text 'SAMER flowdiagram' (figure not extractable as text). Appendix F (PDF pp72-84) is the paper 'Particle Morphology and Size Results from the Smoke Aerosol Measurement Experiment-2'. Text made with plain pdftotext."),
    dict(doc_id="psi102_meta", title="NASA PSI repository metadata for PSI-102 (SAME), investigation version 4",
         year=2025, authors=["NASA Physical Sciences Informatics (PSI) repository"],
         url="https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-102",
         src=f"{RAW}/PSI-102-metadata.json", manifest_key="data/raw/PSI-102-metadata.json", page_count=None,
         identifiers=dict(doi="10.60555/gd4k-8h62", ntrs=None, psi="PSI-102", pmc=None),
         access_note="JSON from the audited Model C snapshot; sources/text/psi102_meta.txt is a flattened 'json.path = value' rendering (file-inventory entries reduced to file_name/file_size/subcategory). modifiedDate 02-Jun-2025, releaseDate 18-Sep-2024. Location fields of items are JSON paths."),
    dict(doc_id="psi101_meta", title="NASA PSI repository metadata for PSI-101 (SAME-R), investigation version 4",
         year=2025, authors=["NASA Physical Sciences Informatics (PSI) repository"],
         url="https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-101",
         src=f"{RAW}/PSI-101-metadata.json", manifest_key="data/raw/PSI-101-metadata.json", page_count=None,
         identifiers=dict(doi="10.60555/2np7-jv14", ntrs=None, psi="PSI-101", pmc=None),
         access_note="JSON from the audited Model C snapshot; sources/text/psi101_meta.txt is a flattened 'json.path = value' rendering (file-inventory entries reduced to file_name/file_size/subcategory). Location fields of items are JSON paths."),
    dict(doc_id="same_csv", title="PSI-102 Experimental table_SAME.csv (planned test conditions)",
         year=None, authors=["NASA PSI repository (SAME team)"],
         url=PSI_DL.format(s="PSI-102", f="PSI-102_Experimental%20table_SAME.csv"),
         src=f"{RAW}/PSI-102_Experimental table_SAME.csv", manifest_key="data/raw/PSI-102_Experimental table_SAME.csv", page_count=None,
         identifiers=dict(doi="10.60555/gd4k-8h62 (investigation)", ntrs=None, psi="PSI-102", pmc=None),
         access_note="331-byte CSV from the audited Model C snapshot; text copy in sources/text/same_csv.txt. Location = file + row."),
    dict(doc_id="samer_csv", title="PSI-101 Experimental table_SAME-R.csv (run and aging index)",
         year=None, authors=["NASA PSI repository (SAME-R team)"],
         url=PSI_DL.format(s="PSI-101", f="PSI-101_Experimental%20table_SAME-R.csv"),
         src=f"{RAW}/PSI-101_Experimental table_SAME-R.csv", manifest_key="data/raw/PSI-101_Experimental table_SAME-R.csv", page_count=None,
         identifiers=dict(doi="10.60555/2np7-jv14 (investigation)", ntrs=None, psi="PSI-101", pmc=None),
         access_note="5,674-byte CSV from the audited Model C snapshot; text copy in sources/text/samer_csv.txt. Location = file + row."),
    dict(doc_id="modelc_same_evidence", title="Model C report: 'SAME smoke detector evidence.md' (project-internal audit, not a NASA document)",
         year=2026, authors=["QK norm project, Model C audit"],
         url=f"{HF}/reports/SAME%20smoke%20detector%20evidence.md",
         src=f"{MC}/reports/SAME smoke detector evidence.md", manifest_key=None, page_count=None,
         identifiers=dict(doi=None, ntrs=None, psi=None, pmc=None),
         access_note="Project-internal derived analysis (HF efe-T/nasa-same-model-c @ 91292a40886564d146dc9e9d496b74c2aefaab5c). Its 2.0 V labels are DERIVED, not NASA-reported alarm events. Text copy in sources/text/modelc_same_evidence.txt."),
    dict(doc_id="modelc_refs", title="Model C research note: 'SAME smoke detector evidence/references.md' (project-internal)",
         year=2026, authors=["QK norm project, Model C audit"],
         url=f"{HF}/research_notes/SAME%20smoke%20detector%20evidence/references.md",
         src=f"{MC}/research_notes/SAME smoke detector evidence/references.md", manifest_key=None, page_count=None,
         identifiers=dict(doi=None, ntrs=None, psi=None, pmc=None),
         access_note="Project-internal notes summarising Meyer et al. 2018 and NTRS papers (secondhand for those papers; the primary papers are handled by other source groups). Text copy in sources/text/modelc_refs.txt."),
    dict(doc_id="modelc_material_oof", title="Model C output: reports/material_majority_oof.csv (per-run derived ISS >=2.0 V reference labels, 84 primary runs)",
         year=2026, authors=["QK norm project, Model C"],
         url=f"{HF}/reports/material_majority_oof.csv",
         src=f"{MC}/reports/material_majority_oof.csv", manifest_key=None, page_count=None,
         identifiers=dict(doi=None, ntrs=None, psi=None, pmc=None),
         access_note="Column 'reference' = Model C derived label (ISS scatter >= 2.0 V from the official combined workbook). Per-material counts in items were computed by this agent with pandas groupby. Text copy in sources/text/modelc_material_oof.txt."),
]

out_docs = []
for d in docs:
    p = d["src"]
    h = sha(p)
    man = manifest.get(d["manifest_key"]) if d["manifest_key"] else None
    match = (man["sha256"] == h) if man else None
    meta = dict(doc_id=d["doc_id"], title=d["title"], year=d["year"], authors=d["authors"], url=d["url"],
                retrieved_utc=mtime_utc(p), sha256=h, bytes=os.path.getsize(p), page_count=d["page_count"],
                identifiers=d["identifiers"],
                license_note=("PSI investigation metadata reports licenseIdentifier CC0-1.0 (Creative Commons Zero v1.0)." if d["doc_id"] in ("same_report", "samer_report", "psi102_meta", "psi101_meta", "same_csv", "samer_csv")
                              else "Project-internal Model C artifact (see LICENSE/NOTICE in the Model C snapshot)."),
                accessible=True,
                access_note=d["access_note"] + (f" Manifest sha256 check: {'MATCH' if match else 'MISMATCH'}." if man is not None else " Not listed in source_manifest.json (project artifact)."),
                local_path=os.path.relpath(p, ROOT),
                text_path=f"sources/text/{d['doc_id']}.txt",
                retrieved_note="retrieved_utc is the mtime of the Model C snapshot file (download time of the snapshot), not a fresh fetch.")
    os.makedirs(f"{SRC}/raw/{d['doc_id']}", exist_ok=True)
    json.dump(meta, open(f"{SRC}/raw/{d['doc_id']}/meta.json", "w"), indent=1, ensure_ascii=False)
    out_docs.append(meta)
    print(d["doc_id"], h[:16], meta["bytes"], "manifest:", match)

json.dump(out_docs, open("/tmp/claude-1000/-home-efeai-Desktop-NasaSpaceApps/6a4d6a96-8583-4b8d-bd50-35dfffa09cc3/scratchpad/same_profiles/docs.json", "w"), indent=1, ensure_ascii=False)
