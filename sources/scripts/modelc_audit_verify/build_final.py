import json, copy, re, hashlib, os, datetime
P = '/home/efeai/Desktop/NasaSpaceApps'
SRC = P + '/sources/extracted/modelc_audit.json'
OUT = P + '/sources/extracted/modelc_audit.final.json'
d = json.load(open(SRC))
f = copy.deepcopy(d)
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
NULLCOND = {"atmosphere_o2_vol_pct": None, "pressure_kpa": None, "airflow_cm_s": None, "gravity": None, "heating_s": None, "aging_s": None}
FLIGHT = "low gravity, ISS Microgravity Science Glovebox (flight)"

# ---------------- per-item verdicts ----------------
notes = {
 '01': None, '02': "Recomputed independently: 6/6 artifact hashes match; anchor (model.joblib hash) present in checksums.json.",
 '03': "Recomputed independently: 7/7 sha256 match and all 5 recorded byte sizes match; anchor (workbook hash) present.",
 '04': "Recomputed independently: 7/7 STATUS.json followup.protected_artifact_sha256 match; anchor key present.",
 '05': "data_dictionary.json alarm_level_reached: rule 'iss_scatter_v >= 2.0', provenance derived, source 'Meyer et al. 2018 Figure 9', assumptions text as paraphrased; label_rule column string confirmed in dashboard_table.csv.",
 '06': "data.py lines 100-154 checked: campaign map {1:SAME,2:SAME-R}, MATERIALS filter, 'a'-suffix secondary rule, missing control over FEATURES[1:] (five controls), heating <= 0, missing/negative signal, y/yes quality flags. 84 primary of 134 reproduced independently from the workbook.",
 '07': "Anchor is in the scope cell of every row of dashboard_measured_only.csv; paraphrase faithful.",
 '08': "Anchor on SAME-R report PDF p3 (Flight Operation). 67 runs incl. two reused samples and 109 entries confirmed; 50 secondary records (8 SAME, 42 SAME-R) recomputed from the workbook. The gloss 'further aging of an already generated smoke batch' is the extractor's paraphrase, consistent with the workbook descriptions ('aged', 'after secondary aging').",
 '10': "evaluation.md line 5 and Limits paragraph checked; 82 primary sample IDs and 81 groups recomputed from dashboard_table.csv (51 K01 and 61 K02 share group-028 via 51a).",
 '11': "Rule string present in dashboard_measured_only.csv; evaluation_followup.md confirms reburns count as runs.",
 '12': "All 14 numbers, test IDs, campaigns and mixing range match the Kapton row of dashboard_measured_only.csv exactly; independently reproduced from the workbook (21 runs, 9 >= 2.0 V).",
 '13': "All 14 numbers, test IDs and campaigns match the Teflon row exactly; independently reproduced from the workbook (15 runs, 4 >= 2.0 V).",
 '14': "All numbers and test IDs match the Lampwick row exactly; workbook gives 17/17.",
 '15': "All numbers and test IDs match the Pyrell row exactly; workbook gives 12/12, SAME-R only.",
 '16': "All numbers and test IDs match the Silicone row exactly (mixing 0.0-8.0 s); workbook gives 19/19.",
 '17': "metrics.json campaign_counts {SAME:17, SAME-R:67} and class_balance {1:61, 0:23} confirmed; below-2 V by material recomputed: Kapton 12, Teflon 11.",
 '18': "Recomputed from dashboard_table.csv: SAME Kapton 4/4 >= 2 V (3.66-5.64 V, 2-8 cm/s); SAME-R 5/17 in 15 groups; SAME:29 3.6637 V vs SAME-R 51/61/73/92 0.418-0.750 V at Rt/R0 1.38, 60 s, 11 s, 8.1 cm/s. heating_s/aging_s conditions apply to the baseline comparison only.",
 '19': None, '20': None, '21': None,
 '22': "Recomputed: 720 s primary aging runs SAME:5 and SAME-R:67 (Silicone), 68 (Lampwick), 69 (Teflon 5.04 V), 70 (Kapton 0.90 V), 71 (Pyrell); Teflon/Pyrell heating always 60 s; only SAME:5 has mixing 0 s; Pyrell SAME-R only. Note: longer aging exists only in secondary records (see verifier item on 11-1800 s aging).",
 '23': "SAME:41 Teflon 'low flow aging' 2 cm/s, Rt/R0 1.44, 60 s, 11 s, 0.0006866452 V confirmed; data_dictionary instrument_limits text confirmed.",
 '24': None,
 '25': "Independently re-derived with openpyxl 3.1.5 by header text (A 'Flight 1=same 2=sameR', C 'Sample Type', G 'SAME #', AW 'ISS Detector Scatter (volts)'): 134 records, 84 primary (17 SAME, 67 SAME-R), 50 secondary; Kapton 21 (SAME 4/4, SAME-R 17/5 >= 2 V), Teflon 15 (SAME 4/0, SAME-R 11/4); all test-ID lists equal Model C's. 51a has heating 60 s and only the secondary flag, so the 22-record alternative is correct.",
 '26': "Verifier full-table comparison: 134/134 rows match on test_id, material, exact ISS float, source_row and recomputed label; training_eligible set equals the suffix-free primary set (84).",
 '27': "All 12 listed rows re-checked against workbook cell C/G/AW and dashboard_table.csv: match. Verifier also drew its own 12-row sample (random seed 4242: SAME-R:98, 55, 94a, 93a, 83a, 77a, 63, 112, 108, 105; SAME:27, 26a): 12/12 match.",
 '28': "AW3 formula ='SAME1 Flight Tests 8-27-09'!Z7 confirmed; all 134 AW cells are single-cell references ('SAME R Results'!AR x109, 'SAME1 Flight Tests 8-27-09'!Z x25) and cached values agree 109/109 and 25/25.",
 '29': "Figure 9 caption anchor present (section 3.2). Verifier viewed detector_fig9.jpg: ISS panel (b) dashed 'Detector alarm boundary' lies on the 2.0 V gridline (axis 0-7 V); STS panel (a) boundary slightly above 0.4 V. Verifier regex search of both PSI report texts (all pages) found no ISS scatter-voltage alarm threshold; '2 mg/m3' hits are mass-concentration criteria (see verifier items).",
 '30': "Anchor on SAME report PDF p12; STS '2 mg/m3 for 5 seconds (based on 1 micron particles)' also on p12 (the omitted alternative criterion is a 0.022 mg/m3/s rise for 20 s).",
 '31': "Anchor on PDF p65 inside Appendix E (title page PDF p59); context is the FDS smoke-transport model.",
 '32': None,
 '33': "Ratios recomputed from dashboard_table.csv: Kapton 12/21 primary, 21/36 all records; Teflon 11/15 primary, 7/11 SAME-R primary, 18/23 all records.",
 '34': "Section 3.2 text confirmed: TEM diameters of average mass < 0.3 um for Kapton; calibration 0.6 um; wavelength approximately 1 um; concern statement for electrical systems.",
 '35': None, '36': None,
 '37': "Anchor on SAME-R report PDF p5 (also reproduced in Appendix F p79 and NTRS 20130000422 p8). Paraphrase faithful; 'will require' multi-moment detection in source is rendered as 'suggesting', which is not overstated.",
 '38': "Anchor on PDF p5; +/-15% repeatability is in the Figure 6 caption on the same page.",
 '39': "p3 (67 runs, two reused samples) and p2 (66 test points, abstract and introduction) both confirmed.",
 '40': "Dates, MSG location and the three SAMER modifications confirmed on PDF p2; 'reflew the same hardware' is on p3 ('utilized the SAME hardware already on orbit').",
 '41': None,
 '42': None,
 '43': "teflon_table1_check.json and external_checks.csv values confirmed; evaluation.md states no column-averaging explanation is documented.",
 '44': "Workbook formulas confirmed: 'Teflon R&T plots' BR28/BS28/BU28/BV28 = AVERAGE(rows 10,11,15,16) = runs 58/T03, 79/T04, 89/T08, 56/T02; values 0.100723/0.169574/2.198322/0.081475; 'ICES 2012 Paper data table' M9:P9 = ROUND(M25:P25,3) <- E12:I12. Each run satisfies the Hatch-Choate relations to < 1e-15 relative error; averaged Dg/sigma_g give 0.11111/0.20664 um.",
 '45': "Kapton BR41 = AVERAGE(BR12:BR15) = runs 61, 73, 92, 51 confirmed; their ISS AW 0.678, 0.437, 0.750, 0.418 V; Teflon runs 58, 79, 89, 56 at 0.188, 1.104, 0.966, 0.184 V; 51 and 61 share group-028.",
 '46': None,
 '47': "SAME-R report Table 1 parsed (Kapton rows p4, others p5); verifier recomputation: Teflon unaged count 0.12165/mass 0.20814 FAIL, Kapton unaged mass 0.10419 (interval 0.10303-0.10536 vs printed 0.106) FAIL, Silicone unaged mass 0.47053 (0.46873-0.47234 vs 0.468) FAIL, other 7 rows pass. 'AIAA 2012 Paper data table' K3:P12 hard-coded values confirmed.",
 '48': "Caption anchor on PDF p8 (Figures 6-7) and p9 (Figure 8). Discrepancy percentages recomputed: +9.4% count, +20.8% mass.",
 '49': None,
 '50': "STATUS.json known_limits[0], MODEL_CARD.md line 7 and domain.json target ('Recorded ISS scatter >=2 V, derived label; not reported real alarm or alarm timing') confirmed.",
 '51': "evaluation_followup.md table and STATUS.json followup values confirmed (0.891342/0.048823, 0.900433/0.056572, 0.870152/0.076360, 0.009091/0.020328, paired differences [0,0,0,0,0.045455]).",
 '52': "metrics.json per_material confirmed: Kapton recall 0.1111, confusion [[11,1],[8,1]], balanced accuracy 0.5139; Teflon recall 0.0, [[11,0],[4,0]], 0.5.",
 '53': "followup_metrics.json within_material pooled_oof confirmed: Kapton BA 0.5833, recall 0.3333, [[10,2],[6,3]], fold BA [0.375,1.0,0.35]; Teflon BA 0.7386, recall 0.75, one single-class fold.",
 '54': "domain.json ood_threshold 9.321957 and ood_definition confirmed; global resistance_ratio range [1.22,1.48]; ood_example.json: Kapton request accepted, predicted true, ood true, distance 10.029.",
 '55': "evaluation.md cross-campaign lines and metrics.json LOMO confirmed (0.6287, 0.8462, Kapton 0.4583, Teflon 0.4432).",
 '56': "evaluation.md Limits paragraph confirmed.",
 '57': "evaluation.md line 65 confirmed; domain.json also states uncertainty not estimated.",
 '58': "MODEL_CARD.md line 13 confirmed.",
 '59': "Verified in dashboard_table.csv: fan_problem/flat_profiles are 'n' for all SAME rows and blank for all SAME-R rows; 19 of the 23 below-2 V primary runs are SAME-R.",
 '09': None,
}

