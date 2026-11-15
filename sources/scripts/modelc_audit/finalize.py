import json, hashlib, os, collections
d = json.load(open("items_draft.json"))
MC = "/home/efeai/Desktop/NasaSpaceApps/external/model_c"
img = f"{MC}/data/references/detector_fig9.jpg"
d["documents"].append(dict(doc_id="detector_fig9.jpg", title="Meyer et al. 2018 Figure 9 image (STS and ISS detector signal vs number concentration), copy in Model C snapshot", year=2018, authors=None,
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/", local_path=img, text_path=None, sha256=hashlib.sha256(open(img,"rb").read()).hexdigest(), page_count=None,
    identifiers=dict(doi="10.1016/j.firesaf.2018.04.004", ntrs=None, psi=None, pmc="PMC7918997"), accessible=True,
    access_note="Image inspected visually by this agent (dashed 'Detector alarm boundary' on the ISS panel at the 2.0 V gridline; STS panel boundary slightly above 0.4 V). Graph reading, not a printed number."))
for it in d["items"]:
    it.pop("_xlsx", None)
out = {
 "source_key": "modelc_audit",
 "documents": d["documents"],
 "items": d["items"],
 "inaccessible": [
  {"what": "notebooks/model_c.ipynb and notebooks/model_c_output.ipynb (listed in release_checksums.json)", "why": "Intentionally not downloaded in the local Model C snapshot; counted as 'not downloaded', not as checksum mismatch."},
  {"what": "Meyer et al. 2018 PDF via PMC (external/model_c/data/references/Meyer2018.blocked.html)", "why": "The saved file is an NCBI 'Preparing to download' proof-of-work page, not the paper; the PMC HTML author manuscript (PMC7918997.html) was used instead. Figure 9 numeric boundary only available as a graph image."},
  {"what": "PSI-101/PSI-102 raw instrument time series, logs and videos (GB-scale PSI inventories)", "why": "Not in the Model C snapshot and not downloaded (disk limit); per-row ISS saturation, LOD and the relation between the recorded scatter voltage and the flight detector's alarm logic cannot be reconstructed from the reduced workbook."}
 ],
 "search_log": [
  {"query": "sha256 of every key in release_checksums.json, artifacts/model_c/checksums.json, data/raw/source_manifest.json, STATUS.json followup.protected_artifact_sha256", "where": "external/model_c (python -I hashlib)", "hits": 107, "notes": "87+6+7+7 pass, 0 mismatch, 2 notebooks not downloaded."},
  {"query": "Combined Rslts Copy this sheet: campaign 1/2, five materials, numeric SAME #, AW >= 2.0", "where": "PSI-101 workbook via openpyxl 3.1.5 (installed into project venv)", "hits": 134, "notes": "134 flight material records, 84 primary, 50 secondary; per-material counts equal Model C."},
  {"query": "random.Random(20261115).sample(records, 12) vs dashboard_table.csv", "where": "PSI-101 workbook + dashboard_table.csv", "hits": 12, "notes": "12/12 match; full 134/134 comparison also matches."},
  {"query": "formula trace of 'ICES 2012 Paper data table' and 'AIAA 2012 Paper data table' sheets to '<Material> R&T plots' rows", "where": "PSI-101 workbook (formula mode)", "hits": 15, "notes": "Unaged rows are column-wise AVERAGE formulas over several runs; aged 720 s rows are single secondary records (Silicone: 2). AIAA sheet values are hard-coded."},
  {"query": "regex (\\b2(\\.0)?\\s?V\\b|2 volt|alarm (level|threshold|point)|threshold)", "where": "sources/text/modelc-psi102-same-final-report.txt and modelc-psi101-samer-final-report.txt (pdftotext, all pages)", "hits": 7, "notes": "No ISS 2.0 V threshold found; hits were 2 mg/m3 detector-requirement figures, 'alarm point ... 0.5 mg/m3', particle-count and image thresholds."},
  {"query": "regex (alarm|volts?|saturat)", "where": "same two report texts", "hits": 86, "notes": "ISS design alarm 1% obscuration/ft (SAME p12, p36); no voltage alarm level."},
  {"query": "2 V / Fig 9 / alarm / threshold / saturat", "where": "sources/text/modelc-pmc7918997.txt (HTML->text)", "hits": 6, "notes": "Section 3.2 + Figure 9 caption: 'voltage threshold boundaries', 'alarm boundary ... dashed red line'; value read visually from detector_fig9.jpg."},
  {"query": "saturat|ISS detector|volt|alarm|100,000|0.001", "where": "sources/text/modelc-ntrs20120012884.txt", "hits": 17, "notes": "P-Trak/DustTrak ranges on p4; no ISS-signal saturation statement."},
  {"query": "Teflon / 0.081 / 2.198 / Table 1", "where": "external/model_c/data/references/20130000422.txt (layout) and sources/text/modelc-ntrs20130000422.txt", "hits": 1, "notes": "Unaged Teflon row at layout line 491, PDF page 7."}
 ],
 "open_questions": [
  "Why did Kapton reach >= 2 V in all 4 SAME primary runs but only 5 of 17 SAME-R runs, including at nominally identical baseline settings (SAME 29: 3.66 V vs SAME-R 51/61/73/92: 0.42-0.75 V)? What does 'Baseline new formula' (SAME-R run 51) refer to?",
  "Is the 2.0 V dashed boundary in Meyer et al. 2018 Figure 9 the ISS detector's operational alarm setting, and how does it relate to the 1%/ft obscuration design criterion (SAME report p12) and the ~0.5 mg/m3 alarm point (SAME report Appendix E, p65)? Not stated within the examined sources.",
  "Which tests/points underlie Meyer's 'over half of the Kapton' and '2/3 of the Teflon' ISS non-alarm fractions (campaign, primary vs secondary, P-Trak availability)? Model C counts are near but not identical.",
  "Which version of the baseline particle-size table is authoritative for Teflon (NTRS 20130000422: 0.081/0.101/0.170/2.198 vs SAME-R report: 0.093/0.111/0.173/2.081), and was column-wise averaging of Dg and sigma_g intended?",
  "SAME-R report says 66 test points (abstract) and 67 runs (Flight Operation); the workbook has 67 primary runs - which run is the 67th in the abstract's accounting?",
  "Exact numeric STS alarm boundary in Figure 9(a) (visually slightly above 0.4 V) and the Shuttle-channel baseline/offset convention needed to label STS data.",
  "Identity of sample in SAME-R secondary record 51a (K02 vs parent K01) - affects whether Kapton has 19 or 20 groups.",
  "Per-row ISS saturation level and detection limit of the reduced scatter channel (would need raw PSI time series)."
 ]
}
cats = collections.Counter(i["category"] for i in out["items"])
json.dump(out, open("/home/efeai/Desktop/NasaSpaceApps/sources/extracted/modelc_audit.json", "w"), indent=1, ensure_ascii=False)
print(len(out["items"]), dict(cats))
