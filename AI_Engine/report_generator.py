"""Generates final outputs:
- Enriched CSV
- JSON report
- Human-readable summary

Consumes:
AI output + Interpretation + Feedback
"""

import pandas as pd
import json
from typing import Dict


class ReportGenerator:
    def __init__(self):
        pass

    # -----------------------------------------------------
    # 1. Save CSV Output
    # -----------------------------------------------------
    def generate_csv(self, df: pd.DataFrame, path: str = "final_report.csv"):
        """
        Save enriched dataframe as CSV
        """
        df.to_csv(path, index=False)

    # -----------------------------------------------------
    # 2. Generate JSON Output (structured)
    # -----------------------------------------------------
    def generate_json(self, df: pd.DataFrame, path: str = "final_report.json"):
        """
        Generate structured JSON output
        """
        import numpy as np

        results = []

        for _, row in df.iterrows():
            # Helper function to safely get value from Series
            def get_val(col_name):
                if col_name not in df.columns:
                    return None
                val = row[col_name]
                
                # Check if it's a Series (column doesn't exist properly)
                if isinstance(val, pd.Series):
                    return None
                    
                # Check for NaN/None
                try:
                    if pd.isna(val):
                        return None
                except (ValueError, TypeError):
                    return None
                    
                # Convert numpy types to Python types
                if isinstance(val, (np.integer, np.floating)):
                    return val.item()
                if isinstance(val, np.bool_):
                    return bool(val)
                return val

            results.append({
                "stream": get_val("stream"),
                "source": get_val("source"),
                "anomaly_flag": int(get_val("anomaly_flag") or 0),
                "anomaly_score": float(get_val("anomaly_score") or 0),
                "severity": get_val("severity"),
                "issue_type": get_val("issue_type"),
                "pattern": get_val("pattern"),
                "insight": get_val("insight"),
                "feedback_status": get_val("feedback_status")
            })

        with open(path, "w") as f:
            json.dump(results, f, indent=2)

    # -----------------------------------------------------
    # 3. Build Summary Metrics
    # -----------------------------------------------------
    def build_summary(self, df: pd.DataFrame) -> Dict:
        """
        Create summary statistics
        """

        summary = {
            "total_streams": len(df),
            "anomalies_detected": int((df["anomaly_flag"] == -1).sum()),
            "new_issues": int((df["feedback_status"] == "NEW").sum()),
            "accepted_issues": int((df["feedback_status"] == "ACCEPTED").sum()),
            "escalated_issues": int((df["feedback_status"] == "ESCALATED").sum())
        }

        return summary

    # -----------------------------------------------------
    # 4. Human Readable Report
    # -----------------------------------------------------
    def generate_text_report(self, df: pd.DataFrame) -> str:
        """
        Generate readable insights report
        """

        report_lines = []

        report_lines.append("=== LOG ANALYSIS REPORT ===\n")

        summary = self.build_summary(df)

        report_lines.append(f"Total Streams Analyzed: {summary['total_streams']}")
        report_lines.append(f"Anomalies Detected: {summary['anomalies_detected']}")
        report_lines.append(f"New Issues: {summary['new_issues']}")
        report_lines.append(f"Accepted Issues: {summary['accepted_issues']}")
        report_lines.append(f"Escalated Issues: {summary['escalated_issues']}\n")

        report_lines.append("=== DETAILED FINDINGS ===\n")

        for _, row in df.iterrows():

            # Filter: focus only important rows
            if row["feedback_status"] == "ACCEPTED":
                continue

            if row["anomaly_flag"] == 1:
                continue

            report_lines.append(f"Stream: {row.get('stream')}")
            report_lines.append(f"Source: {row.get('source')}")
            report_lines.append(f"Issue: {row.get('issue_type')}")
            report_lines.append(f"Pattern: {row.get('pattern')}")
            report_lines.append(f"Severity: {row.get('severity')}")
            report_lines.append(f"Status: {row.get('feedback_status')}")
            report_lines.append(f"Insight: {row.get('insight')}")
            report_lines.append("-" * 50)

        return "\n".join(report_lines)

    # -----------------------------------------------------
    # 5. Save Text Report
    # -----------------------------------------------------
    def save_text_report(self, report: str, path: str = "analysis_report.txt"):
        with open(path, "w") as f:
            f.write(report)

    # -----------------------------------------------------
    # 6. Full Report Pipeline
    # -----------------------------------------------------
    def generate_all(self, df: pd.DataFrame):
        """
        End-to-end report generation
        """

        # CSV
        self.generate_csv(df)

        # JSON
        self.generate_json(df)

        # Text
        report = self.generate_text_report(df)
        self.save_text_report(report)

        return report