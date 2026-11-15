"""Build sources/raw/<doc>/meta.json and sources/extracted/meyer2018.json for source group meyer2018.

Run: /home/efeai/Desktop/NasaSpaceApps/.venv/bin/python -I sources/tools/build_meyer2018.py
Every anchor_quote is checked: <=15 words and present (after whitespace normalisation) in
sources/text/<doc_id>.txt. The script exits non-zero if any check fails.
Texts were made with sources/tools/html2txt_meyer2018.py (pmc / nist modes).
"""
import hashlib
import json
import os
import sys

ROOT = "/home/efeai/Desktop/NasaSpaceApps/sources"
RETRIEVED = "2026-11-15T10:42:46Z"
SK = "meyer2018"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def norm(s):
    return " ".join(s.split())


DOCS = {
    "meyer2018": dict(
        title="Evaluation of Spacecraft Smoke Detector Performance in the Low-Gravity Environment",
        year=2018,
        authors=["Marit E. Meyer", "David L. Urban", "George W. Mulholland", "Victoria Bryg",
                 "Zeng-Guang Yuan", "Gary A. Ruff", "Thomas Cleary", "Jiann Yang"],
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/",
        raw="PMC7918997.html",
        identifiers=dict(doi="10.1016/j.firesaf.2018.04.004", ntrs=None, psi=None, pmc="PMC7918997",
                         pmid="33654340", nihmsid="NIHMS1658855", elsevier_pii="S0379711216302181"),
        license_note=("Elsevier article (Fire Safety Journal 98 (2018) 74-81, per Crossref). Text used is the "
                      "PMC author manuscript (NIHMS1658855); Crossref lists an Elsevier open-access user "
                      "license for the accepted manuscript from 2019-04-25. Copyrighted: anchors <=15 words, "
                      "everything else paraphrased."),
        accessible=True,
        access_note=("Publisher page (sciencedirect) was blocked in the Model C audit; the PMC author manuscript "
                     "was re-fetched with curl on 2026-11-15 and differs from the Model C snapshot copy "
                     "(external/model_c/data/references/PMC7918997.html) only in two session-token lines "
                     "(ncbi_phid meta and csrfmiddlewaretoken). Identity confirmed via citation_* meta tags "
                     "(title, 8 authors, Fire safety journal, vol 98, DOI 10.1016/j.firesaf.2018.04.004, PMID "
                     "33654340) and via Crossref API record saved as crossref.json (title, same 8 authors, "
                     "Fire Safety Journal 98, pages 74-81, issued 2018-06). The author manuscript may differ "
                     "in wording from the final published version (the NIST record's abstract wording differs "
                     "slightly). HTML source: pdf_page is null; locations are section/figure/table names."),
        extra_files={"crossref.json": "Crossref API record for the DOI (fetched 2026-11-15)"},
    ),
    "nist2018_pub": dict(
        title="Evaluation of Spacecraft Smoke Detector Performance in the Low-Gravity Environment (NIST publication record)",
        year=2018,
        authors=["Jiann C. Yang", "Thomas G. Cleary", "Marit Meyer", "D L. Urban", "George W. Mulholland",
                 "Victoria Bryg", "Zeng-guang Yuan", "Gary A. Ruff"],
        url="https://www.nist.gov/publications/evaluation-spacecraft-smoke-detector-performance-low-gravity-environment",
        raw="page.html",
        identifiers=dict(doi="10.1016/j.firesaf.2018.04.004", ntrs=None, psi=None, pmc=None),
        license_note=("NIST web page (publication record with abstract). NIST site text is generally a U.S. "
                      "Government work; abstract text belongs to the Elsevier paper - quote <=15 words."),
        accessible=True,
        access_note=("Fetched with curl (HTTP 200). Author order on the NIST page lists NIST authors first; "
                     "the paper's author order (Meyer first) is in meyer2018. The page links only to the DOI "
                     "(no NIST-hosted PDF found on the page)."),
        extra_files={},
    ),
    "nist2018_news": dict(
        title="NIST/NASA Study Shows One Detector Doesn't 'Fit All' for Smoke in Spacecraft (NIST news release)",
        year=2018,
        authors=["NIST Public Affairs (no byline on page)"],
        url="https://www.nist.gov/news-events/news/2018/05/nistnasa-study-shows-one-detector-doesnt-fit-all-smoke-spacecraft",
        raw="page.html",
        identifiers=dict(doi=None, ntrs=None, psi=None, pmc=None),
        license_note=("NIST news release (released 2018-05-01, page updated 2025-02-03). Text generally a U.S. "
                      "Government work; images carry their own credits (NASA, M.E. Newman/NIST, NASA JSC). "
                      "Quotes kept <=15 words anyway."),
        accessible=True,
        access_note="Fetched with curl (HTTP 200). Press release: secondary/interpretive source about the paper.",
        extra_files={},
    ),
}


def cond(**kw):
    c = dict(atmosphere_o2_vol_pct=None, pressure_kpa=None, airflow_cm_s=None, gravity=None,
             heating_s=None, aging_s=None)
    c.update(kw)
    return c


def num(value, unit, meaning, verbatim):
    return dict(value=value, unit=unit, meaning=meaning, verbatim=verbatim)


ITEMS = []


def add(doc_id, location, anchor, summary, category, investigation=None, materials=None,
        detector=None, numbers=None, conditions=None, n=None, scope=""):
    ITEMS.append(dict(
        item_id=None, doc_id=doc_id, pdf_page=None, printed_page=None, location=location,
        anchor_quote=anchor, summary=summary, category=category, investigation=investigation,
        materials=materials or [], detector=detector, numbers=numbers or [],
        conditions=conditions or cond(), n_independent_tests=n, scope_notes=scope))


M5 = ["Teflon", "Kapton", "silicone rubber", "Pyrell (polyurethane foam)", "cellulose lamp wick"]
LOWG = "low gravity (ISS, SAME flights)"

# ---------------- meyer2018: paper (PMC author manuscript) ----------------
D = "meyer2018"
add(D, "Abstract",
    "The two spacecraft smoke detectors did not successfully detect every type of smoke",
    "Headline finding: neither of the two spacecraft smoke detectors carried in the ISS experiment detected "
    "every smoke type produced by overheating common spacecraft materials.",
    "missed_alarm", "SAME", M5, "two spacecraft smoke detectors (Space Shuttle ionization; ISS light-scattering)",
    conditions=cond(gravity=LOWG),
    scope="Summary statement; the per-detector / per-material breakdown is in Section 3.2 and Figure 9. Refers to "
          "signals below alarm thresholds in the SAME duct, not to alarms during real events.")
add(D, "Abstract",
    "next generation of spacecraft fire detectors must be improved and tested against smoke from relevant",
    "The authors conclude that the next generation of spacecraft fire detectors needs to be improved and "
    "should be tested against smoke from materials actually relevant to spacecraft.",
    "recommendation", "SAME", M5, None, conditions=cond(gravity=LOWG),
    scope="Authors' recommendation derived from SAME detector results; it does not specify a test protocol, "
          "detector technology, or acceptance criteria.")
add(D, "Abstract",
    "not significantly different from smoke particles generated in equivalent experiments performed in normal gravity",
    "Smoke particles from the ISS experiment varied in morphology and average diameter by material, but the "
    "authors report they were not significantly different from particles made in equivalent normal-gravity tests.",
    "particle_property", "SAME", M5, None, conditions=cond(gravity="low gravity vs normal gravity"),
    scope="Equivalence is qualified in Section 3.1 to flow velocities of about 8.1 cm/s or higher; at low or zero "
          "flow the authors expect low-g and 1-g smoke to differ.")
add(D, "1.0. Introduction",
    "All existing spacecraft smoke detectors have been designed based on fire data from experiments",
    "The authors state that all existing spacecraft smoke detectors were designed from normal-gravity fire data, "
    "and that terrestrial detection knowledge (built on UL standard fuels) does not transfer directly to "
    "spacecraft because of the closed volume, the need to detect pre-ignition oxidative pyrolysis early, the "
    "absence of buoyant smoke transport, and different cabin materials.",
    "context", None, [], None,
    scope="Framing statement by the authors (citing Bukowski refs 1-3); not an experimental result.")
