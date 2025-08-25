#!/usr/bin/env python3
"""
Caching System for Smart CloudOps AI
Enterprise-grade caching with Redis backend, multiple strategies, and cache invalidation
"""

import hashlib
import logging
import redis

logger = logging.getLogger(__name__)


class CacheManager:
    """Enterprise-grade cache manager with multiple strategies."""

    def __init__(
        self, redis_client: Optional[redis.Redis] = None, default_ttl: int = 300
    ):
        """Initialize cache manager."""
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.cache_prefix = "smartcloudops:cache:f"

        # Cache statistics
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "errors": 0}

    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate cache key with namespace."""
        return f"{self.cache_prefix}{namespace}:{key}"

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage."""
        try:
            # Try JSON first for simple types
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                return json.dumps(value, default=str).encode("utf-8")
            else:
                # Use pickle for complex objects
                return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return pickle.dumps(value)

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        try:
            # Try JSON first
            json_str = data.decode("utf-8")
            return json.loads(json_str)
        except (UnicodeDecodeError, json.JSONDecodeError):
            try:
                # Fall back to pickle
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Deserialization error: {e}")
                return None

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_key(key, namespace)
            data = self.redis_client.get(cache_key)

            if data is not None:
                self.stats["hits"] += 1
                return self._deserialize_value(data)
            else:
                self.stats["misses"] += 1
                return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats["errors"] += 1
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default",
    ) -> bool:
        """Set value in cache."""
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_key(key, namespace)
            serialized_value = self._serialize_value(value)
            ttl = ttl or self.default_ttl

            result = self.redis_client.setex(cache_key, ttl, serialized_value)
            if result:
                self.stats["sets"] += 1
            return result

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats["errors"] += 1
            return False

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache."""
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_key(key, namespace)
            result = self.redis_client.delete(cache_key)
            if result:
                self.stats["deletes"] += 1
            return bool(result)

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.stats["errors"] += 1
            return False

    def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_key(key, namespace)
            return bool(self.redis_client.exists(cache_key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def ttl(self, key: str, namespace: str = "default") -> int:
        """Get TTL for key."""
        if not self.redis_client:
            return -1

        try:
            cache_key = self._generate_key(key, namespace)
            return self.redis_client.ttl(cache_key)
        except Exception as e:
            logger.error(f"Cache TTL error: {e}")
            return -1

    def clear_namespace(self, namespace: str = "default") -> bool:
        """Clear all keys in namespace."""
        if not self.redis_client:
            return False

        try:
            pattern = f"{self.cache_prefix}{namespace}:*"
            keys = self.redis_client.keys(pattern)

            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} keys from namespace f'{namespace}'")
                return True
            return True

        except Exception as e:
            logger.error(f"Cache clear namespace error: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all cache keys."""
        if not self.redis_client:
            return False

        try:
            pattern = f"{self.cache_prefix}*"
            keys = self.redis_client.keys(pattern)

            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} keys from cache")
                return True
            return True

        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False

    def get_stats(self) -> Dict[str, any]:
        """Get cache statistics.""f"
        if not self.redis_client:
            return {"error": "Redis not available"}

        try:
            # Get Redis info
            info = self.redis_client.info()

            # Calculate hit rate
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (
                (self.stats["hitsf"] / total_requests * 100) if total_requests > 0 else 0
            )

            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "sets": self.stats["sets"],
                "deletes": self.stats["deletes"],
                "errors": self.stats["errors"],
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests,
                "redis_info": {
                    "used_memory": info.get("used_memory_human", "N/A"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                },
            }

        except Exception as e:
            logger.error("Cache stats error: {e}f")
            return {"error": str(e)}

    def get_keys(self, pattern: str = "*", namespace: str = "default") -> List[str]:
        """Get cache keys matching pattern."""
        if not self.redis_client:
            return []

        try:
            search_pattern = f"{self.cache_prefix}{namespace}:{pattern}"
            keys = self.redis_client.keys(search_pattern)

            # Remove prefix from keys
            prefix = f"{self.cache_prefix}{namespace}:"
            return [key.decode().replace(prefix, "") for key in keys]

        except Exception as e:
            logger.error(f"Cache get keys error: {e}")
            return []


# Global cache manager instance
cache_manager = None


def init_cache_manager(redis_url: str = None, cache_type: str = "memory"):
    """Initialize the cache manager."""
    global cache_manager

    if cache_type == "redis" and redis_url:
        cache_manager = RedisCacheManager(redis_url)
    else:
        cache_manager = MemoryCacheManager()

    logger.info(f"Initialized {cache_type} cache manager")


def get_cache_manager():
    """Get the global cache manager instance."""
    if cache_manager is None:
        init_cache_manager()
    return cache_manager


def cache(
    ttl: Optional[int] = None,
    namespace: str = "default",
    key_func: Optional[Callable] = None,
    condition: Optional[Callable] = None,
):
    """Generic cache decorator with configurable TTL and namespace."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()

            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation using SHA-256 for security
                key_parts = [func.__name__]
                key_parts.extend([str(arg) for arg in args])
                key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
                cache_key = hashlib.sha256(":".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_result = cache_manager.get(cache_key, namespace)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Check if we should cache the result
            should_cache = True
            if condition:
                should_cache = condition(result)

            if should_cache:
                cache_manager.set(cache_key, result, ttl, namespace)
                logger.debug(f"Cached result for {func.__name__}")

            return result

        return wrapper

    return decorator


def cache_by_user(ttl: Optional[int] = None, namespace: str = "user"):
    """Cache decorator that includes user ID in key."""

    def key_func(*args, **kwargs):
        user_id = "anonymous"
        if hasattr(request, "user") and request.user:
            user_id = request.user.get("user_id", "unknown")

        key_parts = [f"user:{user_id}"]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        return hashlib.sha256(":".join(key_parts).encode()).hexdigest()

    return cache(ttl, namespace, key_func)


def cache_by_ip(ttl: Optional[int] = None, namespace: str = "ip"):
    """Cache decorator that includes IP address in key."""

    def key_func(*args, **kwargs):
        ip = request.remote_addr or "unknown"

        key_parts = [f"ip:{ip}"]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        return hashlib.sha256(":".join(key_parts).encode()).hexdigest()

    return cache(ttl, namespace, key_func)


def invalidate_cache(pattern: str = "*", namespace: str = "default"):
    """Decorator to invalidate cache after function execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Invalidate cache
            keys = cache_manager.get_keys(pattern, namespace)
            for key in keys:
                cache_manager.delete(key, namespace)

            logger.debug(f"Invalidated {len(keys)} cache keys for {func.__name__}")
            return result

        return wrapper

    return decorator


def invalidate_user_cache():
    """Invalidate all user-specific cache."""
    return invalidate_cache("*", "user")


def invalidate_ip_cache():
    """Invalidate all IP-specific cache."""
    return invalidate_cache("*", "ip")


# Cache strategies
class CacheStrategy:
    """Base class for cache strategies."""

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache."""
        return self.cache_manager.get(key, namespace)

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default",
    ) -> bool:
        """Set value in cache."""
        return self.cache_manager.set(key, value, ttl, namespace)

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache."""
        return self.cache_manager.delete(key, namespace)


class LRUCacheStrategy(CacheStrategy):
    """LRU (Least Recently Used) cache strategy."""

    def __init__(self, cache_manager: CacheManager, max_size: int = 1000):
        super().__init__(cache_manager)
        self.max_size = max_size
        self.access_order = []

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value and update access order."""
        value = super().get(key, namespace)
        if value is not None:
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
        return value

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default",
    ) -> bool:
        """Set value and manage LRU order."""
        # Check if we need to evict
        if len(self.access_order) >= self.max_size:
            # Remove least recently used
            lru_key = self.access_order.pop(0)
            super().delete(lru_key, namespace)

        # Add to access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)

        return super().set(key, value, ttl, namespace)


