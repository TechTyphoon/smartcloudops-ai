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

### 1. main.yml
**Purpose**: Main CI/CD pipeline for application code
**Triggers**: Push to main/develop, PRs, tags, manual
**Features**:
- Code quality checks (Black, isort, flake8)
- Security scanning (Bandit, Safety)
- Unit and integration testing
- Docker image building and pushing
- Infrastructure validation
- Conditional deployments

### 2. infrastructure.yml
**Purpose**: Infrastructure as Code validation
**Triggers**: Terraform changes, PRs
**Features**:
- Terraform format checking
- Terraform validation
- Terraform planning (with AWS credentials)
- Infrastructure security scanning (Checkov)

### 3. security.yml
**Purpose**: Comprehensive security scanning
**Triggers**: Scheduled (weekly), manual, security-sensitive changes
**Features**:
- Python security scanning (Bandit)
- Dependency vulnerability scanning (Safety)
- Secret scanning (Gitleaks)
- Docker image security scanning
- Infrastructure security scanning (tfsec, kubesec)

### 4. reusable.yml
**Purpose**: Reusable workflow components
**Triggers**: Called by other workflows
**Features**:
- Python environment setup
- Code quality checks
- Security scanning
- Shared utilities

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

## 📊 Workflow Status

### Active Workflows
- ✅ **main.yml** - Primary CI/CD pipeline
- ✅ **infrastructure.yml** - Infrastructure validation
- ✅ **security.yml** - Security scanning
- ✅ **reusable.yml** - Reusable components

### Workflow Dependencies
```
Code Changes → main.yml → Quality Gate → Tests → Build → Deploy
Infra Changes → infrastructure.yml → Terraform Validate → Plan → Apply
Security Changes → security.yml → Security Scan → Compliance Check
```

## 🔍 Troubleshooting

### Common Issues
1. **Workflow Failures**: Check logs for specific error messages
2. **Permission Issues**: Verify GitHub secrets and variables
3. **Build Failures**: Check Docker and dependency issues
4. **Test Failures**: Review test output and fix failing tests

### Debug Mode
- Enable debug logging in workflows
- Check workflow run logs
- Verify environment variables
- Test locally before pushing

## 📈 Performance

### Optimization Tips
- Use caching for dependencies
- Parallel job execution
- Conditional job execution
- Efficient Docker builds
- Minimal workflow triggers

## 🔒 Security

### Best Practices
- Use least privilege permissions
- Scan for secrets and vulnerabilities
- Regular dependency updates
- Secure credential management
- Audit workflow access

---

**SmartCloudOps AI v3.3.0** - Workflow Configuration
