# 🔒 SmartCloudOps AI Security Deployment Guide

## Overview
This guide covers the critical security fixes implemented in SmartCloudOps AI to address hardcoded secrets, improve secrets management, and secure the infrastructure.

## 🚨 Critical Security Issues Fixed

### 1. Hardcoded Secrets Removal
- ✅ Removed hardcoded passwords (`admin123`, `password123`, etc.)
- ✅ Replaced with environment variables and secrets management
- ✅ Updated all application files to use secure configuration

### 2. Secrets Management Implementation
- ✅ Created `app/security/secrets_manager.py` for centralized secrets handling
- ✅ AWS Secrets Manager integration with fallback to environment variables
- ✅ Secure credential retrieval for database, Redis, and API keys

### 3. Environment Configuration
- ✅ Updated `.gitignore` to prevent `.env` file commits
- ✅ Created comprehensive `env.example` template
- ✅ Environment variable validation and security checks

### 4. Terraform Remote State
- ✅ Configured S3 backend with DynamoDB locking
- ✅ Added KMS encryption for state files
- ✅ Created `backend.hcl.template` for easy configuration

### 5. Kubernetes Cleanup
- ✅ Removed duplicate configuration files
- ✅ Standardized secret management in K8s manifests
- ✅ Environment variable substitution for all secrets

## 🛠️ Deployment Steps

### Step 1: Environment Setup

1. **Copy environment template:**
   ```bash
   cp env.example .env
   ```

2. **Configure your secrets in `.env`:**
   ```bash
   # Required secrets
   SECRET_KEY=your-super-secret-flask-key-change-in-production
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
   DATABASE_URL=postgresql://smartcloudops:your_postgres_password@localhost:5432/smartcloudops
   POSTGRES_PASSWORD=your_postgres_password_here
   REDIS_PASSWORD=your_redis_password_here
   
   # Optional AI API keys
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Admin user password
   DEFAULT_ADMIN_PASSWORD=your_secure_admin_password
   ```

### Step 2: AWS Secrets Manager Setup (Production)

1. **Create secrets in AWS Secrets Manager:**
   ```bash
   # Database credentials
   aws secretsmanager create-secret \
     --name "smartcloudops/database" \
     --description "Database credentials for SmartCloudOps AI" \
     --secret-string '{"host":"localhost","port":"5432","database":"smartcloudops","username":"smartcloudops","password":"your_secure_password"}'
   
   # Redis credentials
   aws secretsmanager create-secret \
     --name "smartcloudops/redis" \
     --description "Redis credentials for SmartCloudOps AI" \
     --secret-string '{"host":"localhost","port":"6379","password":"your_redis_password","db":"0"}'
   
   # JWT secrets
   aws secretsmanager create-secret \
     --name "smartcloudops/jwt" \
     --description "JWT signing keys for SmartCloudOps AI" \
     --secret-string '{"jwt_secret_key":"your_jwt_secret","jwt_access_token_expires":"3600","jwt_refresh_token_expires":"2592000"}'
   ```

