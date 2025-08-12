# Smart CloudOps AI - Developer Setup Guide

## 🚀 Quick Start for New Developers

### Prerequisites
- Python 3.8+ installed
- Docker and Docker Compose installed
- Git configured with SSH keys
- AWS CLI installed (optional, for production deployment)

### 1. Clone and Initial Setup

```bash
# Clone the repository
git clone git@github.com:your-org/smart-cloudops-ai.git
cd smart-cloudops-ai

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.template .env

# Edit .env file with your values
nano .env  # Or use your preferred editor
```

#### Required Environment Variables
```bash
# ChatOps AI Provider (choose one)
OPENAI_API_KEY=your_openai_key_here
# OR
GEMINI_API_KEY=your_gemini_key_here

# Database (for persistence)
DATABASE_URL=postgresql+psycopg2://cloudops:cloudops@localhost:5432/cloudops
```

### 3. Start Development Environment

```bash
# Start supporting services (PostgreSQL, Prometheus, Grafana)
docker-compose up -d

# Verify services are running
docker-compose ps

# Start the Flask application
python app/main.py
```

The application will be available at:
- **Flask App**: http://localhost:3003
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 4. Verify Setup

```bash
# Run health check
curl http://localhost:3003/health

# Test ChatOps endpoint
curl -X POST http://localhost:3003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the current system status?"}'

# Check metrics
curl http://localhost:3003/metrics
```

## 🏗️ Project Structure

```
smart-cloudops-ai/
├── app/                    # Main Flask application
│   ├── chatops/           # ChatOps functionality
│   ├── remediation/       # Auto-remediation engine
│   ├── config.py          # Configuration management
│   └── main.py           # Main application entry point
├── ml_models/             # Machine learning components
│   ├── anomaly_detector.py
│   ├── data_processor.py
│   └── models/           # Trained model files
├── scripts/               # Utility and deployment scripts
├── terraform/             # Infrastructure as Code
├── configs/              # Configuration files
├── docs/                 # Documentation
└── tests/                # Test files
```

## 🧪 Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... code changes ...

# Run tests
python -m pytest tests/

# Run security scan
bandit -r app/ scripts/ ml_models/

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

### 2. Code Quality Checks

```bash
# Format code
black app/ scripts/ ml_models/
isort app/ scripts/ ml_models/

# Lint code  
flake8 app/ scripts/ ml_models/ --max-line-length=100

# Type checking
mypy app/ --ignore-missing-imports

# Security scan
bandit -r app/ scripts/ ml_models/
```

### 3. Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_chatops.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

## 🔧 Key Development Commands

### Flask Application
```bash
# Start development server
python app/main.py

# Start with debug mode
FLASK_DEBUG=true python app/main.py

# Start on different port
FLASK_PORT=3005 python app/main.py
```

### Database Operations
```bash
# Reset database (development only)
docker-compose down -v
docker-compose up -d postgres

# Connect to database
docker exec -it cloudops_postgres psql -U cloudops -d cloudops
```

### ML Model Training
```bash
# Train anomaly detection model
python ml_models/train_model.py

# Test ML inference
python ml_models/example_usage.py
```

### Docker Operations
```bash
# Build application image
docker build -t smartcloudops-ai .

# Run application in container
docker run -p 3000:3000 smartcloudops-ai

# Build and run with docker-compose
docker-compose up --build
```

## 📊 Monitoring and Debugging

### Local Monitoring Setup

1. **Grafana Dashboard**: http://localhost:3000
   - Username: admin
   - Password: admin
   - Import dashboard from `configs/grafana-dashboard-*.json`

2. **Prometheus Metrics**: http://localhost:9090
   - Query application metrics
   - View targets and rules

### Debug Logging
```python
# Enable debug logging in your code
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message here")
```

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError: No module named 'app'"
```bash
# Solution: Ensure you're in the project root and virtual environment is activated
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Issue: "Connection to PostgreSQL failed"
```bash
# Solution: Ensure Docker services are running
docker-compose ps
docker-compose up -d postgres
```

#### Issue: "ML models not available"
```bash
# Solution: Train the ML model first
python ml_models/train_model.py
```

## 🌐 API Development

### ChatOps Endpoints
```bash
# Query processing
POST /query
{
  "query": "What is the current CPU usage?"
}

# Get conversation history
GET /chatops/history

# Clear conversation history
POST /chatops/clear
```

### ML Endpoints
```bash
# Detect anomaly
POST /anomaly
{
  "metrics": {
    "cpu_usage_avg": 85.0,
    "memory_usage_pct": 75.0
  }
}

# Batch anomaly detection
POST /anomaly/batch
{
  "metrics_batch": [
    {"cpu_usage_avg": 85.0, "memory_usage_pct": 75.0},
    {"cpu_usage_avg": 45.0, "memory_usage_pct": 60.0}
  ]
}

# Get ML status
GET /anomaly/status
```

### Remediation Endpoints
```bash
# Evaluate anomaly for remediation
POST /remediation/evaluate
{
  "anomaly_score": 0.85,
  "metrics": {"cpu_usage_avg": 95.0}
}

# Execute remediation
POST /remediation/execute
{
  "severity": "high",
  "metrics": {"cpu_usage_avg": 95.0}
}
```

## 🔒 Security Guidelines

### Input Validation
```python
# Always validate user inputs
from app.main import validate_string_input, validate_numeric_input, validate_json_input

# Validate string input
query = validate_string_input(user_input, max_length=1000)

# Validate numeric input
value = validate_numeric_input(user_value, min_val=0, max_val=100)

# Validate JSON input
data = validate_json_input(request.get_json())
```

### Secrets Management
```bash
# Never commit secrets to Git
echo ".env" >> .gitignore

# Use environment variables
export OPENAI_API_KEY="your-key-here"

# Or use .env file
echo "OPENAI_API_KEY=your-key-here" >> .env
```

### Security Testing
```bash
# Run security scan
bandit -r app/ scripts/ ml_models/

# Check for hardcoded secrets
git secrets --scan

# Dependency vulnerability check
safety check
```

## 📦 Dependencies

### Core Dependencies
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Prometheus Client**: Metrics collection
- **Scikit-learn**: Machine learning
- **OpenAI/Google AI**: LLM integration

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **bandit**: Security scanning
- **mypy**: Type checking

## 🚀 Deployment

### Local Development
```bash
# Start all services
docker-compose up

# Or start just the app
python app/main.py
```

### Production Deployment
```bash
# Build production image
docker build -f Dockerfile.production -t smartcloudops-ai:prod .

# Deploy with Terraform
cd terraform/
terraform init
terraform plan
terraform apply
```

## 📞 Getting Help

### Documentation
- **Architecture**: `docs/architecture.md`
- **API Reference**: `docs/api-reference.md`
- **Security Guide**: `docs/SECURITY_HARDENING_GUIDE.md`
- **Troubleshooting**: `docs/troubleshooting.md`

### Team Contacts
- **Lead Developer**: dev-team@smartcloudops.ai
- **DevOps Team**: devops@smartcloudops.ai
- **Security Team**: security@smartcloudops.ai

### Internal Resources
- **Slack**: #cloudops-development
- **Wiki**: https://wiki.smartcloudops.ai
- **Issue Tracker**: GitHub Issues

---

*Happy coding! 🎉*

*Last Updated: 2025-01-11*  
*Version: 1.0*
