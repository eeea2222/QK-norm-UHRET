import json, os, re, hashlib, glob, subprocess, sys

ROOT = '/home/efeai/Desktop/NasaSpaceApps/sources'
HERE = os.path.dirname(os.path.abspath(__file__))
SK = 'ntrs_followup'
RETRIEVED = None
# raw-file write time is used as retrieval time (PDFs: curl download; web excerpts: written right after the Exa fetch)
RETRIEVED_OVERRIDE = {'ices2025_361_dusttolerant': '2026-11-15T10:55:00Z', 'ices2025_halo_sd_threshold': '2026-11-15T10:58:00Z'}

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

# ---------------------------------------------------------------- documents
DOCS = [
 dict(doc_id='ntrs_20205003817', title='Spacecraft Smoke Detector Characterization with Reference and Smoke Aerosols', year=2020,
      authors=['Xiaoliang Wang','Judith C. Chow','John G. Watson','Marit E. Meyer','Gary Ruff','John Easton','Gordon Berger','Paul D. Mudgett'],
      url='https://ntrs.nasa.gov/api/citations/20205003817/downloads/ICES_Final_340.pdf', raw='ICES_Final_340.pdf',
      identifiers=dict(doi=None, ntrs='20205003817', psi=None, pmc=None, other=['ICES-2020-340','hdl:2346/86366']),
      license_note='NTRS public distribution (copyright determination GOV_PERMITTED); ICES 2020 conference paper, DRI/NASA GRC authors.',
      accessible=True, access_note='Full PDF downloaded from NTRS; text via plain pdftotext.'),
 dict(doc_id='ntrs_20205000063', title='Spacecraft Fire Safety Technology Development Plan For Exploration Missions', year=2020,
      authors=['Gary A. Ruff','David L. Urban','Daniel L. Dietrich'],
      url='https://ntrs.nasa.gov/api/citations/20205000063/downloads/ICES-2020_173%20Fire%20Safety%20revised%20final%20manuscript%20-%202020%2007%2020.pdf',
      raw='ICES-2020_173 Fire Safety revised final manuscript - 2020 07 20.pdf',
      identifiers=dict(doi=None, ntrs='20205000063', psi=None, pmc=None, other=['ICES-2020-173']),
      license_note='US Government work (NASA GRC authors); no US copyright claimed per manuscript notice.',
      accessible=True, access_note='Full PDF from NTRS. Roadmap Figs. 1-4 (pp. 8-9) are images; their content is not in the text layer and was not extracted.'),
 dict(doc_id='ntrs_20230013826', title='The Influence of Smoke Particle Properties and Cabin Characteristics on Smoke Detection in Lunar Gravity', year=2023,
      authors=['Claire Fortenberry','Ramaswamy Balasubramaniam','David Urban'],
      url='https://ntrs.nasa.gov/api/citations/20230013826/downloads/AAAR%202023%20v1.pdf', raw='AAAR 2023 v1.pdf',
      identifiers=dict(doi=None, ntrs='20230013826', psi=None, pmc=None, other=['AAAR 2023 poster']),
      license_note='NTRS public distribution; NASA GRC/USRA/CWRU poster.',
      accessible=True, access_note='One-page poster PDF from NTRS; plot contents (images) were not quantitatively extracted, only text-layer statements are used.'),
 dict(doc_id='ntrs_20260005612', title='Early Fire Detection System for Partial and Low Gravity Environments', year=2026,
      authors=['Francisco J. Guzman','Timothy Krause','Mona Matar','Matthew Prelich','David Urban'],
      url='https://ntrs.nasa.gov/api/citations/20260005612/downloads/Guzman_GRC2026_FireDetection_v1bREV.pdf', raw='Guzman_GRC2026_FireDetection_v1bREV.pdf',
      identifiers=dict(doi=None, ntrs='20260005612', psi=None, pmc=None, other=['GRC 2026 poster']),
      license_note='NTRS public distribution; NASA GRC poster (funded by NASA Fire Detection System Project under ESDMD).',
      accessible=True, access_note='One-page poster PDF from NTRS; time-series plots are images and were not digitised; only text-layer statements are used.'),
 dict(doc_id='ntrs_20260001992', title='Heat and Smoke Emission from Tests on the SAFFIRE IV-VI Experiments (NTRS record title: Heat and Smoke Emission from Tests on the Saffire VI Experiment)', year=2026,
      authors=['David L. Urban','Gary A. Ruff','Paul Ferkul','John Easton','Jay Owens','Sandra Olson','Claire Fortenberry','John Graf','Oageng George','Balazs Toth','Florian Meyer','Christian Eigenbrod',"James S. T'ien",'Ya-Ting T. Liao','A. Carlos Fernandez-Pello','Guillaume Legros','Augustin Guibaud','Nickolay Smirnov','Osamu Fujita','Ulises Rojas Alva','Grunde Jomaas'],
      url='https://ntrs.nasa.gov/api/citations/20260001992/downloads/ICES%20Saffire%202026%2005%2004%20b.pdf', raw='ICES Saffire 2026 05 04 b.pdf',
      identifiers=dict(doi=None, ntrs='20260001992', psi=None, pmc=None, other=['ICES-2026-577']),
      license_note='NTRS public distribution; ICES 2026 conference paper (NASA GRC lead, international co-authors).',
      accessible=True, access_note='Full PDF from NTRS; Table 1 parsed from text layer (column order verified against the PDF table layout).'),
 dict(doc_id='ntrs_20260003174', title='The Operational NASA Anomaly Gas Analyzer and Exploration Follow-Ons', year=2026,
      authors=['Nicholas R. Wymore','Brian P. Rodrigue','Jeffrey S. Pilgrim'],
      url='https://ntrs.nasa.gov/api/citations/20260003174/downloads/AGA%20Paper%20with%20ICES%20Header%20post%20Review.pdf', raw='AGA Paper with ICES Header post Review.pdf',
      identifiers=dict(doi=None, ntrs='20260003174', psi=None, pmc=None, other=['ICES-2026-266']),
      license_note='NTRS public distribution; NASA JSC / Vista Photonics authors.',
      accessible=True, access_note='Full PDF from NTRS. Table 1 limit-of-quantitation column is scrambled in the text layer; only accuracy and range columns are used.'),
 dict(doc_id='ices2025_361_dusttolerant', title='Towards Dust-tolerant Smoke Detection in Future Space Missions', year=2025,
      authors=['Marit E. Meyer','Thorsten R. P. Schultze','Jan C. Balzer'],
      url='https://doi.org/10.32865/2346/102771', raw='exa_render_excerpt.txt',
      identifiers=dict(doi='10.32865/2346/102771', ntrs=None, psi=None, pmc=None, other=['ICES-2025-361','hdl:2346/102771']),
      license_note='(c) 2025 Northrop Grumman Systems Corporation and Univ. Duisburg-Essen; open repository (TTU ICES). Not a NASA-authored document: first author at Northrop Grumman (formerly NASA GRC). Stored only as verbatim excerpts for private evidence extraction.',
      accessible=True, access_note='PDF not retrievable with curl (TTU repository returned HTTP 403/202 bot challenge). Text obtained via Exa web_fetch rendering of the DOI landing page; raw file and text file are a verbatim EXCERPT of that rendering ([...] marks omissions; nomenclature, figures and references omitted). sha256/bytes refer to the excerpt file, not the original PDF; no PDF page numbers available.'),
 dict(doc_id='ices2025_halo_sd_threshold', title='Approach for Defining an Acceptable Threshold Range for Smoke Detection in the HALO Environment', year=2025,
      authors=['Robert Van Hassel','Marit E. Meyer','Catherine Keen'],
      url='https://ttu-ir.tdl.org/server/api/core/bitstreams/068487fa-2e03-415d-8151-9326f18ab653/content', raw='exa_render_excerpt.txt',
      identifiers=dict(doi=None, ntrs=None, psi=None, pmc=None, other=['ICES 2025 (paper number not shown in rendering)','Approved for Public Release NG25-0826']),
      license_note='(c) 2025 Northrop Grumman Systems Corporation; approved for public release NG25-0826. Industry (Northrop Grumman / Paragon) paper with NASA GRC input, not a NASA-authored document. Stored only as verbatim excerpts.',
      accessible=True, access_note='PDF bitstream blocked for curl (HTTP 202 bot challenge). Text via Exa web_fetch of the bitstream URL; raw/text files are a verbatim EXCERPT ([...] marks omissions; most tables and appendix omitted). sha256/bytes refer to the excerpt file; no PDF page numbers available.'),
]

# ---------------------------------------------------------------- helpers
def N(value, unit, meaning, verbatim):
    return dict(value=value, unit=unit, meaning=meaning, verbatim=verbatim)

def C(o2=None, p=None, flow=None, g=None, heat=None, age=None):
    return dict(atmosphere_o2_vol_pct=o2, pressure_kpa=p, airflow_cm_s=flow, gravity=g, heating_s=heat, aging_s=age)

ITEMS = []
def I(doc, page, printed, loc, anchor, summary, cat, inv=None, mats=None, det=None, nums=None, cond=None, n=None, scope=''):
    ITEMS.append(dict(doc_id=doc, pdf_page=page, printed_page=printed, location=loc, anchor_quote=anchor, summary=summary,
                      category=cat, investigation=inv, materials=mats or [], detector=det, numbers=nums or [],
                      conditions=cond or C(), n_independent_tests=n, scope_notes=scope))

