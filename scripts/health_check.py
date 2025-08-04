#!/usr/bin/env python3
"""
Health check script for Smart CloudOps AI
Phase 1: Basic system health verification
"""

import sys
import os
import requests
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import get_config


def check_prometheus_connection() -> Dict[str, Any]:
    """Check if Prometheus is accessible."""
    config = get_config()
    prometheus_url = f"http://localhost:{config.METRICS_PORT}"
    
    try:
        response = requests.get(f"{prometheus_url}/api/v1/query?query=up", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "message": "Prometheus is accessible"}
        else:
            return {"status": "unhealthy", "message": f"Prometheus returned {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "unhealthy", "message": f"Connection error: {str(e)}"}


def run_health_checks() -> bool:
    """Run all health checks."""
    print("Running Smart CloudOps AI Health Checks...")
    print("=" * 50)
    
    checks = [
        ("Prometheus Connection", check_prometheus_connection),
    ]
    
    all_healthy = True
    
    for check_name, check_function in checks:
        print(f"Checking {check_name}...")
        result = check_function()
        
        if result["status"] == "healthy":
            print(f"✅ {check_name}: {result['message']}")
        else:
            print(f"❌ {check_name}: {result['message']}")
            all_healthy = False
    
    print("=" * 50)
    if all_healthy:
        print("🎉 All health checks passed!")
        return True
    else:
        print("⚠️  Some health checks failed!")
        return False


if __name__ == "__main__":
    success = run_health_checks()
    sys.exit(0 if success else 1)