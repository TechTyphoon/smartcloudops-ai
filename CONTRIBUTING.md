# 🤝 Contributing to SmartCloudOps AI

We love your input! We want to make contributing to SmartCloudOps AI as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 **We Develop with GitHub**

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## 📋 **We Use GitHub Flow**

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

### 🔄 **Pull Request Process**

1. **Fork the repository** and create your branch from `main`
2. **Clone your fork** locally
3. **Create a feature branch**: `git checkout -b feature/amazing-feature`
4. **Make your changes** with clear, commented code
5. **Add tests** if you've added code that should be tested
6. **Update documentation** if you've changed APIs or functionality
7. **Ensure the test suite passes**: `python -m pytest tests/`
8. **Run security audit**: `python scripts/security_audit.py`
9. **Make sure your code follows our style guidelines**
10. **Issue the pull request** with a clear description

### ✅ **Pull Request Checklist**

- [ ] **Code follows** the project's style guidelines
- [ ] **Self-review** performed on the code
- [ ] **Comments added** to hard-to-understand areas
- [ ] **Documentation updated** for any new features
- [ ] **Tests added** for new functionality
- [ ] **All tests pass** locally
- [ ] **Security audit passes**
- [ ] **No breaking changes** or clearly documented

---

## 🐛 **Report Bugs Using GitHub Issues**

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/TechTyphoon/smartcloudops-ai/issues/new).

### 📝 **Bug Report Template**

**Great Bug Reports** tend to have:

- **Clear, descriptive title**
- **Quick summary** and/or background
- **Steps to reproduce**
  - Be specific!
  - Give sample code if you can
- **What you expected** would happen
- **What actually happens**
- **Environment details** (OS, Python version, Docker version)
- **Additional context** (logs, screenshots)

### 🔍 **Example Bug Report**

```
**Bug Summary**: Flask app crashes when processing ML predictions

**Environment**:
- OS: Ubuntu 20.04
- Python: 3.9.7
- Docker: 20.10.12
- SmartCloudOps AI: v3.0.0

**Steps to Reproduce**:
1. Deploy using `docker-compose -f docker-compose.tier2.yml up -d`
2. Send POST request to `/api/predict` endpoint
3. Include malformed JSON payload: `{"metrics": "invalid"}`
4. Observe server crash

**Expected**: HTTP 400 error with validation message
**Actual**: Container exits with 500 error

**Additional Context**: 
- Logs show: `KeyError: 'cpu_usage'` in ml_models.py line 45
- Issue occurs with any malformed prediction request
```

---

## ✨ **Feature Requests**

We love feature ideas! Please [open an issue](https://github.com/TechTyphoon/smartcloudops-ai/issues/new) with:

- **Clear title** describing the feature
- **Detailed description** of the functionality
- **Use cases** and examples
- **Acceptance criteria** for the feature
- **Potential implementation** approach (if known)

---

## 🏗️ **Development Environment Setup**

### 📋 **Prerequisites**
- Python 3.8+
- Docker & Docker Compose
- Git
- Virtual environment tool (venv/conda)

### 🛠️ **Local Development Setup**

```bash
# 1. Fork and clone the repository
git clone https://github.com/YourUsername/smartcloudops-ai.git
cd smartcloudops-ai

# 2. Create and activate virtual environment
python3 -m venv dev_env
source dev_env/bin/activate  # On Windows: dev_env\Scripts\activate

# 3. Install development dependencies
pip install -r requirements-dev.txt

# 4. Set up pre-commit hooks (optional but recommended)
pre-commit install

# 5. Run the application locally
python app.py

# 6. Run tests
python -m pytest tests/ -v

# 7. Run security audit
python scripts/security_audit.py
```

### 🐳 **Docker Development**

```bash
# Build development image
docker build -t smartcloudops-dev .

# Run development stack
docker-compose -f docker-compose.dev.yml up -d

# Run tests in container
docker exec -it smartcloudops-app python -m pytest tests/
```

---

## 📝 **Coding Standards**

### 🐍 **Python Style Guide**
- **PEP 8** compliance
- **Type hints** for function signatures
- **Docstrings** for all functions and classes
- **Meaningful variable names**
- **Comments** for complex logic

### 📁 **File Organization**
- **Modular structure** with clear separation of concerns
- **Tests alongside code** in appropriate test directories
- **Configuration files** in dedicated config directories
- **Documentation** in the `docs/` folder

### 🧪 **Testing Standards**
- **Unit tests** for all functions
- **Integration tests** for API endpoints
- **Security tests** for vulnerabilities
- **Performance tests** for critical paths
- **Minimum 80% test coverage**

### 🔒 **Security Guidelines**
- **No hardcoded secrets** or credentials
- **Input validation** for all user inputs
- **SQL injection prevention**
- **XSS protection** in web interfaces
- **Regular dependency updates**

---

## 🎯 **Areas for Contribution**

### 🚀 **High Priority**
- **Performance optimizations** for ML inference
- **Additional monitoring integrations** (DataDog, New Relic)
- **Enhanced security scanning** capabilities
- **API rate limiting** and throttling
- **Mobile-responsive dashboards**

### 🛠️ **Medium Priority**
- **Additional cloud provider support** (Azure, GCP)
- **Kubernetes Helm charts**
- **VS Code extension** for developers
- **Custom alerting rules**
- **Enhanced documentation** and tutorials

### 🔍 **Good First Issues**
- **Bug fixes** in existing functionality
- **Documentation improvements**
- **Test coverage expansion**
- **UI/UX enhancements**
- **Code cleanup** and refactoring

---

## 📚 **Resources**

### 🔗 **Useful Links**
- **[Project Architecture](docs/ARCHITECTURE.md)**
- **[API Documentation](docs/API_REFERENCE.md)**
- **[Security Guidelines](docs/SECURITY_AUDIT_REPORT_ENHANCED.md)**
- **[Testing Guide](docs/TESTING_GUIDE.md)**

### 🛠️ **Development Tools**
- **[Flask Documentation](https://flask.palletsprojects.com/)**
- **[Prometheus Documentation](https://prometheus.io/docs/)**
- **[Docker Best Practices](https://docs.docker.com/develop/best-practices/)**
- **[Python Testing with pytest](https://docs.pytest.org/)**

---

## 🏆 **Recognition**

Contributors who make significant improvements will be:

- **Listed in CONTRIBUTORS.md**
- **Mentioned in release notes**
- **Given appropriate GitHub repository permissions**
- **Invited to maintainer team** (for major contributors)

---

## 📞 **Get Help**

### 💬 **Communication Channels**
- **GitHub Discussions**: For general questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Discord Server**: For real-time chat *(Coming Soon)*
- **Email**: enterprise@smartcloudops.ai for enterprise inquiries

### 🆘 **Stuck? Need Help?**
Don't hesitate to reach out! We're here to help:
1. **Check existing issues** and discussions first
2. **Ask questions** in GitHub Discussions
3. **Tag maintainers** in issues for urgent matters
4. **Join our community** Discord for real-time help

---

## 📄 **License**

By contributing, you agree that your contributions will be licensed under the MIT License that covers the project.

---

<div align="center">

**🙏 Thank you for contributing to SmartCloudOps AI! 🙏**

*Together, we're building the future of intelligent cloud operations.*

</div>
