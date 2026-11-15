"""Build sources/extracted/same_profiles.final.json from same_profiles.json.

Adversarial verification of the same_profiles extraction. Run with:
  .venv/bin/python -I sources/scripts/same_profiles_verify/build_final.py
Reads only project text files; never modifies same_profiles.json.
"""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

R = Path('/home/efeai/Desktop/NasaSpaceApps')
SRC = R / 'sources/extracted/same_profiles.json'
OUT = R / 'sources/extracted/same_profiles.final.json'

d = json.loads(SRC.read_text())
final = copy.deepcopy(d)
docs = {x['doc_id']: x for x in d['documents']}


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


texts = {k: (R / v['text_path']).read_text() for k, v in docs.items()}


def page_text(doc_id, pdf_page):
    t = texts[doc_id]
    return t.split('\f')[pdf_page - 1] if pdf_page else t


# ---------------------------------------------------------------- raw checks
raw_check = {}
for k, v in docs.items():
    p = R / v['local_path']
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    meta_p = R / 'sources/raw' / k / 'meta.json'
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    raw_check[k] = (h == v['sha256'] == meta.get('sha256'), h)

# ---------------------------------------------------------- default verdicts
V = {}  # item_id -> (verdict, note, original-dict)


def confirm(iid, note):
    V[iid] = ('CONFIRMED', note, {})


def correct(iid, note, **changes):
    V[iid] = ('CORRECTED', note, changes)


NOTE_DEFAULT = ('Anchor found verbatim on the cited page/location; summary, numbers, '
                'category and attributions checked against the source text.')

