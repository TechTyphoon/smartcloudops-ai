"""
Cache Integration with SmartCloudOps Components
Phase 3 Week 4: Advanced Caching Strategies - Integration
"""

import logging
from functools import wraps
from typing import Any, Dict, List, Optional

from ..strategies.cache_manager import (
    CachePolicy,
    CacheStrategy,
    CacheTag,
    cached_with_policy,
    get_cache_manager,
    invalidate_cache_tag,
)

logger = logging.getLogger(__name__)


def integrate_mlops_caching():
    """Integrate caching with MLOps service"""
    cache_manager = get_cache_manager()

    # Register MLOps warmup functions
    def warm_experiments():
        """Warm experiments cache"""
        try:
            from app.services.mlops_service import MLOpsService

            mlops = MLOpsService()

            # Get all experiment IDs and warm cache
            experiments = mlops.get_experiments() or []
            loaded = 0

            for exp in experiments[:50]:  # Limit to 50 most recent
                exp_id = (
                    exp.get("id") if isinstance(exp, dict) else getattr(exp, "id", None)
                )
                if exp_id:
                    cache_key = f"mlops:experiments:{exp_id}"
                    cache_manager.set(
                        cache_key,
                        exp,
                        CachePolicy(ttl=7200, tags=[CacheTag.MLOPS_EXPERIMENTS]),
                    )
                    loaded += 1

            return {"loaded": loaded, "total": len(experiments)}

        except Exception as e:
            logger.error(f"Error warming experiments cache: {e}")
            return {"error": str(e)}

    def warm_models():
        """Warm models cache"""
        try:
            from app.services.mlops_service import MLOpsService

            mlops = MLOpsService()

            # Get all models and warm cache
            models = mlops.get_models() or []
            loaded = 0

            for model in models[:50]:  # Limit to 50 most recent
                model_id = (
                    model.get("id")
                    if isinstance(model, dict)
                    else getattr(model, "id", None)
                )
                if model_id:
                    cache_key = f"mlops:models:{model_id}"
                    cache_manager.set(
                        cache_key,
                        model,
                        CachePolicy(ttl=3600, tags=[CacheTag.MLOPS_MODELS]),
                    )
                    loaded += 1

            return {"loaded": loaded, "total": len(models)}

        except Exception as e:
            logger.error(f"Error warming models cache: {e}")
            return {"error": str(e)}

    # Register warmup functions
    cache_manager.register_warmup_function("mlops:experiments", warm_experiments)
    cache_manager.register_warmup_function("mlops:models", warm_models)

    logger.info("MLOps caching integration completed")


def integrate_api_caching():
    """Integrate caching with API responses"""

    def cache_api_response(endpoint: str, ttl: int = 300):
        """Decorator for caching API responses"""
        return cached_with_policy(
            namespace="api:responses",
            ttl=ttl,
            tags=[CacheTag.API_RESPONSES],
            strategy=CacheStrategy.CACHE_ASIDE,
        )

    return cache_api_response


def integrate_database_caching():
    """Integrate caching with database operations"""

    def cache_query_result(table: str, ttl: int = 1800):
        """Decorator for caching database query results"""
        return cached_with_policy(
            namespace=f"db:{table}",
            ttl=ttl,
            tags=[CacheTag.COMPUTED_RESULTS],
            strategy=CacheStrategy.READ_THROUGH,
        )

    def invalidate_table_cache(table: str):
        """Decorator to invalidate table cache after modifications"""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                # Invalidate cache for this table
                cache_manager = get_cache_manager()
                invalidated = cache_manager.invalidate_by_pattern(f"db:{table}:*")

                if invalidated > 0:
                    logger.info(
                        f"Invalidated {invalidated} cache entries for table: {table}"
                    )

                return result

            return wrapper

        return decorator

    return cache_query_result, invalidate_table_cache


def integrate_user_caching():
    """Integrate caching with user data"""

    @cached_with_policy(
        namespace="user:profile",
        ttl=1800,  # 30 minutes
        tags=[CacheTag.USER_DATA],
        strategy=CacheStrategy.WRITE_THROUGH,
    )
    def get_user_profile(user_id: str):
        """Cached user profile getter"""
        # This would integrate with actual user service
        return {"user_id": user_id, "cached": True}

    @invalidate_cache_tag(CacheTag.USER_DATA)
    def update_user_profile(user_id: str, profile_data: Dict[str, Any]):
        """Update user profile and invalidate cache"""
        # This would integrate with actual user service
        return {"updated": True, "user_id": user_id}

    return get_user_profile, update_user_profile


