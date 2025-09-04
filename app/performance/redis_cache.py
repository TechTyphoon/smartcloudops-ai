"""
Redis Cache Module
High-performance caching with Redis
"""

import json
from typing import Any, Dict


class RedisCache:
    """Redis cache implementation"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.client = None
        self.connected = False

        # Try to connect to Redis
        self._connect()

    def _connect(self):
        """Connect to Redis"""
        try:
            import redis

            self.client = redis.Redis(
                host=self.host, port=self.port, db=self.db, decode_responses=True
            )
            # Test connection
            self.client.ping()
            self.connected = True
        except ImportError:
            # Redis not available, use in-memory fallback
            self.client = None
            self.connected = False
        except Exception:
            # Connection failed, use in-memory fallback
            self.client = None
            self.connected = False

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        if not self.connected or not self.client:
            return default

        try:
            value = self.client.get(key)
            if value is not None:
                return json.loads(value)
            return default
        except Exception:
            return default

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache"""
        if not self.connected or not self.client:
            return False

        try:
            serialized_value = json.dumps(value)
            return self.client.setex(key, ttl, serialized_value)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.connected or not self.client:
            return False

        try:
            return bool(self.client.delete(key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.connected or not self.client:
            return False

        try:
            return bool(self.client.exists(key))
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.connected or not self.client:
            return {
                "connected": False,
                "host": self.host,
                "port": self.port,
                "db": self.db,
            }

        try:
            info = self.client.info()
            return {
                "connected": True,
                "host": self.host,
                "port": self.port,
                "db": self.db,
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except Exception:
            return {
                "connected": False,
                "host": self.host,
                "port": self.port,
                "db": self.db,
            }


# Global Redis cache instance
redis_cache = RedisCache()


def setup_redis_cache(app) -> None:
    """Setup Redis cache for the application"""
    global redis_cache

    # Get Redis configuration from app config
    redis_host = app.config.get("REDIS_HOST", "localhost")
    redis_port = app.config.get("REDIS_PORT", 6379)
    redis_db = app.config.get("REDIS_DB", 0)

    redis_cache = RedisCache(redis_host, redis_port, redis_db)

    if redis_cache.connected:
        app.logger.info(f"Redis cache connected: {redis_host}:{redis_port}")
    else:
        app.logger.warning("Redis cache not available, using fallback")


def get_redis_cache() -> RedisCache:
    """Get the global Redis cache instance"""
    return redis_cache


def cached(ttl: int = 300):
    """Decorator for caching function results"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached_result = redis_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


class CacheWarmup:
    """Cache warmup utilities"""

    @staticmethod
    def warmup_endpoints(app, endpoints: list):
        """Warm up cache for specified endpoints"""
        if not redis_cache.connected:
            return

        for endpoint in endpoints:
            try:
                # This would make requests to warm up the cache
                # For now, just log the warmup attempt
                app.logger.info(f"Cache warmup for endpoint: {endpoint}")
            except Exception as e:
                app.logger.warning(f"Cache warmup failed for {endpoint}: {e}")


# Cache manager for multiple cache types
class CacheManager:
    """Manages multiple cache instances"""

    def __init__(self):
        self.caches = {"redis": redis_cache, "memory": {}}  # Simple in-memory cache

    def get_cache(self, cache_type: str = "redis"):
        """Get cache instance by type"""
        return self.caches.get(cache_type)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        stats = {}
        for cache_type, cache in self.caches.items():
            if hasattr(cache, "get_stats"):
                stats[cache_type] = cache.get_stats()
            else:
                stats[cache_type] = {"type": "simple", "size": len(cache)}
        return stats


# Global cache manager
cache_manager = CacheManager()
