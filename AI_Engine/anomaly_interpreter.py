"""
anomaly_interpreter.py

Converts AI anomaly output into domain-specific insights.

Responsibilities:
- Map anomaly scores to severity
- Identify behavioral patterns
- Generate structured interpretation

NO model training here.
"""

import pandas as pd


class AnomalyInterpreter:
    def __init__(
        self,
        anomaly_threshold: float = 0.0
    ):
        """
        Args:
            anomaly_threshold:
                decision_function threshold (<= = anomaly)
        """
        self.anomaly_threshold = anomaly_threshold

    # -----------------------------------------------------
    # Severity Mapping
    # -----------------------------------------------------
    def classify_severity(self, score: float) -> str:
        """
        Convert anomaly score to severity level.

        More negative → more anomalous
        """
        if score < -0.3:
            return "HIGH"
        elif score < -0.1:
            return "MEDIUM"
        elif score < self.anomaly_threshold:
            return "LOW"
        else:
            return "NORMAL"

    # -----------------------------------------------------
    # Pattern Detection (from features)
    # -----------------------------------------------------
    def detect_pattern(self, row: pd.Series) -> str:
        """
        Identify behavioral pattern using feature signals
        """

        gap_ratio_p95 = row.get("gap_ratio_p95", 0)
        burst_factor = row.get("burst_factor", 1)
        stability = row.get("stability_score", 1)
        missing_ratio = row.get("missing_ratio", 0)

        # --- Missing data patterns ---
        if missing_ratio > 0.3:
            return "BURST_LOSS"
        elif missing_ratio > 0.05:
            return "RANDOM_LOSS"

        # --- Timing patterns ---
        if burst_factor > 5:
            return "SPIKE_DELAY"

        if gap_ratio_p95 > 2 and stability > 0.7:
            return "INTERMITTENT_SPIKES"

        if gap_ratio_p95 > 2 and stability < 0.5:
            return "UNSTABLE_TIMING"

        if gap_ratio_p95 > 1.2:
            return "CONSISTENT_DELAY"

        return "STABLE"

    # -----------------------------------------------------
    # Issue Classification
    # -----------------------------------------------------
    def classify_issue(self, row: pd.Series) -> str:
        """
        Classify issue type
        """

        gap_ratio_avg = row.get("gap_ratio_avg", 1)
        gap_ratio_p95 = row.get("gap_ratio_p95", 1)
        missing_ratio = row.get("missing_ratio", 0)

        if missing_ratio > 0.1:
            return "DATA_LOSS"

        if gap_ratio_avg > 2:
            return "SYSTEMIC_DELAY"

        if gap_ratio_p95 > 2:
            return "LATENCY_SPIKE"

        return "NORMAL_BEHAVIOR"

    # -----------------------------------------------------
    # Insight Generator
    # -----------------------------------------------------
    def generate_insight(self, issue: str, pattern: str) -> str:
        """
        Generate human-readable explanation
        """

        if issue == "DATA_LOSS":
            if pattern == "BURST_LOSS":
                return "Data missing in continuous segments, likely due to pipeline interruption or buffering."
            return "Scattered missing events observed, possibly due to intermittent transmission issues."

        if issue == "SYSTEMIC_DELAY":
            return "Consistent delay across events, indicating system-wide latency or configuration mismatch."

        if issue == "LATENCY_SPIKE":
            if pattern == "SPIKE_DELAY":
                return "Sudden large delays detected, likely due to buffering or batching behavior."
            return "Intermittent latency spikes observed, indicating network jitter or load variation."

        return "Stream behavior appears stable with no significant anomalies."

    # -----------------------------------------------------
    # Main Interpretation Pipeline
    # -----------------------------------------------------
    def interpret(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Interpret anomaly outputs

        Expected columns:
            anomaly_flag
            anomaly_score
            + feature columns

        Returns:
            DataFrame with interpretation results
        """

        df = df.copy()

        results = []

        for idx, row in df.iterrows():
            score = row["anomaly_score"]
            flag = row["anomaly_flag"]

            severity = self.classify_severity(score)
            pattern = self.detect_pattern(row)
            issue = self.classify_issue(row)
            insight = self.generate_insight(issue, pattern)

            results.append({
                "severity": severity,
                "pattern": pattern,
                "issue_type": issue,
                "insight": insight
            })

        interpretation_df = pd.DataFrame(results, index=df.index)

        return interpretation_df