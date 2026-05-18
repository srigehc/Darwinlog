"""
Build normalized_numeric_logs.json from raw logs

Inputs:
- sbxLog.xml    (XML, large)
- DoComLog.txt  (text)
- hl7Log.txt    (HL7 text)

Output:
- normalized_numeric_logs.json

Extraction rules:
- SBX: <num> element with at least one numeric child
- DoCom: text line with at least one numeric key=value
- HL7: ORU^R01 message with at least one OBX numeric (NM)

This script performs NO frequency validation.
It only normalizes numeric stream presence.
"""
# Add parent and current directory to path BEFORE importing local modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Current directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Parent directory

import io
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime
from pathlib import Path

import Numeric_Extraction_Function
import config

# ==========================================================
# Configuration
# ==========================================================

BASE_DIR = config.BASE_DIR
SBX_XML = config.SBX_LOG
DOCOM_TXT = config.DOCOM_LOG    
HL7_TXT = config.HL7_LOG

OUTPUT = os.path.join(BASE_DIR, "Freqency_check", "normalized_numeric_logs.json") 


# ==========================================================
# Helpers
# ==========================================================

def normalize_timestamp(ts: str) -> str | None:
    ts = ts.strip()

    # ISO-like
    try:
        return datetime.fromisoformat(ts.replace("Z", "")).isoformat()
    except Exception:
        pass

    # Legacy format: 22-Apr-26 11:40:02
    try:
        return datetime.strptime(ts, "%d-%b-%y %H:%M:%S").isoformat()
    except Exception:
        pass

    return None

def is_number(text: str) -> bool:
    try:
        float(text)
        return True
    except Exception:
        return False


def parse_timestamp_from_text(line: str) -> str | None:
    """
    Generic timestamp extractor: 22-Apr-26 11:40:02  OR 2026-04-22T11:40:02
    Adjust if needed.
    """
    iso_match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", line)
    if iso_match:
        return iso_match.group(0)

    legacy = re.search(r"\d{2}-[A-Za-z]{3}-\d{2}\s+\d{2}:\d{2}:\d{2}", line)
    if legacy:
        dt = datetime.strptime(legacy.group(0), "%d-%b-%y %H:%M:%S")
        return dt.isoformat()

    return None

def extract_timestamp_nearby(elem):
    """
    Attempt to extract timestamp from the <num> element's ancestors
    or nearby siblings.

    Returns ISO timestamp string or None.
    """

    # 1️⃣ Check attributes on this element and parents
    current = elem
    for _ in range(5):  # walk up max 5 levels (safe)
        if current is None:
            break

        for attr in ("timestamp", "time", "ts", "datetime"):
            if attr in current.attrib:
                return normalize_timestamp(current.attrib[attr])

        current = current.getparent() if hasattr(current, "getparent") else None

    # 2️⃣ Check sibling elements (common in SBX packets)
    parent = current = current.getparent() if hasattr(current, "getparent") else None
    if parent is not None:
        for child in parent:
            if child.tag.lower() in ("timestamp", "time", "ts"):
                if child.text:
                    return normalize_timestamp(child.text)

    return None


# ==========================================================
# SBX extraction (XML)
# ==========================================================


def strip_ns(tag):
    """Remove XML namespace"""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag



# ==========================================================
# DoCom extraction (text)
# ==========================================================

DOCOM_NUMERIC_PATTERN = re.compile(r"\b[A-Za-z0-9_]+\s*=\s*\d+(\.\d+)?")

def extract_docom_numeric():
    records = []

    with open(DOCOM_TXT, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if DOCOM_NUMERIC_PATTERN.search(line):
                ts = parse_timestamp_from_text(line)
                if ts:
                    records.append({
                        "timestamp": ts,
                        "channel": "DOCOM"
                    })

    return records


# ==========================================================
# HL7 extraction
# ==========================================================

def extract_hl7_numeric():
    records = []

    with open(HL7_TXT, encoding="utf-8", errors="ignore") as f:
        message = []
        for line in f:
            line = line.strip()
            if line.startswith("MSH"):
                if message:
                    process_hl7_message(message, records)
                message = [line]
            else:
                message.append(line)

        if message:
            process_hl7_message(message, records)

    return records


def process_hl7_message(lines, records):
    msh = next((l for l in lines if l.startswith("MSH")), None)
    if not msh:
        return

    fields = msh.split("|")
    msg_type = fields[8] if len(fields) > 8 else ""

    if not msg_type.startswith("ORU"):
        return

    timestamp = None
    if len(fields) > 6:
        try:
            dt = datetime.strptime(fields[6][:14], "%Y%m%d%H%M%S")
            timestamp = dt.isoformat()
        except Exception:
            pass

    if not timestamp:
        return

    for line in lines:
        if line.startswith("OBX"):
            parts = line.split("|")
            if len(parts) > 3 and parts[2] == "NM":
                value = parts[5] if len(parts) > 5 else ""
                if is_number(value):
                    records.append({
                        "timestamp": timestamp,
                        "channel": "HL7"
                    })
                    return   # one numeric OBX is enough


# ==========================================================
# Main
# ==========================================================

def main():
    records = []
    print("Extracting SBX numeric data...")
    records.extend(Numeric_Extraction_Function.extract_sbx_numeric_events(SBX_XML))
    
    print("Extracting DoCom numeric data...")
    records.extend(Numeric_Extraction_Function.extract_docom_numeric_events(DOCOM_TXT))

    print("Extracting HL7 numeric data...")
    records.extend(Numeric_Extraction_Function.extract_hl7_numeric_events(HL7_TXT))

    records.sort(key=lambda r: r["timestamp"])

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"✅ Created {OUTPUT}")
    print(f"   Total numeric records: {len(records)}")


if __name__ == "__main__":
    main()