"""
Unit tests for ChatOps Utilities
Comprehensive test coverage for utility functions and context management
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, Any, List

from app.chatops.utils import timed_cache, AdvancedContextManager


class TestTimedCache:
    """Test suite for timed_cache decorator."""

    def test_timed_cache_basic_functionality(self):
        """Test basic timed cache functionality."""
        call_count = 0

        @timed_cache(seconds=1)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call should execute the function
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Second call within cache window should use cached result
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Should not increment

    def test_timed_cache_different_arguments(self):
        """Test that different arguments create different cache entries."""
        call_count = 0

        @timed_cache(seconds=1)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # Different arguments should create separate cache entries
        result1 = expensive_function(1, 2)
        result2 = expensive_function(2, 3)
        result3 = expensive_function(1, 2)  # Should use cache

        assert result1 == 3
        assert result2 == 5
        assert result3 == 3
        assert call_count == 2  # Only 2 actual function calls

    def test_timed_cache_expiration(self):
        """Test that cache entries expire after the specified time."""
        call_count = 0

        @timed_cache(seconds=0.1)  # Very short cache duration
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call within cache window
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1

        # Wait for cache to expire
        time.sleep(0.2)

        # Third call after expiration
        result3 = expensive_function(5)
        assert result3 == 10
        assert call_count == 2  # Should increment again

    def test_timed_cache_keyword_arguments(self):
        """Test cache behavior with keyword arguments."""
        call_count = 0

        @timed_cache(seconds=1)
        def expensive_function(x, y=0, z=0):
            nonlocal call_count
            call_count += 1
            return x + y + z

        # Test with different keyword argument combinations
        result1 = expensive_function(1, y=2, z=3)
        result2 = expensive_function(1, z=3, y=2)  # Same arguments, different order
        result3 = expensive_function(1, y=2)  # Different arguments

        assert result1 == 6
        assert result2 == 6
        assert result3 == 3
        assert call_count == 2  # Should cache same arguments regardless of order

    def test_timed_cache_clear(self):
        """Test cache clearing functionality."""
        call_count = 0

        @timed_cache(seconds=1)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = expensive_function(5)
        assert call_count == 1

        # Second call should use cache
        result2 = expensive_function(5)
        assert call_count == 1

        # Clear cache
        expensive_function.cache_clear()

        # Third call should execute function again
        result3 = expensive_function(5)
        assert call_count == 2

    def test_timed_cache_info(self):
        """Test cache information retrieval."""
        @timed_cache(seconds=1)
        def expensive_function(x):
            return x * 2

        # Call function to populate cache
        expensive_function(5)
        expensive_function(10)

        # Get cache info
        info = expensive_function.cache_info()
        
        assert "size" in info
        assert info["size"] == 2

    def test_timed_cache_cleanup(self):
        """Test automatic cache cleanup for large caches."""
        call_count = 0

        @timed_cache(seconds=1)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Add many cache entries to trigger cleanup
        for i in range(150):  # More than the cleanup threshold
            expensive_function(i)

        # Verify cleanup occurred
        info = expensive_function.cache_info()
        assert info["size"] <= 100  # Should be cleaned up


class TestAdvancedContextManager:
    """Test suite for AdvancedContextManager class."""

    @pytest.fixture
    def context_manager(self):
        """Create AdvancedContextManager instance for testing."""
        return AdvancedContextManager(max_context_size=50, cache_duration=300)

    @pytest.fixture
    def mock_system_data(self) -> Dict[str, Any]:
        """Mock system data for testing."""
        return {
            "system_health": "healthy",
            "recent_anomalies": [],
            "resource_usage": {"cpu": 45, "memory": 60},
            "active_alerts": [],
            "remediation_status": "idle",
            "ml_model_status": "operational"
        }

    def test_init_default_values(self):
        """Test AdvancedContextManager initialization with default values."""
        manager = AdvancedContextManager()
        
        assert manager.max_context_size == 100
        assert manager.cache_duration == 300
        assert isinstance(manager.context_cache, dict)
        assert isinstance(manager.system_state_history, deque)
        assert manager.system_state_history.maxlen == 50

    def test_init_custom_values(self):
        """Test AdvancedContextManager initialization with custom values."""
        manager = AdvancedContextManager(max_context_size=200, cache_duration=600)
        
        assert manager.max_context_size == 200
        assert manager.cache_duration == 600
        assert manager.system_state_history.maxlen == 50

    @patch('app.chatops.utils.datetime')
    def test_get_system_context_success(self, mock_datetime, context_manager, mock_system_data):
        """Test successful system context retrieval."""
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Mock the private methods
        with patch.object(context_manager, '_get_system_health', return_value=mock_system_data["system_health"]), \
             patch.object(context_manager, '_get_recent_anomalies', return_value=mock_system_data["recent_anomalies"]), \
             patch.object(context_manager, '_get_resource_usage', return_value=mock_system_data["resource_usage"]), \
             patch.object(context_manager, '_get_active_alerts', return_value=mock_system_data["active_alerts"]), \
             patch.object(context_manager, '_get_remediation_status', return_value=mock_system_data["remediation_status"]), \
             patch.object(context_manager, '_get_ml_model_status', return_value=mock_system_data["ml_model_status"]):

            context = context_manager.get_system_context()

            assert context["timestamp"] == mock_now.isoformat()
            assert context["system_health"] == mock_system_data["system_health"]
            assert context["recent_anomalies"] == mock_system_data["recent_anomalies"]
            assert context["resource_usage"] == mock_system_data["resource_usage"]
            assert context["active_alerts"] == mock_system_data["active_alerts"]
            assert context["remediation_status"] == mock_system_data["remediation_status"]
            assert context["ml_model_status"] == mock_system_data["ml_model_status"]

            # Verify cache was updated
            assert "system_context" in context_manager.context_cache
            assert context_manager.last_context_update == mock_now

    @patch('app.chatops.utils.datetime')
    def test_get_system_context_exception_handling(self, mock_datetime, context_manager):
        """Test system context retrieval with exception handling."""
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Mock a method to raise an exception
        with patch.object(context_manager, '_get_system_health', side_effect=Exception("System error")):
            context = context_manager.get_system_context()

            # Should return cached context or empty context
            assert isinstance(context, dict)
            assert "timestamp" in context

    def test_get_system_context_caching(self, context_manager, mock_system_data):
        """Test that system context is properly cached."""
        # Mock the private methods
        with patch.object(context_manager, '_get_system_health', return_value=mock_system_data["system_health"]), \
             patch.object(context_manager, '_get_recent_anomalies', return_value=mock_system_data["recent_anomalies"]), \
             patch.object(context_manager, '_get_resource_usage', return_value=mock_system_data["resource_usage"]), \
             patch.object(context_manager, '_get_active_alerts', return_value=mock_system_data["active_alerts"]), \
             patch.object(context_manager, '_get_remediation_status', return_value=mock_system_data["remediation_status"]), \
             patch.object(context_manager, '_get_ml_model_status', return_value=mock_system_data["ml_model_status"]):

            # First call should populate cache
            context1 = context_manager.get_system_context()
            
            # Second call should use cache (methods shouldn't be called again)
            context2 = context_manager.get_system_context()

            assert context1 == context2
            assert "system_context" in context_manager.context_cache

    def test_get_system_context_history_management(self, context_manager, mock_system_data):
        """Test that system context history is properly managed."""
        # Mock the private methods
        with patch.object(context_manager, '_get_system_health', return_value=mock_system_data["system_health"]), \
             patch.object(context_manager, '_get_recent_anomalies', return_value=mock_system_data["recent_anomalies"]), \
             patch.object(context_manager, '_get_resource_usage', return_value=mock_system_data["resource_usage"]), \
             patch.object(context_manager, '_get_active_alerts', return_value=mock_system_data["active_alerts"]), \
             patch.object(context_manager, '_get_remediation_status', return_value=mock_system_data["remediation_status"]), \
             patch.object(context_manager, '_get_ml_model_status', return_value=mock_system_data["ml_model_status"]):

            # Add multiple context entries
            for i in range(60):  # More than maxlen
                context_manager.get_system_context()

            # History should be limited to maxlen
            assert len(context_manager.system_state_history) <= 50

    def test_get_system_context_structure(self, context_manager, mock_system_data):
        """Test that system context has the correct structure."""
        # Mock the private methods
        with patch.object(context_manager, '_get_system_health', return_value=mock_system_data["system_health"]), \
             patch.object(context_manager, '_get_recent_anomalies', return_value=mock_system_data["recent_anomalies"]), \
             patch.object(context_manager, '_get_resource_usage', return_value=mock_system_data["resource_usage"]), \
             patch.object(context_manager, '_get_active_alerts', return_value=mock_system_data["active_alerts"]), \
             patch.object(context_manager, '_get_remediation_status', return_value=mock_system_data["remediation_status"]), \
             patch.object(context_manager, '_get_ml_model_status', return_value=mock_system_data["ml_model_status"]):

            context = context_manager.get_system_context()

            # Check required fields
            required_fields = [
                "timestamp", "system_health", "recent_anomalies", 
                "resource_usage", "active_alerts", "remediation_status", 
                "ml_model_status"
            ]
            
            for field in required_fields:
                assert field in context

    def test_context_manager_state_persistence(self, context_manager):
        """Test that context manager state persists between calls."""
        # Verify initial state
        assert context_manager.context_cache == {}
        assert len(context_manager.system_state_history) == 0

        # Add some context
        context_manager.context_cache["test"] = "value"
        context_manager.system_state_history.append({"test": "entry"})

        # Verify state persists
        assert context_manager.context_cache["test"] == "value"
        assert len(context_manager.system_state_history) == 1

    def test_context_manager_max_context_size(self):
        """Test that context manager respects max_context_size parameter."""
        manager = AdvancedContextManager(max_context_size=10)
        
        # Add more entries than max_context_size
        for i in range(15):
            manager.context_cache[f"key_{i}"] = f"value_{i}"

        # Should not exceed max_context_size
        assert len(manager.context_cache) <= 10

    @patch('app.chatops.utils.datetime')
    def test_context_manager_timestamp_format(self, mock_datetime, context_manager, mock_system_data):
        """Test that timestamps are properly formatted."""
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Mock the private methods
        with patch.object(context_manager, '_get_system_health', return_value=mock_system_data["system_health"]), \
             patch.object(context_manager, '_get_recent_anomalies', return_value=mock_system_data["recent_anomalies"]), \
             patch.object(context_manager, '_get_resource_usage', return_value=mock_system_data["resource_usage"]), \
             patch.object(context_manager, '_get_active_alerts', return_value=mock_system_data["active_alerts"]), \
             patch.object(context_manager, '_get_remediation_status', return_value=mock_system_data["remediation_status"]), \
             patch.object(context_manager, '_get_ml_model_status', return_value=mock_system_data["ml_model_status"]):

            context = context_manager.get_system_context()

            # Timestamp should be ISO format
            assert context["timestamp"] == "2023-01-01T12:00:00"

    def test_context_manager_empty_context_handling(self, context_manager):
        """Test handling of empty or None context data."""
        # Mock methods to return empty/None values
        with patch.object(context_manager, '_get_system_health', return_value=None), \
             patch.object(context_manager, '_get_recent_anomalies', return_value=[]), \
             patch.object(context_manager, '_get_resource_usage', return_value={}), \
             patch.object(context_manager, '_get_active_alerts', return_value=None), \
             patch.object(context_manager, '_get_remediation_status', return_value=""), \
             patch.object(context_manager, '_get_ml_model_status', return_value=None):

            context = context_manager.get_system_context()

            # Should handle None/empty values gracefully
            assert isinstance(context, dict)
            assert "timestamp" in context
            assert context["system_health"] is None
            assert context["recent_anomalies"] == []
            assert context["resource_usage"] == {}
            assert context["active_alerts"] is None
            assert context["remediation_status"] == ""
            assert context["ml_model_status"] is None
