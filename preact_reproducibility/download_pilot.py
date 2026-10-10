"""Download a small, pinned subset of public SWE-Rebench trajectories."""
import hashlib
import gzip
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ.get("PREACT_DATA_ROOT", str(ROOT / "data")))
INDEX_PATH = DATA_ROOT / "rebench_index.jsonl"
PROVENANCE = json.loads((ROOT / 'results/hub_provenance.json').read_text(encoding='utf8'))
BASE = "https://huggingface.co/datasets/ibragim-bad/swe_rebench_07_2026_trajectories/resolve/" + PROVENANCE['revision'] + "/"
if not INDEX_PATH.exists():
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(
        BASE + "index.jsonl",
        INDEX_PATH,
    )
INDEX = [json.loads(s) for s in INDEX_PATH.read_text(encoding="utf8").splitlines()]
if hashlib.sha256(INDEX_PATH.read_bytes()).hexdigest() != PROVENANCE['index_sha256']:
    raise RuntimeError('Source index does not match the inspected pinned release')
PARTICIPANTS = {"claude-code", "gpt-5.6-luna", "qwen3.6-27b"}

for item in INDEX:
    if item["participant_key"] not in PARTICIPANTS:
        continue
    target = DATA_ROOT / "rebench" / item["path"].removeprefix("trajectories/")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        print("Downloading", item["path"], flush=True)
        urllib.request.urlretrieve(BASE + item["path"], target)
    with gzip.open(target, "rb") as stream:
        digest = hashlib.sha256(stream.read()).hexdigest()
    if digest != item["content_sha256"]:
        raise RuntimeError(f"SHA256 mismatch: {target}")
    print("Verified", target, target.stat().st_size, flush=True)
