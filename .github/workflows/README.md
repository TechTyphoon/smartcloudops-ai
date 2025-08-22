# GitHub Actions Workflows Configuration Guide

This document outlines the required GitHub Secrets and Variables for all workflows in this repository.

## 🔐 Required GitHub Secrets

### AWS Credentials (for ECR and Infrastructure workflows)
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: AWS region (default: us-west-2)

### Security Tools
- `GITLEAKS_LICENSE`: License key for Gitleaks secret scanning (optional)

### Container Registry
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

## 🔧 Required GitHub Variables

### AWS Configuration
- `AWS_REGION`: AWS region for deployments (default: us-west-2)
- `ECR_REPOSITORY`: ECR repository name (default: smartcloudops-ai-app)

## 📋 Workflow Dependencies

### Files Required for Workflows

1. **Dockerfile.production** - Used by ECR and security workflows
2. **Dockerfile** - Fallback for ECR and security workflows
3. **requirements.txt** - Python dependencies
4. **requirements-dev.txt** - Development dependencies
5. **terraform/** directory - Infrastructure as Code
6. **k8s/** directory - Kubernetes manifests
7. **tests/unit/** and **tests/integration/** - Test directories

### Environment Files
- **env.example** - Template for local development
- **.env** - Local environment (not committed to git)

## 🚀 Workflow Descriptions

### 1. ci-cd-optimized.yml
**Purpose**: Main CI/CD pipeline for application code
**Triggers**: Push to main/develop, PRs, tags, manual
**Features**:
- Code quality checks (Black, isort, flake8)
- Security scanning (Bandit, Safety)
- Unit and integration testing
- Docker image building and pushing
- Infrastructure validation
- Conditional deployments

### 2. ecr-build-push.yml
**Purpose**: Build and push Docker images to AWS ECR
**Triggers**: Push to main, manual
**Features**:
- AWS ECR authentication
- Docker image building
- Image vulnerability scanning
- Automatic tagging

### 3. security-monitoring.yml
**Purpose**: Comprehensive security scanning
**Triggers**: Scheduled (weekly), manual, security-sensitive changes
**Features**:
- Python security scanning (Bandit)
- Dependency vulnerability scanning (Safety)
- Secret scanning (Gitleaks)
- Docker image security scanning
- Infrastructure security scanning (tfsec, kubesec)

### 4. ci-infra.yml
**Purpose**: Infrastructure as Code validation
**Triggers**: Terraform changes, PRs
**Features**:
- Terraform format checking
- Terraform validation
- Terraform planning (with AWS credentials)
- Infrastructure security scanning (Checkov)

## 🔧 Setup Instructions

### 1. Configure GitHub Secrets
Go to your repository → Settings → Secrets and variables → Actions

Add the following secrets:
```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
GITLEAKS_LICENSE=your_gitleaks_license  # Optional
```

### 2. Configure GitHub Variables
Go to your repository → Settings → Secrets and variables → Actions

Add the following variables:
```bash
AWS_REGION=us-west-2
ECR_REPOSITORY=smartcloudops-ai-app
```

### 3. Verify File Structure
Ensure all required files exist:
```bash
# Check Dockerfiles
ls -la Dockerfile*

# Check requirements files
ls -la requirements*.txt

# Check test directories
ls -la tests/unit/ tests/integration/

# Check infrastructure files
ls -la terraform/ k8s/
```

## 🐛 Troubleshooting

### Common Issues

1. **Docker Build Failures**
   - Ensure Dockerfile.production exists
   - Check for syntax errors in Dockerfile
   - Verify all dependencies are available

2. **Terraform Validation Failures**
   - Run `terraform fmt` locally to fix formatting
   - Check for syntax errors in .tf files
   - Verify AWS credentials are correct

3. **Test Failures**
   - Ensure all test dependencies are in requirements-dev.txt
   - Check that test files follow pytest conventions
   - Verify test data and fixtures are available

4. **Security Scan Failures**
   - Review Bandit and Safety reports
   - Fix high-severity security issues
   - Update vulnerable dependencies

### Debug Commands

```bash
# Test Docker build locally
docker build -f Dockerfile.production -t test-image .

# Test Terraform locally
cd terraform
terraform init
terraform validate
terraform plan

# Run tests locally
pip install -r requirements-dev.txt
pytest tests/ -v

# Run security scans locally
bandit -r app/
safety scan
```

## 📊 Monitoring Workflow Status

All workflows include comprehensive logging and artifact uploads:
- Security scan results are uploaded as artifacts
- Test coverage reports are generated
- Docker scan results are uploaded to GitHub Security
- Infrastructure plans are commented on PRs

## 🔄 Workflow Optimization

The workflows are designed to:
- Run in parallel where possible
- Use caching for dependencies
- Fail fast on critical issues
- Continue on non-critical issues
- Provide detailed feedback and artifacts

## 📝 Best Practices

1. **Always test locally before pushing**
2. **Keep dependencies updated**
3. **Review security scan results regularly**
4. **Monitor workflow execution times**
5. **Use feature branches for development**
6. **Tag releases for production deployments**