def item(n):
    return next(x for x in f['items'] if x['item_id'] == f'modelc_audit-{n}')

def confirm(n, note):
    item(n)['verification'] = {"verdict": "CONFIRMED", "note": note, "original": {}}

def correct(n, changes, note):
    it = item(n); orig = {}
    for k, v in changes.items():
        if k.startswith('conditions.'):
            ck = k.split('.', 1)[1]
            orig.setdefault('conditions', copy.deepcopy(it['conditions']))
            it['conditions'][ck] = v
        else:
            orig[k] = copy.deepcopy(it[k]); it[k] = v
    it['verification'] = {"verdict": "CORRECTED", "note": note, "original": orig}

for k, v in notes.items():
    if v is not None:
        confirm(k, v)

it = item('01')
correct('01', {'summary': it['summary'].replace("Only .gitattributes and release_checksums.json itself are on disk without an entry.",
    "Besides .gitattributes and release_checksums.json itself, the only on-disk files without an entry are Hugging Face client download bookkeeping files under .cache/huggingface/ (lock/metadata files and a tree listing), which are not snapshot content.")},
    "Verifier recomputed: 89 entries, 87 match, 0 mismatch, 2 notebooks absent. The claim that only two files lack an entry was wrong: the .cache/huggingface/ download-metadata tree (about 180 files) is also on disk without entries.")

