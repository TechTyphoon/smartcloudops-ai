#!/usr/bin/env python3
"""
Phase 7.3.2: Production Deployment Planning
Complete production deployment strategy and configuration
"""

import json
import logging
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionDeploymentPlanner:
    """Production deployment planning and configuration generator."""
    
    def __init__(self):
        self.deployment_config = {
            "planning_timestamp": datetime.now().isoformat(),
            "deployment_strategy": {},
            "infrastructure_config": {},
            "security_config": {},
            "monitoring_config": {},
            "backup_strategy": {},
            "disaster_recovery": {},
            "deployment_checklist": []
        }
        
    def generate_deployment_plan(self) -> Dict[str, Any]:
        """Generate comprehensive production deployment plan."""
        logger.info("🚀 Generating production deployment plan...")
        
        # Domain deployment strategy
        self.plan_domain_deployment()
        
        # SSL/TLS configuration
        self.plan_ssl_configuration()
        
        # Environment management
        self.plan_environment_config()
        
        # Security hardening
        self.plan_security_hardening()
        
        # Monitoring and alerting
        self.plan_monitoring_setup()
        
        # Backup and recovery
        self.plan_backup_strategy()
        
        # Deployment checklist
        self.create_deployment_checklist()
        
        return self.deployment_config
    
    def plan_domain_deployment(self):
        """Plan domain deployment strategy."""
        logger.info("🌐 Planning domain deployment strategy...")
        
        self.deployment_config["deployment_strategy"] = {
            "deployment_type": "docker_compose_with_reverse_proxy",
            "domain_requirements": {
                "primary_domain": "your-domain.com",
                "subdomains": {
                    "app": "app.your-domain.com",
                    "api": "api.your-domain.com", 
                    "monitoring": "monitoring.your-domain.com",
                    "grafana": "grafana.your-domain.com"
                }
            },
            "reverse_proxy": {
                "solution": "nginx",
                "features": ["ssl_termination", "load_balancing", "rate_limiting"],
                "configuration_required": True
            },
            "deployment_phases": [
                {
                    "phase": 1,
                    "name": "infrastructure_setup",
                    "tasks": ["domain_configuration", "ssl_certificates", "nginx_setup"]
                },
                {
                    "phase": 2,
                    "name": "application_deployment",
                    "tasks": ["docker_compose_deploy", "environment_configuration", "health_checks"]
                },
                {
                    "phase": 3,
                    "name": "monitoring_setup", 
                    "tasks": ["grafana_config", "prometheus_rules", "alerting_setup"]
                },
                {
                    "phase": 4,
                    "name": "production_validation",
                    "tasks": ["end_to_end_testing", "performance_validation", "security_scan"]
                }
            ]
        }
    
    def plan_ssl_configuration(self):
        """Plan SSL/TLS configuration."""
        logger.info("🔒 Planning SSL/TLS configuration...")
        
        self.deployment_config["security_config"]["ssl_tls"] = {
            "certificate_authority": "lets_encrypt",
            "automation_tool": "certbot",
            "certificate_management": {
                "auto_renewal": True,
                "renewal_frequency": "every_60_days",
                "notification_email": "admin@your-domain.com"
            },
            "nginx_ssl_config": {
                "ssl_protocols": ["TLSv1.2", "TLSv1.3"],
                "ssl_ciphers": "ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384",
                "ssl_prefer_server_ciphers": True,
                "hsts_enabled": True,
                "hsts_max_age": 31536000
            },
            "security_headers": {
                "strict_transport_security": "max-age=31536000; includeSubDomains",
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
                "x_xss_protection": "1; mode=block",
                "referrer_policy": "strict-origin-when-cross-origin"
            }
        }
    
    def plan_environment_config(self):
        """Plan environment configuration management."""
        logger.info("⚙️ Planning environment configuration...")
        
        self.deployment_config["infrastructure_config"] = {
            "environment_management": {
                "strategy": "docker_compose_with_env_files",
                "environments": {
                    "production": {
                        "env_file": ".env.production",
                        "variables": {
                            "FLASK_ENV": "production",
                            "DEBUG": "false",
                            "SECRET_KEY": "generate_secure_key",
                            "DATABASE_URL": "postgresql://user:pass@postgres:5432/smartcloudops",
                            "REDIS_URL": "redis://redis:6379/0",
                            "LOG_LEVEL": "INFO",
                            "PROMETHEUS_URL": "http://prometheus:9090",
                            "GRAFANA_URL": "http://grafana:3000"
                        }
                    },
                    "staging": {
                        "env_file": ".env.staging",
                        "variables": {
                            "FLASK_ENV": "staging",
                            "DEBUG": "false",
                            "SECRET_KEY": "staging_key",
                            "LOG_LEVEL": "DEBUG"
                        }
                    }
                }
            },
            "docker_optimization": {
                "production_dockerfile": True,
                "multi_stage_build": True,
                "image_optimization": ["alpine_base", "layer_caching", "security_scanning"],
                "resource_limits": {
                    "app_container": {"memory": "512m", "cpus": "0.5"},
                    "postgres_container": {"memory": "256m", "cpus": "0.25"},
                    "prometheus_container": {"memory": "512m", "cpus": "0.5"},
                    "grafana_container": {"memory": "256m", "cpus": "0.25"}
                }
            }
        }
    
    def plan_security_hardening(self):
        """Plan security hardening measures."""
        logger.info("🛡️ Planning security hardening...")
        
        self.deployment_config["security_config"]["hardening"] = {
            "container_security": {
                "non_root_user": True,
                "readonly_filesystem": False,  # Some containers need write access
                "security_scanning": True,
                "image_vulnerability_checks": True,
                "secrets_management": "docker_secrets"
            },
            "network_security": {
                "internal_network": True,
                "network_isolation": True,
                "firewall_rules": {
                    "allow_ports": [80, 443, 22],
                    "rate_limiting": True,
                    "ddos_protection": "cloudflare_or_nginx"
                }
            },
            "access_control": {
                "authentication": {
                    "admin_interface": "basic_auth_or_oauth",
                    "api_authentication": "token_based",
                    "monitoring_access": "restricted"
                },
                "authorization": {
                    "role_based_access": True,
                    "api_rate_limiting": True,
                    "monitoring_rbac": True
                }
            },
            "data_protection": {
                "database_encryption": "at_rest_and_in_transit",
                "backup_encryption": True,
                "log_sanitization": True,
                "pii_protection": True
            }
        }
    
    def plan_monitoring_setup(self):
        """Plan production monitoring setup."""
        logger.info("📊 Planning monitoring setup...")
        
        self.deployment_config["monitoring_config"] = {
            "prometheus_config": {
                "retention_period": "30d",
                "storage_size": "10GB",
                "alerting_rules": {
                    "system_alerts": ["high_cpu", "high_memory", "disk_full", "container_down"],
                    "application_alerts": ["high_response_time", "high_error_rate", "ml_model_failure"],
                    "custom_alerts": ["anomaly_detection_spike", "security_events"]
                },
                "recording_rules": True,
                "external_labels": {"environment": "production", "cluster": "main"}
            },
            "grafana_config": {
                "dashboards": ["system_overview", "application_metrics", "ml_performance", "security_monitoring"],
                "alerting": {
                    "notification_channels": ["email", "slack", "webhook"],
                    "alert_routing": True,
                    "escalation_policies": True
                },
                "user_management": {
                    "authentication": "ldap_or_oauth",
                    "role_based_permissions": True
                }
            },
            "log_management": {
                "centralized_logging": True,
                "log_aggregation": "elasticsearch_or_loki",
                "log_retention": "90d",
                "log_analysis": "automated_anomaly_detection"
            },
            "external_monitoring": {
                "uptime_monitoring": "uptimerobot_or_pingdom",
                "performance_monitoring": "newrelic_or_datadog",
                "security_monitoring": "security_scanners"
            }
        }
    
    def plan_backup_strategy(self):
        """Plan backup and disaster recovery strategy."""
        logger.info("💾 Planning backup strategy...")
        
        self.deployment_config["backup_strategy"] = {
            "database_backup": {
                "frequency": "daily",
                "retention": "30d",
                "encryption": True,
                "compression": True,
                "backup_location": ["local", "cloud_storage"],
                "automated_testing": True
            },
            "application_backup": {
                "configuration_backup": True,
                "logs_backup": "weekly",
                "ml_models_backup": True,
                "docker_images_backup": True
            },
            "monitoring_data_backup": {
                "prometheus_data": "weekly",
                "grafana_dashboards": "on_change",
                "alerting_rules": "on_change"
            },
            "backup_verification": {
                "automated_restore_tests": "monthly",
                "backup_integrity_checks": "weekly",
                "recovery_time_testing": "quarterly"
            }
        }
        
        self.deployment_config["disaster_recovery"] = {
            "rto_target": "4_hours",  # Recovery Time Objective
            "rpo_target": "1_hour",   # Recovery Point Objective
            "recovery_procedures": {
                "database_recovery": "automated_script",
                "application_recovery": "docker_compose_redeploy",
                "monitoring_recovery": "configuration_restore"
            },
            "failover_strategy": {
                "dns_failover": True,
                "load_balancer_health_checks": True,
                "automated_failover": "manual_approval_required"
            },
            "recovery_testing": {
                "frequency": "quarterly",
                "test_scenarios": ["database_failure", "application_failure", "complete_system_failure"],
                "documentation_updates": "after_each_test"
            }
        }
    
    def create_deployment_checklist(self):
        """Create comprehensive deployment checklist."""
        logger.info("📋 Creating deployment checklist...")
        
        self.deployment_config["deployment_checklist"] = [
            {
                "category": "Pre-Deployment",
                "tasks": [
                    {"task": "Domain registration and DNS setup", "required": True, "estimated_time": "1-2 hours"},
                    {"task": "SSL certificate acquisition (Let's Encrypt)", "required": True, "estimated_time": "30 minutes"},
                    {"task": "Production environment variables configuration", "required": True, "estimated_time": "1 hour"},
                    {"task": "Database production setup", "required": True, "estimated_time": "2 hours"},
                    {"task": "Security hardening review", "required": True, "estimated_time": "2 hours"},
                    {"task": "Backup procedures setup", "required": True, "estimated_time": "3 hours"},
                    {"task": "Monitoring alerts configuration", "required": True, "estimated_time": "2 hours"}
                ]
            },
            {
                "category": "Deployment",
                "tasks": [
                    {"task": "Production Docker images build", "required": True, "estimated_time": "30 minutes"},
                    {"task": "Docker Compose production deployment", "required": True, "estimated_time": "1 hour"},
                    {"task": "Nginx reverse proxy configuration", "required": True, "estimated_time": "1 hour"},
                    {"task": "SSL/TLS configuration and testing", "required": True, "estimated_time": "1 hour"},
                    {"task": "Database migration and seeding", "required": True, "estimated_time": "30 minutes"},
                    {"task": "Environment variables verification", "required": True, "estimated_time": "15 minutes"}
                ]
            },
            {
                "category": "Post-Deployment",
                "tasks": [
                    {"task": "End-to-end functionality testing", "required": True, "estimated_time": "2 hours"},
                    {"task": "Performance benchmarking", "required": True, "estimated_time": "1 hour"},
                    {"task": "Security scan and validation", "required": True, "estimated_time": "1 hour"},
                    {"task": "Monitoring and alerting verification", "required": True, "estimated_time": "1 hour"},
                    {"task": "Backup and recovery testing", "required": True, "estimated_time": "2 hours"},
                    {"task": "Load testing (optional)", "required": False, "estimated_time": "2 hours"},
                    {"task": "Documentation updates", "required": True, "estimated_time": "1 hour"}
                ]
            },
            {
                "category": "Operations",
                "tasks": [
                    {"task": "Monitoring dashboard setup", "required": True, "estimated_time": "2 hours"},
                    {"task": "Alert notification setup", "required": True, "estimated_time": "1 hour"},
                    {"task": "Operational runbooks creation", "required": True, "estimated_time": "4 hours"},
                    {"task": "Team training on production operations", "required": True, "estimated_time": "4 hours"},
                    {"task": "Incident response procedures", "required": True, "estimated_time": "2 hours"}
                ]
            }
        ]
    
    def generate_nginx_config(self) -> str:
        """Generate production-ready Nginx configuration."""
        return """# Smart CloudOps AI - Production Nginx Configuration

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

# Upstream definitions
upstream smartcloudops_app {
    server smartcloudops-app:3000;
    keepalive 32;
}

upstream grafana {
    server grafana:3000;
    keepalive 16;
}

upstream prometheus {
    server prometheus:9090;
    keepalive 16;
}

# Main application server
server {
    listen 80;
    server_name app.your-domain.com api.your-domain.com your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.your-domain.com api.your-domain.com your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate limiting
    limit_req zone=general burst=50 nodelay;
    
    # API endpoints with stricter rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://smartcloudops_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Main application
    location / {
        proxy_pass http://smartcloudops_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://smartcloudops_app;
        access_log off;
    }
}

# Grafana monitoring interface
server {
    listen 80;
    server_name monitoring.your-domain.com grafana.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monitoring.your-domain.com grafana.your-domain.com;
    
    # SSL Configuration (same as above)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Authentication (add basic auth or integrate with your auth system)
    # auth_basic "Monitoring Access";
    # auth_basic_user_file /etc/nginx/.htpasswd;
    
    location / {
        proxy_pass http://grafana;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}"""
    
    def generate_production_docker_compose(self) -> str:
        """Generate production Docker Compose configuration."""
        return """version: '3.8'

services:
  # Main Application
  smartcloudops-app:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: smartcloudops-app-prod
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - LOG_LEVEL=INFO
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
    networks:
      - smartcloudops_network
    volumes:
      - ./logs:/app/logs:rw
      - ./ml_models:/app/ml_models:ro
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: smartcloudops-postgres-prod
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data:rw
      - ./backups:/backups:rw
    networks:
      - smartcloudops_network
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: smartcloudops-redis-prod
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - smartcloudops_network
    volumes:
      - redis_data:/data:rw
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.1'
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: smartcloudops-prometheus-prod
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--storage.tsdb.retention.size=10GB'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./configs/alert-rules.yml:/etc/prometheus/alert-rules.yml:ro
      - prometheus_data:/prometheus:rw
    networks:
      - smartcloudops_network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: smartcloudops-grafana-prod
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_SERVER_DOMAIN=${GRAFANA_DOMAIN}
      - GF_SERVER_ROOT_URL=https://${GRAFANA_DOMAIN}
      - GF_DATABASE_TYPE=postgres
      - GF_DATABASE_HOST=postgres:5432
      - GF_DATABASE_NAME=${GRAFANA_DB_NAME}
      - GF_DATABASE_USER=${GRAFANA_DB_USER}
      - GF_DATABASE_PASSWORD=${GRAFANA_DB_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana_data:/var/lib/grafana:rw
      - ./configs/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./configs/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - smartcloudops_network
    depends_on:
      - postgres
      - prometheus
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: smartcloudops-node-exporter-prod
    restart: unless-stopped
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - smartcloudops_network
    deploy:
      resources:
        limits:
          memory: 64M
          cpus: '0.1'

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: smartcloudops-nginx-prod
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./configs/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./configs/nginx/sites-available:/etc/nginx/sites-available:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./logs/nginx:/var/log/nginx:rw
    networks:
      - smartcloudops_network
    depends_on:
      - smartcloudops-app
      - grafana
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.1'

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  smartcloudops_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16"""
    
    def save_deployment_plan(self, filename: str = None) -> str:
        """Save deployment plan and configuration files."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"production_deployment_plan_{timestamp}"
        
        # Save main deployment plan
        plan_path = Path(__file__).parent.parent / "docs" / f"{filename}.md"
        
        # Generate markdown report
        markdown_report = self.generate_deployment_markdown()
        
        with open(plan_path, 'w') as f:
            f.write(markdown_report)
        
        # Save deployment configuration files
        config_dir = Path(__file__).parent.parent / "configs" / "production"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Nginx config
        nginx_config_path = config_dir / "nginx.conf"
        with open(nginx_config_path, 'w') as f:
            f.write(self.generate_nginx_config())
        
        # Save production Docker Compose
        docker_compose_path = config_dir / "docker-compose.production.yml"
        with open(docker_compose_path, 'w') as f:
            f.write(self.generate_production_docker_compose())
        
        # Save deployment config as JSON
        json_path = Path(__file__).parent.parent / "logs" / f"{filename}.json"
        json_path.parent.mkdir(exist_ok=True)
        
        with open(json_path, 'w') as f:
            json.dump(self.deployment_config, f, indent=2)
        
        logger.info(f"Deployment plan saved: {plan_path}")
        logger.info(f"Configuration files saved in: {config_dir}")
        
        return str(plan_path)
    
    def generate_deployment_markdown(self) -> str:
        """Generate comprehensive deployment plan markdown."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Production Deployment Plan

