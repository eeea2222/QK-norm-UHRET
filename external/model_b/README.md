---
license: apache-2.0
language: en
tags:
- scientific-ml
- microgravity
- combustion
- measurement-model
---
# NASA Saffire-I model_b

A reproducible CPU measurement model for the luminous dotted-ridge location in NASA mapped camera1 images. It is fitted to18 agent visual annotations from the concurrent phase and evaluated on6 later time-block annotations. It does not predict a new fire experiment, a danger score, or PMMA behavior.

Held-out position MAE: **4.829 nominal mm**, versus simple threshold baseline **4.545mm**. The learned correction did not demonstrate an improvement. Source-reported whole-burn spread values1.8 and1.3mm/s remain separate reference measurements. One mission and one physical sample underlie both sequential phases.

## Reproduce

Use Python3.12 or3.13 on CPU:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m saffire_b.pipeline
.venv/bin/python -m pytest -q
```

The one-command pipeline imports the checksummed original frame subset if present, or downloads the same original ZIP members from the public NASA PSI API. No credentials are needed. It validates SHA256 and ZIP CRC, derives calibration, preserves timestamps, fits/selects six candidate methods on identical development splits, evaluates the later held-out block, writes plots and exports all state. Reproduction repeats the recorded protocol; the historical test block is not newly unseen when rerun. No source rates train the model and no missing measurements are fabricated. `notebooks/model_b_colab.ipynb` embeds the importable source package and pinned metadata, downloads real NASA data, and runs with **Runtime → Run all** on a standard CPU Colab runtime. No private Hub credentials are required by the notebook.

## Layout and boundaries

- `saffire_b/`: public NASA acquisition, deterministic metadata preparation, nominal checkerboard calibration, candidate fitting/evaluation and standalone inference.
- `data/frames/`: original selected JPEGs plus checksummed metadata; `data/processed/`: derived metadata and trajectory tables.
- `data/annotations*.json`: agent labels, separated development/test provenance. `data/source_reported_reference.json`: visually checked publication-table references, never training labels.
- `artifacts/`: standard joblib learned linear correction, JSON preprocessing/domain configuration, nominal calibration, selection freeze, metrics, environment, checksum manifest and sample inference.
- `reports/`: dataset audit, scoring/selection, evaluation and dashboard contract. `figures/`: executed diagnostic plots.
- `tests/`: real-data preprocessing/calibration, model I/O, input validation, OOD and export/load checks.

The final linear correction is a small standard sklearn `LinearRegression`, not a neural net. Export contains all required state. A simple threshold method nearly matches the corrected model and scores slightly better on the one test block. Keeping both results makes the limited evidence visible. Scikit-learn/joblib/numpy versions are pinned; artifact loading requires no training module.

## Notebook-free integration

```python
from saffire_b import predict_model_b
response = predict_model_b({
    "frame_path": "data/frames/Mapped_S1C1-1465937331457.jpeg",
    "camera_id": "C1",
    "image_mapping": "NASA_mapped",
    "material": "SIBAL",
    "units": "mm"
}, artifact_dir="artifacts")
```

The exact recorded sample request/response is in `artifacts/sample_request_response.json`. `reports/Dashboard integration.md` specifies the schema and scientific interpretation. Corrected positions are `predicted`, raw extractor positions/calibration are `derived`, and published reference values are `source_reported`. Unsupported units/materials/cameras or resized images error; inadequate intensity, backlighting and clipped/absent ridges yield null plus an OOD reason. The learned correction warns when its x-coordinate lies outside its development fit range.

## Scientific limits

The nominal30mm checkerboard dimension is documented only in NASA filenames; the calibration PDF link is broken. Grid spacing repeatability is not total physical uncertainty. Agent annotations are not human ground truth; bright ridges meander and the target differs from the pyrolysis front. All time blocks share one physical specimen. No inference about another material, oxygen/flow setting, spacecraft, camera, or independent experiment is supported. Camera2 and sensor-arrival processing are not implemented. The dashboard can compare units with model_a's BASS-II PMMA rates but must preserve material, scale, flow, quantity-definition and validation differences.

Original source: NASA PSI-98 v4, DOI10.60555/0t15-1z43. Public download API, file IDs, versions, original-archive hashes and member hashes are pinned in `data/source_manifest.json`, `data/archive_hashes.json` and `data/frames/frames.json`. Publication references are NTRS20170008805 p29 TableI and20180005168 pp30–31, checked against rendered originals. The audit records conflicts in the source CSV, duration and ignition power rather than reconciling them silently. Original NASA source materials retain their original terms and attribution; see `NOTICE`.

## Execution status

The seven-code-cell notebook ran end-to-end in a standard CPU Colab runtime. The real Colab export passed15 local tests under Python3.12. The runtime was stopped. All148 checksummed release files and10 artifact files were downloaded from private Hugging Face revision60267afa086b32a73e9e66d90c214c1e7b5bccb2 and verified; a CPU inference call reproduced220.28979111936016 nominal mm. See `execution_status.json` for per-deliverable status and `storage_verification.json` for immutable-revision evidence. No improvement over the simple held-out baseline is claimed.

## License

This project is open source under the Apache License, Version 2.0.
The license covers the original project source code, notebooks, documentation,
and trained model artifacts contributed by efe-T. See the root `LICENSE` file
for the full terms and `NOTICE` for attribution and third-party materials.
Source code and model artifacts are publicly available in this repository.

Original NASA datasets, images, publications, and other third-party materials
retain their original terms and attribution; this project does not relicense them
or imply NASA endorsement.
