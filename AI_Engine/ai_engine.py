"""Pure AI module for anomaly detection using Isolation Forest.

Responsibilities:
- Feature normalization (optional)
- Model training
- Anomaly scoring
No domain logic, no rules, no feedback system. """

from typing import Optional
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AIEngine:
    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        random_state: int = 42,
        use_scaling: bool = True
    ):
        """
        Initialize AI engine.

        Args:
            contamination: Expected fraction of anomalies
            n_estimators: Number of trees
            random_state: Reproducibility
            use_scaling: Whether to standardize features
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.use_scaling = use_scaling

        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

    # -----------------------------------------------------
    # Feature Preparation
    # -----------------------------------------------------
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare feature set for model.

        Assumes input already contains engineered features.

        Args:
            df: DataFrame with numeric features

        Returns:
            Feature matrix
        """
        if self.use_scaling:
            self.scaler = StandardScaler()
            scaled = self.scaler.fit_transform(df)
            return pd.DataFrame(scaled, columns=df.columns, index=df.index)

        return df

    # -----------------------------------------------------
    # Training
    # -----------------------------------------------------
    def fit(self, features: pd.DataFrame):
        """
        Train Isolation Forest model.

        Args:
            features: DataFrame with feature columns
        """
        X = self._prepare_features(features)

        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state
        )

        self.model.fit(X)

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------
    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Predict anomaly labels and scores.

        Args:
            features: DataFrame with feature columns

        Returns:
            DataFrame with:
                - anomaly_flag (-1 anomalous, +1 normal)
                - anomaly_score (higher = more normal)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")

        if self.use_scaling and self.scaler is not None:
            X = pd.DataFrame(
                self.scaler.transform(features),
                columns=features.columns,
                index=features.index
            )
        else:
            X = features

        anomaly_flag = self.model.predict(X)
        anomaly_score = self.model.decision_function(X)

        return pd.DataFrame({
            "anomaly_flag": anomaly_flag,
            "anomaly_score": anomaly_score
        }, index=features.index)

    # -----------------------------------------------------
    # Fit + Predict (Convenience)
    # -----------------------------------------------------
    def fit_predict(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Train and predict in one step.

        Args:
            features: DataFrame with feature columns

        Returns:
            DataFrame with anomaly results
        """
        self.fit(features)
        return self.predict(features)
