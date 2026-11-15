"""Hatch-Choate recomputation, same relations as model_c/train.py scientific_checks():
count mean = Dg*exp(0.5 ln^2 sg); diameter of average mass = Dg*exp(1.5 ln^2 sg);
rounding bounds: (Dg -/+ 0.0005)*exp(c*ln(sg -/+ 0.0005)^2)."""
import math, json, sys
def hc(dg, sg, c): return dg * math.exp(c * math.log(sg) ** 2)
def check(dg, dc, dm, sg):
    out = {"printed": dict(dg=dg, count=dc, mass=dm, sg=sg)}
    for lab, c, tgt in (("count", .5, dc), ("mass", 1.5, dm)):
        v = hc(dg, sg, c); lo = hc(dg - .0005, sg - .0005, c); hi = hc(dg + .0005, sg + .0005, c)
        out[lab] = dict(recomputed=v, bounds=[lo, hi], printed_interval=[tgt - .0005, tgt + .0005],
                        overlap=bool(lo <= tgt + .0005 and hi >= tgt - .0005), abs_diff=abs(v - tgt), rel_diff=(v - tgt) / tgt)
    # inverse: sg, dg implied by printed count & mass means
    s2 = math.log(dm / dc); out["implied_from_count_mass"] = dict(sg=math.exp(math.sqrt(s2)), dg=dc / math.exp(.5 * s2))
    return out
res = {}
res["ntrs20130000422_table1"] = {
 "Kapton unaged": check(.042, .056, .101, 2.154), "Kapton 720s": check(.089, .109, .161, 1.872),
 "Lampwick unaged": check(.090, .128, .258, 2.312), "Lampwick 720s": check(.229, .276, .398, 1.834),
 "Silicone unaged": check(.128, .196, .465, 2.530), "Silicone 720s": check(.269, .355, .619, 2.108),
 "Teflon unaged": check(.081, .101, .170, 2.198), "Teflon 720s": check(.070, .105, .232, 2.442),
 "Pyrell unaged": check(.149, .204, .384, 2.211), "Pyrell 720s": check(.293, .359, .539, 1.892)}
res["samer_report_table1"] = {
 "Kapton unaged": check(.047, .062, .106, 2.072), "Kapton 720s": check(.102, .121, .169, 1.790),
 "Lampwick unaged": check(.103, .142, .271, 2.232), "Lampwick 720s": check(.269, .308, .401, 1.673),
 "Silicone unaged": check(.152, .221, .468, 2.382), "Silicone 720s": check(.320, .400, .628, 1.956),
 "Teflon unaged": check(.093, .111, .173, 2.081), "Teflon 720s": check(.080, .115, .237, 2.342),
 "Pyrell unaged": check(.177, .227, .377, 2.032), "Pyrell 720s": check(.348, .400, .529, 1.697)}
# workbook: Teflon R&T plots row 28 = AVERAGE of per-run rows 10,11,15,16 (SAME-R 58,79,89,56)
runs = {"SAME-R:58": (0.0531282678168605, 0.14934491754394455, 2.7638822532432576, 0.031687885565052865),
        "SAME-R:79": (0.16283968830998286, 0.19310173093440533, 1.5111289946801014, 0.14953653401481964),
        "SAME-R:89": (0.05508867666449692, 0.15132510528359466, 2.732534317487376, 0.03323823985693733),
        "SAME-R:56": (0.13183675328073566, 0.18452250171432627, 1.785741217437197, 0.11143717188099855)}
avg = [sum(v[i] for v in runs.values()) / 4 for i in range(4)]
per_run = {k: dict(cmd=v[0], dam=v[1], sg=v[2], dg=v[3], hc_cmd=hc(v[3], v[2], .5), hc_dam=hc(v[3], v[2], 1.5)) for k, v in runs.items()}
res["workbook_teflon_unaged_average"] = dict(per_run=per_run, column_averages=dict(cmd=avg[0], dam=avg[1], sg=avg[2], dg=avg[3]),
    rounded=dict(cmd=round(avg[0], 3), dam=round(avg[1], 3), sg=round(avg[2], 3), dg=round(avg[3], 3)),
    hc_from_averaged_params=dict(cmd=hc(avg[3], avg[2], .5), dam=hc(avg[3], avg[2], 1.5)))
json.dump(res, open(sys.argv[1], "w"), indent=1)
for t in ("ntrs20130000422_table1", "samer_report_table1"):
    print("==", t)
    for k, v in res[t].items():
        print(f"  {k:16s} count {v['count']['recomputed']:.6f} [{v['count']['bounds'][0]:.6f},{v['count']['bounds'][1]:.6f}] ok={v['count']['overlap']}  mass {v['mass']['recomputed']:.6f} [{v['mass']['bounds'][0]:.6f},{v['mass']['bounds'][1]:.6f}] ok={v['mass']['overlap']}  implied sg {v['implied_from_count_mass']['sg']:.4f} dg {v['implied_from_count_mass']['dg']:.4f}")
print(json.dumps(res["workbook_teflon_unaged_average"], indent=1))
