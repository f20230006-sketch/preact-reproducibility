# Individual outer-fold AUROC audit

Unweighted mean and sample SD of defined fold AUROCs; SD describes fold variation, not inferential uncertainty. Same tasks/seeds and outer-fold models as pooled sensitivity. Three seeds are not independent datasets.

| Checkpoint | Seed | Transfer mean (SD) | Own mean (SD) | Defined folds T/O |
|---|---|---|---|---|
|5|20261010|0.517 (0.046)|0.453 (0.036)|5/5|
|5|20261011|0.524 (0.111)|0.444 (0.074)|5/5|
|5|20261012|0.509 (0.072)|0.461 (0.078)|5/5|
|10|20261010|0.472 (0.041)|0.495 (0.072)|5/5|
|10|20261011|0.542 (0.087)|0.448 (0.098)|5/5|
|10|20261012|0.506 (0.097)|0.465 (0.045)|5/5|
|20|20261010|0.517 (0.037)|0.566 (0.061)|5/5|
|20|20261011|0.567 (0.052)|0.497 (0.116)|5/5|
|20|20261012|0.510 (0.100)|0.539 (0.085)|5/5|
|40|20261010|0.549 (0.070)|0.574 (0.078)|5/5|
|40|20261011|0.554 (0.093)|0.523 (0.045)|5/5|
|40|20261012|0.444 (0.109)|0.564 (0.091)|5/5|

Every fold score, task ID, sample count, and pooled consistency check is in `results/per_fold_results.json`. Undefined single-class folds would be excluded and counted explicitly.