import pandas as pd


class TimeAlignment:
    
    def __init__(self, stable_window=20, warmup_drop=10):
        self.stable_window = stable_window
        self.warmup_drop = warmup_drop
    
    # -----------------------------------------------------
    # Detect stable start (IMPORTANT FIX)
    # -----------------------------------------------------
    def detect_stable_start(self, df):

        df = df.copy()

        df["active"] = (
            (df["SBX_count"] > 0) |
            (df["DOCOM_count"] > 0) |
            (df["HL7_count"] > 0)
        ).astype(int)

        active = df["active"].values

        for i in range(len(active) - self.stable_window):
            if all(active[i:i + self.stable_window]):
                return df.iloc[i]["system_time"], "HIGH"

        # fallback if no stable window
        first_active = df[df["active"] == 1]
        if not first_active.empty:
            return first_active.iloc[0]["system_time"], "LOW"

        return None, "NONE"


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
        df = df.copy()
        start_time, confidence, count = self.detect_start_time(df)

        if start_time is None:
            return df, {
                "status": "NO_DOWNSTREAM_DATA"
            }

        
        # Filter valid window
        aligned_df = df[df["system_time"] >= start_time]

        # Remove warmup noise (VERY IMPORTANT)
        aligned_df = aligned_df.iloc[self.warmup_drop:]


        return aligned_df, {
            "start_time": str(start_time),
            "confidence": confidence,
           #"active_rows": count
           "rows_after_alignment": len(aligned_df)
        }