G1 = '1g (ground laboratory)'

# ================= ntrs_20205003817 (ICES-2020-340) =================
D = 'ntrs_20205003817'
I(D, 1, None, 'Abstract', 'Although no single reference aerosol can be used to simulate the response',
  'Ground study testing whether laboratory reference aerosols can act as transfer standards for spacecraft smoke detector testing. Mineral oil (Gemini 501B tester) and DOS (atomizer, 1.5-100% solutions) together spanned the detector-response range of six smokes from oxidative pyrolysis of spacecraft-relevant materials, but no single reference aerosol reproduced the response of the different detection technologies to the different smokes within +/-10%; the derived reference-to-smoke relationships are proposed as conversion factors.',
  'followup_solution', None, ['mineral oil','DOS','PSL','lamp wick (cotton)','Kapton','Nomex','Teflon (PTFE)','PMMA','fluoropolymer/polyimide wire insulation'],
  'CSP light-scattering prototype; IonZG ionization; ISS scatter detector; STS ionization detector; obscuration meter (plus Kidde consumer alarms)',
  [N(10,'%','accuracy target that no single reference aerosol met across detectors and smokes','±10%')], C(g=G1), None,
  'Applies to ground tube-furnace oxidative pyrolysis smokes in a 326-L chamber, not flaming fires, not low gravity. Concentration reference is the DustTrak DRX PM2.5 reading, itself size/composition dependent.')
I(D, 2, '2', 'Sec. I Introduction', 'Although there is no established standard for spacecraft smoke detectors',
  'The authors note that, unlike consumer alarms regulated by UL 217, there is no established performance standard for spacecraft smoke detectors; they are tested with methods similar to UL 217 but using fuels representative of spacecraft materials.',
  'context', None, [], None, [], C(), None, 'Statement about the standards landscape as of 2020; see HALO 2025 paper for a later restatement.')
I(D, 3, '3', 'Sec. II.A Experimental Setup', 'A Commercial Space Prototype (CSP) smoke detector based on light scattering was co-located',
  'Experiments in the GASP laboratory at NASA GRC: reference or smoke aerosols were injected into a 326-L mixed chamber. A light-scattering Commercial Space Prototype (CSP) detector and a commercial ionization detector (IonZG) were logged at 10 Hz; two Kidde consumer alarms (ionization and photoelectric) were logged only as alarm state; a second sample line fed the ISS light-scattering detector and the STS ionization detector, which have no pump and were drawn by a fan. A DustTrak DRX (655 nm laser scattering) served as concentration reference, plus an ASTM E662 obscuration meter; smoke came from a tube furnace flushed with 4.4 L/min filtered air.',
  'test_condition', None, [], 'CSP; IonZG; Kidde I12010S (ionization); Kidde P3010H (photoelectric); ISS scattering smoke detector; STS ionization smoke detector',
  [N(326,'L','smoke chamber volume','326-L'), N(10,'Hz','logging rate of CSP and IonZG analog outputs','10 Hz'), N(4.4,'L/min','filtered air flow through tube furnace','4.4 L/min'), N(655,'nm','DRX laser wavelength','655 nm')],
  C(g=G1), None, 'Ground laboratory; detectors were exposed through different sampling lines, so time series were aligned by correlation with the DRX.')
I(D, 3, '3', 'Sec. II.A Experimental Setup (instrument limitation)', 'Due to fast changing particle size distributions, the SMPS was not used during smoke tests.',
  'Particle size distributions (SMPS, about 0.01-0.7 um) were measured only for reference aerosols; during smoke tests size distributions were not measured, so detector comparisons for smoke rely on the DRX PM2.5 mass reading, which the authors note is less sensitive to particles below about 300 nm and may underestimate PM2.5 for small particles.',
  'measurement_limitation', None, [], 'SMPS (TSI 3938); DustTrak DRX', [N(0.01,'um','SMPS lower size limit','~0.01–0.7 µm'), N(0.7,'um','SMPS upper size limit','~0.01–0.7 µm'), N(300,'nm','size below which DRX is less sensitive (stated on p.7)','≲300 nm')],
  C(g=G1), None, '(iii) particle-size coverage: no size-resolved smoke data in this study. DRX statement is on PDF p.7.')
I(D, 4, '4', 'Sec. II.B Reference Aerosol Materials', 'it was difficult to generate high concentrations of <500 nm monodisperse particles',
  'Monodisperse DOS particles below about 500 nm, and PSL spheres (300, 500, 900 nm), could not be generated at the concentrations needed to produce reliable smoke detector signals; PSL results were therefore excluded. Larger monodisperse DOS (500 and 700 nm) was feasible.',
  'measurement_limitation', None, ['DOS','PSL'], None, [N(500,'nm','size below which high-concentration monodisperse DOS was difficult','<500 nm'), N(300,'nm','PSL size attempted','300 nm'), N(900,'nm','PSL size attempted','900 nm')],
  C(g=G1), None, '(iii) limits size-resolved (monodisperse) detector characterization for the small-particle range; reference aerosols only, not smoke.')
I(D, 4, '4', 'Sec. II.C Smoke Aerosol Materials (continues p.5)', 'Six types of materials relevant to spacecraft safety were tested',
  'Smoke was generated by oxidative pyrolysis of six spacecraft-relevant materials in a tube furnace: cotton lamp wick (3 tests, 0.75-1 g, 200-240 C), Kapton (3 tests, 1-2 g, 450-500 C), Nomex (3 tests, 0.5-1 g, 350-400 C), Teflon/PTFE (3 tests, about 8 g, 400-500 C), PMMA (1 test, 2 g, 200 C) and fluoropolymer/polyimide wire insulation (1 test, 2 g, 450 C).',
  'test_condition', None, ['lamp wick (cotton)','Kapton','Nomex','Teflon (PTFE)','PMMA','fluoropolymer/polyimide wire insulation'], None,
  [N(3,'tests','Kapton tests','Three Kapton tests'), N(450,'°C','Kapton furnace setpoint lower','450–500 °C'), N(500,'°C','Kapton furnace setpoint upper','450–500 °C'),
   N(3,'tests','Teflon tests','Three Teflon tests'), N(8,'g','Teflon sample mass (approx.)','~8 g'), N(400,'°C','Teflon furnace setpoint lower','400–500 °C'), N(500,'°C','Teflon furnace setpoint upper','400–500 °C'),
   N(3,'tests','lamp wick tests','Three lamp wick tests'), N(3,'tests','Nomex tests','Three Nomex tests'), N(1,'tests','PMMA tests','One PMMA test'), N(1,'tests','wire insulation tests','One wire insulation test')],
  C(g=G1), 14, '(i) Kapton and Teflon smokes are included. Smoldering/oxidative pyrolysis only (no flaming); 1-3 tests per material, PMMA and wire insulation single tests.')
I(D, 7, '7', 'Sec. III.A, Fig. 4d', 'saturated at ~6 V with higher PM2.5 concentrations',
  'With mineral-oil reference aerosol, the ISS light-scattering detector signal rose linearly to about 4 V at about 50 mg/m3 (DRX PM2.5) and saturated at about 6 V above roughly 70 mg/m3; its data from one of the three test days were invalidated by a transfer-line leak.',
  'measurement_limitation', None, ['mineral oil'], 'ISS scatter detector',
  [N(4,'V','approximate end of linear range','~4 V'), N(50,'mg/m3','DRX PM2.5 at end of linear range','~50 mg/m3'), N(6,'V','saturation voltage','~6 V'), N(70,'mg/m3','DRX PM2.5 above which saturation observed','≳70 mg/m3')],
  C(g=G1), 2, 'Reference aerosol (mineral oil), two valid test days; saturation also seen with DOS (p.7) and smoke (Fig. 7). Not a statement about alarm-threshold behaviour.')
I(D, 7, '7', 'Sec. III.B, Fig. 6e', 'probably due to the extra plumbing and lack of a pump causing non-uniform concentrations',
  'For DOS aerosols the ISS scatter detector was approximately linear only between about 1 and 15 mg/m3, showed more scatter than other detectors (attributed by the authors probably to extra plumbing and no pump), and its signal rose faster for larger particles than for smaller ones at equal DRX PM2.5.',
  'measurement_limitation', None, ['DOS'], 'ISS scatter detector',
  [N(1,'mg/m3','lower end of approximately linear range','~1-15 mg/m3'), N(15,'mg/m3','upper end of approximately linear range','~1-15 mg/m3')],
  C(g=G1), None, '(iii) size-dependent response of the ISS forward-scatter detector; reference aerosol (DOS), ground test.')
I(D, 7, '7', 'Sec. III.B, Fig. 6c-d', 'this detector had low signal-to-noise ratio for concentration ≲5 mg/m3',
  'The STS ionization detector signal decreased roughly linearly with DRX PM2.5 up to about 80 mg/m3, became nonlinear above about 200 mg/m3, had low signal-to-noise below about 5 mg/m3, and, like the commercial IonZG, responded more per unit mass to smaller particles.',
  'measurement_limitation', None, ['DOS'], 'STS ionization detector',
  [N(80,'mg/m3','approximate upper end of linear decrease','~80 mg/m3'), N(200,'mg/m3','level above which signal nonlinear','~200 mg/m3'), N(5,'mg/m3','level below which SNR was low','≲5 mg/m3')],
  C(g=G1), None, '(iii) ionization detectors favour small particles; DOS reference aerosol, ground test.')
