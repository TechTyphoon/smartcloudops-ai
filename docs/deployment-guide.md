# Smart CloudOps AI - Complete Deployment Guide

**Last Updated**: December 19, 2024  
**Current Status**: Phase 1 Complete - Ready for Production Deployment  

## 🎯 Overview

This guide provides step-by-step instructions for deploying the complete Smart CloudOps AI infrastructure and monitoring stack. Follow these instructions to get a fully functional system running on AWS.

## 📋 Prerequisites

### Required Tools
- **AWS CLI**: Configured with appropriate credentials
- **Terraform**: Version >= 1.0
- **SSH Key Pair**: For EC2 access
- **Git**: For repository management
- **Python 3.10+**: For setup scripts

### AWS Permissions Required
- EC2: Create/manage instances, security groups, key pairs
- VPC: Create/manage VPCs, subnets, internet gateways
- IAM: Basic permissions for resource tagging

### Cost Estimate
- **Free Tier Eligible**: Yes (for new AWS accounts)
- **Estimated Cost**: $0-5/month (depending on usage)
- **Instance Types**: t3.small/medium (free tier eligible)

## 🚀 Deployment Steps

### Step 1: Environment Setup

#### 1.1 Clone Repository and Setup
```bash
# Clone the repository
git clone <repository-url>
cd smartcloudops-ai

# Run automated setup
python3 setup.py

# Verify setup
python3 verify_setup.py
```

#### 1.2 Generate SSH Key Pair
```bash
# Generate SSH key for EC2 access
ssh-keygen -t rsa -b 4096 -f ~/.ssh/smartcloudops-ai-key

# Get public key content (copy this for terraform.tfvars)
cat ~/.ssh/smartcloudops-ai-key.pub
```

#### 1.3 Configure AWS CLI
```bash
# Configure AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

### Step 2: Infrastructure Configuration

#### 2.0 Remote State (Recommended)
Create `terraform/backend.hcl` with your S3/DynamoDB details and initialize with:

```bash
cd terraform
terraform init -backend-config=backend.hcl
```

#### 2.1 Configure Terraform Variables
```bash
# Navigate to terraform directory
cd terraform

# Copy example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit configuration file
nano terraform.tfvars
```

#### 2.2 Required Variables Configuration
Update `terraform.tfvars` with your values:

```hcl
# General Configuration
project_name    = "smartcloudops-ai"
environment     = "dev"
project_owner   = "YourName"

# AWS Configuration
aws_region = "us-west-2"  # or us-east-1 for original plan

# Network Configuration
vpc_cidr               = "10.0.0.0/16"
public_subnet_1_cidr   = "10.0.1.0/24"
public_subnet_2_cidr   = "10.0.2.0/24"
allowed_cidr_blocks    = ["YOUR_IP/32"]  # Replace with your IP

# EC2 Configuration
monitoring_instance_type   = "t3.medium"
application_instance_type  = "t3.small"

# SSH Key Configuration (paste your public key here)
public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAC... your-public-key-here"

# Monitoring Configuration
grafana_admin_password = "your-secure-password"
```

### Step 3: Infrastructure Deployment

#### 3.1 Initialize and Validate Terraform
```bash
# Initialize Terraform
terraform init

# Format configuration files
terraform fmt

# Validate configuration
terraform validate

# Plan deployment (review changes)
terraform plan -var="domain_name=app.example.com" -var="hosted_zone_id=Z123456ABCDEFG"
```

#### 3.2 Deploy Infrastructure
```bash
# Deploy infrastructure
terraform apply -var="domain_name=app.example.com" -var="hosted_zone_id=Z123456ABCDEFG"

# Type 'yes' when prompted to confirm deployment
```

#### 3.3 Capture Deployment Information
```bash
# Get deployment outputs
terraform output

# Save important information
export MONITORING_IP=$(terraform output -raw monitoring_instance_public_ip)
export APPLICATION_IP=$(terraform output -raw application_instance_public_ip)

echo "Monitoring IP: $MONITORING_IP"
echo "Application IP: $APPLICATION_IP"
```

### Step 4: Monitoring Configuration

#### 4.1 Configure Monitoring Stack
```bash
# Run monitoring configuration script
./scripts/configure_monitoring.sh $MONITORING_IP $APPLICATION_IP

# Wait for configuration to complete (2-3 minutes)
```

#### 4.2 Upload Advanced Dashboards (Optional)
```bash
# Upload advanced dashboard configurations
./scripts/upload_dashboards.sh $MONITORING_IP

