"""Build sources/extracted/same_profiles.json (items + validation of anchor quotes).
Run: .venv/bin/python -I build_items.py
"""
import json, re, sys

ROOT = "/home/efeai/Desktop/NasaSpaceApps"
SP = "/tmp/claude-1000/-home-efeai-Desktop-NasaSpaceApps/6a4d6a96-8583-4b8d-bd50-35dfffa09cc3/scratchpad/same_profiles"
KEY = "same_profiles"

items = []


def C(o2=None, p=None, flow=None, g=None, heat=None, age=None):
    return {"atmosphere_o2_vol_pct": o2, "pressure_kpa": p, "airflow_cm_s": flow, "gravity": g, "heating_s": heat, "aging_s": age}


def N(value, unit, meaning, verbatim):
    return {"value": value, "unit": unit, "meaning": meaning, "verbatim": verbatim}


def add(doc, page, loc, anchor, summary, cat, inv=None, mats=None, det=None, nums=None, cond=None, n=None, scope="", printed=None):
    items.append({
        "item_id": f"{KEY}-{len(items)+1:03d}", "doc_id": doc, "pdf_page": page, "printed_page": printed,
        "location": loc, "anchor_quote": anchor, "summary": summary, "category": cat,
        "investigation": inv, "materials": mats or [], "detector": det, "numbers": nums or [],
        "conditions": cond or C(), "n_independent_tests": n, "scope_notes": scope})


UG = "microgravity (ISS, low Earth orbit)"
G1 = "1-g (ground)"
S, SR = "SAME", "SAME-R"
M4 = ["Teflon", "Kapton", "silicone rubber", "lamp wick (cellulose)"]
M5R = ["Teflon", "Kapton", "silicone rubber", "lamp wick (cellulose)", "Pyrell"]
ATM_NOTE = "Test atmosphere O2 concentration and pressure are NOT stated in this document (null, not inferred)."

# =====================================================================
# CHECKSUMS
# =====================================================================
add("same_report", 1, "Cover page; file checksum vs external/model_c/data/raw/source_manifest.json",
    "Smoke Aerosol Measurement Experiment (SAME)",
    "The SAME final report PDF used here (3,712,845 bytes) has sha256 af91c96d22d93bbefbc0f2c5e1cc06e24813f532e5379b3fec9f121cccb22193, identical to the value recorded in the Model C source manifest.",
    "checksum", S, nums=[N(3712845, "bytes", "file size", "3712845")],
    scope="Integrity check only. Also verified: PSI-101 combined workbook sha256 6d3a539c... matches manifest (workbook itself not extracted in this group).")
add("samer_report", 1, "Cover page; file checksum vs source_manifest.json",
    "Smoke Aerosol Measurement Experiment Re-flight (SAMER)",
    "The SAME-R final report PDF (4,578,437 bytes) has sha256 65381e2715eb7379113dd1b9c550baaa5fa5a247dba00419123143aa98ef80d6, identical to the Model C manifest value.",
    "checksum", SR, nums=[N(4578437, "bytes", "file size", "4578437")], scope="Integrity check only.")
add("psi102_meta", None, "$.accession; file checksum vs source_manifest.json", "$.accession = PSI-102",
    "PSI-102 metadata JSON (135,432 bytes) sha256 fe221f1380ad3317f70b559a3213c4e00ef3676b40838a49cb5b3cba89dea5ba matches the Model C manifest.",
    "checksum", S, nums=[N(135432, "bytes", "file size", "135432")], scope="Integrity check only.")
add("psi101_meta", None, "$.accession; file checksum vs source_manifest.json", "$.accession = PSI-101",
    "PSI-101 metadata JSON (552,733 bytes) sha256 e0aa75d015705a5943b51dbb4a8ba52751a35e4cafc2307d9201d77ebed711a5 matches the Model C manifest.",
    "checksum", SR, nums=[N(552733, "bytes", "file size", "552733")], scope="Integrity check only.")
add("same_csv", None, "PSI-102_Experimental table_SAME.csv, header row; checksum", "Sample #,Sample Material  ,Air Flow (cm/s),Weight loss rate (mg/min),Aging Duration (minutes)",
    "SAME experimental-table CSV (331 bytes) sha256 268d1e121d2f211b124407dd32b9475617bd269ede2c2d1749441da3e949a2af matches the Model C manifest.",
    "checksum", S, nums=[N(331, "bytes", "file size", "331")], scope="Integrity check only.")
add("samer_csv", None, "PSI-101_Experimental table_SAME-R.csv, header row; checksum", "Sample Type,SAME Test #,Description,Date,Inlet velocity (cm/s),Rt/R0,Duration (sec)",
    "SAME-R experimental-table CSV (5,674 bytes) sha256 87164b7dc9168a4273c159f7a9f23699afbd06ad97b77974377e79b9bf8a3bef matches the Model C manifest.",
    "checksum", SR, nums=[N(5674, "bytes", "file size", "5674")], scope="Integrity check only.")

# =====================================================================
# SAME PROFILE (same_report)
# =====================================================================
add("same_report", 11, "Section 1 Introduction", "The objective of this work was to make sufficient measurements of smoke from spacecraft fires",
    "Stated SAME objective: obtain enough measurements of smoke from spacecraft-type fire sources to enable better design of future spacecraft smoke detectors.",
    "investigation_profile", S, printed="1", scope="Objective statement; repeated in appended papers.")
add("psi102_meta", None, "$.objective", "quantify the sizes that the liquid smoke particulate achieves in low gravity",
    "PSI metadata objective for SAME: quantify the size reached by liquid smoke particulate in low gravity and relate the droplet size distribution to smoke generation and transport conditions; a numerical code for droplet growth was also planned.",
    "investigation_profile", S, scope="Repository metadata wording; the final report does not describe a completed droplet-growth code (within the examined text).")
add("psi102_meta", None, "$.hypothesis", "possibly result in some detectors not producing an alarm when exposed to this smoke",
    "Motivating hypothesis (metadata): without buoyancy, smoke particles from pyrolyzing/smoldering sources grow larger than in 1 g (esp. liquid droplets), and the changed size distribution/number density could affect detector response and possibly cause some detectors not to alarm.",
    "research_question", S, scope="This is a HYPOTHESIS stated as motivation, not an observed missed alarm.")
add("same_report", 3, "Abstract", "conducted in the Microgravity Science Glovebox (MSG) on the International Space Station (ISS)",
    "Platform: SAME ran inside the Microgravity Science Glovebox (MSG) on the ISS, characterizing size distributions of smoke from overheated spacecraft materials in low gravity.",
    "investigation_profile", S, cond=C(g=UG), printed="iii", scope=ATM_NOTE)
add("same_report", 3, "Abstract", "The SAME experiments were conducted during Expedition 15 on the ISS.",
    "SAME flight operations took place during ISS Expedition 15.", "investigation_profile", S, cond=C(g=UG), printed="iii")
add("same_report", 24, "Section 4 Flight Tests", "The SAME tests were performed on board ISS in September and early October of 2007",
    "Flight test dates: September to early October 2007 aboard ISS (the SAME-R report gives September 9 - October 5, 2007; Appendix A GMT days 252-278 are consistent with that).",
    "investigation_profile", S, cond=C(g=UG), printed="14")
add("same_report", 3, "Abstract", "samples were heated to temperatures below the ignition point",
    "To simulate a pre-fire overheat event, samples were heated below their ignition point (non-flaming pyrolysis), with controlled, repeatable sample surface temperature and air flow.",
    "test_condition", S, mats=M4 + ["DBP reference"], cond=C(g=UG), printed="iii",
    scope="Applies to non-flaming overheat/pyrolysis smoke only; no flaming tests in SAME.")
add("same_report", 3, "Abstract", "aging chamber for times ranging from 10 seconds to 1800 seconds",
    "Transport time from source to detector was emulated by holding smoke in an aging chamber for 10 to 1800 s.",
    "test_condition", S, nums=[N(10, "s", "minimum aging time", "10 seconds"), N(1800, "s", "maximum aging time", "1800 seconds")],
    cond=C(g=UG), printed="iii", scope="Aging range across the campaign; Table 1 reports only unaged and 720 s aged cases.")
add("same_report", 3, "Abstract", "Four materials, typical of those found in spacecraft, were tested including cellulose (lamp wick), Kapton,",
    "Materials: cellulose (lamp wick), Kapton, silicone rubber and Teflon, plus dibutyl phthalate (DBP) held in a cotton wick as a reference material.",
    "investigation_profile", S, mats=M4 + ["dibutyl phthalate (DBP) reference"], printed="iii")
add("same_report", 20, "Section 3.B Instrumentation", "wrapped around an approximately 3 mm diameter cylinder of the sample material",
    "Heating method: a steel wire wrapped around an approximately 3 mm diameter cylinder of sample was resistively heated; wire resistance was monitored to control its temperature.",
    "test_condition", S, nums=[N(3, "mm", "approximate sample cylinder diameter", "approximately 3 mm")], printed="10",
    scope="SAME report gives no sample temperatures in degC; heating set via wire resistance (Rt/R0 only appears in Appendix A comment for test 8).")
add("same_report", 21, "Section 3.B (p.11)", "sample heating time is approximately 60 seconds",
    "Nominal heating interval about 60 s, during which a moving piston in the aging chamber drew the smoke in under controlled flow.",
    "test_condition", S, nums=[N(60, "s", "approximate heating time", "approximately 60 seconds")], cond=C(g=UG, heat=60), printed="11",
    scope="Approximate; Appendix A notes one DBP test (44) with 75 s heating; Model C reports workbook heating durations 10-60 s for SAME primary rows.")
add("same_report", 21, "Section 3.B (p.11)", "designed to provide air flow rates ranging from 2 to 8 cm/s",
    "Flow design range over the sample: 2 to 8 cm/s.", "test_condition", S,
    nums=[N(2, "cm/s", "minimum design airflow", "2"), N(8, "cm/s", "maximum design airflow", "8 cm/s")], printed="11",
    scope="Design range; no quiescent (0 cm/s) runs in SAME (zero-flow was added in SAME-R).")
add("same_report", 21, "Section 3.B (p.11)", "tests were conducted at different sample temperatures, air flow rates, and smoke aging durations",
    "Variables varied in SAME: sample temperature, air flow rate and smoke aging duration (plus material). Items not described as varied: gas composition/pressure, heater type, sample geometry.",
    "test_condition", S, printed="11", scope=ATM_NOTE + " 'Held constant' list is what the report does not vary, not an explicit statement.")
add("same_report", 21, "Section 3.B (p.11)", "Also installed in the diagnostics duct were space shuttle and ISS smoke detectors.",
    "Spacecraft detectors: a Space Shuttle (STS) smoke detector and an ISS smoke detector sat in the diagnostics duct and their outputs were compared with the moment-method results.",
    "investigation_profile", S, det="ISS smoke detector; Space Shuttle (STS) smoke detector", printed="11")