I(D, 8, '8', 'Sec. III.C, Fig. 7', 'The light scattering smoke alarm (Kidde P3010H) was triggered earlier and ended later',
  'In the example smoldering lamp-wick test, all instruments responded; light-scattering instruments rose linearly with smoke while ionization instruments decreased nonlinearly, the STS ion and ISS scatter detectors saturated at higher concentrations, and the photoelectric consumer alarm triggered earlier and cleared later than the ionization consumer alarm.',
  'context', None, ['lamp wick (cotton)'], 'Kidde P3010H; Kidde I12010S; STS ion; ISS scatter', [], C(g=G1), 1,
  'Single illustrative smoldering lamp-wick run with consumer alarms; not a general ranking of detector technologies.')
I(D, 9, '9', 'Sec. III.C, Fig. 8', 'it uses a near infrared laser and measures forward light scattering (30°)',
  'Across reference and smoke aerosols the slope of detector response vs DRX PM2.5 varied least for the CSP detector (COV 13%) and more for the obscuration meter (26%) and the ISS scatter detector (35%); the authors attribute the ISS detector spread to its different optics (near-infrared laser, 30 degree forward scatter) and earlier saturation. ISS scatter responses to smoke differed from reference aerosols by more than 10% except for PMMA, and mineral oil would underestimate its smoke response by more than a factor of three.',
  'measurement_limitation', None, ['lamp wick (cotton)','Kapton','Nomex','Teflon (PTFE)','PMMA','wire insulation'], 'ISS scatter detector; CSP; obscuration meter',
  [N(13,'%','COV of CSP-vs-DRX slopes across aerosols','COV = 13%'), N(26,'%','COV for obscuration meter','COV = 26%'), N(35,'%','COV for ISS scatter detector','COV = 35%'), N(30,'deg','ISS detector forward scattering angle','(30°)'), N(3,'factor','underestimate of ISS scatter smoke response if mineral oil used','a factor of over three')],
  C(g=G1), 14, '(iii) detector-specific particle-size/optical sensitivity; ground smoldering smokes; slopes relative to DRX, not alarm times.')
I(D, 9, '9', 'Sec. III.C, Table 1 discussion', 'Teflon particles generated the highest slope among all tested materials',
  'For the obscuration meter, Teflon smoke gave the highest response slope of all materials (16% above 100% DOS); for the CSP detector, 5% DOS predicted smoke responses within +/-10% except an approximately 20% overestimate for Teflon, while mineral oil represented Teflon well but underestimated most other smokes by 20-35%.',
  'particle_property', None, ['Teflon (PTFE)','Kapton','mineral oil','DOS'], 'obscuration meter; CSP',
  [N(16,'%','Teflon obscuration slope above 100% DOS','16% higher'), N(20,'%','overestimate of Teflon response by 5% DOS (CSP)','~20% overestimation'), N(20,'%','lower bound of mineral-oil underestimate (CSP)','20–35%'), N(35,'%','upper bound of mineral-oil underestimate (CSP)','20–35%')],
  C(g=G1), 3, '(i) Teflon/Kapton smokes: shows smoke-type-dependent detector response; based on 3 Teflon furnace tests; not a missed-alarm result.')
I(D, 11, '11', 'Sec. IV Conclusion', 'which should be increased to improve the signal resolution and reliability',
  'The CSP prototype was linear from below 1 to about 200 mg/m3 and sensitive at low smoke levels (signal-to-noise about 73-110 at 1%/m obscuration for mineral oil), but used only a narrow voltage band (about 0.96 V baseline, up to about 3 V at 30%/m obscuration); the authors recommend widening this range.',
  'measurement_limitation', None, ['mineral oil','DOS'], 'CSP (Commercial Space Prototype) light-scattering detector',
  [N(0.96,'V','baseline at 0%/m obscuration','~0.96 V'), N(3,'V','signal at 30%/m obscuration (upper bound)','≲ 3 V'), N(200,'mg/m3','upper end of linear range','200 mg/m3')],
  C(g=G1), None, 'Prototype detector design recommendation; reference aerosols mainly.')
I(D, 11, '11', 'Sec. IV Conclusion (future work, continues p.12)', 'Future work should experimentally verify the applicability of the derived conversion factors.',
  'The authors call for experimental verification of the reference-to-smoke conversion factors and for measuring smoke size distributions and optical properties, combined with light scattering and absorption modelling, to explain detector differences and guide detector optimisation.',
  'research_question', None, [], None, [], C(), None, 'Forward-looking statement; (iii) size/optical characterization of smoke identified as a need.')

# ================= ntrs_20205000063 (ICES-2020-173) =================
D = 'ntrs_20205000063'
I(D, 1, None, 'Abstract', 'increased oxygen concentrations, partial gravity conditions and the presence of surface dust',
  'Missions beyond low Earth orbit will extend fire-safety conditions beyond NASA\'s five-decade experience to include long durations, dormancy, elevated oxygen, partial gravity and surface dust, all of which can affect fire safety system design.',
  'context', None, [], None, [], C(), None, '(iv) frames elevated O2 / partial gravity / dust as new conditions; programmatic statement, not test data.')
I(D, 2, '2', 'Sec. I.A.2 Prior Detection and Suppression Systems', 'both systems were adapted from terrestrial systems for spacecraft applications without verification',
  'Because no data existed on smoke particle sizes in low gravity or on reference fire sizes, Shuttle-era and later detection and suppression systems were adapted from terrestrial practice without verifying their effectiveness in low gravity; detectors were placed where ventilation ensures sampling, but the effect of the well-mixed cabin on detection threshold was not considered.',
  'context', None, [], 'spacecraft smoke detection systems (Shuttle, ISS)', [], C(), None, 'Historical design-basis statement.')
I(D, 2, '2', 'Sec. I.A.2', 'with the ISS detectors more sensitive to larger particles while the Shuttle detectors',
  'The Shuttle and ISS smoke detectors had quite different particle-size sensitivities: the ISS detectors were more sensitive to larger particles, whereas the Shuttle detectors were designed to reject larger particles; the change followed available terrestrial technology rather than data on target fires.',
  'measurement_limitation', None, [], 'STS (Shuttle) and ISS smoke detectors', [], C(), None, '(iii) particle-size coverage differs by detector; qualitative.')
I(D, 3, '3', 'Sec. I.B.1 Fire Detection Issues (p.2-3)', 'accumulation of hazardous compounds while alarm triggering is delayed',
  'In well-mixed spacecraft cabins smoke is diluted so roughly the whole volume must reach alarm level, and HEPA filtration removes smoke particles so concentration builds more slowly; filters may not remove hazardous gases, so toxic products can accumulate while the smoke alarm is delayed. Earlier modelling found that in many cases hazardous levels of products from multiple materials accumulated before the alarm threshold.',
  'measurement_limitation', None, [], 'ISS and STS smoke detectors (modelled)', [], C(), None,
  'Based on cited modelling (Urban et al. ICES-2016-318), not on a measured missed alarm. Applies to microgravity, well-mixed, HEPA-filtered cabins.')
I(D, 3, '3', 'Sec. I.B.1', 'the detection time could vary by over 2 minutes',
  'A cited ISS Destiny laboratory model (Brooker et al.) showed that, for moderate smoke production rates, detection time could vary by more than two minutes depending on configuration.',
  'measurement_limitation', None, [], None, [N(2,'min','variation in detection time in ISS Destiny model','over 2 minutes')], C(g='microgravity (model)'), None, 'Model result cited from 2007 work; location dependence of detection.')
I(D, 3, '3', 'Sec. I.B.1', 'spacecraft fire detection thresholds should not be based on terrestrial levels or on other spacecraft',
  'The authors conclude that detection thresholds must be chosen for each vehicle volume and its air filtration and ventilation, with the interacting systems usually modelled in detail, rather than copied from terrestrial practice or other spacecraft.',
  'recommendation', None, [], None, [], C(), None, 'Design recommendation derived from modelling studies.')
I(D, 4, '4', 'Sec. I.C Future mission changes', 'the presence of buoyant flow will dominate the smoke transport even at Lunar g-levels',
  'Designing for reliable detection in both low gravity and on planetary surfaces is described as particularly challenging because buoyancy will dominate smoke transport even at lunar gravity, so detection design choices are expected to differ substantially between environments; more EVAs also bring more cabin dust and higher-oxygen environments.',
  'technology_need', None, [], None, [], C(g='lunar / partial gravity'), None, '(iv) partial gravity; expectation statement, no test data.')
I(D, 5, '5', 'Sec. II.C Fire Detection: Validation and Vehicle Scale Transport', 'makes discrimination of smoke from dust particles difficult based simply on the aerosol concentration',
  'A space experiment found typical spacecraft smoke aerosols range roughly 100-500 nm (diameter of average mass); this size range makes it hard to distinguish smoke from dust using aerosol concentration alone. HEPA filtration by the ECLSS can substantially delay detection and allow hazardous products to build up, so detection design and alarm levels depend on the specific vehicle.',
  'measurement_limitation', 'SAME', [], None, [N(100,'nm','lower size of typical smoke (diameter of average mass)','100 to 500 nm'), N(500,'nm','upper size of typical smoke (diameter of average mass)','100 to 500 nm')],
  C(), None, '(ii) dust vs smoke discrimination difficulty and (iii) size range; cites SAME results (Meyer et al. 2018). Not an observed false alarm.')
