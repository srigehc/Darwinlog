
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import csv
import statistics
import json
import sys
import os

# Add parent and current directory to path BEFORE importing config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Current directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Parent directory
import config

SBX_TS_REGEX = re.compile(
    r"@\s*(\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})"
)

def parse_waveform_values(value_str):
    values = []
    for token in value_str.split():
        try:
            values.append(float(token))
        except ValueError:
            pass
    return values


from datetime import datetime

def parse_sbx_timestamp(line):
    m = re.search(r"@(\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})", line)
    if not m:
        return None

    dt = datetime.strptime(m.group(1), "%b %d %H:%M:%S.%f")
    return dt.replace(year=2026).isoformat()   # or derive dynamically


def extract_waveforms_from_wav(wav_elem):
    waveforms = []

    for elem in wav_elem:
        wf_name = elem.tag.split("}")[-1]
        attrs = dict(elem.attrib)

        values = []

        # ✅ Case 1: direct V attribute (flow, volume, pressure)
        if "V" in elem.attrib:
            values = parse_waveform_values(elem.attrib["V"])

        # ✅ Case 2: nested <value V="..."> (ECG, pleth, IP)
        else:
            for child in elem:
                if child.tag.endswith("value") and "V" in child.attrib:
                    values = parse_waveform_values(child.attrib["V"])
                    break

        # remove V from attributes if present
        attrs.pop("V", None)

        waveforms.append({
            "waveform": wf_name,
            "attributes": attrs,
            "data": values
        })

    return waveforms

def extract_sbx_waveform_events(sbx_log_path):
    results = []

    current_ts = None
    buffer = []
    buffering = False

    with open(sbx_log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if "<<<<< Received message" in line:
                current_ts = parse_sbx_timestamp(line)
                continue

            if line.startswith("<sapphire"):
                buffering = True
                buffer = [line]
                continue

            if buffering:
                buffer.append(line)
                if line.startswith("</sapphire>"):
                    buffering = False
                    try:
                        root = ET.fromstring("\n".join(buffer))

                        stream = classify_sbx_waveform_packet(root)
                        if not stream or not current_ts:
                            continue

                        for wav in root.iter():
                            if wav.tag.endswith("wav"):
                                wave_entries = extract_waveforms_from_wav(wav)
                                for entry in wave_entries:
                                    results.append({
                                        "timestamp": current_ts,
                                        "stream": stream,
                                        "waveform": entry["waveform"],
                                        "attributes": entry["attributes"],
                                        "data": entry["data"]
                                    })

                    except ET.ParseError:
                        pass

    return results

def classify_sbx_waveform_packet(root):
    # Anaesthesia indicators
    anaesthesia_tags = {"gasmon", "resp", "gasdeliv"}
    pm_tags = {"ecg", "spo2", "ip"}

    for elem in root.iter():
        tag = elem.tag.lower()

        # Anaesthesia waveforms
        if any(t in tag for t in anaesthesia_tags):
            return "SBX_ANAES_WAVE"

        # PM-only waveforms
        if any(t in tag for t in pm_tags):
            return "SBX_PM_WAVE"

    return None


def classify_docom_waveform(line):
    l = line.lower()
    if any(k in l for k in ["co2", "etco2", "agent", "aa", "gas"]):
        return "DOCOM_ANAES_WAVE"
    if any(k in l for k in ["ecg", "spo2", "pleth", "pulse", "ibp", "nibp"]):
        return "DOCOM_PM_WAVE"
    return None



DOCOM_TS_RE = re.compile(
    r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\w+\s+\d{2},\s+\d{4}\s+\d{2}:\d{2}:\d{2}\.\d{3}"
)

def extract_docom_waveform_events(docom_log_path):
    events = []
    current_ts = None
    wave_type = None

    with open(docom_log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            m = DOCOM_TS_RE.search(line)
            if m:
                if current_ts and wave_type:
                    events.append({
                        "timestamp": current_ts.isoformat(),
                        "channel": wave_type
                    })
                current_ts = datetime.strptime(
                    m.group(0), "%a, %b %d, %Y %H:%M:%S.%f"
                )
                wave_type = None
                continue

            wt = classify_docom_waveform(line)
            if wt:
                wave_type = wt

        if current_ts and wave_type:
            events.append({
                "timestamp": current_ts.isoformat(),
                "channel": wave_type
            })

    return events

def write_waveform_csv(waveform_events, csv_path):
    """
    Writes waveform metadata and summary statistics to CSV.
    Raw waveform arrays are intentionally NOT written.
    """

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "timestamp",
            "stream",
            "waveform",
            "gas",
            "lead",
            "sample_count",
            "min",
            "max",
            "mean"
        ])

        for e in waveform_events:
            data = e.get("data", [])

            if data:
                min_v = min(data)
                max_v = max(data)
                mean_v = round(statistics.mean(data), 4)
            else:
                min_v = max_v = mean_v = ""

            writer.writerow([
                e["timestamp"],
                e["stream"],
                e["waveform"],
                e.get("attributes", {}).get("gas", ""),
                e.get("attributes", {}).get("lead", ""),
                len(data),
                min_v,
                max_v,
                mean_v
            ])


def write_waveform_jsonl(waveform_events, jsonl_path):
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for e in waveform_events:
            f.write(json.dumps(e) + "\n")


def Waveform_freq_check_main():
        sbx_waveform_events = extract_sbx_waveform_events(config.SBX_LOG)
        print(f"✅ Extracted {len(sbx_waveform_events)} SBX waveform events")
        write_waveform_csv(sbx_waveform_events, "Freqency_check/sbx_waveforms.csv")
        write_waveform_jsonl(sbx_waveform_events, "Freqency_check/sbx_waveforms.jsonl")
        #docom_events = extract_docom_waveform_events(r"C:\Users\212805796\Documents\Automation\Darwin log compare\DoComLog.txt")
        #print(f"Extracted {len(docom_events)} DoCom waveform events")
    

if __name__ == "__main__":
    SBX_log_path = config.SBX_LOG
    sbx_events = extract_sbx_waveform_events(SBX_log_path)
    print(f"Extracted {len(sbx_events)} SBX waveform events")
    print(sbx_events[:5])
    write_waveform_csv(sbx_events, "Freqency_check/sbx_waveforms.csv")
    write_waveform_jsonl(sbx_events, "Freqency_check/sbx_waveforms.jsonl")
    #docom_events = extract_docom_waveform_events(r"C:\Users\212805796\Documents\Automation\Darwin log compare\DoComLog.txt")
    #print(f"Extracted {len(docom_events)} DoCom waveform events")

    #all_events = sbx_events + docom_events
    #print(f"Total waveform events: {len(all_events)}")

    # Optionally save to JSON for later analysis
   # with open("output/waveform_events.json", "w", encoding="utf-8") as f:
   #     json.dump(all_events, f, indent=2)