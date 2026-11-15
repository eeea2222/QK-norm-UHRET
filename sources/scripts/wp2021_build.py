"""Build sources/extracted/wp2021.json and sources/raw/wp2021/meta.json.

Run with: .venv/bin/python -I build.py
Anchors are verified against sources/text/wp2021.txt page-by-page.
"""
import hashlib
import json
import os
import sys

ROOT = "/home/efeai/Desktop/NasaSpaceApps"
DOC = "wp2021"
PDF = f"{ROOT}/sources/raw/{DOC}/wp2021.pdf"
TXT = f"{ROOT}/sources/text/{DOC}.txt"
OUT = f"{ROOT}/sources/extracted/{DOC}.json"
META = f"{ROOT}/sources/raw/{DOC}/meta.json"
URL = ("https://science.nasa.gov/wp-content/uploads/2023/05/"
       "154_33f28c6ef0c27b92cf1f526cef0c44b4_Fire_detection_white_paper_final_211031.pdf")
RETRIEVED = "2026-11-15T10:42:28Z"

PSI_TO_KPA = 6.894757


def kpa(psi):
    return round(psi * PSI_TO_KPA, 1)


raw = open(PDF, "rb").read()
SHA = hashlib.sha256(raw).hexdigest()
NBYTES = len(raw)
text = open(TXT, encoding="utf-8").read()
pages = text.split("\f")
if pages and pages[-1].strip() == "":
    pages = pages[:-1]
NPAGES = len(pages)
norm_pages = [" ".join(p.split()) for p in pages]

TITLE = "Research Questions and Challenges for Improved Spacecraft Fire Detection"
AUTHORS = [
    "Claire Fortenberry (Universities Space Research Association, NASA Glenn Research Center) [primary author]",
    "Xiaoliang Wang (Desert Research Institute)",
    "Thomas Cleary (National Institute of Standards and Technology)",
    "John Easton (Case Western Reserve University, NASA Glenn Research Center)",
    "Gordon Berger (Universities Space Research Association, NASA Glenn Research Center)",
    "Marit Meyer (NASA Glenn Research Center)",
]

items = []


def cond(o2=None, p=None, flow=None, g=None, heat=None, age=None):
    return {"atmosphere_o2_vol_pct": o2, "pressure_kpa": p, "airflow_cm_s": flow,
            "gravity": g, "heating_s": heat, "aging_s": age}


def num(value, unit, meaning, verbatim):
    return {"value": value, "unit": unit, "meaning": meaning, "verbatim": verbatim}


def add(page, location, anchor, summary, category, investigation=None, materials=None,
        detector=None, numbers=None, conditions=None, n=None, scope=""):
    items.append({
        "item_id": None,
        "doc_id": DOC,
        "pdf_page": page,
        "printed_page": None,
        "location": location,
        "anchor_quote": anchor,
        "summary": summary,
        "category": category,
        "investigation": investigation,
        "materials": materials or [],
        "detector": detector,
        "numbers": numbers or [],
        "conditions": conditions or cond(),
        "n_independent_tests": n,
        "scope_notes": scope,
    })


# ---------------------------------------------------------------- page 1
add(1, "Cover page, title", TITLE,
    "Exact document title: 'Research Questions and Challenges for Improved Spacecraft Fire Detection'.",
    "context",
    scope="Bibliographic. No printed page numbers anywhere in the PDF, so printed_page is null for all items.")
add(1, "Cover page, submission line",
    "A topical white paper submitted to the National Academies of Sciences, Engineering and",
    "The cover identifies the document as a topical white paper submitted to the National Academies of "
    "Sciences, Engineering and Medicine (NASEM) for the Biological and Physical Sciences Decadal Survey; the "
    "cover labels the survey '2022-2032'. No date is printed in the document body; the PDF metadata creation "
    "date is 2021-10-31 and the file name ends in 211031.",
    "context",
    scope="The cover label '2022-2032' differs from the label '2023-2032' that the same paper uses for the "
          "same decadal survey in its reference 41 (pdf page 10). The date comes from PDF metadata/file name, "
          "not from printed text.")
add(1, "Cover page, primary author",
    "Claire Fortenberry Universities Space Research Association, NASA Glenn Research Center",
    "Primary author: Claire Fortenberry, Universities Space Research Association (USRA) at NASA Glenn "
    "Research Center (contact details for GRC are printed on the cover).",
    "context")
add(1, "Cover page, coauthors", "Xiaoliang Wang, Desert Research Institute",
    "Coauthors: Xiaoliang Wang (Desert Research Institute); Thomas Cleary (NIST); John Easton (Case Western "
    "Reserve University, NASA GRC); Gordon Berger (USRA, NASA GRC); Marit Meyer (NASA GRC).",
    "context")
add(1, "Cover page, cosigners",
    "Luca Carmignani, University of California, Berkeley; Daniel Dietrich, NASA Glenn Research",
    "23 cosigners are listed: Luca Carmignani (UC Berkeley); Daniel Dietrich (NASA GRC); Christian Eigenbrod "
    "(ZARM, University of Bremen, Germany); A. Carlos Fernandez-Pello (UC Berkeley); Osamu Fujita (Hokkaido "
    "University, Japan); Michael Gollner (UC Berkeley); Augustin Guibaud (University College London, UK); "
    "Michael Johnston (USRA, NASA GRC); Grunde Jomaas (FRISSBE, Slovenian National Building and Civil "
    "Engineering Institute (ZAG), Slovenia); Sarah Kingsley (Georgia Institute of Technology); Guillaume "
    "Legros (CNRS, France); Ya-Ting Liao (Case Western Reserve University); Randall McDermott (NIST); "
    "Fletcher Miller (San Diego State University); Justin Niehaus (NASA GRC); Thomas Orlando (Georgia "
    "Institute of Technology); Rosa Padilla (USRA, NASA GRC); Gary Ruff (NASA GRC); Nickolay Smirnov "
    "(Moscow Lomonosov State University, Russia); Benjamin Sumlin (USRA, NASA GRC); James T'ien (Case "
    "Western Reserve University); David Urban (NASA GRC); Indrek Wichman (Michigan State University).",
    "context",
    scope="Cosigners are distinct from authors; the paper is a multi-institution white paper led from NASA GRC, "
          "not a NASA technical report.")
add(1, "Abstract (stated purpose)",
    "This paper describes challenges and recommendations for research to improve spacecraft fire detection.",
    "Stated purpose: to set out challenges and research recommendations for improving spacecraft fire "
    "detection, motivated by crew safety and the need for detectors that catch a wide variety of fires.",
    "context")
add(1, "Abstract",
    "Fire emissions are affected by fuel type, heating conditions, gravity and exploration atmosphere.",
    "The abstract names four factors that affect fire emissions: fuel type, heating conditions, gravity, and "
    "the exploration (cabin) atmosphere.",
    "context",
    scope="Framing statement; no data attached at this point.")
add(1, "Abstract",
    "Advances in sensing technology provide a promising basis for future detectors, which must",
    "The abstract says sensing-technology advances are a promising basis for future detectors, which must be "
    "able to selectively detect a broad variety of fires; addressing these areas is presented as key to future "
    "lunar and deep-space missions.",
    "technology_need")

# ---------------------------------------------------------------- page 2
add(2, "Introduction, para 1",
    "refers specifically to the heat and radiation produced from the reaction of",
    "Definition used: 'fire' means the heat and radiation from a flammable material reacting with oxygen.",
    "definition")
add(2, "Introduction, para 1",
    "fire detection must also encompass the period of fuel overheating prior to flame development",
    "Because early detection is preferred, the authors state that fire detection in practice must also cover "
    "the fuel-overheating phase before any flame develops.",
    "definition",
    scope="Sets detection scope to include pre-flame overheating (oxidative pyrolysis), not only flaming fires.")
add(2, "Introduction, para 1",
    "spacecraft fires are especially dangerous due to limited escape options and extinguishment resources",
    "Compared with building fires on Earth, spacecraft fires are described as especially dangerous because of "
    "limited escape and extinguishing resources; even a survivable fire releases toxic particles and gases that "
    "threaten crew health.",
    "context")
add(2, "Introduction, para 1",
    "Detectable properties of fire include heat, radiation, and smoke.",
    "Detectable fire properties are heat, radiation and smoke. 'Smoke' is defined to include gases (examples "
    "given: CO, CO2, water vapour, volatile organics) and particles formed either by overheating the fuel "
    "(oxidative pyrolysis) or by a flame (e.g., soot and ash).",
    "definition")
add(2, "Introduction, para 1",
    "In microgravity, this buoyant flow does not occur, and this advantage therefore does not exist.",
    "On Earth smoke detection is advantageous because buoyancy carries hot combustion products upward, so "
    "ceiling-mounted detectors sit where smoke concentrates (heat and radiation detectors are noted as useful "
    "for select terrestrial applications, ref. 1). In microgravity there is no buoyant flow, so this placement "
    "advantage is lost.",
    "measurement_limitation", conditions=cond(g="microgravity"),
    scope="Physical argument about smoke transport and detector placement; no test data given here.")
add(2, "Introduction, para 1",
    "smoke detectors are placed in the cabin air return vents in front of the filters",
    "As a consequence of the lack of buoyant flow, ISS smoke detectors are located in the cabin air return "
    "vents, upstream of the filters; the authors note this placement has further implications for fire "
    "detection that they discuss later in the paper.",
    "context", detector="smoke detectors (ISS)",
    scope="Describes ISS detector siting. The later discussion (same page) concerns ECLSS filtration "
          "outpacing smoke accumulation (ref. 6).")
add(2, "Introduction, para 1",
    "Due to a lack of data characterizing microgravity fires, however, spacecraft fire detection",
    "Because data characterising microgravity fires were lacking, spacecraft fire detection strategies have "
    "had to rely on technology developed for terrestrial fire detection.",
    "context")
add(2, "Introduction, para 1",
    "the ionization detector on the Space Shuttle represented the most advanced detection technology",
    "Historical example: the Space Shuttle ionization detector reflected the most advanced detection "
    "technology of the 1970s, when ionization detectors were spreading in homes.",
    "context", detector="ionization detector on the Space Shuttle")