add("same_report", 18, "Section 3.A.2 Implementation of the moment method", "the zeroth moment, M0, was measured using a condensation nuclei counter called the P-TrakTM",
    "Aerosol instruments: P-Trak condensation nuclei counter (M0, number), ionization chamber from a commercial smoke detector (approx. M1), DustTrak 90-degree red-laser photometer (approx. M3, mass); all compact enough for the MSG.",
    "investigation_profile", S, det="P-Trak (TSI); ionization chamber; DustTrak (TSI)", printed="8")
add("same_report", 20, "Section 3.B Instrumentation", "The difference in the signal from the two devices provided a measure of the fraction",
    "Two DustTraks were flown, one with a 1 um and one with a 10 um inlet impactor; their signal difference indicates the fraction of particulate larger than 1 um. Range 0.001-100 mg/m3; dilution needed in some cases.",
    "investigation_profile", S, det="DustTrak (TSI) x2",
    nums=[N(0.001, "mg/m3", "DustTrak lower range", "0.001 mg/m3"), N(100, "mg/m3", "DustTrak upper range", "100 mg /m3")], printed="10")
add("same_report", 19, "Section 3.B Instrumentation", "This instrument is very robust and operates over a range of 0 to 105 particles/cm3",
    "P-Trak range stated as 0 to 10^5 particles/cm3 and 20 nm to 1 um; SAME smoke was about 0.5-5 x10^6 particles/cm3 so dilution was required.",
    "measurement_limitation", S, det="P-Trak (TSI)",
    nums=[N(100000, "particles/cm3", "P-Trak upper count range (printed '105' = 10^5)", "0 to 105 particles/cm3")], printed="9",
    scope="Internal inconsistency: Appendix B (PDF p38) gives the P-Trak size range as 20 nm to 4-5 um and Appendix D (PDF p54) 20 nm to 5 um.")
add("same_report", 22, "Section 3.B (p.12), thermal precipitator", "examined in a TEM to obtain an independent determination of the particle size",
    "A thermal precipitator deposited a side stream of smoke on TEM grids (thermophoresis) for post-flight size/morphology analysis.",
    "investigation_profile", S, det="thermal precipitator / TEM grids", printed="12")
add("same_report", 25, "Section 5 Test Results", "digitized at 1 Hz by an 8 bit A/D converter",
    "All analog instrument signals (incl. ISS and STS detector voltages) were digitized at 1 Hz with an 8-bit A/D converter.",
    "measurement_limitation", S, det="all analog channels incl. ISS and STS detectors",
    nums=[N(1, "Hz", "sampling rate", "1 Hz"), N(8, "bit", "A/D resolution", "8 bit")], printed="15",
    scope="Limits time and amplitude resolution of detector traces; report does not quantify effect.")
add("same_report", 24, "Section 4 Flight Tests", "Overall 30 sample materials were tested.",
    "30 samples were flown: six each of Teflon, Kapton, silicone rubber, cellulose and DBP on a porous wick, tested at different airflow, pyrolysis temperature and aging.",
    "investigation_profile", S, mats=M4 + ["DBP"], nums=[N(30, "samples", "samples tested", "30")], n=30, printed="14",
    scope="30 physical samples = upper bound of independent heating events (24 excluding the DBP reference). Reheats are not independent.")
add("same_report", 33, "Appendix A Log of SAME flight tests (table)", "Appendix A Log of SAME flight tests",
    "Flight log lists 47 test numbers (GMT 252-278): 30 'Initial' heatings (6 per material) and 17 'Reheat' records (16 DBP, 1 Teflon). Comments note an abort on high Rt/Ro (test 8), 2 cm/s runs (33, 34), 8 cm/s (37) and one 30 min aging / 75 s heating DBP run (44).",
    "investigation_profile", S, mats=M4 + ["DBP"], nums=[N(47, "test points", "logged test numbers", "1-47"), N(17, "test points", "reheat records (counted by this agent from the log)", "Reheat")],
    n=30, printed="A-1", scope="Counts derived by this agent from the layout of the Appendix A table. Reheats re-use a sample and are not independent tests.")
add("same_report", 24, "Section 4 Flight Tests", "roughly a 50% greater number of test points (and data) than was originally planned",
    "Ground tele-operation from GRC allowed about 50% more test points than originally planned; hardware assembly took about 5 h of crew time.",
    "investigation_profile", S, nums=[N(50, "%", "extra test points vs plan (approximate)", "roughly a 50%"), N(5, "h", "crew time for assembly (approximate)", "approximately 5 hours")], printed="14")
add("same_csv", None, "PSI-102_Experimental table_SAME.csv rows 1-4 (Teflon) and 5-8", "5,Kapton: same conditions as 1-4,,,",
    "The SAME CSV is a planned-condition table: four Teflon rows (airflow 5 or 10 cm/s, weight-loss rate 1 or 2 mg/min, aging 1 or 20 min) and four rows stating Kapton, silicone rubber, lampwick and DBP use the same conditions as rows 1-4.",
    "test_condition", S, mats=["Teflon", "Kapton", "silicone rubber", "lampwick", "DBP"],
    nums=[N(5, "cm/s", "planned airflow", "5"), N(10, "cm/s", "planned airflow", "10"), N(1, "mg/min", "planned weight-loss rate", "1"), N(2, "mg/min", "planned weight-loss rate", "2"), N(1, "min", "planned aging", "1"), N(20, "min", "planned aging", "20")],
    scope="PLANNED settings, not executed runs. 10 cm/s exceeds the 2-8 cm/s design range in the final report. Model C described this as 'eight numbered Teflon configurations'; actually 4 Teflon rows + 4 'same conditions' rows.")

# Atmosphere / pressure / gravity statements (SAME)
add("same_report", 20, "Section 3.B (p.10)", "installed in the Microgravity Science Glovebox, an ISS facility that provides many resources",
    "TEST ATMOSPHERE: the report says only that the hardware was installed in the MSG (containment, power, data, video, commanding) and that smoke was carried by an 'air' stream; it gives no O2 concentration and no pressure for the test gas.",
    "test_condition", S, cond=C(g=UG), printed="10",
    scope=ATM_NOTE + " Implied only as air inside the MSG; no cabin-air numbers given. Keyword search of the full text found no 'kPa', 'psi', 'pressure', 'O2' or 'atmosphere'.")
add("same_report", 65, "Appendix E, Section III Smoke Transport Model", "Since the ISS is in low earth orbit, the gravitational acceleration was set to zero.",
    "In the companion FDS smoke-transport model of the ISS US Lab, gravity was set to zero (low Earth orbit).", "context", "SAME (FDS model)",
    cond=C(g="0 (model)"), printed="E-7", scope="Numerical model setting, not an experiment.")

# Detector definitions (SAME)
add("same_report", 12, "Section 2 Smoke Background, Space Shuttle Detectors", "designed to alarm at a particle loading of 2 mg/m3 for 5 seconds",
    "STS (Orbiter) ionization detector alarm design: 2 mg/m3 for 5 s (based on 1 um particles) or a rise of 0.022 mg/m3/s for 20 s.",
    "definition", "STS (background)", det="Space Shuttle (STS) ionization smoke detector",
    nums=[N(2, "mg/m3", "STS alarm particle loading", "2 mg/m3"), N(5, "s", "duration at loading", "5 seconds"), N(0.022, "mg/m3/s", "rate-of-rise alarm", "0.022 mg/m3/s"), N(20, "s", "rate-of-rise duration", "20 seconds")],
    printed="2", scope="Design specification from Steisslinger et al. as cited; not a SAME measurement.")
add("same_report", 12, "Section 2, Space Shuttle Detectors", "incipient fires could be discriminated by looking for particulate in the 0.4",
    "STS detector design rationale: incipient fires thought discriminable via 0.4-0.7 um particulate; a pump-driven separator rejected particles larger than 1 um (pump raised power and shortened life).",
    "definition", "STS (background)", det="Space Shuttle (STS) ionization smoke detector",
    nums=[N(0.4, "um", "design size band lower", "0.4"), N(0.7, "um", "design size band upper", "0.7"), N(1, "um", "separator cut", "1")], printed="2",
    scope="Appendices B/C instead say the inertial separator removed particles larger than 1-2 um.")
add("same_report", 12, "Section 2, ISS Detectors", "The ISS detector was designed to alarm at 1% obscuration per foot",
    "ISS detector alarm definition: designed to alarm at 1% obscuration per foot in a UL smoke box with white-light extinction, implemented by setting each unit's amplifiers with a transfer-standard detector and a 0.5 um polystyrene-bead aerosol.",
    "definition", "ISS (background)", det="ISS laser-diode forward-scattering smoke detector (Allied Signal/Honeywell)",
    nums=[N(1, "% obscuration per foot", "ISS alarm design point", "1% obscuration per foot"), N(0.5, "um", "polystyrene bead calibration aerosol", "0.5")], printed="2-3",
    scope="No alarm VOLTAGE is given anywhere in either final report (within examined text). The 2.0 V reference used by Model C comes from Meyer et al. 2018 Fig. 9, not from these reports.")
add("same_report", 12, "Section 2, ISS Detectors", "The system is less sensitive to particles smaller than the wavelength of the laser",
    "ISS detector: 2-pass near-IR laser diode, 30-degree forward scatter referenced to beam intensity; sensitivity reaches down to 0.3 um but is greatest above 1 um; less sensitive to particles smaller than the laser wavelength.",
    "definition", "ISS (background)", det="ISS laser-diode forward-scattering smoke detector",
    nums=[N(0.3, "um", "minimum reported sensitivity", "0.3"), N(30, "degrees", "forward scattering angle", "30 degrees"), N(1.5, "W", "ISS detector power", "1.5 Watts"), N(9, "W", "Orbiter detector power", "9 Watts")], printed="2",
    scope="Appendix E (PDF p60) instead says sensitivity extends down to 0.6 um (with 0.3 um as minimum reported) - internal inconsistency.")
add("same_report", 13, "Section 2 (p.3)", "the ISS and the Orbiter detectors have particle sensitivities that do not overlap",
    "Because they were designed without low-g smoke data, the ISS (scattering) and Orbiter (ionization) detectors have non-overlapping particle-size sensitivities.",
    "measurement_limitation", "STS/ISS (background)", det="ISS and STS smoke detectors", printed="3",
    scope="Design-level statement about the two operational detectors.")
