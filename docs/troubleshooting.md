# SmartCloudOps AI - Troubleshooting Guide

**Last Updated**: January 2025  
**Version**: 3.3.0  
**Covers**: Complete SmartCloudOps AI Platform  

## 🚨 Quick Issue Resolution

### 🔍 Common Symptoms
| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Tests failing | Missing dependencies | `pip install -r requirements.txt` |
| Docker build fails | Build context issues | `docker build --no-cache .` |
| Database connection fails | Connection string | Check `DATABASE_URL` in `.env` |
| ML model errors | Model file missing | Run `python ml_models/train_enhanced_model.py` |
| API authentication fails | JWT token expired | Re-authenticate via `/auth/login` |
| Prometheus targets down | Service discovery | Check `/targets` endpoint |

## 🧪 Testing Issues

### Unit Test Failures

#### Issue: `pytest` fails with import errors
**Symptoms**: 
- ModuleNotFoundError for app modules
- ImportError for ml_models
- Test discovery failures

**Diagnosis**:
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Check test structure
ls -la tests/
pytest --collect-only
```

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests with proper path
PYTHONPATH=. pytest tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/backend/
```

#### Issue: Database tests failing
**Symptoms**:
- SQLAlchemy connection errors
- Database not found
- Migration errors

**Diagnosis**:
```bash
# Check database configuration
echo $DATABASE_URL
python -c "from app.database import get_db_session; print('DB OK')"

# Check migrations
alembic current
alembic history
```

**Solution**:
```bash
# Set up test database
export DATABASE_URL="sqlite:///test.db"
alembic upgrade head

# Run tests with test database
DATABASE_URL="sqlite:///test.db" pytest tests/

# Clean up test database
rm test.db
```

#### Issue: ML model tests failing
**Symptoms**:
- Model file not found
- Scikit-learn version conflicts
- Memory errors during training

**Diagnosis**:
```bash
# Check ML dependencies
python -c "import sklearn, pandas, numpy; print('ML OK')"

# Check model files
ls -la ml_models/
ls -la ml_models/versions/
```

**Solution**:
```bash
# Install ML dependencies
pip install scikit-learn pandas numpy joblib

# Train test model
python ml_models/train_enhanced_model.py

# Run ML tests
pytest tests/unit/test_ml_models.py -v
```

### Integration Test Issues

#### Issue: API integration tests failing
**Symptoms**:
- Flask app not starting
- Authentication token issues
- Endpoint not found errors

**Diagnosis**:
```bash
# Check Flask app
python -c "from app.main import create_app; app = create_app(); print('App OK')"

# Check test client
pytest tests/integration/test_api_endpoints.py -v -s
```

**Solution**:
```bash
# Set test environment
export FLASK_ENV=testing
export TESTING=True

# Run integration tests
pytest tests/integration/ -v

# Check app logs
pytest tests/integration/ -v -s --log-cli-level=DEBUG
```

#### Issue: Database integration tests failing
**Symptoms**:
- Transaction rollback errors
- Data persistence issues
- Constraint violations

**Diagnosis**:
```bash
# Check database session
python -c "from app.database import get_db_session; session = get_db_session(); print('Session OK')"

# Check models
python -c "from app.models import User, Anomaly; print('Models OK')"
```

**Solution**:
```bash
# Use test database
export DATABASE_URL="sqlite:///:memory:"

# Run database tests
pytest tests/integration/test_api_endpoints.py::TestDatabaseIntegration -v

# Check transaction handling
pytest tests/integration/test_api_endpoints.py::TestDatabaseIntegration::test_database_transactions -v -s
```

## 🏗️ Infrastructure Issues

### Docker Deployment Problems

#### Issue: Docker build fails
**Symptoms**:
- Build context errors
- Missing files in Dockerfile
- Permission denied errors

**Diagnosis**:
```bash
# Check Dockerfile
cat Dockerfile

# Check build context
docker build --no-cache . 2>&1 | head -20

# Check file permissions
ls -la Dockerfile
ls -la requirements.txt
```

**Solution**:
```bash
# Clean build
docker system prune -f
docker build --no-cache -t smartcloudops-ai .

# Check for missing files
docker build . 2>&1 | grep "COPY failed"

# Fix file permissions
chmod 644 requirements.txt
chmod 644 Dockerfile
```

#### Issue: Docker Compose services not starting
**Symptoms**:
- Services exiting with code 1
- Port conflicts
- Volume mount errors

**Diagnosis**:
```bash
# Check service status
docker-compose ps
docker-compose logs

# Check port usage
netstat -tlnp | grep :5000
netstat -tlnp | grep :5432
```

**Solution**:
```bash
# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Database Connection Issues

#### Issue: PostgreSQL connection fails
**Symptoms**:
- Connection refused errors
- Authentication failures
- Database not found

**Diagnosis**:
```bash
# Check PostgreSQL container
docker-compose ps postgres
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U cloudops -d cloudops_db
```

**Solution**:
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check environment variables
cat .env | grep DATABASE

# Recreate database
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose up -d
```