def setup_cache_warming_schedule():
    """Setup scheduled cache warming"""
    import threading
    import time

    def warm_caches_periodically():
        """Periodic cache warming function"""
        cache_manager = get_cache_manager()

        while True:
            try:
                # Warm MLOps caches every hour
                cache_manager.warm_cache("mlops:experiments")
                cache_manager.warm_cache("mlops:models")

                logger.info("Periodic cache warming completed")

                # Sleep for 1 hour
                time.sleep(3600)

            except Exception as e:
                logger.error(f"Periodic cache warming error: {e}")
                time.sleep(600)  # Retry in 10 minutes on error

    # Start background thread
    warming_thread = threading.Thread(target=warm_caches_periodically, daemon=True)
    warming_thread.start()

    logger.info("Cache warming schedule started")


def get_cache_health_status() -> Dict[str, Any]:
    """Get comprehensive cache health status"""
    cache_manager = get_cache_manager()

    try:
        # Get cache statistics
        stats = cache_manager.get_stats()

        # Calculate health metrics
        operation_stats = stats.get("operation_stats", {})
        cache_metrics = stats.get("cache_metrics", {})

        total_requests = operation_stats.get("gets", 0)
        total_errors = operation_stats.get("errors", 0)

        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0

        # Overall cache hit rate
        overall_metrics = cache_metrics.get("overall", {})
        hit_rate = overall_metrics.get("overall_hit_rate", 0)

        # Determine health status
        if error_rate > 10:
            health_status = "critical"
        elif error_rate > 5 or hit_rate < 50:
            health_status = "warning"
        elif hit_rate > 80:
            health_status = "excellent"
        elif hit_rate > 60:
            health_status = "good"
        else:
            health_status = "fair"

        return {
            "status": health_status,
            "hit_rate": hit_rate,
            "error_rate": error_rate,
            "total_requests": total_requests,
            "cache_levels": {
                "l1_size": overall_metrics.get("l1_size", 0),
                "l2_size": overall_metrics.get("l2_size", 0),
            },
            "recommendations": _generate_cache_recommendations(stats),
        }

    except Exception as e:
        logger.error(f"Error getting cache health status: {e}")
        return {"status": "error", "error": str(e)}


def _generate_cache_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Generate cache optimization recommendations"""
    recommendations = []

    cache_metrics = stats.get("cache_metrics", {})
    overall_metrics = cache_metrics.get("overall", {})

    hit_rate = overall_metrics.get("overall_hit_rate", 0)
    l1_metrics = cache_metrics.get("l1_memory", {})
    l2_metrics = cache_metrics.get("l2_redis", {})

    # Hit rate recommendations
    if hit_rate < 50:
        recommendations.append(
            "Low cache hit rate - review cache policies and TTL settings"
        )
    elif hit_rate < 70:
        recommendations.append(
            "Moderate cache hit rate - consider cache warming strategies"
        )

    # L1 cache recommendations
    l1_hit_rate = l1_metrics.get("hit_rate", 0)
    if l1_hit_rate < 30:
        recommendations.append(
            "Low L1 cache hit rate - increase L1 cache size or review promotion strategy"
        )

    # L2 cache recommendations
    l2_hit_rate = l2_metrics.get("hit_rate", 0)
    if l2_hit_rate < 50:
        recommendations.append(
            "Low L2 cache hit rate - review cache policies and data access patterns"
        )

    # Operation recommendations
    operation_stats = stats.get("operation_stats", {})
    error_rate = (
        operation_stats.get("errors", 0) / max(operation_stats.get("gets", 1), 1) * 100
    )

    if error_rate > 5:
        recommendations.append(
            "High cache error rate - check Redis connectivity and system resources"
        )

    # Size recommendations
    distribution = stats.get("cache_distribution", {})
    promotion_candidates = distribution.get("promotion_candidates", 0)
    demotion_candidates = distribution.get("demotion_candidates", 0)

    if promotion_candidates > 10:
        recommendations.append(
            f"{promotion_candidates} keys eligible for L1 promotion - run cache optimization"
        )

    if demotion_candidates > 20:
        recommendations.append(
            f"{demotion_candidates} keys eligible for L1 demotion - run cache optimization"
        )

    if not recommendations:
        recommendations.append(
            "Cache performance is optimal - no immediate recommendations"
        )

    return recommendations


def initialize_cache_integration():
    """Initialize all cache integrations"""
    try:
        # Integrate with different components
        integrate_mlops_caching()
        integrate_api_caching()

        # Setup cache warming
        setup_cache_warming_schedule()

        logger.info("Cache integration initialization completed")

    except Exception as e:
        logger.error(f"Cache integration initialization error: {e}")


# Auto-initialize when module is imported
initialize_cache_integration()