add(D, "1.0. Introduction",
    "the latter rapidly reduces the concentration, making detection particularly challenging",
    "Without buoyancy, smoke may stay concentrated near its source and grow by coagulation (aging), which "
    "changes particle size and hence detector response, or it may be spread through the cabin by ventilation, "
    "which quickly dilutes it and makes detection hard.",
    "context", None, [], None, conditions=cond(gravity="low gravity (general)"),
    scope="Qualitative physical reasoning in the introduction; no measurement attached.")
add(D, "1.0. Introduction",
    "This experiment was flown twice on the International Space Station (ISS), in 2007 and 2010",
    "SAME (Smoke Aerosol Measurement Experiment) flew twice on the ISS (2007, 2010); ground tests with identical "
    "smoke-generation and measurement hardware were run during and after the flights, and later ground tests "
    "with a research-grade aerosol instrument measured full size distributions for the five materials (refs 4, 5).",
    "investigation_profile", "SAME", M5, None,
    numbers=[num(2007, "year", "first ISS flight (SAME-1)", "2007"), num(2010, "year", "second ISS flight (SAME-2)", "2010")],
    conditions=cond(gravity="low gravity (ISS) and normal-gravity ground tests"),
    scope="Ground-test details (refs 4, 5: Aerosol Sci. Tech. 49(5), 2015) are not reproduced in this paper.")
add(D, "1.1. Spacecraft Fire Detector Background",
    "were reported to have difficulties with false alarms",
    "Historical note: Skylab (1970s) used approximately 30 UV-sensing fire detectors that were restricted to line "
    "of sight and were reported to suffer from false alarms.",
    "false_alarm", None, [], "UV-sensing fire detectors (Skylab)",
    numbers=[num(30, "detectors", "UV-sensing fire detectors on Skylab", "approximately 30")],
    scope="Secondary citation of Friedman [6]; not SAME data; no false-alarm counts given.")
add(D, "1.1. Spacecraft Fire Detector Background",
    "An inertial separator was designed to eliminate particles larger than 1 to 2",
    "The Space Shuttle smoke detectors used ionization technology (the most advanced at the time) and had an "
    "inertial separator intended to keep particles larger than about 1-2 micrometres out of the sensing volume.",
    "definition", None, [], "Space Shuttle detectors (ionization)",
    numbers=[num(1, "um", "lower bound of particle size removed by inertial separator", "1 to 2 μm"),
             num(2, "um", "upper bound of particle size removed by inertial separator", "1 to 2 μm")],
    scope="Design description; the paper does not quantify the separator's effect on SAME results.")
add(D, "1.1. Spacecraft Fire Detector Background",
    "The International Space Station (ISS) smoke detectors use near-IR forward light scattering",
    "The ISS smoke detectors work by near-infrared forward light scattering, which the authors describe as more "
    "sensitive to particles larger than 0.3 micrometres.",
    "definition", None, [], "ISS smoke detectors (near-IR forward light scattering)",
    numbers=[num(0.3, "um", "particle size above which ISS detector is more sensitive", "larger than 0.3 μm")],
    scope="Design description; the news release calls this the photoelectric ISS detector.")
add(D, "1.1. Spacecraft Fire Detector Background",
    "there were six overheat and failed component events in the NASA Space Shuttle fleet",
    "Context on incidents: six overheat/failed-component events in the Shuttle fleet (per Friedman), several ISS "
    "odor/smoke events (lamp, smoldering polymeric bushing, water recovery system twice, failed pressure-suit "
    "micro-pump), none of which became a real fire; the worst was the 1997 Mir oxygen-generator fire.",
    "context", None, [], None,
    numbers=[num(6, "events", "Space Shuttle overheat/failed component events", "six")],
    scope="Secondary sources (refs 6, 8, 9 incl. a personal communication). The paper prints 'ISS Expedition 18, "
          "September 2006' for the bushing event; date/expedition not verified here.")
add(D, "1.1. Spacecraft Fire Detector Background",
    "there is still a critical need for improved understanding of spacecraft fires and improved detection",
    "The authors argue that, as mission durations grow and failures become more likely, better understanding of "
    "spacecraft fires and better detection remain critical needs.",
    "research_question", None, [], None,
    scope="General statement of need (citing Ruff et al. [10]); not tied to a specific experiment.")
add(D, "2.0. Methods",
    "The goal of SAME was to generate repeatable smoke and obtain particle size statistics on-orbit",
    "SAME aimed to make repeatable smoke on orbit and get particle-size statistics without relying only on sample "
    "return, using three small instruments that each measure a different moment of the size distribution, with "
    "controlled sample temperature, flow and aging time. SAME-1 flew in 2007 and SAME-2 in 2010.",
    "investigation_profile", "SAME", M5, None,
    numbers=[num(2007, "year", "SAME-1", "2007 (SAME-1)"), num(2010, "year", "SAME-2", "(SAME-2) in 2010")],
    conditions=cond(gravity=LOWG),
    scope="Describes the experiment design; 'SAME' in the paper means both flights unless a flight number is given.")
add(D, "2.1. Moment Method",
    "the approach consists of measuring three moments of the size distribution (zeroth, first and third)",
    "The moment method measures the zeroth (number), first (diameter) and third (volume/mass) moments; count mean "
    "diameter (M1/M0) and diameter of average mass ((M3/M0)^1/3) need no distribution assumption, while the "
    "geometric mean diameter and geometric standard deviation require assuming a lognormal distribution.",
    "definition", "SAME", [], None,
    scope="Method definition; validation is cited to Cleary et al. NISTIR 7050 [11] and Meyer et al. [4].")
add(D, "2.2. Instruments",
    "Unfortunately, they all show material or size-dependent behavior.",
    "All three commercial instruments used for the moments (hardened/re-packaged for flight, chosen early for "
    "simplicity, low power and small size) respond in a material- or size-dependent way.",
    "measurement_limitation", "SAME", [], None,
    scope="Authors' stated instrument limitation; it applies to the moment instruments (P-Trak, ionization chamber, "
          "DustTrak), not to the two spacecraft smoke detectors.")
add(D, "2.2. Instruments",
    "which is a condensation particle counter that was modified for use in space",
    "Zeroth moment: a P-Trak condensation particle counter, modified with small wall grooves because its isopropanol "
    "condensate does not drain back to the wick in low gravity; a Dynamic Diluter was added so it would not saturate.",
    "measurement_limitation", "SAME", [], None,
    scope="Low-gravity instrument adaptation; the paper says the modification was tested in a separate space "
          "experiment with good results.")
add(D, "2.2. Instruments",
    "The first moment instrument is the ionization chamber from a residential smoke detector",
    "First moment: an ionization chamber taken from a residential smoke detector (Am-241 source), calibrated to "
    "estimate M1; it needs particle concentrations of order 10^5 per cm^3 for adequate signal-to-noise and no dilution.",
    "definition", "SAME", [], "ionization chamber from a residential smoke detector (first-moment instrument)",
    numbers=[num(1e5, "particles/cm^3", "minimum concentration for adequate signal-to-noise", "on the order of 10^5 particles/cm^3")],
    scope="This is a measurement instrument, distinct from the Space Shuttle ionization smoke detector whose "
          "alarm performance was evaluated.")
add(D, "2.2. Instruments",
    "Material-specific calibrations and corrections were needed to account for the range of particle sizes",
    "Third moment: a DustTrak 90-degree light-scattering nephelometer calibrated on Arizona Test Dust; it needed "
    "material-specific calibration factors and particle density to give M3, because its response is not "
    "inherently proportional to mass. SAME-1 carried two DustTraks with 1 um and 10 um impactor inlets.",
    "measurement_limitation", "SAME", [], "DustTrak (third-moment instrument)",
    numbers=[num(90, "degree", "scattering angle", "90°"), num(1, "um", "impactor cut size (one DustTrak)", "1 μm impactor"),
             num(10, "um", "impactor cut size (other DustTrak)", "10 μm impactor")],
    scope="Calibration factors with uncertainty are in Mulholland et al. [5], not in this paper.")
