# SmartCloudOps AI - Testing Suite

This directory contains the comprehensive test suite for SmartCloudOps AI, ensuring code quality, reliability, and security across all components.

## 🧪 Test Structure

```
tests/
├── 📁 unit/                   # Unit tests
│   ├── test_basic.py         # Basic functionality tests
│   └── __init__.py
├── 📁 integration/            # Integration tests
│   ├── test_basic.py         # Integration test basics
│   └── __init__.py
├── 📁 backend/                # Backend API tests
│   ├── test_chatops.py       # ChatOps functionality tests
│   ├── test_health.py        # Health check tests
│   ├── test_status.py        # Status endpoint tests
│   ├── conftest.py           # Test configuration
│   └── __init__.py
├── 📄 test_ai_handler.py     # AI handler tests
├── 📄 test_chatops.py        # ChatOps integration tests
├── 📄 test_config.py         # Configuration tests
├── 📄 test_database_integration.py # Database tests
├── 📄 test_flask_app.py      # Flask application tests
├── 📄 test_gpt_integration.py # GPT integration tests
├── 📄 test_integration.py    # General integration tests
├── 📄 test_ml_anomaly_detection.py # ML anomaly detection tests
├── 📄 test_ml_endpoints.py   # ML API endpoint tests
├── 📄 test_remediation.py    # Remediation engine tests
├── 📄 test_smoke.py          # Smoke tests
└── 📄 __init__.py
```

## 🚀 Quick Start

### Run All Tests
```bash
# Run complete test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Backend API tests only
pytest tests/backend/

# Specific test file
pytest tests/test_ai_handler.py
```

### Run Tests with Options
```bash
# Run tests in parallel
pytest -n auto

# Stop on first failure
pytest -x

# Run tests matching pattern
pytest -k "test_auth"

# Generate coverage report
pytest --cov=app --cov-report=term-missing
```

## 📋 Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions and classes in isolation
- **Scope**: Single module or component
- **Speed**: Fast execution
- **Dependencies**: Mocked external dependencies

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions
- **Scope**: Multiple modules working together
- **Speed**: Medium execution time
- **Dependencies**: Real database, external services

### Backend API Tests (`tests/backend/`)
- **Purpose**: Test REST API endpoints
- **Scope**: Full API functionality
- **Speed**: Slower execution
- **Dependencies**: Running application, database

### Specialized Tests
- **AI Handler Tests**: Test AI/ML functionality
- **ChatOps Tests**: Test ChatOps integration
- **Database Tests**: Test database operations
- **ML Tests**: Test machine learning components
- **Remediation Tests**: Test auto-remediation engine

## 🔧 Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow running tests
    security: Security tests
```

### conftest.py
- Test fixtures and configuration
- Database setup and teardown
- Mock configurations
- Test data generation

## 🧪 Test Examples

### Unit Test Example
```python
import pytest
from app.auth import authenticate_user

def test_authenticate_user_success():
    """Test successful user authentication"""
    result = authenticate_user("admin", "password123")
    assert result is True

def test_authenticate_user_failure():
    """Test failed user authentication"""
    result = authenticate_user("admin", "wrongpassword")
    assert result is False
```

### Integration Test Example
```python
import pytest
from app.main import create_app

@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

### API Test Example
```python
def test_anomaly_detection_api(client):
    """Test anomaly detection API"""
    data = {
        'cpu_usage': 85.5,
        'memory_usage': 78.2,
        'disk_usage': 45.0
    }
    response = client.post('/anomaly', json=data)
    assert response.status_code == 200
    assert 'anomaly_score' in response.json
```

## 📊 Coverage Requirements

### Minimum Coverage Targets
- **Overall Coverage**: 90%+
- **Critical Paths**: 95%+
- **API Endpoints**: 100%
- **Security Functions**: 100%

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=app --cov-report=xml

# View coverage in terminal
pytest --cov=app --cov-report=term-missing
```

## 🔒 Security Testing

### Security Test Categories
- **Input Validation**: Test for injection attacks
- **Authentication**: Test auth bypass attempts
- **Authorization**: Test permission checks
- **Data Protection**: Test data leakage
- **Rate Limiting**: Test abuse prevention

### Security Test Example
```python
def test_sql_injection_prevention(client):
    """Test SQL injection prevention"""
    malicious_input = "'; DROP TABLE users; --"
    response = client.post('/auth/login', json={
        'username': malicious_input,
        'password': 'password'
    })
    assert response.status_code == 400
```

## 🚀 CI/CD Integration

### GitHub Actions
```yaml
- name: Run Tests
  run: |
    pytest --cov=app --cov-report=xml
    pytest --cov=app --cov-report=html
```

### Pre-commit Hooks
```yaml
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: pytest
      language: system
      pass_filenames: false
```

## 🔍 Debugging Tests

### Common Issues

1. **Test Database Issues**
   ```bash
   # Reset test database
   pytest --reuse-db
   ```

2. **Import Errors**
   ```bash
   # Add project root to PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   pytest
   ```

3. **Slow Tests**
   ```bash
   # Run only fast tests
   pytest -m "not slow"
   ```

### Debug Mode
```bash
# Run with debug output
pytest -s -v

# Run specific test with debug
pytest -s -v tests/test_specific.py::test_function
```

## 📈 Performance Testing

### Load Testing
```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py
```

### Benchmark Tests
```python
import pytest
import time

def test_api_response_time(client):
    """Test API response time"""
    start_time = time.time()
    response = client.get('/health')
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 0.1  # 100ms threshold
```

## 📚 Best Practices

### Test Organization
- **Descriptive Names**: Use clear, descriptive test names
- **Single Responsibility**: Each test should test one thing
- **Arrange-Act-Assert**: Follow AAA pattern
- **Independent Tests**: Tests should not depend on each other

### Test Data
- **Fixtures**: Use pytest fixtures for test data
- **Factories**: Use factory patterns for complex objects
- **Cleanup**: Always clean up test data
- **Isolation**: Tests should not affect each other

### Mocking
- **External Services**: Mock external API calls
- **Database**: Use test database or mocks
- **Time**: Mock time-dependent functions
- **Random**: Mock random number generation

## 🤝 Contributing

### Adding New Tests
1. **Follow Naming Convention**: `test_*.py` for test files
2. **Use Appropriate Category**: Place in correct directory
3. **Write Descriptive Names**: Clear test function names
4. **Add Documentation**: Document test purpose
5. **Ensure Coverage**: Maintain coverage requirements

### Test Review Checklist
- [ ] Tests are descriptive and well-documented
- [ ] Tests cover edge cases and error conditions
- [ ] Tests are independent and can run in any order
- [ ] Tests use appropriate mocking and fixtures
- [ ] Tests maintain coverage requirements

---

**SmartCloudOps AI v3.3.0** - Comprehensive Testing Suite
