#!/bin/bash
# Smart CloudOps AI - Complete Stack Deployment
# Deploys full application stack to AWS instances
#
# Environment Variables:
#   APP_SERVER          - Application server IP/hostname (default: 44.253.225.44)
#   MONITORING_SERVER   - Monitoring server IP/hostname (default: 54.186.188.202)
#   KEY_FILE            - SSH key file path (default: ~/.ssh/smartcloudops-ai-key.pem)
#   IMAGE_NAME          - Docker image name (default: smartcloudops-ai:latest)
#   AWS_REGION          - AWS region (default: us-west-2)
#   ENVIRONMENT         - Deployment environment (default: production)
#   APP_PORT            - Application port (default: 3000)
#   GRAFANA_PORT        - Grafana port (default: 3001)
#   PROMETHEUS_PORT     - Prometheus port (default: 9090)
#   NODE_EXPORTER_PORT  - Node Exporter port (default: 9100)
#
# Usage:
#   ./deploy_complete_stack.sh
#   # Or with custom configuration:
#   APP_SERVER=192.168.1.100 MONITORING_SERVER=192.168.1.101 ./deploy_complete_stack.sh

set -e

echo "🚀 Starting Complete Stack Deployment..."

# Load deployment configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils/load_deployment_config.sh"

# Set defaults for any missing variables
APP_SERVER="${APP_SERVER:-44.253.225.44}"
MONITORING_SERVER="${MONITORING_SERVER:-54.186.188.202}"
KEY_FILE="${KEY_FILE:-~/.ssh/smartcloudops-ai-key.pem}"
IMAGE_NAME="${IMAGE_NAME:-smartcloudops-ai:latest}"
AWS_REGION="${AWS_REGION:-us-west-2}"
ENVIRONMENT="${ENVIRONMENT:-production}"
APP_PORT="${APP_PORT:-3000}"
GRAFANA_PORT="${GRAFANA_PORT:-3001}"
PROMETHEUS_PORT="${PROMETHEUS_PORT:-9090}"
NODE_EXPORTER_PORT="${NODE_EXPORTER_PORT:-9100}"
SSH_USER="${SSH_USER:-ec2-user}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run command on remote server
run_remote() {
    local server=$1
    local command=$2
    print_status "Executing on $server: $command"
    ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no $SSH_USER@$server "$command"
}

# Deploy Application Server
deploy_application() {
    print_status "🏗️ Deploying Complete Application Stack..."
    
    # Save and transfer the Docker image
    print_status "Saving Docker image..."
    docker save $IMAGE_NAME | gzip > smartcloudops-ai.tar.gz
    
    # Transfer image to application server
    print_status "Transferring image to application server..."
    scp -i "$KEY_FILE" -o StrictHostKeyChecking=no smartcloudops-ai.tar.gz $SSH_USER@$APP_SERVER:/tmp/
    
    # Load and run the complete application
    run_remote $APP_SERVER "
        # Load Docker image
        docker load < /tmp/smartcloudops-ai.tar.gz
        
        # Stop any existing containers
        docker stop smartcloudops-flask || true
        docker rm smartcloudops-flask || true
        
        # Run complete application with all endpoints
        docker run -d \
            --name smartcloudops-flask \
            --restart=always \
            -p $APP_PORT:$APP_PORT \
            -e ENVIRONMENT=$ENVIRONMENT \
            -e AWS_REGION=$AWS_REGION \
            -v /var/log/smartcloudops:/app/logs \
            $IMAGE_NAME python app/main.py
            
        # Verify application is running
        sleep 10
        curl -f http://localhost:$APP_PORT/health || echo 'Application health check failed'
        curl -f http://localhost:$APP_PORT/status || echo 'Status endpoint failed'
    "
    
    # Clean up local image file
    rm -f smartcloudops-ai.tar.gz
}