it = item('09')
correct('09', {'summary': it['summary'].replace("Model C counts them as runs but assigns them to the same group as the earlier run, so Kapton has 21 runs in 19 groups and Lampwick 17 runs in 16 groups.",
    "Model C counts them as runs but assigns them to the same group as the earlier run. This gives Lampwick 17 runs in 16 groups. For Kapton the 85/90 reburn removes one group and the conservative 51/51a/61 sample linkage removes another, giving 21 runs in 19 groups.")},
    "Reburn facts, sample IDs (K08, L14), descriptions, source rows 121/60 and ISS values confirmed. Corrected the attribution: the reburn alone explains only one of the two Kapton group reductions (21 -> 19); the other comes from the 51/51a/61 linkage (group-028).")

it = item('19')
correct('19', {'summary': it['summary'].replace("Teflon at the baseline heating setpoint (Rt/R0 1.44-1.445; SAME 25, 26, 28, 41 and SAME-R 56, 58, 79, 89; airflow 2-8.1 cm/s)",
    "Teflon at Rt/R0 <= 1.445 (the 1.445 baseline setpoint, plus SAME runs 28 'Heat down' and 41 'low flow aging' at 1.44; SAME 25, 26, 28, 41 and SAME-R 56, 58, 79, 89; airflow 2-8.1 cm/s)")},
    "Counts recomputed (0/8 at Rt/R0 <= 1.445, max 1.6404 V; 4/7 at 1.448-1.4524, all SAME-R; 100, 105, 83 below). Wording corrected: Rt/R0 1.44 runs are not all 'baseline' (SAME 28 is described as 'Heat down').")

it = item('20')
correct('20', {'scope_notes': it['scope_notes'] + " Airflow is also confounded with heating setpoint: the four SAME-R low/no-flow Kapton runs that reached 2 V (101, 102, 108, 112) all used Rt/R0 1.48 (102 also 120 s heating), the exception 114 used Rt/R0 1.43, and at 8.1 cm/s with Rt/R0 1.48 SAME-R reached 2 V in 1 of 3 runs (62 yes; 70, 77 no)."},
    "Counts recomputed (5/6 at <= 2 cm/s; SAME-R 8.1 cm/s 1/12 in 10 groups; SAME 8.0 cm/s 2/2). Scope note extended with the Rt/R0 confound found in dashboard_table.csv.")

correct('21', {'conditions.heating_s': None},
    "Counts and voltages recomputed (11 no-flow primary runs, all SAME-R, 11 groups, all 11 s aging). heating_s 60 was not valid for the whole item: Kapton SAME-R:102 used 120 s heating; the other 10 runs used 60 s.")

