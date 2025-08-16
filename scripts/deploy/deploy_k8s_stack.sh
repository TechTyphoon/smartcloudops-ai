#!/bin/bash
# deploy_k8s_stack.sh - Kubernetes Production Deployment Script
# Smart CloudOps AI v3.0.0 - Enterprise Kubernetes Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="smartcloudops"
VERSION="3.0.0"
KUBECTL_TIMEOUT="600s"

# Functions
print_header() {
    echo -e "${PURPLE}"
    echo "██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗ ███╗   ██╗███████╗████████╗███████╗███████╗"
    echo "██║ ██╔╝██║   ██║██╔══██╗██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝"
    echo "█████╔╝ ██║   ██║██████╔╝█████╗  ██████╔╝██╔██╗ ██║█████╗     ██║   █████╗  ███████╗"
    echo "██╔═██╗ ██║   ██║██╔══██╗██╔══╝  ██╔══██╗██║╚██╗██║██╔══╝     ██║   ██╔══╝  ╚════██║"
    echo "██║  ██╗╚██████╔╝██████╔╝███████╗██║  ██║██║ ╚████║███████╗   ██║   ███████╗███████║"
    echo "╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚══════╝"
    echo -e "${NC}"
    echo -e "${GREEN}Smart CloudOps AI v$VERSION - Kubernetes Production Deployment${NC}"
    echo -e "${GREEN}==============================================================${NC}\n"
}

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

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

check_prerequisites() {
    print_step "Checking Prerequisites"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        print_info "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    print_success "kubectl: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        print_info "Please ensure your kubeconfig is properly configured"
        exit 1
    fi
    print_success "Kubernetes cluster: Connected"
    
    # Check required Kubernetes files
    k8s_files=(
        "k8s/00-namespace-and-storage.yaml"
        "k8s/01-database.yaml"
        "k8s/02-application.yaml"
        "k8s/03-nginx.yaml"
        "k8s/04-prometheus.yaml"
        "k8s/05-grafana.yaml"
    )
    
    for file in "${k8s_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required Kubernetes manifest missing: $file"
            exit 1
        fi
    done
    print_success "All Kubernetes manifests present"
    
    # Check if Helm is available (optional)
    if command -v helm &> /dev/null; then
        print_success "Helm: $(helm version --short 2>/dev/null || helm version)"
    else
        print_warning "Helm not found (optional for some deployments)"
    fi
}

create_namespace() {
    print_step "Creating Namespace and Storage"
    
    # Apply namespace and storage configuration
    kubectl apply -f k8s/00-namespace-and-storage.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Wait for namespace to be ready
    kubectl wait --for=condition=Ready --timeout=60s namespace/$NAMESPACE 2>/dev/null || true
    
    print_success "Namespace '$NAMESPACE' created and configured"
}

deploy_databases() {
    print_step "Deploying Database Services"
    
    # Deploy PostgreSQL and Redis
    kubectl apply -f k8s/01-database.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Wait for database pods to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=Ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    
    print_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=Ready pod -l app=redis -n $NAMESPACE --timeout=300s
    
    print_success "Database services deployed and ready"
}

deploy_application() {
    print_step "Deploying Application Services"
    
    # Update image in deployment if provided
    if [[ -n "${DOCKER_IMAGE:-}" ]]; then
        print_info "Updating application image to: $DOCKER_IMAGE"
        kubectl set image deployment/smartcloudops-app smartcloudops=$DOCKER_IMAGE -n $NAMESPACE
    fi
    
    # Deploy application
    kubectl apply -f k8s/02-application.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Wait for application pods to be ready
    print_info "Waiting for application pods to be ready..."
    kubectl wait --for=condition=Ready pod -l app=smartcloudops-app -n $NAMESPACE --timeout=300s
    
    # Check if HPA is working
    kubectl get hpa -n $NAMESPACE 2>/dev/null || print_warning "HPA metrics may take a few minutes to appear"
    
    print_success "Application services deployed and ready"
}

