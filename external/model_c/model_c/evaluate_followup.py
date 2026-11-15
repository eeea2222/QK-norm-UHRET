"""Retrospective evaluation only: never exports or overwrites trained weights."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .inference import FEATURES, NUMERIC, UNITS
from .train import SEED, candidates, proba, scores


def majority_predictions(train, test):
    """Learn material-only majority from training rows; ties choose class0."""
    global_class = int(np.bincount(train.alarm_level_reached.astype(int), minlength=2).argmax())
    mapping = {
        name: int(np.bincount(part.alarm_level_reached.astype(int), minlength=2).argmax())
        for name, part in train.groupby("material")
    }
    predictions = test.material.map(mapping).fillna(global_class).astype(int).to_numpy()
    return predictions, mapping, global_class


def summary(values):
    values = [float(v) for v in values if v is not None]
    return {"values": values, "mean": float(np.mean(values)) if values else None,
            "std": float(np.std(values, ddof=1)) if len(values) > 1 else None}


def primary_data(root):
    df = pd.read_csv(root / "data/processed/training.csv", float_precision="round_trip")
    assert df.test_id.is_unique and df.run_id.is_unique
    assert df.training_eligible.all()
    assert np.array_equal(df.alarm_level_reached, (df.iss_scatter_v >= 2).astype(int))
    return df


def compare_baseline(df, old_metrics, old_oof):
    """Use the frozen outer fold membership; do not reselect the deployed model."""
    folds, predictions = [], []
    existing = old_oof.set_index("test_id")
    for frozen in old_metrics["outer_folds"]:
        train = df[df.group_id.isin(frozen["train_groups"])].reset_index(drop=True)
        test = df[df.group_id.isin(frozen["test_groups"])].reset_index(drop=True)
        assert not set(train.group_id) & set(test.group_id)
        assert len(train) + len(test) == len(df)
        saved = existing.loc[test.test_id]
        assert np.array_equal(test.alarm_level_reached, saved.reference)
        assert (saved.fold == frozen["fold"]).all()
        baseline, mapping, fallback = majority_predictions(train, test)
        # Fit a disposable CV estimator. The deployed artifact is never fitted/written.
        forest = candidates()["forest_depth3"].fit(train[FEATURES], train.alarm_level_reached.astype(int))
        forest_pred, forest_score = forest.predict(test[FEATURES]), proba(forest, test[FEATURES])
        baseline_metrics = scores(test.alarm_level_reached, baseline, baseline)
        forest_metrics = scores(test.alarm_level_reached, forest_pred, forest_score)
        selected_metrics = scores(test.alarm_level_reached, saved.predicted.to_numpy(), saved.score.to_numpy())
        assert selected_metrics["balanced_accuracy"] == frozen["model"]["balanced_accuracy"]
        inner = []
        for inner_fold, (a, b) in enumerate(GroupKFold(n_splits=4).split(train, groups=train.group_id)):
            inner_pred, _, _ = majority_predictions(train.iloc[a], train.iloc[b])
            inner.append({"fold": inner_fold, "scores": scores(train.iloc[b].alarm_level_reached, inner_pred),
                          "train_groups": sorted(train.iloc[a].group_id.unique()),
                          "test_groups": sorted(train.iloc[b].group_id.unique())})
        folds.append({"fold": frozen["fold"], "train_groups": frozen["train_groups"], "test_groups": frozen["test_groups"],
                      "train_material_majorities": mapping, "fallback_global_majority": fallback,
                      "material_majority": baseline_metrics, "fixed_forest": forest_metrics,
                      "original_nested_selection": selected_metrics,
                      "forest_minus_material_majority": forest_metrics["balanced_accuracy"] - baseline_metrics["balanced_accuracy"],
                      "nested_selection_minus_material_majority": selected_metrics["balanced_accuracy"] - baseline_metrics["balanced_accuracy"],
                      "inner_material_majority_comparison_only": inner})
        for i, row in test.iterrows():
            predictions.append({"test_id": row.test_id, "group_id": row.group_id, "material": row.material,
                                "fold": frozen["fold"], "reference": int(row.alarm_level_reached),
                                "material_majority": int(baseline[i]), "fixed_forest": int(forest_pred[i]),
                                "forest_score": float(forest_score[i]), "original_nested_selection": int(saved.iloc[i].predicted)})
    oof = pd.DataFrame(predictions)
    assert oof.test_id.is_unique and set(oof.test_id) == set(df.test_id)
    result = {"folds": folds, "majority_tie_rule": "Class0 on equal training counts; unseen material uses training-global majority",
              "scope": "Post-hoc diagnostic on the original frozen outer folds. Fixed-forest score is not a new selection-unbiased headline. Original nested choices and deployed weights remain unchanged.",
              "material_majority": summary([f["material_majority"]["balanced_accuracy"] for f in folds]),
              "fixed_forest": summary([f["fixed_forest"]["balanced_accuracy"] for f in folds]),
              "original_nested_selection": summary([f["original_nested_selection"]["balanced_accuracy"] for f in folds]),
              "forest_minus_material_majority": summary([f["forest_minus_material_majority"] for f in folds]),
              "nested_selection_minus_material_majority": summary([f["nested_selection_minus_material_majority"] for f in folds]),
              "pooled_material_majority": scores(oof.reference, oof.material_majority),
              "pooled_fixed_forest": scores(oof.reference, oof.fixed_forest, oof.forest_score)}
    result["forest_beats_material_majority_mean"] = result["forest_minus_material_majority"]["mean"] > 0
    result["forest_exceeds_original_one_fold_sd_tie_band"] = result["forest_minus_material_majority"]["mean"] > result["fixed_forest"]["std"]
    result["nested_selection_beats_material_majority_mean"] = result["nested_selection_minus_material_majority"]["mean"] > 0
    return result, oof


def within_material(part):
    """Fixed, untuned logistic model on numeric controls only; evaluation-only."""
    part = part.reset_index(drop=True)
    counts = {str(label): {"runs": int((part.alarm_level_reached == label).sum()),
                          "groups": int(part.loc[part.alarm_level_reached == label, "group_id"].nunique())} for label in [0, 1]}
    result = {"n_runs": len(part), "n_groups": int(part.group_id.nunique()), "class_balance": counts,
              "class_definition": "0=ISS scatter below2V,1=atleast2V", "features": NUMERIC,
              "scope": "Post-hoc within-material diagnostic; fixed C1 balanced logistic; no model export or deployment claim"}
    if min(counts[str(label)]["groups"] for label in [0, 1]) < 3:
        return result | {"status": "insufficient data", "reason": "Both classes require at least3 distinct groups"}, pd.DataFrame()
    folds, predictions = [], []
    splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED)
    for fold, (a, b) in enumerate(splitter.split(part, part.alarm_level_reached, part.group_id)):
        train, test = part.iloc[a], part.iloc[b]
        assert not set(train.group_id) & set(test.group_id)
        if train.alarm_level_reached.nunique() != 2:
            return result | {"status": "insufficient data", "reason": "A grouped training fold has only one class"}, pd.DataFrame()
        estimator = make_pipeline(StandardScaler(), LogisticRegression(C=1, class_weight="balanced", max_iter=3000, random_state=SEED))
        estimator.fit(train[NUMERIC], train.alarm_level_reached.astype(int))
        pred, score = estimator.predict(test[NUMERIC]), estimator.predict_proba(test[NUMERIC])[:, 1]
        baseline = np.full(len(test), int(np.bincount(train.alarm_level_reached.astype(int), minlength=2).argmax()))
        folds.append({"fold": fold, "train_groups": sorted(train.group_id.unique()), "test_groups": sorted(test.group_id.unique()),
                      "model": scores(test.alarm_level_reached, pred, score), "majority": scores(test.alarm_level_reached, baseline)})
        for i, (_, row) in enumerate(test.iterrows()):
            predictions.append({"test_id": row.test_id, "group_id": row.group_id, "fold": fold, "reference": int(row.alarm_level_reached),
                                "predicted": int(pred[i]), "score": float(score[i]), "majority": int(baseline[i])})
    oof = pd.DataFrame(predictions)
    result.update({"status": "TESTED_LOCALLY", "folds": folds, "pooled_oof": scores(oof.reference, oof.predicted, oof.score),
                   "pooled_majority": scores(oof.reference, oof.majority),
                   "fold_balanced_accuracy": summary([f["model"]["balanced_accuracy"] for f in folds]),
                   "undefined_fold_policy": "Single-class test folds have null balanced accuracy; excluded from fold mean, included in pooled OOF."})
    return result, oof


def measured_summary(df):
    rows = []
    for material, part in df.groupby("material"):
        row = {"material": material, "n_runs": len(part), "n_groups": int(part.group_id.nunique()),
               "n_reaching_2v": int((part.iss_scatter_v >= 2).sum()),
               "fraction_reaching_2v": float((part.iss_scatter_v >= 2).mean()),
               "value_kind": "derived", "label_provenance": "derived", "signal_kind": "measured",
               "rule": "count(primary ISS scatter>=2V)/count(primary runs)",
               "scope": "Observed primary runs only; secondary aging and DBP excluded; unweighted by sample; descriptive, not a detection probability",
               "campaigns": ";".join(sorted(part.campaign.unique())), "test_ids": ";".join(part.test_id),
               "iss_scatter_v_min": float(part.iss_scatter_v.min()), "iss_scatter_v_max": float(part.iss_scatter_v.max())}
        for key in NUMERIC:
            row[key + "_min"] = float(part[key].min())
            row[key + "_max"] = float(part[key].max())
            row[key + "_unit"] = UNITS[key]
        rows.append(row)
    return pd.DataFrame(rows)


def plot_conditions(part, destination):
    fig, axes = plt.subplots(1, len(NUMERIC), figsize=(18, 4), sharey=True)
    for ax, key in zip(axes, NUMERIC):
        for campaign, marker in [("SAME", "o"), ("SAME-R", "^")]:
            subset = part[part.campaign == campaign]
            ax.scatter(subset[key], subset.iss_scatter_v, label=campaign, marker=marker, alpha=.7, s=40)
        ax.axhline(2, color="black", linestyle="--", linewidth=1)
        ax.set_xlabel(f"{key}\n({UNITS[key]})")
    axes[0].set_ylabel("Source-recorded ISS scatter (V)")
    axes[-1].legend(fontsize=8)
    fig.suptitle(f"{part.material.iloc[0]}: measured primary runs; dashed2V threshold; high-end saturation unresolved")
    fig.tight_layout()
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def write_report(result, output):
    comparison = result["baseline_comparison"]
    lines = ["# Model C follow-up evaluation", "", "Status: TESTED_LOCALLY. Evaluation and reporting only; deployed weights and inference bundle are byte-for-byte unchanged.", "",
             "The original0.870152 headline evaluates nested model selection, not a fixed forest: outer folds selected tree, forest, tree, tree and logistic. We retain it and compare a fixed forest and a training-fold-only material-majority baseline on exactly the saved outer groups. This is a post-hoc diagnostic, not a fresh independent test or a new selection-unbiased estimate. The baseline is also evaluated inside the same4-fold inner splits, without changing original selections. Majority ties choose0; unseen material falls back to training-global majority.", "",
             "| Method | Mean balanced accuracy | Fold SD |", "|---|---:|---:|"]
    for key in ["material_majority", "fixed_forest", "original_nested_selection"]:
        item = comparison[key]
        lines.append(f"|{key}|{item['mean']:.6f}|{item['std']:.6f}|")
    lines += ["", "| Fold | Material majority | Fixed forest | Forest minus material majority | Original nested selection minus material majority |", "|---|---:|---:|---:|---:|"]
    for f in comparison["folds"]:
        lines.append(f"|{f['fold']}|{f['material_majority']['balanced_accuracy']:.6f}|{f['fixed_forest']['balanced_accuracy']:.6f}|{f['forest_minus_material_majority']:.6f}|{f['nested_selection_minus_material_majority']:.6f}|")
    paired = comparison["forest_minus_material_majority"]
    lines += ["", f"Forest-minus-material-majority mean±SD: **{paired['mean']:.6f} ± {paired['std']:.6f}**. This is descriptive fold variability, not a confidence interval.", ""]
    if not comparison["forest_beats_material_majority_mean"]:
        lines += ["**The forest does not beat the per-material majority baseline. Material identity explains the headline score; the original comparison against a global majority baseline does not establish additional predictive value from controlled conditions.**", ""]
    elif comparison["forest_exceeds_original_one_fold_sd_tie_band"]:
        lines += ["The fixed forest has a higher numerical mean outside the original one-fold-SD tie band. This post-hoc difference alone does not establish a new independent generalization claim.", ""]
    else:
        lines += ["The fixed forest has a slightly higher numerical mean than material majority, but the advantage is smaller than one forest fold SD, so they are tied under the original evaluation rule. Four of five paired differences are zero. **Material identity explains the headline score**: the material-only baseline exceeds the original nested-selection headline. There is no demonstrated improvement from controlled conditions beyond that baseline; the small retrospective forest advantage is not an independent generalization claim.", ""]
    lines += ["## Kapton and Teflon", "", "Counts below use primary heating runs only. Groups retain the original conservative connections, including the ambiguous51a linkage. A group can appear in both class counts if it contains conflicting outcomes; class-group counts need not sum to total groups. Both classes require at least3 groups before fitting an untuned three-fold stratified grouped logistic diagnostic on numeric controls only.", "",
              "| Material | Runs | Groups | Below2V runs/groups | Atleast2V runs/groups | Logistic pooled OOF balanced accuracy |", "|---|---:|---:|---|---|---:|"]
    for material, item in result["within_material"].items():
        c = item["class_balance"]
        value = item.get("pooled_oof", {}).get("balanced_accuracy", "insufficient data")
        lines.append(f"|{material}|{item['n_runs']}|{item['n_groups']}|{c['0']['runs']}/{c['0']['groups']}|{c['1']['runs']}/{c['1']['groups']}|{value}|")
    for material, item in result["within_material"].items():
        lines += ["", f"### {material}", "", f"`{json.dumps(item)}`", "", f"![{material} measured signal against five controls]({material.lower()}_conditions.png)"]
    lines += ["", "No fitted within-material models are serialized or used by inference. These are small, post-hoc condition diagnostics. Single-class test folds receive null balanced accuracy; pooled OOF scores retain all runs. Scatter relationships are descriptive and confounded by the experimental test matrix, campaign and reused samples; they are not causal effects.", "",
              "## Measured-only dashboard", "", "`data/processed/dashboard_measured_only.csv` contains one row per material: primary-run counts, groups, count and fraction reaching2V, source test IDs, campaign coverage and min/max of every controlled condition with units. It contains no model prediction or synthetic observations. Fractions and ranges are deterministic derivations from measured/source-reported data, not estimated detection probabilities. Reburn runs count as runs, and group counts expose dependence. Constant controls appear as identical lower/upper limits in the figures.", "",
              "Reproduce without retraining or changing weights: `python -m model_c.evaluate_followup`. The original notebook and model-training results retain their historical Colab status; this addendum was executed locally. `reports/followup_metrics.json` includes all fold memberships, inner baseline scores, OOF metrics, source hashes and the protected deployed-artifact hashes."]
    (output / "evaluation_followup.md").write_text("\n".join(lines) + "\n")
    previous = output / "evaluation.md"
    marker = "\n<!-- evaluation-followup -->\n"
    original = previous.read_text().split(marker)[0]
    previous.write_text(original + marker + "\n" + "\n".join(lines[2:]) + "\n")


def run(root="."):
    root = Path(root)
    artifact = root / "artifacts/model_c"
    protected = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(artifact.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    df = primary_data(root)
    original = json.loads((root / "reports/metrics.json").read_text())
    comparison, oof = compare_baseline(df, original, pd.read_csv(root / "reports/out_of_fold_predictions.csv"))
    output = root / "reports"
    oof.to_csv(output / "material_majority_oof.csv", index=False)
    details = {}
    for material in ["Kapton", "Teflon"]:
        part = df[df.material == material]
        details[material], predictions = within_material(part)
        if not predictions.empty:
            predictions.to_csv(output / f"{material.lower()}_logistic_oof.csv", index=False)
        plot_conditions(part, output / f"{material.lower()}_conditions.png")
    measured_summary(df).to_csv(root / "data/processed/dashboard_measured_only.csv", index=False)
    result = {"status": "TESTED_LOCALLY", "seed": SEED, "baseline_comparison": comparison, "within_material": details,
              "protected_artifact_sha256": protected,
              "input_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ["data/processed/training.csv", "reports/metrics.json", "reports/out_of_fold_predictions.csv"]}}
    for name, checksum in protected.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == checksum, f"Protected artifact changed: {name}"
    (output / "followup_metrics.json").write_text(json.dumps(result, indent=2))
    write_report(result, output)
    print(json.dumps({key: comparison[key] for key in ["material_majority", "fixed_forest", "original_nested_selection", "forest_minus_material_majority"]}, indent=2))
    return result


if __name__ == "__main__":
    run()
