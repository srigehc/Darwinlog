from model import NormalizedEvent
import csv
from helpers import normalize_severity, safe_parse_datetime
import config
import os
def classify_system_event(message: str) -> str:
    msg = message.lower()
    if "state entered" in msg or "state exited" in msg:
        return "STATE_TRANSITION"
    if "alarm" in msg:
        return "ALARM"
    if "connected" in msg or "subscribed" in msg:
        return "CONNECTIVITY"
    if "pressed" in msg or "menu opened" in msg:
        return "USER_ACTION"
    return "INFO"


def normalize_system_logs(csv_path):
    events = []
    #print(f"\n[DEBUG] normalize_system_logs() called with csv_path: {csv_path}")
    
    # Check if file exists
    
    if not os.path.exists(csv_path):
        print(f"[WARNING] System log file not found: {csv_path}")
        return events
    
    try:
        with open(csv_path, newline='', encoding="utf-8") as f:
           # print(f"[DEBUG] File opened successfully")
            reader = csv.DictReader(f)
           # print(f"[DEBUG] CSV columns detected: {reader.fieldnames}")
            
            row_count = 0
            for row in reader:
                row_count += 1
               # print(f"\n[DEBUG] Processing row #{row_count}")
                #print(f"[DEBUG] Row data: {row}")
                
                ts = safe_parse_datetime(
                    f"{row.get('Date', '')} {row.get('Time', '')}",
                    "%d-%b-%Y %H:%M:%S"
                )
               # print(f"[DEBUG] Parsed timestamp: {ts}")
                
                if not ts:
                    #print(f"[DEBUG] Skipping row - timestamp parsing failed")
                    continue
                    
                #print(f"[DEBUG] Parsed SYSTEM timestamp: {ts} from row: {row.get('Date', 'N/A')} {row.get('Time', 'N/A')}")    
                event = NormalizedEvent(
                    timestamp=ts,
                    source="SYSTEM",
                    subsystem=row.get("Software Module", "UNKNOWN"),
                    severity=normalize_severity(row.get("Log Level", "INFO")),
                    event_type=classify_system_event(row.get("Log Message", "")),
                    message=row.get("Log Message", ""),
                    context={
                        "log_type": row.get("Log Type"),
                        "entry_id": row.get("Entry")
                    },
                    raw=str(row)
                )
                events.append(event)
                #print(f"[DEBUG] Event added. Total events so far: {len(events)}")
            
            #print(f"\n[DEBUG] Finished reading CSV. Total rows processed: {row_count}")
    except Exception as e:
        print(f"[ERROR] Exception in normalize_system_logs: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    #print(f"[DEBUG] Returning {len(events)} events")
    return events


if __name__ == "__main__":
    results= normalize_system_logs(config.SystemLog)
    print("Sample normalized SYSTEM event:", results[:100] if results else "No events found")