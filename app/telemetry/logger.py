import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("data/processed/telemetry.jsonl")

def log_event(event):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    item = dict(event)
    item.setdefault("timestamp", datetime.now().isoformat())
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def get_events():
    if not LOG_FILE.exists():
        return []
    rows = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return rows[-500:]
