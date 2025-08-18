#!/bin/bash
set -e

echo "🚀 Starting Smart CloudOps AI v3.1.0 - Production Ready!"
echo "🔒 Security: Environment variables and input validation enabled"
echo "📊 Monitoring: Prometheus metrics and structured logging active"
echo "🌐 Application will be available at:"
echo "   Main App:    http://localhost:5000"
echo "   Health:      http://localhost:5000/health"
echo "   Metrics:     http://localhost:5000/metrics"
echo "   Demo:        http://localhost:5000/demo"

# Set proper Python path
export PYTHONPATH=/app

# Validate required environment variables
if [ -z "$AUTH_SECRET_KEY" ] || [ "$AUTH_SECRET_KEY" = "change-me-in-prod" ]; then
    echo "⚠️  WARNING: AUTH_SECRET_KEY not set or using default value"
    echo "   Please set AUTH_SECRET_KEY environment variable for production"
fi

# Check if we should use the refactored version
if [ "$USE_REFACTORED" = "true" ]; then
    echo "🔄 Using refactored application with modular architecture"
    exec gunicorn --config gunicorn.conf.py "app.main_refactored:app"
else
    echo "🔄 Using standard application"
    exec gunicorn --config gunicorn.conf.py "app.main:app"
fi
