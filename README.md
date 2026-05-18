# 🏥 Darwin Log Compare - Medical Device Log Analysis

Multi-source medical device log correlation and frequency validation pipeline.

## ⚡ Quick Start (< 2 Minutes)

### Windows Users:
**Option 1 (Easiest):** Double-click `RUN.bat`
**Option 2 (If Option 1 fails):** Right-click `RUN.ps1` → "Run with PowerShell"

### Mac/Linux Users:
```bash
python setup_and_run.py
```

Or see [INSTALLATION.md](INSTALLATION.md) for detailed setup.

---

## 📋 What This Does

Correlates events from 4 medical device log sources:

| Source | Format | Events |
|--------|--------|--------|
| **System Log** | CSV | 2,000+ |
| **HL7 Messages** | Text | 100+ |
| **SBX Monitoring** | XML | 50+ |
| **DoCom Anesthesia** | Text | 100+ |

**Outputs:**
- ✓ Normalized unified event log
- ✓ Cross-source event correlation
- ✓ Coverage analysis by event type
- ✓ Frequency validation with gap detection
- ✓ Missing event analysis

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [INSTALLATION.md](INSTALLATION.md) | Setup & usage instructions |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Error solutions & debugging |
| [DISTRIBUTION.md](DISTRIBUTION.md) | How to share with team |
| [PACKAGING_SUMMARY.md](PACKAGING_SUMMARY.md) | Package contents & options |

---

## 🎯 Getting Started

