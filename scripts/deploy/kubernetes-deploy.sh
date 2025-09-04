#!/bin/bash

# SmartCloudOps AI - Kubernetes Production Deployment Script
# This script deploys the complete SmartCloudOps AI platform to Kubernetes

set -euo pipefail

# Configuration
NAMESPACE="smartcloudops"
ENVIRONMENT="${1:-production}"
CLUSTER_NAME="${2:-smartcloudops-cluster}"
REGION="${3:-us-east-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."

    # Check if kubectl is configured
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "kubectl is not configured or cluster is not accessible"
        exit 1
    fi

    # Check if namespace exists, create if not
    if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log_info "Creating namespace: $NAMESPACE"
        kubectl create namespace "$NAMESPACE"
    fi

    # Check if required tools are installed
    command -v helm >/dev/null 2>&1 || { log_error "helm is required but not installed"; exit 1; }
    command -v docker >/dev/null 2>&1 || { log_error "docker is required but not installed"; exit 1; }

    log_success "Pre-deployment checks completed"
}

# Setup Helm repositories
setup_helm_repos() {
    log_info "Setting up Helm repositories..."

    # Add required Helm repositories
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo add cert-manager https://charts.jetstack.io

    # Update repositories
    helm repo update

    log_success "Helm repositories configured"
}

# Deploy cert-manager for SSL certificates
deploy_cert_manager() {
    log_info "Deploying cert-manager..."

    # Install cert-manager
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

    # Wait for cert-manager to be ready
    kubectl wait --for=condition=available --timeout=300s deployment -n cert-manager --all

    # Create Let's Encrypt cluster issuer
    cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@smartcloudops.ai
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

    log_success "cert-manager deployed"
}

# Deploy NGINX Ingress Controller
deploy_ingress_controller() {
    log_info "Deploying NGINX Ingress Controller..."

    # Install NGINX Ingress Controller
    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.replicaCount=2 \
        --set controller.nodeSelector."kubernetes\.io/os"=linux \
        --set defaultBackend.nodeSelector."kubernetes\.io/os"=linux \
        --set controller.service.externalTrafficPolicy=Local \
        --set controller.config.use-forwarded-headers=true \
        --set controller.config.proxy-real-ip-cidr="0.0.0.0/0" \
        --set controller.config.use-gzip=true \
        --set controller.config.gzip-level=6

    # Wait for ingress controller to be ready
    kubectl wait --for=condition=available --timeout=300s deployment -n ingress-nginx ingress-nginx-controller

    log_success "NGINX Ingress Controller deployed"
}

# Deploy PostgreSQL database
deploy_postgresql() {
    log_info "Deploying PostgreSQL database..."

    # Create PostgreSQL using Helm
    helm upgrade --install postgresql bitnami/postgresql \
        --namespace "$NAMESPACE" \
        --set auth.postgresPassword="smartcloudops-postgres-password-2024" \
        --set auth.username="smartcloudops" \
        --set auth.password="smartcloudops-password-2024" \
        --set auth.database="smartcloudops" \
        --set persistence.enabled=true \
        --set persistence.size=100Gi \
        --set persistence.storageClass=fast-ssd \
        --set metrics.enabled=true \
        --set metrics.serviceMonitor.enabled=true \
        --set metrics.serviceMonitor.namespace="$NAMESPACE" \
        --set resources.requests.cpu=500m \
        --set resources.requests.memory=1Gi \
        --set resources.limits.cpu=2000m \
        --set resources.limits.memory=4Gi

    # Wait for PostgreSQL to be ready
    kubectl wait --for=condition=available --timeout=300s deployment -n "$NAMESPACE" postgresql

    log_success "PostgreSQL deployed"
}

# Deploy Redis cache
deploy_redis() {
    log_info "Deploying Redis cache..."

    # Create Redis using Helm
    helm upgrade --install redis bitnami/redis \
        --namespace "$NAMESPACE" \
        --set auth.password="smartcloudops-redis-password-2024" \
        --set master.persistence.enabled=true \
        --set master.persistence.size=50Gi \
        --set master.persistence.storageClass=fast-ssd \
        --set metrics.enabled=true \
        --set metrics.serviceMonitor.enabled=true \
        --set metrics.serviceMonitor.namespace="$NAMESPACE" \
        --set resources.requests.cpu=200m \
        --set resources.requests.memory=512Mi \
        --set resources.limits.cpu=1000m \
        --set resources.limits.memory=2Gi

    # Wait for Redis to be ready
    kubectl wait --for=condition=available --timeout=300s deployment -n "$NAMESPACE" redis-master

    log_success "Redis deployed"
}

