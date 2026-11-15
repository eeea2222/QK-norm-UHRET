# Model C model card — evaluation follow-up

License: Apache License 2.0 for project code and model artifacts. NASA source datasets retain CC0-1.0; reference publications retain their original terms. See LICENSE and NOTICE. Repository visibility: public.

Version1.0.0 weights remain unchanged. This update adds evaluation and reports only. Model SHA256: `1d0a63fe5f51b89df6710e5d2c49632964af7457d67204337dbc3e4eb02f6e01`.

The target is a derived experimental label: source-recorded ISS scatter≥2V. Inputs are tested material, airflow, resistance ratio, heating duration, programmed primary aging and mixing. This is not operational alarm ground truth or a safety certification.

**Material identity explains the headline score.** The original grouped nested-selection estimate is0.870152±0.076360. A per-material majority learned only from each training fold reaches0.891342±0.048823 on the exact same outer groups. A fixed forest reaches0.900433±0.056572, with paired differences `[0,0,0,0,0.045455]`, mean0.009091±0.020328. The forest's small numerical advantage is within one fold SD and is a tie under the original rule. There is no demonstrated extra predictive value from controlled conditions beyond this material baseline. Fold SD is not a confidence interval. These added comparisons are post-hoc, not a fresh independent model-selection estimate.

Kapton:21 primary runs,19 conservative groups; below2V12 runs/10 groups, reaching2V9 runs/9 groups. Teflon:15 runs/15 groups; below2V11 runs/11 groups, reaching2V4 runs/4 groups. Both meet the3-groups-per-class gate for an untuned numeric-only logistic diagnostic. Three-fold stratified grouped pooled OOF balanced accuracy is0.583333 and0.738636 respectively. Diagnostic fits are not serialized, deployed, or used to alter the exported forest.

The measured-only dashboard table has one row per material and no predictions. Observed reaching2V fractions: Kapton9/21, Teflon4/15, Lampwick17/17, Pyrell12/12, Silicone19/19. Each row includes tested control ranges, units, source test IDs and group counts. These describe the available primary experiments, not probabilities for new fires.

The original training/inference notebook was verified on standard CPU Colab with36 tests. New evaluation code and the expanded44-test suite pass locally and on a fresh Hub download. Full-suite [Hub-download logs](logs/pytest-hub-download.txt) are captured from the command `python -m pytest -q 2>&1 | tee logs/pytest-hub-download.txt`, never written as a summary pretending to be process output. Downloaded checksums, unchanged weights and standalone inference also pass; see `STATUS.json` for the verified commit.

Sparse conditions, reused samples, campaign differences, unresolved per-row saturation/LOD and weak material-specific predictive evidence limit all claims. Use measured observations as the primary dashboard evidence. Unseen materials, real alarm timing, spacecraft risk and operational certification remain unsupported.

See [evaluation addendum](reports/evaluation_followup.md), [machine-readable metrics](reports/followup_metrics.json), [README](README.md) and [STATUS.json](STATUS.json).
