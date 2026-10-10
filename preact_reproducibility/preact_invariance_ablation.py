"""Test whether normalized, scaffold-light features transfer better at 20 calls."""
import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from preact_pilot import FEATURES, load_data

ROOT = Path(__file__).resolve().parent
rows = [r for r in load_data() if r["checkpoint"] == 20]

def vectors(rs, kind):
    X = np.array([r["features"] for r in rs])
    if kind == "all": return X
    take = ["error_rate", "recent_error_rate", "error_streak", "max_error_streak",
            "repeat_action_rate", "recent_repeat_rate", "tool_switches",
            "mean_result_chars", "recent_result_chars", "last_action_edit", "last_action_test"]
    x = X[:, [FEATURES.index(k) for k in take]].copy()
    x[:, 6] /= 19
    x[:, 7:9] = np.log1p(x[:, 7:9])
    if kind == "rates": return x
    cats = ["n_edits", "n_reads", "n_searches", "n_tests", "n_shell", "n_other"]
    return np.column_stack([x, X[:, [FEATURES.index(k) for k in cats]] / 20])

def metrics(rs, p):
    y = np.array([r["failure"] for r in rs])
    return {"n":len(rs), "auroc":round(float(roc_auc_score(y,p)),3),
            "auprc":round(float(average_precision_score(y,p)),3),
            "brier":round(float(brier_score_loss(y,p)),3)}

train = [r for r in rows if r["participant"] != "qwen3.6-27b" and r["split"] == "train"]
val = [r for r in rows if r["participant"] != "qwen3.6-27b" and r["split"] == "val"]
source = [r for r in rows if r["participant"] != "qwen3.6-27b" and r["split"] == "test"]
transfer = [r for r in rows if r["participant"] == "qwen3.6-27b" and r["split"] == "test"]
out = []
for kind in ("all", "rates", "rates_plus_tool_mix"):
    for name, model in (
        ("logistic", make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.3))),
        ("hist_gradient_boosting", HistGradientBoostingClassifier(max_iter=90, max_leaf_nodes=7, learning_rate=0.04, l2_regularization=2, random_state=2026)),
    ):
        model.fit(vectors(train,kind), [r["failure"] for r in train])
        out.append({"features":kind,"model":name,
                    "validation":metrics(val,model.predict_proba(vectors(val,kind))[:,1]),
                    "source_test":metrics(source,model.predict_proba(vectors(source,kind))[:,1]),
                    "new_agent_test":metrics(transfer,model.predict_proba(vectors(transfer,kind))[:,1])})
target = ROOT / "results/preact_invariance_ablation_results.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