deploy_loadbalancer() {
    print_step "Deploying Load Balancer"
    
    # Deploy Nginx load balancer
    kubectl apply -f k8s/03-nginx.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Wait for Nginx pods to be ready
    print_info "Waiting for Nginx pods to be ready..."
    kubectl wait --for=condition=Ready pod -l app=nginx -n $NAMESPACE --timeout=300s
    
    # Get external IP (for LoadBalancer type)
    print_info "Checking for external IP assignment..."
    for i in {1..30}; do
        EXTERNAL_IP=$(kubectl get svc nginx -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        if [[ -n "$EXTERNAL_IP" && "$EXTERNAL_IP" != "null" ]]; then
            print_success "External IP assigned: $EXTERNAL_IP"
            break
        fi
        print_info "Waiting for external IP assignment... (attempt $i/30)"
        sleep 10
    done
    
    if [[ -z "$EXTERNAL_IP" || "$EXTERNAL_IP" == "null" ]]; then
        print_warning "External IP not assigned yet. This may take a few minutes depending on your cloud provider."
    fi
    
    print_success "Load balancer deployed"
}

deploy_monitoring() {
    print_step "Deploying Monitoring Stack"
    
    # Deploy Prometheus
    kubectl apply -f k8s/04-prometheus.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Wait for Prometheus to be ready
    print_info "Waiting for Prometheus to be ready..."
    kubectl wait --for=condition=Ready pod -l app=prometheus -n $NAMESPACE --timeout=300s
    
    # Deploy Grafana
    kubectl apply -f k8s/05-grafana.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Wait for Grafana to be ready
    print_info "Waiting for Grafana to be ready..."
    kubectl wait --for=condition=Ready pod -l app=grafana -n $NAMESPACE --timeout=300s
    
    print_success "Monitoring stack deployed and ready"
}

verify_deployment() {
    print_step "Verifying Deployment"
    
    # Check all pods
    print_info "Checking pod status..."
    kubectl get pods -n $NAMESPACE
    
    # Check services
    print_info "Checking service status..."
    kubectl get services -n $NAMESPACE
    
    # Check ingress (if exists)
    kubectl get ingress -n $NAMESPACE 2>/dev/null || print_info "No ingress resources found"
    
    # Test application health
    print_info "Testing application health..."
    
    # Port forward for health check
    kubectl port-forward svc/smartcloudops-app 8080:80 -n $NAMESPACE &
    PORT_FORWARD_PID=$!
    
    # Wait a moment for port forward to establish
    sleep 5
    
    # Test health endpoint
    if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
        print_success "Application health check: PASSED"
    else
        print_warning "Application health check: Could not reach health endpoint"
    fi
    
    # Clean up port forward
    kill $PORT_FORWARD_PID 2>/dev/null || true
    
    # Check HPA status
    print_info "Horizontal Pod Autoscaler status:"
    kubectl get hpa -n $NAMESPACE 2>/dev/null || print_info "HPA not found or metrics not ready"
    
    # Check PVC status
    print_info "Persistent Volume status:"
    kubectl get pvc -n $NAMESPACE
    
    print_success "Deployment verification completed"
}

show_access_information() {
    print_step "Access Information"
    
    echo -e "${GREEN}🎉 Smart CloudOps AI Successfully Deployed to Kubernetes!${NC}\n"
    
    # Get service information
    NGINX_SERVICE=$(kubectl get svc nginx -n $NAMESPACE -o jsonpath='{.spec.type}')
    NGINX_PORT=$(kubectl get svc nginx -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}')
    EXTERNAL_IP=$(kubectl get svc nginx -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    echo -e "${YELLOW}🔗 Access Points:${NC}"
    
    if [[ "$NGINX_SERVICE" == "LoadBalancer" && -n "$EXTERNAL_IP" && "$EXTERNAL_IP" != "null" ]]; then
        echo "🌐 Application:     http://$EXTERNAL_IP"
        echo "🌐 Application SSL: https://$EXTERNAL_IP (if SSL configured)"
    else
        echo "🌐 Application:     Use port-forward: kubectl port-forward svc/nginx 8080:80 -n $NAMESPACE"
        echo "                   Then access: http://localhost:8080"
    fi
    
    echo "📊 Grafana:        kubectl port-forward svc/grafana 3000:3000 -n $NAMESPACE"
    echo "                   Then access: http://localhost:3000 (admin/cloudops123)"
    echo "📈 Prometheus:     kubectl port-forward svc/prometheus 9090:9090 -n $NAMESPACE"
    echo "                   Then access: http://localhost:9090"
    
    echo -e "\n${YELLOW}📋 Management Commands:${NC}"
    echo "📊 View pods:       kubectl get pods -n $NAMESPACE"
    echo "📋 View logs:       kubectl logs -f deployment/smartcloudops-app -n $NAMESPACE"
    echo "🔄 Restart app:     kubectl rollout restart deployment/smartcloudops-app -n $NAMESPACE"
    echo "📈 Scale app:       kubectl scale deployment/smartcloudops-app --replicas=5 -n $NAMESPACE"
    echo "🗑️  Delete stack:    kubectl delete namespace $NAMESPACE"
    
    echo -e "\n${YELLOW}🩺 Health Checks:${NC}"
    echo "🏥 App Health:      kubectl port-forward svc/smartcloudops-app 8080:80 -n $NAMESPACE"
    echo "                   curl http://localhost:8080/health"
    echo "🏥 Prometheus:      kubectl port-forward svc/prometheus 9090:9090 -n $NAMESPACE"
    echo "                   curl http://localhost:9090/-/healthy"
    echo "🏥 Grafana:         kubectl port-forward svc/grafana 3000:3000 -n $NAMESPACE"
    echo "                   curl http://localhost:3000/api/health"
    
    echo -e "\n${YELLOW}📦 Version Information:${NC}"
    echo "📦 Version: $VERSION"
    echo "🔨 Deploy Date: $(date)"
    echo "🏷️  Namespace: $NAMESPACE"
    echo "☸️  Cluster: $(kubectl config current-context)"
    
    echo -e "\n${CYAN}💡 Quick Start Commands:${NC}"
    echo "# Access application"
    echo "kubectl port-forward svc/nginx 8080:80 -n $NAMESPACE"
    echo ""
    echo "# Access Grafana dashboard"
    echo "kubectl port-forward svc/grafana 3000:3000 -n $NAMESPACE"
    echo ""
    echo "# View application logs"
    echo "kubectl logs -f deployment/smartcloudops-app -n $NAMESPACE"
    echo ""
    echo "# Scale application"
    echo "kubectl scale deployment/smartcloudops-app --replicas=5 -n $NAMESPACE"
}

cleanup_on_error() {
    print_error "Deployment failed! Check the logs above for details."
    print_info "To clean up partial deployment, run: kubectl delete namespace $NAMESPACE"
    exit 1
}

# Main execution
main() {
    print_header
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --image)
                DOCKER_IMAGE="$2"
                shift 2
                ;;
            --timeout)
                KUBECTL_TIMEOUT="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --image IMAGE    Docker image to deploy (optional)"
                echo "  --timeout TIME   Kubectl timeout (default: 600s)"
                echo "  --help          Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0"
                echo "  $0 --image ghcr.io/your-username/smartcloudops:v3.0.0"
                echo "  $0 --timeout 900s"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Trap errors and cleanup
    trap cleanup_on_error ERR
    
    # Execute deployment steps
    check_prerequisites
    create_namespace
    deploy_databases
    deploy_application
    deploy_loadbalancer
    deploy_monitoring
    verify_deployment
    show_access_information
    
    print_success "Kubernetes deployment completed successfully! 🎉"
}

# Run main function
main "$@"