add("same_report", 65, "Appendix E, Section III (FDS model)", "The alarm point for the ISS detector is on the order of 0.5 mg/m3.",
    "In the 2008 AIAA paper's ISS smoke-transport model, the ISS detector alarm point is described as on the order of 0.5 mg/m3.",
    "definition", "SAME (FDS model)", det="ISS smoke detector", nums=[N(0.5, "mg/m3", "approximate ISS alarm point used in model", "0.5 mg/m3")], printed="E-7",
    scope="Approximate value used in a numerical model; not a SAME-measured threshold and not a voltage.")

# SAME detector results
add("same_report", 25, "Section 5, Figure 11 discussion (Silicone Run 24, GMT 267)", "both the ISS detector and the STS detectors show strong signals",
    "For a typical silicone rubber run both the ISS and STS detectors gave strong signals, which the authors attribute to silicone smoke's larger diameter of average mass.",
    "context", S, mats=["silicone rubber"], det="ISS smoke detector; STS smoke detector", cond=C(g=UG), printed="15",
    scope="Single illustrated run; signal-level description, no alarm logic evaluated.")
add("same_report", 25, "Section 5, Figure 12 discussion (Teflon Test 25, GMT 268)", "whereas the signal from the ISS detector was more erratic",
    "For a typical Teflon run the STS (ionization) detector gave a strong signal while the ISS (scattering) detector signal was more erratic, because Teflon smoke is mostly below 1 um.",
    "missed_alarm", S, mats=["Teflon"], det="ISS smoke detector (weak/erratic); STS detector (strong)", cond=C(g=UG), printed="15",
    scope="Documented detection weakness of the ISS detector for Teflon smoke. The report does NOT state an alarm/no-alarm outcome - it describes an erratic signal. Not a false alarm.")
add("same_report", 25, "Section 5 (p.15)", "positive deflection of the ISS signal and a negative deflection on the STS signal",
    "Signal convention: smoke produces a positive deflection of the ISS detector signal and a negative deflection of the STS detector signal (both recorded in volts).",
    "definition", S, det="ISS and STS smoke detectors", printed="15", scope="Needed to interpret raw detector traces.")
add("same_report", 28, "Section 5 (p.18)", "detection by light scattering devices which was seen for some of the Teflon tests",
    "Kapton and Teflon smokes had narrow size distributions with little mass above 1 um, consistent with the less effective light-scattering detection seen in some Teflon tests and with the STS/ISS detector signals.",
    "missed_alarm", S, mats=["Teflon", "Kapton"], det="light-scattering devices incl. ISS smoke detector", cond=C(g=UG), printed="18",
    scope="'Some of the Teflon tests' - number not given. Signal-strength statement, not an alarm count.")
add("same_report", 28, "Section 5 (p.18)", "show strong signals on the Space Shuttle detector (ionization)",
    "All SAME tests gave strong signals on the Space Shuttle ionization detector, including the larger-particle lamp wick and silicone smokes.",
    "context", S, mats=M4, det="Space Shuttle (STS) ionization smoke detector", cond=C(g=UG), printed="18",
    scope="SAME conditions only; contrasts with CSD result below.")
add("same_report", 28, "Section 5 (p.18), citing CSD", "poor detection by the Space Shuttle detector for non-flaming overheat of cellulose and silicone rubber",
    "The earlier CSD experiment reported poor detection by the Space Shuttle detector for non-flaming overheat of cellulose and silicone rubber, which the authors read as larger particles; they infer some pre-fire conditions can give size distributions beyond those seen in SAME.",
    "missed_alarm", "CSD (cited in SAME report)", mats=["cellulose", "silicone rubber"], det="Space Shuttle (STS) ionization smoke detector", printed="18",
    scope="Secondhand citation of CSD (Space Shuttle glovebox), not a SAME measurement; 'poor detection' wording, no alarm counts.")
add("same_report", 28, "Section 5 (p.18)", "the smoke size distribution can extend to diameters beyond those seen in the SAME experiment",
    "Authors' inference: under some reasonable pre-fire conditions the smoke size distribution can reach larger diameters than any seen in SAME.",
    "research_question", S, printed="18", scope="Inference from CSD vs SAME comparison.")

# SAME particle properties
add("same_report", 27, "Table 1. Results of SAME flight tests", "Table 1. Results of SAME flight tests",
    "SAME Table 1 (moment instruments; baseline unaged vs 720 s aged): geometric mean / arithmetic mean / diameter of average mass (nm), sigma_g - Kapton 80/105/179/2.08, aged 155/186/267/1.82; lamp wick 186/227/341/1.89, aged 258/308/438/1.81; silicone 189/257/472/2.18, aged 352/422/606/1.83; Teflon 170/205/297/1.84, aged 228/273/392/1.82.",
    "particle_property", S, mats=M4,
    nums=[N(80, "nm", "Kapton unaged GMD", "80"), N(179, "nm", "Kapton unaged Dm", "179"), N(186, "nm", "lamp wick unaged GMD", "186"), N(341, "nm", "lamp wick unaged Dm", "341"),
          N(189, "nm", "silicone unaged GMD", "189"), N(472, "nm", "silicone unaged Dm", "472"), N(606, "nm", "silicone aged Dm", "606"), N(170, "nm", "Teflon unaged GMD", "170"), N(297, "nm", "Teflon unaged Dm", "297")],
    cond=C(g=UG, age=720), printed="17",
    scope="Baseline runs only; GMD and sigma_g assume lognormality. Values differ from the preliminary tables in Appendices C, D, E (see separate items).")
add("same_report", 4, "Abstract (p.iv)", "a substantial portion of the smoke particles are below 500 nm in diameter",
    "Headline result: for the tested materials a substantial fraction of smoke particles were below 500 nm in diameter.",
    "particle_property", S, mats=M4, nums=[N(500, "nm", "size below which a substantial portion lies", "500 nm")], cond=C(g=UG), printed="iv",
    scope="Tested materials and SAME conditions only.")
add("same_report", 27, "Section 5 (p.17)", "will make detection of this smoke challenging for light scattering devices",
    "Authors: the small Kapton and Teflon particle sizes make detection challenging for light-scattering devices, whereas large lamp wick/silicone particles would give very large scattering signals; detection against background therefore needs a system measuring more than one moment.",
    "missed_alarm", S, mats=["Kapton", "Teflon"], det="light-scattering detectors (ISS-type)", printed="17",
    scope="Inference from particle sizes, not from counted alarm failures. Missed-detection side only; large-particle side is a false-alarm/nuisance concern handled separately.")
add("same_report", 27, "Section 5 (p.17)", "for the aged silicone diameter of average mass",
    "Aging substantially increased average particle sizes; the main report says the aged silicone diameter of average mass rose to over 1 um.",
    "particle_property", S, mats=["silicone rubber"], cond=C(g=UG, age=720), printed="17",
    scope="INTERNAL INCONSISTENCY: Table 1 on the same page gives 606 nm for aged silicone Dm and Appendix B (PDF p39) says 'over 500 nm'. Treat the '>1 um' wording as unreliable.")
add("same_report", 27, "Section 5 (p.17-18)", "the aging can be considered to be representative of smoke emerging from a closed volume",
    "Authors treat aged smoke as representative of smoke leaving a closed volume such as an avionics enclosure, so fire sensors must also cover large particles, not only the small Kapton-type particles.",
    "technology_need", S, printed="17-18", scope="Interpretation of the aging chamber as an enclosure analogue.")
add("same_report", 28, "Section 5 (p.18)", "although the CMD for silicone rubber is 189 nm",
    "Mass vs count: although the silicone count mean diameter is quoted as 189 nm, almost half the particle mass is above 1 um (DustTrak ratio); lamp wick behaves similarly. Scattering signals scale with mass, so single statistics can mislead.",
    "particle_property", S, mats=["silicone rubber", "lamp wick"], nums=[N(189, "nm", "silicone CMD as quoted in text", "189 nm")], printed="18",
    scope="189 nm is the GEOMETRIC mean in Table 1 (arithmetic mean 257 nm) - wording inconsistency in source.")
add("same_report", 28, "Section 5 (p.18)", "unfortunately contaminated with extraneous particles",
    "SAME TEM grids returned from the thermal precipitators were contaminated with extraneous particles (believed from precipitator assembly); only lamp wick and Teflon gave distinct particles.",
    "measurement_limitation", S, det="thermal precipitator / TEM", printed="18",
    scope="SAME-R report (PDF p2) calls all SAME TEM grids severely contaminated and unusable.")
add("same_report", 24, "Section 3.C Instrument Calibration (p.14)", "valid as long as the size distribution of the sample does not change significantly",
    "DustTrak response was calibrated per smoke source against a TEOM mass measurement; authors note this is valid only while the sample size distribution does not change significantly. Mie-model uncertainties (refractive index, agglomerates, non-lognormality) remained to be assessed.",
    "measurement_limitation", S, det="DustTrak (TSI)", printed="14")
add("same_report", 19, "Section 3.A.3 Uncertainty Analysis", "whereas that of M1 contributes the most",
    "Uncertainty propagation: the M1 (ionization chamber) uncertainty contributes most to the uncertainty of Dg and sigma_g, M3 contributes least.",
    "measurement_limitation", S, det="ionization chamber (M1)", printed="9")
add("same_report", 48, "Appendix C (2009 AIAA paper), p.C-6", "The Silicone results did not converge for these conditions",
    "In the preliminary Mie-iteration analysis some cases did not converge (possibly bimodal distributions); silicone baseline values were N/A. Preliminary baseline values: Kapton 0.080/0.105/0.172 um, lamp wick 0.186/0.227/0.420 um, Teflon 0.159/0.205/0.219 um (GMD/AMD/Dm).",
    "measurement_limitation", S, mats=M4, printed="C-6",
    scope="Preliminary 2009 values superseded by final Table 1; shown to document method limits and value drift between publications.")
add("same_report", 56, "Appendix D (2008 ICES paper), p.D-6", "interpreting particle sizes by only one statistic can be deceptive",
    "Preliminary 2008 results: unaged count mean diameters all in the 100-200 nm range (Table 1: silicone 227 nm, Teflon 158, lamp wick 172, Kapton 128; DustTrak B/A ratio 1.92, 1.22, 1.79, 1.26); authors warn a single statistic can be deceptive.",
    "particle_property", S, mats=M4,
    nums=[N(227, "nm", "silicone CMD (prelim.)", "227"), N(158, "nm", "Teflon CMD (prelim.)", "158"), N(172, "nm", "lamp wick CMD (prelim.)", "172"), N(128, "nm", "Kapton CMD (prelim.)", "128"), N(1.92, "ratio", "silicone DustTrak B/A", "1.92"), N(1.22, "ratio", "Teflon DustTrak B/A", "1.22")],
    printed="D-6", scope="Preliminary; differs from final Table 1 (e.g. Kapton arithmetic mean 105 nm final).")
