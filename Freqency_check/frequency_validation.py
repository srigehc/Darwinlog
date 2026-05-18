"""
Phase 4: Frequency Validation
=============================
Validates numeric data frequency using NORMALIZED logs only.
Input:
------
- normalized_logs.json
Validation Rules:
-----------------
SBX / DoCom:
- Numeric stream is alive if <num> exists
- Any numeric inside <num> is sufficient
- Expected cadence: 2.0 sec ± tolerance / 10 sec ± tolerance (DoCom)
HL7:
- Numeric stream is alive if:
  message_type == ORU^R01 AND
  at least one OBX with numeric (NM)
- Cadence is gap-based (not fixed 2 sec)
Outputs:
--------
- frequency_summary.csv
- frequency_violations.json
"""
# Add parent and current directory to path BEFORE importing local modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Current directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Parent directory

import json
import statistics
import math
from datetime import datetime
import pandas as pd
import shutil
import waveform_freq_check
import normalized_numeric_logs
import config

NORMALIZED_FILE = config.NORMALIZED_NUM_FILE
NORMALIZED_WAVEFORM_FILE = config.NORMALIZED_WAVEFORM_FILE

EXPECTED_SBX_SEC = config.NUMERIC_RULES["SBX_NUMERIC"]["expected_sec"]
TOLERANCE_SBX_SEC = config.NUMERIC_RULES["SBX_NUMERIC"]["tolerance_sec"]

EXPECTED_DOCOM_SEC = config.NUMERIC_RULES["DOCOM_NUMERIC"]["expected_sec"]
TOLERANCE_DOCOM_SEC = config.NUMERIC_RULES["DOCOM_NUMERIC"]["tolerance_sec"]

EXPECTED_HL7_SEC = config.NUMERIC_RULES["HL7_NUMERIC"]["expected_sec"]
TOLERANCE_HL7_SEC = config.NUMERIC_RULES["HL7_NUMERIC"]["tolerance_sec"]

WAVEFORM_RULES = {
    "SBX_ANAES_WAVE": {
        "csv_stream": "Waveform_AM",
        "expected_sec": 0.4,
        "tolerance_sec": 0.1
    },
    "SBX_PM_WAVE": {
        "csv_stream": "Waveform_PM",
        "expected_sec": 0.5,
        "tolerance_sec": 0.15
    }
}

def parse_ts(ts):
    return datetime.fromisoformat(ts)


def validate_sbx_frequency(events):
    sbx_ts = sorted(
        parse_ts(e["timestamp"])
        for e in events
        if e.get("channel") == "SBX"
    )

    #print("DEBUG: SBX samples found:", len(sbx_ts))

    if len(sbx_ts) < 2:
        return "FAIL", 0, 0.0

    deltas = [
        (b - a).total_seconds()
        for a, b in zip(sbx_ts, sbx_ts[1:])
    ]

    max_gap = max(deltas)
    gaps = [d for d in deltas if d > EXPECTED_SBX_SEC + TOLERANCE_SBX_SEC]

    status = "PASS" if not gaps else "WARN"
    return status, len(sbx_ts), round(max_gap, 3)

def validate_docom_frequency(events):
    docom_ts = sorted(
        parse_ts(e["timestamp"])
        for e in events
        if e.get("channel") == "DOCOM"
    )

    #print("DEBUG: DoCom samples found:", len(docom_ts))

    if len(docom_ts) < 2:
        return "FAIL", 0, 0.0

    deltas = [
        (b - a).total_seconds()
        for a, b in zip(docom_ts, docom_ts[1:])
    ]

    max_gap = max(deltas)

    violations = [
        d for d in deltas
        if d > EXPECTED_DOCOM_SEC + TOLERANCE_DOCOM_SEC
    ]

    status = "PASS" if not violations else "WARN"

    return status, len(docom_ts), round(max_gap, 3)

def validate_hl7_frequency(events):
    hl7_ts = sorted(
        parse_ts(e["timestamp"])
        for e in events
        if e.get("channel") == "HL7"
    )

    #print("DEBUG: HL7 samples found:", len(hl7_ts))

    if len(hl7_ts) < 2:
        return "FAIL", 0, 0.0

    deltas = [
        (b - a).total_seconds()
        for a, b in zip(hl7_ts, hl7_ts[1:])
    ]

    max_gap = max(deltas)
    violations = [
        d for d in deltas
        if d > EXPECTED_HL7_SEC + TOLERANCE_HL7_SEC
    ]

    status = "PASS" if not violations else "WARN"
    return status, len(hl7_ts), round(max_gap, 3)



