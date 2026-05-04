import csv
import json

rows = list(csv.DictReader(open('output/correlation_table.csv')))
corr_events = [r for r in rows if r['SBX_present'] == 'True' or r['DOCOM_present'] == 'True' or r['HL7_present'] == 'True']

print(f'Events with correlations: {len(corr_events)} out of {len(rows)}')

if corr_events:
    print(f'\nFirst 10 correlated events:')
    for r in corr_events[:10]:
        print(f"{r['system_time']} | SBX={r['SBX_present']} | DOCOM={r['DOCOM_present']} | HL7={r['HL7_present']} | {r['system_event'][:50]}")
else:
    print('\n⚠️ No correlated events found!')
    print('\nChecking timestamp ranges...')
    system_times = [r['system_time'] for r in rows]
    print(f'First SYSTEM event: {system_times[0]}')
    print(f'Last SYSTEM event: {system_times[-1]}')
    
    with open('output/normalized_logs.json') as f:
        all_events = json.load(f)
    
    other_times = [e['timestamp'] for e in all_events if e['source'] != 'SYSTEM']
    print(f'\nFirst non-SYSTEM event: {min(other_times) if other_times else "None"}')
    print(f'Last non-SYSTEM event: {max(other_times) if other_times else "None"}')