**Generated**: {timestamp}  
**Phase**: 7.3.2 - Production Deployment Planning  
**Status**: Ready for Implementation  

## 🎯 Deployment Overview

### Strategy
**Deployment Type**: {self.deployment_config['deployment_strategy']['deployment_type']}  
**Reverse Proxy**: {self.deployment_config['deployment_strategy']['reverse_proxy']['solution']}  
**SSL/TLS**: {self.deployment_config['security_config']['ssl_tls']['certificate_authority']}  

### Domain Configuration
"""
        
        domain_config = self.deployment_config['deployment_strategy']['domain_requirements']
        report += f"**Primary Domain**: {domain_config['primary_domain']}\n\n"
        
        report += "**Subdomains**:\n"
        for subdomain, url in domain_config['subdomains'].items():
            report += f"- **{subdomain.title()}**: {url}\n"
        
        report += """
## 🚀 Deployment Phases

"""
        
        phases = self.deployment_config['deployment_strategy']['deployment_phases']
        for phase in phases:
            report += f"### Phase {phase['phase']}: {phase['name'].replace('_', ' ').title()}\n"
            for task in phase['tasks']:
                report += f"- {task.replace('_', ' ').title()}\n"
            report += "\n"
        
        report += """
## 🔒 Security Configuration

### SSL/TLS Setup
"""
        
        ssl_config = self.deployment_config['security_config']['ssl_tls']
        report += f"""
