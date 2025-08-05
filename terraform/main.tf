# Smart CloudOps AI - Terraform Infrastructure Configuration
# Phase 1.1: AWS Infrastructure Setup

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Optional: Uncomment and configure for remote state
  # backend "s3" {
  #   bucket         = "smartcloudops-terraform-state"
  #   key            = "infrastructure/terraform.tfstate"
  #   region         = "us-west-2"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "SmartCloudOpsAI"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.project_owner
    }
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Data source for latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# VPC Configuration
resource "aws_vpc" "smartcloudops_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "smartcloudops_igw" {
  vpc_id = aws_vpc.smartcloudops_vpc.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = aws_vpc.smartcloudops_vpc.id
  cidr_block              = var.public_subnet_1_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.project_name}-public-subnet-1"
    Type = "Public"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.smartcloudops_vpc.id
  cidr_block              = var.public_subnet_2_cidr
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.project_name}-public-subnet-2"
    Type = "Public"
  }
}

# Route Table for Public Subnets
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.smartcloudops_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.smartcloudops_igw.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public_rta_1" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_rta_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_rt.id
}

# Security Group for Web Services
resource "aws_security_group" "web_sg" {
  name        = "${var.project_name}-web-sg"
  description = "Security group for web services"
  vpc_id      = aws_vpc.smartcloudops_vpc.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "SSH access"
  }

  # HTTP access (restricted to allowed CIDRs)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTP access"
  }

  # HTTPS access (restricted to allowed CIDRs)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTPS access"
  }

  # Flask application
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "Flask application"
  }

  # Outbound HTTP traffic
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP outbound"
  }

  # Outbound HTTPS traffic
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  # DNS outbound
  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "DNS outbound"
  }

  tags = {
    Name = "${var.project_name}-web-sg"
  }
}

# Security Group for Monitoring Services
resource "aws_security_group" "monitoring_sg" {
  name        = "${var.project_name}-monitoring-sg"
  description = "Security group for monitoring services"
  vpc_id      = aws_vpc.smartcloudops_vpc.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "SSH access"
  }

  # Prometheus
  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "Prometheus web UI"
  }

  # Node Exporter
  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Node Exporter metrics"
  }

  # Grafana
  ingress {
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "Grafana web UI"
  }

  # Outbound HTTP traffic
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP outbound"
  }

  # Outbound HTTPS traffic
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  # DNS outbound
  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "DNS outbound"
  }

  tags = {
    Name = "${var.project_name}-monitoring-sg"
  }
}

# Key Pair for EC2 instances
resource "aws_key_pair" "smartcloudops_key" {
  key_name   = "${var.project_name}-key"
  public_key = var.public_key

  tags = {
    Name = "${var.project_name}-key"
  }
}

# EC2 Instance for Monitoring
resource "aws_instance" "ec2_monitoring" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.monitoring_instance_type
  key_name                    = aws_key_pair.smartcloudops_key.key_name
  vpc_security_group_ids      = [aws_security_group.monitoring_sg.id]
  subnet_id                   = aws_subnet.public_subnet_1.id
  disable_api_termination     = false
  monitoring                  = true
  ebs_optimized               = true
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = false

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = var.monitoring_volume_size
    encrypted   = true
  }

  user_data = base64encode(file("${path.module}/scripts/monitoring_setup.sh"))

  tags = {
    Name = "${var.project_name}-monitoring"
    Role = "Monitoring"
  }
}

# EC2 Instance for Application
resource "aws_instance" "ec2_application" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.application_instance_type
  key_name                    = aws_key_pair.smartcloudops_key.key_name
  vpc_security_group_ids      = [aws_security_group.web_sg.id, aws_security_group.monitoring_sg.id]
  subnet_id                   = aws_subnet.public_subnet_2.id
  disable_api_termination     = false
  monitoring                  = true
  ebs_optimized               = true
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = false

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = var.application_volume_size
    encrypted   = true
  }

  user_data = base64encode(file("${path.module}/scripts/application_setup.sh"))

  tags = {
    Name = "${var.project_name}-application"
    Role = "Application"
  }
}