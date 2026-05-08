import csv
from datetime import datetime, timedelta

# -----------------------------
# Configuration
# -----------------------------

WINDOWS = {
    "SBX":   (timedelta(seconds=-10), timedelta(seconds=10)),
    "DOCOM": (timedelta(seconds=-10), timedelta(seconds=10)),
    "HL7":   (timedelta(seconds=0),   timedelta(seconds=30)),
}

USER_ACTION_KEYWORDS = [
    "keypressed",
    "quickkey",
    "button",
    "numeric value",
    "menu opened",
]

STATE_EVENT_KEYWORDS = [
    "state entered",
    "start case",
    "therapy",
    "standby",
    "shutdown",
]

NOISE_KEYWORDS = [
    "watchdog",
    "idle cpu",
    "register thread",
    "dispatch latency",
    "endpoint connected",
]


# -----------------------------
# Helpers
# -----------------------------

def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def classify_system_event(text: str) -> str:
    t = text.lower()

    if any(k in t for k in USER_ACTION_KEYWORDS):
        return "USER_ACTION"

    if any(k in t for k in STATE_EVENT_KEYWORDS):
        return "STATE_TRANSITION"

    if any(k in t for k in NOISE_KEYWORDS):
        return "NOISE"

    return "OTHER"


def within_window(anchor_ts, candidate_ts, window):
    return anchor_ts + window[0] <= candidate_ts <= anchor_ts + window[1]


# -----------------------------
# Phase 1 Engine
# -----------------------------

def build_correlation_chains(csv_path: str):
    rows = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["system_time"] = parse_ts(r["system_time"])
            rows.append(r)

    rows.sort(key=lambda r: r["system_time"])

    # Select SYSTEM anchors
    anchors = []
    for r in rows:
        classification = classify_system_event(r["system_event"])
        if classification in ("USER_ACTION", "STATE_TRANSITION"):
            anchors.append({**r, "classification": classification})

    chains = []

    for anchor in anchors:
        T = anchor["system_time"]

        chain = {
            "anchor": {
                "time": anchor["system_time"].isoformat(),
                "event": anchor["system_event"],
                "type": anchor["classification"],
            },
            "SBX": [],
            "DOCOM": [],
            "HL7": [],
        }

        for r in rows:
            t = r["system_time"]

            if r.get("SBX_event") and within_window(T, t, WINDOWS["SBX"]):
                chain["SBX"].append(r["SBX_event"])

            if r.get("DOCOM_event") and within_window(T, t, WINDOWS["DOCOM"]):
                chain["DOCOM"].append(r["DOCOM_event"])

            if r.get("HL7_event") and within_window(T, t, WINDOWS["HL7"]):
                chain["HL7"].append(r["HL7_event"])

        # Deduplicate
        for k in ("SBX", "DOCOM", "HL7"):
            chain[k] = sorted(set(chain[k]))

        chains.append(chain)

    return chains