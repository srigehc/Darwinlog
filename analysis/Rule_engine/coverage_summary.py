import json
import csv
import os
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Path: analysis/Rule_engine/ -> go up 2 levels to project root
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

NORMALIZED_FILE = os.path.join(PROJECT_ROOT, "outputs", "normalized_logs.json")
CORRELATION_FILE = os.path.join(PROJECT_ROOT, "outputs", "correlation_table.csv")
SUMMARY_JSON = os.path.join(BASE_DIR, "coverage_summary.json")
SUMMARY_CSV = os.path.join(PROJECT_ROOT, "outputs", "coverage_summary.csv")
MISSING_CSV = os.path.join(PROJECT_ROOT, "outputs", "missing_events.csv")

# Event types that represent meaningful medical/observable events
# Exclude generic INFO and CONNECTIVITY noise
MEANINGFUL_TYPES = {
    "USER_ACTION", "ALARM", "STATE_TRANSITION", "COMMAND", 
    "LIMIT_CHANGE", "STATUS", "SBX_PARAM_CHANGE", "GAS_CONFIG", 
    "HL7_MESSAGE"
}


def load_normalized_and_correlation():
    """
    Load normalized events and build a lookup of which have correlations.
    Returns list of meaningful SYSTEM events with correlation flags.
    """
    # Load normalized events
    with open(NORMALIZED_FILE) as f:
        normalized = json.load(f)
    
    # Build correlation lookup: system_event -> (has_SBX, has_DOCOM, has_HL7)
    correlation_lookup = {}
    with open(CORRELATION_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            msg = row.get("system_event", "").strip()
            try:
                sbx_count = int(row.get("SBX_count", 0) or 0)
                docom_count = int(row.get("DOCOM_count", 0) or 0)
                hl7_count = int(row.get("HL7_count", 0) or 0)
            except (ValueError, TypeError):
                sbx_count = docom_count = hl7_count = 0
            
            if msg:
                correlation_lookup[msg] = (sbx_count > 0, docom_count > 0, hl7_count > 0)
    
    # Filter to meaningful SYSTEM events only (exclude noise like COMMAND, HL7_MESSAGE which don't have correlation data)
    meaningful_events = []
    for event in normalized:
        event_type = event.get("event_type", "")
        # Only count SYSTEM source events that are meaningful medical events
        # Exclude: COMMAND, GAS_CONFIG, HL7_MESSAGE, LIMIT_CHANGE, STATUS, SBX_PARAM_CHANGE (system noise or from other sources)
        clinically_relevant = {
            "USER_ACTION", "ALARM", "STATE_TRANSITION"
        }
        
        if event.get("source") == "SYSTEM" and event_type in clinically_relevant:
            msg = event.get("message", "").strip()
            # Only include if it has correlation data
            if msg in correlation_lookup:
                sbx, docom, hl7 = correlation_lookup[msg]
                meaningful_events.append({
                    "timestamp": event.get("timestamp"),
                    "source": event.get("source"),
                    "event_type": event_type,
                    "message": msg,
                    "SBX": sbx,
                    "DOCOM": docom,
                    "HL7": hl7
                })
    
    return meaningful_events

def generate_coverage_summary(events):
    """
    Calculate coverage from meaningful events only.
    """
    # Track coverage by event type
    overall_totals = {"total": 0, "SBX": 0, "DOCOM": 0, "HL7": 0}
    by_type = defaultdict(lambda: {"total": 0, "SBX": 0, "DOCOM": 0, "HL7": 0})
    
    missing_rows = []
    
    for event in events:
        event_type = event.get("event_type", "OTHER")
        
        # ✅ Exclude State Transition from coverage KPI
        if event_type == "STATE_TRANSITION":
            continue

        sbx = event.get("SBX", False)
        docom = event.get("DOCOM", False)
        hl7 = event.get("HL7", False)
        
        # Update overall totals
        overall_totals["total"] += 1
        overall_totals["SBX"] += int(sbx)
        overall_totals["DOCOM"] += int(docom)
        overall_totals["HL7"] += int(hl7)
        
        # Update by type
        by_type[event_type]["total"] += 1
        by_type[event_type]["SBX"] += int(sbx)
        by_type[event_type]["DOCOM"] += int(docom)
        by_type[event_type]["HL7"] += int(hl7)
        
        # Track missing coverage (events with incomplete correlation)
        if not (sbx and docom and hl7):
            missing_rows.append({
                "timestamp": event.get("timestamp", ""),
                "event": event.get("message", ""),
                "type": event_type,
                "SBX": sbx,
                "DOCOM": docom,
                "HL7": hl7,
            })
    
    # Calculate percentages
    eligible_total = overall_totals["total"]
    
    summary = {
        "overall": {
            "total": eligible_total,
            "SBX_coverage_pct": round(overall_totals["SBX"] / eligible_total * 100, 1) if eligible_total else 0,
            "DOCOM_coverage_pct": round(overall_totals["DOCOM"] / eligible_total * 100, 1) if eligible_total else 0,
            "HL7_coverage_pct": round(overall_totals["HL7"] / eligible_total * 100, 1) if eligible_total else 0,
        },
        "by_type": {}
    }
    
    for t, c in by_type.items():
        summary["by_type"][t] = {
            "total": c["total"],
            "SBX_coverage_pct": round(c["SBX"] / c["total"] * 100, 1) if c["total"] else 0,
            "DOCOM_coverage_pct": round(c["DOCOM"] / c["total"] * 100, 1) if c["total"] else 0,
            "HL7_coverage_pct": round(c["HL7"] / c["total"] * 100, 1) if c["total"] else 0,
        }
    
    return summary, missing_rows

def write_outputs(summary, missing):
    import shutil
    
    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Write CSV - use try/except in case file is locked
    csv_path = SUMMARY_CSV
    try:
        # Try to write directly
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Scope", "Total", "SBX %", "DoCom %", "HL7 %"])

            writer.writerow([
                "OVERALL",
                summary["overall"]["total"],
                summary["overall"]["SBX_coverage_pct"],
                summary["overall"]["DOCOM_coverage_pct"],
                summary["overall"]["HL7_coverage_pct"],
            ])

            for t in sorted(summary["by_type"].keys()):
                s = summary["by_type"][t]
                display_name = t.replace("_", " ").title()
                writer.writerow([
                    display_name,
                    s["total"],
                    s["SBX_coverage_pct"],
                    s["DOCOM_coverage_pct"],
                    s["HL7_coverage_pct"],
                ])
    except PermissionError:
        # If file is locked, write to alternative file
        alt_path = SUMMARY_CSV.replace(".csv", "_new.csv")
        with open(alt_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Scope", "Total", "SBX %", "DoCom %", "HL7 %"])

            writer.writerow([
                "OVERALL",
                summary["overall"]["total"],
                summary["overall"]["SBX_coverage_pct"],
                summary["overall"]["DOCOM_coverage_pct"],
                summary["overall"]["HL7_coverage_pct"],
            ])

            for t in sorted(summary["by_type"].keys()):
                s = summary["by_type"][t]
                display_name = t.replace("_", " ").title()
                writer.writerow([
                    display_name,
                    s["total"],
                    s["SBX_coverage_pct"],
                    s["DOCOM_coverage_pct"],
                    s["HL7_coverage_pct"],
                ])
        print(f"⚠️  CSV file is locked, wrote to: {alt_path}")
        csv_path = alt_path

    with open(MISSING_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "event", "type", "SBX", "DOCOM", "HL7"]
        )
        writer.writeheader()
        writer.writerows(missing)



def main():
    meaningful_events = load_normalized_and_correlation()
    summary, missing = generate_coverage_summary(meaningful_events)
    write_outputs(summary, missing)

    print("✅ Coverage summary generated (meaningful medical events only)")
    print(f"   Total meaningful events: {len(meaningful_events)}")
    print(f"   Coverage events analyzed: {summary['overall']['total']}")
    print("   → Output files:")
    print(f"      {SUMMARY_JSON}")
    print(f"      {SUMMARY_CSV}")
    print(f"      {MISSING_CSV}")


if __name__ == "__main__":
    main()