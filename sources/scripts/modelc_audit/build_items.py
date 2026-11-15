import json, hashlib, os
MC = "/home/efeai/Desktop/NasaSpaceApps/external/model_c"
SK = "modelc_audit"
def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
ck = json.load(open("checksums_result.json"))
wbc = json.load(open("wb_check_result.json"))
tr = json.load(open("teflon_recompute.json"))
docs_meta = json.load(open("docs_meta.json"))

# ---------- documents ----------
documents = []
for m in docs_meta:
    documents.append(dict(doc_id=m["doc_id"], title=m["title"], year=m["year"], authors=m["authors"], url=m["url"],
        local_path=m["local_path"], text_path=m["text_path"], sha256=m["sha256"], page_count=m["page_count"],
        identifiers=m["identifiers"], accessible=True, access_note=m["access_note"]))
HF = "https://huggingface.co/efe-T/nasa-same-model-c/blob/91292a40886564d146dc9e9d496b74c2aefaab5c/"
mcfiles = {
 "release_checksums.json": ("release_checksums.json", "Model C release checksum manifest"),
 "checksums.json": ("artifacts/model_c/checksums.json", "Model C exported-artifact checksums"),
 "source_manifest.json": ("data/raw/source_manifest.json", "Model C PSI source manifest"),
 "STATUS.json": ("STATUS.json", "Model C deliverable status"),
 "data_dictionary.json": ("data/processed/data_dictionary.json", "Model C data dictionary (processed; byte-identical to artifacts copy)"),
 "dashboard_measured_only.csv": ("data/processed/dashboard_measured_only.csv", "Model C measured-only per-material dashboard"),
 "dashboard_table.csv": ("data/processed/dashboard_table.csv", "Model C per-record dashboard table (134 flight material records)"),
 "evaluation.md": ("reports/evaluation.md", "Model C evaluation report"),
 "evaluation_followup.md": ("reports/evaluation_followup.md", "Model C follow-up evaluation report"),
 "metrics.json": ("reports/metrics.json", "Model C metrics"),
 "followup_metrics.json": ("reports/followup_metrics.json", "Model C follow-up metrics"),
 "external_checks.csv": ("reports/external_checks.csv", "Model C Table 1 lognormal external checks"),
 "teflon_table1_check.json": ("data/references/teflon_table1_check.json", "Model C unaged-Teflon Table 1 check"),
 "MODEL_CARD.md": ("MODEL_CARD.md", "Model C model card"),
 "domain.json": ("artifacts/model_c/domain.json", "Model C applicability domain / OOD definition"),
 "ood_example.json": ("reports/ood_example.json", "Model C OOD inference example"),
 "data.py": ("model_c/data.py", "Model C preprocessing code"),
 "train.py": ("model_c/train.py", "Model C training / scientific-check code"),
 "PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx": ("data/raw/PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx", "PSI-101 analyzed data workbook, SAME and SAME-R results (author-combined)"),
}
for did, (rel, title) in mcfiles.items():
    p = f"{MC}/{rel}"
    documents.append(dict(doc_id=did, title=title, year=None, authors=None,
        url=("https://psi.nasa.gov/geode-py/ws/studies/PSI-101/download?file=PSI-101_Analyzed%20Data_SAME%2C%20SAME-R_Results.xlsx&version=4&redirect=false" if did.endswith(".xlsx") else HF + rel),
        local_path=p, text_path=(None if did.endswith(".xlsx") else p), sha256=sha(p), page_count=None,
        identifiers=dict(doi=None, ntrs=None, psi=("PSI-101" if did.endswith(".xlsx") else None), pmc=None), accessible=True,
        access_note=("Read with openpyxl 3.1.5 (data_only and formula modes); location = sheet!cell." if did.endswith(".xlsx") else "File in read-only Model C snapshot; location = path + line/row/key; pdf_page null.")))

def C(**kw):
    base = dict(atmosphere_o2_vol_pct=None, pressure_kpa=None, airflow_cm_s=None, gravity=None, heating_s=None, aging_s=None)
    base.update(kw); return base
FLIGHT = "low gravity, ISS Microgravity Science Glovebox (flight)"
def N(value, unit, meaning, verbatim): return dict(value=value, unit=unit, meaning=meaning, verbatim=verbatim)
items = []
def add(**kw):
    kw.setdefault("printed_page", None); kw.setdefault("pdf_page", None); kw.setdefault("materials", []); kw.setdefault("detector", None)
    kw.setdefault("numbers", []); kw.setdefault("conditions", C()); kw.setdefault("n_independent_tests", None); kw.setdefault("investigation", None)
    kw["item_id"] = f"{SK}-{len(items)+1:02d}"
    order = ["item_id","doc_id","pdf_page","printed_page","location","anchor_quote","summary","category","investigation","materials","detector","numbers","conditions","n_independent_tests","scope_notes"]
    v = kw.pop("_xlsx", None)
    rec = {k: kw[k] for k in order}
    if v: rec["_xlsx"] = v
    items.append(rec)
ISS = "ISS Detector Scatter (volts)"
BOTH = "SAME;SAME-R"
MATS5 = ["Kapton", "Lampwick", "Pyrell", "Silicone", "Teflon"]
# ================= CHECKSUMS =================
rc = ck["release_checksums"]
add(doc_id="release_checksums.json", location="external/model_c/release_checksums.json (all 89 path keys)", anchor_quote="notebooks/model_c_output.ipynb",
    summary=f"Independent sha256 recomputation (python -I hashlib) of every entry in release_checksums.json: {len(rc['pass'])} files match, {len(rc['fail'])} mismatch, {len(rc['missing'])} not downloaded (notebooks/model_c.ipynb and notebooks/model_c_output.ipynb were intentionally not part of the local snapshot). Only .gitattributes and release_checksums.json itself are on disk without an entry.",
    category="checksum", numbers=[N(89,"files","entries in release_checksums.json","89"), N(87,"files","sha256 match","87"), N(0,"files","sha256 mismatch","0"), N(2,"files","not downloaded (notebooks)","2")],
    scope_notes="Verifies integrity of the local snapshot against the release manifest only; does not prove the manifest itself matches the Hugging Face commit.")
add(doc_id="checksums.json", location="external/model_c/artifacts/model_c/checksums.json (6 keys)", anchor_quote="1d0a63fe5f51b89df6710e5d2c49632964af7457d67204337dbc3e4eb02f6e01",
    summary="All 6 exported-artifact hashes in artifacts/model_c/checksums.json (domain.json, harmonization.json, inference.py, data_dictionary.json, model.joblib, requirements.txt) match the files on disk; 0 mismatches.",
    category="checksum", numbers=[N(6,"files","artifact hashes matching","6"), N(0,"files","mismatch","0")],
    scope_notes="Integrity only; says nothing about model validity.")
add(doc_id="source_manifest.json", location="external/model_c/data/raw/source_manifest.json (7 entries, keys sha256 and bytes)", anchor_quote="6d3a539ccf425b1fa8edc19cc75d828f57d650c7ce734d4e7aa686fea9593218",
    summary="All 7 PSI source files listed in source_manifest.json (PSI-101/PSI-102 metadata JSON, the combined analyzed workbook, the two experimental-table CSVs and the two final-report PDFs) match their recorded sha256; the 5 entries that record byte sizes also match exactly (e.g. workbook 4,061,669 bytes).",
    category="checksum", investigation=BOTH, numbers=[N(7,"files","source sha256 match","7"), N(4061669,"bytes","PSI-101 analyzed workbook size","4061669")],
    scope_notes="Confirms the local copies equal what Model C pinned; PSI upstream versions could have changed since (study version 4).")
add(doc_id="STATUS.json", location="external/model_c/STATUS.json -> followup.protected_artifact_sha256 (7 keys)", anchor_quote="protected_artifact_sha256",
    summary="The 7 protected deployed-artifact hashes recorded in STATUS.json for the follow-up evaluation all match the files on disk, consistent with STATUS.json's claim that weights were not changed by the follow-up.",
    category="checksum", numbers=[N(7,"files","protected artifact hashes matching","7")],
    scope_notes="Integrity of the snapshot; the audit did not retrain or modify anything.")