it = item('24')
correct('24', {'summary': it['summary'].replace("ISS scatter values of Lampwick, Pyrell and Silicone cluster near 6.2-6.29 V;",
    "ISS scatter values of Lampwick, Pyrell and Silicone mostly cluster near 6.2-6.3 V (43 of 48 primary runs; the other five, Lampwick 57 and 96 and Pyrell 71, 95 and 97, read 4.82-6.12 V);")},
    "data_dictionary text confirmed. 'cluster near 6.2-6.29 V' overstated uniformity and the stated upper bound (max 6.2939 V); corrected with recomputed counts from dashboard_table.csv.")

it = item('32')
correct('32', {'summary': it['summary'].replace("about two thirds of the Teflon tests", "2/3 of the Teflon tests")},
    "Section 3.2 text confirmed. The source states '2/3 of the Teflon tests' without a hedge; the added 'about' was removed for fidelity. Missed-alarm framing (hypothetical, against the plotted boundary) is correct.")

correct('35', {'summary': "The ISS detector signal frequently saturated, mainly for the larger-particle smokes (silicone, Pyrell, lamp wick). Audit inference, not stated by Meyer et al.: this is consistent with the ~6.2-6.3 V plateau of these materials in the workbook, so only threshold exceedance of that channel should be used."},
    "Anchor confirmed in section 3.2. Summary rephrased so the link to the workbook voltage plateau is labelled as audit inference rather than part of the source statement.")

it = item('36')
correct('36', {'summary': it['summary'].replace("Model C therefore does not model the STS channel (it needs baseline offset and device-use flags).",
    "Separately, Model C does not model the STS channel; its artifacts/model_c/harmonization.json gives the reason as the STS channel requiring a baseline offset and device-use flags.")},
    "Section 3.2 text confirmed (intermittent operation, internal pump, three liters per minute, no aging tests). 'therefore' implied that Meyer's data-set size is Model C's reason; harmonization.json gives a different reason, so the causal link was removed.")

it = item('42')
correct('42', {'scope_notes': it['scope_notes'] + " The 4-run count and the 8.1 cm/s / 60 s / 11 s conditions come from the PSI workbook trace (item 44), not from the NTRS paper, which says only 'baseline runs' and prints the baseline air flow as 8 cm/s (PDF p7)."},
    "Document identity confirmed (PDF metadata title, NTRS API: AIAA Paper 2012-3536, 42nd ICES, San Diego, 15-19 July 2012, 10 authors). Table 1 unaged Teflon row confirmed on PDF p7; verifier recomputation gives count 0.110450, mass 0.205367, bounds 0.109749-0.111152 and 0.203989-0.206745, implied sigma_g 2.05768 and Dg 0.07785; other 9 rows pass. Scope note added on where n_independent_tests and conditions come from.")

it = item('49')
correct('49', {'summary': it['summary'].replace("AIAA paper, year not printed in the text)", "AIAA conference paper; the year is not printed in the extracted text, but the NTRS record gives publication date 2009-01-05 and an AIAA meeting ending 2009-01-08, report number E-18270)")},
    "Anchor on PDF p4 confirmed (P-Trak 0 to 10^5 particles/cm3 and 20 nm-1 um; DustTrak 0.001-100 mg/m3; only 'saturated' wording in the paper is the P-Trak isopropanol vapour). Year identified from the NTRS citation API (ntrs.nasa.gov/api/citations/20120012884).")


correct('41', {'category': 'measurement_limitation'},
    "Anchor on SAME-R report PDF p2 confirmed; paraphrase faithful. Category changed from model_limitation to measurement_limitation because the statement is a NASA report finding about the experiment's heating-control metric (Rt/R0 vs sample temperature); its consequence for Model C is already carried by item 56 (evaluation.md Limits).")
correct('46', {'n_independent_tests': None},
    "Formulas confirmed: Teflon BR29 =BR25 (58a), Kapton BR42 =BR37 (61a), Lampwick BR32 =BR27 (32a), Pyrell BR27 =BR21 (63a), Silicone BR35 =AVERAGE(BR26,BR28) (23a, 59a). aging_s 720 follows the Table 1 label 'Aged 720 s'; the workbook net-aging column for these secondary records reads 805-893 s. n_independent_tests 1 was not meaningful for an item covering five materials whose aged rows are secondary readings of six parent runs; set to null.")

# ---------------- documents ----------------
for doc in f['documents']:
    doc['verification'] = {"verdict": "CONFIRMED", "note": "sha256 of local_path recomputed by verifier and matches.", "original": {}}
for doc in f['documents']:
    if doc['doc_id'] in ('modelc-ntrs20130000422', 'modelc-ntrs20120012884', 'modelc-psi102-same-final-report', 'modelc-psi101-samer-final-report'):
        doc['verification']['note'] += " Plain pdftotext re-run by verifier is byte-identical to text_path; title/authors/date checked against the title page."
    if doc['doc_id'] == 'modelc-pmc7918997':
        doc['verification']['note'] += " Author block, PMCID and 'Fire Saf J. 2018;98' citation checked in the HTML text."
    if doc['doc_id'] == 'modelc-ntrs20120012884':
        doc['verification'] = {"verdict": "CORRECTED", "note": "sha256 and text confirmed. Year was null; NTRS citation API gives publicationDate 2009-01-05, an AIAA meeting ending 2009-01-08 and report number E-18270 (consistent with the PDF metadata title 'SAME AIAA paper Jan 2009'). Authors match NTRS. meta.json in sources/raw was left unchanged.", "original": {"year": doc['year']}}
        doc['year'] = 2009
    if doc['doc_id'] == 'detector_fig9.jpg':
        doc['verification']['note'] += " Verifier viewed the image: ISS boundary on the 2.0 V gridline, STS boundary slightly above 0.4 V."

