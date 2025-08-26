"""
SmartCloudOps AI - Flask Application Factory
Phase 2C Week 1: Performance & Scaling - Application Factory Pattern
"""

import os
import logging
from pathlib import Path
from flask import Flask
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

def create_app(config=None) -> Flask:
    """
    Application factory pattern for Flask app creation
    Separates concerns and makes testing easier
    """
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.from_object(config)
    else:
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
    
    # CORS configuration
    CORS(app, origins=[
        "http://localhost:3000", 
        "https://smartcloudops.netlify.app"
    ])
    
    # Initialize components
    _init_performance_monitoring(app)
    _init_mlops_service(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    
    return app

def _init_performance_monitoring(app: Flask):
    """Initialize performance monitoring"""
    from app.performance.api_optimization import init_performance_monitoring
    from app.performance.database_optimization import init_optimized_database
    
    # Initialize optimized database
    db_path = os.getenv('DATABASE_PATH', 'data/mlops_optimized.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    init_optimized_database(db_path, max_connections=15)
    
    # Initialize performance monitoring
    init_performance_monitoring(app)
    logger.info("✅ Performance monitoring enabled")

def _init_mlops_service(app: Flask):
    """Initialize MLOps service"""
    from app.services.mlops_service import MLOpsService
    mlops_service = MLOpsService()
    app.mlops_service = mlops_service
    logger.info("✅ MLOps service initialized")

def _register_blueprints(app: Flask):
    """Register API blueprints"""
    # Core API blueprints - these are required and will fail if not available
    from app.api.core import core_bp
    
    app.register_blueprint(core_bp)
    logger.info("✅ Core API blueprint registered")
    
    # MLOps API if service is available
    if hasattr(app, 'mlops_service') and app.mlops_service:
        from app.api.mlops import mlops_bp
        app.register_blueprint(mlops_bp)
        logger.info("✅ MLOps API registered")

def _register_error_handlers(app: Flask):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            "status": "error",
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist"
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log the actual error for debugging
        logger.error(f"Internal server error: {error}")
        return {
            "status": "error", 
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }, 500
