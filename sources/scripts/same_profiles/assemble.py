"""Assemble sources/extracted/same_profiles.json from docs.json + items.json + search log."""
import json, re

ROOT = "/home/efeai/Desktop/NasaSpaceApps"
SP = "/tmp/claude-1000/-home-efeai-Desktop-NasaSpaceApps/6a4d6a96-8583-4b8d-bd50-35dfffa09cc3/scratchpad/same_profiles"
docs = json.load(open(f"{SP}/docs.json"))
items = json.load(open(f"{SP}/items.json"))

keep = ["doc_id", "title", "year", "authors", "url", "local_path", "text_path", "sha256", "page_count", "identifiers", "accessible", "access_note"]
documents = [{k: d.get(k) for k in keep} for d in docs]

# keyword page-hit search log over the two final reports
search_log = [
    {"query": "sha256 of 7 Model C raw files vs external/model_c/data/raw/source_manifest.json", "where": "local: external/model_c/data/raw", "hits": 7,
     "notes": "All 7 manifest entries MATCH (2 PDFs, 2 metadata JSONs, 2 CSVs, combined workbook xlsx 6d3a539c...)."},
]
kws = [("oxygen", r"oxygen"), ("O2", r"\bO2\b"), ("pressure", r"pressure"), ("kPa", r"kPa"), ("psi(g)", r"\bpsig?\b"), ("atmosphere", r"atmospher"),
       ("cabin", r"cabin"), ("lunar", r"lunar"), ("Mars", r"\bMars\b"), ("partial gravity", r"partial.gravity|partial-g"), ("dust", r"dust"), ("false alarm", r"false.{0,10}alarm"),
       ("nuisance", r"nuisance"), ("alarm", r"alarm"), ("DAFT", r"DAFT"), ("2.0 V / 2 V", r"\b2(\.0)? ?V\b"), ("saturat", r"saturat"), ("threshold", r"threshold"),
       ("ISS detector", r"ISS (smoke )?detector"), ("STS detector", r"STS (smoke )?[Dd]etector"), ("obscuration", r"obscuration")]
for doc in ["same_report", "samer_report"]:
    pages = open(f"{ROOT}/sources/text/{doc}.txt", encoding="utf-8").read().split("\f")
    for name, rx in kws:
        hp = [i + 1 for i, t in enumerate(pages) if re.search(rx, t)]
        search_log.append({"query": f"regex '{rx}' ({name})", "where": f"local full text sources/text/{doc}.txt (page-level)", "hits": len(hp),
                           "notes": f"PDF pages: {hp}" if hp else "no hits"})
search_log += [
    {"query": "STS/ISS detector use flags in SAME-R Appendix A", "where": "pdftotext -layout of samer PDF pp31-49", "hits": 17,
     "notes": "'Use STS Detector' = y for runs 67-72, 87-89, 91-92, 109-114; no ISS-detector flag row exists."},
    {"query": "CSV row integrity (SAME-R)", "where": "samer_csv vs samer_report Appendix A", "hits": 2,
     "notes": "Duplicate run 57 (Teflon row) and missing run 112 (Kapton) in CSV."},
    {"query": "per-material derived ISS>=2.0 V counts", "where": "external/model_c/reports/material_majority_oof.csv (pandas groupby campaign x material)", "hits": 84,
     "notes": "SAME Teflon 0/4, Kapton 4/4; SAME-R Teflon 4/11, Kapton 5/17; all other materials 100%."},
    {"query": "PSI metadata descriptive fields (objective, hypothesis, approach, hardware, dates, publications)", "where": "psi102/psi101 metadata JSON", "hits": 2,
     "notes": "PSI-102 approach/experimentHardware describe CSD rather than SAME."},
]

inaccessible = []  # nothing failed to load; unexamined items are listed under open_questions

