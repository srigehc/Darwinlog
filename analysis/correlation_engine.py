from datetime import datetime, timedelta
import json

def parse_ts(ts):
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    return datetime.fromisoformat(ts)

WINDOWS = {
    "DOCOM": (timedelta(seconds=-5), timedelta(seconds=5)),
    "SBX":   (timedelta(seconds=-2), timedelta(seconds=10)),
    "HL7":  (timedelta(seconds=-5), timedelta(seconds=30)),
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

    # SYSTEM-anchored correlation
    for se in by_source.get("SYSTEM", []):
        T = se["ts"]

        docom_matches = [
            e for e in by_source.get("DOCOM", [])
            if T + WINDOWS["DOCOM"][0] <= e["ts"] <= T + WINDOWS["DOCOM"][1]
        ]

        sbx_matches = [
            e for e in by_source.get("SBX", [])
            if T + WINDOWS["SBX"][0] <= e["ts"] <= T + WINDOWS["SBX"][1]
        ]

        hl7_matches = [
            e for e in by_source.get("HL7", [])
            if T + WINDOWS["HL7"][0] <= e["ts"] <= T + WINDOWS["HL7"][1]
        ]

        rows.append({
            "system_time": se["timestamp"],
            "system_event": se["message"],
            "DOCOM_count": len(docom_matches),
            "SBX_count": len(sbx_matches),
            "HL7_count": len(hl7_matches),
        })
    
    return rows

if __name__ == "__main__":
    INPUT_JSON = "output/normalized_logs.json"

    rows = correlate(INPUT_JSON)

    print(f"✅ Correlation rows generated: {len(rows)}")

    # Print first 20 rows for sanity
    for r in rows[:20]:
        print(
            f"{r['system_time']} | "
            f"DOCOM={r['DOCOM_count']} | "
            f"SBX={r['SBX_count']} | "
            f"HL7={r['HL7_count']} | "
            f"{r['system_event'][:50]}"
        )
