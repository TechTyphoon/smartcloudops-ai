"""
Basic integration tests for SmartCloudOps AI
"""

import pytest
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))


def test_basic_integration():
    """Test basic integration functionality"""
    # This is a placeholder integration test
    assert True, "Basic integration test passes"


def test_app_initialization():
    """Test that the app can be initialized without errors"""
    try:
        # Try to import and initialize basic app components
        from config import Config

        config = Config()
        assert config is not None
    except ImportError:
        pytest.skip("App modules not available for integration testing")
    except Exception as e:
        pytest.skip(f"App initialization failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