I(D, 5, '5', 'Sec. II.D Fire Detection: Transfer Standard', 'to characterize other expected smoke and nuisance aerosol sizes',
  'No database of reference spacecraft fires exists for qualifying detectors as terrestrial standards do; the authors propose transfer standards for manufacturers, which require more modelling and characterization of other expected smoke and nuisance aerosol sizes.',
  'technology_need', None, [], None, [], C(), None, '(ii)/(iii) nuisance-aerosol and smoke size characterization identified as open work (as of 2020).')
I(D, 5, '5', 'Sec. II.E Contingency Monitor', 'HF HCl transport in a spacecraft needs further study',
  'Overheated-polymer tests gave initial estimates of HF, HCl and HCN yields and allowed evaluation of candidate gas instruments, but HF/HCl transport (adsorption onto spacecraft materials) needs further study, and more materials and fire sources must be characterized to decide which compounds to monitor.',
  'technology_need', None, [], 'candidate combustion product gas instruments', [], C(), None, 'Gas monitoring for contingency response, not primary smoke detection.')
I(D, 6, '6', 'Sec. II.H Characterization of Lithium-ion Battery Fires', 'The full impact of a Li-ion fire on a spacecraft cannot be reliably predicted',
  'Heat and hazardous-product release from a burning laptop in low gravity is too poorly known to predict the impact of a Li-ion battery fire; specific tests of heat release, product composition and spread risk, and of containment and extinguishment in low gravity, are needed.',
  'technology_need', None, ['lithium-ion batteries / laptops'], None, [], C(), None, 'Need statement; no detector performance data.')
I(D, 7, '7', 'Sec. III.B Partial-Gravity Flammability', 'shutting off the spacecraft ventilation upon detecting a fire, are questionable or ineffective in partial-gravity',
  'Partial-gravity flammability is called a major gap: current low-gravity protocols such as NASA-STD-6001 Test 1 screening and shutting off ventilation upon fire detection may be questionable or ineffective in partial gravity, and no terrestrial facility exists for such experiments (a drop-tower, centrifuge rig and lunar-lander payload were being planned).',
  'technology_need', None, [], None, [], C(g='partial gravity'), None, '(iv) partial gravity; mainly flammability, with an implication for post-detection response.')
I(D, 7, '7', 'Sec. III.C Fire Detection: Validation and Vehicle-Scale Transport', 'There is no common fire detector used on existing spacecraft.',
  'No common fire detector is used across existing spacecraft and this is expected to continue with commercial crew vehicles; different detector technologies respond differently to the range of smoke aerosol sizes and types.',
  'context', None, [], None, [], C(), None, '(iii) motivation for vehicle-specific validation.')
I(D, 7, '7', 'Sec. III.C', 'measure the size distribution of the smokes produced by the experiment in low-g',
  'The plan (as of 2020) was for Saffire IV-VI diagnostics to measure low-gravity smoke size distribution and transport through the vehicle and filters, for post-flight comparison with particulate and combustion product transport models to support future detection system definition.',
  'technology_need', 'Saffire', [], None, [], C(g='microgravity'), None, 'Planned measurement; the later Saffire IV-VI paper in this source group reports DRX mass concentration and an ionization signal, not full size distributions (see open_questions).')
I(D, 7, '7', 'Sec. III.D Fire Detection: Transfer Standard', 'detection technologies for use in Gateway/HALO and Human Landing Systems (HLS) will be evaluated',
  'Because no common detector exists and testing every candidate against every spacecraft smoke is unrealistic, a transfer standard based on reference aerosols is called essential for consistent alarm thresholds; detection technologies for Gateway/HALO and HLS were to be evaluated for those applications.',
  'technology_need', None, [], None, [], C(), None, 'Programmatic plan as of 2020 (Gateway/HALO, HLS).')
I(D, 9, '9', 'Sec. III.E Contingency Air Monitor', 'The Anomaly Gas Analyzer has been under development for use on ISS and Orion',
  'The Anomaly Gas Analyzer was being developed for ISS and Orion as the contingency air monitor; its suitability for Gateway/HALO or HLS was to be assessed, smaller laser-based instruments might be developed, and further testing including burning Li-ion batteries was planned.',
  'followup_solution', None, [], 'Anomaly Gas Analyzer (AGA)', [], C(), None, 'Gas-based contingency monitoring (post-fire), not smoke detection; see ntrs_20260003174 for 2026 status.')

# ================= ntrs_20230013826 (AAAR 2023 poster) =================
D = 'ntrs_20230013826'
I(D, 1, None, 'Poster: Background and Motivation', 'How will lunar dust mitigation strategy affect smoke transport?',
  'The poster poses open questions for lunar habitats: how lunar-dust mitigation (air flow/filtration) will affect smoke transport, where smoke detectors should be placed, and what alarm settings and times to alarm should be; it notes that in lunar gravity some buoyant plume flow is expected and that buoyant and forced flow may be of similar magnitude.',
  'research_question', None, [], None, [], C(g='lunar (0.165 g)'), None, '(ii) dust mitigation interplay and (iv) partial gravity; questions, not results.')
I(D, 1, None, 'Poster: Modeling Strategy (Study 1)', 'Overheating 2 cm circular patch on wall',
  'COMSOL large-eddy-simulation model of a 2 m cubic volume at 8.2 psia and 293.15 K with lunar or Earth gravity, an overheating 2 cm wall patch at 600-1000 K, and forced flow from a supply at or near the ceiling to a floor return; particle trajectories used a massless formulation assuming particles below 1 um, spherical, density about 1-2 g/cm3.',
  'test_condition', None, [], None,
  [N(8.2,'psia','ambient pressure in model','8.2 psia'), N(293.15,'K','ambient temperature','293.15 K'), N(2,'m','domain edge length','2m'), N(600,'K','fuel patch temperature lower bound','600-1000K'), N(1000,'K','fuel patch temperature upper bound','600-1000K'), N(0.165,'g','lunar gravity used','0.165g')],
  C(p=56.5, g='lunar (0.165 g) and Earth (1 g), CFD model'), None,
  'Computational model only (no experiment). pressure_kpa=56.5 is a unit conversion of 8.2 psia (x6.89476), not a printed value.')
I(D, 1, None, 'Poster: Results and Discussion', 'particles are mixed into volume at 5 minutes',
  'In the lunar-gravity simulations a stratified plume layer near the ceiling was partly retained at 1 cm/s forced flow before the forced-flow path developed, whereas at 5 cm/s particles were mixed into the volume by about 5 minutes; for an early fire near the vent flow path even low forced flow (5 cm/s) can impede formation of a ceiling smoke layer.',
  'context', None, [], None, [N(1,'cm/s','forced flow with partly retained layer','uforced = 1 cm/s'), N(5,'cm/s','forced flow at which particles mixed into volume','5 cm/s'), N(5,'min','time by which particles were mixed into volume at 5 cm/s','5 minutes')],
  C(flow=5, g='lunar (0.165 g), CFD model'), None, '(iv) partial-gravity smoke transport; model result for one geometry and supply/return layout.')
I(D, 1, None, 'Poster: Results and Discussion', 'US ECLSS velocity requirements for intramodule circulation: 5.1-20 cm/s',
  'The poster cites US ECLSS intramodule circulation velocity requirements of 5.1-20 cm/s (3.6-102 cm/s as lower/upper limits), i.e. at or above the flow at which the model showed the ceiling smoke layer being disrupted.',
  'context', None, [], None, [N(5.1,'cm/s','ECLSS requirement lower','5.1-20 cm/s'), N(20,'cm/s','ECLSS requirement upper','5.1-20 cm/s'), N(3.6,'cm/s','lower limit','3.6-102 cm/s'), N(102,'cm/s','upper limit','3.6-102 cm/s')],
  C(), None, 'Comparison to model flows is the poster\'s framing; the requirement values are cited, not derived here.')
I(D, 1, None, 'Poster: Conclusions and Future Work', 'In Lunar gravity, even very low forced flow velocities can disrupt smoke layer formation',
  'Conclusion: in lunar gravity even very low forced flows can disrupt smoke-layer formation; ceiling-mounted detectors could allow earlier detection but their placement relative to air supplies and returns must be carefully considered. Next steps: other supply/return placements and flow velocities, alternatives to ceiling/floor placement, and more realistic early-fire scenarios.',
  'recommendation', None, [], None, [], C(g='lunar (0.165 g), CFD model'), None, '(iv) partial gravity; detector placement guidance is tentative ("could").')
I(D, 1, None, 'Poster: Conclusions and Future Work', 'Simplifying assumptions about particle transport must be considered with each scenario',
  'The authors caution that the simplifying particle-transport assumptions (massless particles, sub-micron spherical particles of fixed density) must be reconsidered for each scenario; Kapton and Teflon smoke micrographs from earlier work are shown as context for particle morphology.',
  'measurement_limitation', None, ['Kapton','Teflon'], None, [N(1,'um','assumed maximum particle diameter','d < 1 um')], C(), None,
  'CFD modelling simplification (not Model C). (i) Kapton/Teflon only shown as reference images, not modelled specifically. Lunar dust transport differences mentioned in the NTRS abstract are not shown quantitatively on the poster.')