# ================= DEFINITIONS =================
add(doc_id="data_dictionary.json", location="external/model_c/data/processed/data_dictionary.json, entry name=alarm_level_reached (keys rule, source, assumptions); same rule string per row in dashboard_table.csv column label_rule", anchor_quote="iss_scatter_v >= 2.0",
    summary="Model C's binary label alarm_level_reached is derived (provenance 'derived'), not source-reported: it is 1 when the source-reported ISS scatter voltage (workbook column AW 'ISS Detector Scatter (volts)') is at least 2.0 V. The cited source is Meyer et al. 2018 Figure 9; the dictionary states the summary signal crossing the threshold represents a recorded level, not time-to-alarm.",
    category="definition", investigation=BOTH, detector="ISS smoke detector (scatter channel, 'ISS Detector Scatter (volts)')",
    numbers=[N(2.0,"V","label threshold on ISS scatter voltage","2.0")],
    scope_notes="Applies to every Model C label. Not an observed alarm event, not alarm timing, not an operational alarm setting; see the 2.0 V origin items for where the level comes from.")
add(doc_id="data.py", location="external/model_c/model_c/data.py lines 100-155 (campaign map, material filter, exclusion reasons, training_eligible)", anchor_quote='reasons.append("secondary_aging_reading")',
    summary="Primary run (Model C 'training_eligible') = a flight record from campaign code 1 (SAME) or 2 (SAME-R) of the combined worksheet, material in {Kapton, Lampwick, Pyrell, Silicone, Teflon} (DBP and ground tests excluded), whose SAME # has no secondary suffix 'a', with all five controls present, heating duration > 0, a non-negative ISS signal and no 'y/yes' fan-problem or flat-profile flag. Result: 84 primary runs out of 134 flight material records.",
    category="definition", investigation=BOTH, materials=MATS5, numbers=[N(84,"runs","primary runs","84"), N(134,"records","flight material records in combined sheet","134")],
    scope_notes="Definition is Model C's processing choice; reproduced independently from the workbook in the external_check items (same 84 runs).")
add(doc_id="dashboard_measured_only.csv", location="external/model_c/data/processed/dashboard_measured_only.csv, column scope (all 5 rows)", anchor_quote="Observed primary runs only; secondary aging and DBP excluded",
    summary="The measured-only dashboard restricts counts to observed primary heating runs, excludes secondary-aging readings and the DBP calibration material, does not weight by sample, and describes itself as descriptive rather than a detection probability.",
    category="definition", investigation=BOTH, materials=MATS5,
    scope_notes="Applies to all per-material n_runs / n_reaching_2v figures in this extraction.")
add(doc_id="modelc-psi101-samer-final-report", pdf_page=3, printed_page=None, location="Flight Operation section", anchor_quote="secondary aging runs are listed as separate entities, making the total run number to 109",
    summary="Secondary-aging records: the SAME-R report lists secondary-aging readings (further aging of an already generated smoke batch) as separate entries in its Appendix A, which raises the entry count to 109 although 67 heating runs were conducted. In the combined workbook these carry an 'a' suffix on the SAME # (e.g. 58a); 50 of the 134 flight material records are such readings (8 SAME, 42 SAME-R).",
    category="definition", investigation="SAME-R", numbers=[N(109,"entries","SAME-R entries incl. secondary aging","109"), N(67,"runs","SAME-R heating runs","67"), N(50,"records","secondary 'a' records in combined sheet (both campaigns)","50")],
    scope_notes="Secondary readings share the heating event with their parent run and are not independent tests; Model C excludes them from counts and training.")
add(doc_id="dashboard_table.csv", location="external/model_c/data/processed/dashboard_table.csv rows test_id=SAME-R:90 and SAME-R:57 (column description); workbook 'Combined Rslts Copy this sheet' rows 121 and 60", anchor_quote="Mid Temp aging reburn 85",
    summary="Reburn runs: SAME-R run 90 (Kapton sample K08, described as a reburn of run 85) and SAME-R run 57 (Lampwick sample L14, 'High RT/R0 reburn sample', reusing the sample of run 54) are primary heating runs on previously heated samples. Model C counts them as runs but assigns them to the same group as the earlier run, so Kapton has 21 runs in 19 groups and Lampwick 17 runs in 16 groups.",
    category="definition", investigation="SAME-R", materials=["Kapton", "Lampwick"],
    numbers=[N(0.18647765,"V","ISS scatter, Kapton reburn run SAME-R:90","0.18647765"), N(0.9827577999999999,"V","ISS scatter, parent run SAME-R:85","0.9827577999999999"), N(5.6770475,"V","ISS scatter, Lampwick reburn SAME-R:57","5.6770475")],
    scope_notes="SAME-R report p3 states 67 runs including two using reused samples; reburns must not be counted as independent tests.")
add(doc_id="evaluation.md", location="external/model_c/reports/evaluation.md line 5 and Limits paragraph (line 69)", anchor_quote="84 primary rows; 81 conservative validation groups.",
    summary="Grouping: Model C links records that share a numeric run or a sample ID into connected components. The 84 primary runs come from 82 physical primary samples, which collapse to 81 groups because the ambiguous secondary record 51a (listing sample K02 while its parent 51 lists K01, and K02 is also used in run 61) is conservatively linked.",
    category="definition", investigation=BOTH, numbers=[N(84,"runs","primary runs","84"), N(81,"groups","conservative validation groups","81"), N(82,"samples","physical primary samples","82")],
    n_independent_tests=81, scope_notes="Use group counts, not run counts, as the closest proxy for independent tests; even groups share campaign hardware and smoke-generation settings.")
add(doc_id="dashboard_measured_only.csv", location="external/model_c/data/processed/dashboard_measured_only.csv, column rule (all rows)", anchor_quote="count(primary ISS scatter>=2V)/count(primary runs)",
    summary="fraction_reaching_2v is defined as the number of primary runs with ISS scatter at or above 2 V divided by the number of primary runs for that material; it is unweighted, counts reburn runs as runs, and is labelled value_kind 'derived'.",
    category="definition", investigation=BOTH, materials=MATS5,
    scope_notes="A descriptive fraction of the tested matrix, not a probability of detection for any new fire.")
# ================= MEASURED (per material) =================
def matrow(mat, anchor, n_runs, n_groups, n2, frac, camps, ids, vmin, vmax, af, rr, ht, ag, mx, extra=""):
    add(doc_id="dashboard_measured_only.csv", location=f"external/model_c/data/processed/dashboard_measured_only.csv row material={mat}", anchor_quote=anchor,
        summary=f"{mat}: {n_runs} primary runs in {n_groups} groups, {n2} reached ISS scatter >= 2 V (fraction {frac:.3f}); campaigns {camps}; ISS scatter range {vmin}-{vmax} V; controls airflow {af[0]}-{af[1]} cm/s, Rt/R0 {rr[0]}-{rr[1]}, heating {ht[0]}-{ht[1]} s, primary aging {ag[0]}-{ag[1]} s, mixing {mx[0]}-{mx[1]} s. Test IDs: {ids}.{extra}",
        category="modelc_measured", investigation=camps.replace(" ", ""), materials=[mat], detector="ISS smoke detector (scatter channel, 'ISS Detector Scatter (volts)')",
        numbers=[N(n_runs,"runs","primary runs","%d"%n_runs), N(n_groups,"groups","conservative groups","%d"%n_groups), N(n2,"runs","primary runs with ISS scatter >= 2 V","%d"%n2), N(frac,"1","fraction reaching 2 V (derived)",anchor if anchor.startswith("0.") else repr(frac)),
                 N(vmin,"V","min ISS scatter",str(vmin)), N(vmax,"V","max ISS scatter",str(vmax)), N(af[0],"cm/s","airflow min",str(af[0])), N(af[1],"cm/s","airflow max",str(af[1])), N(rr[0],"1","Rt/R0 min",str(rr[0])), N(rr[1],"1","Rt/R0 max",str(rr[1])), N(ht[0],"s","heating min",str(ht[0])), N(ht[1],"s","heating max",str(ht[1])), N(ag[0],"s","primary aging min",str(ag[0])), N(ag[1],"s","primary aging max",str(ag[1]))],
        conditions=C(gravity=FLIGHT), n_independent_tests=n_groups,
        scope_notes="value_kind derived from measured ISS scatter; descriptive of the SAME/SAME-R test matrix only; reaching 2 V is a recorded signal level, not a reported alarm; ranges are min/max over primary runs, not a full factorial design.")
