import datetime
import re
from model import NormalizedEvent


# ---------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------

# Case 1: Simple timestamp header
#   11:40:44.504  <rest>
TIME_HEADER_RE = re.compile(
    r"^(?P<time>\d{2}:\d{2}:\d{2}\.\d{3})\s+(?P<rest>.+)$"
)

# Case 2: Status Data Response header
#   Status Data Response message received [VTq] : Wed, Apr 22, 2026 11:45:40.220
STATUS_HEADER_RE = re.compile(
    r"Status Data Response message received.*?:\s*"
    r"(?P<date>\w+,\s+\w+\s+\d{1,2},\s+\d{4}\s+"
    r"\d{2}:\d{2}:\d{2}\.\d{3})"
)

# Data Status line
DATA_STATUS_RE = re.compile(
    r"Data\s+Status\s*=\s*(0x[0-9A-Fa-f]+)"
)


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def normalize_ohmeda_log(log_path, base_date):
    """
    Normalize Do‑Com (Ohmeda) logs.

    Supports:
    - HH:MM:SS.mmm headers
    - Status Data Response headers
    - Timestamp inheritance for indented lines
    """
    events = []
    last_command_value = {}

    current_ts = None  # ✅ block-level timestamp

    with open(log_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            if not line.strip():
                continue

            # ---------------------------------------------------------
            # Try to extract a NEW timestamp
            # ---------------------------------------------------------
            ts, text = extract_timestamp(line, base_date)

            if ts is not None:
                # ✅ New timestamp starts a new block
                current_ts = ts
                continue  # header line itself has no commands

            if current_ts is None:
                # ❌ Lines before first timestamp are ignored
                continue

            # ✅ Inherit timestamp
            ts = current_ts
            text = line.strip()

            # ---------------------------------------------------------
            # Data Status (protocol-level)
            # ---------------------------------------------------------
            status_event = parse_data_status(text, ts)
            if status_event:
                events.append(status_event)
                continue

            # ---------------------------------------------------------
            # set … commands (operator / configuration intent)
            # ---------------------------------------------------------
            cmd_event = parse_set_command(
                text, ts, last_command_value
            )
            if cmd_event:
                events.append(cmd_event)
                continue

            # Everything else intentionally ignored

    return events


# ---------------------------------------------------------------------
# Timestamp handling
# ---------------------------------------------------------------------

def extract_timestamp(line, base_date):
    """
    Extract timestamp from either:
      - HH:MM:SS.mmm prefix
      - Status Data Response header
    """
    # Case 1: HH:MM:SS.mmm <text>
    m = TIME_HEADER_RE.match(line)
    if m:
        ts = datetime.datetime.strptime(
            f"{base_date} {m.group('time')}",
            "%Y-%m-%d %H:%M:%S.%f"
        )
        return ts, m.group("rest").strip()

    # Case 2: Status Data Response message
    m = STATUS_HEADER_RE.search(line)
    if m:
        ts = datetime.datetime.strptime(
            m.group("date"),
            "%a, %b %d, %Y %H:%M:%S.%f"
        )
        return ts, None

    return None, line


# ---------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------

def parse_data_status(text, ts):
    """
    Parse:
      Data Status = 0x03
    """
    m = DATA_STATUS_RE.match(text)
    if not m:
        return None

    return NormalizedEvent(
        timestamp=ts,
        source="DO_COM",
        subsystem="PROTOCOL",
        severity="INFO",
        event_type="STATUS",
        message="Data status update",
        context={"status": m.group(1)},
        raw=text
    )


def parse_set_command(text, ts, last_command_value):
    """
    Parse generic:
      set <parameter> = <value> (<unit>)
      set <parameter> = <value>
    """
    if not text.lower().startswith("set "):
        return None

    try:
        left, right = text.split("=", 1)
    except ValueError:
        return None

    param = canonicalize_param(left.replace("set", "", 1))
    right = right.strip()

    # Extract value + optional unit
    if "(" in right:
        value, unit = right.split("(", 1)
        unit = unit.rstrip(")").strip()
        value = value.strip()
    else:
        value = right.strip()
        unit = None

    # Deduplicate repeated values
    prev = last_command_value.get(param)
    if prev == value:
        return None

    last_command_value[param] = value

    return NormalizedEvent(
        timestamp=ts,
        source="DO_COM",
        subsystem=classify_subsystem(param),
        severity="INFO",
        event_type="COMMAND",
        message=f"Set {param}",
        context={
            "parameter": param,
            "value": value,
            "unit": unit,
            "raw_command": text,
        },
        raw=text
    )


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def canonicalize_param(param):
    """
    Normalize spacing without hardcoding param names.
    """
    return " ".join(param.strip().split())


def classify_subsystem(param):
    """
    Best-effort subsystem classification.
    """
    p = param.lower()
    if "press" in p or "peep" in p or "rr" in p:
        return "RESP"
    if "fio2" in p or "gas" in p or "flow" in p or "aa" in p:
        return "GAS"
    return "SYSTEM"