# ================= ntrs_20260005612 (GRC 2026 poster) =================
D = 'ntrs_20260005612'
I(D, 1, None, 'Poster: Overview', 'A significant challenge is the design of a system with a low false alarm rate.',
  'NASA GRC is developing a fire detection system for partial and low gravity; a key design challenge is a low false-alarm rate, which requires discriminating combustion particles from cabin aerosol and lunar dust. Aerosol properties are measured in the GASP laboratory and cross-referenced to target detectors, and a CFD plume model is used for habitat smoke transport.',
  'technology_need', None, [], 'fire detection system under development (photoelectric and ionization detectors, aerosol sensor)', [], C(), None, '(ii) false alarms / dust; development status, preliminary.')
I(D, 1, None, 'Poster: Preliminary Results / GASP Schematic', 'a lunar highlands regolith (LHS) simulant was used',
  'Tests in the GASP chamber exposed photoelectric and ionization detectors, an aerosol sensor and a combustion product monitor, with ELPI+ and TEOM reference instruments, to smoke from Synergy Pro (SGY) heat-resistant fabric (tube furnace / White Sands smoke generator), to lunar highlands regolith simulant (LHS) dispersed by a TOPAS generator, and to the two combined (panels: SGY only, LHS + SGY, LHS only).',
  'test_condition', None, ['Synergy Pro (SGY) fabric','lunar highlands regolith simulant (LHS)'], 'photoelectric detector; ionization detector; aerosol sensor; Combustion Product Monitor',
  [N(15.6,'cm/s','velocity label annotated on White Sands smoke generator photo (meaning not explained in text)','v=15.6 cm/s'), N(3.7,'cm/s','velocity label annotated on White Sands smoke generator photo (meaning not explained in text)','v=3.7 cm/s')],
  C(g=G1), None, 'Number of runs per condition is not stated; plots are images and were not digitised. Single fabric material reported.')
I(D, 1, None, 'Poster: Preliminary Results', 'For the materials studied, the ionization detector produces the earliest detectable signal.',
  'For the materials studied, the ionization detector gave the earliest detectable signal.',
  'followup_solution', None, ['Synergy Pro (SGY) fabric'], 'ionization detector (vs photoelectric)', [], C(g=G1), None, 'Preliminary; scoped by the authors to the materials studied (SGY shown). No numeric lead time given in text.')
I(D, 1, None, 'Poster: Preliminary Results', 'Trace gases are important, but are not considered an early signal.',
  'The authors state that trace gases, though important, are not considered an early fire signal in these tests.',
  'measurement_limitation', None, ['Synergy Pro (SGY) fabric'], 'Combustion Product Monitor / gas reference', [], C(g=G1), None, 'Relevant to gas-based detection: within this poster gases are not treated as the early indicator. Preliminary, material-specific.')
I(D, 1, None, 'Poster: Preliminary Results', 'the smoldering aerosols are likely volatile organic compounds or monomers emitted',
  'Based on reference particle size measurements, the smoldering aerosols are interpreted as likely volatile organic compounds or monomers emitted from the material.',
  'particle_property', None, ['Synergy Pro (SGY) fabric'], 'ELPI+ / reference instruments', [], C(g=G1), None, 'Authors\' interpretation ("likely"); one material.')
I(D, 1, None, 'Poster: Preliminary Results', 'smoke and real lunar dust have overlapping particle sizes that set off the detector',
  'The key challenge identified is that smoke and real lunar dust have overlapping particle sizes, so dust also sets off the detector; Apollo 11 and 17 lunar dust size distributions (Park et al. 2008) are shown for comparison.',
  'false_alarm', None, ['lunar highlands regolith simulant (LHS)','Apollo 11/17 lunar dust (literature)'], 'smoke detector (photoelectric/ionization)', [], C(g=G1), None,
  '(ii) dust-triggered response (false-alarm mechanism) observed with simulant in ground tests; the poster does not quantify alarm counts. Distinct from missed alarms.')
I(D, 1, None, 'Poster: Preliminary Results', 'A key need is a low-cost sensor to discriminate between small pre-pyrolysis particles',
  'A low-cost sensor able to discriminate small pre-pyrolysis particles from lunar dust is named as a key need; signal analysis and discrimination work is ongoing.',
  'technology_need', None, [], None, [], C(), None, '(ii) smoke-dust discrimination; status ongoing as of 2026.')
I(D, 1, None, 'Poster: Fire Scenario Modeling', 'Partial gravity provides unique challenges due to decreased buoyant flow and reduced particle settling velocities.',
  'Fire scenarios for a lunar habitat are being developed from the most probable fires; partial gravity is described as challenging because of weaker buoyant flow and slower particle settling, and the model (NIST FDS laptop-fire plume simulation) includes ECLSS effects on flow and smoke concentration over time.',
  'context', None, ['laptop (fire scenario)'], None, [], C(g='partial gravity (model)'), None, '(iv) partial gravity; modelling in progress, no results quantified in text.')

# ================= ntrs_20260001992 (ICES-2026-577, Saffire IV-VI) =================
D = 'ntrs_20260001992'
I(D, 1, '1', 'Abstract (continues p.2)', 'The hazardous product release results from seven long-duration low-gravity fire tests are presented.',
  'Seven long-duration low-gravity burns aboard uncrewed Cygnus vehicles (SAFFIRE IV-VI) with cabin pressure and oxygen varied toward exploration atmospheres: four 18-cm PMMA samples (two burning on both sides, two one-sided) and three 50-cm cotton or cotton/fiberglass (SIBAL) fabrics, all 40 cm wide in 20 cm/s opposed flow. CO, CO2 and aerosol (light-scattering DustTrak DRX) were measured continuously at a Far Field Diagnostics unit near the cabin air inlet that also carried an ionization sensor from a commercial smoke detector.',
  'test_condition', 'Saffire', ['PMMA','cotton fabric','SIBAL cotton/fiberglass fabric'], 'TSI DustTrak DRX 8533; ionization sensor from a commercial smoke detector (FFD)',
  [N(7,'tests','burn tests reported','seven long-duration low-gravity fire tests'), N(40,'cm','sample width','40 cm wide'), N(20,'cm/s','opposed flow velocity (Table 1 note)','20 cm/s opposed flow'),
   N(1000,'mbar','highest test pressure (IV-2)','1000'), N(541,'mbar','lowest test pressure (VI-2)','541'), N(0.22,'mol fraction','lowest O2 (IV-2)','0.22'), N(0.31,'mol fraction','highest O2 (VI-2)','0.31'), N(16.7,'m3','smallest free volume','16.7'), N(19,'m3','largest free volume','19')],
  C(flow=20, g='microgravity (Cygnus, low Earth orbit)'), 7, '(iv) elevated O2 and reduced pressure covered; flaming fires, not smoldering. Per-test pressure/O2 in Table 1 (p.6).')
I(D, 2, '2', 'Abstract end', 'pressure rise and temperature change were small but the smoke particulate rose to substantial levels',
  'Overall the fires caused small pressure and temperature rises in the spacecraft, but smoke particulate reached substantial levels and gaseous products reached hazardous levels; the paper argues smoke products can be more hazardous than the heat.',
  'context', 'Saffire', ['PMMA','cotton fabric','SIBAL cotton/fiberglass fabric'], None, [], C(g='microgravity (Cygnus)'), 7, 'Vehicle-scale observation for the SAFFIRE IV-VI configuration.')
I(D, 2, '2', 'Sec. I Introduction', 'the fire heat release rate (HRR) was not successfully determined for SAFFIRE IV and V',
  'For SAFFIRE IV and V the heat release rate was not successfully determined, making it hard to relate measured products to fire size; HRR was measured for SAFFIRE VI.',
  'measurement_limitation', 'Saffire', [], None, [], C(g='microgravity (Cygnus)'), None, 'Limits product-vs-fire-size correlation for 4 of the 7 burns (IV and V).')
I(D, 7, '7', 'Sec. III Results, Fig. 7 discussion', 'the detection scenario tested here is likely to be quicker than in many spacecraft',
  'Smoke aerosol at the FFD tracked flame length with little delay because most flow went directly from the flow unit to the FFD without the extensive mixing of geometries like ISS; the authors therefore judge the tested detection scenario likely quicker than in many spacecraft.',
  'test_condition', 'Saffire', ['PMMA'], 'DustTrak DRX; FFD ionization chamber', [], C(g='microgravity (Cygnus)'), None, 'Caveat limiting generalisation of time-to-alarm results to other vehicles (likely optimistic).')
I(D, 8, '8', 'Sec. III Results (CO/CO2 vs SMAC)', 'were likely due to the higher oxygen concentrations for those tests',
  'Peak CO increases exceeded the 24-h CO SMAC (100 ppm) for both SAFFIRE VI PMMA tests, the SAFFIRE IV PMMA test and the SAFFIRE VI SIBAL test, and the 1-h CO2 limit was exceeded in both SAFFIRE VI PMMA tests; the authors attribute the high SAFFIRE VI levels likely to the higher oxygen concentrations.',
  'context', 'Saffire', ['PMMA','SIBAL cotton/fiberglass fabric'], None,
  [N(338,'ppm','max CO increase VI-3 (2-sided PMMA)','338'), N(309,'ppm','max CO increase VI-4 (1-sided PMMA)','309'), N(100,'ppm','24-hour CO SMAC','100 ppm'), N(425,'ppm','1-hour CO SMAC','425 ppm'), N(3,'mm Hg','CO2 1-hour limit (partial pressure)','3 mm Hg')],
  C(g='microgravity (Cygnus)'), None, '(iv) elevated O2 (0.29-0.31 mol fraction) at about 541-550 mbar in SAFFIRE VI; peak values, not values at alarm; attribution to O2 is the authors\' hedged interpretation.')
