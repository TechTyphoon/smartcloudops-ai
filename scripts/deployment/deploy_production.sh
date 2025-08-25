#!/bin/bash

# SmartCloudOps AI Production Deployment Script
# Phase 7: Production Launch & Feedback
# Supports AWS EC2, DigitalOcean, and other cloud providers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"
DOMAIN_NAME="${DOMAIN_NAME:-yourdomain.com}"
SSL_EMAIL="${SSL_EMAIL:-admin@yourdomain.com}"

# Logging
LOG_FILE="$PROJECT_ROOT/logs/deployment_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$PROJECT_ROOT/logs"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check if running as root or with sudo
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root. Consider using a non-root user with sudo privileges."
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running. Please start Docker first."
    fi
    
    # Check available disk space (at least 10GB)
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 10 ]; then
        error "Insufficient disk space. Need at least 10GB, available: ${AVAILABLE_SPACE}GB"
    fi
    
    # Check available memory (at least 4GB)
    AVAILABLE_MEMORY=$(free -g | awk 'NR==2 {print $7}')
    if [ "$AVAILABLE_MEMORY" -lt 4 ]; then
        warn "Low memory available: ${AVAILABLE_MEMORY}GB. Recommended: 8GB+"
    fi
    
    log "Prerequisites check completed successfully"
}

# Function to setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log "Creating .env file from template..."
        cp "$PROJECT_ROOT/env.template" "$PROJECT_ROOT/.env"
        
        # Generate secure passwords
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        REDIS_PASSWORD=$(openssl rand -base64 32)
        JWT_SECRET_KEY=$(openssl rand -base64 64)
        
        # Update .env file with generated values
        sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" "$PROJECT_ROOT/.env"
        sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" "$PROJECT_ROOT/.env"
        sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" "$PROJECT_ROOT/.env"
        sed -i "s/DOMAIN_NAME=.*/DOMAIN_NAME=$DOMAIN_NAME/" "$PROJECT_ROOT/.env"
        sed -i "s/SSL_EMAIL=.*/SSL_EMAIL=$SSL_EMAIL/" "$PROJECT_ROOT/.env"
        
        log "Environment variables configured. Please review and update .env file as needed."
    else
        log "Environment file already exists. Skipping setup."
    fi
}

# Function to create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/backups"
    mkdir -p "$PROJECT_ROOT/configs/ssl"
    mkdir -p "$PROJECT_ROOT/data"
    
    # Set proper permissions
    chmod 755 "$PROJECT_ROOT/logs"
    chmod 755 "$PROJECT_ROOT/backups"
    chmod 700 "$PROJECT_ROOT/configs/ssl"
    chmod 755 "$PROJECT_ROOT/data"
    
    log "Directories created successfully"
}

# Function to setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    if [ "$DOMAIN_NAME" = "yourdomain.com" ]; then
        warn "Using default domain name. SSL setup will be skipped."
        warn "Please update DOMAIN_NAME in .env file and run this script again for SSL setup."
        return 0
    fi
    
    # Check if certificates already exist
    if [ -f "$PROJECT_ROOT/configs/ssl/live/$DOMAIN_NAME/fullchain.pem" ]; then
        log "SSL certificates already exist. Skipping setup."
        return 0
    fi
    
    # Create temporary nginx configuration for SSL challenge
    cat > "$PROJECT_ROOT/configs/nginx-ssl.conf" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF
    
    # Start nginx for SSL challenge
    log "Starting nginx for SSL certificate challenge..."
    docker run -d --name nginx-ssl \
        -p 80:80 \
        -v "$PROJECT_ROOT/configs/nginx-ssl.conf:/etc/nginx/conf.d/default.conf" \
        -v "$PROJECT_ROOT/configs/ssl:/etc/letsencrypt" \
        -v "$PROJECT_ROOT/logs:/var/log/nginx" \
        nginx:alpine
    
    # Wait for nginx to start
    sleep 5
    
    # Obtain SSL certificate
    log "Obtaining SSL certificate from Let's Encrypt..."
    docker run --rm \
        -v "$PROJECT_ROOT/configs/ssl:/etc/letsencrypt" \
        -v "$PROJECT_ROOT/logs:/var/log/letsencrypt" \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$SSL_EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN_NAME"
    
    # Stop temporary nginx
    docker stop nginx-ssl
    docker rm nginx-ssl
    
    # Clean up temporary config
    rm -f "$PROJECT_ROOT/configs/nginx-ssl.conf"
    
    log "SSL certificates setup completed"
}

# Function to build and start services
deploy_services() {
    log "Deploying SmartCloudOps AI services..."
    
    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" pull
    
    # Build application image
    log "Building application image..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" build app
    
    # Start services
    log "Starting services..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    timeout=300  # 5 minutes timeout
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" ps | grep -q "healthy"; then
            log "All services are healthy!"
            break
        fi
        
        sleep 10
        counter=$((counter + 10))
        
        if [ $counter -ge $timeout ]; then
            warn "Timeout waiting for services to be healthy. Checking service status..."
            docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" ps
            docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" logs --tail=50
        fi
    done
}

