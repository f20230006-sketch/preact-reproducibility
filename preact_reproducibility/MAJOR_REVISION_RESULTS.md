# Major revision: complete exploratory results

All new analyses follow reviewer feedback on 10 October 2026. Neither checkpoint 20 nor these comparisons were preregistered. Original four-checkpoint reporting is retained. No target test labels fit transformations, calibration, models, or thresholds.

## Paired task-cluster differences on the original split

| Checkpoint | Target n | Own minus transfer AUROC | Paired 95% interval |
|---|---:|---:|---|
|5|85|-0.106|[-0.228, 0.005]|
|10|85|0.149|[-0.003, 0.311]|
|20|85|0.235|[-0.071, 0.459]|
|40|74|0.062|[-0.055, 0.184]|

Intervals condition on fitted models and test tasks; they do not include full training uncertainty. No multiplicity-adjusted tests or acceptance probabilities are claimed.

## Repeated grouped five-fold cross-validation

Each outer fold holds out whole tasks across all systems. A random 20% subset of the remaining tasks is validation; the rest trains the candidates. Target-trained and transferred scores are evaluated on identical target runs. Pooled out-of-fold AUROC mixes fold-specific score scales; results are sensitivity analyses, not independent replications. The paired intervals condition on the fold models.

| Checkpoint | Seed | Transfer AUROC | Own AUROC | Difference [paired 95% interval] |
|---|---|---:|---:|---|
|5|20261010|0.508|0.436|-0.072 [-0.169, 0.034]|
|5|20261011|0.510|0.448|-0.062 [-0.152, 0.030]|
|5|20261012|0.507|0.439|-0.068 [-0.164, 0.021]|
|10|20261010|0.454|0.494|0.040 [-0.065, 0.142]|
|10|20261011|0.537|0.455|-0.083 [-0.182, 0.015]|
|10|20261012|0.470|0.440|-0.030 [-0.126, 0.058]|
|20|20261010|0.463|0.557|0.094 [-0.001, 0.187]|
|20|20261011|0.562|0.496|-0.065 [-0.151, 0.021]|
|20|20261012|0.472|0.506|0.034 [-0.054, 0.119]|
|40|20261010|0.519|0.587|0.068 [-0.037, 0.185]|
|40|20261011|0.564|0.524|-0.040 [-0.134, 0.045]|
|40|20261012|0.521|0.529|0.008 [-0.088, 0.106]|

## Target adaptation on the original split

Prior-shift correction adjusts log odds using source-training and target-validation failure prevalence; label-shift assumptions are unverified. Sigmoid regression uses target-validation labels only and allows negative slope, which reverses ranking at some checkpoints. ECDF baseline fits source feature ranks on source training and target ranks on target validation, then selects source classifiers using source validation. It does not use target test labels.

| Checkpoint | Method | AUROC | AP | Brier |
|---|---|---:|---:|---:|
|5|unchanged|0.475|0.680|0.445|
|5|prior_shift|0.475|0.680|0.304|
|5|target_validation_sigmoid|0.525|0.689|0.223|
|5|ecdf_normalized|0.382|0.617|0.311|
|5|target_trained|0.369|0.617|0.245|
|5|target_validation_prior|0.500|0.671|0.223|
|10|unchanged|0.422|0.653|0.455|
|10|prior_shift|0.422|0.653|0.334|
|10|target_validation_sigmoid|0.578|0.788|0.213|
|10|ecdf_normalized|0.516|0.719|0.350|
|10|target_trained|0.571|0.769|0.223|
|10|target_validation_prior|0.500|0.671|0.223|
|20|unchanged|0.456|0.647|0.300|
|20|prior_shift|0.456|0.647|0.244|
|20|target_validation_sigmoid|0.456|0.647|0.229|
|20|ecdf_normalized|0.446|0.672|0.463|
|20|target_trained|0.691|0.795|0.200|
|20|target_validation_prior|0.500|0.671|0.223|
|40|unchanged|0.551|0.653|0.229|
|40|prior_shift|0.551|0.653|0.266|
|40|target_validation_sigmoid|0.449|0.561|0.265|
|40|ecdf_normalized|0.566|0.715|0.268|
|40|target_trained|0.613|0.719|0.224|
|40|target_validation_prior|0.500|0.622|0.250|

## Eligibility by system and terminal outcome

Denominators use all 555 trajectories per system, stratified by terminal outcome. Eligibility means a prefix can be extracted; these are not event-time failure labels.

| Checkpoint | System | Outcome | Eligible / total | Fraction |
|---|---|---|---|---:|
|5|claude-code|success|335/335|1.000|
|5|claude-code|failure|220/220|1.000|
|5|gpt-5.6-luna|success|242/242|1.000|
|5|gpt-5.6-luna|failure|313/313|1.000|
|5|qwen3.6-27b|success|173/173|1.000|
|5|qwen3.6-27b|failure|382/382|1.000|
|10|claude-code|success|335/335|1.000|
|10|claude-code|failure|220/220|1.000|
|10|gpt-5.6-luna|success|206/242|0.851|
|10|gpt-5.6-luna|failure|290/313|0.927|
|10|qwen3.6-27b|success|173/173|1.000|
|10|qwen3.6-27b|failure|382/382|1.000|
|20|claude-code|success|300/335|0.896|
|20|claude-code|failure|218/220|0.991|
|20|gpt-5.6-luna|success|24/242|0.099|
|20|gpt-5.6-luna|failure|84/313|0.268|
|20|qwen3.6-27b|success|173/173|1.000|
|20|qwen3.6-27b|failure|380/382|0.995|
|40|claude-code|success|165/335|0.493|
|40|claude-code|failure|165/220|0.750|
|40|gpt-5.6-luna|success|0/242|0.000|
|40|gpt-5.6-luna|failure|1/313|0.003|
|40|qwen3.6-27b|success|151/173|0.873|
|40|qwen3.6-27b|failure|339/382|0.887|

