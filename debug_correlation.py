from datetime import datetime, timedelta
import json

def parse_ts(ts):
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    return datetime.fromisoformat(ts)

WINDOWS = {
    "SBX":   (timedelta(seconds=-10), timedelta(seconds=10)),
    "DOCOM": (timedelta(seconds=-30), timedelta(seconds=5)),
    "HL7":   (timedelta(seconds=0), timedelta(seconds=30)),
}

with open('output/normalized_logs.json') as f:
    events = json.load(f)

# Parse timestamps
for e in events:
    e["ts"] = parse_ts(e.get("timestamp"))

events = [e for e in events if e["ts"] is not None]

# Bucket by source
by_source = {}
for e in events:
    by_source.setdefault(e["source"], []).append(e)

print(f"Events by source after bucketing:")
for source in by_source:
    print(f"  {source}: {len(by_source[source])} events")

print(f"\nDOCOM events in by_source:")
docom_count = len(by_source.get("DOCOM", []))
print(f"  Total: {docom_count}")

if docom_count > 0:
    docom = by_source["DOCOM"]
    print(f"  First: {docom[0]['timestamp']} -> parsed: {docom[0]['ts']}")
    print(f"  Last: {docom[-1]['timestamp']} -> parsed: {docom[-1]['ts']}")

# Test correlation for one SYSTEM event
system_events = by_source.get("SYSTEM", [])
print(f"\nTesting first 3 SYSTEM events:")

for i, system_event in enumerate(system_events[:3]):
    T = system_event["ts"]
    docom_matches = [
        e for e in by_source.get("DOCOM", [])
        if T + WINDOWS["DOCOM"][0] <= e["ts"] <= T + WINDOWS["DOCOM"][1]
    ]
    print(f"\n  System {i}: {system_event['timestamp']} (parsed: {T})")
    print(f"    Window: {T + WINDOWS['DOCOM'][0]} to {T + WINDOWS['DOCOM'][1]}")
    print(f"    DOCOM matches: {len(docom_matches)}")

# Check a SYSTEM event at 11:38:26 (which we know has DOCOM matches)
print(f"\n\nLooking for SYSTEM event at 2026-04-22T11:38:26:")
target_sys = [e for e in system_events if "11:38:26" in e['timestamp']]
if target_sys:
    sys_evt = target_sys[0]
    T = sys_evt["ts"]
    print(f"  Found: {sys_evt['timestamp']} (parsed: {T})")
    print(f"  Window: {T + WINDOWS['DOCOM'][0]} to {T + WINDOWS['DOCOM'][1]}")
    
    docom_matches = [
        e for e in by_source.get("DOCOM", [])
        if T + WINDOWS["DOCOM"][0] <= e["ts"] <= T + WINDOWS["DOCOM"][1]
    ]
    print(f"  DOCOM matches: {len(docom_matches)}")
    if docom_matches:
        print(f"    Sample matches:")
        for e in docom_matches[:3]:
            print(f"      {e['timestamp']} | {e['message']}")
