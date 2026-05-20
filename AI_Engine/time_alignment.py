import pandas as pd


class TimeAlignment:
    def __init__(self, min_active_rows=10):
        self.min_active_rows = min_active_rows

    def detect_start_time(self, df):
        active_rows = df[
            (df["SBX_count"] > 0) |
            (df["DOCOM_count"] > 0) |
            (df["HL7_count"] > 0)
        ]

        if active_rows.empty:
            return None, "NO_DATA", 0

        start_time = active_rows["system_time"].min()

        confidence = "LOW"
        if len(active_rows) > self.min_active_rows:
            confidence = "HIGH"

        return start_time, confidence, len(active_rows)

    def apply_alignment(self, df):

        start_time, confidence, count = self.detect_start_time(df)

        if start_time is None:
            return df, {
                "status": "NO_DOWNSTREAM_DATA"
            }

        aligned_df = df[df["system_time"] >= start_time]

        return aligned_df, {
            "start_time": str(start_time),
            "confidence": confidence,
            "active_rows": count
        }