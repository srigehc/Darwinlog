"""Create a time-aligned, sortable view of all events so we can observe patterns mechanically.
Action
Load normalized_logs.json
Parse timestamps into datetime
Sort by timestamp
Inspect cross-source adjacency

No rules, no assumptions — just raw temporal ordering.
"""
import json
from datetime import datetime

def parse_ts(ts):
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, str):
        return datetime.fromisoformat(ts)
    return None

with open("output/normalized_logs.json", encoding="utf-8") as f:
    events = json.load(f)

for e in events:
    e["ts"] = parse_ts(e.get("timestamp"))

events = [e for e in events if e["ts"] is not None]
events.sort(key=lambda x: x["ts"])

for e in events[:50]:
    print(f"{e['timestamp']} | {e['source']} | {e['event_type']} | {e['message']}")