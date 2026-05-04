import json
from datetime import datetime, timedelta

events = json.load(open('output/normalized_logs.json'))

target = datetime.fromisoformat('2026-04-22T11:38:06')

system = [e for e in events if e['source']=='SYSTEM' and e.get('timestamp')]
parsed = [(e, datetime.fromisoformat(e['timestamp'])) for e in system]
nearby = [(e, ts) for e, ts in parsed if abs((ts-target).total_seconds()) < 300]

print(f"SYSTEM events within 300s of 11:38:06: {len(nearby)}\n")
print(f"{'Time':<15} | {'Message':<60}")
print("-" * 80)
for e, ts in sorted(nearby, key=lambda x: x[1])[:15]:
    time_str = ts.strftime("%H:%M:%S")
    msg = e['message'][:55]
    print(f"{time_str:<15} | {msg:<60}")

# Check DOCOM events in detail
docom_events = [e for e in events if e['source'] == 'DO_COM' and e.get('timestamp')]
print(f"\n\nAll {len(docom_events)} DOCOM events and nearest SYSTEM events:")
print("-" * 100)

for i, docom in enumerate(docom_events[:5]):
    docom_ts = datetime.fromisoformat(docom['timestamp'])
    # Find nearest SYSTEM events
    system_parsed = [(e, datetime.fromisoformat(e['timestamp'])) for e in system]
    diffs = [(e, ts, abs((ts - docom_ts).total_seconds())) for e, ts in system_parsed]
    nearest = sorted(diffs, key=lambda x: x[2])[:3]
    
    print(f"\nDOCOM {i+1}: {docom_ts} | {docom['message']}")
    for e, ts, diff in nearest:
        print(f"  -> SYSTEM at {ts} (diff: {diff:.1f}s)")