2. **Configure AWS credentials:**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-west-2
   ```

### Step 3: Terraform Remote State Setup

1. **Create S3 bucket and DynamoDB table:**
   ```bash
   # Create S3 bucket for Terraform state
   aws s3 mb s3://your-terraform-state-bucket-name
   
   # Enable versioning
   aws s3api put-bucket-versioning \
     --bucket your-terraform-state-bucket-name \
     --versioning-configuration Status=Enabled
   
   # Create DynamoDB table for state locking
   aws dynamodb create-table \
     --table-name terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
   ```

2. **Configure Terraform backend:**
   ```bash
   # Copy and edit the backend template
   cp terraform/backend.hcl.template terraform/backend.hcl
   
   # Edit backend.hcl with your values
   bucket         = "your-terraform-state-bucket-name"
   key            = "smartcloudops-ai/terraform.tfstate"
   region         = "us-west-2"
   encrypt        = true
   dynamodb_table = "terraform-locks"
   kms_key_id     = "arn:aws:kms:us-west-2:YOUR_ACCOUNT_ID:key/your-kms-key-id"
   ```

3. **Initialize Terraform with remote backend:**
   ```bash
   cd terraform
   terraform init -backend-config=backend.hcl
   ```

### Step 4: Kubernetes Deployment

1. **Set environment variables for K8s secrets:**
   ```bash
   # Base64 encode your secrets
   export POSTGRES_PASSWORD_BASE64=$(echo -n "your_postgres_password" | base64)
   export REDIS_PASSWORD_BASE64=$(echo -n "your_redis_password" | base64)
   export JWT_SECRET_KEY_BASE64=$(echo -n "your_jwt_secret_key" | base64)
   export GRAFANA_ADMIN_PASSWORD_BASE64=$(echo -n "your_grafana_password" | base64)
   export OPENAI_API_KEY_BASE64=$(echo -n "your_openai_api_key" | base64)
   export GEMINI_API_KEY_BASE64=$(echo -n "your_gemini_api_key" | base64)
   ```

2. **Deploy to Kubernetes:**
   ```bash
   # Create namespace
   kubectl apply -f k8s/namespace.yaml
   
   # Deploy secrets and applications
   kubectl apply -f k8s/postgresql.yaml
   kubectl apply -f k8s/redis.yaml
   kubectl apply -f k8s/app.yaml
   kubectl apply -f k8s/monitoring.yaml
   ```

### Step 5: Security Validation

1. **Run security validation script:**
   ```bash
   python3 scripts/security/validate_secrets.py
   ```

2. **Expected output:**
   ```
   ✅ All security checks passed!
   ✅ Environment is properly configured
   ✅ No hardcoded secrets found
   ```

## 🔧 Configuration Files Updated

### Application Files
- `app/config.py` - Updated to use secrets manager
- `app/auth_module.py` - Removed hardcoded admin password
- `app/database.py` - Environment variable for admin password
- `postgres-init/01-init.sql` - Environment variable substitution

### Infrastructure Files
- `terraform/main.tf` - Remote state configuration
- `terraform/backend.hcl.template` - Backend configuration template
- `k8s/*.yaml` - Environment variable substitution for secrets

### Security Files
- `app/security/secrets_manager.py` - Centralized secrets management
- `scripts/security/validate_secrets.py` - Security validation script
- `.gitignore` - Enhanced to prevent .env commits

## 🚨 Security Best Practices

### 1. Secrets Management
- ✅ Never commit secrets to version control
- ✅ Use AWS Secrets Manager or HashiCorp Vault in production
- ✅ Rotate secrets regularly
- ✅ Use least privilege access

### 2. Environment Variables
- ✅ Use strong, unique passwords
- ✅ Set different secrets for each environment
- ✅ Validate environment configuration on startup

### 3. Infrastructure Security
- ✅ Enable encryption at rest and in transit
- ✅ Use IAM roles and policies
- ✅ Implement network security groups
- ✅ Enable audit logging

### 4. Application Security
- ✅ Input validation and sanitization
- ✅ Rate limiting and DDoS protection
- ✅ Secure session management
- ✅ Regular security updates

## 🔍 Monitoring and Alerting

### Security Monitoring
- Monitor for failed authentication attempts
- Track secret access patterns
- Alert on suspicious activities
- Log all security events

### Infrastructure Monitoring
- Monitor Terraform state changes
- Track AWS resource modifications
- Alert on unauthorized access
- Monitor compliance status

## 📋 Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] AWS credentials set up
- [ ] S3 bucket and DynamoDB table created
- [ ] Terraform backend configured
- [ ] Kubernetes cluster ready

### Deployment
- [ ] Secrets created in AWS Secrets Manager
- [ ] Terraform infrastructure deployed
- [ ] Kubernetes applications deployed
- [ ] Security validation passed
- [ ] Monitoring configured

### Post-Deployment
- [ ] Admin password changed
- [ ] Default credentials updated
- [ ] Security monitoring active
- [ ] Backup procedures tested
- [ ] Documentation updated

## 🆘 Troubleshooting

### Common Issues

1. **Secrets not found:**
   - Check AWS credentials and permissions
   - Verify secret names in AWS Secrets Manager
   - Ensure environment variables are set

2. **Terraform backend issues:**
   - Verify S3 bucket exists and is accessible
   - Check DynamoDB table configuration
   - Ensure KMS key permissions

3. **Kubernetes secret issues:**
   - Verify base64 encoding of secrets
   - Check namespace and resource names
   - Validate YAML syntax

### Support
For security-related issues, contact the security team or create an issue in the repository with the `security` label.

---

**⚠️ IMPORTANT**: This guide covers critical security fixes. Always test in a staging environment before deploying to production.
