import datetime
from model import NormalizedEvent


def parse_timestamp(line: str):
    """
    Example line:
    Status Data Response message received [VTq] : Wed, Apr 22, 2026 11:38:06.511
    """
    try:
        ts_part = line.split(":", 1)[1].strip()
        return datetime.datetime.strptime(
            ts_part,
            "%a, %b %d, %Y %H:%M:%S.%f"
        )
    except Exception:
        return None


def normalize_ohmeda_log(file_path):
    events = []

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    current_ts = None
    current_settings = {}

    def flush_block():
        """Emit one event per Status Data Response block"""
        if current_ts is not None and current_settings:
            events.append(
                NormalizedEvent(
                    timestamp=current_ts,
                    source="DOCOM",
                    subsystem="VENTILATOR",
                    severity="INFO",
                    event_type="VENT_SETTINGS_SNAPSHOT",
                    message="Ventilator status / settings snapshot",
                    context=current_settings.copy(),
                    raw=None
                )
            )

    for line in lines:
        line = line.rstrip()

        # ---- Start of a new Status Data Response block ----
        if line.startswith("Status Data Response message received"):
            flush_block()
            current_settings.clear()
            current_ts = parse_timestamp(line)
            continue

        # ---- Parse "set <param> = <value> (<unit>)" lines ----
        if line.strip().startswith("set "):
            try:
                # Split once at "="
                left, right = line.split("=", 1)

                name = left.replace("set", "").strip()

                # Split value and unit
                if "(" in right:
                    value_part, unit_part = right.split("(", 1)
                    unit = unit_part.replace(")", "").strip()
                else:
                    value_part = right
                    unit = None

                raw_value = value_part.strip()

                # Normalize placeholders
                if raw_value in ("", "---", "----"):
                    value = None
                else:
                    value = raw_value

                current_settings[name] = {
                    "value": value,
                    "unit": unit
                }
            except Exception:
                # Ignore malformed lines safely
                continue

    # Flush last block
    flush_block()

    return events
