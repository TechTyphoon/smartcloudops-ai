#!/usr/bin/env python3
"""
Production Readiness Assessment and Fixes
Smart CloudOps AI - Missing Components Analysis
"""

import os
import subprocess
import sys
from pathlib import Path


class ProductionReadinessChecker:
    def __init__(self):
        self.project_root = Path.cwd()
        self.missing_components = []
        self.fixes_applied = []

    def check_testing_framework(self):
        """Check if tests are working"""
        print("🧪 Checking Testing Framework...")

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.missing_components.append("pytest not installed")
            else:
                print(f"✅ pytest available: {result.stdout.strip()}")
        except:
            self.missing_components.append("pytest framework missing")

        # Check if tests run
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if "FAILED" in result.stdout or result.returncode != 0:
                self.missing_components.append(f"Tests failing: {result.stdout}")
            else:
                print("✅ Tests passing")
        except Exception as e:
            self.missing_components.append(f"Cannot run tests: {e}")

    def check_production_server(self):
        """Check production WSGI server setup"""
        print("⚡ Checking Production Server...")

        # Check for gunicorn
        try:
            result = subprocess.run(
                ["gunicorn", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.missing_components.append("gunicorn not installed")
            else:
                print(f"✅ gunicorn available: {result.stdout.strip()}")
        except:
            self.missing_components.append("gunicorn missing")

        # Check for production config
        if not (self.project_root / "gunicorn.conf.py").exists():
            self.missing_components.append("gunicorn configuration missing")

    def check_database_integration(self):
        """Check database setup"""
        print("📊 Checking Database Integration...")

        # Check for database packages
        db_packages = ["psycopg2-binary", "SQLAlchemy", "alembic"]
        for package in db_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"✅ {package} available")
            except ImportError:
                self.missing_components.append(f"{package} not installed")

        # Check for database config
        if not (self.project_root / "alembic.ini").exists():
            self.missing_components.append("Database migrations not configured")

    def check_security_features(self):
        """Check security implementations"""
        print("🔒 Checking Security Features...")

        security_packages = ["flask-limiter", "flask-jwt-extended", "cryptography"]
        for package in security_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"✅ {package} available")
            except ImportError:
                self.missing_components.append(f"{package} not installed")

        # Check for SSL certificates
        if not (self.project_root / "certs").exists():
            self.missing_components.append("SSL certificates not configured")

    def check_containerization(self):
        """Check Docker production setup"""
        print("🐳 Checking Containerization...")

        # Check Docker files
        docker_files = ["Dockerfile.production", "docker-compose.production.yml"]
        for file in docker_files:
            if (self.project_root / file).exists():
                print(f"✅ {file} exists")
            else:
                self.missing_components.append(f"{file} missing")

        # Check for Kubernetes manifests
        if not (self.project_root / "k8s").exists():
            self.missing_components.append("Kubernetes manifests missing")

    def generate_fixes(self):
        """Generate fixes for missing components"""
        print("\n🛠️  Generating Production Fixes...")

        fixes = {
            "install_production_deps": [
                "pip install gunicorn psycopg2-binary SQLAlchemy alembic",
                "pip install flask-limiter flask-jwt-extended cryptography",
                "pip install prometheus-client grafana-api",
                "pip install pytest pytest-cov pytest-mock",
            ],
            "create_gunicorn_config": self._create_gunicorn_config(),
            "create_database_config": self._create_database_config(),
            "create_security_config": self._create_security_config(),
            "create_k8s_manifests": self._create_k8s_manifests(),
            "create_production_tests": self._create_production_tests(),
        }

        return fixes

    def _create_gunicorn_config(self):
        return """# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
enable_stdio_inheritance = True
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
"""

    def _create_database_config(self):
        return """# database_config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://smartcloudops:password@localhost/smartcloudops_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

    def _create_security_config(self):
        return """# security_config.py
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
JWT_ACCESS_TOKEN_EXPIRES = False
"""

    def _create_k8s_manifests(self):
        return """# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smartcloudops-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smartcloudops-ai
  template:
    metadata:
      labels:
        app: smartcloudops-ai
    spec:
      containers:
      - name: smartcloudops-ai
        image: smartcloudops-ai:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
"""

    def _create_production_tests(self):
        return """# tests/test_production_endpoints.py
import pytest
import requests
from complete_production_app_real_data import app

class TestProductionEndpoints:
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        return app.test_client()

    def test_health_endpoint_real_data(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['data_source'] == '100% real system data'

    def test_all_endpoints_respond(self, client):
        endpoints = ['/health', '/status', '/metrics', '/anomaly/status']
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
"""

    def run_assessment(self):
        """Run complete production readiness assessment"""
        print("🔍 Smart CloudOps AI - Production Readiness Assessment")
        print("=" * 60)

        self.check_testing_framework()
        self.check_production_server()
        self.check_database_integration()
        self.check_security_features()
        self.check_containerization()

        print(f"\n📋 Assessment Results:")
        print(f"❌ Missing Components: {len(self.missing_components)}")

        if self.missing_components:
            print("\n🚨 Critical Issues Found:")
            for i, issue in enumerate(self.missing_components, 1):
                print(f"  {i}. {issue}")

        fixes = self.generate_fixes()
        print(f"\n🛠️  Available Fixes: {len(fixes)}")

        return {
            "missing_components": self.missing_components,
            "fixes": fixes,
            "production_ready": len(self.missing_components) == 0,
        }


if __name__ == "__main__":
    checker = ProductionReadinessChecker()
    result = checker.run_assessment()

    if not result["production_ready"]:
        print(
            f"\n⚠️  Project requires {len(result['missing_components'])} fixes before production deployment"
        )
        print("Run the fixes to achieve production readiness!")
    else:
        print("\n✅ Project is production ready!")
