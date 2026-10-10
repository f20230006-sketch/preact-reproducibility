"""Descriptive repeat-run opportunity, not a causal restart experiment."""
import gzip
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ.get("PREACT_DATA_ROOT", str(ROOT / "data")))
by_key = defaultdict(list)
for path in sorted((DATA_ROOT / "rebench").glob("*/*.jsonl.gz")):
    with gzip.open(path, "rt", encoding="utf8") as f:
        for line in f:
            x = json.loads(line)
            key = (x["participant"]["key"], x["instance_id"])
            success = bool(x["evaluation"]["resolved"])
            steps = x["usage"].get("steps")
            if steps is None:
                steps = sum(e.get("type") == "tool_call" for e in x["events"])
            steps = int(steps)
            by_key[key].append((success, steps))

out = {}
for participant in sorted(set(p for p, _ in by_key)):
    groups = [runs for (p, _), runs in by_key.items() if p == participant]
    failures = [(runs, i) for runs in groups for i, (ok, _) in enumerate(runs) if not ok]
    # Among other independent attempts at the same task, fraction successful.
    next_attempt_rate = sum(
        sum(ok for j, (ok, _) in enumerate(runs) if j != i) / (len(runs)-1)
        for runs, i in failures) / len(failures)
    any_other_success = sum(any(ok for j, (ok, _) in enumerate(runs) if j != i)
                            for runs, i in failures) / len(failures)
    out[participant] = {
        "tasks": len(groups), "runs_per_task": sorted(set(len(r) for r in groups)),
        "failed_runs": len(failures),
        "other_attempt_success_rate_given_failure": round(next_attempt_rate, 4),
        "share_failed_runs_with_at_least_one_other_success": round(any_other_success, 4),
        "mean_steps_success": round(sum(s for r in groups for ok,s in r if ok) /
                                    sum(ok for r in groups for ok,s in r), 1),
        "mean_steps_failure": round(sum(s for r in groups for ok,s in r if not ok) /
                                    sum(not ok for r in groups for ok,s in r), 1),
    }
target = ROOT / "results/preact_retry_opportunity_results.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
