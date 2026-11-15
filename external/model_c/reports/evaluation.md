# Model C evaluation

Executed environment: Google Colab CPU. Seed 2026. Versions: `{"python": "3.13.18", "sklearn": "1.6.1", "numpy": "2.2.6", "pandas": "2.2.3", "joblib": "1.4.2"}`.

84 primary rows; 81 conservative validation groups. Physical primary samples total82, but ambiguous aged51a merges an additional group to prevent leakage.

Headline selection-unbiased estimate: grouped nested5-fold balanced accuracy **0.870152 ± 0.076360** (sample fold standard deviation). Baseline **0.500000 ± 0.000000**. Paired difference **0.370152 ± 0.076360**. This estimates the entire selection procedure, not a separately held-out final fitted forest.

Outer folds remain untouched by candidate selection; inner4-fold GroupKFold compares fixed majority, depth2 tree, C1 logistic and100-tree depth3 forest. No post-error candidates were added. Equal fixed-configuration budget, zero hyperparameter searches. Candidates within the best candidate's one-fold SD are treated as tied; choose in simplicity order majority→tree→logistic→forest. The architecture order was fixed before inspecting validation scores.

| Outer fold | Selected | Model balanced accuracy | Baseline | Paired difference |
|---|---|---:|---:|---:|
|0|tree_depth2|0.833333|0.500000|0.333333|
|1|forest_depth3|0.875000|0.500000|0.375000|
|2|tree_depth2|0.833333|0.500000|0.333333|
|3|tree_depth2|1.000000|0.500000|0.500000|
|4|logistic|0.809091|0.500000|0.309091|

## Candidate comparison only

These full-data inner folds are selection results, not the headline validation estimate.

| Candidate | Mean balanced accuracy | Fold SD |
|---|---:|---:|
|majority|0.500000|0.000000|
|tree_depth2|0.782344|0.071748|
|logistic|0.845365|0.099712|
|forest_depth3|0.891719|0.045925|

Final export: **forest_depth3**. Objective: predict a binary derived2V scatter threshold using categorical material and five controlled settings. Logistic minimizes regularized weighted log loss; trees/forest use weighted Gini splits. Primary metric balanced accuracy.

## Pooled outer predictions

`{"n": 84, "positive": 61, "negative": 23, "precision": 0.9795918367346939, "recall": 0.7868852459016393, "f1": 0.8727272727272727, "balanced_accuracy": 0.8717034925160371, "confusion_matrix": [[22, 1], [13, 48]], "pr_auc_average_precision": 0.9726305651119029}`

## Per material

Single-class strata have undefined balanced accuracy and PR-AUC (null).

| Material | n | Positives | Precision | Recall | F1 | Balanced accuracy |
|---|---:|---:|---:|---:|---:|---:|
|Kapton|21|9|0.5000|0.1111|0.1818|0.5138888888888888|
|Lampwick|17|17|1.0000|1.0000|1.0000|None|
|Pyrell|12|12|1.0000|1.0000|1.0000|None|
|Silicone|19|19|1.0000|0.9474|0.9730|None|
|Teflon|15|4|0.0000|0.0000|0.0000|0.5|

## Campaign shift

Train-only selection repeated in each source campaign. Test uses only materials seen in source. Pyrell is excluded from SAME→SAME-R. These are stress tests, not nested headline scores.

- SAME -> other: `{"selected": "tree_depth2", "n_train": 17, "n_test_supported_materials": 55, "excluded_unseen_material_rows": 12, "scores": {"n": 55, "positive": 36, "negative": 19, "precision": 0.7272727272727273, "recall": 0.8888888888888888, "f1": 0.8, "balanced_accuracy": 0.6286549707602339, "confusion_matrix": [[7, 12], [4, 32]], "pr_auc_average_precision": 0.7191919191919192}, "scope": "Domain-shift stress test only; material intersection; not final model performance."}`
- SAME-R -> other: `{"selected": "forest_depth3", "n_train": 67, "n_test_supported_materials": 17, "excluded_unseen_material_rows": 0, "scores": {"n": 17, "positive": 13, "negative": 4, "precision": 1.0, "recall": 0.6923076923076923, "f1": 0.8181818181818182, "balanced_accuracy": 0.8461538461538461, "confusion_matrix": [[4, 0], [4, 9]], "pr_auc_average_precision": 0.9819004524886878}, "scope": "Domain-shift stress test only; material intersection; not final model performance."}`

