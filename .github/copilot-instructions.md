# Smart CloudOps AI - AI Coding Assistant Instructions

## Project Overview

**Smart CloudOps AI** is a phased DevOps automation platform combining Terraform infrastructure, Prometheus/Grafana monitoring, Flask ChatOps APIs, and ML-powered anomaly detection. Currently at **Phase 1 Complete** (Infrastructure + Monitoring + Flask App) with zero-cost AWS deployment.

## Architecture & Component Boundaries

### 1. **Infrastructure Layer** (`terraform/`)
- **Pattern**: Modular Terraform with shared VPC, separate EC2 instances for monitoring/application
- **Key Files**: `main.tf` (350+ lines), `variables.tf`, `configs/prometheus.yml`
- **Deployment**: Uses AWS Free Tier with t3.small/medium instances, encrypted EBS
- **Convention**: All resources tagged with Project/Environment/ManagedBy

### 2. **Monitoring Stack** (`terraform/configs/`, `terraform/scripts/`)
- **Architecture**: Prometheus (port 9090) + Grafana (port 3000) + Node Exporter (port 9100)
- **Data Flow**: Node Exporter → Prometheus → Grafana dashboards
- **Setup Scripts**: `monitoring_setup.sh` (238 lines) installs Docker stack on monitoring instance
- **Critical**: Prometheus config uses placeholder `APPLICATION_SERVER_IP` replaced by `configure_monitoring.sh` during deployment
- **Deployment Pattern**: Monitoring instance runs Docker containers, application instance runs native services

### 3. **Application Layer** (`app/`)
- **Pattern**: Phase-based Flask app with config classes and environment-based configuration
- **Current State**: Complete Flask application with metrics, health checks, error handling
- **Key Features**: `/metrics` endpoint for Prometheus, `/health` for monitoring, comprehensive logging
- **Testing**: Full test suite with 5 test cases covering all endpoints

## Critical Development Workflows

### Infrastructure Changes
```bash
# Always run local validation before push (from project root)
terraform fmt -recursive terraform/
terraform validate -chdir=terraform/
python test_workflows_locally.py  # Comprehensive pre-push validation (231 lines)

# For AWS changes, ensure you have valid credentials
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
```

### Testing Strategy
- **Pytest Config**: `pytest.ini` enforces 80% coverage, strict markers (`unit`, `integration`, `slow`)
- **Local Testing**: `test_workflows_locally.py` simulates all CI/CD steps locally
- **Health Checks**: `scripts/health_check.py` validates Prometheus connectivity

### CI/CD Patterns
- **Path-Based Triggers**: Terraform changes trigger `ci-infra.yml`, app changes trigger `ci-app.yml`
- **Multi-Python Matrix**: Tests against Python 3.10 and 3.11
- **Security First**: All workflows include flake8 linting and security scanning

## Project-Specific Conventions

### Configuration Management
```python
# Pattern: Environment-based config classes in app/config.py
from app.config import get_config
config = get_config("production")  # or "development"
```

### Phased Development Approach
- **Current**: Phase 1 complete (Infrastructure + Monitoring)
- **Next**: Phase 2 (Flask ChatOps + Docker), Phase 3 (ML Anomaly Detection)
- **Documentation**: `docs/PROJECT_STATUS.md` tracks completion, `SMART_CLOUDOPS_AI_PROJECT_PLAN.md` defines phases

### Resource Naming & Tagging
```hcl
# Terraform naming convention
resource "aws_instance" "monitoring" {
  tags = {
    Name        = "${var.project_name}-monitoring-${var.environment}"
    Project     = "SmartCloudOpsAI"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

## Integration Points & Data Flows

### Monitoring Data Flow
1. **Node Exporter** (9100) → **Prometheus** (9090) → **Grafana** (3000)
2. **Flask App** `/metrics` endpoint → Prometheus scraping
3. **Alert Rules**: `terraform/configs/alert-rules.yml` defines 7 critical system alerts

### Service Discovery Pattern
- Prometheus uses both static configs and EC2 service discovery
- Application server IP dynamically replaced in prometheus.yml during deployment via `configure_monitoring.sh`
- Pattern: `sed -i "s/APPLICATION_SERVER_IP/$APPLICATION_IP/g" prometheus.yml`
- Future ML layer will consume Prometheus API for anomaly detection

### Docker Development Stack
```yaml
# docker-compose.yml: Local development mirrors production monitoring
services:
  smartcloudops-app: # Flask app (port 3000)
  prometheus:        # Metrics collection (port 9090)  
  grafana:          # Visualization (port 3001)
```

## Essential Commands & Scripts

### Development Setup
```bash
python setup.py                    # Automated environment setup (212 lines)
python verify_setup.py            # Validation script
python test_workflows_locally.py  # Pre-commit testing (simulates CI/CD)
```

### Infrastructure Operations
```bash
# Apply infrastructure (from terraform/ directory)
terraform init && terraform plan && terraform apply

# Post-deployment scripts (run on EC2 instances)
terraform/scripts/monitoring_setup.sh     # Installs Docker + monitoring stack
terraform/scripts/configure_monitoring.sh # Replaces APPLICATION_SERVER_IP placeholders
terraform/scripts/application_setup.sh    # Configures app server with Flask + Node Exporter
```

### Health & Monitoring
```bash
python scripts/health_check.py  # Basic connectivity checks
# Manual checks: http://localhost:9090 (Prometheus), http://localhost:3000 (Grafana)
```

## Current Technical Debt & Known Issues

### Known Limitations (Phase 1)
- **Dynamic IP Issue**: Prometheus config has hardcoded placeholder IPs requiring post-deployment replacement via `configure_monitoring.sh`
- **Basic ChatOps**: Flask app has basic endpoints; full ChatOps features planned for Phase 2
- **Missing ML Components**: No ML models implemented (Phase 3 scope)
- **Local Development**: Docker-compose stack doesn't fully replicate AWS deployment patterns

### Established Patterns to Follow
- **Error Handling**: All scripts use try/catch with structured responses and proper logging
- **Configuration**: Environment-based config classes in `app/config.py`, never hardcode values in code
- **Documentation**: Every phase completion updates `docs/PROJECT_STATUS.md` with detailed status
- **Security**: IAM least-privilege principles, encrypted EBS volumes, restrictive security groups
- **Testing**: Run `test_workflows_locally.py` before any push to simulate full CI/CD pipeline

## Files Requiring Special Attention

- **`terraform/main.tf`** (352 lines): Complete infrastructure definition with VPC, EC2, security groups
- **`terraform/scripts/monitoring_setup.sh`** (238 lines): Critical monitoring installation with Docker setup
- **`test_workflows_locally.py`** (231 lines): Comprehensive pre-push validation simulating all CI/CD steps
- **`terraform/configs/prometheus.yml`**: Contains `APPLICATION_SERVER_IP` placeholders requiring runtime replacement
- **`app/config.py`**: Environment-based configuration pattern - use `get_config()` function
- **`.cursor/rules/cloudops-rules.mdc`**: Existing AI assistant rules for consistency with project standards
