# PreAct cross-system prediction audit

Reproducible prefix-only failure prediction on 1,665 evaluated software-agent trajectories. This repository contains code and **aggregate results only**. It does not contain the source trajectories, model weights, or a demonstrated intervention policy.

## Revised interpretation

The latest source revision also reports individual outer-fold mean AUROC and sample SD alongside pooled metrics. See `PER_FOLD_RESULTS.md` and `results/per_fold_results.json`. `final_editor_revision.py` updates the same manuscript with standalone inline vector plots for the native editor. No conference submission has been made. Code and results are published at https://github.com/f20230006-sketch/preact-reproducibility.

The constant target-validation prior achieves checkpoint-20 Brier 0.223, outperforming sigmoid adaptation (0.229). Probability adaptation improves over unchanged transfer but does not establish benefit beyond this prior control. All calibration comparisons exclude target test labels from fitting.

The original task partition gives checkpoint-20 AUROC **0.700** for source systems, **0.456** for Qwen transfer and **0.691** for Qwen-specific training. The paired own-minus-transfer difference is **0.235, 95% task-bootstrap interval [-0.071, 0.459]**. Across three repeated grouped five-fold partitions, transfer AUROC is **0.463-0.562** and own-training AUROC **0.497-0.558**; the advantage changes sign. Target-validation probability adaptation improves Brier at checkpoint 20 without restoring ranking. Eligibility differs strongly by system/outcome.

These are exploratory observational findings, not established target-training superiority, a model-only effect, or prevented failures. Checkpoint 20 was emphasized after inspecting original test results; all four checkpoints and new comparisons are reported. Read [MAJOR_REVISION_RESULTS.md](MAJOR_REVISION_RESULTS.md) and [results/major_revision_results.json](results/major_revision_results.json). Original outputs remain in [COMPLETE_RESULTS.md](COMPLETE_RESULTS.md).

## Data source and access

Downloads are pinned to commit `cdae27cdd16673f0c682871ad55d325f24cc7020`; its index matches the inspected local index exactly. `results/hub_provenance.json`, `source_index.json`, and `task_manifest.json` provide provenance, hashes and task IDs. Direct pinned files are used independently of the Hub preview.

Source: [SWE-Rebench July 2026 trajectories](https://huggingface.co/datasets/ibragim-bad/swe_rebench_07_2026_trajectories), hosted on Hugging Face. The selected subset uses five runs over the same 111 tasks for `claude-code`, `gpt-5.6-luna`, and `qwen3.6-27b`. The dataset page currently identifies its license as `other`; review its terms before rehosting raw records. The downloader fetches the public index and 15 compressed shards, then checks the source-provided SHA-256 digest of **decompressed** content. Expect roughly 70 MB of compressed input plus local outputs.

## Requirements

Use Python 3.13.5 and **requirements-clean.txt**. A clean isolated rerun reproduced all four original analyses exactly and all revision fields within 1e-8. `ENVIRONMENT.md` explains verification and legacy runtime issues; `requirements-verified.txt` is a historical local snapshot, not the recommended lock. Optional bibliography verification requires `review/requirements-review.txt`.

- Python 3.13.5 for the verified clean rerun; other versions are not verified here
- Packages in `requirements.txt`
- Network access for first-time source download

Install and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-clean.txt
python download_pilot.py
python preact_pilot.py
python preact_pilot_audit.py
python preact_invariance_ablation.py
python preact_retry_opportunity.py
python visualize_results.py
python revision_analysis.py
python per_fold_audit.py
python build_major_revision.py
python final_editor_revision.py
```

The scripts write `results/*.json`. They do not call a language-model API. By default, the downloader stores source data under `data/`, which `.gitignore` excludes. To keep data elsewhere, set `PREACT_DATA_ROOT` to an absolute directory before running every script. On PowerShell:

```powershell
$env:PREACT_DATA_ROOT = 'D:\path\to\preact-data'
```

## Protocol

For the revision setup, set `OMP_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1`. `run_all.ps1` runs download, original analyses, audit and revision generation in order. Preserve the two sibling folders: manuscript generation writes into `paper_mosicom2026`.

Prediction is made after the 5th, 10th, 20th, or 40th **completed tool result**. Features use only preceding calls and observations; final answers, evaluation labels, future trajectory length, and reference patches are excluded. Task IDs are hashed with nominal 60/20/20 assignment probabilities; actual counts are **78/16/17 tasks**, keeping repeated attempts together. Logistic regression and a small histogram gradient-boosted classifier are selected by validation AUPRC independently at each checkpoint. Qwen is entirely absent from pooled training and validation for transfer evaluation. The audit script uses 2,000 task-cluster bootstrap resamples for AUROC intervals.

The three systems differ in model and scaffold, so the transfer result does not isolate model weights from harness behavior. Only 17 distinct tasks fall in the test partition. The dataset does not identify the first causal failure or contain randomized intervention branches; it cannot measure a warning horizon or prevention benefit.

## Repository layout

| File | Role |
|---|---|
| `download_pilot.py` | Fetch and verify the selected public data |
| `preact_pilot.py` | Prefix feature extraction, model selection, primary metrics |
| `preact_pilot_audit.py` | Per-agent controls, task-cluster intervals, alarm operating points |
| `preact_invariance_ablation.py` | Scaffold-light feature variants |
| `preact_retry_opportunity.py` | Descriptive repeat-attempt analysis; not a causal restart estimate |
| `results/*.json` | Saved aggregate outputs from the September 2026 run |
| `revision_analysis.py` | Paired uncertainty, grouped partitions, eligibility, calibration, ECDF baseline and drift |
| `build_major_revision.py` | Current manuscript, revision figures and complete report |
| `results/task_manifest.json` | Task IDs, groups and source digests |
| `verify_release_sources.py` | Optional network checks of cited identities and pinned index |

## Expanded literature review

The `review/` folder contains the 40-paper extraction, categories, detailed summaries and gaps, search protocol, bibliography and supplementary evidence map. The main paper uses a compact closest-study table. `review/bibliography_verification.json` documents current successful identity checks for all 23 cited arXiv records. Verification and extraction do not imply independent replication. Copied full texts are excluded from the archive.

## Citation and reuse

Cite the source dataset when using the traces and cite the corresponding research paper if using this analysis. The code in this folder is under the MIT License; source trajectory data remain governed by their source terms. No personal data or credentials are included in this repository package.

## Figures and complete results
`visualize_results.py` regenerates original curves and ablations. `build_major_revision.py` regenerates the empirical base source/figures; follow it with `final_editor_revision.py` for the current inline-vector manuscript and per-fold table. Keep the existing editor open and compile that saved source with the native compiler. An older disk PDF is excluded from the archive until the updated preview is exported. Old `update_paper_visuals.py` and `review/strengthen_paper.py` are legacy helpers. Original graphs/results remain supplementary.
