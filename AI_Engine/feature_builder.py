""" Responsible for converting validated log data into ML-ready feature sets.

This module:
- Computes derived metrics
- Normalizes behavioral signals
- Produces clean feature matrices for AI models
NO ML logic here. Just pure feature engineering. """

import pandas as pd


class FeatureBuilder:
    def __init__(self):
        pass

    # -----------------------------------------------------
    # Frequency-Based Feature Engineering
    # -----------------------------------------------------
    def build_frequency_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build frequency-related features from validation output.

        Expected columns:
            avg_gap, p95_gap, max_gap, expected_gap

        Returns:
            DataFrame with engineered features
        """

        df = df.copy()

        # Avoid division by zero
        df["expected_gap"] = df["expected_gap"].replace(0, 1)
        df["avg_gap"] = df["avg_gap"].replace(0, 1)

        # Core ratios
        df["gap_ratio_avg"] = df["avg_gap"] / df["expected_gap"]
        df["gap_ratio_p95"] = df["p95_gap"] / df["expected_gap"]

        # Burst behavior (spikes vs baseline)
        df["burst_factor"] = df["max_gap"] / df["avg_gap"]

        # Spread / variability
        df["spread"] = df["p95_gap"] - df["avg_gap"]

        # Stability indicator (lower = stable)
        df["stability_score"] = df["avg_gap"] / df["p95_gap"]

        # Optional: cap extreme values to avoid model distortion
        df["burst_factor"] = df["burst_factor"].clip(upper=50)
        df["gap_ratio_p95"] = df["gap_ratio_p95"].clip(upper=50)

        return df[[
            "gap_ratio_avg",
            "gap_ratio_p95",
            "burst_factor",
            "spread",
            "stability_score"
        ]]

    # -----------------------------------------------------
    # Missing Data Features (from correlation layer)
    # -----------------------------------------------------
    def build_missing_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build features related to missing events.

        Expected columns:
            expected_events, received_events

        Returns:
            DataFrame with missing data features
        """

        df = df.copy()

        df["expected_events"] = df["expected_events"].replace(0, 1)

        df["coverage_ratio"] = df["received_events"] / df["expected_events"]
        df["missing_ratio"] = 1 - df["coverage_ratio"]

        # Severity buckets (helpful for model patterning)
        df["missing_severity"] = pd.cut(
            df["missing_ratio"],
            bins=[-1, 0.01, 0.1, 0.3, 1],
            labels=[0, 1, 2, 3]
        ).astype(int)

        return df[[
            "coverage_ratio",
            "missing_ratio",
            "missing_severity"
        ]]

    # -----------------------------------------------------
    # Time-Series Gap Features (from waveform JSONL)
    # -----------------------------------------------------
    def build_gap_sequence_features(self, gaps_df: pd.DataFrame) -> pd.DataFrame:
        """
        Build features from raw gap sequences.

        Expected columns:
            gaps (list of intervals per stream)

        Returns:
            DataFrame with sequence-derived features
        """

        rows = []

        for idx, row in gaps_df.iterrows():
            gaps = row["gaps"]

            if not gaps or len(gaps) < 2:
                rows.append({
                    "gap_std": 0,
                    "gap_skew": 0,
                    "gap_outlier_ratio": 0
                })
                continue

            s = pd.Series(gaps)

            mean_gap = s.mean()
            std_gap = s.std()

            # Outliers: gaps significantly larger than average
            outliers = s[s > (mean_gap * 2)]
            outlier_ratio = len(outliers) / len(s)

            rows.append({
                "gap_std": std_gap,
                "gap_skew": s.skew(),
                "gap_outlier_ratio": outlier_ratio
            })

        return pd.DataFrame(rows, index=gaps_df.index)

    # -----------------------------------------------------
    # Combined Feature Builder
    # -----------------------------------------------------
    def build_all_features(
        self,
        freq_df: pd.DataFrame,
        missing_df: pd.DataFrame = None,
        gaps_df: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Combine all feature types into one feature matrix.

        Args:
            freq_df: frequency metrics (required)
            missing_df: missing event stats (optional)
            gaps_df: time-series gap data (optional)

        Returns:
            Combined feature DataFrame
        """

        features = self.build_frequency_features(freq_df)

        if missing_df is not None:
            missing_features = self.build_missing_features(missing_df)
            features = features.join(missing_features, how="left")

        if gaps_df is not None:
            gap_features = self.build_gap_sequence_features(gaps_df)
            features = features.join(gap_features, how="left")

        # Fill NaN (important for ML)
        features = features.fillna(0)

        return features
    
    def build_correlation_features(self, corr_result: dict):
        """
        Convert CorrelationAnalyzer output → feature vector
        """
        features = corr_result["features"]
        return pd.DataFrame([features])

    def merge_features(self, freq_features: pd.DataFrame, corr_features: pd.DataFrame):
        """
        Merge frequency and correlation features
        """
        # repeat correlation features to match frequency rows
        corr_repeated = pd.concat(
            [corr_features] * len(freq_features),
            ignore_index=True
        )

        merged = pd.concat([freq_features.reset_index(drop=True),
                            corr_repeated], axis=1)

        return merged
