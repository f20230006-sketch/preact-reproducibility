"""Task-cluster uncertainty, within-agent controls, and alarm operating points."""
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from preact_pilot import load_data

ROOT = Path(__file__).resolve().parent
RNG = np.random.default_rng(20260930)


def candidate_models():
    return {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.3)),
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=90, max_leaf_nodes=7, learning_rate=0.04, l2_regularization=2, random_state=2026),
    }


def fit_and_select(train, val):
    X = np.array([r["features"] for r in train]); y = np.array([r["failure"] for r in train])
    Xv = np.array([r["features"] for r in val]); yv = np.array([r["failure"] for r in val])
    ranked = []
    for name, model in candidate_models().items():
        model.fit(X, y)
        ranked.append((average_precision_score(yv, model.predict_proba(Xv)[:, 1]), name, model))
    return max(ranked, key=lambda t: t[0])


def report(test, p):
    y = np.array([r["failure"] for r in test])
    return {"n": len(y), "tasks": len(set(r["instance"] for r in test)),
            "failure_rate": round(float(y.mean()), 3),
            "auroc": round(float(roc_auc_score(y, p)), 3),
            "auprc": round(float(average_precision_score(y, p)), 3),
            "brier": round(float(brier_score_loss(y, p)), 3)}


def task_bootstrap(test, p, reps=2000):
    tasks = sorted(set(r["instance"] for r in test))
    indices = {t: [i for i, r in enumerate(test) if r["instance"] == t] for t in tasks}
    y = np.array([r["failure"] for r in test])
    vals = []
    for _ in range(reps):
        chosen = RNG.choice(tasks, size=len(tasks), replace=True)
        idx = [i for task in chosen for i in indices[task]]
        if len(set(y[idx])) < 2: continue
        vals.append(roc_auc_score(y[idx], p[idx]))
    return [round(float(v), 3) for v in np.quantile(vals, [0.025, 0.975])]


def alarm(val, test, pv, pt, target_fpr=0.1):
    yv = np.array([r["failure"] for r in val]); yt = np.array([r["failure"] for r in test])
    success_scores = pv[yv == 0]
    # Strictly above the empirical (1-alpha) quantile; no test-set tuning.
    cutoff = float(np.quantile(success_scores, 1 - target_fpr))
    fired = pt > cutoff
    return {"threshold": round(cutoff, 4), "fired": int(fired.sum()),
            "false_alarm_rate": round(float(fired[yt == 0].mean()), 3),
            "failure_recall": round(float(fired[yt == 1].mean()), 3)}


def main():
    data = load_data()
    output = {"method": "fixed tool-call checkpoints; instance_id task split; 2000 task-cluster bootstrap resamples", "cases": [], "transfer_cases": []}
    for cp in (5, 10, 20):
        cp_rows = [r for r in data if r["checkpoint"] == cp]
        for participant in ("claude-code", "gpt-5.6-luna", "qwen3.6-27b"):
            train = [r for r in cp_rows if r["participant"] == participant and r["split"] == "train"]
            val = [r for r in cp_rows if r["participant"] == participant and r["split"] == "val"]
            test = [r for r in cp_rows if r["participant"] == participant and r["split"] == "test"]
            if min(len(train), len(val), len(test)) == 0: continue
            validation_ap, name, model = fit_and_select(train, val)
            pv = model.predict_proba(np.array([r["features"] for r in val]))[:, 1]
            pt = model.predict_proba(np.array([r["features"] for r in test]))[:, 1]
            output["cases"].append({"checkpoint": cp, "participant": participant, "selected_model": name,
                "validation_auprc": round(float(validation_ap), 3), "test": report(test, pt),
                "auroc_task_bootstrap_95pct": task_bootstrap(test, pt),
                "alarm_at_val_10pct_fpr": alarm(val, test, pv, pt)})
        train = [r for r in cp_rows if r["participant"] != "qwen3.6-27b" and r["split"] == "train"]
        val = [r for r in cp_rows if r["participant"] != "qwen3.6-27b" and r["split"] == "val"]
        for group, test in (
            ("source_agents_unseen_tasks", [r for r in cp_rows if r["participant"] != "qwen3.6-27b" and r["split"] == "test"]),
            ("new_agent_unseen_tasks", [r for r in cp_rows if r["participant"] == "qwen3.6-27b" and r["split"] == "test"]),
        ):
            validation_ap, name, model = fit_and_select(train, val)
            pv = model.predict_proba(np.array([r["features"] for r in val]))[:, 1]
            pt = model.predict_proba(np.array([r["features"] for r in test]))[:, 1]
            output["transfer_cases"].append({"checkpoint": cp, "group": group, "selected_model": name,
                "test": report(test, pt), "auroc_task_bootstrap_95pct": task_bootstrap(test, pt),
                "alarm_at_val_10pct_fpr": alarm(val, test, pv, pt)})
    out = ROOT / "results/preact_pilot_audit_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2), encoding="utf8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__": main()
