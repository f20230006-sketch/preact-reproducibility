# Publication verification

Checked 11 October 2026 against the staged publication snapshot.

- 21 Python source files parsed successfully.
- Prefix invariance to future observations and terminal labels passed; incomplete prefixes were excluded.
- Real-data task grouping kept all repeated attempts together over 111 tasks.
- Source checkpoint-20 metrics matched the stored four-decimal output exactly: AUROC **0.6998**, AP **0.7301**, Brier **0.2145**. The paper rounds AUROC to **0.700**.
- Transfer **0.4561**, target-trained **0.6911**, and target-validation prior Brier **0.2227** were recomputed from inspected traces.
- Individual-fold means/SDs matched the saved fold outputs and all five task folds partitioned the 111 tasks exactly.
- All 24 bibliography keys were cited; the three standalone inline vector figures and supplied author block were present.
- No raw data, copied full-text source cache, credentials or local user paths were present in the publication snapshot.
- The current source compiled successfully with the native document editor. No stale manuscript PDF was included.

The fresh numerical gate was `python preact_reproducibility/verify_publication.py` with PREACT_DATA_ROOT pointing outside the release snapshot to the inspected local source data and OpenMP/OpenBLAS thread counts set to one. This release gate is intended for a clean snapshot, not a data-populated working folder. The earlier clean-environment comparison is separately documented in `results/clean_replication_check.json`.

Pre-publication review covered source-data integrity, target-test exclusion, code execution boundaries, outcome conventions and release hygiene. No unresolved critical publication issue was found. This verification does not establish independent-data replication, conference acceptance or intervention benefits.
