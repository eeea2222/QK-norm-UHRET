"""Grouped nested selection, scientific checks, standard export and dashboard rows."""
import argparse
import hashlib
import itertools
import json
import os
import platform
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, balanced_accuracy_score, confusion_matrix,
                             f1_score, precision_score, recall_score)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree

from .data import acquire, preprocess, sha, WORKBOOK_SHA
from .inference import FEATURES, NUMERIC, UNITS, predict_model_c

SEED = 2026


def candidates():
    prep = ColumnTransformer([("material", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["material"]), ("controls", StandardScaler(), NUMERIC)])
    models = {
        "majority": DummyClassifier(strategy="most_frequent"),
        "tree_depth2": DecisionTreeClassifier(max_depth=2, min_samples_leaf=3, class_weight="balanced", random_state=SEED),
        "logistic": LogisticRegression(C=1, class_weight="balanced", max_iter=3000, random_state=SEED),
        "forest_depth3": RandomForestClassifier(n_estimators=100, max_depth=3, min_samples_leaf=3, class_weight="balanced", random_state=SEED, n_jobs=1),
    }
    return {name: make_pipeline(clone(prep), model) for name, model in models.items()}


def scores(y, pred, probability=None):
    y = np.asarray(y, dtype=int)
    result = {"n": len(y), "positive": int(y.sum()), "negative": int(len(y) - y.sum()),
              "precision": float(precision_score(y, pred, zero_division=0)), "recall": float(recall_score(y, pred, zero_division=0)),
              "f1": float(f1_score(y, pred, zero_division=0)), "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None,
              "confusion_matrix": confusion_matrix(y, pred, labels=[0, 1]).tolist()}
    result["pr_auc_average_precision"] = float(average_precision_score(y, probability)) if probability is not None and len(np.unique(y)) == 2 else None
    return result


def proba(model, x):
    probabilities = model.predict_proba(x)
    classes = model.classes_
    if 1 not in classes:
        return np.zeros(len(x))
    return probabilities[:, list(classes).index(1)]