- **Certificate Authority**: {ssl_config['certificate_authority']}
- **Automation Tool**: {ssl_config['automation_tool']}
- **Auto Renewal**: {'✅' if ssl_config['certificate_management']['auto_renewal'] else '❌'}
- **Renewal Frequency**: {ssl_config['certificate_management']['renewal_frequency']}
- **Protocols**: {', '.join(ssl_config['nginx_ssl_config']['ssl_protocols'])}

### Security Headers
"""
        
        for header, value in ssl_config['security_headers'].items():
            report += f"- **{header.replace('_', '-').title()}**: {value}\n"
        
        report += """
### Security Hardening
"""
        
        hardening = self.deployment_config['security_config']['hardening']
        report += f"""
- **Container Security**: Non-root users, security scanning enabled
- **Network Security**: Internal network with isolation
- **Access Control**: Role-based authentication and authorization
- **Data Protection**: Encryption at rest and in transit
"""
        
        report += """
## 📊 Monitoring Configuration

### Prometheus Setup
"""
        
        prometheus_config = self.deployment_config['monitoring_config']['prometheus_config']
        report += f"""
- **Retention Period**: {prometheus_config['retention_period']}
- **Storage Size**: {prometheus_config['storage_size']}
- **System Alerts**: {', '.join(prometheus_config['alerting_rules']['system_alerts'])}
- **Application Alerts**: {', '.join(prometheus_config['alerting_rules']['application_alerts'])}

