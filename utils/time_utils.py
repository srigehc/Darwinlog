from datetime import datetime
import re

def safe_parse_datetime(date_str, fmt):
    try:
        return datetime.strptime(date_str, fmt)
    except Exception:
        return None

def normalize_severity(level):
    level = level.upper()
    if level in ["ERROR", "ERR"]:
        return "ERROR"
    if level in ["WARN", "WARNING"]:
        return "WARNING"
    if level in ["ALARM"]:
        return "ALARM"
    return "INFO"
