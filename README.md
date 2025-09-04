# SmartCloudOps AI

A comprehensive AI-powered cloud operations platform with automated anomaly detection, remediation, and intelligent monitoring.

## Features

- 🤖 **AI-Powered Anomaly Detection**: Advanced ML models for real-time anomaly detection
- 🔄 **Auto-Remediation**: Intelligent automated response to detected issues
- 📊 **Comprehensive Monitoring**: Multi-layer observability with Prometheus, Grafana, and custom metrics
- 🔒 **Enterprise Security**: Advanced security validation, rate limiting, and secrets management
- 🚀 **MLOps Integration**: Complete ML lifecycle management with experiment tracking
- 💬 **ChatOps Interface**: Natural language interaction with the system
- 🏗️ **Infrastructure as Code**: Terraform configurations for automated deployment

## Quick Start

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/TechTyphoon/smartcloudops-ai.git
   cd smartcloudops-ai
   ```

2. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file with required variables
   cp env.template .env
   # Edit .env with your configuration
   ```

4. **Run the backend**
   ```bash
   python app/main.py
   ```

### Frontend Setup

5. **Install frontend dependencies**
   ```bash
   cd Frontend
   npm install
   ```

6. **Run the frontend**
   ```bash
   npm run dev
   ```

### Full Stack with Docker (Recommended)

7. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## Authentication System

The application uses JWT-based authentication with the following features:

- **JWT Tokens**: Access and refresh tokens with configurable expiry
- **Role-Based Access Control**: User roles (admin, user) with permission checking
- **Protected Endpoints**: All sensitive endpoints require authentication
- **Testing Support**: Automatic authentication bypass in testing mode
- **Audit Logging**: Comprehensive audit trail for all authentication events

### Required Environment Variables

- `JWT_SECRET_KEY`: Secret key for JWT token signing (minimum 32 characters)
- `SECRET_KEY`: Flask application secret key (minimum 32 characters)

### Protected Endpoints

The following endpoints require authentication:
- `/api/anomalies/*` - Anomaly management
- `/api/remediation/*` - Remediation actions
- `/api/ml/train` - ML model training
- `/api/chatops/*` - ChatOps functionality

## Architecture

The platform consists of several key components:

- **Flask Backend**: RESTful API with modular blueprints
- **ML Pipeline**: Automated model training and deployment
- **Monitoring Stack**: Prometheus, Grafana, and custom metrics
- **Security Layer**: Input validation, rate limiting, and secrets management
- **ChatOps Interface**: AI-powered conversational interface

## Documentation

- [Complete API Reference](docs/API_REFERENCE_COMPLETE.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [ML Pipeline Guide](docs/API_REFERENCE_SERVICE_LAYER.md)
- [Security Guide](docs/SECURITY_HARDENING_GUIDE.md)
- [Production Runbook](docs/PRODUCTION_DEPLOYMENT_RUNBOOK.md)
- [User Guide](docs/USER_GUIDE.md)
- [Observability Guide](docs/observability/README.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

For support and questions, please open an issue on GitHub.

---

**Last updated:** September 2025
**Version:** 3.3.0
