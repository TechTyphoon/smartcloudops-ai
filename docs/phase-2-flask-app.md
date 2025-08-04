# Phase 2: Flask ChatOps App + Dockerization

**Status**: 🚧 Ready to Start  
**Target Start Date**: Immediate  
**Estimated Duration**: 2-3 hours  

## 📋 Overview

Phase 2 focuses on developing the Flask ChatOps application with GPT integration, comprehensive Dockerization, and CI/CD pipeline enhancement. This phase builds upon the infrastructure established in Phase 1.

## 🎯 Objectives

### Phase 2.1: Flask App Basics
- [ ] Create app/main.py with core endpoints
- [ ] Implement /query, /status, /logs endpoints
- [ ] Add Prometheus metrics integration
- [ ] Basic request handling and validation

### Phase 2.2: GPT Integration
- [ ] Integrate OpenAI SDK or LiteLLM
- [ ] Implement prompt template system
- [ ] Add input sanitization and validation
- [ ] Create intelligent response handling

### Phase 2.3: Dockerization
- [ ] Create production-ready Dockerfile
- [ ] Implement multi-stage build process
- [ ] Add health checks and monitoring
- [ ] Optimize container size and security

### Phase 2.4: CI/CD Enhancement
- [ ] Enhance application CI/CD pipeline
- [ ] Add automated testing for Flask app
- [ ] Implement container building and pushing
- [ ] Add deployment automation

## 📁 Files to be Created

```
📂 app/
├── 📄 main.py                      # Main Flask application
├── 📄 requirements.txt             # Application dependencies
├── 📄 config.py                    # Configuration management
├── 📄 chatops/
│   ├── 📄 __init__.py
│   ├── 📄 gpt_handler.py          # GPT integration
│   ├── 📄 prometheus_metrics.py   # Metrics collection
│   └── 📄 utils.py                # Utility functions
├── 📂 templates/                   # Jinja2 templates (if needed)
├── 📂 static/                      # Static files (if needed)
└── 📂 tests/
    ├── 📄 test_main.py
    ├── 📄 test_gpt_handler.py
    └── 📄 test_endpoints.py
```

## 🔧 Dependencies Required

### 📦 Python Dependencies
**Core Flask**:
- Flask==2.3.3
- Flask-CORS==4.0.0
- gunicorn==21.2.0

**AI/GPT Integration**:
- openai==1.3.0 (or litellm==1.8.0)

**Monitoring**:
- prometheus-client==0.19.0

**Configuration**:
- python-dotenv==1.0.0
- pyyaml==6.0.1

### 🔑 External Dependencies
**Required from User**:
- **OpenAI API Key**: For GPT integration (Phase 2.2)

**Infrastructure Ready**:
- ✅ AWS EC2 application server
- ✅ Monitoring stack integration
- ✅ Docker environment

## 🏗️ Implementation Plan

### Phase 2.1: Flask App Basics

#### Core Application Structure
```python
# app/main.py structure
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": "Smart CloudOps AI", "status": "running"}

@app.route('/query', methods=['POST'])
def query():
    # ChatOps query handler
    pass

@app.route('/status')
def status():
    # System status endpoint
    pass

@app.route('/logs')
def logs():
    # Log retrieval endpoint
    pass

@app.route('/metrics')
def metrics():
    # Prometheus metrics endpoint
    pass
```

#### Endpoint Specifications
- **/** (GET): Basic health check and application info
- **/query** (POST): Main ChatOps query interface
- **/status** (GET): System health and status information  
- **/logs** (GET): Log retrieval with filtering
- **/metrics** (GET): Prometheus metrics endpoint

### Phase 2.2: GPT Integration

#### GPT Handler Implementation
```python
# app/chatops/gpt_handler.py structure
import openai
from typing import Dict, Any

class GPTHandler:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def process_query(self, query: str, context: Dict[str, Any]) -> str:
        # Process ChatOps queries with context
        pass
    
    def sanitize_input(self, query: str) -> str:
        # Input sanitization and validation
        pass
```

#### Prompt Template System
- System prompts for DevOps assistant role
- Context integration (logs, metrics, alerts)
- Response formatting and validation

### Phase 2.3: Dockerization

#### Multi-stage Dockerfile
```dockerfile
# Multi-stage build for optimization
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim as runtime
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY app/ .
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/status || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "main:app"]
```

### Phase 2.4: CI/CD Enhancement

#### Enhanced Pipeline Features
- **Testing**: Unit tests, integration tests, load tests
- **Security**: Dependency scanning, container scanning
- **Building**: Multi-architecture container builds
- **Deployment**: Automated deployment to EC2

## 🔐 Security Considerations

### Input Validation
- Query sanitization and length limits
- SQL injection prevention
- XSS protection for any web interfaces

### API Security
- Rate limiting implementation
- Authentication for sensitive endpoints
- Secure credential management

### Container Security
- Non-root user execution
- Minimal base image
- Security scanning integration

## 📊 Monitoring Integration

### Application Metrics
- Request count and duration
- Error rates and types
- GPT API usage and performance
- System resource utilization

### Prometheus Integration
- Custom metrics for ChatOps functionality
- Integration with existing monitoring stack
- Alerting for application-specific issues

## 🧪 Testing Strategy

### Unit Tests
- Endpoint functionality testing
- GPT handler testing (with mocking)
- Configuration and utility testing

### Integration Tests
- End-to-end query processing
- Prometheus metrics validation
- Health check verification

### Load Testing
- Concurrent request handling
- GPT API rate limit testing
- Memory and CPU usage under load

## 📋 Prerequisites for Starting

### Infrastructure Ready ✅
- AWS EC2 application server deployed
- Monitoring stack operational
- CI/CD pipelines configured

### User Requirements ⏳
- **OpenAI API Key**: Required for Phase 2.2
  - Sign up at https://platform.openai.com/
  - Generate API key
  - Configure in environment variables

### Development Environment ✅
- Python 3.10+ virtual environment
- Docker and Docker Compose
- Git repository access

## 🚀 Getting Started

### Immediate Next Steps
1. **Set up Flask application structure**
2. **Implement basic endpoints**
3. **Add Prometheus metrics integration**
4. **Create comprehensive tests**

### User Action Required
When ready for Phase 2.2 (GPT Integration):
- Provide OpenAI API key
- No other external dependencies needed

---

**Status**: Ready to begin immediately  
**Estimated Completion**: 2-3 hours for complete Phase 2  
**Next Phase**: [Phase 3: ML Anomaly Detection](phase-3-ml-layer.md)