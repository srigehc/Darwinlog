#!/usr/bin/env python3
"""
Auto-setup and run script for Darwin Log Compare project
Run this script to automatically install dependencies and execute the pipeline
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    try:
        # Use shell=True for Windows compatibility, but avoid it when possible
        if sys.platform == "win32":
            result = subprocess.run(cmd, shell=True, capture_output=False)
        else:
            result = subprocess.run(cmd.split(), capture_output=False)
        
        if result.returncode != 0:
            print(f"❌ {description} failed with exit code {result.returncode}")
            return False
        print(f"✅ {description} completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  Darwin Log Compare - Auto Setup & Run")
    print("="*60)
    
    # Step 1: Check Python version
    print(f"\n✓ Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    # Step 2: Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"✓ Working directory: {script_dir}")
    
    # Step 3: Check and install requirements
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print(f"\n📦 Installing dependencies from {requirements_file}...")
        install_cmd = f'"{sys.executable}" -m pip install -q -r {requirements_file}'
        if not run_command(install_cmd, "Dependency Installation"):
            print("⚠️  Warning: Some dependencies may not have installed correctly")
            print("Attempting to continue anyway...")
    else:
        print(f"⚠️  {requirements_file} not found, skipping dependency installation")
    
    # Step 4: Create output directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    print("✓ Output directory ready")
    
    # Step 5: Run main pipeline
    print("\n" + "="*60)
    print("  Starting Pipeline Execution")
    print("="*60)
    
    main_cmd = f'"{sys.executable}" main.py'
    if not run_command(main_cmd, "Pipeline Execution"):
        print("\n❌ Pipeline execution failed!")
        print("\nTroubleshooting:")
        print("1. Check that all input log files exist:")
        print("   - SystemLog.csv")
        print("   - hl7Log.txt")
        print("   - sbxLog.xml")
        print("   - DoComLog.txt")
        print("2. Ensure at least 500MB free disk space")
        print("3. Check file permissions")
        sys.exit(1)
    
    # Step 6: Summary
    print("\n" + "="*60)
    print("  ✅ ALL TASKS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📊 Output files:")
    output_dir = "outputs"
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            for f in sorted(files):
                fpath = os.path.join(output_dir, f)
                if os.path.isfile(fpath):
                    size = os.path.getsize(fpath)
                    print(f"   • {f} ({size:,} bytes)")
        else:
            print("   (No files yet)")
    
    print("\n📁 Frequency validation files:")
    freq_files = ["frequency_validations.csv", "frequency_validations.json"]
    for f in freq_files:
        fp = os.path.join("Freqency_check", f)
        if os.path.exists(fp):
            size = os.path.getsize(fp)
            print(f"   • {fp} ({size:,} bytes)")
    
    print("\n" + "="*60)
    print("  ✨ Done! Check the outputs/ folder for results")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ User interrupted the process")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

