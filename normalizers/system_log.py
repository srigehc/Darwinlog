from model import NormalizedEvent
import csv
from helpers import normalize_severity, safe_parse_datetime

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

    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = safe_parse_datetime(
                f"{row['Date']} {row['Time']}",
                "%d-%b-%y %H:%M:%S"
            )
            if not ts:
                continue

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

    return events