Leave-one-material-out fixed-logistic diagnostic results are in metrics.json. Inference rejects unseen materials; this diagnostic does not support deployment on held-out materials.

## External checks and errors

Source-workbook moment check: n=131; max absolute diameter error=2.22044604925e-16 μm for1000*M1/M0. No lognormal assumption for this ratio.

external_checks.csv compares all10 visually verified Table1 rows from [NTRS20130000422](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf), p7. It recomputes count and mass-equivalent diameters from rounded geometric mean and geometric SD, assuming lognormal sizes. This is algebraic/rounding validation; those table rows cannot be treated as independent predictive validation or matched to exact raw run IDs.

External check **fails for unaged Teflon**: printed Dg=0.081 μm and sigma=2.198 imply count0.110450225 μm and mass0.205366583 μm, versus source0.101 and0.170 μm. The discrepancy exceeds ±0.0005 rounding propagated through all inputs and outputs. The original table was visually rechecked. No column-averaging explanation is documented: unresolved source-table inconsistency, not repaired data. This check is independent of the classifier labels. All numerical pairs and rounding intervals are in external_checks.csv.

failure_cases.csv contains every nested OOF error with source rows and controls. validation.png shows predicted vs derived reference classes and measured scatter vs airflow. The scatter plot is descriptive, not causal. No uncertainty interval or calibrated probability is claimed. Fold SD describes variability, not a confidence interval.

## Limits

Only84 analyzed primary records, uneven material/condition/campaign coverage,81 conservative validation groups.82 primary physical samples collapse to81 because the ambiguous aged51aK02 record is conservatively connected to51K01/61K02. Retaining reburns reflects experimental history that controls do not fully capture. SAME-R source quality flags are blank/unknown. AW retains source numeric voltages with unresolved per-row saturation and LOD; only threshold exceedance is modeled. Rt/R0 does not uniquely determine actual sample temperature. No ambient spacecraft generalization, time-to-alarm, flame/fatality risk, detector certification, or unseen-material prediction. Full raw instrument calibration reconstruction was not performed; source-reduced common channel is used. No standalone2021 report verified; exact challenge page unavailable during audit.

<!-- evaluation-followup -->

Status: TESTED_LOCALLY. Evaluation and reporting only; deployed weights and inference bundle are byte-for-byte unchanged.

The original0.870152 headline evaluates nested model selection, not a fixed forest: outer folds selected tree, forest, tree, tree and logistic. We retain it and compare a fixed forest and a training-fold-only material-majority baseline on exactly the saved outer groups. This is a post-hoc diagnostic, not a fresh independent test or a new selection-unbiased estimate. The baseline is also evaluated inside the same4-fold inner splits, without changing original selections. Majority ties choose0; unseen material falls back to training-global majority.

| Method | Mean balanced accuracy | Fold SD |
|---|---:|---:|
|material_majority|0.891342|0.048823|
|fixed_forest|0.900433|0.056572|
|original_nested_selection|0.870152|0.076360|

| Fold | Material majority | Fixed forest | Forest minus material majority | Original nested selection minus material majority |
|---|---:|---:|---:|---:|
|0|0.875000|0.875000|0.000000|-0.041667|
|1|0.875000|0.875000|0.000000|0.000000|
|2|0.833333|0.833333|0.000000|0.000000|
|3|0.964286|0.964286|0.000000|0.035714|
|4|0.909091|0.954545|0.045455|-0.100000|

Forest-minus-material-majority mean±SD: **0.009091 ± 0.020328**. This is descriptive fold variability, not a confidence interval.

The fixed forest has a slightly higher numerical mean than material majority, but the advantage is smaller than one forest fold SD, so they are tied under the original evaluation rule. Four of five paired differences are zero. **Material identity explains the headline score**: the material-only baseline exceeds the original nested-selection headline. There is no demonstrated improvement from controlled conditions beyond that baseline; the small retrospective forest advantage is not an independent generalization claim.

## Kapton and Teflon

Counts below use primary heating runs only. Groups retain the original conservative connections, including the ambiguous51a linkage. A group can appear in both class counts if it contains conflicting outcomes; class-group counts need not sum to total groups. Both classes require at least3 groups before fitting an untuned three-fold stratified grouped logistic diagnostic on numeric controls only.

| Material | Runs | Groups | Below2V runs/groups | Atleast2V runs/groups | Logistic pooled OOF balanced accuracy |
|---|---:|---:|---|---|---:|
|Kapton|21|19|12/10|9/9|0.5833333333333334|
|Teflon|15|15|11/11|4/4|0.7386363636363636|