add(2, "Introduction, para 1",
    "the ISS forward light scattering detector utilized improvements in photodiode technology developed",
    "Similarly, the ISS forward light scattering detector drew on 1990s improvements in photodiode technology "
    "(ref. 2).",
    "context", detector="ISS forward light scattering detector",
    scope="Identifies the ISS smoke detector type as forward light scattering.")
add(2, "Introduction, para 2",
    "Recent research has demonstrated that current fire detection strategies are inadequate for ensuring",
    "The authors state that recent research has shown current fire detection strategies to be inadequate for "
    "ensuring crew safety on long-duration missions; the following sentences give the supporting evidence "
    "(SAME missed alarms, ECLSS filtration, dust nuisance alarms).",
    "measurement_limitation",
    scope="Authors' summary judgement, not a single measured result.")
add(2, "Introduction, para 2",
    "which was the first study to examine oxidative pyrolysis particles in microgravity",
    "The Smoke Aerosol Measurement Experiment (SAME) is described as the first study to examine oxidative "
    "pyrolysis (overheating) smoke particles in microgravity.",
    "investigation_profile", investigation="SAME", conditions=cond(g="microgravity"),
    scope="Only SAME is named; SAME-R (the reflight) is not mentioned anywhere in this white paper.")
add(2, "Introduction, para 2",
    "the ISS detector failed to alarm for Kapton smoke in half of the tests",
    "In SAME, the ISS detector did not alarm for Kapton smoke in half of the tests. Refs. 3-5 are cited for "
    "the SAME results: Meyer et al. 2015 (Aerosol Sci. Technol. 49(5):299-309, moment method), Mulholland "
    "et al. 2015 (Aerosol Sci. Technol. 49(5):310-321, low-gravity pyrolysis smoke), and Meyer et al. 2018 "
    "(Fire Saf. J. 98:74-81, spacecraft smoke detector performance in low gravity).",
    "missed_alarm", investigation="SAME", materials=["Kapton"], detector="ISS detector",
    numbers=[num(50, "% of tests",
                 "share of SAME Kapton smoke tests in which the ISS detector failed to alarm "
                 "(50 is a conversion of the printed word 'half')", "half of the tests")],
    conditions=cond(g="microgravity (ISS)"),
    scope="Missed alarm (no alarm while smoke was present), not a false alarm. The white paper gives no test "
          "count, no heating temperature, aging time, flow speed or alarm threshold, and does not say which of "
          "refs. 3-5 holds the figure. 'ISS detector' here is, per the same page, the ISS forward light "
          "scattering detector. Applies to SAME only; SAME-R is not mentioned. Wording 'half' is as printed; "
          "the task brief's 'roughly 50%' is not the source wording.")
add(2, "Introduction, para 2",
    "and for Teflon smoke in two-thirds of the tests, a troubling result",
    "In the same SAME sentence, the ISS detector did not alarm for Teflon smoke in two-thirds of the tests "
    "(same citations, refs. 3-5).",
    "missed_alarm", investigation="SAME", materials=["Teflon"], detector="ISS detector",
    numbers=[num(66.7, "% of tests",
                 "share of SAME Teflon smoke tests in which the ISS detector failed to alarm "
                 "(66.7 is a rounded conversion of the printed 'two-thirds')", "two-thirds of the tests")],
    conditions=cond(g="microgravity (ISS)"),
    scope="Missed alarm, not false alarm. No test count or test conditions are given in the white paper; the "
          "denominator must be taken from refs. 3-5. Applies to SAME only (SAME-R not mentioned). The task "
          "brief's 'roughly 67%' is a conversion; printed wording is 'two-thirds'.")
add(2, "Introduction, para 2",
    "Kapton and Teflon are abundant in spacecraft electrical systems, where a spacecraft fire is likely",
    "The authors call the SAME missed-alarm result troubling because Kapton and Teflon are abundant in "
    "spacecraft electrical systems, where a spacecraft fire is likely to begin (refs. 3-5 cited at sentence end).",
    "context", investigation="SAME", materials=["Kapton", "Teflon"])
add(2, "Introduction, para 2",
    "particle filtration rates provided by the Environmental Control and Life Support System (ECLSS)",
    "Urban et al. (2016, ref. 6) are cited as showing that ECLSS particle filtration is fast enough to outpace "
    "smoke accumulation for a small or early-stage fire, so detection may fail or be delayed if the event does "
    "not raise cabin smoke concentration to the detector's alarm threshold.",
    "measurement_limitation", detector=None,
    scope="Concerns small/early-stage fires and the detector alarm threshold (detector not further specified "
          "in this sentence). The white paper does not state whether ref. 6 is an analysis/model or an "
          "experiment, nor give filtration rates or thresholds. 'May fail or be delayed' is a hedged "
          "implication, not a counted missed alarm.")
add(2, "Introduction, para 2",
    "because the ISS detector does not select for smoke particles, the device is",
    "Because the ISS detector is not selective for smoke particles, it is prone to nuisance alarms from "
    "suspended dust, which can desensitise the crew to real alarms.",
    "false_alarm", detector="ISS detector",
    scope="False/nuisance alarm (alarm without fire, from dust). No alarm counts or rates are given; no "
          "citation is attached to this sentence.")
add(2, "Introduction, para 2",
    "when ISS crew members vacuum the cabin, they typically disable the smoke",
    "Operational practice reported: when ISS crew vacuum the cabin they typically disable the smoke detectors "
    "so that suspended dust does not trigger alarms.",
    "false_alarm", detector="smoke detectors (ISS)",
    scope="Operational workaround for dust nuisance alarms; the paper gives no frequency, duration or citation. "
          "It does not quantify the time detectors are disabled.")
add(2, "Introduction, para 2",
    "relying on detection of a single fire property, like the forward light scattering",
    "From these observations the authors conclude that a system relying on a single fire property, such as "
    "the ISS forward light scattering detector, is unlikely to achieve successful early fire detection in all "
    "relevant scenarios.",
    "measurement_limitation", detector="forward light scattering detector on the ISS",
    scope="Authors' inference from SAME missed alarms, filtration analysis and dust nuisance alarms; motivates "
          "the multi-sensor recommendation (Section D, Recommendation 4).")
add(2, "Introduction, para 3",
    "future experiments must address the shortcomings of traditional fire detection methods and establish",
    "Future experiments must address shortcomings of traditional fire detection methods and establish optimal "
    "detection methods for future spacecraft.",
    "recommendation")
add(2, "Introduction, para 3",
    "as missions move deeper into space and utilize different exploration atmospheres, new risks",
    "As missions go deeper into space and use different exploration atmospheres, new risks arise that must be "
    "evaluated.",
    "research_question")
add(2, "Introduction, para 3",
    "flammability limits are not expected to meet current requirements under elevated O2 (34%) and",
    "Material flammability limits are not expected to meet current requirements under the elevated-oxygen "
    "(34%) and reduced-pressure (8.2 psi) conditions planned for future lunar habitats; these conditions are "
    "also expected to affect fire emissions.",
    "test_condition",
    numbers=[num(34, "% O2", "planned lunar habitat oxygen concentration", "34%"),
             num(8.2, "psi", "planned lunar habitat pressure", "8.2 psi")],
    conditions=cond(o2=34, p=kpa(8.2), g="lunar habitat (planned)"),
    scope="Expectation for planned conditions, not a measurement. pressure_kpa converted from 8.2 psi "
          "(x6.894757); printed value is in psi.")

# ---------------------------------------------------------------- page 3
add(3, "Introduction, end of para 3 (sentence starts on pdf page 2)",
    "realistic fire scenarios, characterization of gravity and exploration impacts on fire signatures, and",
    "Research topics to investigate: identifying realistic fire scenarios; characterising how gravity and "
    "exploration atmospheres affect fire signatures; and developing novel detectors that selectively detect a "
    "wider range of spacecraft fires.",
    "research_question")
add(3, "Research Topics and Challenges, A (heading)",
    "Identification of realistic fire scenarios and characterization of fire signatures from",
    "Topic A: identify realistic fire scenarios and characterise fire signatures of unstudied and "
    "understudied fuels; since a detection system must catch smoke from many scenarios, the fuels of interest "
    "must be identified and examined thoroughly.",
    "research_question")
add(3, "Section A",
    "Experiments should examine both small scale (similar to SAME) and large-scale fires",
    "Experiments should cover both small-scale fires (like SAME) and large-scale fires (like the Saffire "
    "experiments, refs. 7-9), to evaluate detection of early-stage and fully developed spacecraft fires "
    "respectively.",
    "recommendation", investigation="SAME; Saffire",
    scope="Only mention of Saffire in the body text; no Saffire results are reported in the white paper.")
add(3, "Section A",
    "A fire source of major concern is the lithium ion battery",
    "Lithium ion batteries (LIBs) are a major fire-source concern; they power on-orbit laptops, power tools "
    "and space suits.",
    "context", materials=["lithium ion battery (LIB)"])
add(3, "Section A",
    "laptop LIB fires constitute one of the most likely and most dangerous spacecraft fire",
    "Laptop LIB fires are described as among the most likely and most dangerous spacecraft fire scenarios for "
    "long-duration missions (ref. 10).",
    "context", materials=["laptop lithium ion battery"])
add(3, "Section A",
    "increased reliance on LIBs to power electrical components for longer periods of time",
    "The community anticipates more reliance on LIBs, for longer periods, as crewed missions move to the Moon, "
    "Mars and beyond (ref. 11).",
    "context", materials=["lithium ion battery (LIB)"])
add(3, "Section A",
    "we are aware of only one study that characterized the properties of smoke",
    "Gap: several studies have examined gaseous products of LIB fires (refs. 12-15) and particles from "
    "large-scale LIB fires such as car batteries (refs. 16-17), but the authors know of only one study "
    "(ref. 18) characterising smoke particles from laptop LIB fires.",
    "research_question", materials=["laptop lithium ion battery"],
    scope="Gap as of the authors' 2021 awareness; not a claim that no other study exists.")
add(3, "Section A",
    "Another fuel of immediate interest is the to-be-determined fabric that will compose crew",
    "A second fuel of immediate interest is the not-yet-selected fabric for crew clothing in future lunar "
    "missions.",
    "research_question", materials=["crew clothing fabric (to be determined)"])