add("same_report", 64, "Appendix E (2008 AIAA paper), Table 1", "percentage increase over the sizes from a comparable test in",
    "Earliest (2008) count mean diameters for baseline runs with % larger than comparable 1-g tests: silicone 263 nm (+53%), Teflon 223 nm (+15%), lamp wick 248 nm (+65%), Kapton 114 nm (+58%).",
    "particle_property", S, mats=M4,
    nums=[N(263, "nm", "silicone CMD", "263"), N(53, "%", "silicone larger than 1-g", "53"), N(223, "nm", "Teflon CMD", "223"), N(15, "%", "Teflon larger than 1-g", "15"), N(248, "nm", "lamp wick CMD", "248"), N(65, "%", "lamp wick larger than 1-g", "65"), N(114, "nm", "Kapton CMD", "114"), N(58, "%", "Kapton larger than 1-g", "58")],
    cond=C(g=UG), printed="E-6", scope="Only zeroth and first moment instruments used; values differ from later tables. 1-g comparison test details not given here.")
add("same_report", 66, "Appendix E, IV Conclusion", "typically 50% large in count mean diameter than similar conditions in normal gravity",
    "2008 conclusion: low-g smoke count mean diameter typically about 50% larger than in similar 1-g conditions, all below 300 nm, suggesting smoke/dust discrimination might be done by detecting in the sub-micrometer range.",
    "particle_property", S, mats=M4, nums=[N(50, "%", "typical increase vs 1-g", "50%"), N(300, "nm", "upper bound of resultant sizes", "300 nm")], cond=C(g=UG), printed="E-8",
    scope="Preliminary count-mean results only; later SAME-R aging/zero-flow results show larger sizes.")
add("same_report", 66, "Appendix E, IV Conclusion", "actual detection times can be quite long and strongly dependent on location and the presence",
    "FDS modelling of the ISS US Lab predicted long detection times strongly dependent on source location and obstructions; mixing dominates transport in low g.",
    "context", "SAME (FDS model)", det="ISS area smoke detectors (modelled)", printed="E-8", scope="Numerical model, not experiment.")
add("same_report", 66, "Appendix E, Figures 7-8 caption", "condition occurred for LA1 for the 0.05 soot yield",
    "Model runs recorded 'DNA (did not alarm)' cases for the 0.05 soot-yield source at some wall locations (e.g. LA1 N1 wall for LAS5RR; LA3 S3 wall for LAP1RR; several LA6 walls).",
    "context", "SAME (FDS model)", det="ISS area smoke detectors (modelled)", nums=[N(0.05, "soot yield", "low soot-yield case with DNA", "0.05")], printed="E-8",
    scope="MODELLED did-not-alarm outcomes, not experimental missed alarms.")

# SAME conclusions / dust / false alarm
add("same_report", 29, "Section 6 Closing Remarks", "will probably require a detection system that can discriminate the particle size distribution",
    "Closing conclusion: detecting smoke across the SAME+CSD size range while discriminating against (large) dust will probably need a detector with at least limited size discrimination - either measuring more than one moment or classifying particles into size ranges.",
    "recommendation", S, printed="19", scope="Authors' recommendation; based on overheat (non-flaming) smoke of the tested materials.")
add("same_report", 57, "Appendix D, Conclusions", "produced significant numbers of sub-micron particulate that are better detected using an ionization smoke detector",
    "2008 conclusion: under SAME conditions all samples produced many sub-micron particles that are better detected by an ionization detector; with CSD, broader size distributions are possible from credible pre-fire overheat; multi-moment detectors may detect and reject alarms better.",
    "recommendation", S, mats=M4, det="ionization smoke detector", printed="D-7")
add("same_report", 11, "Section 1 Introduction", "increased reliability of fire detection systems in addition to robust false alarm resistance",
    "Missions beyond low Earth orbit will need more reliable fire detection together with robust false-alarm resistance.",
    "technology_need", S, printed="1")
add("same_report", 11, "Section 1 Introduction", "Extended lunar-surface missions will require systems that are not influenced by lunar dust",
    "Extended lunar-surface missions will need detection systems not influenced by lunar dust and other nuisance dust.",
    "technology_need", S, cond=C(g="lunar surface (stated need, not tested)"), printed="1",
    scope="Statement of need only; SAME did not test lunar dust or partial gravity (within the examined text).")
add("same_report", 11, "Section 2 Smoke Background", "limited to line-of-sight and were reported to have difficulties with false alarms",
    "Historical context: Skylab carried about 30 UV-sensing fire detectors, limited to line of sight and reported to have false-alarm difficulties.",
    "false_alarm", "Skylab (background)", det="UV-sensing fire detectors", nums=[N(30, "detectors", "approximate Skylab UV detectors", "approximately 30")], printed="1",
    scope="Background citation (Friedman); not SAME data.")
add("same_report", 11, "Section 2 Smoke Background", "the primary target for detection is the pyrolysis products and not the soot",
    "Detection target: early-phase pyrolysis/smoldering products rather than soot from established flaming fires, because spacecraft volume is constrained.",
    "context", S, printed="1", scope="Defines the scope of SAME: pre-fire overheat smoke.")
add("same_report", 13, "Section 2 (p.3)", "None of these events spread into a real fire",
    "Six overheat/failed-component events in the Orbiter fleet and similar ISS incidents occurred, none spreading into a real fire; Mir 1997 showed oxygen-generation failures can be serious.",
    "context", "STS/ISS/Mir (background)", nums=[N(6, "events", "Orbiter overheat/failed component events", "six")], printed="3",
    scope="Only oxygen mention in SAME report relates to Mir oxygen generator failure, not to test atmosphere.")
add("same_report", 13, "Section 2 (p.3)", "the background dust aerosol conditions must be considered",
    "Fire detection must discriminate against ambient background/nuisance signals, so spacecraft background dust aerosol must be considered.",
    "context", S, printed="3")
add("same_report", 14, "Section 2 (p.4)", "a feasibility experiment to validate the operation of an aerosol particle counter in low-gravity (DAFT).",
    "Link to DAFT: the only prior ISS background aerosol data came from DAFT, a feasibility experiment validating an aerosol particle counter in low gravity (US Lab, Increment 10); counts were at instrument noise level.",
    "context", "DAFT (cited in SAME report)", det="aerosol particle counter (DAFT)", printed="4",
    scope="DAFT is listed in the acronyms (PDF p9) as a precursor project of SAME.")
add("same_report", 14, "Section 2 (p.4)", "particle count levels were at the noise level for the instrument (less than 5 particles/cm3)",
    "DAFT ISS background measurement: particle counts were at instrument noise level, below 5 particles/cm3.",
    "context", "DAFT (cited in SAME report)", nums=[N(5, "particles/cm3", "upper bound of measured background count", "less than 5 particles/cm3")], cond=C(g=UG), printed="4",
    scope="US Lab, Increment 10, secondhand in SAME report.")
add("same_report", 14, "Section 2 (p.4)", "~ 40% of the particles in each of the",
    "STS-32 (1990) background: two cascade impactors found a bimodal distribution, about 40% of particles each in 2.5-10 um and >100 um bins; a scattering instrument gave 17 measurements in 12 locations of 50-70 ug/m3, over 5x typical indoor levels in the populated bins.",
    "context", "STS-32 (background)", nums=[N(40, "%", "share of particles in each dominant bin", "~ 40%"), N(17, "measurements", "light-scattering measurements", "17"), N(50, "ug/m3", "min mass concentration", "50"), N(70, "ug/m3", "max mass concentration", "70")],
    printed="4", scope="Background dust data cited from Liu et al. 1991; not SAME data.")
add("same_report", 14, "Section 2 (p.4)", "suggest a zone of opportunity for spacecraft fire detection",
    "Low STS particle levels below 2.5 um and low ISS counts suggest a 'zone of opportunity' for fire detection in that size range, but more complete particle size statistics are needed.",
    "research_question", S, nums=[N(2.5, "um", "size band upper limit", "2.5")], printed="4", scope="Explicit data gap identified by authors.")
add("same_report", 20, "Section 3.B (p.10)", "These changes were tested in a separate space experiment with good results",
    "The P-Trak condenser was modified with small grooves so isopropanol condensate returns to the wick in low g; this was tested in a separate earlier space experiment with good results.",
    "measurement_limitation", S, det="P-Trak (TSI)", printed="10",
    scope="The 'separate space experiment' is cited as Urban et al. 2005; the text does not name it, though the same reference is the DAFT background source - linking it to DAFT is plausible but NOT explicit here.")
add("same_report", 40, "Appendix B (2009 ICES paper), p.B-6", "This could indicate increased sensitively to nuisance sources such as dust",
    "Hypothetical single-point alarm requirement analysis (2 mg/m3, GMD 500 nm, GSD 1.3): as particle size increases, a scattering detector needs progressively fewer particles to alarm, indicating raised sensitivity to nuisance sources such as dust.",
    "false_alarm", S, det="scattering detector (modelled)", nums=[N(2, "mg/m3", "hypothetical alarm level", "2 mg/m"), N(500, "nm", "hypothetical GMD", "500 nm"), N(1.3, "GSD", "hypothetical GSD", "1.3")],
    printed="B-6", scope="Calculated response curves for a hypothetical requirement, not observed false alarms.")
add("same_report", 40, "Appendix B, p.B-6", "may suffer from conditions where it is either too sensitive or not sensitive enough",
    "A detector measuring a single moment may be too sensitive or not sensitive enough depending on particle size; a single-size (or no-size) specification is risky, as with the current ISS and STS detectors tuned to different size ranges.",
    "measurement_limitation", S, det="single-moment detectors (ISS, STS)", printed="B-6")
add("same_report", 40, "Appendix B, p.B-6", "alarm requirements that include criteria at particle sizes spanning the expected range of fire particulate",
    "Proposed alternative: alarm requirements with criteria at several particle sizes spanning expected fire particulate (e.g. 200-1200 nm); two-moment detectors could exploit the moment ratio, and the two signals might help reduce false alarms.",
    "recommendation", S, nums=[N(200, "nm", "example lower bound", "200"), N(1200, "nm", "example upper bound", "1200 nm")], printed="B-6")

# =====================================================================
# SAME-R PROFILE (samer_report)
# =====================================================================
add("samer_report", 2, "Abstract", "was introduced to replace DBP samples",
    "SAME-R vs SAME (1): Pyrell (intumescent fire-retardant foam, Foamex) replaced the DBP reference samples.",
    "investigation_profile", SR, mats=["Pyrell"], scope="Appendix F (PDF p78) still lists dibutyl-phthalate among the materials of the excerpted paper - inconsistency, likely from combining both flights.")
add("samer_report", 2, "Abstract", "test condition ranges was extended to include higher heating temperature and no-flow conditions",
    "SAME-R vs SAME (2): test conditions extended to higher heating temperatures and no-flow (quiescent) heating.",
    "investigation_profile", SR, cond=C(g=UG, flow=0))
