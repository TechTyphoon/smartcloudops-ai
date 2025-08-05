# Smart CloudOps AI - Setup Requirements

## 🔑 Required GitHub Secrets

You must add these secrets to your GitHub repository:

### **AWS Credentials**
1. Go to your GitHub repository: `https://github.com/TechTyphoon/smartcloudops-ai`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AWS_ACCESS_KEY_ID` | `your_aws_access_key_id` | Your AWS Access Key |
| `AWS_SECRET_ACCESS_KEY` | `your_aws_secret_access_key` | Your AWS Secret Key |
| `AWS_REGION` | `ap-south-1` | Your AWS Region |

### **Optional Secrets (for Phase 2+)**
| Secret Name | Value | Description |
|-------------|-------|-------------|
| `OPENAI_API_KEY` | `your_openai_api_key` | OpenAI API Key for ChatOps |
| `GRAFANA_PASSWORD` | `your_secure_password` | Grafana Admin Password |

## 🛠️ Local Development Setup

### **1. Environment Variables**
Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env

# Edit with your values
nano .env
```

### **2. Python Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **3. AWS CLI Configuration**
```bash
# Configure AWS CLI
aws configure

# Verify access
aws sts get-caller-identity
```

### **4. SSH Key Pair (for EC2 access)**
```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/smartcloudops-ai-key

# Get public key for Terraform
cat ~/.ssh/smartcloudops-ai-key.pub
```

## 🚀 Deployment Prerequisites

### **Required Tools**
- **Terraform** >= 1.0
- **AWS CLI** configured
- **Python** 3.10+
- **Docker** (for containerization)
- **SSH Key Pair** (for EC2 access)

### **AWS Permissions**
Your AWS user/role needs these permissions:
- EC2: Create/manage instances, security groups, key pairs
- VPC: Create/manage VPCs, subnets, internet gateways
- IAM: Basic permissions for resource tagging
- CloudWatch: Create log groups and put metrics
- Systems Manager: Read parameters

## 🔍 Verification Steps

### **1. Test Local Setup**
```bash
# Run comprehensive tests
python3 test_github_workflows.py
```

### **2. Test Terraform**
```bash
cd terraform
terraform init
terraform validate
terraform plan
```

### **3. Test Docker Build**
```bash
docker build -t smartcloudops-ai .
```

## 🚨 Common Issues & Solutions

### **GitHub Actions Timeout**
- **Issue**: Workflows timing out during dependency installation
- **Solution**: Added `--no-cache-dir` and timeout settings

### **AWS Credentials Not Found**
- **Issue**: Terraform plan fails with credential errors
- **Solution**: Ensure GitHub secrets are properly configured

### **Python Import Errors**
- **Issue**: Module not found errors in CI/CD
- **Solution**: All dependencies are now in requirements.txt

### **Security Scan Failures**
- **Issue**: Checkov security violations
- **Solution**: All security issues have been fixed in the latest code

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Run local tests: `python3 test_github_workflows.py`
3. Verify all secrets are configured
4. Ensure AWS credentials have proper permissions 