add(3, "Section A",
    "clothing worn by crew members on the ISS (e.g., cotton jersey t-shirts) may not be",
    "Because planned exploration atmospheres are expected to raise material flammability, ISS crew clothing "
    "(e.g., cotton jersey t-shirts) may be unsuitable for lunar missions; a fire-resistant fabric is being "
    "sought for the lunar habitat.",
    "context", materials=["cotton jersey"], conditions=cond(g="lunar habitat (planned)"),
    scope="Expectation; no flammability data given here.")
add(3, "Section A",
    "This fabric must be investigated as a potential fuel to identify fire signatures",
    "The chosen fabric must be tested as a potential fuel to identify its fire signatures, which will guide "
    "selection of an optimal fire detector.",
    "recommendation", materials=["crew clothing fabric (to be determined)"])
add(3, "Section A",
    "the same fuel heated to different maximum temperatures can yield particles with",
    "Differences in heating method complicate scenario definition: ground experiments in Meyer (2015, ref. 19) "
    "showed that one fuel heated to different maximum temperatures can give particles of drastically "
    "different sizes and morphologies.",
    "particle_property", conditions=cond(g="1 g (ground)"),
    scope="Ground experiments; the white paper does not name the fuels or temperatures here.")
add(3, "Section A",
    "the longer fuel residence time experienced in reduced gravity drastically impact the formation and growth",
    "Parabolic-flight measurements show that longer fuel residence time in reduced gravity strongly affects "
    "particle formation and growth (ref. 20), fundamentally changing how readily a flame produces smoke from a "
    "given fuel (ref. 21).",
    "particle_property", conditions=cond(g="reduced gravity (parabolic flight)"),
    scope="Refs. 20-21 (Guibaud et al. 2020) concern flames spreading over polyethylene-coated wires in "
          "opposed flow, per their titles; applies to flaming smoke, not oxidative pyrolysis.")
add(3, "Section A",
    "Future spacecraft smoke detection studies must attempt to recreate a variety of realistic overheating",
    "Future spacecraft smoke detection studies should reproduce a range of realistic overheating scenarios, "
    "including different peak heating temperatures and different temperature ramp methods.",
    "recommendation")
add(3, "Section A",
    "most spacecraft detection research to date has focused on characterization of smoke sizes",
    "Because recent spacecraft detectors sense smoke particles, most spacecraft detection research so far has "
    "concentrated on smoke particle sizes and morphologies.",
    "context")
add(3, "Section A",
    "there is a need for expanded smoke measurements including but not limited to gas",
    "Owing to challenges with particle detection, smoke measurements need to be expanded to include, among "
    "others, gas composition and concentrations, particle charge distributions and particle chemical "
    "composition.",
    "technology_need")
add(3, "Section A",
    "monomers generated from polymer degradation during a fire constitute a potential detection target",
    "Extra flammable gases released in microgravity fires can feed flame propagation (example: vapour jetting "
    "of monomers in PMMA combustion, ref. 22), so monomers from polymer degradation are a potential "
    "gas-phase detection target.",
    "technology_need", materials=["polymethyl methacrylate (PMMA)"], conditions=cond(g="microgravity"))
add(3, "Section A",
    "potential gas-phase detection targets are electrolyte vapors vented in the early stages of LIB",
    "Electrolyte vapours vented early in LIB failure are another candidate gas-phase detection target.",
    "technology_need", materials=["lithium ion battery (LIB)"],
    scope="Proposed target; no detection data in the white paper.")
add(3, "Section A (continues on pdf page 4)",
    "Ground measurements of particles and gases from spacecraft-relevant sources could inform future",
    "Characterising spacecraft-relevant fire signatures would also benefit Earth: ground measurements could "
    "inform terrestrial smoke detector standards and, for LIBs (laptops, phones, electric vehicles), help "
    "evaluate detection standards and air-quality risks from LIB fires.",
    "context")

# ---------------------------------------------------------------- page 4
add(4, "Research Topics and Challenges, B (heading)",
    "Evaluation of gravity impacts on fire signatures and plume transport.",
    "Topic B: evaluate how gravity affects fire signatures and smoke plume transport.",
    "research_question")
add(4, "Section B",
    "spacecraft fire detection studies have focused on microgravity applications, with heavy reliance on",
    "So far, spacecraft fire detection studies have targeted microgravity and leaned heavily on complementary "
    "ground experiments.",
    "context", conditions=cond(g="microgravity"),
    scope="Implies partial gravity (lunar/Martian) is comparatively unstudied within this source's framing.")
add(4, "Section B",
    "smoke particles generated in microgravity were larger compared to those generated in ground experiments",
    "In SAME, smoke particles produced in microgravity were larger than those from ground experiments below an "
    "air-flow threshold of 8.1 cm/s, with the largest size and morphology differences seen in no-flow tests.",
    "particle_property", investigation="SAME",
    numbers=[num(8.1, "cm/s", "air-flow threshold below which microgravity particles were larger than ground "
                 "particles", "8.1 cm s-1")],
    conditions=cond(g="microgravity (ISS) vs 1 g ground"),
    scope="airflow_cm_s left null because 8.1 cm/s is a threshold (below it), not a single test condition. "
          "Materials and test counts not stated in the white paper.")
add(4, "Section B",
    "Differences in particle formation and evolution in reduced gravity are attributable to increased residence",
    "The authors attribute the reduced-gravity particle differences to longer residence times near the smoke "
    "source, because plumes disperse slowly at low air speeds without buoyant flow (refs. 3, 4).",
    "particle_property", investigation="SAME", conditions=cond(g="reduced gravity"))
add(4, "Section B",
    "In lunar gravity, the dependence of smoke particle size on air flow remains unclear.",
    "Open question: how smoke particle size depends on air flow in lunar gravity is not known.",
    "research_question", conditions=cond(g="lunar"))
add(4, "Section B",
    "particle sizes must be characterized in reduced gravity under air velocity conditions relevant",
    "To choose a suitable detector for a lunar habitat, particle sizes must be measured in reduced gravity at "
    "air velocities relevant to that environment.",
    "recommendation", conditions=cond(g="lunar / reduced gravity"))
add(4, "Section B",
    "Experiments must also examine particle growth over relevant timescales",
    "Experiments must also track particle growth over relevant timescales, chosen using cabin air transport "
    "parameters and space-specific environmental conditions.",
    "recommendation")
add(4, "Section B",
    "the effects of reduced gravity on smoke particle properties should be examined for a",
    "Reduced-gravity effects on smoke particle properties should be studied across a variety of "
    "spacecraft-relevant fuels.",
    "recommendation", conditions=cond(g="reduced gravity"))
add(4, "Section B, text beside Figure 1",
    "The magnitude of gravity influences smoke plume",
    "Gravity level affects smoke plume transport, illustrated by Figure 1, which compares plume transport in "
    "terrestrial, microgravity and lunar gravity (per the caption).",
    "context", conditions=cond(g="1 g / microgravity / lunar"),
    scope="Only the caption text was extracted; the figure graphic was not analysed.")
add(4, "Section B",
    "The optimal location for a smoke detector within a lunar vehicle cabin must be",
    "Where to put a smoke detector in a lunar vehicle cabin must be determined by further research.",
    "research_question", conditions=cond(g="lunar"))
add(4, "Section B",
    "Lunar dust is expected to pose a significant threat to crew health and",
    "Lunar dust is expected to threaten crew health and materials; floor-level air returns would help remove "
    "lunar dust from cabin air via gravitational settling.",
    "context", conditions=cond(g="lunar"),
    scope="Expectation; relevant to dust nuisance alarms and to detector siting near returns.")
add(4, "Section B",
    "it may be advantageous to place detectors on the cabin ceilings",
    "If buoyant transport in lunar gravity is strong enough to overcome the downward (floor-return) flow, "
    "ceiling-mounted detectors may be advantageous.",
    "research_question", conditions=cond(g="lunar"),
    scope="Conditional and hedged ('may'); no modelling or test result given.")
add(4, "Section B",
    "Modeling smoke transport in lunar gravity is therefore prioritized for upcoming fire safety research.",
    "Modelling smoke transport in lunar gravity is therefore made a priority for upcoming fire safety research.",
    "recommendation", conditions=cond(g="lunar"))
add(4, "Section B",
    "the development of a lunar gravity smoke model could provide the framework for Martian studies",
    "A lunar-gravity smoke model could later serve as the framework for Mars studies.",
    "research_question", conditions=cond(g="lunar; Martian (future)"))
add(4, "Section B",
    "smoke emission factors (i.e., mass of smoke component per mass fuel burned)",
    "Future fire safety modelling will depend on smoke emission factors, defined as mass of a smoke component "
    "per mass of fuel burned, measured in microgravity and partial-gravity experiments (ref. 6).",
    "definition", conditions=cond(g="microgravity; partial gravity"))
add(4, "Section B",
    "determination of realistic emission factors for different fuels and fire scenarios are critical for",
    "Emission factors combined with habitat filtration and mixing parameters allow alarm-time predictions; "
    "because cabin air is usually well mixed and heavily filtered, realistic emission factors for different "
    "fuels and scenarios are critical for predicting time to alarm and for choosing detector placement.",
    "recommendation",
    scope="Detection time is discussed only as a prediction need; no alarm times are reported in the paper.")
add(4, "Research Topics and Challenges, C (heading)",
    "Evaluation of exploration atmosphere impacts on fire signatures in reduced gravity.",
    "Topic C: evaluate how exploration atmospheres affect fire signatures in reduced gravity.",
    "research_question", conditions=cond(g="reduced gravity"))
add(4, "Section C",
    "planned environment for future lunar habitats is 34% O2 and 8.2 psi",
    "The planned lunar habitat atmosphere is 34% O2 at 8.2 psi (ref. 23).",
    "test_condition",
    numbers=[num(34, "% O2", "planned lunar habitat oxygen", "34% O2"),
             num(8.2, "psi", "planned lunar habitat pressure", "8.2 psi")],
    conditions=cond(o2=34, p=kpa(8.2), g="lunar habitat (planned)"),
    scope="Planned condition, not a tested one. pressure_kpa converted from psi.")