add(D, "2.2. Instruments (SAME hardware description)",
    "a rising piston drew smoke into a 6 liter aging chamber",
    "Sample heated about 60 s in the smoke-generation duct while a rising piston drew smoke into a 6 L aging chamber; "
    "half was pushed almost immediately to the instruments (unaged), the rest after a preset aging period.",
    "test_condition", "SAME", [], None,
    numbers=[num(6, "L", "aging chamber volume", "6 liter"), num(60, "s", "sample heating duration", "approximately 60 sec")],
    conditions=cond(gravity=LOWG, heating_s=60),
    scope="Hardware description for the space experiments; heating duration is approximate.")
add(D, "2.2. Instruments (SAME hardware description)",
    "The SAME hardware system was installed in the Microgravity Science Glovebox (MSG)",
    "SAME ran inside the ISS Microgravity Science Glovebox, which supplied power, data, video, commanding and "
    "containment of the smoke; software ran the sequence after the crew inserted the sample carousel.",
    "test_condition", "SAME", [], None, conditions=cond(gravity=LOWG),
    scope="The paper does not state the gas composition (O2 %) or pressure inside the glovebox during runs "
          "(within the examined text); those fields are left null.")
add(D, "2.2. Instruments (SAME hardware description)",
    "A small cylindrical sample of material (approximately 0.5 cm diameter and 1.3 cm long)",
    "Samples were small cylinders about 0.5 cm in diameter and 1.3 cm long, heated about 60 s by a wrapped "
    "stainless-steel wire held at constant resistance by feedback, keeping wire temperature within a few degrees "
    "Celsius of a material-specific target.",
    "test_condition", "SAME", M5, None,
    numbers=[num(0.5, "cm", "sample diameter", "approximately 0.5 cm"), num(1.3, "cm", "sample length", "1.3 cm"),
             num(60, "s", "heating duration", "approximately 60 sec")],
    conditions=cond(gravity=LOWG, heating_s=60),
    scope="Temperatures are wire temperatures inferred from resistance; per-run values appear only in Table 1 rows.")
add(D, "2.2. Instruments (SAME hardware description)",
    "Space shuttle and ISS smoke detectors were exposed to smoke in the duct.",
    "Both spacecraft smoke detectors were exposed to the smoke inside the SAME diagnostics duct, alongside the "
    "moment instruments.",
    "test_condition", "SAME", M5, "Space shuttle and ISS smoke detectors", conditions=cond(gravity=LOWG),
    scope="Exposure was inside the experiment duct in the glovebox; the paper does not describe testing in the "
          "operational cabin-ventilation installation.")
add(D, "3.0. Results and Discussion",
    "Over 100 samples were tested, comprised of 6 materials commonly used in the spacecraft cabin.",
    "More than 100 samples were tested across six materials: Teflon, Pyrell polyurethane foam, cotton lamp wick "
    "(cellulose), Kapton, silicone rubber, and dibutyl phthalate (DBP) on a porous wick.",
    "test_condition", "SAME", M5 + ["dibutyl phthalate (DBP) on porous wick"], None,
    numbers=[num(100, "samples", "samples tested (lower bound)", "Over 100"), num(6, "materials", "materials tested", "6 materials")],
    conditions=cond(gravity=LOWG),
    scope="Exact count not given. Unaged and aged measurements come from the same sample and are not independent "
          "tests. Conclusions speak of five materials (DBP gave no TEM-visible particles). Whether the count "
          "includes ground tests is not stated.")
add(D, "3.0. Results and Discussion",
    "The baseline air flow velocity was 8.1 cm/s",
    "Baseline duct air flow was 8.1 cm/s; runs went down to 2 cm/s, and a limited set used no forced airflow "
    "during heating.",
    "test_condition", "SAME", M5, None,
    numbers=[num(8.1, "cm/s", "baseline air flow velocity", "8.1 cm/s"), num(2, "cm/s", "lowest forced flow tested", "down to 2 cm/s")],
    conditions=cond(gravity=LOWG, airflow_cm_s=8.1),
    scope="Zero-flow runs are described in Section 3.3 (eleven tests).")
add(D, "3.0. Results and Discussion",
    "to produce 1 to 2 mg of sample mass loss in 60 sec",
    "Baseline temperatures were chosen per material to give 1-2 mg of mass loss in 60 s of heating with usable "
    "signal on the moment instruments; higher-temperature conditions were added that did not saturate the instruments.",
    "test_condition", "SAME", M5, None,
    numbers=[num(1, "mg", "lower target mass loss", "1 to 2 mg"), num(2, "mg", "upper target mass loss", "1 to 2 mg"),
             num(60, "s", "heating duration", "60 sec")],
    conditions=cond(gravity=LOWG, heating_s=60),
    scope="Target temperatures differ by material (examples in Table 1); full list not given in this paper.")
add(D, "3.0. Results and Discussion",
    "particle concentrations were a few million particles per",
    "Typical runs had a few million particles per cm^3 and mass concentrations of 2-15 mg/m^3; some runs had fewer particles.",
    "test_condition", "SAME", M5, None,
    numbers=[num(2, "mg/m^3", "lower typical mass concentration", "2 to 15 mg/m^3"),
             num(15, "mg/m^3", "upper typical mass concentration", "2 to 15 mg/m^3")],
    conditions=cond(gravity=LOWG),
    scope="'Typical runs' only.")
add(D, "3.0. Results and Discussion",
    "The TEM grids recovered from the thermal precipitators on SAME-1 were found to be contaminated",
    "TEM grids from SAME-1 thermal precipitators were contaminated and unusable; with stricter assembly controls, "
    "SAME-2 produced many good particle images.",
    "measurement_limitation", "SAME", [], "thermal precipitator / TEM grids",
    scope="Implies all TEM results in the paper come from SAME-2 (inference from this sentence).")
add(D, "3.1. Moment Instrument Results",
    "reasonably valid for the spherical smoke particles generated from Kapton and lamp wick",
    "The lognormal assumption behind the geometric mean and geometric standard deviation was checked in ground "
    "tests and found reasonably valid for the spherical smoke from Kapton and lamp wick; for other materials the "
    "authors only note Table 1 is somewhat compatible with it.",
    "measurement_limitation", "SAME", ["Kapton", "cellulose lamp wick"], None,
    conditions=cond(gravity="normal gravity (ground tests)"),
    scope="Validation is material-specific; agglomerate smokes (Teflon, Pyrell) were not stated as validated.")
add(D, "3.1. Moment Instrument Results",
    "The aging results show a substantial increase in the observed diameters.",
    "Aging substantially increased measured diameters; the count mean diameter rose more than the diameter of "
    "average mass because coagulation mainly removes the smallest particles; theory predicts a self-preserving "
    "geometric standard deviation near 1.32.",
    "particle_property", "SAME", M5, None,
    numbers=[num(1.32, "-", "theoretical self-preserving geometric standard deviation", "1.32")],
    conditions=cond(gravity=LOWG),
    scope="1.32 is a theoretical value from Hinds [18], not a SAME measurement.")
add(D, "3.1. Moment Instrument Results",
    "Overall, the Teflon and Kapton smoke particles were smallest.",
    "Teflon and Kapton gave the smallest smoke particles; lamp wick, Pyrell and silicone gave substantially larger "
    "diameters of average mass, especially after aging.",
    "particle_property", "SAME", M5, None, conditions=cond(gravity=LOWG),
    scope="Ranking across the five materials for SAME test conditions.")
