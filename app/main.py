#!/usr/bin/env python3
"""
Smart CloudOps AI - Flask Application (Phase 1)
Basic Flask application with metrics endpoint for Prometheus monitoring
"""

import sys
import os
import time
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('flask_requests_total', 'Total Flask requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('flask_request_duration_seconds', 'Flask request duration')
SYSTEM_HEALTH = Gauge('system_health_status', 'System health status (1=healthy, 0=unhealthy)')

def create_app(config_name='development'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.update(config.from_env())
    
    # Set system health to healthy by default
    SYSTEM_HEALTH.set(1)
    
    @app.before_request
    def before_request():
        """Record request metrics."""
        request.start_time = time.time()
        REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint or 'unknown').inc()
    
    @app.after_request
    def after_request(response):
        """Record request duration."""
        if hasattr(request, 'start_time'):
            REQUEST_DURATION.observe(time.time() - request.start_time)
        return response
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        try:
            return jsonify({
                'status': 'healthy',
                'service': config.APP_NAME,
                'version': config.VERSION,
                'timestamp': time.time()
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            SYSTEM_HEALTH.set(0)
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }), 500
    
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint."""
        try:
            # Update system health metric
            SYSTEM_HEALTH.set(1)
            
            # Generate Prometheus metrics
            return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {str(e)}")
            return jsonify({'error': 'Failed to generate metrics'}), 500
    
    @app.route('/')
    def index():
        """Root endpoint."""
        return jsonify({
            'service': config.APP_NAME,
            'version': config.VERSION,
            'status': 'running',
            'phase': 'Phase 1 - Infrastructure & Monitoring',
            'endpoints': {
                'health': '/health',
                'metrics': '/metrics'
            }
        })
    
    @app.route('/status')
    def status():
        """System status endpoint (Phase 1 basic implementation)."""
        return jsonify({
            'system': 'operational',
            'monitoring': 'active',
            'prometheus_ready': True,
            'phase': 'Phase 1 Complete',
            'next_phase': 'Phase 2 - ChatOps Implementation'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal error: {str(error)}")
        SYSTEM_HEALTH.set(0)
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info(f"Flask application created successfully - {config.APP_NAME} v{config.VERSION}")
    return app

def main():
    """Main entry point for the application."""
    # Determine environment
    env = os.getenv('FLASK_ENV', 'development')
    config = get_config(env)
    
    # Create Flask app
    app = create_app(env)
    
    # Start the application
    port = int(os.getenv('PORT', 3000))
    debug = config.DEBUG
    
    logger.info(f"Starting Smart CloudOps AI Flask Application")
    logger.info(f"Environment: {env}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Port: {port}")
    logger.info(f"Metrics endpoint: http://localhost:{port}/metrics")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
