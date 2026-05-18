# Darwin Log Compare - Installation & Execution Guide

## ⚠️ Quick Help

### "Got an error?" 
👉 **See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for solutions to common issues

### Most Common Error: "'C:\Program' is not recognized"
**Quick Fix:** Right-click `RUN.ps1` → "Run with PowerShell"

---

## Quick Start (Recommended for Windows Users)

### Option 1: Double-Click to Run (Easiest)
1. Download the entire project folder
2. **Double-click `RUN.bat`** in the project root
3. Wait for the program to complete (2-5 minutes depending on log size)
4. Check the `outputs/` folder for results

That's it! No setup required.

---

## Manual Setup (for Advanced Users or Linux/Mac)

### Prerequisites
- **Python 3.8 or higher** installed and in your system PATH
- Windows, macOS, or Linux

### Step 1: Verify Python Installation
```bash
python --version
# or on macOS/Linux:
python3 --version
```
Should show Python 3.8+. If not, install from: https://www.python.org/

### Step 2: Install Dependencies
```bash
# Navigate to project folder
cd path\to\Darwin log compare

# Install required packages
pip install -r requirements.txt
```

### Step 3: Run the Program
```bash
python setup_and_run.py
```
Or simply run main.py directly:
```bash
python main.py
```

---

## What the Program Does

The pipeline executes 4 sequential steps:

1. **Normalization** (main.py)
   - Reads 4 log sources: System Log, HL7, SBX XML, DoCom Log
   - Normalizes all events into a unified format
   - Output: `outputs/normalized_logs.json`

2. **Correlation Engine** (correlation_engine.py)
   - Correlates events across the 4 sources
   - Generates correlation table
   - Output: `outputs/correlation_table.csv`

3. **Coverage Summary** (coverage_summary.py)
   - Calculates event coverage across sources
   - Output: `outputs/coverage_summary.csv`

4. **Frequency Validation** (frequency_validation.py)
   - Validates numeric data frequency
   - Output: `outputs/frequency_validations.csv`

---

## Output Files

All results are saved in the `outputs/` folder:

- **normalized_logs.json** - All events in unified format
- **correlation_table.csv** - Event correlations across sources
- **coverage_summary.csv** - Coverage metrics by event type
- **frequency_validations.csv** - Frequency analysis results
- **missing_events.csv** - Events that couldn't be correlated
- **frequency_validations.json** - Detailed frequency insights

---

## Troubleshooting

### Error: "'C:\Program' is not recognized"
This error occurs when Python is installed in a path with spaces (like `C:\Program Files\Python\...`).

**Solutions (try in order):**

1. **Use PowerShell instead of Command Prompt:**
   - Right-click `RUN.ps1` → "Run with PowerShell"
   - This handles paths with spaces better

2. **Reinstall Python to a path without spaces:**
   - Uninstall Python
   - Install to: `C:\Python311` (instead of Program Files)
   - Make sure ✓ "Add Python to PATH" is checked
   - Restart computer
   - Double-click `RUN.bat` again

3. **Run from Command Prompt with full quotes:**
   ```bash
   cd "C:\Users\...\Darwin log compare"
   python setup_and_run.py
   ```

4. **Use Administrator Command Prompt:**
   - Right-click `cmd.exe` → "Run as Administrator"
   - Navigate to project folder
   - Run: `python setup_and_run.py`

### Error: "Python is not installed"
- Download Python from https://www.python.org/
- **Important:** Check "Add Python to PATH" during installation
- Restart your computer and try again

### Error: "ModuleNotFoundError: No module named 'pandas'"
```bash
# Install dependencies manually
pip install pandas
```

### Error: "Log files not found"
- Verify these files exist in the project root:
  - `SystemLog.csv`
  - `hl7Log.txt`
  - `sbxLog.xml`
  - `DoComLog.txt`

### Program runs slowly
- This is normal for large log files (100K+ events)
- First run takes longer due to dependency installation
- Subsequent runs are faster

### Output folder is empty
- Check the console output for error messages
- Ensure input log files are in the correct location
- Verify sufficient disk space (at least 100MB free)

---

## For Development/Customization

### Edit Configuration
Edit `config.py` to change:
- Log file paths
- Frequency validation rules
- Medical event type definitions
- Output paths

### Run Individual Steps
```bash
# Just normalization
python main.py

# Just correlation
python analysis/correlation_engine.py

# Just frequency validation
python Freqency_check/frequency_validation.py
```

### View Raw Logs
```bash
# Check system log events
python view_csv.py

# Check correlations
python check_correlations.py
```

---

## Requirements

- **pandas** 1.5.0+ (automatically installed)
- **Python 3.8+**
- Windows 7+, macOS 10.14+, or Linux
- 500MB disk space minimum
- 4GB RAM minimum

---

## Support & Issues

If you encounter issues:
1. Check the console output for error messages
2. Verify all input log files exist
3. Ensure Python 3.8+ is installed
4. Try running from command line for detailed error output:
   ```bash
   python setup_and_run.py
   ```

---

## Version Info
- Project: Darwin Log Compare v1.0
- Last Updated: May 2026
- License: Internal Use Only
