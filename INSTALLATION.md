# 📦 Installation Guide - SmartCloudOps AI

Complete installation guide for SmartCloudOps AI, covering all deployment options and configurations.

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Quick Installation](#-quick-installation)
- [Detailed Installation Options](#-detailed-installation-options)
- [Configuration](#-configuration)
- [Verification](#-verification)
- [Troubleshooting](#-troubleshooting)

---

## 🔧 Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4GB | 8GB+ |
| **CPU** | 2 cores | 4+ cores |
| **Storage** | 10GB | 20GB+ |
| **OS** | Linux/macOS/Windows | Linux (Ubuntu 20.04+) |

### Required Software

#### 1. Docker & Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version          # Should show 20.10+
docker-compose --version  # Should show 2.0+
```

#### 2. Python (for development)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS
brew install python3

# Windows
# Download from https://python.org/downloads/

# Verify installation
python3 --version  # Should show 3.8+
```

#### 3. Git
```bash
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# Windows
# Download from https://git-scm.com/downloads

# Verify installation
git --version
```

---

## 🚀 Quick Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/TechTyphoon/smartcloudops-ai.git
cd smartcloudops-ai
```

### Step 2: Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit configuration (optional)
nano .env
```

### Step 3: Deploy with Docker
```bash
# Start all services
docker-compose up -d

# Verify deployment
docker-compose ps
```

### Step 4: Access Services
- **Application**: http://localhost:5000
- **Grafana**: http://localhost:13000 (admin/admin)
- **Prometheus**: http://localhost:9090

### Step 5: Verify Installation
```bash
# Health check
curl http://localhost:5000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

🎉 **Installation Complete!** Your SmartCloudOps AI platform is now running.

---

## 📦 Detailed Installation Options

### Option 1: Docker Compose (Recommended)

#### Production Stack
```bash
# Full production environment with all services
docker-compose up -d

# Services included:
# - smartcloudops-main (Flask application)
# - postgres (PostgreSQL database)
# - redis (Redis cache)
# - prometheus (Metrics collection)
# - grafana (Dashboards)
# - node-exporter (System metrics)
```

#### Development Stack
```bash
# Lightweight development environment
docker-compose -f docker-compose.dev.yml up -d

# Services included:
# - smartcloudops-main (Flask application)
# - redis (Redis cache)
```

#### Custom Configuration
```bash
# Create custom docker-compose override
cp docker-compose.yml docker-compose.override.yml

# Edit override file for custom settings
nano docker-compose.override.yml

# Start with custom configuration
docker-compose up -d
```

### Option 2: Python Virtual Environment

#### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv smartcloudops_env

# Activate environment
# Linux/macOS:
source smartcloudops_env/bin/activate
# Windows:
smartcloudops_env\Scripts\activate
```

#### Step 2: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

#### Step 3: Database Setup
```bash
# Start PostgreSQL (using Docker)
docker run -d \
  --name postgres-dev \
  -e POSTGRES_USER=cloudops \
  -e POSTGRES_PASSWORD=cloudops \
  -e POSTGRES_DB=cloudops \
  -p 5434:5432 \
  postgres:17-alpine

# Start Redis
docker run -d \
  --name redis-dev \
  -p 6379:6379 \
  redis:7-alpine
```

#### Step 4: Run Application
```bash
# Set environment variables
export FLASK_ENV=development
export FLASK_PORT=5000
export DATABASE_URL=postgresql://cloudops:cloudops@localhost:5434/cloudops
export REDIS_URL=redis://localhost:6379

# Run application
python app/main.py
```

### Option 3: Kubernetes Deployment

#### Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install minikube (for local testing)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

#### Deploy to Kubernetes
```bash
# Start minikube
minikube start

# Deploy application
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n smartcloudops

# Access application
kubectl port-forward svc/smartcloudops-app 5000:5000 -n smartcloudops
```

### Option 4: Cloud Deployment

#### AWS Deployment
```bash
# Deploy to AWS EC2
./scripts/deploy_to_aws.sh

# Or use Terraform
cd terraform
terraform init
terraform plan
terraform apply
```

#### Azure Deployment
```bash
# Deploy to Azure
./scripts/deploy_k8s_stack.sh

# Or use Azure CLI
az group create --name smartcloudops-rg --location eastus
az aks create --resource-group smartcloudops-rg --name smartcloudops-cluster
```

#### GCP Deployment
```bash
# Deploy to Google Cloud
gcloud container clusters create smartcloudops-cluster
kubectl apply -f k8s/
```

---

## ⚙️ Configuration

### Environment Variables

#### Core Configuration
```bash
# Application Settings
FLASK_ENV=production
FLASK_PORT=5000
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port

# Security Settings
JWT_SECRET_KEY=your-secret-key-here
AUTH_SECRET_KEY=your-auth-secret-key
SECURITY_AUDIT_ENABLED=true
SECURITY_COMPLIANCE_LEVEL=80

# API Keys
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
METRICS_RETENTION=15d

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
CORS_SUPPORTS_CREDENTIALS=true
```

#### Advanced Configuration
```bash
# ML Model Settings
ML_MODEL_PATH=/app/models
ML_INFERENCE_TIMEOUT=30
ANOMALY_THRESHOLD=0.8

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_STORAGE_URL=redis://redis:6379

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log

# Performance
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100
```

### Configuration Files

#### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  smartcloudops-main:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://cloudops:cloudops@postgres:5432/cloudops
    depends_on:
      - postgres
      - redis
```

#### Kubernetes Configuration
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: smartcloudops-config
data:
  FLASK_ENV: "production"
  SECURITY_COMPLIANCE_LEVEL: "90"
  ML_INFERENCE_TIMEOUT: "15"
```

#### Prometheus Configuration
```yaml
# configs/monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'smartcloudops'
    static_configs:
      - targets: ['smartcloudops-main:5000']
```

---

## ✅ Verification

### Health Checks

#### Application Health
```bash
# Basic health check
curl http://localhost:5000/health

# Detailed status
curl http://localhost:5000/status

# Metrics endpoint
curl http://localhost:5000/metrics
```

#### Container Health
```bash
# Check all containers
docker ps

# Check container logs
docker-compose logs smartcloudops-main

# Check resource usage
docker stats
```

#### Database Connectivity
```bash
# Test PostgreSQL connection
docker exec -it postgres-database psql -U cloudops -d cloudops -c "SELECT version();"

# Test Redis connection
docker exec -it redis-cache-server redis-cli ping
```

### Performance Tests

#### API Performance
```bash
# Load test
python scripts/load_testing.py

# Performance benchmark
python scripts/performance_test.py
```

#### ML Model Performance
```bash
# Test anomaly detection
curl -X POST http://localhost:5000/api/ml/anomalies \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_usage": 85.5,
    "memory_usage": 78.2,
    "disk_usage": 45.0
  }'
```

### Security Verification
```bash
# Security audit
python scripts/security_audit.py

# Vulnerability scan
docker run --rm -v $(pwd):/app owasp/zap2docker-stable zap-baseline.py -t http://localhost:5000
```

---

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
sudo netstat -tlnp | grep :5000

# Stop conflicting service
sudo systemctl stop conflicting-service

# Or change ports in docker-compose.yml
ports:
  - "5001:5000"  # Use port 5001 instead
```

#### Container Won't Start
```bash
# Check container logs
docker-compose logs smartcloudops-main

# Common causes:
# - Insufficient memory (need 4GB+)
# - Port conflicts
# - Missing environment variables
# - Database connection issues
```

#### Database Connection Issues
```bash
# Check database status
docker-compose logs postgres

# Reset database
docker-compose down
docker volume rm smartcloudops_postgres_data
docker-compose up -d
```

#### Permission Errors
```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER ./logs ./data
```

### Performance Issues

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Optimize container resources
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 1G
    reservations:
      memory: 512M
```

#### Slow Response Times
```bash
# Check application logs
docker-compose logs smartcloudops-main | grep -i "slow\|timeout"

# Optimize database queries
# Check Redis cache hit rate
docker exec -it redis-cache-server redis-cli info memory
```

### Network Issues

#### Container Communication
```bash
# Test network connectivity
docker network ls
docker network inspect smartcloudops_default

# Test inter-container communication
docker exec smartcloudops-main ping postgres
docker exec smartcloudops-main ping redis
```

#### External Connectivity
```bash
# Test external API access
docker exec smartcloudops-main curl -I https://api.openai.com

# Check DNS resolution
docker exec smartcloudops-main nslookup api.openai.com
```

### Log Analysis

#### Application Logs
```bash
# View real-time logs
docker-compose logs -f smartcloudops-main

# Search for errors
docker-compose logs smartcloudops-main | grep -i error

# Check specific time period
docker-compose logs --since="2025-01-27T10:00:00" smartcloudops-main
```

#### System Logs
```bash
# Check system resources
htop
df -h
free -h

# Check Docker daemon logs
sudo journalctl -u docker.service
```

---

## 📞 Getting Help

### Support Resources
- **📖 Documentation**: Check the [Getting Started Guide](docs/GETTING_STARTED.md)
- **🔧 Troubleshooting**: See [Troubleshooting Guide](docs/troubleshooting.md)
- **💬 Community**: [GitHub Discussions](https://github.com/TechTyphoon/smartcloudops-ai/discussions)
- **🐛 Issues**: [GitHub Issues](https://github.com/TechTyphoon/smartcloudops-ai/issues)
- **📧 Enterprise Support**: enterprise@smartcloudops.ai

### Diagnostic Information
When reporting issues, please include:
- **OS and version**
- **Docker version**
- **Python version** (if applicable)
- **Error messages and logs**
- **Steps to reproduce**
- **Expected vs actual behavior**

---

<div align="center">

**🚀 Ready to get started? Follow the Quick Installation guide above! 🚀**

[Back to Main README](../README.md) | [Next: Getting Started Guide](docs/GETTING_STARTED.md)

</div>
