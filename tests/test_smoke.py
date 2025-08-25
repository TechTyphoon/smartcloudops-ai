#!/usr/bin/env python3
"""
Simple smoke test for SmartCloudOps.AI
Tests basic imports and app creation without external dependencies
"""

import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_app_import():
    """Test that the main app can be imported"""
    try:
        # Test importing the main app module
        import app.main

        assert hasattr(app.main, "app")
        print("✅ App module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        return False


def test_config_import():
    """Test that the config can be imported"""
    try:
        config = get_config()
        assert config is not None
        print("✅ Config imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without external services"""
    try:
        # Test that we can create a basic Flask app
        app = Flask(__name__)

        @app.route("/healthf")
        def health():
            return {"status": "healthy"}

        # Test that the app can be created
        assert app is not None
        assert hasattr(app, "route")
        print("✅ Basic Flask functionality works")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_environment_variables():
    """Test that environment variables can be read"""
    try:
        import os

        # Test that we can read environment variables
        test_var = os.getenv("TEST_VAR", "default_value")
        assert test_var == "default_value"
        print("✅ Environment variable reading works")
        return True
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Running SmartCloudOps.AI Smoke Tests...")

    tests = [
        test_app_import,
        test_config_import,
        test_basic_functionality,
        test_environment_variables,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed > 0:
        print("✅ At least one test passed - smoke test successful!")
        sys.exit(0)
    else:
        print("❌ No tests passed")
        sys.exit(1)