### Kapton

`{"n_runs": 21, "n_groups": 19, "class_balance": {"0": {"runs": 12, "groups": 10}, "1": {"runs": 9, "groups": 9}}, "class_definition": "0=ISS scatter below2V,1=atleast2V", "features": ["airflow_cm_s", "resistance_ratio", "heating_s", "aging_s", "mixing_s"], "scope": "Post-hoc within-material diagnostic; fixed C1 balanced logistic; no model export or deployment claim", "status": "TESTED_LOCALLY", "folds": [{"fold": 0, "train_groups": ["group-009", "group-011", "group-015", "group-028", "group-058", "group-065", "group-085", "group-095", "group-098", "group-112", "group-114", "group-126", "group-131"], "test_groups": ["group-023", "group-045", "group-061", "group-069", "group-096", "group-133"], "model": {"n": 6, "positive": 2, "negative": 4, "precision": 0.0, "recall": 0.0, "f1": 0.0, "balanced_accuracy": 0.375, "confusion_matrix": [[3, 1], [2, 0]], "pr_auc_average_precision": 0.26666666666666666}, "majority": {"n": 6, "positive": 2, "negative": 4, "precision": 0.0, "recall": 0.0, "f1": 0.0, "balanced_accuracy": 0.5, "confusion_matrix": [[4, 0], [2, 0]], "pr_auc_average_precision": null}}, {"fold": 1, "train_groups": ["group-009", "group-011", "group-015", "group-023", "group-045", "group-058", "group-061", "group-069", "group-095", "group-096", "group-114", "group-131", "group-133"], "test_groups": ["group-028", "group-065", "group-085", "group-098", "group-112", "group-126"], "model": {"n": 8, "positive": 2, "negative": 6, "precision": 1.0, "recall": 1.0, "f1": 1.0, "balanced_accuracy": 1.0, "confusion_matrix": [[6, 0], [0, 2]], "pr_auc_average_precision": 1.0}, "majority": {"n": 8, "positive": 2, "negative": 6, "precision": 0.25, "recall": 1.0, "f1": 0.4, "balanced_accuracy": 0.5, "confusion_matrix": [[0, 6], [0, 2]], "pr_auc_average_precision": null}}, {"fold": 2, "train_groups": ["group-023", "group-028", "group-045", "group-061", "group-065", "group-069", "group-085", "group-096", "group-098", "group-112", "group-126", "group-133"], "test_groups": ["group-009", "group-011", "group-015", "group-058", "group-095", "group-114", "group-131"], "model": {"n": 7, "positive": 5, "negative": 2, "precision": 0.5, "recall": 0.2, "f1": 0.2857142857142857, "balanced_accuracy": 0.35, "confusion_matrix": [[1, 1], [4, 1]], "pr_auc_average_precision": 0.81}, "majority": {"n": 7, "positive": 5, "negative": 2, "precision": 0.0, "recall": 0.0, "f1": 0.0, "balanced_accuracy": 0.5, "confusion_matrix": [[2, 0], [5, 0]], "pr_auc_average_precision": null}}], "pooled_oof": {"n": 21, "positive": 9, "negative": 12, "precision": 0.6, "recall": 0.3333333333333333, "f1": 0.42857142857142855, "balanced_accuracy": 0.5833333333333334, "confusion_matrix": [[10, 2], [6, 3]], "pr_auc_average_precision": 0.4586404054799308}, "pooled_majority": {"n": 21, "positive": 9, "negative": 12, "precision": 0.25, "recall": 0.2222222222222222, "f1": 0.23529411764705882, "balanced_accuracy": 0.3611111111111111, "confusion_matrix": [[6, 6], [7, 2]], "pr_auc_average_precision": null}, "fold_balanced_accuracy": {"values": [0.375, 1.0, 0.35], "mean": 0.5750000000000001, "std": 0.36827299656640594}, "undefined_fold_policy": "Single-class test folds have null balanced accuracy; excluded from fold mean, included in pooled OOF."}`

![Kapton measured signal against five controls](kapton_conditions.png)

### Teflon

