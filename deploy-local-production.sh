#!/bin/bash
# SmartCloudOps AI - Local Production Deployment
set -e

echo "🚀 SmartCloudOps AI - Local Production Stack"
echo "============================================"

# Stop any existing development services
echo "🛑 Stopping development services..."
pkill -f gunicorn 2>/dev/null || echo "No gunicorn processes found"
docker-compose down 2>/dev/null || echo "No existing docker-compose services"

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker container prune -f
docker volume prune -f

# Set production environment variables
export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
export VERSION="3.1.0"
export VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
export SECRET_KEY="smartcloudops_production_$(openssl rand -hex 16)"

echo "📦 Building production images..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "🚀 Starting production stack..."
docker-compose -f docker-compose.production.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🏥 Health checking services..."
echo "  ▶️ PostgreSQL..."
docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U smartcloudops -d smartcloudops_production || echo "  ⚠️ PostgreSQL not ready"

echo "  ▶️ Redis..."
docker-compose -f docker-compose.production.yml exec -T redis redis-cli -a cloudops123 ping || echo "  ⚠️ Redis not ready"

echo "  ▶️ Application..."
curl -s http://localhost:15000/health | jq . || echo "  ⚠️ Application not ready"

echo -e "\n🎉 Local Production Stack Running!"
echo "=================================="
echo "🌐 Application: http://localhost:15000"
echo "📊 Grafana: http://localhost:13000 (admin/admin)"
echo "🔍 Prometheus: http://localhost:19090"
echo "💾 PostgreSQL: localhost:15432"
echo "⚡ Redis: localhost:16379"
echo ""
echo "🧪 Test Endpoints:"
echo "  curl http://localhost:15000/health"
echo "  curl http://localhost:15000/demo"
echo "  curl http://localhost:15000/anomaly"
echo ""
echo "📋 View Logs:"
echo "  docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo "🛑 Stop Services:"
echo "  docker-compose -f docker-compose.production.yml down"
