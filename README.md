# 🚀 SmartCloudOps AI - Enterprise AI-Powered Cloud Operations Platform

<div align="center">

![SmartCloudOps AI](https://img.shields.io/badge/SmartCloudOps-AI%20v3.3.0-blue?style=for-the-badge&logo=robot)
[![License](https://img.shields.io/github/license/TechTyphoon/smartcloudops-ai?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue?style=for-the-badge&logo=kubernetes)](https://kubernetes.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-orange?style=for-the-badge&logo=prometheus)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-orange?style=for-the-badge&logo=grafana)](https://grafana.com/)

**Enterprise-grade AI-powered CloudOps platform with real-time monitoring, ML-driven anomaly detection, and automated incident response.**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🏗️ Architecture](#️-architecture) • [🔧 API Reference](#-api-reference) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 Overview

SmartCloudOps AI is a production-ready, enterprise-grade platform that revolutionizes cloud operations through artificial intelligence and machine learning. Built with Flask, Prometheus, Grafana, and advanced ML models, it provides comprehensive infrastructure monitoring, predictive analytics, and automated incident response.

### ✨ Key Features
- **🤖 AI-Powered Anomaly Detection** - ML models with ~20ms inference times
- **📊 Real-time Monitoring** - Prometheus + Grafana observability stack
- **🔄 Automated Remediation** - Intelligent incident response and recovery
- **💬 ChatOps Integration** - Natural language operations interface
- **🛡️ Enterprise Security** - JWT authentication, role-based access control
- **☁️ Cloud-Native** - Docker, Kubernetes, and multi-cloud support
- **📈 Performance Analytics** - Custom metrics and predictive insights

---

## 🚀 Quick Start

### Frontend Decision
**⚠️ IMPORTANT: Frontend Integration Decision Required**

This repository currently provides a **REST API-only backend** for SmartCloudOps AI. You have two options:

1. **API-Only Approach** (Recommended for now):
   - Use the REST API endpoints directly
   - Integrate with existing monitoring dashboards (Grafana, etc.)
   - Build custom frontend later if needed
   - Remove CORS configurations if not planning frontend

2. **Frontend Integration** (Future enhancement):
   - Add React/Vue.js frontend
   - Implement ChatOps UI
   - Add real-time monitoring dashboard
   - Configure CORS properly

**Current Status**: API-only with monitoring integration via Grafana dashboards.

### Prerequisites
- **Docker & Docker Compose** (v20.10+)
- **Python 3.8+** (for development)
- **4GB+ RAM** (8GB recommended)

### 1. Clone & Deploy
```bash
git clone https://github.com/TechTyphoon/smartcloudops-ai.git
cd smartcloudops-ai

# Deploy complete production stack
docker-compose up -d
```

### 2. Access Services
- **🏠 Application**: http://localhost:5000
- **📊 Grafana**: http://localhost:13000 (admin/admin)
- **📈 Prometheus**: http://localhost:9090
- **🔧 API Docs**: http://localhost:5000/api/docs

### 3. Verify Deployment
```bash
# Health check
curl http://localhost:5000/health

# Expected: {"status": "healthy", "version": "3.3.0"}
```

🎉 **Ready!** Your SmartCloudOps AI platform is now running.

---

## 🏗️ Architecture

### System Components
```
┌─────────────────────────────────────────────────────────┐
│                 SmartCloudOps AI v3.3.0                │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐│
│  │ Flask App   │  │ Prometheus   │  │ Grafana         ││
│  │ Port: 5000  │  │ Port: 9090   │  │ Port: 13000     ││
│  │ AI/ML API   │  │ Metrics      │  │ Dashboards      ││
│  └─────────────┘  └──────────────┘  └─────────────────┘│
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐│
│  │ Node Export │  │ Redis Cache  │  │ PostgreSQL      ││
│  │ Port: 9100  │  │ Port: 6379   │  │ Port: 5434      ││
│  │ System Metrics│ │ Performance  │  │ Data Storage    ││
│  └─────────────┘  └──────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Backend**: Flask 3.1.1, Python 3.8+
- **Database**: PostgreSQL 17, Redis 7
- **Monitoring**: Prometheus, Grafana, Node Exporter
- **ML/AI**: Scikit-learn, OpenAI, Google Generative AI
- **Security**: JWT, bcrypt, role-based access control
- **Deployment**: Docker, Kubernetes, Terraform

---

## 🔧 API Reference

### Core Endpoints

#### Health & Status
```bash
GET /health                    # Application health check
GET /status                    # Detailed system status
GET /metrics                   # Prometheus metrics
```

#### Authentication
```bash
POST /auth/login              # User authentication
POST /auth/register           # User registration
GET  /auth/verify             # Token verification
```

#### AI & ML Services
```bash
POST /anomaly                 # ML anomaly detection
GET  /anomaly                 # Get anomaly history
POST /query                   # ChatOps AI queries
GET  /query                   # Query history
```

#### Monitoring & Remediation
```bash
GET  /remediation/actions     # List remediation actions
POST /remediation/trigger     # Trigger remediation
GET  /monitoring/metrics      # System metrics
```

### Example Usage

```bash
# Health check
curl http://localhost:5000/health

# Authenticate
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# AI Query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "What is the current system status?"}'
```

---

## 📁 Project Structure

```
smartcloudops-ai/
├── app/                      # Main Flask application
│   ├── api/                  # REST API endpoints
│   ├── auth/                 # Authentication modules
│   ├── chatops/              # ChatOps integration
│   ├── mlops/                # ML operations
│   ├── monitoring/           # Monitoring services
│   ├── remediation/          # Auto-remediation engine
│   ├── security/             # Security modules
│   └── main.py              # Application entry point
├── configs/                  # Configuration files
├── docs/                     # Documentation
├── k8s/                      # Kubernetes manifests
├── ml_models/                # ML model definitions
├── scripts/                  # Utility scripts
│   ├── deployment/           # Deployment scripts
│   ├── monitoring/           # Monitoring scripts
│   ├── testing/              # Testing scripts
│   ├── security/             # Security scripts
│   └── utils/                # Utility scripts
├── terraform/                # Infrastructure as Code
├── tests/                    # Test suite
├── docker-compose.yml        # Docker orchestration
├── Dockerfile               # Container definition
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

---

## 🔄 CI/CD Pipeline

### Active Workflows
- **🔄 main.yml** - Primary CI/CD pipeline with quality gates, testing, and deployment
- **🏗️ infrastructure.yml** - Infrastructure validation and Terraform operations
- **🔒 security.yml** - Security scanning and compliance checks
- **⚙️ reusable.yml** - Reusable workflow components

### Pipeline Stages
1. **Quality Gate** - Code quality, security scanning, change detection
2. **Testing** - Unit tests, integration tests, coverage reporting
3. **Build** - Docker image building and security scanning
4. **Infrastructure** - Terraform validation and planning
5. **Deployment** - Conditional deployment to staging/production

---

## 📖 Documentation

- **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions
- **[Usage Guide](USAGE.md)** - Comprehensive usage examples
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Security Guide](docs/SECURITY_HARDENING_GUIDE.md)** - Security best practices
- **[Contributing](CONTRIBUTING.md)** - Development guidelines
- **[Changelog](CHANGELOG.md)** - Version history and updates

---

## 🛠️ Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/TechTyphoon/smartcloudops-ai.git
cd smartcloudops-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your configuration

# Run development server
python app/main.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run local test suite
./scripts/testing/test-local.sh
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/

# Quick lint fix
./scripts/utils/quick-lint-fix.sh
```

---

## 🚀 Deployment

### Docker Deployment
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# With custom environment
docker-compose --env-file .env.production up -d

# Deploy complete stack
./scripts/deployment/deploy_complete_stack.sh
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n smartcloudops

# Deploy with scripts
./scripts/deployment/deploy_k8s_stack.sh
```

### Terraform Infrastructure
```bash
# Initialize Terraform
cd terraform
terraform init

# Deploy infrastructure
terraform plan
terraform apply
```

---

## 🔒 Security

- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Comprehensive request sanitization
- **Rate Limiting**: API protection against abuse
- **Audit Logging**: Complete action tracking
- **Security Scanning**: Automated vulnerability detection
- **Secret Management**: Secure credential handling

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Ensure security best practices

---

## 📊 Monitoring & Observability

### Metrics Available
- **System Metrics**: CPU, Memory, Disk, Network
- **Application Metrics**: Request rates, response times, error rates
- **Business Metrics**: User activity, feature usage
- **Custom Metrics**: ML model performance, remediation actions

### Dashboards
- **System Overview**: Real-time system health
- **Application Performance**: API performance and errors
- **ML Operations**: Model performance and predictions
- **Security**: Authentication and authorization events

### Health Monitoring
```bash
# Health check
python scripts/testing/health_check.py

# Continuous monitoring
python scripts/monitoring/continuous_health_monitor.py

# System monitoring
python scripts/monitoring/real_system_monitor.py
```

---

## 🆘 Support

### Getting Help
- **Documentation**: Check our comprehensive docs
- **Issues**: [GitHub Issues](https://github.com/TechTyphoon/smartcloudops-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TechTyphoon/smartcloudops-ai/discussions)
- **Enterprise Support**: enterprise@smartcloudops.ai

### Troubleshooting
- Check the [Troubleshooting Guide](docs/troubleshooting.md)
- Review application logs: `docker-compose logs smartcloudops-main`
- Verify service health: `curl http://localhost:5000/health`
- Run health checks: `python scripts/testing/health_check.py`

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Flask Community** - Web framework
- **Prometheus** - Monitoring and alerting
- **Grafana** - Visualization and dashboards
- **Scikit-learn** - Machine learning library
- **OpenAI** - AI capabilities

---

<div align="center">

**Made with ❤️ by the SmartCloudOps AI Team**

[![GitHub stars](https://img.shields.io/github/stars/TechTyphoon/smartcloudops-ai?style=social)](https://github.com/TechTyphoon/smartcloudops-ai/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/TechTyphoon/smartcloudops-ai?style=social)](https://github.com/TechTyphoon/smartcloudops-ai/network)
[![GitHub issues](https://img.shields.io/github/issues/TechTyphoon/smartcloudops-ai)](https://github.com/TechTyphoon/smartcloudops-ai/issues)

</div>
