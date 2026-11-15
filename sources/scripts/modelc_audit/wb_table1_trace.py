"""Trace the ICES 2012 Paper data table rows (rounded = NTRS 20130000422 Table 1) to per-run rows."""
import openpyxl, sys, re, json, math
from openpyxl.utils import column_index_from_string as C, range_boundaries
W, OUT = sys.argv[1], sys.argv[2]
wbf = openpyxl.load_workbook(W, data_only=False)
wbv = openpyxl.load_workbook(W, data_only=True)
ices_f, ices_v = wbf["ICES 2012 Paper data table"], wbv["ICES 2012 Paper data table"]
out = []
for r in range(3, 18):
    mat = ices_v.cell(r, 3).value; state = ices_v.cell(r, 4).value
    ref = ices_f.cell(r, 5).value  # E = CMD reference
    if not mat or not isinstance(ref, str) or "!" not in ref: continue
    m = re.match(r"='([^']+)'!([A-Z]+)(\d+)", ref)
    sheet, rown = m[1], int(m[3])
    f = wbf[sheet]; v = wbv[sheet]
    formula = f.cell(rown, C("BR")).value
    rows = []
    if isinstance(formula, str) and formula.upper().startswith("=AVERAGE("):
        for part in formula[9:-1].split(","):
            mn_c, mn_r, mx_c, mx_r = range_boundaries(part)
            rows += list(range(mn_r, mx_r + 1))
    elif isinstance(formula, str) and re.fullmatch(r"=BR\d+", formula):
        rows = [int(formula[3:])]
    runs = []
    for rr in rows:
        runs.append(dict(sheet_row=rr, campaign={1: "SAME", 2: "SAME-R"}.get(v.cell(rr, 1).value, v.cell(rr, 1).value), same_no=str(v.cell(rr, C("G")).value),
                         sample_id=v.cell(rr, C("D")).value, desc=v.cell(rr, C("H")).value,
                         cmd=v.cell(rr, C("BR")).value, dam=v.cell(rr, C("BS")).value, sg=v.cell(rr, C("BU")).value, dg=v.cell(rr, C("BV")).value))
    rec = dict(material=mat, state=state, ices_row=r, source_sheet=sheet, source_row=rown, br_formula=formula,
               bu_formula=f.cell(rown, C("BU")).value, bv_formula=f.cell(rown, C("BV")).value,
               cmd=ices_v.cell(r, 5).value, dam=ices_v.cell(r, 6).value, sg=ices_v.cell(r, 8).value, dg=ices_v.cell(r, 9).value, runs=runs)
    # per-run Hatch-Choate self-consistency and averaged-parameter consistency
    for x in runs:
        if all(isinstance(x[k], (int, float)) for k in ("cmd", "dam", "sg", "dg")):
            s2 = math.log(x["sg"]) ** 2
            x["hc_cmd"] = x["dg"] * math.exp(0.5 * s2); x["hc_dam"] = x["dg"] * math.exp(1.5 * s2)
    if isinstance(rec["sg"], (int, float)):
        s2 = math.log(rec["sg"]) ** 2
        rec["hc_cmd_from_avg_params"] = rec["dg"] * math.exp(0.5 * s2)
        rec["hc_dam_from_avg_params"] = rec["dg"] * math.exp(1.5 * s2)
    out.append(rec)
json.dump(out, open(OUT, "w"), indent=1, default=str)
for rec in out:
    print(rec["material"], rec["state"], rec["source_sheet"], rec["source_row"], rec["br_formula"], "| BU:", rec["bu_formula"])
    print("   avg cmd %.5f dam %.5f sg %.5f dg %.5f | HC from avg params: cmd %.5f dam %.5f" % (rec["cmd"], rec["dam"], rec["sg"], rec["dg"], rec.get("hc_cmd_from_avg_params", float('nan')), rec.get("hc_dam_from_avg_params", float('nan'))))
    for x in rec["runs"]:
        print("     ", x["campaign"], x["same_no"], x["sample_id"], x["desc"], "cmd", x["cmd"], "sg", x["sg"], "dg", x["dg"], "hc_cmd", x.get("hc_cmd"))