# ---------------------------------------------------- item-specific outcomes
confirm('same_profiles-001', 'Recomputed sha256 of the PDF and of the PSI-101 workbook; both equal source_manifest.json. Text file regenerated with plain pdftotext is byte-identical.')
confirm('same_profiles-002', 'Recomputed sha256 equals manifest and meta.json; regenerated pdftotext output is byte-identical.')
confirm('same_profiles-003', 'Recomputed sha256 equals manifest and meta.json.')
confirm('same_profiles-004', 'Recomputed sha256 equals manifest and meta.json.')
confirm('same_profiles-005', 'Recomputed sha256 equals manifest; sources/text/same_csv.txt is byte-identical to the raw CSV.')
confirm('same_profiles-006', 'Recomputed sha256 equals manifest; sources/text/samer_csv.txt is byte-identical to the raw CSV.')
confirm('same_profiles-012', 'Also checked: GMT day 252 of 2007 = Sept 9 and day 278 = Oct 5, consistent with SAME-R p2.')
confirm('same_profiles-017', 'Appendix A (layout check) shows the 75 s heating comment on test 44 (a DBP reheat); Model C evidence note gives SAME heating durations 10-60 s.')
confirm('same_profiles-027', 'Recounted from a -layout rendering of PDF p33: 47 tests, 30 Initial (6 per material) and 17 Reheat (16 DBP, 1 Teflon = test 10); comments sit on tests 8, 33, 34, 37 (a DBP reheat) and 44 (a DBP reheat). Verbatim "1-47" is a range label, not printed text.')
confirm('same_profiles-029', 'CSV rows checked; Model C phrase "eight numbered Teflon configurations" confirmed in modelc_same_evidence.txt line 11.')
confirm('same_profiles-034', 'Anchor on PDF p12; the 0.5 um polystyrene-bead value is printed on PDF p13 (printed page 3, rendered "0.5 m" with the micro sign lost).')
confirm('same_profiles-035', 'PDF p60 (Appendix E) indeed says sensitivity extends down to 0.6 um while also giving 0.3 um as minimum reported.')
confirm('same_profiles-045', 'All 32 Table 1 values re-read on PDF p27 and match.')
confirm('same_profiles-048', 'p17 text says over 1 um; Table 1 (same page) 606 nm; Appendix B p39 "over 500 nm" - inconsistency correctly flagged.')
confirm('same_profiles-058', 'Detection-time / obstruction statement is on p66; the "mixing dominates" clause comes from the abstract (p4) and Appendix E abstract (p59) - see added item same_profiles-153.')
confirm('same_profiles-059', 'DNA cases re-read in Fig. 7-9 captions on p66; these are MODELLED did-not-alarm outcomes.')
confirm('same_profiles-087', 'Appendix A (layout) confirms run 57 = Lampwick L14 "reburn sample" (L14 first used in run 54) and run 90 = "Mid Temp aging reburn 85"; 109 entries = 67 primary + 42 secondary.')
confirm('same_profiles-095', 'Re-aggregated with pandas: 67 primary rows; durations 60 s (66) and 120 s (run 102); primary aging 11 s (61), 720 s (runs 67-71), 1 s (run 53); mixing 8 s for all; velocities 8.1/8/2/1/0.')
confirm('same_profiles-096', 'Rt/R0 ranges re-aggregated with pandas and match.')
confirm('same_profiles-097', 'Values 264.7/242.1/516.3 (Fig. 20) and 574 degC (Fig. 19) are on PDF p17; the 380 degC silicone value is on PDF p18 (Fig. 21), as the summary says.')
confirm('same_profiles-102', 'CSV has 11 primary zero-flow runs (95-102, 104-106 excluding 103 which is 1 cm/s), covering all five materials; none is a reburn.')
confirm('same_profiles-108', 'All 40 Table 1 values re-read; Kapton row is on PDF p4, the rest on p5, as the location states. airflow_cm_s=8 is the stated baseline flow; CSV logs these baseline runs at 8.1 cm/s.')
confirm('same_profiles-129', 'Re-parsed Appendix A (pp31-49) with -layout column alignment: STS flag "y" for exactly 17 primary runs 67-72, 87-89, 91-92, 109-114. Verbatim "48-114" is a range label.')
confirm('same_profiles-130', 'Appendix A layout: run 112 = Kapton, 9/9, 2 cm/s, Rt/R0 1.480, STS y; Kapton 17 and Teflon 11 primary runs recounted.')
confirm('same_profiles-131', 'pandas: 67 primary CSV rows, 66 unique ids; 57 duplicated (Lampwick and Teflon), 112 missing; CSV material counts Kapton 16 / Teflon 12.')
confirm('same_profiles-132', 'pandas: 42 suffix-a rows; net aging 218-1923 s (95a n/a); Appendix A secondary aging durations seen: 180, 480, 720, 1800 (and 0).')
confirm('same_profiles-139', 'Confirmed. Note: PSI-101 metadata $.experimentHardware also reads "Comparitive Soot Diagnostic Hardware; Refer to final report" - same curation issue for SAME-R.')
confirm('same_profiles-141', 'managingNasaCenter = Glenn Research Center (GRC); flightProgram = ISS.')
confirm('same_profiles-143', 'publications[7] and publications[13] titles/DOIs confirmed in psi102_meta.txt.')
confirm('same_profiles-147', 'Quote found in modelc_refs.txt line 10; keyword scan of both final reports finds no "2.0 V"/"2 V" string.')
confirm('same_profiles-149', 'Confirmed in modelc_same_evidence.txt (lines 3, 30, 64). n_independent_tests=82 is Model C\'s primary physical-sample count; Model C trained with 81 conservative connected groups (line 102). Verifier cross-check: the workbook SAME ids are 5, 23-35, 41, 46, 47, so the non-DBP initial heatings of flight-log tests 1, 6, 7, 8, 13, 14, 17 (carousels 1-2) and the Teflon reheat test 10 are not among Model C\'s 17 SAME primary runs.')
confirm('same_profiles-150', 'Re-grouped material_majority_oof.csv by campaign/material with pandas: SAME 13/17, SAME-R 48/67, per-material counts as stated.')

