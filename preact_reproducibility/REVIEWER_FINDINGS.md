# Reviewer findings: revision and evidence ledger

**Historical ledger for the earlier CNN-mismatched review.** The substantive 10 October full-paper review is addressed in `../paper_mosicom2026/major_revision_response.md` and `MAJOR_REVISION_RESULTS.md`. Grouped evaluation, paired differences, eligibility sensitivities, adaptation/shift diagnostics and clean-environment replication have now been executed. The current interpretation supersedes the earlier single-partition emphasis below.

Updated 6 October 2026. The supplied review was intended for this paper, but its CNN-specific account conflicts with the manuscript. This ledger addresses each substantive concern using the actual agent study. Image-classification claims are not adopted as PreAct evidence.

| Reviewer concern | Revision / existing evidence | Status and remaining requirement |
|---|---|---|
| Unclear objectives and mechanism | Paper states trajectory-monitor scope, prefix pipeline, prediction target and intervention estimand | Addressed in writing; causal prevention is still unmeasured |
| Missing architecture | Specifies 20 structural features, training-only scaling, LR/HGB candidates, exact settings and alarm rule | Addressed for this monitor; no CNN architecture exists |
| Unknown datasets | Names source, 111 tasks, three systems, five attempts, terminal labels, digest verification and risk sets | Addressed; only one source dataset evaluated |
| Missing training settings | Reports LR C/iterations; HGB iterations/leaves/rate/penalty/seed; validation criterion, hash split and actual 78/16/17 task counts | Addressed; epochs and SGD momentum do not apply |
| Unclear metrics/results | Retains AUROC/AP/Brier, prevalence controls, confusion matrices, alarm rates and calibration curves | Addressed for prediction; prevention/horizon/savings require new labels and trials |
| Uncertain statistical significance | Retains task-cluster intervals and explicitly preliminary interpretation | Partially addressed; no broad significance or superiority claim, and no multiplicity-adjusted hypothesis test |
| Missing ablations | All full-feature/rate/tool-mixture LR and HGB variants retained, with test-independent model selection | Existing evidence documented; semantic monitor and broad tuning comparisons remain open |
| Weak generalization | Explicitly reports unsuccessful held-out-system transfer and confines conclusions to this dataset | Partially addressed; new datasets and independent model/scaffold shifts remain open |
| Missing code/environment | Adds audit script, current verified dependency pins, recorded machine environment and script hashes; existing download and rerun instructions retained | Local package addressed; GitHub publication pending, no URL invented |
| Unknown compute overhead | New real-data CPU audit reports extraction, two-model fit, and warmed batch prediction timings | Addressed as a narrow offline measurement; no energy, original agent compute, or online latency claim |
| Fairness, privacy and deployment safety | Adds trace privacy, aggregate redistribution, false-disruption risk and subgroup-evaluation limits | Discussed; subgroup fairness and safety guarantees are not established |
| Incremental novelty | Related work acknowledges existing prefix prediction, repair, transfer and calibration studies | Addressed through narrower contribution; new intervention method still requires empirical validation |
| More datasets / larger architectures / hyperparameter sweeps | Translates to additional software-agent sources, semantic/event monitors, factorial model/scaffold shifts and validation-only tuning | Planned, not completed; CNN scaling/vision-transformer experiments are inapplicable |
| Practical applications | Limits evidence to software-agent outcome monitoring and warns against automatic intervention on unsupported systems | Addressed; medical/security-critical deployment is not supported |

## New executed audit

Run from this repository folder:

```powershell
$env:PREACT_DATA_ROOT = 'D:\Proactive\data'
$env:OMP_NUM_THREADS = '1'
python reviewer_audit.py
```

`results/reviewer_audit.json` records observed environment, task counts, timings, source-script hashes, and audit assertions. It uses real downloaded traces for task splitting and timing; the future-suffix check uses a controlled fixture. Original result JSONs are not overwritten. Runtime is hardware dependent. The current SciPy/scikit-learn combination emitted an `Unknown solver options: iprint` optimization warning; fitting completed, and HGB was selected. This warning and the current audit environment should not be represented as the historical September training environment.

## What this revision cannot resolve by editing

Additional data collection, online randomized branches, multiple training seeds, independent model/scaffold comparisons, and public repository publication are separate work. They are explicitly unperformed. No fabricated benchmark, GPU run, fairness result, or prevention benefit is introduced to mark these findings complete.
