# GitHub Actions Setup Guide

This guide provides step-by-step instructions for setting up GitHub Actions workflows in your SmartCloudOps AI repository.

## 🔐 Required GitHub Secrets

### Step 1: Access Repository Settings

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Add Required Secrets

Click **New repository secret** and add the following secrets:

#### AWS Credentials
```
Name: AWS_ACCESS_KEY_ID
Value: your_aws_access_key_id_here
```

```
Name: AWS_SECRET_ACCESS_KEY
Value: your_aws_secret_access_key_here
```

```
Name: AWS_REGION
Value: us-west-2
```

#### Security Tools (Optional)
```
Name: GITLEAKS_LICENSE
Value: your_gitleaks_license_key_here
```

## 🔧 Required GitHub Variables

### Step 1: Add Repository Variables

In the same **Secrets and variables** → **Actions** page, click on the **Variables** tab, then click **New repository variable**:

#### AWS Configuration
```
Name: AWS_REGION
Value: us-west-2
```

```
Name: ECR_REPOSITORY
Value: smartcloudops-ai-app
```

## 🚀 Workflow Configuration

### Workflow Descriptions

1. **ci-cd-optimized.yml** - Main CI/CD pipeline
   - Triggers: Push to main/develop, PRs, tags, manual
   - Features: Code quality, testing, building, deployment

2. **ecr-build-push.yml** - ECR image building
   - Triggers: Push to main, manual
   - Features: Docker build, ECR push, security scanning

3. **security-monitoring.yml** - Security scanning
   - Triggers: Scheduled (weekly), manual, security changes
   - Features: Code security, dependency scanning, infrastructure security

4. **ci-infra.yml** - Infrastructure validation
   - Triggers: Terraform changes, PRs
   - Features: Terraform validation, planning, security scanning

## 🔍 Pre-Setup Validation

Before pushing to GitHub, run the local validation script:

```bash
python3 scripts/validate_github_workflows.py
```

This script checks:
- ✅ All required files exist
- ✅ Python syntax is valid
- ✅ Dockerfiles are present
- ✅ Terraform configuration is valid
- ✅ Test structure is correct
- ✅ Workflow YAML syntax is valid

## 📋 Setup Checklist

### Before First Push
- [ ] Run local validation script
- [ ] Configure GitHub Secrets (AWS credentials)
- [ ] Configure GitHub Variables (AWS region, ECR repo)
- [ ] Ensure all required files are committed
- [ ] Test workflows locally if possible

### After First Push
- [ ] Monitor workflow execution in GitHub Actions tab
- [ ] Check for any failed jobs
- [ ] Review security scan results
- [ ] Verify ECR repository creation
- [ ] Test deployment processes

## 🐛 Troubleshooting

### Common Issues

#### 1. AWS Credentials Errors
```
Error: AWS credentials not found
```
**Solution**: Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets are configured.

#### 2. ECR Repository Not Found
```
Error: Repository does not exist
```
**Solution**: 
- Check `ECR_REPOSITORY` variable is set correctly
- Ensure ECR repository exists in your AWS account
- Verify AWS region matches ECR repository location

#### 3. Docker Build Failures
```
Error: Docker build failed
```
**Solution**:
- Check Dockerfile syntax
- Verify all dependencies are available
- Ensure build context is correct

#### 4. Terraform Validation Failures
```
Error: Terraform validation failed
```
**Solution**:
- Run `terraform fmt` locally to fix formatting
- Check for syntax errors in .tf files
- Verify AWS credentials are correct

#### 5. Test Failures
```
Error: Tests failed
```
**Solution**:
- Check test dependencies in requirements-dev.txt
- Verify test files follow pytest conventions
- Check for missing test data or fixtures

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

## 📊 Monitoring Workflows

### GitHub Actions Dashboard
- Go to **Actions** tab in your repository
- Monitor workflow execution in real-time
- Review logs for failed jobs
- Download artifacts for analysis

### Key Metrics to Monitor
- Workflow execution time
- Success/failure rates
- Security scan results
- Test coverage reports
- Build artifact sizes

### Alerts and Notifications
- Configure repository notifications
- Set up Slack/Discord webhooks for workflow status
- Monitor security alerts from GitHub Security tab

## 🔒 Security Best Practices

### Secrets Management
- Never commit secrets to version control
- Use GitHub Secrets for sensitive data
- Rotate AWS credentials regularly
- Use least-privilege IAM policies

### Workflow Security
- Review workflow permissions
- Use `pull_request` triggers for security-sensitive changes
- Enable branch protection rules
- Require status checks to pass before merging

### Code Security
- Run security scans on every PR
- Review dependency vulnerabilities
- Scan Docker images for vulnerabilities
- Monitor for secrets in code

## 📈 Optimization Tips

### Performance
- Use caching for dependencies
- Parallelize independent jobs
- Optimize Docker layer caching
- Use matrix builds for multiple configurations

### Reliability
- Add retry logic for flaky tests
- Use `continue-on-error` for non-critical steps
- Implement proper error handling
- Add comprehensive logging

### Maintainability
- Keep workflows modular
- Use reusable workflow components
- Document complex configurations
- Regular dependency updates

## 📞 Support

If you encounter issues:

1. **Check the logs**: Review detailed logs in GitHub Actions
2. **Run local validation**: Use the validation script
3. **Review documentation**: Check this guide and workflow comments
4. **Search issues**: Look for similar issues in the repository
5. **Create issue**: Report bugs with detailed information

## 🔄 Updates and Maintenance

### Regular Tasks
- Update dependencies monthly
- Review security scan results weekly
- Monitor workflow performance
- Update workflow configurations as needed

### Version Updates
- Keep GitHub Actions versions updated
- Update Terraform version when needed
- Update Python version in workflows
- Review and update security tools

---

**Note**: This setup guide assumes you have the necessary AWS permissions and resources configured. Adjust the configuration based on your specific environment and requirements.
