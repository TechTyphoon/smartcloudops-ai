# 🚀 Getting Started with SmartCloudOps AI

Welcome to SmartCloudOps AI! This guide will help you get up and running quickly with our enterprise-grade AI-powered CloudOps platform.

## 📋 **Prerequisites**

Before you begin, ensure you have the following installed:

### 🔧 **Required Software**
- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- **Python**: Version 3.8+ ([Install Python](https://python.org/downloads/))
- **Git**: Latest version ([Install Git](https://git-scm.com/downloads))

### 💻 **System Requirements**
- **RAM**: Minimum 4GB, Recommended 8GB+
- **CPU**: 2+ cores (4+ cores recommended for ML workloads)
- **Disk**: 10GB+ free space
- **Network**: Internet connection for container images

### 🔍 **Verification**
Verify your installation:
```bash
docker --version          # Should show 20.10+
docker-compose --version  # Should show 2.0+
python3 --version         # Should show 3.8+
git --version            # Should show recent version
```

---

## 🏃‍♂️ **Quick Start (5 Minutes)**

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/TechTyphoon/smartcloudops-ai.git
cd smartcloudops-ai
```

### 2️⃣ **Deploy the Stack**
```bash
# Deploy complete 5-container production stack
docker-compose -f docker-compose.tier2.yml up -d

# Wait for all containers to be healthy (30-60 seconds)
docker-compose -f docker-compose.tier2.yml ps
```

### 3️⃣ **Verify Deployment**
```bash
# Check all containers are running
docker ps

# Expected output: 5 running containers
# - smartcloudops-app (Flask application)
# - prometheus (Metrics collection)
# - grafana (Dashboards)
# - node-exporter (System metrics)
# - redis (Caching)
```

### 4️⃣ **Access Services**
Open your browser and navigate to:
- **🏠 Main Application**: http://localhost:5000
- **📊 Grafana Dashboards**: http://localhost:3000 (admin/admin)
- **📈 Prometheus Metrics**: http://localhost:9090
- **📚 API Documentation**: http://localhost:5000/docs

### 5️⃣ **Run Health Check**
```bash
# Quick health verification
curl http://localhost:5000/health

# Expected response: {"status": "healthy", "timestamp": "..."}
```

🎉 **Congratulations!** SmartCloudOps AI is now running on your system.

---

## 🔧 **Detailed Setup Options**

### 🐳 **Option 1: Docker Compose (Recommended)**

#### **Production Stack (5 Containers)**
```bash
# Full production environment
docker-compose -f docker-compose.tier2.yml up -d

# View logs
docker-compose -f docker-compose.tier2.yml logs -f

# Scale specific services
docker-compose -f docker-compose.tier2.yml up -d --scale app=2
```

#### **Development Stack (Minimal)**
```bash
# Lightweight development environment
docker-compose up -d

# Includes: Flask app + Redis only
```

### 🐍 **Option 2: Python Virtual Environment**

```bash
# Create virtual environment
python3 -m venv smartcloudops_env
source smartcloudops_env/bin/activate  # Windows: smartcloudops_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export FLASK_PORT=5000
export REDIS_URL=redis://localhost:6379

# Start Redis (required)
docker run -d -p 6379:6379 redis:alpine

# Run the application
python app.py
```

### ☸️ **Option 3: Kubernetes**

```bash
# Deploy to Kubernetes cluster
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n smartcloudops

# Access via port-forward
kubectl port-forward svc/smartcloudops-app 5000:5000 -n smartcloudops
```

---

## 🎯 **First Steps After Installation**

### 1️⃣ **Verify System Health**
```bash
# Run comprehensive health check
python scripts/comprehensive_audit.py

# Expected output: Grade A security, all systems healthy
```

### 2️⃣ **Explore the Dashboard**
1. Visit **Grafana** at http://localhost:3000
2. Login with `admin` / `admin`
3. Navigate to **SmartCloudOps AI** dashboards
4. Explore system metrics and ML predictions

### 3️⃣ **Test API Endpoints**
```bash
# System status
curl http://localhost:5000/api/status

# ML prediction (anomaly detection)
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"cpu_usage": 85, "memory_usage": 78, "disk_usage": 45}'

# ChatOps context
curl http://localhost:5000/chatops/context
```

### 4️⃣ **Morning Health Check**
```bash
# Daily system validation
./scripts/morning_check.sh

# This checks:
# - Container health
# - API responsiveness  
# - Security posture
# - Performance metrics
```

---

## 🛠️ **Configuration**

### 📝 **Environment Variables**

Create a `.env` file for custom configuration:

```bash
# Core Application
FLASK_ENV=production
FLASK_PORT=5000
FLASK_DEBUG=false

# Database & Cache
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://user:pass@localhost:5432/smartcloudops

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
METRICS_RETENTION=15d

# Security
SECURITY_AUDIT_ENABLED=true
SECURITY_COMPLIANCE_LEVEL=80
ENABLE_RATE_LIMITING=true

# ML Models
ML_MODEL_PATH=/app/models
ML_INFERENCE_TIMEOUT=30
ANOMALY_THRESHOLD=0.8

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### ⚙️ **Advanced Configuration**

#### **Docker Compose Overrides**
Create `docker-compose.override.yml`:
```yaml
version: '3.8'
services:
  app:
    environment:
      - FLASK_DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./logs:/app/logs
  
  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your_secure_password
```

#### **Kubernetes Configuration**
Update `k8s/configmap.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: smartcloudops-config
data:
  FLASK_ENV: "production"
  SECURITY_COMPLIANCE_LEVEL: "90"
  ML_INFERENCE_TIMEOUT: "15"
```

---

## 🧪 **Testing Your Installation**

### ✅ **Automated Tests**
```bash
# Run complete test suite
python scripts/beta_testing.py

# Security audit
python scripts/security_audit.py

# Performance benchmarks
python scripts/performance_test.py
```

### 🔍 **Manual Verification**

#### **1. Container Health**
```bash
# All containers should be healthy
docker ps --format "table {{.Names}}\t{{.Status}}"

# Expected output:
# smartcloudops-app    Up 5 minutes (healthy)
# prometheus          Up 5 minutes (healthy)  
# grafana            Up 5 minutes (healthy)
# node-exporter      Up 5 minutes (healthy)
# redis              Up 5 minutes (healthy)
```

#### **2. API Functionality**
```bash
# Health endpoint
curl -s http://localhost:5000/health | jq

# Metrics endpoint
curl -s http://localhost:5000/metrics | head -20

# ML prediction
curl -s -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"cpu_usage": 75, "memory_usage": 68, "disk_usage": 35}' | jq
```

#### **3. Dashboard Access**
- **Grafana**: Login at http://localhost:3000 (admin/admin)
- **Prometheus**: Access at http://localhost:9090
- **Application**: Browse to http://localhost:5000

---

## 🚨 **Troubleshooting**

### ❓ **Common Issues**

#### **Port Already in Use**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :5000

# Stop conflicting service or change ports
docker-compose -f docker-compose.tier2.yml down
```

#### **Containers Not Starting**
```bash
# Check container logs
docker-compose -f docker-compose.tier2.yml logs app

# Common causes:
# - Insufficient memory (need 4GB+)
# - Port conflicts
# - Docker daemon not running
```

#### **Permission Errors**
```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER ./logs ./data
```

### 🔧 **Advanced Troubleshooting**

#### **Performance Issues**
```bash
# Check system resources
docker stats

# Monitor application performance
curl http://localhost:5000/api/performance

# Review logs for bottlenecks
docker-compose logs app | grep -i "slow\|timeout\|error"
```

#### **Network Issues**
```bash
# Test container networking
docker network ls
docker network inspect smartcloudops_default

# Test connectivity between containers
docker exec smartcloudops-app ping prometheus
```

---

## 🎓 **Next Steps**

### 📚 **Learn More**
- **[Architecture Overview](ARCHITECTURE.md)** - Understand system design
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Security Guide](../docs/SECURITY_AUDIT_REPORT_ENHANCED.md)** - Security best practices
- **[Monitoring Guide](MONITORING_GUIDE.md)** - Dashboard setup and alerts

### 🛠️ **Advanced Usage**
- **[Cloud Deployment](CLOUD_DEPLOYMENT.md)** - AWS/Azure/GCP setup
- **[Kubernetes Guide](KUBERNETES_GUIDE.md)** - Production K8s deployment
- **[Custom Integrations](INTEGRATIONS.md)** - Extend with third-party tools
- **[Performance Tuning](PERFORMANCE_TUNING.md)** - Optimization techniques

### 🤝 **Get Involved**
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute
- **[Issues](https://github.com/TechTyphoon/smartcloudops-ai/issues)** - Report bugs or request features
- **[Discussions](https://github.com/TechTyphoon/smartcloudops-ai/discussions)** - Ask questions and share ideas

---

## 🆘 **Getting Help**

If you encounter issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Review troubleshooting**: Search this guide for your issue
3. **Search issues**: [GitHub Issues](https://github.com/TechTyphoon/smartcloudops-ai/issues)
4. **Ask the community**: [GitHub Discussions](https://github.com/TechTyphoon/smartcloudops-ai/discussions)
5. **Contact support**: enterprise@smartcloudops.ai

---

<div align="center">

**🚀 Ready to revolutionize your cloud operations? Let's get started! 🚀**

[Back to Main README](../README.md) | [Next: Architecture Overview](ARCHITECTURE.md)

</div>