# Deploy Monitoring Stack
deploy_monitoring() {
    print_status "📊 Deploying Monitoring Stack..."
    
    run_remote $MONITORING_SERVER "
        # Update system
        sudo yum update -y
        
        # Install Docker if not present
        if ! command -v docker &> /dev/null; then
            sudo yum install -y docker
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker ec2-user
        fi
        
        # Start Docker service
        sudo systemctl start docker
        
        # Stop existing containers
        docker stop grafana prometheus node-exporter || true
        docker rm grafana prometheus node-exporter || true
        
        # Create monitoring directories
        mkdir -p ~/monitoring/{prometheus,grafana}
        
        # Create Prometheus config
        cat > ~/monitoring/prometheus/prometheus.yml << 'EOF'
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
      - targets: ['$APP_SERVER:$APP_PORT']
    metrics_path: '/metrics'
EOF

        # Run Prometheus
        docker run -d \
            --name prometheus \
            --restart=always \
            -p $PROMETHEUS_PORT:9090 \
            -v ~/monitoring/prometheus:/etc/prometheus \
            prom/prometheus:latest \
            --config.file=/etc/prometheus/prometheus.yml \
            --storage.tsdb.path=/prometheus \
            --web.console.libraries=/etc/prometheus/console_libraries \
            --web.console.templates=/etc/prometheus/consoles \
            --web.enable-lifecycle
        
        # Run Node Exporter
        docker run -d \
            --name node-exporter \
            --restart=always \
            -p $NODE_EXPORTER_PORT:9100 \
            -v '/proc:/host/proc:ro' \
            -v '/sys:/host/sys:ro' \
            -v '/:/rootfs:ro' \
            prom/node-exporter:latest \
            --path.procfs=/host/proc \
            --path.sysfs=/host/sys \
            --collector.filesystem.mount-points-exclude='^/(sys|proc|dev|host|etc)(\$|/)'
        
        # Run Grafana
        docker run -d \
            --name grafana \
            --restart=always \
            -p $GRAFANA_PORT:3000 \
            -e GF_SECURITY_ADMIN_PASSWORD=admin \
            -v grafana-storage:/var/lib/grafana \
            grafana/grafana:latest
        
        # Wait for services to start
        sleep 30
        
        # Verify services
        curl -f http://localhost:$PROMETHEUS_PORT/-/healthy || echo 'Prometheus health check failed'
        curl -f http://localhost:$NODE_EXPORTER_PORT/metrics | head -5 || echo 'Node Exporter metrics failed'
        curl -f http://localhost:$GRAFANA_PORT/login || echo 'Grafana login page failed'
    "
}

# Main deployment function
main() {
    print_status "🚀 Starting Complete Smart CloudOps AI Deployment"
    
    # Check if we can reach the servers
    print_status "🔍 Checking server connectivity..."
    if ! ping -c 1 $APP_SERVER &> /dev/null; then
        print_error "Cannot reach application server $APP_SERVER"
        exit 1
    fi
    
    if ! ping -c 1 $MONITORING_SERVER &> /dev/null; then
        print_error "Cannot reach monitoring server $MONITORING_SERVER"
        exit 1
    fi
    
    print_status "✅ Both servers are reachable"
    
    # Deploy components
    deploy_application
    deploy_monitoring
    
    # Final verification
    print_status "🔍 Final Verification..."
    sleep 30
    
    print_status "Testing Application Server endpoints:"
    curl -f http://$APP_SERVER:$APP_PORT/health && print_status "✅ Health endpoint working" || print_error "❌ Health endpoint failed"
    curl -f http://$APP_SERVER:$APP_PORT/status && print_status "✅ Status endpoint working" || print_error "❌ Status endpoint failed"
    curl -f http://$APP_SERVER:$APP_PORT/metrics && print_status "✅ Metrics endpoint working" || print_error "❌ Metrics endpoint failed"
    
    print_status "Testing Monitoring Server:"
    curl -f http://$MONITORING_SERVER:$PROMETHEUS_PORT/-/healthy && print_status "✅ Prometheus healthy" || print_error "❌ Prometheus failed"
    curl -f http://$MONITORING_SERVER:$NODE_EXPORTER_PORT/metrics && print_status "✅ Node Exporter working" || print_error "❌ Node Exporter failed"
    curl -f http://$MONITORING_SERVER:$GRAFANA_PORT/login && print_status "✅ Grafana accessible" || print_error "❌ Grafana failed"
    
    print_status "🎉 Deployment completed!"
    print_status "📍 Service URLs:"
    print_status "   Flask App: http://$APP_SERVER:$APP_PORT"
    print_status "   Grafana:   http://$MONITORING_SERVER:$GRAFANA_PORT (admin/admin)"
    print_status "   Prometheus: http://$MONITORING_SERVER:$PROMETHEUS_PORT"
    print_status "   Node Exporter: http://$MONITORING_SERVER:$NODE_EXPORTER_PORT/metrics"
}

# Run main function
main "$@"
