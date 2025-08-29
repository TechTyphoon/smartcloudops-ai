"""Pytest configuration for backend tests."""

import os
import sys

import pytest
from flask.testing import FlaskClient

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# Set test environment
os.environ["FLASK_ENV"] = "testing"
os.environ["TEST_MODE"] = "1"
os.environ["FLASK_PORT"] = "5000"
os.environ["FLASK_HOST"] = "127.0.0.1"

# Disable external services for testing
os.environ["AI_PROVIDER"] = "local"
os.environ["DISABLE_AWS_SERVICES"] = "true"
os.environ["DISABLE_ELASTICSEARCH"] = "true"
os.environ["USE_LOCAL_STORAGE"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Mock external dependencies
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["REDIS_PASSWORD"] = "test-password"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32-chars-minimum"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-testing-only-32-chars-minimum"


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing."""
    from app.main import create_app

    # Create app for testing
    flask_app = create_app()

    # Configure for testing
    flask_app.config.update(
        {
            "TESTING": True,
            "DEBUG": True,
            "WTF_CSRF_ENABLED": False,
        }
    )

    return flask_app


@pytest.fixture
def client(app) -> FlaskClient:
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test runner."""
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Ensure we're in test mode
    os.environ["TEST_MODE"] = "1"
    os.environ["FLASK_ENV"] = "testing"

    yield

    # Cleanup after test
    pass