I(D, 8, '8', 'Sec. III Results', 'The SAFFIRE configuration in the spacecraft had no method to remove CO',
  'There was no CO removal and limited CO2 removal, so after the first test a baseline of these gases remained; CO and CO2 are therefore reported as increases per test rather than absolute values.',
  'measurement_limitation', 'Saffire', [], None, [], C(g='microgravity (Cygnus)'), None, 'Data-reporting caveat for Table 1 gas values.')
I(D, 9, '9', 'Sec. IV Conclusion (Table 1 on p.6, threshold analysis p.8-9)', 'a 2 mg/m3 detection threshold was not low enough to detect the fires before',
  'Applying an assumed alarm point of 2 mg/m3 total particulate (DRX at the FFD) to the data: it was reached before hazardous CO for the SAFFIRE IV PMMA and SAFFIRE VI SIBAL tests, but in both SAFFIRE VI PMMA tests CO had already risen above the 24-h SMAC (105 and 283 ppm increases), with the one-sided sample approaching the 1-h SMAC; for that one-sided test the CO2 increase at the alarm point (3.09 mm Hg) also exceeded the 3 mm Hg 1-h limit (marked red in Table 1). Tabulated times to this alarm point were 1037-1603 s for PMMA and 92-201 s for the thin fabrics.',
  'measurement_limitation', 'Saffire', ['PMMA','SIBAL cotton/fiberglass fabric','cotton fabric'], 'DustTrak DRX total PM (surrogate alarm at 2 mg/m3); no flight smoke detector alarm evaluated',
  [N(2,'mg/m3','assumed alarm threshold, DRX total PM','2 mg/m3'), N(105,'ppm','CO increase at alarm, VI-3 2-sided PMMA (544 mbar, O2 0.30)','105'), N(283,'ppm','CO increase at alarm, VI-4 1-sided PMMA (550 mbar, O2 0.29)','283'),
   N(1037,'s','time to alarm VI-3 (reference time point of Table 1 not explicitly stated)','1037'), N(1603,'s','time to alarm VI-4','1603'), N(1083,'s','time to alarm IV-2 PMMA','1083'), N(1117,'s','time to alarm V-3 PMMA','1117'), N(92,'s','time to alarm IV-1 SIBAL','92'), N(146,'s','time to alarm V-2 cotton','146'), N(201,'s','time to alarm VI-2 SIBAL','201'), N(544,'mbar','VI-3 pressure','544'), N(550,'mbar','VI-4 pressure','550'), N(3.09,'mm Hg','CO2 increase at alarm, VI-4 (exceeds 3 mm Hg 1-h limit)','3.09')],
  C(g='microgravity (Cygnus)'), 7,
  'Post-hoc surrogate threshold on a reference aerosol monitor, NOT an observed missed alarm of a smoke detector. Detection was late relative to CO hazard in 2 of 7 tests (both elevated-O2, reduced-pressure SAFFIRE VI PMMA). Flaming fires; transport path was direct (likely optimistic).')
I(D, 9, '9', 'Sec. IV Conclusion', 'would require either a lower threshold or additional smoke detectors to reduce the transport time',
  'The authors conclude that smoke detection for these design fires in this spacecraft would need a lower threshold or more detectors to cut transport time, and that judging whether a detector finds a fire before the cabin becomes uninhabitable requires vehicle-specific analysis using heat and smoke production data in a model of the planned spacecraft.',
  'recommendation', 'Saffire', [], None, [], C(), None, 'Applies to the Cygnus/SAFFIRE configuration and design fires tested.')

# ================= ntrs_20260003174 (ICES-2026-266, AGA) =================
D = 'ntrs_20260003174'
I(D, 1, '1', 'Abstract', 'Seven AGA instruments are currently deployed on the International Space Station',
  'The Anomaly Gas Analyzer is a portable, battery-powered laser-spectroscopy instrument monitoring H2O, CO2, O2, CO, NH3, HCN, HF and HCl at 1 Hz; seven units are deployed on ISS, Orion-specific units were manifested for (and two flew aboard) Artemis 2, an HLS variant is in development, and a three-gas subset forms the Primary Constituent Monitor for Gateway HALO.',
  'followup_solution', None, [], 'Anomaly Gas Analyzer (AGA)', [N(7,'units','AGA instruments deployed on ISS','Seven AGA instruments'), N(1,'Hz','data rate','1 Hz'), N(2,'units','AGA units flown aboard Artemis 2 (p.7)','Two of those instruments flew aboard Artemis 2')],
  C(), None, 'Combustion-product gas monitoring; the paper presents instrument development/calibration, not fire-detection timing tests.')
I(D, 8, '8', 'Table 1 (flight AGA characteristics)', 'Table 1. Physical and analytical characteristics of the flight AGA',
  'Flight AGA: 4.3 kg, 6.0 L, 6.5 W; required accuracy and ranges include CO 5 ppm over 5-1,000 ppm, HF, HCl and HCN each 1 ppm over 2-50 ppm, O2 1% over 14-50%, CO2 0.2 mmHg over 0.3-21 mmHg.',
  'followup_solution', None, [], 'Anomaly Gas Analyzer (AGA)',
  [N(4.3,'kg','mass','4.3 kg'), N(6.5,'W','power','6.5 W'), N(5,'ppm','CO accuracy','5 ppm'), N(1000,'ppm','CO range upper','5 – 1,000 ppm'), N(2,'ppm','HF/HCl/HCN range lower','2 – 50 ppm'), N(50,'ppm','HF/HCl/HCN range upper','2 – 50 ppm'), N(14,'%','O2 range lower','14 – 50 %'), N(50,'%','O2 range upper','14 – 50 %')],
  C(), None, 'Limit-of-quantitation column not used (text-layer order ambiguous).')
I(D, 7, '7', 'Sec. III.A AGA (calibration)', 'one has to accommodate gross changes to the bulk speed of sound',
  'Because CO and HCN are sensed by photoacoustic spectroscopy, calibration must correct for speed-of-sound changes caused by varying cabin O2 and CO2, plus empirical corrections for absolute pressure and spectroscopic temperature corrections; calibrating the 8-gas instrument took about three weeks per campaign.',
  'measurement_limitation', None, [], 'AGA photoacoustic CO and HCN channels', [N(3,'weeks','duration of final calibration activity','about three weeks')],
  C(), None, '(iv) relevant to elevated-O2 / reduced-pressure exploration atmospheres: gas readings depend on composition- and pressure-specific corrections.')
I(D, 1, '1', 'Abstract; Sec. III.B HLS-AGA (p.8-9)', 'A wider calibrated operating pressure envelope is required in this application.',
  'The lunar Human Landing System variant (HLS AGA) needs a wider calibrated operating pressure envelope; two HLS AGA engineering units were delivered in mid-2025 and four flight units were scheduled for 2026, with some maximum concentration ranges (O2, CO2, NH3) reduced for the HLS cabin.',
  'technology_need', None, [], 'HLS AGA (AGA 1.5)', [N(4,'units','HLS AGA flight units scheduled for 2026','Four flight units')], C(), None, '(iv) reduced/variable pressure for lunar lander; development status as of 2026.')
I(D, 9, '9', 'Sec. III.C PCM', 'Two PCMs will be installed in HALO as part of the environmental control loop',
  'For Gateway HALO the Primary Constituent Monitor uses only the H2O, CO2 and O2 subset of AGA sensing, radiation-hardened for a 15-year target life, with redundant O2 channels and a 9.5-15.2 psia operating range.',
  'followup_solution', None, [], 'Primary Constituent Monitor (PCM)', [N(9.5,'psia','PCM pressure range lower','9.5–15.2 psia'), N(15.2,'psia','PCM pressure range upper','9.5–15.2 psia'), N(15,'years','HALO target lifetime','fifteen years')],
  C(), None, 'Within this paper the PCM lists no combustion-product (CO/HCN/HF/HCl) channels, so it is not described as a fire-detection device.')
I(D, 11, '11', 'Sec. V Conclusion', 'now-operational Anomaly Gas Analyzer for ISS and Orion contingency monitoring',
  'The conclusion frames the AGA as an operational contingency-monitoring instrument for ISS and Orion (three Orion units, four HLS units in build, PCMs for Gateway HALO).',
  'context', None, [], 'Anomaly Gas Analyzer (AGA)', [], C(), None, 'Role is contingency (post-event) atmosphere monitoring; within the examined sources no AGA fire-detection-time data were found.')

# ================= ices2025_361_dusttolerant =================
D = 'ices2025_361_dusttolerant'
L0 = 'excerpt; '
I(D, None, None, 'Abstract', 'causing false alarms and requiring operational controls, such as turning off smoke detectors during housekeeping',
  'Airborne cabin dust in low Earth orbit has caused smoke-detector false alarms and led to operational controls such as switching detectors off during housekeeping; the authors argue this practice should not become the norm at dusty destinations (Moon, Mars).',
  'false_alarm', None, ['spacecraft cabin dust'], 'heritage spacecraft smoke detectors', [], C(), None,
  '(ii) Industry/academic paper (Northrop Grumman, Univ. Duisburg-Essen), summarising ISS practice; not a NASA test report. No false-alarm counts given here.')
