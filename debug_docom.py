import json
from datetime import datetime, timedelta

with open('output/normalized_logs.json') as f:
    all_events = json.load(f)

# Test DOCOM correlation directly
system_events = [e for e in all_events if e['source'] == 'SYSTEM' and e.get('timestamp')]
docom_events = [e for e in all_events if e['source'] == 'DO_COM' and e.get('timestamp')]

DOCOM_WINDOW = (timedelta(seconds=-30), timedelta(seconds=5))

print(f"Total SYSTEM events: {len(system_events)}")
print(f"Total DOCOM events: {len(docom_events)}\n")

# Check if any DOCOM event can correlate with any SYSTEM event
correlations = 0
for docom in docom_events:
    docom_ts = datetime.fromisoformat(docom['timestamp'])
    
    for system in system_events:
        system_ts = datetime.fromisoformat(system['timestamp'])
        
        # Check if within window
        diff = system_ts - docom_ts
        if DOCOM_WINDOW[0] <= diff <= DOCOM_WINDOW[1]:
            correlations += 1
            if correlations <= 5:
                print(f"✓ Match found!")
                print(f"  DOCOM: {docom_ts} | {docom['message']}")
                print(f"  SYSTEM: {system_ts} | {system['message'][:50]}")
                print(f"  Diff: {diff.total_seconds():.1f}s\n")

print(f"Total DOCOM-SYSTEM correlations: {correlations}")

# Check the window range for first DOCOM event
if docom_events:
    docom_ts = datetime.fromisoformat(docom_events[0]['timestamp'])
    print(f"\nFirst DOCOM: {docom_ts}")
    print(f"Window range: {docom_ts + DOCOM_WINDOW[0]} to {docom_ts + DOCOM_WINDOW[1]}")
    
    in_range = [s for s in system_events if datetime.fromisoformat(s['timestamp']) >= docom_ts + DOCOM_WINDOW[0] and datetime.fromisoformat(s['timestamp']) <= docom_ts + DOCOM_WINDOW[1]]
    print(f"SYSTEM events in window: {len(in_range)}")
    if in_range:
        print(f"  First: {in_range[0]['timestamp']}")
