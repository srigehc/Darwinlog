import json

events = json.load(open('output/normalized_logs.json'))
hl7 = [e for e in events if e['source']=='HL7']

print(f'Total HL7 events: {len(hl7)}')
print(f'With timestamps: {sum(1 for e in hl7 if e.get("timestamp"))}')
print(f'\nFirst 5 HL7 events:')
for e in hl7[:5]:
    print(f"  {e.get('timestamp')} | {e.get('message', 'N/A')}")