# ---------------- added items ----------------
def add(n, **kw):
    base = {"item_id": f"modelc_audit-{n}", "pdf_page": None, "printed_page": None, "investigation": None, "materials": [], "detector": None,
            "numbers": [], "conditions": dict(NULLCOND), "n_independent_tests": None, "added_by_verifier": True}
    base.update(kw)
    base['verification'] = {"verdict": "CONFIRMED", "note": "Added by verifier; anchor checked on the cited page/location.", "original": {}}
    f['items'].append(base)

add(60, doc_id='modelc-pmc7918997', location='Abstract',
    anchor_quote='The two spacecraft smoke detectors did not successfully detect every type of smoke',
    summary="Meyer et al. state in the abstract that neither of the two spacecraft smoke detectors flown in the ISS experiment (ISS and Space Shuttle designs) detected every type of smoke, and conclude that the next generation of spacecraft fire detectors must be improved and tested against smoke from relevant space materials.",
    category='missed_alarm', investigation='SAME;SAME-R', detector='ISS smoke detector; Space Shuttle smoke detector',
    conditions=dict(NULLCOND, gravity=FLIGHT),
    scope_notes="Per section 3.2 the non-detections are judged against the plotted Figure 9 alarm boundaries (ISS: Kapton, Teflon; Shuttle: Kapton, Teflon, lamp wick), not observed alarm events; overheated-material smoke, not flaming fires.")
add(61, doc_id='modelc-pmc7918997', location='Abstract',
    anchor_quote='not significantly different from smoke particles generated in equivalent experiments performed in normal gravity',
    summary="Meyer et al. report that smoke particles from the ISS experiment vary in morphology and average diameter between materials but are not significantly different from particles produced in equivalent normal-gravity experiments; the conclusions add that ground tests at 8.1 cm/s gave particle dimensions very close to the flight results.",
    category='particle_property', investigation='SAME;SAME-R', conditions=dict(NULLCOND, gravity=FLIGHT),
    numbers=[{"value": 8.1, "unit": "cm/s", "meaning": "ground-test air flow at which dimensions matched flight", "verbatim": "8.1 cm/s"}],
    scope_notes="Applies to flow conditions of at least 8.1 cm/s per the conclusions; zero-flow smoke was larger. Differs from the earlier SAME Appendix E conclusion (item 67) that low-g count mean diameters were typically about 50% larger than 1-g.")
add(62, doc_id='modelc-pmc7918997', location='Section 4.0 Conclusions (last point)',
    anchor_quote='improbable that a single-moment device can be sensitive across the smoke particle size spectrum',
    summary="Because spacecraft fire scenarios involve a wider array of materials and heating conditions than tested, and spacecraft background aerosols can be quite large, Meyer et al. judge it improbable that a single-moment detector can be sensitive across the smoke particle size range while also resisting false alarms. The same conclusions note that the light-scattering ISS detector showed reduced performance for the smaller Kapton and Teflon smoke and the ionization Shuttle detector fared slightly better for Teflon.",
    category='technology_need', investigation='SAME;SAME-R', materials=['Kapton', 'Teflon'], detector='single-moment smoke detectors (general); ISS smoke detector; Space Shuttle smoke detector',
    conditions=dict(NULLCOND, gravity=FLIGHT),
    scope_notes="Authors' judgement linking missed-alarm risk (small particles) and false-alarm risk (large background dust); no false-alarm test was performed in SAME.")
add(63, doc_id='modelc-pmc7918997', location='Section 3.0 Results and Discussion (first paragraph)',
    anchor_quote='Over 100 samples were tested, comprised of 6 materials commonly used in the spacecraft cabin.',
    summary="Test matrix per Meyer et al.: over 100 samples of 6 materials (Teflon, Pyrell, lamp wick, Kapton, silicone rubber and DBP on a porous wick); baseline air flow 8.1 cm/s, runs down to 2 cm/s and a limited no-flow set; baseline temperatures chosen to give 1 to 2 mg mass loss in 60 s of heating; typical particle concentrations a few million per cm3 and 2 to 15 mg/m3, with some runs lower.",
    category='test_condition', investigation='SAME;SAME-R', materials=['Teflon', 'Pyrell', 'Lampwick', 'Kapton', 'Silicone', 'DBP'],
    numbers=[{"value": 100, "unit": "samples", "meaning": "lower bound on samples tested", "verbatim": "Over 100"},
             {"value": 8.1, "unit": "cm/s", "meaning": "baseline air flow", "verbatim": "8.1 cm/s"},
             {"value": 2, "unit": "cm/s", "meaning": "lowest non-zero air flow", "verbatim": "2 cm/s"},
             {"value": 60, "unit": "s", "meaning": "heating time used to select baseline temperature", "verbatim": "60 sec"},
             {"value": 2, "unit": "mg/m3", "meaning": "typical mass concentration, lower end", "verbatim": "2 to 15 mg/m3"},
             {"value": 15, "unit": "mg/m3", "meaning": "typical mass concentration, upper end", "verbatim": "2 to 15 mg/m3"}],
    conditions=dict(NULLCOND, gravity=FLIGHT),
    scope_notes="'Over 100 samples' includes DBP and both campaigns; Model C's 84 primary runs exclude DBP, ground tests and secondary readings, so the counts are not directly comparable.")
