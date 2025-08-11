# Smart CloudOps AI - Terraform Variables
# Phase 1.1: Infrastructure Variables

# General Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "smartcloudops-ai"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_owner" {
  description = "Owner of the project"
  type        = string
  default     = "CloudOps-Team"
}

# AWS Configuration
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2" # Changed to us-west-2 to match current deployment
}

variable "account_id" {
  description = "AWS Account ID used for scoping IAM resources"
  type        = string
  default     = "*"
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_1_cidr" {
  description = "CIDR block for public subnet 1"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_2_cidr" {
  description = "CIDR block for public subnet 2"
  type        = string
  default     = "10.0.2.0/24"
}

# Private subnets for ECS/RDS
variable "private_subnet_1_cidr" {
  description = "CIDR block for private subnet 1"
  type        = string
  default     = "10.0.3.0/24"
}

variable "private_subnet_2_cidr" {
  description = "CIDR block for private subnet 2"
  type        = string
  default     = "10.0.4.0/24"
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the infrastructure"
  type        = list(string)
  # Allow access from anywhere for development; restrict in production
  default = ["0.0.0.0/0"]
}

# EC2 Configuration
variable "monitoring_instance_type" {
  description = "Instance type for monitoring server"
  type        = string
  default     = "t3.medium"
}

variable "application_instance_type" {
  description = "Instance type for application server"
  type        = string
  default     = "t3.small"
}

variable "monitoring_volume_size" {
  description = "Root volume size for monitoring instance (GB)"
  type        = number
  default     = 20
}

variable "application_volume_size" {
  description = "Root volume size for application instance (GB)"
  type        = number
  default     = 10
}

variable "public_key" {
  description = "Public key for EC2 key pair"
  type        = string
  default     = ""
}

# Monitoring Configuration
variable "prometheus_retention_days" {
  description = "Days to retain Prometheus data"
  type        = number
  default     = 15
}

variable "grafana_admin_password" {
  description = "Admin password for Grafana"
  type        = string
  default     = "admin"
  sensitive   = true
}

# Application Configuration
variable "flask_debug" {
  description = "Enable Flask debug mode"
  type        = bool
  default     = true
}

variable "openai_api_key" {
  description = "OpenAI API key for ChatOps"
  type        = string
  default     = ""
  sensitive   = true
}

# Domain for ACM/ALB
variable "domain_name" {
  description = "Fully qualified domain name for the application (e.g. app.example.com)"
  type        = string
  default     = ""
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID for the domain"
  type        = string
  default     = ""
}

# Database settings
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "rds_backup_retention_days" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
}

variable "db_username" {
  description = "Database admin username"
  type        = string
  default     = "cloudops"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "cloudops"
}