add(D, "3.1. Moment Instrument Results / Figure 5",
    "exhibit larger portions of the particle distribution (~ 40% of the mass)",
    "From the ratio of DustTraks with 10 um and 1 um impactors, lamp wick and silicone smoke had roughly 40% of "
    "mass in particles above 1 um, versus about 20% for Teflon and Kapton.",
    "particle_property", "SAME", ["cellulose lamp wick", "silicone rubber", "Teflon", "Kapton"], "DustTrak (1 um and 10 um impactors)",
    numbers=[num(40, "% of mass", "fraction above 1 um, lamp wick and silicone", "~ 40% of the mass"),
             num(20, "% of mass", "fraction above 1 um, Teflon and Kapton", "20% of the mass")],
    conditions=cond(gravity=LOWG, aging_s=None),
    scope="Figure 5 covers unaged conditions over several flows/temperatures; dual-impactor setup is described "
          "for SAME-1. Values approximate.")
add(D, "3.1. Moment Instrument Results",
    "will make detection of these smokes challenging for light scattering devices",
    "Because Kapton and Teflon particles are comparatively small, the authors expect them to be hard for "
    "light-scattering detectors to sense, while large lamp-wick and silicone particles would give very large signals.",
    "particle_property", "SAME", ["Kapton", "Teflon", "cellulose lamp wick", "silicone rubber"], "light scattering devices",
    conditions=cond(gravity=LOWG),
    scope="Expectation from particle size; the detector outcome is reported in Section 3.2.")
add(D, "3.1. Moment Instrument Results",
    "without excessive nuisance alarms from large dust particles",
    "Citing Urban et al., the authors say some size discrimination is generally needed so that a detector can "
    "alarm on the weak signal of small Teflon/Kapton smoke without excessive nuisance alarms from large dust.",
    "false_alarm", "SAME", ["Teflon", "Kapton"], None,
    scope="Design reasoning (refs 19, 20); SAME did not measure dust or nuisance-alarm rates in this paper.")
add(D, "3.1. Moment Instrument Results",
    "a detection system capable of measuring more than one moment of the particle size distribution",
    "The authors suggest that separating these smoke particles from the background environment would be helped "
    "by a detection system that measures more than one moment of the size distribution.",
    "technology_need", "SAME", ["Teflon", "Kapton"], None,
    scope="Suggestion ('suggests'); no multi-moment detector was tested in this paper.")
add(D, "3.1. Moment Instrument Results / Figure 6",
    "a strong trend of increased particle size at low flow rates",
    "Across five duct flow velocities (constant temperature per material, no aging), diameter of average mass "
    "rose strongly at low flow, most for silicone and Pyrell; the authors infer smoke trapped in avionics "
    "enclosures or poorly ventilated areas would be substantially larger than smoke in well-ventilated areas.",
    "particle_property", "SAME", M5, None,
    conditions=cond(gravity=LOWG, aging_s=0),
    scope="The enclosure statement is an extrapolation, not a measurement inside an avionics box.")
add(D, "3.1. Moment Instrument Results / Figure 7",
    "producing an increase in the diameter from 55 to 100%",
    "To mimic smoke held in poorly ventilated spaces, aging time was varied from 30 s to 2000 s; diameter of "
    "average mass grew consistently with aging, by 55% to 100%.",
    "particle_property", "SAME", M5, None,
    numbers=[num(30, "s", "shortest aging time", "30 sec"), num(2000, "s", "longest aging time", "2000 sec"),
             num(55, "%", "lower diameter increase with aging", "55 to 100%"), num(100, "%", "upper diameter increase with aging", "55 to 100%")],
    conditions=cond(gravity=LOWG, airflow_cm_s=8.1, aging_s="30-2000"),
    scope="Figure 7: five materials at low temperature and 8.1 cm/s.")
add(D, "3.1. Moment Instrument Results / Figure 8",
    "Overall the results correlate strongly with a slope of 1.",
    "Ground tests duplicating flight baseline (8.1 cm/s, 1-2 mg in 60 s, nominal aging 720 s) gave diameters of "
    "average mass that correlate strongly with low-gravity results with slope 1, so at 8.1 cm/s or more, "
    "normal-gravity smoke sizes are roughly the same as low-gravity ones.",
    "particle_property", "SAME", M5, None,
    numbers=[num(8.1, "cm/s", "flow velocity of comparison", "8.1 cm/s"), num(720, "s", "nominal aging", "720 sec"),
             num(1, "-", "slope of low-g vs 1-g diameter", "slope of 1")],
    conditions=cond(gravity="low gravity vs normal gravity", airflow_cm_s=8.1, heating_s=60, aging_s="218-1923 (Fig. 8, all combined)"),
    scope="Valid for flows of about 8.1 cm/s or higher (range of current spacecraft ventilation); no correlation "
          "coefficient is given in the text.")
add(D, "3.1. Moment Instrument Results",
    "could increase the diameter of average mass by as much as a factor of 2.5",
    "Limit of the ground-test analogy: Figure 6 implies lower flow could raise diameter of average mass up to "
    "2.5 times, and at low or zero flow low-g smoke stays concentrated while 1-g smoke rises and dilutes, so sizes "
    "would differ.",
    "measurement_limitation", "SAME", M5, None,
    numbers=[num(2.5, "x", "possible increase of diameter of average mass at lower flow", "as much as a factor of 2.5")],
    conditions=cond(gravity="low gravity vs normal gravity"),
    scope="Error estimate for using 1-g tests at low flow; not a measured 1-g vs low-g difference.")
add(D, "3.1. Moment Instrument Results",
    "normal-gravity smoke tests with proper attention to smoke aging time may be an adequate substitute",
    "The authors suggest normal-gravity smoke tests that properly account for aging time may adequately "
    "replace costly flight experiments.",
    "recommendation", "SAME", M5, None, conditions=cond(gravity="normal gravity"),
    scope="Hedged ('may'); applies to ventilated conditions (about 8.1 cm/s or more), not to zero-flow low-g cases.")
add(D, "3.2. Spacecraft Smoke Detector Results",
    "Kapton smoke particles are substantially smaller than the other materials",
    "Selected ISS runs (Table 1) show Kapton smoke much smaller than other materials, with TEM diameters of "
    "average mass below 0.3 um; because the ISS detector is calibrated with 0.6 um particles and uses a laser of "
    "about 1 um wavelength, reduced performance is expected for much smaller particles.",
    "measurement_limitation", "SAME", ["Kapton"], "ISS smoke detector",
    numbers=[num(0.3, "um", "upper bound of Kapton TEM diameter of average mass", "less than 0.3 μm"),
             num(0.6, "um", "ISS detector calibration particle size", "0.6 μm"),
             num(1, "um", "ISS detector laser wavelength", "approximately 1 μm")],
    conditions=cond(gravity=LOWG),
    scope="Explains the mechanism; the alarm outcome is in the next items.")
add(D, "3.2. Spacecraft Smoke Detector Results / Figure 9",
    "cases where the detectors would have failed to alarm",
    "In Figure 9, points under the voltage threshold lines are runs in which the detectors would not have alarmed.",
    "definition", "SAME", M5, "Space Shuttle smoke detector; ISS smoke detector",
    conditions=cond(gravity=LOWG),
    scope="Missed alarm is inferred from signal below the alarm boundary; threshold values appear only graphically "
          "in Figure 9 and are not stated in the text.")
add(D, "3.2. Spacecraft Smoke Detector Results",
    "For the Space Shuttle detector, the materials in this category are Kapton, Teflon,",
    "Space Shuttle detector: some runs with Kapton, Teflon and lamp wick smoke fell below the alarm boundary "
    "(would have failed to alarm).",
    "missed_alarm", "SAME", ["Kapton", "Teflon", "cellulose lamp wick"], "Space Shuttle smoke detector",
    conditions=cond(gravity=LOWG, aging_s=0),
    scope="Shuttle detector data set is small and contains no aged-smoke tests; the text gives no counts or "
          "fractions for the Shuttle detector.")