matrow("Kapton", "0.42857142857142855", 21, 19, 9, 9/21, "SAME;SAME-R", "SAME:29,30,33,47; SAME-R:51,61,62,70,73,75,77,85,90,92,93,94,101,102,108,112,114", 0.18647765, 6.242, (0.0, 8.1), (1.38, 1.48), (20.0, 120.0), (11.0, 720.0), (8.0, 8.0))
matrow("Teflon", "0.26666666666666666", 15, 15, 4, 4/15, "SAME;SAME-R", "SAME:25,26,28,41; SAME-R:50,56,58,69,79,81,83,89,100,105,111", 0.0006866452, 5.041518999999999, (0.0, 8.1), (1.44, 1.4524143054229013), (60.0, 60.0), (11.0, 720.0), (8.0, 8.0))
matrow("Lampwick", "5.6770475", 17, 16, 17, 1.0, "SAME;SAME-R", "SAME:31,32,34,46; SAME-R:49,54,55,57,68,78,80,82,88,96,98,106,110", 5.6770475, 6.279388000000001, (0.0, 8.1), (1.245, 1.32), (20.0, 60.0), (11.0, 720.0), (8.0, 8.0))
matrow("Pyrell", "4.819808999999999", 12, 12, 12, 1.0, "SAME-R", "SAME-R:52,63,64,71,74,76,84,87,95,97,107,113", 4.819808999999999, 6.283677000000002, (0.0, 8.1), (1.22, 1.23), (60.0, 60.0), (11.0, 720.0), (8.0, 8.0), extra=" Pyrell was tested only in SAME-R.")
matrow("Silicone", "6.2120555555555566", 19, 19, 19, 1.0, "SAME;SAME-R", "SAME:5,23,24,27,35; SAME-R:48,53,59,60,65,66,67,72,86,91,99,103,104,109", 6.2120555555555566, 6.2939, (0.0, 8.1), (1.304, 1.38), (10.0, 60.0), (1.0, 720.0), (0.0, 8.0))
add(doc_id="metrics.json", location='external/model_c/reports/metrics.json keys campaign_counts and class_balance', anchor_quote='"SAME-R": 67',
    summary="Across all five materials Model C has 84 primary runs (17 SAME, 67 SAME-R); 61 reached ISS scatter >= 2 V and 23 did not. All 23 below-2 V primary runs are Kapton (12) or Teflon (11); every Lampwick, Pyrell and Silicone primary run reached 2 V.",
    category="modelc_measured", investigation=BOTH, materials=MATS5, detector="ISS smoke detector (scatter channel)",
    numbers=[N(17,"runs","SAME primary runs","17"), N(67,"runs","SAME-R primary runs","67"), N(61,"runs","primary runs >= 2 V","61"), N(23,"runs","primary runs < 2 V","23")],
    conditions=C(gravity=FLIGHT), n_independent_tests=81, scope_notes="Counts of primary runs (81 groups). The below-2 V set being only Kapton/Teflon is a property of this test matrix, not a general claim about all materials.")
add(doc_id="dashboard_table.csv", location="external/model_c/data/processed/dashboard_table.csv, training_eligible rows with material=Kapton, grouped by campaign (row SAME-R:51 shown as anchor)", anchor_quote="Baseline new formula",
    summary="Kapton differs sharply by campaign: all 4 SAME primary runs reached >= 2 V (3.66-5.64 V, airflow 2-8 cm/s), but only 5 of 17 SAME-R primary runs (15 groups) did. At nominally similar baseline settings (Rt/R0 1.38, 60 s heating, 11 s aging, 8.0-8.1 cm/s) SAME run 29 read 3.66 V while SAME-R runs 51, 61, 73 and 92 read 0.42-0.75 V.",
    category="modelc_measured", investigation=BOTH, materials=["Kapton"], detector="ISS smoke detector (scatter channel)",
    numbers=[N(4,"runs","SAME Kapton primary runs >= 2 V (of 4)","4"), N(5,"runs","SAME-R Kapton primary runs >= 2 V (of 17)","5"), N(3.663712,"V","SAME:29 baseline ISS scatter","3.6637120000000003"), N(0.417557,"V","SAME-R:51 baseline ISS scatter","0.4175567")],
    conditions=C(gravity=FLIGHT, heating_s=60.0, aging_s=11.0), n_independent_tests=19,
    scope_notes="Descriptive only. Campaign is confounded with hardware state, sample batch and test sequence; SAME-R run 51 is described as 'Baseline new formula', whose meaning is not documented within the examined files. Not a causal effect of campaign.")
add(doc_id="dashboard_table.csv", location="external/model_c/data/processed/dashboard_table.csv, training_eligible Teflon rows (columns resistance_ratio, airflow_cm_s, iss_scatter_v)", anchor_quote="Baseline aging",
    summary="Teflon at the baseline heating setpoint (Rt/R0 1.44-1.445; SAME 25, 26, 28, 41 and SAME-R 56, 58, 79, 89; airflow 2-8.1 cm/s) never reached 2 V (0 of 8 runs; maximum 1.64 V). The four Teflon runs that reached 2 V (SAME-R 50, 69, 81, 111) all used Rt/R0 1.45-1.4524. Across all SAME-R runs at Rt/R0 1.448-1.4524, 4 of 7 reached 2 V; the two no-flow runs (100, 105; Rt/R0 1.45) and the mid-temperature run 83 (Rt/R0 1.448) stayed below.",
    category="test_condition", investigation=BOTH, materials=["Teflon"], detector="ISS smoke detector (scatter channel)",
    numbers=[N(0,"runs","Teflon runs >= 2 V at Rt/R0 <= 1.445 (of 8)","0"), N(4,"runs","Teflon runs >= 2 V at Rt/R0 >= 1.448 (of 7)","4"), N(1.6403656500000001,"V","max ISS scatter at baseline setpoint (SAME:25, 4 cm/s)","1.6403656500000001")],
    conditions=C(gravity=FLIGHT, heating_s=60.0), n_independent_tests=15,
    scope_notes="Descriptive subset counts (8 and 7 groups). Higher setpoints occur only in SAME-R; Rt/R0 is not a unique sample temperature (SAME-R report p2). No causal or threshold claim about temperature.")
add(doc_id="dashboard_table.csv", location="external/model_c/data/processed/dashboard_table.csv, training_eligible Kapton rows (columns airflow_cm_s, campaign, iss_scatter_v)", anchor_quote="No flow run w/ aging",
    summary="Kapton by airflow: at <= 2 cm/s (including no flow) 5 of 6 primary runs reached 2 V (SAME 33; SAME-R 101, 102, 108, 112; the exception is SAME-R 114 at 0.77 V); at 8.1 cm/s in SAME-R only 1 of 12 runs (10 groups) reached 2 V (run 62, 6.24 V); both SAME runs at 8.0 cm/s reached 2 V.",
    category="test_condition", investigation=BOTH, materials=["Kapton"], detector="ISS smoke detector (scatter channel)",
    numbers=[N(5,"runs","Kapton runs >= 2 V at airflow <= 2 cm/s (of 6)","5"), N(1,"runs","SAME-R Kapton runs >= 2 V at 8.1 cm/s (of 12)","1"), N(0.7652435499999999,"V","SAME-R:114 (2 cm/s) ISS scatter","0.7652435499999999")],
    conditions=C(gravity=FLIGHT), n_independent_tests=19,
    scope_notes="Descriptive; airflow is confounded with campaign (all 8.1 cm/s runs are SAME-R). Consistent in direction with the SAME-R report's statement that particles were larger at low flow (p5), but no causal claim.")
add(doc_id="dashboard_table.csv", location="external/model_c/data/processed/dashboard_table.csv, training_eligible rows with airflow_cm_s=0.0", anchor_quote="No flow run w/ aging",
    summary="No-airflow heating (SAME-R only): Teflon 0 of 2 runs reached 2 V (100: 0.95 V, 105: 0.73 V), whereas Kapton 2 of 2, Lampwick 3 of 3, Pyrell 2 of 2 and Silicone 2 of 2 did.",
    category="test_condition", investigation="SAME-R", materials=MATS5, detector="ISS smoke detector (scatter channel)",
    numbers=[N(0.0,"cm/s","airflow during heating","0.0"), N(0.9495089499999999,"V","Teflon SAME-R:100 ISS scatter","0.9495089499999999"), N(0.7279054500000001,"V","Teflon SAME-R:105 ISS scatter","0.7279054500000001")],
    conditions=C(gravity=FLIGHT, airflow_cm_s=0.0, heating_s=60.0, aging_s=11.0), n_independent_tests=11,
    scope_notes="Two Teflon runs only; descriptive.")