### Step 1: Verify Prerequisites
- ✓ Python 3.8+ installed ([download here](https://www.python.org/downloads/))
- ✓ Log files present in project folder:
  - `SystemLog.csv`
  - `hl7Log.txt`
  - `sbxLog.xml`
  - `DoComLog.txt`
- ✓ 500MB+ free disk space

### Step 2: Run the Program

**Windows:**
```bash
# Simply double-click:
RUN.bat

# Or if that fails, try:
RUN.ps1  (right-click → Run with PowerShell)
```

**Mac/Linux:**
```bash
python setup_and_run.py
```

### Step 3: Check Results
Results appear in `outputs/` folder:
- `normalized_logs.json` - All events
- `correlation_table.csv` - Event relationships
- `coverage_summary.csv` - Coverage metrics
- `frequency_validations.csv` - Frequency analysis

---

## 🛠️ Project Structure

```
Darwin log compare/
├── RUN.bat                    # ⭐ Windows launcher
├── RUN.ps1                    # ⭐ PowerShell launcher
├── setup_and_run.py           # Auto-setup script
├── main.py                    # Normalization pipeline
├── config.py                  # Configuration
│
├── normalizers/               # Source-specific parsers
│   ├── system_log.py
│   ├── hl7_log.py
│   ├── sbx_log.py
│   └── ohmeda_log.py
│
├── analysis/                  # Analysis modules
│   ├── correlation_engine.py
│   └── Rule_engine/
│       ├── coverage_summary.py
│       ├── pipeline.py
│       └── phase1_correlation.py
│
├── Freqency_check/           # Frequency analysis
│   └── frequency_validation.py
│
├── outputs/                  # Results (auto-created)
├── INSTALLATION.md           # 📖 Read this first
├── TROUBLESHOOTING.md        # 🆘 If you get errors
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Log file paths
SystemLog = "SystemLog.csv"
HL7_LOG = "hl7Log.txt"
SBX_LOG = "sbxLog.xml"
DOCOM_LOG = "DoComLog.txt"

# Frequency validation rules
NUMERIC_RULES = {
    "SBX_NUMERIC": {"expected_sec": 2.0, "tolerance_sec": 0.5},
    "DOCOM_NUMERIC": {"expected_sec": 10.0, "tolerance_sec": 2.0},
    "HL7_NUMERIC": {"expected_sec": 10.0, "tolerance_sec": 5.0}
}
```

---

## 📊 Output Files

### normalized_logs.json
All 4,000+ events in unified format:
```json
{
  "source": "SYSTEM",
  "event_type": "USER_ACTION",
  "timestamp": "2026-05-13T10:30:45.123456",
  "description": "User initiated setup"
}
```

### correlation_table.csv
Events matched across sources:
```
event_id,source,event_type,timestamp,correlated_count
1,SYSTEM,USER_ACTION,2026-05-13T10:30:45,3
2,HL7,ALARM,2026-05-13T10:31:12,2
```

### coverage_summary.csv
Coverage metrics by type:
```
Scope,Total,SBX %,DoCom %,HL7 %
OVERALL,251,58.2,73.3,73.3
User Action,174,64.4,81.6,81.6
Alarm,35,8.6,31.4,31.4
```

### frequency_validations.csv
Numeric stream frequency analysis:
```
stream,count,expected,max_gap,avg_gap,p90,p95,status
SBX_NUMERIC,81,2.0,243.888,2.154,2.301,2.505,FAIL
DOCOM_NUMERIC,181,10.0,11.029,9.887,10.234,10.876,PASS
HL7_NUMERIC,134,10.0,8.0,10.123,10.567,10.892,PASS
```

---

## 🚀 Common Tasks

### Run only normalization:
```bash
python main.py
```

### Run only correlation:
```bash
python analysis/correlation_engine.py
```

### Run only frequency analysis:
```bash
python Freqency_check/frequency_validation.py
```

### View correlation results:
```bash
python check_correlations.py
```

### View system log events:
```bash
python view_csv.py
```

---

## 🐛 Troubleshooting

### "Command not recognized" / "'C:\Program' error"
→ See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#error-cprogram-is-not-recognized)

### "Python not found"
→ See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#error-python-is-not-installed)

### "Output folder is empty"
→ See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#-output-files-empty-or-corrupted)

### Other issues?
→ See full [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide

---

## 📦 Sharing with Your Team

See [DISTRIBUTION.md](DISTRIBUTION.md) for:
- How to zip and share
- Deployment options
- Testing checklist
- Maintenance guide

---

## 📋 Requirements

- **Python:** 3.8+
- **Dependencies:** pandas 1.5.0+
- **OS:** Windows 7+, macOS 10.14+, or Linux
- **Disk:** 500MB minimum
- **RAM:** 4GB minimum
- **Input files:** 4 log files (included)

---

## 🔧 Tech Stack

- **Language:** Python 3
- **Standard Library:** json, csv, xml, datetime, re, statistics
- **External:** pandas (only dependency)
- **Log Formats:** CSV, XML, HL7 text
- **Output:** JSON, CSV

---

## 📝 Event Types Supported

### User Actions
- Setup, configuration, mode changes

### Alarms
- Equipment alarms, warnings, alerts

### State Transitions
- Device state changes, transitions

### Commands
- User commands, system commands

### Measurements
- Numeric measurements, parameters

### Status Updates
- Device status, connection status

---

## 🎯 Use Cases

1. **Quality Assurance:** Verify event logging across systems
2. **Troubleshooting:** Find gaps in event correlation
3. **Compliance:** Document event correlation for audits
4. **Analysis:** Study event sequences and timing
5. **Validation:** Ensure numeric data consistency

---

## 📈 Performance

| Log Size | Processing Time |
|----------|-----------------|
| 50K events | 30-60 seconds |
| 100K events | 1-2 minutes |
| 250K events | 3-5 minutes |
| 500K events | 10-15 minutes |

First run includes dependency installation (+1-2 min).

---

## 📞 Support

**For detailed help:**
- Installation issues → [INSTALLATION.md](INSTALLATION.md)
- Error messages → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Distribution → [DISTRIBUTION.md](DISTRIBUTION.md)
- Package details → [PACKAGING_SUMMARY.md](PACKAGING_SUMMARY.md)

---

## 📄 License

Internal Use Only

---

## ✨ Version

**Darwin Log Compare v1.0**
- Released: May 2026
- Status: Production Ready
- Support: Internal Team

---

**Ready to get started? Double-click `RUN.bat` and check the `outputs/` folder! 🚀**