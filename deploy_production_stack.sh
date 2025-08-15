#!/bin/bash
# deploy_production_stack.sh - Production Stack Deployment Automation
# Smart CloudOps AI v3.0.0 - Complete Production Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
PROJECT_NAME="smartcloudops"
VERSION="3.0.0"

# Functions
print_step() {
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}🚀 $1${NC}"
    echo -e "${BLUE}===================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    print_step "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose: $(docker-compose --version)"
    
    # Check required files
    required_files=("$COMPOSE_FILE" "Dockerfile.production" "nginx.conf" "prometheus.yml" "grafana-datasources.yml")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    print_success "All required configuration files present"
}

setup_directories() {
    print_step "Setting Up Data Directories"
    
    # Create data directories
    directories=(
        "data/postgres"
        "data/redis"
        "data/app"
        "data/prometheus"
        "data/grafana"
        "logs"
        "logs/nginx"
        "ssl"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_success "Created directory: $dir"
    done
    
    # Set proper permissions
    sudo chown -R $USER:$USER data logs
    chmod -R 755 data logs
}

generate_ssl_certificates() {
    print_step "Generating SSL Certificates"
    
    if [[ ! -f "ssl/nginx.crt" || ! -f "ssl/nginx.key" ]]; then
        print_warning "Generating self-signed SSL certificates for development"
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/nginx.key \
            -out ssl/nginx.crt \
            -subj "/C=US/ST=State/L=City/O=SmartCloudOps/CN=smartcloudops.local" \
            2>/dev/null
            
        chmod 600 ssl/nginx.key
        chmod 644 ssl/nginx.crt
        print_success "SSL certificates generated"
    else
        print_success "SSL certificates already exist"
    fi
}

setup_environment() {
    print_step "Setting Up Environment"
    
    # Create .env file if not exists
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
# Smart CloudOps AI Production Environment
PROJECT_NAME=smartcloudops
VERSION=$VERSION
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')

# Security
SECRET_KEY=smartcloudops_production_secret_$(openssl rand -hex 16)

# Database
POSTGRES_PASSWORD=cloudops123
REDIS_PASSWORD=cloudops123

# Monitoring
GRAFANA_ADMIN_PASSWORD=cloudops123
EOF
        print_success "Environment file created"
    else
        print_success "Environment file already exists"
    fi
}

build_images() {
    print_step "Building Docker Images"
    
    # Set build arguments
    export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    export VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')
    
    # Build with no cache for production
    docker-compose -f $COMPOSE_FILE build --no-cache --parallel
    print_success "Docker images built successfully"
}

deploy_stack() {
    print_step "Deploying Production Stack"
    
    # Stop existing services
    docker-compose -f $COMPOSE_FILE down --remove-orphans 2>/dev/null || true
    
    # Start services
    docker-compose -f $COMPOSE_FILE up -d
    print_success "Production stack deployed"
}

verify_deployment() {
    print_step "Verifying Deployment"
    
    # Wait for services to be ready
    print_warning "Waiting for services to start..."
    sleep 30
    
    # Check service health
    services=("postgres" "redis" "app" "nginx" "prometheus" "grafana")
    
    for service in "${services[@]}"; do
        if docker-compose -f $COMPOSE_FILE ps $service | grep -q "Up"; then
            print_success "Service $service: Running"
        else
            print_error "Service $service: Not running"
            docker-compose -f $COMPOSE_FILE logs --tail=20 $service
            return 1
        fi
    done
    
    # Test application endpoints
    print_warning "Testing application endpoints..."
    
    # Wait for application to be fully ready
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:5000/health > /dev/null; then
            print_success "Application health check: OK"
            break
        else
            print_warning "Attempt $attempt/$max_attempts: Application not ready yet..."
            sleep 5
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Application failed to start within expected time"
        return 1
    fi
    
    # Test other endpoints
    endpoints=("http://localhost:5000/status" "http://localhost:3000" "http://localhost:9090")
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s "$endpoint" > /dev/null; then
            print_success "Endpoint $endpoint: OK"
        else
            print_warning "Endpoint $endpoint: Not responding"
        fi
    done
}

show_deployment_info() {
    print_step "Deployment Information"
    
    echo -e "${GREEN}🎉 Smart CloudOps AI Production Stack Deployed Successfully!${NC}\n"
    
    echo -e "${YELLOW}Access Points:${NC}"
    echo "🌐 Application:     http://localhost:5000"
    echo "🌐 Application SSL: https://localhost (with self-signed cert)"
    echo "📊 Grafana:        http://localhost:3000 (admin/cloudops123)"
    echo "📈 Prometheus:     http://localhost:9090"
    echo "🐘 PostgreSQL:     localhost:5432 (smartcloudops/cloudops123)"
    echo "🔴 Redis:          localhost:6379 (password: cloudops123)"
    
    echo -e "\n${YELLOW}Management Commands:${NC}"
    echo "📋 View logs:       docker-compose -f $COMPOSE_FILE logs -f"
    echo "⏹️  Stop stack:      docker-compose -f $COMPOSE_FILE down"
    echo "🔄 Restart stack:   docker-compose -f $COMPOSE_FILE restart"
    echo "📊 View status:     docker-compose -f $COMPOSE_FILE ps"
    
    echo -e "\n${YELLOW}Health Check URLs:${NC}"
    echo "🏥 App Health:      curl http://localhost:5000/health"
    echo "🏥 DB Status:       curl http://localhost:5000/database/status"
    echo "🏥 Nginx Status:    curl http://localhost/nginx-health"
    
    echo -e "\n${YELLOW}Version Information:${NC}"
    echo "📦 Version: $VERSION"
    echo "🔨 Build Date: $(date)"
    echo "🏷️  Git Ref: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
}

cleanup_on_error() {
    print_error "Deployment failed! Cleaning up..."
    docker-compose -f $COMPOSE_FILE down --remove-orphans 2>/dev/null || true
    exit 1
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "██████╗ ███╗   ███╗ █████╗ ██████╗ ████████╗ ██████╗██╗      ██████╗ ██╗   ██╗██████╗  ██████╗ ██████╗ ███████╗"
    echo "██╔═══██╗████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗██╔═══██╗██╔══██╗██╔════╝"
    echo "██║   ██║██╔████╔██║███████║██████╔╝   ██║   ██║     ██║     ██║   ██║██║   ██║██║  ██║██║   ██║██████╔╝███████╗"
    echo "██║   ██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   ██║     ██║     ██║   ██║██║   ██║██║  ██║██║   ██║██╔═══╝ ╚════██║"
    echo "╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝╚██████╔╝██║     ███████║"
    echo " ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚══════╝"
    echo -e "${NC}\n"
    echo -e "${GREEN}Smart CloudOps AI v$VERSION - Production Stack Deployment${NC}"
    echo -e "${GREEN}================================================================${NC}\n"
    
    # Trap errors and cleanup
    trap cleanup_on_error ERR
    
    # Execute deployment steps
    check_prerequisites
    setup_directories
    generate_ssl_certificates
    setup_environment
    build_images
    deploy_stack
    verify_deployment
    show_deployment_info
    
    print_success "Production deployment completed successfully! 🎉"
}

# Run main function
main "$@"
