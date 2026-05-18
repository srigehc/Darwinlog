import xml.etree.ElementTree as ET
import re
from datetime import datetime
import sys
import os

# Add parent and current directory to path BEFORE importing config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Current directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Parent directory

import config


# --------------------------------------------------
# Helpers
# --------------------------------------------------

TIMESTAMP_RE = re.compile(
    r'@([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\.\d{3})'
)

def parse_sbx_timestamp(comment_line: str) -> str | None:
    """
    Extract timestamp from SBX comment line and return ISO string.
    Example:
    <!-- <<<<< Received message ... @Apr 22 11:35:23.302 -->
    """
    match = TIMESTAMP_RE.search(comment_line)
    if not match:
        return None

    raw = match.group(1)
    dt = datetime.strptime(raw, "%b %d %H:%M:%S.%f")

    # SBX logs do not contain year; assume current year if needed
    dt = dt.replace(year=datetime.now().year)
    return dt.isoformat()


def strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def is_numeric_value(v: str) -> bool:
    try:
        float(v)
        return True
    except Exception:
        return False


def sapphire_has_numeric(sapphire_xml: str) -> bool:
    """
    Return True if sapphire block contains any numeric under <num>.
    Numeric values are stored as attributes V="..."
    """
    root = ET.fromstring(sapphire_xml)

    for elem in root.iter():
        if strip_namespace(elem.tag) == "num":
            for child in elem.iter():
                val = child.attrib.get("V")
                if val is not None and is_numeric_value(val):
                    return True
    return False


# --------------------------------------------------
# ✅ MAIN SBX NUMERIC EXTRACTOR
# --------------------------------------------------

def extract_sbx_numeric_events(sbx_log_path: str) -> list[dict]:
    """
    Extract SBX numeric events as:
    { "timestamp": ISO_TIME, "channel": "SBX" }
    """
    
    results = []

    current_timestamp = None
    buffering = False
    sapphire_lines = []

    with open(sbx_log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # 1️⃣ Capture timestamp
            if "<<<<< Received message" in line:
                ts = parse_sbx_timestamp(line)
                if ts:
                    current_timestamp = ts
                continue

            # 2️⃣ Start sapphire block
            if line.startswith("<sapphire"):
                buffering = True
                sapphire_lines = [line]
                continue

            # 3️⃣ Buffer sapphire block
            if buffering:
                sapphire_lines.append(line)

                if line.startswith("</sapphire>"):
                    buffering = False

                    if current_timestamp:
                        sapphire_xml = "\n".join(sapphire_lines)
                        try:
                            if sapphire_has_numeric(sapphire_xml):
                                results.append({
                                    "timestamp": current_timestamp,
                                    "channel": "SBX"
                                })
                        except ET.ParseError:
                            # ignore malformed blocks safely
                            pass

    return results
# --------------------------------------------------
# ✅ MAIN DoCom NUMERIC EXTRACTOR
# --------------------------------------------------

HEADER_RE = re.compile(
    r"Status Data Response message received .*?:\s*(\w{3},\s*\w{3}\s+\d{2},\s+\d{4}\s+\d{2}:\d{2}:\d{2}\.\d{3})"
)

NUMERIC_RE = re.compile(r"=\s*([0-9]+(?:\.[0-9]+)?)")

def extract_docom_numeric_events(docom_log_path):
    results = []

    current_ts = None
    saw_numeric = False

    with open(docom_log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # 1️⃣ Start of a new VTq message
            header_match = HEADER_RE.search(line)
            if header_match:
                # flush previous block
                if current_ts and saw_numeric:
                    results.append({
                        "timestamp": current_ts.isoformat(),
                        "channel": "DOCOM"
                    })

                raw_ts = header_match.group(1)
                current_ts = datetime.strptime(
                    raw_ts, "%a, %b %d, %Y %H:%M:%S.%f"
                )
                saw_numeric = False
                continue

            # 2️⃣ Detect numeric fields (ignore ---)
            if "=" in line and "---" not in line:
                if NUMERIC_RE.search(line):
                    saw_numeric = True

        # flush last block
        if current_ts and saw_numeric:
            results.append({
                "timestamp": current_ts.isoformat(),
                "channel": "DOCOM"
            })

    return results
# --------------------------------------------------
# ✅ MAIN HL7 NUMERIC EXTRACTOR
# --------------------------------------------------

def extract_hl7_numeric_events(hl7_log_path):
    results = []

    with open(hl7_log_path, "r", encoding="utf-8", errors="ignore") as f:
        message = []

        for line in f:
            line = line.strip()

            if line.startswith("MSH"):
                if message:
                    ev = process_hl7_message(message)
                    if ev:
                        results.append(ev)
                message = [line]
            else:
                message.append(line)

        # last message
        if message:
            ev = process_hl7_message(message)
            if ev:
                results.append(ev)

    return results


def process_hl7_message(lines):
    msh = next((l for l in lines if l.startswith("MSH")), None)
    if not msh:
        return None

    fields = msh.split("|")
    if len(fields) < 9:
        return None

    msg_type = fields[8]
    if not msg_type.startswith("ORU"):
        return None

    # MSH-7 timestamp (YYYYMMDDHHMMSS[.SSS])
    raw_ts = fields[6][:14]
    try:
        ts = datetime.strptime(raw_ts, "%Y%m%d%H%M%S")
    except ValueError:
        return None

    # detect numeric OBX
    for line in lines:
        if line.startswith("OBX"):
            parts = line.split("|")
            if len(parts) > 5 and parts[2] == "NM":
                try:
                    float(parts[5])
                    return {
                        "timestamp": ts.isoformat(),
                        "channel": "HL7"
                    }
                except ValueError:
                    pass

    return None



if __name__ == "__main__":
    #no need to run this directly; it's imported by normalized_numeric_logs.py  
    #run this only for debugging DoCom extraction in isolation
    sbx_log_path = config.SBX_LOG
    #print(extract_sbx_numeric_events(sbx_log_path))
    DoComLog_path = config.DOCOM_LOG
    #print(extract_docom_numeric_events(DoComLog_path))
    HL7Log_path = config.HL7_LOG
    print(extract_hl7_numeric_events(HL7Log_path))