add(4, "Section C",
    "expected to influence material flammability, flame spread rates, and smoke emission for materials",
    "These atmosphere parameters together with reduced gravity are expected to influence material "
    "flammability, flame spread rates and smoke emission (refs. 21, 24-26).",
    "context", conditions=cond(o2=34, p=kpa(8.2), g="reduced gravity"),
    scope="Expectation; no detector data.")
add(4, "Section C",
    "methane flames, soot surface growth and oxidation rates increase as O2 % increases",
    "Lee et al. (2000, ref. 27) found that in methane flames soot surface growth and oxidation rates rise with "
    "oxygen percentage.",
    "context", materials=["methane (gaseous fuel)"],
    scope="Terrestrial laboratory flame study with a gaseous fuel; not a spacecraft detection test.")
add(4, "Section C",
    "soot inception and surface growth rates increase by orders of magnitude, with substantial changes",
    "Edland et al. (2020, ref. 28) showed that in propane flames soot inception and surface growth rates rise "
    "by orders of magnitude, with large changes above 30% O2.",
    "context", materials=["propane (gaseous fuel)"],
    numbers=[num(30, "% O2", "oxygen level above which substantial soot changes occurred", "30% O2")],
    scope="Gaseous fuel, technical-scale turbulent flames on Earth; not a detection test.")
add(4, "Section C",
    "below a critical pressure at which soot formation is maximized, reduced pressures are expected",
    "Below the critical pressure at which soot formation peaks, lower pressures are expected to reduce soot "
    "formation (ref. 29).",
    "context",
    scope="Critical pressure value not given in the white paper.")
add(4, "Section C (sentence continues on pdf page 5)",
    "pressure conditions targeted for future lunar vehicles are expected to impact sizes, and therefore",
    "Based on these studies, the elevated O2 and reduced pressure targeted for lunar vehicles are expected to "
    "change soot sizes from fully developed fires, and therefore their detection.",
    "research_question", conditions=cond(o2=34, p=kpa(8.2), g="lunar vehicle (planned)"),
    scope="Expectation inferred from gaseous-fuel flame studies (refs. 27-29); not a measured detection "
          "result. Applies to soot from fully developed (flaming) fires.")

# ---------------------------------------------------------------- page 5
add(5, "Section C",
    "these studies utilized gaseous fuels rather than solid fuels, and more research is needed",
    "The cited soot studies used gaseous fuels; more research is needed on how O2 and pressure affect solid "
    "fuel combustion.",
    "research_question")
add(5, "Section C",
    "Effects of O2 concentration and pressure on oxidative pyrolysis particles remain unclear",
    "How O2 concentration and pressure affect oxidative pyrolysis (overheating) particles is unclear and must "
    "be investigated.",
    "research_question")
add(5, "Research Topics and Challenges, D (heading)",
    "Development of improved fire detection systems.",
    "Topic D: develop improved fire detection systems, using experiments that characterise fire signatures "
    "under spacecraft-relevant conditions as the basis.",
    "technology_need")
add(5, "Section D",
    "a CO detector in parallel with a smoke detector was suggested as a solution",
    "Urban et al. (2016, ref. 6) suggested pairing a CO detector with a smoke detector to counter rapid "
    "particle filtration by the ECLSS.",
    "followup_solution", detector="CO detector in parallel with a smoke detector",
    scope="Proposal from ref. 6; the white paper reports no test of this configuration.")
add(5, "Section D",
    "an ideal spacecraft fire detection system would incorporate a network of instruments and sensors",
    "An ideal spacecraft fire detection system would use a network of instruments and sensors monitoring fire "
    "properties in the cabin: temperature, radiation, gas composition and concentrations, and particle "
    "properties and concentrations.",
    "technology_need",
    scope="Multi-property / multi-sensor concept; stated as an ideal, not a demonstrated system.")
add(5, "Section D",
    "The feasibility of such a system must be addressed in future work.",
    "Whether such a networked system is feasible must be addressed in future work.",
    "research_question")
add(5, "Section D",
    "utilize monitoring technology already incorporated into the spacecraft for other purposes, like cabin air",
    "A sensor network for fire detection could reuse monitoring technology already on the spacecraft for other "
    "purposes, such as cabin air quality monitoring.",
    "technology_need")
add(5, "Section D",
    "gas monitors currently on the ISS, including a laser spectroscopy-based combustion products",
    "ISS gas monitors, including a laser spectroscopy-based combustion products monitor (ref. 30), could be "
    "folded into a larger fire detection network in a future vehicle.",
    "technology_need", detector="laser spectroscopy-based combustion products monitor")
add(5, "Section D",
    "only expand the subset of detectable fires but would also reduce false alarms",
    "An array of sensors continuously watching for predetermined fire signatures would both widen the set of "
    "detectable fires and reduce false alarms.",
    "technology_need",
    scope="Expected benefit; no false-alarm rates are reported.")
add(5, "Section D",
    "measuring particle chemical composition or charges could differentiate between smoke particles and lunar dust",
    "A future detector that measures particle chemical composition or charge could distinguish smoke "
    "particles from lunar dust, greatly improving fire safety in lunar spacecraft.",
    "technology_need", conditions=cond(g="lunar"),
    scope="Proposed discrimination approach against dust false alarms; not demonstrated in the paper.")
add(5, "Section D",
    "have enabled in situ molecular-level particle and gas chemical characterization",
    "Advances in chemical measurement (e.g., gas chromatography mass spectrometry) allow in situ "
    "molecular-level characterisation of particles and gases; work to shorten analysis time, cut power and "
    "footprint and improve robustness (refs. 31-33) makes these candidates for selective smoke detectors.",
    "technology_need")
add(5, "Section D",
    "Chemical characterization of particles and gases produced during a fire can also provide",
    "Chemical characterisation of fire particles and gases could also reveal what material is burning, the "
    "approximate fire temperature and the toxicity of products; immediate knowledge of these would help "
    "choose the best fire response (ref. 34).",
    "technology_need")
add(5, "Section D",
    "machine learning techniques like positive matrix factorization",
    "Novel data analysis, including positive matrix factorization (refs. 35-37) and deep long short-term "
    "memory networks with variational autoencoders (ref. 38), could reduce complex data sets and identify "
    "analyte sources efficiently.",
    "technology_need")
add(5, "Capabilities",
    "Table 1 lists a subset of resources currently available for spacecraft smoke characterization",
    "The Capabilities section introduces Table 1 as a partial list of resources available for spacecraft smoke "
    "characterisation research.",
    "context")
add(5, "Capabilities",
    "Gases and Aerosols from Smoldering Polymers (GASP)",
    "At NASA GRC, the Gases and Aerosols from Smoldering Polymers (GASP) laboratory (ref. 19) and the new "
    "Battery Test Facility (BTF) support ground testing at terrestrial O2 and pressure.",
    "context", conditions=cond(g="1 g (ground)"))
add(5, "Capabilities",
    "Parabolic flights provide short durations of microgravity or partial gravity (approximately 30 s)",
    "Parabolic flights give short periods (approximately 30 s) of microgravity or partial gravity, useful to "
    "prove experiment feasibility before longer missions (refs. 20, 21, 39).",
    "context", numbers=[num(30, "s", "approximate duration of reduced gravity per parabola",
                            "approximately 30 s")],
    conditions=cond(g="microgravity or partial gravity (parabolic flight)"))
add(5, "Capabilities",
    "drop tower centrifuge rig can currently provide 5.2 seconds of lunar gravity",
    "The Zero-Gravity Research Facility (ZGRF) drop tower centrifuge rig currently provides 5.2 s of lunar "
    "gravity (ref. 40); planned GRC drop tower upgrades would extend reduced-gravity time to 10 s (ref. 41).",
    "context",
    numbers=[num(5.2, "s", "current lunar-gravity duration of ZGRF centrifuge rig", "5.2 seconds"),
             num(10, "s", "planned reduced-gravity duration after drop tower improvements", "10 seconds")],
    conditions=cond(g="lunar (drop tower centrifuge)"))
add(5, "Capabilities",
    "Experiments on lunar vehicles (e.g., through Commercial Lunar Payload Services) are necessary",
    "Experiments on lunar vehicles (e.g., via Commercial Lunar Payload Services) are needed to thoroughly "
    "study the effect of partial gravity on fire emissions.",
    "recommendation", conditions=cond(g="lunar (partial gravity)"))
add(5, "Capabilities",
    "continued combustion experiments on the ISS (e.g., using the microgravity science glovebox",
    "Continued ISS combustion experiments (e.g., Microgravity Science Glovebox, refs. 42-43; Combustion "
    "Integrated Rack, ref. 44) and future low-Earth-orbit spacecraft are needed to improve microgravity fire "
    "detection, which stays relevant for deep-space missions.",
    "recommendation", conditions=cond(g="microgravity"))

# ---------------------------------------------------------------- page 6
add(6, "Capabilities",
    "improvements in sensing technology for both particles and gases will enable unprecedented measurements",
    "Better particle and gas sensing technology will allow unprecedented measurements within spacecraft "
    "constraints.",
    "technology_need")
add(6, "Capabilities",
    "sensors can be calibrated to reference aerosols and instruments to provide particle size distributions",
    "Beyond instruments already used on spacecraft (refs. 30, 45), novel sensors can be calibrated against "
    "reference aerosols and instruments to give particle size distributions and concentrations (refs. 46-47).",
    "technology_need",
    scope="Refs. 46-47 evaluate low-cost particulate sensors on Earth (per titles).")
add(6, "Capabilities",
    "Particle and gas sensors increasingly feature smaller footprints and power requirements",
    "Particle and gas sensors are getting smaller and lower-power, a logistical advantage for future lunar and "
    "deep-space chamber studies.",
    "context")
add(6, "Capabilities",
    "is crucial for determining detector design and placement strategies",
    "Using computational fluid dynamics to assess whether fire effluent can be detected as it spreads from the "
    "source is crucial for detector design and placement strategies.",
    "recommendation")
