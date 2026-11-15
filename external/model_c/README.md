---
license: apache-2.0
library_name: scikit-learn
tags:
  - nasa
  - microgravity
  - smoke-detection
  - tabular-classification
---

# SAME / SAME-R model C

Project code and model artifacts are licensed under Apache License 2.0; see [LICENSE](LICENSE). NASA source datasets retain their CC0-1.0 designation. Third-party reference publications retain their own terms; see [NOTICE](NOTICE).

Predict whether source-recorded ISS detector scatter reaches **2.0 V**, from a tested smoke material and five controlled settings. This is an experimental **derived threshold-response label**, not a recorded operational alarm, time-to-alarm prediction, or fire-risk score. Only real PSI-102 and PSI-101 data are used.

The verified combined workbook supplies **17 SAME + 67 SAME-R primary heating records**, 61 above the threshold and 23 below. It also supplies 50 secondary-aging records retained only for measured/derived dashboard display. SAME-R has **67 heating runs**, correcting the proposed66.82 primary physical samples become81 conservative validation groups because the ambiguous secondary51a sample identity links two groups.

Grouped nested5-fold balanced accuracy is **0.870152 ± 0.076360**, compared with **0.500000 ± 0.000000** for the majority baseline; paired improvement **0.370152 ± 0.076360**. These are fold mean and sample SD, not confidence intervals. The estimate evaluates the entire inner model-selection procedure. Final export is a100-tree random forest with depth3, selected from a majority baseline, depth2 tree, regularized logistic regression and shallow forest. Comparison-only candidate results and all fold selections are in `reports/metrics.json`.

**Follow-up: material identity explains the headline score.** On the exact saved outer folds, a training-fold-only per-material majority baseline achieves **0.891342 ± 0.048823**, above the original nested-selection headline. The fixed forest achieves **0.900433 ± 0.056572**, with paired differences **[0, 0, 0, 0, 0.045455]** and mean difference **0.009091 ± 0.020328**. Its small numerical advantage is tied under the original one-fold-SD rule; it does not establish additional predictive value from the controlled conditions. The fixed-forest comparison is retrospective and is not a new selection-unbiased headline. The deployed model weights and entire inference bundle are unchanged. See [follow-up evaluation](reports/evaluation_followup.md) and [model card](MODEL_CARD.md).

Latest full suite: **44 passed locally and on a fresh Hub download**. [Hub-download test output](logs/pytest-hub-download.txt) is captured directly with `python -m pytest -q 2>&1 | tee logs/pytest-hub-download.txt`. The original notebook passed **36 tests in Colab**; the new evaluations have status `TESTED_LOCALLY`, not `COLAB_VERIFIED`. Execution status and storage verification are in [STATUS.json](STATUS.json); notebook outputs and logs are preserved. No GPU or paid API is needed.

## Reproduce

Use Python3.12 or3.13. From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m model_c.train
python -m pytest -q
```

For the evaluation-only follow-up, preserving deployed weights and original metrics:

```bash
python -m model_c.evaluate_followup
set -o pipefail
python -m pytest -q 2>&1 | tee logs/pytest-local.txt
```

Do not run `model_c.train` when reproducing this follow-up: that separate original command retrains and exports a model.

`python -m model_c.train` downloads metadata and pinned original files for both studies, verifies SHA256, preprocesses, evaluates every candidate in grouped nested CV, trains the selected model, exports it, performs scientific formula checks, and creates all dashboard rows. It uses cached originals when checksums match. A corrupt cache is rejected; remove the corrupt file and rerun to fetch it again. Upstream network access is required only when an original is absent. The resolver uses investigation version4, while the combined workbook's file version is1; it returns a temporary URL that is fetched separately and never persisted.

Open `notebooks/model_c.ipynb` in standard Google Colab and choose **Runtime → Run all**. The notebook embeds importable source and tests, installs pinned packages and downloads public NASA originals without Hub credentials. `notebooks/model_c_output.ipynb` is the executed notebook. Rebuild the embedded source after changing modules or tests with `python scripts/build_notebook.py`. `requirements-lock-local.txt` records the complete local package environment; the model's critical dependencies are pinned in its artifact directory.

## CPU inference contract

The only core dependency of inference is the standard exported scikit-learn pipeline and its pinned environment. The serialized pipeline contains fitted encoders, scalers, classifier parameters and class map0=below2V,1=atleast2V. `domain.json` contains training conditions, units, applicability, calibration choices and empirical OOD state. Checksums are checked before loading. Use only trusted joblib bundles.

```python
from model_c import predict_model_c

