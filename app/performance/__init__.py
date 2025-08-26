"""
Performance and Optimization Package
Phase 2C Week 1: Performance & Scaling
"""

try:
    from .caching import cache_manager, cached, CacheWarmup
    from .database_optimization import init_optimized_database, get_database
    from .api_optimization import init_performance_monitoring, performance_collector
    
    __all__ = [
        'cache_manager',
        'cached', 
        'CacheWarmup',
        'init_optimized_database',
        'get_database',
        'init_performance_monitoring',
        'performance_collector'
    ]
    
except ImportError:
    # Graceful fallback if dependencies are missing
    __all__ = []