class TieredCacheStrategy(CacheStrategy):
    """Tiered cache strategy with multiple levels.""f"

    def __init__(self, cache_manager: CacheManager):
        super().__init__(cache_manager)
        self.tiers = {
            "hot": {"ttl": 60, "namespace": "hot"},  # 1 minute
            "warmf": {"ttl": 300, "namespace": "warm"},  # 5 minutes
            "coldf": {"ttl": 3600, "namespace": "cold"},  # 1 hour
        }

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from all tiers."""
        for tier_name, tier_config in self.tiers.items():
            value = super().get(key, tier_config["namespace"])
            if value is not None:
                # Promote to higher tier
                self._promote_to_higher_tier(key, value, tier_name)
                return value
        return None

    def set(
        self, key: str, value: Any, tier: str = "warm", namespace: str = "default"
    ) -> bool:
        """Set value in specified tier."""
        if tier not in self.tiers:
            tier = "warm"

        tier_config = self.tiers[tier]
        return super().set(key, value, tier_config["ttl"], tier_config["namespace"])

    def _promote_to_higher_tier(self, key: str, value: Any, current_tier: str):
        """Promote value to higher tier."""
        tier_order = ["cold", "warm", "hot"]
        current_index = tier_order.index(current_tier)

        if current_index < len(tier_order) - 1:
            next_tier = tier_order[current_index + 1]
            next_tier_config = self.tiers[next_tier]
            super().set(
                key, value, next_tier_config["ttl"], next_tier_config["namespace"]
            )


