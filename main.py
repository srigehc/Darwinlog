# This is the main entry point for the log normalization and correlation process.
# It orchestrates the normalization of different log types and saves the combined output.
# After running this, you can run analysis/correlation_engine.py to perform correlation and save results to CSV.
#this is step 1)
from datetime import datetime
import json
import os
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
from AI_Engine.Master import main as ai_main

def main():
    # ---------- Phase 1: Normalize ----------
    system_events = normalize_system_logs(config.SystemLog)
    print("✅ System events:", len(system_events))

    # For large files, use batch streaming
    print("💾 Processing HL7 logs in batch streaming mode...")
    hl7_file = "outputs/hl7_streaming.json"
    stream_normalize_events(
        "HL7", 
        normalize_hl7_log(config.HL7_LOG), 
        hl7_file
    )

    # ✅ derive SBX base time from SYSTEM
    sbx_base_time = system_events[0].timestamp if system_events else None

    sbx_events = normalize_sbx_log(config.SBX_LOG, sbx_base_time)
    print("✅ SBX events:", len(sbx_events))
    
    # For large Ohmeda file, use streaming/batch approach
    base_date = sbx_base_time.strftime("%Y-%m-%d") if sbx_base_time else None
    
    print("💾 Processing Ohmeda logs in batch streaming mode...")
    ohmeda_file = "outputs/ohmeda_streaming.json"
    stream_normalize_events(
        "Ohmeda",
        normalize_ohmeda_log(config.DOCOM_LOG, base_date),
        ohmeda_file
    )
    
    # ---------- Phase 2: Merge (without HL7 & Ohmeda - they're streamed) ----------
    all_events = system_events + sbx_events

    print(f"✅ Normalized {len(all_events)} events (HL7 and Ohmeda streamed separately)")

    # ---------- Phase 3: Save (optional) ----------
    with open("outputs/normalized_logs.json", "w", encoding="utf-8") as f:
        json.dump(
            [serialize_event(e) for e in all_events],
            f,
            indent=2
        )
def print_section(title):
    """Helper to print section headers consistently"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def stream_normalize_events(source_name, event_generator, output_file):
    """Generic batch streaming function for large log files"""
    total = 0
    
    try:
        with open(output_file, "w", encoding="utf-8") as out_f:
            out_f.write("[\n")
            first = True
            
            for event in event_generator:
                if not first:
                    out_f.write(",\n")
                first = False
                
                out_f.write(json.dumps(serialize_event(event)))
                total += 1
                
                if total % 50000 == 0:
                    print(f"  → {source_name}: Processed {total} events...")
            
            out_f.write("\n]")
        
        print(f"✅ Streamed {total} {source_name} events to {output_file}")
    except Exception as e:
        print(f"[ERROR] Streaming {source_name} logs: {e}")


def serialize_event(event):
    d = asdict(event)
    if isinstance(d.get("timestamp"), datetime):
        d["timestamp"] = d["timestamp"].isoformat()
    return d


if __name__ == "__main__":
    try:
        print_section("Phase 1: Normalizing Logs")
        main()
        
        print_section("Phase 2: Generating Correlation Matrix")
        correlation_engine.correlation_engine_main()
        
        print_section("Phase 3: Applying Correlation Rules")
        pipeline.main()
        
        print_section("Phase 4: Generating Coverage Summary")
        coverage_summary.main()
        
        print_section("Phase 5: Validating Frequency & Waveforms")
        frequency_validation.freqency_validation_main()
        
        print_section("Phase 6: Running AI Analysis")
        ai_main(input_file="frequency_validations.csv")
        
        print_section("✅ All processes completed successfully!")
        print("📊 Check outputs in: correlation_summary/ and frequency_validations/\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()