def percentile(values, pct):
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * (pct / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    return values[int(f)] + (values[int(c)] - values[int(f)]) * (k - f)


def nearest_rank_percentile(values, percent):
    """
    Returns the value V such that `percent`% of the values are <= V
    (nearest-rank method).
    """
    if not values:
        return 0.0
    #round(None, 3)
    values = sorted(values)
    n = len(values)

    k = math.ceil((percent / 100) * n)
    k = max(1, min(k, n))  # clamp

    return float(values[k - 1])


def validate_frequency(events, channel, expected_sec, tolerance_sec):
    timestamps = sorted(
        parse_ts(e["timestamp"])
        for e in events
        if e.get("channel") == channel
    )

    count = len(timestamps)
    if count < 2:
        return {
            "stream": channel,
            "count": count,
            "status": "FAIL",
            "insight": "Insufficient samples"
        }

    # Calculate time deltas between consecutive timestamps (in seconds)
    deltas_raw = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps) - 1)]
    
    # ensure clean numeric deltas
    deltas = [float(d) for d in deltas_raw if d is not None]

    if len(deltas) == 0:
        max_gap = avg_gap = jitter = p90 = p95 = 0.0
    else:
        max_gap = round(max(deltas), 3)
        avg_gap = round(statistics.mean(deltas), 3)
        jitter = round(statistics.stdev(deltas), 3) if len(deltas) > 1 else 0.0
        p90 = round(nearest_rank_percentile(deltas, 90), 3)
        p95 = round(nearest_rank_percentile(deltas, 95), 3)

    #print("DEBUG final p90/p95:", p90, p95)
    violations = [
            d for d in deltas
            if d > expected_sec + tolerance_sec
        ]

    if not violations:
        status = "PASS"
        insight = "Stable cadence, minimal jitter"
    else:
        status = "WARN"
        insight = f"{len(violations)} gaps exceeded tolerance"

    return {
        "stream": channel,
        "count": count,
        "expected": expected_sec,
        "max_gap": round(max_gap, 3),
        "avg_gap": avg_gap,
        "90%": p90,
        "95%": p95,
        "jitter": jitter,
        "status": status,
        "insight": insight
    }

def main():
    with open(NORMALIZED_FILE) as f:
        events = json.load(f)

    
    
    sbx_result = validate_frequency(events, "SBX", expected_sec=EXPECTED_SBX_SEC, tolerance_sec=TOLERANCE_SBX_SEC)
    docom_result = validate_frequency(events, "DOCOM", expected_sec=EXPECTED_DOCOM_SEC, tolerance_sec=TOLERANCE_DOCOM_SEC)
    hl7_result = validate_frequency(events, "HL7", expected_sec=EXPECTED_HL7_SEC, tolerance_sec=TOLERANCE_HL7_SEC)

    results = [sbx_result, docom_result, hl7_result]

    
    results = [
        sbx_result,
        docom_result,
        hl7_result
    ]

    pd.DataFrame(results).to_csv(
        "frequency_validations.csv",
        index=False
    )

    with open("frequency_validations.json", "w") as f:
        json.dump(
            {
                "generated_at": datetime.now().isoformat(),
                "summary": results
            },
            f,
            indent=2
        )
       
    print("\nDETAILED NUMERIC FREQUENCY SUMMARY")
    print("--------------------------------------------------------------------------")
    print("Stream | Events | Exp(s) | MaxGap | AvgGap | P90  | P95  | Jitter | Status")
    print("--------------------------------------------------------------------------")

    for r in results:
        print(
            f"{r['stream']:<6} | "
            f"{r['count']:<6} | "
            f"{r.get('expected','-'):<6} | "
            f"{r.get('max_gap','-'):<6} | "
            f"{r.get('avg_gap','-'):<6} | "
            f"{r.get('p90','-'):<4} | "
            f"{r.get('p95','-'):<4} | "
            f"{r.get('jitter','-'):<6} | "
            f"{r['status']}"
        )

    print("--------------------------------------------------------------------------\n")

    for r in results:
        print(f"{r['stream']} Insight → {r['insight']}")
    
   




