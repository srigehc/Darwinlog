import datetime
import re
import xml.etree.ElementTree as ET
from model import NormalizedEvent


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Only these semantic areas are relevant for correlation
ALLOWED_SBX_PATH_FRAGMENTS = (
    "systemState",
    "numLimit",
    "limit",
    "gasControlMode",
    "respGas",
    "endTidalConc",
    "freshGasFlow",
    "mode",
)

# Safety cap to guarantee termination
MAX_SBX_EVENTS = 5000

def iter_sbx_blocks_with_timestamp(xml_path, sbx_base_time):
    """
    Iterates through SBX file sequentially.
    Carries forward the last 'Received message @' timestamp
    and attaches it to the following <sapphire> block.
    """
    current_ts = None
    buffer = []

    with open(xml_path, encoding="utf-8") as f:
        for line in f:
            # Capture receive timestamp
            m = re.search(
                r"Received message.*?@(\w+\s+\d+\s+\d+:\d+:\d+(?:\.\d+)?)",
                line
            )
            if m:
                ts_str = f"{m.group(1)} {datetime.datetime.now().year}"
                try:
                    current_ts = datetime.datetime.strptime(
                        ts_str, "%b %d %H:%M:%S.%f %Y"
                    )
                except ValueError:
                    current_ts = datetime.datetime.strptime(
                        ts_str, "%b %d %H:%M:%S %Y"
                    )
                continue

            # Start SBX block
            if "<sapphire" in line:
                buffer = [line]
                continue

            # Accumulate block
            if buffer:
                buffer.append(line)
                if "</sapphire>" in line:
                    block = "".join(buffer)
                    yield current_ts or sbx_base_time, block
                    buffer = []

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def normalize_sbx_log(xml_path, sbx_base_time):
    events = []
    last_sbx_state = {}
    fallback_count = 0

    with open(xml_path, encoding="utf-8") as f:
        content = f.read()

    # Non-greedy match: one sapphire block at a time
    #xml_blocks = re.findall(r"<sapphire.*?</sapphire>", content, re.DOTALL)

    for idx, (ts, block) in enumerate(
            iter_sbx_blocks_with_timestamp(xml_path, sbx_base_time)
    ):
        try:
            root = ET.fromstring(block)
        except Exception:
            continue

        extract_sbx_semantic_changes(
            root=root,
            ts=ts,
            block=block,
            events=events,
            last_state=last_sbx_state
        )


        if len(events) >= MAX_SBX_EVENTS:
            break

    if fallback_count > 0:
        print(
            f"INFO: SBX fallback timestamp used for {fallback_count} blocks "
            f"(expected for internal / untimestamped SBX updates)"
        )

    print("DEBUG: normalize_sbx_log returning", len(events), "events")
    return events


# ---------------------------------------------------------------------
# Timestamp extraction
# ---------------------------------------------------------------------

def extract_transport_timestamp(block):
    """
    Extracts receive timestamp from SBX XML comments.
    Example:
      <!-- <<<<< Received message on connection ... @Apr 22 11:40:25.271 -->
    """
    m = re.search(
        r"Received message.*?@(\w+\s+\d+\s+\d+:\d+:\d+(?:\.\d+)?)",
        block
    )
    if not m:
        return None

    ts_str = f"{m.group(1)} {datetime.datetime.now().year}"
    try:
        return datetime.datetime.strptime(ts_str, "%b %d %H:%M:%S.%f %Y")
    except ValueError:
        return datetime.datetime.strptime(ts_str, "%b %d %H:%M:%S %Y")


# ---------------------------------------------------------------------
# Core SBX semantic extraction
# ---------------------------------------------------------------------

def extract_sbx_semantic_changes(root, ts, block, events, last_state):
    """
    Extracts only meaningful SBX configuration/state changes.
    Prevents telemetry explosion by restricting to cfg trees.
    """

    current = flatten_cfg_state(root)

    for key, new_val in current.items():

        # Allow-list semantic paths only
        if not any(fragment in key for fragment in ALLOWED_SBX_PATH_FRAGMENTS):
            continue

        old_val = last_state.get(key)

        if old_val == new_val:
            continue

        event_type, subsystem = classify_sbx_event(key)

        events.append(
            NormalizedEvent(
                timestamp=ts,
                source="SBX",
                subsystem=subsystem,
                severity="INFO",
                event_type=event_type,
                message=f"{key} changed from {old_val} to {new_val}",
                context={
                    "key": key,
                    "old": old_val,
                    "new": new_val
                },
                raw=block[:500]
            )
        )

        last_state[key] = new_val


# ---------------------------------------------------------------------
# SBX helpers
# ---------------------------------------------------------------------

def flatten_cfg_state(root):
    """
    Flatten ONLY configuration (cfg) trees.
    Avoids telemetry / waveform data completely.
    """
    state = {}

    for cfg in root.iter():
        if cfg.tag.split("}")[-1] == "cfg":
            for child in cfg:
                walk_cfg(child, "cfg", state)

    return state


def walk_cfg(elem, path, state):
    tag = elem.tag.split("}")[-1]
    new_path = f"{path}.{tag}" if path else tag

    if "V" in elem.attrib:
        state[new_path] = elem.attrib["V"]

    for child in elem:
        walk_cfg(child, new_path, state)


def classify_sbx_event(key):
    if "systemState" in key:
        return "STATE_TRANSITION", "SYSTEM"
    if "limit" in key or "numLimit" in key:
        return "LIMIT_CHANGE", "RESP"
    if "gas" in key or "flow" in key or "conc" in key:
        return "GAS_CONFIG", "GAS"
    if "mode" in key:
        return "MODE_CHANGE", "RESP"
    return "SBX_PARAM_CHANGE", "SBX"