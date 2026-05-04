from datetime import datetime, timedelta
import json
import csv
import os

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

def correlate(json_path):
    with open(json_path, encoding="utf-8") as f:
        events = json.load(f)

    # Parse timestamps
    for e in events:
        e["ts"] = parse_ts(e.get("timestamp"))

    events = [e for e in events if e["ts"] is not None]

    # Bucket by source
    by_source = {}
    for e in events:
        by_source.setdefault(e["source"], []).append(e)

    rows = []

    # SYSTEM-anchored correlation (as per design)
    for system_event in by_source.get("SYSTEM", []):
        T = system_event["ts"]

        # Look for matching events in each other source within their time windows
        sbx_matches = [
            e for e in by_source.get("SBX", [])
            if T + WINDOWS["SBX"][0] <= e["ts"] <= T + WINDOWS["SBX"][1]
        ]

        docom_matches = [
            e for e in by_source.get("DO_COM", [])
            if T + WINDOWS["DOCOM"][0] <= e["ts"] <= T + WINDOWS["DOCOM"][1]
        ]

        hl7_matches = [
            e for e in by_source.get("HL7", [])
            if T + WINDOWS["HL7"][0] <= e["ts"] <= T + WINDOWS["HL7"][1]
        ]

        # Format matched events as strings
        sbx_events_str = " | ".join([f"{e['timestamp']}: {e['message']}" for e in sbx_matches]) if sbx_matches else ""
        docom_events_str = " | ".join([f"{e['timestamp']}: {e['message']}" for e in docom_matches]) if docom_matches else ""
        hl7_events_str = " | ".join([f"{e['timestamp']}: {e['message']}" for e in hl7_matches]) if hl7_matches else ""

        rows.append({   
            "system_time": system_event["timestamp"],
            "system_event": system_event["message"],
            "SBX_count": len(sbx_matches),
            "SBX_events": sbx_events_str,
            "DOCOM_count": len(docom_matches),
            "DOCOM_events": docom_events_str,
            "HL7_count": len(hl7_matches),
            "HL7_events": hl7_events_str,
        })
    
    return rows

def save_to_csv(rows, output_path):
    """Save correlation results to CSV"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'system_time', 'system_event',
            'SBX_count', 'SBX_events',
            'DOCOM_count', 'DOCOM_events',
            'HL7_count', 'HL7_events'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ CSV saved to {output_path}")


if __name__ == "__main__":
    INPUT_JSON = "output/normalized_logs.json"
    OUTPUT_CSV = "output/correlation_table.csv"

    rows = correlate(INPUT_JSON)

    print(f"✅ Correlation rows generated: {len(rows)}")

    # Save to CSV
    save_to_csv(rows, OUTPUT_CSV)

    # Print first 10 rows for sanity
    print(f"\nSample correlated events (first 10 with matches):\n")
    with_matches = [r for r in rows if r['SBX_count'] > 0 or r['DOCOM_count'] > 0 or r['HL7_count'] > 0]
    for r in with_matches[:10]:
        print(f"SYSTEM: {r['system_time']}")
        print(f"  Event: {r['system_event'][:70]}")
        if r['SBX_count'] > 0:
            print(f"  SBX ({r['SBX_count']}): {r['SBX_events'][:100]}")
        if r['DOCOM_count'] > 0:
            print(f"  DOCOM ({r['DOCOM_count']}): {r['DOCOM_events'][:100]}")
        if r['HL7_count'] > 0:
            print(f"  HL7 ({r['HL7_count']}): {r['HL7_events'][:100]}")
        print()