add(6, "Capabilities",
    "designed for fire flows in any gravity environment with fire or other heat sources",
    "The NIST Fire Dynamics Simulator (FDS) is cited as a model built for fire flows in any gravity "
    "environment (refs. 48-49).",
    "context")
add(6, "Capabilities",
    "Recent updates to FDS include advancements in aerosol dynamics modeling",
    "Recent FDS updates add aerosol dynamics, tracking particle size distributions and processes that change "
    "particle size and concentration (coagulation, deposition, thermophoresis).",
    "context")
add(6, "Capabilities",
    "the code may be modified to account for currently un-modeled physics",
    "Because FDS is free and open source, it can be modified to include physics it does not yet model.",
    "model_limitation",
    scope="The paper does not list which physics are un-modelled.")
add(6, "Table 1 caption",
    "Partial list of experimental resources enabling investigation of smoke particle",
    "Table 1 is a partial list of experimental resources for studying smoke particle characteristics and "
    "transport under various gravity and cabin atmosphere conditions; columns are duration, gravity (g), O2 "
    "(%) and pressure (psi).",
    "context")

ROWNOTE = ("Facility capability listed in Table 1, not a test result. pressure_kpa converted from psi "
           "(x6.894757).")
add(6, "Table 1, row 'GASP and BTF (GRC)'", "GASP and BTF (GRC) Full burn 1 21 14.7",
    "Table 1: GASP and BTF at GRC offer full-burn duration at 1 g, 21% O2, 14.7 psi.",
    "context",
    numbers=[num(1, "g", "gravity", "1"), num(21, "% O2", "oxygen", "21"), num(14.7, "psi", "pressure", "14.7")],
    conditions=cond(o2=21, p=kpa(14.7), g="1 g"), scope=ROWNOTE)
add(6, "Table 1, row 'MSG (ISS)'", "MSG42,43 (ISS) Full burn 0 21 14.7",
    "Table 1: Microgravity Science Glovebox on ISS (refs. 42-43): full burn, 0 g, 21% O2, 14.7 psi.",
    "context",
    numbers=[num(0, "g", "gravity", "0"), num(21, "% O2", "oxygen", "21"), num(14.7, "psi", "pressure", "14.7")],
    conditions=cond(o2=21, p=kpa(14.7), g="0 g (ISS)"), scope=ROWNOTE)
add(6, "Table 1, row 'CIR (ISS)'", "CIR (ISS) Full burn 0 10-40 0.29-44",
    "Table 1: Combustion Integrated Rack on ISS (ref. 44): full burn, 0 g, O2 range 10-40%, pressure range "
    "0.29-44 psi.",
    "context",
    numbers=[num(10, "% O2", "lower bound of O2 range", "10-40"), num(40, "% O2", "upper bound of O2 range", "10-40"),
             num(0.29, "psi", "lower bound of pressure range", "0.29-44"),
             num(44, "psi", "upper bound of pressure range", "0.29-44")],
    conditions=cond(g="0 g (ISS)"),
    scope=ROWNOTE + " O2 and pressure are ranges, so condition fields left null.")
add(6, "Table 1, row 'ZGRF drop tower centrifuge rig (GRC)'",
    "ZGRF drop tower centrifuge rig (GRC) 5.2 s 0.165 21 14.7",
    "Table 1: ZGRF drop tower centrifuge rig at GRC (ref. 40): 5.2 s at 0.165 g, 21% O2, 14.7 psi.",
    "context",
    numbers=[num(5.2, "s", "duration", "5.2 s"), num(0.165, "g", "gravity (lunar)", "0.165"),
             num(21, "% O2", "oxygen", "21"), num(14.7, "psi", "pressure", "14.7")],
    conditions=cond(o2=21, p=kpa(14.7), g="0.165 g (lunar)"), scope=ROWNOTE)
add(6, "Table 1, row 'Parabolic Aircraft/DIAMONDS (CNES)'",
    "Parabolic Aircraft/DIAMONDS (CNES)20,21,39 ~30 s 0-0.379 <21 7.3-20",
    "Table 1: CNES parabolic aircraft / DIAMONDS (refs. 20, 21, 39): about 30 s, 0-0.379 g, below 21% O2, "
    "7.3-20 psi.",
    "context",
    numbers=[num(30, "s", "approximate duration", "~30 s"), num(0, "g", "gravity lower bound", "0-0.379"),
             num(0.379, "g", "gravity upper bound (Mars level)", "0-0.379"),
             num(21, "% O2", "upper limit (O2 below 21%)", "<21"),
             num(7.3, "psi", "pressure lower bound", "7.3-20"), num(20, "psi", "pressure upper bound", "7.3-20")],
    conditions=cond(g="0-0.379 g"),
    scope=ROWNOTE + " Ranges, so condition fields left null. The 'Mars level' gloss for 0.379 g is this "
                    "extractor's annotation, not printed in the table.")
add(6, "Table 1, row 'Blue Origin New Shepard Rotating Capsule'",
    "Blue Origin New Shepard Rotating Capsule ~120 s 0.165 ~34 ~8.2",
    "Table 1: Blue Origin New Shepard rotating capsule: about 120 s at 0.165 g, about 34% O2, about 8.2 psi.",
    "context",
    numbers=[num(120, "s", "approximate duration", "~120 s"), num(0.165, "g", "gravity (lunar)", "0.165"),
             num(34, "% O2", "approximate oxygen", "~34"), num(8.2, "psi", "approximate pressure", "~8.2")],
    conditions=cond(o2=34, p=kpa(8.2), g="0.165 g (lunar)"),
    scope=ROWNOTE + " Values are approximate (printed with ~).")
add(6, "Table 1, row 'Commercial Lunar Payload Services Experiments'",
    "Commercial Lunar Payload Services Experiments Full burn 0.165 ~34 ~8.2",
    "Table 1: Commercial Lunar Payload Services experiments: full burn at 0.165 g, about 34% O2, about 8.2 psi.",
    "context",
    numbers=[num(0.165, "g", "gravity (lunar)", "0.165"), num(34, "% O2", "approximate oxygen", "~34"),
             num(8.2, "psi", "approximate pressure", "~8.2")],
    conditions=cond(o2=34, p=kpa(8.2), g="0.165 g (lunar)"),
    scope=ROWNOTE + " Values are approximate (printed with ~); listed as a resource, not an existing result.")
add(6, "Conclusions and Recommendations",
    "Transformative spacecraft fire detection research is paramount to ensuring crew safety",
    "The conclusions state that transformative fire detection research is essential to crew safety on lunar "
    "and deep-space missions, and list four priorities.",
    "context")
add(6, "Conclusions and Recommendations, priority 1",
    "Fuels prioritized for immediate testing include LIBs and the crew clothing fabric",
    "Priority 1: identify realistic fire scenarios and characterise fire signatures of unstudied and "
    "understudied fuels; LIBs and the crew clothing fabric to be chosen for Artemis missions are prioritised "
    "for immediate testing.",
    "recommendation", materials=["lithium ion battery (LIB)", "Artemis crew clothing fabric (to be selected)"])
add(6, "Conclusions and Recommendations, priority 2",
    "Proof-of-concept studies in simulated lunar gravity will provide a starting point for lunar habitat experiments",
    "Priority 2: evaluate gravity effects on fire signatures and plume transport, starting with "
    "proof-of-concept studies in simulated lunar gravity as a basis for lunar habitat experiments.",
    "recommendation", conditions=cond(g="simulated lunar gravity"))
add(6, "Conclusions and Recommendations, priority 2",
    "Emission factors from these studies will enable computational simulations of smoke plume transport",
    "Emission factors from those studies would feed computational simulations of smoke plume transport and "
    "guide detector placement in future cabins.",
    "recommendation")
add(6, "Conclusions and Recommendations, priority 3",
    "Elevated O2 and reduced cabin pressure conditions will influence fire signatures and therefore",
    "Priority 3: evaluate exploration-atmosphere effects on fire signatures in reduced gravity; elevated O2 and "
    "reduced cabin pressure will influence fire signatures and hence fire detection.",
    "recommendation", conditions=cond(g="reduced gravity"))
add(6, "Conclusions and Recommendations, priority 3",
    "Each variable must be investigated individually in both ground and reduced gravity experiments",
    "O2 and pressure must each be investigated separately, in both ground and reduced-gravity experiments.",
    "recommendation")
add(6, "Conclusions and Recommendations, priority 4",
    "capable of rapidly identifying smoke components through a combination of different particle and gas",
    "Priority 4: develop improved detection systems from spacecraft fire safety data; a transformative system "
    "would quickly identify smoke components by combining different particle and gas measurement techniques.",
    "recommendation")
add(6, "Conclusions and Recommendations, priority 4",
    "reduce nuisance alarms from suspended cabin and lunar dust",
    "Such a combined system would increase the number of detectable fires and cut nuisance alarms caused by "
    "suspended cabin dust and lunar dust.",
    "recommendation", conditions=cond(g="cabin / lunar"),
    scope="Expected benefit, not demonstrated; relates to false (nuisance) alarms, not missed alarms.")

