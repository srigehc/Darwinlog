from datetime import datetime

def safe_parse_datetime(value, fmt):
    try:
        return datetime.strptime(value, fmt)
    except Exception:
        return None

def normalize_severity(level):
    level = level.upper()
    if level in ["ERROR", "ERR"]:
        return "ERROR"
    if level in ["WARNING", "WARN"]:
        return "WARNING"
    if level == "ALARM":
        return "ALARM"
    return "INFO"

def events_before(target_event, all_events, seconds=10):
    # Guard: target event must have timestamp
    if target_event.timestamp is None:
        return []

    end_ts = target_event.timestamp.timestamp()
    start_ts = end_ts - seconds

    result = []

    for e in all_events:
        if e.timestamp is None:
            continue

        ts = e.timestamp.timestamp()
        if start_ts <= ts < end_ts:
            result.append(e)

    return result