add(doc_id="dashboard_table.csv", location="external/model_c/data/processed/dashboard_table.csv, training_eligible rows (columns aging_s, heating_s, mixing_s)", anchor_quote="High temp aged STS det",
    summary="Coverage gaps in the primary test matrix: each material has only one primary run with 720 s primary aging (Silicone two) - Kapton run 70 stayed below 2 V (0.90 V) while Teflon run 69 reached 5.04 V; all Teflon and Pyrell runs used 60 s heating; all runs except one Silicone run used 8 s mixing; Pyrell exists only in SAME-R.",
    category="test_condition", investigation=BOTH, materials=MATS5,
    numbers=[N(720.0,"s","long primary aging setting","720.0"), N(0.8977507499999998,"V","Kapton SAME-R:70 (720 s aging) ISS scatter","0.8977507499999998"), N(5.041518999999999,"V","Teflon SAME-R:69 (720 s aging) ISS scatter","5.041518999999999")],
    conditions=C(gravity=FLIGHT), scope_notes="Single-run cells cannot support conclusions about aging effects; listed so Agent 5 does not over-read sparse cells.")
add(doc_id="dashboard_table.csv", location="external/model_c/data/processed/dashboard_table.csv row test_id=SAME:41 (iss_scatter_v); data_dictionary.json iss_scatter_v.instrument_limits", anchor_quote="0.0006866452",
    summary="The lowest primary ISS scatter value is Teflon SAME run 41 ('low flow aging', 2 cm/s): 0.0006866452 V. Model C's data dictionary states that per-row detection limit and saturation cannot be reconstructed from the summary, so near-zero readings are kept as reported numbers and only used for the 2 V threshold.",
    category="measurement_limitation", investigation="SAME", materials=["Teflon"], detector="ISS smoke detector (scatter channel)",
    numbers=[N(0.0006866452,"V","ISS scatter SAME:41","0.0006866452")], conditions=C(gravity=FLIGHT, airflow_cm_s=2.0, heating_s=60.0, aging_s=11.0), n_independent_tests=1,
    scope_notes="Do not interpret as 'no smoke'; LOD/zero offset of the reduced channel is undocumented within the examined files.")
add(doc_id="data_dictionary.json", location="external/model_c/data/processed/data_dictionary.json entry iss_scatter_v (keys limitations, instrument_limits)", anchor_quote="High-end saturation not numerically de-censored",
    summary="ISS scatter values of Lampwick, Pyrell and Silicone cluster near 6.2-6.29 V; Model C treats the high end as possibly saturated, does not de-censor it, has no calibrated LOD, and therefore uses the channel only for the >= 2 V threshold, not as an analog response.",
    category="measurement_limitation", investigation=BOTH, materials=["Lampwick", "Pyrell", "Silicone"], detector="ISS smoke detector (scatter channel)",
    numbers=[N(6.2939,"V","max Silicone primary ISS scatter","6.2939")], conditions=C(gravity=FLIGHT),
    scope_notes="Saturation for the ISS detector is stated in Meyer et al. 2018 section 3.2; exact per-row saturation cut-off not established in examined files.")
# ================= EXTERNAL CHECKS (workbook) =================
s = wbc["workbook_primary_summary"]
add(doc_id="PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx", location="sheet 'Combined Rslts Copy this sheet', header row 2 (A, C, G, AW), records rows 3-167", anchor_quote=ISS,
    _xlsx=("Combined Rslts Copy this sheet", "AW2", False),
    summary=f"Independent recomputation directly from the PSI workbook (openpyxl, columns located by header text, no Model C code): campaign code 1/2, material in the five tested materials, SAME # purely numeric = primary. Kapton {s['Kapton']['n_primary']} primary runs (SAME {s['Kapton']['by_campaign']['SAME']}, SAME-R {s['Kapton']['by_campaign']['SAME-R']}) with {s['Kapton']['n_ge_2v']} at >= 2.0 V; Teflon {s['Teflon']['n_primary']} (SAME {s['Teflon']['by_campaign']['SAME']}, SAME-R {s['Teflon']['by_campaign']['SAME-R']}) with {s['Teflon']['n_ge_2v']}; Lampwick 17/17, Pyrell 12/12, Silicone 19/19; total {wbc['n_primary_total']} primary and {wbc['n_secondary_total']} secondary records. All per-material counts and test-ID lists match dashboard_measured_only.csv.",
    category="external_check", investigation=BOTH, materials=MATS5, detector="ISS smoke detector (scatter channel)",
    numbers=[N(21,"runs","Kapton primary (workbook)","21"), N(9,"runs","Kapton >= 2.0 V (workbook)","9"), N(15,"runs","Teflon primary (workbook)","15"), N(4,"runs","Teflon >= 2.0 V (workbook)","4"), N(84,"runs","all primary (workbook)","84")],
    conditions=C(gravity=FLIGHT), scope_notes="PASS. Same primary definition as Model C (suffix-free SAME #); a different definition (e.g. including 51a, which has a positive heating duration) would change Kapton to 22 records.")
fr = wbc["full_row_comparison"]
add(doc_id="dashboard_table.csv", location="external/model_c/data/processed/dashboard_table.csv all 134 rows (columns test_id, material, iss_scatter_v, source_row, alarm_level_reached, training_eligible)", anchor_quote="ISS scatter >=2.0 V; Meyer et al. 2018 Figure 9",
    summary=f"Full-table comparison of dashboard_table.csv against the workbook: {fr['match']} of 134 rows match on test ID, material, ISS scatter voltage (exact float) and source row; 0 mismatches, 0 missing, 0 extra. Recomputing the label (ISS >= 2.0 V) for all 134 rows gives 0 disagreements, and Model C's training_eligible set equals the independently derived primary set (84 = 84).",
    category="external_check", investigation=BOTH, materials=MATS5,
    numbers=[N(134,"rows","rows matching workbook","134"), N(0,"rows","label disagreements","0")], scope_notes="PASS; checks transcription and labelling only, not the scientific validity of the 2 V proxy.")
spot = wbc["random_spot_check"]
add(doc_id="dashboard_table.csv", location="dashboard_table.csv rows " + ", ".join(x["test_id"] for x in spot) + " vs workbook 'Combined Rslts Copy this sheet' rows " + ", ".join(str(x["workbook_row"]) for x in spot), anchor_quote="SAME-R:81",
    summary="Random spot check (Python random seed 20261115, 12 rows drawn from the 134 workbook records, including primary and secondary rows): " + "; ".join(f"{x['test_id']} {x['workbook_material']} {x['workbook_iss_v']:.6g} V row {x['workbook_row']} label {x['recomputed_label']}" for x in spot) + ". All 12 match dashboard_table.csv on material, ISS scatter, source row and label.",
    category="external_check", investigation=BOTH, materials=MATS5,
    numbers=[N(12,"rows","randomly sampled rows checked","12"), N(12,"rows","rows matching","12")], scope_notes="PASS (12/12). Seed recorded for reproducibility; script kept in the agent scratchpad (wb_check.py).")
cs = wbc["campaign_sheet_crosscheck"]
add(doc_id="PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx", location="sheet 'Combined Rslts Copy this sheet' cell AW3 (formula) vs sheets 'SAME R Results' (columns F, B, AR) and 'SAME1 Flight Tests 8-27-09' (columns E, B, Z)", anchor_quote="='SAME1 Flight Tests 8-27-09'!Z7",
    _xlsx=("Combined Rslts Copy this sheet", "AW3", True),
    summary=f"The combined sheet's ISS scatter cells are formulas pointing to the per-campaign sheets. Cached values agree with 'SAME R Results' column AR for {cs['SAME R Results']['n_agree']} of 109 SAME-R records and with 'SAME1 Flight Tests 8-27-09' column Z for {cs['SAME1 Flight Tests 8-27-09']['n_agree']} of 25 SAME material records (0 disagreements).",
    category="external_check", investigation=BOTH, numbers=[N(109,"records","SAME-R agreement","109"), N(25,"records","SAME agreement","25")],
    scope_notes="Confirms internal workbook consistency; both sheets are author-reduced values, so this is not an independent measurement check, and raw instrument time series were not re-reduced.")
