# PreAct MoSICoM 2026 paper draft

The current manuscript is [preact_mosicom2026.tex](preact_mosicom2026.tex), open in the native editor. The older saved `preact_mosicom2026.pdf` is not the current v5 export; export the updated preview before submission.

## Format

The [MoSICoM 2026 submission guidelines](https://mosicom2026.com/submissions), checked 10 October 2026, require IEEE conference formatting and typically at most six pages including references. This revised empirical paper uses `\documentclass[conference]{IEEEtran}`, two columns, US letter, with 24 references. The earlier saved PDF was five pages; check the page count of the current native-editor export. The author clarified that nothing has been submitted. Confirm current new-submission eligibility, anonymity and supplementary rules; no existing CMT revision is assumed. The normal IEEE author block contains the user-supplied Yuvaraj Nayak affiliation and contact details; no anonymity requirement is stated on the official website.

## Major revision

The current title is **Cross-System Transfer in Prefix-Based Software-Agent Failure Prediction**. The paper now centers measured paired uncertainty, grouped-partition sensitivity, checkpoint eligibility, target-validation adaptation and feature shift. The original target-training advantage is not robust across grouped partitions; conclusions are narrowed accordingly. Interventions are future work only.

`v5_revision_response.md` addresses the latest review; `major_revision_response.md` records the earlier substantive changes. `intervention_protocol.tex` preserves the unexecuted design as a supplementary LaTeX fragment. The full evidence map and all original ROC/PR/calibration and ablation graphs remain in the adjacent reproducibility folder. The locally prepared reproducibility ZIP is under `../release/`; the public code repository is https://github.com/f20230006-sketch/preact-reproducibility; no conference submission has been made.

Run `python build_major_revision.py` from the adjacent reproducibility folder to rebuild the current source and figures. Then run `final_editor_revision.py` and check the same saved source using the built-in compiler. The latest source embeds its vector plots and compiles successfully in the built-in editor. No separate PDF compilation or replacement document was performed for v5.

## Status

This is a research revision reporting an observational audit on 1,665 traces. It does not claim prevention or stable target-training superiority. The normal IEEE author block uses the supplied author details. Results, scripts, provenance and the verified clean lock are in the sibling `preact_reproducibility` folder.

Before upload, confirm current new-submission eligibility and anonymity/supplementary rules. Add identifying authors only if that submission requires them. Independent-data validation and intervention experiments remain necessary for broader claims.

## Build

The current v5 source embeds vector plots and compiled successfully using the built-in editor compiler. Keep this same document open. The native compiler checks the preview without exporting a disk PDF. Export the current preview, verify its page count/layout, and supply that export rather than the older saved PDF. No separate PDF compilation was performed for this revision.

## Reference and empirical visuals

The supplied IEEE template/checklist informed captions and cross-references; sample authors were not copied. Three main vector figures now show confusion matrices, paired uncertainty/eligibility, and separate AUROC/Brier comparisons. Feature-shift graphics are supplementary. Original checkpoint curves, ROC/PR/reliability, ablations and the full literature map remain supplementary. The code package includes PNG previews and both complete result reports.
