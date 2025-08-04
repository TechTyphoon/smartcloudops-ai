# Smart CloudOps AI - Troubleshooting Guide

**Last Updated**: December 19, 2024  
**Covers**: Phase 0 & Phase 1 Issues  

## 🚨 Quick Issue Resolution

### 🔍 Common Symptoms
| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Terraform apply fails | Invalid configuration | `terraform validate` |
| Cannot access Grafana | Security group issue | Check `allowed_cidr_blocks` |
| No monitoring data | Prometheus targets down | Check `/targets` endpoint |
| SSH connection fails | Key permissions | `chmod 400 ~/.ssh/key.pem` |
| Docker services down | Resource limits | Check `docker ps` and logs |

## 🔧 Phase 0: Foundation Issues

### Setup Script Failures

#### Issue: `python3 setup.py` fails
**Symptoms**: 
- Missing dependencies error
- Permission denied
- Virtual environment creation fails

**Diagnosis**:
```bash
# Check Python version
python3 --version

# Check available tools
which terraform docker aws git

# Check permissions
ls -la setup.py
```

**Solution**:
```bash
# Install missing tools
sudo apt update
sudo apt install python3-venv python3-pip

# Fix permissions
chmod +x setup.py

# Manual venv creation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Issue: Verification script fails
**Symptoms**: 
- "Missing files" errors
- Directory structure issues
- CI/CD workflow validation fails

**Diagnosis**:
```bash
# Run verification with details
python3 verify_setup.py

# Check file structure
ls -la
tree . -L 2
```

**Solution**:
```bash
# Recreate missing directories
mkdir -p terraform app scripts ml_models .github/workflows docs

# Verify git repository
git status
git add .
```

### CI/CD Pipeline Issues

#### Issue: GitHub Actions failing
**Symptoms**:
- Workflow syntax errors
- Permission denied in actions
- Security scanning failures

**Diagnosis**:
```bash
# Validate workflow files
github-action-validator .github/workflows/ci-infra.yml
github-action-validator .github/workflows/ci-app.yml

# Check repository settings
# - Actions permissions
# - Branch protection rules
```

**Solution**:
```yaml
# Fix common workflow issues
# In .github/workflows/ci-*.yml

# Add proper permissions
permissions:
  contents: read
  security-events: write

# Fix dependency installation
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

## 🏗️ Phase 1: Infrastructure Issues

### Terraform Deployment Problems

#### Issue: `terraform apply` fails with user_data size error
**Symptoms**:
```
Error: expected length of user_data to be in the range (0 - 16384)
```

**Diagnosis**:
```bash
# Check user_data size
cd terraform
terraform plan

# Validate configuration
terraform validate
```

**Solution**:
```bash
# This was fixed in our implementation
# User data now uses simplified approach
# If you encounter this, update main.tf:

# Replace complex templatefile with simple file reference
user_data = base64encode(file("${path.module}/scripts/monitoring_setup.sh"))
```

#### Issue: AWS permissions denied
**Symptoms**:
- "UnauthorizedOperation" errors
- "AccessDenied" for specific resources
- "InvalidUserID.NotFound" errors

**Diagnosis**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify permissions
aws iam get-user
aws iam list-attached-user-policies --user-name <username>
```

**Solution**:
```bash
# Configure AWS CLI
aws configure

# Required permissions for Smart CloudOps AI:
# - EC2: DescribeInstances, RunInstances, TerminateInstances
# - VPC: CreateVpc, CreateSubnet, CreateInternetGateway
# - IAM: Basic permissions for resource tagging
```

#### Issue: Resource already exists errors
**Symptoms**:
- "AlreadyExists" errors for VPC, subnets
- "InvalidKeyPair.Duplicate" errors
- State file conflicts

**Diagnosis**:
```bash
# Check existing resources
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=smartcloudops-*"
aws ec2 describe-key-pairs --key-names smartcloudops-ai-key

# Check terraform state
terraform state list
```

**Solution**:
```bash
# Option 1: Import existing resources
terraform import aws_vpc.smartcloudops_vpc vpc-xxxxxxxx
terraform import aws_key_pair.smartcloudops_key smartcloudops-ai-key

# Option 2: Use different names
# Edit variables.tf
project_name = "smartcloudops-ai-v2"

# Option 3: Clean up existing resources
aws ec2 delete-key-pair --key-name smartcloudops-ai-key
```

### EC2 Instance Issues

#### Issue: Instances not accessible
**Symptoms**:
- SSH timeout
- HTTP/HTTPS connection refused
- Services not responding

**Diagnosis**:
```bash
# Check instance status
aws ec2 describe-instances --filters "Name=tag:Name,Values=smartcloudops-ai-*"

# Check security groups
aws ec2 describe-security-groups --filters "Name=group-name,Values=smartcloudops-ai-*"

# Test connectivity
telnet <instance-ip> 22
telnet <instance-ip> 9090
```

**Solution**:
```bash
# Fix security group rules
# Edit terraform/terraform.tfvars
allowed_cidr_blocks = ["YOUR_ACTUAL_IP/32"]