### Grafana Setup
"""
        
        grafana_config = self.deployment_config['monitoring_config']['grafana_config']
        report += f"""
- **Dashboards**: {', '.join(grafana_config['dashboards'])}
- **Notification Channels**: {', '.join(grafana_config['alerting']['notification_channels'])}
- **Authentication**: {grafana_config['user_management']['authentication']}
"""
        
        report += """
## 💾 Backup Strategy

### Database Backup
"""
        
        db_backup = self.deployment_config['backup_strategy']['database_backup']
        report += f"""
- **Frequency**: {db_backup['frequency'].title()}
- **Retention**: {db_backup['retention']}
- **Encryption**: {'✅' if db_backup['encryption'] else '❌'}
- **Locations**: {', '.join(db_backup['backup_location'])}
- **Automated Testing**: {'✅' if db_backup['automated_testing'] else '❌'}

### Disaster Recovery
"""
        
        dr_config = self.deployment_config['disaster_recovery']
        report += f"""
- **RTO Target**: {dr_config['rto_target'].replace('_', ' ')}
- **RPO Target**: {dr_config['rpo_target'].replace('_', ' ')}
- **Testing Frequency**: {dr_config['recovery_testing']['frequency'].title()}
"""
        
        report += """
## 📋 Deployment Checklist