# --- corrections -------------------------------------------------------------
correct('same_profiles-030',
        'Scope note overstated the keyword search: "Atmosphere" does occur once, in the Appendix E heading "F. Spacecraft Atmosphere Dust Background" (PDF p61), about background dust, not test gas; "oxygen" occurs only in the Mir oxygen-generator sentence (pp13, 36, 44, 52, 61). The extractor\'s case-sensitive regex missed the capitalised word. Conclusion (no test-gas O2 or pressure stated) unchanged.',
        scope_notes='Test atmosphere O2 concentration and pressure are NOT stated in this document (null, not inferred). Implied only as air inside the MSG; no cabin-air numbers given. Case-insensitive keyword scan of the full text: no "kPa", "psi", "pressure" or "O2"; "Atmosphere" appears only in the Appendix E heading "Spacecraft Atmosphere Dust Background" (PDF p61, about background dust); "oxygen" appears only in the Mir oxygen-generation sentence.')
correct('same_profiles-039',
        'Category changed missed_alarm -> measurement_limitation: the source reports a "more erratic" ISS signal, not an alarm/no-alarm outcome, so this is a documented weaker detector response, not a documented missed alarm. Detector field had an added "(weak/erratic)" qualifier not in the source.',
        category='measurement_limitation',
        detector='ISS smoke detector; Space Shuttle (STS) smoke detector')
correct('same_profiles-041',
        'Category changed missed_alarm -> measurement_limitation: "less effective detection by light scattering devices ... for some of the Teflon tests" describes reduced detection effectiveness, with no alarm outcome or count.',
        category='measurement_limitation')
correct('same_profiles-043',
        'Category changed missed_alarm -> measurement_limitation: the SAME report says CSD showed "poor detection" / "reduced signal" on the Shuttle detector; no alarm outcome is stated in the examined text.',
        category='measurement_limitation')
correct('same_profiles-047',
        'Category changed missed_alarm -> measurement_limitation: this is the authors\' inference from particle sizes ("will make detection ... challenging"), not an observed missed alarm.',
        category='measurement_limitation')
correct('same_profiles-054',
        'Table 1 on PDF p48 (layout-checked) lists a silicone geometric mean diameter of 0.189 um; only the silicone arithmetic mean and diameter of average mass are N/A. Summary said all silicone baseline values were N/A.',
        summary='In the preliminary 2009 Mie-iteration analysis some cases did not converge (authors suggest possibly bimodal distributions). Preliminary baseline values (GMD / arithmetic mean / Dm, um): Kapton 0.080/0.105/0.172, lamp wick 0.186/0.227/0.420, Teflon 0.159/0.205/0.219; silicone GMD listed as 0.189 with arithmetic mean and Dm given as N/A ("did not converge").')
correct('same_profiles-055',
        'Numbers (Table 1) are printed on PDF p57 (D-7), not on the anchor page p56; location updated. Added to scope: the source says all count mean diameters are 100-200 nm although its own table gives silicone 227 nm.',
        location='Appendix D (2008 ICES paper), p.D-6 text (PDF p56); Table 1 printed on PDF p57 (D-7)',
        scope_notes='Preliminary; differs from final Table 1 (e.g. Kapton arithmetic mean 105 nm final). Source-internal inconsistency: text says all CMDs are in the 100-200 nm range, but its Table 1 gives silicone 227 nm.')