I(D, None, None, 'Sec. I Introduction', 'the immediate automated response is shutting down ventilation and other systems',
  'On ISS a smoke alarm automatically shuts down ventilation and other systems, requiring hours of ground work to restore and document; frequent false alarms also risk crews taking alarms less seriously.',
  'false_alarm', None, [], 'ISS smoke detection system', [], C(), None, '(ii) operational consequence of false alarms; qualitative.')
I(D, None, None, 'Sec. I Introduction', 'these two goals are mutually exclusive and cannot be achieved simultaneously',
  'Raising detector sensitivity to catch the earliest smoke increases false alarms from cabin dust; the authors state that high early-smoke sensitivity and immunity to dusty events cannot both be achieved with smoke detectors currently in space vehicles.',
  'measurement_limitation', None, [], 'current spacecraft smoke detectors', [], C(), None, '(ii) sensitivity vs false-alarm trade-off; authors\' assessment.')
I(D, None, None, 'Sec. II Background', 'spacecraft smoke detectors have never been proven in an emergency scenario',
  'No fire has occurred aboard a NASA vehicle in flight, so spacecraft smoke detectors have never been proven in a real emergency; flight detectors derive from the terrestrial aircraft industry.',
  'context', None, [], None, [], C(), None, 'Explains why limitation evidence comes from experiments, not flight fires.')
I(D, None, None, 'Sec. II.A Current Spacecraft Smoke Detectors', 'there is no mechanism to distinguish the particle type in either technology',
  'Both heritage technologies (Shuttle ionization, ISS photoelectric) are particle detectors with no means to tell smoke from dust; dust entering the chamber removes ions or scatters light exactly as smoke does, which is the mechanism of false alarms.',
  'measurement_limitation', None, [], 'Space Shuttle ionization detector; ISS photoelectric detector', [], C(), None, '(ii) mechanism statement.')
I(D, None, None, 'Sec. II.B Spacecraft Smoke Particle Characterization', 'The most likely spacecraft smoke particles range from 100 nm to 1000 nm',
  'Summarising the ISS smoke experiment, matching ground tests and WSTF tests (ten smoke types), the authors state that the most likely spacecraft smoke particles are about 100-1000 nm and mostly round and compact, with some particles outside this range and some agglomerates.',
  'particle_property', 'SAME', [], None, [N(100,'nm','lower bound of most likely smoke size','100 nm'), N(1000,'nm','upper bound of most likely smoke size','1000 nm (1 µm)')], C(), None, '(iii) secondary summary of NASA results; oxidative pyrolysis smokes at ISS-like flow.')
I(D, None, None, 'Sec. II.C Airborne Particles on ISS', 'larger concentration spikes, mostly occurring on weekends when the crew was performing vacuuming',
  'Real-time ISS particle data showed intermittent spikes of about 500-1500 particles/cm3 during the day, near-zero levels during crew sleep, and larger spikes mostly on weekend vacuuming; another analysis reported baselines of 10-100 particles/cm3 with spikes up to 80,000 particles/cm3 during crew activities. These spikes would have caused false alarms had detectors not been switched off during vacuuming.',
  'false_alarm', None, ['ISS cabin dust'], None,
  [N(500,'particles/cm3','intermittent spike lower','500 and 1500 particles/cm 3'), N(1500,'particles/cm3','intermittent spike upper','500 and 1500 particles/cm 3'), N(80000,'particles/cm3','maximum spike (Fortenberry and Meyer 2023)','80,000 particles/cm 3')],
  C(g='microgravity (ISS)'), None, '(ii) potential false-alarm conditions inferred from particle data; because detectors are turned off during vacuuming, these are not recorded alarms.')
I(D, None, None, 'Sec. II.D Lunar and Planetary Dust', 'These sizes will interfere with smoke detection in the same manner that the typical ISS',
  'A significant fraction of lunar dust (Apollo samples) is smaller than 1 um, overlapping smoke sizes, and may be present at much higher concentrations than ISS dust; switching detectors off while cleaning suits and air would leave much longer undetected periods than on ISS.',
  'false_alarm', None, ['lunar dust'], None, [N(1,'um','size below which a significant fraction of lunar dust lies','1 µm')], C(g='lunar'), None, '(ii) projected false-alarm risk for lunar missions; not an observed event.')
I(D, None, None, 'Sec. II.E Smoke Detector False Alarms', 'with a total of 14 events (note that this total combines built-in test',
  'False-alarm reports date back to Skylab UV fire detectors; Shuttle reports total 14 events, combining built-in-test failures and false alarms; ISS incidents are known but not publicly tracked, with anecdotal reports from the US Lab, the Russian service module and SpaceX Crew Dragon.',
  'false_alarm', None, [], 'Skylab UV fire detectors; Shuttle smoke detectors', [N(14,'events','Shuttle smoke detector events (BIT failures and false alarms combined)','14 events')], C(), None,
  '(ii) the 14 is not a pure false-alarm count. ISS frequency not published (stated by authors).')
I(D, None, None, 'Sec. II.E Smoke Detector False Alarms', 'smoke alarm events in spacecraft smoke detection have occurred due to interference from nuisance dust',
  'The authors state that historically most spacecraft smoke-alarm events have been caused by nuisance dust rather than smoke, since target smoke sizes sit in the middle of ISS airborne particle sizes (5 nm-3 um measured in real time).',
  'false_alarm', None, ['spacecraft cabin dust'], None, [], C(), None, '(ii) qualitative claim; the paper notes quantitative false-alarm frequency is not typically published.')
I(D, None, None, 'Sec. II.F Smoke Detector Inlet Features', 'A filter will capture smoke particles by multiple mechanisms',
  'Putting a filter ahead of a detector to block dust would also capture smoke and delay alarm; any barrier or long tubing to the cabin air prolongs time to alarm, though coarse screens for microgravity debris can be optimised by modelling.',
  'measurement_limitation', None, [], None, [], C(), None, 'Design caution; no test data in excerpt.')
I(D, None, None, 'Sec. III Smoke Detector Design to Avoid False Alarms', 'evaluation of scattered light measurements at two different colors / wavelengths',
  'High-end terrestrial detectors reduce false alarms by comparing scattered light at two wavelengths (blue and infrared), exploiting that small smoke particles scatter blue light more strongly while larger dust shows little difference.',
  'followup_solution', None, [], 'dual-wavelength scattering detectors (terrestrial)', [], C(), None,
  '(ii) technique description; this paper presents no test with spacecraft smokes or lunar dust for the dual-wavelength method, and lunar dust overlapping smoke sizes may limit a purely size-based contrast (inference not made by the authors).')
I(D, None, None, 'Sec. III.A Polarimetric Approach', 'Results show that the discrimination of lunar dust should be possible based on the assumption',
  'Univ. Duisburg-Essen polarimetric detector prototypes identify irregular dust by depolarized scattered light (about 0.2 depolarization for Dolomite D90 at 90 degrees, about 650 nm); a variant tested with smoke and lunar simulant JSC-1AF indicated discrimination should be possible if the simulant matches real lunar dust morphology, and prototypes still detected smoke added to air already containing dust.',
  'followup_solution', None, ['lunar dust simulant JSC-1AF','Dolomite D90 dust','smoldering cotton wick'], 'UDE polarimetric light-scattering smoke detector prototype',
  [N(0.2,'ratio','degree of depolarization for Dolomite D90','approx. 0.2'), N(90,'deg','scattering angle','90°'), N(650,'nm','wavelength','approx. 650 nm')], C(g=G1), None,
  '(ii) prototype-level evidence (proof of principle); hedged ("should be possible"); depends on simulant representativeness; not yet tested with a wide range of spacecraft-material smokes.')
I(D, None, None, 'Sec. IV.A Environment', 'ionization smoke detectors must ionize air molecules, which will be less abundant at low pressures',
  'Exploration hardware must work at low pressure (HALO nominal 10.2 psi / 70.3 kPa) and survive vacuum; photoelectric detection is pressure-independent, but ionization detectors\' baseline current changes at low pressure, so baseline operation must be characterised across the vehicle pressure range. Multi-year dormancy may challenge COTS aviation detectors.',
  'measurement_limitation', None, [], 'ionization smoke detectors; photoelectric smoke detectors', [N(70.3,'kPa','HALO nominal cabin pressure','10.2 psi (70.3 kPa)')], C(p=70.3), None,
  '(iv) reduced pressure; engineering statement, no measured pressure-response data in the excerpt.')
I(D, None, None, 'Sec. IV.C Features and Requirements', 'the ability to reprogram smoke detector parameters while deployed during a mission',
  'Predicted post-EVA lunar dust loads in NASA-STD-1008 are conservative estimates with values still to be resolved, so the authors recommend detectors whose alarm thresholds and parameters can be reprogrammed in flight as real dust data become available.',
  'recommendation', None, ['lunar dust'], None, [], C(), None, '(ii) acknowledges lunar dust load uncertainty.')
I(D, None, None, 'Sec. V Conclusion', 'COTS detectors from the aviation industry will not suffice as they have in LEO missions',
  'The authors conclude that overlapping sizes of target smoke and spacecraft/lunar dust make false alarms inevitable with heritage detector designs and that COTS aviation detectors will not suffice for exploration missions; dust-tolerant detectors engineered for space are needed.',
  'technology_need', None, [], 'COTS aviation smoke detectors', [], C(), None, '(ii) conclusion by industry/academic authors.')
