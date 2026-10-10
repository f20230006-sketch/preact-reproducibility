# PreAct: cross-system failure-prediction reliability audit

Reproducibility package for **Cross-System Transfer in Prefix-Based Software-Agent Failure Prediction**.

Author: **Yuvaraj Nayak**, Department of Computer Science, BITS Pilani, Dubai Campus.

This is an empirical evaluation study using 1,665 public software-agent traces from three systems over 111 shared tasks. It does not implement or demonstrate an intervention controller.

## What the evidence shows

- Original checkpoint-20 AUROC: source systems **0.700**, unchanged Qwen transfer **0.456**, Qwen-specific training **0.691**.
- Paired target-trained minus transferred difference: **0.235**, task-bootstrap 95% interval **[-0.071, 0.459]**.
- The target-training advantage changes sign across repeated grouped evaluations. Within-fold summaries are reported separately from pooled predictions.
- Eligibility changes strongly by system and outcome. Target-validation recalibration improves over unchanged scores but does not beat the constant target-validation prior at checkpoint 20.

These are exploratory reliability findings, not evidence of universal transfer failure, target-training superiority, or prevented failures.

## Layout

| Path | Contents |
|---|---|
| [preact_reproducibility](preact_reproducibility) | Analysis scripts, environment lock, all numerical reports, source manifests, and literature review |
| [paper_mosicom2026](paper_mosicom2026) | Current standalone LaTeX source, inline vector plots, supplied author metadata and review-response documents |
| `archive_manifest.json` | SHA-256 digests of the published file snapshot; the manifest itself is excluded from its own hash list |

The older saved manuscript PDF is deliberately excluded: export the current compiled editor preview rather than supplying a stale PDF. Nothing has been submitted to a conference. The official MoSICom website does not state an anonymity requirement; the paper uses the user-supplied author information.

## Reproduce

Use Python **3.13.5**. On Windows PowerShell:

```powershell
git clone https://github.com/f20230006-sketch/preact-reproducibility.git
cd preact-reproducibility
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r preact_reproducibility/requirements-clean.txt
cd preact_reproducibility
.\run_all.ps1
```

The downloader uses pinned Hub commit `cdae27cdd16673f0c682871ad55d325f24cc7020`, verifies the index and decompressed shard hashes, and downloads raw data locally into an ignored directory. It does not depend on the Hub preview. No GPU or language-model API is needed for the analysis. Preserve the two sibling folders because manuscript generation uses that layout.

Read [the detailed instructions](preact_reproducibility/README.md), [complete revision results](preact_reproducibility/MAJOR_REVISION_RESULTS.md), [per-fold results](preact_reproducibility/PER_FOLD_RESULTS.md), and [outcome conventions](preact_reproducibility/OUTCOME_CONVENTION.md). The native editor compiles the current standalone source; export its preview to obtain a current manuscript PDF.

## Verification and limitations

A clean isolated environment reproduced the four original analyses exactly and revision numerical fields within 1e-8 on the same data/code. This is environment portability, not independent-data replication. See [ENVIRONMENT.md](preact_reproducibility/ENVIRONMENT.md) and [the comparison report](preact_reproducibility/results/clean_replication_check.json).

One dataset and three jointly changing model/scaffold systems limit generalization. Bootstrap intervals condition on fitted models; repeated seeds are not independent datasets. Missing later prefixes of short runs prevent identifying full-population selection-adjusted performance. Intervention utility and fairness remain unmeasured.

## Data and licensing

Code is under the [MIT License](LICENSE). Source traces retain their source terms and are **not redistributed**. Copied research-paper full texts, credentials, local environment directories and repository history are excluded. Literature files contain original summaries, primary-source links and evidence qualifications.
