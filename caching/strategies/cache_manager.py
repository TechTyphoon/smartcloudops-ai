"""
Centralized Cache Management and Strategy Implementation
Phase 3 Week 4: Advanced Caching Strategies - Cache Manager
"""

import asyncio
import hashlib
import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from .multi_tier_cache import CacheLevel, MultiTierCache, get_multi_tier_cache
from .redis_cache import get_redis_cache

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache invalidation and refresh strategies"""

    WRITE_THROUGH = "write_through"  # Write to cache and storage simultaneously
    WRITE_BEHIND = "write_behind"  # Write to cache first, storage later
    WRITE_AROUND = "write_around"  # Write only to storage, bypass cache
    READ_THROUGH = "read_through"  # Read from storage if not in cache
    CACHE_ASIDE = "cache_aside"  # Application manages cache manually
    REFRESH_AHEAD = "refresh_ahead"  # Proactively refresh before expiration


class CacheTag(Enum):
    """Cache content tags for intelligent invalidation"""

    USER_DATA = "user_data"
    SYSTEM_CONFIG = "system_config"
    MLOPS_MODELS = "mlops_models"
    MLOPS_EXPERIMENTS = "mlops_experiments"
    MLOPS_DATA = "mlops_data"
    API_RESPONSES = "api_responses"
    COMPUTED_RESULTS = "computed_results"
    STATIC_CONTENT = "static_content"


@dataclass
class CachePolicy:
    """Cache policy configuration"""

    ttl: int = 3600  # Time to live in seconds
    strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    target_level: Optional[CacheLevel] = None  # Preferred cache level
    tags: List[CacheTag] = None  # Content tags
    compress: bool = False  # Enable compression
    serializer: str = "json"  # Serialization method
    refresh_ahead_ratio: float = 0.8  # Refresh when TTL reaches this ratio
    max_size: Optional[int] = None  # Maximum cache size for this policy

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class CacheManager:
    """Centralized cache management system"""

    def __init__(self):
        self.multi_tier_cache = get_multi_tier_cache()
        self.redis_cache = get_redis_cache()

        # Cache policies by namespace
        self.policies: Dict[str, CachePolicy] = {}

        # Tag-based invalidation tracking
        self.tag_keys: Dict[CacheTag, set] = {tag: set() for tag in CacheTag}

        # Background refresh tracking
        self.refresh_tasks = {}
        self.refresh_executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="cache_refresh"
        )

        # Cache warming functions
        self.warmup_functions: Dict[str, Callable] = {}

        # Statistics
        self.operation_stats = {
            "gets": 0,
            "sets": 0,
            "deletes": 0,
            "invalidations": 0,
            "refreshes": 0,
            "errors": 0,
        }

        self._lock = threading.RLock()

        # Initialize default policies
        self._setup_default_policies()

        logger.info("Cache Manager initialized")

    def _setup_default_policies(self):
        """Setup default cache policies for different namespaces"""
        self.set_policy(
            "mlops:experiments",
            CachePolicy(
                ttl=7200,  # 2 hours
                strategy=CacheStrategy.READ_THROUGH,
                tags=[CacheTag.MLOPS_EXPERIMENTS],
                target_level=CacheLevel.L1_MEMORY,
            ),
        )

        self.set_policy(
            "mlops:models",
            CachePolicy(
                ttl=3600,  # 1 hour
                strategy=CacheStrategy.WRITE_THROUGH,
                tags=[CacheTag.MLOPS_MODELS],
                target_level=CacheLevel.L2_REDIS,
            ),
        )

        self.set_policy(
            "mlops:data",
            CachePolicy(
                ttl=1800,  # 30 minutes
                strategy=CacheStrategy.CACHE_ASIDE,
                tags=[CacheTag.MLOPS_DATA],
                compress=True,
            ),
        )

        self.set_policy(
            "api:responses",
            CachePolicy(
                ttl=300,  # 5 minutes
                strategy=CacheStrategy.CACHE_ASIDE,
                tags=[CacheTag.API_RESPONSES],
                target_level=CacheLevel.L1_MEMORY,
                refresh_ahead_ratio=0.9,
            ),
        )

        self.set_policy(
            "user:data",
            CachePolicy(
                ttl=1800,  # 30 minutes
                strategy=CacheStrategy.WRITE_THROUGH,
                tags=[CacheTag.USER_DATA],
                target_level=CacheLevel.L2_REDIS,
            ),
        )

        self.set_policy(
            "system:config",
            CachePolicy(
                ttl=86400,  # 24 hours
                strategy=CacheStrategy.READ_THROUGH,
                tags=[CacheTag.SYSTEM_CONFIG],
                target_level=CacheLevel.L1_MEMORY,
            ),
        )

    def set_policy(self, namespace: str, policy: CachePolicy):
        """Set cache policy for namespace"""
        with self._lock:
            self.policies[namespace] = policy
            logger.info(f"Set cache policy for namespace: {namespace}")

    def get_policy(self, key: str) -> CachePolicy:
        """Get cache policy for key based on namespace"""
        # Extract namespace from key (before first colon)
        namespace = key.split(":", 1)[0] if ":" in key else "default"

        # Try specific namespace first, then default
        return self.policies.get(
            f"{namespace}:*",
            self.policies.get(namespace, self.policies.get("default", CachePolicy())),
        )

    def get(
        self,
        key: str,
        fetch_func: Optional[Callable] = None,
        policy: Optional[CachePolicy] = None,
    ) -> Any:
        """Get value with intelligent caching strategy"""
        start_time = time.time()

        with self._lock:
            self.operation_stats["gets"] += 1

            try:
                # Get applicable policy
                if policy is None:
                    policy = self.get_policy(key)

                # Try cache first
                value = self.multi_tier_cache.get(key)

                if value is not None:
                    # Check if refresh ahead is needed
                    self._check_refresh_ahead(key, policy, fetch_func)
                    return value

                # Cache miss - handle based on strategy
                if policy.strategy in [
                    CacheStrategy.READ_THROUGH,
                    CacheStrategy.CACHE_ASIDE,
                ]:
                    if fetch_func:
                        value = self._fetch_and_cache(key, fetch_func, policy)
                        return value

                return None

            except Exception as e:
                logger.error(f"Cache get error for key {key}: {e}")
                self.operation_stats["errors"] += 1

                # Fallback to fetch function if available
                if fetch_func:
                    try:
                        return fetch_func()
                    except Exception:
                        pass

                return None

    def set(
        self,
        key: str,
        value: Any,
        policy: Optional[CachePolicy] = None,
        storage_func: Optional[Callable] = None,
    ) -> bool:
        """Set value with caching strategy"""
        start_time = time.time()

        with self._lock:
            self.operation_stats["sets"] += 1

            try:
                # Get applicable policy
                if policy is None:
                    policy = self.get_policy(key)

                # Handle based on strategy
                if policy.strategy == CacheStrategy.WRITE_THROUGH:
                    # Write to storage first
                    if storage_func and not storage_func(value):
                        return False

                    # Then write to cache
                    success = self._cache_set(key, value, policy)

                elif policy.strategy == CacheStrategy.WRITE_BEHIND:
                    # Write to cache first
                    success = self._cache_set(key, value, policy)

                    # Schedule storage write
                    if storage_func and success:
                        self.refresh_executor.submit(storage_func, value)

                elif policy.strategy == CacheStrategy.WRITE_AROUND:
                    # Write only to storage
                    if storage_func:
                        success = storage_func(value)
                    else:
                        success = False

                    # Don't cache the value

                else:  # CACHE_ASIDE or others
                    success = self._cache_set(key, value, policy)

                # Update tag tracking
                if success:
                    self._update_tag_tracking(key, policy.tags)

                return success

            except Exception as e:
                logger.error(f"Cache set error for key {key}: {e}")
                self.operation_stats["errors"] += 1
                return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            self.operation_stats["deletes"] += 1

            try:
                # Remove from cache
                success = self.multi_tier_cache.delete(key)

                # Remove from tag tracking
                self._remove_from_tag_tracking(key)

                # Cancel any pending refresh
                if key in self.refresh_tasks:
                    self.refresh_tasks[key].cancel()
                    del self.refresh_tasks[key]

                return success

            except Exception as e:
                logger.error(f"Cache delete error for key {key}: {e}")
                self.operation_stats["errors"] += 1
                return False

    def invalidate_by_tag(self, tag: CacheTag) -> int:
        """Invalidate all cache entries with specific tag"""
        with self._lock:
            self.operation_stats["invalidations"] += 1

            try:
                keys_to_invalidate = self.tag_keys[tag].copy()
                invalidated = 0

                for key in keys_to_invalidate:
                    if self.delete(key):
                        invalidated += 1

                logger.info(f"Invalidated {invalidated} keys with tag: {tag.value}")
                return invalidated

            except Exception as e:
                logger.error(f"Tag invalidation error for tag {tag}: {e}")
                self.operation_stats["errors"] += 1
                return 0

    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        with self._lock:
            self.operation_stats["invalidations"] += 1

            try:
                return self.multi_tier_cache.invalidate_pattern(pattern)
            except Exception as e:
                logger.error(f"Pattern invalidation error for pattern {pattern}: {e}")
                self.operation_stats["errors"] += 1
                return 0

    def warm_cache(self, namespace: str, keys: List[str] = None) -> Dict[str, Any]:
        """Warm cache for specific namespace"""
        if namespace not in self.warmup_functions:
            logger.warning(f"No warmup function registered for namespace: {namespace}")
            return {"status": "error", "message": "No warmup function registered"}

        warmup_func = self.warmup_functions[namespace]

        try:
            start_time = time.time()

            if keys:
                # Warm specific keys
                loaded = 0
                for key in keys:
                    try:
                        value = warmup_func(key)
                        if value is not None:
                            policy = self.get_policy(key)
                            if self._cache_set(key, value, policy):
                                loaded += 1
                    except Exception as e:
                        logger.error(f"Error warming key {key}: {e}")

                duration = time.time() - start_time

                return {
                    "status": "success",
                    "namespace": namespace,
                    "loaded_keys": loaded,
                    "total_keys": len(keys),
                    "duration": duration,
                }
            else:
                # Let warmup function handle batch loading
                result = warmup_func()
                duration = time.time() - start_time

                return {
                    "status": "success",
                    "namespace": namespace,
                    "result": result,
                    "duration": duration,
                }

        except Exception as e:
            logger.error(f"Cache warming error for namespace {namespace}: {e}")
            return {"status": "error", "message": str(e)}

    def register_warmup_function(self, namespace: str, func: Callable):
        """Register cache warmup function for namespace"""
        self.warmup_functions[namespace] = func
        logger.info(f"Registered warmup function for namespace: {namespace}")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._lock:
            # Get multi-tier cache metrics
            cache_metrics = self.multi_tier_cache.get_metrics()

            # Get cache distribution
            distribution = self.multi_tier_cache.get_cache_distribution()

            # Get tag statistics
            tag_stats = {}
            for tag, keys in self.tag_keys.items():
                tag_stats[tag.value] = len(keys)

            return {
                "operation_stats": self.operation_stats.copy(),
                "cache_metrics": cache_metrics,
                "cache_distribution": distribution,
                "tag_statistics": tag_stats,
                "policies_count": len(self.policies),
                "warmup_functions": list(self.warmup_functions.keys()),
                "active_refresh_tasks": len(self.refresh_tasks),
            }

    def optimize(self) -> Dict[str, Any]:
        """Perform cache optimization"""
        with self._lock:
            try:
                # Optimize multi-tier cache
                optimization_result = self.multi_tier_cache.optimize_cache()

                # Clean up completed refresh tasks
                completed_tasks = [
                    key for key, task in self.refresh_tasks.items() if task.done()
                ]

                for key in completed_tasks:
                    del self.refresh_tasks[key]

                optimization_result["cleaned_refresh_tasks"] = len(completed_tasks)

                logger.info(f"Cache optimization completed: {optimization_result}")
                return optimization_result

            except Exception as e:
                logger.error(f"Cache optimization error: {e}")
                return {"status": "error", "message": str(e)}

    def _cache_set(self, key: str, value: Any, policy: CachePolicy) -> bool:
        """Internal cache set with policy application"""
        return self.multi_tier_cache.set(
            key=key, value=value, ttl=policy.ttl, target_level=policy.target_level
        )

    def _fetch_and_cache(
        self, key: str, fetch_func: Callable, policy: CachePolicy
    ) -> Any:
        """Fetch data and cache according to policy"""
        try:
            value = fetch_func()
            if value is not None:
                self._cache_set(key, value, policy)
                self._update_tag_tracking(key, policy.tags)
            return value
        except Exception as e:
            logger.error(f"Fetch and cache error for key {key}: {e}")
            raise

    def _check_refresh_ahead(
        self, key: str, policy: CachePolicy, fetch_func: Optional[Callable]
    ):
        """Check if refresh ahead is needed"""
        if (
            policy.strategy == CacheStrategy.REFRESH_AHEAD
            and fetch_func
            and policy.refresh_ahead_ratio > 0
        ):

            # Check TTL remaining
            if self.redis_cache:
                ttl_remaining = self.redis_cache.ttl(key)
                if ttl_remaining > 0:
                    refresh_threshold = policy.ttl * policy.refresh_ahead_ratio

                    if ttl_remaining <= (policy.ttl - refresh_threshold):
                        # Schedule refresh if not already scheduled
                        if key not in self.refresh_tasks:
                            task = self.refresh_executor.submit(
                                self._background_refresh, key, fetch_func, policy
                            )
                            self.refresh_tasks[key] = task

    def _background_refresh(self, key: str, fetch_func: Callable, policy: CachePolicy):
        """Background refresh of cache entry"""
        try:
            self.operation_stats["refreshes"] += 1

            value = fetch_func()
            if value is not None:
                self._cache_set(key, value, policy)
                logger.debug(f"Background refreshed key: {key}")

        except Exception as e:
            logger.error(f"Background refresh error for key {key}: {e}")
            self.operation_stats["errors"] += 1
        finally:
            # Remove from tracking
            if key in self.refresh_tasks:
                del self.refresh_tasks[key]

    def _update_tag_tracking(self, key: str, tags: List[CacheTag]):
        """Update tag-based tracking for key"""
        # Remove key from all tag sets first
        self._remove_from_tag_tracking(key)

        # Add to relevant tag sets
        for tag in tags:
            self.tag_keys[tag].add(key)

    def _remove_from_tag_tracking(self, key: str):
        """Remove key from all tag tracking"""
        for tag_keys in self.tag_keys.values():
            tag_keys.discard(key)

    def close(self):
        """Cleanup cache manager resources"""
        try:
            # Shutdown executor
            self.refresh_executor.shutdown(wait=True)

            # Cancel pending tasks
            for task in self.refresh_tasks.values():
                task.cancel()

            self.refresh_tasks.clear()

            logger.info("Cache Manager closed")

        except Exception as e:
            logger.error(f"Error closing Cache Manager: {e}")


# Decorators for easy caching
def cached_with_policy(
    namespace: str,
    ttl: Optional[int] = None,
    tags: List[CacheTag] = None,
    strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE,
):
    """Decorator for caching function results with policy"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{namespace}:{func.__name__}"

            # Add arguments to key if present
            if args or kwargs:
                arg_str = "_".join(str(arg) for arg in args)
                kwarg_str = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                key_parts = [cache_key, arg_str, kwarg_str]
                cache_key = ":".join(filter(None, key_parts))

            # Hash long keys
            if len(cache_key) > 250:
                cache_key = hashlib.md5(cache_key.encode()).hexdigest()

            # Create policy
            policy = CachePolicy(ttl=ttl or 3600, strategy=strategy, tags=tags or [])

            # Try cache first
            cache_manager = get_cache_manager()

            def fetch_func():
                return func(*args, **kwargs)

            return cache_manager.get(cache_key, fetch_func, policy)

        return wrapper

    return decorator


def invalidate_cache_tag(tag: CacheTag):
    """Decorator to invalidate cache by tag after function execution"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Invalidate cache
            cache_manager = get_cache_manager()
            invalidated = cache_manager.invalidate_by_tag(tag)

            if invalidated > 0:
                logger.info(
                    f"Invalidated {invalidated} cache entries for tag: {tag.value}"
                )

            return result

        return wrapper

    return decorator


# Global cache manager instance
_cache_manager = None
_cache_manager_lock = threading.Lock()


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager

    if _cache_manager is None:
        with _cache_manager_lock:
            if _cache_manager is None:
                _cache_manager = CacheManager()

    return _cache_manager
