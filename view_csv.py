import csv

rows = list(csv.DictReader(open('output/correlation_table.csv')))
print('CSV Columns:', list(rows[0].keys()))

print('\n' + '='*100)
print('Sample rows with correlations:')
print('='*100)

with_matches = [r for r in rows if r['SBX_count'] != '0' or r['DOCOM_count'] != '0' or r['HL7_count'] != '0']
for i, row in enumerate(with_matches[:3]):
    print(f"\nRow {i+1}:")
    print(f"  System Time: {row['system_time']}")
    print(f"  System Event: {row['system_event']}")
    print(f"  SBX Count: {row['SBX_count']}")
    if row['SBX_events']:
        print(f"    Events: {row['SBX_events'][:150]}")
    print(f"  DOCOM Count: {row['DOCOM_count']}")
    if row['DOCOM_events']:
        print(f"    Events: {row['DOCOM_events'][:150]}")
    print(f"  HL7 Count: {row['HL7_count']}")
    if row['HL7_events']:
        print(f"    Events: {row['HL7_events'][:150]}")

print(f"\n\nTotal rows: {len(rows)}")
print(f"Rows with at least one correlation: {len(with_matches)}")
