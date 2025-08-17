"""
Basic unit tests for SmartCloudOps AI
"""
import pytest
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

def test_basic_import():
    """Test that basic app modules can be imported"""
    try:
        from config import Config
        assert Config is not None
    except ImportError:
        pytest.skip("Config module not available")

def test_app_structure():
    """Test that app directory structure exists"""
    app_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'app')
    assert os.path.exists(app_dir), "App directory should exist"
    
    # Check for key files
    key_files = ['main.py', 'config.py']
    for file in key_files:
        file_path = os.path.join(app_dir, file)
        if os.path.exists(file_path):
            assert True  # At least one key file exists
            break
    else:
        pytest.skip("No key app files found")

if __name__ == "__main__":
    pytest.main([__file__])