add("samer_report", 2, "Abstract", "was used to replace one of the two Commercial Diagnostic Enclosures",
    "SAME-R vs SAME (3): a new GRC-built instrument, MPASS (M-pass), replaced one of the two Commercial Diagnostic Enclosures (DustTrak + ionization detector).",
    "investigation_profile", SR, det="MPASS (Multi-Parameter Aerosol Scattering Sensor)",
    scope="Appendix A lists a cyclone inlet on CDA (MPASS) and a 10 um impactor on CDB; the dual 1 um / 10 um DustTrak comparison is described for SAME-1 only.")
add("samer_report", 2, "Abstract", "SAMER flight tests were conducted from July 16, to September 9, 2010",
    "SAME-R flight dates: July 16 - September 9, 2010 (Appendix F: Expedition 24).", "investigation_profile", SR, cond=C(g=UG))
add("samer_report", 2, "Introduction", "all the TEM grids were severely contaminated with some unidentified foreign particles",
    "Motivation: SAME's main problem was that all TEM grids were severely contaminated with unidentified foreign particles and unusable; SAME-R used rebuilt thermal precipitators (Appendix F: more rigorous assembly controls gave good images).",
    "measurement_limitation", S, det="thermal precipitator / TEM grids")
add("samer_report", 2, "Introduction", "conducted under exactly the same conditions as those for the SAMER flight tests",
    "Post-flight ground work: (1) apparatus flow tests for accurate P-Trak/DustTrak dilution ratios, (2) 1-g TEM tests under the same conditions as flight to identify gravity effects, (3) SMPS drum tests to check the lognormal assumption.",
    "investigation_profile", SR, cond=C(g=G1), scope="Ground (1-g) tests; not flight data.")
add("samer_report", 2, "Introduction", "the same Rt/R0, the sample heating temperatures can be quite different",
    "Data-reduction improvement: sample heating temperatures were derived from logged engineering data because identical Rt/R0 setpoints can give quite different sample temperatures.",
    "measurement_limitation", SR, det="heater wire resistance control (Rt/R0)")
add("samer_report", 26, "Sample heating temperature derivation", "the actual heating temperature difference can be as large as 30 degrees Celsius",
    "For the same Rt/R0 setpoint, derived actual heating temperatures differed by as much as 30 degC (wire length and room temperature vary between samples).",
    "measurement_limitation", SR, det="heater wire resistance control (Rt/R0)", nums=[N(30, "degC", "max temperature difference at same Rt/R0", "30 degrees Celsius")],
    scope="Rt/R0 is therefore an imperfect proxy for sample temperature in both SAME and SAME-R.")
add("samer_report", 3, "Flight Operation", "SAME-R utilized the SAME hardware already on orbit with reloaded sample carousels",
    "SAME-R reused the SAME hardware already on orbit with reloaded carousels, 30 extra loose samples, rebuilt thermal precipitators and a refilled P-Trak alcohol cartridge; apparatus and moment method otherwise unchanged.",
    "investigation_profile", SR, cond=C(g=UG))
add("samer_report", 3, "Flight Operation", "thirty loose samples were also uploaded to ISS",
    "Samples: six preloaded carousels (mixed materials) plus 30 loose samples (6 Pyrell, 6 silicone, 9 Kapton, 5 lamp wick, 4 Teflon) loaded into carousel 4 in groups of six, logged as carousels 7(4)-11(4).",
    "investigation_profile", SR, mats=M5R, nums=[N(30, "samples", "loose samples uploaded", "thirty")])
add("samer_report", 3, "Flight Operation", "Pyrell sample installed in position 6 of carousel 5 was found unusable",
    "One Pyrell sample (carousel 5, position 6) was unusable, probably shaken loose during launch.", "measurement_limitation", SR, mats=["Pyrell"])
add("samer_report", 3, "Flight Operation", "Totally 67 runs were conducted including two runs using reused samples.",
    "Run count: 67 runs including two on reused samples; with secondary-aging runs listed separately the total is 109 entries. 70 TEM samples collected.",
    "investigation_profile", SR, mats=M5R,
    nums=[N(67, "runs", "primary heating runs", "67"), N(2, "runs", "runs on reused samples (reburns)", "two"), N(109, "entries", "runs incl. secondary aging", "109"), N(70, "TEM samples", "TEM samples collected", "70")],
    n=65, scope="Independent heating events: 65 physical samples (67 runs minus 2 reburns: run 57 reburned L14 from run 54; run 90 reburned the sample of run 85). The 42 secondary-aging records are repeat measurements of the same smoke batch. INTERNAL INCONSISTENCY: abstract (p2) and PSI-101 metadata say 66 test points; Appendix F says 72 TEM samples.")
add("samer_report", 2, "Abstract", "successfully completing 66 test points",
    "The SAME-R abstract (and PSI-101 metadata approach) reports 66 test points, conflicting with the 67 runs stated on p3 and the 67 run numbers (48-114) in Appendix A.",
    "measurement_limitation", SR, nums=[N(66, "test points", "test points in abstract", "66")],
    scope="Source-internal count discrepancy; Appendix A table supports 67.")
add("samer_report", 3, "Flight Operation", "carried out from July 16, 2010 to September 9, 2010 in 7 time periods",
    "Operations in 7 periods: July 16, July 19-22, July 29-30, August 2, August 23-27, August 30, September 7-9, 2010.", "investigation_profile", SR)
add("samer_report", 3, "Flight Operation", "Six re-assembled Thermal Precipitators, each having 12 TEM grids in it",
    "Six re-assembled thermal precipitators with 12 TEM grids each were flown (capacity 72 grids).", "investigation_profile", SR, det="thermal precipitator / TEM",
    nums=[N(6, "units", "thermal precipitators", "Six"), N(12, "grids", "TEM grids per precipitator", "12")])
add("samer_report", 4, "Flight Operation (p.4)", "The hardware worked fine without any unexpected events.",
    "Authors report smooth flight operations with no unexpected hardware events.", "investigation_profile", SR)
add("samer_report", 4, "SAMER results (excerpt of SAME-2 paper)", "The baseline air flow rate was 8 cm/s",
    "Flow conditions: baseline 8 cm/s, runs down to 2 cm/s, and a limited set with no airflow during heating.",
    "test_condition", SR, nums=[N(8, "cm/s", "baseline airflow", "8 cm/s"), N(2, "cm/s", "lowest non-zero flow named in text", "2 cm/s")], cond=C(g=UG, flow=8),
    scope="Appendix A / CSV also show 1 cm/s runs (103, 107, 108) and inlet velocity logged as 8.1 cm/s for most runs.")
add("samer_report", 4, "SAMER results", "selected to produce 1 to 2 mg of weight loss in 60 seconds",
    "Heating criterion: material-specific baseline temperature chosen for 1-2 mg weight loss in 60 s with reasonable signal on every moment instrument; higher-temperature conditions chosen not to saturate the moment instruments.",
    "test_condition", SR, mats=M5R, nums=[N(1, "mg", "min baseline weight loss", "1"), N(2, "mg", "max baseline weight loss", "2 mg"), N(60, "s", "heating time", "60 seconds")], cond=C(g=UG, heat=60))
add("samer_report", 4, "SAMER results", "the mass concentrations were 2 to 15 mg/m3",
    "Typical run concentrations: a few million particles/cc and 2-15 mg/m3, with some runs lower; billions of particles sampled typically, several million in the lowest-concentration test.",
    "particle_property", SR, nums=[N(2, "mg/m3", "typical min mass conc.", "2"), N(15, "mg/m3", "typical max mass conc.", "15 mg/m3")], cond=C(g=UG))
add("samer_csv", None, "PSI-101_Experimental table_SAME-R.csv, all rows (aggregated by this agent)", "Kapton,102,No flow run w/ aging,8-Sep,0,1.48,120,11,8,28",
    "SAME-R run index (CSV): heating duration 60 s for all primary rows except run 102 (120 s); primary aging 11 s for most runs, 720 s for runs 67-71, 1 s for run 53; primary mixing 8 s throughout; inlet velocity 8.1 (or 8) cm/s, 2, 1 or 0 cm/s.",
    "test_condition", SR, mats=M5R,
    nums=[N(60, "s", "heating duration (typical)", "60"), N(120, "s", "heating duration run 102", "120"), N(11, "s", "primary aging (typical)", "11"), N(720, "s", "primary aging runs 67-71", "720"), N(8, "s", "primary mixing", "8")],
    cond=C(g=UG), scope="Aggregated by this agent from CSV rows; see separate item on CSV vs report discrepancies.")
add("samer_csv", None, "PSI-101_Experimental table_SAME-R.csv, Rt/R0 column by material (aggregated)", "Teflon,50,B.L. High RT/R0,20-Jul,8.1,1.452,60,11,8,33",
    "Rt/R0 heating setpoints by material (primary rows): Kapton 1.38-1.48, silicone 1.304-1.36, lampwick 1.245-1.28, Teflon 1.445-1.452 (plus an anomalous 1.253 row), Pyrell 1.22-1.23.",
    "test_condition", SR, mats=M5R,
    nums=[N(1.38, "Rt/R0", "Kapton min", "1.38"), N(1.48, "Rt/R0", "Kapton max", "1.48"), N(1.304, "Rt/R0", "silicone min", "1.304"), N(1.36, "Rt/R0", "silicone max", "1.36"), N(1.245, "Rt/R0", "lampwick min", "1.245"), N(1.28, "Rt/R0", "lampwick max", "1.28"), N(1.445, "Rt/R0", "Teflon min (excl. anomalous row)", "1.445"), N(1.452, "Rt/R0", "Teflon max", "1.452"), N(1.22, "Rt/R0", "Pyrell min", "1.22"), N(1.23, "Rt/R0", "Pyrell max", "1.23")],
    scope="Setpoints, not temperatures (same Rt/R0 can differ by up to 30 degC).")
add("samer_report", 17, "TEM Particle Morphology Results (Fig. 19-20 captions)", "TEM images of unaged smoke from flight tests-- Lamp wick, 264.7",
    "Derived flight sample heating temperatures quoted in figure captions: lamp wick 264.7 degC, Pyrell 242.1 degC, Teflon 516.3 degC (unaged flight tests); Kapton high-temperature test 574 degC (Fig. 19); silicone 380 degC (Fig. 21, PDF p18).",
    "test_condition", SR, mats=M5R,
    nums=[N(264.7, "degC", "lamp wick flight heating temp", "264.7"), N(242.1, "degC", "Pyrell flight heating temp", "242.1"), N(516.3, "degC", "Teflon flight heating temp", "516.3"), N(574, "degC", "Kapton high-temperature flight test", "574"), N(380, "degC", "silicone (Fig. 21)", "380")],
    cond=C(g=UG), scope="Individual tests only; derived (not directly measured) temperatures. Ground SMPS tests cite other temperatures (e.g. Kapton 510.5 degC, silicone 369.2 degC).")