# Wait for services to restart (1-2 minutes)
```

### Step 5: Verification and Access

#### 5.1 Verify Service Health
```bash
# Check Prometheus
curl -s http://$MONITORING_IP:9090/api/v1/targets

# Check Grafana
curl -s http://$MONITORING_IP:3001/api/health

# Check Node Exporters
curl -s http://$MONITORING_IP:9100/metrics | head
curl -s http://$APPLICATION_IP:9100/metrics | head

# Check Flask application
curl -s http://$APPLICATION_IP:3000/status
```

#### 5.2 Access Web Interfaces
Open these URLs in your browser:

- **Prometheus**: http://[MONITORING_IP]:9090
- **Grafana**: http://[MONITORING_IP]:3001
  - Username: `admin`
  - Password: `admin` (or your configured password)
- **Flask Application**: https://[YOUR_DOMAIN] or http://[ALB_DNS] (HTTP redirects to HTTPS)
  - Route53: Alias record `A` for `[YOUR_DOMAIN]` pointing to ALB DNS is auto-created when vars set.

### Step 5.3 Application Environments
- Development/local: use `.env` (copied from `env.template`). `docker-compose.yml` provisions Postgres and sets `DATABASE_URL` for the app service.
- Production: set environment variables via your orchestrator or AWS SSM. `DATABASE_URL` is required; `FLASK_ENV=production` and `FLASK_PORT=3000` are expected.

### Step 6: SSH Access Configuration

#### 6.1 Configure SSH Access
```bash
# Set correct permissions for SSH key
chmod 400 ~/.ssh/smartcloudops-ai-key

# Test SSH access to monitoring server
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@$MONITORING_IP

# Test SSH access to application server
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@$APPLICATION_IP
```

#### 6.2 SSH Convenience (Optional)
Add to `~/.ssh/config`:
```
Host smartcloudops-monitoring
    HostName [MONITORING_IP]
    User ec2-user
    IdentityFile ~/.ssh/smartcloudops-ai-key

Host smartcloudops-application
    HostName [APPLICATION_IP]
    User ec2-user
    IdentityFile ~/.ssh/smartcloudops-ai-key
```

## 🔧 Post-Deployment Configuration

### Grafana Dashboard Setup

#### 1. Access Grafana
1. Open http://[MONITORING_IP]:3001
2. Login with admin/admin (change password when prompted)
3. Navigate to Dashboards

#### 2. Verify Dashboards
- **System Overview**: Should show CPU, memory, disk metrics
- **Prometheus Monitoring**: Should show target health and performance

#### 3. Customize Dashboards (Optional)
- Modify thresholds and colors
- Add additional panels
- Create custom alerts

### Prometheus Configuration

#### 1. Verify Targets
1. Open http://[MONITORING_IP]:9090
2. Go to Status > Targets
3. Verify all targets show "UP" status

#### 2. Test Queries
Sample queries to test:
```promql
# CPU usage
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Terraform Deployment Fails
**Problem**: Permission denied or resource conflicts  
**Solution**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify region availability
aws ec2 describe-availability-zones --region us-west-2

# Check for resource name conflicts
terraform import aws_key_pair.smartcloudops_key smartcloudops-ai-key
```

#### 2. Cannot Access Services
**Problem**: Services not accessible via web browser  
**Solution**:
```bash
# Check security group rules
aws ec2 describe-security-groups --group-names smartcloudops-ai-*

# Verify instance status
aws ec2 describe-instances --filters "Name=tag:Name,Values=smartcloudops-ai-*"

# Check service status on instances
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@$MONITORING_IP "docker ps"
```

#### 3. Monitoring Data Missing
**Problem**: Grafana shows "No Data"  
**Solution**:
```bash
# Check Prometheus targets
curl http://$MONITORING_IP:9090/api/v1/targets

# Verify Node Exporter
curl http://$APPLICATION_IP:9100/metrics

# Check Grafana data source
curl -u admin:admin http://$MONITORING_IP:3001/api/datasources
```

#### 4. SSH Connection Issues
**Problem**: Cannot SSH to instances  
**Solution**:
```bash
# Check key permissions
chmod 400 ~/.ssh/smartcloudops-ai-key

# Verify security group allows SSH from your IP
aws ec2 describe-security-groups --filters "Name=group-name,Values=smartcloudops-ai-*"

# Check instance public IP
terraform output monitoring_instance_public_ip
```

### Log Locations

#### Monitoring Server
```bash
# Docker container logs
docker logs prometheus
docker logs grafana
docker logs node-exporter

