#!/usr/bin/env python3
"""
Unit tests for FeedbackService
Tests business logic layer for feedback operations
"""

import os

# Import the service we're testing
import sys
from datetime import datetime
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.feedback_service import FeedbackService


class TestFeedbackService:
    """Test suite for FeedbackService business logic."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = FeedbackService()

    def test_service_initialization(self):
        """Test that FeedbackService initializes correctly."""
        assert self.service is not None
        assert len(self.service.mock_data) == 2  # Default mock data
        assert all(isinstance(feedback, dict) for feedback in self.service.mock_data)

    def test_get_feedback_default_pagination(self):
        """Test getting feedback with default pagination."""
        feedback, pagination = self.service.get_feedback()

        assert isinstance(feedback, list)
        assert isinstance(pagination, dict)
        assert len(feedback) == 2  # All mock data fits in one page
        assert pagination["page"] == 1
        assert pagination["per_page"] == 20
        assert pagination["total"] == 2
        assert pagination["pages"] == 1

    def test_get_feedback_custom_pagination(self):
        """Test getting feedback with custom pagination."""
        feedback, pagination = self.service.get_feedback(page=1, per_page=1)

        assert len(feedback) == 1  # Only one per page
        assert pagination["page"] == 1
        assert pagination["per_page"] == 1
        assert pagination["total"] == 2
        assert pagination["pages"] == 2

    def test_get_feedback_type_filter(self):
        """Test filtering feedback by type."""
        feedback, pagination = self.service.get_feedback(feedback_type="bug_report")

        assert len(feedback) == 1
        assert all(f["feedback_type"] == "bug_report" for f in feedback)

    def test_get_feedback_status_filter(self):
        """Test filtering feedback by status."""
        feedback, pagination = self.service.get_feedback(status="open")

        assert len(feedback) == 1
        assert all(f["status"] == "open" for f in feedback)

    def test_get_feedback_priority_filter(self):
        """Test filtering feedback by priority."""
        feedback, pagination = self.service.get_feedback(priority="medium")

        assert len(feedback) == 1
        assert all(f["priority"] == "medium" for f in feedback)

    def test_get_feedback_user_id_filter(self):
        """Test filtering feedback by user ID."""
        feedback, pagination = self.service.get_feedback(user_id=1)

        assert len(feedback) == 1
        assert all(f["user_id"] == 1 for f in feedback)

    def test_get_feedback_by_id_existing(self):
        """Test getting an existing feedback item by ID."""
        feedback = self.service.get_feedback_by_id(1)

        assert feedback is not None
        assert feedback["id"] == 1
        assert "title" in feedback
        assert "description" in feedback

    def test_get_feedback_by_id_nonexistent(self):
        """Test getting a non-existent feedback item by ID."""
        feedback = self.service.get_feedback_by_id(999)

        assert feedback is None

    def test_create_feedback_valid_data(self):
        """Test creating feedback with valid data."""
        feedback_data = {
            "feedback_type": "feature_request",
            "title": "Test Feature",
            "description": "Test description",
            "rating": 4,
            "priority": "low",
        }

        original_count = len(self.service.mock_data)
        new_feedback = self.service.create_feedback(feedback_data)

        assert new_feedback is not None
        assert new_feedback["id"] == original_count + 1
        assert new_feedback["feedback_type"] == "feature_request"
        assert new_feedback["title"] == "Test Feature"
        assert new_feedback["rating"] == 4
        assert new_feedback["priority"] == "low"
        assert new_feedback["status"] == "open"  # Default status
        assert len(self.service.mock_data) == original_count + 1
        assert "created_at" in new_feedback
        assert "updated_at" in new_feedback

    def test_create_feedback_missing_required_field(self):
        """Test creating feedback with missing required fields."""
        feedback_data = {
            "feedback_type": "bug_report",
            # Missing title and description
        }

        with pytest.raises(ValueError, match="Missing required field: title"):
            self.service.create_feedback(feedback_data)

    def test_create_feedback_invalid_type(self):
        """Test creating feedback with invalid type."""
        feedback_data = {
            "feedback_type": "invalid_type",
            "title": "Test Feedback",
            "description": "Test description",
        }

        with pytest.raises(ValueError, match="Invalid feedback type"):
            self.service.create_feedback(feedback_data)

    def test_create_feedback_invalid_rating(self):
        """Test creating feedback with invalid rating."""
        feedback_data = {
            "feedback_type": "general",
            "title": "Test Feedback",
            "description": "Test description",
            "rating": 6,  # Invalid: > 5
        }

        with pytest.raises(
            ValueError, match="Rating must be an integer between 1 and 5"
        ):
            self.service.create_feedback(feedback_data)

    def test_create_feedback_invalid_priority(self):
        """Test creating feedback with invalid priority."""
        feedback_data = {
            "feedback_type": "general",
            "title": "Test Feedback",
            "description": "Test description",
            "priority": "invalid_priority",
        }

        with pytest.raises(ValueError, match="Invalid priority"):
            self.service.create_feedback(feedback_data)

    def test_create_feedback_no_rating(self):
        """Test creating feedback without rating (should be allowed)."""
        feedback_data = {
            "feedback_type": "general",
            "title": "Test Feedback",
            "description": "Test description",
        }

        new_feedback = self.service.create_feedback(feedback_data)

        assert new_feedback["rating"] is None
        assert new_feedback["priority"] == "medium"  # Default priority

    def test_update_feedback_existing(self):
        """Test updating an existing feedback item."""
        update_data = {"title": "Updated Title", "priority": "high", "rating": 5}

        updated_feedback = self.service.update_feedback(1, update_data)

        assert updated_feedback is not None
        assert updated_feedback["id"] == 1
        assert updated_feedback["title"] == "Updated Title"
        assert updated_feedback["priority"] == "high"
        assert updated_feedback["rating"] == 5
        assert "updated_at" in updated_feedback

    def test_update_feedback_nonexistent(self):
        """Test updating a non-existent feedback item."""
        update_data = {"title": "Updated Title"}

        updated_feedback = self.service.update_feedback(999, update_data)

        assert updated_feedback is None

    def test_update_feedback_invalid_rating(self):
        """Test updating feedback with invalid rating."""
        update_data = {"rating": 0}  # Invalid: < 1

        with pytest.raises(
            ValueError, match="Rating must be an integer between 1 and 5"
        ):
            self.service.update_feedback(1, update_data)

    def test_update_feedback_invalid_priority(self):
        """Test updating feedback with invalid priority."""
        update_data = {"priority": "invalid_priority"}

        with pytest.raises(ValueError, match="Invalid priority"):
            self.service.update_feedback(1, update_data)

    def test_update_feedback_invalid_status(self):
        """Test updating feedback with invalid status."""
        update_data = {"status": "invalid_status"}

        with pytest.raises(ValueError, match="Invalid status"):
            self.service.update_feedback(1, update_data)

    def test_delete_feedback_existing(self):
        """Test deleting an existing feedback item."""
        original_count = len(self.service.mock_data)
        deleted_feedback = self.service.delete_feedback(1)

        assert deleted_feedback is not None
        assert deleted_feedback["id"] == 1
        assert len(self.service.mock_data) == original_count - 1

        # Verify feedback is actually deleted
        assert self.service.get_feedback_by_id(1) is None

    def test_delete_feedback_nonexistent(self):
        """Test deleting a non-existent feedback item."""
        original_count = len(self.service.mock_data)
        deleted_feedback = self.service.delete_feedback(999)

        assert deleted_feedback is None
        assert len(self.service.mock_data) == original_count

    def test_get_feedback_statistics(self):
        """Test getting feedback statistics."""
        stats = self.service.get_feedback_statistics()

        assert isinstance(stats, dict)
        assert "total_feedback" in stats
        assert "by_type" in stats
        assert "by_status" in stats
        assert "by_priority" in stats
        assert "ratings" in stats

        assert stats["total_feedback"] == 2
        assert isinstance(stats["by_type"], dict)
        assert isinstance(stats["by_status"], dict)
        assert isinstance(stats["by_priority"], dict)
        assert isinstance(stats["ratings"], dict)

        # Check rating statistics structure
        assert "total_ratings" in stats["ratings"]
        assert "average_rating" in stats["ratings"]
        assert "rating_distribution" in stats["ratings"]

    def test_get_feedback_types(self):
        """Test getting available feedback types."""
        feedback_types = self.service.get_feedback_types()

        assert isinstance(feedback_types, list)
        assert (
            len(feedback_types) == 4
        )  # bug_report, feature_request, general, performance

        for feedback_type in feedback_types:
            assert isinstance(feedback_type, dict)
            assert "value" in feedback_type
            assert "label" in feedback_type
            assert "description" in feedback_type

        # Check specific types exist
        type_values = [ft["value"] for ft in feedback_types]
        assert "bug_report" in type_values
        assert "feature_request" in type_values
        assert "general" in type_values
        assert "performance" in type_values


@pytest.mark.unit
class TestFeedbackServiceEdgeCases:
    """Test edge cases and error conditions for FeedbackService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = FeedbackService()

    def test_pagination_edge_cases(self):
        """Test pagination edge cases."""
        # Test page beyond available data
        feedback, pagination = self.service.get_feedback(page=10, per_page=20)
        assert len(feedback) == 0
        assert pagination["page"] == 10
        assert pagination["total"] == 2

    def test_filter_no_matches(self):
        """Test filtering that returns no matches."""
        feedback, pagination = self.service.get_feedback(feedback_type="nonexistent")
        assert len(feedback) == 0
        assert pagination["total"] == 0

    def test_multiple_filters_combined(self):
        """Test multiple filters applied together."""
        feedback, pagination = self.service.get_feedback(
            feedback_type="feature_request", status="in_progress", priority="low"
        )

        # Should match feedback with id=2
        assert len(feedback) == 1
        assert feedback[0]["id"] == 2

    def test_rating_statistics_with_mixed_ratings(self):
        """Test rating statistics calculation with various ratings."""
        # Add feedback items with different ratings
        self.service.create_feedback(
            {
                "feedback_type": "general",
                "title": "Test 1",
                "description": "Test description",
                "rating": 1,
            }
        )

        self.service.create_feedback(
            {
                "feedback_type": "general",
                "title": "Test 2",
                "description": "Test description",
                "rating": 5,
            }
        )

        # Create one without rating
        self.service.create_feedback(
            {
                "feedback_type": "general",
                "title": "Test 3",
                "description": "Test description",
                # No rating
            }
        )

        stats = self.service.get_feedback_statistics()

        # Original 2 items: one with rating 3, one with rating 5
        # Added 2 more: one with rating 1, one with rating 5
        # Total ratings: 3, 5, 1, 5 = average 3.5
        assert stats["ratings"]["total_ratings"] == 4
        assert stats["ratings"]["average_rating"] == 3.5

        # Check distribution
        distribution = stats["ratings"]["rating_distribution"]
        assert distribution.get("1", 0) == 1
        assert distribution.get("3", 0) == 1
        assert distribution.get("5", 0) == 2

    def test_rating_statistics_no_ratings(self):
        """Test rating statistics when no feedback has ratings."""
        # Clear data and add feedback without ratings
        self.service.mock_data = [
            {
                "id": 1,
                "feedback_type": "general",
                "title": "Test",
                "description": "Test",
                "rating": None,
                "status": "open",
                "priority": "medium",
                "user_id": 1,
                "tags": [],
            }
        ]

        stats = self.service.get_feedback_statistics()

        assert stats["ratings"]["total_ratings"] == 0
        assert stats["ratings"]["average_rating"] == 0
        assert stats["ratings"]["rating_distribution"] == {}

    def test_update_feedback_no_changes(self):
        """Test updating feedback with no actual changes."""
        original_feedback = self.service.get_feedback_by_id(1)
        updated_feedback = self.service.update_feedback(1, {})

        assert updated_feedback is not None
        assert updated_feedback["title"] == original_feedback["title"]
        # updated_at should still be updated
        assert "updated_at" in updated_feedback

    def test_create_feedback_with_all_optional_fields(self):
        """Test creating feedback with all optional fields."""
        feedback_data = {
            "feedback_type": "performance",
            "title": "Test Performance Issue",
            "description": "Test description",
            "rating": 2,
            "status": "in_progress",
            "priority": "high",
            "tags": ["performance", "slow"],
            "user_id": 42,
        }

        new_feedback = self.service.create_feedback(feedback_data)

        assert new_feedback["rating"] == 2
        assert new_feedback["status"] == "in_progress"
        assert new_feedback["priority"] == "high"
        assert new_feedback["tags"] == ["performance", "slow"]
        assert new_feedback["user_id"] == 42

    def test_update_feedback_rating_to_none(self):
        """Test updating feedback to remove rating."""
        update_data = {"rating": None}

        updated_feedback = self.service.update_feedback(1, update_data)

        assert updated_feedback is not None
        assert updated_feedback["rating"] is None