# ================= 2.0 V ORIGIN =================
add(doc_id="modelc-pmc7918997", location="Section 3.2 Spacecraft Smoke Detector Results, Figure 9 caption; Figure 9(b) image external/model_c/data/references/detector_fig9.jpg", anchor_quote="In both cases the alarm boundary is indicated with a dashed red line.",
    summary="Origin of the 2.0 V level: Meyer et al. 2018 Figure 9 plots ISS (right) and Space Shuttle (left) detector signal versus particle number concentration with a dashed 'Detector alarm boundary'. The numeric value is not written in the text; visual inspection of the figure shows the ISS boundary on the 2.0 V gridline (axis 0-7 V) and the Shuttle (STS) boundary slightly above 0.4 V. Within the examined SAME (PSI-102) and SAME-R (PSI-101) final-report texts, including their appended papers, no 2.0 V or other ISS scatter-voltage alarm threshold is stated (searched for 2 V / 2.0 V / alarm / threshold / volt patterns).",
    category="reference", investigation=BOTH, materials=MATS5, detector="ISS smoke detector; Space Shuttle smoke detector",
    numbers=[N(2.0,"V","ISS alarm boundary read from Figure 9(b) gridline (visual)","2.0")], conditions=C(gravity=FLIGHT),
    scope_notes="The 2.0 V value is a graph reading confirmed visually, not a printed number; the STS value is approximate and not used by Model C. Whether the plotted boundary equals the flight detector's operational alarm setting is not stated in the examined text.")
add(doc_id="modelc-psi102-same-final-report", pdf_page=12, location="Background section on ISS and STS detectors (report body)", anchor_quote="detector was designed to alarm at 1% obscuration per foot using an Underwriters Laboratory",
    summary="The SAME final report gives the ISS smoke detector's design alarm criterion as 1% obscuration per foot in a UL smoke box (and the STS detector's as a mass concentration of 2 mg/m3 for 5 s, based on 1 micron particles). This is a specification in obscuration units, not a voltage on the recorded scatter channel.",
    category="context", investigation="SAME", detector="ISS smoke detector; STS (Space Shuttle) smoke detector",
    numbers=[N(1,"%/ft","ISS design alarm obscuration","1%"), N(2,"mg/m3","STS design alarm particle loading","2 mg/m3")],
    scope_notes="No conversion from 1%/ft obscuration to the 2.0 V scatter-channel level is given within the examined files.")
add(doc_id="modelc-psi102-same-final-report", pdf_page=65, location="Appendix E (Spacecraft Fire Detection: Smoke Properties and Transport in Low-Gravity), smoke-transport modelling section", anchor_quote="The alarm point for the ISS detector is on the order of 0.5 mg/m3.",
    summary="An appended paper in the SAME report states the ISS detector alarm point is roughly 0.5 mg/m3, used in a computational smoke-transport study of ISS detector response.",
    category="context", investigation="SAME", detector="ISS smoke detector", numbers=[N(0.5,"mg/m3","approximate ISS detector alarm point (modelling input)","0.5 mg/m3")],
    scope_notes="Approximate ('on the order of'); a modelling assumption, not a flight measurement; not linked to the 2.0 V scatter level within the examined files.")
# ================= Meyer section 3.2 =================
add(doc_id="modelc-pmc7918997", location="Section 3.2 Spacecraft Smoke Detector Results", anchor_quote="The data points below the voltage threshold boundaries are cases where the detectors would",
    summary="Meyer et al. interpret Figure 9 points below the voltage boundary as cases where the detectors would have failed to alarm: for the Space Shuttle detector Kapton, Teflon and lamp wick; for the ISS detector Kapton and Teflon. The ISS detector would not have alarmed for over half of the Kapton tests and about two thirds of the Teflon tests; the Shuttle detector, though somewhat less sensitive overall, did better than the ISS detector on Teflon smoke under the tested conditions.",
    category="missed_alarm", investigation=BOTH, materials=["Kapton", "Teflon", "Lampwick"], detector="ISS smoke detector (near-IR forward light scattering); Space Shuttle smoke detector (ionization)",
    numbers=[N(0.5,"fraction","lower bound only: Kapton ISS tests without alarm stated as 'over half'","over half"), N(0.6667,"fraction","Teflon ISS tests without alarm","2/3")], conditions=C(gravity=FLIGHT),
    scope_notes="Hypothetical 'would have failed to alarm' judged against the plotted boundary, not observed alarm events; the exact set of points/tests behind the fractions is not stated in the text.")
add(doc_id="modelc-pmc7918997", location="Section 3.2 vs external/model_c/data/processed/dashboard_table.csv", anchor_quote="The ISS detector would not have alarmed for over half of the Kapton smoke",
    summary="Comparison of Meyer's aggregate statement with Model C counts: Kapton primary runs below 2 V = 12/21 (0.571; all records incl. secondary 21/36 = 0.583) - consistent with 'over half'. Teflon below 2 V = 11/15 primary (0.733), 7/11 SAME-R primary (0.636), 18/23 all records (0.783) - near the stated 2/3 but not exactly reproducible because the paper does not state which points (campaign, primary/secondary, P-Trak availability) are plotted.",
    category="external_check", investigation=BOTH, materials=["Kapton", "Teflon"], detector="ISS smoke detector (scatter channel)",
    numbers=[N(0.5714,"fraction","Kapton primary below 2 V (12/21)","12/21"), N(0.7333,"fraction","Teflon primary below 2 V (11/15)","11/15"), N(0.6364,"fraction","Teflon SAME-R primary below 2 V (7/11)","7/11")],
    scope_notes="Directionally consistent; exact denominator mismatch unresolved. Do not use Meyer's fractions as Model C accuracy targets.")
add(doc_id="modelc-pmc7918997", location="Section 3.2 Spacecraft Smoke Detector Results", anchor_quote="Since the ISS smoke detector is calibrated with 0.6 μm particles and the laser",
    summary="Meyer et al. explain the ISS shortfall physically: the ISS detector is calibrated with 0.6 um particles and its laser wavelength is about 1 um, so response is expected to drop for particles much smaller than that; Kapton smoke had TEM diameters of average mass below 0.3 um. They flag this as a concern because Kapton and Teflon are common in spacecraft electrical systems and may be among the first materials to overheat.",
    category="particle_property", investigation=BOTH, materials=["Kapton", "Teflon"], detector="ISS smoke detector (near-IR forward light scattering)",
    numbers=[N(0.6,"um","ISS detector calibration particle size","0.6 μm"), N(1,"um","approximate laser wavelength","approximately 1 μm"), N(0.3,"um","Kapton TEM diameter of average mass upper bound","less than 0.3 μm")],
    conditions=C(gravity=FLIGHT), scope_notes="Mechanistic interpretation by the authors; 'approximately' retained.")
add(doc_id="modelc-pmc7918997", location="Section 3.2 Spacecraft Smoke Detector Results", anchor_quote="The ISS detector signal was frequently saturated mainly by the larger smoke materials",
    summary="The ISS detector signal frequently saturated, mainly for the larger-particle smokes (silicone, Pyrell, lamp wick); this supports treating the ~6.2 V plateau in the workbook as saturation and using only threshold exceedance.",
    category="measurement_limitation", investigation=BOTH, materials=["Silicone", "Pyrell", "Lampwick"], detector="ISS smoke detector",
    conditions=C(gravity=FLIGHT), scope_notes="No numeric saturation voltage is given in the text.")
add(doc_id="modelc-pmc7918997", location="Section 3.2 Spacecraft Smoke Detector Results", anchor_quote="There is a much smaller data set for the Space Shuttle detector",
    summary="The Space Shuttle detector has far fewer data because it was operated only intermittently: its internal pump drew three liters per minute of aerosol, which made aging tests impossible. Model C therefore does not model the STS channel (it needs baseline offset and device-use flags).",
    category="measurement_limitation", investigation=BOTH, detector="Space Shuttle smoke detector (ionization)",
    numbers=[N(3,"L/min","Shuttle detector pump flow","three liters per minute")], conditions=C(gravity=FLIGHT),
    scope_notes="Limits any comparison of the two detectors to a smaller, non-aged subset.")