add(D, "3.2. Spacecraft Smoke Detector Results",
    "The ISS detector would not have alarmed for over half of the Kapton smoke tests",
    "ISS detector: had difficulty with Kapton and Teflon; it would not have alarmed for more than half of the "
    "Kapton smoke tests and about two thirds of the Teflon tests.",
    "missed_alarm", "SAME", ["Kapton", "Teflon"], "ISS smoke detector",
    numbers=[num(0.5, "fraction of Kapton tests", "share of Kapton tests below alarm boundary (lower bound)", "over half"),
             num(0.667, "fraction of Teflon tests", "share of Teflon tests below alarm boundary", "2/3")],
    conditions=cond(gravity=LOWG),
    scope="Fractions of SAME runs shown in Figure 9 (aged and unaged mixed); the number of Kapton and Teflon runs "
          "is not stated in the text. 'Would not have alarmed' = signal below threshold, not an observed alarm event.")
add(D, "3.2. Spacecraft Smoke Detector Results",
    "The Shuttle was somewhat less sensitive than the ISS detector but, for the conditions tested,",
    "Overall the Shuttle (ionization) detector was somewhat less sensitive than the ISS detector, but under the "
    "tested conditions it did better than the ISS detector on Teflon smoke.",
    "missed_alarm", "SAME", ["Teflon"], "Space Shuttle smoke detector vs ISS smoke detector",
    conditions=cond(gravity=LOWG),
    scope="Qualitative comparison limited to the conditions tested; Shuttle data excludes aging tests.")
add(D, "3.2. Spacecraft Smoke Detector Results",
    "There is a much smaller data set for the Space Shuttle detector",
    "The Space Shuttle detector was run only intermittently because its internal pump drew three litres per "
    "minute of aerosol, which made aging tests with it impossible; its data set is much smaller.",
    "measurement_limitation", "SAME", [], "Space Shuttle smoke detector",
    numbers=[num(3, "L/min", "Shuttle detector sample flow", "three liters per minute")],
    conditions=cond(gravity=LOWG),
    scope="Limits any conclusion about the Shuttle detector on aged smoke.")
add(D, "3.2. Spacecraft Smoke Detector Results",
    "The ISS detector signal was frequently saturated mainly by the larger smoke materials",
    "The ISS detector signal often saturated, mainly with the larger-particle smokes (silicone, Pyrell, lamp wick).",
    "measurement_limitation", "SAME", ["silicone rubber", "Pyrell (polyurethane foam)", "cellulose lamp wick"], "ISS smoke detector",
    conditions=cond(gravity=LOWG),
    scope="Saturation means those smokes exceeded the alarm level; it is a dynamic-range limit, not a missed alarm.")
add(D, "3.2. Spacecraft Smoke Detector Results",
    "Kapton and Teflon are very commonly used in spacecraft, especially in electrical systems",
    "The poor ISS-detector response to Kapton and Teflon matches the known weaker light scattering of particles "
    "much smaller than the wavelength, and is a concern because these materials are widespread in spacecraft "
    "electrical systems, likely among the first to overheat in a smoke event.",
    "technology_need", "SAME", ["Kapton", "Teflon"], "ISS smoke detector",
    scope="Priority rationale by the authors; 'likely first to overheat' is an expectation, not measured.")
add(D, "3.2. Spacecraft Smoke Detector Results / Figure 9 caption",
    "In both cases the alarm boundary is indicated with a dashed red line.",
    "Figure 9 plots detector signal versus particle number concentration for the Space Shuttle detector (signal "
    "as offset from baseline, A/D-scaled) and the ISS detector, by material, with the alarm boundary marked.",
    "measurement_limitation", "SAME", M5, "Space Shuttle smoke detector; ISS smoke detector",
    conditions=cond(gravity=LOWG),
    scope="Per-run values, alarm voltages and run counts are only graphical; not extracted (no digitisation done).")
add(D, "3.3. TEM Results",
    "DBP presented no particles that were visible via TEM",
    "Particles were collected on 72 TEM grids; DBP showed no visible particles (probably liquid evaporating in the "
    "microscope vacuum) and silicone smoke lost its volatile part, leaving only residue.",
    "measurement_limitation", "SAME", ["dibutyl phthalate (DBP)", "silicone rubber"], "thermal precipitator / TEM",
    numbers=[num(72, "TEM grids", "grids with collected particles", "72")],
    scope="Grids are samples, not independent tests. TEM morphology therefore missing/limited for DBP and silicone.")
add(D, "3.3. TEM Results",
    "the most visible change is the disappearance of the smallest particles",
    "In TEM images aging mainly shows up as the loss of the smallest particles (they coagulate onto larger ones) "
    "rather than as a visible growth of particle size.",
    "particle_property", "SAME", ["Pyrell (polyurethane foam)", "cellulose lamp wick", "Kapton"], None,
    conditions=cond(gravity=LOWG),
    scope="Figure 11 shows Pyrell, lamp wick and Kapton.")
add(D, "3.3. TEM Results",
    "If the particles are liquid, the colliding particles will coalesce and form larger droplets.",
    "Morphology depends on material: liquid-like lamp wick and Kapton smoke coalesces into droplets, while solid "
    "Teflon and Pyrell smoke forms low-density fractal-like agglomerates of primary particles.",
    "particle_property", "SAME", ["cellulose lamp wick", "Kapton", "Teflon", "Pyrell (polyurethane foam)"], None,
    conditions=cond(gravity=LOWG),
    scope="Based on TEM images (SAME-2).")
add(D, "3.3. TEM Results",
    "Key parameters affecting the properties of the smoke produced here are the convective flow",
    "The authors list convective flow past the heated wire, wire temperature, aging time and the low-gravity "
    "condition as key controls of smoke properties; hotter wires give more mass and larger diameter of average mass.",
    "test_condition", "SAME", M5, None, conditions=cond(gravity=LOWG),
    scope="Qualitative summary of controlling parameters.")
add(D, "3.3. TEM Results (Impact of flow on particle morphology)",
    "Eleven tests were performed with the zero-flow condition.",
    "Zero-flow (no forced flow through the smoke-generation duct) was added late by changing valve operation; it "
    "gave very concentrated smoke and enhanced low-g aging. Eleven zero-flow tests were run.",
    "test_condition", "SAME", M5, None,
    numbers=[num(11, "tests", "zero-flow tests", "Eleven")],
    conditions=cond(gravity=LOWG, airflow_cm_s=0),
    n=11,
    scope="Zero-flow refers to forced flow; thermal-expansion flow of 0.5-1.5 cm/s was still observed.")
add(D, "3.3. TEM Results (Impact of flow on particle morphology)",
    "approximately 2/3 of the smoke was lost from the system",
    "Because the hardware was not designed for zero flow, about two thirds of the smoke escaped by diffusion and "
    "thermal expansion through the sample carousel into the glovebox, so particle counts were lower and TEM grids "
    "had few particles.",
    "measurement_limitation", "SAME", M5, None,
    numbers=[num(0.667, "fraction", "smoke lost in zero-flow runs", "approximately 2/3")],
    conditions=cond(gravity=LOWG, airflow_cm_s=0),
    scope="Applies to the eleven zero-flow tests.")
add(D, "3.3. TEM Results (Impact of flow on particle morphology)",
    "The diameter of average mass is a factor of 1.7 larger for the zero-flow",
    "With zero forced flow, thermal-expansion flow of 0.5-1.5 cm/s was seen on video, vapor concentration was "
    "about 8 times the 8.1 cm/s case, and diameter of average mass was on average 1.7 times larger (from 1.3x for "
    "Teflon to 2.8x for Kapton).",
    "particle_property", "SAME", M5, None,
    numbers=[num(0.5, "cm/s", "lowest thermal-expansion smoke flow", "0.5 cm/s"), num(1.5, "cm/s", "highest thermal-expansion smoke flow (Kapton, Teflon)", "1.5 cm/s"),
             num(8, "x", "vapor concentration vs 8.1 cm/s case", "about eight times higher"),
             num(1.7, "x", "average D_m ratio zero-flow / 8.1 cm/s", "a factor of 1.7"),
             num(1.3, "x", "D_m ratio for Teflon", "1.3 for Teflon"), num(2.8, "x", "D_m ratio for Kapton", "2.8 for Kapton")],
    conditions=cond(gravity=LOWG, airflow_cm_s=0),
    scope="The Conclusions describe the same effect as 'on average, double the size' - inconsistent with 1.7 here.")