def select(x, y, groups):
    results = {}
    splits = list(GroupKFold(n_splits=min(4, len(set(groups)))).split(x, y, groups))
    for name, estimator in candidates().items():
        values = []
        for train, test in splits:
            fitted = clone(estimator).fit(x.iloc[train], y.iloc[train])
            value = scores(y.iloc[test], fitted.predict(x.iloc[test]))["balanced_accuracy"]
            if value is not None:
                values.append(value)
        results[name] = {"fold_scores": values, "mean": float(np.mean(values)), "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0}
    best = max(results, key=lambda name: results[name]["mean"])
    # A one-fold-standard-deviation tie is intentionally conservative at small n.
    cutoff = results[best]["mean"] - results[best]["std"]
    selected = next(name for name in candidates() if results[name]["mean"] >= cutoff)
    return selected, results


def domain_for(df):
    scale = df[NUMERIC].std(ddof=0).to_numpy()
    scale[scale == 0] = 1
    maximum = 0.0
    for material, part in df.groupby("material"):
        arr = part[NUMERIC].to_numpy() / scale
        group = part.group_id.to_numpy()
        for i in range(len(part)):
            other = group != group[i]
            if not other.any():
                raise ValueError(f"No independent same-material neighbor for {material}")
            maximum = max(maximum, float(np.linalg.norm(arr[other] - arr[i], axis=1).min()))
    return {"model_version": "1.0.0", "materials": sorted(df.material.unique()), "campaigns": sorted(df.campaign.unique()),
            "ranges": {k: [float(df[k].min()), float(df[k].max())] for k in NUMERIC},
            "scale": scale.tolist(), "ood_threshold": maximum,
            "ood_definition": "Maximum same-material standardized nearest condition distance from a different training group; population SD of numeric controls.",
            "training_conditions": df[FEATURES + ["group_id", "test_id", "campaign"]].to_dict("records"),
            "target": "Recorded ISS scatter >=2 V, derived label; not reported real alarm or alarm timing",
            "units": UNITS, "source_workbook_sha256": WORKBOOK_SHA,
            "uncertainty": "Not estimated; sample size and adaptive selection do not support calibrated prediction intervals.",
            "calibration": "No raw-signal calibration applied. Uses source author-combined AW voltage channel and Figure9 threshold.",
            "assumptions": ["Common ISS scatter voltage channel and alarm reference across source-combined campaigns", "Saturated signals above2 V establish only threshold exceedance"],
            "versions": {"python": platform.python_version(), "sklearn": sklearn.__version__, "numpy": np.__version__, "pandas": pd.__version__, "joblib": joblib.__version__}}


def scientific_checks(observations, output):
    valid = observations.dropna(subset=["derived_amd_um", "source_amd_um"])
    error = np.abs(valid.derived_amd_um - valid.source_amd_um)
    # Visually checked NTRS20130000422 Table1 p7. These are published calculations,
    # not independent observations; formula agreement checks transcription only.
    table = [("Kapton", "unaged", .042, .056, .101, 2.154), ("Kapton", "720s", .089, .109, .161, 1.872),
             ("Lampwick", "unaged", .090, .128, .258, 2.312), ("Lampwick", "720s", .229, .276, .398, 1.834),
             ("Silicone", "unaged", .128, .196, .465, 2.530), ("Silicone", "720s", .269, .355, .619, 2.108),
             ("Teflon", "unaged", .081, .101, .170, 2.198), ("Teflon", "720s", .070, .105, .232, 2.442),
             ("Pyrell", "unaged", .149, .204, .384, 2.211), ("Pyrell", "720s", .293, .359, .539, 1.892)]
    rows = []
    for material, state, dg, dc, dm, sg in table:
        derived_dc = dg * np.exp(.5 * np.log(sg) ** 2)
        derived_dm = dg * np.exp(1.5 * np.log(sg) ** 2)
        ranges = {}
        for label, coefficient, target in [("count", .5, dc), ("mass", 1.5, dm)]:
            lower = (dg-.0005)*np.exp(coefficient*np.log(sg-.0005)**2)
            upper = (dg+.0005)*np.exp(coefficient*np.log(sg+.0005)**2)
            ranges[label + "_rounding_lower_um"] = lower
            ranges[label + "_rounding_upper_um"] = upper
            ranges[label + "_rounding_overlap"] = bool(lower <= target+.0005 and upper >= target-.0005)
        agreement = all(ranges[k] for k in ["count_rounding_overlap", "mass_rounding_overlap"])
        rows.append({"material": material, "state": state, "source_count_um": dc, "calculated_count_um": derived_dc, "source_mass_um": dm, "calculated_mass_um": derived_dm, "absolute_count_error_um": abs(dc-derived_dc), "absolute_mass_error_um": abs(dm-derived_dm), **ranges, "agreement_status": "consistent_with_source_rounding" if agreement else "unresolved_source_table_inconsistency", "provenance": "source_reported", "calculation_kind": "derived", "assumptions": "lognormal size distribution; each three-decimal input/output rounding ±0.0005, not instrument uncertainty", "source": "NTRS20130000422 Table1 PDFp7"})
    pd.DataFrame(rows).to_csv(output / "external_checks.csv", index=False)
    return {"workbook_moment_ratio_n": len(valid), "workbook_moment_ratio_max_absolute_error_um": float(error.max()), "external_checks": rows,
            "validation_scope": "Formula consistency only, not independent predictive validation. No per-run publication table of alarm ground truth found."}


def run(root="."):
    root = Path(root)
    output = root / "reports"
    output.mkdir(exist_ok=True)
    observations = preprocess(acquire(root), root / "data/processed")
    df = observations[observations.training_eligible].reset_index(drop=True)
    x, y, groups = df[FEATURES], df.alarm_level_reached.astype(int), df.group_id
    folds, predictions = [], []
    outer = list(GroupKFold(n_splits=5).split(x, y, groups))
    all_oof = np.empty(len(df), dtype=int)
    all_baseline = np.empty(len(df), dtype=int)
    all_probability = np.empty(len(df))
    for fold, (train, test) in enumerate(outer):
        assert not set(groups.iloc[train]) & set(groups.iloc[test])
        chosen, comparison = select(x.iloc[train].reset_index(drop=True), y.iloc[train].reset_index(drop=True), groups.iloc[train].reset_index(drop=True))
        estimator = candidates()[chosen].fit(x.iloc[train], y.iloc[train])
        baseline = candidates()["majority"].fit(x.iloc[train], y.iloc[train])
        pred, base, prob = estimator.predict(x.iloc[test]), baseline.predict(x.iloc[test]), proba(estimator, x.iloc[test])
        all_oof[test], all_baseline[test], all_probability[test] = pred, base, prob
        model_score, base_score = scores(y.iloc[test], pred, prob), scores(y.iloc[test], base, proba(baseline, x.iloc[test]))
        folds.append({"fold": fold, "train_groups": sorted(set(groups.iloc[train])), "test_groups": sorted(set(groups.iloc[test])), "chosen": chosen,
                      "model": model_score, "baseline": base_score,
                      "paired_balanced_accuracy_difference": model_score["balanced_accuracy"] - base_score["balanced_accuracy"], "inner_selection": comparison})
        for pos, index in enumerate(test):
            predictions.append({"test_id": df.iloc[index].test_id, "group_id": groups.iloc[index], "fold": fold, "reference": int(y.iloc[index]), "predicted": int(pred[pos]), "baseline": int(base[pos]), "score": float(prob[pos]), "selected": chosen})
    chosen, comparison = select(x, y, groups)
    final = candidates()[chosen].fit(x, y)
    domain = domain_for(df)
    domain["selected_candidate"] = chosen
    artifact = root / "artifacts/model_c"
    artifact.mkdir(parents=True, exist_ok=True)
    os.environ["MODEL_C_ARTIFACT"] = str(artifact.resolve())
    joblib.dump(final, artifact / "model.joblib")
    (artifact / "domain.json").write_text(json.dumps(domain, indent=2))
    for name in ["harmonization.json", "data_dictionary.json"]:
        (artifact / name).write_bytes((root / "data/processed" / name).read_bytes())
    (artifact / "inference.py").write_bytes(Path(__file__).with_name("inference.py").read_bytes())
    (artifact / "requirements.txt").write_text("numpy==2.2.6\npandas==2.2.3\nscikit-learn==1.6.1\nscipy==1.15.3\njoblib==1.4.2\n")
    (artifact / "checksums.json").write_text(json.dumps({p.name: sha(p) for p in artifact.iterdir() if p.is_file() and p.name != "checksums.json"}, indent=2))
    cross = {}
    for campaign in df.campaign.unique():
        train = df[df.campaign == campaign]
        test = df[(df.campaign != campaign) & df.material.isin(train.material.unique())]
        selection, comparisons = select(train[FEATURES].reset_index(drop=True), train.alarm_level_reached.astype(int).reset_index(drop=True), train.group_id.reset_index(drop=True))
        fitted = candidates()[selection].fit(train[FEATURES], train.alarm_level_reached.astype(int))
        cross[campaign + " -> other"] = {"selected": selection, "n_train": len(train), "n_test_supported_materials": len(test), "excluded_unseen_material_rows": int(((df.campaign != campaign) & ~df.material.isin(train.material.unique())).sum()), "scores": scores(test.alarm_level_reached.astype(int), fitted.predict(test[FEATURES]), proba(fitted, test[FEATURES])), "scope": "Domain-shift stress test only; material intersection; not final model performance."}
    per_material = {material: scores(y[df.material == material], all_oof[df.material == material], all_probability[df.material == material]) for material in sorted(df.material.unique())}
    material_stress = {}
    for material in sorted(df.material.unique()):
        train = df[df.material != material]
        test = df[df.material == material]
        fitted = candidates()["logistic"].fit(train[FEATURES], train.alarm_level_reached.astype(int))
        material_stress[material] = {"method": "fixed logistic diagnostic only; unseen material encoded all-zero", "scores": scores(test.alarm_level_reached.astype(int), fitted.predict(test[FEATURES]), proba(fitted, test[FEATURES]))}
    model_values = [r["model"]["balanced_accuracy"] for r in folds]
    baseline_values = [r["baseline"]["balanced_accuracy"] for r in folds]
    paired = [r["paired_balanced_accuracy_difference"] for r in folds]
    metrics = {"environment": "Google Colab CPU" if "COLAB_RELEASE_TAG" in os.environ else "local CPU", "seed": SEED, "task": domain["target"], "n_rows": len(df), "n_groups": df.group_id.nunique(),
               "campaign_counts": df.groupby("campaign").size().to_dict(), "class_balance": y.value_counts().to_dict(),
               "selected_final": chosen, "comparison_only_full_data_inner_cv": comparison, "outer_folds": folds,
               "headline_selection_unbiased_nested_cv": {"metric": "balanced_accuracy", "mean": float(np.mean(model_values)), "std": float(np.std(model_values, ddof=1)), "baseline_mean": float(np.mean(baseline_values)), "baseline_std": float(np.std(baseline_values, ddof=1)), "paired_mean": float(np.mean(paired)), "paired_std": float(np.std(paired, ddof=1)), "paired_differences": paired},
               "pooled_oof": scores(y, all_oof, all_probability), "baseline_pooled_oof": scores(y, all_baseline), "per_material": per_material, "cross_campaign": cross, "leave_one_material_out_stress_test": material_stress, "scientific_checks": scientific_checks(observations, output), "versions": domain["versions"]}
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2))
    oof = pd.DataFrame(predictions)
    oof.to_csv(output / "out_of_fold_predictions.csv", index=False)
    failures = df.assign(oof_predicted=all_oof, reference=y)
    failures[failures.oof_predicted != failures.reference].to_csv(output / "failure_cases.csv", index=False)
    dashboard = observations.copy()
    dashboard["predicted_alarm_level_reached"] = None
    dashboard["prediction_value_kind"] = None
    dashboard["ood"] = None
    dashboard["ood_reason"] = "Unsupported/ambiguous followup configuration; measured data only"
    dashboard["prediction_scope"] = "none"
    for i, row in dashboard[dashboard.training_eligible].iterrows():
        request = {k: row[k] for k in FEATURES}
        request["units"] = UNITS
        result = predict_model_c(request)
        for key in ["predicted_alarm_level_reached", "ood", "ood_reason", "nearest_distance", "ood_threshold", "nearest_training_test_id"]:
            dashboard.loc[i, key] = result[key]
        dashboard.loc[i, "prediction_value_kind"] = "predicted"
        dashboard.loc[i, "prediction_scope"] = "in_sample_final_model; use OOF columns for validation"
    dashboard = dashboard.merge(oof[["test_id", "predicted", "fold"]].rename(columns={"predicted": "oof_predicted", "fold": "oof_fold"}), on="test_id", how="left")
    dashboard["derived_label_kind"] = "derived"
    dashboard["model_version"] = domain["model_version"]
    dashboard.to_csv(root / "data/processed/dashboard_table.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    cm = confusion_matrix(y, all_oof, labels=[0, 1])
    axes[0].imshow(cm, cmap="Blues")
    for (i, j), v in np.ndenumerate(cm):
        axes[0].text(j, i, str(v), ha="center", va="center")
    axes[0].set(xticks=[0,1], yticks=[0,1], xlabel="Nested OOF predicted threshold class", ylabel="Derived reference class", title="Grouped nested validation")
    axes[1].scatter(df.airflow_cm_s, df.iss_scatter_v, c=y, cmap="coolwarm", alpha=.6)
    axes[1].axhline(2, color="black", linestyle="--", label="2 V source alarm level")
    axes[1].set(xlabel="Controlled inlet airflow (cm/s)", ylabel="Source-recorded ISS scatter (V)", title="Measured response; high-end saturation")
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(output / "validation.png", dpi=170)
    plt.close(fig)
    if chosen == "tree_depth2":
        fig = plt.figure(figsize=(12, 5))
        plot_tree(final[-1], feature_names=final[0].get_feature_names_out(), class_names=["below2V", "atleast2V"], filled=True, precision=2)
        fig.tight_layout()
        fig.savefig(output / "selected_tree.png", dpi=170)
        plt.close(fig)
    # Find an accepted but OOD input for the integration contract and regression test.
    corners = itertools.product(*[domain["ranges"][k] for k in NUMERIC])
    found = None
    for values in corners:
        for material in domain["materials"]:
            request = dict(zip(NUMERIC, values)) | {"material": material, "units": UNITS}
            response = predict_model_c(request)
            if response["ood"]:
                found = {"request": request, "response": response}
                break
        if found:
            break
    if found is None:
        raise RuntimeError("No accepted OOD corner: empirical domain detector needs review")
    (output / "ood_example.json").write_text(json.dumps(found, indent=2))
    sample = {k: df.iloc[0][k] for k in FEATURES} | {"units": UNITS}
    (output / "sample_inference.json").write_text(json.dumps({"request": sample, "response": predict_model_c(sample)}, indent=2))
    write_evaluation(metrics, output)
    print(json.dumps({"selected": chosen, "headline": metrics["headline_selection_unbiased_nested_cv"], "rows": len(df), "groups": df.group_id.nunique()}, indent=2))
    return metrics


def write_evaluation(metrics, output):
    h = metrics["headline_selection_unbiased_nested_cv"]
    lines = ["# Model C evaluation", "", f"Executed environment: {metrics['environment']}. Seed {SEED}. Versions: `{json.dumps(metrics['versions'])}`.", "",
             f"{metrics['n_rows']} primary rows; {metrics['n_groups']} conservative validation groups. Physical primary samples total82, but ambiguous aged51a merges an additional group to prevent leakage.", "",
             f"Headline selection-unbiased estimate: grouped nested5-fold balanced accuracy **{h['mean']:.6f} ± {h['std']:.6f}** (sample fold standard deviation). Baseline **{h['baseline_mean']:.6f} ± {h['baseline_std']:.6f}**. Paired difference **{h['paired_mean']:.6f} ± {h['paired_std']:.6f}**. This estimates the entire selection procedure, not a separately held-out final fitted forest.", "",
             "Outer folds remain untouched by candidate selection; inner4-fold GroupKFold compares fixed majority, depth2 tree, C1 logistic and100-tree depth3 forest. No post-error candidates were added. Equal fixed-configuration budget, zero hyperparameter searches. Candidates within the best candidate's one-fold SD are treated as tied; choose in simplicity order majority→tree→logistic→forest. The architecture order was fixed before inspecting validation scores.", "",
             "| Outer fold | Selected | Model balanced accuracy | Baseline | Paired difference |", "|---|---|---:|---:|---:|"]
    for f in metrics["outer_folds"]:
        lines.append(f"|{f['fold']}|{f['chosen']}|{f['model']['balanced_accuracy']:.6f}|{f['baseline']['balanced_accuracy']:.6f}|{f['paired_balanced_accuracy_difference']:.6f}|")
    lines += ["", "## Candidate comparison only", "", "These full-data inner folds are selection results, not the headline validation estimate.", "", "| Candidate | Mean balanced accuracy | Fold SD |", "|---|---:|---:|"]
    for name, value in metrics["comparison_only_full_data_inner_cv"].items():
        lines.append(f"|{name}|{value['mean']:.6f}|{value['std']:.6f}|")
    lines += ["", f"Final export: **{metrics['selected_final']}**. Objective: predict a binary derived2V scatter threshold using categorical material and five controlled settings. Logistic minimizes regularized weighted log loss; trees/forest use weighted Gini splits. Primary metric balanced accuracy.", "", "## Pooled outer predictions", "", f"`{json.dumps(metrics['pooled_oof'])}`", "", "## Per material", "", "Single-class strata have undefined balanced accuracy and PR-AUC (null).", "", "| Material | n | Positives | Precision | Recall | F1 | Balanced accuracy |", "|---|---:|---:|---:|---:|---:|---:|"]
    for material, s in metrics["per_material"].items():
        lines.append(f"|{material}|{s['n']}|{s['positive']}|{s['precision']:.4f}|{s['recall']:.4f}|{s['f1']:.4f}|{s['balanced_accuracy']}|")
    lines += ["", "## Campaign shift", "", "Train-only selection repeated in each source campaign. Test uses only materials seen in source. Pyrell is excluded from SAME→SAME-R. These are stress tests, not nested headline scores.", ""]
    for direction, s in metrics["cross_campaign"].items():
        lines += [f"- {direction}: `{json.dumps(s)}`"]
    lines += ["", "Leave-one-material-out fixed-logistic diagnostic results are in metrics.json. Inference rejects unseen materials; this diagnostic does not support deployment on held-out materials.", "", "## External checks and errors", "", f"Source-workbook moment check: n={metrics['scientific_checks']['workbook_moment_ratio_n']}; max absolute diameter error={metrics['scientific_checks']['workbook_moment_ratio_max_absolute_error_um']:.12g} μm for1000*M1/M0. No lognormal assumption for this ratio.", "", "external_checks.csv compares all10 visually verified Table1 rows from [NTRS20130000422](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf), p7. It recomputes count and mass-equivalent diameters from rounded geometric mean and geometric SD, assuming lognormal sizes. This is algebraic/rounding validation; those table rows cannot be treated as independent predictive validation or matched to exact raw run IDs.", "", "External check **fails for unaged Teflon**: printed Dg=0.081 μm and sigma=2.198 imply count0.110450225 μm and mass0.205366583 μm, versus source0.101 and0.170 μm. The discrepancy exceeds ±0.0005 rounding propagated through all inputs and outputs. The original table was visually rechecked. No column-averaging explanation is documented: unresolved source-table inconsistency, not repaired data. This check is independent of the classifier labels. All numerical pairs and rounding intervals are in external_checks.csv.", "", "failure_cases.csv contains every nested OOF error with source rows and controls. validation.png shows predicted vs derived reference classes and measured scatter vs airflow. The scatter plot is descriptive, not causal. No uncertainty interval or calibrated probability is claimed. Fold SD describes variability, not a confidence interval.", "", "## Limits", "", "Only84 analyzed primary records, uneven material/condition/campaign coverage,81 conservative validation groups.82 primary physical samples collapse to81 because the ambiguous aged51aK02 record is conservatively connected to51K01/61K02. Retaining reburns reflects experimental history that controls do not fully capture. SAME-R source quality flags are blank/unknown. AW retains source numeric voltages with unresolved per-row saturation and LOD; only threshold exceedance is modeled. Rt/R0 does not uniquely determine actual sample temperature. No ambient spacecraft generalization, time-to-alarm, flame/fatality risk, detector certification, or unseen-material prediction. Full raw instrument calibration reconstruction was not performed; source-reduced common channel is used. No standalone2021 report verified; exact challenge page unavailable during audit."]
    (output / "evaluation.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    run(args.root)