# ---------------------------------------------------------------- references
# (number, pdf_page, anchor, citation, cited_where)
REFS = [
    (1, 7, "Lag Times Associated with Fire Detection and Suppression",
     "Mowrer, F. W. Lag Times Associated with Fire Detection and Suppression. Fire Technol. 1990, 26(3), 244-265. doi:10.1007/BF01040111.",
     "p2: heat/radiation detectors useful for select terrestrial applications"),
    (2, 7, "Safety Design for Space Systems",
     "Musgrave, G.; Larsen, A.; Sgobba, T. Safety Design for Space Systems, 1st ed.; Butterworth-Heinemann: Burlington, MA; Oxford, 2009.",
     "p2: history of Shuttle ionization and ISS forward light scattering detectors"),
    (3, 7, "Smoke Characterization and Feasibility of the Moment Method for Spacecraft Fire Detection",
     "Meyer, M. E.; Mulholland, G. W.; Bryg, V.; Urban, D. L.; Yuan, Z.-G.; Ruff, G. A.; Cleary, T.; Yang, J. Smoke Characterization and Feasibility of the Moment Method for Spacecraft Fire Detection. Aerosol Sci. Technol. 2015, 49(5), 299-309. doi:10.1080/02786826.2015.1025124.",
     "p2: SAME missed-alarm statement (refs 3-5); p4: residence-time explanation of SAME particle size differences (refs 3,4)"),
    (4, 7, "Pyrolysis Smoke Generated Under Low-Gravity Conditions",
     "Mulholland, G. W.; Meyer, M.; Urban, D. L.; Ruff, G. A.; Yuan, Z.; Bryg, V.; Cleary, T.; Yang, J. Pyrolysis Smoke Generated Under Low-Gravity Conditions. Aerosol Sci. Technol. 2015, 49(5), 310-321. doi:10.1080/02786826.2015.1025125.",
     "p2: SAME missed-alarm statement (refs 3-5); p4: residence-time explanation (refs 3,4)"),
    (5, 7, "Evaluation of Spacecraft Smoke Detector Performance in the",
     "Meyer, M. E.; Urban, D. L.; Mulholland, G. W.; Bryg, V.; Yuan, Z.-G.; Ruff, G. A.; Cleary, T.; Yang, J. Evaluation of Spacecraft Smoke Detector Performance in the Low-Gravity Environment. Fire Saf. J. 2018, 98, 74-81. doi:10.1016/j.firesaf.2018.04.004.",
     "p2: SAME missed-alarm statement (refs 3-5); by title, the reference most directly about detector performance"),
    (6, 7, "Fire Detection Tradeoffs as a Function of Vehicle Parameters",
     "Urban, D.; Dietrich, D.; Brooker, J.; Meyer, M.; Ruff, G. Fire Detection Tradeoffs as a Function of Vehicle Parameters. 46th Int. Conf. Environ. Syst., Vienna, Austria, 10-14 July 2016; ICES-2016-318. https://ttu-ir.tdl.org/handle/2346/67662.",
     "p2: ECLSS filtration outpacing smoke accumulation; p4: emission factors; p5: CO detector in parallel with smoke detector"),
    (7, 7, "Operation and Development Status of the Spacecraft Fire Experiments",
     "Ruff, G.; Urban, D. Operation and Development Status of the Spacecraft Fire Experiments (Saffire). 46th Int. Conf. Environ. Syst., Vienna, Austria, 10-14 July 2016; ICES-2016-428. https://ttu-ir.tdl.org/handle/2346/67728.",
     "p3: Saffire large-scale fire experiments (refs 7-9)"),
    (8, 7, "Safety Implications of Preliminary Results from Saffire IV and V Experiments on Large",
     "Urban, D.; Ruff, G.; Ferkul, P.; Owens, J.; Olson, S.; Meyer, M.; Fortenberry, C.; Brooker, J.; Graf, J.; Casteel, M.; Jomaas, G.; Toth, B.; Eigenbrod, C.; T'ien, J.; Liao, Y.-T.; Fernandez-Pello, C.; Meyer, F.; Legros, G.; Guibaud, A.; Smirnov, N.; Fujita, O. Fire Safety Implications of Preliminary Results from Saffire IV and V Experiments on Large Scale Spacecraft Fires. 50th Int. Conf. Environ. Syst., 12-15 July 2021; ICES-2021-266. https://ttu-ir.tdl.org/handle/2346/87224.",
     "p3: Saffire (refs 7-9)"),
    (9, 7, "Evaluation of Combustion Products from Large-Scale Spacecraft Fires during the",
     "Fortenberry, C.; Casteel, M.; Graf, J.; Easton, J.; Niehaus, J.; Meyer, M.; Urban, D.; Ruff, G. Evaluation of Combustion Products from Large-Scale Spacecraft Fires during the Saffire-IV and Saffire-V Experiments. 50th Int. Conf. Environ. Syst., 12-15 July 2021; ICES-2021-244. https://ttu-ir.tdl.org/handle/2346/87212.",
     "p3: Saffire (refs 7-9)"),
    (10, 7, "Characterization of Laptop Fires in Spacecraft",
     "Padilla, R.; Dietrich, D.; Lynch, K.; Juarez, A.; Harper, S.; Nagel, C.; Ruff, G.; Urban, D. Characterization of Laptop Fires in Spacecraft. 49th Int. Conf. Environ. Syst., Boston, MA, 7-11 July 2019; ICES-2019-188. https://ttu-ir.tdl.org/handle/2346/84955.",
     "p3: laptop LIB fires among most likely and most dangerous scenarios"),
    (11, 7, "Spacecraft Fire Safety Technology Development Plan",
     "Ruff, G.; Urban, D.; Dietrich, D. L. Spacecraft Fire Safety Technology Development Plan for Exploration Missions. Int. Conf. Environ. Syst., 2020; ICES-2020-173. https://ttu-ir.tdl.org/handle/2346/86349.",
     "p3: anticipated increased reliance on LIBs"),
    (12, 7, "Toxicity, a Serious Concern of Thermal Runaway from Commercial Li-Ion Battery",
     "Sun, J.; Li, J.; Zhou, T.; Yang, K.; Wei, S.; Tang, N.; Dang, N.; Li, H.; Qiu, X.; Chen, L. Toxicity, a Serious Concern of Thermal Runaway from Commercial Li-Ion Battery. Nano Energy 2016, 27, 313-319. doi:10.1016/j.nanoen.2016.06.031.",
     "p3: gaseous products of LIB fires (refs 12-15)"),
    (13, 7, "Toxic Gas Emissions from Damaged Lithium Ion",
     "Nedjalkov, A.; Meyer, J.; Kohring, M.; Doering, A.; Angelmahr, M.; Dahle, S.; Sander, A.; Fischer, A.; Schade, W. Toxic Gas Emissions from Damaged Lithium Ion Batteries - Analysis and Safety Enhancement Solution. Batteries 2016, 2(1), 5. doi:10.3390/batteries2010005.",
     "p3: gaseous products of LIB fires (refs 12-15)"),
    (14, 8, "Gas Generation Measurement and Evaluation during Mechanical Processing",
     "Diaz, F.; Wang, Y.; Weyhe, R.; Friedrich, B. Gas Generation Measurement and Evaluation during Mechanical Processing and Thermal Treatment of Spent Li-Ion Batteries. Waste Manag. 2019, 84, 102-111. doi:10.1016/j.wasman.2018.11.029.",
     "p3: gaseous products of LIB fires (refs 12-15)"),
    (15, 8, "Recycling of Mixed Cathode Lithium-Ion Batteries for Electric Vehicles",
     "Or, T.; Gourley, S. W. D.; Kaliyappan, K.; Yu, A.; Chen, Z. Recycling of Mixed Cathode Lithium-Ion Batteries for Electric Vehicles: Current Status and Future Outlook. Carbon Energy 2020, 2(1), 6-43. doi:10.1002/cey2.29.",
     "p3: gaseous products of LIB fires (refs 12-15)"),
    (16, 8, "Comprehensive Hazard Analysis of Failing Automotive Lithium-Ion Batteries",
     "Essl, C.; Golubkov, A. W.; Gasser, E.; Nachtnebel, M.; Zankel, A.; Ewert, E.; Fuchs, A. Comprehensive Hazard Analysis of Failing Automotive Lithium-Ion Batteries in Overtemperature Experiments. Batteries 2020, 6(2), 30. doi:10.3390/batteries6020030.",
     "p3: particles from large-scale LIB fires (refs 16,17)"),
    (17, 8, "Detection of Li-Ion Battery Failure and Venting with Carbon Dioxide Sensors",
     "Cai, T.; Valecha, P.; Tran, V.; Engle, B.; Stefanopoulou, A.; Siegel, J. Detection of Li-Ion Battery Failure and Venting with Carbon Dioxide Sensors. eTransportation 2021, 7, 100100. doi:10.1016/j.etran.2020.100100.",
     "p3: large-scale LIB fires (refs 16,17)"),
    (18, 8, "Hazardous Effects of Li-Ion Battery Based Fires",
     "Padilla, R.; Alcantara, I.; Meyer, M.; Juarez, A.; Dietrich, D.; Urban, D.; Ruff, G.; Nagel, C. R. Hazardous Effects of Li-Ion Battery Based Fires. Int. Conf. Environ. Syst., 2020; ICES-2020-433. https://ttu-ir.tdl.org/handle/2346/86372.",
     "p3: the only known study of smoke particles from laptop LIB fires"),
    (19, 8, "Particle Morphology and Elemental Composition of Smoke Generated by",
     "Meyer, M. E. Particle Morphology and Elemental Composition of Smoke Generated by Overheating Common Spacecraft Materials; NASA/TM-2015-218912; NASA Glenn Research Center: Cleveland, OH, 2015. https://ntrs.nasa.gov/citations/20160000940.",
     "p3: same fuel at different max temperatures gives different particles; p5: GASP laboratory"),
    (20, 8, "Spread Rate and Soot Production",
     "Guibaud, A.; Citerne, J.-M.; Consalvi, J.-L.; Legros, G. On the Effects of Opposed Flow Conditions on Non-Buoyant Flames Spreading over Polyethylene-Coated Wires - Part I: Spread Rate and Soot Production. Combust. Flame 2020, 221, 530-543. doi:10.1016/j.combustflame.2020.07.044.",
     "p3: residence time in reduced gravity affects particle formation; p5 and Table 1: parabolic flights"),
    (21, 8, "Soot Oxidation Quenching and Smoke Release",
     "Guibaud, A.; Citerne, J.-M.; Consalvi, J.-L.; Legros, G. On the Effects of Opposed Flow Conditions on Non-Buoyant Flames Spreading over Polyethylene-Coated Wires - Part II: Soot Oxidation Quenching and Smoke Release. Combust. Flame 2020, 221, 544-551. doi:10.1016/j.combustflame.2020.08.038.",
     "p3: smoke-generation propensity; p4: atmosphere/gravity effects (refs 21,24-26); p5 and Table 1: parabolic flights"),
    (22, 8, "Near-Surface Vapour Bubble Layers in Buoyant Low Stretch",
     "Olson, S. L.; T'ien, J. S. Near-Surface Vapour Bubble Layers in Buoyant Low Stretch Burning of Polymethylmethacrylate. Fire Mater. 1999, 23(5), 227-237. doi:10.1002/(SICI)1099-1018(199909/10)23:5<227::AID-FAM689>3.0.CO;2-2.",
     "p3: PMMA monomer vapour jetting"),
    (23, 8, "Fundamentals of Fire Suppression in Reduced",
     "Dietrich, D. L.; Ruff, G. A.; Urban, D. L. Fundamentals of Fire Suppression in Reduced Gravity Environments. SAE Int. J. Aerosp. 2008, 1(1), 307-316. doi:10.4271/2008-01-2087.",
     "p4: planned lunar habitat 34% O2, 8.2 psi"),
    (24, 8, "Buoyant Downward Diffusion Flame Spread and Extinction",
     "Sacksteder, K. R.; Tien, J. S. Buoyant Downward Diffusion Flame Spread and Extinction in Partial-Gravity Accelerations. Symp. Int. Combust. 1994, 25(1), 1685-1692. doi:10.1016/S0082-0784(06)80816-7.",
     "p4: atmosphere/gravity effects on flammability (refs 21,24-26)"),
    (25, 8, "Low-Pressure Flame Spread Limits of Fire Resistant Fabrics",
     "Osorio, A. F.; Fernandez Pello, A.; Urban, D. L.; Ruff, G. A. Low-Pressure Flame Spread Limits of Fire Resistant Fabrics. 43rd Int. Conf. Environ. Syst., Vail, CO, 14-18 July 2013; AIAA, 2013. doi:10.2514/6.2013-3386.",
     "p4: refs 21,24-26"),
    (26, 8, "Limiting Conditions for Flame Spread in Fire Resistant Fabrics",
     "Osorio, A. F.; Fernandez-Pello, C.; Urban, D. L.; Ruff, G. A. Limiting Conditions for Flame Spread in Fire Resistant Fabrics. Proc. Combust. Inst. 2013, 2(34), 2691-2697 (volume/issue as printed). doi:10.1016/j.proci.2012.07.053.",
     "p4: refs 21,24-26"),
    (27, 9, "Soot Formation Effects of Oxygen Concentration in the Oxidizer Stream",
     "Lee, K.-O.; Megaridis, C.; Zelepouga, S.; Saveliev, A.; Kennedy, L.; Charon, O.; Ammouri, F. Soot Formation Effects of Oxygen Concentration in the Oxidizer Stream of Laminar Coannular Nonpremixed Methane/Air Flames. Combust. Flame 2000, 121, 323-333. doi:10.1016/S0010-2180(99)00131-5.",
     "p4: methane soot vs O2"),
    (28, 9, "Turbulent Propane Flames at the Technical Scale",
     "Edland, R.; Allguren, T.; Normann, F.; Andersson, K. Formation of Soot in Oxygen-Enriched Turbulent Propane Flames at the Technical Scale. Energies 2020, 13(1), 191. doi:10.3390/en13010191.",
     "p4: propane soot vs O2 (above 30% O2)"),
    (29, 9, "The Influence of Pressure and Temperature on Soot Formation in Premixed Flames",
     "Bohm, H.; Hesse, D.; Jander, H.; Luers, B.; Pietscher, J.; Wagner, H. G. G.; Weiss, M. The Influence of Pressure and Temperature on Soot Formation in Premixed Flames. Symp. Int. Combust. 1989, 22(1), 403-411. doi:10.1016/S0082-0784(89)80047-5.",
     "p4: reduced pressure and soot formation"),
    (30, 9, "Laser Spectroscopy Multi-Gas Monitor: Results of a Year Long Technology Demonstration on ISS",
     "Mudgett, P. D.; Pilgrim, J. S.; Wood, W. R. Laser Spectroscopy Multi-Gas Monitor: Results of a Year Long Technology Demonstration on ISS. 45th Int. Conf. Environ. Syst., Bellevue, WA, 12-16 July 2015; ICES-2015-243. https://ttu-ir.tdl.org/handle/2346/64501.",
     "p5: laser spectroscopy-based combustion products monitor; p6: instrumentation already on spacecraft"),
    (31, 9, "The First Combined Thermal Desorption Aerosol Gas",
     "Williams, B. J.; Jayne, J. T.; Lambe, A. T.; Hohaus, T.; Kimmel, J. R.; Sueper, D.; Brooks, W.; Williams, L. R.; Trimborn, A. M.; Martinez, R. E.; Hayes, P. L.; Jimenez, J. L.; Kreisberg, N. M.; Hering, S. V.; Worton, D. R.; Goldstein, A. H.; Worsnop, D. R. The First Combined Thermal Desorption Aerosol Gas Chromatograph-Aerosol Mass Spectrometer (TAG-AMS). Aerosol Sci. Technol. 2014, 48(4), 358-370. doi:10.1080/02786826.2013.875114.",
     "p5: in situ chemical instruments (refs 31-33)"),
    (32, 9, "Development of a Volatility and Polarity Separator (VAPS)",
     "Martinez, R. E.; Williams, B. J.; Zhang, Y.; Hagan, D.; Walker, M.; Kreisberg, N. M.; Hering, S. V.; Hohaus, T.; Jayne, J. T.; Worsnop, D. R. Development of a Volatility and Polarity Separator (VAPS) for Volatility- and Polarity-Resolved Organic Aerosol Measurement. Aerosol Sci. Technol. 2016, 50(3), 255-271. doi:10.1080/02786826.2016.1147645.",
     "p5: refs 31-33"),
    (33, 9, "Aerosol Chemical Speciation Monitor (ACSM) Instrument Handbook",
     "Watson, T. B. Aerosol Chemical Speciation Monitor (ACSM) Instrument Handbook; DOE/SC-ARM-TR-196; DOE Office of Science ARM Program, Brookhaven National Laboratory: Upton, NY, 2017. doi:10.2172/1375336.",
     "p5: refs 31-33"),
    (34, 9, "Pollutant Emissions during the Pyrolysis and Combustion of Flexible Polyurethane Foam",
     "Garrido, M. A.; Font, R.; Conesa, J. A. Pollutant Emissions during the Pyrolysis and Combustion of Flexible Polyurethane Foam. Waste Manag. 2016. doi:10.1016/j.wasman.2016.04.007.",
     "p5: chemical characterisation informs fire response"),
    (35, 9, "A Technique for Rapid Gas Chromatography Analysis Applied to Ambient Organic",
     "Zhang, Y.; Williams, B. J.; Goldstein, A. H.; Docherty, K.; Ulbrich, I. M.; Jimenez, J. L. A Technique for Rapid Gas Chromatography Analysis Applied to Ambient Organic Aerosol Measurements from the Thermal Desorption Aerosol Gas Chromatograph (TAG). Aerosol Sci. Technol. 2014, 48(11), 1166-1182. doi:10.1080/02786826.2014.967832.",
     "p5: positive matrix factorization (refs 35-37)"),
    (36, 9, "A Technique for Rapid Source Apportionment",
     "Zhang, Y.; Williams, B. J.; Goldstein, A. H.; Docherty, K. S.; Jimenez, J. L. A Technique for Rapid Source Apportionment Applied to Ambient Organic Aerosol Measurements from a Thermal Desorption Aerosol Gas Chromatograph (TAG). Atmos. Meas. Tech. 2016, 9(11), 5637-5653. doi:10.5194/amt-9-5637-2016.",
     "p5: refs 35-37"),
    (37, 9, "Catalytic Lignin Depolymerization Using Positive Matrix Factorization",
     "Gao, Y.; Walker, M. J.; Barrett, J. A.; Hosseinaei, O.; Harper, D. P.; Ford, P. C.; Williams, B. J.; Foston, M. B. Analysis of Gas Chromatography/Mass Spectrometry Data for Catalytic Lignin Depolymerization Using Positive Matrix Factorization. Green Chem. 2018, 20(18), 4366-4377. doi:10.1039/C8GC01474D.",
     "p5: refs 35-37"),
    (38, 10, "Deep LSTM Variational Autoencoder for Improved Sensitivity and Reliability",
     "Xu, Z.; Guo, Y.; Saleh, J. H. Advances Toward the Next Generation Fire Detection: Deep LSTM Variational Autoencoder for Improved Sensitivity and Reliability. IEEE Access 2021, 9, 30636-30653. doi:10.1109/ACCESS.2021.3060338.",
     "p5: deep LSTM networks with variational autoencoders"),
    (39, 10, "Investigating Flame Spread Interaction over Wires",
     "Citerne, J.-M.; Dutilleul, H.; Kizawa, K.; Nagachi, M.; Fujita, O.; Kikuchi, M.; Jomaas, G.; Rouvreau, S.; Torero, J. L.; Legros, G. Fire Safety in Space - Investigating Flame Spread Interaction over Wires. Acta Astronaut. 2016, 126, 500-509. doi:10.1016/j.actaastro.2015.12.021.",
     "p5 and Table 1: parabolic flights"),
    (40, 10, "Zero-Gravity Centrifuge Used for the Evaluation of Material",
     "Ferkul, P. V.; Olson, S. L. Zero-Gravity Centrifuge Used for the Evaluation of Material Flammability in Lunar Gravity. J. Thermophys. Heat Transf. 2011, 25(3), 457-461. doi:10.2514/1.T3651.",
     "p5 and Table 1: ZGRF drop tower centrifuge rig (5.2 s lunar gravity)"),
    (41, 10, "High Throughput Ground-Based Reduced Gravity Testing [white paper]",
     "Urban, D.; Paul, A.-L.; Sackett, C.; Weislogel, M.; Kim, J.; Sinha-Ray, S.; Liao, Y.-T.; Miller, F.; Neumann, E. High Throughput Ground-Based Reduced Gravity Testing [white paper]. Submitted to NASEM for the Decadal Survey on Biological and Physical Sciences in Space 2023-2032, 2021. URL on surveygizmoresponseuploads.s3.amazonaws.com (UrbanDavidL.docx; accessed 31 Oct 2021).",
     "p5: planned drop tower improvements to 10 s"),
    (42, 10, "An Overview of the Microgravity Science Glovebox (MSG)",
     "Spivey, R.; Flores, G. An Overview of the Microgravity Science Glovebox (MSG) Facility, and the Gravity-Dependent Phenomena Research Performed in the MSG on the International Space Station (ISS). 46th AIAA Aerospace Sciences Meeting and Exhibit, Reno, NV, 7-10 Jan 2008; AIAA, 2008. doi:10.2514/6.2008-812.",
     "p5 and Table 1: MSG"),
    (43, 10, "Results from On-Board CSA-CP and CDM Sensor Readings",
     "Olson, S. L.; Ferkul, P. V.; Bhattacharjee, S.; Miller, F. J.; Fernandez-Pello, C.; Link, S.; T'ien, J. S.; Wichman, I. Results from On-Board CSA-CP and CDM Sensor Readings during the Burning and Suppression of Solids - II (BASS-II) Experiment in the Microgravity Science Glovebox (MSG). 45th Int. Conf. Environ. Syst., Bellevue, WA, 12-16 July 2015; ICES-2015-196. https://ttu-ir.tdl.org/handle/2346/64468.",
     "p5 and Table 1: MSG"),
    (44, 10, "Droplet Combustion Experiments Aboard the International Space Station",
     "Dietrich, D. L.; Nayagam, V.; Hicks, M. C.; Ferkul, P. V.; Dryer, F. L.; Farouk, T.; Shaw, B. D.; Suh, H. K.; Choi, M. Y.; Liu, Y. C.; Avedisian, C. T.; Williams, F. A. Droplet Combustion Experiments Aboard the International Space Station. Microgravity Sci. Technol. 2014, 26(2), 65-76. doi:10.1007/s12217-014-9372-2.",
     "p5 and Table 1: CIR"),
    (45, 10, "Monitoring of the Atmosphere on the International Space Station with the Air Quality Monitor",
     "Wallace, W. T.; Limero, T. F.; Loh, L. J.; Mudgett, P. D.; Gazda, D. B. Monitoring of the Atmosphere on the International Space Station with the Air Quality Monitor. 47th Int. Conf. Environ. Syst., Charleston, SC, 16-20 July 2017; ICES-2017-103. https://ttu-ir.tdl.org/handle/2346/64468 (handle as printed; identical to ref 43's handle).",
     "p6: instrumentation already on spacecraft (refs 30,45)"),
    (46, 10, "Evaluation of Nine Low-Cost-Sensor-Based Particulate Matter Monitors",
     "Li, J.; Mattewal, S. K.; Patel, S.; Biswas, P. Evaluation of Nine Low-Cost-Sensor-Based Particulate Matter Monitors. Aerosol Air Qual. Res. 2020, 20(2), 254-270. doi:10.4209/aaqr.2018.12.0485.",
     "p6: novel calibrated sensors (refs 46,47)"),
    (47, 10, "Low-Cost PM2.5 Sensors: An Assessment of Their Suitability for Various",
     "Jayaratne, R.; Liu, X.; Ahn, K.-H.; Asumadu-Sakyi, A.; Fisher, G.; Gao, J.; Mabon, A.; Mazaheri, M.; Mullins, B.; Nyaku, M.; Ristovski, Z.; Scorgie, Y.; Thai, P.; Dunbabin, M.; Morawska, L. Low-Cost PM2.5 Sensors: An Assessment of Their Suitability for Various Applications. Aerosol Air Qual. Res. 2020, 20(3), 520-532. doi:10.4209/aaqr.2018.10.0390.",
     "p6: refs 46,47"),
    (48, 10, "ISS Destiny Laboratory Smoke Detection Model",
     "Brooker, J. E.; Urban, D. L.; Ruff, G. A. ISS Destiny Laboratory Smoke Detection Model; SAE Technical Paper 2007-01-3076; SAE International: Warrendale, PA, 2007. doi:10.4271/2007-01-3076.",
     "p6: NIST FDS for any gravity environment (refs 48,49)"),
    (49, 11, "Modeling and Analysis of Realistic Fire Scenarios in Spacecraft",
     "Brooker, J. E.; Dietrich, D. L.; Gokoglu, S. A.; Urban, D. L.; Ruff, G. A. Modeling and Analysis of Realistic Fire Scenarios in Spacecraft. 45th Int. Conf. Environ. Syst., Bellevue, WA, 12-16 July 2015; ICES-2015-204. https://ttu-ir.tdl.org/handle/2346/64475.",
     "p6: refs 48,49"),
]
for n, pg, anc, cit, where in REFS:
    extra = ""
    if n in (5, 7, 11, 22, 28, 30, 41, 45):
        extra = (" Citation text normalised where pdftotext dropped a line-end hyphen (checked against a "
                 "layout rendering).")
    add(pg, f"References, entry ({n})", anc, f"[{n}] {cit}", "reference",
        scope=f"Cited in the white paper at: {where}.{extra}")

