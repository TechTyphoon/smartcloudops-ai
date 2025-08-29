#!/usr/bin/env python3
"""
SmartCloudOps AI - Main Application Entry Point
Phase 2C Week 1: Performance & Scaling - Refactored with Factory Pattern
"""
import logging
from flask import Flask, jsonify, request
import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)


def main():
    """Main application entry point using factory pattern"""
    from app import create_app

    app = create_app()

    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"

    logger.info(f"🚀 Starting SmartCloudOps AI server on {host}:{port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(
        f"⚡ Performance features: {'enabled' if _check_performance_available() else 'disabled'}"
    )

    try:
        # Start the Flask application
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
    finally:
        # Cleanup
        if _check_performance_available():
            try:
                from app.performance.api_optimization import shutdown_performance_monitoring

                shutdown_performance_monitoring()
                logger.info("✅ Performance monitoring shutdown complete")
            except Exception as e:
                logger.error(f"❌ Performance monitoring shutdown error: {e}")

        logger.info("👋 SmartCloudOps AI server stopped")


def _check_performance_available():
    """Check if performance monitoring is available"""
    try:
        from app.performance.api_optimization import performance_collector

        return True
    except ImportError:
        return False


if __name__ == "__main__":
    main()