# ================= reports: particle/technology =================
add(doc_id="modelc-psi101-samer-final-report", pdf_page=5, location="Moment Instrument Results, text following Table 1", anchor_quote="comparatively much smaller diameters for the Kapton and Teflon will make detection of this smoke",
    summary="The SAME-R report states that the much smaller Kapton and Teflon smoke particles make detection challenging for light-scattering devices, while lamp wick and silicone give very large scattering signals; tuning a single-signal detector sensitive enough for Kapton/Teflon without excessive nuisance alarms from large dust is described as difficult without some particle-size discrimination, suggesting multi-moment detection.",
    category="technology_need", investigation="SAME-R", materials=["Kapton", "Teflon", "Lampwick", "Silicone"], detector="light-scattering smoke detectors (general)",
    conditions=C(gravity=FLIGHT), scope_notes="Couples missed-alarm risk (small particles) with false-alarm risk (dust); qualitative.")
add(doc_id="modelc-psi101-samer-final-report", pdf_page=5, location="Moment Instrument Results, discussion of Figures 6-8", anchor_quote="These figures show a strong trend of increased particle size at low flow rates.",
    summary="For Teflon, Kapton and lamp wick, particle diameters increased strongly at low duct velocity (linear fits in Figures 6-8; repeatability of diameter measurements estimated at about +/-15%), which the authors interpret as smoke trapped in avionics enclosures being larger than smoke released in ventilated areas.",
    category="particle_property", investigation="SAME-R", materials=["Teflon", "Kapton", "Lampwick"],
    numbers=[N(15,"%","estimated repeatability of diameter measurements","+/- 15%")], conditions=C(gravity=FLIGHT),
    scope_notes="Consistent in direction with Model C's Kapton airflow pattern, but the report does not analyse the ISS detector channel here.")
add(doc_id="modelc-psi101-samer-final-report", pdf_page=3, location="Flight Operation section (and Abstract on PDF p2)", anchor_quote="Totally 67 runs were conducted including two runs using reused samples.",
    summary="The SAME-R report's Flight Operation section reports 67 runs (two on reused samples) from July 16 to September 9, 2010, while its abstract and introduction (PDF p2) say 66 test points; Model C and the workbook contain 67 SAME-R primary runs, matching the Flight Operation count.",
    category="investigation_profile", investigation="SAME-R",
    numbers=[N(67,"runs","SAME-R runs (Flight Operation)","67"), N(66,"test points","SAME-R test points (abstract)","66"), N(2,"runs","runs on reused samples","two")],
    conditions=C(gravity=FLIGHT), n_independent_tests=None,
    scope_notes="Internal count difference in the report (66 vs 67) is unexplained within the examined text; the 67 figure is consistent with the workbook.")
add(doc_id="modelc-psi101-samer-final-report", pdf_page=2, location="Abstract / Introduction", anchor_quote="SAMER flight tests were conducted from July 16, to September 9, 2010",
    summary="Campaign profile: SAME flew in the ISS Microgravity Science Glovebox from September 9 to October 5, 2007; SAME-R (SAMER) reflew the same hardware from July 16 to September 9, 2010, adding Pyrell, higher heating temperatures, no-flow heating and a new instrument (M-pass) replacing one commercial diagnostic enclosure.",
    category="investigation_profile", investigation=BOTH, materials=MATS5, conditions=C(gravity=FLIGHT),
    scope_notes="Campaign differences (materials, condition ranges, instruments) are why Model C reports campaign-shift stress tests separately.")
add(doc_id="modelc-psi101-samer-final-report", pdf_page=2, location="Introduction (data reduction improvements)", anchor_quote="It was realized that even two tests use the same Rt/R0, the",
    summary="The SAME-R report notes that two tests with the same Rt/R0 heater-resistance setpoint can have quite different sample heating temperatures, motivating temperature-based characterisation; Rt/R0 is therefore an imperfect surrogate for sample temperature.",
    category="model_limitation", investigation="SAME-R", conditions=C(gravity=FLIGHT),
    scope_notes="Applies to Model C, which uses Rt/R0 (not derived temperature) as a control input.")
# ================= TEFLON TABLE 1 =================
t1 = tr["ntrs20130000422_table1"]["Teflon unaged"]
add(doc_id="modelc-ntrs20130000422", pdf_page=7, printed_page="7", location="Section C.1 Moment Instrument Results, Table 1 (row Teflon / Unaged); also external/model_c/data/references/20130000422.txt line 491 (layout text)", anchor_quote="Table 1: Diameter results for baseline runs for each material (Diameters are in micrometers).",
    summary=f"NTRS 20130000422 (Urban et al., 'Particle Morphology and Size Results from the Smoke Aerosol Measurement Experiment-2', 42nd ICES, AIAA 2012-3536, July 2012) Table 1 prints for unaged Teflon: geometric mean 0.081 um, count mean 0.101 um, diameter of average mass 0.170 um, sigma_g 2.198. Applying the lognormal (Hatch-Choate) relations used in Model C train.py (count = Dg exp(0.5 ln^2 sg), mass = Dg exp(1.5 ln^2 sg)) gives count {t1['count']['recomputed']:.6f} um and mass {t1['mass']['recomputed']:.6f} um. With +/-0.0005 rounding on Dg and sg the recomputed ranges are {t1['count']['bounds'][0]:.6f}-{t1['count']['bounds'][1]:.6f} and {t1['mass']['bounds'][0]:.6f}-{t1['mass']['bounds'][1]:.6f} um, disjoint from the printed 0.1005-0.1015 and 0.1695-0.1705. Conversely the printed count/mass pair implies sigma_g {t1['implied_from_count_mass']['sg']:.4f} and Dg {t1['implied_from_count_mass']['dg']:.4f} um. The other 9 rows are consistent within rounding.",
    category="external_check", investigation="SAME-R", materials=["Teflon"],
    numbers=[N(0.081,"um","printed geometric mean (unaged Teflon)","0.081"), N(2.198,"1","printed sigma_g","2.198"), N(0.101,"um","printed count mean","0.101"), N(0.170,"um","printed diameter of average mass","0.170"),
             N(round(t1['count']['recomputed'],6),"um","recomputed count mean","%.6f"%t1['count']['recomputed']), N(round(t1['mass']['recomputed'],6),"um","recomputed diameter of average mass","%.6f"%t1['mass']['recomputed'])],
    conditions=C(gravity=FLIGHT, airflow_cm_s=8.1, heating_s=60.0, aging_s=11.0), n_independent_tests=4,
    scope_notes="Algebraic consistency check of published rounded values, not new measurements; independent of the ISS 2 V labels. Matches Model C's external_checks.csv and teflon_table1_check.json to all printed digits.")
add(doc_id="teflon_table1_check.json", location="external/model_c/data/references/teflon_table1_check.json key status; reports/external_checks.csv row Teflon/unaged", anchor_quote="source_internal_inconsistency_unresolved",
    summary="Model C recorded the same unaged-Teflon discrepancy (recomputed count 0.11045 um, mass 0.20537 um; implied sigma_g 2.0577, Dg 0.07785 um) and left it unresolved, stating that no column-averaging explanation is documented in the publication; its 9 other Table 1 rows are 'consistent_with_source_rounding'. This agent's independent recomputation reproduces those numbers exactly.",
    category="external_check", investigation="SAME-R", materials=["Teflon"],
    numbers=[N(0.11045022504616728,"um","Model C recomputed count mean","0.11045022504616728"), N(0.20536658318748371,"um","Model C recomputed mass diameter","0.20536658318748371")],
    scope_notes="Agreement between Model C and this audit; see next item for a workbook-level explanation candidate.")