add("samer_report", 8, "D. Impact of flow on particle morphology", "These products may include partially oxidized species resulting from the reaction with oxygen.",
    "TEST ATMOSPHERE: the only statement touching gas composition is that pyrolysis products may include partially oxidized species from reaction with oxygen; no O2 concentration or pressure of the test gas is given.",
    "test_condition", SR, cond=C(g=UG),
    scope=ATM_NOTE + " Implies oxygen was present (air), nothing more. Keyword search found 'kPa'/'psi' only for the ground drum purge (309 kPa-g) and 'pressure' only for drum/N2 regulator context.")
add("samer_report", 25, "Flow test - verification of dilution ratio", "the aerosol stream was diluted with the N2 gas provided by the ISS",
    "Sample dilution for P-Trak and DustTrak used nitrogen supplied by the ISS (P-Trak via a dynamic diluter; DustTrak via an on/off orifice).",
    "test_condition", S + "/" + SR, det="P-Trak; DustTrak", cond=C(g=UG),
    scope="Dilution gas for instruments only - not the sample/heating atmosphere.")
add("samer_report", 11, "Drum Hardware and Experimental Process (ground)", "HEPA-filtered house air at approximately 309 kPa-g (45 psig)",
    "Ground SMPS drum purge used HEPA-filtered house air at about 309 kPa gauge (45 psig).",
    "context", "SAME-R ground test", cond=C(g=G1), nums=[N(309, "kPa (gauge)", "drum purge air pressure", "309 kPa-g"), N(45, "psig", "drum purge air pressure", "45 psig")],
    scope="Ground purge pressure ONLY; must not be used as the flight test-atmosphere pressure (pressure_kpa left null).")
add("samer_report", 8, "D. Impact of flow on particle morphology", "rather than being diluted in the 6000 cm3 piston",
    "Aging chamber: a piston chamber of about 6000 cm3; under zero flow, smoke (diffusing ~4 cm in 60 s) would occupy ~64 cm3, giving ~50x higher initial concentration and faster coagulation.",
    "test_condition", SR, nums=[N(6000, "cm3", "aging piston volume", "6000 cm3"), N(64, "cm3", "estimated zero-flow smoke volume", "64 cm3"), N(50, "x", "estimated concentration ratio zero-flow vs flow", "50 times")], cond=C(g=UG, flow=0),
    scope="Order-of-magnitude estimate by authors.")
add("samer_report", 9, "D. Impact of flow (zero-flow)", "was examined for 11 tests by modifying the valve operation in the SAME hardware",
    "Zero-flow condition was not in the original hardware design; it was run for 11 tests by modifying valve operation.",
    "test_condition", SR, mats=M5R, nums=[N(11, "tests", "zero-flow tests", "11")], cond=C(g=UG, flow=0), n=11,
    scope="CSV shows 11 primary zero-flow runs (95-106 range) across all five materials.")
add("samer_report", 9, "D. Impact of flow (zero-flow)", "approximately half the smoke was lost from the system because it diffused out",
    "Zero-flow limitation: about half the smoke diffused out of the inlet into the MSG volume, so total particle counts were lower than normal and TEM grids had few particles.",
    "measurement_limitation", SR, mats=M5R, nums=[N(50, "%", "approximate smoke lost (half)", "approximately half")], cond=C(g=UG, flow=0),
    scope="Applies to the 11 zero-flow tests only.")
add("samer_report", 9, "D. Impact of flow (zero-flow)", "diameter of average mass is 30 % to 40 % larger for the zero-flow tests",
    "For all materials the diameter of average mass was 30-40% larger in zero-flow tests than in flow tests; the authors stress this condition is unique to low gravity (buoyancy would enlarge the mixing zone in 1 g).",
    "particle_property", SR, mats=M5R, nums=[N(30, "%", "min increase in Dm, zero flow", "30 %"), N(40, "%", "max increase in Dm, zero flow", "40 %")], cond=C(g=UG, flow=0),
    scope="INTERNAL INCONSISTENCY: Appendix F conclusion (PDF p84) says zero-flow particles were 2-3 times larger than at 8 cm/s.")
add("samer_report", 84, "Appendix F, III Conclusions", "produced smoke particles that were 2 to 3 times larger than those produced",
    "Appendix F conclusion: zero-flow conditions produced smoke particles 2-3 times larger than at the nominal 8 cm/s flow.",
    "particle_property", SR, mats=M5R, nums=[N(2, "x", "min size ratio zero-flow/8 cm/s", "2"), N(3, "x", "max size ratio", "3 times")], cond=C(g=UG, flow=0),
    scope="Conflicts with the 30-40% Dm increase stated on PDF p9/p83; which diameter statistic is meant is not specified.")
add("samer_report", 5, "A. Moment Instrument Results (p.5)", "These figures show a strong trend of increased particle size at low flow rates.",
    "Teflon, Kapton and lamp wick diameters plotted vs duct velocity show a strong increase in particle size at low flow; authors conclude smoke trapped in an avionics enclosure can be substantially larger than smoke in ventilated areas.",
    "particle_property", SR, mats=["Teflon", "Kapton", "lamp wick"], cond=C(g=UG),
    scope="Linear fits over 0-8 cm/s; repeatability +/-15%.")
add("samer_report", 5, "Figure 6 caption", "The repeatability of the diameter measurements is estimated to be +/- 15%.",
    "Estimated repeatability of the diameter measurements: +/-15%.", "measurement_limitation", SR, nums=[N(15, "%", "diameter repeatability (+/-)", "+/- 15%")])

# SAME-R particle table
add("samer_report", 5, "Table 1 (continued from PDF p4)", "Table 1: Diameter results for baseline runs for each material (Diameters are in micrometers).",
    "SAME-R Table 1 (baseline runs, um; Dg / CMD / Dm / sigma_g): Kapton unaged 0.047/0.062/0.106/2.072, aged 720 s 0.102/0.121/0.169/1.790; lampwick 0.103/0.142/0.271/2.232, aged 0.269/0.308/0.401/1.673; silicone 0.152/0.221/0.468/2.382, aged 0.320/0.400/0.628/1.956; Teflon 0.093/0.111/0.173/2.081, aged 0.080/0.115/0.237/2.342; Pyrell 0.177/0.227/0.377/2.032, aged 0.348/0.400/0.529/1.697.",
    "particle_property", SR, mats=M5R,
    nums=[N(0.062, "um", "Kapton unaged CMD", "0.062"), N(0.106, "um", "Kapton unaged Dm", "0.106"), N(0.111, "um", "Teflon unaged CMD", "0.111"), N(0.173, "um", "Teflon unaged Dm", "0.173"), N(0.468, "um", "silicone unaged Dm", "0.468"), N(0.628, "um", "silicone aged Dm", "0.628"), N(0.377, "um", "Pyrell unaged Dm", "0.377"), N(0.529, "um", "Pyrell aged Dm", "0.529")],
    cond=C(g=UG, flow=8, age=720), scope="Kapton row printed on PDF p4. Teflon aged Dg (0.080) is smaller than unaged (0.093). Values differ from NTRS 20130000422 Table 1 as transcribed by Model C (e.g. Kapton CMD 0.056 there).")
add("samer_report", 4, "A. Moment Instrument Results", "This assumption cannot be directly tested with the available data",
    "Lognormality (needed for Dg and sigma_g) cannot be tested directly with flight data; authors cite CMD < Dm and sigma_g between 1 and about 3.5 as indirect support.",
    "measurement_limitation", SR, scope="CMD and Dm themselves do not require lognormality.")
add("samer_report", 5, "A. Moment Instrument Results (p.5)", "signal gain sensitive enough to trigger an alarm for the lower signal from small particles",
    "Design trade-off stated by the authors: a scattering system with gain high enough to alarm on the weak signal from small Teflon/Kapton particles, without excessive nuisance alarms from large dust, is difficult without some particle-size discrimination.",
    "technology_need", SR, mats=["Teflon", "Kapton"], det="light-scattering smoke detection systems",
    scope="Combines a missed-detection risk (small particles) and a nuisance/false-alarm risk (large dust); neither was counted as an event in SAME-R. No dust was tested in SAME-R (within the examined text).")
add("samer_report", 5, "A. Moment Instrument Results (p.5)", "smoke trapped in an avionics enclosure can be expected to be substantially larger",
    "Implication: smoke trapped in an avionics enclosure (low flow) is expected to be substantially larger than smoke released in ventilated areas.",
    "research_question", SR, scope="Extrapolation from duct-velocity trend; not tested in an actual enclosure.")
add("samer_report", 6, "B. MPASS Results", "The MPASS was included in SAME-2 to demonstrate the effectiveness of a two-moment smoke detector.",
    "MPASS purpose: demonstrate a two-moment smoke detector. A single least-squares third-order correlation (all test points with SNR > 2, independent of material, heating and aging) predicted number and mass concentration from MPASS outputs.",
    "investigation_profile", SR, det="MPASS", nums=[N(2, "SNR", "minimum signal-to-noise for inclusion", "greater than 2")])
add("samer_report", 7, "B. MPASS Results (p.7)", "a feature which can minimize false smoke detector alarms",
    "MPASS result: the two-moment correlation reduced relative variance by at least about a factor of 2 vs a single-output sensor (better for mass than number); authors argue it can tell a high smoke concentration from a lower concentration of very large dust particles, which can minimize false alarms.",
    "followup_solution", SR, det="MPASS", nums=[N(2, "factor", "minimum variance reduction vs single-output sensor (roughly)", "a factor of at least 2")],
    scope="Dust discrimination is an inference: the correlation was built on smoke test points only; no dust challenge is described in the report. Not an observed false-alarm reduction.")
add("samer_report", 77, "Appendix F, F. Instruments (MPASS)", "enable the alarm to be less sensitive to larger particles that are typical of dust",
    "MPASS design: two fixed-angle detectors approximating 2nd and 3rd moments, optimized by Mie modelling for smoke-like aerosols (GMD 0.1-1.0 um, GSD 1.6-1.9, lognormal, refractive index 1.6), intended to make alarms less sensitive to dust-sized particles.",
    "investigation_profile", SR, det="MPASS", nums=[N(0.1, "um", "design GMD min", "0.1"), N(1.0, "um", "design GMD max", "1.0"), N(1.6, "GSD", "design GSD min", "1.6"), N(1.9, "GSD", "design GSD max", "1.9"), N(1.6, "refractive index", "assumed real refractive index", "1.6")],
    scope="Technology demonstration; design assumptions limit applicability to non-lognormal or non-spherical smokes.")