correct('same_profiles-056',
        'INVENTED NUMBER REMOVED: the Teflon "% larger than 1-g" cell of Appendix E Table 1 (PDF p64) is blank (confirmed by word coordinates and a rendered crop); the "15" the extractor used is the superscript reference number of "Brooker et al.15" in the adjacent text column. Silicone 263/53, Teflon 223, lamp wick 248/65, Kapton 114/58 confirmed.',
        summary='Earliest (2008) count mean diameters for baseline runs, with % larger than comparable 1-g tests: silicone 263 nm (+53%), Teflon 223 nm (no percentage given - the cell is blank), lamp wick 248 nm (+65%), Kapton 114 nm (+58%).',
        numbers=[{'value': 263, 'unit': 'nm', 'meaning': 'silicone CMD', 'verbatim': '263'},
                 {'value': 53, 'unit': '%', 'meaning': 'silicone larger than 1-g', 'verbatim': '53'},
                 {'value': 223, 'unit': 'nm', 'meaning': 'Teflon CMD (no % vs 1-g given)', 'verbatim': '223'},
                 {'value': 248, 'unit': 'nm', 'meaning': 'lamp wick CMD', 'verbatim': '248'},
                 {'value': 65, 'unit': '%', 'meaning': 'lamp wick larger than 1-g', 'verbatim': '65'},
                 {'value': 114, 'unit': 'nm', 'meaning': 'Kapton CMD', 'verbatim': '114'},
                 {'value': 58, 'unit': '%', 'meaning': 'Kapton larger than 1-g', 'verbatim': '58'}],
        scope_notes='Only zeroth and first moment instruments used; values differ from later tables. 1-g comparison test details not given here. Teflon has no stated 1-g percentage.')
correct('same_profiles-063',
        'conditions.gravity held "lunar surface (stated need, not tested)", which is not a test condition of any evidence; set to null (lunar context kept in summary/scope).',
        conditions={'atmosphere_o2_vol_pct': None, 'pressure_kpa': None, 'airflow_cm_s': None,
                    'gravity': None, 'heating_s': None, 'aging_s': None})
correct('same_profiles-070',
        'Summary attached the "over a factor of 5 above typical indoor" comparison to the light-scattering readings; the source attributes it to the impactor results for the two most populated size ranges, with the light-scattering readings "supporting" them.',
        summary='STS-32 (1990) background: two cascade impactors (each about 15 m3 of air over about 30 h) found a bimodal distribution with about 40% of particles in each of the 2.5-10 um and >100 um ranges, at concentrations over 5x typical indoor levels for those two ranges; a light-scattering instrument supporting these data made 17 measurements in 12 locations, all 50-70 ug/m3.')
correct('same_profiles-073',
        'Category changed false_alarm -> measurement_limitation: the passage is a calculated response analysis for a hypothetical alarm requirement ("could indicate increased sensitivity to nuisance sources"), not an observed false alarm.',
        category='measurement_limitation')
correct('same_profiles-120',
        'The Kapton 98-100% figure is printed on PDF p19, the silicone 40%/60%/20% figures on PDF p20 (anchor page); location updated.',
        location='Limitations of Aerosol Instrument Measurement Ranges (ground SMPS), PDF pp19-20 incl. Fig. 23 (p20)')
correct('same_profiles-151',
        'Summary stated saturation "near about 6.25 V" as fact; Model C only says the approximately 6.25 V plateau is consistent with published saturation and that no precise cutoff should be invented.',
        summary='Model C notes an ISS scatter-signal plateau at approximately 6.25 V that it considers consistent with published saturation, but it set no precise saturation cutoff, left per-row saturation unresolved, and used only the 2.0 V threshold label.')

# ------------------------------------------------------------- apply to items
id2item = {it['item_id']: it for it in final['items']}
for it in final['items']:
    iid = it['item_id']
    t = page_text(it['doc_id'], it['pdf_page'])
    anchor_ok = norm(it['anchor_quote']) in norm(t)
    nwords = len(it['anchor_quote'].split())
    verdict, note, changes = V.get(iid, ('CONFIRMED', NOTE_DEFAULT, {}))
    if not anchor_ok or nwords > 15:
        verdict, note = 'REJECTED', f'Anchor not found on cited page or too long ({nwords} words). ' + note
    original = {}
    for k, v in changes.items():
        original[k] = it.get(k)
        it[k] = v
    it['verification'] = {'verdict': verdict, 'note': note, 'original': original}