add(64, doc_id='modelc-psi102-same-final-report', pdf_page=12, printed_page='2', location='Background, ISS Detectors paragraph',
    anchor_quote='The sensitivity extends down to 0.3 μm but is greatest for particles larger than 1',
    summary="The SAME report describes the ISS smoke detectors as laser-diode forward-scattering (30 degree) detectors whose sensitivity reaches down to 0.3 um but is greatest for particles larger than 1 um, and which are less sensitive to particles smaller than the near-IR laser wavelength. The design choice was supported by data that early smoldering fires produce larger particulate than established flaming fires.",
    category='particle_property', investigation='SAME', detector='ISS smoke detector (laser-diode forward scattering)',
    numbers=[{"value": 0.3, "unit": "um", "meaning": "lower limit of ISS detector sensitivity (minimum reported sensitivity)", "verbatim": "0.3 μm"},
             {"value": 1, "unit": "um", "meaning": "size above which sensitivity is greatest", "verbatim": "1 μm"}],
    scope_notes="Design description, not a flight measurement; explains the reduced response to small Kapton/Teflon smoke reported in Meyer et al. 2018.")
add(65, doc_id='modelc-psi102-same-final-report', pdf_page=12, printed_page='2', location='Background, ISS Detectors paragraph',
    anchor_quote='The system is designed to alarm based on the magnitude of the scattered light signal',
    summary="The ISS detector's alarm logic uses the magnitude of the scattered-light signal referenced to the beam intensity, which a separate light-transmission sensor monitors. Within the examined sources, no document states how this referenced alarm signal relates to the workbook channel 'ISS Detector Scatter (volts)' on which Model C's 2.0 V label is computed.",
    category='measurement_limitation', investigation='SAME', detector='ISS smoke detector',
    scope_notes="The second sentence is an audit observation about an evidence gap, not a claim that the 2.0 V label is wrong; the 2.0 V level itself comes from Meyer et al. 2018 Figure 9.")
add(66, doc_id='modelc-psi102-same-final-report', pdf_page=66, printed_page='E-8', location='Appendix E, Figures 7-9 captions and IV. Conclusion (model setup on PDF p65)',
    anchor_quote='predicted that actual detection times can be quite long and strongly dependent on location',
    summary="In an FDS (CFD) smoke-transport model of the ISS US Lab with zero gravity, a propane-burner smoke source at three soot yields (1.46, 2.95 and 8.47 mg/s smoke output) and an assumed ISS alarm point of about 0.5 mg/m3, detection times were predicted to be quite long and strongly dependent on source location and obstructions. At the lowest soot yield (0.05) several source locations gave a 'did not alarm' (DNA) condition for one or both modelled area detectors (LAS5RR, LAP1RR).",
    category='missed_alarm', investigation=None, detector='ISS area smoke detectors (modelled)',
    numbers=[{"value": 0.05, "unit": "soot yield", "meaning": "lowest soot yield, at which DNA conditions occurred", "verbatim": "0.05"},
             {"value": 0.5, "unit": "mg/m3", "meaning": "approximate ISS detector alarm point used in the model", "verbatim": "0.5 mg/m3"},
             {"value": 1.46, "unit": "mg/s", "meaning": "lowest modelled smoke output", "verbatim": "1.46"}],
    conditions=dict(NULLCOND, gravity="zero gravity (numerical model)"),
    scope_notes="Computational simulation in a conference paper appended to the SAME report, not a flight or ground experiment; DNA is a simulated missed alarm for a given location/yield.")
add(67, doc_id='modelc-psi102-same-final-report', pdf_page=66, printed_page='E-8', location='Appendix E, IV. Conclusion',
    anchor_quote='typically 50% large in count mean diameter than similar conditions in normal gravity',
    summary="The Appendix E paper (early SAME results from zeroth- and first-moment instruments only) concluded that low-gravity smoke had count mean diameters typically about 50% larger than comparable normal-gravity conditions, with all sizes below 300 nm, suggesting smoke could possibly be discriminated from spacecraft dust by detecting in the sub-micrometre range.",
    category='particle_property', investigation='SAME', materials=['Silicone', 'Teflon', 'Lampwick', 'Kapton'],
    numbers=[{"value": 50, "unit": "%", "meaning": "typical increase of low-g count mean diameter over 1-g", "verbatim": "50%"},
             {"value": 300, "unit": "nm", "meaning": "upper bound of resulting sizes", "verbatim": "300 nm"}],
    conditions=dict(NULLCOND, gravity=FLIGHT),
    scope_notes="Preliminary SAME-1 analysis (PDF p64 says only zeroth/first moment results were presented); later Meyer et al. 2018 reports flight particles not significantly different from equivalent 1-g experiments (item 61). The conflict is unresolved within the examined sources.")