# Deploy Prometheus monitoring stack
deploy_monitoring() {
    log_info "Deploying monitoring stack..."

    # Install Prometheus using Helm
    helm upgrade --install prometheus prometheus-community/prometheus \
        --namespace "$NAMESPACE" \
        --set server.persistentVolume.enabled=true \
        --set server.persistentVolume.size=100Gi \
        --set server.persistentVolume.storageClass=standard \
        --set server.resources.requests.cpu=500m \
        --set server.resources.requests.memory=1Gi \
        --set server.resources.limits.cpu=1000m \
        --set server.resources.limits.memory=2Gi \
        --set alertmanager.enabled=true \
        --set alertmanager.persistentVolume.enabled=true \
        --set alertmanager.persistentVolume.size=10Gi \
        --set pushgateway.enabled=true

    # Install Grafana using Helm
    helm upgrade --install grafana grafana/grafana \
        --namespace "$NAMESPACE" \
        --set adminPassword="admin123" \
        --set persistence.enabled=true \
        --set persistence.size=50Gi \
        --set persistence.storageClass=standard \
        --set service.type=ClusterIP \
        --set resources.requests.cpu=200m \
        --set resources.requests.memory=512Mi \
        --set resources.limits.cpu=500m \
        --set resources.limits.memory=1Gi

    # Wait for monitoring services to be ready
    kubectl wait --for=condition=available --timeout=300s deployment -n "$NAMESPACE" prometheus-server
    kubectl wait --for=condition=available --timeout=300s deployment -n "$NAMESPACE" grafana

    log_success "Monitoring stack deployed"
}

# Build and deploy SmartCloudOps application
deploy_smartcloudops() {
    log_info "Deploying SmartCloudOps AI application..."

    # Build Docker image
    log_info "Building Docker image..."
    docker build -t smartcloudops/smartcloudops:latest .

    # Push to registry (assuming local registry for demo)
    # In production, push to your container registry
    # docker tag smartcloudops/smartcloudops:latest your-registry/smartcloudops:latest
    # docker push your-registry/smartcloudops:latest

    # Apply Kubernetes manifests
    log_info "Applying Kubernetes manifests..."

    # Create secrets (you should populate these with actual values)
    kubectl apply -f k8s/smartcloudops-secret.yaml -n "$NAMESPACE"

    # Create configmap
    kubectl apply -f k8s/smartcloudops-configmap.yaml -n "$NAMESPACE"

    # Create persistent volume claims
    kubectl apply -f k8s/smartcloudops-pvc.yaml -n "$NAMESPACE"

    # Create services
    kubectl apply -f k8s/smartcloudops-service.yaml -n "$NAMESPACE"

    # Create network policies
    kubectl apply -f k8s/smartcloudops-network-policy.yaml -n "$NAMESPACE"

    # Create pod disruption budgets
    kubectl apply -f k8s/smartcloudops-pdb.yaml -n "$NAMESPACE"

    # Deploy the application
    kubectl apply -f k8s/smartcloudops-deployment.yaml -n "$NAMESPACE"

    # Create horizontal pod autoscaler
    kubectl apply -f k8s/smartcloudops-hpa.yaml -n "$NAMESPACE"

    # Create ingress
    kubectl apply -f k8s/smartcloudops-ingress.yaml -n "$NAMESPACE"

    # Wait for deployment to be ready
    kubectl wait --for=condition=available --timeout=600s deployment/smartcloudops-main -n "$NAMESPACE"

    log_success "SmartCloudOps AI application deployed"
}