#### Issue: Redis connection fails
**Symptoms**:
- Redis connection timeout
- Cache not working
- Session storage errors

**Diagnosis**:
```bash
# Check Redis container
docker-compose ps redis
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

**Solution**:
```bash
# Restart Redis
docker-compose restart redis

# Check Redis configuration
docker-compose exec redis redis-cli config get maxmemory
```

## 🔧 Application Issues

### Flask App Problems

#### Issue: Flask app not starting
**Symptoms**:
- Import errors
- Configuration issues
- Port already in use

**Diagnosis**:
```bash
# Check app startup
python app/main.py

# Check imports
python -c "from app.main import create_app; print('Import OK')"

# Check configuration
python -c "from app.config import get_config; print(get_config())"
```

**Solution**:
```bash
# Set environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start app
python app/main.py

# Check for port conflicts
lsof -i :5000
```

#### Issue: API endpoints returning errors
**Symptoms**:
- 500 Internal Server Error
- 404 Not Found
- Authentication errors

**Diagnosis**:
```bash
# Check app logs
tail -f logs/app.log

# Test endpoints
curl http://localhost:5000/health
curl http://localhost:5000/status

# Check authentication
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Solution**:
```bash
# Check database connection
python -c "from app.database import get_db_session; session = get_db_session(); print('DB OK')"

# Restart application
docker-compose restart smartcloudops-main

# Check service logs
docker-compose logs smartcloudops-main
```

### ML Model Issues

#### Issue: Anomaly detection not working
**Symptoms**:
- Model prediction errors
- Low accuracy scores
- Model file not found

**Diagnosis**:
```bash
# Check model files
ls -la ml_models/
ls -la ml_models/versions/

# Test model loading
python -c "from ml_models.anomaly_detector import AnomalyDetector; print('Model OK')"
```

**Solution**:
```bash
# Retrain model
python ml_models/train_enhanced_model.py

# Test model
python -c "
from ml_models.anomaly_detector import AnomalyDetector
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'cpu_usage': [50, 60, 70],
    'memory_usage': [40, 50, 60]
})
detector = AnomalyDetector()
result = detector.predict_anomalies(data)
print('Prediction:', result)
"
```

#### Issue: Model training fails
**Symptoms**:
- Memory errors
- Data validation failures
- Training timeout

**Diagnosis**:
```bash
# Check available memory
free -h

# Check training data
python -c "import pandas as pd; print('Pandas OK')"
```

**Solution**:
```bash
# Reduce memory usage
export PYTHONUNBUFFERED=1
python ml_models/train_enhanced_model.py --max-samples 1000

# Use smaller model
python ml_models/train_enhanced_model.py --model-type isolation_forest
```

## 🔐 Security Issues

### Authentication Problems

#### Issue: JWT token validation fails
**Symptoms**:
- Token expired errors
- Invalid signature
- Missing token

**Diagnosis**:
```bash
# Check JWT configuration
python -c "from app.auth import AuthManager; print('Auth OK')"

# Test token generation
python -c "
from app.auth import AuthManager
auth = AuthManager()
token = auth.generate_token('testuser')
print('Token:', token[:20] + '...')
"
```

**Solution**:
```bash
# Check secret key
echo $SECRET_KEY

# Regenerate token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### Issue: Password hashing errors
**Symptoms**:
- Login failures
- Password validation errors
- Hash comparison failures

**Diagnosis**:
```bash
# Check bcrypt installation
python -c "import bcrypt; print('Bcrypt OK')"

# Test password hashing
python -c "
import bcrypt
password = 'test123'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print('Hash:', hashed[:20])
"
```

**Solution**:
```bash
# Reinstall bcrypt
pip uninstall bcrypt
pip install bcrypt

# Reset admin password
python -c "
from app.database import get_db_session
from app.models import User
import bcrypt

session = get_db_session()
user = session.query(User).filter_by(username='admin').first()
if user:
    user.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    session.commit()
    print('Password reset')
"
```

## 📊 Monitoring Issues

### Prometheus Problems

#### Issue: Prometheus not collecting metrics
**Symptoms**:
- Empty metrics
- Targets showing DOWN
- No data in Grafana

**Diagnosis**:
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Prometheus configuration
curl http://localhost:9090/api/v1/status/config

# Check service discovery
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'
```

**Solution**:
```bash
# Restart Prometheus
docker-compose restart prometheus

# Check configuration
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# Verify targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

### Grafana Issues

#### Issue: Grafana dashboards not loading
**Symptoms**:
- "No Data" in dashboards
- Data source errors
- Query timeouts

**Diagnosis**:
```bash
# Check Grafana data sources
curl -u admin:admin http://localhost:3000/api/datasources

