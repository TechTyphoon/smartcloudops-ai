#!/usr/bin/env python3
"""
Unit tests for AnomalyService
Tests business logic layer for anomaly operations
"""

import os

# Import the service we're testing
import sys
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.anomaly_service import AnomalyService


class TestAnomalyService:
    """Test suite for AnomalyService business logic."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = AnomalyService()

    def test_service_initialization(self):
        """Test that AnomalyService initializes correctly."""
        assert self.service is not None
        assert len(self.service.mock_data) == 2  # Default mock data
        assert all(isinstance(anomaly, dict) for anomaly in self.service.mock_data)

    def test_get_anomalies_default_pagination(self):
        """Test getting anomalies with default pagination."""
        anomalies, pagination = self.service.get_anomalies()

        assert isinstance(anomalies, list)
        assert isinstance(pagination, dict)
        assert len(anomalies) == 2  # All mock data fits in one page
        assert pagination["page"] == 1
        assert pagination["per_page"] == 20
        assert pagination["total"] == 2
        assert pagination["pages"] == 1

    def test_get_anomalies_custom_pagination(self):
        """Test getting anomalies with custom pagination."""
        anomalies, pagination = self.service.get_anomalies(page=1, per_page=1)

        assert len(anomalies) == 1  # Only one per page
        assert pagination["page"] == 1
        assert pagination["per_page"] == 1
        assert pagination["total"] == 2
        assert pagination["pages"] == 2

    def test_get_anomalies_status_filter(self):
        """Test filtering anomalies by status."""
        anomalies, pagination = self.service.get_anomalies(status="open")

        assert len(anomalies) == 1
        assert all(anomaly["status"] == "open" for anomaly in anomalies)

    def test_get_anomalies_severity_filter(self):
        """Test filtering anomalies by severity."""
        anomalies, pagination = self.service.get_anomalies(severity="high")

        assert len(anomalies) == 1
        assert all(anomaly["severity"] == "high" for anomaly in anomalies)

    def test_get_anomalies_source_filter(self):
        """Test filtering anomalies by source."""
        anomalies, pagination = self.service.get_anomalies(source="ml_model")

        assert len(anomalies) == 1
        assert all(anomaly["source"] == "ml_model" for anomaly in anomalies)

    def test_get_anomalies_multiple_filters(self):
        """Test filtering anomalies with multiple filters."""
        anomalies, pagination = self.service.get_anomalies(
            status="acknowledged", severity="medium"
        )

        assert len(anomalies) == 1
        assert anomalies[0]["status"] == "acknowledged"
        assert anomalies[0]["severity"] == "medium"

    def test_get_anomaly_by_id_existing(self):
        """Test getting an existing anomaly by ID."""
        anomaly = self.service.get_anomaly_by_id(1)

        assert anomaly is not None
        assert anomaly["id"] == 1
        assert "title" in anomaly
        assert "description" in anomaly

    def test_get_anomaly_by_id_nonexistent(self):
        """Test getting a non-existent anomaly by ID."""
        anomaly = self.service.get_anomaly_by_id(999)

        assert anomaly is None

    def test_create_anomaly_valid_data(self):
        """Test creating an anomaly with valid data."""
        anomaly_data = {
            "title": "Test Anomaly",
            "description": "Test description",
            "severity": "medium",
            "anomaly_score": 0.75,
            "confidence": 0.85,
            "source": "test",
        }

        original_count = len(self.service.mock_data)
        new_anomaly = self.service.create_anomaly(anomaly_data)

        assert new_anomaly is not None
        assert new_anomaly["id"] == original_count + 1
        assert new_anomaly["title"] == "Test Anomaly"
        assert new_anomaly["severity"] == "medium"
        assert new_anomaly["status"] == "open"  # Default status
        assert len(self.service.mock_data) == original_count + 1
        assert "created_at" in new_anomaly
        assert "updated_at" in new_anomaly

    def test_create_anomaly_missing_required_field(self):
        """Test creating an anomaly with missing required fields."""
        anomaly_data = {
            "title": "Test Anomaly",
            # Missing description, severity, anomaly_score, confidence
        }

        with pytest.raises(ValueError, match="Missing required field: description"):
            self.service.create_anomaly(anomaly_data)

    def test_create_anomaly_invalid_severity(self):
        """Test creating an anomaly with invalid severity."""
        anomaly_data = {
            "title": "Test Anomaly",
            "description": "Test description",
            "severity": "invalid",
            "anomaly_score": 0.75,
            "confidence": 0.85,
        }

        with pytest.raises(ValueError, match="Invalid severity"):
            self.service.create_anomaly(anomaly_data)

    def test_create_anomaly_invalid_anomaly_score(self):
        """Test creating an anomaly with invalid anomaly score."""
        anomaly_data = {
            "title": "Test Anomaly",
            "description": "Test description",
            "severity": "medium",
            "anomaly_score": 1.5,  # Invalid: > 1
            "confidence": 0.85,
        }

        with pytest.raises(ValueError, match="anomaly_score must be between 0 and 1"):
            self.service.create_anomaly(anomaly_data)

    def test_create_anomaly_invalid_confidence(self):
        """Test creating an anomaly with invalid confidence."""
        anomaly_data = {
            "title": "Test Anomaly",
            "description": "Test description",
            "severity": "medium",
            "anomaly_score": 0.75,
            "confidence": -0.1,  # Invalid: < 0
        }

        with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
            self.service.create_anomaly(anomaly_data)

    def test_update_anomaly_existing(self):
        """Test updating an existing anomaly."""
        update_data = {"title": "Updated Title", "severity": "critical"}

        updated_anomaly = self.service.update_anomaly(1, update_data)

        assert updated_anomaly is not None
        assert updated_anomaly["id"] == 1
        assert updated_anomaly["title"] == "Updated Title"
        assert updated_anomaly["severity"] == "critical"
        assert "updated_at" in updated_anomaly

    def test_update_anomaly_nonexistent(self):
        """Test updating a non-existent anomaly."""
        update_data = {"title": "Updated Title"}

        updated_anomaly = self.service.update_anomaly(999, update_data)

        assert updated_anomaly is None

    def test_update_anomaly_invalid_severity(self):
        """Test updating an anomaly with invalid severity."""
        update_data = {"severity": "invalid"}

        with pytest.raises(ValueError, match="Invalid severity"):
            self.service.update_anomaly(1, update_data)

    def test_delete_anomaly_existing(self):
        """Test deleting an existing anomaly."""
        original_count = len(self.service.mock_data)
        deleted_anomaly = self.service.delete_anomaly(1)

        assert deleted_anomaly is not None
        assert deleted_anomaly["id"] == 1
        assert len(self.service.mock_data) == original_count - 1

        # Verify anomaly is actually deleted
        assert self.service.get_anomaly_by_id(1) is None

    def test_delete_anomaly_nonexistent(self):
        """Test deleting a non-existent anomaly."""
        original_count = len(self.service.mock_data)
        deleted_anomaly = self.service.delete_anomaly(999)

        assert deleted_anomaly is None
        assert len(self.service.mock_data) == original_count

    def test_acknowledge_anomaly_existing(self):
        """Test acknowledging an existing anomaly."""
        acknowledged_anomaly = self.service.acknowledge_anomaly(1)

        assert acknowledged_anomaly is not None
        assert acknowledged_anomaly["id"] == 1
        assert acknowledged_anomaly["status"] == "acknowledged"
        assert "updated_at" in acknowledged_anomaly

    def test_acknowledge_anomaly_nonexistent(self):
        """Test acknowledging a non-existent anomaly."""
        acknowledged_anomaly = self.service.acknowledge_anomaly(999)

        assert acknowledged_anomaly is None

    def test_resolve_anomaly_existing(self):
        """Test resolving an existing anomaly."""
        resolved_anomaly = self.service.resolve_anomaly(1)

        assert resolved_anomaly is not None
        assert resolved_anomaly["id"] == 1
        assert resolved_anomaly["status"] == "resolved"
        assert "updated_at" in resolved_anomaly

    def test_resolve_anomaly_nonexistent(self):
        """Test resolving a non-existent anomaly."""
        resolved_anomaly = self.service.resolve_anomaly(999)

        assert resolved_anomaly is None

    def test_get_anomaly_statistics(self):
        """Test getting anomaly statistics."""
        stats = self.service.get_anomaly_statistics()

        assert isinstance(stats, dict)
        assert "total_anomalies" in stats
        assert "by_severity" in stats
        assert "by_status" in stats
        assert "by_source" in stats

        assert stats["total_anomalies"] == 2
        assert isinstance(stats["by_severity"], dict)
        assert isinstance(stats["by_status"], dict)
        assert isinstance(stats["by_source"], dict)

    @patch("app.services.anomaly_service.datetime")
    def test_create_anomaly_timestamps(self, mock_datetime):
        """Test that anomaly creation sets proper timestamps."""
        # Mock datetime.now() to return a fixed time
        fixed_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time

        anomaly_data = {
            "title": "Test Anomaly",
            "description": "Test description",
            "severity": "medium",
            "anomaly_score": 0.75,
            "confidence": 0.85,
        }

        new_anomaly = self.service.create_anomaly(anomaly_data)

        expected_timestamp = "2024-01-15T12:00:00+00:00Z"
        assert new_anomaly["created_at"] == expected_timestamp
        assert new_anomaly["updated_at"] == expected_timestamp


@pytest.mark.unit
class TestAnomalyServiceEdgeCases:
    """Test edge cases and error conditions for AnomalyService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = AnomalyService()

    def test_pagination_edge_cases(self):
        """Test pagination edge cases."""
        # Test page beyond available data
        anomalies, pagination = self.service.get_anomalies(page=10, per_page=20)
        assert len(anomalies) == 0
        assert pagination["page"] == 10
        assert pagination["total"] == 2

    def test_filter_no_matches(self):
        """Test filtering that returns no matches."""
        anomalies, pagination = self.service.get_anomalies(status="nonexistent")
        assert len(anomalies) == 0
        assert pagination["total"] == 0

    def test_update_anomaly_no_changes(self):
        """Test updating an anomaly with no actual changes."""
        original_anomaly = self.service.get_anomaly_by_id(1)
        updated_anomaly = self.service.update_anomaly(1, {})

        assert updated_anomaly is not None
        assert updated_anomaly["title"] == original_anomaly["title"]
        # updated_at should still be updated
        assert "updated_at" in updated_anomaly

    def test_create_anomaly_with_optional_fields(self):
        """Test creating an anomaly with optional fields."""
        anomaly_data = {
            "title": "Test Anomaly",
            "description": "Test description",
            "severity": "medium",
            "anomaly_score": 0.75,
            "confidence": 0.85,
            "status": "acknowledged",  # Optional
            "source": "custom_source",  # Optional
        }

        new_anomaly = self.service.create_anomaly(anomaly_data)

        assert new_anomaly["status"] == "acknowledged"
        assert new_anomaly["source"] == "custom_source"
