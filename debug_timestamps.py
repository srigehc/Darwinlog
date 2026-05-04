import json
from datetime import datetime

with open('output/normalized_logs.json') as f:
    all_events = json.load(f)

# Group by source and get time ranges
by_source = {}
for e in all_events:
    source = e['source']
    ts = e['timestamp']
    if source not in by_source:
        by_source[source] = []
    by_source[source].append(ts)

print("=" * 80)
print("TIMESTAMP RANGES BY SOURCE")
print("=" * 80)

for source in ['SYSTEM', 'SBX', 'DO_COM', 'HL7']:
    if source in by_source:
        times = sorted([t for t in by_source[source] if t is not None])
        if times:
            print(f"\n{source}:")
            print(f"  Count:  {len(times)}")
            print(f"  First:  {times[0]}")
            print(f"  Last:   {times[-1]}")
            print(f"  Sample: {times[len(times)//2]}")
        else:
            print(f"\n{source}: No valid timestamps")

print("\n" + "=" * 80)
print("OVERLAP ANALYSIS")
print("=" * 80)

system_times = set(by_source.get('SYSTEM', []))
docom_times = set(by_source.get('DO_COM', []))
hl7_times = set(by_source.get('HL7', []))
sbx_times = set(by_source.get('SBX', []))

print(f"\nExact timestamp matches (SYSTEM timestamp = other timestamp):")
print(f"  SYSTEM ∩ SBX:   {len(system_times & sbx_times)}")
print(f"  SYSTEM ∩ DOCOM: {len(system_times & docom_times)}")
print(f"  SYSTEM ∩ HL7:   {len(system_times & hl7_times)}")

# Check if there's ANY time overlap
if docom_times:
    docom_min = min(docom_times)
    docom_max = max(docom_times)
    system_min = min(system_times)
    system_max = max(system_times)
    
    print(f"\nTime range overlap (DOCOM vs SYSTEM):")
    print(f"  DOCOM range:  {docom_min} to {docom_max}")
    print(f"  SYSTEM range: {system_min} to {system_max}")
    
    if docom_min <= system_max and system_min <= docom_max:
        print(f"  ✓ Ranges OVERLAP")
    else:
        print(f"  ✗ Ranges DO NOT overlap!")

if hl7_times:
    hl7_min = min(hl7_times)
    hl7_max = max(hl7_times)
    
    print(f"\nTime range overlap (HL7 vs SYSTEM):")
    print(f"  HL7 range:   {hl7_min} to {hl7_max}")
    print(f"  SYSTEM range: {system_min} to {system_max}")
    
    if hl7_min <= system_max and system_min <= hl7_max:
        print(f"  ✓ Ranges OVERLAP")
    else:
        print(f"  ✗ Ranges DO NOT overlap!")

print("\n" + "=" * 80)
