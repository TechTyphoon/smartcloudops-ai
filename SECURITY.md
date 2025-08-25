# 🔒 Security Hardening Guide - SmartCloudOps AI

## Overview
This document outlines the security measures implemented in the SmartCloudOps AI platform to ensure enterprise-grade security compliance.

## 🔐 Secrets Management

### Environment Variables
All sensitive configuration values are managed through environment variables:

```bash
# Required Environment Variables
DB_PASSWORD=${DB_PASSWORD}
OPENAI_API_KEY=${OPENAI_API_KEY}
GEMINI_API_KEY=${GEMINI_API_KEY}
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
REDIS_PASSWORD=${REDIS_PASSWORD}
GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
SSH_PUBLIC_KEY=${SSH_PUBLIC_KEY}
```

### AWS Secrets Manager Integration
For production deployments, use AWS Secrets Manager:

```python
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=os.environ.get('AWS_REGION', 'us-west-2')
    )
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        raise
```

### HashiCorp Vault Integration
Alternative secrets management using HashiCorp Vault:

```python
import hvac

def get_vault_secret(secret_path):
    """Retrieve secret from HashiCorp Vault"""
    client = hvac.Client(
        url=os.environ.get('VAULT_URL'),
        token=os.environ.get('VAULT_TOKEN')
    )
    
    try:
        response = client.secrets.kv.v2.read_secret_version(
            path=secret_path,
            mount_point='secret'
        )
        return response['data']['data']
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_path}: {e}")
        raise
```

## 🛡️ Input Validation & Sanitization

### XSS Prevention
All user inputs are sanitized using the `bleach` library:

```python
import bleach

def sanitize_input(user_input: str) -> str:
    """Sanitize user input to prevent XSS attacks"""
    return bleach.clean(
        user_input,
        tags=[],  # No HTML tags allowed
        attributes={},
        protocols=[],
        strip=True
    )
```

### SQL Injection Prevention
Comprehensive SQL injection pattern detection:

```python
import re

def validate_sql_safety(input_string: str) -> bool:
    """Validate input for SQL injection patterns"""
    sql_patterns = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(\b(and|or)\b\s+\d+\s*[=<>])",
        r"(--|#|/\*|\*/)",
        r"(\bxp_|sp_|fn_)",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return False
    return True
```

### Command Injection Prevention
Protection against command injection attacks:

```python
def validate_command_safety(input_string: str) -> bool:
    """Validate input for command injection patterns"""
    command_patterns = [
        r"(\b(system|exec|eval|subprocess|os\.system)\b)",
        r"(\b(import\s+os|import\s+subprocess)\b)",
        r"(\b(__import__|getattr|setattr)\b)",
    ]
    
    for pattern in command_patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return False
    return True
```

## 🔒 Container Security

### Dockerfile Security Best Practices
- Multi-stage builds to reduce attack surface
- Non-root user execution
- Minimal base images
- No `apt-get upgrade` to prevent package conflicts
- Proper file permissions

### Image Scanning
All Docker images are scanned with Trivy:

```yaml
- name: 🔍 Scan image for vulnerabilities (Trivy)
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}-${{ matrix.target }}
    format: 'sarif'
    output: 'trivy-results-${{ matrix.target }}.sarif'
    severity: 'CRITICAL,HIGH'
```

## 🔍 CI/CD Security

### GitHub Actions Security
- Minimal required permissions
- Encrypted secrets for sensitive data
- Security scanning in pipeline
- No plaintext secrets in workflows

### Required GitHub Secrets
```bash
# Test Environment Secrets
TEST_OPENAI_API_KEY
TEST_GEMINI_API_KEY
TEST_REDIS_PASSWORD
TEST_SECRET_KEY
TEST_JWT_SECRET_KEY

# Production Secrets (set in repository settings)
PROD_DB_PASSWORD
PROD_OPENAI_API_KEY
PROD_GEMINI_API_KEY
PROD_SECRET_KEY
PROD_JWT_SECRET_KEY
PROD_REDIS_PASSWORD
PROD_GRAFANA_ADMIN_PASSWORD
PROD_SSH_PUBLIC_KEY
```

## 🚨 Security Monitoring

### Logging Security Events
```python
import logging
from datetime import datetime

def log_security_event(event_type: str, details: dict, user_id: str = None):
    """Log security events for monitoring"""
    security_logger = logging.getLogger('security')
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'details': details
    }
    
    security_logger.warning(f"SECURITY_EVENT: {json.dumps(log_entry)}")
```

### Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)

@app.route("/api/chatops", methods=["POST"])
@limiter.limit("10 per minute")
def chatops_endpoint():
    # Endpoint implementation
    pass
```

## 🔐 Authentication & Authorization

### JWT Token Security
```python
from flask_jwt_extended import create_access_token, create_refresh_token

def create_secure_tokens(user_id: str):
    """Create secure JWT tokens"""
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(hours=1)
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        expires_delta=timedelta(days=30)
    )
    return access_token, refresh_token
```

### Password Security
```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

## 🛡️ Network Security

### CORS Configuration
```python
from flask_cors import CORS

CORS(app, 
     origins=os.environ.get('CORS_ORIGINS', '').split(','),
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
```

### Security Headers
```python
from flask_talisman import Talisman

Talisman(app,
         content_security_policy={
             'default-src': "'self'",
             'script-src': "'self'",
             'style-src': "'self' 'unsafe-inline'",
             'img-src': "'self' data:",
             'font-src': "'self'"
         },
         force_https=True)
```

## 🔍 Security Testing

### Automated Security Scans
```bash
# Run security scans locally
bandit -r app/ -f json -o bandit-results.json
safety scan
trivy fs --severity HIGH,CRITICAL .
```

### Manual Security Testing
1. **SQL Injection Testing**: Use tools like SQLMap
2. **XSS Testing**: Test with various payloads
3. **Authentication Testing**: Test token validation
4. **Authorization Testing**: Test role-based access

## 📋 Security Checklist

### Pre-Deployment
- [ ] All secrets moved to environment variables
- [ ] Input validation implemented
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Logging configured for security events

### Post-Deployment
- [ ] Security scans completed
- [ ] Vulnerability assessment done
- [ ] Penetration testing completed
- [ ] Security monitoring enabled
- [ ] Incident response plan ready

## 🚨 Incident Response

### Security Incident Response Plan
1. **Detection**: Automated monitoring alerts
2. **Assessment**: Evaluate severity and scope
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Document and improve

### Contact Information
- Security Team: security@smartcloudops.ai
- Emergency: +1-XXX-XXX-XXXX
- Bug Bounty: https://smartcloudops.ai/security

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [AWS Security Best Practices](https://aws.amazon.com/security/security-learning/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
