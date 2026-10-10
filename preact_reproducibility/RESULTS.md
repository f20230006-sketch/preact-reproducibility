# Results and interpretation

Run date: 30 September 2026. Dataset: 1,665 trajectories, 111 tasks, three systems, five independent attempts per system/task. Outcome: source evaluation's unresolved flag. Fixed-checkpoint evaluation conditions on a run surviving to that tool-result count; the cohort changes across checkpoints.

| Completed tool results | Group | Runs | Failure prevalence | AUROC | AUPRC | Brier |
|---:|---|---:|---:|---:|---:|---:|
| 5 | Known systems, unseen tasks | 170 | .477 | .585 | .583 | .247 |
| 5 | New system, unseen tasks | 85 | .671 | .475 | .680 | .445 |
| 10 | Known systems, unseen tasks | 158 | .468 | .610 | .566 | .240 |
| 10 | New system, unseen tasks | 85 | .671 | .422 | .653 | .455 |
| 20 | Known systems, unseen tasks | 92 | .478 | **.700** | **.730** | **.214** |
| 20 | New system, unseen tasks | 85 | .671 | **.456** | **.647** | **.300** |
| 40 | Known systems, unseen tasks | 50 | .400 | .588 | .444 | .245 |
| 40 | New system, unseen tasks | 74 | .622 | .551 | .653 | .229 |

At 20 results, 2,000 task-cluster bootstrap replicates give AUROC intervals of **[.549, .837]** on unseen tasks from known systems and **[.303, .640]** on the unseen agent. A separate Qwen-only monitor reaches AUROC **.691** [bootstrap interval **.528, .821**], AUPRC **.795**, and Brier **.200** on that agent's held-out tasks. Rates-only feature ablations did not improve new-agent AUROC above approximately .50.

A threshold selected on known-system validation successes for nominal 10% false alarms yields, at 20 results, 29.5% failure recall and 4.2% false alarms on held-out tasks from those systems. On the new agent, it yields 8.8% recall and 10.7% false alarms. This illustrates threshold transfer failure; it is not a prevention rate.

Independent-repeat descriptive opportunity: after a failed attempt, another independent attempt at the same task succeeds 16.4% of the time for Claude Code, 15.3% for GPT-5.6-Luna, and 17.3% for Qwen3.6-27B. These fresh attempts are not matched continuations from the failed attempt's prefix.

**Conclusion:** Prefix-visible structure has some predictive utility within known systems at a mid-run checkpoint. The tested monitor does not transfer reliably to a new model/scaffold combination. These traces cannot establish that any intervention improves task success. Controlled branches at identical prefixes are the next required experiment.