# ------------------------------------------------------------ verifier items
NULLC = {'atmosphere_o2_vol_pct': None, 'pressure_kpa': None, 'airflow_cm_s': None,
         'gravity': None, 'heating_s': None, 'aging_s': None}


def C(**kw):
    c = dict(NULLC)
    c.update(kw)
    return c


new = [
    dict(doc_id='same_report', pdf_page=4, printed_page='iv', location='Abstract (p.iv); repeated in Appendix E abstract (PDF p59)',
         anchor_quote='mixing dominates the smoke transport and that consequently detection time lags are longer',
         summary='Abstract: the companion smoke-transport model of the ISS showed that mixing dominates smoke transport in low gravity and that, as a result, detection time lags are longer than in normal gravity (Appendix E, PDF p65, contrasts this with 1 g, where smoke concentrates near the ceiling).',
         category='context', investigation='SAME (FDS model)', materials=[], detector='ISS area smoke detectors (modelled)',
         numbers=[], conditions=C(gravity='0 (model)'), n_independent_tests=None,
         scope_notes='Numerical FDS model of the ISS US Lab (propane-burner source), not an experiment; no detection-time values are given in this sentence.'),
    dict(doc_id='same_report', pdf_page=9, printed_page='ix', location='Acronyms',
         anchor_quote='DAFT: Dust Aerosol measurement Feasibility Test, a precursor project of SAME',
         summary='The SAME final report\'s acronym list defines DAFT as the Dust Aerosol measurement Feasibility Test and calls it a precursor project of SAME; the report\'s only DAFT data are ISS US Lab background particle counts at instrument noise level (PDF p14).',
         category='context', investigation='DAFT', materials=[], detector=None, numbers=[], conditions=C(), n_independent_tests=None,
         scope_notes='Explicit SAME-DAFT link (precursor). The report does not say SAME instruments were flown in DAFT, and DAFT-2 is not mentioned in either final report or metadata (within the examined text). The P-Trak low-g modification was tested in "a separate space experiment" (same ref. 5 as the DAFT data) - plausibly DAFT but not stated.'),
    dict(doc_id='same_report', pdf_page=11, printed_page='1', location='Section 1 Introduction',
         anchor_quote='current spacecraft fire detectors were developed based upon experience on normal gravity fire behavior',
         summary='There was no spacecraft-fire data set comparable to terrestrial fire studies, so the existing spacecraft fire detectors were developed from normal-gravity fire experience; the authors call this necessary given the absence of microgravity smoke data.',
         category='context', investigation='STS/ISS (background)', materials=[], detector='ISS and STS smoke detectors (design basis)',
         numbers=[], conditions=C(), n_independent_tests=None,
         scope_notes='Design-basis statement. Appendix E (PDF p59) adds that no microgravity smoke measurements existed when the Shuttle and ISS detectors were designed, which led to two technologies with very different particle-size sensitivities.'),
    dict(doc_id='same_report', pdf_page=3, printed_page='iii', location='Abstract',
         anchor_quote='because of the relatively small volume of the MSG, it cannot accommodate the instruments',
         summary='The small volume of the Microgravity Science Glovebox could not hold the laboratory instruments normally used to measure smoke size distributions, so a "moment method" was developed that infers the size distribution from a minimum number of portable instruments, assuming a lognormal distribution.',
         category='measurement_limitation', investigation='SAME', materials=[], detector=None, numbers=[],
         conditions=C(gravity='microgravity (ISS, low Earth orbit)'), n_independent_tests=None,
         scope_notes='On-orbit constraint shared by SAME-R. Full size distributions were not measured in flight; lognormality was checked only in 1-g ground tests (see same_profiles-159).'),
    dict(doc_id='same_report', pdf_page=3, printed_page='iii', location='Abstract',
         anchor_quote='the preliminary results of CSD project were not conclusive because of a minor variation',
         summary='The SAME abstract says the earlier Shuttle-glovebox CSD experiment indicated larger low-g soot particles, but its preliminary results were not conclusive because of a minor variation in hot-wire temperature and because CSD could not measure the liquid drops in smoke from several samples; CSD was also not designed for on-orbit size-distribution measurement.',
         category='measurement_limitation', investigation='CSD (cited in SAME report)', materials=[], detector=None, numbers=[],
         conditions=C(), n_independent_tests=None,
         scope_notes='Secondhand description of CSD that motivated SAME; CSD primary reports not examined in this group.'),
    dict(doc_id='same_report', pdf_page=39, printed_page='B-5', location='Appendix B (2009 ICES paper), Detector Design Requirement Implications',
         anchor_quote='The requirement should represent the best understanding of spacecraft smoke conditions.',
         summary='Appendix B lists four overarching criteria for future spacecraft smoke-detector requirements: the requirement should not effectively define the technology, must be verifiable in a laboratory, must allow a subtest to qualify production units if the full test cannot be run on every unit, and should represent the best understanding of spacecraft smoke conditions. One option it examines is a requirement stating an aerosol condition at alarm.',
         category='recommendation', investigation='SAME', materials=[], detector=None, numbers=[], conditions=C(), n_independent_tests=None,
         scope_notes='Requirements-writing criteria proposed by the authors; the follow-on single-point-requirement analysis is item same_profiles-073/074/075.'),
    dict(doc_id='samer_report', pdf_page=9, printed_page=None, location='SAME Smoke-in-Drums Ground-Based Experiment',
         anchor_quote='This cannot be accomplished in low gravity, so this investigation was performed with the ground-based',
         summary='Checking whether smoke size distributions are lognormal required detailed distributions from a reference instrument (an SMPS), which the authors state cannot be done in low gravity; the check was therefore made on the ground with the identical engineering SAME hardware and the returned flight aerosol instruments. Because the SMPS needs a two-minute scan and the aging chamber supplies smoke for at most 30 s, smoke was buffered in 55-gallon drums.',
         category='measurement_limitation', investigation='SAME-R ground test', materials=['Teflon', 'Kapton', 'silicone rubber', 'lamp wick (cellulose)', 'Pyrell'],
         detector='SMPS (TSI 3936) reference', numbers=[
             {'value': 2, 'unit': 'min', 'meaning': 'SMPS scan duration', 'verbatim': 'two minute scan'},
             {'value': 30, 'unit': 's', 'meaning': 'maximum smoke supply duration from aging chamber', 'verbatim': 'at most 30 seconds'},
             {'value': 55, 'unit': 'gallon', 'meaning': 'buffer drum size', 'verbatim': '55 gallon drum'}],
         conditions=C(gravity='1-g (ground)'), n_independent_tests=None,
         scope_notes='Lognormality was not verified with flight data; the ground (1 g) check found Kapton and lamp wick lognormal, silicone not (items 118-119).'),
    dict(doc_id='samer_report', pdf_page=9, printed_page=None, location='D. Impact of flow on particle morphology (zero-flow), Fig. 13',
         anchor_quote='change in the morphology of the Pyrell smoke from fractal-like clusters with up to 30',
         summary='With no flow, heat moves mainly by conduction, which the authors say is likely to raise the gas temperature substantially compared with 8 cm/s flow; a striking result is that Pyrell smoke changed from fractal-like clusters of up to 30 primary spheres at 8 cm/s to spherical particles with no flow (Fig. 13: run 63 vs run 95).',
         category='particle_property', investigation='SAME-R', materials=['Pyrell'], detector='TEM', numbers=[
             {'value': 30, 'unit': 'primary spheres', 'meaning': 'max primaries per cluster at 8 cm/s', 'verbatim': 'up to 30'},
             {'value': 8, 'unit': 'cm/s', 'meaning': 'comparison flow', 'verbatim': '8 cm/s'}],
         conditions=C(airflow_cm_s=0, gravity='microgravity (ISS, low Earth orbit)'), n_independent_tests=None,
         scope_notes='TEM images of individual runs (63 at 8 cm/s, 95 at zero flow); the gas-temperature rise is the authors\' "likely" explanation, not a measurement.'),
    dict(doc_id='samer_report', pdf_page=14, printed_page=None, location='Ground TEM test: Comparison with drum test results (PDF p14; Fig. 18 on p15)',
         anchor_quote='have a similar spread but do not agree well in the peak location',
         summary='Ground lamp wick comparison (two tests with heating temperatures within 0.6 degC): TEM (17 images, 4668 particles) and SMPS volume distributions had similar spread but disagreed on peak location; counting faint TEM particles without thresholding lowered the TEM geometric mean diameter and widened its sigma_gn relative to SMPS (Fig. 18 on p15: SMPS dgn 248 nm vs TEM 131 nm). The SMPS distribution stops at 1000 nm while TEM has no upper limit.',
         category='measurement_limitation', investigation='SAME-R ground test', materials=['lamp wick (cellulose)'], detector='TEM; SMPS', numbers=[
             {'value': 0.6, 'unit': 'degC', 'meaning': 'max heating-temperature difference between compared tests', 'verbatim': 'within 0.6'},
             {'value': 17, 'unit': 'images', 'meaning': 'TEM images processed', 'verbatim': '17 images'},
             {'value': 4668, 'unit': 'particles', 'meaning': 'TEM particles counted', 'verbatim': '4668 particles'}],
         conditions=C(gravity='1-g (ground)'), n_independent_tests=None,
         scope_notes='Ground test of one material; dgn values 248/131 nm are printed on PDF p15 (Fig. 18 caption).'),
    dict(doc_id='samer_report', pdf_page=18, printed_page=None, location='TEM Particle Morphology Results from Flight Tests (p.18)',
         anchor_quote='it was thought that pyrolysis smoke was made up of spherical droplets',
         summary='The authors note that before this work pyrolysis smoke was thought to consist of spherical droplets; the SAME-R TEM images of Teflon and Pyrell agglomerates contradict that for those materials (a companion paper explains agglomerate formation).',
         category='particle_property', investigation='SAME-R', materials=['Teflon', 'Pyrell'], detector='TEM', numbers=[],
         conditions=C(gravity='microgravity (ISS, low Earth orbit)'), n_independent_tests=None,
         scope_notes='Morphology finding relevant to the spherical-particle assumptions of the moment method and of scattering-detector calibration.'),
    dict(doc_id='samer_report', pdf_page=28, printed_page=None, location='Cumulative moments for limited particle size range',
         anchor_quote='the instrument cannot sense the entire range of the distribution as the theory describes',
         summary='Each moment instrument has a limited particle-size range (some also have inlet impactors that remove larger particles), so it cannot sense the whole lognormal distribution; SAME-R derived an error-function formula for the fraction of each moment an instrument captures between its lower and upper size limits, to improve uncertainty analysis.',
         category='measurement_limitation', investigation='SAME/SAME-R', materials=[], detector='moment instruments (P-Trak, ionization chamber, DustTrak)', numbers=[],
         conditions=C(), n_independent_tests=None,
         scope_notes='Method only; in the examined text it is applied to the ground SMPS range (PDF pp19-20), not used to correct flight detector signals.'),
]

