# SAME scientific reference evidence

## What do the publications establish about labels and experimental independence?

### Takeaway
Detector analog responses and alarm boundaries are different outputs. Fresh and aged measurements from a smoke batch share a heating event and must remain grouped. The literature does not justify pooling uncalibrated raw voltages across hardware or treating saturated readings as exact signal measurements.

### Cited Findings
- The 2018 article's correct citation is Meyer et al., *Evaluation of Spacecraft Smoke Detector Performance in the Low-Gravity Environment*, Fire Safety Journal 98, 74–81, DOI 10.1016/j.firesaf.2018.04.004. Its full author manuscript was downloaded as `data/references/PMC7918997.html` and text extracted as `PMC7918997.txt`. Section 2.2 explicitly describes software-controlled heating, airflow and aging; half the smoke is measured unaged and the remainder after aging. These are controlled configuration fields, not reasons to exclude variables as unavailable. [Full author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/)
- Section 3.2 and Figure 9: ISS detector signal is frequently saturated for silicone, Pyrell and lamp wick. Shuttle observations are fewer because its pump consumes 3 L/min and prevents aging experiments. Shuttle signal plotted is the offset between baseline and smoke response; the A/D system scales the raw output. These definitions must be reconciled with raw files before alarm labels are calculated. Figure 9's dashed ISS alarm boundary coincides with the 2.0 V tick. The Shuttle dashed boundary is graphically near 0.42 V, but there is no exact numerical statement verified here: do not encode 0.42 as an exact source threshold. Figure downloaded to `data/references/detector_fig9.jpg` and visually inspected. [Full author manuscript, section 3.2 and Figure 9](https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/)
- Section 3.2 reports ISS failures to alarm in over half the Kapton tests and two thirds of Teflon tests; this is a published aggregate, not a per-run label table or denominator. Do not treat it as a model accuracy target. ISS calibration particles are 0.6 μm and laser wavelength approximately 1 μm. [Full author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/)
- Section 3.3 reports 72 TEM grids; DBP particles evaporated in TEM vacuum and silicone leaves residue. SAME-1 TEM grids were contaminated, so TEM coverage is not equivalent across campaigns. [Full author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/)
- NTRS 20130000422 is *Particle Morphology and Size Results from the Smoke Aerosol Measurement Experiment-2*, Urban et al., AIAA 2012-3536, 42nd ICES, July 15–19 2012. Abstract confirms SAME-R/SAME-2 in Expedition 24 July–September 2010; adds two-moment detector and expanded test matrix. It states heating airflow from quiescent to 8 cm/s and chamber aging approximately 11–1800 s. [NASA PDF](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf)
- NTRS 20120012884 exact title is *Properties of Smoke from Overheated Materials in Low-Gravity*, Urban et al.; it is not titled "SAME flight results with instrument calibrations." PDF pp4–5 describe P-Trak, first moment ion chamber, DustTrak and calibration. P-Trak nominal range 0–100,000 particles/cm³ and 20 nm–1 μm; smoke requires dilution. DustTrak range 0.001–100 mg/m³. SAME-1 used 1 μm and 10 μm impactors; differences concern particles above 1 μm. Raw factory mass is not automatically calibrated smoke mass. [NASA PDF](https://ntrs.nasa.gov/api/citations/20120012884/downloads/20120012884.pdf)
- NTRS 20130000422 PDF pp4–6: P-Trak correlations vary with particle size; ion-chamber correlation was substantially insensitive to size in the tested range; DustTrak response depends on size and refractive index and needs material-specific calibration. First-moment diagnostic ion chamber is distinct from the spacecraft Shuttle detector. [NASA PDF](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf)
- User's NIST final report link resolves in the web tool to a 61-page report titled *Smoke Aerosol Measurement Experiment (SAME)*, **Final Report**, March 5, 2010, project period November 1, 2000–April 14, 2009. Listed authors start with David L. Urban, Gary A. Ruff and William Sheredy, followed by Cleary, Yang, Mulholland, Yuan. It is not verified as a Yang-led NASA TM. Contents include uncertainty analysis, calibration, and Appendix A flight-test log. PDF front matter ii confirms four spacecraft materials plus DBP reference in SAME-1 and 10–1800 s aging. [NIST final report](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=904707)

### Inferences
- Use a heating-run ID as the minimum grouping unit where aging measurements share the same smoke batch; a material × condition row is not itself proof of an independent experiment.
- Thresholding an analog output can support a derived alarm proxy only once the raw channel baseline, scaling and source threshold are reconciled. Do not train alarm from that same analog signal.
- A ceiling plateau around 6.2 V is visible in ISS Figure 9, but an exact saturation cutoff is not established here and should come from raw-file documentation.

### Gaps
- No standalone 2021 NASA SAME/SAME-R report was verified. Search of NASA/NTRS and exact titles found the 2018 article whose manuscript became available in PMC on **March 1, 2021**. This is a plausible date confusion, not proof of what the user intended. Do not cite an invented 2021 report.
- Challenge URL `https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/` returned a web-fetch 502; challenge content was not independently verified.
- NIST final PDF could be read via the web tool, but direct urllib download returned HTTP 403. The two NASA PDF files and the full 2018 HTML are locally preserved; `Meyer2018.blocked.html` records the failed PMC PDF route rather than masquerading as a PDF.

## Which formulas and numerical comparisons can validate processing?

### Takeaway
Count mean diameter M1/M0 and diameter of average mass (M3/M0)^(1/3) do not require a lognormal size distribution. Inferring geometric mean or geometric standard deviation adds assumptions; mass-to-third-moment conversion also requires particle density and spherical-equivalent interpretation.

### Cited Findings
- NTRS 20130000422 PDF pp3–4 equations (2), (6), (7): M_i = integral D^i f_N(D)dD; count mean = M1/M0; diameter of average mass = (M3/M0)^(1/3). For lognormal distribution D_p=D_g exp(p ln² sigma_g), p=0.5 and 1.5 respectively. Hence sigma_g=exp(sqrt(ln(D_mass/D_count))) and D_g=D_count exp(-0.5 ln² sigma_g). Do not apply square root if D_mass < D_count. [NASA PDF](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf)
- Meyer et al. 2015, *Smoke Characterization and Feasibility of the Moment Method for Spacecraft Fire Detection*, Aerosol Science and Technology 49(5), 299–309, DOI 10.1080/02786826.2015.1025124: lognormal and near-spherical assumptions reasonably met for Kapton and lamp wick; Teflon and Pyrell aggregate morphology and unstable silicone complicate interpretation. Ground drum testing did not yield reliable moment data because one or more returned moment instruments malfunctioned; SMPS analysis therefore assessed lognormality rather than supplying a direct moment validation. [Publisher article](https://www.tandfonline.com/doi/full/10.1080/02786826.2015.1025124)
- NTRS 20130000422 PDF p7 Table 1 was extracted using `pdftotext -layout` and **every one of its 10 rows visually checked against the original rendered PDF page**, saved as `data/references/20130000422_table1.png`. The table below is a transcription of source-reported deterministic diameter calculations, not raw sensor measurements. These baseline conditions are not tied to explicit run IDs in that table and should be used as checks only after matching baseline configuration, not as independent test labels. [NASA PDF Table 1](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf)

| Material | State | Geometric mean μm | Count mean μm | Diameter average mass μm | Geometric std |
|---|---|---:|---:|---:|---:|
| Kapton | unaged | 0.042 | 0.056 | 0.101 | 2.154 |
| Kapton | aged 720 s | 0.089 | 0.109 | 0.161 | 1.872 |
| Lampwick | unaged | 0.090 | 0.128 | 0.258 | 2.312 |
| Lampwick | aged 720 s | 0.229 | 0.276 | 0.398 | 1.834 |
| Silicone | unaged | 0.128 | 0.196 | 0.465 | 2.530 |
| Silicone | aged 720 s | 0.269 | 0.355 | 0.619 | 2.108 |
| Teflon | unaged | 0.081 | 0.101 | 0.170 | 2.198 |
| Teflon | aged 720 s | 0.070 | 0.105 | 0.232 | 2.442 |
| Pyrell | unaged | 0.149 | 0.204 | 0.384 | 2.211 |
| Pyrell | aged 720 s | 0.293 | 0.359 | 0.539 | 1.892 |

### Inferences
- Validate formula consistency within published rounding tolerance, but do not mistake that calculation for predictive validation.
- A condition-to-count-mean or condition-to-detector signal task avoids algebraic leakage only when moments and all other measured outcomes stay out of features.

### Gaps
- The exact calibration coefficients, uncertainty propagation and channel mapping still require the dataset's instrument/calibration files. Do not apply literature instrument ranges as per-row censoring thresholds without checking scaling and dilution.
- No direct processed-data comparisons have been run by this research agent. The table provides real source targets for the engineering pipeline, and any comparison needs actual code outputs.

### Addendum: Teflon unaged internal consistency check

The engineering check found a substantial discrepancy in the Teflon unaged row. I reopened and visually inspected the original rendered PDF page 7 a second time. The source unambiguously prints **Dg 0.081 μm, count mean 0.101 μm, diameter of average mass 0.170 μm, sigma_g 2.198**. Those four transcription values are correct and must remain unchanged. [NASA original Table 1](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf)

Executed Python `math` calculations are saved in `data/references/teflon_table1_check.json`. The first two columns cannot be recovered from the geometric pair using the paper's stated lognormal identities: Dg=0.081 and sigma=2.198 imply count mean **0.11045022504616728 μm** and average-mass diameter **0.20536658318748371 μm**, whereas the printed values are **0.101** and **0.170 μm**. Allowing ±0.0005 for rounding of each printed geometric parameter gives count bounds **0.10974877077239335–0.11115192836639257 μm** and mass-diameter bounds **0.203989227499317–0.20674536762330673 μm**. Neither overlaps the corresponding printed value's rounding interval. Conversely, the printed count/mass pair implies Dg **0.0778498177110715 μm** and sigma **2.0576820999219536**.

The surrounding text calls these "results ... for baseline runs" and the caption calls them "Diameter results for baseline runs for each material." It does **not** state that the four columns were averaged independently, specify an averaging operation for the table, or explain the Teflon discrepancy. The preceding calibration discussion (PDF pp5–6) says average-mass diameter was computed for each sample using estimated material densities. This does not establish independent column averaging in Table 1. Independent averaging of nonlinear transformations could in principle break a row-level identity, but this is only a possible explanation, **not verified provenance**. A typographical error or some undocumented processing difference is also possible and likewise unverified.

Report this as an **unresolved internal inconsistency in the source table**, not a failed implementation, corrected source value, or proven averaging effect. Preserve all printed values, flag this row for failed agreement, and exclude it from any claim of formula agreement. Numerical identity agreement for the other rows is a check of published internal consistency, not a learned-model validation or proof that the lognormal morphology assumptions hold for Teflon.
