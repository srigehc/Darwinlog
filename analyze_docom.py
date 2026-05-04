import json
from datetime import datetime, timedelta

with open('output/normalized_logs.json') as f:
    all_events = json.load(f)

# Check DOCOM events
docom_events = [e for e in all_events if e['source'] == 'DO_COM']
system_events = [e for e in all_events if e['source'] == 'SYSTEM']

print("=" * 80)
print("DETAILED DOCOM ANALYSIS")
print("=" * 80)

print(f"\nTotal DOCOM events: {len(docom_events)}")
print(f"\nFirst 5 DOCOM events:")
for e in docom_events[:5]:
    print(f"\n  Timestamp: {e['timestamp']} (type: {type(e['timestamp'])})")
    print(f"  Message: {e['message']}")
    print(f"  Event type: {e.get('event_type', 'N/A')}")

# Parse a DOCOM timestamp and check if it parses correctly
print(f"\n" + "=" * 80)
print("TIMESTAMP PARSING TEST")
print("=" * 80)

if docom_events and docom_events[0]['timestamp']:
    ts_str = docom_events[0]['timestamp']
    print(f"\nDOCOM timestamp string: {ts_str}")
    try:
        ts = datetime.fromisoformat(ts_str)
        print(f"Parsed to: {ts} (type: {type(ts)})")
    except Exception as e:
        print(f"Error parsing: {e}")

# Check if SYSTEM event timestamps parse correctly
print(f"\nSYSTEM timestamp string: {system_events[0]['timestamp']}")
try:
    ts = datetime.fromisoformat(system_events[0]['timestamp'])
    print(f"Parsed to: {ts} (type: {type(ts)})")
except Exception as e:
    print(f"Error parsing: {e}")

# Now test the correlation logic manually with a specific DOCOM event
print(f"\n" + "=" * 80)
print("MANUAL CORRELATION TEST")
print("=" * 80)

docom_event = docom_events[0]
docom_ts = datetime.fromisoformat(docom_event['timestamp'])

print(f"\nDOCOM event at: {docom_ts}")

# Look for SYSTEM events within the window
WINDOWS = {
    "DOCOM": (timedelta(seconds=-10), timedelta(seconds=10)),
}

system_in_window = []
for se in system_events:
    if se['timestamp'] is None:
        continue
    try:
        se_ts = datetime.fromisoformat(se['timestamp'])
        if docom_ts + WINDOWS["DOCOM"][0] <= se_ts <= docom_ts + WINDOWS["DOCOM"][1]:
            system_in_window.append(se)
    except:
        pass

print(f"SYSTEM events within ±10s window: {len(system_in_window)}")
if system_in_window:
    print(f"Sample: {system_in_window[0]['timestamp']} - {system_in_window[0]['message'][:60]}")

print("\n" + "=" * 80)