`{"n_runs": 15, "n_groups": 15, "class_balance": {"0": {"runs": 11, "groups": 11}, "1": {"runs": 4, "groups": 4}}, "class_definition": "0=ISS scatter below2V,1=atleast2V", "features": ["airflow_cm_s", "resistance_ratio", "heating_s", "aging_s", "mixing_s"], "scope": "Post-hoc within-material diagnostic; fixed C1 balanced logistic; no model export or deployment claim", "status": "TESTED_LOCALLY", "folds": [{"fold": 0, "train_groups": ["group-004", "group-008", "group-019", "group-035", "group-037", "group-073", "group-077", "group-091", "group-120", "group-130"], "test_groups": ["group-005", "group-027", "group-057", "group-081", "group-110"], "model": {"n": 5, "positive": 2, "negative": 3, "precision": 0.5, "recall": 1.0, "f1": 0.6666666666666666, "balanced_accuracy": 0.6666666666666666, "confusion_matrix": [[1, 2], [0, 2]], "pr_auc_average_precision": 1.0}, "majority": {"n": 5, "positive": 2, "negative": 3, "precision": 0.0, "recall": 0.0, "f1": 0.0, "balanced_accuracy": 0.5, "confusion_matrix": [[3, 0], [2, 0]], "pr_auc_average_precision": null}}, {"fold": 1, "train_groups": ["group-004", "group-005", "group-027", "group-035", "group-037", "group-057", "group-077", "group-081", "group-110", "group-130"], "test_groups": ["group-008", "group-019", "group-073", "group-091", "group-120"], "model": {"n": 5, "positive": 0, "negative": 5, "precision": 0.0, "recall": 0.0, "f1": 0.0, "balanced_accuracy": null, "confusion_matrix": [[4, 1], [0, 0]], "pr_auc_average_precision": null}, "majority": {"n": 5, "positive": 0, "negative": 5, "precision": 0.0, "recall": 0.0, "f1": 0.0, "balanced_accuracy": null, "confusion_matrix": [[5, 0], [0, 0]], "pr_auc_average_precision": null}}, {"fold": 2, "train_groups": ["group-005", "group-008", "group-019", "group-027", "group-057", "group-073", "group-081", "group-091", "group-110", "group-120"], "test_groups": ["group-004", "group-035", "group-037", "group-077", "group-130"], "model": {"n": 5, "positive": 2, "negative": 3, "precision": 1.0, "recall": 0.5, "f1": 0.6666666666666666, "balanced_accuracy": 0.75, "confusion_matrix": [[3, 0], [1, 1]], "pr_auc_average_precision": 1.0}, "majority": {"n": 5, "positive": 2, "negative": 3, "precision": 0.0, "recall": 0.0, "f1": 0.0, "balanced_accuracy": 0.5, "confusion_matrix": [[3, 0], [2, 0]], "pr_auc_average_precision": null}}], "pooled_oof": {"n": 15, "positive": 4, "negative": 11, "precision": 0.5, "recall": 0.75, "f1": 0.6, "balanced_accuracy": 0.7386363636363636, "confusion_matrix": [[8, 3], [1, 3]], "pr_auc_average_precision": 0.775}, "pooled_majority": {"n": 15, "positive": 4, "negative": 11, "precision": 0.0, "recall": 0.0, "f1": 0.0, "balanced_accuracy": 0.5, "confusion_matrix": [[11, 0], [4, 0]], "pr_auc_average_precision": null}, "fold_balanced_accuracy": {"values": [0.6666666666666666, 0.75], "mean": 0.7083333333333333, "std": 0.05892556509887899}, "undefined_fold_policy": "Single-class test folds have null balanced accuracy; excluded from fold mean, included in pooled OOF."}`

![Teflon measured signal against five controls](teflon_conditions.png)

No fitted within-material models are serialized or used by inference. These are small, post-hoc condition diagnostics. Single-class test folds receive null balanced accuracy; pooled OOF scores retain all runs. Scatter relationships are descriptive and confounded by the experimental test matrix, campaign and reused samples; they are not causal effects.

## Measured-only dashboard

`data/processed/dashboard_measured_only.csv` contains one row per material: primary-run counts, groups, count and fraction reaching2V, source test IDs, campaign coverage and min/max of every controlled condition with units. It contains no model prediction or synthetic observations. Fractions and ranges are deterministic derivations from measured/source-reported data, not estimated detection probabilities. Reburn runs count as runs, and group counts expose dependence. Constant controls appear as identical lower/upper limits in the figures.

Reproduce without retraining or changing weights: `python -m model_c.evaluate_followup`. The original notebook and model-training results retain their historical Colab status; this addendum was executed locally. `reports/followup_metrics.json` includes all fold memberships, inner baseline scores, OOF metrics, source hashes and the protected deployed-artifact hashes.
