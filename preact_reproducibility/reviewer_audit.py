"""Check prefix invariance and measure offline monitor overhead on real data.

Timing excludes downloads and original agent execution; not a deployment benchmark.
"""
import copy
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import matplotlib
import numpy as np
import sklearn
import scipy
from preact_pilot import FEATURES, extract, load_data, split_for
from preact_pilot_audit import fit_and_select

ROOT = Path(__file__).resolve().parent


def main():
    # Appending arbitrary future failures must not alter the earlier prefix.
    events = []
    for i in range(20):
        events += [{"type": "tool_call", "tool": "read", "input": {"path": str(i)}, "tool_call_id": str(i)},
                   {"type": "tool_result", "tool_call_id": str(i), "status": "success", "content": "observed"}]
    trace = {"events": events, "evaluation": {"resolved": True}}
    original = extract(trace, 20)
    changed = copy.deepcopy(trace)
    changed["evaluation"]["resolved"] = False
    changed["events"] += [{"type": "assistant_message", "content": "future final answer"},
                          {"type": "tool_call", "tool": "write", "tool_call_id": "future", "input": {}},
                          {"type": "tool_result", "tool_call_id": "future", "status": "error", "content": "future error"}]
    assert original == extract(changed, 20)
    assert extract({"events": events[:10]}, 20) is None
    start = time.perf_counter()
    rows = load_data()
    load_seconds = time.perf_counter() - start
    assert rows, "No source trajectories found; set PREACT_DATA_ROOT before running."
    assignments = {}
    for row in rows:
        assignments.setdefault(row['instance'], set()).add(row['split'])
    assert all(len(s) == 1 for s in assignments.values())
    assert all(r['split'] == split_for(r['instance']) for r in rows)
    cp = [r for r in rows if r['checkpoint'] == 20 and r['participant'] != 'qwen3.6-27b']
    train = [r for r in cp if r['split'] == 'train']
    val = [r for r in cp if r['split'] == 'val']
    test = [r for r in cp if r['split'] == 'test']
    start = time.perf_counter()
    ap, name, model = fit_and_select(train, val)
    fit_seconds = time.perf_counter() - start
    X = np.array([r['features'] for r in test])
    model.predict_proba(X)
    timings = []
    for _ in range(20):
        start = time.perf_counter()
        model.predict_proba(X)
        timings.append(time.perf_counter() - start)
    result = {
        'scope': 'Current-machine offline CPU timing; original agent execution and downloads excluded. Batch inference is not single-request latency.',
        'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scikit_learn': sklearn.__version__,
                        'matplotlib': matplotlib.__version__, 'scipy': scipy.__version__, 'omp_num_threads': os.environ.get('OMP_NUM_THREADS'), 'platform': platform.platform(), 'processor': platform.processor(),
                        'logical_cpu_count': os.cpu_count()},
        'checks': {'future_suffix_and_terminal_label_invariance': True, 'short_prefix_excluded': True, 'task_split_disjointness': True},
        'feature_count': len(FEATURES), 'task_counts': {s: sum(s in v for v in assignments.values()) for s in ('train','val','test')},
        'feature_rows': len(rows), 'load_and_extract_seconds': load_seconds,
        'checkpoint_20': {'train_n': len(train), 'validation_n': len(val), 'test_n': len(test), 'selected_model': name,
                          'validation_auprc': float(ap), 'fit_two_candidates_seconds': fit_seconds,
                          'batch_predict_median_ms': float(np.median(timings)*1000),
                          'amortized_predict_us_per_row': float(np.median(timings)*1e6/len(test))},
        'script_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('preact_*.py')}
    }
    out = ROOT/'results/reviewer_audit.json'
    out.write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