add("samer_report", 7, "C. TEM Results", "silicone rubber presented no particles that were visible via TEM",
    "72 TEM particle samples were taken (p3 says 70); silicone rubber showed no TEM-visible particles, presumed condensed liquid that evaporated before imaging.",
    "measurement_limitation", SR, mats=["silicone rubber"], det="thermal precipitator / TEM", nums=[N(72, "samples", "TEM samples per excerpted paper", "72")],
    scope="Count conflicts with '70 TEM samples' on PDF p3.")
add("samer_report", 8, "D. Impact of flow on particle morphology", "This is the case for the Teflon and Pyrell smokes",
    "Morphology: lamp wick, silicone and Kapton smokes are liquid droplets that coalesce; Teflon and Pyrell smokes are solid fractal-like agglomerates of primary particles.",
    "particle_property", SR, mats=M5R)
add("samer_report", 8, "D. Impact of flow on particle morphology", "Pyrell increasing slightly with flow while Teflon and Kapton decrease",
    "Mass concentration vs flow at fixed wire temperature: silicone, lampwick and Pyrell rose slightly with flow, Teflon and Kapton fell; authors suggest the sample surface temperature may change with flow even at fixed wire temperature.",
    "measurement_limitation", SR, mats=M5R, scope="Possible explanation offered, not verified.")
add("samer_report", 11, "SMPS Results for Spherical Smoke Aerosols (ground)", "are not spherical aerosols and thus are not relevant to the moment method approach",
    "Ground SMPS validation: Pyrell and Teflon are non-spherical and deemed not relevant to the moment-method lognormal check; Kapton and lamp wick fit lognormal well, silicone poorly.",
    "measurement_limitation", "SAME-R ground test", mats=M5R, cond=C(g=G1))
add("samer_report", 22, "Comparison of SMPS Data ... Hatch-Choate Diameters (ground)", "lamp wick can be considered lognormal and silicone should not",
    "Conclusion of ground SMPS comparison: Kapton and lamp wick size distributions can be treated as lognormal, silicone should not.",
    "measurement_limitation", "SAME-R ground test", mats=["Kapton", "lamp wick", "silicone rubber"], cond=C(g=G1))
add("samer_report", 20, "Limitations of Aerosol Instrument Measurement Ranges (ground SMPS)", "of the distribution is missed by the instrument",
    "SMPS range limit: for high-temperature silicone the 1000 nm upper limit captures only about 40% of the volume distribution (60% missed), about 20% with a conservative 700 nm limit; Kapton is 98-100% captured.",
    "measurement_limitation", "SAME-R ground test", mats=["silicone rubber", "Kapton"],
    nums=[N(60, "%", "silicone volume distribution missed at 1000 nm", "60%"), N(20, "%", "silicone captured at 700 nm (approx.)", "approximately 20%"), N(98, "%", "Kapton captured (min)", "98%")], cond=C(g=G1))
add("samer_report", 18, "TEM Particle Size Distribution Results", "only Kapton and lamp wick are spherical aerosols so they are better suited",
    "Only Kapton and lamp wick are spherical aerosols and therefore better suited to the moment method; silicone is treated as liquid droplets; dm remains valid for non-spherical Pyrell and Teflon via material-specific DustTrak calibration.",
    "measurement_limitation", SR, mats=M5R)
add("samer_report", 18, "TEM Particle Size Distribution Results", "Silicone TEM images outlined above and the fractal nature of Teflon particles preclude",
    "Silicone TEM residue and Teflon's fractal structure prevented reliable TEM size distributions; only Kapton, lamp wick and Pyrell were analysed.",
    "measurement_limitation", SR, mats=["silicone rubber", "Teflon"], det="TEM")
add("samer_report", 23, "Comparison Between Size Distribution Parameters from TEM and Moment Method", "the flight lamp wick TEM data was not comprehensive",
    "Flight lamp wick TEM data were not comprehensive, so complete TEM vs moment comparisons were possible only for Kapton.",
    "measurement_limitation", SR, mats=["lamp wick"], det="TEM")
add("samer_report", 24, "Comparison ... (error bars)", "exceeded the calibration range for the ionization detector which measures the first moment",
    "Many smoke aerosols exceeded the calibration range of the ionization (first-moment) detector, the input with the largest influence on Dg/sigma_g; Kapton (small particles) was unaffected and gave the most reliable moment results.",
    "measurement_limitation", SR, mats=M5R, det="ionization chamber (M1)",
    scope="Affects M1-based statistics (CMD, Dg, sigma_g) for non-Kapton materials; Dm (M0+M3) is not affected.")
add("samer_report", 24, "Comparison ... (error bars)", "The zeroth moment instrument error was estimated to be",
    "Moment-instrument error estimates: first moment +/-12%, third moment +/-25% (from Cleary et al. 2009), zeroth moment estimated +/-30%.",
    "measurement_limitation", SR, det="P-Trak (M0); ionization chamber (M1); DustTrak (M3)",
    nums=[N(12, "%", "M1 instrument error (+/-)", "12 %"), N(25, "%", "M3 instrument error (+/-)", "25 %"), N(30, "%", "M0 instrument error (+/-)", "30 %")])
add("samer_report", 26, "Flow test - verification of dilution ratio (p.26)", "the diluting N2 flow was not working under the critical flow regime as original designed",
    "DustTrak dilution: the N2 dilution orifice did not operate in the critical-flow regime as designed (regulator undersized, upstream pressure varied); the four orifices were not calibrated at procurement, so a generic manufacturer curve was used.",
    "measurement_limitation", S + "/" + SR, det="DustTrak dilution system",
    scope="Adds uncertainty to DustTrak dilution ratios in data reduction.")
add("samer_report", 25, "Comparison ... (Fig. 29)", "maintained their calibration sufficiently to quantify one of the moment average diameters from flight data",
    "Flight TEM vs moment-method Dm agreed reasonably for lamp wick, Kapton and Pyrell; authors conclude zeroth and third moment instruments held calibration well enough to quantify Dm from flight data.",
    "particle_property", SR, mats=["lamp wick", "Kapton", "Pyrell"])
add("samer_report", 2, "Abstract", "the moment method in conjunction the lognormal distribution assumption is a valid and effective approach",
    "Overall SAME-R conclusion (abstract): the moment method with the lognormal assumption is valid and effective for characterising spacecraft aerosols; size distributions for five common spacecraft materials were identified.",
    "context", SR, mats=M5R, scope="Ground SMPS work qualifies this: silicone is not lognormal and Teflon/Pyrell are non-spherical.")

# STS detector usage in SAME-R
add("samer_report", 36, "Appendix A Test matrix, row 'Use STS Detector' (PDF pp31-49)", "Use STS Detector",
    "Appendix A flags the STS detector as used ('y') in only 17 of 67 primary runs (67-72, 87-89, 91-92, 109-114); all other runs are 'n'. The SAME-R report contains no ISS- or STS-detector results section (within the examined text).",
    "measurement_limitation", SR, det="Space Shuttle (STS) smoke detector", nums=[N(17, "runs", "primary runs with STS detector flagged 'y' (counted by this agent)", "y"), N(67, "runs", "primary runs", "48-114")],
    n=17, scope="Counted by this agent from the layout of Appendix A rows. The ISS detector has no 'use' flag in Appendix A; its results are not discussed in the SAME-R report text.")
add("samer_report", 49, "Appendix A, carousel 11(4) column for SAME Test # 112", "Use STS Detector",
    "Appendix A lists run 112 as Kapton, low flow (2 cm/s) with STS, Rt/R0 1.480, 9/9/2010, and run 57 only as a lampwick (L14) reburn - so Kapton has 17 primary runs and Teflon 11 in the report.",
    "investigation_profile", SR, mats=["Kapton"], nums=[N(2, "cm/s", "inlet velocity run 112", "2"), N(1.48, "Rt/R0", "run 112 setpoint", "1.480")], cond=C(g=UG, flow=2),
    scope="Used to diagnose the CSV discrepancy below.")
add("samer_csv", None, "PSI-101_Experimental table_SAME-R.csv rows 'Lampwick,57' and 'Teflon,57'", "Teflon,57,High RT/R0 reburn sample,29-Jul,8.1,1.253,60,11,8,n/a",
    "CSV vs report discrepancy: the CSV has 67 primary rows but only 66 unique run numbers - run 57 appears twice (Lampwick and Teflon, identical Rt/R0 1.253 outside Teflon's 1.445-1.452 range) and run 112 (Kapton) is missing. The CSV therefore shows 16 Kapton / 12 Teflon primary rows vs 17 / 11 in report Appendix A.",
    "measurement_limitation", SR, mats=["Teflon", "Kapton", "lampwick"],
    scope="Likely a transcription error in the repository CSV; do not count 'Teflon 57' as an independent Teflon test.")
add("samer_csv", None, "PSI-101_Experimental table_SAME-R.csv, secondary rows ('a' suffix)", "Silicone,65a,aged,23-Aug,8.1,1.327,,,,1923",
    "Secondary aging records (42 rows with suffix 'a') re-measure the retained smoke after net aging of roughly 218-1923 s (e.g. 65a 1923 s; most between about 557 and 856 s). They share the heating event of their parent run.",
    "test_condition", SR, mats=M5R, nums=[N(42, "records", "secondary-aging rows", "42"), N(1923, "s", "longest net aging (65a)", "1923"), N(218, "s", "shortest secondary net aging (55a)", "218")],
    cond=C(g=UG), scope="NOT independent tests. Report Appendix A gives programmed secondary aging durations 180, 480, 720 or 1800 s.")

# SAME-R conclusions
add("samer_report", 84, "Appendix F, III Conclusions", "sub-micron particulate that are readily detected using an ionization smoke detector",
    "Appendix F conclusion: all SAME samples produced significant numbers of sub-micron particles readily detected by an ionization detector.",
    "particle_property", SR, mats=M5R, det="ionization smoke detector", scope="Inference from particle size; SAME-R reports no ionization-detector results.")
add("samer_report", 84, "Appendix F, III Conclusions", "silicone rubber can produce smoke that can reach sizes better detected by light scattering techniques",
    "Aging results suggest some materials such as silicone rubber can produce smoke reaching sizes better detected by light scattering.",
    "particle_property", SR, mats=["silicone rubber"], det="light-scattering detection")
add("samer_report", 84, "Appendix F, III Conclusions", "Since spacecraft fire conditions include an even wider array of materials than those tested here",
    "Authors note real spacecraft fire conditions involve more materials and broader flow/temperature ranges than tested, so broad smoke size distributions should be expected from credible pre-fire overheat events.",
    "research_question", SR, scope="Explicit scope limitation: five materials, limited flow and temperature ranges.")