"""
        
        checklist = self.deployment_config['deployment_checklist']
        for category in checklist:
            report += f"### {category['category']}\n\n"
            total_time = 0
            
            for task in category['tasks']:
                required_icon = "✅" if task['required'] else "⚪"
                time_str = task['estimated_time']
                report += f"- [{required_icon}] **{task['task']}** ({time_str})\n"
                
                # Calculate total time (rough estimation)
                if 'hour' in time_str:
                    hours = float(time_str.split(' ')[0].split('-')[-1])
                    total_time += hours
                elif 'minute' in time_str:
                    minutes = float(time_str.split(' ')[0])
                    total_time += minutes / 60
            
            report += f"\n**Estimated Total Time**: {total_time:.1f} hours\n\n"
        
        report += """
## 🛠️ Configuration Files

### Generated Files
- **Nginx Configuration**: `configs/production/nginx.conf`
- **Production Docker Compose**: `configs/production/docker-compose.production.yml`
- **Environment Template**: `.env.production.template`

### Manual Configuration Required
1. **Domain DNS Configuration**
   - Point domain A records to your server IP
   - Configure CNAME records for subdomains

2. **Environment Variables**
   - Copy `.env.production.template` to `.env.production`
   - Generate secure SECRET_KEY
   - Configure database credentials
   - Set up notification endpoints

