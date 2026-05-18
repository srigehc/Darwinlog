#!/usr/bin/env python
"""
Master Orchestration Script
Runs the analysis pipeline in sequence:
1. main.py (Normalize logs)
2. correlation_engine.py (Correlate events)
3. Pipeline.py (Validate correlations)
4. coverage_summary.py (Generate coverage report)
"""

import subprocess
import sys
import os
from datetime import datetime

# Get project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define pipeline steps
PIPELINE_STEPS = [
    {
        "name": "Normalization",
        "script": "main.py",
        "description": "Normalize logs from all sources (System, HL7, SBX, Ohmeda)"
    },
    {
        "name": "Correlation Engine",
        "script": "analysis/correlation_engine.py",
        "description": "Correlate normalized events across systems"
    },
    {
        "name": "Validation Pipeline",
        "script": "analysis/Rule_engine/pipeline.py",
        "description": "Validate correlations using rule engine"
    },
    {
        "name": "Coverage Summary",
        "script": "analysis/Rule_engine/coverage_summary.py",
        "description": "Generate coverage report"
    },
]

def run_step(step_num, total_steps, script_path, description):
    """
    Run a single pipeline step.
    Returns True on success, False on failure.
    """
    full_path = os.path.join(PROJECT_ROOT, script_path)
    
    print("\n" + "=" * 70)
    print(f"[{step_num}/{total_steps}] {description}")
    print("=" * 70)
    print(f"📍 Script: {script_path}")
    print(f"⏱️  Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    try:
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, full_path],
            cwd=PROJECT_ROOT,
            capture_output=False,
            text=True,
            timeout=600  # 10 minute timeout per step
        )
        
        print("-" * 70)
        print(f"⏱️  End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result.returncode == 0:
            print(f"✅ PASSED")
            return True
        else:
            print(f"❌ FAILED with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("-" * 70)
        print(f"⏱️  End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  TIMEOUT - script took longer than 10 minutes")
        print(f"❌ FAILED")
        return False
    except Exception as e:
        print("-" * 70)
        print(f"⏱️  End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"❌ ERROR: {str(e)}")
        return False


def main():
    """
    Execute the full pipeline in sequence.
    """
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DARWIN LOG ANALYSIS PIPELINE" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    print(f"\n🚀 Pipeline started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Working directory: {PROJECT_ROOT}")
    print(f"📋 Total steps: {len(PIPELINE_STEPS)}")
    
    results = {}
    failed_step = None
    
    for i, step in enumerate(PIPELINE_STEPS, 1):
        script_name = step["script"]
        results[script_name] = {
            "name": step["name"],
            "description": step["description"],
            "status": "pending"
        }
        
        success = run_step(i, len(PIPELINE_STEPS), script_name, step["description"])
        results[script_name]["status"] = "completed" if success else "failed"
        
        if not success:
            failed_step = i
            print(f"\n⚠️  Pipeline stopped at step {i}")
            break
    
    # Print summary
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    
    for i, (script, result) in enumerate(results.items(), 1):
        status_icon = "✅" if result["status"] == "completed" else "❌" if result["status"] == "failed" else "⏸️"
        print(f"{i}. {status_icon} {result['name']:25} {result['status'].upper():12} - {result['description']}")
    
    print("=" * 70)
    
    if failed_step:
        print(f"\n❌ PIPELINE FAILED at step {failed_step}")
        print(f"⏱️  Failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 1
    else:
        print(f"\n✅ PIPELINE COMPLETED SUCCESSFULLY")
        print(f"⏱️  Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📊 Output files generated:")
        print("   - output/normalized_logs.json")
        print("   - output/correlation_table.csv")
        print("   - analysis/Rule_engine/validated_correlation.json")
        print("   - analysis/Rule_engine/coverage_summary.json")
        print("   - analysis/Rule_engine/coverage_summary.csv")
        print("   - analysis/Rule_engine/missing_events.csv")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
