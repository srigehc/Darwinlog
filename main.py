from datetime import datetime
import json
from dataclasses import asdict

from normalizers.system_log import normalize_system_logs
from normalizers.hl7_log import normalize_hl7_log
from normalizers.sbx_log import normalize_sbx_log
from normalizers.ohmeda_log import normalize_ohmeda_log


def main():
    # ---------- Phase 1: Normalize ----------
    system_events = normalize_system_logs("SystemLog.csv")
    print("System events in main():", len(system_events))

    hl7_events = normalize_hl7_log("hl7Log.txt")
    print("HL7 events in main():", len(hl7_events))

    # ✅ derive SBX base time from SYSTEM
    sbx_base_time = system_events[0].timestamp if system_events else None

    sbx_events = normalize_sbx_log("sbxLog.xml", sbx_base_time)
    print("SBX events in main():", len(sbx_events))

    ohmeda_events = normalize_ohmeda_log("DoComLog.txt")
    print("Ohmeda events in main():", len(ohmeda_events))

    # ---------- Phase 2: Merge ----------
    all_events = (
        system_events +
        hl7_events +
        sbx_events +
        ohmeda_events
    )

    print("✅ Normalized", len(all_events), "events")

    # ---------- Phase 3: Save (optional) ----------
    with open("output/normalized_logs.json", "w", encoding="utf-8") as f:
        json.dump(
            [serialize_event(e) for e in all_events],
            f,
            indent=2
        )


def serialize_event(event):
    d = asdict(event)
    if isinstance(d.get("timestamp"), datetime):
        d["timestamp"] = d["timestamp"].isoformat()
    return d


if __name__ == "__main__":
    main()
