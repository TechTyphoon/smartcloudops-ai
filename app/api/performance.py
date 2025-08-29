"""
Performance API Endpoints
Phase 5: Performance & Cost Optimization - Performance Monitoring API
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from flask import Blueprint, jsonify, request, current_app
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.observability.enhanced_logging import get_logger, log_business_event
from app.performance.redis_cache import get_redis_cache, RedisCacheConfig
from app.performance.anomaly_optimization import get_anomaly_detector, AnomalyConfig
from app.performance.log_optimization import get_log_manager, LogConfig
from app.performance.database_optimization import get_optimized_database, DatabaseConfig

# Create blueprint
performance_bp = Blueprint("performance", __name__)
# Get logger
logger = get_logger(__name__)


@performance_bp.route("/health", methods=["GET"])
def health_check():
    """Performance system health check"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check Redis cache
        redis_cache = get_redis_cache(
    if redis_cache:
            health_status["components"]["redis_cache"] = {
                "status": "healthy" if redis_cache._redis_client else "unavailable",
                "connected": redis_cache._redis_client is not None
            }
        else:
            health_status["components"]["redis_cache"] = {"status": "not_initialized"}
        
        # Check anomaly detector
        anomaly_detector = get_anomaly_detector(
    if anomaly_detector:
            health_status["components"]["anomaly_detector"] = {
                "status": "healthy",
                "model_version": anomaly_detector.model_version
            }
        else:
            health_status["components"]["anomaly_detector"] = {"status": "not_initialized"}
        
        # Check log manager
        log_manager = get_log_manager(
    if log_manager:
            health_status["components"]["log_manager"] = {
                "status": "healthy",
                "async_enabled": log_manager.config.enable_async
            }
        else:
            health_status["components"]["log_manager"] = {"status": "not_initialized"}
        
        # Check database
        db = get_optimized_database(
    if db:
            health_status["components"]["database"] = {
                "status": "healthy",
                "cache_enabled": db.config.enable_query_cache
            }
        else:
            health_status["components"]["database"] = {"status": "not_initialized"}
        
        # Log business event
        log_business_event("performance_health_check", {
            "status": health_status["status"],
            "components_count": len(health_status["components"])
        })
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Performance health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@performance_bp.route("/cache/stats", methods=["GET"])
def cache_stats():
    """Get cache statistics"""
    try:
        redis_cache = get_redis_cache(
    if not redis_cache:
            return jsonify({"error": "Cache not initialized"}), 404
        
        stats = redis_cache.get_stats()
        
        # Log business event
        log_business_event("cache_stats_retrieved", {
            "hit_rate": stats.get("hit_rate", 0),
            "total_requests": stats.get("total_requests", 0)
        })
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Cache stats retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Clear cache"""
    try:
        data = request.get_json() or {}
        namespace = data.get("namespace", "default")
        
        redis_cache = get_redis_cache(
    if not redis_cache:
            return jsonify({"error": "Cache not initialized"}), 404
        
        success = redis_cache.clear(namespace)
        
        # Log business event
        log_business_event("cache_cleared", {
            "namespace": namespace,
            "success": success
        })
        
        return jsonify({
            "success": success,
            "namespace": namespace,
            "timestamp": datetime.utcnow().isoformat()
        }), 200 if success else 500
        :
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/anomaly/detect", methods=["POST"])
def detect_anomaly():
    """Detect anomaly in data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        use_cache = request.args.get("use_cache", "true").lower() == "true"
        
        anomaly_detector = get_anomaly_detector(
    if not anomaly_detector:
            return jsonify({"error": "Anomaly detector not initialized"}), 404
        
        result = anomaly_detector.detect_anomaly(data, use_cache)
        
        # Log business event
        log_business_event("anomaly_detected", {
            "is_anomaly": result.is_anomaly,
            "confidence": result.confidence,
            "processing_time": result.processing_time
        })
        
        return jsonify({
            "is_anomaly": result.is_anomaly,
            "confidence": result.confidence,
            "score": result.score,
            "features": result.features,
            "timestamp": result.timestamp.isoformat(),
            "model_version": result.model_version,
            "processing_time": result.processing_time
        }), 200
        
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/anomaly/stats", methods=["GET"])
def anomaly_stats():
    """Get anomaly detection statistics"""
    try:
        anomaly_detector = get_anomaly_detector(
    if not anomaly_detector:
            return jsonify({"error": "Anomaly detector not initialized"}), 404
        
        stats = anomaly_detector.get_stats()
        
        # Log business event
        log_business_event("anomaly_stats_retrieved", {}
            "model_version": stats.get("model_version", "unknown"),
            "cache_enabled": stats.get("cache_enabled", False)
        })
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Anomaly stats retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/logs/stats", methods=["GET"])
def log_stats():
    """Get log optimization statistics"""
    try:
        log_manager = get_log_manager(
    if not log_manager:
            return jsonify({"error": "Log manager not initialized"}), 404
        
        stats = log_manager.get_stats()
        
        # Log business event
        log_business_event("log_stats_retrieved", {}
            "total_files": stats.get("total_files", 0),
            "total_size": stats.get("total_size", 0)
        })
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Log stats retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/database/stats", methods=["GET"])
def database_stats():
    """Get database optimization statistics"""
    try:
        db = get_optimized_database(
    if not db:
            return jsonify({"error": "Database not initialized"}), 404
        
        stats = db.get_stats()
        
        # Log business event
        log_business_event("database_stats_retrieved", {}
            "total_queries": stats.get("query_stats", {}).get("total_queries", 0),
            "avg_time": stats.get("query_stats", {}).get("avg_time", 0)
        })
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Database stats retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/database/optimize", methods=["POST"])
def optimize_database():
    """Optimize database tables"""
    try:
        db = get_optimized_database(
    if not db:
            return jsonify({"error": "Database not initialized"}), 404
        
        db.optimize_tables()
        
        # Log business event
        log_business_event("database_optimized", {}
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return jsonify({}
            "success": True,
            "message": "Database optimization completed",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/metrics", methods=["GET"])
def performance_metrics():
    """Get Prometheus metrics"""
    try:
        # Generate Prometheus metrics
        metrics = generate_latest(
    # Log business event
        log_business_event("performance_metrics_retrieved", {}
            "metrics_size": len(metrics)
        })
        
        return metrics, 200, {"Content-Type": CONTENT_TYPE_LATEST}
        
    except Exception as e:
        logger.error(f"Performance metrics generation failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/config", methods=["GET"])
def get_config():
    """Get performance configuration"""
    try:
        config = {
            "redis_cache": {}
                "host": "localhost",
                "port": 6379,
                "default_ttl": 3600,
                "enable_compression": True
            },
            "anomaly_detection": {}
                "batch_size": 100,
                "batch_timeout": 0.5,
                "max_workers": 4,
                "cache_predictions": True
            },
            "log_optimization": {}
                "enable_rotation": True,
                "enable_compression": True,
                "enable_async": True,
                "max_file_size": 10 * 1024 * 1024
            },
            "database_optimization": {}
                "enable_query_cache": True,
                "enable_connection_pooling": True,
                "enable_query_logging": True,
                "slow_query_threshold": 1.0
            }
        }
        
        # Log business event
        log_business_event("performance_config_retrieved", {}
            "config_sections": len(config)
        })
        
        return jsonify(config), 200
        
    except Exception as e:
        logger.error(f"Performance config retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/config", methods=["PUT"])
def update_config():
    """Update performance configuration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No configuration provided"}), 400
        
        # Update Redis cache config
        if "redis_cache" in data:
            redis_config = data["redis_cache"]
            redis_cache = get_redis_cache(
    if redis_cache and hasattr(redis_cache, 'config':
                for key, value in redis_config.items():
                    if hasattr(redis_cache.config, key:
                        setattr(redis_cache.config, key, value)
        
        # Update anomaly detection config
        if "anomaly_detection" in data:
            anomaly_config = data["anomaly_detection"]
            anomaly_detector = get_anomaly_detector(
    if anomaly_detector and hasattr(anomaly_detector, 'config':
                for key, value in anomaly_config.items():
                    if hasattr(anomaly_detector.config, key:
                        setattr(anomaly_detector.config, key, value)
        
        # Log business event
        log_business_event("performance_config_updated", {}
            "updated_sections": list(data.keys()
        })
        
        return jsonify({}
            "success": True,
            "message": "Configuration updated",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Performance config update failed: {e}")
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/summary", methods=["GET"])
def performance_summary():
    """Get comprehensive performance summary"""
    try:
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Redis cache summary
        redis_cache = get_redis_cache(
    if redis_cache:
            cache_stats = redis_cache.get_stats()
            summary["components"]["redis_cache"] = {}
                "status": "active" if cache_stats.get("redis_connected") else "inactive",:
                "hit_rate": cache_stats.get("hit_rate", 0),
                "total_requests": cache_stats.get("total_requests", 0)
            }
        
        # Anomaly detection summary
        anomaly_detector = get_anomaly_detector(
    if anomaly_detector:
            anomaly_stats = anomaly_detector.get_stats()
            summary["components"]["anomaly_detection"] = {}
                "status": "active",
                "model_version": anomaly_stats.get("model_version", "unknown"),
                "cache_enabled": anomaly_stats.get("cache_enabled", False)
            }
        
        # Log optimization summary
        log_manager = get_log_manager(
    if log_manager:
            log_stats = log_manager.get_stats()
            summary["components"]["log_optimization"] = {}
                "status": "active",
                "total_files": log_stats.get("total_files", 0),
                "total_size": log_stats.get("total_size", 0)
            }
        
        # Database optimization summary
        db = get_optimized_database(
    if db:
            db_stats = db.get_stats()
            summary["components"]["database_optimization"] = {}
                "status": "active",
                "total_queries": db_stats.get("query_stats", {}).get("total_queries", 0),
                "avg_query_time": db_stats.get("query_stats", {}).get("avg_time", 0)
            }
        
        # Overall performance score
        active_components = sum(1 for comp in summary["components"].values() 
                              if comp.get("status") == "active")
        total_components = len(summary["components"])
        performance_score = (active_components / total_components * 100) if total_components > 0 else 0
        
        summary["performance_score"] = performance_score
        summary["active_components"] = active_components
        summary["total_components"] = total_components
        
        # Log business event:
        log_business_event("performance_summary_retrieved", {}:
            "performance_score": performance_score,
            "active_components": active_components
        })
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Performance summary generation failed: {e}")
        return jsonify({"error": str(e)}), 500
