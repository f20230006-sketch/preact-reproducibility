# PreAct targeted literature mapping protocol, v1.0

Date: 4 October 2026 (Asia/Dubai). This documents an expansion of an existing 22-paper targeted review. It is retrospective for the inherited seed set and prospective for the current extraction. It is not a registered systematic review or an independently double-screened review.

## Questions

1. What does a monitor predict: terminal outcome, an error boundary, unsafe reachability, process defects, or intervention utility?
2. What observations exist before the decision, and what information requires future execution or benchmark reference solutions?
3. Which evaluations establish unseen-task, unseen-model, unseen-scaffold, or unseen-domain validity?
4. Which studies measure downstream effects, disruption, cost, and uncertainty rather than prediction alone?
5. What narrowly supported contribution remains for the existing PreAct pilot?

## Scope and search

Primary agent studies from January 2022 through 4 October 2026; older calibration foundations may be included as methodological context. English-language sources. Search combinations of agent/trajectory/prefix/tool use with failure prediction/early warning/runtime monitoring/restart/recovery/process reward/calibration/transfer. Follow references and author-maintained trajectory-analysis bibliographies. Verify identity and versions against primary arXiv records; inspect full-text methods and results for included papers. Treat comments about acceptance as author-reported status unless a proceedings record is also checked.

The current search uses public web discovery, arXiv, author repositories, and reference chaining. No authenticated Scopus, Web of Science, ACM DL, or IEEE Xplore database export was performed. Consequently, the corpus is an auditable targeted evidence map, not an exhaustive census. Search results may differ on repetition. Record exact discovery queries and retrieved identifiers; do not fabricate database hit counts or a PRISMA denominator.

## Eligibility and relevance

- Category 1: direct prefix/pre-action prediction, early termination, monitor transfer/calibration, or online predictor-to-intervention evaluation. Safety prediction is included with a separate target label.
- Category 2: adjacent diagnosis, error attribution, process-quality assessment, deterministic runtime enforcement, recovery, or empirical trajectory/failure analysis.
- Category 3: agent architectures, benchmarks, evaluator validity, calibration foundations, and cross-domain predictive-monitoring precedent. These supply context, not direct evidence of PreAct-style effectiveness.

Exclude unrelated sensing/predictive maintenance, ordinary one-shot chat evaluation, speculative decoding without reliability monitoring, and redundant versions. Broad surveys are discovery aids, not independent primary experimental evidence. The local PreAct pilot is not counted as an external paper or peer-reviewed study.

## Extraction and assessment

One record per paper/version, preserving shared benchmark dependence. Fields: identifier, full authors, title, first date, inspected version, status, domain, target, observable representation, method, split, calibration, transfer, downstream intervention/control, quantitative findings with source location, artifacts, limitation, reviewer-assessed gap, and proposed future experiment. Record NR when evidence was not extracted; NR does not prove the study omitted it.

Full-text verification is reading and source checking, not independent reproduction. Do not invent confidence intervals or unavailable metrics. Do not interpret accuracy, AUROC, safety reduction, failure recovery conditional on a failed run, and population task-success improvement as interchangeable.

## Synthesis

Use an evidence map and narrative contrasts. Do not pool AUROC or percentage gains across incompatible benchmarks, agents, prefixes, and denominators. Separate authors' results from reviewer proposals. Strong novelty claims require identifying prior work that already performs transfer, calibration, matched-prefix repair, and intervention validation. Preserve negative and qualified findings.

## Remaining review limitations

One assistant performed screening and extraction; human independent review remains pending. Sources are predominantly preprints; no quality score implies peer review. Long author lists and versions are machine-extracted and should receive a final author audit before submission. No off-platform search or source access is claimed. Source cache is excluded from GitHub distribution.
