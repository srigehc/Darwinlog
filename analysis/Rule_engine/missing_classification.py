import csv
import json
import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MISSING_EVENTS_FILE = os.path.join(BASE_DIR, "missing_events.csv")
RULE_FILE = os.path.join(BASE_DIR, "missing_classification_rules.yaml")
OUTPUT_JSON = os.path.join(BASE_DIR, "missing_classification.json")
OUTPUT_CSV = os.path.join(BASE_DIR, "missing_classification.csv")


def load_rules():
    with open(RULE_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)["rules"]


def classify_event(event_text, missing_targets, rules):
    text = event_text.lower()

    for rule in rules:
        if "missing_in" in rule:
            if rule["missing_in"] not in missing_targets:
                continue

        keywords = rule.get("system_event_contains", [])
        if keywords:
            if not any(k.lower() in text for k in keywords):
                continue

        return {
            "classification": rule["classification"],
            "reason": rule["reason"],
            "rule_id": rule["id"],
        }

    # Fallback
    return {
        "classification": "REVIEW_REQUIRED",
        "reason": "No classification rule matched",
        "rule_id": "DEFAULT",
    }


def main():
    rules = load_rules()
    classified = []

    with open(MISSING_EVENTS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            missing_in = []
            if row["SBX"] == "False":
                missing_in.append("SBX")
            if row["DOCOM"] == "False":
                missing_in.append("DOCOM")
            if row["HL7"] == "False":
                missing_in.append("HL7")

            result = classify_event(
                row["event"],
                missing_in,
                rules
            )

            classified.append({
                "time": row["time"],
                "event": row["event"],
                "type": row["type"],
                "missing_in": missing_in,
                **result
            })

    # Write JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(classified, f, indent=2)

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "time",
                "event",
                "type",
                "missing_in",
                "classification",
                "reason",
                "rule_id",
            ]
        )
        writer.writeheader()
        for r in classified:
            r["missing_in"] = ",".join(r["missing_in"])
            writer.writerow(r)

    print("✅ Missing event classification completed")
    print("   →", OUTPUT_JSON)
    print("   →", OUTPUT_CSV)


if __name__ == "__main__":
    main()