# Re-apply terraform
terraform apply

# Check SSH key permissions
chmod 400 ~/.ssh/smartcloudops-ai-key

# Verify instance is running
aws ec2 describe-instance-status --instance-ids <instance-id>
```

#### Issue: User data script failures
**Symptoms**:
- Services not installed
- Docker not running
- Monitoring stack not started

**Diagnosis**:
```bash
# SSH to instance and check logs
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@<instance-ip>

# Check cloud-init logs
sudo tail -f /var/log/cloud-init-output.log
sudo cat /var/log/cloud-init.log

# Check service status
sudo systemctl status docker
sudo systemctl status node_exporter
```

**Solution**:
```bash
# Manual service restart
sudo systemctl start docker
sudo systemctl enable docker

# Check Docker services
cd /opt/monitoring
sudo docker-compose ps
sudo docker-compose logs

# Restart monitoring stack
sudo docker-compose down
sudo docker-compose up -d
```

## 📊 Monitoring Stack Issues

### Prometheus Problems

#### Issue: Prometheus not collecting data
**Symptoms**:
- Empty metrics in Grafana
- Targets showing as "DOWN"
- No data points in queries

**Diagnosis**:
```bash
# Check Prometheus targets
curl http://<monitoring-ip>:9090/api/v1/targets

# Check Prometheus configuration
curl http://<monitoring-ip>:9090/api/v1/status/config

# SSH to monitoring server
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@<monitoring-ip>
cd /opt/monitoring
docker logs prometheus
```

**Solution**:
```bash
# Update Prometheus configuration with correct IPs
./scripts/configure_monitoring.sh <monitoring-ip> <application-ip>

# Restart Prometheus
cd /opt/monitoring
docker-compose restart prometheus

# Verify targets
curl http://<monitoring-ip>:9090/api/v1/targets | jq '.data.activeTargets[].health'
```

#### Issue: Node Exporter not accessible
**Symptoms**:
- Node exporter targets DOWN
- No system metrics
- Connection refused on port 9100

**Diagnosis**:
```bash
# Test Node Exporter directly
curl http://<instance-ip>:9100/metrics

# Check service status
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@<instance-ip>
sudo systemctl status node_exporter

# Check if port is listening
sudo netstat -tlnp | grep :9100
```

**Solution**:
```bash
# Restart Node Exporter service
sudo systemctl restart node_exporter
sudo systemctl enable node_exporter

# Check service logs
sudo journalctl -u node_exporter -f

# Verify metrics endpoint
curl localhost:9100/metrics | head -20
```

### Grafana Problems

#### Issue: Grafana shows "No Data"
**Symptoms**:
- Dashboards display "No Data"
- Data source connection issues
- Query errors

**Diagnosis**:
```bash
# Check Grafana logs
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@<monitoring-ip>
cd /opt/monitoring
docker logs grafana

# Check data source configuration
curl -u admin:admin http://<monitoring-ip>:3001/api/datasources

# Test Prometheus connectivity from Grafana
curl -u admin:admin http://<monitoring-ip>:3001/api/datasources/proxy/1/api/v1/query?query=up
```

**Solution**:
```bash
# Restart Grafana
cd /opt/monitoring
docker-compose restart grafana

# Re-configure data source (if needed)
# Access Grafana UI: http://<monitoring-ip>:3001
# Go to Configuration > Data Sources
# Verify Prometheus URL: http://localhost:9090

# Upload advanced dashboards
./scripts/upload_dashboards.sh <monitoring-ip>
```

#### Issue: Cannot login to Grafana
**Symptoms**:
- Invalid credentials error
- Login page not loading
- Connection timeout

**Diagnosis**:
```bash
# Check Grafana service
cd /opt/monitoring
docker ps | grep grafana
docker logs grafana

# Test Grafana port
telnet <monitoring-ip> 3001
```

**Solution**:
```bash
# Reset Grafana admin password
cd /opt/monitoring
docker-compose exec grafana grafana-cli admin reset-admin-password admin

# Restart Grafana service
docker-compose restart grafana

# Default credentials: admin/admin
# Change password on first login
```

## 🔐 Security and Access Issues

### SSH Access Problems

#### Issue: SSH key authentication fails
**Symptoms**:
- "Permission denied (publickey)"
- "Host key verification failed"
- Connection timeout

**Diagnosis**:
```bash
# Check key permissions
ls -la ~/.ssh/smartcloudops-ai-key*

# Test SSH with verbose output
ssh -v -i ~/.ssh/smartcloudops-ai-key ec2-user@<instance-ip>

# Verify public key in terraform.tfvars
cat ~/.ssh/smartcloudops-ai-key.pub
```

**Solution**:
```bash
# Fix key permissions
chmod 400 ~/.ssh/smartcloudops-ai-key
chmod 644 ~/.ssh/smartcloudops-ai-key.pub

