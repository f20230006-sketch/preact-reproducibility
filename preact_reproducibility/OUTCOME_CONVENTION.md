# Outcome and recalibration conventions

- Current manuscript: **Y=1 means unresolved terminal failure; Y=0 means resolved success**.
- Prediction code: `failure = int(not evaluation.resolved)`; `predict_proba(... )[:, 1]` scores failure.
- Confusion matrices: actual success/failure rows correspond to labels 0/1; continue/alarm columns correspond to 0/1. Counts concern terminal outcomes, not prevention.
- Repeat-attempt script: its separately named `success` boolean means resolved=true. It is not the manuscript variable Y.
- Proposed intervention fragment: Y(m)=1 means failure and S(m)=1-Y(m) means success; positive utility uses S(m). This fragment is an unexecuted design.
- Legacy JSON key `target_validation_sigmoid` denotes **target-validation logistic recalibration**. The fit allows negative slope and ranking reversal; the figure's short label Sigmoid does not assert monotonicity.
- Historical drafts using a different Y convention are excluded from the review archive. Original numerical reports name success/failure explicitly and remain original supplementary outputs.

Individual fold AUROCs are stored to four decimal places; the means and sample SDs summarize those stored values and are reported to three decimals. SD is descriptive fold variability, not an SE or confidence interval. All five folds are defined for every reported checkpoint/seed. Pooled consistency assertions reproduce the original cross-fitted scores; repeated seeds reuse the same tasks.
