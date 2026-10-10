"""Leakage-aware prefix failure-prediction pilot on SWE-Rebench traces.

This is observational prediction only. It does not estimate intervention effects.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ.get("PREACT_DATA_ROOT", str(ROOT / "data")))
CHECKPOINTS = (5, 10, 20, 40)
FEATURES = (
    "n_errors", "error_rate", "recent_error_rate", "error_streak", "max_error_streak",
    "n_unique_actions", "repeat_action_rate", "recent_repeat_rate", "n_edits",
    "n_reads", "n_searches", "n_tests", "n_shell", "n_other",
    "tool_switches", "mean_result_chars", "recent_result_chars",
    "n_assistant_messages", "last_action_edit", "last_action_test",
)


def split_for(instance_id: str) -> str:
    n = int(hashlib.sha256(instance_id.encode()).hexdigest()[:12], 16) % 10
    return "train" if n < 6 else ("val" if n < 8 else "test")


def action_category(event: dict) -> str:
    tool = str(event.get("tool", "")).lower()
    inp = event.get("input", {})
    if not isinstance(inp, dict):
        inp = {"value": str(inp)}
    command = str(inp.get("command", "")).lower()
    if tool in {"edit", "write", "replace", "create"} or re.search(r"\b(sed|perl|apply_patch|cat\s*>|tee)\b", command):
        return "edit"
    if re.search(r"\b(pytest|unittest|npm test|yarn test|go test|cargo test|mvn test|gradle test)\b", command):
        return "test"
    if tool in {"read", "open", "scroll_down", "goto"} or re.search(r"\b(cat|head|tail|less)\b", command):
        return "read"
    if tool in {"grep", "glob", "search_file"} or re.search(r"\b(grep|rg|find|ls|dir)\b", command):
        return "search"
    if tool in {"bash", "bash_terminal"}:
        return "shell"
    return "other"


def action_fingerprint(event: dict) -> str:
    inp = event.get("input", {})
    # Exact prefix-visible action repetition, excluding unstable call IDs.
    return str(event.get("tool", "")).lower() + ":" + json.dumps(inp, sort_keys=True, default=str)[:500]


def extract(trace: dict, checkpoint: int):
    calls = []
    result_by_id = {}
    assistant_count = 0
    for e in trace["events"]:
        typ = e.get("type")
        if typ == "assistant_message":
            assistant_count += 1
        elif typ == "tool_result":
            result_by_id[e.get("tool_call_id")] = e
        elif typ == "tool_call":
            calls.append((e, result_by_id.get(e.get("tool_call_id"))))
        if len(calls) >= checkpoint and typ == "tool_result":
            # The checkpoint is after the Nth observed tool result.
            seen = sum(1 for c, _ in calls[:checkpoint] if c.get("tool_call_id") in result_by_id)
            if seen == checkpoint:
                break
    if len(calls) < checkpoint:
        return None
    calls = [e for e, _ in calls[:checkpoint]]
    results = [result_by_id.get(e.get("tool_call_id"), {}) for e in calls]
    if any(not r for r in results):
        return None
    categories = [action_category(e) for e in calls]
    fingerprints = [action_fingerprint(e) for e in calls]
    errors = [int(str(r.get("status", "")).lower() == "error") for r in results]
    lengths = [min(len(str(r.get("content", ""))), 65536) for r in results]
    seen = set()
    repeats = []
    for f in fingerprints:
        repeats.append(int(f in seen))
        seen.add(f)
    streak = maximum = 0
    for error in errors:
        streak = streak + 1 if error else 0
        maximum = max(maximum, streak)
    recent = min(5, checkpoint)
    values = {
        "n_errors": sum(errors), "error_rate": np.mean(errors),
        "recent_error_rate": np.mean(errors[-recent:]), "error_streak": streak,
        "max_error_streak": maximum, "n_unique_actions": len(seen),
        "repeat_action_rate": np.mean(repeats), "recent_repeat_rate": np.mean(repeats[-recent:]),
        "n_edits": categories.count("edit"), "n_reads": categories.count("read"),
        "n_searches": categories.count("search"), "n_tests": categories.count("test"),
        "n_shell": categories.count("shell"), "n_other": categories.count("other"),
        "tool_switches": sum(a != b for a, b in zip(categories, categories[1:])),
        "mean_result_chars": np.mean(lengths), "recent_result_chars": np.mean(lengths[-recent:]),
        "n_assistant_messages": assistant_count,
        "last_action_edit": int(categories[-1] == "edit"),
        "last_action_test": int(categories[-1] == "test"),
    }
    return [float(values[k]) for k in FEATURES]


def load_data():
    rows = []
    for path in sorted((DATA_ROOT / "rebench").glob("*/*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf8") as f:
            for line in f:
                x = json.loads(line)
                for cp in CHECKPOINTS:
                    features = extract(x, cp)
                    if features is not None:
                        rows.append({
                            "instance": x["instance_id"], "participant": x["participant"]["key"],
                            "run": x["run"]["index"], "checkpoint": cp,
                            "split": split_for(x["instance_id"]),
                            "failure": int(not x["evaluation"]["resolved"]),
                            "features": features,
                        })
    return rows


def metrics(rows, probs):
    y = np.array([r["failure"] for r in rows])
    if len(y) == 0 or len(set(y)) < 2:
        return {"n": len(y)}
    return {
        "n": len(y), "failure_rate": round(float(y.mean()), 4),
        "auroc": round(float(roc_auc_score(y, probs)), 4),
        "auprc": round(float(average_precision_score(y, probs)), 4),
        "brier": round(float(brier_score_loss(y, probs)), 4),
    }


def main():
    rows = load_data()
    summary = {"source": "SWE-Rebench 07/2026, 3 participants x 5 runs x 111 tasks", "checkpoints": CHECKPOINTS,
               "feature_names": FEATURES, "n_unique_trajectories": len({(r['participant'],r['run'],r['instance']) for r in rows}),
               "results": []}
    for cp in CHECKPOINTS:
        subset = [r for r in rows if r["checkpoint"] == cp]
        # Hold out qwen entirely to probe transfer; all tasks for qwen are test-only.
        train = [r for r in subset if r["split"] == "train" and r["participant"] != "qwen3.6-27b"]
        val = [r for r in subset if r["split"] == "val" and r["participant"] != "qwen3.6-27b"]
        test = [r for r in subset if r["split"] == "test" and r["participant"] != "qwen3.6-27b"]
        transfer = [r for r in subset if r["split"] == "test" and r["participant"] == "qwen3.6-27b"]
        X = np.array([r["features"] for r in train]); y = np.array([r["failure"] for r in train])
        Xv = np.array([r["features"] for r in val]); yv = np.array([r["failure"] for r in val])
        candidates = {
            "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.3)),
            "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=90, max_leaf_nodes=7, learning_rate=0.04, l2_regularization=2, random_state=2026),
        }
        fit = {}
        for name, model in candidates.items():
            model.fit(X, y)
            fit[name] = (average_precision_score(yv, model.predict_proba(Xv)[:, 1]), model)
        best_name = max(fit, key=lambda n: fit[n][0])
        model = fit[best_name][1]
        prior = float(y.mean())
        for group, data in (("held_out_tasks", test), ("held_out_agent_and_tasks", transfer)):
            if not data: continue
            Xt = np.array([r["features"] for r in data])
            probs = model.predict_proba(Xt)[:, 1]
            model_metrics = metrics(data, probs)
            prior_metrics = metrics(data, np.full(len(data), prior))
            heuristic = np.array([min(1, 0.05 + 0.35*r["features"][FEATURES.index("error_rate")] +
                                      0.5*r["features"][FEATURES.index("repeat_action_rate")]) for r in data])
            heuristic_metrics = metrics(data, heuristic)
            summary["results"].append({"checkpoint": cp, "group": group, "selected_model": best_name,
                                       "validation_auprc": round(fit[best_name][0], 4),
                                       "monitor": model_metrics, "prior": prior_metrics,
                                       "error_repeat_heuristic": heuristic_metrics})
    out = ROOT / "results/preact_pilot_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