# System logs
sudo journalctl -u docker
tail -f /var/log/cloud-init-output.log
```

#### Application Server
```bash
# Flask application logs
sudo journalctl -u smartcloudops-app

# Node Exporter logs
sudo journalctl -u node_exporter

# System logs
tail -f /var/log/cloud-init-output.log
```

## 🧹 Cleanup and Destruction

### Temporary Cleanup
```bash
# Stop services without destroying infrastructure
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@$MONITORING_IP "cd /opt/monitoring && docker-compose down"
```

### Complete Destruction
```bash
# Destroy all infrastructure
cd terraform
terraform destroy

# Type 'yes' when prompted to confirm destruction
```

## 📊 Health Monitoring

### Service Health Checks
```bash
#!/bin/bash
# health-check.sh - Monitor service health

echo "=== Smart CloudOps AI Health Check ==="

# Check Prometheus
if curl -s http://$MONITORING_IP:9090/api/v1/targets >/dev/null; then
    echo "✅ Prometheus: Healthy"
else
    echo "❌ Prometheus: Unhealthy"
fi

# Check Grafana
if curl -s http://$MONITORING_IP:3001/api/health >/dev/null; then
    echo "✅ Grafana: Healthy"
else
    echo "❌ Grafana: Unhealthy"
fi

# Check Flask App
if curl -s http://$APPLICATION_IP:3000/status >/dev/null; then
    echo "✅ Flask App: Healthy"
else
    echo "❌ Flask App: Unhealthy"
fi

# Check Node Exporters
if curl -s http://$MONITORING_IP:9100/metrics >/dev/null; then
    echo "✅ Node Exporter (Monitoring): Healthy"
else
    echo "❌ Node Exporter (Monitoring): Unhealthy"
fi

if curl -s http://$APPLICATION_IP:9100/metrics >/dev/null; then
    echo "✅ Node Exporter (Application): Healthy"
else
    echo "❌ Node Exporter (Application): Unhealthy"
fi
```

## 🚀 Next Steps

After successful deployment, you're ready for Phase 2:

1. **Flask ChatOps Application Development**
2. **GPT Integration** (OpenAI API key required)
3. **Advanced Dockerization**
4. **Enhanced CI/CD for Application**

See [Phase 2 Documentation](phase-2-flask-app.md) for next steps.

## 📞 Support

For deployment issues:
1. Check the troubleshooting section above
2. Review the [monitoring guide](../terraform/monitoring-guide.md)
3. Check service logs as described above
4. Verify all prerequisites are met

---

**🎉 Congratulations!** You now have a fully functional Smart CloudOps AI infrastructure with comprehensive monitoring capabilities.

### Step 6: CI/CD and Image Security

- Configure GitHub Actions secret `AWS_ROLE_TO_ASSUME` and repository variables `AWS_REGION`, `ECR_REPOSITORY`.
- On push to main, workflow `.github/workflows/ecr-build-push.yml` builds `Dockerfile.production`, pushes to ECR, and scans with Trivy. The build fails on HIGH/CRITICAL findings.

### Step 7: Alarms and Notifications

- SNS topic `${project_name}-ops-alarms` is created. Provide `-var="alarm_email=you@example.com"` to subscribe an email.
- CloudWatch alarms include ALB 5xx/4xx, ECS CPU/Mem, and RDS failover.

- Optional Slack: set `-var="enable_slack_notifications=true" -var="slack_webhook_secret_name=projects/smartcloudops/slack/webhook"` where the secret contains `{ "webhook": "https://hooks.slack.com/services/..." }`. The Lambda bridge posts alarm summaries to Slack.
  - Validate: publish test to `$(terraform output -raw ops_alarms_topic_arn)` and check Slack.

### Step 8: HTTPS and Fallback

- If `domain_name` and `hosted_zone_id` provided, ACM cert is validated via Route53 and HTTP redirects to HTTPS.
- If no domain provided, ALB serves HTTP directly for smoke tests. Once ACM is ready, re-apply with domain vars to enforce HTTPS.

### Step 9: Database Persistence

- App resolves `DATABASE_URL` from SSM SecureString. RDS runs Multi-AZ with encryption and backups.
- A Secrets Manager secret for RDS creds is provisioned with a 30-day rotation placeholder (attach rotation Lambda later for full automation).

### Step 10: Safe Releases (Optional)

- Enable CodeDeploy Blue/Green with `-var="enable_blue_green=true"`. This wires a CodeDeploy application/group to coordinate traffic shifting with ALB listeners. Default remains ECS rolling with circuit breaker and rollback.
  - Two target groups (`-tg` and `-tg-green`) are configured for full blue/green isolation.