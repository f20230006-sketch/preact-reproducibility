# Response to the full paper review

Revision date: 10 October 2026. The author subsequently clarified that nothing has been submitted; the earlier existing-submission assumption was incorrect. The new manuscript is titled **Cross-System Transfer in Prefix-Based Software-Agent Failure Prediction**. Original results are preserved in the accompanying package; additional analyses are explicitly exploratory.

## 1. Implement interventions or reposition

**Addressed by repositioning.** The title, abstract, introduction and conclusion now describe an observational empirical audit. The action-value framework and extended intervention design have been removed from the main paper and retained as a proposed supplementary protocol. No verification/restart/abstention policy is claimed to have been executed. Future work is one short paragraph. The distracting image-classification statement is removed.

## 2. Paired statistics and repeated grouped evaluation

**Executed.** Source-transfer and target-trained predictions are evaluated on the exact same Qwen examples. A 2,000-resample task-cluster paired bootstrap estimates target-trained minus transferred AUROC. At checkpoint 20 the difference is **0.235, 95% interval [-0.071, 0.459]**. Because the interval includes zero, we withdrew language establishing a robust improvement.

Three seeded five-fold outer task partitions, each with a separate inner task-validation subset, were evaluated at all four checkpoints. At checkpoint 20, pooled out-of-fold transfer AUROC is **0.463, 0.562, 0.472**; target-trained AUROC is **0.558, 0.497, 0.506**. All paired intervals include zero and one advantage reverses. The abstract and conclusion now center this instability. Intervals condition on fold fits, cross-fitted AUROC mixes fold score scales, and shared tasks make these sensitivities rather than independent replications. No corrected significance claim is made.

## 3. Survival / risk-set confounding

**Executed descriptive sensitivities; population adjustment remains unidentified.** Eligibility is reported for every checkpoint by system and terminal outcome. At 20 results, successful-run eligibility is **300/335 Claude, 24/242 Luna, and 173/173 Qwen**; failed-run eligibility is **218/220, 84/313, and 380/382**. The paper now explains the changing source mixture.

The all-system common task/run cohort leaves only 16 target test runs at 20 results, yielding transfer/own AUROC **0.564/0.691**. At 40 results it is empty. A fixed cohort of 74 Qwen runs reaching checkpoint 40 yields checkpoint-20 **0.480/0.665**. These analyses use future duration only for descriptive cohort definition; they are not proposed deployment rules. We explicitly acknowledge collider selection and that missing later prefixes of completed short runs prevent identifying a full-population inverse-weighted effect.

## 4. Model versus scaffold

**Addressed through consistent scope and terminology.** The manuscript uses cross-system transfer and states that model/scaffold changes are joint. Call/result counting, command categories, argument fingerprints and messages can encode harness behavior. No model-only causal explanation is claimed. A model/scaffold factorial experiment remains future work; it has not been run.

## 5. Calibration and competing explanations

**Executed.** All fitting uses source training/validation or target validation, never target test labels. At checkpoint 20:

| Method | AUROC | AP | Brier |
|---|---:|---:|---:|
| Unchanged source | .456 | .647 | .300 |
| Constant target-validation prior | .500 | .671 | .223 |
| Prior correction | .456 | .647 | .245 |
| Target-validation sigmoid | .456 | .647 | .229 |
| ECDF rank normalization | .446 | .672 | .463 |
| Target-trained | .691 | .795 | .200 |

Probability adaptation improves Brier without recovering ranking at this checkpoint, but does not beat the constant target-validation prior. At checkpoint 40, unconstrained sigmoid fitting reverses ranking and worsens Brier (.229 to .265); this negative result is reported. Prior-shift assumptions are explicitly unverified. Source-training ECDFs and target-validation ECDFs provide a distribution-normalized baseline. All 20 validation-only standardized differences and KS distances are released. They diagnose observed feature/mixture shifts, not causes. A semantic baseline and independent conditional-label diagnosis remain open.

## 6. Novelty and closest predecessors

**Addressed.** The full evidence map moves out of the main paper. A compact table compares FailFast, EarlyEval, telemetry monitoring and this audit by dataset, representation, evaluation objective and empirical scope. Prior work already establishes transfer, recalibration and executed repair. The contribution is the task-grouped sensitivity audit on a distinct SWE-Rebench cohort; no first-discovery or state-of-the-art claim is retained.

## 7. Reproducibility and source verification

**Local archive prepared, upload destination pending.** The pinned dataset commit is `cdae27cdd16673f0c682871ad55d325f24cc7020`. Its downloaded index is byte-identical to the inspected local index, SHA-256 `db3879a1e77db5b412fd8acebbd794da8d845acb84fbee2d88f16b7eaced093f`. Selected index records, per-shard compressed/decompressed digests, task IDs/splits, scripts, version pins, numerical outputs and rerun instructions are included. Raw source traces and copied paper full texts are excluded. Each of 23 cited arXiv primary records was reachable and matched the inspected title; the 24th reference is the verified dataset. Bibliography-check JSON is provided. This verifies identity/access, not independent replication, venue acceptance or all evidence-map judgments.

## 8. Presentation and submission status

**Clean-environment verification added:** the four original analyses reproduced exactly; every revision field matched within 1e-8 under isolated NumPy 2.2.6/SciPy 1.15.3/scikit-learn 1.6.1. The primary clean dependency lock and comparison JSON are included. This resolves the inconsistent legacy NumPy metadata and optimizer warning for release verification, without claiming independent-data replication.

**Revised.** Larger scientific-figure labels show paired uncertainty, eligibility, adaptation, feature shift and exact confusion counts. Original ROC/PR/calibration and ablation figures remain supplementary. Author placeholders are removed and a provisional anonymous review block is used. IEEE conference formatting is retained.

Official submission guidance checked on 10 October confirms IEEE formatting and a typical six-page maximum: https://mosicom2026.com/submissions. It does not state an anonymity rule. The dates page renders dates as images that could not be verified with the available web tool: https://mosicom2026.com/important-dates. Nothing has been submitted. Confirm current new-submission eligibility, deadline, anonymity and supplementary-upload rules; no extension or permission is inferred. No submission or communication to the organizers has been made.

## Remaining limits

The revised study still has one dataset, three systems with joint model/scaffold variation, no semantic predictor, conditional statistical intervals, and no measured intervention benefit. The new analyses weaken rather than inflate the original finding. Independent data and controlled interventions are required for broader claims.
