import datetime
import re
from model import NormalizedEvent


# ---------------------------------------------------------------------
# Regex patterns (generic / future‑proof)
# ---------------------------------------------------------------------

# Matches HH:MM:SS.mmm
TIMESTAMP_RE = re.compile(
    r"^(?P<time>\d{2}:\d{2}:\d{2}\.\d{3})\s+(?P<rest>.+)$"
)


# Matches: Data Status = 0x03
DATA_STATUS_RE = re.compile(
    r"Data\s+Status\s*=\s*(?P<status>0x[0-9A-Fa-f]+)"
)

# Matches generic set commands:
#   set Plimit = 045 (cmH2O)
#   set FiO2 = 075 (%)
#   set Gas Control Mode = e
SET_COMMAND_RE = re.compile(
    r"set\s+(?P<param>[A-Za-z0-9\s]+?)\s*=\s*"
    r"(?P<value>[A-Za-z0-9\.\-]+)"
    r"(?:\s*\((?P<unit>[^)]+)\))?",
    re.IGNORECASE
)

STATUS_HEADER_RE = re.compile(
    r"Status Data Response message received.*?:\s*"
    r"(?P<date>\w+,\s+\w+\s+\d{2},\s+\d{4}\s+"
    r"\d{2}:\d{2}:\d{2}\.\d{3})"
)


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def normalize_ohmeda_log(log_path, base_date):
    """
    Normalize Do‑Com (Ohmeda) logs into:
      - STATUS events (protocol / internal)
      - COMMAND events (operator intent)

    :param log_path: path to DoComLog.txt
    :param base_date: YYYY‑MM‑DD date string from system context
    :return: list[NormalizedEvent]
    """
    events = []
    
    print(f"[DEBUG] Entering normalize_ohmeda_log")
    print(f"[DEBUG] log_path={log_path}, base_date={base_date}")

    # Used to suppress duplicate command echoes
    last_command_value = {}
    current_ts = None   # ✅ carry forward timestamp
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            print(f"[DEBUG] RAW LINE: {line.rstrip()}")
            line = line.strip()
            if not line:
                continue

            ts, text = extract_timestamp_and_tex(line, base_date)
            print(f"[DEBUG] ts={ts}, text={text}")
            if ts is None:
                current_ts = ts
                print("[DEBUG] ❌ Timestamp NOT extracted")
                continue
            elif current_ts is None:  # Skip until first timestamped block
                continue
            else:
                ts = current_ts
                text = line.strip()

            # ---------------------------------------------------------
            # 1) Protocol / status event (DO NOT ignore)
            # ---------------------------------------------------------
            status_event = parse_data_status(text, ts)
            print(f"[DEBUG] DataStatus check: {status_event is not None}")
            if status_event:
                events.append(status_event)
                continue
            
            
            # ---------------------------------------------------------
            # 2) Operator intent command
            # ---------------------------------------------------------
            cmd_event = parse_set_command(
                text, ts, last_command_value
            )
            print(f"[DEBUG] SetCommand check: {cmd_event is not None}")
            if cmd_event:
                print(f"[DEBUG] ✅ Created COMMAND event: {cmd_event.context}")
                events.append(cmd_event)
                continue

            # ---------------------------------------------------------
            # 3) Everything else is ignored by design
            # ---------------------------------------------------------

    return events


# ---------------------------------------------------------------------
# Timestamp handling
# ---------------------------------------------------------------------

def extract_timestamp_and_tex(line, base_date):
    
    m = re.match(r"^(\d{2}:\d{2}:\d{2}\.\d{3})\s+(.*)", line)
    if not m:
        return None, line

    ts = datetime.datetime.strptime(
        f"{base_date} {m.group(1)}",
        "%Y-%m-%d %H:%M:%S.%f"
    )
    return ts, m.group(2).strip()

    # Case 2: Status Data Response header
    m = STATUS_HEADER_RE.search(line)
    if m:
        ts = datetime.datetime.strptime(
            m.group("date"),
            "%a, %b %d, %Y %H:%M:%S.%f"
        )
        return ts, None  # block header only

    return None, line


# ---------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------

def parse_data_status(text, ts):
    if not text.startswith("Data Status"):
        return None

    _, value = text.split("=", 1)

    return NormalizedEvent(
        timestamp=ts,
        source="DO_COM",
        subsystem="PROTOCOL",
        severity="INFO",
        event_type="STATUS",
        message="Data status update",
        context={"status": value.strip()},
        raw=text
    )

def parse_set_command(text, ts, last_command_value):
    if not text.lower().startswith("set "):
        return None

    # Example:
    # "set Plimit                   = 045 (cmH2O)"
    left, right = text.split("=", 1)

    param = canonicalize_param(left.replace("set", "", 1))
    right = right.strip()

    # Extract value and optional unit
    if "(" in right:
        value, unit = right.split("(", 1)
        unit = unit.rstrip(")")
        value = value.strip()
    else:
        value = right.strip()
        unit = None

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
            "raw_command": text
        },
        raw=text
    )


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def canonicalize_param(param):
    """
    Normalize parameter names without hard‑coding.
    """
    return " ".join(param.strip().split())


def classify_subsystem(param):
    """
    Best‑effort subsystem classification.
    """
    p = param.lower()
    if "press" in p:
        return "RESP"
    if "fio2" in p or "gas" in p or "flow" in p:
        return "GAS"
    return "SYSTEM"