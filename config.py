import os

# ✅ Base input directory
BASE_DIR = r"C:\Users\212805796\Documents\Automation\Darwin log compare"

# ✅ Input files
SBX_LOG = os.path.join(BASE_DIR, "sbxLog.xml")
DOCOM_LOG = os.path.join(BASE_DIR, "DoComLog.txt")
HL7_LOG = os.path.join(BASE_DIR, "hl7Log.txt")
SystemLog = os.path.join(BASE_DIR, "SystemLog.csv")

# intermidiate output (normalized logs)
NORMALIZED_NUM_FILE = os.path.join(BASE_DIR, "Freqency_check", "normalized_numeric_logs.json")
NORMALIZED_WAVEFORM_FILE = os.path.join(BASE_DIR, "Freqency_check", "sbx_waveforms.jsonl")
CORRELATION_TABLE = os.path.join(BASE_DIR, "output", "correlation_table.csv")

# ✅ Output directory (create if not exists)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Output files
FREQUENCY_CSV = os.path.join(OUTPUT_DIR, "frequency_validations.csv")
WAVEFORM_JSONL = os.path.join(OUTPUT_DIR, "sbx_waveforms.jsonl")

# ✅ Frequency rules (centralized)
NUMERIC_RULES = {
    "SBX_NUMERIC": {"expected_sec": 2.0, "tolerance_sec": 0.5},
    "DOCOM_NUMERIC": {"expected_sec": 10.0, "tolerance_sec": 2.0},
    "HL7_NUMERIC": {"expected_sec": 10.0, "tolerance_sec": 2.0},
}

WAVEFORM_RULES = {
    "SBX_ANAES_WAVE": {"expected_sec": 0.4, "tolerance_sec": 0.1},
    "SBX_PM_WAVE": {"expected_sec": 0.5, "tolerance_sec": 0.15},
}
