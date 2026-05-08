import os
import json
from phase1_correlation import build_correlation_chains
from phase2_validation import apply_rules

# ✅ Absolute path to Rule_engine directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Adjust ONLY these if files move
CORRELATION_TABLE = r"C:\Users\212805796\Documents\Automation\Darwin log compare\output\correlation_table.csv"

RULE_FILE = os.path.join(
    BASE_DIR, "rules.yaml"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR, "validated_correlation.json"
)


def main():
    print("▶ Running Phase 1: Deterministic Auto-Correlation")
    print("   Using correlation table:", CORRELATION_TABLE)

    chains = build_correlation_chains(CORRELATION_TABLE)
    print(f"✔ Built {len(chains)} correlation chains")

    print("▶ Running Phase 2: Rule-Based Validation")
    print("   Using rules file:", RULE_FILE)

    validated = apply_rules(chains, RULE_FILE)
    print(f"✔ Validated {len(validated)} chains")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2)

    print(f"✅ Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()