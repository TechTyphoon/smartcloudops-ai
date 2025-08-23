# SmartCloudOps AI - Application Core

This directory contains the main Flask application for SmartCloudOps AI, an enterprise-grade AI-powered cloud operations platform.

## 🏗️ Architecture Overview

```
app/
├── 📁 api/                    # REST API endpoints
│   ├── ai.py                 # AI/ML API endpoints
│   ├── anomalies.py          # Anomaly detection API
│   ├── feedback.py           # User feedback API
│   ├── ml.py                 # Machine learning API
│   └── remediation.py        # Auto-remediation API
├── 📁 chatops/               # ChatOps integration
│   ├── ai_handler.py         # AI conversation handler
│   ├── gpt_handler.py        # GPT integration
│   └── utils.py              # ChatOps utilities
├── 📁 mlops/                 # ML Operations
│   ├── autonomous_ops.py     # Autonomous operations
│   ├── data_pipeline.py      # Data processing pipeline
│   ├── knowledge_base.py     # Knowledge management
│   ├── model_registry.py     # Model versioning
│   └── reinforcement_learning.py # RL components
├── 📁 monitoring/            # Monitoring services
│   └── metrics.py            # Custom metrics collection
├── 📁 remediation/           # Auto-remediation engine
│   ├── actions.py            # Remediation actions
│   ├── engine.py             # Remediation logic
│   ├── notifications.py      # Alert notifications
│   └── safety.py             # Safety controls
├── 📁 security/              # Security modules
│   ├── caching.py            # Security caching
│   ├── error_handling.py     # Error handling
│   ├── input_validation.py   # Input sanitization
│   └── rate_limiting.py      # Rate limiting
├── 📄 main.py               # Application entry point
├── 📄 config.py             # Configuration management
├── 📄 database.py           # Database operations
├── 📄 models.py             # Data models
├── 📄 auth.py               # Authentication system
└── 📄 auth_routes.py        # Auth endpoints
```

## 🚀 Quick Start

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../env.example .env
# Edit .env with your configuration

# Run the application
python main.py
```

### Production Deployment
```bash
# Using Docker
docker-compose up -d

# Using Gunicorn
gunicorn -c gunicorn.conf.py app.main:app
```

## 🔧 Core Components

### Main Application (`main.py`)
- Flask application factory
- Blueprint registration
- Middleware configuration
- Health check endpoints
- Prometheus metrics

### Configuration (`config.py`)
- Environment-based configuration
- Security settings
- Database connections
- API keys management

### Authentication (`auth.py`, `auth_routes.py`)
- JWT-based authentication
- Role-based access control
- User management
- Security middleware

### Database (`database.py`, `models.py`)
- SQLAlchemy ORM setup
- Database migrations
- Data models
- Connection management

## 📡 API Endpoints

### Health & Status
- `GET /health` - Application health check
- `GET /status` - Detailed system status
- `GET /metrics` - Prometheus metrics

### Authentication
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `GET /auth/verify` - Token verification

### AI & ML Services
- `POST /anomaly` - ML anomaly detection
- `GET /anomaly` - Get anomaly history
- `POST /query` - ChatOps AI queries
- `GET /query` - Query history

### Monitoring & Remediation
- `GET /remediation/actions` - List remediation actions
- `POST /remediation/trigger` - Trigger remediation
- `GET /monitoring/metrics` - System metrics

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Admin and user roles
- **Input Validation**: Comprehensive request sanitization
- **Rate Limiting**: API abuse prevention
- **Audit Logging**: Complete security event tracking
- **CORS Protection**: Cross-origin request handling

## 📊 Monitoring & Observability

### Metrics Collection
- **System Metrics**: CPU, Memory, Disk, Network
- **Application Metrics**: Request rates, response times, error rates
- **Business Metrics**: User activity, feature usage
- **Custom Metrics**: ML model performance, remediation actions

### Logging
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic log management
- **Centralized Logging**: Unified log collection

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/backend/

# Run with coverage
pytest --cov=app
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Security
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# AI Services
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key

# Monitoring
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
```

### Configuration Files
- `config.py` - Application configuration
- `gunicorn.conf.py` - Production server configuration
- `alembic.ini` - Database migration configuration

## 🚀 Deployment

### Docker
```bash
# Build image
docker build -t smartcloudops-ai .

# Run container
docker run -p 5000:5000 smartcloudops-ai
```

### Kubernetes
```bash
# Deploy to Kubernetes
kubectl apply -f ../k8s/
```

### Production
```bash
# Using Gunicorn
gunicorn -c gunicorn.conf.py --bind 0.0.0.0:5000 app.main:app

# Using Docker Compose
docker-compose -f ../docker-compose.yml up -d
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check `DATABASE_URL` environment variable
   - Verify database is running
   - Check network connectivity

2. **Authentication Issues**
   - Verify `JWT_SECRET_KEY` is set
   - Check token expiration settings
   - Review user permissions

3. **ML Model Errors**
   - Ensure model files are present in `../ml_models/`
   - Check API keys for AI services
   - Verify model dependencies

### Debug Mode
```bash
# Enable debug mode
export FLASK_DEBUG=1
export FLASK_ENV=development
python main.py
```

## 📚 Documentation

- [API Reference](../docs/API_REFERENCE.md)
- [Architecture Guide](../docs/ARCHITECTURE.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)
- [Security Guide](../docs/SECURITY_HARDENING_GUIDE.md)

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

---

**SmartCloudOps AI v3.3.0** - Enterprise AI-Powered Cloud Operations Platform
