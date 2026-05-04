import csv
import json
from collections import Counter

# Load correlation results
rows = list(csv.DictReader(open('output/correlation_table.csv')))

# Count correlations
sbx_corr = sum(1 for r in rows if r['SBX_present'] == 'True')
docom_corr = sum(1 for r in rows if r['DOCOM_present'] == 'True')
hl7_corr = sum(1 for r in rows if r['HL7_present'] == 'True')

print("=" * 70)
print("CORRELATION SUMMARY REPORT")
print("=" * 70)
print(f"\nTotal SYSTEM events analyzed: {len(rows)}")
print(f"\nCorrelation Coverage:")
print(f"  SBX events found:   {sbx_corr:4d} ({100*sbx_corr/len(rows):5.1f}%)")
print(f"  DOCOM events found: {docom_corr:4d} ({100*docom_corr/len(rows):5.1f}%)")
print(f"  HL7 events found:   {hl7_corr:4d} ({100*hl7_corr/len(rows):5.1f}%)")

# Count multi-source correlations
no_corr = sum(1 for r in rows if r['SBX_present'] != 'True' and r['DOCOM_present'] != 'True' and r['HL7_present'] != 'True')
all_three = sum(1 for r in rows if r['SBX_present'] == 'True' and r['DOCOM_present'] == 'True' and r['HL7_present'] == 'True')

print(f"\nEvents with NO correlations:  {no_corr:4d} ({100*no_corr/len(rows):5.1f}%)")
print(f"Events with all 3 sources:    {all_three:4d} ({100*all_three/len(rows):5.1f}%)")

# Get SBX/DOCOM/HL7 event counts from normalized logs
with open('output/normalized_logs.json') as f:
    all_events = json.load(f)

sources = Counter(e['source'] for e in all_events)
print(f"\nSource Event Counts (normalized_logs.json):")
print(f"  SYSTEM:  {sources.get('SYSTEM', 0):4d}")
print(f"  SBX:     {sources.get('SBX', 0):4d}")
print(f"  DOCOM:   {sources.get('DO_COM', 0):4d}")
print(f"  HL7:     {sources.get('HL7', 0):4d}")
print(f"  Total:   {len(all_events):4d}")

print("\n" + "=" * 70)
print("Sample correlated events with SBX matches:")
print("=" * 70)
sbx_events = [r for r in rows if r['SBX_present'] == 'True'][:5]
for r in sbx_events:
    print(f"\n{r['system_time']}")
    print(f"  Event: {r['system_event']}")
    print(f"  Matches: SBX={r['SBX_count']}, DOCOM={r['DOCOM_count']}, HL7={r['HL7_count']}")

print("\n" + "=" * 70)
