#!/bin/bash
set -e

echo "🚀 Starting Smart CloudOps AI v3.0.0 with Full Features..."
echo "📊 Phase 7: Complete Production Stack with ML & ChatOps!"
echo "🌐 Application will be available at:"
echo "   Main App:    http://localhost:5000"
echo "   Health:      http://localhost:5000/health"
echo "   ML API:      http://localhost:5000/api/predict"
echo "   ChatOps:     http://localhost:5000/chatops/context"
echo "   Metrics:     http://localhost:5000/metrics"

# Set proper Python path
export PYTHONPATH=/app

# Run the advanced application with all features
exec python app/main.py