add(68, doc_id='modelc-psi102-same-final-report', pdf_page=40, printed_page='B-6', location='Appendix B, Detector Design Requirement Implications',
    anchor_quote='Consequently a specification for a single particle size (or no size specification) would be risky.',
    summary="Comparing detector technologies against one hypothetical alarm-requirement aerosol, the authors find that a single-moment detector may be too sensitive (for example to dust) or not sensitive enough depending on particle size, so a single-size (or no-size) alarm specification would be risky; they note this is essentially the case for the current ISS and STS detectors, which are tuned to different size ranges. They suggest alarm requirements with criteria spanning the expected fire particulate sizes (e.g. 200 to 1200 nm) and detectors combining two moment measurements, which might also help reduce false alarms.",
    category='recommendation', investigation='SAME', detector='ISS smoke detector; STS smoke detector; two-moment detectors (proposed)',
    numbers=[{"value": 200, "unit": "nm", "meaning": "lower end of suggested size range for alarm criteria", "verbatim": "200 to 1200 nm"},
             {"value": 1200, "unit": "nm", "meaning": "upper end of suggested size range for alarm criteria", "verbatim": "200 to 1200 nm"}],
    scope_notes="Design-requirement reasoning based on calculated detector responses (Figs. 3-4), not on observed alarms.")
add(69, doc_id='modelc-psi102-same-final-report', pdf_page=39, printed_page='B-5', location='Appendix B, Experimental Results and Figure 3 caption',
    anchor_quote='assuming the alarm level was set at 2 mg/m3 for 500 nm GMD',
    summary="In Appendix B the '2 mg/m3' alarm level is a hypothetical single-point alarm-requirement aerosol (2 mg/m3 mass concentration, lognormal with 500 nm geometric mean diameter and GSD 1.3) used to compute the alarm number and mass concentrations of four detector technologies as a function of particle size. It is a mass concentration and is unrelated to the 2.0 V ISS scatter-voltage level used for Model C's label.",
    category='definition', investigation='SAME',
    numbers=[{"value": 2, "unit": "mg/m3", "meaning": "hypothetical alarm-requirement mass concentration", "verbatim": "2 mg/m3"},
             {"value": 500, "unit": "nm", "meaning": "GMD of the alarm-requirement aerosol", "verbatim": "500 nm"},
             {"value": 1.3, "unit": "1", "meaning": "GSD of the alarm-requirement aerosol", "verbatim": "1.3"}],
    scope_notes="Prevents conflating the '2' in 2 mg/m3 (here and the STS design criterion on PDF p12) with the 2.0 V boundary of Meyer et al. 2018 Figure 9(b).")
add(70, doc_id='modelc-ntrs20130000422', pdf_page=12, printed_page='12', location='III. Conclusions',
    anchor_quote='detection methods that can measure more than one moment of the size distribution may show',
    summary="SAME-2 conclusions: under SAME conditions all samples produced significant numbers of sub-micron particles that an ionization detector readily detects; aging suggests some materials (e.g. silicone rubber) produce smoke large enough to be better detected by light scattering; zero-flow particles were 2 to 3 times larger than at the nominal 8 cm/s; broad size distributions are expected from credible pre-fire overheat events. The authors suggest that detectors measuring more than one moment may show more successful detection and false-alarm rejection than single-moment detectors, and call the prototype 2-moment MPASS results very encouraging.",
    category='recommendation', investigation='SAME-R', materials=['Silicone'], detector='multi-moment detection; MPASS prototype two-moment detector; ionization detector',
    numbers=[{"value": 2, "unit": "x", "meaning": "zero-flow particle size relative to 8 cm/s, lower end", "verbatim": "2 to 3 times larger"},
             {"value": 3, "unit": "x", "meaning": "zero-flow particle size relative to 8 cm/s, upper end", "verbatim": "2 to 3 times larger"}],
    conditions=dict(NULLCOND, gravity=FLIGHT),
    scope_notes="Hedged ('may show'); MPASS evaluated by correlation against the other SAME instruments, not in a false-alarm test. Meyer et al. 2018 conclusions instead give zero-flow particles as on average double the 8.1 cm/s size.")
add(71, doc_id='modelc-ntrs20130000422', pdf_page=1, printed_page=None, location='Abstract',
    anchor_quote='holding the smoke in the aging chamber for times ranging from 11 to 1800 s',
    summary="SAME-2 varied the effective smoke transport time by holding smoke in the aging chamber for 11 to 1800 s, with air flow past the sample from quiescent to 8 cm/s. In the Model C data, primary runs cover programmed primary aging of 1-720 s only; longer aging appears only in secondary 'a' records (dashboard_table.csv net_aging_s up to about 1964 s, e.g. SAME:46a with 1800 s programmed aging), which Model C excludes from its counts and labels.",
    category='test_condition', investigation='SAME;SAME-R',
    numbers=[{"value": 11, "unit": "s", "meaning": "shortest aging (hold) time", "verbatim": "11"},
             {"value": 1800, "unit": "s", "meaning": "longest aging (hold) time", "verbatim": "1800 s"}],
    conditions=dict(NULLCOND, gravity=FLIGHT),
    scope_notes="Long transport/aging times are therefore outside Model C's measured-only dashboard; the secondary readings share the heating event with their parent run and are not independent tests.")
