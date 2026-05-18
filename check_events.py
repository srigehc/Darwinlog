import json
import csv
from collections import Counter

# Load normalized events
with open('output/normalized_logs.json') as f:
    events = json.load(f)

print(f"Total events: {len(events)}\n")
print("Event types distribution:")
types = Counter(e.get('event_type') for e in events)
for t, count in types.most_common():
    print(f"  {t}: {count}")

print("\n\nFirst 20 system events (sample):")
system_events = [e for e in events if e.get('source') == 'SYSTEM']
for i, e in enumerate(system_events[:20]):
    msg = e.get('message', '')[:70]
    print(f"  {i+1}. {msg}")

print(f"\n\nTotal SYSTEM events: {len(system_events)}")

# Check correlation data
print("\n\nCorrelation table sample:")
with open('output/correlation_table.csv') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 10:
            break
        msg = row.get('system_event', '')[:70]
        sbx = row.get('SBX_count', '0')
        docom = row.get('DOCOM_count', '0')
        hl7 = row.get('HL7_count', '0')
        print(f"  {msg}")
        print(f"    → SBX:{sbx} DoCom:{docom} HL7:{hl7}")