add(D, "3.3. TEM Results (Impact of flow on particle morphology)",
    "fractal-like clusters with up to 30 primary spheres",
    "Pyrell smoke changed from fractal-like clusters (up to 30 primary spheres) at 8.1 cm/s to much larger single "
    "spheres at zero flow, likely due to higher gas temperature with conduction-dominated heat transport.",
    "particle_property", "SAME", ["Pyrell (polyurethane foam)", "cellulose lamp wick"], None,
    numbers=[num(30, "primary spheres", "max primaries per Pyrell cluster at 8.1 cm/s", "up to 30 primary spheres")],
    conditions=cond(gravity=LOWG, airflow_cm_s=0),
    scope="TEM images (Figure 12) for Pyrell and lamp wick.")
add(D, "3.3. TEM Results (Impact of flow on particle morphology)",
    "It is important to recognize that this zero-flow condition is unique to low-gravity scenarios.",
    "Zero flow is specific to low gravity (at 1 g buoyancy would widen the mixing zone), so the larger particles "
    "seen in zero-flow runs should be considered when developing improved spacecraft fire detection.",
    "technology_need", "SAME", M5, None, conditions=cond(gravity=LOWG, airflow_cm_s=0),
    scope="Cannot be reproduced by normal-gravity tests; based on eleven zero-flow runs with smoke loss.")
add(D, "4.0. Conclusions",
    "all samples produced significant numbers of sub-micron particles that are readily detected using an ionization",
    "For SAME conditions, all samples produced many sub-micron particles that the authors say an ionization smoke "
    "detector readily detects.",
    "particle_property", "SAME", M5, "an ionization smoke detector (unspecified)",
    conditions=cond(gravity=LOWG),
    scope="The text does not say which ionization device is meant; Section 3.2 reports Space Shuttle ionization "
          "detector runs below the alarm boundary for Kapton, Teflon and lamp wick, so this is not a statement "
          "that the Shuttle detector alarmed on all smokes.")
add(D, "4.0. Conclusions",
    "Particle sizes ranged from 100 to 600 nm",
    "Measured particle sizes were 100-600 nm and consistent with a lognormal distribution.",
    "particle_property", "SAME", M5, None,
    numbers=[num(100, "nm", "smallest particle size", "100 to 600 nm"), num(600, "nm", "largest particle size", "100 to 600 nm")],
    conditions=cond(gravity=LOWG),
    scope="Size measure (mean type) not specified in the bullet.")
add(D, "4.0. Conclusions",
    "on average, double the size of those produced at the nominal 8.1 cm/s flow rate",
    "Conclusions: lower air flow substantially increased diameter of average mass; zero-flow particles were on "
    "average about double the size seen at 8.1 cm/s.",
    "particle_property", "SAME", M5, None,
    numbers=[num(2, "x", "average size ratio zero-flow / 8.1 cm/s", "double")],
    conditions=cond(gravity=LOWG, airflow_cm_s=0),
    scope="Section 3.3 gives the average factor as 1.7 (range 1.3-2.8); internal inconsistency in the paper.")
add(D, "4.0. Conclusions",
    "Ground based testing at 8.1 cm/s showed particle dimensions very close to the flight results.",
    "Ground tests at 8.1 cm/s matched flight particle sizes closely, so low-g smoke at flows of at least 8.1 cm/s "
    "is well predicted by ground testing.",
    "particle_property", "SAME", M5, None,
    numbers=[num(8.1, "cm/s", "flow velocity", "8.1 cm/s")],
    conditions=cond(gravity="low gravity vs normal gravity", airflow_cm_s=8.1),
    scope="Does not apply to low/zero-flow conditions.")
add(D, "4.0. Conclusions",
    "showed reduced performance for Kapton and Teflon smoke particles",
    "Conclusions: the light-scattering ISS detector performed worse on the smaller Kapton and Teflon smoke; the "
    "ionization-based Space Shuttle detector did slightly better on Teflon smoke.",
    "missed_alarm", "SAME", ["Kapton", "Teflon"], "ISS Detector (light scattering); Space Shuttle detector (ionization)",
    conditions=cond(gravity=LOWG),
    scope="Restates Section 3.2.")
add(D, "4.0. Conclusions",
    "the detection environment is complicated by spacecraft background aerosols which can be quite large",
    "Real spacecraft fire scenarios involve more materials and heating conditions than tested, and detection is "
    "complicated by background aerosols in the cabin that can be quite large.",
    "false_alarm", None, [], None,
    scope="Authors' assessment; background aerosols were not measured in this paper.")
add(D, "4.0. Conclusions",
    "improbable that a single-moment device can be sensitive across the smoke particle size spectrum",
    "The authors judge it improbable that any single-moment detector can be sensitive across the whole smoke size "
    "range while also resisting false alarms.",
    "technology_need", None, [], "single-moment device",
    scope="Statement concerns single-moment devices; the NIST news release broadens it to 'no single smoke "
          "detection method currently available'.")
add(D, "Acknowledgements",
    "the crews of ISS increments 10, 13, 15, and 24 are gratefully acknowledged",
    "Acknowledgements thank the SAME team and the crews of ISS increments 10, 13, 15 and 24; SAME was run under the "
    "ISS Exploration Research Project of the Exploration Technology Development Program.",
    "investigation_profile", "SAME", [], None,
    numbers=[num(10, "increment", "ISS increment acknowledged", "10"), num(13, "increment", "ISS increment acknowledged", "13"),
             num(15, "increment", "ISS increment acknowledged", "15"), num(24, "increment", "ISS increment acknowledged", "24")],
    scope="Increment list as printed; mapping of increments to SAME-1/SAME-2 or other activities not given.")
add(D, "References [4]",
    "Smoke Characterization and Feasibility of the Moment Method for Spacecraft Fire Detection",
    "Meyer et al. 2015, Aerosol Sci. Tech. 49(5):299-309 - moment-method feasibility and SAME ground tests "
    "(cited for validation and Table 1).",
    "reference", "SAME", [], None, scope="Pointer only; not fetched in this step.")
add(D, "References [5]",
    "Pyrolysis Smoke Generated under Low-Gravity Conditions",
    "Mulholland et al. 2015, Aerosol Sci. Tech. 49(5):310-321 - heating sequence, DustTrak calibration factors, "
    "aging effects.",
    "reference", "SAME", [], None, scope="Pointer only; not fetched in this step.")
add(D, "References [20]",
    "Smoke Particle Sizes in Low-Gravity and Implications for the Design of Spacecraft Smoke Detectors",
    "Urban et al. 2009 ICES paper 2009-01-2468 - cited for size discrimination vs nuisance alarms.",
    "reference", "SAME", [], None, scope="Pointer only; not fetched in this step.")
add(D, "References [21]",
    "Particle Morphology and Elemental Composition of Smoke Generated by Overheating Common Spacecraft Materials",
    "Meyer, NASA TM 2015-218891 - TEM morphology/elemental composition of SAME smoke.",
    "reference", "SAME", [], None, scope="Pointer only; not fetched in this step.")

