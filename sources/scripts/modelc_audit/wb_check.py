"""Independent spot-check of Model C dashboard_table.csv against the PSI workbook.
Does not import model_c. Columns located by row-2 header text."""
import openpyxl, sys, json, re, random, csv
from openpyxl.utils import get_column_letter as L
W = sys.argv[1]; DASH = sys.argv[2]; OUT = sys.argv[3]
MATS = {"Kapton", "Lampwick", "Pyrell", "Silicone", "Teflon"}
wb = openpyxl.load_workbook(W, data_only=True, read_only=True)

def load(sheet, hdr_row=2):
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[hdr_row-1]
    return rows, hdr

def col(hdr, text, start=0):
    for j, h in enumerate(hdr):
        if j >= start and isinstance(h, str) and h.strip().lower() == text.lower():
            return j
    raise KeyError(text)

res = {}
rows, hdr = load("Combined Rslts Copy this sheet")
cA = 0  # 'Flight 1=same 2=sameR, g=ground'
assert hdr[cA].startswith("Flight 1=same")
cMat = col(hdr, "Sample Type"); cSame = col(hdr, "SAME #"); cDur = col(hdr, "Duration (sec)")
cAW = col(hdr, "ISS Detector Scatter (volts)"); cSID = col(hdr, "Sample ID"); cDesc = col(hdr, "Description")
res["combined_columns"] = {k: L(v+1) for k, v in dict(material=cMat, same_no=cSame, duration=cDur, iss_scatter=cAW, sample_id=cSID, description=cDesc).items()}
recs = []
for i, r in enumerate(rows, 1):
    if i <= 2: continue
    camp = {1: "SAME", 2: "SAME-R"}.get(r[cA])
    if camp is None or r[cMat] not in MATS: continue
    same = str(r[cSame]).strip()
    primary = re.fullmatch(r"\d+", same) is not None
    recs.append(dict(row=i, campaign=camp, material=r[cMat], same=same, primary=primary, iss=r[cAW], dur=r[cDur], sample=r[cSID], desc=r[cDesc]))
res["n_flight_material_records"] = len(recs)
summ = {}
for m in sorted(MATS):
    p = [x for x in recs if x["material"] == m and x["primary"]]
    summ[m] = dict(n_primary=len(p), n_ge_2v=sum(1 for x in p if isinstance(x["iss"], (int, float)) and x["iss"] >= 2.0),
                   by_campaign={c: sum(1 for x in p if x["campaign"] == c) for c in ["SAME", "SAME-R"]},
                   ids=[f'{x["campaign"]}:{x["same"]}' for x in p],
                   min_iss=min(x["iss"] for x in p), max_iss=max(x["iss"] for x in p),
                   ge2_ids=[f'{x["campaign"]}:{x["same"]}' for x in p if x["iss"] >= 2.0])
res["workbook_primary_summary"] = summ
res["n_primary_total"] = sum(v["n_primary"] for v in summ.values())
res["n_secondary_total"] = sum(1 for x in recs if not x["primary"])
# compare against dashboard_table.csv
dash = {}
with open(DASH, newline="") as f:
    for d in csv.DictReader(f):
        dash[d["test_id"]] = d
res["dashboard_rows"] = len(dash)
full = {"match": 0, "mismatch": [], "missing_in_dashboard": [], "extra_in_dashboard": []}
wbkeys = set()
for x in recs:
    k = f'{x["campaign"]}:{x["same"]}'
    wbkeys.add(k)
    d = dash.get(k)
    if d is None:
        full["missing_in_dashboard"].append(k); continue
    ok = d["material"] == x["material"] and abs(float(d["iss_scatter_v"]) - float(x["iss"])) < 1e-12 and int(d["source_row"]) == x["row"]
    if ok: full["match"] += 1
    else: full["mismatch"].append((k, x["material"], x["iss"], d["material"], d["iss_scatter_v"], d["source_row"], x["row"]))
full["extra_in_dashboard"] = sorted(set(dash) - wbkeys)
res["full_row_comparison"] = full
# dashboard training_eligible vs independent primary definition
te = {k for k, d in dash.items() if d["training_eligible"] == "True"}
prim = {f'{x["campaign"]}:{x["same"]}' for x in recs if x["primary"]}
res["primary_def_vs_training_eligible"] = {"only_workbook_primary": sorted(prim - te), "only_dashboard_eligible": sorted(te - prim), "n_both": len(prim & te)}
# random spot check (seeded) with printed detail
rng = random.Random(20261115)
sample = rng.sample(recs, 12)
spot = []
for x in sample:
    k = f'{x["campaign"]}:{x["same"]}'; d = dash[k]
    spot.append(dict(test_id=k, workbook_row=x["row"], workbook_material=x["material"], workbook_iss_v=x["iss"],
                     dashboard_material=d["material"], dashboard_iss_v=float(d["iss_scatter_v"]),
                     dashboard_source_row=int(d["source_row"]), dashboard_label=d["alarm_level_reached"],
                     recomputed_label=int(x["iss"] >= 2.0),
                     match=(d["material"] == x["material"] and abs(float(d["iss_scatter_v"]) - x["iss"]) < 1e-12 and int(d["source_row"]) == x["row"] and int(float(d["alarm_level_reached"])) == int(x["iss"] >= 2.0))))
res["random_spot_check"] = spot
# label check for all rows
lab_mis = [k for k, d in dash.items() if d["iss_scatter_v"] and int(float(d["alarm_level_reached"])) != int(float(d["iss_scatter_v"]) >= 2.0)]
res["label_rule_mismatches_all_rows"] = lab_mis

# Cross-check against per-campaign original sheets
def campaign_sheet(sheet, same_hdr, mat_hdr, iss_hdr, camp):
    rws, h = load(sheet)
    cs, cm, ci = col(h, same_hdr), col(h, mat_hdr), col(h, iss_hdr)
    out = {}
    for i, r in enumerate(rws, 1):
        if i <= 2 or r[cm] not in MATS or r[cs] is None: continue
        out[f"{camp}:{str(r[cs]).strip()}"] = (i, r[cm], r[ci])
    return out, {"same": L(cs+1), "material": L(cm+1), "iss": L(ci+1)}
cross = {}
for sheet, camp in [("SAME R Results", "SAME-R"), ("SAME1 Flight Tests 8-27-09", "SAME")]:
    try:
        m, cols = campaign_sheet(sheet, "SAME #", "Sample Type", "ISS Detector Scatter (volts)", camp)
    except KeyError as e:
        cross[sheet] = f"header not found: {e}"; continue
    agree, disagree, absent = 0, [], []
    for x in recs:
        if x["campaign"] != camp: continue
        k = f'{x["campaign"]}:{x["same"]}'
        if k not in m: absent.append(k); continue
        _, mm, iv = m[k]
        if mm == x["material"] and isinstance(iv, (int, float)) and abs(iv - x["iss"]) < 1e-9: agree += 1
        else: disagree.append((k, x["material"], x["iss"], mm, iv, m[k][0]))
    cross[sheet] = {"columns": cols, "n_agree": agree, "disagree": disagree, "absent_in_campaign_sheet": absent}
res["campaign_sheet_crosscheck"] = cross
json.dump(res, open(OUT, "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k not in ("random_spot_check",)}, indent=1, default=str)[:6000])
for s in spot: print(s)
