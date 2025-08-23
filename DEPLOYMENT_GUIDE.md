# 🚀 Deployment Guide - SmartCloudOps AI

This guide provides comprehensive deployment instructions for SmartCloudOps AI across different environments and platforms.

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Environment Setup](#-environment-setup)
- [Docker Deployment](#-docker-deployment)
- [Kubernetes Deployment](#-kubernetes-deployment)
- [Terraform Infrastructure](#-terraform-infrastructure)
- [Production Deployment](#-production-deployment)
- [Monitoring Setup](#-monitoring-setup)
- [Troubleshooting](#-troubleshooting)

---

## 🔧 Prerequisites

### System Requirements
- **CPU**: 2+ cores (4+ recommended for production)
- **RAM**: 4GB minimum (8GB+ recommended for production)
- **Storage**: 20GB+ available disk space
- **Network**: Stable internet connection for dependencies

### Software Requirements
- **Docker**: v20.10+
- **Docker Compose**: v2.0+
- **Python**: 3.8+ (for development)
- **Git**: Latest version
- **kubectl**: v1.24+ (for Kubernetes deployment)
- **Terraform**: v1.0+ (for infrastructure deployment)

### Cloud Requirements (Production)
- **AWS Account** with appropriate permissions
- **ECR Repository** for container images
- **RDS Instance** for PostgreSQL (optional)
- **ElastiCache** for Redis (optional)

---

## 🌍 Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/TechTyphoon/smartcloudops-ai.git
cd smartcloudops-ai
```

### 2. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit configuration
nano .env
```

### 3. Key Environment Variables
```bash
# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret_key
SECRET_KEY=your_flask_secret_key

# AI/ML Configuration
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Monitoring Configuration
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
```

---

## 🐳 Docker Deployment

### Quick Start (Development)
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f smartcloudops-main
```

### Production Deployment
```bash
# Deploy production stack
./scripts/deployment/deploy_production_stack.sh

# Deploy with custom configuration
./scripts/deployment/deploy_production_stack.sh --env production

# Deploy with blue-green strategy
./scripts/deployment/deploy_production_stack.sh --strategy blue-green
```

### Service Verification
```bash
# Health check
curl http://localhost:5000/health

# Verify all services
python scripts/testing/health_check.py

# Check service status
docker-compose ps
```

### Service Management
```bash
# Stop services
docker-compose down

# Restart specific service
docker-compose restart smartcloudops-main

# Update and restart
docker-compose pull && docker-compose up -d

# View service logs
docker-compose logs -f [service_name]
```

---

## ☸️ Kubernetes Deployment

### Prerequisites
```bash
# Verify kubectl access
kubectl cluster-info

# Create namespace
kubectl create namespace smartcloudops

# Set namespace as default
kubectl config set-context --current --namespace=smartcloudops
```

### Deploy to Kubernetes
```bash
# Deploy complete stack
./scripts/deployment/deploy_k8s_stack.sh

# Deploy with custom namespace
./scripts/deployment/deploy_k8s_stack.sh --namespace smartcloudops

# Deploy specific components
kubectl apply -f k8s/01-database.yaml
kubectl apply -f k8s/02-application.yaml
kubectl apply -f k8s/03-nginx.yaml
kubectl apply -f k8s/04-prometheus.yaml
kubectl apply -f k8s/05-grafana.yaml
```

### Kubernetes Verification
```bash
# Check pod status
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress

# View pod logs
kubectl logs -f deployment/smartcloudops-main

# Port forward for local access
kubectl port-forward service/smartcloudops-main 5000:5000
```

### Kubernetes Scaling
```bash
# Scale application
kubectl scale deployment smartcloudops-main --replicas=3

# Auto-scaling configuration
kubectl autoscale deployment smartcloudops-main --min=2 --max=10 --cpu-percent=80

# Check scaling status
kubectl get hpa
```

---

## 🏗️ Terraform Infrastructure

### Prerequisites
```bash
# Install Terraform
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs)"
sudo apt-get update && sudo apt-get install terraform

# Configure AWS credentials
aws configure
```

### Infrastructure Deployment
```bash
# Navigate to Terraform directory
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file=terraform.tfvars

# Apply infrastructure
terraform apply -var-file=terraform.tfvars

# Verify deployment
terraform show
```

### Infrastructure Components
- **VPC**: Custom VPC with public and private subnets
- **EC2 Instances**: Application and monitoring servers
- **RDS**: PostgreSQL database (optional)
- **ElastiCache**: Redis cache (optional)
- **ALB**: Application Load Balancer
- **Security Groups**: Network security rules

### Infrastructure Management
```bash
# Update infrastructure
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars

# Destroy infrastructure
terraform destroy -var-file=terraform.tfvars

# Output values
terraform output
```

---

## 🏭 Production Deployment

### Pre-Deployment Checklist
- [ ] **Environment Variables**: All required variables configured
- [ ] **Dependencies**: All services and dependencies available
- [ ] **Security**: Security scans passed
- [ ] **Testing**: All tests passing
- [ ] **Backup**: Database and configuration backed up
- [ ] **Monitoring**: Monitoring systems ready

### Production Deployment Steps

#### 1. Prepare Environment
```bash
# Set production environment
export ENVIRONMENT=production

# Verify configuration
python scripts/testing/verify_setup.py --production

# Run pre-deployment checks
./scripts/deployment/deploy_production_stack.sh --validate
```

#### 2. Deploy Application
```bash
# Deploy with production configuration
./scripts/deployment/deploy_production_stack.sh --env production

# Verify deployment
python scripts/testing/health_check.py --production

# Check all services
python scripts/testing/verify_setup.py --post-deployment
```

#### 3. Configure Monitoring
```bash
# Deploy monitoring stack
./scripts/deployment/deploy_monitoring_server.sh

# Configure dashboards
python scripts/monitoring/continuous_health_monitor.py --configure-alerts

# Start monitoring
python scripts/monitoring/continuous_health_monitor.py --start
```

#### 4. Post-Deployment Verification
```bash
# Health checks
curl https://your-domain.com/health

# API tests
python scripts/testing/health_check.py --api-tests

# Performance tests
python scripts/testing/health_check.py --performance

# Security verification
python scripts/testing/verify_setup.py --security
```

---

## 📊 Monitoring Setup

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'smartcloudops'
    static_configs:
      - targets: ['smartcloudops-main:5000']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Grafana Dashboards
```bash
# Import dashboards
./scripts/monitoring/upload_dashboards.sh

# Configure data sources
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{"name":"Prometheus","type":"prometheus","url":"http://prometheus:9090"}'
```

### Monitoring Scripts
```bash
# Start continuous monitoring
python scripts/monitoring/continuous_health_monitor.py

# Monitor specific services
python scripts/monitoring/continuous_health_monitor.py --services app,database,redis

# Real-time system monitoring
python scripts/monitoring/real_system_monitor.py

# Daily status reports
./scripts/monitoring/daily_status.sh
```

### Alerting Configuration
```yaml
# alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        title: 'SmartCloudOps Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check service logs
docker-compose logs smartcloudops-main

# Verify environment variables
python scripts/testing/verify_setup.py --env-check

# Check dependencies
python scripts/testing/health_check.py --dependencies
```

#### 2. Database Connection Issues
```bash
# Test database connection
python scripts/testing/health_check.py --database

# Check database status
docker-compose exec postgres pg_isready

# Verify database configuration
python scripts/testing/verify_setup.py --database-config
```

#### 3. Monitoring Issues
```bash
# Check Prometheus status
curl http://localhost:9090/-/healthy

# Check Grafana status
curl http://localhost:3000/api/health

# Verify monitoring configuration
python scripts/testing/verify_setup.py --monitoring
```

#### 4. Performance Issues
```bash
# Check system resources
python scripts/monitoring/real_system_monitor.py

# Analyze application metrics
curl http://localhost:5000/metrics

# Check for bottlenecks
python scripts/testing/health_check.py --performance
```

### Debug Commands
```bash
# Enable debug mode
export FLASK_DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug output
python scripts/testing/health_check.py --debug

# Check configuration
python scripts/testing/verify_setup.py --verbose

# Monitor logs in real-time
docker-compose logs -f --tail=100
```

### Recovery Procedures

#### 1. Service Recovery
```bash
# Restart failed service
docker-compose restart smartcloudops-main

# Rebuild and restart
docker-compose build --no-cache smartcloudops-main
docker-compose up -d smartcloudops-main
```

#### 2. Database Recovery
```bash
# Backup database
docker-compose exec postgres pg_dump -U cloudops cloudops > backup.sql

# Restore database
docker-compose exec -T postgres psql -U cloudops cloudops < backup.sql
```

#### 3. Configuration Recovery
```bash
# Restore configuration
cp env.example .env
# Edit .env with correct values

# Restart services
docker-compose down
docker-compose up -d
```

---

## 📚 Additional Resources

### Documentation
- [Installation Guide](INSTALLATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Security Guide](SECURITY.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

### Scripts Reference
- [Scripts Documentation](scripts/README.md)
- [Deployment Scripts](scripts/deployment/)
- [Monitoring Scripts](scripts/monitoring/)
- [Testing Scripts](scripts/testing/)

### Support
- **Documentation**: Check comprehensive docs
- **Issues**: [GitHub Issues](https://github.com/TechTyphoon/smartcloudops-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TechTyphoon/smartcloudops-ai/discussions)
- **Enterprise Support**: enterprise@smartcloudops.ai

---

**SmartCloudOps AI v3.3.0** - Deployment Guide