3. **SSL Certificates**
   ```bash
   sudo certbot --nginx -d your-domain.com -d app.your-domain.com -d monitoring.your-domain.com
   ```

4. **Initial Deployment**
   ```bash
   docker-compose -f configs/production/docker-compose.production.yml up -d
   ```

## 🎯 Success Criteria

### Deployment Success
- [ ] All containers healthy and running
- [ ] SSL certificates installed and valid
- [ ] All endpoints accessible via HTTPS
- [ ] Monitoring dashboards operational
- [ ] Backup procedures verified

### Performance Targets
- [ ] API response time < 100ms
- [ ] ML inference time < 150ms
- [ ] 99.9% uptime target
- [ ] Zero security vulnerabilities

### Security Validation
- [ ] SSL/TLS A+ rating
- [ ] No exposed sensitive endpoints
- [ ] Authentication working correctly
- [ ] Security headers properly configured

---

**Next Steps**: Review and customize configuration files, then proceed with Phase 1 of deployment.

*Generated by Smart CloudOps AI Production Deployment Planner - Phase 7.3.2*
"""
        
        return report


def main():
    """Main function to generate production deployment plan."""
    print("🚀 Smart CloudOps AI - Production Deployment Planning")
    print("=" * 55)
    
    planner = ProductionDeploymentPlanner()
    
    try:
        # Generate comprehensive deployment plan
        deployment_config = planner.generate_deployment_plan()
        
        # Save deployment plan and configuration files
        plan_path = planner.save_deployment_plan("production_deployment_plan")
        
        print("\n" + "=" * 55)
        print("✅ Production Deployment Plan Complete!")
        print(f"📋 Plan saved: {plan_path}")
        print("🔧 Configuration files generated in: configs/production/")
        
        # Print summary
        print(f"\n🎯 DEPLOYMENT PLAN SUMMARY:")
        print(f"Strategy: Docker Compose with Nginx Reverse Proxy")
        print(f"Security: Let's Encrypt SSL/TLS with security headers")
        print(f"Monitoring: Prometheus + Grafana with comprehensive alerting")
        print(f"Backup: Daily automated backups with disaster recovery")
        
        total_tasks = sum(len(cat['tasks']) for cat in deployment_config['deployment_checklist'])
        print(f"Total Tasks: {total_tasks} deployment tasks identified")
        
        print("\n🚀 Ready for production deployment!")
        
    except Exception as e:
        logger.error(f"Deployment planning failed: {e}")
        print(f"❌ Deployment planning failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