open_questions = [
    "Test atmosphere (O2 vol% and pressure) of SAME and SAME-R runs is not stated in either final report or the PSI metadata; only 'air' flow inside the MSG and 'reaction with oxygen' are mentioned. Unexamined PSI files that might state it: PSI-102 'SAME_EIRD.pdf', 'SAME Verification Plan and Engineering Requirements Document (VPRED)_January 2007.pdf', 'SAME_Operations Manual_007.pdf', 'SAME_Baseline Concept Description Doc.pdf', PSI-101 'SAME EIRD Rev 2.00'. Not downloaded in this step.",
    "The 2.0 V ISS alarm reference is absent from both SAME/SAME-R final reports; Model C reads it graphically from Meyer et al. 2018 Fig. 9. Does Meyer 2018 (meyer2018 source group) state the voltage numerically and explain how it maps to the 1%/ft obscuration design alarm?",
    "SAME-R report has no ISS- or STS-detector results section; per-run detector outcomes exist only in the combined workbook (used by Model C) and in Meyer 2018. Are SAME-R ISS detector alarm/no-alarm outcomes documented anywhere as events (rather than derived from voltage)?",
    "SAME-R run count: abstract/PSI-101 metadata say 66 test points; p3 and Appendix A say 67 runs (48-114). The repository CSV has 67 primary rows but duplicates run 57 (Teflon) and omits run 112 (Kapton). Which is authoritative for Teflon/Kapton denominators?",
    "TEM sample count: SAME-R p3 says 70, Appendix F (excerpted paper) says 72.",
    "Zero-flow size effect: SAME-R p9/p83 say Dm is 30-40% larger; Appendix F conclusion (p84) says particles were 2-3 times larger. Which statistic does each refer to?",
    "Aged silicone Dm: SAME main text says >1 um, its own Table 1 says 606 nm, Appendix B says >500 nm. SAME text also calls 189 nm (the GMD) the silicone CMD.",
    "SAME count/size values drift between the 2008/2009 appended papers and the final Table 1 (e.g. Kapton CMD 114, 128, 105 nm); SAME-R Table 1 also differs from NTRS 20130000422 Table 1 as transcribed by Model C (Kapton CMD 0.062 vs 0.056 um). Which version is final for each campaign?",
    "SAME flight log has 24 non-DBP initial heatings (+1 Teflon reheat) but the combined workbook used by Model C has 17 SAME primary non-DBP runs. Which flight tests were excluded and why?",
    "SAME-R Appendix C (mass loss) marks all carousel 6 samples 'Carousel 6 Not Tested' while Appendix A lists runs 67-72 on carousel 6 sample IDs; the red-text/highlight conventions cannot be read from extracted text. Needs a visual check of PDF pp51-52.",
    "ISS detector sensitivity floor: SAME main report says down to 0.3 um; appended 2008 AIAA paper says down to 0.6 um (0.3 um 'minimum reported'). Model C notes cite 0.6 um calibration particles from Meyer 2018.",
    "P-Trak size range: 20 nm-1 um (main report, App. C/E) vs 20 nm-4/5 um (App. B) vs 20 nm-5 um (App. D).",
    "PSI-102 metadata 'approach' and 'experimentHardware' describe CSD hardware/procedure, not SAME; should be flagged to the dataset curators and not used as a SAME profile.",
    "No dust (lunar or cabin) challenge tests are described in SAME or SAME-R (within the examined text); the MPASS false-alarm-reduction claim is inferred from smoke-only correlations. Was MPASS ever tested against dust (e.g. in DAFT or later work)?",
    "No high-O2, reduced-pressure, or partial-gravity conditions appear in SAME or SAME-R (within the examined text); all flight runs were in microgravity on ISS, ground validation runs at 1 g.",
    "The SAME report says the P-Trak condenser modification was validated in 'a separate space experiment' (Urban et al. 2005); whether this is DAFT is not stated explicitly in the examined text.",
]

out = {"source_key": "same_profiles", "documents": documents, "items": items, "inaccessible": inaccessible,
       "search_log": search_log, "open_questions": open_questions}
json.dump(out, open(f"{ROOT}/sources/extracted/same_profiles.json", "w"), indent=1, ensure_ascii=False)
print("written", len(items), "items", len(search_log), "log entries")