# Table 1 rows: (label, temp, aging, n, Dm_TEM, Dm_mom, D_TEM, D_mom, Dg_TEM, Dg_mom, sg_TEM, sg_mom)
T1 = [
    ("Lampwick #54 unaged", "Low 264.7", 56.8, 511, 0.403, 0.253, 0.304, 0.110, 0.255, 0.072, 1.84, 2.49, "cellulose lamp wick"),
    ("Lampwick #55 aged", "Low 262.9", 218.0, 196, 0.499, 0.320, 0.359, 0.149, 0.284, 0.102, 2.07, 2.40, "cellulose lamp wick"),
    ("Kapton #94 aged", "Low 527.3", 567.4, 1353, 0.159, 0.176, 0.120, 0.136, 0.103, 0.119, 1.72, 1.67, "Kapton"),
    ("Kapton #62 unaged", "High 574.3", 38.8, 1320, 0.226, 0.251, 0.180, 0.148, 0.158, 0.114, 1.68, 2.07, "Kapton"),
    ("Kapton #62 aged", "High 574.3", 807.6, 796, 0.289, 0.383, 0.235, 0.243, 0.210, 0.194, 1.63, 1.96, "Kapton"),
    ("Pyrell #63 unaged", "Low 225.3", 55.6, 3436, 0.394, 0.392, 0.290, 0.207, 0.244, 0.151, 1.81, 2.22, "Pyrell (polyurethane foam)"),
    ("Pyrell #63 aged", "Low 225.3", 839.6, 2658, 0.468, 0.539, 0.354, 0.359, 0.292, 0.293, 1.92, 1.89, "Pyrell (polyurethane foam)"),
    ("Pyrell #64 unaged", "High 242.1", 47.0, 1888, 0.411, 0.445, 0.298, 0.254, 0.249, 0.192, 1.84, 2.12, "Pyrell (polyurethane foam)"),
    ("Pyrell #64 aged", "High 242.1", 842.4, 1560, 0.540, 0.616, 0.403, 0.450, 0.328, 0.385, 1.98, 1.75, "Pyrell (polyurethane foam)"),
]
for (lab, temp, age, n, a, b, c, d, e, f, g, h, mat) in T1:
    tval = float(temp.split()[1])
    add(D, f"Table 1, row '{lab}'", lab,
        f"Table 1 (selected ISS runs, TEM vs moment method): {lab}, {temp.split()[0].lower()} temperature setting "
        f"{tval} C, net aging {age} s, {n} particles counted in TEM. Diameter of average mass TEM {a} / moment {b} um; "
        f"count mean TEM {c} / moment {d} um; geometric mean TEM {e} / moment {f} um; geometric std TEM {g} / moment {h}.",
        "particle_property", "SAME", [mat], None,
        numbers=[num(tval, "degC", "sample temperature", temp), num(age, "s", "net aging duration", str(age)),
                 num(n, "particles", "particles counted in TEM", str(n)),
                 num(a, "um", "diameter of average mass, TEM", f"{a:.3f}"), num(b, "um", "diameter of average mass, moment", f"{b:.3f}"),
                 num(c, "um", "count mean diameter, TEM", f"{c:.3f}"), num(d, "um", "count mean diameter, moment M1/M0", f"{d:.3f}"),
                 num(e, "um", "geometric mean diameter, TEM (Dgn)", f"{e:.3f}"), num(f, "um", "geometric mean diameter, moment", f"{f:.3f}"),
                 num(g, "-", "geometric std, TEM", f"{g:.2f}"), num(h, "-", "geometric std, moment", f"{h:.2f}")],
        conditions=cond(gravity=LOWG, aging_s=age),
        scope="Single run (unaged and aged rows with the same run number share one sample). TEM data must come from "
              "SAME-2 because SAME-1 grids were unusable (inference). Flow velocity for these runs is not given in "
              "the table. Table 1 has no Teflon or silicone rows. 'Unaged' rows still have tens of seconds of net aging.")

# ---------------- nist2018_pub ----------------
D = "nist2018_pub"
add(D, "Publication record header / Citation",
    "Evaluation of Spacecraft Smoke Detector Performance in the Low-Gravity Environment",
    "NIST publication record for the paper: published 25 April 2018 (online), Fire Safety Journal vol. 98, DOI "
    "10.1016/j.firesaf.2018.04.004; keywords fire detector, microgravity, smoke.",
    "reference", "SAME", [], None,
    numbers=[num(98, "volume", "Fire Safety Journal volume", "98")],
    scope="Bibliographic record only; NIST lists its own authors first.")
add(D, "Abstract (NIST record)",
    "characterize smoke particles generated from the oxidative pyrolysis of five common spacecraft materials",
    "The abstract on the NIST record (apparently the published wording) says the ISS experiment characterized "
    "smoke from oxidative pyrolysis of five common spacecraft materials.",
    "investigation_profile", "SAME", M5, None, conditions=cond(gravity=LOWG),
    scope="The PMC manuscript abstract does not give the count; its Results section says 6 materials including DBP.")
add(D, "Abstract (NIST record)",
    "The two spacecraft smoke detectors did not successfully detect every type of smoke",
    "Same headline as the manuscript: the two spacecraft smoke detectors did not detect every smoke type, so next-"
    "generation detectors must be improved and tested against smoke from relevant space materials.",
    "missed_alarm", "SAME", M5, "two spacecraft smoke detectors", conditions=cond(gravity=LOWG),
    scope="Corroborates meyer2018 abstract wording.")

# ---------------- nist2018_news ----------------
D = "nist2018_news"
add(D, "Headline",
    "One Detector Doesn’t ‘Fit All’ for Smoke in Spacecraft",
    "NIST news release (1 May 2018) headline: no single detector suits all spacecraft smoke.",
    "context", "SAME", [], None, scope="Press framing of meyer2018.")
add(D, "Body, paragraph 2",
    "Working with the National Institute of Standards and Technology (NIST) since 2002",
    "The release says NASA has worked with NIST since 2002 studying smoke behaviour in microgravity as a basis for "
    "spaceflight smoke detection.",
    "context", None, [], None, numbers=[num(2002, "year", "start of NASA-NIST collaboration", "since 2002")],
    scope="Programmatic statement by NIST.")
add(D, "Body, paragraph on detection in space",
    "are placed within the ventilation system rather than on a compartment wall",
    "The release explains that ISS and modern spacecraft smoke detectors sit in the ventilation system rather than "
    "on walls, since without buoyancy smoke does not rise.",
    "context", None, [], "smoke detectors on the ISS", scope="General explanatory statement; no data.")
add(D, "Body, paragraph on detection in space",
    "with the smoke often aggregating into large particles or long chains",
    "The release states that in microgravity flames are spherical and smoke often aggregates into large particles or "
    "long chains spreading in all directions.",
    "context", None, [], None, scope="General press statement, not a SAME result; not quantified.")
add(D, "Body, SAME description",
    "SAME investigated the smoke particles produced by five materials commonly found aboard spacecraft",
    "Five materials: cellulose (cotton lamp wick), Kapton (thermal insulation), silicone rubber (seals/gaskets), "
    "Teflon (wire insulation) and Pyrell (polyurethane packing foam).",
    "investigation_profile", "SAME", M5, None,
    scope="Uses the name 'Smoke and Aerosol Measurement Experiment'; the paper says 'Smoke Aerosol Measurement "
          "Experiment'. DBP is not mentioned.")
add(D, "Body, SAME description",
    "the ionization model used during the space shuttle program and the photoelectric system",
    "Per the release, samples were loaded into a carousel in an ISS glovebox, heated electrically, aged in a "
    "chamber, and the smoke routed to six devices including the Shuttle-era ionization detector and the "
    "photoelectric ISS detector.",
    "investigation_profile", "SAME", M5, "ionization model (space shuttle program); photoelectric system (ISS)",
    conditions=cond(gravity=LOWG), scope="Press description; instrument list wording differs from the paper.")
add(D, "Body, quote from T. Cleary (NIST)",
    "the rate of sample heating, the airflow passing around the heated material and the age",
    "NIST's Tom Cleary is quoted that three factors were varied - sample heating rate, airflow around the sample "
    "and smoke age - to represent a range of fire conditions.",
    "test_condition", "SAME", M5, None, conditions=cond(gravity=LOWG),
    scope="Paper describes controlled heating temperature rather than heating rate.")
add(D, "Body, quote from M. Meyer (NASA GRC)",
    "it frequently failed to detect the smaller smoke particles from Teflon and Kapton",
    "Meyer is quoted that the photoelectric ISS detector easily sensed the large particles from cellulose, silicone "
    "and Pyrell but often failed on the smaller Teflon and Kapton particles - a concern since these are used "
    "extensively in electronics, called the most likely fire/smoke source in space.",
    "missed_alarm", "SAME", ["Teflon", "Kapton", "cellulose lamp wick", "silicone rubber", "Pyrell (polyurethane foam)"],
    "light-scattering photoelectric ISS detector", conditions=cond(gravity=LOWG),
    scope="Press quote; quantitative fractions are in meyer2018 Section 3.2. 'Most likely source' is the speaker's claim.")