next_n = max(int(it['item_id'].rsplit('-', 1)[1]) for it in final['items']) + 1
for k, ni in enumerate(new):
    iid = f'same_profiles-{next_n + k:03d}'
    item = {'item_id': iid}
    item.update(ni)
    t = page_text(item['doc_id'], item['pdf_page'])
    ok = norm(item['anchor_quote']) in norm(t) and len(item['anchor_quote'].split()) <= 15
    if not ok:
        sys.exit(f'added item {iid} anchor failed')
    item['added_by_verifier'] = True
    item['verification'] = {'verdict': 'CONFIRMED', 'note': 'Added by verifier; anchor checked verbatim (whitespace-normalised) on the cited page.', 'original': {}}
    final['items'].append(item)

# ------------------------------------------------------------- doc-level info
for doc in final['documents']:
    ok, h = raw_check[doc['doc_id']]
    doc['verification'] = {
        'verdict': 'CONFIRMED' if ok else 'REJECTED',
        'note': ('Raw file exists; recomputed sha256 matches documents[] and sources/raw/<doc_id>/meta.json'
                 + (' and source_manifest.json' if doc['doc_id'] in ('same_report', 'samer_report', 'psi101_meta', 'psi102_meta', 'same_csv', 'samer_csv') else ' (project artifact, not in manifest)')
                 + '. Title/authors/year checked against the cover page or file.' if ok else f'sha256 mismatch: {h}'),
        'original': {}}

