---
language: en
library_name: sklearn
pipeline_tag: tabular-regression
tags:
- scientific-machine-learning
- nasa
- microgravity
- small-data
- random-forest
---
# NASA BASS-II model_a

Exploratory CPU model for **source-reported PMMA slab flame-spread rate (mm/s)** under BASS-II opposed-flow microgravity conditions. Trained and evaluated in **Google Colab CPU through the Colab CLI**, with end-to-end notebook and export/load tests executed. This model is unsuitable for certification, operational fire-safety decisions, extinction claims, or arbitrary hazard scores.

## Evidence and task

NASA Table5.1, printed page57/PDF page65, has20 PMMA slab burns; M6/M12 say `Not tracked`. The remaining39 airflow segments belong to18 distinct physical samples, verified against the PSI experiment CSV. Every table cell was checked against the rendered PDF. Reported rates were derived by the source authors from video position/time slopes; this project does not claim to have re-tracked the videos. Segment expansion, units and provenance are deterministic. No synthetic training data.

Inputs: `thickness_mm`, `width_cm`, `velocity_cm_s`, `initial_o2_vol_pct`. Outputs: spread estimate inmm/s, model version, domain and warnings. Material is restricted to clear-cast PMMA slabs. Burning-side count, final oxygen, and burn duration are excluded. Initial oxygen is a pre-burn measured proxy for changing oxygen during the burn; unmodeled burning geometry/history confounds the estimates.

## Validation

The initial5candidate comparison was expanded to7 after inspecting failures. Final nestedCV does not remove this researcher adaptivity; all results remain exploratory. Five outer grouped folds by physical sample; four inner grouped folds choose models independently inside each outer training fold. Equal total training weight per experiment. Fixed candidates, no hyperparameter search. Primary score is experiment-macro MAE; secondary RMSE/R² use segment rows within each fold. Entries below are fold mean±population standard deviation. Candidate rows share the folds that select the final model, so they are comparison results, not independent confirmation of that selection. `nested_selection` estimates the selection procedure; no untouched final test exists.

| Candidate | MAE (mm/s) | RMSE (mm/s) | R² |
|---|---|---|---|
| extra_trees | 0.016862 ± 0.005360 | 0.020700 ± 0.008301 | 0.036937 ± 0.557532 |
| hist_gradient_boosting | 0.019006 ± 0.003805 | 0.025866 ± 0.010040 | -0.240459 ± 0.437544 |
| inverse_thickness_ridge | 0.015538 ± 0.006265 | 0.020783 ± 0.010625 | -0.068609 ± 1.069377 |
| mean | 0.021566 ± 0.007809 | 0.028435 ± 0.013943 | -0.331376 ± 0.328203 |
| nested_selection | 0.018556 ± 0.005184 | 0.026734 ± 0.010710 | -0.443989 ± 0.953252 |
| random_forest | 0.014971 ± 0.003429 | 0.019721 ± 0.007136 | 0.217304 ± 0.333606 |
| rbf_svr | 0.016651 ± 0.006614 | 0.025476 ± 0.011688 | -0.353513 ± 1.071644 |
| ridge | 0.017333 ± 0.004978 | 0.025616 ± 0.010743 | -0.226101 ± 0.439281 |

The exported full-data model is random forest:200 trees, min_samples_leaf3, random_state42, n_jobs2. Objective: squared-error tree splits; selected by grouped MAE and one-fold-std/stability rule. Negative mean nested R² and only18 samples substantially limit generalization. No calibrated uncertainty intervals or significance claim.

## Load and predict

Download this repository, then run from its root. The shipped JSON forest needs only Python standard library (no notebook or ML dependencies):

```bash
python -c "import json; from model_a.inference import predict_model_a; print(predict_model_a(json.load(open('artifacts/model_a_v1/sample_request.json'))))"
```

The portable model.json contains fitted scaler and forest arrays; config contains bounds and observed combinations. Standard-library inference reproduces float32 tree evaluation and is checked against sklearn on all39 source rows. The original complete joblib pipeline is retained for audit and optional pinned-package loading. Loading requires no training module. Only load pickle/joblib files from trusted sources.

Separate interpreters executed this demo in Colab and locally outside Colab without importing any ML packages; see reports/local_inference.json. Tests: see `reports/test_results.txt`. Missing/extra fields, nonfinite values, wrong units, unsupported material, and out-of-range numbers raise ValueError. Distance-based coverage is `TESTED_LOCALLY`: ood.json stores39 unique FEATURES conditions from data/processed/segments.csv, experiment/group IDs and population training mean/std (ddof=0). Each reference distance is the standardized Euclidean distance to the nearest condition from a DIFFERENT group_id; the threshold is the maximum reference distance. Inference computes nearest_distance to any training condition and returns out_of_distribution = nearest_distance > ood_threshold, plus nearest_experiment_id. The coverage warning appears only when OOD is true. The threshold uses only18 groups, so it is a rough coverage check, not a calibrated novelty probability or predictive uncertainty interval. Passing the check does not establish reliable predictions. No weights or metrics changed and no retraining occurred. Rebuild with python -m model_a.build_ood; run eight local regression tests with python -m unittest discover -s tests -p test_ood.py -v. See reports/ood_distance_validation.json and reports/ood_fix_tests.txt; the executed Colab notebook records the original training run. Sample JSON request/response is in `artifacts/model_a_v1/`.

## Reproduce

```bash
python -m model_a.data
python -m model_a.train
python -m pytest -q tests
```

Raw source files download from official NASA endpoints and are checksum-verified. Or upload `model_a_source.zip` to a standard Colab runtime and run all cells in `notebooks/model_a.ipynb`. The executed notebook is `notebooks/model_a_output.ipynb`. Reports and all candidate fold metrics, OOF predictions, failure cases, sensitivity relationships and processed observations are included.

## Sources and limits

- [NASA BASS-II Summary Report](https://ntrs.nasa.gov/citations/20210011385), Table5.1 printedp57, section5 and AppendixA.4.
- [NASA PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25), study version4; DOI10.60555/4qc4-de67. PSI metadata lists CC0. Code and weights do not imply NASA endorsement.

Source discrepancies are preserved and documented: M8 plotted10cm/s slope differs from its table rate; table widths1.2/2.2cm differ from nominal prose1/2cm. Widths and rates use the audited table, not invented corrections. No extrapolation to other materials, gravity levels, geometries, or full-scale spacecraft fires. No causal intervention guarantees or extinction predictions.