# Verify key format (should start with ssh-rsa)
cat ~/.ssh/smartcloudops-ai-key.pub

# Re-deploy with correct public key
# Edit terraform/terraform.tfvars
public_key = "ssh-rsa AAAAB3NzaC1yc2E... your-key-here"
terraform apply
```

### Network Access Issues

#### Issue: Cannot access web interfaces
**Symptoms**:
- Browser timeout for Grafana/Prometheus
- Connection refused errors
- Firewall blocking access

**Diagnosis**:
```bash
# Check your public IP
curl ifconfig.me

# Verify security group rules
aws ec2 describe-security-groups --filters "Name=group-name,Values=smartcloudops-ai-*"

# Test specific ports
telnet <monitoring-ip> 9090  # Prometheus
telnet <monitoring-ip> 3001  # Grafana
```

**Solution**:
```bash
# Update allowed CIDR blocks
# Edit terraform/terraform.tfvars
allowed_cidr_blocks = ["$(curl -s ifconfig.me)/32"]

# Apply changes
terraform apply

# Verify security group updates
aws ec2 describe-security-groups --filters "Name=group-name,Values=smartcloudops-ai-monitoring-sg"
```

## 🚀 Performance Issues

### High Resource Usage

#### Issue: High CPU/Memory on instances
**Symptoms**:
- Slow response times
- Services becoming unresponsive
- Instance status checks failing

**Diagnosis**:
```bash
# Check instance metrics in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=<instance-id> \
  --start-time 2024-12-19T00:00:00Z \
  --end-time 2024-12-19T23:59:59Z \
  --period 3600 \
  --statistics Average

# SSH to instance and check resources
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@<instance-ip>
top
htop
df -h
free -h
```

**Solution**:
```bash
# Scale up instance if needed
# Edit terraform/variables.tf
monitoring_instance_type = "t3.large"
application_instance_type = "t3.medium"

# Apply changes
terraform apply

# Optimize Docker resource usage
cd /opt/monitoring
# Edit docker-compose.yml to add resource limits
services:
  prometheus:
    deploy:
      resources:
        limits:
          memory: 1G
```

## 🔄 Recovery Procedures

### Complete System Recovery

#### Issue: Total system failure
**Symptoms**:
- All services down
- Cannot access any interfaces
- Infrastructure corrupted

**Recovery Steps**:
```bash
# 1. Verify infrastructure state
cd terraform
terraform state list
terraform plan

# 2. Rebuild infrastructure if needed
terraform destroy  # Only if necessary
terraform apply

# 3. Reconfigure monitoring
MONITORING_IP=$(terraform output -raw monitoring_instance_public_ip)
APPLICATION_IP=$(terraform output -raw application_instance_public_ip)
./scripts/configure_monitoring.sh $MONITORING_IP $APPLICATION_IP

# 4. Upload dashboards
./scripts/upload_dashboards.sh $MONITORING_IP

# 5. Verify all services
./scripts/health-check.sh  # From deployment guide
```

### Partial Service Recovery

#### Issue: Single service failure
**Recovery for specific services**:

```bash
# Prometheus recovery
cd /opt/monitoring
docker-compose restart prometheus

# Grafana recovery
docker-compose restart grafana

# Node Exporter recovery
sudo systemctl restart node_exporter

# Flask app recovery (Phase 2+)
sudo systemctl restart smartcloudops-app
```

## 📋 Prevention Best Practices

### Regular Maintenance
```bash
# Weekly health checks
./scripts/health-check.sh

# Monthly security updates
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@<instance-ip>
sudo yum update -y

# Backup configurations
cd terraform
terraform plan -out=backup.tfplan
```

### Monitoring Setup
- Set up CloudWatch alarms for instance health
- Configure Grafana alerts for critical metrics
- Regular testing of backup and recovery procedures

---

## 🆘 Getting Help

### Information to Gather
Before seeking help, collect:
1. **Error messages**: Full error text and logs
2. **System info**: OS, versions, configurations
3. **Steps to reproduce**: What you were doing when issue occurred
4. **Environment**: Development vs production setup

### Log Locations
- **Terraform**: `terraform apply` output
- **AWS**: CloudWatch logs for instances
- **Docker**: `docker logs <container-name>`
- **System**: `/var/log/cloud-init-output.log`
- **Services**: `sudo journalctl -u <service-name>`

### Quick Diagnostic Commands
```bash
# Infrastructure status
terraform output
aws ec2 describe-instances --filters "Name=tag:Name,Values=smartcloudops-ai-*"

# Service status
curl http://<monitoring-ip>:9090/api/v1/targets
curl http://<monitoring-ip>:3001/api/health
curl http://<application-ip>:3000/status

# System health
ssh -i ~/.ssh/smartcloudops-ai-key ec2-user@<instance-ip> "top -n1 -b | head -20"
```

---

This troubleshooting guide covers the most common issues for Phase 0 and Phase 1. It will be updated as new phases are completed and new issues are identified.