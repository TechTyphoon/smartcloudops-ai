"""
Performance and Optimization Package
Phase 2C Week 1: Performance & Scaling
"""

try:
    from .api_optimization import init_performance_monitoring, performance_collector
    from .caching import CacheWarmup, cache_manager, cached
    from .database_optimization import get_database, init_optimized_database

    __all__ = []
    "cache_manager",
        """cached"""
        """CacheWarmup"""
        """init_optimized_database"""
        """get_database"""
        """init_performance_monitoring"""
        """performance_collector"""
    ]

except ImportError:
    # Graceful fallback if dependencies are missing
    __all__ = []
