# Clean replication environment and legacy limitations

## Verified clean rerun

An isolated Python 3.13.5 environment with NumPy 2.2.6, SciPy 1.15.3, scikit-learn 1.6.1 and Matplotlib 3.10.3 reran all four original numerical analyses and the complete major-revision analysis on the same pinned traces. Original numerical outputs matched exactly. The largest difference in revision fields was 7.8e-16; no field differed beyond 1e-8. The check covers all four checkpoints and all three repeated grouped evaluation seeds. This is environment replication, not independent data collection or independent model implementation.

Use **requirements-clean.txt** as the primary full dependency lock. It includes all installed analysis dependencies from the isolated environment. Both OMP_NUM_THREADS and OPENBLAS_NUM_THREADS were one. No optimizer warning was emitted in the clean revision run. `results/clean_replication_check.json` records the comparison. The legacy snapshot below is retained for transparency, not recommended for installation.

## Legacy local runtime

The revision analyses ran on 10 October 2026 using Python 3.13.5, Windows 11, scikit-learn 1.6.1, SciPy 1.18.0, Matplotlib 3.10.9 and an imported NumPy reporting 2.5.1. OpenMP and OpenBLAS thread counts were set to one.

The NumPy installed distribution metadata reports **2.2.6**, while its imported module reports **2.5.1**. Thus this prior local environment has inconsistent metadata. `requirements-verified.txt` retains that observed snapshot under its legacy filename; use the clean lock above. The discrepancy was resolved for release verification by an isolated compatible environment, whose results matched rather than by relabeling the legacy runtime.

SciPy emits a non-fatal `OptimizeWarning: Unknown solver options: iprint` during scikit-learn logistic-regression fits. The analyses complete; all saved results correspond to this environment. Warning text is recorded here without local usernames. The original September environment is not reconstructed from this snapshot.

The manuscript's findings are measured outputs from inspected traces. The clean same-data/code rerun above establishes the reported numerical comparison for these two environments. It does not validate the statistical assumptions, eliminate task-partition sensitivity, or substitute for independent datasets and implementations.