# ---------------------------------------------------------------- checksum
add(1, "Raw file sources/raw/wp2021/wp2021.pdf (whole document)", TITLE,
    f"Raw PDF sha256 {SHA}, {NBYTES} bytes, {NPAGES} pages, retrieved {RETRIEVED} from the science.nasa.gov "
    f"URL; text made with plain pdftotext (no -layout).",
    "checksum", scope="File integrity record; anchor is the document title on pdf page 1.")

# ---------------------------------------------------------------- verify
errors = []
for i, it in enumerate(items, 1):
    it["item_id"] = f"{DOC}-{i:02d}" if len(items) < 100 else f"{DOC}-{i:03d}"
    a = " ".join(it["anchor_quote"].split())
    nw = len(a.split())
    if nw > 15:
        errors.append(f"{it['item_id']}: anchor has {nw} words")
    pg = it["pdf_page"]
    if pg is None or a not in norm_pages[pg - 1]:
        hits = [k + 1 for k, p in enumerate(norm_pages) if a in p]
        errors.append(f"{it['item_id']}: anchor not on page {pg}; found on {hits}: {a!r}")
if errors:
    print("\n".join(errors))
    sys.exit(1)

identifiers = {"doi": None, "ntrs": None, "psi": None, "pmc": None}
access_note = ("Downloaded directly with curl (HTTP 200, application/pdf). Text-based PDF, 11 pages; no "
               "printed page numbers. Cover labels the survey 2022-2032.")
