# Final fixes following the second review

Date: 10 October 2026. The author clarified that **nothing has been submitted anywhere**. Earlier references to an existing submission were incorrect and have been removed from the current manuscript and instructions.

## Figure 3

Replaced the combined AUROC/Brier bars with two horizontal panels. The methods are Source, Target prior, Prior correction, Sigmoid, ECDF, and Target trained. Each panel has its own scale and explicitly preferred direction. The numerical Table IV is retained. Sigmoid is a short figure label for target-validation logistic recalibration; it is not a monotonicity guarantee. Feature-shift graphics remain supplementary. Figures are embedded as vector graphics in the same LaTeX source, so the native editor no longer needs companion figure files to compile the manuscript.

## Per-fold AUROC

The exact three seeded task partitions were recreated, with their original training/validation/test assignments. Their pooled scores match the existing report. All five outer folds have both outcome classes for every checkpoint/seed. At checkpoint 20:

| Seed | Transfer pooled | Transfer fold mean (SD) | Own pooled | Own fold mean (SD) |
|---|---:|---:|---:|---:|
|20261010|.463|.517 (.037)|.558|.566 (.061)|
|20261011|.562|.567 (.052)|.497|.497 (.116)|
|20261012|.472|.510 (.100)|.506|.539 (.085)|

Means are unweighted over defined individual fold AUROCs; sample SD describes fold variation, not an SE or confidence interval. Three seeds reuse the same 111 tasks and are not independent datasets. The current Table III adds these summaries beside pooled AUROC and paired intervals. `PER_FOLD_RESULTS.md` and `results/per_fold_results.json` include all four checkpoints and every fold score, task assignment and sample count. The target-training advantage still changes sign.

## Primary contribution and wording

The introduction and conclusion explicitly identify the evaluation protocol's contribution: a promising single-split result becomes inconclusive under stronger paired, grouped, eligibility and calibration analyses. The paper remains a structural-monitor reliability audit. Target-validation logistic recalibration is named consistently; existing JSON key `target_validation_sigmoid` is retained for schema compatibility and documented as an alias. Reviewer-specific provenance wording is removed from the manuscript, while the non-preregistered checkpoint emphasis remains disclosed.

## Outcome convention

The current prediction code uses `failure = int(not evaluation.resolved)`: failure=1, success=0. Confusion matrices encode rows success/failure and columns continue/alarm. The repeat-attempt script's `success` flag remains explicitly a success indicator and is not called Y. The proposed intervention fragment now defines Y(m)=1 as failure and S(m)=1-Y(m) as success before defining success-based utility. Historical drafts are excluded from the archive.

## Archive and submission status

The local reproducibility archive is refreshed and integrity checked. It excludes raw traces, copied full texts, repository history and any stale manuscript PDF. Source files, plots, manifests, environment lock, result reports and current source are included. The revised source compiled successfully using the built-in editor compiler. This tool checks the preview without exporting a disk PDF; export the current preview before uploading the manuscript. An older disk PDF must not be supplied as v5.

The reproducibility repository is published at https://github.com/f20230006-sketch/preact-reproducibility on 11 October 2026. No conference submission has been created; current venue eligibility must be established before submission. No CMT revision window is presumed. Anonymity and supplement policies must be checked before creating a new submission. The local package is ready for that step, but local preparation is not claimed as public availability.

## Author information correction

The official submission guidelines and call for papers do not state an anonymity requirement. At the user's request, the anonymous block was replaced with Yuvaraj Nayak, Department of Computer Science, BITS Pilani Dubai Campus, and the supplied email. The public GitHub package includes these authorized author details. No double-blind requirement is inferred.