add("samer_report", 84, "Appendix F, III Conclusions", "may show more successful detection and false alarm rejection than single moment detectors",
    "Recommendation: detection methods measuring more than one moment may give better detection and false-alarm rejection than single-moment detectors; the MPASS prototype was 'very encouraging'.",
    "recommendation", SR, det="multi-moment detectors (MPASS prototype)")
add("samer_report", 84, "Appendix F, III Conclusions", "fire particulate can be expected to have a broad range of morphologies",
    "TEM showed fire particulate can have a broad range of morphologies depending on heating rate, material and flow.",
    "particle_property", SR, mats=M5R, det="TEM")
add("samer_report", 72, "Appendix F abstract", "smoke particle sizes were found to be in the 200 nm to 400 nm range",
    "Appendix F abstract: most average smoke particle sizes were 200-400 nm, with some quiescent (zero-flow) cases producing substantially larger particles; aging times 11-1800 s; flow quiescent to 8 cm/s.",
    "particle_property", SR, mats=M5R, nums=[N(200, "nm", "typical average size lower", "200 nm"), N(400, "nm", "typical average size upper", "400 nm"), N(11, "s", "min aging", "11"), N(1800, "s", "max aging", "1800 s")], cond=C(g=UG))

# PSI metadata issues
add("psi102_meta", None, "$.approach and $.experimentHardware", "turned on the igniter for a predefined period of time (15 to 60 seconds)",
    "Metadata inconsistency: the PSI-102 'approach' text describes near-field hardware, a Far Field Box, an igniter run 15-60 s, thermophoretic soot samplers and ~2 min combustion events, and 'experimentHardware' is 'Comparitive Soot Diagnostic Hardware' - this matches the earlier CSD experiment, not SAME's resistively heated pyrolysis procedure.",
    "measurement_limitation", S, scope="Do not use PSI-102 'approach' as a SAME profile; only its last sentence (controlled temperature, flow, aging) matches SAME.")
add("psi102_meta", None, "$.investigationStartDate / $.investigationEndDate", "$.investigationStartDate = 03-02-2001",
    "PSI-102 investigation dates: 03-02-2001 to 02-28-2008 (programme span; flight was Sept-Oct 2007).", "investigation_profile", S)
add("psi101_meta", None, "$.investigationStartDate / $.investigationEndDate", "$.investigationStartDate = 07-01-2010",
    "PSI-101 investigation dates: 07-01-2010 to 09-30-2010; flight program ISS; managing center GRC.", "investigation_profile", SR)
add("psi101_meta", None, "$.objective", "Based on that experience the SAME-R investigation employed several modification covering new materials",
    "PSI-101 objective: same primary objective as SAME (liquid smoke particle sizes in low g vs generation/transport conditions), with modifications (new materials, extended conditions, diagnostics) motivated by the contaminated SAME TEM grids.",
    "investigation_profile", SR)
add("psi102_meta", None, "$.publications[7].title", "Characterization of Nuisance Particulates in the ISS: Space Smoke Aerosols and Lunar Dust Abatement",
    "PSI-102 publication list includes 'Characterization of Nuisance Particulates in the ISS: Space Smoke Aerosols and Lunar Dust Abatement' (DOI 10.1017/S1431927610060563) and Meyer et al. 2018 'Evaluation of spacecraft smoke detector performance in the low-gravity environment' (10.1016/j.firesaf.2018.04.004).",
    "reference", S, scope="Pointers only; contents not examined in this group (Meyer 2018 handled by another source group).")


add("same_report", 25, "Section 5, Figure 13 discussion (silicone aging run 23)", "This behavior is consistent with particle coagulation with limited wall loss.",
    "Aging run (silicone): number concentration (P-Trak) fell substantially while DustTrak mass concentrations stayed fairly steady - consistent with coagulation with limited wall loss.",
    "particle_property", S, mats=["silicone rubber"], det="P-Trak; DustTrak", cond=C(g=UG), printed="15",
    scope="Implication (not stated by authors): number-sensitive signals fall with aging while mass/scatter-sensitive signals persist.")
add("samer_report", 4, "A. Moment Instrument Results", "the increase in the count mean diameter is greater than the corresponding increase",
    "Aging raised the count mean diameter proportionally more than the diameter of average mass (small particles scavenged by large ones); theory suggests sigma_g tends toward a self-preserving value of 1.32.",
    "particle_property", SR, mats=M5R, nums=[N(1.32, "sigma_g", "self-preserving GSD (theoretical)", "1.32")])
add("same_report", 52, "Appendix D (2008 ICES paper), p.D-2", "all use ionization smoke detectors while the US, JEM and Columbus labs of the",
    "Operational context (2008): the Space Shuttle and Russian ISS segments use ionization smoke detectors, while the US, JEM and Columbus labs of the ISS use light-scattering detectors; low-g smoke data were unavailable when these were designed.",
    "context", "ISS/STS (background)", det="ionization detectors (Shuttle, Russian segment); light-scattering detectors (US, JEM, Columbus)", printed="D-2")

# =====================================================================
# MODEL C (derived) items
# =====================================================================
add("modelc_refs", None, "references.md, 'What do the publications establish...', bullet on Section 3.2 and Figure 9", "Figure 9's dashed ISS alarm boundary coincides with the 2.0 V tick.",
    "Provenance of the 2.0 V ISS alarm reference: Model C read it graphically from the dashed ISS alarm line in Meyer et al. 2018 Figure 9 (Fire Safety Journal 98:74-81); it is not stated in either SAME/SAME-R final report. The Shuttle dashed line near 0.42 V was not treated as exact.",
    "context", "SAME / SAME-R", det="ISS smoke detector", nums=[N(2.0, "V", "ISS alarm reference read from Fig. 9", "2.0 V")],
    scope="Secondhand; primary verification belongs to the meyer2018 source group. Graphical reading, not a printed number.")
add("modelc_refs", None, "references.md, Section 3.2 bullet", "reports ISS failures to alarm in over half the Kapton tests and two thirds",
    "Model C's note of Meyer et al. 2018 Sec. 3.2: the ISS detector failed to alarm in over half of the Kapton tests and two-thirds of the Teflon tests (aggregate, no per-run denominator given in the note).",
    "missed_alarm", "SAME / SAME-R (per Meyer 2018)", mats=["Kapton", "Teflon"], det="ISS smoke detector",
    scope="Secondhand summary - verify against meyer2018 extraction before use.")
add("modelc_same_evidence", None, "Section 'SAME data support experimental detector comparisons'", "61 responses at or above 2 V versus 23 below",
    "Model C derived labels: of 84 primary material-smoke records (17 SAME, 67 SAME-R) in the official combined workbook, 61 reached ISS scatter >= 2.0 V and 23 did not (SAME 13/4, SAME-R 48/19).",
    "modelc_measured", "SAME / SAME-R", mats=M5R, det="ISS smoke detector (scatter channel, V)",
    nums=[N(84, "records", "primary records", "84"), N(61, "records", ">= 2 V", "61"), N(23, "records", "< 2 V", "23")], n=82,
    scope="DERIVED threshold label, not a NASA-reported alarm event or time-to-alarm. 82 conservative physical-sample groups (17 SAME + 65 SAME-R). Model C's SAME subset has 17 primary non-DBP heating runs, whereas the SAME flight log lists 24 non-DBP initial heatings plus one Teflon reheat; which log entries are missing from the workbook was not resolved here.")
add("modelc_material_oof", None, "material_majority_oof.csv, columns material x reference grouped by campaign (computed by this agent)", "test_id,group_id,material,fold,reference,material_majority,fixed_forest,forest_score,original_nested_selection",
    "Per-material derived ISS >= 2.0 V counts (primary runs): SAME - Kapton 4/4, lampwick 4/4, silicone 5/5, Teflon 0/4; SAME-R - Kapton 5/17, lampwick 13/13, Pyrell 12/12, silicone 14/14, Teflon 4/11. Below-threshold cases occur only for Kapton and Teflon.",
    "modelc_measured", "SAME / SAME-R", mats=M5R, det="ISS smoke detector (scatter channel, V)",
    nums=[N(0, "runs", "SAME Teflon >= 2 V (of 4)", "0"), N(4, "runs", "SAME-R Teflon >= 2 V (of 11)", "4"), N(5, "runs", "SAME-R Kapton >= 2 V (of 17)", "5"), N(4, "runs", "SAME Kapton >= 2 V (of 4)", "4")],
    scope="DERIVED labels at a graphically read 2.0 V reference; reburn run 90 shares a sample with 85 (Kapton) and 57 with 54 (lampwick), so per-material independent counts are 1 lower there. Conditions differ across runs (flow 0-8.1 cm/s, aging 11-720 s).")
add("modelc_same_evidence", None, "Section 'Common controls support an ISS response label...'", "The approximately 6.25 V plateau is consistent with published saturation",
    "ISS scatter signal saturates near about 6.25 V; Model C kept per-row saturation unresolved and used only the threshold label.",
    "measurement_limitation", "SAME / SAME-R", det="ISS smoke detector (scatter channel)", nums=[N(6.25, "V", "approximate saturation plateau", "approximately 6.25 V")],
    scope="Saturation prevents using analog magnitude above the plateau.")
add("modelc_same_evidence", None, "Section 'Common controls support an ISS response label...'", "Shuttle data cannot be labeled by interpreting zero as no detection",
    "STS detector data in the workbook include not-used flags, zeros and near-negative-zero readings, so zero cannot be read as 'no detection'; Model C did not derive STS alarm labels.",
    "measurement_limitation", "SAME / SAME-R", det="Space Shuttle (STS) smoke detector",
    scope="Consistent with the SAME-R Appendix A 'Use STS Detector' flags (17/67 runs).")

# ---------------------------------------------------------------------
docs = json.load(open(f"{SP}/docs.json"))
doc_ids = {d["doc_id"] for d in docs}

# ---------------- validation ----------------
texts = {d: open(f"{ROOT}/sources/text/{d}.txt", encoding="utf-8").read() for d in doc_ids}
norm = lambda s: " ".join(s.split())
bad = []
for it in items:
    assert it["doc_id"] in doc_ids, it["doc_id"]
    t = texts[it["doc_id"]]
    if it["pdf_page"]:
        pages = t.split("\f")
        t = pages[it["pdf_page"] - 1]
    a = it["anchor_quote"]
    if len(a.split()) > 15:
        bad.append((it["item_id"], "too long", len(a.split()), a))
    if norm(a) not in norm(t):
        bad.append((it["item_id"], "NOT FOUND", it["doc_id"], it["pdf_page"], a))
for b in bad:
    print(b)
print("items", len(items), "bad", len(bad))
json.dump(items, open(f"{SP}/items.json", "w"), indent=1, ensure_ascii=False)