wa = tr["workbook_teflon_unaged_average"]
add(doc_id="PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx", location="sheet 'Teflon R&T plots' cells BR28, BS28, BU28, BV28 (row label 'Baseline Aging') -> sheet 'ICES 2012 Paper data table' E12:I12, M25:P25 and ROUND(...,3) cells M9:P9", anchor_quote="=AVERAGE(BR10:BR11,BR15:BR16)",
    _xlsx=("Teflon R&T plots", "BR28", True),
    summary=f"Workbook trace of the unaged-Teflon row: the PSI workbook sheet 'ICES 2012 Paper data table' rounds to 3 decimals exactly the printed Table 1 values (0.081, 0.101, 0.17, 2.198); they come from 'Teflon R&T plots' row 28, where count mean, mass diameter, sigma_g and Dg are each a separate AVERAGE over four SAME-R baseline runs (56/T02, 58/T03, 79/T04, 89/T08). Each run satisfies the lognormal relations exactly, but the runs are heterogeneous (sigma_g {min(v['sg'] for v in wa['per_run'].values()):.3f}-{max(v['sg'] for v in wa['per_run'].values()):.3f}, Dg {min(v['dg'] for v in wa['per_run'].values()):.4f}-{max(v['dg'] for v in wa['per_run'].values()):.4f} um), so applying the relations to the averaged Dg ({wa['column_averages']['dg']:.6f}) and sigma_g ({wa['column_averages']['sg']:.6f}) gives {wa['hc_from_averaged_params']['cmd']:.4f}/{wa['hc_from_averaged_params']['dam']:.4f} um instead of the averaged {wa['column_averages']['cmd']:.4f}/{wa['column_averages']['dam']:.4f} um. Column-wise averaging of lognormal parameters is therefore a documented-in-workbook mechanism that reproduces the inconsistency.",
    category="external_check", investigation="SAME-R", materials=["Teflon"],
    numbers=[N(round(wa['column_averages']['dg'],6),"um","averaged Dg (4 runs)","%.6f"%wa['column_averages']['dg']), N(round(wa['column_averages']['sg'],6),"1","averaged sigma_g","%.6f"%wa['column_averages']['sg']), N(round(wa['column_averages']['cmd'],6),"um","averaged count mean","%.6f"%wa['column_averages']['cmd']), N(round(wa['column_averages']['dam'],6),"um","averaged diameter of average mass","%.6f"%wa['column_averages']['dam'])],
    conditions=C(gravity=FLIGHT, airflow_cm_s=8.1, heating_s=60.0, aging_s=11.0), n_independent_tests=4,
    scope_notes="Shows how the published numbers arise in the workbook; it does not show which value set the authors intended, and the publication itself does not document the averaging. The NTRS-to-workbook link is by matching rounded values and the sheet name 'ICES 2012 Paper data table'.")
add(doc_id="PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx", location="sheet 'Kapton R&T plots' cell BR41 (=AVERAGE(BR12:BR15)), 'Teflon R&T plots' rows 10, 11, 15, 16 (column AW) and 'Kapton R&T plots' rows 12-15", anchor_quote="=AVERAGE(BR12:BR15)",
    _xlsx=("Kapton R&T plots", "BR41", True),
    summary="Link between particle-size table and detector response: the unaged Kapton Table 1 row averages SAME-R runs 51, 61, 73 and 92, and the unaged Teflon row averages SAME-R runs 56, 58, 79 and 89. All eight of these baseline runs had ISS scatter below 2.0 V (Kapton 0.42-0.75 V; Teflon 0.18-1.10 V), i.e. the published small 'baseline' Kapton/Teflon diameters come from runs that stayed below the Figure 9 boundary.",
    category="external_check", investigation="SAME-R", materials=["Kapton", "Teflon"], detector="ISS smoke detector (scatter channel)",
    numbers=[N(0.18,"V","lowest of the 8 runs (Teflon SAME-R:56)","0.1842"), N(1.10,"V","highest of the 8 runs (Teflon SAME-R:79)","1.1039280000000002")],
    conditions=C(gravity=FLIGHT, airflow_cm_s=8.1, heating_s=60.0, aging_s=11.0), n_independent_tests=7,
    scope_notes="Kapton runs 51 and 61 share a conservative group (51a ambiguity), so 8 runs = 7 Model C groups. Co-occurrence only; no causal claim.")
add(doc_id="PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx", location="sheet 'Teflon R&T plots' cell BR29 (=BR25, row label 'Aged 720 sec'); analogous rows in Kapton/Lampwick/Pyrell/Silicone R&T sheets", anchor_quote="=BR25",
    _xlsx=("Teflon R&T plots", "BR29", True),
    summary="The 'Aged 720 s' Table 1 rows are single secondary-aging readings, not multi-run means: Teflon = SAME-R 58a, Kapton = SAME-R 61a, Lampwick = SAME 32a, Pyrell = SAME-R 63a; Silicone averages two (SAME 23a and SAME-R 59a).",
    category="external_check", investigation=BOTH, materials=MATS5,
    conditions=C(gravity=FLIGHT, aging_s=720.0), n_independent_tests=1,
    scope_notes="Aged rows rest on one secondary record per material (two for Silicone) and cannot be treated as independent replicate tests.")
t2 = tr["samer_report_table1"]
add(doc_id="modelc-psi101-samer-final-report", pdf_page=5, location="Moment Instrument Results, Table 1 (Kapton rows on PDF p4, other rows on p5); workbook sheet 'AIAA 2012 Paper data table' K3:P12 (hard-coded values)", anchor_quote="Table 1: Diameter results for baseline runs for each material (Diameters are in micrometers).",
    summary=f"A second version of 'Table 1' exists: the SAME-R final report prints different values (e.g. unaged Teflon Dg 0.093, count mean 0.111, mass 0.173 um, sigma_g 2.081), matching the workbook sheet 'AIAA 2012 Paper data table'. Applying the same lognormal check, unaged Teflon again fails (recomputed {t2['Teflon unaged']['count']['recomputed']:.4f} and {t2['Teflon unaged']['mass']['recomputed']:.4f} um), and the unaged Kapton and unaged Silicone mass diameters miss the rounding interval by small margins (recomputed {t2['Kapton unaged']['mass']['recomputed']:.4f} vs printed 0.106; {t2['Silicone unaged']['mass']['recomputed']:.4f} vs 0.468); the other 7 rows pass.",
    category="external_check", investigation="SAME-R", materials=["Teflon", "Kapton", "Silicone"],
    numbers=[N(0.093,"um","SAME-R report unaged Teflon Dg","0.093"), N(0.111,"um","SAME-R report unaged Teflon count mean","0.111"), N(0.173,"um","SAME-R report unaged Teflon mass diameter","0.173"), N(2.081,"1","SAME-R report unaged Teflon sigma_g","2.081")],
    scope_notes="Two published versions of the baseline size table disagree for Teflon (0.081/0.101/0.170/2.198 in NTRS 20130000422 vs 0.093/0.111/0.173/2.081 in the SAME-R report); which is authoritative is not stated within the examined sources.")
add(doc_id="modelc-ntrs20130000422", pdf_page=8, location="Figure 6-8 captions (lampwick, Kapton; Teflon caption on p9)", anchor_quote="The repeatability of the diameter measurements is estimated to be +/- 15%.",
    summary="The same paper estimates repeatability of the diameter measurements at about +/-15%; the unaged-Teflon algebraic discrepancy (about 9% for count mean and 21% for mass diameter relative to printed values) is a table-consistency issue, separate from measurement repeatability.",
    category="measurement_limitation", investigation="SAME-R", materials=["Teflon", "Kapton", "Lampwick"], numbers=[N(15,"%","diameter repeatability estimate","+/- 15%")],
    scope_notes="Percentages of the discrepancy computed by this audit from printed vs recomputed values (0.1105 vs 0.101; 0.2054 vs 0.170).")
add(doc_id="modelc-ntrs20120012884", pdf_page=4, location="Section on diagnostics (P-Trak and DustTrak descriptions)", anchor_quote="This instrument is very robust and operates over a range of 0 to",
    summary="NTRS 20120012884 is 'Properties of Smoke from Overheated Materials in Low-Gravity' (Urban, Ruff, Sheredy, Cleary, Yang, Mulholland, Yuan; AIAA paper, year not printed in the text). Its PDF p4 gives the P-Trak range (0 to 10^5 particles/cm3, 20 nm to 1 um) and DustTrak range (0.001 to 100 mg/m3), matching what Model C cites; the only 'saturated' wording on pp4-5 refers to the P-Trak isopropanol vapour, so ISS-signal saturation is supported by Meyer et al. 2018 section 3.2, not by this paper.",
    category="external_check", investigation="SAME", numbers=[N(100000,"particles/cm3","P-Trak upper range (10^5; superscript flattened to 105 in the extracted text)","105"), N(0.001,"mg/m3","DustTrak lower range","0.001 mg/m3"), N(100,"mg/m3","DustTrak upper range","100 mg /m3")],
    scope_notes="Nominal instrument ranges; Model C correctly warns they must not be used as censoring limits on diluted/corrected workbook values.")
# ================= MODEL LIMITATIONS =================
add(doc_id="STATUS.json", location="external/model_c/STATUS.json known_limits[0]; MODEL_CARD.md line 7; domain.json key target", anchor_quote="Experimental2V proxy, not reported operational alarm",
    summary="Model C's target is a derived experimental proxy (recorded ISS scatter >= 2 V), not a reported operational alarm, alarm event or safety certification; Agent 5 must phrase any Model C output as 'signal reached the 2 V reference level in the experiment', never as 'the detector alarmed'.",
    category="model_limitation", investigation=BOTH, detector="ISS smoke detector (scatter channel)", scope_notes="Applies to all Model C labels and predictions.")