doc = {
    "doc_id": DOC, "title": TITLE, "year": 2021, "authors": AUTHORS, "url": URL,
    "local_path": f"sources/raw/{DOC}/wp2021.pdf", "text_path": f"sources/text/{DOC}.txt",
    "sha256": SHA, "page_count": NPAGES, "identifiers": identifiers, "accessible": True,
    "access_note": access_note,
}
meta = {
    "doc_id": DOC, "title": TITLE, "year": 2021, "authors": AUTHORS, "url": URL,
    "retrieved_utc": RETRIEVED, "sha256": SHA, "bytes": NBYTES, "page_count": NPAGES,
    "identifiers": identifiers,
    "license_note": ("White paper submitted to NASEM decadal survey, hosted on science.nasa.gov; no explicit "
                     "license statement found in the PDF. Several authors are US Government (NASA) employees; "
                     "treat as quotable with attribution, excerpts only."),
    "accessible": True, "access_note": access_note,
    "pdf_metadata_creation_date": "2021-10-31T16:11:32-04:00",
}

out = {
    "source_key": DOC,
    "documents": [doc],
    "items": items,
    "inaccessible": [
        {"what": "Figure 1 graphic (smoke plume transport in terrestrial, micro- and lunar gravity), pdf page 4",
         "why": "Only the caption and surrounding text were extracted with pdftotext; the figure image was not "
                "analysed, so no claims are made about its drawn content."},
    ],
    "search_log": [
        {"query": "direct download of the given white-paper URL", "where": "science.nasa.gov (curl)",
         "hits": 1, "notes": "HTTP 200, 233897 bytes, application/pdf, 11 pages."},
        {"query": "SAME-R|DAFT|ACME|E-FIELD|CFI", "where": "sources/text/wp2021.txt (grep)", "hits": 0,
         "notes": "Only SAME is mentioned; no SAME-R, DAFT or ACME mention within this source."},
        {"query": "Saffire", "where": "sources/text/wp2021.txt (grep, matching lines)", "hits": 4,
         "notes": "Body: one sentence on pdf page 3 (refs 7-9). Rest are reference titles (refs 7, 8, 9)."},
        {"query": "alarm|nuisance|false|dust", "where": "sources/text/wp2021.txt (grep, matching lines)", "hits": 13,
         "notes": "Missed-alarm (p2), filtration/alarm threshold (p2), dust nuisance alarms and vacuuming (p2), "
                  "alarm time prediction (p4), false alarm reduction and smoke-vs-lunar-dust discrimination (p5), "
                  "nuisance alarms in recommendation 4 (p6)."},
        {"query": "pdftotext -layout cross-check", "where": "scratchpad copy (not saved in sources/)",
         "hits": 1, "notes": "Used only to confirm Table 1 column alignment and line-end hyphens in references."},
    ],
    "open_questions": [
        "The white paper states the SAME missed-alarm result only as 'half' (Kapton) and 'two-thirds' (Teflon) "
        "of tests, citing refs 3-5 jointly; it gives no test counts, heating temperatures, aging, flow or alarm "
        "criteria. The denominators and conditions must be confirmed in Meyer et al. 2018 (Fire Saf. J. 98:74-81) "
        "and Meyer/Mulholland et al. 2015 (Aerosol Sci. Technol. 49(5)).",
        "Whether the 'ISS detector' result includes SAME-R tests: the white paper names only SAME.",
        "The cover says 'Decadal Survey, 2022-2032' while ref 41 in the same paper says '2023-2032'; the task "
        "brief also says 2023-2032.",
        "The statement that ISS crew disable smoke detectors while vacuuming carries no citation in the paper.",
        "Whether ref 6 (Urban et al. 2016, ICES-2016-318) is a model/analysis or experiment is not stated in the "
        "white paper.",
        "Ref 45's handle (2346/64468) is identical to ref 43's handle; one of them is probably a citation error.",
        "DAFT, ACME and SAME-R are not mentioned within this source; their absence here says nothing about "
        "whether NASA studied them.",
    ],
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
with open(META, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=1)
from collections import Counter
print("items", len(items))
print(Counter(i["category"] for i in items))
