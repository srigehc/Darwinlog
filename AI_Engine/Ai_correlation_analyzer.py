"""Analyzes event-level correlation between:
MASTER → SBX / DoCom / HL7

Responsibilities:
- Detect missing patterns
- Detect burst loss
- Detect mismatch between systems
- Generate correlation feature signals

This is NOT ML — it feeds ML and interpreter.
"""

import pandas as pd


class CorrelationAnalyzer:

    def __init__(self):
        pass

    # -----------------------------------------------------
    # PREP: Convert counts → presence
    # -----------------------------------------------------
    def _prepare_presence(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()

        df["master_present"] = 1
        df["sbx_present"] = (df["SBX_count"] > 0).astype(int)
        df["docom_present"] = (df["DOCOM_count"] > 0).astype(int)
        df["hl7_present"] = (df["HL7_count"] > 0).astype(int)

        return df

    # -----------------------------------------------------
    # Missing signals
    # -----------------------------------------------------
    def _compute_missing(self, df: pd.DataFrame):

        df["sbx_missing"] = df["master_present"] - df["sbx_present"]
        df["docom_missing"] = df["master_present"] - df["docom_present"]
        df["hl7_missing"] = df["master_present"] - df["hl7_present"]

        return df

    # -----------------------------------------------------
    # Cross-system mismatch
    # -----------------------------------------------------
    def _compute_mismatch(self, df: pd.DataFrame):

        df["sbx_vs_docom"] = abs(df["sbx_present"] - df["docom_present"])
        df["sbx_vs_hl7"] = abs(df["sbx_present"] - df["hl7_present"])

        df["mismatch_score"] = df["sbx_vs_docom"] + df["sbx_vs_hl7"]

        return df

    # -----------------------------------------------------
    # Detect burst loss (consecutive missing)
    # -----------------------------------------------------
    def _max_consecutive(self, series):

        max_len = 0
        current = 0

        for val in series:
            if val == 1:
                current += 1
                max_len = max(max_len, current)
            else:
                current = 0

        return max_len

    # -----------------------------------------------------
    # Pattern analysis per system
    # -----------------------------------------------------
    def _analyze_system(self, df: pd.DataFrame, col_prefix: str):

        missing_col = f"{col_prefix}_missing"

        series = df[missing_col]

        total = len(series)
        missing_total = series.sum()

        if total == 0:
            return {}

        missing_ratio = missing_total / total
        max_burst = self._max_consecutive(series)

        # pattern classification
        if missing_ratio > 0.6:
            pattern = "SEVERE_LOSS"
        elif max_burst > 20:
            pattern = "BURST_LOSS"
        elif missing_ratio > 0.1:
            pattern = "INTERMITTENT_LOSS"
        else:
            pattern = "STABLE"

        return {
            "missing_ratio": missing_ratio,
            "max_burst": max_burst,
            "pattern": pattern
        }

    # -----------------------------------------------------
    # Overall mismatch analysis
    # -----------------------------------------------------
    def _analyze_mismatch(self, df: pd.DataFrame):

        mismatch_total = df["mismatch_score"].sum()
        total = len(df)

        if total == 0:
            return {}

        mismatch_ratio = mismatch_total / total

        if mismatch_ratio > 0.5:
            pattern = "HIGH_MISMATCH"
        elif mismatch_ratio > 0.1:
            pattern = "MODERATE_MISMATCH"
        else:
            pattern = "LOW_MISMATCH"

        return {
            "mismatch_ratio": mismatch_ratio,
            "pattern": pattern
        }

    # -----------------------------------------------------
    # Main correlation analysis
    # -----------------------------------------------------
    def analyze(self, df: pd.DataFrame):

        df = df.copy()

        # Step 1: Presence
        df = self._prepare_presence(df)

        # Step 2: Missing
        df = self._compute_missing(df)

        # Step 3: Mismatch
        df = self._compute_mismatch(df)

        # Step 4: Per-system analysis
        sbx_analysis = self._analyze_system(df, "sbx")
        docom_analysis = self._analyze_system(df, "docom")
        hl7_analysis = self._analyze_system(df, "hl7")

        # Step 5: Cross-system mismatch
        mismatch_analysis = self._analyze_mismatch(df)

        # Step 6: Aggregate features (for AI)
        features = {
            "sbx_missing_ratio": sbx_analysis.get("missing_ratio", 0),
            "docom_missing_ratio": docom_analysis.get("missing_ratio", 0),
            "hl7_missing_ratio": hl7_analysis.get("missing_ratio", 0),

            "sbx_max_burst": sbx_analysis.get("max_burst", 0),
            "docom_max_burst": docom_analysis.get("max_burst", 0),
            "hl7_max_burst": hl7_analysis.get("max_burst", 0),

            "mismatch_ratio": mismatch_analysis.get("mismatch_ratio", 0)
        }

        # Step 7: Structured result
        result = {
            "sbx": sbx_analysis,
            "docom": docom_analysis,
            "hl7": hl7_analysis,
            "mismatch": mismatch_analysis,
            "features": features
        }

        return result