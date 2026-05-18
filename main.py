# This is the main entry point for the log normalization and correlation process.
# It orchestrates the normalization of different log types and saves the combined output.
# After running this, you can run analysis/correlation_engine.py to perform correlation and save results to CSV.
#this is step 1)
from datetime import datetime
import json
from dataclasses import asdict

from analysis import correlation_engine
from analysis.Rule_engine import coverage_summary
import config
from normalizers.system_log import normalize_system_logs
from normalizers.hl7_log import normalize_hl7_log
from normalizers.sbx_log import normalize_sbx_log
from normalizers.ohmeda_log import normalize_ohmeda_log
from Freqency_check import frequency_validation
from analysis.Rule_engine import pipeline

def main():
    # ---------- Phase 1: Normalize ----------
    system_events = normalize_system_logs(config.SystemLog)
    print("System events in main():", len(system_events))

    hl7_events = normalize_hl7_log(config.HL7_LOG)
    print("HL7 events in main():", len(hl7_events))

    # ✅ derive SBX base time from SYSTEM
    sbx_base_time = system_events[0].timestamp if system_events else None

    sbx_events = normalize_sbx_log(config.SBX_LOG, sbx_base_time)
    print("SBX events in main():", len(sbx_events))
    
    base_date = sbx_base_time.strftime("%Y-%m-%d")
    ohmeda_events = normalize_ohmeda_log(config.DOCOM_LOG, base_date)
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
    with open("outputs/normalized_logs.json", "w", encoding="utf-8") as f:
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
    print("\n\n=========\t==============\t============\t===========\n          Logs normalized...           \n=========\t==============\t============\t===========")
    correlation_engine.correlation_engine_main()
    print("\n\n=========\t==============\t============\t===========\n          Correlation matrix generatied...       \n=========\t==============\t============\t===========")
    pipeline.main()
    print("\n\n=========\t==============\t============\t===========\n          Correlation Rules applied...           \n=========\t==============\t============\t===========")
    coverage_summary.main()
    print("\n\n=========\t==============\t============\t===========\n         Correlation Summary Generated...           \n=========\t==============\t============\t===========")
    print("\n\n=========\t==============\t============\t===========\n         Generating numarical and waveform summary...           \n=========\t==============\t============\t===========")
    frequency_validation.freqency_validation_main()
    print ("\n\n=========\t==============\t============\t===========\n          Running frequency validation...           \n=========\t==============\t============\t===========")
    print("\n\n=========\t==============\t============\t===========\n         All processes completed successfully!           \n=========\t==============\t============\t===========")
    print("\n\n=========\t==============\t============\t===========\n         Check outputs in correlation_summary and frequency_validations           \n=========\t==============\t============\t==========="  )
