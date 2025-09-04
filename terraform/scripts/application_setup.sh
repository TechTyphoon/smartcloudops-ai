#!/bin/bash
# Smart CloudOps AI - Application Server Setup Script
# This script sets up the application server with Docker and Node Exporter

set -e

# Update system
yum update -y

# Install required packages
yum install -y wget curl docker git python3 python3-pip

# Start and enable Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directories
mkdir -p /opt/smartcloudops/{app,logs,data}
chown -R ec2-user:ec2-user /opt/smartcloudops

# Install Node Exporter
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/

# Create node_exporter user
useradd --no-create-home --shell /bin/false node_exporter

# Create systemd service file for Node Exporter
cat > /etc/systemd/system/node_exporter.service << 'EOF'
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# Enable and start node_exporter
systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter

# Install Python dependencies
pip3 install --upgrade pip
pip3 install flask gunicorn prometheus-client

# Create basic Flask application structure
cat > /opt/smartcloudops/app/main.py << 'EOF'
#!/usr/bin/env python3
"""
Smart CloudOps AI - Basic Flask Application
This is a placeholder application that will be expanded in Phase 2
"""

import time
import logging
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('flask_requests_total', 'Total Flask HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('flask_request_duration_seconds', 'Flask HTTP request latency')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    
    if hasattr(request, 'start_time'):
        REQUEST_LATENCY.observe(time.time() - request.start_time)
    
    return response

@app.route('/')
def home():
    return jsonify({
        "message": "Smart CloudOps AI - Flask Application",
        "status": "running",
        "version": "1.0.0-alpha"
    })

@app.route('/status')
def status():
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": "placeholder"
    })

@app.route('/query', methods=['POST'])
def query():
    """Placeholder for ChatOps queries (Phase 5)"""
    data = request.get_json()
    return jsonify({
        "message": "ChatOps functionality will be implemented in Phase 5",
        "query": data.get('query', 'No query provided') if data else 'No data provided'
    })

@app.route('/logs')
def logs():
    """Placeholder for log retrieval (Phase 4)"""
    return jsonify({
        "message": "Log retrieval functionality will be implemented in Phase 4",
        "logs": []
    })

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    logger.info("Starting Smart CloudOps AI Flask Application")
    app.run(host='0.0.0.0', port=3000, debug=False)
EOF

# Create systemd service for the Flask app
cat > /etc/systemd/system/smartcloudops-app.service << 'EOF'
[Unit]
Description=Smart CloudOps AI Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/smartcloudops/app
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown ec2-user:ec2-user /opt/smartcloudops/app/main.py
chmod +x /opt/smartcloudops/app/main.py

# Enable services
systemctl daemon-reload
systemctl enable smartcloudops-app

# Create startup script
cat > /home/ec2-user/start_application.sh << 'EOF'
#!/bin/bash
systemctl start smartcloudops-app
echo "Application started!"
echo "Application URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "Status endpoint: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000/status"
echo "Metrics endpoint: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000/metrics"
EOF

chmod +x /home/ec2-user/start_application.sh
chown ec2-user:ec2-user /home/ec2-user/start_application.sh

# Log completion
echo "Application setup completed at $(date)" >> /var/log/application-setup.log