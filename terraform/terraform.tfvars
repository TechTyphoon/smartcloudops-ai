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

# SSH Key Configuration
public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDfcLojY9LqRTZhNvZJMSWpxu7ED/RrSOKZhGZ2+oQemdECdtKVhdJd+W/unbcbV2Cz9lMkafpUcE9qMCa4KznyqERT3GmKpO54QlIsfsvbC/74509woIUuVzbPuteOQ/6SXrGZSYVO1XDh8+mVm0zIa9dZUj3NCL3VSsPutB8z8WICnOoDajIU6SJvCeFqg44JFYmGMf92FJ3ReGpYs9raUXLjgei4AoxsUzuE7jod+CGl6pRAsBr8tD5/pEbpSfo5+qq73iLUdZE1T8rrVD+prYimwigs8MPikVSut9C4a23YTGtdQGZFcZlVDSrltDbMwAAAlOjYdkB9vamPxSbSagYcTRNz6UpeKey+HyVZiT+LRmUcDHj7U32zOCHXCS/85+OIkPrQB/zliw46ctmzU3lihKLDT3IRa33iNImoizG1dJOWEVTAbV3WJSUQN8QGz4zcAFF6pQODIk9vB5tBgUxnVdiRCqNk8+XmDxB1xnwVDwksuxssjB+t2/YBb7umzA0QzR0m0l2VhDq7aSMRSA5a9YvdH32mhQ3gEWZO4BDfivVY7SccBd2n6v0XnOu8KkEYRb0BFizyr/p4cXtCyltaEqkoaUfed8MSJkZgPn9+vn3drpDw5xFZ9RU/m5Ejc6LuzXNkBP6/6pMZKzpocT4OIGmTXNt5wZA4FQdPl1w== reddy@Devops"

# Monitoring Configuration
prometheus_retention_days = 15
grafana_admin_password    = "SmartCloudOps2024!"

# Application Configuration
flask_debug    = true
openai_api_key = "" # Leave empty for now, can be added later