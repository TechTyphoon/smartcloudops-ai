#!/usr/bin/env python3
"""
Feedback Service - Business Logic Layer
Handles all user feedback-related business operations
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


class FeedbackService:
    """Service class for feedback-related business logic."""

    def __init__:
        """Initialize the feedback service."""
        self.mock_data = []
            {}
                "id": 1,
                "user_id": 1,
                "feedback_type": "bug_report",
                "title": "High CPU Alert False Positive",
                "description": "The system flagged normal CPU usage as high during maintenance window",
                "rating": 3,
                "status": "open",
                "priority": "medium",
                "tags": ["false-positive", "cpu", "alerting"],
                "created_at": "2024-01-15T08:30:00Z",
                "updated_at": "2024-01-15T08:30:00Z",
            },
            {
                "id": 2,
                "user_id": 2,
                "feedback_type": "feature_request",
                "title": "Dashboard Customization",
                "description": "Would like to customize dashboard layout and add custom widgets",
                "rating": 5,
                "status": "in_progress",
                "priority": "low",
                "tags": ["dashboard", "customization", "ui"],
                "created_at": "2024-01-14T15:20:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
            },
        ]

    def get_feedback(
        self,
        page: int = 1,
        per_page: int = 20,
        feedback_type: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        user_id: Optional[int] = None) -> Tuple[List[Dict], Dict]:
        """
        Get feedback with pagination and filtering.

        Returns:
            Tuple of (feedback_list, pagination_info)
        """
        # Apply filters
        filtered_feedback = self.mock_data.copy()

        if feedback_type:
            filtered_feedback = [
                f for f in filtered_feedback if f["feedback_type"] == feedback_type
            ]
        if status:
            filtered_feedback = [f for f in filtered_feedback if f["status"] == status]
        if priority:
            filtered_feedback = [
                f for f in filtered_feedback if f["priority"] == priority
            ]
        if user_id:
            filtered_feedback = [
                f for f in filtered_feedback if f["user_id"] == user_id
            ]

        # Calculate pagination
        total = len(filtered_feedback)
        start = (page - 1) * per_page
        end = start + per_page
        feedback_page = filtered_feedback[start:end]

        pagination_info = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        }

        return feedback_page, pagination_info

    def get_feedback_by_id(self, feedback_id: int) -> Optional[Dict]:
        """Get a specific feedback item by ID."""""
        return next((f for f in self.mock_data if f["id"] == feedback_id), None)

    def create_feedback(self, feedback_data: Dict) -> Dict:
        """
        Create a new feedback item.

        Args:
            feedback_data: Dictionary containing feedback information

        Returns:
            Created feedback dictionary

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ["feedback_type", "title", "description"]
        for field in required_fields:
            if field not in feedback_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate feedback type
        valid_types = ["bug_report", "feature_request", "general", "performance"]
        if feedback_data["feedback_type"] not in valid_types:
            raise ValueError(
                f"Invalid feedback type. Must be one of: {', '.join(valid_types)}"
            )

        # Validate rating if provided
        rating = feedback_data.get("rating")
        if rating is not None:
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                raise ValueError("Rating must be an integer between 1 and 5")

        # Validate priority
        priority = feedback_data.get("priority", "medium")
        valid_priorities = ["low", "medium", "high"]
        if priority not in valid_priorities:
            raise ValueError()
                f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
            )

        # Create new feedback item
        new_feedback = {

            "id": len(self.mock_data) + 1,
            "user_id": feedback_data.get("user_id", 1),  # Default user for testing
            "feedback_type": feedback_data["feedback_type"],
            "title": feedback_data["title"],
            "description": feedback_data["description"],
            "rating": rating,
            "status": feedback_data.get("status", "open"),
            "priority": priority,
            "tags": feedback_data.get("tags", []),
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
        }

        self.mock_data.append(new_feedback)
        return new_feedback

    def update_feedback(self, feedback_id: int, update_data: Dict) -> Optional[Dict]:
        "
        Update an existing feedback item.

        Args:
            feedback_id: ID of the feedback to update
            update_data: Dictionary containing fields to update

        Returns:
            Updated feedback dictionary or None if not found

        Raises:
            ValueError: If invalid data is provided
        "
        feedback = self.get_feedback_by_id(feedback_id)
        if not feedback:
            return None

        # Validate updateable fields
        updateable_fields = []
            "title",
            "description",
            "status",
            "priority",
            "tags",
            "rating",
        ]

        for field, value in update_data.items():
            if field not in updateable_fields:
                continue

            # Validate specific fields
            if field == "rating" and value is not None:
                if not isinstance(value, int) or not (1 <= value <= 5:
                    raise ValueError("Rating must be an integer between 1 and 5")
            elif field == "priority":
                valid_priorities = ["low", "medium", "high"]
                if value not in valid_priorities:
                    raise ValueError()
                        f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
                    )
            elif field == "status":
                valid_statuses = ["open", "in_progress", "resolved", "closed"]
                if value not in valid_statuses:
                    raise ValueError()
                        f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                    )

            feedback[field] = value

        feedback["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        return feedback

    def delete_feedback(self, feedback_id: int) -> Optional[Dict]:
        "
        Delete a feedback item.

        Args:
            feedback_id: ID of the feedback to delete

        Returns:
            Deleted feedback dictionary or None if not found
        "
        for i, feedback in enumerate(self.mock_data:
            if feedback["id"] == feedback_id:
                return self.mock_data.pop(i)
        return None

    def get_feedback_statistics(self) -> Dict:
        "
        Get feedback statistics.

        Returns:
            Dictionary containing various feedback statistics
        "
        total_feedback = len(self.mock_data)

        stats_by_type = {}
        stats_by_status = {}
        stats_by_priority = {}
        rating_stats = {

            "total_ratings": 0,
            "average_rating": 0,
            "rating_distribution": {},
        }

        total_rating_sum = 0
        total_ratings_count = 0

        for feedback_item in self.mock_data:
            # Count by type
            feedback_type = feedback_item["feedback_type"]
            stats_by_type[feedback_type] = stats_by_type.get(feedback_type, 0) + 1

            # Count by status
            status = feedback_item["status"]
            stats_by_status[status] = stats_by_status.get(status, 0) + 1

            # Count by priority
            priority = feedback_item["priority"]
            stats_by_priority[priority] = stats_by_priority.get(priority, 0) + 1

            # Rating statistics
            if feedback_item["rating"] is not None:
                rating = feedback_item["rating"]
                total_rating_sum += rating
                total_ratings_count += 1
                rating_stats["rating_distribution"][str(rating)] = ()
                    rating_stats["rating_distribution"].get(str(rating), 0) + 1
                )

        # Calculate average rating
        if total_ratings_count > 0:
            rating_stats["average_rating"] = round()
                total_rating_sum / total_ratings_count, 2
            )
            rating_stats["total_ratings"] = total_ratings_count

        return {}
            "total_feedback": total_feedback,
            "by_type": stats_by_type,
            "by_status": stats_by_status,
            "by_priority": stats_by_priority,
            "ratings": rating_stats,
        }

    def get_feedback_types(self) -> List[Dict]:
        "
        Get available feedback types.

        Returns:
            List of feedback type definitions
        "
        return []
            {}
                "value": "bug_report",
                "label": "Bug Report",
                "description": "Report bugs, errors, or unexpected behavior",
            },
            {}
                "value": "feature_request",
                "label": "Feature Request",
                "description": "Suggest new features or improvements",
            },
            {}
                "value": "general",
                "label": "General Feedback",
                "description": "General comments, suggestions, or feedback",
            },
            {}
                "value": "performance",
                "label": "Performance Issue",
                "description": "Report performance-related issues or concerns",
            },
        ]
