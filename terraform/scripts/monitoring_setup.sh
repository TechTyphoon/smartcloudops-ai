#!/bin/bash
# Smart CloudOps AI - Monitoring Server Setup Script
# This script sets up Prometheus and Grafana on the monitoring instance

set -e

# Update system
yum update -y

# Install required packages
yum install -y wget curl docker git

# Start and enable Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create monitoring directories
mkdir -p /opt/monitoring/{prometheus,grafana}
mkdir -p /opt/monitoring/prometheus/{config,data}
mkdir -p /opt/monitoring/grafana/{config,data,dashboards,datasources}

# Set permissions
chown -R ec2-user:ec2-user /opt/monitoring

# Create Prometheus configuration
cat > /opt/monitoring/prometheus/config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter-monitoring'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'node-exporter-application'
    static_configs:
      - targets: ['PLACEHOLDER_APP_IP:9100']

  - job_name: 'flask-app'
    static_configs:
      - targets: ['PLACEHOLDER_APP_IP:3000']
    metrics_path: '/metrics'
EOF

# Download configuration files from GitHub (or create basic ones)
# Basic Prometheus configuration
cat > /opt/monitoring/prometheus/config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter-monitoring'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'node-exporter-application'
    static_configs:
      - targets: ['PLACEHOLDER_APP_IP:9100']

  - job_name: 'flask-application'
    static_configs:
      - targets: ['PLACEHOLDER_APP_IP:3000']
    metrics_path: '/metrics'
EOF

# Basic Grafana data source configuration
cat > /opt/monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    editable: true
EOF

# Basic alert rules
cat > /opt/monitoring/prometheus/config/alert_rules.yml << 'EOF'
groups:
  - name: smartcloudops.rules
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "High CPU usage detected on {{ $labels.instance }}"

      - alert: InstanceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} is down"
EOF

# Create Docker Compose file for monitoring stack
cat > /opt/monitoring/docker-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/config:/etc/prometheus
      - ./prometheus/data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    volumes:
      - ./grafana/data:/var/lib/grafana
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_ADMIN_USER=admin
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
EOF

# Install Node Exporter as systemd service (backup)
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/

# Create node_exporter user
useradd --no-create-home --shell /bin/false node_exporter

# Create systemd service file
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

# Create startup script
cat > /home/ec2-user/start_monitoring.sh << 'EOF'
#!/bin/bash
cd /opt/monitoring
docker-compose up -d
echo "Monitoring stack started!"
echo "Prometheus: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9090"
echo "Grafana: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3001"
echo "Default Grafana credentials: admin/admin"
EOF

chmod +x /home/ec2-user/start_monitoring.sh
chown ec2-user:ec2-user /home/ec2-user/start_monitoring.sh

# Log completion
echo "Monitoring setup completed at $(date)" >> /var/log/monitoring-setup.log