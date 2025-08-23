# 🤝 Contributing to SmartCloudOps AI

Thank you for your interest in contributing to SmartCloudOps AI! This document provides guidelines and information for contributors.

---

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Coding Standards](#-coding-standards)
- [Testing Guidelines](#-testing-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Issue Reporting](#-issue-reporting)
- [Code of Conduct](#-code-of-conduct)

---

## 🚀 Getting Started

### Ways to Contribute

We welcome contributions in many forms:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Propose new capabilities
- **📝 Documentation**: Improve guides and tutorials
- **🔧 Code Contributions**: Submit pull requests
- **🧪 Testing**: Help with test coverage and validation
- **🎨 UI/UX**: Improve user experience and interfaces
- **🔒 Security**: Report security vulnerabilities
- **🌐 Localization**: Help with translations

### Before You Start

1. **Check existing issues** to avoid duplicates
2. **Read the documentation** to understand the project
3. **Join discussions** in GitHub Discussions
4. **Set up your development environment**

---

## 🛠️ Development Setup

### Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose**
- **Git**
- **Virtual environment tool** (venv/conda)

### Local Development Environment

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YourUsername/smartcloudops-ai.git
cd smartcloudops-ai

# Add upstream remote
git remote add upstream https://github.com/TechTyphoon/smartcloudops-ai.git
```

#### 2. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv dev_env

# Activate environment
# Linux/macOS:
source dev_env/bin/activate
# Windows:
dev_env\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 3. Set Up Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files (optional)
pre-commit run --all-files
```

#### 4. Database Setup
```bash
# Start required services with Docker
docker-compose up -d postgres redis

# Or start all services for full testing
docker-compose up -d
```

#### 5. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit configuration for development
nano .env

# Key development settings:
FLASK_ENV=development
FLASK_DEBUG=true
LOG_LEVEL=DEBUG
```

### Running the Application

#### Development Mode
```bash
# Run Flask development server
python app/main.py

# Or use Flask CLI
export FLASK_APP=app.main
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

#### Docker Development
```bash
# Build development image
docker build -t smartcloudops-dev .

# Run with development configuration
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f smartcloudops-main
```

---

## 📝 Coding Standards

### Python Style Guide

#### Code Formatting
- **PEP 8** compliance
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/
```

#### Code Style Examples
```python
# ✅ Good
def calculate_anomaly_score(metrics: Dict[str, float]) -> float:
    """Calculate anomaly score from system metrics.
    
    Args:
        metrics: Dictionary containing system metrics
        
    Returns:
        Anomaly score between 0 and 1
    """
    if not metrics:
        raise ValueError("Metrics cannot be empty")
    
    # Calculate weighted average
    weights = {"cpu": 0.4, "memory": 0.3, "disk": 0.3}
    score = sum(metrics.get(key, 0) * weight for key, weight in weights.items())
    
    return min(max(score / 100, 0), 1)

# ❌ Bad
def calc_score(m):
    if m=={}:return 0
    s=m.get('cpu',0)*.4+m.get('mem',0)*.3+m.get('disk',0)*.3
    return s/100
```

#### Type Hints
```python
from typing import Dict, List, Optional, Union
from datetime import datetime

def process_metrics(
    metrics: Dict[str, Union[int, float]],
    threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Process system metrics with optional threshold filtering."""
    pass
```

#### Documentation
```python
class AnomalyDetector:
    """Machine learning model for detecting system anomalies.
    
    This class provides methods for training and using anomaly detection
    models based on system metrics data.
    
    Attributes:
        model: The trained ML model
        version: Model version string
        last_trained: Timestamp of last training
    """
    
    def __init__(self, model_path: str):
        """Initialize the anomaly detector.
        
        Args:
            model_path: Path to the model file
        """
        self.model_path = model_path
        self.model = None
        self.version = "1.0.0"
        self.last_trained = None
```

### File Organization

#### Directory Structure
```
app/
├── __init__.py
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── auth/                  # Authentication module
│   ├── __init__.py
│   ├── routes.py
│   └── models.py
├── api/                   # API endpoints
│   ├── __init__.py
│   ├── anomalies.py
│   ├── remediation.py
│   └── feedback.py
├── ml/                    # Machine learning
│   ├── __init__.py
│   ├── models.py
│   └── training.py
└── utils/                 # Utility functions
    ├── __init__.py
    ├── validators.py
    └── helpers.py
```

#### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

---

## 🧪 Testing Guidelines

### Test Structure

#### Test Organization
```
tests/
├── __init__.py
├── conftest.py            # Pytest configuration
├── unit/                  # Unit tests
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_ml.py
│   └── test_utils.py
├── integration/           # Integration tests
│   ├── __init__.py
│   ├── test_api.py
│   └── test_database.py
└── fixtures/              # Test data
    ├── sample_metrics.json
    └── test_users.json
```

#### Writing Tests
```python
import pytest
from unittest.mock import Mock, patch
from app.ml.models import AnomalyDetector

class TestAnomalyDetector:
    """Test cases for AnomalyDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a test instance of AnomalyDetector."""
        return AnomalyDetector("test_model.pkl")
    
    @pytest.fixture
    def sample_metrics(self):
        """Sample metrics data for testing."""
        return {
            "cpu_usage": 75.5,
            "memory_usage": 68.2,
            "disk_usage": 45.0
        }
    
    def test_initialization(self, detector):
        """Test AnomalyDetector initialization."""
        assert detector.model_path == "test_model.pkl"
        assert detector.model is None
        assert detector.version == "1.0.0"
    
    def test_predict_anomaly(self, detector, sample_metrics):
        """Test anomaly prediction with valid metrics."""
        with patch.object(detector, 'model') as mock_model:
            mock_model.predict.return_value = [0.8]
            
            result = detector.predict(sample_metrics)
            
            assert result['anomaly_score'] == 0.8
            assert result['is_anomaly'] is True
            mock_model.predict.assert_called_once()
    
    def test_predict_invalid_metrics(self, detector):
        """Test prediction with invalid metrics."""
        with pytest.raises(ValueError, match="Invalid metrics"):
            detector.predict({})
    
    @pytest.mark.integration
    def test_end_to_end_prediction(self, detector, sample_metrics):
        """Integration test for complete prediction workflow."""
        # This test requires actual model file
        if not detector.load_model():
            pytest.skip("Model file not available")
        
        result = detector.predict(sample_metrics)
        
        assert 'anomaly_score' in result
        assert 'is_anomaly' in result
        assert 0 <= result['anomaly_score'] <= 1
        assert isinstance(result['is_anomaly'], bool)
```

### Running Tests

#### Test Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py

# Run tests matching pattern
pytest -k "test_predict"

# Run integration tests only
pytest -m integration

# Run tests in parallel
pytest -n auto

# Generate coverage report
pytest --cov=app --cov-report=term-missing
```

#### Test Configuration
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    security: Security tests
```

---

## 🔄 Pull Request Process

### Creating a Pull Request

#### 1. Create Feature Branch
```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/your-bug-description
```

#### 2. Make Your Changes
```bash
# Make your changes
# Write tests for new functionality
# Update documentation

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add anomaly detection threshold configuration

- Add configurable threshold for anomaly detection
- Update ML model to use dynamic thresholds
- Add tests for threshold validation
- Update API documentation

Closes #123"
```

#### 3. Push and Create PR
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Use the PR template and fill in all sections
```

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] **Code follows** project style guidelines
- [ ] **Self-review** performed on the code
- [ ] **Comments added** to complex logic
- [ ] **Documentation updated** for new features
- [ ] **Tests added** for new functionality
- [ ] **All tests pass** locally
- [ ] **Security audit passes**
- [ ] **No breaking changes** or clearly documented
- [ ] **Commit messages** follow conventional format
- [ ] **PR description** is clear and complete

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples
```bash
feat(auth): add JWT token refresh endpoint

fix(ml): resolve memory leak in anomaly detection

docs(api): update authentication examples

test(integration): add database connection tests

refactor(utils): simplify metric calculation logic
```

---

## 🐛 Issue Reporting

### Creating Issues

#### Bug Reports
When reporting bugs, please include:

1. **Clear title** describing the issue
2. **Environment details**:
   - OS and version
   - Python version
   - Docker version
   - SmartCloudOps AI version
3. **Steps to reproduce**:
   - Detailed step-by-step instructions
   - Sample code if applicable
4. **Expected behavior**
5. **Actual behavior**
6. **Error messages and logs**
7. **Screenshots** if relevant

#### Feature Requests
For feature requests, include:

1. **Clear title** describing the feature
2. **Detailed description** of the functionality
3. **Use cases** and examples
4. **Acceptance criteria**
5. **Potential implementation** approach
6. **Impact** on existing functionality

### Issue Templates

#### Bug Report Template
```markdown
## Bug Description
Brief description of the bug

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- Docker Version: [e.g., 20.10.12]
- SmartCloudOps AI Version: [e.g., 3.3.0]

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Error Messages
```
Error details here
```

## Additional Context
Any other context about the problem
```

#### Feature Request Template
```markdown
## Feature Description
Brief description of the feature

## Problem Statement
What problem does this feature solve?

## Proposed Solution
How should this feature work?

## Use Cases
- Use case 1
- Use case 2
- Use case 3

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context
Any other context about the feature request
```

---

## 📋 Code of Conduct

### Our Standards

We are committed to providing a welcoming and inspiring community for all. We expect all contributors to:

- **Be respectful** and inclusive
- **Use welcoming and inclusive language**
- **Be collaborative** and open to feedback
- **Focus on what is best for the community**
- **Show empathy** towards other community members

### Unacceptable Behavior

The following behaviors are considered harassment and are unacceptable:

- **Violence and threats** of violence
- **Inappropriate or unwanted** sexual attention or advances
- **Trolling, insulting/derogatory comments**, and personal or political attacks
- **Public or private harassment**
- **Publishing others' private information** without explicit permission
- **Other conduct** which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at conduct@smartcloudops.ai. All complaints will be reviewed and investigated promptly and fairly.

---

## 🏆 Recognition

### Contributor Recognition

Contributors who make significant improvements will be:

- **Listed in CONTRIBUTORS.md**
- **Mentioned in release notes**
- **Given appropriate GitHub repository permissions**
- **Invited to maintainer team** (for major contributors)

### Contribution Levels

- **🥉 Bronze**: 1-5 contributions
- **🥈 Silver**: 6-20 contributions  
- **🥇 Gold**: 21+ contributions
- **💎 Diamond**: Core maintainer

---

## 📞 Getting Help

### Communication Channels

- **💬 GitHub Discussions**: For general questions and ideas
- **🐛 GitHub Issues**: For bugs and feature requests
- **📧 Email**: enterprise@smartcloudops.ai for enterprise inquiries
- **📖 Documentation**: Check our comprehensive guides

### Resources

- **[Getting Started Guide](docs/GETTING_STARTED.md)**
- **[API Reference](docs/API_REFERENCE.md)**
- **[Architecture Overview](docs/ARCHITECTURE.md)**
- **[Security Guidelines](docs/SECURITY_HARDENING_GUIDE.md)**

### Stuck? Need Help?

Don't hesitate to reach out! We're here to help:

1. **Check existing issues** and discussions first
2. **Ask questions** in GitHub Discussions
3. **Tag maintainers** in issues for urgent matters
4. **Join our community** for real-time help

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License that covers the project.

---

<div align="center">

**🙏 Thank you for contributing to SmartCloudOps AI! 🙏**

*Together, we're building the future of intelligent cloud operations.*

[Back to Main README](../README.md)

</div>