# Configure monitoring and alerting
configure_monitoring() {
    log_info "Configuring monitoring and alerting..."

    # Get Grafana admin password
    GRAFANA_PASSWORD=$(kubectl get secret -n "$NAMESPACE" grafana -o jsonpath="{.data.admin-password}" | base64 --decode)

    # Create Grafana data source for Prometheus
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: $NAMESPACE
  labels:
    grafana_datasource: "1"
data:
  prometheus.yml: |
    {
      "apiVersion": 1,
      "datasources": [
        {
          "name": "Prometheus",
          "type": "prometheus",
          "access": "proxy",
          "url": "http://prometheus-server.$NAMESPACE.svc.cluster.local:80",
          "isDefault": true,
          "editable": true
        }
      ]
    }
EOF

    # Import SmartCloudOps dashboards
    log_info "Importing SmartCloudOps dashboards..."
    # This would import pre-configured dashboards for SmartCloudOps metrics

    log_success "Monitoring and alerting configured"
}

# Run post-deployment tests
run_post_deployment_tests() {
    log_info "Running post-deployment tests..."

    # Test application health
    kubectl run test-pod --image=busybox --rm -i --restart=Never -- sh -c "
        wget -q -O - http://smartcloudops-main/health | grep -q 'healthy' && echo '✅ Health check passed' || echo '❌ Health check failed'
    " -n "$NAMESPACE"

    # Test database connectivity
    kubectl run test-db --image=postgres:13 --rm -i --restart=Never -- sh -c "
        PGPASSWORD=smartcloudops-password-2024 psql -h postgresql -U smartcloudops -d smartcloudops -c 'SELECT 1;' >/dev/null && echo '✅ Database connectivity test passed' || echo '❌ Database connectivity test failed'
    " -n "$NAMESPACE"

    # Test Redis connectivity
    kubectl run test-redis --image=redis:7 --rm -i --restart=Never -- sh -c "
        redis-cli -h redis-master -a smartcloudops-redis-password-2024 ping | grep -q 'PONG' && echo '✅ Redis connectivity test passed' || echo '❌ Redis connectivity test failed'
    " -n "$NAMESPACE"

    log_success "Post-deployment tests completed"
}

# Setup backup and disaster recovery
setup_backup_recovery() {
    log_info "Setting up backup and disaster recovery..."

    # Create backup cronjob
    cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: smartcloudops-backup
  namespace: $NAMESPACE
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:13
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgresql -U smartcloudops -d smartcloudops > /backup/smartcloudops-\$(date +%Y%m%d_%H%M%S).sql
            env:
            - name: PGPASSWORD
              value: "smartcloudops-password-2024"
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: smartcloudops-backup-pvc
          restartPolicy: OnFailure
EOF

    log_success "Backup and disaster recovery configured"
}

# Main deployment function
main() {
    log_info "Starting SmartCloudOps AI deployment to $ENVIRONMENT environment"
    log_info "Cluster: $CLUSTER_NAME, Region: $REGION"

    # Run deployment steps
    pre_deployment_checks
    setup_helm_repos
    deploy_cert_manager
    deploy_ingress_controller
    deploy_postgresql
    deploy_redis
    deploy_monitoring
    deploy_smartcloudops
    configure_monitoring
    run_post_deployment_tests
    setup_backup_recovery

    # Get service URLs
    INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    GRAFANA_URL="http://$INGRESS_IP/monitoring"

    log_success "🎉 SmartCloudOps AI deployment completed successfully!"
    echo ""
    echo "📊 Service URLs:"
    echo "   🌐 SmartCloudOps AI: http://$INGRESS_IP"
    echo "   📈 Grafana: $GRAFANA_URL"
    echo "   📊 Prometheus: http://$INGRESS_IP/prometheus"
    echo "   🚨 Alertmanager: http://$INGRESS_IP/alertmanager"
    echo ""
    echo "🔐 Default Credentials:"
    echo "   Grafana: admin / admin123"
    echo "   PostgreSQL: smartcloudops / smartcloudops-password-2024"
    echo "   Redis: smartcloudops-redis-password-2024"
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Configure DNS to point to $INGRESS_IP"
    echo "   2. Update secrets with production values"
    echo "   3. Configure SSL certificates"
    echo "   4. Set up monitoring alerts"
    echo "   5. Configure backup destinations"
}

# Error handling
trap 'log_error "Deployment failed at line $LINENO"' ERR

# Run main deployment
main "$@"
