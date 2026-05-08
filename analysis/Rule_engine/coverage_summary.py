import json
import csv
import os
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VALIDATED_FILE = os.path.join(BASE_DIR, "validated_correlation.json")
SUMMARY_JSON = os.path.join(BASE_DIR, "coverage_summary.json")
SUMMARY_CSV = os.path.join(BASE_DIR, "coverage_summary.csv")
MISSING_CSV = os.path.join(BASE_DIR, "missing_events.csv")


def load_validated_data():
    with open(VALIDATED_FILE, encoding="utf-8") as f:
        return json.load(f)


def generate_coverage_summary(records):
    total = len(records)

    overall = Counter()
    by_type = defaultdict(Counter)

    missing_rows = []

    for r in records:
        event_type = r["anchor"]["type"]

        sbx = r["coverage"]["SBX"]
        docom = r["coverage"]["DOCOM"]
        hl7 = r["coverage"]["HL7"]

        overall["TOTAL"] += 1
        overall["SBX"] += int(sbx)
        overall["DOCOM"] += int(docom)
        overall["HL7"] += int(hl7)

        by_type[event_type]["TOTAL"] += 1
        by_type[event_type]["SBX"] += int(sbx)
        by_type[event_type]["DOCOM"] += int(docom)
        by_type[event_type]["HL7"] += int(hl7)

        if not (sbx and docom and hl7):
            missing_rows.append({
                "time": r["anchor"]["time"],
                "event": r["anchor"]["event"],
                "type": event_type,
                "SBX": sbx,
                "DOCOM": docom,
                "HL7": hl7,
            })

    summary = {
        "overall": {
            "total": overall["TOTAL"],
            "SBX_coverage_pct": round(overall["SBX"] / total * 100, 2),
            "DOCOM_coverage_pct": round(overall["DOCOM"] / total * 100, 2),
            "HL7_coverage_pct": round(overall["HL7"] / total * 100, 2),
        },
        "by_type": {}
    }

    for t, c in by_type.items():
        summary["by_type"][t] = {
            "total": c["TOTAL"],
            "SBX_coverage_pct": round(c["SBX"] / c["TOTAL"] * 100, 2),
            "DOCOM_coverage_pct": round(c["DOCOM"] / c["TOTAL"] * 100, 2),
            "HL7_coverage_pct": round(c["HL7"] / c["TOTAL"] * 100, 2),
        }

    return summary, missing_rows


def write_outputs(summary, missing):
    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Scope", "Total", "SBX %", "DoCom %", "HL7 %"])

        writer.writerow([
            "OVERALL",
            summary["overall"]["total"],
            summary["overall"]["SBX_coverage_pct"],
            summary["overall"]["DOCOM_coverage_pct"],
            summary["overall"]["HL7_coverage_pct"],
        ])

        for t, s in summary["by_type"].items():
            writer.writerow([
                t,
                s["total"],
                s["SBX_coverage_pct"],
                s["DOCOM_coverage_pct"],
                s["HL7_coverage_pct"],
            ])

    with open(MISSING_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["time", "event", "type", "SBX", "DOCOM", "HL7"]
        )
        writer.writeheader()
        writer.writerows(missing)


def main():
    records = load_validated_data()
    summary, missing = generate_coverage_summary(records)
    write_outputs(summary, missing)

    print("✅ Coverage summary generated")
    print("   →", SUMMARY_JSON)
    print("   →", SUMMARY_CSV)
    print("   →", MISSING_CSV)


if __name__ == "__main__":
    main()