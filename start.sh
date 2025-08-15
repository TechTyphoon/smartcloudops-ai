#!/bin/bash
set -e

echo "🚀 Starting Smart CloudOps AI v3.0.0 Production Server..."
echo "📊 Phase 4: Container Orchestration Complete!"
echo "🌐 Application will be available at:"
echo "   HTTP:  http://localhost:8080"
echo "   HTTPS: https://localhost:8443"

exec python complete_production_app_with_database.py
