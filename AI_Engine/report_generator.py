
"""
report_generator.py

Generates final outputs:
- Enriched CSV
- JSON report
- Human-readable summary
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
        df.to_csv(path, index=False)

    # -----------------------------------------------------
    # 2. Generate JSON Output
    # -----------------------------------------------------
    def generate_json(self, df: pd.DataFrame, path: str = "final_report.json"):

        results = []

        for _, row in df.iterrows():
            results.append({
                "stream": row.get("stream"),
                "source": row.get("source"),
                "anomaly_flag": int(row.get("anomaly_flag", 0)),
                "anomaly_score": float(row.get("anomaly_score", 0)),
                "severity": row.get("severity"),
                "issue_type": row.get("issue_type"),
                "pattern": row.get("pattern"),
                "insight": str(row.get("insight")),
                "feedback_status": row.get("feedback_status")
            })

        with open(path, "w") as f:
            json.dump(results, f, indent=2)

    # -----------------------------------------------------
    # 3. Summary Metrics
    # -----------------------------------------------------
    def build_summary(self, df: pd.DataFrame) -> Dict:

        return {
            "total_streams": df["stream"].nunique(),
            "anomalies_detected": int((df["anomaly_flag"] == -1).sum()),
            "new_issues": int((df["feedback_status"] == "NEW").sum()),
            "accepted_issues": int((df["feedback_status"] == "ACCEPTED").sum()),
            "escalated_issues": int((df["feedback_status"] == "ESCALATED").sum())
        }

    # -----------------------------------------------------
    # ✅ MAIN FIXED REPORT FUNCTION
    # -----------------------------------------------------
    def generate_text_report(self, df, corr_result=None, alignment_info=None):

        df = df.copy()
        report_lines = []

        report_lines.append("=== LOG ANALYSIS REPORT ===\n")

        # ✅ Streams (FIXED)
        streams = df["stream"].dropna().unique().tolist()
        
        streams_text = ", ".join(streams)
        
        report_lines.append(f"Total Streams Analyzed: {len(streams)} {{Streams: {streams_text}}}\n" )

        report_lines.append("")

        # ✅ Summary
        summary = self.build_summary(df)

        report_lines.append(f"Anomalies Detected: {summary['anomalies_detected']}")
        report_lines.append(f"New Issues: {summary['new_issues']}")
        report_lines.append(f"Accepted Issues: {summary['accepted_issues']}")
        report_lines.append(f"Escalated Issues: {summary['escalated_issues']}\n")

        # ✅ Alignment Info
        if alignment_info:
            report_lines.append("=== TIME ALIGNMENT INFO ===")
            report_lines.append(f"Start Time: {alignment_info.get('start_time')}")
            report_lines.append(f"Confidence: {alignment_info.get('confidence')}")
            report_lines.append("")

        # ✅ Frequency Section
        report_lines.append("=== FREQUENCY VALIDATION ===\n")

        for _, row in df.iterrows():
            report_lines.append(f"Stream: {row.get('stream')}")
            report_lines.append(f"  Avg Gap: {row.get('avg_gap')} ms")
            report_lines.append(f"  P95 Gap: {row.get('p95_gap')} ms")
            report_lines.append(f"  Expected: {row.get('expected_gap')} ms")
            report_lines.append(f"  Status: {row.get('status')}")
            report_lines.append("")

        # ✅ Correlation Section
        if corr_result:

            report_lines.append("=== DATA PROPAGATION ANALYSIS ===\n")

            for system in ["sbx", "docom", "hl7"]:
                s = corr_result.get(system, {})

                report_lines.append(f"{system.upper()}:")
                report_lines.append(
                    f"  Missing Ratio: {round(s.get('missing_ratio', 0)*100, 2)}%"
                )
                report_lines.append(f"  Pattern: {s.get('pattern')}")
                report_lines.append(f"  Max Burst: {s.get('max_burst')}")
                report_lines.append("")

            # ✅ Intelligent summary
            report_lines.append("=== CORRELATION SUMMARY ===")

            sbx = corr_result.get("sbx", {})
            docom = corr_result.get("docom", {})
            hl7 = corr_result.get("hl7", {})

            if (
                sbx.get("missing_ratio", 0) < 0.1 and
                docom.get("missing_ratio", 0) < 0.1 and
                hl7.get("missing_ratio", 0) < 0.1
            ):
                report_lines.append("✔ All systems are consistent with source logs")
            else:
                report_lines.append("⚠ Data discrepancies detected across systems")

            report_lines.append("")

        # ✅ Findings Section
        report_lines.append("=== DETAILED FINDINGS ===\n")

        for _, row in df.iterrows():

            if row.get("feedback_status") == "ACCEPTED":
                continue

            if row.get("anomaly_flag") == 1:
                continue

            insight = row.get("insight")

            if isinstance(insight, pd.Series):
                insight = insight.iloc[0]

            report_lines.append(f"Stream: {row.get('stream')}")
            report_lines.append(f"Issue: {row.get('issue_type')}")
            report_lines.append(f"Pattern: {row.get('pattern')}")
            report_lines.append(f"Severity: {row.get('severity')}")
            report_lines.append(f"Status: {row.get('feedback_status')}")
            report_lines.append(f"Insight: {insight}")
            report_lines.append("-" * 50)

        # ✅ Final Conclusion
        report_lines.append("=== FINAL CONCLUSION ===")

        if corr_result:
            sbx_loss = corr_result.get("sbx", {}).get("missing_ratio", 0)

            if sbx_loss < 0.1:
                report_lines.append("✔ System behavior is NORMAL")
            else:
                report_lines.append("⚠ Data propagation issues detected")

        report_lines.append("")

        return "\n".join(report_lines)

    # -----------------------------------------------------
    # Save Text
    # -----------------------------------------------------
    def save_text_report(self, report: str, path: str = "analysis_report.txt"):
        with open(path, "w") as f:
            f.write(report)

    # -----------------------------------------------------
    # Full Pipeline
    # -----------------------------------------------------
    def generate_all(self, df: pd.DataFrame, corr_result=None, alignment_info=None):

        self.generate_csv(df)
        self.generate_json(df)

        report = self.generate_text_report(
            df,
            corr_result=corr_result,
            alignment_info=alignment_info
        )

        self.save_text_report(report)

        return report