def validate_waveform_frequency(timestamps, expected_sec, tolerance_sec):
    if len(timestamps) < 2:
        return {
            "validated_events": len(timestamps),
            "max_gap_sec": "",
            "avg_gap_sec": "",
            "p90_gap_sec": "",
            "p95_gap_sec": "",
            "status": "FAIL",
            "insight": "Insufficient samples"
        }

    gaps = [
        (b - a).total_seconds()
        for a, b in zip(timestamps, timestamps[1:])
    ]

    max_gap = max(gaps)
    avg_gap = statistics.mean(gaps)
    p90 = nearest_rank_percentile(gaps, 90)
    p95 = nearest_rank_percentile(gaps, 95)

    status = (
        "PASS" if max_gap <= expected_sec + tolerance_sec else "WARN"
    )
    insight = "Stable cadence" if status == "PASS" else "Exceeded tolerance"

    return {
        "validated_events": len(timestamps),
        "max_gap_sec": round(max_gap, 3),
        "avg_gap_sec": round(avg_gap, 3),
        "p90_gap_sec": round(p90, 3),
        "p95_gap_sec": round(p95, 3),
        "jitter": None,  # Jitter can be added if needed by calculating stdev of gaps
        "status": status,
        "insight": insight
    }
def build_waveform_validation_rows(waveform_events):
    rows = []

    for stream, cfg in WAVEFORM_RULES.items():
        timestamps = collect_packet_timestamps(waveform_events, stream)

        result = validate_waveform_frequency(
            timestamps,
            cfg["expected_sec"],
            cfg["tolerance_sec"]
        )

        rows.append({
            "stream": cfg["csv_stream"],
            "validated_events": result["validated_events"],
            "expected_sec": cfg["expected_sec"],
            "max_gap_sec": result["max_gap_sec"],
            "avg_gap_sec": result["avg_gap_sec"],
            "p90_gap_sec": result["p90_gap_sec"],
            "p95_gap_sec": result["p95_gap_sec"],
            "jitter": "N/A",
            "status": result["status"],
            "insight": result["insight"]
        })

    return rows


def append_to_frequency_csv(new_rows, csv_path="frequency_validations.csv"):
    """
    Appends waveform validation rows to the frequency CSV as a separate table.
    This maintains two distinct tables: event streams and waveform data.
    """
    waveform_columns = ["stream", "validated_events", "expected_sec", "max_gap_sec", "avg_gap_sec", "p90_gap_sec", "p95_gap_sec", "jitter", "status", "insight"]
    
    try:
        # Read existing CSV (which has event data)
        with open(csv_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = ""

    # Create DataFrame for waveform rows with only relevant columns
    df_waveform = pd.DataFrame(new_rows)
    waveform_csv = df_waveform[waveform_columns].to_csv(index=False)

    # Write combined file: existing event data + blank line + waveform table header + waveform data
    with open(csv_path, "w", encoding="utf-8") as f:
        # Write existing event data
        if existing_content:
            f.write(existing_content)
            f.write("\n")  # Blank line separator
        
        # Write waveform table with header
        f.write(waveform_csv)

def load_waveform_jsonl(path):
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            events.append(json.loads(line))
    return events


def collect_packet_timestamps(events, stream):
    """    One packet = one unique timestamp per stream.   """
    ts = {
        e["timestamp"]
        for e in events
        if e["stream"] == stream
    }
    return sorted(datetime.fromisoformat(t) for t in ts)


def compute_intervals(timestamps):
    return [
        (b - a).total_seconds()
        for a, b in zip(timestamps, timestamps[1:])
    ]

def copy_file():

    source_csv = "frequency_validations.csv"
    dest_dir = os.path.join(config.BASE_DIR, "outputs")
    os.makedirs(dest_dir, exist_ok=True)
    dest_csv = os.path.join(dest_dir, "frequency_validations.csv")
    shutil.copy(source_csv, dest_csv)
    print(f"✅ Copied {source_csv} to {dest_csv}")


def freqency_validation_main():
    main()
    normalized_numeric_logs.main()
    waveform_freq_check.Waveform_freq_check_main()
    waveform_events = load_waveform_jsonl(NORMALIZED_WAVEFORM_FILE)
    waveform_rows = build_waveform_validation_rows(waveform_events)
    append_to_frequency_csv(waveform_rows)
    copy_file()

if __name__ == "__main__":
    # for numaric extraction and normalization run only this program, it will create normalized_numeric_logs.json 
    # which is input for frequency_validation.py and summary csv and json outputs for frequency validation
    main()
    normalized_numeric_logs.main()
    waveform_freq_check.Waveform_freq_check_main()
    # Extract and process waveform events
    #sbx_waveform_events = waveform_freq_check.extract_sbx_waveform_events(config.SBX_LOG)
    #print(f"✅ Extracted {len(sbx_waveform_events)} SBX waveform events")
    waveform_events = load_waveform_jsonl(NORMALIZED_WAVEFORM_FILE)
    waveform_rows = build_waveform_validation_rows(waveform_events)
    append_to_frequency_csv(waveform_rows)
    copy_file()
   