# Check Prometheus connectivity
curl -u admin:admin http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=up
```

**Solution**:
```bash
# Restart Grafana
docker-compose restart grafana

# Reconfigure data source
# Access http://localhost:3000
# Go to Configuration > Data Sources
# Verify Prometheus URL: http://prometheus:9090

# Upload dashboards
python scripts/upload_dashboards.py
```

## 🚀 Performance Issues

### High Resource Usage

#### Issue: High CPU/Memory usage
**Symptoms**:
- Slow response times
- Out of memory errors
- Service timeouts

**Diagnosis**:
```bash
# Check resource usage
docker stats

# Check application metrics
curl http://localhost:5000/metrics

# Check system resources
top
htop
```

**Solution**:
```bash
# Optimize Docker resources
# Edit docker-compose.yml
services:
  smartcloudops-main:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

# Restart with limits
docker-compose down
docker-compose up -d

# Monitor performance
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Database Performance

#### Issue: Slow database queries
**Symptoms**:
- Long response times
- Connection timeouts
- Query errors

**Diagnosis**:
```bash
# Check database performance
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "SELECT * FROM pg_stat_activity;"

# Check slow queries
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

**Solution**:
```bash
# Optimize database
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "VACUUM ANALYZE;"

# Add indexes
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);"

# Check query performance
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "EXPLAIN ANALYZE SELECT * FROM anomalies WHERE timestamp > NOW() - INTERVAL '1 hour';"
```

## 🔄 Recovery Procedures

### Complete System Recovery

#### Issue: Total system failure
**Symptoms**:
- All services down
- Database corrupted
- Configuration lost

**Recovery Steps**:
```bash
# 1. Stop all services
docker-compose down -v

# 2. Backup current state
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup

# 3. Restore from backup
cp .env.backup .env
cp docker-compose.yml.backup docker-compose.yml

# 4. Rebuild and start
docker-compose build --no-cache
docker-compose up -d

# 5. Run migrations
docker-compose exec smartcloudops-main alembic upgrade head

# 6. Verify services
docker-compose ps
curl http://localhost:5000/health
```

### Data Recovery

#### Issue: Database data loss
**Symptoms**:
- Missing records
- Corrupted data
- Migration failures

**Recovery Steps**:
```bash
# 1. Check database integrity
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "SELECT COUNT(*) FROM anomalies;"
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "SELECT COUNT(*) FROM users;"

# 2. Restore from backup (if available)
docker-compose exec postgres pg_restore -U cloudops -d cloudops_db backup.sql

# 3. Re-run migrations
docker-compose exec smartcloudops-main alembic upgrade head

# 4. Verify data
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "SELECT COUNT(*) FROM anomalies;"
```

## 📋 Prevention Best Practices

### Regular Maintenance
```bash
# Daily health checks
curl http://localhost:5000/health
curl http://localhost:9090/api/v1/targets
curl http://localhost:3000/api/health

# Weekly database maintenance
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "VACUUM ANALYZE;"

# Monthly security updates
docker-compose pull
docker-compose build --no-cache
docker-compose up -d
```

### Monitoring Setup
- Set up Grafana alerts for critical metrics
- Configure Prometheus alerting rules
- Regular testing of backup and recovery procedures
- Monitor application logs for errors

### Testing Best Practices
```bash
# Run tests before deployment
pytest tests/ -v --cov=app

# Run integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/unit/test_ml_models.py::TestMLModelsPerformance -v

# Check code quality
flake8 app/
black --check app/
mypy app/
```

---

## 🆘 Getting Help

### Information to Gather
Before seeking help, collect:
1. **Error messages**: Full error text and logs
2. **System info**: OS, Python version, Docker version
3. **Steps to reproduce**: What you were doing when issue occurred
4. **Environment**: Development vs production setup
5. **Test results**: Output from `pytest tests/ -v`

### Log Locations
- **Application**: `logs/app.log`
- **Docker**: `docker-compose logs`
- **Database**: `docker-compose logs postgres`
- **Prometheus**: `docker-compose logs prometheus`
- **Grafana**: `docker-compose logs grafana`

### Quick Diagnostic Commands
```bash
# System status
docker-compose ps
docker stats

# Application health
curl http://localhost:5000/health
curl http://localhost:5000/status

# Database status
docker-compose exec postgres psql -U cloudops -d cloudops_db -c "SELECT version();"

# Monitoring status
curl http://localhost:9090/api/v1/targets
curl http://localhost:3000/api/health

# Test coverage
pytest tests/ --cov=app --cov-report=html
```

### Common Test Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/backend/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing

# Run performance tests
pytest tests/unit/test_ml_models.py::TestMLModelsPerformance -v

# Run database tests
pytest tests/integration/test_api_endpoints.py::TestDatabaseIntegration -v
```

---

This troubleshooting guide covers the most common issues for the complete SmartCloudOps AI platform. It will be updated as new features are added and new issues are identified.