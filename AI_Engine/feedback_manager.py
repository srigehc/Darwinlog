"""
feedback_manager.py

Manages user feedback for anomalies:
- Store accepted issues
- Match future anomalies
- Suppress or escalate known issues

Persistence: JSON file (can upgrade to DB later)
"""

import json
import os
from datetime import datetime
from typing import List, Dict


class FeedbackManager:
    def __init__(self, storage_path: str = "accepted_issues.json"):
        self.storage_path = storage_path
        self.issues = self._load()

    # -----------------------------------------------------
    # Storage Handling
    # -----------------------------------------------------
    def _load(self) -> List[Dict]:
        if not os.path.exists(self.storage_path):
            return []

        with open(self.storage_path, "r") as f:
            return json.load(f)

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.issues, f, indent=2)

    # -----------------------------------------------------
    # Signature Generation
    # -----------------------------------------------------
    def generate_signature(self, row) -> Dict:
        """
        Generate a normalized signature for an anomaly
        """

        return {
            "stream": row.get("stream"),
            "issue_type": row.get("issue_type"),
            "pattern": row.get("pattern"),
            # bucket values to allow flexible matching
            "severity_bucket": self._bucketize_severity(row.get("severity")),
            "gap_ratio_bucket": self._bucketize_ratio(row.get("gap_ratio_p95", 1))
        }

    def _bucketize_severity(self, severity: str) -> str:
        return severity  # already categorical

    def _bucketize_ratio(self, value: float) -> str:
        if value < 1.5:
            return "LOW"
        elif value < 3:
            return "MEDIUM"
        else:
            return "HIGH"

    # -----------------------------------------------------
    # Add Accepted Issue
    # -----------------------------------------------------
    def accept_issue(self, row, user: str = "user"):
        """
        Store an accepted issue signature
        """
        signature = self.generate_signature(row)

        entry = {
            "signature": signature,
            "status": "ACCEPTED",
            "created_by": user,
            "created_at": datetime.now().isoformat()
        }

        self.issues.append(entry)
        self._save()

    # -----------------------------------------------------
    # Matching Logic
    # -----------------------------------------------------
    def is_known_issue(self, row) -> Dict:
        """
        Check if current issue matches any accepted issue

        Returns:
            dict with:
                - matched (True/False)
                - status (ACCEPTED / NEW / ESCALATED)
        """

        current_sig = self.generate_signature(row)

        for entry in self.issues:
            saved_sig = entry["signature"]

            if self._match_signature(current_sig, saved_sig):
                # Check if escalation
                if self._is_escalated(row, saved_sig):
                    return {
                        "matched": True,
                        "status": "ESCALATED"
                    }

                return {
                    "matched": True,
                    "status": "ACCEPTED"
                }

        return {
            "matched": False,
            "status": "NEW"
        }

    def _match_signature(self, sig1: Dict, sig2: Dict) -> bool:
        """
        Loose matching logic (pattern-based, not exact)
        """

        return (
            sig1["stream"] == sig2["stream"] and
            sig1["issue_type"] == sig2["issue_type"] and
            sig1["pattern"] == sig2["pattern"]
        )

    # -----------------------------------------------------
    # Escalation Detection
    # -----------------------------------------------------
    def _is_escalated(self, row, saved_sig) -> bool:
        """
        Detect if issue has worsened significantly
        """

        current_bucket = self._bucketize_ratio(row.get("gap_ratio_p95", 1))
        saved_bucket = saved_sig.get("gap_ratio_bucket")

        severity_order = ["LOW", "MEDIUM", "HIGH"]

        return severity_order.index(current_bucket) > severity_order.index(saved_bucket)

    # -----------------------------------------------------
    # Apply Feedback to DataFrame
    # -----------------------------------------------------
    def apply_feedback(self, df):
        """
        Apply feedback classification to all rows

        Adds:
            feedback_status = NEW / ACCEPTED / ESCALATED
        """

        statuses = []

        for _, row in df.iterrows():
            result = self.is_known_issue(row)
            statuses.append(result["status"])

        df = df.copy()
        df["feedback_status"] = statuses

        return df