result = predict_model_c({
    "material": "Silicone",
    "airflow_cm_s": 8.0,
    "resistance_ratio": 1.327,
    "heating_s": 45.0,
    "aging_s": 720.0,
    "mixing_s": 0.0,
    "units": {"airflow_cm_s": "cm/s", "resistance_ratio": "1",
              "heating_s": "s", "aging_s": "s", "mixing_s": "s"}
})
```

This actual sample returns `predicted_alarm_level_reached=true`, `value_kind="predicted"`, `model_version="1.0.0"`, `ood=false`, `nearest_distance=0.0`, `ood_threshold=9.321957129180966`, nearest test`SAME:5`, and `uncertainty=null`. The full output also includes the applicable materials, ranges, campaigns, target definition, OOD reason and interpretation. Full request/response: `reports/sample_inference.json`.

| Field | Type | Unit | Accepted range/category |
|---|---|---|---|
| material | string | category | Kapton, Lampwick, Pyrell, Silicone, Teflon |
| airflow_cm_s | finite number | cm/s |0–8.1|
| resistance_ratio | finite number |1|1.22–1.48|
| heating_s | finite number |s|10–120|
| aging_s | finite number |s|1–720; programmed primary aging, not net age|
| mixing_s | finite number |s|0–8|
| units | exact object shown above | — | no implicit conversions |

Missing/extra fields, invalid numbers, unseen materials, wrong units and out-of-range numbers raise `ValueError`. Accepted numerical combinations can still be OOD. Compute Euclidean distance after dividing controls by population SD, searching only the same material. The threshold is the maximum training-condition distance to its nearest **different-group**, same-material condition. This is a coverage heuristic, not a calibrated safety boundary. `reports/ood_example.json` proves accepted OOD behavior: Kapton at0cm/s,ratio1.22,heat10s,age1s,mix0s has distance10.029009>9.321957. Sparse experimental coverage makes this threshold permissive; an in-domain result is not proof of physical generalization.

For notebook-free use outside this repository, copy only `artifacts/model_c`, install its requirements, place its `inference.py` on your Python path and set:

```bash
export MODEL_C_ARTIFACT=/absolute/path/to/artifacts/model_c
```

Then `from inference import predict_model_c` works without training/acquisition modules. Inference does not need openpyxl, Colab, notebook packages or NASA access. A clean-process round-trip is recorded in the storage verification log.

## Dashboard integration

Feature: **“Did comparable experimental smoke reach the ISS alarm level?”** Let users select a tested material and settings; show the predicted threshold class and domain flag beside the source-recorded scatter and derived threshold response of the nearest experiment. Label units and value kinds visibly. Render `data/processed/dashboard_table.csv` directly for observed conditions without a model call.

The table has134 source material-smoke observations. Measured voltages (`signal_kind=measured`), deterministic threshold labels (`derived_label_kind=derived`), final fitted predictions (`prediction_value_kind=predicted`), and nested held-out predictions (`oof_predicted`,`oof_fold`) remain separate. Final fitted predictions on training rows are explicitly marked in-sample. Secondary-aging rows carry measured/derived observations and no fabricated model prediction. Raw numeric high-end signals retain unresolved saturation status and must not be displayed as precise unconstrained concentration estimates.

Place this panel beside model_a's PMMA flame-spread rate and model_b's Saffire video progression. The datasets represent different experiments; they do not form a synchronized fire trajectory or a combined danger score.

Prefer the measured-only companion `data/processed/dashboard_measured_only.csv`: one row per material with primary-run count, conservative group count, observed fraction reaching2V, source test IDs, campaigns, and tested ranges/units for every control. Fractions are9/21 for Kapton,4/15 for Teflon,17/17 for Lampwick,12/12 for Pyrell and19/19 for Silicone. These are descriptive fractions of observed primary runs, not predicted alarm probabilities. Secondary-aging readings are excluded from the denominators; reburn runs are included as runs and identified through group counts.

## Validation and scientific checks

All splits use connected sample/run groups. Inner4-fold GroupKFold chooses fixed candidates; outer5-fold GroupKFold estimates selection performance. The one-SD tie band is the best inner candidate's fold SD, with fixed simplicity order majority→depth2 tree→logistic→forest. Every tried candidate and per-fold paired baseline difference is recorded; no model was added after error inspection. Per-material and campaign stress results, class balances, precision/recall/F1, confusion matrices, average-precision PR-AUC, failures and figures are in `reports/evaluation.md` and `reports/metrics.json`.

Cross-campaign balanced accuracy: SAME→SAME-R **0.628655** on55 supported-material rows (12 Pyrell rows excluded); SAME-R→SAME **0.846154** on17 rows. These stress tests show substantial shift and are separate from the pooled nested estimate. Single-class material strata have null balanced accuracy and PR-AUC. No uncertainty interval or calibrated alarm probability is supplied.

The aggregate score hides weak performance on the difficult materials: Kapton held-out balanced accuracy is0.513889 with positive recall0.111111; Teflon balanced accuracy is0.500000 with positive recall0. These failures prevent reliable material-specific alarm-coverage prediction. The measured/derived experimental records should remain the primary evidence shown by the dashboard.

The follow-up fits one fixed, untuned numeric-control logistic model per material solely for diagnostic grouped CV, without exporting it. Kapton has21 runs/19 groups, with12 below2V runs in10 groups and9 at/above2V runs in9 groups. Teflon has15 runs/15 groups, with11 below and4 at/above2V, each in separate groups. Both meet the minimum of3 groups per class. Three-fold stratified grouped OOF balanced accuracy is0.583333 for Kapton and0.738636 for Teflon. These are post-hoc diagnostics, not new deployment claims. Measured signal against all five controls is plotted in `reports/kapton_conditions.png` and `reports/teflon_conditions.png`; constant controls remain explicitly visible.

Recomputed1000*M1/M0 matches131 source-reported count diameters to maximum absolute error2.22e-16μm. The published2012 Table1 provides a second, limited formula check:9 rows agree within propagated source rounding; **unaged Teflon fails**. Published count/mass diameters are0.101/0.170μm, but its printed geometric pair implies0.110450/0.205367μm. The values were visually rechecked; no undocumented correction or averaging explanation was applied. This is an unresolved source-table inconsistency and does not validate classifier predictions. See `reports/external_checks.csv` and `data/references/teflon_table1_check.json`.

## Layout and trade-offs

- `model_c/data.py`: original-file acquisition, explicit source statuses, conservative groups and deterministic preprocessing.
- `model_c/train.py`: fixed candidates, nested CV, scientific checks, standard joblib export and precomputed dashboard table.
- `model_c/inference.py`: strict CPU input validation, checksum verification and same-material OOD distance. No training dependency.
- `data/raw`, `data/references`: original files, manifests and visual reference checks.
- `data/processed`: observations, eligible training rows, dictionary, harmonization map, correlations and dashboard table.
- `reports`: dataset/task audit, executed evaluation, machine-readable metrics, failures, external checks and figures.
- `notebooks`: runnable self-contained notebook and executed outputs.
- `model_c/evaluate_followup.py`: material-only baseline on frozen nested folds, disposable CV fits, measured-only summary and plots; never writes model weights.
- `tests`:44 tests covering the original pipeline plus baseline isolation, exact fold reuse, unchanged artifacts, class-group gating and measured-only summaries.

Using the authors' common reduced workbook avoids reconstructing the full instrument chain during the hackathon. AW saturation preserves a binary above2V label but blocks honest unrestricted analog regression. The five controls remain inputs because they are programmed, while measured moments and detector signals never enter the condition model. The82-sample/81-group distinction deliberately loses one validation group to protect against an ambiguous source identity. Campaign is excluded as a predictive feature so the interface expresses experimental settings; campaign transfer is measured separately.

The audit did not decode all6.3GB of SAME-R data or every original raw series, reconstruct per-row LOD/saturation/electronic resolution, establish an exact Shuttle threshold, or find the requested separate2021 report. The2018 manuscript's PMC availability date is2021. The challenge page could not be independently fetched. No new-material, flaming-fire, transport, alarm-time, operational ISS or certification claim is supported.

Storage: public [efe-T/nasa-same-model-c](https://huggingface.co/efe-T/nasa-same-model-c). The release is versioned and checksummed; storage verification downloads the uploaded commit and checks every release file plus one standalone inference call. See `logs/storage_verification.json` and `STATUS.json` for actual execution evidence.
