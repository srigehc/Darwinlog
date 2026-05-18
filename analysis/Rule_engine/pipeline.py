import os
import sys
import json

# Add current directory to path BEFORE importing local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Current directory
import phase1_correlation
import phase2_validation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))  # Parent directory
import config
# ✅ Absolute path to Rule_engine directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = config.BASE_DIR
# ✅ Adjust ONLY these if files move
#CORRELATION_TABLE = config.CORRELATION_TABLE
CORRELATION_TABLE = os.path.join(file_path, "outputs", "correlation_table.csv")
RULE_FILE = os.path.join(
    BASE_DIR, "rules.yaml"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR, "validated_correlation.json"
)


def main():
    print("▶ Running Phase 1: Deterministic Auto-Correlation")
    print("   Using correlation table:", CORRELATION_TABLE)

    chains = phase1_correlation.build_correlation_chains(CORRELATION_TABLE)
    print(f"✔ Built {len(chains)} correlation chains")

    print("▶ Running Phase 2: Rule-Based Validation")
    print("   Using rules file:", RULE_FILE)

    validated = phase2_validation.apply_rules(chains, RULE_FILE)
    print(f"✔ Validated {len(validated)} chains")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2)

    print(f"✅ Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()