add(72, doc_id='domain.json', location='external/model_c/artifacts/model_c/domain.json key assumptions (and key calibration)',
    anchor_quote='Common ISS scatter voltage channel and alarm reference across source-combined campaigns',
    summary="Model C assumes that the ISS scatter-voltage channel and the 2 V alarm reference are common across SAME and SAME-R in the author-combined workbook, applies no raw-signal calibration, and treats signals above 2 V (including saturated ones) only as threshold exceedance.",
    category='model_limitation', investigation='SAME;SAME-R', detector='ISS smoke detector (scatter channel)',
    scope_notes="Within the examined files this cross-campaign assumption is not tested; the large Kapton difference between SAME and SAME-R at nominally similar settings (item 18) is one reason to treat it with caution.")
add(73, doc_id='modelc-pmc7918997', location='Section 1.1 Spacecraft Fire Detector Background',
    anchor_quote='were limited to line-of-sight and were reported to have difficulties with false alarms',
    summary="Historical context in Meyer et al.: Skylab used about 30 UV-sensing fire detectors that were limited to line of sight and reportedly had false-alarm difficulties; Shuttle detectors used ionization with an inertial separator removing particles larger than 1 to 2 um; ISS detectors use near-IR forward light scattering, more sensitive to particles larger than 0.3 um.",
    category='false_alarm', investigation=None, detector='Skylab UV-sensing fire detectors; Space Shuttle ionization detector; ISS near-IR forward-scattering detector',
    numbers=[{"value": 30, "unit": "detectors", "meaning": "approximate number of Skylab UV detectors", "verbatim": "approximately 30"},
             {"value": 0.3, "unit": "um", "meaning": "size above which ISS detector is more sensitive", "verbatim": "0.3 μm"}],
    scope_notes="Secondhand (cites Friedman [6]); no false-alarm counts or test data given; not a SAME result.")

# ---------------- search log / open questions ----------------
f['search_log'].extend([
 {"query": "verifier: sha256 of all entries in release_checksums.json, artifacts/model_c/checksums.json, source_manifest.json, STATUS.json protected hashes; on-disk files without entry", "where": "external/model_c (python -I hashlib)", "hits": 107, "notes": "87/6/7/7 match, 0 mismatch, 2 notebooks absent; .cache/huggingface bookkeeping files also lack entries."},
 {"query": "verifier: openpyxl header-text lookup in 'Combined Rslts Copy this sheet'; per-material primary counts; full 134-row comparison; own random sample seed 4242", "where": "PSI-101 workbook + dashboard_table.csv", "hits": 134, "notes": "All match Model C; 12/12 own sample match."},
 {"query": "verifier: regex (2(.0)? V|volt|alarm|threshold|saturat|obscuration) over every page", "where": "sources/text/modelc-psi102-same-final-report.txt, modelc-psi101-samer-final-report.txt", "hits": 90, "notes": "No ISS scatter-voltage alarm threshold; found ISS alarm logic (p12), 2 mg/m3 hypothetical alarm aerosol (p39-40), FDS DNA results (p66)."},
 {"query": "verifier: Hatch-Choate recomputation of all 20 rows of both Table 1 versions", "where": "NTRS 20130000422 p7 and SAME-R report p4-5", "hits": 20, "notes": "NTRS: only unaged Teflon fails; SAME-R: unaged Teflon, unaged Kapton mass, unaged Silicone mass fail."},
 {"query": "verifier: NTRS citation API for 20120012884 and 20130000422", "where": "https://ntrs.nasa.gov/api/citations/<id>", "hits": 2, "notes": "20120012884 publicationDate 2009-01-05 (E-18270); 20130000422 AIAA Paper 2012-3536, 42nd ICES."},
])
f['open_questions'].extend([
 "Does the workbook column 'ISS Detector Scatter (volts)' carry the raw scatter signal or the scatter signal referenced to beam intensity that the ISS alarm logic uses (SAME report p12)? Not stated within the examined sources.",
 "Low-g vs 1-g particle size: SAME report Appendix E (p66) says count mean diameters were typically about 50% larger in low-g, whereas Meyer et al. 2018 (abstract) says they were not significantly different from equivalent 1-g experiments. Which applies to which runs/instruments?",
 "Zero-flow size ratio: NTRS 20130000422 (p12) says 2 to 3 times larger than at 8 cm/s; Meyer et al. 2018 conclusions say on average double. Which runs and size measure underlie each figure?",
 "Meyer et al. report 'over 100 samples' of 6 materials; how does this map to Model C's 84 primary flight runs of 5 materials plus DBP, ground and secondary records?",
])
json.dump(f, open(OUT, 'w'), indent=1, ensure_ascii=False)
print('written', OUT, len(f['items']))
