# Smart CloudOps AI - Terraform Variables
# Configuration for AWS deployment

# General Configuration
project_name  = "smartcloudops-ai"
environment   = "dev"
project_owner = "reddy"

# AWS Configuration
aws_region = "us-west-2"

# Network Configuration
vpc_cidr             = "10.0.0.0/16"
public_subnet_1_cidr = "10.0.1.0/24"
public_subnet_2_cidr = "10.0.2.0/24"
allowed_cidr_blocks  = ["157.50.160.73/32"] # Restrict to user's IP for secure access

# EC2 Configuration
monitoring_instance_type  = "t3.medium"
application_instance_type = "t3.small"
monitoring_volume_size    = 20
application_volume_size   = 10

# SSH Key Configuration - Use environment variable for security
public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."

# Monitoring Configuration
prometheus_retention_days = 15
grafana_admin_password    = "admin123"

# Application Configuration
flask_debug    = true
openai_api_key = "sk-demo-key-for-testing"