#!/bin/bash
echo "🔧 Deploying Monitoring Server..."

# Stop instance, update user data, and start
aws ec2 stop-instances --instance-ids i-07c69200a0e2ce609
aws ec2 wait instance-stopped --instance-ids i-07c69200a0e2ce609

# Create user data script
cat > /tmp/monitoring_userdata.sh << 'EOF'
#!/bin/bash
# Smart CloudOps AI - Monitoring Server Setup
yum update -y
yum install -y docker

# Start Docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# Create monitoring directories
mkdir -p /opt/monitoring/{prometheus,grafana}

# Create Prometheus config
cat > /opt/monitoring/prometheus/prometheus.yml << 'PROMEOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
      
  - job_name: 'flask-app'
    static_configs:
      - targets: ['44.253.225.44:3000']
    metrics_path: '/metrics'
PROMEOF

# Start Prometheus
docker run -d \
    --name prometheus \
    --restart=always \
    -p 9090:9090 \
    -v /opt/monitoring/prometheus:/etc/prometheus \
    prom/prometheus:latest \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/prometheus \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.console.templates=/etc/prometheus/consoles \
    --web.enable-lifecycle

# Start Node Exporter
docker run -d \
    --name node-exporter \
    --restart=always \
    -p 9100:9100 \
    -v '/proc:/host/proc:ro' \
    -v '/sys:/host/sys:ro' \
    -v '/:/rootfs:ro' \
    prom/node-exporter:latest \
    --path.procfs=/host/proc \
    --path.sysfs=/host/sys \
    --collector.filesystem.mount-points-exclude='^/(sys|proc|dev|host|etc)($|/)'

# Start Grafana
docker run -d \
    --name grafana \
    --restart=always \
    -p 3001:3000 \
    -e GF_SECURITY_ADMIN_PASSWORD=admin \
    -v grafana-storage:/var/lib/grafana \
    grafana/grafana:latest

# Log completion
echo "Monitoring services deployed at $(date)" >> /var/log/deployment.log
EOF

# Update user data
aws ec2 modify-instance-attribute --instance-id i-07c69200a0e2ce609 --user-data file:///tmp/monitoring_userdata.sh

# Start instance
aws ec2 start-instances --instance-ids i-07c69200a0e2ce609
aws ec2 wait instance-running --instance-ids i-07c69200a0e2ce609

echo "✅ Monitoring server deployment initiated"
