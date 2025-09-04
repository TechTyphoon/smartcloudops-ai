# Terraform Backend Configuration
# S3 backend with DynamoDB locking for team collaboration

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # S3 Backend Configuration
  backend "s3" {
    # These values will be provided via backend configuration
    # bucket         = "smartcloudops-terraform-state"
    # key            = "terraform.tfstate"
    # region         = "us-west-2"
    # dynamodb_table = "terraform-locks"
    # encrypt        = true
    # kms_key_id     = "alias/terraform-state-key"
  }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = var.project_owner
    }
  }
}

# Provider for ACM certificates (us-east-1 required)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