final['verification_summary'] = {
    'verifier_role': 'adversarial verifier for source group same_profiles',
    'checks': [
        'sha256 of all 9 underlying files recomputed; the 6 NASA files also match external/model_c/data/raw/source_manifest.json; combined workbook sha256 also matches manifest',
        'sources/text/same_report.txt and samer_report.txt regenerated with plain pdftotext and found byte-identical; CSV and Model C text copies byte-identical to raw files',
        'every anchor re-checked (whitespace-normalised, case-sensitive) on its cited page; every number verbatim checked on page; off-page verbatims inspected manually',
        'Appendix A tables (SAME p33; SAME-R pp31-49) re-read with pdftotext -layout column alignment; Appendix E Table 1 (SAME p64) checked with pdfplumber word coordinates and a rendered crop',
    ],
}
final['search_log'].append({
    'query': 'case-insensitive regex for kPa|psi|pressure|O2|oxygen|atmospher|cabin|nitrogen|N2|lunar|Moon|Mars|partial gravity|false alarm|nuisance|DAFT|2.0 V|threshold|dust',
    'where': 'verifier: sources/text/same_report.txt and samer_report.txt (page-level)',
    'hits': 70,
    'notes': 'Correction to the extractor\'s case-sensitive "atmospher" search (0 hits): "Atmosphere" occurs in the SAME Appendix E heading "Spacecraft Atmosphere Dust Background" (PDF p61). No test-gas O2 or pressure value found in either report; DAFT-2 appears nowhere.'})
