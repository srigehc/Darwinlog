import yaml


def apply_rules(correlation_chains, rule_file):
    with open(rule_file, "r") as f:
        rules = yaml.safe_load(f)["rules"]

    results = []

    for chain in correlation_chains:
        chain_result = {
            "anchor": chain["anchor"],
            "coverage": {
                "SBX": len(chain["SBX"]) > 0,
                "DOCOM": len(chain["DOCOM"]) > 0,
                "HL7": len(chain["HL7"]) > 0,
            },
            "rule_results": [],
            "final_status": "PASS",
        }

        for rule in rules:
            if rule.get("applies_to") and rule["applies_to"] != chain["anchor"]["type"]:
                continue

            triggered = False
            for key in rule.get("match", {}).get("system_event_contains", []):
                if key.lower() in chain["anchor"]["event"].lower():
                    triggered = True

            if not triggered:
                continue

            # Coverage rules
            failed = False

            if "require" in rule:
                if len(chain["SBX"]) < rule["require"].get("SBX_min", 0):
                    failed = True
                if len(chain["DOCOM"]) < rule["require"].get("DOCOM_min", 0):
                    failed = True

            if "require_SBX_contains" in rule:
                for required in rule["require_SBX_contains"]:
                    if not any(required in e for e in chain["SBX"]):
                        failed = True

            status = "PASS" if not failed else rule["severity"]
            chain_result["rule_results"].append(
                {"rule_id": rule["id"], "status": status}
            )

            if failed and rule["severity"] == "ERROR":
                chain_result["final_status"] = "FAIL"

        results.append(chain_result)

    return results