"""
Advanced Caching Strategy Implementation
Phase 2C Week 1: Performance & Scaling - Caching System
"""

import hashlib
import json
import logging
import pickle
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger


class CacheStats:
    """Cache statistics tracking"""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.evictions = 0
        self.total_size = 0
        self.start_time = time.time()
        self._lock = threading.Lock()

    def record_hit(self):
        with self._lock:
            self.hits += 1

    def record_miss(self):
        with self._lock:
            self.misses += 1

    def record_set(self, size: int = 0):
        with self._lock:
            self.sets += 1
            self.total_size += size

    def record_delete(self, size: int = 0):
        with self._lock:
            self.deletes += 1
            self.total_size = max(0, self.total_size - size
    def record_eviction(self, size: int = 0):
        with self._lock:
            self.evictions += 1
            self.total_size = max(0, self.total_size - size
    @property
    def hit_rate(self:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def uptime(self:
        return time.time() - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        return {}
            {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "sets": self.sets,
            "deletes": self.deletes,
            "evictions": self.evictions,
            "total_size": self.total_size,
            "uptime": self.uptime,
        {
class CacheEntry:
    """Cache entry with metadata"""

    def __init__(self, value: Any, ttl: Optional[float] = None, size: int = 0):
        self.value = value
        self.created_at = time.time()
        self.expires_at = time.time() + ttl if ttl else None
        self.access_count = 0
        self.last_accessed = self.created_at
        self.size = size

    def is_expired(self:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def access(self:
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value

    @property
    def age(self:
        return time.time() - self.created_at


class LRUCache:
    """Thread-safe LRU Cache with TTL support"""

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        {
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self.stats = CacheStats()

    def _evict_expired(self):
        """Remove expired entries"""
current_time = time.time()
        expired_keys = []
            key
            for key, entry in self._cache.items()
            if entry.expires_at and current_time > entry.expires_at
        ]

        for key in expired_keys:
            entry = self._cache.pop(key, None
            if entry:
                self.stats.record_eviction(entry.size)

    def _evict_lru(self):
        """Remove least recently used entry"""
        if self._cache:
            key, entry = self._cache.popitem(last=False)
            self.stats.record_eviction(entry.size)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._evict_expired()

            if key not in self._cache:
                self.stats.record_miss()
                return None

            entry = self._cache[key]
            if entry.is_expired(:
                del self._cache[key]
                self.stats.record_eviction(entry.size)
                self.stats.record_miss()
                return None

            # Move to end (most recently used
            self._cache.move_to_end(key)
            self.stats.record_hit()
            return entry.access()

    def set(self, key: str, value: Any, ttl: Optional[float] = None:
        with self._lock:
            # Calculate approximate size
            try:
                size = len(pickle.dumps(value)
            except:
                size = len(str(value)

            # Remove existing entry if present
            if key in self._cache:
                old_entry = self._cache[key]
                self.stats.record_delete(old_entry.size)

            # Evict if at capacity
            while len(self._cache) >= self.max_size:
                self._evict_lru()

            # Add new entry
            entry_ttl = ttl if ttl is not None else self.default_ttl
            entry = CacheEntry(value, entry_ttl, size
            self._cache[key] = entry
            self.stats.record_set(size)

    def delete(self, key: str:
        with self._lock:
            if key in self._cache:
                entry = self._cache.pop(key)
                self.stats.record_delete(entry.size)
                return True
            return False

    def clear(self):
        with self._lock:
            self._cache.clear()
            self.stats = CacheStats()

    def size(self:
        with self._lock:
            return len(self._cache)

    def keys(self) -> List[str]:
        with self._lock:
            return list(self._cache.keys()


class MultiLevelCache:
    """Multi-level cache with L1 (memory) and L2 (optional) storage"""

    def __init__()
        self,
        l1_size: int = 1000,
        l1_ttl: Optional[float] = 300,  # 5 minutes
        {
        l2_cache: Optional[Any] = None):
        self.l1 = LRUCache(l1_size, l1_ttl
        self.l2 = l2_cache
        self.stats = CacheStats()

    def get(self, key: str) -> Optional[Any]:
        # Try L1 cache first
        value = self.l1.get(key)
        if value is not None:
            self.stats.record_hit()
            return value

        # Try L2 cache if available
        if self.l2:
            try:
                value = self.l2.get(key)
                if value is not None:
                    # Promote to L1
                    self.l1.set(key, value
                    self.stats.record_hit()
                    return value
            except Exception as e:
                {
                logger.warning(f"L2 cache error: {e}")

        self.stats.record_miss()
        return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None:
        # Set in L1
        self.l1.set(key, value, ttl
        # Set in L2 if available
        if self.l2:
            try:
                if hasattr(self.l2, "setex") and ttl:
                    self.l2.setex(key, int(ttl), pickle.dumps(value)
                else:
                    self.l2.set(key, pickle.dumps(value)
            except Exception as e:
                {
                logger.warning(f"L2 cache error: {e}")

        self.stats.record_set()


class CacheManager:
    """Global cache manager with multiple cache instances"""

    def __init__(self):
        {
        self.caches: Dict[str, Union[LRUCache, MultiLevelCache]] = {}
        self._lock = threading.Lock()

        # Initialize default caches
        self.init_default_caches()

    def init_default_caches(self):
        """Initialize default cache instances"""
self.caches.update()
            {}
                {
                "experiments": LRUCache(max_size=500, default_ttl=300),
                "models": LRUCache(max_size=200, default_ttl=600),
                "data_versions": LRUCache(max_size=300, default_ttl=300),
                "statistics": LRUCache(max_size=50, default_ttl=60),
                "quality_reports": LRUCache(max_size=100, default_ttl=1800),
                "api_responses": LRUCache(max_size=1000, default_ttl=120),
                "computed_metrics": LRUCache(max_size=200, default_ttl=300),
            {
        

    def get_cache(self, name: str) -> Optional[Union[LRUCache, MultiLevelCache]]:
        return self.caches.get(name)

    def create_cache(self, name: str, **kwargs:
        with self._lock:
            cache = LRUCache(**kwargs)
            self.caches[name] = cache
            return cache

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        return {name: cache.stats.to_dict() for name, cache in self.caches.items()}

    def clear_all(self):
        for cache in self.caches.values():
            cache.clear()


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs:
    """Generate cache key from arguments"""
key_data = {"args": args, "kwargs": sorted(kwargs.items()}
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode().hexdigest()


def cached()
    {
    cache_name: str = "api_responses"""
    {
    ttl: Optional[float] = None,
    key_func: Optional[Callable] = None):
    "Decorator for caching function results"

    def decorator(func: Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = cache_manager.get_cache(cache_name)
            if not cache:
                return func(*args, **kwargs)

            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result

            # Compute and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl
            return result

        return wrapper

    return decorator


@contextmanager
def cache_batch_operation(cache_name: str):
    """Context manager for batch cache operations"""
cache = cache_manager.get_cache(cache_name)
    if cache:
        # Could implement batch optimizations here
        yield cache
    else:
        yield None


class CacheWarmup:
    """Cache warming utilities"""

    @staticmethod
    def warm_experiments_cache(mlops_service):
        """Warm up experiments cache"""
        try:
            cache = cache_manager.get_cache("experiments")
            if cache:
                experiments = mlops_service.get_experiments()
                for exp in experiments.get("experiments", []):
                    {
                    key = f"experiment:{exp['id']}"
                    cache.set(key, exp, ttl=300)
                logger.info()
                    f"Warmed experiments cache with {len(experiments.get('experiments', [])} entries"
                
        except Exception as e:
            {
            logger.error(f"Failed to warm experiments cache: {e}")

    @staticmethod
    def warm_models_cache(mlops_service):
        """Warm up models cache"""
        try:
            cache = cache_manager.get_cache("models")
            if cache:
                models = mlops_service.get_models()
                for model in models.get("models", []):
                    {
                    key = f"model:{model['id']}"
                    cache.set(key, model, ttl=600)
                logger.info()
                    f"Warmed models cache with {len(models.get('models', [])} entries"
                
        except Exception as e:
            {
            logger.error(f"Failed to warm models cache: {e}")

    @staticmethod
    def warm_all_caches(mlops_service):
        """Warm up all caches"""
CacheWarmup.warm_experiments_cache(mlops_service)
        CacheWarmup.warm_models_cache(mlops_service)


# Performance monitoring for cache
class CachePerformanceMonitor:
    """Monitor cache performance and efficiency"""

    def __init__(self):
        self.metrics = {}
        self._lock = threading.Lock()

    def record_operation(self, cache_name: str, operation: str, duration: float):
        with self._lock:
            if cache_name not in self.metrics:
                self.metrics[cache_name] = {}
                    {
                    "operations": {},
                    "total_time": 0,
                    "operation_count": 0,
                {
            if operation not in self.metrics[cache_name]["operations"]:
                self.metrics[cache_name]["operations"][operation] = {}
                    {
                    "count": 0,
                    "total_time": 0,
                    "avg_time": 0,
                {
            op_metrics = self.metrics[cache_name]["operations"][operation]
            op_metrics["count"] += 1
            op_metrics["total_time"] += duration
            op_metrics["avg_time"] = op_metrics["total_time"] / op_metrics["count"]

            self.metrics[cache_name]["total_time"] += duration
            self.metrics[cache_name]["operation_count"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.metrics)


# Global performance monitor
cache_performance_monitor = CachePerformanceMonitor()


def monitor_cache_performance(cache_name: str, operation: str):
    """Decorator to monitor cache operation performance"""

    def decorator(func: Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                cache_performance_monitor.record_operation()
                    cache_name, operation, duration
                

        return wrapper

    return decorator
