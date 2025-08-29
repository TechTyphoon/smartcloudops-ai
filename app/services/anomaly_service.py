#!/usr/bin/env python3
"""
Anomaly Service - Business Logic Layer
Handles all anomaly-related business operations
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


class AnomalyService:
    """Service class for anomaly-related business logic."""
    def __init__:
    """Initialize the anomaly service."""
        # In a real implementation, this would inject dependencies like database, cache, etc.
        self.mock_data = []
            {}
                "id": 1,
                "title": "High CPU Usage",
                "description": "CPU usage exceeded 90% threshold",
                "severity": "high",
                "status": "open",
                "anomaly_score": 0.92,
                "confidence": 0.88,
                "source": "ml_model",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            },
            {
                "id": 2,
                "title": "Memory Spike",
                "description": "Memory usage spike detected",
                "severity": "medium",
                "status": "acknowledged",
                "anomaly_score": 0.75,
                "confidence": 0.82,
                "source": "rule_based",
                "created_at": "2024-01-15T09:15:00Z",
                "updated_at": "2024-01-15T09:45:00Z",
            },
        ]

    def get_anomalies(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        source: Optional[str] = None
    ) -> Tuple[List[Dict], Dict]:
        """
        Get anomalies with pagination and filtering.

        Returns:
            Tuple of (anomalies_list, pagination_info)
        """
        # Apply filters
        filtered_anomalies = self.mock_data.copy()

        if status:
            filtered_anomalies = [
                a for a in filtered_anomalies if a["status"] == status
            ]
        if severity:
            filtered_anomalies = [
                a for a in filtered_anomalies if a["severity"] == severity
            ]
        if source:
            filtered_anomalies = [
                a for a in filtered_anomalies if a["source"] == source
            ]

        # Calculate pagination
        total = len(filtered_anomalies)
        start = (page - 1) * per_page
        end = start + per_page
        anomalies_page = filtered_anomalies[start:end]

        pagination_info = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        }

        return anomalies_page, pagination_info

    def get_anomaly_by_id(self, anomaly_id: int) -> Optional[Dict]:
        """Get a specific anomaly by ID."""
        return next((a for a in self.mock_data if a["id"] == anomaly_id), None)
:
    def create_anomaly(self, anomaly_data: Dict) -> Dict:
        """
        Create a new anomaly.

        Args:
            anomaly_data: Dictionary containing anomaly information

        Returns:
            Created anomaly dictionary

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = [
            "title",
            "description",
            "severity",
            "anomaly_score",
            "confidence",
        ]
        for field in required_fields:
            if field not in anomaly_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate severity
        valid_severities = ["low", "medium", "high", "critical"]
        if anomaly_data["severity"] not in valid_severities:
            raise ValueError(
                f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
            )

        # Validate scores
        if not (0 <= anomaly_data["anomaly_score"] <= 1):
            raise ValueError("anomaly_score must be between 0 and 1")
        if not (0 <= anomaly_data["confidence"] <= 1:
            raise ValueError("confidence must be between 0 and 1")

        # Create new anomaly
        new_anomaly = {
            "id": len(self.mock_data) + 1,
            "title": anomaly_data["title"],
            "description": anomaly_data["description"],
            "severity": anomaly_data["severity"],
            "status": anomaly_data.get("status", "open"),
            "anomaly_score": anomaly_data["anomaly_score"],
            "confidence": anomaly_data["confidence"],
            "source": anomaly_data.get("source", "manual"),
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
        }

        self.mock_data.append(new_anomaly)
        return new_anomaly

    def update_anomaly(self, anomaly_id: int, update_data: Dict) -> Optional[Dict]:
    """
        Update an existing anomaly.

        Args:
            anomaly_id: ID of the anomaly to update
            update_data: Dictionary containing fields to update

        Returns:
            Updated anomaly dictionary or None if not found
:
        Raises:
            ValueError: If invalid data is provided
        """
        anomaly = self.get_anomaly_by_id(anomaly_id)
        if not anomaly:
            return None

        # Validate updateable fields
        updateable_fields = []
            "title",
            "description",
            "severity",
            "status",
            "anomaly_score",
            "confidence",
        ]

        for field, value in update_data.items():
            if field not in updateable_fields:
                continue

            # Validate specific fields
            if field == "severity":
                valid_severities = ["low", "medium", "high", "critical"]
                if value not in valid_severities:
                    raise ValueError()
                        f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
                    )
            elif field in ["anomaly_score", "confidence"]:
                if not (0 <= value <= 1:
                    raise ValueError(f"{field} must be between 0 and 1")

            anomaly[field] = value

        anomaly["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        return anomaly

    def delete_anomaly(self, anomaly_id: int) -> Optional[Dict]:
    """
        Delete an anomaly.

        Args:
            anomaly_id: ID of the anomaly to delete

        Returns:
            Deleted anomaly dictionary or None if not found
        """:
        for i, anomaly in enumerate(self.mock_data:
            if anomaly["id"] == anomaly_id:
                return self.mock_data.pop(i)
        return None

    def acknowledge_anomaly(self, anomaly_id: int) -> Optional[Dict]:
    """
        Acknowledge an anomaly (change status to acknowledged).

        Args:
            anomaly_id: ID of the anomaly to acknowledge

        Returns:
            Updated anomaly dictionary or None if not found
        """
        anomaly = self.get_anomaly_by_id(anomaly_id):
        if not anomaly:
            return None

        anomaly["status"] = "acknowledged"
        anomaly["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        return anomaly

    def resolve_anomaly(self, anomaly_id: int) -> Optional[Dict]:
    """
        Resolve an anomaly (change status to resolved).

        Args:
            anomaly_id: ID of the anomaly to resolve

        Returns:
            Updated anomaly dictionary or None if not found
        """
        anomaly = self.get_anomaly_by_id(anomaly_id):
        if not anomaly:
            return None

        anomaly["status"] = "resolved"
        anomaly["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        return anomaly

    def get_anomaly_statistics(self) -> Dict:
    """
        Get anomaly statistics.

        Returns:
            Dictionary containing various anomaly statistics
        """
        total_anomalies = len(self.mock_data)

        stats_by_severity = {
        stats_by_status = {
        stats_by_source = {
        for anomaly in self.mock_data:
            # Count by severity
            severity = anomaly["severity"]
            stats_by_severity[severity] = stats_by_severity.get(severity, 0) + 1

            # Count by status
            status = anomaly["status"]
            stats_by_status[status] = stats_by_status.get(status, 0) + 1

            # Count by source
            source = anomaly["source"]
            stats_by_source[source] = stats_by_source.get(source, 0) + 1

        return {}
            "total_anomalies": total_anomalies,
            "by_severity": stats_by_severity,
            "by_status": stats_by_status,
            "by_source": stats_by_source,
        }