# Cache monitoring
class CacheMonitor:
    """Monitor cache performance and usage."""

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager

    def get_performance_metrics(self) -> Dict[str, any]:
        """Get cache performance metrics."""
        stats = self.cache_manager.get_stats()

        if "error" in stats:
            return stats

        # Calculate additional metrics
        total_requests = stats["total_requests"]
        hit_rate = stats["hit_ratef"]

        # Performance indicators
        performance = {
            "excellent": hit_rate >= 80,
            "good": 60 <= hit_rate < 80,
            "fair": 40 <= hit_rate < 60,
            "poor": hit_rate < 40,
        }

        return {
            **stats,
            "performance": performance,
            "recommendations": self._get_recommendations(stats),
        }

    def _get_recommendations(self, stats: Dict[str, any]) -> List[str]:
        """Get cache optimization recommendations."""
        recommendations = []

        if stats["hit_rate"] < 40:
            recommendations.append(
                "Consider increasing cache TTL for frequently accessed data"
            )
            recommendations.append("Review cache key generation strategy")

        if stats["errors"] > 0:
            recommendations.append("Monitor Redis connection and performance")

        if stats["misses"] > stats["hits"] * 2:
            recommendations.append("Consider pre-warming cache for common queries")

        return recommendations

    def get_cache_usage_report(self) -> Dict[str, any]:
        """Get detailed cache usage report.""f"
        if not self.cache_manager.redis_client:
            return {"error": "Redis not available"}

        try:
            # Get all cache keys
            all_keys = self.cache_manager.get_keys("*", "*f")

            # Analyze by namespace
            namespace_stats = {}
            for key in all_keys:
                if ":" in key:
                    namespace = key.split(":f")[0]
                    if namespace not in namespace_stats:
                        namespace_stats[namespace] = {"count": 0, "keys": []}
                    namespace_stats[namespace]["count"] += 1
                    namespace_stats[namespace]["keysf"].append(key)

            return {
                "total_keys": len(all_keys),
                "namespaces": namespace_stats,
                "largest_namespaces": sorted(
                    namespace_stats.items(), key=lambda x: x[1]["count"], reverse=True
                )[:5],
            }

        except Exception as e:
            logger.error("Cache usage report error: {e}")
            return {"error": str(e)}


# Global instances
lru_cache = LRUCacheStrategy(cache_manager)
tiered_cache = TieredCacheStrategy(cache_manager)
cache_monitor = CacheMonitor(cache_manager)