I(D, None, None, 'Sec. V Conclusion', 'Future tests with a revised and improved prototype are planned',
  'Planned work: test a revised polarimetric prototype against various dusts, pyrolysis smoke from many common spacecraft materials and EN 54 standard test fires, using a newer lunar simulant and an ISS-vacuum-bag-based cabin dust simulant, plus months-long dust exposure tests.',
  'technology_need', None, ['lunar simulant','ISS cabin dust simulant'], 'UDE polarimetric prototype', [], C(), None, 'Planned, not completed, as of 2025.')

# ================= ices2025_halo_sd_threshold =================
D = 'ices2025_halo_sd_threshold'
I(D, None, None, 'Sec. I Introduction', 'there is no National Aeronautics and Space Administration (NASA) standard governing',
  'The authors state that, as of 2025, no NASA standard governs smoke detector performance (particularly for mass-concentration detectors) for space use; terrestrial detectors adapted to LEO become less viable with higher radiation and longer missions beyond Earth\'s magnetic field.',
  'technology_need', None, [], None, [], C(), None, 'Industry paper (Northrop Grumman, Paragon) with NASA GRC input.')
I(D, None, None, 'Sec. I-II Method Approach', 'requirements development for smoke detectors, ionization style in this case',
  'The HALO smoke detector alarm threshold (ionization-style detector) was derived from tabulated 2012 GRC tests at WSTF in which 0.5 g samples of spacecraft materials (FR-4 circuit board, Nomex, wire insulation, Kapton, Teflon) were overheated, gases were measured by commercial and prototype sensors and smoke mass by a reference aerosol instrument, with results scaled to HALO and compared with 1-h SMACs (CO 425, HCN 8, HF 3 ppm).',
  'test_condition', None, ['FR-4 circuit board','Nomex','wire insulation','Kapton','Teflon'], 'HALO smoke detector (ionization style)',
  [N(0.5,'g','sample mass in WSTF tests','0.5 g'), N(425,'ppm','1-h SMAC CO','425'), N(8,'ppm','1-h SMAC HCN','8'), N(3,'ppm','1-h SMAC HF','3')], C(), None,
  '(i) Kapton/Teflon included. Analysis/extrapolation, not a detector test; the final HALO threshold value is not given in the examined excerpt.')
I(D, None, None, 'Sec. III Assumptions', 'If the generation rate does not exceed air filtration, the SD will not alarm',
  'The authors note that smoke generation competes with cabin filtration: if generation does not exceed filtration the detector will never alarm, while toxic gases keep accumulating unless removed; their analysis assumes instantaneous release and detection and ignores transport time.',
  'measurement_limitation', None, [], 'smoke detector (generic, HALO)', [], C(), None,
  'Analytical statement of a missed-alarm condition, not an observed missed alarm; consistent with earlier NASA modelling (Urban et al. 2016).')
I(D, None, None, 'Sec. III Assumptions', 'spacecraft Kapton is present in thin sheets or tape rather than ground or cut',
  'Data-set limitations listed: assumed equal smoke/gas generation for all fuels and linear scaling with mass (only 0.5 g samples, no time-resolved data), notoriously unrepeatable smoke generation (runs averaged), large gas-sensor variation (TDLS and PAS most reliable), and unrealistic sample preparation (e.g. ground or cut Kapton, granulated PTFE) compared with spacecraft use.',
  'measurement_limitation', None, ['Kapton','PTFE','printed circuit board'], 'TDLS and PAS gas sensors (2012 WSTF data)', [N(0.5,'g','only sample size used in analysed campaigns','0.5 g')], C(), None, '(i) Kapton/Teflon representativeness limitation.')
I(D, None, None, 'Sec. V Results', 'SMAC exceedances were observed for the wire insulation at 540 °C and Kapton squares',
  'Scaled to HALO, a 3 mg/m3 threshold gave few 1-h SMAC exceedances (HF for wire insulation at 540 C, HCN for Kapton squares); at 5 mg/m3 HF exceedances grew (all wire insulation sets, worst-case 100% TFE); at 7 mg/m3 further exceedances appeared (100% Kapton for HCN, PTFE/TFE for HF) and CO exceeded for Kapton squares.',
  'followup_solution', None, ['wire insulation','Kapton','PTFE/TFE'], 'HALO smoke detector threshold analysis',
  [N(3,'mg/m3','threshold with few exceedances','3 mg/m 3'), N(5,'mg/m3','threshold with more HF exceedances','5 mg/m 3'), N(7,'mg/m3','threshold with first CO exceedance','7 mg/m')], C(), None,
  '(i) Kapton/Teflon smokes: hazard at alarm is material dependent; extrapolated analysis, not measured in HALO.')
I(D, None, None, 'Sec. VI Conclusion', 'A large gap in the currently available data is the absence of space vehicle filtration',
  'Recommended future smoke campaigns: newer spacecraft materials and finishes, multiple low-pressure test points, time-resolved smoke and gas data, and larger-scale tests with filtration as a variable, to support models of airflow, filtration, thresholds and detector placement.',
  'technology_need', None, [], None, [], C(), None, '(iv) low pressure and filtration named as data gaps; industry authors.')

# ---------------------------------------------------------------- build
docs_out = []
pages_cache = {}
for d in DOCS:
    rawdir = os.path.join(ROOT, 'raw', d['doc_id'])
    rawf = os.path.join(rawdir, d['raw'])
    b = open(rawf, 'rb').read()
    sha = hashlib.sha256(b).hexdigest()
    textp = os.path.join(ROOT, 'text', d['doc_id'] + '.txt')
    txt = open(textp, encoding='utf-8').read()
    if rawf.endswith('.pdf'):
        out = subprocess.run(['pdfinfo', rawf], capture_output=True, text=True).stdout
        pc = int(re.search(r'Pages:\s+(\d+)', out).group(1))
        pages_cache[d['doc_id']] = txt.split('\f')
    else:
        pc = None
        pages_cache[d['doc_id']] = None
    pages_cache[d['doc_id'] + '#all'] = txt
    ids = dict(d['identifiers'])
    import datetime
    rt = RETRIEVED_OVERRIDE.get(d['doc_id']) or datetime.datetime.fromtimestamp(os.path.getmtime(rawf), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    meta = dict(doc_id=d['doc_id'], title=d['title'], year=d['year'], authors=d['authors'], url=d['url'], retrieved_utc=rt,
                sha256=sha, bytes=len(b), page_count=pc,
                identifiers=dict(doi=ids['doi'], ntrs=ids['ntrs'], psi=ids['psi'], pmc=ids['pmc'], other=ids.get('other', [])),
                license_note=d['license_note'], accessible=d['accessible'], access_note=d['access_note'], source_key=SK, raw_file=d['raw'])
    json.dump(meta, open(os.path.join(rawdir, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
    docs_out.append(dict(doc_id=d['doc_id'], title=d['title'], year=d['year'], authors=d['authors'], url=d['url'],
                         local_path=os.path.relpath(rawf, '/home/efeai/Desktop/NasaSpaceApps'), text_path=os.path.relpath(textp, '/home/efeai/Desktop/NasaSpaceApps'),
                         sha256=sha, page_count=pc, identifiers=meta['identifiers'], accessible=d['accessible'], access_note=d['access_note']))

errors = []
items_out = []
for k, it in enumerate(ITEMS, 1):
    a = norm(it['anchor_quote'])
    nw = len(a.split())
    if nw > 15:
        errors.append(f"{k} anchor too long ({nw}): {a}")
    pages = pages_cache[it['doc_id']]
    if pages is None:
        if a not in norm(pages_cache[it['doc_id'] + '#all']):
            errors.append(f"{k} anchor not found in {it['doc_id']}: {a}")
    else:
        hits = [i + 1 for i, p in enumerate(pages) if a in norm(p)]
        if it['pdf_page'] not in hits:
            errors.append(f"{k} anchor page mismatch {it['doc_id']} p{it['pdf_page']} hits={hits}: {a}")
    o = dict(item_id=f"{SK}-{k:02d}")
    o.update(it)
    items_out.append(o)

if errors:
    print('\n'.join(errors)); sys.exit(1)

# search log
notes = json.load(open(os.path.join(HERE, 'search_notes.json')))
slog = []
for fn in sorted(glob.glob(os.path.join(HERE, 'q', '*.json')), key=os.path.getmtime):
    q = os.path.basename(fn)[:-5].replace('_', ' ')
    d = json.load(open(fn))
    slog.append(dict(query=q, where='NTRS API https://ntrs.nasa.gov/api/citations/search (page.size=25, relevance order)', hits=d['stats']['total'],
                     notes=notes.get(q, 'Reviewed returned titles; no additional 2018-2026 spacecraft fire-detection document selected from this query.')))
slog += notes['_web']

out = dict(source_key=SK, documents=docs_out, items=items_out,
           inaccessible=notes['_inaccessible'], search_log=slog, open_questions=notes['_open_questions'])
os.makedirs(os.path.join(ROOT, 'extracted'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, 'extracted', SK + '.json'), 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print('items', len(items_out), Counter(i['category'] for i in items_out))
print('docs', len(docs_out))