# Function to initialize database
initialize_database() {
    log "Initializing database..."
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    timeout=60
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T postgres pg_isready -U smartcloudops; then
            log "Database is ready!"
            break
        fi
        
        sleep 5
        counter=$((counter + 5))
    done
    
    if [ $counter -ge $timeout ]; then
        error "Database failed to start within timeout"
    fi
    
    # Run database initialization
    log "Running database initialization..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T app python3 -c "
import sys
sys.path.append('/app')
from app.database import init_db, seed_initial_data
init_db()
seed_initial_data()
print('Database initialized successfully')
"
    
    log "Database initialization completed"
}

# Function to setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Wait for Prometheus to be ready
    log "Waiting for Prometheus to be ready..."
    timeout=60
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost:9090/-/healthy &> /dev/null; then
            log "Prometheus is ready!"
            break
        fi
        
        sleep 5
        counter=$((counter + 5))
    done
    
    # Wait for Grafana to be ready
    log "Waiting for Grafana to be ready..."
    timeout=60
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost:3000/api/health &> /dev/null; then
            log "Grafana is ready!"
            break
        fi
        
        sleep 5
        counter=$((counter + 5))
    done
    
    log "Monitoring setup completed"
}

# Function to run health checks
run_health_checks() {
    log "Running health checks..."
    
    # Check application health
    if curl -f http://localhost/health &> /dev/null; then
        log "✓ Application is healthy"
    else
        error "✗ Application health check failed"
    fi
    
    # Check API endpoints
    if curl -f http://localhost/api/health &> /dev/null; then
        log "✓ API endpoints are accessible"
    else
        error "✗ API endpoints health check failed"
    fi
    
    # Check Grafana
    if curl -f http://localhost/grafana/api/health &> /dev/null; then
        log "✓ Grafana is accessible"
    else
        warn "✗ Grafana health check failed"
    fi
    
    # Check Prometheus
    if curl -f http://localhost/prometheus/-/healthy &> /dev/null; then
        log "✓ Prometheus is accessible"
    else
        warn "✗ Prometheus health check failed"
    fi
    
    log "Health checks completed"
}

# Function to display deployment information
display_deployment_info() {
    log "Deployment completed successfully!"
    echo
    echo -e "${BLUE}=== SmartCloudOps AI Production Deployment ===${NC}"
    echo
    echo -e "${GREEN}Application URLs:${NC}"
    echo -e "  Main Application: ${YELLOW}https://$DOMAIN_NAME${NC}"
    echo -e "  API Documentation: ${YELLOW}https://$DOMAIN_NAME/api/docs${NC}"
    echo -e "  Grafana Dashboard: ${YELLOW}https://$DOMAIN_NAME/grafana${NC}"
    echo -e "  Prometheus: ${YELLOW}https://$DOMAIN_NAME/prometheus${NC}"
    echo
    echo -e "${GREEN}Default Credentials:${NC}"
    echo -e "  Admin User: ${YELLOW}admin${NC}"
    echo -e "  Admin Password: ${YELLOW}Set via DEFAULT_ADMIN_PASSWORD environment variable${NC}"
    echo -e "  Demo User: ${YELLOW}demo${NC}"
    echo -e "  Demo Password: ${YELLOW}demo123${NC}"
    echo
    echo -e "${GREEN}Important Notes:${NC}"
    echo -e "  • Set DEFAULT_ADMIN_PASSWORD environment variable"
    echo -e "  • Review and update environment variables in .env file"
    echo -e "  • Monitor logs: ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f${NC}"
    echo -e "  • Backup database regularly"
    echo -e "  • SSL certificates will auto-renew"
    echo
    echo -e "${GREEN}Useful Commands:${NC}"
    echo -e "  View logs: ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f app${NC}"
    echo -e "  Restart services: ${YELLOW}docker-compose -f docker-compose.prod.yml restart${NC}"
    echo -e "  Stop services: ${YELLOW}docker-compose -f docker-compose.prod.yml down${NC}"
    echo -e "  Update services: ${YELLOW}docker-compose -f docker-compose.prod.yml pull && docker-compose -f docker-compose.prod.yml up -d${NC}"
    echo
}

# Function to cleanup on error
cleanup() {
    error "Deployment failed. Cleaning up..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" down --remove-orphans
    docker system prune -f
}

# Main deployment function
main() {
    log "Starting SmartCloudOps AI production deployment..."
    log "Deployment environment: $DEPLOYMENT_ENV"
    log "Domain name: $DOMAIN_NAME"
    log "SSL email: $SSL_EMAIL"
    log "Log file: $LOG_FILE"
    
    # Set trap for cleanup on error
    trap cleanup ERR
    
    # Run deployment steps
    check_prerequisites
    setup_environment
    create_directories
    setup_ssl
    deploy_services
    initialize_database
    setup_monitoring
    run_health_checks
    display_deployment_info
    
    log "Production deployment completed successfully!"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
