# CI/CD Pipeline Developer Guide

## 🚀 One-Command Local CI Replication

To run the **exact same checks** that GitHub Actions runs, use:

```bash
make ci
```

This command will:
- ✅ Install all dependencies (production + dev)
- ✅ Format & lint code (Black, isort, Flake8)
- ✅ Run security scans (Bandit, Safety)
- ✅ Execute full test suite with coverage
- ✅ Generate comprehensive reports

## 🔧 Quick Development Commands

```bash
# Setup development environment
make setup

# Format code before committing
make format

# Run tests only
make test

# Fast parallel tests
make test-fast

# Pre-commit checks (quick)
make pre-commit

# Security scans only
make security
```

## 📋 CI/CD Pipeline Overview

Our pipeline runs in **5 stages** for maximum reliability:

### Stage 1: 🔍 Code Quality & Security (10 min timeout)
- **Black formatting** (exact version: 24.4.2) - BLOCKS on failure
- **isort import sorting** - BLOCKS on failure  
- **Flake8 linting** - Critical errors block, style warnings reported
- **Bandit security scan** - Reports but doesn't block
- **Safety dependency scan** - Reports but doesn't block

### Stage 2: 🧪 Comprehensive Testing (20 min timeout)
- **Matrix testing**: Python 3.11 & 3.12 on Ubuntu
- **Mocked services**: PostgreSQL & Redis (lightweight)
- **Test environment**: All external APIs mocked
- **Coverage reporting**: 75% minimum threshold
- **Parallel execution**: Fast feedback

### Stage 3: 🐳 Build & Container Security (15 min timeout)
- **Docker multi-platform build** (cached)
- **Container vulnerability scanning** (Trivy)
- **SARIF security reporting**
- **GitHub Container Registry** push

### Stage 4: 🚀 Deployment (Conditional)
- **Staging**: Auto-deploy on `develop` branch
- **Production**: Auto-deploy on version tags (`v*`)

### Stage 5: 📊 Reporting & Notifications
- **Pipeline status summary**
- **Artifact collection** (test results, coverage, security reports)
- **Clear failure explanations**

## 🛠️ Fixing Common CI Issues

### Black Formatting Mismatch
The pipeline uses **Black 24.4.2** with **LF line endings** via `.gitattributes`:
```bash
# Fix locally
make format
git add -A && git commit -m "Fix Black formatting"
```

### Test Failures
```bash
# Run tests locally exactly like CI
make test

# Debug failing tests
pytest tests/ -vvv --tb=long --maxfail=1
```

### Security Scan Issues
```bash
# Run security scans locally
make security

# View detailed bandit report
bandit -r . -f json -o bandit_report.json
cat bandit_report.json | jq
```

### Dependency Issues
```bash
# Update and check dependencies
make update-deps
make check-deps
```

## 🔄 Pipeline Caching Strategy

- **Pip dependencies**: Cached by `requirements-*.txt` hash
- **Docker layers**: GitHub Actions cache with `gha` mode
- **Test artifacts**: Retained for 30 days

## 📊 Key Metrics & Thresholds

- **Code Coverage**: 75% minimum (configurable in `pyproject.toml`)
- **Security**: Critical/High vulnerabilities reported, not blocking
- **Performance**: Pipeline completes in ~15-20 minutes
- **Reliability**: Fail-fast disabled, all matrix jobs complete

## 🎯 Success Criteria

The pipeline **passes** when:
1. ✅ Code formatting is consistent (Black + isort)
2. ✅ No critical syntax/import errors (Flake8)
3. ✅ All tests pass with adequate coverage
4. ✅ Docker image builds successfully
5. ✅ No critical security vulnerabilities in build

The pipeline **provides warnings** for:
- 🔶 Style issues (Flake8 warnings)
- 🔶 Security vulnerabilities (reported, not blocking)
- 🔶 Dependency vulnerabilities (reported, not blocking)

## 🚫 What Does NOT Fail the Build

- Style warnings (max line length, complexity)
- Security scan warnings (unless critical)
- Coverage below 75% (warning only)
- Container vulnerability scans (reported only)

This approach prioritizes **developer happiness** while maintaining **production quality**.