final['search_log'].append({
    'query': 'layout re-parse of Appendix A run tables',
    'where': 'verifier: pdftotext -layout on SAME p33 and SAME-R pp31-49 (scratch output only)',
    'hits': 2,
    'notes': 'Confirmed 47 SAME tests (30 initial/17 reheat), SAME-R STS flags on 17 primary runs, reburns 57 (L14) and 90 (of 85), run 112 Kapton.'})
final['open_questions'] = list(final['open_questions']) + [
    'Appendix E Table 1 (SAME p64) gives no 1-g percentage for Teflon (blank cell); is the Teflon 1-g comparison reported in the original 2008 AIAA paper or elsewhere?',
    'Model C\'s 17 SAME primary runs omit the flight-log non-DBP initial heatings of tests 1, 6, 7, 8, 13, 14 and 17 (carousels 1-2). Were these excluded for data-quality reasons (e.g. test 8 abort) or missing from the workbook?',
    'SAME-R Appendix C notes "Red text indicates a repeated test due to the astronaut\'s error"; which runs were repeats cannot be read from extracted text (visual check of PDF pp51-52 needed).',
    'PSI-101 metadata $.experimentHardware also lists the CSD hardware ("Refer to final report"); flag together with the PSI-102 approach/hardware mismatch.',
]

OUT.write_text(json.dumps(final, indent=1, ensure_ascii=False) + '\n')
from collections import Counter
print('items', len(final['items']), Counter(i['verification']['verdict'] for i in final['items']))
print('added', sum(1 for i in final['items'] if i.get('added_by_verifier')))
print('docs', [(x['doc_id'], x['verification']['verdict']) for x in final['documents']])