## Cohort sensitivities

Common eligibility matches the same task/run index across all three systems, not the same stochastic trajectory. Conditioning on future eligibility is a descriptive sensitivity analysis, never a deployable selection rule. It can introduce collider selection and does not identify a causal selection-adjusted population effect. Fixed-target cohort uses Qwen runs reaching checkpoint 40, evaluated at earlier checkpoints. Missing-prefix inverse weighting is not identifiable here because completed short runs have no features at later checkpoints.

| Checkpoint | Common n | Common transfer / own AUROC | Fixed-target n | Fixed transfer / own AUROC |
|---|---:|---|---:|---|
|5|85|0.4746 / 0.3687|74|0.4282 / 0.3238|
|10|73|0.4092 / 0.5524|74|0.4161 / 0.5807|
|20|16|0.5636 / 0.6909|74|0.4798 / 0.6654|
|40|0|NA / NA|74|0.5512 / 0.6134|

## Validation-only feature-shift diagnostics

These compare source versus target validation cohorts, whose outcome mixtures and harnesses differ. Standardized mean differences and KS distances are descriptive; they do not isolate a model-weight effect. No KS p-values or causal interpretation are used.

| Checkpoint | Feature | Standardized mean difference | KS distance |
|---|---|---:|---:|
|5|n_errors|0.932|0.394|
|5|error_rate|0.932|0.394|
|5|recent_error_rate|0.932|0.394|
|5|error_streak|0.421|0.113|
|5|max_error_streak|0.931|0.394|
|5|n_unique_actions|-0.345|0.062|
|5|repeat_action_rate|0.345|0.062|
|5|recent_repeat_rate|0.345|0.062|
|5|n_edits|-1.307|0.506|
|5|n_reads|0.625|0.319|
|5|n_searches|0.525|0.438|
|5|n_tests|-0.112|0.006|
|5|n_shell|0.036|0.056|
|5|n_other|0.000|0.000|
|5|tool_switches|0.231|0.156|
|5|mean_result_chars|-0.881|0.412|
|5|recent_result_chars|-0.881|0.412|
|5|n_assistant_messages|3.435|0.906|
|5|last_action_edit|-1.095|0.375|
|5|last_action_test|-0.112|0.006|
|10|n_errors|0.820|0.437|
|10|error_rate|0.820|0.437|
|10|recent_error_rate|0.377|0.188|
|10|error_streak|-0.143|0.052|
|10|max_error_streak|0.829|0.437|
|10|n_unique_actions|-0.414|0.100|
|10|repeat_action_rate|0.414|0.100|
|10|recent_repeat_rate|0.214|0.037|
|10|n_edits|-1.171|0.519|
|10|n_reads|1.066|0.404|
|10|n_searches|0.387|0.386|
|10|n_tests|-0.467|0.123|
|10|n_shell|0.012|0.114|
|10|n_other|0.000|0.000|
|10|tool_switches|0.060|0.126|
|10|mean_result_chars|-0.324|0.196|
|10|recent_result_chars|0.552|0.301|
|10|n_assistant_messages|4.910|0.949|
|10|last_action_edit|-0.431|0.184|
|10|last_action_test|-0.542|0.128|
|20|n_errors|1.224|0.523|
|20|error_rate|1.224|0.523|
|20|recent_error_rate|0.383|0.142|
|20|error_streak|0.365|0.104|
|20|max_error_streak|1.130|0.523|
|20|n_unique_actions|-0.678|0.254|
|20|repeat_action_rate|0.678|0.254|
|20|recent_repeat_rate|0.519|0.139|
|20|n_edits|-0.667|0.285|
|20|n_reads|0.895|0.378|
|20|n_searches|-0.082|0.223|
|20|n_tests|-0.539|0.173|
|20|n_shell|0.251|0.070|
|20|n_other|0.000|0.000|
|20|tool_switches|0.348|0.146|
|20|mean_result_chars|0.030|0.242|
|20|recent_result_chars|0.281|0.179|
|20|n_assistant_messages|8.723|1.000|
|20|last_action_edit|-0.126|0.053|
|20|last_action_test|-0.276|0.078|
|40|n_errors|1.753|0.658|
|40|error_rate|1.753|0.658|
|40|recent_error_rate|0.518|0.181|
|40|error_streak|0.360|0.068|
|40|max_error_streak|1.226|0.509|
|40|n_unique_actions|-1.082|0.566|
|40|repeat_action_rate|1.082|0.566|
|40|recent_repeat_rate|0.942|0.351|
|40|n_edits|0.169|0.130|
|40|n_reads|0.076|0.279|
|40|n_searches|-0.564|0.339|
|40|n_tests|-0.197|0.091|
|40|n_shell|0.593|0.286|
|40|n_other|-0.059|0.008|
|40|tool_switches|0.523|0.219|
|40|mean_result_chars|0.201|0.306|
|40|recent_result_chars|0.077|0.136|
|40|n_assistant_messages|11.420|1.000|
|40|last_action_edit|0.022|0.009|
|40|last_action_test|-0.080|0.027|