add(doc_id="evaluation_followup.md", location="external/model_c/reports/evaluation_followup.md lines 7-23 (baseline comparison table and interpretation)", anchor_quote="Material identity explains the headline score",
    summary="Material identity explains Model C's score: a per-material majority baseline reaches balanced accuracy 0.891342 +/- 0.048823 on the saved outer folds, a fixed forest 0.900433 +/- 0.056572, and the original nested-selection headline 0.870152 +/- 0.076360. Forest minus material-majority is 0.009091 +/- 0.020328 with 4 of 5 fold differences exactly zero, so controlled conditions add no demonstrated predictive value beyond material.",
    category="model_limitation", investigation=BOTH, materials=MATS5,
    numbers=[N(0.891342,"balanced accuracy","material-majority baseline mean","0.891342"), N(0.900433,"balanced accuracy","fixed forest mean","0.900433"), N(0.870152,"balanced accuracy","original nested-selection headline","0.870152"), N(0.009091,"balanced accuracy","forest minus majority mean","0.009091")],
    scope_notes="Post-hoc comparison on the same outer groups; fold SD is not a confidence interval. The 0.5 'majority baseline' in the original headline is a global-majority baseline, not the material baseline.")
add(doc_id="metrics.json", location='external/model_c/reports/metrics.json per_material.Kapton.recall and per_material.Teflon.recall; evaluation.md Per material table', anchor_quote="0.1111111111111111",
    summary="On held-out (nested out-of-fold) predictions Model C recovers almost none of the Kapton and Teflon runs that reached 2 V: Kapton recall 0.111 (1 of 9 positives; confusion [[11,1],[8,1]]), Teflon recall 0.0 (0 of 4; [[11,0],[4,0]]), balanced accuracy 0.514 and 0.5. It effectively predicts 'below 2 V' for these materials.",
    category="model_limitation", investigation=BOTH, materials=["Kapton", "Teflon"],
    numbers=[N(0.1111111111111111,"recall","Kapton held-out positive recall","0.1111111111111111"), N(0.0,"recall","Teflon held-out positive recall","0.0"), N(0.5138888888888888,"balanced accuracy","Kapton per-material","0.5138888888888888")],
    n_independent_tests=34, scope_notes="Kapton 19 + Teflon 15 groups. Model C cannot be used to identify which Kapton/Teflon conditions reach 2 V.")
add(doc_id="evaluation_followup.md", location="external/model_c/reports/evaluation_followup.md lines 25-46 (Kapton and Teflon within-material diagnostics)", anchor_quote="Post-hoc within-material diagnostic; fixed C1 balanced logistic; no model export or deployment claim",
    summary="Within-material logistic diagnostics on numeric controls only: Kapton pooled out-of-fold balanced accuracy 0.583 (recall 0.333; fold values 0.375, 1.0, 0.35), Teflon 0.739 (recall 0.75; one fold single-class). They are small, post-hoc, unserialized and confounded by test matrix, campaign and reused samples.",
    category="model_limitation", investigation=BOTH, materials=["Kapton", "Teflon"],
    numbers=[N(0.5833333333333334,"balanced accuracy","Kapton pooled OOF","0.5833333333333334"), N(0.7386363636363636,"balanced accuracy","Teflon pooled OOF","0.7386363636363636")],
    n_independent_tests=34, scope_notes="Not evidence of reliable condition effects; scatter relationships are descriptive, not causal.")
add(doc_id="domain.json", location="external/model_c/artifacts/model_c/domain.json keys ood_definition, ood_threshold, ranges; reports/ood_example.json", anchor_quote="Maximum same-material standardized nearest condition distance from a different training group",
    summary="Model C's out-of-distribution flag is a heuristic: a request is flagged when its standardized nearest-neighbour distance to same-material training conditions exceeds 9.32 (the largest such distance between different training groups). Range checks use global ranges, so a Kapton request at Rt/R0 1.22 (Kapton was only tested at 1.38-1.48) with 0 cm/s, 10 s heating, 1 s aging is accepted, predicted True and only flagged OOD (distance 10.03).",
    category="model_limitation", investigation=BOTH, materials=["Kapton"],
    numbers=[N(9.321957129180975,"1","OOD distance threshold","9.321957129180975"), N(10.029008507411396,"1","example request distance","10.029008507411396")],
    scope_notes="OOD flag is not a calibrated uncertainty; unseen materials are rejected, but unseen per-material condition combinations are only flagged.")
add(doc_id="evaluation.md", location="external/model_c/reports/evaluation.md lines 48-55 (Campaign shift; leave-one-material-out); metrics.json leave_one_material_out_stress_test", anchor_quote="Inference rejects unseen materials; this diagnostic does not support deployment on held-out materials.",
    summary="Generalization stress tests are weak: training on SAME and testing on SAME-R gives balanced accuracy 0.629 (12 Pyrell rows excluded as unseen), SAME-R to SAME 0.846 on 17 rows; leave-one-material-out logistic gives Kapton 0.458 and Teflon 0.443. Model C rejects unseen materials.",
    category="model_limitation", investigation=BOTH, materials=MATS5,
    numbers=[N(0.6286549707602339,"balanced accuracy","SAME -> SAME-R","0.6286549707602339"), N(0.8461538461538461,"balanced accuracy","SAME-R -> SAME","0.8461538461538461"), N(0.45833333333333337,"balanced accuracy","LOMO Kapton","0.45833333333333337"), N(0.4431818181818182,"balanced accuracy","LOMO Teflon","0.4431818181818182")],
    scope_notes="No support for other materials, campaigns or hardware.")
add(doc_id="evaluation.md", location="external/model_c/reports/evaluation.md line 69 (Limits)", anchor_quote="No ambient spacecraft generalization, time-to-alarm, flame/fatality risk, detector certification, or unseen-material prediction.",
    summary="Model C's stated scope excludes ambient spacecraft generalization, time-to-alarm, flame or fatality risk, detector certification and unseen materials; it also notes only 84 primary records with uneven coverage, unresolved per-row saturation/LOD, blank (unknown) SAME-R quality flags, Rt/R0 not determining sample temperature, and no raw instrument calibration reconstruction.",
    category="model_limitation", investigation=BOTH, materials=MATS5, scope_notes="Agent 5 must not extend Model C outputs to flaming fires, full-scale cabins or alarm timing.")
add(doc_id="evaluation.md", location="external/model_c/reports/evaluation.md line 65", anchor_quote="No uncertainty interval or calibrated probability is claimed.",
    summary="Model C reports no uncertainty intervals and no calibrated probabilities; fold standard deviations describe variability only.",
    category="model_limitation", investigation=BOTH, scope_notes="Any probability-like number shown by Agent 5 from Model C would be unsupported.")
add(doc_id="MODEL_CARD.md", location="external/model_c/MODEL_CARD.md line 13 (measured-only dashboard paragraph)", anchor_quote="These describe the available primary experiments, not probabilities for new fires.",
    summary="The measured fractions (Kapton 9/21, Teflon 4/15, Lampwick 17/17, Pyrell 12/12, Silicone 19/19 reaching 2 V) describe the available primary experiments, not probabilities for new fires.",
    category="model_limitation", investigation=BOTH, materials=MATS5,
    numbers=[N(9,"runs","Kapton reaching 2 V of 21","9/21"), N(4,"runs","Teflon reaching 2 V of 15","4/15")],
    scope_notes="Use as test-matrix description with group counts, never as detection probability.")
add(doc_id="evaluation.md", location="external/model_c/reports/evaluation.md line 69 (Limits) and lines 61-63", anchor_quote="SAME-R source quality flags are blank/unknown.",
    summary="SAME's fan-problem and flat-profile flags are 'n' but SAME-R's are blank, which Model C treats as unknown rather than verified absence; together with author-reduced (not re-calibrated) channels this limits data-quality filtering for the SAME-R runs that hold most below-2 V cases.",
    category="model_limitation", investigation="SAME-R", scope_notes="Quality of individual SAME-R runs cannot be confirmed from the workbook flags.")
json.dump(dict(items=items, documents=documents), open("items_draft.json", "w"), indent=1, ensure_ascii=False)
print(len(items), "items;", len(documents), "documents")
