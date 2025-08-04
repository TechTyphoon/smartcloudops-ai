# Smart CloudOps AI - Terraform Infrastructure

This directory contains the Terraform configuration for provisioning AWS infrastructure for the Smart CloudOps AI project.

## 🏗️ Infrastructure Components

### Phase 1.1 - Core Infrastructure
- **VPC**: 10.0.0.0/16 with DNS support
- **Subnets**: 2 public subnets across availability zones
- **Internet Gateway**: For public internet access
- **Security Groups**: Web and monitoring access controls
- **EC2 Instances**: Monitoring and application servers
- **Key Pair**: SSH access to instances

## 📋 Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Terraform installed** (>= 1.0)
3. **SSH key pair generated** for EC2 access

## 🚀 Quick Start

### 1. Generate SSH Key Pair
```bash
# Generate a new SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/smartcloudops-ai-key

# Get the public key content
cat ~/.ssh/smartcloudops-ai-key.pub
```

### 2. Configure Variables
```bash
# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Important variables to update:**
- `public_key`: Your SSH public key content
- `allowed_cidr_blocks`: Your IP address for security
- `grafana_admin_password`: Secure password for Grafana
- `openai_api_key`: Your OpenAI API key (for Phase 5)

### 3. Deploy Infrastructure
```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply
```

### 4. Access Your Infrastructure
After deployment, Terraform will output connection information:
```bash
# SSH to monitoring server
ssh -i ~/.ssh/smartcloudops-ai-key.pem ec2-user@<monitoring-ip>

# SSH to application server  
ssh -i ~/.ssh/smartcloudops-ai-key.pem ec2-user@<application-ip>

# Access services
# Prometheus: http://<monitoring-ip>:9090
# Grafana: http://<monitoring-ip>:3001 (admin/admin)
# Flask App: http://<application-ip>:3000
```

## 🔧 Configuration Files

- `main.tf`: Main infrastructure configuration
- `variables.tf`: Input variables
- `outputs.tf`: Output values
- `terraform.tfvars.example`: Example variables
- `scripts/`: Instance setup scripts
- `configs/`: Service configuration files

## 🛡️ Security Features

- **Encrypted EBS volumes** for all instances
- **Security groups** with minimal required access
- **SSH key-based authentication** only
- **Configurable CIDR blocks** for access control

## 🔄 Remote State (Optional)

For team collaboration, uncomment the S3 backend in `main.tf`:

```hcl
backend "s3" {
  bucket         = "smartcloudops-terraform-state"
  key            = "infrastructure/terraform.tfstate"
  region         = "us-west-2"
  encrypt        = true
  dynamodb_table = "terraform-state-lock"
}
```

Create the S3 bucket and DynamoDB table first:
```bash
# Create state bucket
aws s3 mb s3://smartcloudops-terraform-state

# Create lock table
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
```

## 🧹 Cleanup

To destroy the infrastructure:
```bash
terraform destroy
```

## 📊 Monitoring Setup

The infrastructure automatically sets up:
- **Prometheus** on the monitoring server (port 9090)
- **Grafana** on the monitoring server (port 3001)
- **Node Exporter** on both servers (port 9100)
- **Flask application** with metrics endpoint (port 3000)

## 🔍 Troubleshooting

### Common Issues

1. **Permission denied on SSH**
   ```bash
   chmod 400 ~/.ssh/smartcloudops-ai-key.pem
   ```

2. **Cannot access services**
   - Check security group rules
   - Verify instance is running
   - Check if services started correctly

3. **Terraform errors**
   - Verify AWS credentials: `aws sts get-caller-identity`
   - Check region availability
   - Ensure unique resource names

### Logs and Debugging

```bash
# Check instance logs
ssh -i ~/.ssh/smartcloudops-ai-key.pem ec2-user@<ip>
sudo journalctl -u smartcloudops-app
sudo tail -f /var/log/cloud-init-output.log
```

## 🔜 Next Steps

After Phase 1.1 completion:
1. **Phase 1.2**: Configure monitoring dashboards
2. **Phase 2**: Deploy Flask ChatOps application
3. **Phase 3**: Implement ML anomaly detection

## 📚 References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Grafana Documentation](https://grafana.com/docs/)