add(D, "Body, after Meyer quote",
    "older ionization detector from the space shuttle era fared only slightly better for Teflon smoke",
    "The release says the older Shuttle-era ionization detector did only slightly better for Teflon smoke.",
    "missed_alarm", "SAME", ["Teflon"], "ionization detector from the space shuttle era",
    conditions=cond(gravity=LOWG), scope="Press paraphrase of the paper's conclusion.")
add(D, "Body, quote from M. Meyer",
    "no single smoke detection method currently available is sensitive enough to detect all possible",
    "Meyer is quoted that, given the many materials and heating conditions and background aerosols such as dust, "
    "the team concluded no currently available single detection method is sensitive enough for all smoke particle sizes.",
    "technology_need", "SAME", [], None,
    scope="Broader than the paper, which says a single-moment device is improbable to cover the size spectrum and "
          "resist false alarms. Dust is named here explicitly as background aerosol.")
add(D, "Body, quote from M. Meyer",
    "More research is needed to better understand how fires behave in microgravity",
    "Meyer calls for more research on how fires behave in microgravity and how to detect them as early as possible "
    "from whatever smoke they make.",
    "research_question", None, [], None, scope="Press quote; no specific research questions listed.")
add(D, "Body, recommendation paragraph",
    "Because not all of the particles were consistently detected, the researchers recommend that",
    "The release repeats the paper's recommendation that next-generation spacecraft fire detectors be improved and "
    "tested against smoke from relevant space materials.",
    "recommendation", "SAME", [], None, scope="Quotes meyer2018 abstract.")
add(D, "Body, Saffire paragraphs",
    "which also will include smoke particle measurements",
    "The release presents Saffire as the follow-on: three tests in 2016-2017 in uncrewed cargo vehicles, and three "
    "more burns scheduled for 2019-2020 that would include smoke particle measurements, with NIST calibrating the "
    "particle instruments.",
    "followup_solution", "Saffire", [], None,
    numbers=[num(3, "tests", "Saffire tests 2016-2017", "three tests"), num(3, "burns", "further Saffire burns scheduled 2019-2020", "Three more")],
    conditions=cond(gravity="low gravity (uncrewed cargo vehicle)"),
    scope="Forward-looking as of May 2018; whether these occurred as planned is not verified in this source.")
add(D, "Body, opening paragraph",
    "A lithium-perchlorate canister, designed to generate oxygen via a chemical reaction, suddenly burst into flames",
    "The release opens with the February 1997 Mir fire from an oxygen-generating lithium-perchlorate canister, "
    "which filled the station with dense smoke.",
    "context", None, [], None, scope="Historical context; not SAME data.")


def main():
    texts = {d: open(os.path.join(ROOT, "text", d + ".txt"), encoding="utf-8").read() for d in DOCS}
    ntexts = {d: norm(t) for d, t in texts.items()}
    bad = 0
    for i, it in enumerate(ITEMS, 1):
        it["item_id"] = f"{SK}-{i:02d}"
        q = norm(it["anchor_quote"])
        nw = len(q.split())
        cnt = ntexts[it["doc_id"]].count(q)
        if nw > 15 or cnt == 0:
            bad += 1
            print("ANCHOR FAIL", it["item_id"], nw, cnt, q)
    docs = []
    for d, m in DOCS.items():
        rawp = os.path.join(ROOT, "raw", d, m["raw"])
        meta = dict(doc_id=d, title=m["title"], year=m["year"], authors=m["authors"], url=m["url"],
                    retrieved_utc=RETRIEVED, sha256=sha256(rawp), bytes=os.path.getsize(rawp), page_count=None,
                    identifiers=m["identifiers"], license_note=m["license_note"], accessible=m["accessible"],
                    access_note=m["access_note"], raw_file=m["raw"],
                    text_path=os.path.join(ROOT, "text", d + ".txt"),
                    text_method="sources/tools/html2txt_meyer2018.py (" + ("pmc" if d == "meyer2018" else "nist") + " mode)")
        for fn, desc in m["extra_files"].items():
            fp = os.path.join(ROOT, "raw", d, fn)
            meta.setdefault("extra_files", []).append(dict(file=fn, description=desc, sha256=sha256(fp),
                                                           bytes=os.path.getsize(fp)))
        with open(os.path.join(ROOT, "raw", d, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1, ensure_ascii=False)
        docs.append(dict(doc_id=d, title=m["title"], year=m["year"], authors=m["authors"], url=m["url"],
                         local_path=rawp, text_path=meta["text_path"], sha256=meta["sha256"], page_count=None,
                         identifiers=m["identifiers"], accessible=m["accessible"], access_note=m["access_note"]))
    out = dict(
        source_key=SK,
        documents=docs,
        items=ITEMS,
        inaccessible=[
            dict(what="Publisher version of record, Fire Safety Journal 98 (2018) 74-81 (sciencedirect, PII S0379711216302181)",
                 why="Paywalled/blocked in the Model C audit (Meyer2018.blocked.html is a PMC proof-of-work interstitial); "
                     "not re-attempted. The PMC author manuscript was used instead, so wording may differ slightly from the final article."),
            dict(what="Per-run values behind Figure 9 (detector signal vs number concentration) and Figures 5-8",
                 why="Only available as images; no data table in the paper. Not digitised in this step (no numbers invented)."),
        ],
        search_log=[
            dict(query="local check of Model C references", where="external/model_c/data/references/", hits=3,
                 notes="Meyer2018.blocked.html (PMC proof-of-work page, no content), PMC7918997.html/.txt (author manuscript), detector_fig9.jpg (figure image)."),
            dict(query="curl https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/", where="PMC", hits=1,
                 notes="HTTP 200, 175412 bytes; identical to Model C copy except session tokens."),
            dict(query="curl https://api.crossref.org/works/10.1016/j.firesaf.2018.04.004", where="Crossref API", hits=1,
                 notes="Confirms title, 8 authors, Fire Safety Journal 98, pages 74-81, issued 2018-06; AM license from 2019-04-25."),
            dict(query="curl NIST publication page", where="www.nist.gov/publications", hits=1,
                 notes="HTTP 200; abstract + citation; only a DOI link, no NIST PDF."),
            dict(query="curl NIST news release 2018/05", where="www.nist.gov/news-events", hits=1, notes="HTTP 200; full release text."),
        ],
        open_questions=[
            "How many Kapton, Teflon and other runs did the ISS and Space Shuttle detectors see? The text gives only "
            "'over half' (Kapton) and '2/3' (Teflon) for the ISS detector; counts would need Figure 9 digitisation "
            "(an image of it exists at external/model_c/data/references/detector_fig9.jpg).",
            "Alarm threshold voltages for both detectors are shown only as dashed lines in Figure 9, not in the text.",
            "Gas composition (O2 %) and pressure inside the Microgravity Science Glovebox during SAME runs are not stated "
            "in this paper (within the examined text); presumably cabin-like but unverified.",
            "The conclusion bullet that sub-micron smoke is 'readily detected using an ionization smoke detector' does "
            "not name the device; it may refer to the residential ionization chamber used as first-moment instrument, "
            "since the Space Shuttle ionization detector had below-threshold runs for Kapton, Teflon and lamp wick.",
            "Zero-flow size increase is 1.7x on average in Section 3.3 but 'double' in the Conclusions - which is correct?",
            "Results say 6 materials (incl. DBP); Conclusions, NIST abstract and news release say five. DBP role (reference "
            "aerosol?) is not explained in this paper.",
            "Which runs belong to SAME-1 vs SAME-2 is not stated for the detector results (Figure 9).",
            "No dust/nuisance-aerosol tests were reported in this paper; false-alarm concerns are argued, not measured "
            "(within the examined sources).",
        ],
    )
    with open(os.path.join(ROOT, "extracted", SK + ".json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("items", len(ITEMS), "anchor failures", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
