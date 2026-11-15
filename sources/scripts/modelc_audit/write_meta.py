import json, hashlib, os
MC = "/home/efeai/Desktop/NasaSpaceApps/external/model_c"
RAW = "/home/efeai/Desktop/NasaSpaceApps/sources/raw"
SNAP = "Copied from read-only Model C snapshot (HF efe-T/nasa-same-model-c @ 91292a40886564d146dc9e9d496b74c2aefaab5c); not re-downloaded by this agent (disk limit). Original retrieval time not recorded in the snapshot."
def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
def pages(txt):
    return open(txt, encoding="utf-8").read().count("\f")
docs = [
 dict(doc_id="modelc-ntrs20130000422", title="Particle Morphology and Size Results from the Smoke Aerosol Measurement Experiment-2", year=2012,
      authors=["David L. Urban", "Gary A. Ruff", "Paul S. Greenberg", "David Fischer", "Marit Meyer", "George Mulholland", "Zeng-guang Yuan", "Victoria Bryg", "Thomas Cleary", "Jiann Yang"],
      url="https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf", src=f"{MC}/data/references/20130000422.pdf",
      identifiers=dict(doi="10.2514/6.2012-3536", ntrs="20130000422", psi=None, pmc=None),
      license_note="AIAA conference paper (42nd ICES, AIAA 2012-3536); third-party publication, original terms retained; quotes limited to short anchors.",
      extra="Same paper is attached as Appendix F of the SAME-R final report."),
 dict(doc_id="modelc-ntrs20120012884", title="Properties of Smoke from Overheated Materials in Low-Gravity", year=None,
      authors=["David L. Urban", "Gary A. Ruff", "William Sheredy", "Thomas Cleary", "Jiann Yang", "George Mulholland", "Zeng-guang Yuan"],
      url="https://ntrs.nasa.gov/api/citations/20120012884/downloads/20120012884.pdf", src=f"{MC}/data/references/20120012884.pdf",
      identifiers=dict(doi=None, ntrs="20120012884", psi=None, pmc=None),
      license_note="AIAA paper hosted on NTRS; third-party publication, original terms retained.",
      extra="Publication year not printed in the extracted text; PDF metadata title reads 'SAME AIAA paper Jan 2009 3 18 10 corrected.doc' (so year left null). Also attached as Appendix C of the SAME final report."),
 dict(doc_id="modelc-psi102-same-final-report", title="Smoke Aerosol Measurement Experiment (SAME) Final Report (covering November 1, 2000 - April 14, 2009; dated March 15, 2010)", year=2010,
      authors=["David L. Urban", "Gary A. Ruff", "William Sheredy", "Thomas Cleary", "Jiann Yang", "George Mulholland", "Zeng-Guang Yuan"],
      url="https://psi.nasa.gov/geode-py/ws/studies/PSI-102/download?file=PSI-102_Reports_SAME_Final%20Science%20Report.pdf&version=4&redirect=false", src=f"{MC}/data/raw/PSI-102_Reports_SAME_Final Science Report.pdf",
      identifiers=dict(doi=None, ntrs=None, psi="PSI-102", pmc=None),
      license_note="NASA PSI dataset file; Model C STATUS.json records PSI source datasets as CC0-1.0 (not independently re-verified here).",
      extra="Appendices B-E are attached conference papers (B: SAE 2009-01-2468; C: Properties of Smoke...; D: SAE 2008-01-2089; E: Spacecraft Fire Detection: Smoke Properties and Transport in Low-Gravity)."),
 dict(doc_id="modelc-psi101-samer-final-report", title="Smoke Aerosol Measurement Experiment Re-flight (SAMER) Final Report (dated June 2, 2014)", year=2014,
      authors=["David L. Urban", "Gary A. Ruff", "William Sheredy", "Marit Meyer", "Thomas Cleary", "Jiann Yang", "George Mulholland", "Zeng-Guang Yuan"],
      url="https://psi.nasa.gov/geode-py/ws/studies/PSI-101/download?file=PSI-101_Reports_SAME-R_Final%20Report.pdf&version=4&redirect=false", src=f"{MC}/data/raw/PSI-101_Reports_SAME-R_Final Report.pdf",
      identifiers=dict(doi=None, ntrs=None, psi="PSI-101", pmc=None),
      license_note="NASA PSI dataset file; Model C STATUS.json records PSI source datasets as CC0-1.0 (not independently re-verified here).",
      extra="Appendix F (PDF p72 onward) reproduces NTRS 20130000422."),
 dict(doc_id="modelc-pmc7918997", title="Evaluation of Spacecraft Smoke Detector Performance in the Low-Gravity Environment (author manuscript)", year=2018,
      authors=["Marit Meyer", "David Urban", "George Mulholland", "Victoria Bryg", "Zengguang Yuan", "Gary Ruff", "Thomas Cleary", "Jiann Yang"],
      url="https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/", src=f"{MC}/data/references/PMC7918997.html",
      identifiers=dict(doi="10.1016/j.firesaf.2018.04.004", ntrs=None, psi=None, pmc="PMC7918997"),
      license_note="PMC author manuscript of a Fire Safety Journal article (vol. 98, 2018); original terms retained.",
      extra="HTML converted with stdlib html.parser; location = section/figure, pdf_page null. Figure 9 image checked visually from external/model_c/data/references/detector_fig9.jpg."),
]
out = []
for d in docs:
    tp = f"/home/efeai/Desktop/NasaSpaceApps/sources/text/{d['doc_id']}.txt"
    meta = dict(doc_id=d["doc_id"], title=d["title"], year=d["year"], authors=d["authors"], url=d["url"], retrieved_utc=None,
                sha256=sha(d["src"]), bytes=os.path.getsize(d["src"]),
                page_count=(pages(tp) if d["src"].endswith(".pdf") else None),
                identifiers=d["identifiers"], license_note=d["license_note"], accessible=True,
                access_note=SNAP + " " + d["extra"], local_path=d["src"], text_path=tp)
    json.dump(meta, open(f"{RAW}/{d['doc_id']}/meta.json", "w"), indent=1, ensure_ascii=False)
    out.append(meta)
json.dump(out, open("docs_meta.json", "w"), indent=1, ensure_ascii=False)
for m in out: print(m["doc_id"], m["page_count"], m["bytes"], m["sha256"][:16])
